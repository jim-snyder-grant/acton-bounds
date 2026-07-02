"""
Acton Bounds Report — Cover Page
SimpInkScr script for Inkscape

Usage:
  1. Install SimpInkScr extension in Inkscape
     (https://github.com/spakin/SimpInkScr)
  2. Create ~/.acton_bounds_base_path (one line, no trailing slash) with the
     path to the directory that CONTAINS your "Bounds" folder, e.g.:
       ~/Insync/you@example.com/GoogleDrive/Board
     (this file lives outside the repo and is never committed -- see below)
  3. Open Inkscape with a blank letter-size document (8.5 x 11 in)
  4. Extensions > Render > Simple Inkscape Scripting
  5. Paste or load this script and click Apply

After running, all objects are live Inkscape objects —
move, resize, swap, or delete any of them by hand.
"""

import os
import random
import tempfile
import shutil
from PIL import Image as PILImage

# ── Configuration ──────────────────────────────────────────────────────────────

# The real base path lives in a local file outside the repo (not
# ~/path/to-style placeholders committed here) since this script is public
# on GitHub. Using a fixed home-directory dotfile rather than a path
# relative to this script's own location, since Inkscape's Simple Inkscape
# Scripting console may run pasted/loaded code with an unpredictable
# working directory -- __file__-relative lookups aren't reliable here.
BASE_PATH_FILE = os.path.expanduser("~/.acton_bounds_base_path")


def _load_base_path():
    if not os.path.exists(BASE_PATH_FILE):
        raise SystemExit(
            f"{BASE_PATH_FILE} not found -- create it with the path to the "
            f"directory that contains your Bounds folder, on a single line, "
            f"e.g.:\n  ~/Insync/you@example.com/GoogleDrive/Board"
        )
    with open(BASE_PATH_FILE, encoding="utf-8") as f:
        return os.path.expanduser(f.read().strip())


_BASE = _load_base_path()
PHOTO_DIR = os.path.join(_BASE, "Bounds", "Photos", "Monument Photos")

# Acton seal — local copy (download from https://actonma.gov/ImageRepository/Document?documentId=10424)
SEAL_PATH = os.path.join(_BASE, "Bounds", "acton_seal.png")
# SEAL_PATH = "https://actonma.gov/ImageRepository/Document?documentId=10424"

# Random seed — change this to get a different arrangement of tilts
RANDOM_SEED = 42

# Maximum pixel dimension for cover photos (width or height).
# At 300dpi letter size, portrait slots are ~360px wide and landscape ~490px wide.
# 800px gives comfortable quality with headroom for the tilt/overlap rendering.
MAX_COVER_PX = 800

# Temp directory for downscaled copies — created fresh each run
TEMP_DIR = tempfile.mkdtemp(prefix='acton_cover_')

def prep_image(fname):
    """Return path to a downscaled copy of fname suitable for the cover.
    Creates a JPEG in TEMP_DIR, reusing it if already created this run."""
    src = os.path.join(PHOTO_DIR, fname)
    # Use a safe flat filename (replace path separators and spaces)
    safe = fname.replace('/', '_').replace(' ', '_')
    # Ensure .jpg extension for PIL output
    safe = os.path.splitext(safe)[0] + '.jpg'
    dst = os.path.join(TEMP_DIR, safe)
    if not os.path.exists(dst):
        try:
            with PILImage.open(src) as im:
                im = im.convert('RGB')  # handles PNGs with alpha
                im.thumbnail((MAX_COVER_PX, MAX_COVER_PX), PILImage.LANCZOS)
                im.save(dst, 'JPEG', quality=88)
        except Exception as e:
            print(f"Warning: could not prep {fname}: {e}")
            return src  # fall back to original
    return dst

def prep_seal(path):
    """Return path to a downscaled copy of the seal."""
    dst = os.path.join(TEMP_DIR, 'acton_seal.png')
    if not os.path.exists(dst):
        try:
            with PILImage.open(path) as im:
                im.thumbnail((400, 400), PILImage.LANCZOS)
                im.save(dst)
        except Exception as e:
            print(f"Warning: could not prep seal: {e}")
            return path
    return dst

# ── Photo selections ────────────────────────────────────────────────────────────
# 10 landscape photos for top (5) and bottom (5) strips.
# One per monument where possible; no two adjacent from same location.
# Deliberately excludes "no monument found" context shots.

