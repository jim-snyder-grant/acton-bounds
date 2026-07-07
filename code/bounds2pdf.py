from datetime import datetime, timedelta
import argparse
import html
import io
import json
import re
import math
import csv

import pandas as pd
from pathlib import Path
from PIL import Image as PILImage
import asyncio
from playwright.async_api import async_playwright

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, HRFlowable, PageBreak,
)
from reportlab.pdfgen import canvas as pdfcanvas

from status_colors import STATUS_COLORS, DEFAULT_STATUS_COLOR, knockout_text_color

# ---------------------------------------------------------------------------
# Page constants (letter: 612 × 792 pt)
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = letter
MARGIN = 72                          # 1-inch margins
AVAIL_W = PAGE_W - 2 * MARGIN       # 468 pt
AVAIL_H = PAGE_H - 2 * MARGIN       # 648 pt

# SimpleDocTemplate's page frame adds its own 6pt padding on every side (a
# ReportLab default, not something we set) on top of the margins above, so
# the true usable width for anything actually laid out in the frame is 12pt
# narrower than AVAIL_W. Pre-measurement (flowable_h below) must wrap at
# this width, not AVAIL_W, or it'll underestimate how tall a long wrapped
# title really renders -- which then lets choose_cols() overallocate space
# to photos and spill them onto a second page for no real reason.
FRAME_PAD = 6
TEXT_W = AVAIL_W - 2 * FRAME_PAD    # 456 pt

PHOTOS_DIR = Path("../Photos/Monument Photos")
OSM_DIR = Path("osm_screenshots")
OSM_CACHE = OSM_DIR / "osm_url_cache.json"
MAP_SIZE = 150      # OSM map display size in points
MAP_GAP = 12        # gap between left text column and map column
MAX_PHOTO_H = 200   # hard upper limit on photo height; actual cap computed dynamically

# This script only generates the Monument Listings section — all of the
# report's intro material (cover, legal background, history, road-name
# changes, overview map, and Jim's Monument Listings intro) is a separate
# document, merged in front of this one during final assembly. The footer
# below is self-contained to this section ("Monument Listings, page X of
# N", right-justified) and never needs to know the intro material's page
# count -- a separate final-assembly script stamps the report-wide page
# number (left-justified) across every page of the merged PDF once the
# whole document exists. See "Page numbering" in code/claude.md.

# ---------------------------------------------------------------------------
# Paragraph styles
# ---------------------------------------------------------------------------
TITLE_S = ParagraphStyle('MonTitle',
    fontName='Helvetica-Bold', fontSize=14, leading=17,
    alignment=TA_CENTER, spaceBefore=0, spaceAfter=4)

SMALL = ParagraphStyle('MonSmall',
    fontName='Helvetica', fontSize=10, leading=13,
    spaceBefore=1, spaceAfter=1)

DETL = ParagraphStyle('MonDetail',
    fontName='Helvetica', fontSize=11, leading=14,
    spaceBefore=2, spaceAfter=2,
    leftIndent=4)

CAPTION = ParagraphStyle('MonCaption',
    fontName='Helvetica-Oblique', fontSize=8, leading=10,
    alignment=TA_CENTER,
    spaceBefore=2, spaceAfter=0)

CLICK_NOTE = ParagraphStyle('ClickNote',
    fontName='Helvetica-Oblique', fontSize=8, leading=10,
    alignment=TA_CENTER, textColor=colors.HexColor('#555555'),
    spaceBefore=2, spaceAfter=4)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def esc(val):
    """Escape a value for use in ReportLab XML paragraph markup."""
    try:
        if pd.isna(val):
            return ''
    except (TypeError, ValueError):
        pass
    return html.escape(str(val)).replace('\n', '<br/>')


def safe_str(val):
    if pd.isna(val):
        return ''
    return str(val)


def parse_visit_date(val):
    """Return (display_str, contacts_key) for a Date of visit cell value."""
    if pd.isna(val):
        return "Not yet visited", None
    if isinstance(val, float):
        dt = datetime(1899, 12, 30) + timedelta(days=int(val))
        return dt.strftime('%B %-d, %Y'), dt.strftime('%b %-d, %Y')
    if isinstance(val, (pd.Timestamp, datetime)):
        return val.strftime('%B %-d, %Y'), val.strftime('%b %-d, %Y')
    val_str = str(val).strip()
    base = re.sub(r'\s*\(\d+\)\s*$', '', val_str).strip()
    try:
        dt = datetime.strptime(base, '%b %d, %Y')
        return dt.strftime('%B %-d, %Y'), val_str
    except ValueError:
        return val_str, val_str


