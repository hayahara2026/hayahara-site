# Code-rendered cloth. Each product type is its own composition.
# Cards, the home hero, and category plates always use these scenes.
# A future file in mapot-src/photos/ is for the product-page gallery only.
import html as H
import re

CLOTH = "#efe4d2"
GROUND = "#e7dcc8"
INK = "#1c1916"


def uid_of(s):
    return re.sub(r"[^A-Za-z0-9]+", "", str(s)) or "p"


def _defs(uid):
    return (
        f'<defs>'
        f'<filter id="sh{uid}" x="-60%" y="-60%" width="220%" height="220%">'
        f'<feGaussianBlur stdDeviation="16"/>'
        f"</filter>"
        f'<filter id="tx{uid}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
        f'<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" seed="4" result="n"/>'
        f'<feColorMatrix in="n" type="matrix" result="g" values="'
        f"0 0 0 0 0.22  0 0 0 0 0.16  0 0 0 0 0.1  0 0 0 0.28 0\"/>"
        f'<feBlend in="SourceGraphic" in2="g" mode="multiply"/>'
        f"</filter>"
        f'<filter id="wv{uid}" x="-8%" y="-8%" width="116%" height="116%" color-interpolation-filters="sRGB">'
        f'<feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="2" seed="9" result="n"/>'
        f'<feDisplacementMap in="SourceGraphic" in2="n" scale="3" xChannelSelector="R" yChannelSelector="G"/>'
        f"</filter>"
        f'<linearGradient id="lg{uid}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="0.55"/>'
        f'<stop offset="0.38" stop-color="#fff" stop-opacity="0.02"/>'
        f'<stop offset="1" stop-color="#140e0a" stop-opacity="0.38"/>'
        f"</linearGradient>"
        f'<linearGradient id="dk{uid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#140e0a" stop-opacity="0.2"/>'
        f'<stop offset="0.18" stop-color="#140e0a" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="#140e0a" stop-opacity="0.28"/>'
        f"</linearGradient>"
        f"</defs>"
    )


def _svg(body, w, h, fabric):
    fab = fabric if fabric in ("linen", "satin", "floral") else "linen"
    return (
        f'<svg class="{fab}" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
        f"{body}</svg>"
    )


def _fill():
    return f'style="fill:var(--cloth,{CLOTH})"'


def _sheen(uid, d):
    return (
        f'<g clip-path="url(#cp{uid})">'
        f'<rect class="sheen-band" x="-20%" y="0" width="50%" height="100%" fill="url(#lg{uid})" opacity="0.9"/>'
        f"</g>"
    )


def _flowers(uid):
    # A few large blooms, not a tiled stamp.
    spots = [(210, 340, 1), (430, 260, 0.85), (520, 480, 1.1), (300, 560, 0.7), (150, 500, 0.6)]
    parts = []
    for i, (x, y, s) in enumerate(spots):
        parts.append(
            f'<g transform="translate({x} {y}) scale({s})" fill="none" stroke="{INK}" stroke-width="1.4" opacity="0.55">'
            f'<path d="M0-18c6 8 6 14 0 22c-6-8-6-14 0-22z"/>'
            f'<path d="M0 18c6-8 6-14 0-22c-6 8-6 14 0 22z"/>'
            f'<path d="M-18 0c8-6 14-6 22 0c-8 6-14 6-22 0z"/>'
            f'<path d="M18 0c-8-6-14-6-22 0c8 6 14 6 22 0z"/>'
            f'<path d="M-12-12c10 2 14 8 12 16" opacity="0.7"/>'
            f'<circle r="2.2" fill="{INK}" stroke="none"/>'
            f"</g>"
        )
    return "".join(parts)


