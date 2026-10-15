#!/usr/bin/env python3
# Builds /mapot/ from mapot-src/copy.md + mapot-src/data/products.json.
# Self-contained: no path outside this repo.
import html as H
import json, os, re, shutil, sys
import atmosphere
import media_slot
import plates

R = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(R)
C = json.load(open(os.path.join(R, "config.json"), encoding="utf-8"))
B = C["brand"]
BASE = C["base"].rstrip("/") + "/"
ORIGIN = C["origin"].rstrip("/")
WA = C["wa"]
PH = C["phone"]
EMAIL = C["email"]
SHOW_COLORS = bool(C.get("show_placeholder_colors", True))
SHOW_AVAIL = bool(C.get("show_availability", False))
PREVIEW = bool(C.get("preview", True))

copy_rel = C.get("copy", "copy.md")
copy_path = copy_rel if os.path.isabs(copy_rel) else os.path.join(R, copy_rel)
if not os.path.isfile(copy_path):
    sys.exit("copy file missing: " + copy_path)
md = open(copy_path, encoding="utf-8").read().replace("{BRAND}", B)

OUT = os.path.join(ROOT, "mapot")

DATA = json.load(open(os.path.join(R, "data", "products.json"), encoding="utf-8"))
COLORS = {c["key"]: c for c in DATA["colors"]}
MATS = {m["code"]: m for m in DATA["materials"]}
MAT_PHRASE = {"satin": "מסאטן", "linen": "מפשתן", "floral": "מבד פרחים"}
TYPE_ORDER = ["tablecloth", "napkin", "runner", "chair_cover"]
SIZE_ORDER = ["1.5×1.5", "1.5×3", "2.2×2.2", "3×3", "עגולה"]
FAB_ORDER = ["satin", "linen", "floral"]
CATS = [
    ("tablecloths", "tablecloth", "מפות", "מפה"),
    ("napkins", "napkin", "מפיות", "מפית"),
    ("runners", "runner", "ראנרים", "ראנר"),
    ("chair-covers", "chair_cover", "כיסויי כיסאות", "כיסוי כיסא"),
]
CAT_BY_TYPE = {t: (slug, name) for slug, t, name, _ in CATS}
NAV = [
    ("/mapot/catalog/", "קטלוג"),
    ("/mapot/tablecloths/", "מפות"),
    ("/mapot/napkins/", "מפיות"),
    ("/mapot/runners/", "ראנרים"),
    ("/mapot/chair-covers/", "כיסויי כיסאות"),
    ("/mapot/halls-catering/", "אולמות"),
    ("/mapot/service-areas/", "אזורים"),
    ("/mapot/faq/", "שאלות"),
]
EVENTS = [
    ("/mapot/wedding/", "חתונה"),
    ("/mapot/bar-mitzvah/", "בר מצווה"),
    ("/mapot/brit/", "ברית"),
    ("/mapot/sheva-brachot/", "שבע ברכות"),
    ("/mapot/halls-catering/", "אולמות וקייטרינג"),
]
FAQ_FIX = {
    "באילו מידות יש מפות?": "מפות במידות 1.5×1.5, 1.5×3, 2.2×2.2 ו־3×3, וגם מפה עגולה.",
    "כמה זה עולה?": "לקבלת הצעת מחיר, לפי הפריטים והכמות.",
}
ORG_ID = ORIGIN + "/#business"


def esc(s):
    return H.escape("" if s is None else str(s), quote=True)


def strip_pending(s):
    if "[ממתין לצבי]" not in s:
        return s.strip()
    parts = re.split(r"(?<=[\.!?])\s+", s)
    kept = [p.strip() for p in parts if p.strip() and "[ממתין לצבי]" not in p]
    return " ".join(kept).strip()


def inl(s):
    s = strip_pending(s)
    if not s:
        return ""
    s = H.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = s.replace(PH, f'<a href="{WA}">{PH}</a>')
    s = s.replace(EMAIL, f'<a href="mailto:{EMAIL}">{EMAIL}</a>')
    return s


def md2html(lines):
    o, ul, tbl = [], False, []

    def end_ul():
        nonlocal ul
        if ul:
            o.append("</ul>")
            ul = False

    def end_tbl():
        nonlocal tbl
        if not tbl:
            return
        header, rows = tbl[0], tbl[1:]
        tbl = []
        if not rows:
            return
        th = "".join(f"<th>{inl(c)}</th>" for c in header)
        body = "".join(
            "<tr>" + "".join(f"<td>{inl(c)}</td>" for c in r) + "</tr>" for r in rows
        )
        o.append(f"<table><tr>{th}</tr>{body}</table>")

    for raw in lines:
        l = raw.rstrip()
        if l.startswith("|"):
            end_ul()
            if re.match(r"^\|[-|\s]+\|$", l):
                continue
            cells = [c.strip() for c in l.strip("|").split("|")]
            if any("[ממתין לצבי]" in c for c in cells):
                continue
            tbl.append(cells)
            continue
        end_tbl()
        if l.startswith("- "):
            item = inl(l[2:])
            if not item:
                continue
            if not ul:
                o.append("<ul>")
                ul = True
            o.append(f"<li>{item}</li>")
            continue
        end_ul()
        if not l or l == "---" or l.startswith("(") or l.startswith("**title") or l.startswith("**meta"):
            continue
        m = re.match(r"^(#{1,3}) (.*)", l)
        if m:
            level = len(m.group(1))
            text = inl(m.group(2))
            if text:
                o.append(f"<h{level}>{text}</h{level}>")
            continue
        text = inl(l)
        if text:
            o.append(f"<p>{text}</p>")
    end_ul()
    end_tbl()
    return "\n".join(o)


