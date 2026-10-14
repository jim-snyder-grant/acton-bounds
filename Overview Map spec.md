# Overview Map — Spec

Section 5 of 8 in the report (after "How this report was created," before
"Monument Listings intro").

**Status: built.** Implemented in `code/overview_map.py`, which produces
`code/overview_map.pdf` (vector, the deliverable) and `code/overview_map.png`
(raster preview). This document is the single authoritative spec — it
consolidates and supersedes the six `INBOX-overview-map-*.md` messages
(rotation, base-map, mockup handoff, corner-fix, etc.) that were folded in and
deleted Jul 9 2026 (see CHANGELOG.md). All layout numbers below match the
mockup Jim approved through four iterations with claude.ai; the geometry was
then ported into the real `code/` script by Claude Code with real MassGIS data.

---

## Page

- **Legal portrait, 8.5×14in** — larger than the rest of the report (which is
  US Letter) so the rotated map stays legible. Confirmed via mockup.
- Exported as **vector PDF** (matplotlib), so rotation and multi-mile extent
  never hit a raster DPI ceiling.
- Single page expected.

## Orientation / rotation

- The map is **rotated ~27.97° counterclockwise** so the line from the
  Acton/Concord/Maynard/Sudbury corner (ACMS) to the Acton/Maynard/Stow corner
  (AMS) runs parallel to the bottom edge of the page (bearing N 61°57′ W;
  matches Jim's ~30° eyeball estimate).
- **The angle is computed programmatically from the real ACMS and AMS
  coordinates** in `Acton Bounds.xlsx`, never hardcoded, so it self-corrects if
  either coordinate is ever revised (`rot_rad` in the script).
- The base map, boundary line, all icon positions, and the compass rose are
  rotated together as one coordinate system — nothing is rotated as a finished
  flat image.

## Map extent

- Shows Acton plus a **~0.5-mile context buffer** on all sides.
- **The buffer/context zone (outside the town boundary) is kept plain/white** —
  no roads or water rendered there. (Reversed from an earlier draft: Jim
  decided context-zone base-map detail makes the callout lines harder to
  follow.) Real roads and water render **only inside the boundary polygon**.

## Base map (inside the boundary only)

Real MassGIS/MassDOT vector data, rendered locally via `geopandas` +
`matplotlib` (not a raster static-map API — that was the deciding factor for
vector-PDF quality and lossless rotation). Both layers are free, public-domain,
no API key. **Downloaded once and cached** in `code/gis_data/` (gitignored),
then clipped to the boundary polygon at render time — the API is not hit on
every run.

- **Roads:** MassDOT RoadInventory, ArcGIS REST service
  `gis.massdot.state.ma.us/arcgis/rest/services/Roads/RoadInventory/MapServer/0/query`
  (`f=geojson`, queried by bounding box). All local roads, line weight scaled by
  `F_F_Class` (functional class). Cached to `roads_acton.geojson`;
  `--refresh-roads` re-queries. The single largest road (lowest functional
  class present, e.g. Route 2) is labeled; a second label was dropped because
  it fell back to an awkward ramp name.
- **Water (open water only):** MassGIS/MassDEP Hydrography 1:25,000 (the
  1:25,000 layer, not the coarser 1:100,000). Downloaded once as `hydro25k.zip`
  (~60 MB, MassGIS S3). Filtered to **`POLY_CODE in {1, 6}`** = reservoirs
  (e.g. Nagog Pond) and lakes/ponds/wide-river/impoundment; wetlands, bogs,
  tidal flats, etc. are excluded to avoid clutter. Only open water was wanted,
  for orientation.

## Boundary overlay

- Acton's town bounds drawn as a **thick gold line** (`#C9A227`, lw 4.5).
- Constructed as **straight-line segments connecting the Corner-type monuments
  in `Order` sequence** (MA town boundaries are legally straight between
  corners — same assumption as `check_distance_to_line.py`). The ring is closed
  explicitly so the final ACMS↔AMS segment is drawn.
- **Acton/Carlisle/Concord corner:** the recorded row is a **witness monument**
  ~35 m from the true corner (which sits inside a private house). The gold line
  runs to the **true corner** — coordinates `42.50447314, -71.38494746`, parsed
  from that row's "Notes on Monument" text — substituted at Order 12. The
  witness monument keeps its own icon at its recorded (different) coordinates,
  near but not on the line.

## Icons (3 types)

Icon **shape encodes monument `Type`**, independent of the callout box's color
(which encodes `Status`) — two visual channels (shape + color), also better for
colorblind readers. Hollow markers (transparent face, dark `#1a1a1a` outline)
so roads underneath stay visible; solid dots were too hard to tell apart.

1. **Corner** — circle (`o`)
2. **Street Crossing** — square (`s`)
3. **Witness** — triangle (`^`)

The `Type = "Witness"` value was added to the spreadsheet for both witness
rows — the ACC witness monument and the Acton/Littleton "W B Marker" on Fort
Pond Road (Order 31). **Already done** (Jim confirmed).

## Callout boxes (51)

- One **square** box per monument (`Order` 1–51), numbered by `Order`, colored
  by `Status` using the shared `code/status_colors.py` palette (Painted green,
  Found blue, Couldn't paint orange, Not Found red, Documented gray). Large
  bold number, minimal padding — deliberately matching the order/status boxes
  on the monument-listing pages (fontsize 21 in a 0.58in box).
- The **2 monuments with no coordinates** still get a numbered box in `Order`
  position but **no callout line** (nothing to point at).
- **Placement — square boxes on a rectangular perimeter, walked
  counterclockwise from Order 1 (ACMS) in the lower-right corner.** Note this is
  the *opposite* rotational sense from `Order` itself, which runs clockwise
  around the actual boundary from ACMS — stated explicitly so a reader doesn't
  assume they match. Square boxes are what keep the edge-to-edge gap constant
  across the four page corners.
- **Per-side pitch, each side owns one corner outright** (the "corner-fix"
  algorithm): a first pass with a single global arc-length pitch is used only
  to *assign* which `Order` values group onto which side; then each side places
  its first box exactly on its owned page corner and computes its own pitch from
  its own box count and side length. This avoids the corner-overlap bug that a
  single global pitch produces — pure uniform arc-length spacing only guarantees
  equal spacing measured *along the path*, so at a 90° corner the straight-line
  gap between two boxes on either side of the bend collapses unless one box sits
  exactly on the vertex. Gaps now vary slightly side to side (acceptable to Jim,
  clearly better than overlap).

## Callout lines (leaders)

- Each box (with coordinates) connects to its monument's icon with a **`#5a5a5a`,
  linewidth-1.1** leader.
- **The leader attaches to the box on its interior-facing edge**, not the box
  center (Jim, Jul 9): the midpoint of the side facing the map for an edge box
  (left-middle for a right-edge box, top-middle for a bottom-edge box, etc.),
  and the **inner corner** for each of the 4 boxes that sit on a page corner.
- Each leader is a shallow **quadratic Bézier that bows away from the town
  center**, so lines separate and hug the outer margin. Goal: **minimize leaders
  crossing back through the map interior or the gold boundary line.** Treated as
  an optimization goal, not a hard guarantee — full avoidance isn't always
  possible depending on where an icon sits.

## Legend

- Positioned in the **middle of the map**, with its own background
  (fine to obscure roads behind it), sized to hug its content.
- Lists the **5 status colors** (Painted / Found / Couldn't paint / Not Found /
  Documented) and the **3 icon types** (Corner / Street Crossing / Witness).

## Compass rose

- Directly **below the legend**, same horizontal center, showing which way is
  north given the page rotation (arrow is not straight up).

## Title, caption and footer

- **Title:** "Overview Map" — centered, bold (~20pt), with a rule beneath,
  in a reserved band at the top of the page above the perimeter boxes,
  matching the centered H1 + rule style the intro sections use (`intro2pdf.py`).
- **Caption:** "Numbered boxes correspond to the Monument Listings section" —
  large (13pt), dark, bold, reading like a diagram title, centered near the
  bottom.
- **Footer:** right-justified "Overview Map, page 1 of 1" in the shared intro
  footer style (Helvetica 9pt, `#555555`, ending at the 1in body margin, 26pt
  up from the bottom edge — see "Page numbering — two-part footer" in
  `code/claude.md`). The left-justified whole-report footer is stamped later at
  final assembly.

## Open items

- [x] **Clickable callout boxes** — DONE Jul 9 2026. Rather than
      named-destination anchors, the links are added at final assembly:
      `overview_map.py` records each box's rectangle (PDF points) to
      `overview_map_links.json`, and `assemble_report.py` overlays an internal
      GoTo link over each box on the merged map page, targeting that
      monument's listing page (`listings_start + Order - 1`). Works because
      everything lands in one combined PDF, so it's a plain intra-document
      jump. Guarded to skip if the listings page count ever stops matching the
      box count 1:1.
- [ ] Long-term: if corner coordinates are revised, re-run
      `overview_map.py` (rotation and boundary self-update from the sheet).
