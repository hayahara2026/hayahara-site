# BRIEF: אתר «היערה אירועים» (hayahara.co.il/mapot/) — Rebuild brief for a coding agent

Repo: https://github.com/hayahara2026/hayahara-site · branch `mapot-preview` · open the PR against `mapot-preview`. NEVER touch `main`, never deploy to production, never un-noindex.

## 0. Brand / entity (decision by Zvi, 15.10)
- Brand: **«היערה אירועים»** (HaYaara Events). It is a SUB-BRAND of **מכבסת היערה בע״מ**, not a separate business/registration.
- Contact is identical to HaYaara laundry: email office@hayahara.co.il, phone/WhatsApp 053-2535393, address פרי גן 16, מישור אדומים, legal footer = מכבסת היערה בע״מ.
- JSON-LD: organization = מכבסת היערה (`@id` https://hayahara.co.il/#business) with `alternateName`/`brand` = «היערה אירועים». No separate Organization/registration. (Already applied in `build_mapot.py`; `config.json` brand = `היערה אירועים`.)

## 1. Goal and Zvi's words (quote)
- Zvi: «האתר החדש של ההערה לא יצא טוב בכלל… האתר של היערה כן יוצא מצוין. האתר של המפות, אני רוצה שתיצור אותו עם קורסור… קטלוג מטורף… יפה מאוד, ויזואלי… לא AI, שיהיה מעוצב, שיהיה מותאם לטלפון».
- Earlier: «האתר נראה מידי בינה מלאכותית תעצב את זה ברמה גבוהה יותר». The redesign in commits 49b392a / e39318b still looks too AI. The rest of the HaYaara site is excellent (use it as the quality/style bar: open hayahara.co.il and the repo root pages); only /mapot/ is bad.
- Wanted: designed-by-a-human feel, very visual, mobile-first/responsive, a real product-catalog feel like the reference rental sites, filters, product pages, «הוסף להזמנה», cart, order form -> email only.
- For now: catalog + orders, NO stock shown, but infrastructure so it later connects to the «מלאי מפות» app and can show how many can be ordered.
- Design direction: avoid AI tells (generic gradients, glassmorphism, emoji, identical rounded cards with soft shadows, centered-everything hero + 3 feature cards, stock icon sets, purple/blue neon). Prefer editorial typography, asymmetric grid, real rhythm, restrained palette, fine details (hairlines, swatch "fabric" rendering, size-diagram drawings). No emojis, no AI images.

## 2. Reference sites
No URL list of reference sites was found in /workspace (the earlier note says "reference rental sites he sent" in chat only; no file holds them). Agent: search the web yourself for Israeli/international table-linen rental catalogs (Hebrew: השכרת מפות / מפיות / ראנרים) and tell Zvi which you used; ask the parent for Zvi's original links if needed. Available local visual material: `/workspace/mapot-redesign/*.png` (screens of the current redesign, what NOT to repeat), `/workspace/hayaara-mapot-2026-10-14.zip` (3 real warehouse photos: bins, shelves, white linen — storage, not product shots; plus 2 campaign videos), `/workspace/mapot-photos/` (px_* = stock placeholders, real_*.jpg = warehouse shots). Don't use px_* as product images.

## 3. Current state (what exists)
- `mapot-src/`: `build_mapot.py` (generates `/mapot/` from copy), `config.json` (`brand`, `preview:true` -> `<meta robots noindex>` on every page, `base`, `wa`, `phone`), `copy.md` (copy of QA-approved copywriter file `/workspace/copywriter/mapot-site-texts-2026-10-15.md`; build re-copies it from there if present — change `copy` in config to make it self-contained in repo), `mapot.css`, `cart.js` (localStorage cart), `api.js` (worker API, see below), `data/products.json` (NEW, see §5).
- Build: `python3 mapot-src/build_mapot.py` -> writes `mapot/` (15 pages: home, 4 category pages, event pages, halls-catering, faq, service-areas, catalog, product, order) + `mapot/_products.json` (slug -> name map used by the API) + `mapot/_redirects.json`. Product pages today: only `tablecloth-3x3` + one "example" per category.
- Serving: Cloudflare Pages project `hayahara-site`, advanced mode `_worker.js`, all files embedded in the worker as base64. `tools/build_worker.py` (production) and `tools/build_worker_preview.py` (preview, branch `mapot-preview`; run from /workspace with repo at ./hayahara-site) build `_worker.js` = `mapot-src/api.js` + PRODUCTS map + static file map + 301 map. The worker routes `/mapot/api/*` to `mapotApi`. Deploys go through a Cloudflare API snippet (`cfp_deploy_preview.js`) that needs credentials: **the cloud agent has none and must not deploy**; it builds and tests locally (e.g. `wrangler`-less: static server + stub API) and the parent deploys the preview.
- Preview URL (parent deploys): https://mapot-preview.hayahara-site.pages.dev/mapot/
- API (`api.js`): `POST /mapot/api/order` JSON {business, contact, phone, email, event_date, address, notes, items:[{slug,qty}], website(honeypot)}. Validation (name, IL phone regex, date, address, items must exist in PRODUCTS, qty 1..10000), honeypot -> silent ok, rate limit 5/hour/IP via Cache API (hashed IP), D1 `orders` best-effort silent backup (binding `DB`), email through service binding `MAILER` (worker `mapot-mailer`, `POST https://mailer/send` {subject,text,from_name,reply_to}); notes starting with `TEST` get subject prefix `[TEST]`. Mailer already sends Hebrew minimal HTML (`<div dir="rtl">`) — do not change mail format. **KEEP all of this.** Admin page/API already removed — don't re-add.
- Changing product slugs/SKUs requires regenerating `_products.json` from `products.json` (do this in the build) so the API accepts them.

## 4. Content rules (hard)
- Texts: use `/workspace/copywriter/mapot-site-texts-2026-10-15.md` (QA-approved; mirrored in `mapot-src/copy.md`). New UI strings must follow the same rules and be reviewed by the parent.
- Positive wording only (say what the business does; no «אנחנו לא…»). 
- NO chair-cover colors anywhere (text, filters, swatches, JSON-LD, alt text, data).
- Nothing about what happens after the event (laundering/return cycle/next round).
- Tablecloth size «3×3» may appear; «סט נקי ומגוהץ» allowed.
- No AI-generated images, no emojis, no hotel/client names, no invented numbers/claims/prices/years/ratings/reviews.
- No «מלאי» word anywhere visible to customers. No stock numbers.
- Items: ONLY tablecloths, napkins, runners, chair covers. No bedding/towels.
- Placeholders in copy `[ממתין לצבי]` must never render as garbage; render gracefully (hide the field or show neutral text).

## 5. Data layer — single source: `mapot-src/data/products.json`
Exported 15.10 (read-only) from the «מלאי מפות» app (see §6). Contents: materials (satin סאטן, linen פשתן; floral פרחים exists in the app but Zvi listed only linen/satin -> `published:false`), tablecloth sizes 1.5×1.5, 1.5×3, 2.2×2.2, 3×3 (+ "עגולה", no diameter, unpublished pending Zvi), napkins in satin/linen (no size), runner (no material/size), chair covers (no material/size/colors). 15 product rows with SKU, `published`, `price:null`, `min_qty:null`, `photos:[]`, `inventory:{tracked:false,qty_total:null,qty_available:null}`.
- **Colors:** the app has none really (only «שמנת» created in the DB; and the app's chair-cover allowed list must be ignored for the site). `products.json` has 10 TEMPORARY colors (`placeholder:true`: לבן, שמנת, שמפניה, זהב, אפור בהיר, אפור פחם, שחור, כחול נייבי, ירוק מרווה, בורדו) assigned to tablecloths/napkins/runners only; `colors:[]` for chair covers. Hex values are rendered swatches only. These MUST be easily replaceable and must not appear in JSON-LD/SEO text as facts while `placeholder:true` (use a build flag `SHOW_PLACEHOLDER_COLORS`, default true in preview, false for go-live unless Zvi confirms).
- Build should expand products x colors into variants (or a color selector on the product page); product page per SKU family is fine (`/mapot/catalog/<slug>/`), with color/size chosen on the page. Cart line = sku + color + qty. API must accept sku+color (extend validation from products.json) and include them in the email.
- Missing price -> «לקבלת הצעת מחיר»; missing min_qty/delivery time -> omit silently.
- Photos: slot by file name `mapot-src/photos/<sku>.jpg` (+ `<sku>-2.jpg`…). If missing, render the designed placeholder (below). Build picks them up automatically; document in README.
- **Inventory provider interface** (hidden from UI now): `GET /mapot/api/availability?sku=&color=&from=YYYY-MM-DD&to=YYYY-MM-DD` -> `{"sku":"…","available":<int|null>}`; `null` = not tracked -> UI shows nothing. Implement `inventory` provider abstraction in `api.js`: `provider = env.INVENTORY_URL ? remoteProvider : nullProvider` (remote = fetch to the inventory service with a bearer in `env.INVENTORY_TOKEN`; not configured now). Add a feature flag `SHOW_AVAILABILITY` (false). Later UI idea: show "ניתן להזמין עד N" and cap the quantity field. Never expose raw totals.
- Do NOT enable any of it now; build + test the null provider path only.

## 6. «מלאי מפות» app (what I found)
- Next.js app running locally on Zvi's PC (`Documents\tablecloth-inventory`, started with start.bat; backups via backup.bat into `backups\<timestamp>`, last: 14.10 13:54). Spec on the box: `/workspace/tablecloth-inventory/SPEC_HE.md` (+ sql/), source snapshot zip in `/workspace/cloud-agent-artifacts/*/tablecloth-inventory-local.zip`.
- Storage: **PGlite** (embedded Postgres) in `data\pglite` — local only, no cloud, no public API. Tables incl. materials, product_types, sizes, colors, items, stock_balances, stock_movements, orders, order_lines, customers, laundry_*. Today the `items` table is EMPTY (no stock rows entered yet), colors has just «שמנת».
- Availability by date exists in the spec as "שלב 2" (unknown whether built). There is NO HTTP API or export for external sync today. Options for later (not decided): (a) a scheduled export of a read-only `availability.json` pushed to Cloudflare KV/D1 and read by the worker; (b) expose a small read-only endpoint from the app via tunnel. Unknown: whether the PC is always on; auth needs. Recommend (a). Say "unknown" in README rather than guessing.

## 7. Technical constraints
- Static build (Python) + Cloudflare Pages worker, free tier (worker bundle size matters: embedded base64 files — keep images optimized, WebP/AVIF, total small; consider moving large assets out of the worker if limit is approached).
- RTL Hebrew, `lang="he"`. Fonts: self-host (woff2 subset, `font-display:swap`, preload critical); no third-party requests. (Current design uses Frank Ruhl Libre/Heebo — verify how they're loaded.)
- Performance: LCP < 2.5s on mobile 4G, CLS ~0, minimal JS (cart + filters vanilla), no framework required. Accessibility: WCAG AA contrast, keyboard operable filters/cart, visible focus, labels, aria-live for cart count, reduced-motion. Site has an accessibility statement page (`/accessibility.html`) — keep consistent, link it in footer.
- Mobile-first: sticky «הוסף להזמנה»/cart bar, filter drawer on mobile, touch targets >= 44px.
- noindex in preview via `config.json preview:true`; at go-live flipping that flag also switches robots/sitemap/canonical behaviour. The agent must keep it `true`.
- No real photos exist. Designed placeholders that do not look fake: render in code (SVG/CSS) a fabric swatch per product — woven linen texture (SVG feTurbulence/pattern) vs satin sheen, in the chosen color, top-down table drawing with correct proportions of the size (1.5×1.5 square, 1.5×3 rectangle, 2.2×2.2, 3×3, round), napkin fold, runner stripe, chair cover silhouette (no colors for chair covers: neutral drawing). Keep it understated/technical-drawing like, with a discreet caption, never a "photo coming soon" box.

## 8. SEO + GEO (AI search) — required
- Unique Hebrew `<title>` (<=60 chars) and meta description (~150) per page; clean URLs: `/mapot/tablecloths/`, `/mapot/napkins/`, `/mapot/runners/`, `/mapot/chair-covers/`, `/mapot/catalog/<slug>/`, event & area pages (exist). One H1 per page, logical headings.
- JSON-LD per page: LocalBusiness (org = מכבסת היערה, alternateName/brand «היערה אירועים»), BreadcrumbList, ItemList on catalog/category pages, Product (+ Offer only when a real price exists; otherwise no Offer, no aggregateRating, no reviews) on product pages, FAQPage on FAQ and product pages that have FAQ. Validate JSON syntax in a test.
- Canonical on each page; sitemap.xml and robots.txt for /mapot/ (preview: noindex + sitemap not advertised; go-live flag generates them correctly; don't edit the root sitemap on main from this branch — provide a snippet in README). No hreflang.
- `llms.txt` for /mapot/ (what the service is, categories, contact, areas, how to order) — facts only.
- FAQ answers short, self-contained, quotable (1–3 sentences), from the approved copy only; no invented numbers.
- Internal linking: add a link block from main HaYaara pages (home, rental/linen service pages) to /mapot/ — deliver as a separate small commit/list in README (main pages are production; don't alter on this branch beyond the preview).
- Image alt texts descriptive, no keyword stuffing; fast CWV as above.
- Target queries: השכרת מפות, השכרת מפות לאירועים, השכרת מפיות וראנרים, השכרת כיסויי כיסאות; geo: ירושלים, בית שמש, מרכז. Use them naturally in titles/H1/intro, areas page.
- No invented claims: no "הכי זול", years, counts, ratings, client names.

## 9. Deliverables (Definition of done)
1. `python3 mapot-src/build_mapot.py` works from a clean checkout (no dependence on /workspace paths: copy file self-contained), generates all pages from `products.json`.
2. Preview-deploy compatible (worker builds via `tools/build_worker_preview.py`; bundle builds without errors).
3. Screenshots desktop (1440) + mobile (390): home, catalog with filters, product, cart, order — committed under `docs/screens/`.
4. Tests: static checks (no forbidden words: מלאי, «אנחנו לא», chair-cover colors, emojis, [ממתין לצבי] leaks; JSON-LD parse; links), and an order-flow test against the preview URL with notes starting `TEST` (parent will run/deploy; script provided `tests/order_test.py`, honoring the rate limit 5/hour).
5. README `mapot-src/README.md`: how to add photos, set prices, sizes, colors, min qty, how to turn on availability later, how to go live (flag list).
6. PR against `mapot-preview`.
Out of scope: production deploy, DNS, main branch, editing live pages, sending emails.