TOP_PHOTOS = [
    "Acton-Boxborough Littlefield Road, 2025-11-06 14-15, 2.jpg",
    "Acton-Littleton 2, 2025-05-19 16-44, Nagog Pond is in the back.jpg",
    "Acton-Concord Laws Brook Road, 2025-04-23 16-21, Looking from Concord into Acton.jpg",
    "Acton-Littleton 1, 2025-03-25 10-37, 2.jpg",
    "Acton-Maynard Conant Street, 2025-07-24 10-05.jpg",
]

BOTTOM_PHOTOS = [
    "Acton-Boxborough-Stow, 2024-06-28 15-13.jpg",
    "Acton-Concord Keefe Road, 2025-11-28 14-57, 3.jpg",
    "Acton-Concord Old Stow Road, 2025-09-24 11-04.jpg",
    "Acton-Littleton Nagog Hill Road, 2025-06-02 13-16, Observers  and painters.jpg",
    "Acton-Maynard Parker Street, 2025-07-24 09-31.jpg",
]

# 10 portrait photos, 5 per side.
# Spread across different boundary lines (Boxborough, Carlisle, Concord,
# Littleton, Maynard, Stow borders all represented).

LEFT_PHOTOS = [
    "Acton-Boxborough Central Street, 2024-10-22 18-03.jpg",
    "Acton-Carlisle Main Street (Rte 27), 2024-10-30 12-22.jpg",
    "Acton-Concord Great Road, 2025-04-23 16-44, 2.jpg",
    "Acton-Littleton Fort Pond Road, 2025-03-25 10-18, 2.jpg",
    "Acton-Maynard Main Street (Rte 27), 2024-10-18 10-48.jpg",
]

RIGHT_PHOTOS = [
    "Acton-Boxborough-Stow, 2024-06-28 15-11.jpg",
    "Acton-Concord Old Stow Road, 2025-04-23 15-52, Old road visible to the left of the monument.jpg",
    "Acton-Concord-Maynard-Sudbury, 2024-10-14 15-49.jpg",
    "Acton-Littleton Newtown Road, 2024-10-26 17-12.jpg",
    "Acton-Maynard-Stow, 2025-07-24 10-32, Painted.jpg",  # Stow border, replaces duplicate Maynard
]

# ── Layout constants (in px at 96dpi; canvas is letter = 816 x 1056 px) ───────

random.seed(RANDOM_SEED)

W = float(canvas.width)
H = float(canvas.height)

# Portrait photo dimensions (shown on sides)
P_W = W * 0.14
P_H = P_W * 1.4

# Landscape photo dimensions (shown on top/bottom) — larger to fill corners
L_W = W * 0.205
L_H = L_W * 0.72

# White border around each photo
BORDER = 3

# Inner clear zone (the central area reserved for the title)
INNER_L = W * 0.19
INNER_R = W * 0.81
INNER_T = H * 0.23
INNER_B = H * 0.77

# Margin from page edge for outermost photo centres
MARGIN = W * 0.025

# Tilt ranges (degrees)
SIDE_TILT   = 15   # portraits on sides: ±15°
STRIP_TILT  = 12   # landscapes on top/bottom: ±12°

# ── Helper: place one photo with white border ───────────────────────────────────

def place_photo(fname, cx, cy, target_w, target_h, tilt):
    """Place a photo centred at (cx, cy), scaled to (target_w x target_h),
    rotated by tilt degrees. A white rectangle behind it simulates a border."""
    fpath = prep_image(fname)

    # Get native image dimensions so we can compute the scale factor
    try:
        with PILImage.open(fpath) as pil_img:
            native_w, native_h = pil_img.size
    except Exception as e:
        print(f"Warning: could not open {fname}: {e}")
        return

    scale_factor = target_w / native_w

    # Top-left corner of the photo in page coordinates
    x0 = cx - target_w / 2
    y0 = cy - target_h / 2

    # White border rect (slightly larger than target, centred)
    bw = target_w + BORDER * 2
    bh = target_h + BORDER * 2
    bdr = rect(
        (cx - bw / 2, cy - bh / 2),
        (cx + bw / 2, cy + bh / 2),
        fill='white',
        stroke='none',
    )
    bdr.rotate(tilt, (cx, cy))

    # Use a combined SVG transform: translate to final position, then scale.
    # SVG transforms apply right-to-left, so "translate then scale" in the
    # string means scale is applied first (shrinks native image to target size),
    # then translate moves the already-scaled image to (x0, y0).
    transform_str = f'translate({x0},{y0}) scale({scale_factor})'
    img = image(fpath, (0, 0), embed=True, transform=transform_str)
    img.rotate(tilt, (cx, cy))


