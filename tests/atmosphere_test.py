#!/usr/bin/env python3
"""Atmosphere slots stay off product cards, and the crops follow the focal point."""
import os
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mapot-src"))
import atmosphere  # noqa: E402


fail = []


def bad(msg):
    fail.append(msg)


def test_crop_box():
    box = atmosphere.crop_box(100, 50, (1, 1), (0, 0), (0, 0), 1)
    if box != (0, 0, 50, 50):
        bad(f"top-left square crop {box}")
    right = atmosphere.crop_box(100, 50, (1, 1), (1, 0.5), (0.5, 0.5), 1)
    if right != (50, 0, 100, 50):
        bad(f"right-edge crop {right}")
    full = atmosphere.crop_box(300, 200, (3, 2), (0.2, 0.2), (0.5, 0.5), 1)
    if full != (0, 0, 300, 200):
        bad(f"matching ratio should keep the frame {full}")


def test_slot_files():
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "src"
        dest = Path(d) / "out"
        src.mkdir()
        Image.new("RGB", (40, 30), (120, 90, 70)).save(src / "hero.jpg", quality=80)
        # A lookalike name must not become a second hero, and a subfolder is ignored.
        (src / "nested").mkdir()
        Image.new("RGB", (40, 30), (1, 2, 3)).save(src / "nested" / "hero.jpg")
        ready = atmosphere.plan(str(src))
        if set(ready) != {"hero"}:
            bad(f"expected only hero, got {sorted(ready)}")
        if "events-1" in ready:
            bad("missing events file was planned")
        html = atmosphere.picture(ready, "hero", kind="hero", sizes="100vw", priority=True)
        for needle in (
            'type="image/avif"',
            'type="image/webp"',
            "hero-narrow-480",
            "hero-wide-1920",
            "(max-width: 699px)",
            'alt="אולם חתונה ערוך במפות ארוכות ובמפיות מקופלות"',
            'fetchpriority="high"',
            'sizes="100vw"',
        ):
            if needle not in html:
                bad("hero picture missing " + needle)
        if atmosphere.picture(ready, "events-1", kind="header", sizes="100vw"):
            bad("absent events slot rendered a picture")
        band = atmosphere.picture(ready, "hero", kind="band", sizes="80vw")
        if "max-width" in band or "hero-wide-" in band:
            bad("band picture switched crops")
        atmosphere.render(str(src), str(dest))
        for name in ("hero-narrow-480.avif", "hero-narrow-800.webp", "hero-wide-1280.jpg", "hero-wide-1920.avif"):
            path = dest / name
            if not path.is_file() or path.stat().st_size < 100:
                bad(f"missing derivative {name}")
        with Image.open(dest / "hero-narrow-480.jpg") as im:
            if im.size != (480, 720):
                bad(f"narrow hero size {im.size}")
        with Image.open(dest / "hero-wide-1280.jpg") as im:
            if im.size != (1280, 853) and im.size != (1280, 854):
                # 1280 * 2/3 = 853.333, round half may vary by one pixel
                if im.size[0] != 1280 or abs(im.size[1] - 853) > 1:
                    bad(f"wide hero size {im.size}")


if __name__ == "__main__":
    test_crop_box()
    test_slot_files()
    if fail:
        print("\n".join(fail))
        sys.exit(1)
    print("atmosphere ok")