def square(uid, fabric, w=800, h=1000):
    uid = uid_of(uid)
    cloth = (
        "M70 250 C 160 150, 340 190, 470 140 C 620 90, 730 180, 760 250 "
        "C 790 420, 740 560, 780 760 C 640 820, 470 740, 300 810 "
        "C 160 870, 40 760, 20 620 C 0 430, 40 340, 70 250 Z"
    )
    bloom = _flowers(uid) if fabric == "floral" else ""
    body = (
        f"{_defs(uid)}"
        f'<clipPath id="cp{uid}"><path d="{cloth}"/></clipPath>'
        f'<rect width="{w}" height="{h}" fill="#ddd2c2"/>'
        f'<ellipse cx="400" cy="860" rx="300" ry="46" fill="{INK}" opacity="0.16" filter="url(#sh{uid})"/>'
        f'<path d="{cloth}" {_fill()} filter="url(#tx{uid})"/>'
        f'<path d="M120 300 C 220 420, 200 620, 90 760" fill="none" stroke="#140e0a" stroke-width="28" stroke-linecap="round" opacity="0.1"/>'
        f'<path d="M250 240 C 340 380, 300 640, 210 800" fill="none" stroke="#fff" stroke-width="22" stroke-linecap="round" opacity="0.16"/>'
        f'<path d="M480 180 C 560 360, 520 600, 610 780" fill="none" stroke="#140e0a" stroke-width="18" stroke-linecap="round" opacity="0.12"/>'
        f'<path d="{cloth}" fill="url(#lg{uid})"/>'
        f'<path d="{cloth}" fill="url(#dk{uid})"/>'
        f"{bloom}"
        f'<path d="M760 250 C 790 420, 740 560, 780 760 C 640 820, 470 740, 300 810 C 160 870, 40 760, 20 620" fill="none" stroke="#140e0a" stroke-width="10" opacity="0.15"/>'
        f"{_sheen(uid, cloth)}"
    )
    return _svg(body, w, h, fabric)


def banquet(uid, fabric):
    uid = uid_of(uid)
    # Long cloth seen from the near end: empty floor above, deep vertical folds below.
    top = "M40 300 C 180 250, 400 280, 620 240 C 700 230, 760 260, 780 300"
    hang = (
        "M40 300 C 180 250, 400 280, 620 240 C 700 230, 760 260, 780 300 "
        "L 800 980 L 0 980 L 40 300 Z"
    )
    body = (
        f"{_defs(uid)}"
        f'<clipPath id="cp{uid}"><path d="{hang}"/></clipPath>'
        f'<rect width="800" height="1000" fill="#d9cebc"/>'
        f'<ellipse cx="400" cy="300" rx="340" ry="28" fill="{INK}" opacity="0.13" filter="url(#sh{uid})"/>'
        f'<path d="{hang}" {_fill()} filter="url(#tx{uid})"/>'
        f'<path d="M150 300 C 130 520, 170 760, 110 980" fill="none" stroke="#140e0a" stroke-width="36" opacity="0.12" stroke-linecap="round"/>'
        f'<path d="M300 280 C 320 500, 260 740, 340 990" fill="none" stroke="#fff" stroke-width="26" opacity="0.14" stroke-linecap="round"/>'
        f'<path d="M520 250 C 490 520, 560 760, 500 990" fill="none" stroke="#140e0a" stroke-width="30" opacity="0.1" stroke-linecap="round"/>'
        f'<path d="M680 270 C 710 540, 650 780, 730 990" fill="none" stroke="#fff" stroke-width="18" opacity="0.12" stroke-linecap="round"/>'
        f'<path d="{hang}" fill="url(#dk{uid})"/>'
        f'<path d="{top}" fill="none" stroke="#fff" stroke-width="3" opacity="0.35"/>'
        f"{_sheen(uid, hang)}"
    )
    return _svg(body, 800, 1000, fabric)


def round_cloth(uid, fabric):
    uid = uid_of(uid)
    body = (
        f"{_defs(uid)}"
        f'<clipPath id="cp{uid}"><circle cx="400" cy="470" r="300"/></clipPath>'
        f'<rect width="800" height="1000" fill="#e3d7c6"/>'
        f'<ellipse cx="400" cy="800" rx="250" ry="36" fill="{INK}" opacity="0.18" filter="url(#sh{uid})"/>'
        f'<circle cx="400" cy="500" r="330" fill="#140e0a" opacity="0.18"/>'
        f'<circle cx="400" cy="470" r="300" {_fill()} filter="url(#tx{uid})"/>'
        f'<path d="M400 180 C 460 300, 430 520, 400 760" fill="none" stroke="#140e0a" stroke-width="22" opacity="0.1"/>'
        f'<path d="M180 400 C 300 450, 520 430, 680 500" fill="none" stroke="#fff" stroke-width="18" opacity="0.14"/>'
        f'<path d="M230 260 C 300 360, 280 520, 210 640" fill="none" stroke="#140e0a" stroke-width="16" opacity="0.1"/>'
        f'<path d="M560 240 C 520 400, 600 560, 640 700" fill="none" stroke="#fff" stroke-width="14" opacity="0.12"/>'
        f'<circle cx="400" cy="470" r="300" fill="url(#lg{uid})"/>'
        f'<circle cx="400" cy="470" r="300" fill="none" stroke="#140e0a" stroke-width="8" opacity="0.12"/>'
        f"{_sheen(uid, '')}"
    )
    return _svg(body, 800, 1000, fabric)


