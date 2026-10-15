#!/usr/bin/env python3
"""Photo slots: warehouse files stay off cards, product files stay in the gallery."""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mapot-src"))
import build_mapot  # noqa: E402
import media_slot  # noqa: E402

fail = []


def bad(msg):
    fail.append(msg)


def test_listing():
    with tempfile.TemporaryDirectory() as d:
        photos = Path(d) / "photos"
        nested = photos / "nested"
        nested.mkdir(parents=True)
        (photos / ".gitkeep").write_text("", encoding="utf-8")
        (photos / "notes.txt").write_text("x", encoding="utf-8")
        (photos / "TC-LINEN-15X15.jpg").write_bytes(b"a")
        (photos / "TC-LINEN-15X15-2.webp").write_bytes(b"b")
        (photos / "TC-LINEN-15X3.jpg").write_bytes(b"c")
        (photos / "tc-linen-15x3-sign.mp4").write_bytes(b"d")
        (photos / "TC-FLORAL.jpg").write_bytes(b"e")
        (photos / "TC-FLORAL-2.png").write_bytes(b"f")
        (nested / "TC-LINEN-3X3.jpg").write_bytes(b"g")

        wide = media_slot.product_files(str(photos), "TC-LINEN-15X15", "tc-linen-15x15")
        if wide != ["TC-LINEN-15X15.jpg", "TC-LINEN-15X15-2.webp"]:
            bad(f"15x15 matched {wide}")
        narrow = media_slot.product_files(str(photos), "TC-LINEN-15X3", "tc-linen-15x3")
        if narrow != ["TC-LINEN-15X3.jpg", "tc-linen-15x3-sign.mp4"]:
            bad(f"15x3 matched {narrow}")
        floral = media_slot.product_files(str(photos), "TC-FLORAL-*", "tc-floral")
        if floral != ["TC-FLORAL.jpg", "TC-FLORAL-2.png"]:
            bad(f"floral matched {floral}")
        buried = media_slot.product_files(str(photos), "TC-LINEN-3X3", "tc-linen-3x3")
        if buried:
            bad(f"subdirectory leaked into a product: {buried}")

        rng = Path(d) / "range"
        rng.mkdir()
        (rng / ".gitkeep").write_text("", encoding="utf-8")
        (rng / "shelf-a.jpg").write_bytes(b"a")
        (rng / "walk.webm").write_bytes(b"b")
        (rng / "skip.txt").write_text("n", encoding="utf-8")
        (rng / "more").mkdir()
        (rng / "more" / "hidden.jpg").write_bytes(b"c")
        (rng / "TC-LINEN-3X3.jpg").write_bytes(b"z")
        got = media_slot.range_files(str(rng))
        if got != ["shelf-a.jpg", "TC-LINEN-3X3.jpg", "walk.webm"]:
            bad(f"range listed {got}")
        if media_slot.product_files(str(photos), "TC-LINEN-3X3", "tc-linen-3x3"):
            bad("a warehouse file was treated as a product photo")


def test_surfaces():
    for surface in ("card", "hero", "category", "related"):
        if media_slot.files_for_surface(surface, ["a.jpg"]):
            bad(f"{surface} surface returned a file")
    if media_slot.files_for_surface("gallery", ["a.jpg", "b.mp4"]) != ["a.jpg", "b.mp4"]:
        bad("gallery surface dropped product files")
    if media_slot.files_for_surface("gallery", None) != []:
        bad("empty gallery")

    p = {
        "files": ["TC-LINEN-3X3.mp4", "TC-LINEN-3X3.jpg"],
        "type": "tablecloth",
        "sku": "TC-LINEN-3X3",
        "size": "3×3",
        "material": "linen",
        "name_he": "מפה פשתן 3×3",
        "public_colors": [{"key": "c10", "hex": "#6B2A35", "name": "בורדו"}],
    }
    card = build_mapot.plate_for(p, "cardx")
    if "<img" in card or "<video" in card or "media-frame" in card or "<svg" not in card:
        bad("card used a photo")
    hero = build_mapot.plate_for(p, "herox", mode="hero")
    if "<img" in hero or "<video" in hero or "heroimg" not in hero or "<svg" not in hero:
        bad("hero used a photo")
    fallback = build_mapot.plate_for(dict(p, files=[]), "empty")
    if "<svg" not in fallback or "<img" in fallback:
        bad("missing drawn fallback")
    gal = build_mapot.gallery_for(p, "galx")
    if "/mapot/media/TC-LINEN-3X3.jpg" not in gal or "/mapot/media/TC-LINEN-3X3.mp4" not in gal:
        bad("gallery missed a product file")
    if "/mapot/media/range/" in gal:
        bad("gallery pointed at the warehouse slot")
    if gal.count("autoplay") != 1:
        bad(f"gallery autoplay count {gal.count('autoplay')}")
    if build_mapot.range_section([]):
        bad("empty warehouse slot rendered a section")
    sec = build_mapot.range_section(["bags.jpg", "clip.mp4"])
    needles = (
        "צבעים על המדף",
        "המחסן",
        "3×3",
        "1.5×3",
        'alt="מפות ארוזות במחסן"',
        'aria-label="סרטון מהמחסן"',
        "/mapot/media/range/bags.jpg",
        "/mapot/media/range/clip.mp4",
        "controls",
        "playsinline",
    )
    for needle in needles:
        if needle not in sec:
            bad("range section missing " + needle)
    if "autoplay" in sec:
        bad("warehouse video autoplays")
    for banned in ("מלאי", "אנחנו לא", "לבן", "שמנת", "בורדו", "נייבי", "שרטוט"):
        if banned in sec:
            bad("range copy has " + banned)


if __name__ == "__main__":
    test_listing()
    test_surfaces()
    if fail:
        print("\n".join(fail))
        sys.exit(1)
    print("media slot ok")