def load_person_towns(xlsx_path):
    """Build {full_name: town} from the person directory in the Contacts sheet.

    The directory lives below the attendance table, starting at row 10 (header).
    Only rows with a non-empty 'Only for Town' value are included.
    """
    df = pd.read_excel(xlsx_path, sheet_name='Contacts', header=11)
    towns = {}
    for _, row in df.iterrows():
        first = row.get('First Names')
        last  = row.get('Last Names')
        town  = row.get('Only for Town')
        if pd.isna(first) or pd.isna(last) or pd.isna(town):
            continue
        first, last, town = str(first).strip(), str(last).strip(), str(town).strip()
        if not first or first.lower() == 'various' or not last or not town:
            continue
        towns[f'{first} {last}'] = town
    return towns


def annotate_witnesses(present_str, person_towns):
    """Append (Town) after names listed in person_towns (non-Acton attendees)."""
    if not present_str:
        return present_str
    parts = []
    for name in present_str.split(','):
        name = name.strip()
        town = person_towns.get(name)
        parts.append(f'{name} ({town})' if town else name)
    return ', '.join(parts)


def load_osm_cache():
    if OSM_CACHE.exists():
        with open(OSM_CACHE) as f:
            return json.load(f)
    return {}


def save_osm_cache(cache):
    with open(OSM_CACHE, 'w') as f:
        json.dump(cache, f, indent=2)