def floral_cloth(uid, fabric):
    uid = uid_of(uid)
    cloth = (
        "M60 220 C 200 150, 420 200, 760 180 L 790 820 C 600 880, 300 800, 40 860 "
        "C 20 560, 30 360, 60 220 Z"
    )
    # Turned-back corner, underside lighter.
    flap = "M560 180 L 790 180 L 790 420 C 700 300, 620 240, 560 180 Z"
    body = (
        f"{_defs(uid)}"
        f'<clipPath id="cp{uid}"><path d="{cloth}"/></clipPath>'
        f'<rect width="800" height="1000" fill="#e6dcc8"/>'
        f'<ellipse cx="420" cy="860" rx="280" ry="40" fill="{INK}" opacity="0.15" filter="url(#sh{uid})"/>'
        f'<path d="{cloth}" {_fill()} filter="url(#tx{uid})"/>'
        f'<path d="M140 260 C 180 460, 120 680, 90 840" fill="none" stroke="#140e0a" stroke-width="24" opacity="0.1" stroke-linecap="round"/>'
        f'<path d="M360 200 C 400 420, 340 680, 390 860" fill="none" stroke="#fff" stroke-width="18" opacity="0.13" stroke-linecap="round"/>'
        f"{_flowers(uid)}"
        f'<path d="{flap}" fill="#f4efe6" filter="url(#tx{uid})"/>'
        f'<path d="M560 180 C 640 250, 720 320, 790 420" fill="none" stroke="#140e0a" stroke-width="6" opacity="0.2"/>'
        f'<path d="{cloth}" fill="url(#lg{uid})"/>'
        f"{_sheen(uid, cloth)}"
    )
    return _svg(body, 800, 1000, fabric or "floral")


def napkin(uid, fabric):
    uid = uid_of(uid)
    # Macro of a thick fold. Almost no background.
    a = "M-20 180 L 820 40 L 820 620 L -20 760 Z"
    b = "M-20 430 L 820 300 L 820 1040 L -20 1040 Z"
    body = (
        f"{_defs(uid)}"
        f'<clipPath id="cp{uid}"><rect width="800" height="1000"/></clipPath>'
        f'<rect width="800" height="1000" fill="#d8cebc"/>'
        f'<path d="{b}" {_fill()} filter="url(#tx{uid})"/>'
        f'<path d="{b}" fill="url(#dk{uid})"/>'
        f'<path d="{a}" {_fill()} filter="url(#tx{uid})"/>'
        f'<path d="M0 180 L 820 40" fill="none" stroke="#fff" stroke-width="8" opacity="0.45"/>'
        f'<path d="M0 430 L 820 300" fill="none" stroke="#140e0a" stroke-width="10" opacity="0.2"/>'
        f'<path d="M80 200 C 200 360, 160 640, 60 900" fill="none" stroke="#fff" stroke-width="20" opacity="0.16" stroke-linecap="round"/>'
        f'<path d="M520 80 C 560 300, 500 620, 580 980" fill="none" stroke="#140e0a" stroke-width="16" opacity="0.1" stroke-linecap="round"/>'
        f'<path d="{a}" fill="url(#lg{uid})"/>'
        f"{_sheen(uid, a)}"
    )
    return _svg(body, 800, 1000, fabric)


def napkin_stack(uid, fabric):
    uid = uid_of(uid)
    layers = []
    for i, y in enumerate((180, 300, 430, 560)):
        layers.append(
            f'<path d="M90 {y} L 700 {y+30} L 680 {y+150} L 110 {y+130} Z" {_fill()} '
            f'filter="url(#tx{uid})" opacity="{0.92 - i * 0.08}"/>'
            f'<path d="M90 {y} L 700 {y+30}" fill="none" stroke="#fff" stroke-width="4" opacity="0.4"/>'
        )
    body = (
        f"{_defs(uid)}"
        f'<clipPath id="cp{uid}"><rect width="800" height="1000"/></clipPath>'
        f'<rect width="800" height="1000" fill="#e5d9c6"/>'
        f'<ellipse cx="400" cy="820" rx="260" ry="30" fill="{INK}" opacity="0.14" filter="url(#sh{uid})"/>'
        f'{"".join(layers)}'
        f"{_sheen(uid, '')}"
    )
    return _svg(body, 800, 1000, fabric)


