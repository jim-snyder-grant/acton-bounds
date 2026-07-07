"""One-off helper: pull Acton entries out of a MassDOT Town_Corners.kml
export into a CSV Jim can import into Google Sheets. Not part of the
report pipeline (bounds2pdf.py doesn't import this).

KML <Point><coordinates> is always WGS84 lon,lat regardless of the
source projection (per the KML spec) -- MassGIS's own data is state
plane meters (NAD83, EPSG 26986), so this Point value is MassGIS's own
WGS84 conversion, not something we're computing ourselves.
"""
import csv
import re
import sys
import xml.etree.ElementTree as ET

NS = {'kml': 'http://www.opengis.net/kml/2.2'}


def state_name_to_our_format(name):
    """'ACTON-CARLISLE 1' -> 'Acton/Carlisle 1'; '-'-joined town names,
    each title-cased, any trailing ' N' disambiguator left as-is."""
    return '/'.join(part.strip().title() for part in name.split('-'))


def main(kml_path, out_path):
    tree = ET.parse(kml_path)
    root = tree.getroot()

    rows = []
    for placemark in root.iter('{http://www.opengis.net/kml/2.2}Placemark'):
        corner = None
        for sd in placemark.iter('{http://www.opengis.net/kml/2.2}SimpleData'):
            if sd.get('name') == 'Corner':
                corner = sd.text
                break
        if not corner or 'acton' not in corner.lower():
            continue

        point = placemark.find('.//kml:Point/kml:coordinates', NS)
        if point is None or not point.text:
            continue
        lon, lat, *_ = point.text.strip().split(',')

        rows.append({
            'Name': state_name_to_our_format(corner),
            'Latitude': lat,
            'Longitude': lon,
        })

    with open(out_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'Latitude', 'Longitude'])
        writer.writeheader()
        writer.writerows(rows)

    print(f'Wrote {len(rows)} rows to {out_path}')


if __name__ == '__main__':
    kml_path = sys.argv[1] if len(sys.argv) > 1 else 'Town_Corners.kml'
    out_path = sys.argv[2] if len(sys.argv) > 2 else 'acton_town_corners.csv'
    main(kml_path, out_path)
