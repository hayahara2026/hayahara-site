# Code-drawn cloth plates. Technical drawings, not photographs.
import html as H
import re

INK = "#1c1916"
PAPER = "#f3efe6"
CLOTH = "#f4efe4"
UNDYED = "#e6dcc8"

SIZES = {
    "1.5×1.5": (1.5, 1.5),
    "2.2×2.2": (2.2, 2.2),
    "3×3": (3.0, 3.0),
    # Long side drawn horizontal so the banquet proportion reads in the plate.
    "1.5×3": (3.0, 1.5),
}


def uid_of(s):
    return re.sub(r"[^A-Za-z0-9]+", "", str(s)) or "p"


def _defs(uid, fabric):
    parts = []
    if fabric in ("linen", "floral", None, "runner"):
        parts.append(
            f'<pattern id="wv{uid}" width="6" height="6" patternUnits="userSpaceOnUse">'
            f'<path d="M0 3H6" stroke="{INK}" stroke-width="0.4" opacity="0.22"/>'
            f'<path d="M3 0V6" stroke="{INK}" stroke-width="0.32" opacity="0.16"/>'
            f'<path d="M0 3H6" stroke="#fff" stroke-width="0.35" opacity="0.34" transform="translate(0 0.8)"/>'
            f"</pattern>"
        )
    if fabric == "satin":
        parts.append(
            f'<linearGradient id="sh{uid}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0.28" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset="0.46" stop-color="#fff" stop-opacity="0.7"/>'
            f'<stop offset="0.58" stop-color="#fff" stop-opacity="0.08"/>'
            f'<stop offset="0.72" stop-color="#fff" stop-opacity="0"/>'
            f"</linearGradient>"
        )
    if fabric == "floral":
        petal = (
            f'<g fill="none" stroke-width="0.7">'
            f'<path d="M13 6.5c1.7 2 1.7 3.6 0 5.4c-1.7-1.8-1.7-3.4 0-5.4z"/>'
            f'<path d="M13 19.5c1.7-2 1.7-3.6 0-5.4c-1.7 1.8-1.7 3.4 0 5.4z"/>'
            f'<path d="M6.5 13c2-1.7 3.6-1.7 5.4 0c-2 1.7-3.6 1.7-5.4 0z"/>'
            f'<path d="M19.5 13c-2-1.7-3.6-1.7-5.4 0c2 1.7 3.6 1.7 5.4 0z"/>'
            f'<circle cx="13" cy="13" r="0.85" fill="currentColor" stroke="none"/>'
            f"</g>"
        )
        parts.append(
            f'<pattern id="fl{uid}" width="28" height="28" patternUnits="userSpaceOnUse">'
            f'<g color="{INK}" opacity="0.4">{petal}</g>'
            f'<g color="#fff" opacity="0.35" transform="translate(0.6 0.6)">{petal}</g>'
            f"</pattern>"
        )
    return "".join(parts)


def _overlays(uid, fabric, x, y, w, h, clip):
    bits = []
    if fabric in ("linen", "floral", None, "runner"):
        bits.append(f'<rect {clip} x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#wv{uid})"/>')
    if fabric == "satin":
        bits.append(f'<rect {clip} x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#sh{uid})"/>')
    if fabric == "floral":
        bits.append(f'<rect {clip} x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#fl{uid})"/>')
    return "".join(bits)


def _ticks(x, y, w, h):
    n = 11
    return (
        f'<path fill="none" stroke="{INK}" stroke-width="0.9" '
        f'd="M{x} {y+n}V{y}H{x+n} M{x+w} {y+n}V{y}H{x+w-n} '
        f'M{x} {y+h-n}V{y+h}H{x+n} M{x+w} {y+h-n}V{y+h}H{x+w-n}"/>'
    )


def _cross(cx, cy):
    return (
        f'<path d="M{cx-7} {cy}H{cx+7} M{cx} {cy-7}V{cy+7}" '
        f'fill="none" stroke="{INK}" stroke-width="0.6" opacity="0.4"/>'
    )


def _svg(w, h, body, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{H.escape(label, quote=True)}" '
        f'preserveAspectRatio="xMidYMid meet">{body}</svg>'
    )