# ── Background (must be first so everything else paints on top) ────────────────
rect((0, 0), (W, H), fill='#f5f2ec', stroke='none')

# ── Place side portraits ────────────────────────────────────────────────────────

def place_side(photos, x_centre, inner_top, inner_bot):
    """Distribute portrait photos evenly along one side."""
    n = len(photos)
    # Spread from inner_top to inner_bot, centred vertically
    span = inner_bot - inner_top
    step = span / (n - 1) if n > 1 else 0
    for i, fname in enumerate(photos):
        cy = inner_top + i * step
        tilt = random.uniform(-SIDE_TILT, SIDE_TILT)
        place_photo(fname, x_centre, cy, P_W, P_H, tilt)

# Left side: centre of photos at x = MARGIN + P_W/2
place_side(LEFT_PHOTOS,  MARGIN + P_W / 2,          INNER_T, INNER_B)
# Right side
place_side(RIGHT_PHOTOS, W - MARGIN - P_W / 2,      INNER_T, INNER_B)


# ── Place top/bottom landscapes ─────────────────────────────────────────────────

def place_strip(photos, y_centre, inner_left, inner_right):
    """Distribute landscape photos evenly along top or bottom strip."""
    n = len(photos)
    span = inner_right - inner_left
    step = span / (n - 1) if n > 1 else 0
    for i, fname in enumerate(photos):
        cx = inner_left + i * step
        tilt = random.uniform(-STRIP_TILT, STRIP_TILT)
        place_photo(fname, cx, y_centre, L_W, L_H, tilt)

# Top strip: centre of photos at y = MARGIN + L_H/2
place_strip(TOP_PHOTOS,    MARGIN + L_H / 2,         INNER_L, INNER_R)
# Bottom strip
place_strip(BOTTOM_PHOTOS, H - MARGIN - L_H / 2,     INNER_L, INNER_R)


# ── Centre area: seal + title ───────────────────────────────────────────────────

cx = W / 2
cy = H / 2

# Thin horizontal rules bracketing the title block
# Wider: span the full title text width
rule_w = (INNER_R - INNER_L) * 0.72
rule_color = '#8a7a5a'
# Moved closer to the title text
rule_y_top = cy - H * 0.085
rule_y_bot = cy + H * 0.075

line((cx - rule_w/2, rule_y_top), (cx + rule_w/2, rule_y_top),
     stroke=rule_color, stroke_width=0.75)
line((cx - rule_w/2, rule_y_bot), (cx + rule_w/2, rule_y_bot),
     stroke=rule_color, stroke_width=0.75)

# Acton seal — 50% larger than before
seal_size = W * 0.18
try:
    seal_src = prep_seal(SEAL_PATH)
    with PILImage.open(seal_src) as pil_seal:
        seal_native_w, _ = pil_seal.size
    seal_scale = seal_size / seal_native_w
    seal_x = cx - seal_size / 2
    seal_y = rule_y_top - seal_size - H * 0.018
    seal_transform = f'translate({seal_x},{seal_y}) scale({seal_scale})'
    image(seal_src, (0, 0), embed=True, transform=seal_transform)
except Exception as e:
    print(f"Warning: could not place seal: {e}")

# Main title
text(
    'Acton Bounds Report',
    (cx, cy - H * 0.015),
    text_anchor='middle',
    font_family='Georgia, "Times New Roman", serif',
    font_size='7pt',
    font_weight='bold',
    fill='#1a1a1a',
)

# Year subtitle
text(
    '2025\u20132026',
    (cx, cy + H * 0.038),
    text_anchor='middle',
    font_family='Georgia, "Times New Roman", serif',
    font_size='7pt',
    font_weight='normal',
    fill='#444444',
)

# Descriptor line below lower rule — shortened to fit within rule width
text(
    'PERAMBULATION OF TOWN BOUNDS',
    (cx, rule_y_bot + H * 0.028),
    text_anchor='middle',
    font_family='Georgia, "Times New Roman", serif',
    font_size='4pt',
    font_weight='normal',
    fill=rule_color,
)


