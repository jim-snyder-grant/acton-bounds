#!/usr/bin/env python3
"""Render an intro-section Markdown file to a styled PDF that matches the
monument-listing pages produced by bounds2pdf.py.

Shared look (see "Page numbering" / styles in code/claude.md and bounds2pdf.py):
US Letter, 1-inch margins, Helvetica body, and a right-justified per-section
footer "<Section Name>, page X of N" in 9pt #555555 gray at the same baseline
as the monument pages. The whole-report left-justified footer is added later at
final assembly, not here.

Supported Markdown (what the current intro drafts use):
  # H1            -> section title (centered, bold, rule beneath). Also becomes
                    the footer's section name unless --section is given.
  ## H2           -> subsection heading (kept on the same page as the content
                    that follows it -- never stranded at a page foot)
  paragraph       -> left-aligned body text (blank line separates paragraphs)
  - item          -> bullet list (also `* item`)
  > quote         -> block quote (gold left rule, indented); blank `>` splits
                    quote paragraphs
  ---             -> horizontal rule
  ![cap](path)    -> photo; consecutive image lines (no blank line between)
                    group into one dynamic-grid row (<=3 across), caption in
                    small italic beneath, same as the monument pages. Paths
                    resolve relative to the script dir / cwd / the .md's own
                    dir. If the filename matches a photo_manifest.csv row with
                    a docushare_url, the image links to it.
  ![cap](path){float=left|right width=N}
                  -> floated photo at N pt wide: the text after it (up to the
                    next heading) wraps beside and then below. Consecutive
                    floated lines on the same side stack in a side column with
                    the prose in the other column (they share width N, so the
                    stack lines up). Omit the braces for the normal centered row.
  [text](url)     -> inline link; clickable, drawn in a darkened gold. The
                    visible text is whatever `text` says, so spell the URL out
                    there when a print reader needs to be able to type it.
  **bold**  *italic*  -> inline emphasis

Usage:
  python3 intro2pdf.py <file.md> [more.md ...] [--section NAME] [--out OUT.pdf]
  (--section / --out apply only when a single file is given.)

Note: draft-note headers and bracketed [editor: ...] asides in the source .md
render literally -- strip them from the Markdown before a final run.
"""
import argparse
import csv
import html
import io
import math
import os
import re
import sys

from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, KeepTogether,
                                Image as RLImage)
from reportlab.platypus.flowables import ImageAndFlowables
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdfcanvas

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_RE = re.compile(r"!\[(.*?)\]\((.*?)\)(?:\s*\{([^}]*)\})?\s*$")
# Inline [text](url) link. The (?<!!) keeps this from eating an ![img](path)
# line, which is handled separately by IMG_RE.
LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)")
MAX_PHOTO_H = 220   # hard upper limit on an intro photo's display height (pt)

# --- page geometry: identical to bounds2pdf.py ---
PAGE_W, PAGE_H = letter          # 612 x 792 pt
MARGIN = 72                      # 1 inch
AVAIL_W = PAGE_W - 2 * MARGIN    # 468 pt
FRAME_PAD = 6                    # SimpleDocTemplate frame padding per side
TEXT_W = AVAIL_W - 2 * FRAME_PAD # 456 pt

GOLD = colors.HexColor("#C9A227")
GRAY = colors.HexColor("#555555")
# A darkened GOLD for link text. GOLD itself is only ever used for rules and
# other non-text accents, where contrast doesn't matter; at 11pt body size it
# scores 2.42:1 on white, well under the 4.5:1 WCAG AA needs. This reads as the
# same accent but passes at 4.91:1.
LINK = colors.HexColor("#8A6D0F")

# --- paragraph styles ---
H1 = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=18, leading=22,
                    alignment=TA_CENTER, spaceBefore=0, spaceAfter=6)
H2 = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=13, leading=16,
                    spaceBefore=14, spaceAfter=4)
BODY = ParagraphStyle("Body", fontName="Helvetica", fontSize=11, leading=15,
                      alignment=TA_LEFT, spaceBefore=2, spaceAfter=6)
BULLET = ParagraphStyle("Bullet", parent=BODY, alignment=TA_LEFT,
                        leftIndent=20, bulletIndent=6,
                        spaceBefore=1, spaceAfter=3)
QUOTE = ParagraphStyle("Quote", fontName="Helvetica", fontSize=10.5, leading=14,
                       textColor=colors.HexColor("#333333"),
                       spaceBefore=3, spaceAfter=3, alignment=TA_LEFT)