def tablecloth(uid, fabric, size, stage=False):
    uid = uid_of(uid)
    if size == "עגולה":
        return _round(uid, fabric, stage)
    wm, hm = SIZES.get(size, (2.2, 2.2))
    ppm = 92 if stage else 84
    pad = 58 if stage else 28
    W = int(round(wm * ppm + pad * 2))
    Hh = int(round(hm * ppm + pad * 2))
    x, y = pad, pad
    w, h = wm * ppm, hm * ppm
    inset = max(12, int(min(w, h) * 0.16))
    label = f"שרטוט מפה {size or ''} {fabric or ''}".strip()
    cloth = (
        f'<defs>{_defs(uid, fabric)}'
        f'<clipPath id="cp{uid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" style="fill:var(--cloth,{CLOTH})"/>'
        f'{_overlays(uid, fabric, x, y, w, h, "")}'
        f'<rect x="{x+inset}" y="{y+inset}" width="{w-inset*2}" height="{h-inset*2}" fill="none" '
        f'stroke="{INK}" stroke-width="0.8" stroke-dasharray="2.2 2.4" opacity="0.55"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="1.35"/>'
        f'{_ticks(x, y, w, h)}{_cross(x+w/2, y+h/2)}'
    )
    if stage and size:
        cloth += (
            f'<text x="{x+w/2}" y="{y+h+28}" text-anchor="middle" '
            f'font-family="Heebo, sans-serif" font-size="14" fill="#3f3a34">{H.escape(size)}</text>'
        )
        Hh = int(Hh + 18)
    return _svg(W, Hh, cloth, label), W, Hh


def _round(uid, fabric, stage):
    d = 250 if stage else 210
    pad = 36
    extra = 28 if stage else 0
    W = d + pad * 2
    Hh = d + pad * 2 + extra
    cx, cy, r = W / 2, pad + d / 2, d / 2
    ri = r * 0.72
    label = "שרטוט מפה עגולה"
    body = (
        f'<defs>{_defs(uid, fabric)}'
        f'<clipPath id="cp{uid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath></defs>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" style="fill:var(--cloth,{CLOTH})"/>'
        f'<g clip-path="url(#cp{uid})">{_overlays(uid, fabric, cx-r, cy-r, d, d, "")}</g>'
        f'<circle cx="{cx}" cy="{cy}" r="{ri}" fill="none" stroke="{INK}" stroke-width="0.8" '
        f'stroke-dasharray="2.2 2.4" opacity="0.55"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="1.35"/>'
        f'{_cross(cx, cy)}'
    )
    if stage:
        body += (
            f'<text x="{cx}" y="{cy+r+26}" text-anchor="middle" '
            f'font-family="Heebo, sans-serif" font-size="14" fill="#3f3a34">עגולה</text>'
        )
    return _svg(W, Hh, body, label), W, Hh


def napkin(uid, fabric, stage=False):
    uid = uid_of(uid)
    W, Hh = (340, 360) if stage else (280, 300)
    x, y, w, h = (W - 168) / 2, 36, 168, 196
    label = "שרטוט מפית מקופלת"
    body = (
        f'<defs>{_defs(uid, fabric)}'
        f'<clipPath id="cp{uid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" style="fill:var(--cloth,{CLOTH})"/>'
        f'{_overlays(uid, fabric, x, y, w, h, "")}'
        f'<path d="M{x} {y+62}H{x+w}" fill="none" stroke="{INK}" stroke-width="0.9" opacity="0.7"/>'
        f'<path d="M{x} {y} L{x+54} {y+62} H{x} Z" fill="none" stroke="{INK}" stroke-width="0.9"/>'
        f'<path d="M{x+w/2} {y} V{y+h}" fill="none" stroke="{INK}" stroke-width="0.6" '
        f'stroke-dasharray="2 2.4" opacity="0.45"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="1.35"/>'
        f'{_ticks(x, y, w, h)}'
    )
    return _svg(W, Hh, body, label), W, Hh


def runner(uid, fabric, stage=False):
    uid = uid_of(uid)
    fab = fabric or "runner"
    W, Hh = (520, 280) if stage else (460, 230)
    tx, ty, tw, th = 28, 36, W - 56, Hh - 88
    rw = th * 0.42
    rx = tx + (tw - rw) / 2
    label = "שרטוט ראנר על שולחן"
    body = (
        f'<defs>{_defs(uid, fab)}'
        f'<clipPath id="cp{uid}"><rect x="{rx}" y="{ty}" width="{rw}" height="{th}"/></clipPath></defs>'
        f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="none" stroke="{INK}" '
        f'stroke-width="0.9" stroke-dasharray="2.4 2.6" opacity="0.6"/>'
        f'<rect x="{rx}" y="{ty}" width="{rw}" height="{th}" style="fill:var(--cloth,{CLOTH})"/>'
        f'{_overlays(uid, fab, rx, ty, rw, th, "")}'
        f'<rect x="{rx}" y="{ty}" width="{rw}" height="{th}" fill="none" stroke="{INK}" stroke-width="1.35"/>'
        f'{_cross(rx+rw/2, ty+th/2)}'
    )
    return _svg(W, Hh, body, label), W, Hh