def slug_for(sku):
    s = sku.lower().replace("*", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def photo_files(sku, slug):
    """Dressed-table or single-product files in photos/. Top of the folder only."""
    return media_slot.product_files(os.path.join(R, "photos"), sku, slug)


def is_video(name):
    return media_slot.is_video(name)


def public_colors(prod):
    if prod["type"] == "chair_cover" or not prod.get("colors"):
        return []
    out = []
    for key in prod["colors"]:
        col = COLORS.get(key)
        if not col:
            continue
        if col.get("placeholder") and not SHOW_COLORS:
            continue
        out.append(col)
    return out


def mat_name(prod):
    m = MATS.get(prod.get("material") or "")
    return m["name_he"] if m else ""


def price_label(prod):
    if prod.get("price") is None:
        return "לקבלת הצעת מחיר"
    return f'{prod["price"]} ₪'


def blurb(prod):
    phrase = MAT_PHRASE.get(prod.get("material") or "", "")
    size = prod.get("size")
    if prod["type"] == "tablecloth":
        if size == "עגולה":
            head = f"מפה עגולה {phrase}".strip()
        elif size:
            head = f"מפה {phrase} במידה {size}".strip()
        else:
            head = f"מפה {phrase}".strip()
        return head + ". מגיעה נקייה ומגוהצת, מוכנה לפריסה."
    if prod["type"] == "napkin":
        return f"מפית {phrase}. מגיעה נקייה, מוכנה לקיפול, ומשלימה את עריכת השולחן.".replace("  ", " ")
    if prod["type"] == "runner":
        extra = f" בצבע לבחירה" if public_colors(prod) else ""
        return "ראנר לאורך השולחן, שנותן למפה קו עיצובי. מגיע נקי, מוכן לפריסה." if not extra else "ראנר לאורך השולחן, שנותן למפה קו עיצובי. מגיע נקי, מוכן לפריסה."
    return "כיסוי כיסא שנותן לאולם מראה אחיד ומסודר. מגיע נקי, מוכן להלבשה."


def alt_text(prod):
    return prod["name_he"]


# Display color for the code-rendered cloth. Not a catalog fact: every swatch stays available.
ACCENT = {
    "TC-SATIN-15X15": "c10",
    "TC-SATIN-15X3": "c04",
    "TC-SATIN-22X22": "c08",
    "TC-SATIN-3X3": "c03",
    "TC-SATIN-ROUND": "c09",
    "TC-LINEN-15X15": "c02",
    "TC-LINEN-15X3": "c06",
    "TC-LINEN-22X22": "c01",
    "TC-LINEN-3X3": "c10",
    "TC-LINEN-ROUND": "c08",
    "NP-SATIN": "c07",
    "NP-LINEN": "c09",
    "RN-STD": "c08",
    "TC-FLORAL-*": "c03",
}


def accent_of(p):
    cols = p["public_colors"]
    if not cols or p["type"] == "chair_cover":
        return None
    key = ACCENT.get(p["sku"])
    for col in cols:
        if col["key"] == key:
            return col
    return cols[0]


def kind_of(prod):
    return {"tablecloth": "tablecloth", "napkin": "napkin", "runner": "runner", "chair_cover": "chair"}[prod["type"]]


def fabric_code(prod):
    return prod.get("material") or ""


def load_products():
    items = []
    for prod in DATA["products"]:
        if not prod.get("published"):
            continue
        slug = slug_for(prod["sku"])
        files = photo_files(prod["sku"], slug)
        cols = public_colors(prod)
        items.append({**prod, "slug": slug, "files": files, "public_colors": cols})
    def key(p):
        return (
            TYPE_ORDER.index(p["type"]) if p["type"] in TYPE_ORDER else 9,
            FAB_ORDER.index(p["material"]) if p.get("material") in FAB_ORDER else 9,
            SIZE_ORDER.index(p["size"]) if p.get("size") in SIZE_ORDER else 9,
            p["sku"],
        )
    items.sort(key=key)
    slugs = [p["slug"] for p in items]
    if len(slugs) != len(set(slugs)):
        sys.exit("duplicate product slugs")
    return items


PRODUCTS = load_products()
BY_SLUG = {p["slug"]: p for p in PRODUCTS}
BY_SKU = {p["sku"]: p for p in PRODUCTS}
RANGE_FILES = media_slot.range_files(os.path.join(R, "range"))
ATMOS = {}

# copy pages
PAGES = {}
for m in re.finditer(
    r"^#{2,3} [\d.]+ ([^:\n]+): (/mapot/[^\s]*)\n(.*?)(?=^#{2,3} [\d.]+ |^## שאלות פתוחות|\Z)",
    md,
    re.S | re.M,
):
    name, url, body = m.group(1).strip(), m.group(2), m.group(3)
    title = re.search(r"\*\*title:\*\* (.*)", body).group(1).strip()
    desc = re.search(r"\*\*meta description:\*\* (.*)", body).group(1).strip()
    lines = [x for x in body.split("\n") if not x.startswith("**title") and not x.startswith("**meta")]
    PAGES[url] = dict(name=name, title=title, desc=desc, lines=lines)

ORDER = PAGES.pop("/mapot/order/")
ORDER_FIELDS = dict(re.findall(r"\*\*([^*]+):\*\* (.*)", "\n".join(ORDER["lines"])))
FOOT = [strip_pending(l[2:]) for l in md.split("\n") if l.startswith("> ") and strip_pending(l[2:])]

TEMPLATES = {}
for m in re.finditer(r"^### 6\.\d (.+?)\n(.*?)(?=^### |^---)", md, re.S | re.M):
    b = m.group(2)
    TEMPLATES[m.group(1).strip()] = dict(
        pts=[strip_pending(x) for x in re.findall(r"^- (.*)", b, re.M) if strip_pending(x)],
        btn=re.search(r"\*\*כפתור:\*\* (.*)", b).group(1).strip(),
        qty=strip_pending(re.search(r"\*\*הערה לשדה הכמות:\*\* (.*)", b).group(1)),
    )
TKEY = {"tablecloth": "מפה", "napkin": "מפית", "runner": "ראנר", "chair_cover": "כיסוי כיסא"}


def jsonld(obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def org():
    return {
        "@type": "LocalBusiness",
        "@id": ORG_ID,
        "name": C["parent"],
        "legalName": C["legal"],
        "alternateName": B,
        "brand": {"@type": "Brand", "name": B},
        "url": BASE,
        "telephone": C["phone_e164"],
        "email": EMAIL,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": C["street"],
            "addressLocality": C["locality"],
            "addressCountry": "IL",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": 31.794167, "longitude": 35.331778},
        "areaServed": ["השרון", "גוש דן", "עוטף ירושלים", "ים המלח", "גוש עציון"],
    }


def crumbs_ld(crumbs):
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": ORIGIN + u} for i, (n, u) in enumerate(crumbs)]
    return {"@type": "BreadcrumbList", "itemListElement": items}


def item_list(prods):
    return {
        "@type": "ItemList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": p["name_he"],
                "url": ORIGIN + f"/mapot/catalog/{p['slug']}/",
            }
            for i, p in enumerate(prods)
        ],
    }


def product_ld(p):
    node = {
        "@type": "Product",
        "name": p["name_he"],
        "sku": p["sku"],
        "description": blurb(p),
        "category": CAT_BY_TYPE[p["type"]][1],
        "brand": {"@type": "Brand", "name": B},
        "url": ORIGIN + f"/mapot/catalog/{p['slug']}/",
    }
    if mat_name(p):
        node["material"] = mat_name(p)
    if p.get("size"):
        node["size"] = p["size"]
    images = [name for name in p["files"] if not is_video(name)]
    if images:
        node["image"] = ORIGIN + "/mapot/media/" + images[0]
    if isinstance(p.get("price"), (int, float)) and not isinstance(p.get("price"), bool):
        node["offers"] = {"@type": "Offer", "price": p["price"], "priceCurrency": "ILS", "url": node["url"]}
    return node