def runner(uid, fabric):
    uid = uid_of(uid)
    # Diagonal band, cropped by the frame. Ground is undyed.
    band = "M180 -40 L 460 -40 L 700 1040 L 420 1040 Z"
    body = (
        f"{_defs(uid)}"
        f'<clipPath id="cp{uid}"><path d="{band}"/></clipPath>'
        f'<rect width="800" height="1000" fill="#efe6d4"/>'
        f'<path d="M0 0 H800 V1000 H0 Z" fill="#efe6d4" filter="url(#tx{uid})" opacity="0.9"/>'
        f'<path d="{band}" {_fill()} filter="url(#tx{uid})"/>'
        f'<path d="M260 0 C 300 250, 250 520, 320 1000" fill="none" stroke="#fff" stroke-width="16" opacity="0.18" stroke-linecap="round"/>'
        f'<path d="M400 0 C 430 300, 380 640, 450 1000" fill="none" stroke="#140e0a" stroke-width="14" opacity="0.12" stroke-linecap="round"/>'
        f'<path d="M180 -40 L 420 1040" fill="none" stroke="#140e0a" stroke-width="6" opacity="0.18"/>'
        f'<path d="M460 -40 L 700 1040" fill="none" stroke="#fff" stroke-width="4" opacity="0.25"/>'
        f'<path d="{band}" fill="url(#lg{uid})"/>'
        f"{_sheen(uid, band)}"
    )
    return _svg(body, 800, 1000, fabric)


def weave(uid, fabric):
    uid = uid_of(uid)
    body = (
        f"{_defs(uid)}"
        f'<clipPath id="cp{uid}"><rect width="800" height="1000"/></clipPath>'
        f'<rect width="800" height="1000" {_fill()} filter="url(#wv{uid})"/>'
        f'<rect width="800" height="1000" {_fill()} filter="url(#tx{uid})" opacity="0.85"/>'
        f'<path d="M-40 280 C 200 180, 420 420, 860 300 L 860 560 C 400 700, 160 420, -40 560 Z" fill="#140e0a" opacity="0.13"/>'
        f'<path d="M-40 300 C 220 200, 440 430, 860 320" fill="none" stroke="#fff" stroke-width="18" opacity="0.2" stroke-linecap="round"/>'
        f'<rect width="800" height="1000" fill="url(#lg{uid})"/>'
        f"{_sheen(uid, '')}"
    )
    return _svg(body, 800, 1000, fabric)


def pairing(uid, fabric):
    uid = uid_of(uid)
    # Corner of a table: cloth, a runner entering from the top, a folded napkin. No plate.
    cloth = "M0 120 L 800 60 L 800 1000 L 0 1000 Z"
    band = "M300 -20 L 470 -20 L 430 1040 L 250 1040 Z"
    nap = "M70 560 L 340 520 L 380 860 L 90 910 Z"
    body = (
        f"{_defs(uid)}"
        f'<clipPath id="cp{uid}"><path d="{cloth}"/></clipPath>'
        f'<rect width="800" height="1000" fill="#ddd4c4"/>'
        f'<path d="{cloth}" {_fill()} filter="url(#tx{uid})"/>'
        f'<path d="M80 200 C 120 480, 60 720, 40 1000" fill="none" stroke="#140e0a" stroke-width="20" opacity="0.1" stroke-linecap="round"/>'
        f'<path d="{band}" fill="#f6f1e6" filter="url(#tx{uid})"/>'
        f'<path d="M330 0 C 360 300, 320 640, 370 1000" fill="none" stroke="#140e0a" stroke-width="8" opacity="0.12"/>'
        f'<path d="{nap}" {_fill()} filter="url(#tx{uid})"/>'
        f'<path d="M70 560 L 340 520" fill="none" stroke="#fff" stroke-width="5" opacity="0.4"/>'
        f'<path d="M120 640 L 360 610" fill="none" stroke="#140e0a" stroke-width="8" opacity="0.12"/>'
        f'<path d="{cloth}" fill="url(#lg{uid})"/>'
        f"{_sheen(uid, cloth)}"
    )
    return _svg(body, 800, 1000, fabric)


