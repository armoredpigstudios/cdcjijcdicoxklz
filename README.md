# Armored Pig Studios website

A static site with a console-menu look. There is no server code: any static host can serve `site/`.
The workflow in `.github/workflows/site.yml` publishes it to GitHub Pages and keeps the review counts fresh.

```
site/                 the website: upload this folder's contents
  index.html          home: text logo, studio stats, featured games, latest releases, library
  games.html          all games, sortable by date, name or reviews
  games/<slug>.html   one page per game
  studio.html, contact.html, 404.html
  data/reviews.json   review counts from the store, written by src/reviews.py
  assets/css/site.css, assets/js/site.js     edited by hand
  assets/fonts/       DejaVu Sans Mono (licence included)
  assets/img/<slug>/  cover.webp, cover-sm.webp, banner.webp, shot-N.webp, shot-N-sm.webp, og.jpg
src/
  games.json          every game's text, credits and store details
  build.py            writes the HTML pages from games.json (standard library only)
  reviews.py          reads each game's review count from its store page into site/data/reviews.json
  logo.txt            the cell grid the text logo is drawn from
.github/workflows/site.yml   builds and publishes the site to GitHub Pages, hourly and on every push
```

## Preview

```
python -m http.server 8000 --directory site
```

then open http://localhost:8000.

## Change things

- **Game text, credits, featured games:** edit `src/games.json`, then run `python src/build.py`.
  `"featured": true` puts a game on the home page shelf (four fit in a row). `news` is the release log,
  newest first.
- **Studio facts (1M+ players, 5 years, based in America):** `PLAYERS`, `PLAYERS_WORDS`, `YEARS` and `BASED_IN`
  at the top of `src/build.py`. Bump `YEARS` each year. The studio's About text is in `build_studio()`
  and the contact page's Business part in `build_contact()`.
- **Email, domain, privacy link:** the settings at the top of `src/build.py`, then rebuild.
- **Colours and layout:** `site/assets/css/site.css` (the colours are the variables at the top).
- **A new game:** add it to `games.json` and put its images in `site/assets/img/<slug>/`: `cover.webp`
  (1600 x 900) and `cover-sm.webp` (640 x 360) from the store's landscape cover, `banner.webp` (2048 x 614)
  from the store's hero image, `shot-1.webp`... (1600 x 900) with `shot-1-sm.webp`... (640 x 360), and
  `og.jpg` (1200 x 675) for link previews. Then run `python src/reviews.py` and `python src/build.py`.

Don't edit the HTML files directly: `build.py` rewrites them.

## Put it online

The domain stays at GoDaddy and GitHub Pages hosts the site, free and with HTTPS. The workflow publishes it on
every push and every hour with fresh review counts. `USERNAME` below is the GitHub account (or organization) that
owns the repository.

1. Make a **public** repository on GitHub (Pages is free only for public ones) and push this folder to its `main`
   branch: `git init -b main`, `git add .`, `git commit -m "Website"`, then the `git remote add` and `git push`
   lines GitHub shows on the new repository's page.
2. Recommended: verify the domain first, in your GitHub account's Settings > Pages > Add a domain. It gives you
   a TXT record to add at GoDaddy, and then nobody else can use the domain on GitHub Pages.
3. In the repository, Settings > Pages > Source: **GitHub Actions**. Then Actions > Publish site > **Run workflow**.
   The site appears at `https://USERNAME.github.io/REPOSITORY/`.
4. Settings > Pages > Custom domain: `armoredpigstudios.com`, then Save.
5. At GoDaddy, Domain Portfolio > the domain > DNS. Set these records:

   | Type  | Name | Value              |
   |-------|------|--------------------|
   | A     | @    | 185.199.108.153    |
   | A     | @    | 185.199.109.153    |
   | A     | @    | 185.199.110.153    |
   | A     | @    | 185.199.111.153    |
   | CNAME | www  | USERNAME.github.io |

   Replace the A record GoDaddy already has for `@` (its parked page) and edit the existing `www` record rather
   than adding a second. Turn off domain forwarding if it's on, and delete any `*` (wildcard) record. Leave the
   nameservers and the MX and TXT records alone: your email depends on them. IPv6 is optional: four `AAAA`
   records for `@`: `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`.
6. When Settings > Pages says the DNS check passed (DNS changes can take up to 24 hours), tick **Enforce HTTPS**
   (it can also take up to 24 hours to be offered). `www.armoredpigstudios.com` then redirects to
   `armoredpigstudios.com`.

To check the records from Windows: `Resolve-DnsName armoredpigstudios.com` and
`Resolve-DnsName www.armoredpigstudios.com`. After the first run, open it on the Actions tab: the "Read review
counts from the store" step should list six counts. If the store turns GitHub's servers away, the site still
publishes, with the counts saved in the repository.

**GoDaddy's own hosting instead:** buy a Web Hosting (cPanel) plan, zip the contents of `site/`, upload the zip
to `public_html` in File Manager and extract it there. The review counts then stay as uploaded (see "On another
host" below).

## Review counts

Each game shows its review count from its store page: every player rating, the number the store shows as
"3K ratings" (and as (3K) on its cards). The store's smaller "864 reviews" counts only ratings with written text,
and isn't used. The home, studio and contact pages add the counts up.

- `python src/reviews.py` reads the six store pages (one request each, a second apart) and writes
  `site/data/reviews.json`. A page it can't read keeps its last count, and the script exits with status 1.
- `python src/build.py` puts the counts into the HTML, so they show without JavaScript.
- In the browser, `site.js` loads `data/reviews.json` when a page opens, again every 10 minutes while it's open,
  and when the tab comes back into view. A newer file on the server shows without rebuilding the pages.

**On GitHub Pages** (see "Put it online"), the workflow runs on every push and every hour: it reads the counts,
builds the pages and publishes them. GitHub turns off hourly workflows in a public repository after 60 days
without a commit (it emails first); re-enable it on the Actions tab, or push any change.

**On another host:** run `python src/reviews.py` and `python src/build.py` on a schedule (cron, a scheduled
task) and upload `site/`, or at least `site/data/reviews.json`.

The counts come from the public store pages, as Meta's robots.txt allows for these pages. That file also
carries Meta's notice that automated data collection needs their written permission; the script reads only
the six listings on this site, six requests an hour. To check less often, change the `cron` line in the workflow.

## Where the content came from

Game descriptions, credits, ratings, release dates, covers, banners and screenshots are from each game's
Meta Horizon Store listing (November 2026). Small changes: emoji removed from Murder Monkey's text and
spelling fixed in Web Weaver's.
