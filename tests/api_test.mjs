// Local checks for mapot-src/api.js: order validation, color rules, null availability.
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { webcrypto } from "node:crypto";

const root = new URL("..", import.meta.url);
const api = readFileSync(new URL("mapot-src/api.js", root), "utf8");
const products = readFileSync(new URL("mapot/_products.json", root), "utf8");
const store = new Map();
const mails = [];
let remoteBody = null;
const context = {
  console,
  URL,
  URLSearchParams,
  TextEncoder,
  crypto: webcrypto,
  Response,
  Request,
  caches: {
    default: {
      async match(k) {
        const v = store.get(String(k));
        return v == null ? undefined : new Response(v);
      },
      async put(k, res) {
        store.set(String(k), await res.clone().text());
      },
    },
  },
  fetch: async (url, opts) => {
    remoteBody = { url: String(url), headers: opts && opts.headers };
    return new Response(JSON.stringify({ available: 4, qty_total: 99, qty_available: 80 }), { status: 200 });
  },
};
vm.createContext(context);
vm.runInContext(api + "\nconst PRODUCTS=" + products + ";\nthis.mapotApi=mapotApi;", context);

function env(extra = {}) {
  return {
    MAILER: {
      async fetch(_url, opts) {
        mails.push(JSON.parse(opts.body));
        return new Response("ok", { status: 200 });
      },
    },
    DB: { prepare() { return { bind() { return { async run() {} }; } }; } },
    ...extra,
  };
}
function orderReq(body, ip = "203.0.113.10") {
  return new Request("https://hayahara.co.il/mapot/api/order", {
    method: "POST",
    headers: { "content-type": "application/json", "cf-connecting-ip": ip },
    body: JSON.stringify(body),
  });
}
const good = {
  business: "אולם בדיקה",
  contact: "בדיקה",
  phone: "053-2535393",
  email: "office@hayahara.co.il",
  event_date: "2026-12-01",
  address: "פרי גן 16 מישור אדומים",
  notes: "TEST בדיקת זרימה",
  items: [{ sku: "TC-LINEN-3X3", color: "c01", qty: 4 }],
};
let n = 0;
async function check(name, cond) {
  n++;
  if (!cond) {
    console.error("FAIL", name);
    process.exitCode = 1;
  }
}

const url = new URL("https://hayahara.co.il/mapot/api/order");
const res = await context.mapotApi(orderReq(good), env(), url, "/mapot/api/order");
const body = await res.json();
await check("order ok", res.status === 200 && body.ok && body.mail === "sent");
await check("test subject", mails[0].subject.startsWith("[TEST] "));
await check("mail has color", mails[0].text.includes("לבן") && mails[0].text.includes("מפה פשתן 3×3"));
await check("mail has no stock word", !mails[0].text.includes("מלאי"));
await check("from name kept", mails[0].from_name === "הזמנות מפות");

const honeypotBefore = mails.length;
const hp = await context.mapotApi(orderReq({ ...good, website: "http://spam.example" }, "203.0.113.11"), env(), url, "/mapot/api/order");
await check("honeypot silent", (await hp.json()).ok === true && mails.length === honeypotBefore);

const chairBad = await context.mapotApi(orderReq({ ...good, items: [{ sku: "CC-STD", color: "c01", qty: 2 }] }, "203.0.113.12"), env(), url, "/mapot/api/order");
await check("chair rejects color", chairBad.status === 400);

const chairOk = await context.mapotApi(orderReq({ ...good, items: [{ sku: "CC-STD", qty: 6 }] }, "203.0.113.13"), env(), url, "/mapot/api/order");
const chairMailAt = mails.length;
await check("chair without color", chairOk.status === 200);
await check("chair mail omits color", mails[chairMailAt - 1].text.includes("כיסויי כיסאות") && !mails[chairMailAt - 1].text.includes("·"));

const floral = await context.mapotApi(orderReq({ ...good, items: [{ sku: "TC-FLORAL-*", color: "c09", qty: 1 }] }, "203.0.113.14"), env(), url, "/mapot/api/order");
await check("floral published sku", floral.status === 200 && mails.at(-1).text.includes("מפה פרחים"));

const round = await context.mapotApi(orderReq({ ...good, items: [{ sku: "TC-LINEN-ROUND", color: "c02", qty: 2 }, { sku: "TC-SATIN-ROUND", color: "c04", qty: 1 }] }, "203.0.113.15"), env(), url, "/mapot/api/order");
await check("round cloths", round.status === 200);

const missingColor = await context.mapotApi(orderReq({ ...good, items: [{ sku: "NP-SATIN", qty: 3 }] }, "203.0.113.16"), env(), url, "/mapot/api/order");
await check("color required when listed", missingColor.status === 400);

const badPhone = await context.mapotApi(orderReq({ ...good, phone: "123" }, "203.0.113.17"), env(), url, "/mapot/api/order");
await check("phone", badPhone.status === 400);

const noMailer = await context.mapotApi(orderReq(good, "203.0.113.18"), {}, url, "/mapot/api/order");
await check("no mailer", noMailer.status === 503);

let last = 200;
for (let i = 0; i < 6; i++) {
  const r = await context.mapotApi(orderReq(good, "203.0.113.40"), env(), url, "/mapot/api/order");
  last = r.status;
}
await check("rate limit", last === 429);

const aurl = new URL("https://hayahara.co.il/mapot/api/availability?sku=TC-SATIN-3X3&color=c01");
const avail = await context.mapotApi(new Request(aurl, { headers: { "cf-connecting-ip": "203.0.113.50" } }), env(), aurl, "/mapot/api/availability");
const aj = await avail.json();
await check("null provider", avail.status === 200 && aj.available === null && aj.sku === "TC-SATIN-3X3" && !("qty_total" in aj));

const rurl = new URL("https://hayahara.co.il/mapot/api/availability?sku=TC-SATIN-3X3&color=c03&from=2026-12-01&to=2026-12-02");
const remote = await context.mapotApi(new Request(rurl, { headers: { "cf-connecting-ip": "203.0.113.51" } }), env({ INVENTORY_URL: "https://inventory.internal/avail", INVENTORY_TOKEN: "secret" }), rurl, "/mapot/api/availability");
const rj = await remote.json();
await check("remote provider hides totals", remote.status === 200 && rj.available === 4 && rj.qty_total == null && rj.qty_available == null);
await check("bearer sent", remoteBody && remoteBody.headers.authorization === "Bearer secret");

const missing = await context.mapotApi(new Request("https://hayahara.co.il/mapot/api/availability?sku=NOPE", { headers: { "cf-connecting-ip": "203.0.113.52" } }), env(), new URL("https://hayahara.co.il/mapot/api/availability?sku=NOPE"), "/mapot/api/availability");
await check("unknown sku", missing.status === 404);

if (process.exitCode) process.exit(process.exitCode);
console.log("api ok", n, "checks");