def measure(uid, fabric, size):
    uid = uid_of(uid)
    label = H.escape(size or "", quote=True)
    if size == "עגולה":
        shape = f'<circle cx="400" cy="430" r="220" {_fill()} filter="url(#tx{uid})"/>'
        shape += f'<circle cx="400" cy="430" r="220" fill="url(#lg{uid})"/>'
    elif size == "1.5×3":
        shape = f'<rect x="80" y="360" width="640" height="220" {_fill()} filter="url(#tx{uid})"/>'
        shape += f'<rect x="80" y="360" width="640" height="220" fill="url(#lg{uid})"/>'
    else:
        shape = f'<rect x="170" y="250" width="460" height="460" {_fill()} filter="url(#tx{uid})"/>'
        shape += f'<rect x="170" y="250" width="460" height="460" fill="url(#lg{uid})"/>'
    body = (
        f"{_defs(uid)}"
        f'<clipPath id="cp{uid}"><rect width="800" height="1000"/></clipPath>'
        f'<rect width="800" height="1000" fill="#f3efe6"/>'
        f'<ellipse cx="400" cy="760" rx="220" ry="24" fill="{INK}" opacity="0.1" filter="url(#sh{uid})"/>'
        f"{shape}"
        f'<text x="400" y="860" text-anchor="middle" font-family="Heebo, sans-serif" font-size="42" fill="{INK}">{label}</text>'
    )
    return _svg(body, 800, 1000, fabric)


def fold_corner(uid, fabric):
    uid = uid_of(uid)
    cloth = "M0 0 H800 V1000 H0 Z"
    flap = "M430 0 L 800 0 L 800 390 C 680 240, 540 120, 430 0 Z"
    body = (
        f"{_defs(uid)}"
        f'<clipPath id="cp{uid}"><rect width="800" height="1000"/></clipPath>'
        f'<path d="{cloth}" {_fill()} filter="url(#tx{uid})"/>'
        f'<path d="{flap}" fill="#f7f1e6" filter="url(#tx{uid})"/>'
        f'<path d="M430 0 C 560 140, 690 250, 800 390" fill="none" stroke="#140e0a" stroke-width="8" opacity="0.2"/>'
        f'<path d="M120 80 C 180 300, 100 620, 80 980" fill="none" stroke="#140e0a" stroke-width="22" opacity="0.1" stroke-linecap="round"/>'
        f'<path d="{cloth}" fill="url(#lg{uid})"/>'
        f"{_sheen(uid, cloth)}"
    )
    return _svg(body, 800, 1000, fabric)


def hero(uid, fabric):
    uid = uid_of(uid)
    # Wide, low angle. Folds come toward the camera. No plate, no frame.
    sheet = (
        "M0 180 C 280 80, 700 140, 1100 60 C 1360 10, 1540 80, 1600 140 "
        "L 1600 820 L 0 820 Z"
    )
    body = (
        f"{_defs(uid)}"
        f'<clipPath id="cp{uid}"><path d="{sheet}"/></clipPath>'
        f'<rect width="1600" height="820" fill="#cfc3ae"/>'
        f'<path d="{sheet}" {_fill()} filter="url(#tx{uid})"/>'
        f'<path d="M180 200 C 140 400, 220 600, 80 820" fill="none" stroke="#140e0a" stroke-width="46" opacity="0.12" stroke-linecap="round"/>'
        f'<path d="M460 140 C 500 380, 400 600, 520 820" fill="none" stroke="#fff" stroke-width="34" opacity="0.16" stroke-linecap="round"/>'
        f'<path d="M860 90 C 800 360, 940 580, 780 820" fill="none" stroke="#140e0a" stroke-width="40" opacity="0.1" stroke-linecap="round"/>'
        f'<path d="M1200 70 C 1280 340, 1160 580, 1320 820" fill="none" stroke="#fff" stroke-width="28" opacity="0.14" stroke-linecap="round"/>'
        f'<path d="{sheet}" fill="url(#dk{uid})"/>'
        f'<path d="M0 180 C 280 80, 700 140, 1100 60 C 1360 10, 1540 80, 1600 140" fill="none" stroke="#fff" stroke-width="4" opacity="0.35"/>'
        f"{_sheen(uid, sheet)}"
    )
    return _svg(body, 1600, 820, fabric)