def faq_ld(pairs):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in pairs
            if a
        ],
    }


def product_faq(p):
    phone = f"בטלפון או בוואטסאפ {PH}, או במייל {EMAIL}"
    if p["type"] == "tablecloth":
        return [
            ("באיזה מצב מגיעה המפה?", "כל מפה מגיעה נקייה ומגוהצת, מוכנה לפריסה."),
            ("איך מזמינים?", f"בוחרים את הפריט ואת הכמות ושולחים בקשת הזמנה. אפשר גם {phone}."),
        ]
    if p["type"] == "napkin":
        return [
            ("באיזה מצב מגיעות המפיות?", "המפיות מגיעות נקיות, מוכנות לקיפול."),
            ("איך מזמינים?", f"בוחרים כמות ושולחים בקשת הזמנה. אפשר גם {phone}."),
        ]
    if p["type"] == "runner":
        return [
            ("באיזה מצב מגיע הראנר?", "הראנר מגיע נקי, מוכן לפריסה."),
            ("איך מזמינים?", f"בוחרים כמות ושולחים בקשת הזמנה. אפשר גם {phone}."),
        ]
    return [
        ("באיזה מצב מגיע הכיסוי?", "הכיסויים מגיעים נקיים, מוכנים להלבשה."),
        ("איך מזמינים?", f"בוחרים כמות ושולחים בקשת הזמנה. אפשר גם {phone}."),
    ]


SITEMAP = []


def shell(url, title, desc, crumbs, body, extra=None, noindex=False, main_class="", dock="", og_image=""):
    if len(title) > 60:
        print("TITLE OVER 60:", len(title), title)
    graph = [org(), crumbs_ld([(B, "/mapot/")] + crumbs)] + (extra or [])
    cr = [(B, "/mapot/")] + crumbs
    crumb_html = ""
    if crumbs:
        bits = []
        for i, (n, u) in enumerate(cr):
            if i:
                bits.append('<span class="sep" aria-hidden="true">/</span>')
            if i == len(cr) - 1:
                bits.append(f"<span>{esc(n)}</span>")
            else:
                bits.append(f'<a href="{u}">{esc(n)}</a>')
        crumb_html = f'<nav class="crumb" aria-label="מיקום">{"".join(bits)}</nav>'
    robots = '<meta name="robots" content="noindex">' if (PREVIEW or noindex) else ""
    canon = ORIGIN + url
    nav = []
    for u, n in NAV:
        cur = ' aria-current="page"' if u == url or (u != "/mapot/catalog/" and url.startswith(u)) else ""
        nav.append(f'<a href="{u}"{cur}>{esc(n)}</a>')
    nav_html = (
        f'<nav class="site-nav" id="sitenav" aria-label="ראשי">'
        f'<button type="button" class="nav-scrim" id="navscrim" tabindex="-1" aria-hidden="true"></button>'
        f'<div class="nav-sheet">'
        f'<div class="nav-head">'
        f'<a class="nav-brand" id="navbrand" href="/mapot/"><b>{esc(B)}</b><small>מבית מכבסת היערה</small></a>'
        f'<button type="button" class="nav-close" id="navclose" aria-label="סגירת התפריט">'
        f'<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false">'
        f'<path d="M5 5 L19 19 M19 5 L5 19" fill="none" stroke="currentColor" stroke-width="2"/>'
        f'</svg><span>סגירה</span></button>'
        f'</div>'
        f'<div class="nav-links">{"".join(nav)}</div>'
        f'</div></nav>'
    )
    avail = "1" if SHOW_AVAIL else "0"
    foot_nav = "".join(f'<a href="{u}">{esc(n)}</a>' for u, n in NAV + EVENTS[:4])
    doc = f"""<!DOCTYPE html>
<html lang="he" dir="rtl" data-avail="{avail}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}
<link rel="canonical" href="{esc(canon)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canon)}">
<meta property="og:locale" content="he_IL">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(B)}">{f'{chr(10)}<meta property="og:image" content="{esc(og_image)}">' if og_image else ""}
<meta name="theme-color" content="#f3efe6">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="preload" href="/mapot/assets/fonts/frank-ruhl-libre.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/mapot/assets/fonts/heebo.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/mapot/assets/mapot.css">
<script type="application/ld+json">{jsonld({"@context": "https://schema.org", "@graph": graph})}</script>
<script src="/mapot/assets/cart.js" defer></script>
</head>
<body class="{'has-dock' if dock else ''}">
<a class="skip" href="#content">לתוכן</a>
<header class="hdr">
<a class="brand" href="/mapot/"><b>{esc(B)}</b><small>מבית מכבסת היערה</small></a>
{nav_html}
<div class="tools">
<a class="cartlink" href="/mapot/order/" aria-label="סל ההזמנה"><span class="cartlabel">הזמנה</span><span id="cartn" class="badge" aria-live="polite">0</span></a>
<button type="button" class="nav-toggle" id="navtoggle" aria-expanded="false" aria-controls="sitenav">תפריט</button>
</div>
</header>
<main id="content" class="{main_class}"><div class="wrap">
{crumb_html}
{body}
</div></main>
<footer class="foot"><div class="foot-in">
<p class="foot-brand">{esc(B)}</p>
<p>{'<br>'.join(esc(x) for x in FOOT)}</p>
<p>{esc(C['street'])}, {esc(C['locality'])}<br>
טלפון ווואטסאפ: <a href="{WA}">{PH}</a><br>
<a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p><a href="{ORIGIN}/">מכבסת היערה</a></p>
<nav class="foot-nav" aria-label="תחתית">{foot_nav}</nav>
<p class="legal">{esc(C['legal'])} · <a href="{ORIGIN}/accessibility.html">הצהרת נגישות</a> · <a href="{ORIGIN}/privacy.html">פרטיות</a></p>
</div></footer>
{dock}
</body></html>
"""
    path = url[len("/mapot/"):]
    d = os.path.join(OUT, path)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(doc)
    if not noindex or PREVIEW:
        if url != "/mapot/order/":
            SITEMAP.append(url)


def cloth_style(p, dyed=True):
    if not dyed or p["type"] == "chair_cover":
        return ""
    col = accent_of(p)
    if not col:
        return ""
    return f' style="--cloth:{esc(col["hex"])}"'


def media_tag(name, alt, autoplay=True):
    src = f"/mapot/media/{esc(name)}"
    if is_video(name):
        play = " muted loop playsinline" + (" autoplay" if autoplay else "")
        label = f' aria-label="{esc(alt)}"' if alt else ""
        return f'<video src="{src}"{play}{label}></video>'
    alt_attr = f' alt="{esc(alt)}"' if alt else ' alt=""'
    return f'<img src="{src}"{alt_attr}>'


