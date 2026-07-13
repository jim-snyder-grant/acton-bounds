"""
scrape_docushare.py

Fetches the DocuShare "Perambulation Images" collection page and extracts
each photo's Document-NNNNN ID, writing filename/document_id/docushare_url
triples to docushare_urls.csv.

The collection URL is publicly viewable without login (confirmed Jun 30 2026),
so no auth/cookies are needed -- normally. DocuShare's anonymous/guest access
seems to allow only one guest session at a time, and this can lock out
*everyone* (not just this script) for an extended period -- observed
repeatedly in the days leading up to Select Board meetings (heavier DocuShare
traffic). If https://doc.actonma.gov/dsweb/View/Collection-20474 shows a
"DocuShare License Error" even in an incognito browser window, it's this
lockout, not a bug here. Workaround: log into DocuShare directly (bypasses
the guest-session limit), open the collection page, "Save Page As" (HTML
only is fine) to a local file, then pass that file's path as the argument
below instead of a URL.

Pagination is NOT handled yet -- this only reads a single page (default page
size: 100 results). Not actually a problem in practice: as of Jul 2 2026 a
174-document collection still rendered on one page with nothing clipped.
Revisit if a future collection is large enough to trigger real pagination.

Run from the code/ directory:
    python3 scrape_docushare.py
    python3 scrape_docushare.py https://doc.actonma.gov/dsweb/View/Collection-20474
    python3 scrape_docushare.py /path/to/saved_collection_page.html
"""

import csv
import html as html_module
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import unquote

DEFAULT_COLLECTION_URL = 'https://doc.actonma.gov/dsweb/View/Collection-20474'
OUTPUT_PATH = Path(__file__).resolve().parent / 'docushare_urls.csv'   # code-local

# Each document's table row starts at <tr about="..."> and runs to the next
# </tr> (rows aren't nested in this markup, confirmed against a real fetch).
ROW_BLOCK_RE = re.compile(
    r'<tr about="(/dsweb/Get/Document-\d+/[^"]+)".*?</tr>', re.DOTALL)
DOC_ID_RE = re.compile(r'Document-(\d+)')
# The human-readable filename, e.g. <strong property="dc:title">foo.jpg</strong>.
# DocuShare mangles the URL-encoded path text (':' truncates it, quotes/
# apostrophes get replaced with junk -- see code/claude.md), but dc:title
# keeps the real, complete original filename. Prefer it when present.
TITLE_RE = re.compile(r'<strong property="dc:title">(.*?)</strong>', re.DOTALL)


USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8', errors='replace')


def parse_rows(html: str):
    """Yield (filename, document_id, docushare_url) for each document row.

    docushare_url is built from the (possibly mangled-looking) URL-encoded
    path -- DocuShare resolves Get/ links purely by Document ID and ignores
    the trailing filename text, so this is a working link regardless
    (verified Jul 2 2026 including with a nonsense filename). filename is
    taken from dc:title when available, since that's the real, complete
    original name; falls back to the URL-encoded path otherwise.
    """
    for block_match in ROW_BLOCK_RE.finditer(html):
        path = block_match.group(1)
        block = block_match.group(0)
        doc_id = DOC_ID_RE.search(path).group(1)
        url = f'https://doc.actonma.gov{path}'

        title_match = TITLE_RE.search(block)
        if title_match:
            filename = html_module.unescape(title_match.group(1)).strip()
        else:
            filename = unquote(path.split('/', 4)[-1])

        yield filename, doc_id, url


def check_for_known_failure_pages(html: str):
    """Raise with a clear message if the fetch hit a login wall or license error.

    DocuShare's anonymous/guest access appears to allow only one concurrent
    session. Fetching again too soon after a prior fetch can return a
    "DocuShare License Error" page, or a logged-out landing page, instead of
    the actual collection listing -- neither contains any <tr about="..."">
    rows, so without this check the script would silently write an empty
    docushare_urls.csv. If this happens, wait a few minutes (for the prior
    guest session to time out) and try again.
    """
    title_match = re.search(r'<title>(.*?)</title>', html)
    title = title_match.group(1) if title_match else ''
    if 'License Error' in title:
        raise SystemExit(
            'DocuShare returned a "License Error" page -- the guest session '
            'limit was likely hit by a recent request. Wait a few minutes '
            'and try again.'
        )
    if 'Click to login' in html and '<tr about=' not in html:
        raise SystemExit(
            'DocuShare returned a logged-out landing page instead of the '
            'collection listing. Wait a few minutes and try again.'
        )


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_COLLECTION_URL

    local_path = Path(source)
    if local_path.exists():
        print(f'Reading local file {local_path} ...')
        html = local_path.read_text(encoding='utf-8', errors='replace')
    else:
        print(f'Fetching {source} ...')
        html = fetch(source)
    check_for_known_failure_pages(html)

    entries = list(parse_rows(html))
    print(f'  {len(entries)} document(s) found.')
    if not entries:
        raise SystemExit(
            'No document rows found -- the page may not be the expected '
            'collection listing. Not overwriting docushare_urls.csv.'
        )
    if len(entries) >= 100:
        print('  WARNING: 100+ results on this page -- pagination is not yet '
              'handled, so some photos may be missing. See the DocuShare '
              'photo linking note.')

    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'document_id', 'docushare_url'])
        writer.writerows(entries)

    print(f'Written to {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