def chair(uid, view):
    uid = uid_of(uid)
    # Neutrals only. No palette color and no --cloth.
    if view == "texture":
        body = (
            f"{_defs(uid)}"
            f'<clipPath id="cp{uid}"><rect width="800" height="1000"/></clipPath>'
            f'<rect width="800" height="1000" fill="#f3eee4" filter="url(#wv{uid})"/>'
            f'<rect width="800" height="1000" fill="#efe6d6" opacity="0.55"/>'
            f'<path d="M-20 360 C 220 260, 480 520, 840 340 L 840 620 C 460 820, 180 500, -20 640 Z" fill="#d9d0c2" opacity="0.85"/>'
            f'<path d="M-20 380 C 240 280, 500 530, 840 360" fill="none" stroke="#fff" stroke-width="16" opacity="0.35"/>'
        )
        return _svg(body, 800, 1000, "linen")
    shift = ' transform="translate(70 20) rotate(8 400 500)"' if view == "angle" else ""
    body = (
        f"{_defs(uid)}"
        f'<rect width="800" height="1000" fill="#e7dcc8"/>'
        f'<g{shift}>'
        f'<ellipse cx="400" cy="900" rx="210" ry="28" fill="{INK}" opacity="0.16" filter="url(#sh{uid})"/>'
        f'<path d="M230 250 C 230 120, 570 120, 570 250 L 590 430 L 210 430 Z" fill="#f7f2e8" filter="url(#tx{uid})"/>'
        f'<path d="M250 230 C 250 160, 550 160, 550 230" fill="none" stroke="#d9d0c2" stroke-width="10" opacity="0.8"/>'
        f'<path d="M175 400 L 625 400 L 690 900 L 110 900 Z" fill="#f4efe6" filter="url(#tx{uid})"/>'
        f'<path d="M230 400 L 250 900" fill="none" stroke="#cfc6b6" stroke-width="18" opacity="0.7"/>'
        f'<path d="M400 400 L 400 900" fill="none" stroke="#fff" stroke-width="22" opacity="0.35"/>'
        f'<path d="M560 400 L 575 900" fill="none" stroke="#cfc6b6" stroke-width="16" opacity="0.65"/>'
        f'<path d="M300 430 C 340 500, 460 500, 500 430 C 470 470, 330 470, 300 430 Z" fill="#e5dccb"/>'
        f'<path d="M175 400 L 625 400 L 690 900 L 110 900 Z" fill="url(#dk{uid})" opacity="0.45"/>'
        f"</g>"
    )
    return _svg(body, 800, 1000, "linen")


def card_view(kind, fabric, size):
    if kind == "chair":
        return "front"
    if kind == "napkin":
        return "nap"
    if kind == "runner":
        return "run"
    if kind == "setting":
        return "hero"
    if size == "עגולה":
        return "round"
    if size == "1.5×3":
        return "banquet"
    if fabric == "floral":
        return "floral"
    return "square"


def views_for(kind, fabric, size):
    if kind == "chair":
        return [("front", "כיסוי"), ("angle", "צד"), ("texture", "מרקם")]
    if kind == "napkin":
        return [("nap", "קיפול"), ("weave", "אריג"), ("stack", "ערימה"), ("set", "עריכה")]
    if kind == "runner":
        return [("run", "ראנר"), ("weave", "אריג"), ("set", "עריכה")]
    out = [("table", "שולחן"), ("weave", "אריג")]
    if size:
        out.append(("measure", "מידה"))
    else:
        out.append(("fold", "קפל"))
    out.append(("set", "עריכה"))
    return out


def render_view(kind, fabric, size, uid, view):
    uid = uid_of(uid)
    if kind == "chair" or view in ("front", "angle", "texture"):
        return chair(uid, "front" if view == "front" else view)
    if view == "hero":
        return hero(uid, fabric)
    if view in ("round",) or (view == "table" and size == "עגולה"):
        return round_cloth(uid, fabric)
    if view in ("banquet",) or (view == "table" and size == "1.5×3"):
        return banquet(uid, fabric)
    if view in ("floral",) or (view == "table" and fabric == "floral"):
        return floral_cloth(uid, fabric)
    if view == "table":
        return square(uid, fabric)
    if view == "nap":
        return napkin(uid, fabric)
    if view == "stack":
        return napkin_stack(uid, fabric)
    if view == "run":
        return runner(uid, fabric)
    if view == "weave":
        return weave(uid, fabric)
    if view == "measure":
        return measure(uid, fabric, size)
    if view == "fold":
        return fold_corner(uid, fabric)
    if view == "set":
        if kind == "napkin":
            return pairing(uid, fabric)
        if kind == "runner":
            return pairing(uid + "r", fabric)
        return pairing(uid, fabric)
    return square(uid, fabric)
