"""Hall atmosphere. Not product photography.

Sources live in mapot-src/atmosphere/ and are chosen by filename.
hero.jpg is the home hero. events-1.jpg, events-2.jpg, … are for
event pages, category headers, and the home hall band.
A missing file leaves that slot on the drawn scene. Nothing here is a SKU.
"""
import html
import os
from PIL import Image

NARROW_EXT = {".jpg", ".jpeg", ".png", ".webp"}
HERO_BREAK = "699px"
HEADER_BREAK = "959px"

# focal is the subject in the source (0–1). anchor is where that point
# should sit inside the crop. zoom 1 keeps the largest crop of that shape.
SLOTS = {
    "hero": {
        "files": (
            "hero.jpg",
            "hero.jpeg",
            "01-white-tablecloths-grey-napkins-balloons-hall.jpg",
        ),
        "alt": "אולם חתונה ערוך במפות ארוכות ובמפיות מקופלות",
        "narrow": {
            "ratio": (2, 3),
            "focal": (0.46, 0.64),
            "anchor": (0.50, 0.40),
            "zoom": 0.86,
            "widths": (480, 800),
        },
        "wide": {
            "ratio": (3, 2),
            "focal": (0.50, 0.58),
            "anchor": (0.50, 0.55),
            "zoom": 1.0,
            "widths": (1280, 1920),
        },
    },
    "events-1": {
        "files": (
            "events-1.jpg",
            "events-1.jpeg",
            "02-ivory-round-tables-floral-centerpiece-glass-hall.jpg",
        ),
        "alt": "שולחנות עגולים ערוכים במפה, עם סידור פרחים, באולם עם חלונות גבוהים",
        "caption": "שולחנות עגולים",
        "narrow": {
            "ratio": (16, 9),
            "focal": (0.36, 0.68),
            "anchor": (0.42, 0.62),
            "zoom": 1.0,
            "widths": (720, 1440),
        },
        "wide": {
            "ratio": (4, 5),
            "focal": (0.34, 0.62),
            "anchor": (0.48, 0.55),
            "zoom": 0.92,
            "widths": (700, 1200),
        },
    },
    "events-2": {
        "files": (
            "events-2.jpg",
            "events-2.jpeg",
            "03-chandelier-ballroom-white-linen-round-tables.jpg",
        ),
        "alt": "אולם נשף עם נברשת, שולחנות עגולים וכיסויי כיסאות",
        "caption": "אולם עם נברשת",
        "narrow": {
            "ratio": (16, 9),
            "focal": (0.50, 0.55),
            "anchor": (0.50, 0.55),
            "zoom": 1.0,
            "widths": (720, 1440),
        },
        "wide": {
            "ratio": (4, 5),
            "focal": (0.50, 0.48),
            "anchor": (0.50, 0.42),
            "zoom": 1.0,
            "widths": (700, 1200),
        },
    },
    "events-3": {
        "files": (
            "events-3.jpg",
            "events-3.jpeg",
            "04-white-round-tablecloths-greenhouse-venue.jpg",
        ),
        "alt": "אולם זכוכית עם עצים ושולחנות עגולים ערוכים במפות",
        "caption": "אולם זכוכית",
        "narrow": {
            "ratio": (16, 9),
            "focal": (0.38, 0.62),
            "anchor": (0.40, 0.58),
            "zoom": 1.0,
            "widths": (720, 1440),
        },
        "wide": {
            "ratio": (4, 5),
            "focal": (0.36, 0.58),
            "anchor": (0.46, 0.52),
            "zoom": 0.95,
            "widths": (700, 1200),
        },
    },
    "events-4": {
        "files": (
            "events-4.jpg",
            "events-4.jpeg",
            "05-spacious-hall-ivory-tablecloth-pampas-decor.jpg",
        ),
        "alt": "אולם אירועים עם שולחן ארוך ערוך במפה ובסידורי פרחים",
        "caption": "שולחן ארוך",
        "narrow": {
            "ratio": (16, 9),
            "focal": (0.55, 0.46),
            "anchor": (0.55, 0.50),
            "zoom": 1.0,
            "widths": (720, 1440),
        },
        "wide": {
            "ratio": (4, 5),
            "focal": (0.62, 0.42),
            "anchor": (0.55, 0.45),
            "zoom": 0.9,
            "widths": (700, 1200),
        },
    },
}

# Page slug → atmosphere slot. Not a product, and not a chair-cover page.
HEADERS = {
    "tablecloths": "events-1",
    "wedding": "events-2",
    "bar-mitzvah": "events-4",
    "brit": "events-3",
    "sheva-brachot": "events-1",
    "halls-catering": "events-3",
}
BAND = ("events-1", "events-2", "events-3")


