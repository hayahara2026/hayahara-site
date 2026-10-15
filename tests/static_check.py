#!/usr/bin/env python3
"""Static checks for the generated /mapot/ site. Run after build_mapot.py."""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mapot-src"))
import atmosphere  # noqa: E402
import media_slot  # noqa: E402
SITE = ROOT / "mapot"
SRC = json.loads((ROOT / "mapot-src" / "data" / "products.json").read_text(encoding="utf-8"))
CFG = json.loads((ROOT / "mapot-src" / "config.json").read_text(encoding="utf-8"))

COLOR_NAMES = ["לבן", "שמנת", "שמפניה", "זהב", "אפור בהיר", "אפור פחם", "שחור", "כחול נייבי", "ירוק מרווה", "בורדו"]
COLOR_HEX = [c["hex"].lower() for c in SRC["colors"]]
FORBIDDEN = re.compile(r"מלאי|אנחנו לא|\[ממתין לצבי\]|תמונה תתווסף|photo coming soon", re.I)
EMOJI = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]")
fail = []


def bad(msg):
    fail.append(msg)


if CFG.get("preview") is not True:
    bad("config preview must stay true")
if CFG.get("show_availability") not in (False, None):
    bad("show_availability must stay false until the inventory sync exists")

htmls = sorted(SITE.rglob("*.html"))
if len(htmls) < 20:
    bad(f"too few pages: {len(htmls)}")

public_text = []
for path in SITE.rglob("*"):
    if not path.is_file() or path.name.startswith("_"):
        continue
    if path.suffix.lower() not in {".html", ".css", ".js", ".txt", ".xml"}:
        continue
    public_text.append((path, path.read_text(encoding="utf-8")))

for path, text in public_text:
    if FORBIDDEN.search(text):
        bad(f"forbidden wording in {path.relative_to(ROOT)}")
    if EMOJI.search(text):
        bad(f"emoji in {path.relative_to(ROOT)}")
    if "fonts.googleapis.com" in text or "fonts.gstatic.com" in text:
        bad(f"third-party font request in {path.relative_to(ROOT)}")

for path in htmls:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(SITE)
    title = re.search(r"<title>(.*?)</title>", text)
    if not title:
        bad(f"missing title {rel}")
    elif len(title.group(1)) > 60:
        bad(f"title {len(title.group(1))}>60 {rel}: {title.group(1)}")
    if text.count("<h1") != 1:
        bad(f"h1 count {text.count('<h1')} {rel}")
    if 'name="robots" content="noindex"' not in text:
        bad(f"missing noindex {rel}")
    if 'rel="canonical"' not in text:
        bad(f"missing canonical {rel}")
    if 'lang="he"' not in text or 'dir="rtl"' not in text:
        bad(f"missing he/rtl {rel}")
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', text)
    if not blocks:
        bad(f"missing json-ld {rel}")
    for block in blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError as e:
            bad(f"json-ld {rel}: {e}")
            continue
        blob = json.dumps(data, ensure_ascii=False)
        for hx in COLOR_HEX:
            if hx in blob.lower():
                bad(f"placeholder color hex in json-ld {rel}")
        for node in data.get("@graph", []):
            if node.get("@type") == "Product":
                if "offers" in node or "aggregateRating" in node or "review" in node:
                    bad(f"product schema has offer/rating {rel}")
                for name in COLOR_NAMES:
                    if name in json.dumps(node, ensure_ascii=False):
                        bad(f"placeholder color name in product schema {rel}: {name}")
    urls = []
    for href in re.findall(r'(?:href|src)="(/mapot/[^"]*)"', text):
        urls.append(href)
    for srcset in re.findall(r'srcset="([^"]*)"', text):
        for part in srcset.split(","):
            url = part.strip().split()[0] if part.strip() else ""
            if url.startswith("/mapot/"):
                urls.append(url)
    for href in urls:
        target = href.split("#")[0].split("?")[0]
        if target.endswith("/"):
            fp = SITE / target[len("/mapot/"):] / "index.html"
        else:
            fp = SITE / target[len("/mapot/"):]
        if not fp.is_file():
            bad(f"broken {href} from {rel}")

