#!/usr/bin/env python3
"""Overview Map generator for the Acton Bounds report (report section 5).

Produces a single legal-portrait (8.5x14in) vector-PDF page: Acton's boundary
as a thick gold line through the corner monuments in Order sequence, every
monument as a hollow type-coded icon, and a numbered/status-colored callout
box per monument arranged counter-clockwise around the page perimeter (Order 1
= ACMS = lower right). The base map inside the boundary is real MassGIS data:
MassDOT RoadInventory (all local roads, weighted by functional class) and
MassDEP Hydrography 1:25,000 open water (ponds/lakes, labeled by name).

See "Overview Map spec.md" in the Bounds folder for the full design rationale.
The geometry/layout (projection, rotation, boundary, boxes, legend, compass)
is ported from claude.ai's approved mockup, with the per-side corner-fix
box-placement algorithm.

Data sources (both free, public domain, no API key):
  Roads: https://gis.massdot.state.ma.us/arcgis/rest/services/Roads/
         RoadInventory/MapServer/0  (queried by bounding box, cached locally)
  Water: https://s3.us-east-1.amazonaws.com/download.massgis.digital.mass.gov/
         shapefiles/state/hydro25k.zip  (downloaded once to gis_data/)

Usage:
  python3 overview_map.py [--refresh-roads]
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon as MplPolygon

import geopandas as gpd
import shapely
from shapely.geometry import LineString, Polygon, shape
from shapely.ops import transform as shp_transform

from status_colors import STATUS_COLORS, DEFAULT_STATUS_COLOR, knockout_text_color

# --- paths ---
HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, "..", "Acton Bounds.xlsx")
GIS_DIR = os.path.join(HERE, "gis_data")
HYDRO_ZIP = os.path.join(GIS_DIR, "hydro25k.zip")
ROADS_CACHE = os.path.join(GIS_DIR, "roads_acton.geojson")
OUT_PDF = os.path.join(HERE, "overview_map.pdf")
OUT_PNG = os.path.join(HERE, "overview_map.png")
LINKS_JSON = os.path.join(HERE, "overview_map_links.json")

ROADS_URL = ("https://gis.massdot.state.ma.us/arcgis/rest/services/Roads/"
             "RoadInventory/MapServer/0/query")
HYDRO_DOWNLOAD_URL = ("https://s3.us-east-1.amazonaws.com/"
                      "download.massgis.digital.mass.gov/shapefiles/state/hydro25k.zip")

# ACC true corner (Acton/Carlisle/Concord) -- the recorded row is the witness
# monument ~35m away, so the gold line uses this true-corner coordinate parsed
# from that row's "Notes on Monument" text instead. Order 12 in the sequence.
ACC_TRUE_LAT, ACC_TRUE_LON = 42.50447314, -71.38494746
ACC_ORDER = 12

ICON_MARKERS = {"Corner": "o", "Street Crossing": "s", "Witness": "^"}
N_TOTAL = 51


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------
def load_monuments():
    df = pd.read_excel(XLSX, sheet_name="Monuments")
    df = df.dropna(subset=["Order"]).copy()
    df["Order"] = df["Order"].astype(int)
    df = df.sort_values("Order").reset_index(drop=True)
    return df


def fetch_roads(bbox_wgs84, refresh=False):
    """Return list of GeoJSON road features (WGS84) intersecting bbox.
    Cached to gis_data/roads_acton.geojson; --refresh-roads bypasses the cache."""
    if os.path.exists(ROADS_CACHE) and not refresh:
        with open(ROADS_CACHE) as fh:
            return json.load(fh)["features"]

    xmin, ymin, xmax, ymax = bbox_wgs84
    features = []
    offset = 0
    page = 2000
    while True:
        params = {
            "geometry": f"{xmin},{ymin},{xmax},{ymax}",
            "geometryType": "esriGeometryEnvelope",
            "inSR": "4326", "outSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "St_Name,Route_Number,F_F_Class",
            "resultOffset": str(offset),
            "resultRecordCount": str(page),
            "f": "geojson",
        }
        url = ROADS_URL + "?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        got = data.get("features", [])
        features.extend(got)
        if len(got) < page:
            break
        offset += page
    os.makedirs(GIS_DIR, exist_ok=True)
    with open(ROADS_CACHE, "w") as fh:
        json.dump({"type": "FeatureCollection", "features": features}, fh)
    print(f"  fetched {len(features)} road segments from MassDOT, cached")
    return features


def load_hydro_open_water(bbox_wgs84):
    """Return a GeoDataFrame (EPSG:4326) of open-water polygons in the bbox,
    with a NAME column, from the cached hydro25k shapefile.

    Open water = POLY_CODE in {1, 6} per the MassGIS HYDRO25K metadata domain:
      1 = RESERVOIR (with PWSID)  -- e.g. Nagog Pond
      6 = LAKE, POND, WIDE RIVER, IMPOUNDMENT
    Excluded: 2 wetland/marsh/swamp/bog, 3 submerged wetland, 4 cranberry bog,
    5 salt wetland, 7 tidal flats, 8 bay/ocean, 9 inundated area."""
    if not os.path.exists(HYDRO_ZIP):
        sys.exit(f"Missing {HYDRO_ZIP}. Download it once from:\n  {HYDRO_DOWNLOAD_URL}")
    # bbox for pyogrio must be in the layer CRS (EPSG:26986)
    xmin, ymin, xmax, ymax = bbox_wgs84
    b = gpd.GeoSeries([shapely.geometry.box(xmin, ymin, xmax, ymax)], crs="EPSG:4326")
    b26986 = b.to_crs("EPSG:26986").total_bounds
    gdf = gpd.read_file(f"zip://{HYDRO_ZIP}!HYDRO25K_POLY.shp", bbox=tuple(b26986))
    gdf = gdf[gdf["POLY_CODE"].isin([1, 6])].to_crs("EPSG:4326")
    return gdf


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh-roads", action="store_true",
                    help="re-query MassDOT roads instead of using the local cache")
    args = ap.parse_args()

    df = load_monuments()

    # --- local equirectangular projection (meters), centered on the data ---
    lat0 = df["Latitude"].dropna().mean()
    lon0 = df["Longitude"].dropna().mean()
    m_per_deg_lat = 110574.0
    m_per_deg_lon = 111320.0 * np.cos(np.radians(lat0))

    def project(lat, lon):
        return (np.asarray(lon) - lon0) * m_per_deg_lon, (np.asarray(lat) - lat0) * m_per_deg_lat

    df["x"], df["y"] = project(df["Latitude"], df["Longitude"])

    # --- rotation from the ACMS->AMS bearing (spec: run that line parallel to
    #     the page bottom); derived from coordinates, not hardcoded ---
    try:
        acms = df[df["Name"] == "Acton/Concord/Maynard/Sudbury"].iloc[0]
        ams = df[df["Name"] == "Acton/Maynard/Stow"].iloc[0]
    except IndexError:
        sys.exit("Could not find ACMS/AMS corner rows by name; check the Name column.")
    dx, dy = ams["x"] - acms["x"], ams["y"] - acms["y"]
    rot_rad = np.radians(180.0 - np.degrees(np.arctan2(dy, dx)))
    print(f"  rotation: {np.degrees(rot_rad):.2f} degrees (from ACMS->AMS)")

    cos_r, sin_r = np.cos(rot_rad), np.sin(rot_rad)

    def rotate(x, y):
        x = np.asarray(x); y = np.asarray(y)
        return x * cos_r - y * sin_r, x * sin_r + y * cos_r

    df["rx"], df["ry"] = rotate(df["x"].values, df["y"].values)

    # ACC true corner in local + rotated meters
    accx, accy = project(ACC_TRUE_LAT, ACC_TRUE_LON)
    accx, accy = float(accx), float(accy)

    def L2F(x, y):
        """local meters -> figure inches (rotate then place on page)."""
        rx, ry = rotate(x, y)
        return to_fig(rx, ry)

    # --- boundary polygon: Corner-type monuments + ACC true corner, in Order ---
    corners = df[df["Type"] == "Corner"][["Name", "Order", "x", "y"]].copy()
    corners = pd.concat([corners, pd.DataFrame(
        [{"Name": "ACC true corner", "Order": ACC_ORDER, "x": accx, "y": accy}])])
    corners = corners.sort_values("Order").reset_index(drop=True)
    boundary_local = list(zip(corners["x"], corners["y"]))
    boundary_poly = Polygon(boundary_local)  # unrotated local meters, for clipping

    # --- page extent (rotated-meter space), matching the mockup ---
    finite = df.dropna(subset=["rx", "ry"])
    data_xmin, data_xmax = finite["rx"].min(), finite["rx"].max()
    data_ymin, data_ymax = finite["ry"].min(), finite["ry"].max()
    BUFFER_M = 804.672   # 0.5 mile context margin (kept plain per spec)
    BOX_BAND_M = 750.0
    map_xmin, map_xmax = data_xmin - BUFFER_M, data_xmax + BUFFER_M
    map_ymin, map_ymax = data_ymin - BUFFER_M, data_ymax + BUFFER_M
    page_xmin, page_xmax = map_xmin - BOX_BAND_M, map_xmax + BOX_BAND_M
    page_ymin, page_ymax = map_ymin - BOX_BAND_M, map_ymax + BOX_BAND_M
    page_w_m, page_h_m = page_xmax - page_xmin, page_ymax - page_ymin

    fig_w_in, fig_h_in = 8.5, 14.0
    MARGIN_IN = 0.4
    TITLE_BAND_IN = 0.65   # reserved strip at the top for the "Overview Map" title
    draw_w_in = fig_w_in - 2 * MARGIN_IN
    draw_h_in = fig_h_in - 2 * MARGIN_IN - TITLE_BAND_IN
    scale = min(draw_w_in / page_w_m, draw_h_in / page_h_m)

    # to_fig centers the map within [MARGIN_IN, MARGIN_IN + draw_h_in] vertically,
    # i.e. below the reserved title band, keeping the bottom margin fixed.
    def to_fig(mx, my):
        mx = np.asarray(mx); my = np.asarray(my)
        fx = MARGIN_IN + (mx - page_xmin) * scale + (draw_w_in - page_w_m * scale) / 2
        fy = MARGIN_IN + (my - page_ymin) * scale + (draw_h_in - page_h_m * scale) / 2
        return fx, fy

    # --- fetch base-map data over the boundary's WGS84 bbox ---
    corner_lat = [ACC_TRUE_LAT] + list(df[df["Type"] == "Corner"]["Latitude"].dropna())
    corner_lon = [ACC_TRUE_LON] + list(df[df["Type"] == "Corner"]["Longitude"].dropna())
    pad = 0.006
    bbox_wgs84 = (min(corner_lon) - pad, min(corner_lat) - pad,
                  max(corner_lon) + pad, max(corner_lat) + pad)

    print("Loading roads...")
    road_features = fetch_roads(bbox_wgs84, refresh=args.refresh_roads)
    print("Loading hydrography...")
    hydro = load_hydro_open_water(bbox_wgs84)

    # --- figure ---
    fig = plt.figure(figsize=(fig_w_in, fig_h_in))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, fig_w_in); ax.set_ylim(0, fig_h_in)
    ax.axis("off")

    # white page
    mx0f, my0f = to_fig(page_xmin, page_ymin)
    mx1f, my1f = to_fig(page_xmax, page_ymax)
    ax.add_patch(Rectangle((mx0f, my0f), mx1f - mx0f, my1f - my0f,
                           facecolor="#FFFFFF", edgecolor="none", zorder=0))

    # subtle town-interior fill so the boundary reads even where base map is sparse.
    # Close the ring explicitly (append the first point) so the polyline drawn
    # for the gold line below includes the final ACMS<->AMS contact segment.
    boundary_fig = [L2F(x, y) for x, y in boundary_local] + [L2F(*boundary_local[0])]
    bxs, bys = zip(*boundary_fig)
    ax.add_patch(MplPolygon(list(zip(bxs, bys)), closed=True,
                            facecolor="#FCFBF6", edgecolor="none", zorder=0.5))
    cenx, ceny = L2F(boundary_poly.centroid.x, boundary_poly.centroid.y)

    # --- roads (clipped to boundary, weighted by functional class) ---
    def road_style(fc):
        try:
            fc = int(fc)
        except (TypeError, ValueError):
            return 0.5, "#a8a8a8"
        if fc in (1, 2, 3):
            return 1.7, "#6f6f6f"   # interstate / principal arterial
        if fc == 4:
            return 1.2, "#7d7d7d"   # minor arterial
        if fc == 5:
            return 0.9, "#949494"   # major collector
        if fc == 6:
            return 0.7, "#a0a0a0"   # minor collector
        return 0.5, "#b0b0b0"       # local / unknown

    def iter_lines(geom):
        if geom.is_empty:
            return
        gt = geom.geom_type
        if gt == "LineString":
            yield list(geom.coords)
        elif gt in ("MultiLineString", "GeometryCollection"):
            for g in geom.geoms:
                yield from iter_lines(g)

    def road_label(props):
        rn = (props.get("Route_Number") or "").strip()
        if rn and rn.strip("0"):
            try:
                num = int(rn)
                if num <= 300:   # real signed MA route numbers; larger = internal ID
                    return f"Route {num}"
            except ValueError:
                pass
        name = (props.get("St_Name") or "").strip()
        return name.title() if name else ""

    n_roads_drawn = 0
    road_records = []  # (fc_int, label, clipped_geom) for major-road labeling
    for feat in road_features:
        geom = feat.get("geometry")
        if not geom:
            continue
        line = shape(geom)
        # project WGS84 -> local meters (coords are lon,lat)
        line = shp_transform(lambda lon, lat, z=None: project(lat, lon), line)
        clipped = line.intersection(boundary_poly)
        if clipped.is_empty:
            continue
        props = feat["properties"]
        fc_raw = props.get("F_F_Class")
        try:
            fc_int = int(fc_raw)
        except (TypeError, ValueError):
            fc_int = None
        lw, color = road_style(fc_raw)
        for coords in iter_lines(clipped):
            fxs, fys = zip(*[L2F(x, y) for x, y in coords])
            ax.plot(fxs, fys, color=color, linewidth=lw, solid_capstyle="round",
                    zorder=2)
            n_roads_drawn += 1
        if fc_int is not None:
            road_records.append((fc_int, road_label(props), clipped))

    # --- label the single largest road (lowest functional class present) ---
    n_road_labels = 0
    fcs = [r[0] for r in road_records if r[1]]
    if fcs:
        min_fc = min(fcs)
        by_label = {}
        for fc, label, geom in road_records:
            if fc == min_fc and label:
                by_label.setdefault(label, []).append(geom)
        ranked = sorted(by_label.items(),
                        key=lambda kv: -sum(g.length for g in kv[1]))[:1]
        for label, geoms in ranked:
            pieces = [c for g in geoms for c in iter_lines(g)]
            longest = max(pieces, key=lambda c: LineString(c).length)
            mid = longest[len(longest) // 2]
            nbr = longest[min(len(longest) // 2 + 1, len(longest) - 1)]
            fx, fy = L2F(*mid)
            fx2, fy2 = L2F(*nbr)
            ang = np.degrees(np.arctan2(fy2 - fy, fx2 - fx))
            ang = (ang + 180) % 180
            if ang > 90:
                ang -= 180
            ax.text(fx, fy, label, fontsize=7.5, color="#404040", rotation=ang,
                    ha="center", va="center", rotation_mode="anchor", zorder=6.5,
                    bbox=dict(boxstyle="round,pad=0.1", facecolor="white",
                              edgecolor="none", alpha=0.7))
            n_road_labels += 1

    # --- open water (clipped to boundary, filled) ---
    def iter_polys(geom):
        if geom.is_empty:
            return
        gt = geom.geom_type
        if gt == "Polygon":
            yield geom
        elif gt in ("MultiPolygon", "GeometryCollection"):
            for g in geom.geoms:
                yield from iter_polys(g)

    for _, wrow in hydro.iterrows():
        wgeom = shp_transform(lambda lon, lat, z=None: project(lat, lon), wrow.geometry)
        clipped = wgeom.intersection(boundary_poly)
        if clipped.is_empty:
            continue
        for poly in iter_polys(clipped):
            fxs, fys = zip(*[L2F(x, y) for x, y in poly.exterior.coords])
            ax.add_patch(MplPolygon(list(zip(fxs, fys)), closed=True,
                                    facecolor="#CFE3F2", edgecolor="#9EC9E2",
                                    linewidth=0.5, zorder=2.6))

    # --- gold boundary line ---
    ax.plot(bxs, bys, color="#C9A227", linewidth=4.5, solid_joinstyle="round",
            zorder=3)

    # --- callout boxes: per-side pitch, each side owns one corner (corner-fix) ---
    box_size = 0.58
    x_left_c, x_right_c = mx0f + box_size / 2, mx1f - box_size / 2
    y_bottom_c, y_top_c = my0f + box_size / 2, my1f - box_size / 2
    W_c, H_c = x_right_c - x_left_c, y_top_c - y_bottom_c
    P_c = 2 * (W_c + H_c)

    def side_of(frac):
        s = frac * P_c
        if s < H_c:
            return "right"
        elif s < H_c + W_c:
            return "top"
        elif s < 2 * H_c + W_c:
            return "left"
        return "bottom"

    df["side"] = [side_of((int(o) - 1) / N_TOTAL) for o in df["Order"]]
    side_orders = {s: sorted(df[df["side"] == s]["Order"].tolist())
                   for s in ["right", "top", "left", "bottom"]}
    # the first box on each side sits exactly on a page corner (corner-fix);
    # its callout leaves from the box's inner (toward-center) corner instead
    # of a side midpoint.
    corner_orders = {side_orders[s][0] for s in ("right", "top", "left", "bottom")
                     if side_orders[s]}
    side_by_order = dict(zip(df["Order"], df["side"]))
    page_cx, page_cy = (mx0f + mx1f) / 2, (my0f + my1f) / 2

    def box_anchor(order, bx, by):
        """Point on the box outline where its callout line attaches: the
        midpoint of the interior-facing side, or the inner corner for the
        four boxes that sit on a page corner."""
        h = box_size / 2
        if order in corner_orders:
            sx = 1 if bx < page_cx else -1
            sy = 1 if by < page_cy else -1
            return bx + sx * h, by + sy * h
        side = side_by_order[order]
        if side == "right":
            return bx - h, by
        if side == "left":
            return bx + h, by
        if side == "top":
            return bx, by - h
        return bx, by + h   # bottom

    positions = {}
    for o_i, o in enumerate(side_orders["right"]):    # owns bottom-right, walks up
        positions[o] = (x_right_c, y_bottom_c + o_i * (H_c / len(side_orders["right"])))
    for o_i, o in enumerate(side_orders["top"]):      # owns top-right, walks left
        positions[o] = (x_right_c - o_i * (W_c / len(side_orders["top"])), y_top_c)
    for o_i, o in enumerate(side_orders["left"]):     # owns top-left, walks down
        positions[o] = (x_left_c, y_top_c - o_i * (H_c / len(side_orders["left"])))
    for o_i, o in enumerate(side_orders["bottom"]):   # owns bottom-left, walks right
        positions[o] = (x_left_c + o_i * (W_c / len(side_orders["bottom"])), y_bottom_c)

    # curved callout leader: a quadratic Bezier bowing away from the town
    # center, so lines separate and hug the outer margin instead of cutting
    # straight across the interior.
    def draw_leader(bx, by, ix, iy):
        length = np.hypot(ix - bx, iy - by)
        if length < 1e-6:
            return
        px, py = -(iy - by) / length, (ix - bx) / length   # perpendicular unit
        mx, my = (bx + ix) / 2, (by + iy) / 2
        off = 0.16 * length
        c1 = (mx + px * off, my + py * off)
        c2 = (mx - px * off, my - py * off)
        # control point on whichever side is farther from the town center
        d1 = (c1[0] - cenx) ** 2 + (c1[1] - ceny) ** 2
        d2 = (c2[0] - cenx) ** 2 + (c2[1] - ceny) ** 2
        cx, cy = c1 if d1 > d2 else c2
        t = np.linspace(0, 1, 30)
        xs = (1 - t) ** 2 * bx + 2 * (1 - t) * t * cx + t ** 2 * ix
        ys = (1 - t) ** 2 * by + 2 * (1 - t) * t * cy + t ** 2 * iy
        ax.plot(xs, ys, color="#5a5a5a", linewidth=1.1, alpha=0.85, zorder=3.2)

    # icons (draw before boxes so callout lines/boxes sit on top cleanly);
    # transparent face so the roads underneath stay visible
    for _, row in finite.iterrows():
        fx, fy = to_fig(row["rx"], row["ry"])
        marker = ICON_MARKERS.get(row["Type"], "o")
        ax.plot(fx, fy, marker=marker, markersize=12, markerfacecolor="none",
                markeredgecolor="#1a1a1a", markeredgewidth=2.0, zorder=4)

    # box rectangles in PDF points (fig inches * 72; matplotlib's PDF origin is
    # bottom-left, same as PDF) -- written to a sidecar so assemble_report.py can
    # drop an internal "go to that monument's page" link over each box.
    box_rects = {}
    for _, row in df.iterrows():
        order = int(row["Order"])
        fx, fy = positions[order]
        box_rects[order] = [round((fx - box_size / 2) * 72, 2),
                            round((fy - box_size / 2) * 72, 2),
                            round((fx + box_size / 2) * 72, 2),
                            round((fy + box_size / 2) * 72, 2)]
        color = STATUS_COLORS.get(row["Status"], DEFAULT_STATUS_COLOR)
        txt_color = knockout_text_color(color)
        if not pd.isna(row["rx"]):
            ix, iy = to_fig(row["rx"], row["ry"])
            ax_x, ax_y = box_anchor(order, fx, fy)
            draw_leader(ax_x, ax_y, ix, iy)
        ax.add_patch(FancyBboxPatch((fx - box_size / 2, fy - box_size / 2),
                     box_size, box_size,
                     boxstyle="round,pad=0.015,rounding_size=0.05",
                     facecolor=color, edgecolor="#333333", linewidth=0.6, zorder=5))
        ax.text(fx, fy, str(order), ha="center", va="center", fontsize=21,
                color=txt_color, fontweight="bold", zorder=6)

    # --- legend ---
    draw_legend(ax, rot_rad)

    # --- title (centered bold + rule, matching the intro sections' H1) in the
    #     reserved top band, above the perimeter boxes ---
    title_y = fig_h_in - MARGIN_IN - 0.30
    ax.text(fig_w_in / 2, title_y, "Overview Map", ha="center", va="center",
            fontsize=20, fontweight="bold", color="#000000", zorder=8)
    rule_y = title_y - 0.27
    ax.plot([mx0f, mx1f], [rule_y, rule_y], color="#333333", linewidth=1.0, zorder=8)

    # --- caption ---
    ax.text(fig_w_in / 2, MARGIN_IN + 0.15,
            "Numbered boxes correspond to the Monument Listings section",
            ha="center", va="bottom", fontsize=13, color="#222222",
            fontweight="bold", zorder=8)

    # --- footer (matches the other sections' right-justified footer style:
    #     Helvetica 9pt #555555, ending at the 1in body margin, 26pt up from
    #     the bottom edge -- see "Page numbering" in code/claude.md) ---
    FOOTER_MARGIN_IN = 1.0
    ax.text(fig_w_in - FOOTER_MARGIN_IN, 26.0 / 72.0,
            "Overview Map, page 1 of 1", ha="right", va="baseline",
            fontsize=9, color="#555555", family="sans-serif", zorder=8)

    fig.savefig(OUT_PDF)
    fig.savefig(OUT_PNG, dpi=200)

    with open(LINKS_JSON, "w") as fh:
        json.dump({"page_w_pt": fig_w_in * 72, "page_h_pt": fig_h_in * 72,
                   "boxes": box_rects}, fh, indent=2)

    print(f"  roads: {n_roads_drawn} segments, {n_road_labels} labeled")
    print(f"Wrote {OUT_PDF}, {OUT_PNG}, {os.path.basename(LINKS_JSON)}")


def draw_legend(ax, rot_rad):
    # Width snug to the content ("Couldn't paint" is the widest label) and the
    # center nudged left so the right edge clears the gold boundary line; the
    # left edge stays where it was (it already had clear space).
    leg_w = 1.95
    row_h = 0.34
    n_status, n_types = len(STATUS_COLORS), len(ICON_MARKERS)
    title_h, header_h, gap_h, pad = 0.44, 0.30, 0.16, 0.18
    leg_h = pad + title_h + header_h + n_status * row_h + gap_h + header_h + n_types * row_h + pad
    leg_cx, leg_cy = 4.65, 7.55
    leg_x0, leg_y0 = leg_cx - leg_w / 2, leg_cy - leg_h / 2
    ax.add_patch(FancyBboxPatch((leg_x0, leg_y0), leg_w, leg_h,
                 boxstyle="round,pad=0.05,rounding_size=0.08",
                 facecolor="#FBF8F1", edgecolor="#999999", linewidth=1.0, zorder=7))
    y = leg_y0 + leg_h - pad
    ax.text(leg_cx, y, "Legend", ha="center", va="top", fontsize=13,
            fontweight="bold", zorder=8)
    y -= title_h
    ax.text(leg_x0 + 0.16, y, "Status", fontsize=11, fontweight="bold", va="top", zorder=8)
    y -= header_h
    for name, color in STATUS_COLORS.items():
        y -= row_h
        ax.add_patch(Rectangle((leg_x0 + 0.16, y + row_h / 2 - 0.10), 0.34, 0.20,
                     facecolor=color, edgecolor="#333", linewidth=0.4, zorder=8))
        ax.text(leg_x0 + 0.66, y + row_h / 2, name, fontsize=11, va="center", zorder=8)
    y -= gap_h
    ax.text(leg_x0 + 0.16, y, "Monument type", fontsize=11, fontweight="bold", va="top", zorder=8)
    y -= header_h
    for name, marker in ICON_MARKERS.items():
        y -= row_h
        ax.plot(leg_x0 + 0.33, y, marker=marker, markersize=12, markerfacecolor="none",
                markeredgecolor="#1a1a1a", markeredgewidth=1.6, zorder=8)
        ax.text(leg_x0 + 0.66, y, name, fontsize=11, va="center", zorder=8)

    # compass rose below the legend, reflecting the page rotation
    cr_cx, cr_cy = leg_cx, leg_y0 - 0.80
    north = np.array([np.cos(rot_rad + np.pi / 2), np.sin(rot_rad + np.pi / 2)])
    arrow_len = 0.38
    ax.add_patch(Circle((cr_cx, cr_cy), 0.48, facecolor="#FBF8F1",
                 edgecolor="#999999", linewidth=1.0, zorder=9))
    ax.annotate("", xy=(cr_cx + north[0] * arrow_len, cr_cy + north[1] * arrow_len),
                xytext=(cr_cx, cr_cy),
                arrowprops=dict(facecolor="#333333", edgecolor="#333333",
                                width=2.5, headwidth=8, headlength=9), zorder=10)
    ax.text(cr_cx + north[0] * (arrow_len + 0.16), cr_cy + north[1] * (arrow_len + 0.16),
            "N", ha="center", va="center", fontsize=10, fontweight="bold", zorder=10)


if __name__ == "__main__":
    main()
