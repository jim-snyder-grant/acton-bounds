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
  ## H2           -> subsection heading
  paragraph       -> left-aligned body text (blank line separates paragraphs)
  - item          -> bullet list (also `* item`)
  > quote         -> block quote (gold left rule, indented); blank `>` splits
                    quote paragraphs
  ---             -> horizontal rule
  **bold**  *italic*  -> inline emphasis

Usage:
  python3 intro2pdf.py <file.md> [more.md ...] [--section NAME] [--out OUT.pdf]
  (--section / --out apply only when a single file is given.)

Note: draft-note headers and bracketed [editor: ...] asides in the source .md
render literally -- strip them from the Markdown before a final run.
"""
import argparse
import html
import os
import re
import sys

from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable)
from reportlab.pdfgen import canvas as pdfcanvas

# --- page geometry: identical to bounds2pdf.py ---
PAGE_W, PAGE_H = letter          # 612 x 792 pt
MARGIN = 72                      # 1 inch
AVAIL_W = PAGE_W - 2 * MARGIN    # 468 pt
FRAME_PAD = 6                    # SimpleDocTemplate frame padding per side
TEXT_W = AVAIL_W - 2 * FRAME_PAD # 456 pt

GOLD = colors.HexColor("#C9A227")
GRAY = colors.HexColor("#555555")

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


def inline(text):
    """Escape XML, then convert **bold** and *italic* to ReportLab markup."""
    text = html.escape(text, quote=False)          # & < >
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


def parse_markdown(text):
    """Return (flowables, first_h1_title)."""
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
    flow, title = parse_markdown(text)
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
