# Code-rendered fabric scenes. Not photographs and not technical drawings.
# A real photo in mapot-src/photos/ replaces the scene at build time.
import re

CLOTH = "#efe4d2"


def uid_of(s):
    return re.sub(r"[^A-Za-z0-9]+", "", str(s)) or "p"


def _fold(uid):
    n = 0
    for ch in str(uid):
        n = (n * 33 + ord(ch)) & 0xFFFFFFFF
    return "f" + str(n % 3)


def classes_for(kind, fabric, size, uid, hero=False):
    fold = _fold(uid)
    fab = fabric if fabric in ("linen", "satin", "floral") else "linen"
    if kind == "chair":
        return ["scene", "chair", fold]
    if kind in ("setting",) or hero:
        out = ["scene", "hero", "sq", fab, fold, "with-nap", "with-run", "with-plate"]
        if fab == "floral":
            out.append("floral")
        return out
    if kind == "napkin":
        return ["scene", "napkin", fab, fold, "with-nap"]
    if kind == "runner":
        return ["scene", "runner", "linen", fold, "with-run", "with-nap"]
    if size == "עגולה":
        out = ["scene", "round", fab, fold, "with-nap", "with-plate"]
    elif size == "1.5×3":
        out = ["scene", "banquet", fab, fold, "with-run", "with-nap"]
    elif fab == "floral" or not size:
        out = ["scene", "sq", fab, fold, "with-nap", "with-plate"]
    else:
        out = ["scene", "sq", fab, fold, "with-nap"]
        if fold != "f1":
            out.append("with-run")
    if fab == "floral":
        out.append("floral")
    return out


def _floral(uid):
    return (
        f'<svg class="print" viewBox="0 0 200 200" preserveAspectRatio="xMidYMid slice">'
        f'<defs><pattern id="fl{uid}" width="46" height="46" patternUnits="userSpaceOnUse">'
        f'<g fill="none" stroke="#1c1916" stroke-width="0.8" opacity="0.55">'
        f'<path d="M23 8c2.2 4.2 2.2 7.2 0 11.2c-2.2-4-2.2-7 0-11.2z"/>'
        f'<path d="M23 38c2.2-4.2 2.2-7.2 0-11.2c-2.2 4-2.2 7 0 11.2z"/>'
        f'<path d="M8 23c4.2-2.2 7.2-2.2 11.2 0c-4.2 2.2-7.2 2.2-11.2 0z"/>'
        f'<path d="M38 23c-4.2-2.2-7.2-2.2-11.2 0c4.2 2.2 7.2 2.2 11.2 0z"/>'
        f'<path d="M23 23c4-6 9-6 12 0c-5 1-8 3-12 0z" opacity="0.7"/>'
        f'<circle cx="23" cy="23" r="1.15" fill="#1c1916" stroke="none"/>'
        f"</g></pattern></defs>"
        f'<rect width="200" height="200" fill="url(#fl{uid})"/></svg>'
    )


def _fabric(uid, floral):
    bloom = _floral(uid) if floral else ""
    return (
        '<i class="wood"></i>'
        '<div class="cloth"><i class="fall"></i><div class="face">'
        '<i class="ridge"></i><i class="weave"></i><i class="sheen"></i>'
        f"{bloom}</div></div>"
        '<i class="run"></i><i class="nap"></i><i class="plate"></i>'
    )


def _chair():
    return '<i class="shadow"></i><i class="skirt"></i><i class="back"></i><i class="band"></i><i class="bow"></i>'


def render(kind, fabric, size, uid, stage=False, hero=False, cloth=None):
    uid = uid_of(uid)
    classes = classes_for(kind, fabric, size, uid, hero=hero)
    style = ""
    if cloth and "chair" not in classes:
        style = f' style="--cloth:{cloth}"'
    ident = ' id="stage"' if stage else ""
    floral = "floral" in classes
    inner = _chair() if "chair" in classes else _fabric(uid, floral)
    return f'<div class="{" ".join(classes)}"{ident}{style} aria-hidden="true">{inner}</div>'