chair_pages = [
    SITE / "chair-covers" / "index.html",
    SITE / "catalog" / "cc-std" / "index.html",
]
for path in chair_pages:
    text = path.read_text(encoding="utf-8")
    for name in COLOR_NAMES:
        if name in text:
            bad(f"color name on chair page {path.name}: {name}")
    low = text.lower()
    for hx in COLOR_HEX:
        if hx in low:
            bad(f"color hex on chair page {path.name}: {hx}")
    if "צבע" in text:
        bad(f"color word on chair page {path.name}")

products = json.loads((SITE / "_products.json").read_text(encoding="utf-8"))
published = [p for p in SRC["products"] if p.get("published")]
if len(published) != 15:
    bad(f"expected 15 published products, got {len(published)}")
if set(products) != {p["sku"] for p in published}:
    bad(" _products.json sku set does not match published products")
for sku in ("TC-LINEN-ROUND", "TC-SATIN-ROUND", "TC-FLORAL-*"):
    if sku not in products:
        bad(f"missing published sku {sku}")
if products.get("CC-STD", {}).get("colors"):
    bad("chair cover must have no colors in the API map")
for sku, row in products.items():
    if sku == "CC-STD":
        continue
    if not row.get("colors"):
        bad(f"expected colors on {sku} while show_placeholder_colors is on")

sm = (SITE / "sitemap.xml").read_text(encoding="utf-8")
if "/mapot/order/" in sm:
    bad("order page is in the sitemap")
if "tc-floral" not in sm or "tc-linen-round" not in sm or "tc-satin-round" not in sm:
    bad("sitemap missing a newly published product")
robots = (SITE / "robots.txt").read_text(encoding="utf-8")
if CFG["preview"] and "Disallow: /mapot/" not in robots:
    bad("preview robots should not advertise the catalog")
if CFG["preview"] and "Sitemap:" in robots:
    bad("preview robots advertises a sitemap")
llms = (SITE / "llms.txt").read_text(encoding="utf-8")
for needle in (CFG["phone"], CFG["email"], "עוטף ירושלים", "לקבלת הצעת מחיר"):
    if needle not in llms:
        bad(f"llms.txt missing {needle}")
if any(hx in llms.lower() for hx in COLOR_HEX):
    bad("llms.txt lists placeholder color hex")

home = (SITE / "index.html").read_text(encoding="utf-8")
if 'data-avail="1"' in home:
    bad("availability UI flag is on")
if "id=\"availnote\"" in (SITE / "catalog" / "tc-linen-3x3" / "index.html").read_text(encoding="utf-8"):
    bad("availability note is rendered while the flag is off")

for path, text in public_text:
    if "שרטוט" in text:
        bad(f"drawing caption still in {path.relative_to(ROOT)}")
    if "Website" in text:
        bad(f"English honeypot label in {path.relative_to(ROOT)}")

order = (SITE / "order" / "index.html").read_text(encoding="utf-8")
if 'type="date"' not in order or 'id="f-event_date"' not in order:
    bad("order date is not a single date field")
if 'id="f-day"' in order or 'id="f-month"' in order or 'id="f-year"' in order:
    bad("order date is still three selects")
if "ינואר" not in order or "דצמבר" not in order:
    bad("Hebrew month names missing from the order page")
if 'name="website"' not in order:
    bad("honeypot field name missing")
if 'class="badge"' not in home or 'class="sep"' not in (SITE / "catalog" / "index.html").read_text(encoding="utf-8"):
    bad("cart badge or breadcrumb separator missing")
if "<br>" not in re.search(r"<h1[^>]*>.*?</h1>", home, re.S).group(0):
    bad("home h1 has no designed line break")
catalog = (SITE / "catalog" / "index.html").read_text(encoding="utf-8")
if 'class="plate"' in catalog or "item-wide" in catalog:
    bad("catalog still uses the shared plate or uneven card spans")
linen = (SITE / "catalog" / "tc-linen-3x3" / "index.html").read_text(encoding="utf-8")
if linen.count('data-view=') < 4:
    bad("product gallery is missing views")
if 'id="zoom"' not in linen:
    bad("product gallery has no zoom control")
if 'class="swatch-name"' not in linen or "בורדו" not in linen:
    bad("color swatch is missing a visible name")
