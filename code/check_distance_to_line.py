"""One-off QA check: how far is each monument's recorded coordinate from
the straight town-line segment connecting its two neighboring official
corner monuments? Massachusetts town boundaries are straight survey lines
between corner monuments, so a street-crossing monument that's far off
that line likely has a bad recorded coordinate (map-estimate error, typo,
etc.) rather than an actually-crooked boundary.

Not part of the report pipeline -- a standalone diagnostic Jim asked for.
"""
import math
import re

import pandas as pd

XLSX = '../Acton Bounds.xlsx'

# Acton/Carlisle/Concord's Latitude/Longitude columns hold the *witness*
# monument's position (the real corner is inside a house; the state put up
# a witness marker ~35m away -- see code/claude.md). Using the witness
# position as a line vertex would throw off the distance check for every
# monument on the two segments touching this corner, so we substitute the
# true corner coordinates recorded in this row's "Notes on Monument" text.
CARLISLE_CONCORD_OVERRIDE_NAME = 'Acton/Carlisle/Concord'


def parse_true_corner(notes_text):
    m = re.search(r'actual corner is at\s*([\-\d.]+),\s*([\-\d.]+)', notes_text)
    if not m:
        raise SystemExit(f"Couldn't parse true-corner coordinates from: {notes_text!r}")
    return float(m.group(1)), float(m.group(2))


def to_local_meters(lat, lon, lat0, lon0):
    """Flat-earth approximation, fine at this scale (a few km across)."""
    x = (lon - lon0) * 111320 * math.cos(math.radians(lat0))
    y = (lat - lat0) * 110540
    return x, y


def point_to_segment_distance(px, py, ax, ay, bx, by):
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    seg_len_sq = abx * abx + aby * aby
    t = max(0.0, min(1.0, (apx * abx + apy * aby) / seg_len_sq))
    cx, cy = ax + t * abx, ay + t * aby
    dist = math.hypot(px - cx, py - cy)
    return dist, t


def main():
    df = pd.read_excel(XLSX, sheet_name='Monuments').sort_values('Order').reset_index(drop=True)

    lat0, lon0 = df['Latitude'].mean(), df['Longitude'].mean()

    # Per-row working coordinates, with the Carlisle/Concord override applied.
    lat = df['Latitude'].copy()
    lon = df['Longitude'].copy()
    cc_mask = df['Name'] == CARLISLE_CONCORD_OVERRIDE_NAME
    true_lat, true_lon = parse_true_corner(df.loc[cc_mask, 'Notes on Monument'].iloc[0])
    lat.loc[cc_mask] = true_lat
    lon.loc[cc_mask] = true_lon

    corner_idx = df.index[df['Type'] == 'Corner'].tolist()
    n_corners = len(corner_idx)

    results = []
    for seg in range(n_corners):
        start_i = corner_idx[seg]
        end_i = corner_idx[(seg + 1) % n_corners]
        ax, ay = to_local_meters(lat[start_i], lon[start_i], lat0, lon0)
        bx, by = to_local_meters(lat[end_i], lon[end_i], lat0, lon0)

        # Rows strictly between start_i and end_i in Order sequence
        # (wrapping past the end of the table for the final segment).
        if seg + 1 < n_corners:
            between = range(start_i + 1, end_i)
        else:
            between = list(range(start_i + 1, len(df))) + list(range(0, end_i))

        for i in between:
            if pd.isna(lat[i]) or pd.isna(lon[i]):
                results.append((df.at[i, 'Order'], df.at[i, 'Name'], None, None,
                                 df.at[i, 'Name']))
                continue
            px, py = to_local_meters(lat[i], lon[i], lat0, lon0)
            dist, t = point_to_segment_distance(px, py, ax, ay, bx, by)
            results.append((df.at[i, 'Order'], df.at[i, 'Name'], dist, t,
                             f"{df.at[start_i,'Name']} -> {df.at[end_i,'Name']}"))

    print(f"{'Order':>5}  {'Distance (m)':>12}  {'t':>5}  Name  [segment]")
    for order, name, dist, t, seg_name in sorted(
            results, key=lambda r: (-1 if r[2] is None else -r[2])):
        if dist is None:
            print(f"{order:>5}  {'no coords':>12}  {'':>5}  {name}")
        else:
            flag = '  <-- off-segment (t outside 0-1)' if not (0 <= t <= 1) else ''
            print(f"{order:>5}  {dist:>12.1f}  {t:>5.2f}  {name}  [{seg_name}]{flag}")


if __name__ == '__main__':
    main()