def plate_for(p, uid, dyed=True, mode="card"):
    # Cards, the hero, category plates, and related cards stay drawn scenes,
    # even when a product file exists. Warehouse shots never reach this path.
    kind = kind_of(p)
    fab = fabric_code(p) or None
    size = p.get("size")
    view = "hero" if mode == "hero" else plates.card_view(kind, fab, size)
    svg = plates.render_view(kind, fab, size, uid, view)
    cls = "scene heroimg" if mode == "hero" else "scene"
    return f'<div class="{cls}"{cloth_style(p, dyed)} aria-hidden="true">{svg}</div>'


def gallery_for(p, uid):
    dyed = p["type"] != "chair_cover"
    files = media_slot.files_for_surface("gallery", p["files"])
    if files:
        views = []
        for i, name in enumerate(files):
            label = f"סרטון {i+1}" if is_video(name) else f"תמונה {i+1}"
            main = media_tag(name, alt_text(p) if i == 0 else "", autoplay=(i == 0))
            thumb = media_tag(name, "", autoplay=False)
            views.append((str(i), label, main, thumb))
    else:
        kind = kind_of(p)
        fab = fabric_code(p) or None
        size = p.get("size")
        views = []
        for key, label in plates.views_for(kind, fab, size):
            svg = plates.render_view(kind, fab, size, uid + key, key)
            thumb = plates.render_view(kind, fab, size, uid + key + "t", key)
            views.append((key, label, svg, thumb))
    mains, thumbs = [], []
    for i, (key, label, inner, thumb) in enumerate(views):
        hidden = "" if i == 0 else " hidden"
        on = " is-on" if i == 0 else ""
        mains.append(f'<div class="g-view{on}" data-view="{esc(key)}"{hidden}>{inner}</div>')
        thumbs.append(
            f'<button type="button" role="tab" data-go="{esc(key)}" aria-selected="{"true" if i==0 else "false"}">'
            f'<span class="mini" aria-hidden="true">{thumb}</span><span>{esc(label)}</span></button>'
        )
    tabs = ""
    if len(views) > 1:
        tabs = f'<div class="g-thumbs" role="tablist" aria-label="מבטים">{"".join(thumbs)}</div>'
    return (
        f'<div class="gallery" id="stage"{cloth_style(p, dyed)}>'
        f'<div class="gallery-main">{"".join(mains)}'
        f'<button type="button" class="zoom" id="zoom" aria-pressed="false">הגדלה</button></div>'
        f"{tabs}</div>"
    )


def card(p, cls=""):
    cat = CAT_BY_TYPE[p["type"]][0]
    colors = " ".join(c["key"] for c in p["public_colors"])
    klass = "item" + ((" " + cls) if cls else "")
    return (
        f'<a class="{klass}" href="/mapot/catalog/{p["slug"]}/" data-type="{cat}" '
        f'data-size="{esc(p.get("size") or "")}" data-fabric="{esc(fabric_code(p))}" data-colors="{esc(colors)}">'
        f'{plate_for(p, "card"+p["sku"])}'
        f'<strong>{esc(p["name_he"])}</strong>'
        f'<span class="price">{esc(price_label(p))}</span>'
        f"</a>"
    )


def grid(prods):
    return f'<div class="catalog-grid" id="grid">{"".join(card(p) for p in prods)}</div>'


def filter_bar(prods, lock=""):
    sizes, fabs = [], []
    for p in prods:
        if p.get("size") and p["size"] not in sizes:
            sizes.append(p["size"])
        if p.get("material") and p["material"] not in fabs:
            fabs.append(p["material"])
    sizes.sort(key=lambda s: SIZE_ORDER.index(s) if s in SIZE_ORDER else 99)
    fabs.sort(key=lambda s: FAB_ORDER.index(s) if s in FAB_ORDER else 99)
    show_colors = SHOW_COLORS and lock != "chair-covers" and any(p["public_colors"] for p in prods)
    parts = ['<div id="filterpanel"><button type="button" class="btn-ghost btn" id="closef">סגירה</button>']
    if not lock:
        parts.append('<fieldset><legend>סוג</legend><div class="choices">')
        parts.append('<button type="button" class="choice" data-filter="type" data-value="" aria-pressed="true">הכול</button>')
        for slug, _t, name, _s in CATS:
            parts.append(
                f'<button type="button" class="choice" data-filter="type" data-value="{slug}" aria-pressed="false">{esc(name)}</button>'
            )
        parts.append("</div></fieldset>")
    if sizes:
        parts.append('<fieldset><legend>מידה</legend><div class="choices">')
        parts.append('<button type="button" class="choice" data-filter="size" data-value="" aria-pressed="true">הכול</button>')
        for s in sizes:
            parts.append(
                f'<button type="button" class="choice" data-filter="size" data-value="{esc(s)}" aria-pressed="false">{esc(s)}</button>'
            )
        parts.append("</div></fieldset>")
    if fabs and lock != "chair-covers":
        parts.append('<fieldset><legend>בד</legend><div class="choices">')
        parts.append('<button type="button" class="choice" data-filter="fabric" data-value="" aria-pressed="true">הכול</button>')
        for code in fabs:
            parts.append(
                f'<button type="button" class="choice" data-filter="fabric" data-value="{esc(code)}" aria-pressed="false">{esc(MATS[code]["name_he"])}</button>'
            )
        parts.append("</div></fieldset>")
    if show_colors:
        parts.append('<fieldset><legend>צבע</legend><div class="swatches">')
        parts.append('<button type="button" class="choice" data-filter="color" data-value="" aria-pressed="true">הכול</button>')
        for key, col in COLORS.items():
            if col.get("placeholder") and not SHOW_COLORS:
                continue
            if not any(key in [c["key"] for c in p["public_colors"]] for p in prods):
                continue
            parts.append(
                f'<button type="button" class="swatch" data-filter="color" data-value="{esc(key)}" aria-pressed="false" '
                f'title="{esc(col["name"])}" aria-label="{esc(col["name"])}" style="--sw:{esc(col["hex"])}">'
                f'<span class="swatch-chip" aria-hidden="true"></span><span class="swatch-name">{esc(col["name"])}</span></button>'
            )
        parts.append("</div></fieldset>")
    parts.append("</div>")
    return (
        f'<div class="layout"><div id="filters" data-lock="{esc(lock)}">{"".join(parts)}</div><div>'
    )


def close_layout():
    return (
        '<p id="emptyf" hidden>לבחירה הזו אין פריטים בקטלוג. '
        '<button type="button" id="resetf">איפוס הסינון</button></p></div></div>'
    )


def split_head(html):
    html = re.sub(r"^<h1>.*?</h1>\n?", "", html, count=1)
    m = re.match(r"<p>(.*?)</p>\n?", html, re.S)
    if not m:
        return "", html
    return m.group(1), html[m.end():]


