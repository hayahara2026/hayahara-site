"""Owner media slots. Listing only: this module does not build the site.

photos/  future dressed-table or single-product files, top of the folder,
         named by SKU. The product-page gallery is the only place they appear.

range/   warehouse stills and the short warehouse video. Never matched to a
         product, and never used on a card or the hero.
"""
import os
import re

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
VIDEO_EXT = {".mp4", ".webm"}
MEDIA_EXT = PHOTO_EXT | VIDEO_EXT
# Cards, the home hero, category plates, and related cards stay drawn scenes.
SCENE_SURFACES = {"card", "hero", "category", "related"}


def is_video(name):
    return os.path.splitext(name)[1].lower() in VIDEO_EXT


def list_files(folder):
    """Top-level media files. Directories, dotfiles, and other types are skipped."""
    if not folder or not os.path.isdir(folder):
        return []
    found = []
    for name in os.listdir(folder):
        if not name or name.startswith("."):
            continue
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            continue
        if os.path.splitext(name)[1].lower() not in MEDIA_EXT:
            continue
        found.append(name)
    found.sort(key=str.lower)
    return found


def _stems(sku, slug):
    stems = []
    for raw in (sku, re.sub(r"[^A-Za-z0-9_-]+", "", sku or ""), slug):
        low = (raw or "").lower()
        if low and low not in stems:
            stems.append(low)
    return stems


def _matches(base, stem):
    """Exact, or stem plus a hyphen or underscore.

    TC-LINEN-15X3 must not claim TC-LINEN-15X15.
    """
    low = base.lower()
    stem = (stem or "").lower()
    if not stem:
        return False
    if low == stem:
        return True
    return low.startswith(stem + "-") or low.startswith(stem + "_")


def product_files(folder, sku, slug):
    stems = _stems(sku, slug)
    found = []
    for name in list_files(folder):
        base = os.path.splitext(name)[0]
        if any(_matches(base, stem) for stem in stems):
            found.append(name)

    def rank(name):
        base = os.path.splitext(name)[0].lower()
        exact = 0 if base in stems else 1
        return (exact, name.lower())

    found.sort(key=rank)
    return found


def range_files(folder):
    return list_files(folder)


def files_for_surface(surface, product_files_):
    """Product files reach the product gallery only. Every other surface stays a scene."""
    if surface in SCENE_SURFACES:
        return []
    if surface == "gallery":
        return list(product_files_ or [])
    return []
