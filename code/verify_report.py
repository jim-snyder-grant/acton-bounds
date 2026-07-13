#!/usr/bin/env python3
"""Verify the assembled Acton Bounds report -- primarily that every clickable
overview-map callout box links to the correct monument page.

This is the standalone version of the ad-hoc link check that used to be run as
an inline python3 heredoc after each assembly. Run it any time after
`assemble_report.py`:

    python3 code/verify_report.py            # checks the canonical report
    python3 code/verify_report.py --report "some other.pdf"

What it checks (all derived from the actual PDF + the overview_map_links.json
sidecar, nothing hardcoded, so it stays correct as page counts shift):

  1. The report opens and its page count is reported.
  2. Exactly one page carries internal "go to page" (GoTo /Dest) link
     annotations -- that's the overview map.
  3. The number of those links equals the number of callout boxes in the
     sidecar (one per monument).
  4. Each link's rectangle matches exactly one sidecar box, which identifies
     its Order number; every Order 1..N is covered exactly once.
  5. The Order -> destination-page mapping is affine with slope 1 -- i.e.
     Order k lands on listings_start + (k - 1), so box N points at the Nth
     monument page in Order sequence (catches a scrambled or off-by-one set,
     not just a non-contiguous one).

Exit status is 0 on PASS, 1 on any FAIL, so it doubles as a pre-commit check.
Needs `pypdf` (already in requirements.txt).
"""
import argparse
import json
import os
import sys

from pypdf import PdfReader

HERE = os.path.dirname(os.path.abspath(__file__))          # code/
ROOT = os.path.dirname(HERE)                                # Bounds/
DEFAULT_REPORT = os.path.join(ROOT, "Acton Bounds Report 2025-2026.pdf")
LINKS_JSON = os.path.join(HERE, "overview_map_links.json")


def rect_key(rect):
    """Round a [x0,y0,x1,y1] rect to a hashable key robust to float noise."""
    return tuple(round(float(v), 1) for v in rect)


def internal_links(page, page_index_by_id):
    """Yield (dest_page_index, rect) for each internal GoTo /Dest link on page."""
    for ref in (page.get("/Annots") or []):
        annot = ref.get_object()
        if annot.get("/Subtype") != "/Link":
            continue
        dest = annot.get("/Dest")
        if dest is None:                      # URI links (photos/OSM) have /A, skip
            continue
        target = dest[0]
        idnum = getattr(target, "idnum", None)
        if idnum in page_index_by_id and annot.get("/Rect") is not None:
            yield page_index_by_id[idnum], [float(v) for v in annot["/Rect"]]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", default=DEFAULT_REPORT,
                    help="path to the assembled report PDF "
                         "(default: the canonical one at the Bounds root)")
    args = ap.parse_args()

    fails = []

    if not os.path.exists(args.report):
        print(f"FAIL: report not found: {args.report}")
        sys.exit(1)
    reader = PdfReader(args.report)
    page_index_by_id = {p.indirect_reference.idnum: i
                        for i, p in enumerate(reader.pages)}
    n_pages = len(reader.pages)
    print(f"Report: {os.path.basename(args.report)}  ({n_pages} pages)")

    if not os.path.exists(LINKS_JSON):
        print(f"FAIL: sidecar not found: {LINKS_JSON} "
              f"(run overview_map.py, then assemble_report.py)")
        sys.exit(1)
    with open(LINKS_JSON) as fh:
        boxes = json.load(fh)["boxes"]                       # {order_str: rect}
    n_boxes = len(boxes)
    orders = sorted(int(k) for k in boxes)
    expected_orders = list(range(1, n_boxes + 1))
    if orders != expected_orders:
        fails.append(f"sidecar Orders are not a clean 1..{n_boxes} sequence: {orders}")
    order_by_rect = {rect_key(rect): int(order) for order, rect in boxes.items()}

    # Which page(s) carry internal callout links?
    link_pages = {}
    for i, page in enumerate(reader.pages):
        links = list(internal_links(page, page_index_by_id))
        if links:
            link_pages[i] = links
    if len(link_pages) != 1:
        print(f"FAIL: expected exactly one page with internal callout links, "
              f"found {len(link_pages)} (pages {[p + 1 for p in link_pages]})")
        sys.exit(1)
    map_idx, links = next(iter(link_pages.items()))
    print(f"Overview-map page: {map_idx + 1};  callout links: {len(links)};  "
          f"sidecar boxes: {n_boxes}")

    if len(links) != n_boxes:
        fails.append(f"link count {len(links)} != box count {n_boxes}")

    # Match each link to its box (by rect) -> Order, then check Order->page.
    seen_orders, offsets = [], set()
    for dest_idx, rect in links:
        order = order_by_rect.get(rect_key(rect))
        if order is None:
            fails.append(f"link at page {dest_idx + 1} has rect {rect_key(rect)} "
                         f"matching no sidecar box")
            continue
        seen_orders.append(order)
        offsets.add(dest_idx - (order - 1))   # == listings_start for a correct map

    dup = sorted({o for o in seen_orders if seen_orders.count(o) > 1})
    if dup:
        fails.append(f"Orders linked more than once: {dup}")
    missing = sorted(set(expected_orders) - set(seen_orders))
    if missing:
        fails.append(f"Orders with no link: {missing}")
    if len(offsets) > 1:
        fails.append(f"Order->page mapping is not slope-1 (scrambled/off-by-one); "
                     f"listings_start disagrees across links: {sorted(offsets)}")
    elif offsets:
        start = next(iter(offsets))
        print(f"Monument listings start: page {start + 1};  "
              f"Order 1 -> p{start + 1} ... Order {n_boxes} -> p{start + n_boxes}")

    print()
    if fails:
        print("RESULT: FAIL")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print(f"RESULT: PASS -- all {n_boxes} overview-map links resolve to the "
          f"correct monument pages.")


if __name__ == "__main__":
    main()