def size_table():
    rows = [
        ("1.5×1.5", "מרובעת"),
        ("1.5×3", "מלבנית"),
        ("2.2×2.2", "מרובעת"),
        ("3×3", "מרובעת"),
        ("עגולה", "עגולה"),
    ]
    body = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in rows)
    return (
        '<table class="sizes"><caption>מידות מפות להשכרה</caption>'
        f"<thead><tr><th>מידה</th><th>צורה</th></tr></thead><tbody>{body}</tbody></table>"
    )


def first_paragraph_and_rest(url):
    html = md2html(PAGES[url]["lines"])
    if url == "/mapot/tablecloths/":
        html = html.replace("<h2>מידות מפות להשכרה</h2>", "<h2>מידות מפות להשכרה</h2>\n" + size_table(), 1)
    return split_head(html)


def range_section(files=None):
    """Home shelf rail. Omitted when mapot-src/range/ has no media."""
    files = RANGE_FILES if files is None else files
    if not files:
        return ""
    bits = []
    for name in files:
        src = f"/mapot/media/range/{esc(name)}"
        if is_video(name):
            inner = (
                f'<video src="{src}" muted loop playsinline controls preload="metadata" '
                f'aria-label="סרטון מהמחסן"></video>'
            )
        else:
            inner = f'<img src="{src}" alt="מפות ארוזות במחסן">'
        bits.append(f'<figure class="range-item">{inner}</figure>')
    return (
        '<section class="range" aria-labelledby="range-h">'
        '<p class="kicker">המחסן</p>'
        '<h2 id="range-h">צבעים על המדף</h2>'
        "<p>במחסן המפות ארוזות בשקיות על המדף, ועל המדף שלטי מידה של 3×3 ושל 1.5×3.</p>"
        f'<div class="range-rail">{"".join(bits)}</div>'
        "</section>"
    )


def atmo_picture(slot_id, kind, sizes, priority=False):
    return atmosphere.picture(ATMOS, slot_id, kind=kind, sizes=sizes, priority=priority)


def hall_band():
    figures = []
    for slot_id in atmosphere.BAND:
        pic = atmo_picture(slot_id, "band", "(min-width: 900px) 34vw, 80vw")
        if not pic:
            continue
        caption = ATMOS[slot_id].get("caption") or ""
        figures.append(f"<figure>{pic}<figcaption>{esc(caption)}</figcaption></figure>")
    if not figures:
        return ""
    return (
        '<section class="atmo-band" aria-labelledby="atmo-h">'
        '<p class="kicker">אווירה</p>'
        '<h2 id="atmo-h">אולמות ערוכים</h2>'
        "<p>צילומי אווירה של שולחנות ערוכים לאירוע.</p>"
        f'<div class="atmo-rail">{"".join(figures)}</div>'
        "</section>"
    )


def head_plate(slug, fallback):
    slot_id = atmosphere.HEADERS.get(slug)
    pic = atmo_picture(slot_id, "header", "(min-width: 960px) 42vw, 100vw") if slot_id else ""
    if pic:
        return f'<div class="page-plate has-photo">{pic}</div>'
    return f'<div class="page-plate">{fallback}</div>'


def home():
    pg = PAGES["/mapot/"]
    lede, rest = first_paragraph_and_rest("/mapot/")
    rest = re.sub(r"<h2>נקי ומוכן לפריסה</h2>\s*<p>.*?</p>", "", rest, count=1, flags=re.S)
    hero = BY_SKU["TC-LINEN-3X3"]
    kinds = []
    metas = {
        "tablecloths": "סאטן, פשתן, פרחים",
        "napkins": "סאטן ופשתן",
        "runners": "קו עיצובי לשולחן",
        "chair-covers": "מראה אחיד לאולם",
    }
    for i, (slug, _t, name, _s) in enumerate(CATS, 1):
        kinds.append(
            f'<a href="/mapot/{slug}/">'
            f'<span class="kind-no">{i:02d}</span><span class="kind-name">{esc(name)}</span>'
            f'<span class="kind-meta">{esc(metas[slug])}</span></a>'
        )
    featured = [
        "TC-LINEN-3X3", "TC-SATIN-22X22", "TC-LINEN-ROUND", "NP-SATIN",
        "RN-STD", "TC-FLORAL-*", "TC-SATIN-15X3", "CC-STD",
    ]
    tiles = []
    for sku in featured:
        p = BY_SKU[sku]
        tiles.append(
            f'<a class="tile" href="/mapot/catalog/{p["slug"]}/">'
            f'{plate_for(p, "home"+p["sku"])}'
            f'<strong>{esc(p["name_he"])}</strong>'
            f'<span class="price">{esc(price_label(p))}</span></a>'
        )
    toc = "".join(
        f'<li><a href="{u}"><span class="no">{i:02d}</span><span class="nm">{esc(n)}</span><span class="go">לעמוד</span></a></li>'
        for i, (u, n) in enumerate(EVENTS, 1)
    )
    hero_pic = atmo_picture("hero", "hero", "100vw", priority=True)
    if hero_pic:
        stage = f'<div class="hero-stage has-photo">{hero_pic}</div>'
        bleed = "hero-bleed has-photo"
        og = ORIGIN + "/mapot/media/atmosphere/hero-wide-1280.jpg"
    else:
        stage = f'<div class="hero-stage">{plate_for(hero, "mast", mode="hero")}</div>'
        bleed = "hero-bleed"
        og = ""
    band = hall_band()
    band_html = ("\n" + band) if band else ""
    body = f"""
<section class="{bleed}">
{stage}
<div class="hero-copy">
<div class="hero-panel">
<p class="kicker">{esc(B)} · מבית מכבסת היערה</p>
<h1 class="display">השכרת מפות<br>לעסקים ולמוסדות</h1>
<div class="actions"><a class="btn" href="/mapot/catalog/">לקטלוג</a><a class="btn btn-ghost" href="{WA}">וואטסאפ {PH}</a></div>
</div>
<p class="lede">{lede}</p>
</div>
</section>
<nav class="kinds" aria-label="סוגי פריטים">{''.join(kinds)}</nav>{band_html}
<div class="folio">{''.join(tiles)}</div>{(chr(10) + range_section()) if RANGE_FILES else ""}
<section class="essay">
<div class="essay-body prose">{rest}</div>
<div class="pull-col"><h2>נקי ומוכן לפריסה</h2><blockquote class="pull"><p>כל הזמנה מגיעה נקייה, והמפות מגיעות מגוהצות, מוכנות לפריסה.</p></blockquote></div>
</section>
<section>
<h2>לפי סוג אירוע</h2>
<ol class="toc">{toc}</ol>
</section>
"""
    shell("/mapot/", pg["title"], pg["desc"], [], body, main_class="home", og_image=og)


