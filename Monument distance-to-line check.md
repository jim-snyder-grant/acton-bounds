# Monument distance-to-line check

Results from `code/check_distance_to_line.py` (Jul 7 2026): for each
Street-Crossing monument, the perpendicular distance from its recorded
coordinates to the straight line connecting its two nearest official
corner monuments. Massachusetts town boundaries are straight survey
lines between corners, so a large offset usually means a bad recorded
coordinate rather than an actually-crooked boundary.

Uses the true Acton/Carlisle/Concord corner location parsed from that
row's "Notes on Monument" text (42.50447314, -71.38494746) as the line
anchor there, not the witness-monument coordinates in the Lat/Long
columns.

## Clear data-entry bug (not a field discrepancy)

- [ ] **Acton/Maynard Conant Street** (Order 48): ~110 km off the line.
      Stored latitude is `43.445701`, but every neighboring Acton/Maynard
      monument is `42.44`–`42.45`. Almost certainly a typo — `43` should
      be `42`.

## Worth a field re-check — real, unexplained offsets

- [ ] **Acton/Concord Great Road** (Order 8): ~52m off the line. Source
      "GIS iPad," no notes explaining why.
- [ ] **Acton/Littleton Nagog Hill Road** (Order 29): ~16m off. Source
      "GIS iPad." Its own note says "right next to boundary marker" —
      16m is more than that note implies.

## Not concerning — self-explained

- **Acton/Littleton W B Marker on Fort Pond Road** (Order 31): ~15m
  off, but it's explicitly a Witness Bound (placed because a monument
  couldn't go at the actual boundary point) — an offset is expected
  here, not an error.

## Everything else

All other monuments with known coordinates are within ~4m of the line
— normal GPS/map-estimate noise, not worth chasing. Two monuments have
no coordinates at all (Acton/Carlisle unknown road, Acton/Westford
unknown road) and were skipped.

## Re-running after fixes

`cd code && .venv/bin/python3 check_distance_to_line.py` — prints every
monument's distance, sorted worst-first. Re-run any time after editing
coordinates to see the updated picture.
