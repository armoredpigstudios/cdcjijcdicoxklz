#!/usr/bin/env python3
"""Reads each game's review count from its store page into site/data/reviews.json.

    python src/reviews.py

The count is every player rating, the number the store page shows as "3K ratings" and on its cards as (3K).
The store calls only the ratings that come with written text "reviews"; those aren't used here.

build.py puts these counts into the pages, and the pages read site/data/reviews.json again when they open
(and every few minutes after that), so a newer copy on the server shows up without a rebuild. The workflow in
.github/workflows/site.yml runs this every hour before it builds and publishes the site.

A game whose page can't be read keeps its last count, and the script exits with status 1 so the failure shows.
Standard library only.
"""
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = json.loads((ROOT / "src" / "games.json").read_text(encoding="utf-8"))["games"]
OUT = ROOT / "site" / "data" / "reviews.json"
HEADERS = {
    "User-Agent": "review-counts/1.0 (python urllib)",
    "Accept": "text/html",               # without it the store sends a lighter page without its own record
    "Accept-Language": "en-US,en;q=0.9",
}
LD_JSON = re.compile(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', re.S)


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=40) as res:
        return res.read().decode("utf-8", "replace")


def schema_count(page, app_id):
    """ratingCount from the page's schema.org data, from the entry whose links carry this app's id."""
    for block in LD_JSON.findall(page):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
        for node in nodes if isinstance(nodes, list) else []:
            if isinstance(node, dict) and "aggregateRating" in node and app_id in json.dumps(node):
                try:
                    return int(node["aggregateRating"]["ratingCount"])
                except (KeyError, TypeError, ValueError):
                    return None
    return None


def record_count(page, app_id):
    """quality_rating_count from the app's own record on the page (its id, then a little further on its
    numbers), with the store's short form of it ("3K"). (None, None) if the record isn't there."""
    for m in re.finditer(r'"id":"%s"' % re.escape(app_id), page):
        rec = page[m.end():m.end() + 3000]
        nxt = rec.find('"id":"')
        if nxt >= 0:
            rec = rec[:nxt]                      # stop where the next record starts
        count = re.search(r'"quality_rating_count":(\d+)', rec)
        if count:
            shown = re.search(r'"quality_rating_i18n_count_string":"([^"]*)"', rec)
            return int(count.group(1)), shown.group(1) if shown else None
    return None, None


def read_count(page, app_id):
    """(count, the store's short form of it or None), or None if the page has no count or contradicts itself."""
    schema = schema_count(page, app_id)
    record, shown = record_count(page, app_id)
    if schema is not None and record is not None and schema != record:
        return None
    count = schema if schema is not None else record
    return None if count is None else (count, shown)


def main():
    last = json.loads(OUT.read_text(encoding="utf-8"))["games"] if OUT.exists() else {}
    games, failed = {}, 0
    for i, g in enumerate(GAMES):
        if i:
            time.sleep(1)                        # one page at a time
        slug, url = g["slug"], g["storeUrl"]
        try:
            found = read_count(fetch(url), url.rstrip("/").rsplit("/", 1)[-1])
            why = "no count on the page"
        except Exception as err:                 # no connection, an HTTP error, a timeout
            found, why = None, str(err)
        if found:
            count, shown = found
            games[slug] = {"reviews": count}
            print(f"{slug:16} {count:>7,} reviews" + (f"   (the store page says {shown})" if shown else ""))
            continue
        failed += 1
        if slug in last:
            games[slug] = {"reviews": last[slug]["reviews"]}
        print(f"{slug:16} kept the last count ({why})", file=sys.stderr)

    data = {"checked": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "games": games}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT.relative_to(ROOT).as_posix())
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