def category(url):
    pg = PAGES[url]
    slug = url.strip("/").split("/")[-1]
    lede, rest = first_paragraph_and_rest(url)
    prods = [p for p in PRODUCTS if CAT_BY_TYPE[p["type"]][0] == slug]
    sample = prods[0]
    h1 = re.search(r"^# (.+)", "\n".join(pg["lines"]), re.M).group(1).strip()
    body = f"""
<header class="page-head">
<div>
<p class="kicker">השכרה</p>
<h1>{esc(h1)}</h1>
<p class="lede">{lede}</p>
</div>
{head_plate(slug, plate_for(sample, "cat"+slug))}
</header>
<div class="catalog-top"><p id="resultn" aria-live="polite"></p><button type="button" class="btn-ghost btn filter-open" id="openf" aria-expanded="false" aria-controls="filterpanel">סינון</button></div>
{filter_bar(prods, lock=slug)}
{grid(prods)}
{close_layout()}
<div class="prose">{rest}</div>
<p><a class="btn" href="/mapot/catalog/">לכל הקטלוג</a></p>
"""
    extra = [
        item_list(prods),
        {
            "@type": "Service",
            "name": h1,
            "serviceType": "השכרה",
            "provider": {"@id": ORG_ID},
            "url": ORIGIN + url,
        },
    ]
    shell(url, pg["title"], pg["desc"], [("קטלוג", "/mapot/catalog/"), (pg["name"], url)], body, extra)


def event_page(url):
    pg = PAGES[url]
    h1 = re.search(r"^# (.+)", "\n".join(pg["lines"]), re.M).group(1).strip()
    lede, rest = first_paragraph_and_rest(url)
    slug = url.strip("/").split("/")[-1]
    event_cloth = {
        "wedding": "#6d2428",
        "bar-mitzvah": "#243044",
        "brit": "#3e4a38",
        "sheva-brachot": "#8a5a32",
        "halls-catering": "#6d2428",
    }.get(slug, "#6d2428")
    fig = (
        f'<div class="scene" style="--cloth:{event_cloth}" aria-hidden="true">'
        f'{plates.render_view("setting", "linen", None, "ev"+slug, "hero")}</div>'
    )
    chips = "".join(f'<a class="btn btn-ghost" href="/mapot/{s}/">{esc(n)}</a>' for s, _t, n, _x in CATS)
    body = f"""
<header class="page-head">
<div>
<p class="kicker">לפי סוג אירוע</p>
<h1>{esc(h1)}</h1>
<p class="lede">{lede}</p>
</div>
{head_plate(slug, fig)}
</header>
<div class="prose">{rest}</div>
<div class="actions">{chips}</div>
"""
    extra = [{"@type": "Service", "name": h1, "provider": {"@id": ORG_ID}, "url": ORIGIN + url}]
    shell(url, pg["title"], pg["desc"], [(pg["name"], url)], body, extra)


def faq_pairs(lines):
    pairs, q, buf = [], None, []

    def flush():
        nonlocal q, buf
        if not q:
            return
        ans = strip_pending(" ".join(buf))
        ans = re.sub(r"\s+", " ", ans).strip()
        if q in FAQ_FIX and (not ans or "[ממתין לצבי]" in ans):
            ans = FAQ_FIX[q]
        ans = ans.replace(PH, PH)
        if ans:
            pairs.append((q, ans))
        q, buf = None, []

    for l in lines:
        if l.startswith("## "):
            flush()
            q = l[3:].strip()
            buf = []
        elif l.startswith("# ") or l.startswith("**"):
            continue
        elif l.strip() and not l.startswith("("):
            buf.append(l.strip())
    flush()
    return pairs


def faq_page():
    pg = PAGES["/mapot/faq/"]
    h1 = re.search(r"^# (.+)", "\n".join(pg["lines"]), re.M).group(1).strip()
    pairs = faq_pairs(pg["lines"])
    blocks = [f"<h1>{esc(h1)}</h1>"]
    for q, a in pairs:
        blocks.append(f"<h2>{esc(q)}</h2><p>{inl(a)}</p>")
    blocks.append(f'<p><a class="btn" href="/mapot/catalog/">לקטלוג ולהזמנה</a></p>')
    shell("/mapot/faq/", pg["title"], pg["desc"], [("שאלות נפוצות", "/mapot/faq/")], "\n".join(blocks), [faq_ld(pairs)])


def areas_page():
    pg = PAGES["/mapot/service-areas/"]
    h1 = re.search(r"^# (.+)", "\n".join(pg["lines"]), re.M).group(1).strip()
    body = md2html(pg["lines"])
    body = re.sub(r"^<h1>.*?</h1>", f"<h1>{esc(h1)}</h1>", body, count=1)
    extra = [{
        "@type": "Service",
        "name": "השכרת מפות ומפיות",
        "provider": {"@id": ORG_ID},
        "areaServed": ["השרון", "גוש דן", "עוטף ירושלים", "ים המלח", "גוש עציון"],
        "url": ORIGIN + "/mapot/service-areas/",
    }]
    shell("/mapot/service-areas/", pg["title"], pg["desc"], [("אזורי שירות", "/mapot/service-areas/")], f'<div class="prose">{body}</div><p><a class="btn" href="/mapot/catalog/">לקטלוג ולהזמנה</a></p>', extra)


def catalog():
    title = f"השכרת מפות, מפיות וראנרים | {B}"
    desc = f"קטלוג {B}: השכרת מפות, מפיות, ראנרים וכיסויי כיסאות לעסקים ולמוסדות. בוחרים פריטים וכמויות ושולחים בקשת הזמנה. לקבלת הצעת מחיר."
    body = f"""
<header class="page-head">
<div>
<p class="kicker">היערה אירועים</p>
<h1>השכרת מפות, מפיות, ראנרים וכיסויי כיסאות</h1>
<p class="lede">בוחרים פריטים, מוסיפים להזמנה ושולחים. את הכמויות ואת המשלוח מאשרים איתכם בשיחה. {esc(price_label({'price': None}))}.</p>
</div>
</header>
<div class="catalog-top"><p id="resultn" aria-live="polite"></p><button type="button" class="btn-ghost btn filter-open" id="openf" aria-expanded="false" aria-controls="filterpanel">סינון</button></div>
{filter_bar(PRODUCTS)}
{grid(PRODUCTS)}
{close_layout()}
"""
    shell(
        "/mapot/catalog/",
        title,
        desc,
        [("קטלוג", "/mapot/catalog/")],
        body,
        [item_list(PRODUCTS)],
    )


def related(p):
    same = [x for x in PRODUCTS if x["type"] == p["type"] and x["sku"] != p["sku"]]
    others = [x for x in PRODUCTS if x["type"] != p["type"]]
    pick = (same + others)[:3]
    # A chair page must not carry palette hex, so its related scenes stay undyed.
    dyed = p["type"] != "chair_cover"
    bits = []
    for x in pick:
        bits.append(
            f'<a class="item" href="/mapot/catalog/{x["slug"]}/">'
            f'{plate_for(x, "rel"+p["sku"]+x["sku"], dyed=dyed)}'
            f'<strong>{esc(x["name_he"])}</strong>'
            f'<span class="price">{esc(price_label(x))}</span></a>'
        )
    return f'<section class="related"><h2>עוד בקטלוג</h2><div class="related-grid">{"".join(bits)}</div></section>'


