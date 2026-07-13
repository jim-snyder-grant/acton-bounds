"""
merge_docushare.py

Merges docushare_urls.csv (produced by scrape_docushare.py) into
photo_manifest.csv by filename, populating/updating the docushare_url
column. Rows with no match are left untouched (docushare_url stays blank
or whatever it was before) -- not every photo will be uploaded yet.

Run from the code/ directory:
    python3 scrape_docushare.py
    python3 merge_docushare.py
"""

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent          # code/ (both files are code-local)
DOCUSHARE_URLS_PATH = HERE / 'docushare_urls.csv'
MANIFEST_PATH = HERE / 'photo_manifest.csv'

MANIFEST_COLUMNS = [
    'filename',
    'monument_name',
    'datetime',
    'caption',
    'include',
    'exclude_reason',
    'section',
    'orientation',
    'cover_candidate',
    'docushare_url',
]


def load_docushare_urls(path: Path) -> dict:
    urls = {}
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            urls[row['filename']] = row['docushare_url']
    return urls


def main():
    if not DOCUSHARE_URLS_PATH.exists():
        raise SystemExit(
            f'{DOCUSHARE_URLS_PATH} not found -- run scrape_docushare.py first.'
        )

    docushare_urls = load_docushare_urls(DOCUSHARE_URLS_PATH)
    print(f'Loaded {len(docushare_urls)} DocuShare URL(s).')

    with open(MANIFEST_PATH, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    matched = 0
    for row in rows:
        row.setdefault('docushare_url', '')
        url = docushare_urls.get(row['filename'])
        if url:
            row['docushare_url'] = url
            matched += 1

    with open(MANIFEST_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f'Matched {matched} of {len(docushare_urls)} DocuShare URL(s) to manifest rows.')
    unmatched = set(docushare_urls) - {r['filename'] for r in rows}
    if unmatched:
        print(f'  WARNING: {len(unmatched)} DocuShare filename(s) not found in manifest:')
        for fn in sorted(unmatched):
            print(f'    {fn!r}')


if __name__ == '__main__':
    main()