def crop_box(im_w, im_h, ratio, focal, anchor, zoom):
    """Pixel box for one art-directed crop. Clamped to the source."""
    target = ratio[0] / ratio[1]
    if im_w / im_h > target:
        max_h = im_h
        max_w = int(round(im_h * target))
    else:
        max_w = im_w
        max_h = int(round(im_w / target))
    zoom = min(1.0, max(0.2, float(zoom)))
    crop_w = max(1, int(round(max_w * zoom)))
    crop_h = max(1, int(round(crop_w / target)))
    if crop_h > im_h:
        crop_h = im_h
        crop_w = max(1, int(round(crop_h * target)))
    if crop_w > im_w:
        crop_w = im_w
        crop_h = max(1, int(round(crop_w / target)))
    cx = min(1.0, max(0.0, focal[0])) * im_w
    cy = min(1.0, max(0.0, focal[1])) * im_h
    ax = min(1.0, max(0.0, anchor[0]))
    ay = min(1.0, max(0.0, anchor[1]))
    left = int(round(cx - ax * crop_w))
    top = int(round(cy - ay * crop_h))
    left = max(0, min(left, im_w - crop_w))
    top = max(0, min(top, im_h - crop_h))
    return (left, top, left + crop_w, top + crop_h)


def find_source(folder, slot):
    if not folder or not os.path.isdir(folder):
        return None
    for name in slot["files"]:
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            return path
    return None


def _variants(slot_id, view, crop):
    rw, rh = crop["ratio"]
    out = []
    for w in crop["widths"]:
        h = max(1, int(round(w * rh / rw)))
        out.append({"w": w, "h": h, "stem": f"{slot_id}-{view}-{w}"})
    return out


def plan(folder):
    """Slots that have a source file, with the variant names the HTML will use."""
    ready = {}
    for slot_id, slot in SLOTS.items():
        src = find_source(folder, slot)
        if not src:
            continue
        ready[slot_id] = {
            "alt": slot["alt"],
            "caption": slot.get("caption") or "",
            "source": src,
            "narrow": _variants(slot_id, "narrow", slot["narrow"]),
            "wide": _variants(slot_id, "wide", slot["wide"]),
            "narrow_crop": slot["narrow"],
            "wide_crop": slot["wide"],
        }
    return ready


def _save(im, dest, stem):
    os.makedirs(dest, exist_ok=True)
    base = os.path.join(dest, stem)
    im.save(base + ".jpg", format="JPEG", quality=82, optimize=True, progressive=True)
    im.save(base + ".webp", format="WEBP", quality=78, method=6)
    im.save(base + ".avif", format="AVIF", quality=50, speed=6)
    return stem


def render(folder, dest):
    """Write jpg, webp, and avif for every ready slot. Returns the plan."""
    ready = plan(folder)
    for slot_id, row in ready.items():
        with Image.open(row["source"]) as raw:
            im = raw.convert("RGB")
            w, h = im.size
            for view in ("narrow", "wide"):
                crop = row[view + "_crop"]
                box = crop_box(w, h, crop["ratio"], crop["focal"], crop["anchor"], crop["zoom"])
                framed = im.crop(box)
                for variant in row[view]:
                    sized = framed.resize((variant["w"], variant["h"]), Image.Resampling.LANCZOS)
                    _save(sized, dest, variant["stem"])
    return ready


def _srcset(variants, ext):
    bits = []
    for variant in variants:
        bits.append(f"/mapot/media/atmosphere/{variant['stem']}.{ext} {variant['w']}w")
    return ", ".join(bits)


def _source_tags(variants, sizes, media):
    media_attr = f' media="{media}"' if media else ""
    tags = []
    for mime, ext in (("image/avif", "avif"), ("image/webp", "webp")):
        tags.append(
            f'<source{media_attr} type="{mime}" srcset="{_srcset(variants, ext)}" sizes="{html.escape(sizes, quote=True)}">'
        )
    tags.append(
        f'<source{media_attr} srcset="{_srcset(variants, "jpg")}" sizes="{html.escape(sizes, quote=True)}">'
    )
    return "".join(tags)


def picture(ready, slot_id, *, kind, sizes, priority=False):
    """Responsive picture. kind is hero, header, or band. Empty when the file is absent."""
    row = (ready or {}).get(slot_id)
    if not row:
        return ""
    if kind == "band":
        variants = row["narrow"]
        sources = _source_tags(variants, sizes, "")
        chosen = variants[-1]
        extra = ' loading="lazy" decoding="async"'
    elif kind == "header":
        sources = _source_tags(row["narrow"], sizes, f"(max-width: {HEADER_BREAK})")
        sources += _source_tags(row["wide"], sizes, "")
        chosen = row["wide"][-1]
        extra = ' loading="lazy" decoding="async"'
    elif kind == "hero":
        sources = _source_tags(row["narrow"], sizes, f"(max-width: {HERO_BREAK})")
        sources += _source_tags(row["wide"], sizes, "")
        chosen = row["wide"][-1]
        extra = ' fetchpriority="high" decoding="async"' if priority else ' decoding="async"'
    else:
        return ""
    alt = html.escape(row["alt"], quote=True)
    src = f"/mapot/media/atmosphere/{chosen['stem']}.jpg"
    srcset = _srcset(row["narrow"] if kind == "band" else row["wide"], "jpg")
    return (
        f"<picture>{sources}"
        f'<img src="{src}" srcset="{srcset}" sizes="{html.escape(sizes, quote=True)}" '
        f'alt="{alt}" width="{chosen["w"]}" height="{chosen["h"]}"{extra}>'
        f"</picture>"
    )
