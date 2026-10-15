// Desktop + mobile screenshots and the order-flow UI. Serves nothing; expects http://127.0.0.1:8765
import puppeteer from "/tmp/pw/node_modules/puppeteer-core/lib/puppeteer/puppeteer-core.js";
import { mkdir } from "node:fs/promises";

const chrome = process.env.CHROME_PATH || "/usr/local/bin/google-chrome";
const base = process.env.MAPOT_LOCAL || "http://127.0.0.1:8765";
const out = new URL("../docs/screens/", import.meta.url).pathname;
await mkdir(out, { recursive: true });

const browser = await puppeteer.launch({
  executablePath: chrome,
  headless: true,
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--font-render-hinting=none"],
});
const page = await browser.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
page.on("console", (m) => {
  if (m.type() === "error") errors.push(m.text());
});

async function ready() {
  await page.waitForFunction(() => document.fonts && document.fonts.status === "loaded");
  await new Promise((r) => setTimeout(r, 150));
}
async function shot(name) {
  await page.screenshot({ path: out + name + ".png", fullPage: true });
  console.log("shot", name);
}
async function h1Lines() {
  return page.$eval("h1", (el) => {
    const lh = parseFloat(getComputedStyle(el).lineHeight);
    return Math.round(el.getBoundingClientRect().height / lh);
  });
}

async function desktop() {
  await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });
  await page.goto(base + "/mapot/", { waitUntil: "networkidle0" });
  await ready();
  const lines = await h1Lines();
  if (lines > 2) throw new Error("home h1 lines " + lines);
  const badge = await page.$eval(".cartlink", (el) => {
    const label = el.querySelector(".cartlabel").getBoundingClientRect();
    const mark = el.querySelector(".badge").getBoundingClientRect();
    const gap = Math.min(Math.abs(mark.right - label.left), Math.abs(label.right - mark.left));
    return { text: el.querySelector(".badge").textContent.trim(), gap, bg: getComputedStyle(el.querySelector(".badge")).backgroundColor };
  });
  if (badge.text !== "0" || badge.gap < 6 || badge.bg === "rgba(0, 0, 0, 0)") throw new Error("cart badge " + JSON.stringify(badge));
  await shot("home-desktop");

  await page.goto(base + "/mapot/catalog/", { waitUntil: "networkidle0" });
  await ready();
  await shot("catalog-desktop");
  await page.click('[data-filter="fabric"][data-value="linen"]');
  await page.waitForFunction(() => {
    const items = [...document.querySelectorAll("#grid .item")];
    return items.some((el) => el.hidden) && items.filter((el) => !el.hidden).length === 6;
  });
  await shot("catalog-linen-desktop");

  await page.goto(base + "/mapot/catalog/tc-linen-3x3/", { waitUntil: "networkidle0" });
  await ready();
  const crumb = await page.$$eval(".crumb > *", (els) =>
    els.map((el) => ({ t: el.textContent.trim(), x: el.getBoundingClientRect().x }))
  );
  const homeCrumb = crumb.find((c) => c.t.includes("היערה"));
  const here = crumb[crumb.length - 1];
  if (!homeCrumb || homeCrumb.x < here.x) throw new Error("breadcrumb RTL order " + JSON.stringify(crumb));
  if (!crumb.some((c) => c.t === "/")) throw new Error("breadcrumb slash missing");
  await page.click('.swatch[data-color="c08"]');
  const cloth = await page.$eval("#stage", (el) => getComputedStyle(el).getPropertyValue("--cloth").trim());
  if (cloth.toLowerCase() !== "#23314f") throw new Error("color did not reach the plate: " + cloth);
  await page.$eval("#q", (el) => { el.value = "2"; });
  await shot("product-desktop");
  await page.click("#add");
  await page.waitForSelector("#added:not([hidden])");
  const count = await page.$eval("#cartn", (el) => el.textContent.trim());
  if (count !== "2") throw new Error("cart count " + count);

  await page.goto(base + "/mapot/order/", { waitUntil: "networkidle0" });
  await ready();
  const line = await page.$eval("#lines", (el) => el.innerText);
  if (!line.includes("מפה פשתן 3×3") || !line.includes("כחול נייבי")) throw new Error("cart line missing: " + line);
  await shot("cart-desktop");
  await page.evaluate(() => document.getElementById("orderform").scrollIntoView());
  await page.screenshot({ path: out + "order-desktop.png" });
  console.log("shot order-desktop");

  await page.click('button[type="submit"]');
  await page.waitForSelector("#err:not([hidden])");

  await page.type("#f-business", "אולם בדיקה");
  await page.type("#f-contact", "בדיקה");
  await page.type("#f-phone", "053-2535393");
  await page.type("#f-email", "office@hayahara.co.il");
  await page.select("#f-day", "01");
  await page.select("#f-month", "12");
  await page.select("#f-year", "2026");
  await page.type("#f-address", "פרי גן 16 מישור אדומים");
  await page.type("#f-notes", "TEST בדיקת דפדפן");

  const payload = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("no order request")), 8000);
    const onReq = async (req) => {
      try {
        if (!req.url().includes("/mapot/api/order")) {
          await req.continue();
          return;
        }
        clearTimeout(timer);
        page.off("request", onReq);
        const body = JSON.parse(req.postData());
        await req.respond({ status: 200, contentType: "application/json", body: JSON.stringify({ ok: true, id: "T1", mail: "sent" }) });
        resolve(body);
      } catch (err) {
        reject(err);
      }
    };
    page.on("request", onReq);
    page.setRequestInterception(true).then(() => page.click('button[type="submit"]')).catch(reject);
  });
  if (payload.items[0].sku !== "TC-LINEN-3X3" || payload.items[0].color !== "c08" || payload.items[0].qty !== 2) {
    throw new Error("bad payload " + JSON.stringify(payload.items));
  }
  if (payload.event_date !== "2026-12-01") throw new Error("event_date " + payload.event_date);
  const hp = await page.$eval(".hp", (el) => {
    const r = el.getBoundingClientRect();
    return { w: r.width, h: r.height, text: el.innerText };
  });
  if (hp.w > 2 || hp.h > 2 || /Website/i.test(hp.text)) throw new Error("honeypot visible " + JSON.stringify(hp));
  if (!payload.notes.startsWith("TEST")) throw new Error("notes");
  await page.waitForSelector("#done:not([hidden])");
  const left = await page.evaluate(() => localStorage.getItem("mapot_cart_v2"));
  if (left) throw new Error("cart not cleared " + left);
}