if 'id="adddock"' in linen or linen.count('id="add"') != 1:
    bad("product page does not have a single add button")
if "btn#add{display:none}" in (SITE / "assets" / "mapot.css").read_text(encoding="utf-8").replace(" ", ""):
    bad("add button is hidden from the accessibility tree")
round_html = (SITE / "catalog" / "tc-satin-round" / "index.html").read_text(encoding="utf-8")
if 'rx="246"' not in round_html or 'r="300"' in round_html:
    bad("round cloth is still a circle in a square")
floral_html = (SITE / "catalog" / "tc-floral" / "index.html").read_text(encoding="utf-8")
if "<pattern" not in floral_html:
    bad("floral cloth is missing a print pattern")
if 'id="navclose"' not in home or 'id="navbrand"' not in home or 'class="nav-scrim"' not in home:
    bad("mobile menu is missing a close control or wordmark")
if "סגירה" not in home:
    bad("mobile menu close control has no visible label")
if "M70 250" in catalog or "L748 830" not in catalog:
    bad("square cloth still reads as a blotch")

photos_present = bool(media_slot.list_files(str(ROOT / "mapot-src" / "photos")))
range_present = bool(media_slot.range_files(str(ROOT / "mapot-src" / "range")))
atmo_ready = atmosphere.plan(str(ROOT / "mapot-src" / "atmosphere"))
if not range_present:
    for path, text in public_text:
        if "/mapot/media/range/" in text or 'class="range"' in text:
            bad(f"empty warehouse slot rendered in {path.relative_to(ROOT)}")
if not photos_present and not range_present:
    for path in htmls:
        text = path.read_text(encoding="utf-8")
        if "<video" in text:
            bad(f"video while the product and warehouse slots are empty: {path.relative_to(ROOT)}")
        for tag in re.findall(r"<img\b[^>]*>", text):
            if "/mapot/media/atmosphere/" not in tag:
                bad(f"non-atmosphere image while product slots are empty: {path.relative_to(ROOT)}")
for path in htmls:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT)
    if 'class="media-frame"' in text:
        bad(f"photo frame on a card: {rel}")
    for card in re.findall(r'class="(?:item|tile)"[^>]*>.*?</a>', text, re.S):
        if "<img" in card or "<video" in card or "/mapot/media/atmosphere/" in card:
            bad(f"atmosphere or product photo on a card: {rel}")
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        for node in data.get("@graph", []):
            if node.get("@type") == "Product" and "atmosphere" in json.dumps(node):
                bad(f"atmosphere photo filed as a product image: {rel}")
if "hero" in atmo_ready:
    if "hero-stage has-photo" not in home or "image/avif" not in home or "image/webp" not in home:
        bad("home hero is missing the responsive atmosphere picture")
    if atmo_ready["hero"]["alt"] not in home:
        bad("home hero alt text missing")
    if "hero-narrow-" not in home or "hero-wide-" not in home:
        bad("home hero is missing the mobile or desktop crop")
else:
    if "/mapot/media/atmosphere/hero-" in home:
        bad("hero picture rendered without a source file")
for slug, slot in atmosphere.HEADERS.items():
    page = (SITE / slug / "index.html").read_text(encoding="utf-8")
    if slot in atmo_ready:
        if "page-plate has-photo" not in page or f"{slot}-narrow-" not in page:
            bad(f"{slug} header did not receive {slot}")
    elif "/mapot/media/atmosphere/" in page:
        bad(f"{slug} shows an atmosphere photo that is not on disk")
chair_html = (SITE / "chair-covers" / "index.html").read_text(encoding="utf-8")
if "/mapot/media/atmosphere/" in chair_html:
    bad("chair-cover category uses an atmosphere photo")
product_html = (SITE / "catalog" / "tc-linen-3x3" / "index.html").read_text(encoding="utf-8")
if "/mapot/media/atmosphere/" in product_html:
    bad("product page is using an atmosphere photo")
if not photos_present and "<img" in product_html:
    bad("product page is using a photo while the product slot is empty")

if fail:
    print("\n".join(fail))
    sys.exit(1)
print(f"static ok: {len(htmls)} pages, {len(products)} skus")
