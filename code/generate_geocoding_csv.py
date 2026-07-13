"""One-off: export monument coordinates as a lon/lat CSV for Geoapify's
reverse-geocoding drag-and-drop tool (geoapify.com/tools/reverse-geocoding-online).

Not part of the report pipeline -- a standalone utility Jim asked for.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent          # Bounds root
XLSX = ROOT / 'Acton Bounds.xlsx'
OUT = ROOT / 'monument_coordinates_for_geoapify.csv'


def main():
    df = pd.read_excel(XLSX, sheet_name='Monuments').sort_values('Order').reset_index(drop=True)

    missing = df[df['Latitude'].isna() | df['Longitude'].isna()]
    if len(missing):
        print(f'Skipping {len(missing)} row(s) with no coordinates:')
        for _, row in missing.iterrows():
            print(f"  Order {row['Order']}: {row['Name']}")

    have_coords = df.dropna(subset=['Latitude', 'Longitude'])
    out = have_coords[['Longitude', 'Latitude']].rename(
        columns={'Longitude': 'lon', 'Latitude': 'lat'})
    out.to_csv(OUT, index=False)
    print(f'Wrote {len(out)} rows to {OUT}')
    print('Row order matches Order-column sequence -- match Geoapify\'s '
          'output back to monuments by row position, since no name/ID '
          'column is included (Jim\'s spec: lon/lat only).')


if __name__ == '__main__':
    main()