# Matches bounds2pdf.py's photo caption style so intro photos read the same.
CAPTION = ParagraphStyle("Caption", fontName="Helvetica-Oblique", fontSize=8,
                         leading=10, alignment=TA_CENTER,
                         spaceBefore=2, spaceAfter=0)


class LinkableImage(RLImage):
    """Image flowable that also draws a clickable link over itself.

    relative=1 anchors the link rect to the flowable's own draw-time
    transform, so it lands correctly regardless of table/hAlign placement.
    (Same technique as bounds2pdf.py's LinkableImage.)
    """
    def __init__(self, *args, link_url=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.link_url = link_url

    def draw(self):
        super().draw()
        if self.link_url:
            self.canv.linkURL(
                self.link_url, (0, 0, self.drawWidth, self.drawHeight), relative=1)


class CaptionedImage(RLImage):
    """An image that reserves and draws a wrapped caption directly beneath
    itself, so the image-plus-caption reads as one unit that can be handed to
    ImageAndFlowables as its single "image" for a text-wrap float. (Plain
    photo rows keep the image and its caption as separate flowables; only the
    wrap case needs them fused, because ImageAndFlowables reserves a rectangle
    sized to one Image.) Also draws a click-through link over the image, like
    LinkableImage. The caption band sits below the image within drawHeight.
    """
    def __init__(self, jpeg_bytes, width, height, caption="", link_url=None):
        super().__init__(io.BytesIO(jpeg_bytes), width=width, height=height)
        self._reader = ImageReader(io.BytesIO(jpeg_bytes))
        self.link_url = link_url
        self._imgW, self._imgH = width, height
        self._cap_lines = self._wrap_caption(caption, width) if caption else []
        cap_h = len(self._cap_lines) * CAPTION.leading + (2 if self._cap_lines else 0)
        self.drawWidth, self.drawHeight = width, height + cap_h

    @staticmethod
    def _wrap_caption(text, width):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        lines, cur = [], ""
        for word in text.split():
            trial = (cur + " " + word).strip()
            if not cur or stringWidth(trial, CAPTION.fontName, CAPTION.fontSize) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    # ImageAndFlowables drives sizing through these; keep our fixed size (the
    # extended drawHeight that includes the caption band) and skip the
    # aspect-ratio restriction logic, which doesn't know about the caption.
    def wrap(self, availWidth, availHeight):
        return self.drawWidth, self.drawHeight

    def _restrictSize(self, availWidth, availHeight):
        self._oldDrawSize = None
        return self.drawWidth, self.drawHeight

    def _unRestrictSize(self):
        pass

    def draw(self):
        c = self.canv
        cap_h = self.drawHeight - self._imgH
        c.drawImage(self._reader, 0, cap_h, self._imgW, self._imgH, mask="auto")
        if self.link_url:
            c.linkURL(self.link_url,
                      (0, cap_h, self._imgW, cap_h + self._imgH), relative=1)
        if self._cap_lines:
            c.setFont(CAPTION.fontName, CAPTION.fontSize)
            c.setFillColor(GRAY)
            y = cap_h - CAPTION.fontSize
            for line in self._cap_lines:
                c.drawCentredString(self._imgW / 2.0, y, line)
                y -= CAPTION.leading


def load_docushare_map():
    """filename -> docushare_url from photo_manifest.csv (best-effort, may be empty)."""
    path = os.path.join(SCRIPT_DIR, "photo_manifest.csv")
    ds = {}
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                url = (row.get("docushare_url") or "").strip()
                if url:
                    ds[row["filename"]] = url
    except FileNotFoundError:
        pass
    return ds


def resolve_image_path(raw, md_dir):
    """Find an image path referenced in the Markdown, trying a few bases.

    The intro drafts write paths like `../Photos/Monument Photos/x.jpg`
    relative to code/ (matching bounds2pdf.py's convention), but be forgiving
    about where intro2pdf.py is actually invoked from.
    """
    if os.path.isabs(raw) and os.path.exists(raw):
        return raw
    for base in (SCRIPT_DIR, os.getcwd(), md_dir):
        cand = os.path.normpath(os.path.join(base, raw))
        if os.path.exists(cand):
            return cand
    return None


def photo_dims(path, col_width, max_h):
    """Return (display_width, display_height) fitting col_width, capped at max_h."""
    with PILImage.open(path) as img:
        nat_w, nat_h = img.size
    natural_h = col_width * nat_h / nat_w
    if natural_h > max_h:
        return int(max_h * nat_w / nat_h), int(max_h)
    return int(col_width), int(natural_h)


def fixed_width_dims(path, width):
    """Return (width, proportional_height) at exactly `width` pt, no height cap.

    Floated photos are placed at an author-chosen width (so a stack shares one
    edge), and their height just follows the aspect ratio -- unlike photo_dims,
    which fills a column and caps the height.
    """
    with PILImage.open(path) as img:
        nat_w, nat_h = img.size
    return int(width), int(round(width * nat_h / nat_w))


FLOAT_DEFAULT_WIDTH = 160

def parse_img_attrs(attr_str):
    """Parse an image line's `{float=left width=160}` suffix.

    Returns {'float': 'left'|'right'|None, 'width': int|None}. Unknown keys and
    malformed values are ignored, so a stray attribute never breaks a build.
    """
    out = {"float": None, "width": None}
    for tok in (attr_str or "").split():
        if "=" not in tok:
            continue
        key, val = tok.split("=", 1)
        key, val = key.strip().lower(), val.strip()
        if key == "float" and val.lower() in ("left", "right"):
            out["float"] = val.lower()
        elif key == "width":
            try:
                out["width"] = int(val)
            except ValueError:
                pass
    return out


def to_jpeg_bytes(path, display_width, display_height, dpi_scale=2):
    """Resize to display_size x dpi_scale and return JPEG bytes (keeps PDF small)."""
    with PILImage.open(path) as img:
        img = img.convert("RGB").resize(
            (int(display_width * dpi_scale), int(display_height * dpi_scale)),
            PILImage.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()


def build_image_group(group, md_dir, ds_map):
    """Turn consecutive ![cap](path) lines into dynamic-grid photo-row tables."""
    resolved = []
    for cap, raw in group:
        p = resolve_image_path(raw, md_dir)
        if p is None:
            print(f"  WARNING: intro image not found, skipping: {raw}", file=sys.stderr)
            continue
        resolved.append((p, cap, ds_map.get(os.path.basename(p))))
    if not resolved:
        return []

    n = len(resolved)
    cols = min(n, 3)
    col_width = int((TEXT_W - (cols - 1) * 8) // cols)
    flowables, n_rows = [], math.ceil(n / cols)
    for row_i in range(n_rows):
        chunk = resolved[row_i * cols:(row_i + 1) * cols]
        cells = []
        for p, cap, url in chunk:
            dw, dh = photo_dims(p, col_width, MAX_PHOTO_H)
            img = LinkableImage(io.BytesIO(to_jpeg_bytes(p, dw, dh)),
                                width=dw, height=dh, hAlign="CENTER",
                                link_url=url or None)
            content = [img]
            if cap:
                content.append(Paragraph(inline(cap), CAPTION))
            cells.append(content)
        for _ in range(cols - len(chunk)):
            cells.append([Spacer(1, 1)])
        t = Table([cells], colWidths=[col_width + 4] * cols)
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        if row_i > 0:
            flowables.append(Spacer(1, 6))
        flowables.append(t)
    return flowables


def build_float_group(group, beside, side, width, md_dir, ds_map):
    """Lay out a run of floated images with prose flowing beside (and below).

    `group` is a list of (caption, raw_path); `beside` is the already-built list
    of flowables (paragraphs, bullets, ...) that should wrap around / sit next
    to the images; `side` is 'left' or 'right'; `width` is the image display
    width in pt (all images in the run share it, so a stack lines up).

    One image -> ImageAndFlowables, so the prose flows down the image's side and
    then reclaims full width beneath it. Several images -> a two-column table
    (images stacked on `side`, prose in the other column) -- true wrap only
    reserves one image's rectangle, and stacking preserves each photo's caption.
    Falls back to returning `beside` unchanged if no image resolves.
    """
    resolved = []
    for cap, raw in group:
        p = resolve_image_path(raw, md_dir)
        if p is None:
            print(f"  WARNING: intro image not found, skipping: {raw}", file=sys.stderr)
            continue
        resolved.append((p, cap, ds_map.get(os.path.basename(p))))
    if not resolved:
        return list(beside)
    width = width or FLOAT_DEFAULT_WIDTH
    beside = list(beside)

    if len(resolved) == 1:
        p, cap, url = resolved[0]
        dw, dh = fixed_width_dims(p, width)
        img = CaptionedImage(to_jpeg_bytes(p, dw, dh), dw, dh,
                             caption=cap, link_url=url)
        gap = 8
        return [ImageAndFlowables(
            img, beside, imageSide=side,
            imageLeftPadding=(gap if side == "right" else 0),
            imageRightPadding=(gap if side == "left" else 0),
            imageBottomPadding=6)]

    # Several images: stack them in one column, prose in the other.
    col = []
    for idx, (p, cap, url) in enumerate(resolved):
        dw, dh = fixed_width_dims(p, width)
        col.append(LinkableImage(io.BytesIO(to_jpeg_bytes(p, dw, dh)),
                                 width=dw, height=dh, hAlign="CENTER",
                                 link_url=url or None))
        if cap:
            col.append(Paragraph(inline(cap), CAPTION))
        if idx < len(resolved) - 1:
            col.append(Spacer(1, 10))
    img_col_w = width + 10
    text_col_w = TEXT_W - img_col_w
    if side == "left":
        cells, widths = [col, beside], [img_col_w, text_col_w]
        inner = [("RIGHTPADDING", (0, 0), (0, 0), 12),
                 ("LEFTPADDING", (1, 0), (1, 0), 6)]
    else:
        cells, widths = [beside, col], [text_col_w, img_col_w]
        inner = [("RIGHTPADDING", (0, 0), (0, 0), 6),
                 ("LEFTPADDING", (1, 0), (1, 0), 12)]
    t = Table([cells], colWidths=widths)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (-1, 0), (-1, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ] + inner))
    return [t]


def inline(text):
    """Escape XML, then convert [text](url), **bold** and *italic* to ReportLab markup."""
    text = html.escape(text, quote=False)          # & < >
    # Links first, so link text can still carry emphasis: [**x**](u) -> <a><b>x</b></a>.
    text = LINK_RE.sub(
        lambda m: '<a href="%s" color="#%s">%s</a>' % (
            html.escape(m.group(2), quote=True), LINK.hexval()[2:], m.group(1)),
        text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return text


def quote_block(qlines):
    """Build a gold-left-rule table wrapping one or more quote paragraphs."""
    paras, buf = [], []
    for ql in qlines:
        if ql == "":
            if buf:
                paras.append(Paragraph(inline(" ".join(buf)), QUOTE))
                buf = []
        else:
            buf.append(ql)
    if buf:
        paras.append(Paragraph(inline(" ".join(buf)), QUOTE))
    tbl = Table([[paras]], colWidths=[TEXT_W])
    tbl.setStyle(TableStyle([
        ("LINEBEFORE", (0, 0), (0, -1), 2, GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return tbl


def parse_markdown(text, md_dir=".", ds_map=None):
    """Return (flowables, first_h1_title)."""
    ds_map = ds_map or {}
    lines = text.split("\n")
    flow, para = [], []
    title = None
    n = i = 0
    n = len(lines)

    def flush_para():
        if para:
            flow.append(Paragraph(inline(" ".join(l.strip() for l in para)), BODY))
            para.clear()

    while i < n:
        line = lines[i].strip()
        if not line:
            flush_para(); i += 1; continue

        if line.startswith("# "):
            flush_para()
            t = line[2:].strip()
            if title is None:
                title = t
            flow.append(Paragraph(inline(t), H1))
            flow.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#333333"),
                                   spaceBefore=2, spaceAfter=8))
            i += 1; continue

        if line.startswith("## "):
            flush_para()
            flow.append(Paragraph(inline(line[3:].strip()), H2))
            i += 1; continue

        if re.fullmatch(r"-{3,}", line):
            flush_para()
            flow.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#999999"),
                                   spaceBefore=6, spaceAfter=6))
            i += 1; continue

        if line.startswith(">"):
            flush_para()
            qlines = []
            while i < n and lines[i].strip().startswith(">"):
                qlines.append(lines[i].strip()[1:].strip())
                i += 1
            flow.append(Spacer(1, 4))
            flow.append(quote_block(qlines))
            flow.append(Spacer(1, 6))
            continue

        if IMG_RE.match(line):
            flush_para()
            # Gather a run of consecutive image lines. A run is homogeneous in
            # float-ness: a floated image ends the run when the next image has a
            # different float side (or none), so a centered row and a float
            # block never merge.
            group = []
            float_side = float_width = None
            first = True
            while i < n:
                m = IMG_RE.match(lines[i].strip())
                if not m:
                    break
                attrs = parse_img_attrs(m.group(3))
                if first:
                    float_side, float_width = attrs["float"], attrs["width"]
                    first = False
                elif bool(attrs["float"]) != bool(float_side) or (
                        attrs["float"] and attrs["float"] != float_side):
                    break
                group.append((m.group(1), m.group(2)))
                i += 1

            if float_side:
                # Everything up to the next heading wraps around the image(s).
                beside_lines = []
                while i < n and not lines[i].strip().startswith("#"):
                    beside_lines.append(lines[i])
                    i += 1
                beside, _ = parse_markdown("\n".join(beside_lines), md_dir, ds_map)
                flow.append(Spacer(1, 4))
                flow.extend(build_float_group(group, beside, float_side,
                                              float_width, md_dir, ds_map))
                flow.append(Spacer(1, 6))
            else:
                imgs = build_image_group(group, md_dir, ds_map)
                if imgs:
                    flow.append(Spacer(1, 4))
                    flow.extend(imgs)
                    flow.append(Spacer(1, 6))
            continue

        if re.match(r"[-*]\s+", line):
            flush_para()
            while i < n and re.match(r"[-*]\s+", lines[i].strip()):
                itext = re.sub(r"^[-*]\s+", "", lines[i].strip())
                i += 1
                # fold indented continuation lines into the same item
                while (i < n and lines[i].strip()
                       and not re.match(r"[-*]\s+", lines[i].strip())
                       and lines[i][:1] in " \t"):
                    itext += " " + lines[i].strip(); i += 1
                flow.append(Paragraph(inline(itext), BULLET, bulletText="•"))
            continue

        para.append(line); i += 1

    flush_para()
    return flow, title


def keep_headings_with_next(flow):
    """Bind each `##` subhead to the content that follows it (keep-with-next),
    so a heading is never stranded alone at the foot of a page while its
    material starts on the next one.

    For each H2 paragraph we wrap it, plus any immediately following Spacers,
    plus the first real content flowable after them (paragraph, image row,
    quote, bullet, ...), in a KeepTogether. Intervening Spacers matter because
    an image/quote block emits a leading Spacer, so a plain style-level
    keepWithNext flag would only tie the heading to that empty spacer. A run of
    consecutive headings is left un-consumed so each still binds to its own
    body. This is layout-only and general -- it re-flows correctly no matter
    how the text shifts as the source is edited.
    """
    out, i, n = [], 0, len(flow)
    while i < n:
        f = flow[i]
        if getattr(f, "style", None) is H2:
            group, j = [f], i + 1
            while j < n and isinstance(flow[j], Spacer):
                group.append(flow[j]); j += 1
            if j < n and getattr(flow[j], "style", None) is not H2:
                group.append(flow[j]); j += 1
            out.append(KeepTogether(group))
            i = j
        else:
            out.append(f); i += 1
    return out


def make_canvas(section_name):
    """Canvas subclass that stamps the per-section right-justified footer,
    using the same two-pass count-then-draw technique as bounds2pdf.py."""
    class SectionCanvas(pdfcanvas.Canvas):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self._saved = []

        def showPage(self):
            self._saved.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._saved)
            for st in self._saved:
                self.__dict__.update(st)
                self.setFont("Helvetica", 9)
                self.setFillColor(GRAY)
                self.drawRightString(PAGE_W - MARGIN, 0.5 * 72 - 10,
                                     f"{section_name}, page {self._pageNumber} of {total}")
                super().showPage()
            super().save()

    return SectionCanvas


def render(md_path, out_path=None, section=None):
    with open(md_path, encoding="utf-8") as fh:
        text = fh.read()
    md_dir = os.path.dirname(os.path.abspath(md_path))
    flow, title = parse_markdown(text, md_dir=md_dir, ds_map=load_docushare_map())
    flow = keep_headings_with_next(flow)
    section_name = section or title or os.path.splitext(os.path.basename(md_path))[0]
    if out_path is None:
        out_path = os.path.splitext(md_path)[0] + ".pdf"
    doc = SimpleDocTemplate(out_path, pagesize=letter,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN, bottomMargin=MARGIN,
                            title=section_name)
    doc.build(flow, canvasmaker=make_canvas(section_name))
    print(f"Wrote {out_path}  (section: '{section_name}')")


def main():
    ap = argparse.ArgumentParser(description="Render intro-section Markdown to styled PDF.")
    ap.add_argument("md", nargs="+", help="Markdown file(s) to render")
    ap.add_argument("--section", help="footer section name (single file only; "
                                       "defaults to the first # H1 title)")
    ap.add_argument("--out", help="output PDF path (single file only)")
    args = ap.parse_args()

    if len(args.md) > 1 and (args.section or args.out):
        sys.exit("--section/--out only apply when rendering a single file.")
    for path in args.md:
        render(path, out_path=args.out, section=args.section)


if __name__ == "__main__":
    main()