async function mobile() {
  await page.setRequestInterception(false);
  await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
  await page.goto(base + "/mapot/", { waitUntil: "networkidle0" });
  await ready();
  const mobileLines = await h1Lines();
  if (mobileLines > 2) throw new Error("mobile home h1 lines " + mobileLines);
  const wide = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
  if (wide) throw new Error("mobile home overflows");
  await shot("home-mobile");

  await page.goto(base + "/mapot/catalog/", { waitUntil: "networkidle0" });
  await ready();
  await shot("catalog-mobile");
  await page.click("#openf");
  await page.waitForSelector("#filterpanel.open");
  await shot("catalog-filters-mobile");
  await page.click("#closef");

  await page.goto(base + "/mapot/catalog/tc-satin-round/", { waitUntil: "networkidle0" });
  await ready();
  await page.click('.swatch[data-color="c10"]');
  const dock = await page.$eval(".dock", (el) => getComputedStyle(el).display);
  if (dock === "none") throw new Error("mobile dock hidden");
  const clipped = await page.evaluate(() => {
    const row = [...document.querySelectorAll(".spec")].find((el) => el.querySelector("span")?.textContent === "מידה");
    const dockBox = document.querySelector(".dock").getBoundingClientRect();
    const r = row.getBoundingClientRect();
    const onScreen = r.top < window.innerHeight && r.bottom > 0;
    return { onScreen, top: r.top, bottom: r.bottom, dockTop: dockBox.top, hit: onScreen && r.bottom > dockBox.top + 1 && r.top < dockBox.bottom };
  });
  if (!clipped.onScreen || clipped.hit) throw new Error("spec row vs dock " + JSON.stringify(clipped));
  await shot("product-mobile");
  await page.click("#adddock");
  await page.waitForSelector("#added:not([hidden])");

  await page.goto(base + "/mapot/order/", { waitUntil: "networkidle0" });
  await ready();
  const line = await page.$eval("#lines", (el) => el.innerText);
  if (!line.includes("מפה עגולה סאטן") || !line.includes("בורדו")) throw new Error("mobile cart " + line);
  await shot("cart-mobile");
  await page.evaluate(() => document.getElementById("orderform").scrollIntoView());
  await page.screenshot({ path: out + "order-mobile.png" });
  console.log("shot order-mobile");
}

try {
  await desktop();
  await mobile();
  if (errors.length) {
    console.error(errors.join("\n"));
    process.exitCode = 1;
  } else {
    console.log("browser flow ok");
  }
} finally {
  await browser.close();
}
if (process.exitCode) process.exit(process.exitCode);