def load_manifest(path):
    """Return dict: monument_name -> [(path, caption, docushare_url), ...] sorted by datetime."""
    result = {}
    p = Path(path)
    if not p.exists():
        return result
    with open(p, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['include'] != 'yes' or row['section'] != 'monument':
                continue
            name = row['monument_name']
            result.setdefault(name, []).append((
                row['datetime'], PHOTOS_DIR / row['filename'],
                row['caption'], row.get('docushare_url', '')
            ))
    return {
        name: [(p, cap, url) for _, p, cap, url in sorted(entries)]
        for name, entries in result.items()
    }


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------

class LinkableImage(RLImage):
    """An Image flowable that also draws a clickable link region over itself.

    relative=1 anchors the link rect to the flowable's own draw-time
    transform, so it lands correctly regardless of table/hAlign placement.
    """
    def __init__(self, *args, link_url=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.link_url = link_url

    def draw(self):
        super().draw()
        if self.link_url:
            self.canv.linkURL(
                self.link_url, (0, 0, self.drawWidth, self.drawHeight), relative=1)


class NumberedCanvas(pdfcanvas.Canvas):
    """Draws a right-justified 'Monument Listings, page X of N' footer on
    every page -- self-contained to this section (X and N never include
    other sections' pages; see the module-level comment on this near the
    top of the file for why).

    Standard ReportLab two-pass technique: buffer each page's drawing state
    via showPage(), then once the true page count is known (in save()),
    replay each buffered page and stamp the footer before the real showPage.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_footer(num_pages)
            super().showPage()
        super().save()

    def _draw_footer(self, total_pages):
        self.setFont('Helvetica', 9)
        self.setFillColor(colors.HexColor('#555555'))
        self.drawRightString(
            PAGE_W - MARGIN, 0.5 * 72 - 10,
            f'Monument Listings, page {self._pageNumber} of {total_pages}')


def photo_dims(path, col_width, max_h):
    """Return (display_width, display_height) capped at max_h."""
    with PILImage.open(path) as img:
        nat_w, nat_h = img.size
    natural_h = col_width * nat_h / nat_w
    if natural_h > max_h:
        display_h = int(max_h)
        display_w = int(max_h * nat_w / nat_h)
    else:
        display_h = int(natural_h)
        display_w = int(col_width)
    return display_w, display_h


def to_jpeg_bytes(path, display_width, display_height, dpi_scale=2):
    """Resize to display_size × dpi_scale and return JPEG bytes."""
    target_w = int(display_width * dpi_scale)
    target_h = int(display_height * dpi_scale)
    with PILImage.open(path) as img:
        img = img.convert('RGB')
        img = img.resize((target_w, target_h), PILImage.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        buf.seek(0)
        return buf.getvalue()


def photos_all_portrait(photos):
    """Return True if every photo in the list is taller than it is wide."""
    for path, _, _ in photos:
        try:
            with PILImage.open(path) as img:
                w, h = img.size
                if w >= h:
                    return False
        except Exception:
            return False
    return len(photos) > 0


# ---------------------------------------------------------------------------
# Photo layout
# ---------------------------------------------------------------------------

def flowable_h(f):
    """Measure a flowable's rendered height at the true usable frame width."""
    try:
        _, h = f.wrap(TEXT_W, AVAIL_H)
        return h
    except Exception:
        return 0


def _max_cap_h(captions, col_width):
    """Return the tallest caption paragraph height at col_width."""
    max_h = 0
    for cap in captions:
        if cap:
            p = Paragraph(html.escape(cap), CAPTION)
            try:
                _, h = p.wrap(col_width, 1000)
                max_h = max(max_h, h)
            except Exception:
                pass
    return max(max_h, 10)  # at least one CAPTION line


def choose_cols(photos, remaining_h):
    """Choose (cols, col_width, max_photo_h) targeting ≤2 rows in remaining_h.

    Starts at 3-across for all-portrait monuments (they're narrower), otherwise 2.
    Uses actual measured caption height so multi-line captions don't overflow.

    For 1-2 photos, uses the full page width (1 column for a single photo,
    2 side-by-side for two) and skips the MAX_PHOTO_H cap -- remaining_h
    already bounds the size to whatever actually fits on the page, so with
    few photos and lots of leftover space they can grow larger without risk
    of overlap.
    """
    n = len(photos)
    captions = [cap for _, cap, _ in photos]
    all_portrait = photos_all_portrait(photos)
    # Portrait photos are narrow; start at 3-across so they're not over-large
    if n == 1:
        base_min = 1
    elif all_portrait and n >= 3:
        base_min = 3
    else:
        base_min = 2
    min_cols = max(base_min, math.ceil(n / 2))

    for cols in range(min_cols, 6):
        col_width = int((AVAIL_W - (cols - 1) * 8) // cols)
        if col_width < 60:
            break
        n_photo_rows = math.ceil(n / cols)
        cap_h = _max_cap_h(captions, col_width)
        per_row_oh = cap_h + 4  # caption text height + CAPTION spaceBefore (2) + bottom cell padding (2)
        overhead = max(0, n_photo_rows - 1) * 6 + n_photo_rows * per_row_oh
        max_h = int((remaining_h - overhead) / n_photo_rows)
        if max_h >= 60:
            capped_max_h = max_h if n <= 2 else min(max_h, MAX_PHOTO_H)
            return cols, col_width, capped_max_h

    # Fallback: 4-across, fixed small size
    return 4, max(60, int((AVAIL_W - 24) // 4)), 80


def build_photo_tables(photos, cols, col_width, max_h):
    """One Table per photo row; caption lives in same cell as photo."""
    flowables = []
    n_rows = math.ceil(len(photos) / cols)
    for row_i in range(n_rows):
        group = photos[row_i * cols: (row_i + 1) * cols]
        n_pad = cols - len(group)

        cells = []
        for path, cap, docushare_url in group:
            dw, dh = photo_dims(path, col_width, max_h)
            img = LinkableImage(io.BytesIO(to_jpeg_bytes(path, dw, dh)),
                                width=dw, height=dh, hAlign='CENTER',
                                link_url=docushare_url or None)
            cell_content = [img]
            if cap:
                cell_content.append(Paragraph(html.escape(cap), CAPTION))
            cells.append(cell_content)
        for _ in range(n_pad):
            cells.append([Spacer(1, 1)])

        t = Table([cells], colWidths=[col_width + 4] * cols)
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        if row_i > 0:
            flowables.append(Spacer(1, 6))
        flowables.append(t)
    return flowables


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--force-screenshots', action='store_true',
                        help='Re-capture all OSM screenshots, ignoring the cache')
    args = parser.parse_args()

    df = pd.read_excel('../Acton Bounds.xlsx', sheet_name='Monuments')

    # Page order is driven by the 'Order' column (Jim's clockwise walk
    # starting at the Acton/Concord/Maynard/Sudbury corner -- see
    # code/claude.md), not by however the sheet happens to be sorted. Sort
    # explicitly here so a future accidental re-sort/insert in the sheet
    # can't silently change the report's page order.
    if df['Order'].isna().any():
        raise SystemExit("Monuments sheet has blank 'Order' values -- fill in every row before running.")
    if sorted(df['Order']) != list(range(1, len(df) + 1)):
        print(f"WARNING: 'Order' column is not a clean 1..{len(df)} sequence "
              f"(duplicates or gaps) -- check the Monuments sheet.")
    if not df['Order'].is_monotonic_increasing:
        print("NOTE: Monuments sheet rows were not already in Order-column sequence -- re-sorted for this run.")
    df = df.sort_values('Order').reset_index(drop=True)

    df_contacts = pd.read_excel('../Acton Bounds.xlsx', sheet_name='Contacts')
    manifest = load_manifest('photo_manifest.csv')
    person_towns = load_person_towns('../Acton Bounds.xlsx')

    contacts = {}
    for _, crow in df_contacts.iterrows():
        date_val, present_val = crow['Dates'], crow['Present']
        if not pd.isna(date_val) and not pd.isna(present_val):
            contacts[str(date_val).strip()] = str(present_val).strip()

    osm_cache = load_osm_cache()

    def needs_capture(i, osm_link):
        if args.force_screenshots:
            return True
        local = OSM_DIR / f'osm_screenshot_{i}.jpg'
        return not (local.exists() and osm_cache.get(str(i)) == str(osm_link))

    rows_needing_capture = {
        i for i in range(len(df))
        if not pd.isna(df.at[i, 'OpenStreetMap link'])
        and needs_capture(i, df.at[i, 'OpenStreetMap link'])
    }
    if rows_needing_capture:
        print(f'Capturing {len(rows_needing_capture)} OSM screenshot(s)...')
    else:
        print('All OSM screenshots cached.')

    story = []

    async with async_playwright() as pwright:
        browser = await pwright.chromium.launch() if rows_needing_capture else None
        pw_page = await browser.new_page() if browser else None

        for i in range(len(df)):
            print(f'row={i}  {df.at[i, "Name"]}')
            if i > 0:
                story.append(PageBreak())

            name = safe_str(df.at[i, 'Name']) or 'Unknown'
            status = safe_str(df.at[i, 'Status'])

            ps = []   # flowables for this monument

            # -- One-line headline + rule --
            # Order number, then name, then status -- order number and status
            # share the same status color, each in a box sized to just its
            # own text ("knockout" white text on dark backgrounds, black on
            # light ones, decided automatically per color -- see
            # knockout_text_color()). This also gives each monument a stable,
            # colored order number to later reuse as a clickable marker on
            # the overview map.
            order_num = safe_str(df.at[i, 'Order'])
            bg = STATUS_COLORS.get(status, DEFAULT_STATUS_COLOR)
            fg = knockout_text_color(bg)
            ps.append(Paragraph(
                f'<span backColor="{bg}" textColor="{fg}">&nbsp;{esc(order_num)}&nbsp;</span>'
                f'&nbsp;&nbsp;{esc(name)}&nbsp;&nbsp;'
                f'<span backColor="{bg}" textColor="{fg}">&nbsp;{esc(status)}&nbsp;</span>',
                TITLE_S))
            ps.append(HRFlowable(
                width='100%', thickness=1, color=colors.black, spaceAfter=4))

            # -- Date of visit --
            # "Not Found" means Jim went and searched but didn't locate the
            # monument -- "Date of visit" would wrongly imply he found it, so
            # use "Date searched" instead for that status.
            visit_display, contacts_key = parse_visit_date(df.at[i, 'Date of visit'])
            if status == 'Not Found':
                visit_label = 'Date searched:'
                if visit_display == 'Not yet visited':
                    visit_display = 'Not yet searched'
            else:
                visit_label = 'Date of visit:'
            ps.append(Paragraph(
                f'<b>{visit_label}</b> {esc(visit_display)}', DETL))

            # -- Witnesses --
            # Witnesses are for witnessing the physical bound itself -- only
            # meaningful when Jim actually located the monument (Painted,
            # Couldn't paint -- found but couldn't paint it, or Found).
            # Not Found / Documented searches were solo, even on days when
            # others were along painting different monuments.
            if (status in ('Painted', "Couldn't paint", 'Found')
                    and contacts_key and contacts_key in contacts):
                witnesses = annotate_witnesses(contacts[contacts_key], person_towns)
                ps.append(Paragraph(
                    f'<b>Witnesses:</b> {esc(witnesses)}', DETL))

            # -- Coordinates --
            lat = df.at[i, 'Latitude']
            if pd.isna(lat):
                ps.append(Paragraph('<b>Coordinates:</b> Unknown', DETL))
            else:
                # Report shows 5 decimal places (~1m precision) regardless of
                # how many digits are stored in the XLSX -- Jim wants to keep
                # the full-precision source data in case it's useful later.
                ps.append(Paragraph(
                    f'<b>Coordinates:</b>  <b>Latitude</b> {df.at[i, "Latitude"]:.5f}'
                    f'  <b>Longitude</b> {df.at[i, "Longitude"]:.5f}',
                    DETL))
                coord_src = df.at[i, 'Coordinate Source']
                second_line = []
                if not pd.isna(coord_src):
                    second_line.append(f'<b>Coordinate Source:</b> {esc(coord_src)}')
                second_line.append('<b>Datum:</b> WGS84 (EPSG 4326)')
                ps.append(Paragraph('  '.join(second_line), DETL))

            # -- Left column: all fields between coords and photos --
            left_items = []

            street_lines = [
                f'<b>Nearest Acton Street:</b> '
                f'{esc(df.at[i, "Nearest Acton street name"])}'
            ]
            other = df.at[i, 'Nearest other town street name']
            if not pd.isna(other):
                street_lines.append(
                    f'<b>Nearest other town street:</b> {esc(other)}')
            landmark = df.at[i, 'Nearby landmark']
            if not pd.isna(landmark):
                street_lines.append(f'<b>Nearby landmark:</b> {esc(landmark)}')
            left_items.append(Paragraph('<br/>'.join(street_lines), DETL))

            notes_loc = df.at[i, 'Notes on location']
            if not pd.isna(notes_loc):
                left_items.append(Paragraph(
                    f'<b>Notes on Location:</b> {esc(notes_loc)}', DETL))

            desc_1904 = df.at[i, 'From 1904 description']
            if not pd.isna(desc_1904):
                # Label reads "In 1904 description:" (not "From") so that
                # the 8 monuments whose cell just says "no" (not mentioned
                # in the 1904 book) read as a sensible answer -- "In 1904
                # description: no" -- rather than an odd non-answer.
                left_items.append(Paragraph(
                    f'<b>In 1904 description:</b> {esc(desc_1904)}', DETL))

            mon_notes = df.at[i, 'Notes on Monument']
            if not pd.isna(mon_notes):
                left_items.append(Paragraph(
                    f'<b>Notes on Monument:</b> {esc(mon_notes)}', DETL))

            next_steps = df.at[i, 'Possible Next Steps']
            if not pd.isna(next_steps):
                left_items.append(Paragraph(
                    f'<b>Possible Next Steps:</b> {esc(next_steps)}', DETL))

            # -- OSM map (right column) or full-width fallback --
            osm_link = df.at[i, 'OpenStreetMap link']
            local_path = OSM_DIR / f'osm_screenshot_{i}.jpg'
            if not pd.isna(osm_link):
                if i in rows_needing_capture:
                    await pw_page.goto(
                        str(osm_link), wait_until='networkidle', timeout=30000)
                    await pw_page.screenshot(
                        path=local_path, full_page=False, type='jpeg', quality=100,
                        clip={'x': 352, 'y': 100, 'width': 574, 'height': 574},
                    )
                    osm_cache[str(i)] = str(osm_link)
                    save_osm_cache(osm_cache)
                osm_img = LinkableImage(
                    io.BytesIO(to_jpeg_bytes(local_path, MAP_SIZE, MAP_SIZE)),
                    width=MAP_SIZE, height=MAP_SIZE, link_url=str(osm_link))
                osm_cell = [osm_img, Paragraph('Click map to see full size', CAPTION)]
                left_w = AVAIL_W - MAP_SIZE - MAP_GAP
                two_col = Table(
                    [[left_items, osm_cell]],
                    colWidths=[left_w, MAP_SIZE + MAP_GAP],
                )
                two_col.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    # Table cells render ~6pt further left than a plain
                    # paragraph with the same LEFTPADDING (measured against
                    # this reportlab version); compensate so this column's
                    # text aligns with the top fields, which sit directly in
                    # the page frame with no table wrapper.
                    ('LEFTPADDING', (0, 0), (0, 0), 6),
                    ('LEFTPADDING', (1, 0), (1, 0), MAP_GAP),
                ]))
                ps.append(two_col)
            else:
                ps.extend(left_items)

            # -- Photos --
            photos = manifest.get(name, [])
            if photos:
                if any(docushare_url for _, _, docushare_url in photos):
                    ps.append(Paragraph(
                        'Click any picture to see full size', CLICK_NOTE))
                text_h = sum(flowable_h(f) for f in ps)
                # ReportLab's frame adds ~26-28pt of inter-flowable spacing (spaceBefore/spaceAfter)
                # that wrap() doesn't report. Buffer of 40 covers that overhead plus a real margin.
                remaining_h = AVAIL_H - text_h - 40
                cols, col_width, max_h = choose_cols(photos, remaining_h)
                ps.extend(build_photo_tables(photos, cols, col_width, max_h))

            story.extend(ps)

        if browser:
            await browser.close()

    doc = SimpleDocTemplate(
        '../Acton Bounds Report 2025-2026.pdf', pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
    )
    doc.build(story, canvasmaker=NumberedCanvas)
    print('Done — ../Acton Bounds Report 2025-2026.pdf written.')


if __name__ == '__main__':
    asyncio.run(main())