def product_page(p):
    t = TEMPLATES[TKEY[p["type"]]]
    url = f"/mapot/catalog/{p['slug']}/"
    title = f'{p["name_he"]} | {B}'
    desc = blurb(p) + " לקבלת הצעת מחיר."
    if len(desc) > 170:
        desc = blurb(p)
    specs = []
    if mat_name(p):
        specs.append(("בד", mat_name(p)))
    if p.get("size"):
        specs.append(("מידה", p["size"]))
    specs.append(("מק״ט", p["sku"]))
    specs.append(("מחיר", price_label(p)))
    spec_html = "".join(f'<div class="spec"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in specs)
    sw = ""
    accent = accent_of(p)
    if p["public_colors"]:
        buttons = []
        for c in p["public_colors"]:
            on = accent and c["key"] == accent["key"]
            buttons.append(
                f'<button type="button" class="swatch" role="radio" aria-checked="{"true" if on else "false"}" '
                f'title="{esc(c["name"])}" aria-label="{esc(c["name"])}" data-color="{esc(c["key"])}" data-name="{esc(c["name"])}" '
                f'data-hex="{esc(c["hex"])}" style="--sw:{esc(c["hex"])}">'
                f'<span class="swatch-chip" aria-hidden="true"></span><span class="swatch-name">{esc(c["name"])}</span></button>'
            )
        first = accent["name"] if accent else p["public_colors"][0]["name"]
        sw = (
            f'<div class="swatches" role="radiogroup" aria-label="צבע">{"".join(buttons)}</div>'
            f'<p class="chosen"><span class="sr">הצבע הנבחר</span> <span id="cname">{esc(first)}</span></p>'
        )
    min_qty = p.get("min_qty")
    min_attr = int(min_qty) if isinstance(min_qty, int) and min_qty > 0 else 1
    min_note = f'<p class="qty-note">כמות מינימלית: {min_attr}</p>' if isinstance(min_qty, int) and min_qty else ""
    needs = "1" if p["public_colors"] else "0"
    size_attr = esc(p.get("size") or "")
    fabric_attr = esc(mat_name(p))
    pts = "".join(f"<li>{esc(x)}</li>" for x in t["pts"])
    pairs = product_faq(p)
    faq_html = "".join(f"<h2>{esc(q)}</h2><p>{esc(a)}</p>" for q, a in pairs)
    avail = '<p id="availnote" class="qty-note" aria-live="polite"></p>' if SHOW_AVAIL else ""
    stage = gallery_for(p, "stage" + p["sku"])
    body = f"""
<article class="product">
<div class="stage-wrap">{stage}</div>
<div class="buy">
<p class="kicker">{esc(CAT_BY_TYPE[p['type']][1])}</p>
<h1>{esc(p['name_he'])}</h1>
<p class="price-lg">{esc(price_label(p))}</p>
<div class="specs">{spec_html}</div>
<p>{esc(blurb(p))}</p>
{sw}
{avail}
<label class="qty-note" for="q">{esc(t['qty'])}</label>
<div class="stepper"><button type="button" id="qdec" aria-label="הפחתת כמות">−</button><input id="q" type="number" min="{min_attr}" max="10000" value="{min_attr}" inputmode="numeric" aria-label="כמות"><button type="button" id="qinc" aria-label="הגדלת כמות">+</button></div>
{min_note}
<div class="actions"><button type="button" class="btn" id="add" data-sku="{esc(p['sku'])}" data-name="{esc(p['name_he'])}" data-size="{size_attr}" data-fabric="{fabric_attr}" data-needs-color="{needs}" data-min="{min_attr}">{esc(t['btn'])}</button></div>
<p id="added" hidden role="status">נוסף לסל. <a href="/mapot/order/">לסל ההזמנה</a></p>
<ul class="points">{pts}</ul>
<p>אפשר גם בטלפון או בוואטסאפ: <a href="{WA}">{PH}</a></p>
</div>
</article>
<section class="faq-block">{faq_html}</section>
{related(p)}
<noscript><p>להזמנה בטלפון או בוואטסאפ: <a href="{WA}">{PH}</a></p></noscript>
"""
    dock = f'''<div class="dock" aria-hidden="true"><div><b>{esc(p["name_he"])}</b><span>{esc(price_label(p))}</span></div></div>'''
    cat_slug, cat_name = CAT_BY_TYPE[p["type"]]
    shell(
        url,
        title,
        desc,
        [("קטלוג", "/mapot/catalog/"), (cat_name, f"/mapot/{cat_slug}/"), (p["name_he"], url)],
        body,
        [product_ld(p), faq_ld(pairs)],
        dock=dock,
    )


MONTHS_HE = ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"]


def date_field(label):
    months = ",".join(MONTHS_HE)
    return (
        f'<fieldset class="datefield" data-months="{esc(months)}"><legend>{esc(label)} *</legend>'
        f'<div class="datepick"><span class="dateface" id="dateface">בחירת תאריך</span>'
        f'<input id="f-event_date" name="event_date" type="date" required '
        f'min="2026-01-01" max="2032-12-31" aria-label="{esc(label)}"></div></fieldset>'
    )


def order_page():
    labels = ORDER_FIELDS["תוויות שדות"].split(" | ")
    names = ["business", "contact", "phone", "email", "event_date", "address", "notes"]
    types = ["text", "text", "tel", "email", "text", "text", "textarea"]
    auto = ["organization", "name", "tel", "email", "off", "street-address", "off"]
    req = {"contact", "phone", "address"}
    fields = []
    for label, name, typ, ac in zip(labels, names, types, auto):
        if name == "event_date":
            fields.append(date_field(label))
            continue
        star = " *" if name in req else ""
        req_attr = " required" if name in req else ""
        if typ == "textarea":
            control = f'<textarea id="f-{name}" name="{name}" maxlength="1000" autocomplete="{ac}"></textarea>'
        else:
            extra = ' inputmode="tel"' if name == "phone" else ""
            if name == "contact":
                extra += ' minlength="2"'
            control = f'<input id="f-{name}" name="{name}" type="{typ}" maxlength="200" autocomplete="{ac}"{req_attr}{extra}>'
        fields.append(f'<label for="f-{name}">{esc(label)}{star}{control}</label>')
    body = f"""
<h1>סל ההזמנה</h1>
<p class="lede">{inl(ORDER_FIELDS['טקסט פתיחה'])}</p>
<div id="empty" hidden><p>{inl(ORDER_FIELDS['סל ריק'])}</p><a class="btn" href="/mapot/catalog/">לקטלוג</a></div>
<div class="order-grid" id="cartbox">
<div><table class="lines" id="lines"></table></div>
<form id="orderform" novalidate>
<div class="fields">{''.join(fields)}</div>
<div class="hp"><label for="hp-site">השאר ריק</label><input id="hp-site" name="website" tabindex="-1" autocomplete="off" value=""></div>
<div class="actions"><button class="btn" type="submit">{esc(ORDER_FIELDS['כפתור'])}</button></div>
<p id="err" class="err" role="alert" hidden></p>
</form>
</div>
<div id="done" hidden tabindex="-1"><p>{inl(ORDER_FIELDS['הודעת אישור'])}</p></div>
<noscript><p>אפשר להזמין בטלפון או בוואטסאפ: <a href="{WA}">{PH}</a></p></noscript>
"""
    shell("/mapot/order/", ORDER["title"], ORDER["desc"], [("סל ההזמנה", "/mapot/order/")], body, noindex=True)


def write_assets():
    os.makedirs(os.path.join(OUT, "assets", "fonts"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "media"), exist_ok=True)
    for name in ("mapot.css", "cart.js"):
        shutil.copy(os.path.join(R, name), os.path.join(OUT, "assets", name))
    for name in ("heebo.woff2", "frank-ruhl-libre.woff2"):
        shutil.copy(os.path.join(R, "fonts", name), os.path.join(OUT, "assets", "fonts", name))
    seen = set()
    for p in PRODUCTS:
        for name in p["files"]:
            if name in seen:
                continue
            seen.add(name)
            shutil.copy(os.path.join(R, "photos", name), os.path.join(OUT, "media", name))
    if RANGE_FILES:
        dest = os.path.join(OUT, "media", "range")
        os.makedirs(dest, exist_ok=True)
        for name in RANGE_FILES:
            shutil.copy(os.path.join(R, "range", name), os.path.join(dest, name))


def write_meta():
    products_map = {}
    for p in PRODUCTS:
        products_map[p["sku"]] = {
            "name": p["name_he"],
            "slug": p["slug"],
            "colors": [c["key"] for c in p["public_colors"]],
            "color_names": {c["key"]: c["name"] for c in p["public_colors"]},
        }
    json.dump(products_map, open(os.path.join(OUT, "_products.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    redirects = {
        "/services/tablecloth-rental.html": "/mapot/",
        "/services/event-hall-tablecloth-rental.html": "/mapot/halls-catering/",
        "/services/tablecloth-rental-jerusalem.html": "/mapot/service-areas/",
        "/services/tablecloth-rental-gush-etzion.html": "/mapot/service-areas/",
        "/services/tablecloth-rental-sharon.html": "/mapot/service-areas/",
        "/services/table-linen.html": "/mapot/tablecloths/",
        "/mapot/catalog/tablecloth-3x3/": "/mapot/catalog/tc-linen-3x3/",
        "/mapot/catalog/tablecloths-example/": "/mapot/tablecloths/",
        "/mapot/catalog/napkins-example/": "/mapot/napkins/",
        "/mapot/catalog/runners-example/": "/mapot/runners/",
        "/mapot/catalog/chair-covers-example/": "/mapot/chair-covers/",
    }
    json.dump(redirects, open(os.path.join(OUT, "_redirects.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    urls = []
    seen = set()
    for u in SITEMAP:
        if u not in seen:
            seen.add(u)
            urls.append(u)
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{ORIGIN}{u}</loc></url>")
    sm.append("</urlset>\n")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm))
    if PREVIEW:
        robots = "User-agent: *\nDisallow: /mapot/\n"
    else:
        robots = f"User-agent: *\nAllow: /mapot/\n\nSitemap: {ORIGIN}/mapot/sitemap.xml\n"
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(robots)
    lines = [
        f"# {B}",
        "",
        f"{B} הוא קו השכרה של {C['legal']} למפות, למפיות, לראנרים ולכיסויי כיסאות. הלקוחות הם אולמות, קייטרינג, מלונות, מסעדות, עסקים ומוסדות.",
        "",
        "מה משכירים: מפות מסאטן, מפשתן ומבד פרחים, במידות 1.5×1.5, 1.5×3, 2.2×2.2, 3×3, ומפה עגולה. מפיות מסאטן ומפשתן. ראנרים. כיסויי כיסאות. מפות זמינות גם לרכישה.",
        "הפריטים מגיעים נקיים, והמפות מגיעות מגוהצות, מוכנות לפריסה. יש איסוף ומשלוח, וגם סבב קבוע לאולמות, למלונות ולקייטרינג.",
        "",
        f"הזמנה: באתר, דרך סל ההזמנה, או בטלפון ובוואטסאפ {PH}, או במייל {EMAIL}. את הכמויות ואת המשלוח מאשרים בשיחה. מחיר: לקבלת הצעת מחיר.",
        f"כתובת: {C['street']}, {C['locality']}.",
        "אזורי שירות: ריכוזי הערים החרדיות, השרון, גוש דן, עוטף ירושלים, ים המלח וגוש עציון.",
        "",
        "עמודים:",
    ]
    for u in urls:
        lines.append(f"- {ORIGIN}{u}")
    lines.append("")
    open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8").write("\n".join(lines))


def forbid():
    bad_re = re.compile(r"מלאי|אנחנו לא|\[ממתין לצבי\]|תמונה תתווסף|שרטוט|Website")
    emoji = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F9FF]")
    hits = []
    for dirpath, _, files in os.walk(OUT):
        for fn in files:
            if fn.startswith("_"):
                continue
            path = os.path.join(dirpath, fn)
            if os.path.splitext(fn)[1].lower() not in {".html", ".css", ".js", ".txt", ".xml", ""}:
                continue
            text = open(path, encoding="utf-8", errors="replace").read()
            if bad_re.search(text) or emoji.search(text):
                hits.append(path)
    if hits:
        sys.exit("forbidden text in: " + ", ".join(hits))


def main():
    global ATMOS
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, "media", "atmosphere"), exist_ok=True)
    ATMOS = atmosphere.render(os.path.join(R, "atmosphere"), os.path.join(OUT, "media", "atmosphere"))
    home()
    for slug, _t, _n, _s in CATS:
        category(f"/mapot/{slug}/")
    for url, _n in EVENTS:
        if url == "/mapot/halls-catering/":
            event_page(url)
        elif url in PAGES:
            event_page(url)
    faq_page()
    areas_page()
    catalog()
    for p in PRODUCTS:
        product_page(p)
    order_page()
    write_assets()
    write_meta()
    forbid()
    print(f"{len(PRODUCTS)} products, {len(set(SITEMAP))} sitemap urls, colors={'on' if SHOW_COLORS else 'off'}, preview={PREVIEW}")


if __name__ == "__main__":
    main()