def chair(uid, stage=False):
    uid = uid_of(uid)
    W, Hh = (300, 380) if stage else (240, 320)
    s = Hh / 320
    def P(v):
        return round(v * s, 1)
    label = "שרטוט כיסוי כיסא"
    # Neutral line drawing. No palette color.
    body = (
        f'<g fill="{PAPER}" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round">'
        f'<path d="M{P(78)} {P(108)} C{P(78)} {P(46)} {P(162)} {P(46)} {P(162)} {P(108)} V{P(132)} H{P(78)} Z"/>'
        f'<path d="M{P(58)} {P(128)} H{P(182)} L{P(196)} {P(286)} H{P(44)} Z"/>'
        f'</g>'
        f'<path d="M{P(86)} {P(100)} C{P(86)} {P(64)} {P(154)} {P(64)} {P(154)} {P(100)}" '
        f'fill="none" stroke="{INK}" stroke-width="0.8" opacity="0.55"/>'
        f'<path d="M{P(64)} {P(176)} H{P(176)}" fill="none" stroke="{INK}" stroke-width="0.8" opacity="0.6"/>'
        f'<path d="M{P(120)} {P(132)} V{P(286)}" fill="none" stroke="{INK}" stroke-width="0.6" opacity="0.35"/>'
        f'<path d="M{P(28)} {P(298)} H{P(212)}" fill="none" stroke="{INK}" stroke-width="0.7" opacity="0.45"/>'
    )
    return _svg(W, Hh, body, label), W, Hh


def setting(uid):
    uid = uid_of(uid)
    W, Hh = 560, 380
    label = "שרטוט עריכת שולחן: מפה, ראנר ומפית"
    cloth = (36, 32, 488, 300)
    rx, ry, rw, rh = 230, 32, 100, 300
    nx, ny, nw, nh = 78, 70, 92, 108
    body = (
        f'<defs>{_defs(uid+"c", "linen")}{_defs(uid+"r", "satin")}{_defs(uid+"n", "linen")}</defs>'
        f'<rect x="{cloth[0]}" y="{cloth[1]}" width="{cloth[2]}" height="{cloth[3]}" fill="{CLOTH}"/>'
        f'<rect x="{cloth[0]}" y="{cloth[1]}" width="{cloth[2]}" height="{cloth[3]}" fill="url(#wv{uid}c)"/>'
        f'<rect x="{cloth[0]}" y="{cloth[1]}" width="{cloth[2]}" height="{cloth[3]}" fill="none" stroke="{INK}" stroke-width="1.3"/>'
        f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{UNDYED}"/>'
        f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="url(#sh{uid}r)"/>'
        f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="none" stroke="{INK}" stroke-width="1.2"/>'
        f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" fill="{CLOTH}"/>'
        f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" fill="url(#wv{uid}n)"/>'
        f'<path d="M{nx} {ny+36}H{nx+nw}" fill="none" stroke="{INK}" stroke-width="0.8"/>'
        f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" fill="none" stroke="{INK}" stroke-width="1.15"/>'
        f'{_ticks(*cloth)}'
    )
    return _svg(W, Hh, body, label), W, Hh


def draw(kind, fabric, size, uid, stage=False):
    if kind == "tablecloth":
        return tablecloth(uid, fabric, size, stage)
    if kind == "napkin":
        return napkin(uid, fabric, stage)
    if kind == "runner":
        return runner(uid, fabric, stage)
    if kind == "chair":
        return chair(uid, stage)
    if kind == "setting":
        return setting(uid)
    raise ValueError(kind)


FABRIC_HE = {"linen": "פשתן", "satin": "סאטן", "floral": "פרחים", "runner": ""}


def caption_for(kind, fabric, size):
    fab = FABRIC_HE.get(fabric or "", "")
    if kind == "tablecloth":
        bits = ["שרטוט מפה"]
        if size:
            bits.append(size)
        if fab:
            bits.append(fab)
        return " · ".join(bits)
    if kind == "napkin":
        return " · ".join(x for x in ("שרטוט מפית מקופלת", fab) if x)
    if kind == "runner":
        return " · ".join(x for x in ("שרטוט ראנר", fab) if x)
    if kind == "chair":
        return "שרטוט כיסוי כיסא"
    return "שרטוט עריכת שולחן"


def figure(kind, fabric, size, uid, stage=False, cls=""):
    svg, w, h = draw(kind, fabric, size, uid, stage)
    cap = caption_for(kind, fabric, size)
    klass = "fig fig-stage" if stage else "fig"
    if cls:
        klass += " " + cls
    return (
        f'<figure class="{klass}" style="--ar:{w}/{h}">'
        f'<div class="frame">{svg}</div>'
        f'<figcaption>{H.escape(cap)}</figcaption>'
        f"</figure>"
    )
