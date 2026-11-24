#!/usr/bin/env python3
"""Builds the Armored Pig Studios website into site/ from src/games.json and src/logo.txt.

    python src/build.py

It writes every HTML page (plus sitemap.xml and robots.txt). The CSS, JavaScript, fonts and images in
site/assets are edited by hand and left alone. Standard library only.
"""
import hashlib
import html
import json
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------------------------- settings
SITE_URL = "https://armoredpigstudios.com"        # where the site is hosted: share images and the sitemap use it
EMAIL = "kinoa@armoredpigstudios.com"             # the public contact address
PRIVACY_URL = "https://sites.google.com/view/babydeathrampage/home"   # the privacy policy the store pages link to
STUDIO = "Armored Pig Studios"
PLAYERS = "1M+"                                   # players across all games: the home and studio stat
PLAYERS_WORDS = "over a million"                  # the same, in a sentence
YEARS = 5                                         # years in the industry: bump it each year
BASED_IN = "America"
HEADSETS = "Quest 3S, 3, Pro, 2"                  # the headsets line on each game page
LOGO_LETTERS = "ARMOREDPIGSTUDIOS"                # the small letters the big logo is made of

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "src", ROOT / "site"
DATA = json.loads((SRC / "games.json").read_text(encoding="utf-8"))
GAMES = DATA["games"]
BY_SLUG = {g["slug"]: g for g in GAMES}
NEWS = DATA["news"]
FEATURED = [g for g in GAMES if g.get("featured")]
NEWEST = sorted(GAMES, key=lambda g: g["released"], reverse=True)
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
NUMBER_WORDS = "zero one two three four five six seven eight nine ten eleven twelve".split()

# Review counts from the store, written by src/reviews.py. The pages are built with these, and site.js reads
# the same file again in the browser so a newer copy on the server shows without a rebuild.
REVIEWS_FILE = OUT / "data" / "reviews.json"
REVIEWS = json.loads(REVIEWS_FILE.read_text(encoding="utf-8"))["games"] if REVIEWS_FILE.exists() else {}

# Added to the stylesheet and script links (site.css?v=...) so browsers fetch them again after they change.
ASSET_VERSION = hashlib.sha1(b"".join((OUT / "assets" / p).read_bytes()
                                      for p in ("css/site.css", "js/site.js"))).hexdigest()[:8]

e = html.escape


def long_date(iso):
    y, m, d = (iso.split("-") + ["", ""])[:3]
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}" if d else f"{MONTHS[int(m) - 1]} {y}"


def credit(g):
    """'2080 Games, Armored Pig Studios' -> '2080 Games × Armored Pig Studios'."""
    return g["developer"].replace(", ", " × ")


def review_count(slug):
    """A game's written-review count from the store, or None if src/reviews.py hasn't read it yet."""
    n = REVIEWS.get(slug, {}).get("reviews")
    return n if isinstance(n, int) else None


def reviews_html(slug):
    """The count as a number site.js keeps current, e.g. <span data-reviews="web-weaver">128</span>."""
    return f'<span data-reviews="{slug}">{review_count(slug):,}</span>'


TOTAL_REVIEWS = sum(review_count(g["slug"]) or 0 for g in GAMES)


def img(r, slug, name):
    return f"{r}assets/img/{slug}/{name}"


def glyph(letter):
    return f'<span class="glyph" aria-hidden="true">{letter}</span>'


def tags(items):
    return '<ul class="tags">' + "".join(f"<li>{e(t)}</li>" for t in items) + "</ul>"


def hints(path, *keys):
    """The console-style bar along the bottom (desktop only): a path and the keys that do something here."""
    k = "".join(
        '<span class="hint">' + "".join(f"<kbd>{e(c)}</kbd>" for c in caps) + f" {e(label)}</span>"
        for caps, label in keys)
    return f'<span class="hints__path">{e(path)}</span><span class="hints__keys">{k}</span>'


NAV = [("home", "Home", "index.html"), ("games", "Games", "games.html"),
       ("studio", "Studio", "studio.html"), ("contact", "Contact", "contact.html")]


def page(*, out, title, description, body, active=None, r="", canonical=None, og_image="assets/img/og.jpg",
         hint="", body_attrs=""):
    tabs = "\n        ".join(
        f'<a class="tab" href="{r}{href}"' + (' aria-current="page"' if key == active else "") + f">{label}</a>"
        for key, label, href in NAV)
    canon = f'\n<link rel="canonical" href="{SITE_URL}/{canonical}">' if canonical is not None else ""
    og_url = f'\n<meta property="og:url" content="{SITE_URL}/{canonical}">' if canonical is not None else ""
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="theme-color" content="#121214">{canon}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{STUDIO}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:image" content="{SITE_URL}/{og_image}">{og_url}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{r}favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{r}apple-touch-icon.png">
<link rel="preload" href="{r}assets/fonts/dejavu-sans-mono-400.woff" as="font" type="font/woff" crossorigin>
<link rel="preload" href="{r}assets/fonts/dejavu-sans-mono-700.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="{r}assets/css/site.css?v={ASSET_VERSION}">
<script src="{r}assets/js/site.js?v={ASSET_VERSION}" defer></script>
</head>
<body{body_attrs}>
<a class="skip" href="#main">Skip to content</a>
<header class="bar">
  <div class="wrap bar__inner">
    <a class="brand" href="{r}index.html"><span class="brand__name">ARMORED PIG</span><span class="brand__sub">STUDIOS</span></a>
    <nav class="tabs" aria-label="Main">
        {tabs}
    </nav>
    <time class="clock" data-clock aria-hidden="true">--:--</time>
  </div>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="foot">
  <div class="wrap foot__inner">
    <p>&copy; {date.today().year} {STUDIO}</p>
    <ul>
      <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
      <li><a href="{PRIVACY_URL}" rel="noopener">Privacy policy</a></li>
    </ul>
  </div>
</footer>
<div class="hints" aria-hidden="true"><div class="wrap hints__inner">{hint}</div></div>
</body>
</html>
"""
    path = OUT / out
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc, encoding="utf-8", newline="\n")
    print("wrote", path.relative_to(ROOT))


# ---------------------------------------------------------------------------------------------- pieces
def logo_html():
    """The studio name drawn in small letters, like the splash screen in the games."""
    rows = (SRC / "logo.txt").read_text(encoding="utf-8").rstrip("\n").split("\n")
    lines = []
    for y, row in enumerate(rows):
        k = y * 5
        out, kind = [], " "              # kind of the open run: " " none, "#" solid cell, "+" edge cell
        for cell in row:
            if cell != kind:
                if kind != " ":
                    out.append("</span>")
                if cell != " ":
                    out.append('<span class="b">' if cell == "#" else '<span class="d">')
                kind = cell
            if cell == " ":
                out.append(" ")
            else:
                out.append(LOGO_LETTERS[k % len(LOGO_LETTERS)])
                k += 1
        if kind != " ":
            out.append("</span>")
        lines.append("".join(out))
    return "\n".join(lines)


def tile(g, r, i=None, selected=False):
    attrs = f' data-index="{i}"' if i is not None else ""
    if selected:
        attrs += ' aria-current="true"'
    cls = "tile is-selected" if selected else "tile"
    return (f'<li><a class="{cls}" href="{r}games/{g["slug"]}.html"{attrs}>'
            f'<img src="{img(r, g["slug"], "cover-sm.webp")}" width="640" height="360" alt="" loading="lazy">'
            f'<span class="tile__name">{e(g["name"])}</span></a></li>')


def kicker(g):
    k = e(credit(g))
    return k + (' <span class="badge">Early Access</span>' if g.get("earlyAccess") else "")


def mini_count(g):
    """'864 reviews' at the right of a game in the home page's library list."""
    if review_count(g["slug"]) is None:
        return ""
    return f'<span class="mini__count">{reviews_html(g["slug"])} reviews</span>'


def store_button(g, letter="Y", label="Store page", primary=False, attrs=""):
    cls = "btn btn--primary" if primary else "btn"
    return (f'<a class="{cls}" href="{e(g["storeUrl"])}" target="_blank" rel="noopener"{attrs}>'
            f'{glyph(letter)}{label}<span class="sr-only"> (opens in a new tab)</span></a>')


def news_list(items, r):
    out = []
    for n in items:
        g = BY_SLUG[n["slug"]]
        out.append(f'<li><time datetime="{n["date"]}">{n["date"]}</time>'
                   f'<a href="{r}games/{g["slug"]}.html">{e(g["name"])}</a><span>{e(n["text"])}</span></li>')
    return '<ol class="log">' + "".join(out) + "</ol>"


def about_html(g):
    out = []
    for b in g["about"]:
        if "lead" in b:
            out.append(f'<p class="lead">{e(b["lead"])}</p>')
        elif "quote" in b:
            out.append(f'<blockquote><p>&ldquo;{e(b["quote"])}&rdquo;</p><footer>{e(b["by"])}</footer></blockquote>')
        else:
            if "h" in b:
                out.append(f'<h3>{e(b["h"])}</h3>')
            if "p" in b:
                out.append(f'<p>{e(b["p"])}</p>')
            if "list" in b:
                out.append("<ul>" + "".join(f"<li>{e(i)}</li>" for i in b["list"]) + "</ul>")
    return "\n      ".join(out)


# ---------------------------------------------------------------------------------------------- pages
def build_home():
    r = ""
    first = FEATURED[0]
    feat_json = json.dumps([{
        "slug": g["slug"], "name": g["name"], "sub": g.get("subtitle", ""), "kicker": kicker(g),
        "tags": tags(g["genres"]), "text": g["tagline"], "reviews": review_count(g["slug"]),
        "href": f"games/{g['slug']}.html", "store": g["storeUrl"],
        "cover": img(r, g["slug"], "cover.webp"), "alt": f"{g['name']} cover art",
    } for g in FEATURED], ensure_ascii=False).replace("</", "<\\/")
    shelf = "\n      ".join(tile(g, r, i, i == 0) for i, g in enumerate(FEATURED))
    sub = e(first.get("subtitle", ""))
    first_reviews = review_count(first["slug"])
    library = "".join(
        f'<li><a href="games/{g["slug"]}.html"><span class="mini__name">{e(g["name"])}</span>{mini_count(g)}'
        f'<span class="mini__dev">{e(credit(g))}</span></a></li>' for g in NEWEST)
    body = f"""
<section class="boot" aria-labelledby="boot-title">
  <h1 id="boot-title" class="sr-only">{STUDIO}</h1>
  <pre class="logo" aria-hidden="true">{logo_html()}</pre>
  <div class="boot__row">
    <p class="boot__lead">We make multiplayer VR games.</p>
    <div class="actions">
      <a class="btn btn--primary" href="games.html">{glyph("A")}Browse games</a>
      <a class="btn" href="studio.html">{glyph("Y")}The studio</a>
    </div>
  </div>
  <ul class="facts facts--stats" aria-label="The studio in numbers">
    <li><span class="facts__v">{PLAYERS}</span><span class="facts__k">Players across all games</span></li>
    <li><span class="facts__v">{YEARS}</span><span class="facts__k">Years in the industry</span></li>
    <li><span class="facts__v" data-reviews-total>{TOTAL_REVIEWS:,}</span><span class="facts__k">Player reviews</span></li>
  </ul>
</section>

<section class="panel featured" aria-labelledby="featured-title" data-featured>
  <header class="panel__head">
    <h2 id="featured-title" class="panel__title">Featured</h2>
    <span class="panel__meta"><span data-feat-count>01</span> / {len(FEATURED):02d}</span>
  </header>
  <div class="featured__body">
    <a class="featured__art" href="games/{first["slug"]}.html" tabindex="-1" aria-hidden="true" data-feat-link>
      <img src="{img(r, first["slug"], "cover.webp")}" width="1600" height="900" alt="{e(first["name"])} cover art" data-feat-img>
    </a>
    <div class="featured__info" aria-live="polite">
      <p class="featured__kicker" data-feat-kicker>{kicker(first)}</p>
      <h3 class="featured__name" data-feat-name>{e(first["name"])}</h3>
      <p class="featured__sub" data-feat-sub{"" if sub else " hidden"}>{sub}</p>
      <div data-feat-tags>{tags(first["genres"])}</div>
      <p class="featured__text" data-feat-text>{e(first["tagline"])}</p>
      <p class="featured__reviews"{"" if first_reviews is not None else " hidden"}>Reviews <b data-reviews="{first["slug"]}" data-feat-reviews>{first_reviews or 0:,}</b></p>
      <div class="actions featured__actions">
        <a class="btn btn--primary" href="games/{first["slug"]}.html" data-feat-link>{glyph("A")}View game</a>
        {store_button(first, attrs=" data-feat-store")}
      </div>
    </div>
  </div>
  <ul class="shelf" data-shelf aria-label="Featured games">
      {shelf}
  </ul>
</section>
<script type="application/json" id="featured-data">{feat_json}</script>

<div class="split">
  <section class="panel" aria-labelledby="latest-title">
    <header class="panel__head">
      <h2 id="latest-title" class="panel__title">Latest</h2>
      <a class="panel__link" href="studio.html#log">Release log</a>
    </header>
    {news_list(NEWS[:5], r)}
  </section>
  <section class="panel" aria-labelledby="library-title">
    <header class="panel__head">
      <h2 id="library-title" class="panel__title">Library</h2>
      <a class="panel__link" href="games.html">All {len(GAMES)} games</a>
    </header>
    <ul class="mini mini--count">{library}</ul>
  </section>
</div>
"""
    page(out="index.html", title=f"{STUDIO} – multiplayer VR games",
         description=f"{STUDIO} makes multiplayer VR games, played by {PLAYERS_WORDS} people: "
                     + ", ".join(g["name"] for g in NEWEST) + ".",
         body=body, active="home", r=r, canonical="",
         hint=hints("AP:\\HOME", (["←", "→"], "Select"), (["Enter"], "Open")))


def build_games():
    r = ""
    rows = []
    for g in NEWEST:
        s = g["slug"]
        n = review_count(s)
        reviews = f'\n      <div><dt>Reviews</dt><dd>{reviews_html(s)}</dd></div>' if n is not None else ""
        rows.append(f"""
  <li class="row" data-slug="{s}" data-date="{g["released"]}" data-name="{e(g["name"].lower())}" data-count="{n or 0}">
    <a class="row__art" href="games/{s}.html" tabindex="-1" aria-hidden="true"><img src="{img(r, s, "cover-sm.webp")}" width="640" height="360" alt="" loading="lazy"></a>
    <div class="row__body">
      <h2 class="row__name"><a href="games/{s}.html">{e(g["name"])}</a></h2>
      <p class="row__dev">{kicker(g)}</p>
      <p class="row__text">{e(g["tagline"])}</p>
      {tags(g["genres"])}
    </div>
    <dl class="row__meta">{reviews}
      <div><dt>Released</dt><dd>{long_date(g["released"])}</dd></div>
      <div><dt>Players</dt><dd>{e(g["players"])}</dd></div>
      <div><dt>Age rating</dt><dd>{e(g["rating"])}</dd></div>
    </dl>
  </li>""")
    body = f"""
<header class="page-head">
  <h1 class="page-title">Games</h1>
  <p class="page-lead">{NUMBER_WORDS[len(GAMES)].capitalize()} games, {PLAYERS_WORDS} players between them.</p>
</header>
<div class="toolbar">
  <span>Sort</span>
  <div class="seg" role="group" aria-label="Sort games">
    <button type="button" data-sort="date" aria-pressed="true">Newest</button>
    <button type="button" data-sort="name" aria-pressed="false">A&ndash;Z</button>
    <button type="button" data-sort="reviews" aria-pressed="false">Reviews</button>
  </div>
  <span class="toolbar__count">{len(GAMES)} titles</span>
</div>
<ol class="library" data-library>{"".join(rows)}
</ol>
"""
    page(out="games.html", title=f"Games | {STUDIO}",
         description=f"Every {STUDIO} game: " + ", ".join(g["name"] for g in NEWEST) + ".",
         body=body, active="games", r=r, canonical="games.html",
         hint=hints("AP:\\GAMES", (["↑", "↓"], "Select"), (["Enter"], "Open")))


def build_game(g):
    r = "../"
    s = g["slug"]
    title = g["name"] + (f": {g['subtitle']}" if g.get("subtitle") else "")
    facts = "".join(f'<li><span class="facts__v">{e(v)}</span><span class="facts__k">{e(k)}</span></li>'
                    for k, v in g.get("facts", []))
    if review_count(s) is not None:
        facts = f'<li><span class="facts__v">{reviews_html(s)}</span><span class="facts__k">Reviews</span></li>' + facts
    shots = "".join(
        f'<li><a href="{img(r, s, f"shot-{n}.webp")}" data-shot>'
        f'<img src="{img(r, s, f"shot-{n}-sm.webp")}" width="640" height="360" alt="{e(g["name"])} screenshot {n}" loading="lazy"></a></li>'
        for n in range(1, g["shots"] + 1))
    spec = [("Developer", e(g["developer"])), ("Publisher", e(g["publisher"])),
            ("Released", long_date(g["released"]))]
    if g.get("earlyAccess"):
        spec.append(("Status", "Early Access"))
    spec += [("Genres", e(", ".join(g["genres"]))), ("Modes", e(", ".join(g["gameModes"]))),
             ("Players", e(g["players"])), ("Play", e(", ".join(g["playerModes"]))),
             ("Headsets", HEADSETS),
             ("Age rating", f'{e(g["rating"])}<small>{e(g["ratingNotes"])}</small>'),
             ("Comfort", e(g["comfort"])), ("Internet", e(g["internet"]))]
    spec_html = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in spec)
    links = "".join(f'<a class="btn" href="{e(u)}" target="_blank" rel="noopener">{glyph("X")}{e(label)}</a>'
                    for label, u in g.get("links", []))
    others = [o for o in NEWEST if o["slug"] != s]
    more = "\n      ".join(tile(o, r) for o in others)
    sub = f'\n      <p class="game-sub">{e(g["subtitle"])}</p>' if g.get("subtitle") else ""
    body = f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{r}games.html">Games</a><span aria-hidden="true">/</span><span aria-current="page">{e(g["name"])}</span></nav>
<figure class="banner"><img src="{img(r, s, "banner.webp")}" width="2048" height="614" alt="{e(title)} key art"></figure>
<header class="game-head">
  <div>
    <h1 class="game-title">{e(g["name"])}</h1>{sub}
    <p class="game-credit">{kicker(g)}</p>
  </div>
  <div class="actions">
    {store_button(g, "A", "Get the game", primary=True)}
    {links}
  </div>
</header>
<ul class="facts">{facts}</ul>
<div class="game-grid">
  <div class="game-main">
    <section class="prose" aria-labelledby="about-title">
      <h2 id="about-title" class="section-title">About</h2>
      {about_html(g)}
    </section>
    <section aria-labelledby="shots-title">
      <h2 id="shots-title" class="section-title">Screenshots</h2>
      <ul class="shots">{shots}</ul>
    </section>
  </div>
  <aside class="game-side">
    <section class="panel" aria-labelledby="info-title">
      <header class="panel__head"><h2 id="info-title" class="panel__title">Info</h2></header>
      <dl class="spec">{spec_html}</dl>
      <div class="panel__foot">{store_button(g, "A", "Store page", primary=True, attrs=' data-block')}</div>
    </section>
  </aside>
</div>
<section class="more" aria-labelledby="more-title">
  <header class="panel__head panel__head--bare">
    <h2 id="more-title" class="panel__title">More games</h2>
    <a class="panel__link" href="{r}games.html">Library</a>
  </header>
  <ul class="shelf shelf--more">
      {more}
  </ul>
</section>
<dialog class="viewer" data-viewer aria-label="{e(g["name"])} screenshots">
  <div class="viewer__bar">
    <span data-viewer-count>1 / {g["shots"]}</span>
    <button type="button" class="btn btn--small" data-viewer-close>{glyph("B")}Close</button>
  </div>
  <img data-viewer-img src="" alt="" width="1600" height="900">
  <div class="viewer__nav">
    <button type="button" class="btn btn--small" data-viewer-prev><span aria-hidden="true">&#9664;</span> Prev</button>
    <button type="button" class="btn btn--small" data-viewer-next>Next <span aria-hidden="true">&#9654;</span></button>
  </div>
</dialog>
"""
    page(out=f"games/{s}.html", title=f"{title} | {STUDIO}", description=g["tagline"], body=body,
         active="games", r=r, canonical=f"games/{s}.html", og_image=f"assets/img/{s}/og.jpg",
         hint=hints(f"AP:\\GAMES\\{s.upper().replace('-', '_')}", (["Esc"], "Back to games")),
         body_attrs=' data-back="../games.html"')


def build_studio():
    r = ""
    log = news_list(NEWS, r)            # games.json keeps the news newest first
    body = f"""
<header class="page-head">
  <h1 class="page-title">Studio</h1>
  <p class="page-lead">{NUMBER_WORDS[YEARS].capitalize()} years in the industry, and {PLAYERS_WORDS} players across our games.</p>
</header>
<div class="split split--studio">
  <section class="prose" aria-labelledby="about-studio">
    <h2 id="about-studio" class="section-title">About</h2>
    <p class="lead">{STUDIO} is a VR game studio based in {BASED_IN}.</p>
    <p>We love social multiplayer games, the kind where the best moments come from whoever else is in the room, so everything we make can be played together. Half the fun of Murder Mystery is working out who's holding the knife. Buddy Beatdown is at its best with a lobby full of friends and far too many explosives.</p>
    <p>Most of our games have public rooms to drop into, private rooms you join with a code, and voice chat.</p>
    <p>Our own games:</p>
    <ul>
      <li><a href="games/prison-break.html">Prison Break</a>, where inmates plan a breakout and cops try to stop them</li>
      <li><a href="games/murder-monkey.html">Murder Monkey</a>, a murder mystery where you move like a gorilla</li>
      <li><a href="games/devastation.html">DEVASTATION</a>, a destruction sandbox in Early Access where buildings come down in chunks</li>
      <li><a href="games/murder-mystery.html">Murder Mystery</a>, a social deduction game for up to 12 players</li>
      <li><a href="games/web-weaver.html">Web Weaver</a>, a physics-based web-swinging game</li>
    </ul>
    <p><a href="games/buddy-beatdown.html">Buddy Beatdown</a> is made with 2080 Games and gets a big free update every month.</p>
    <p class="actions"><a class="btn btn--primary" href="games.html">{glyph("A")}Browse games</a><a class="btn" href="contact.html">{glyph("Y")}Contact</a></p>
  </section>
  <aside>
    <section class="panel" aria-labelledby="sys-title">
      <header class="panel__head"><h2 id="sys-title" class="panel__title">Studio info</h2></header>
      <dl class="spec">
        <div><dt>Name</dt><dd>{STUDIO}</dd></div>
        <div><dt>Makes</dt><dd>Social multiplayer VR games</dd></div>
        <div><dt>Experience</dt><dd>{YEARS} years in the industry</dd></div>
        <div><dt>Players</dt><dd>{PLAYERS} across all games</dd></div>
        <div><dt>Reviews</dt><dd><span data-reviews-total>{TOTAL_REVIEWS:,}</span> across all games</dd></div>
        <div><dt>Games</dt><dd><a href="games.html">{len(GAMES)} out now</a></dd></div>
        <div><dt>Contact</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
      </dl>
    </section>
  </aside>
</div>
<section class="panel log-panel" id="log" aria-labelledby="log-title">
  <header class="panel__head">
    <h2 id="log-title" class="panel__title">Release log</h2>
    <span class="panel__meta">Newest first</span>
  </header>
  {log}
</section>
"""
    page(out="studio.html", title=f"Studio | {STUDIO}",
         description=f"{STUDIO} makes social multiplayer VR games: {NUMBER_WORDS[YEARS]} years in the industry "
                     f"and {PLAYERS_WORDS} players.",
         body=body, active="studio", r=r, canonical="studio.html", hint=hints("AP:\\STUDIO"))


def build_contact():
    r = ""
    stores = "".join(
        f'<li><a href="{e(g["storeUrl"])}" target="_blank" rel="noopener"><span class="mini__name">{e(g["name"])}</span>'
        f'<span class="mini__dev">Store page</span></a></li>' for g in NEWEST)
    discord = "".join(
        f'<li><a href="{e(u)}" target="_blank" rel="noopener"><span class="mini__name">{e(g["name"])}</span>'
        f'<span class="mini__dev">{e(label)}</span></a></li>'
        for g in NEWEST for label, u in g.get("links", []) if label == "Discord")
    body = f"""
<header class="page-head">
  <h1 class="page-title">Contact</h1>
  <p class="page-lead">Players, press, creators and business: write to one inbox and we'll take it from there.</p>
</header>
<div class="split">
  <section class="panel" aria-labelledby="mail-title">
    <header class="panel__head"><h2 id="mail-title" class="panel__title">Email</h2></header>
    <div class="panel__body">
      <p class="mail"><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p class="actions">
        <a class="btn btn--primary" href="mailto:{EMAIL}">{glyph("A")}Write to us</a>
        <button type="button" class="btn" data-copy="{EMAIL}">{glyph("X")}<span data-copy-label>Copy address</span></button>
      </p>
      <h3 class="sub-title">Help with a game</h3>
      <p>Tell us which game, which headset, and your username. A screenshot or a short clip of the problem helps a lot.</p>
      <h3 class="sub-title">Press and creators</h3>
      <p>Say which game you're covering and where it will run, and we'll get back to you.</p>
    </div>
  </section>
  <section class="panel" aria-labelledby="find-title">
    <header class="panel__head"><h2 id="find-title" class="panel__title">Find the games</h2></header>
    <ul class="mini">{stores}{discord}</ul>
  </section>
</div>
<section class="panel biz" aria-labelledby="biz-title">
  <header class="panel__head"><h2 id="biz-title" class="panel__title">Business</h2></header>
  <div class="biz__body">
    <div class="panel__body">
      <p class="biz__lead">Co-development, publishing, licensing and brand partnerships.</p>
      <p>Buddy Beatdown is a co-development with 2080 Games. Tell us who you are, what you have in mind and when, and we'll get back to you.</p>
      <p class="actions"><a class="btn btn--primary" href="mailto:{EMAIL}?subject=Business%20inquiry">{glyph("A")}Business inquiry</a></p>
    </div>
    <dl class="spec">
      <div><dt>Experience</dt><dd>{YEARS} years in the industry</dd></div>
      <div><dt>Players</dt><dd>{PLAYERS} across all games</dd></div>
      <div><dt>Reviews</dt><dd><span data-reviews-total>{TOTAL_REVIEWS:,}</span> across all games</dd></div>
      <div><dt>Games</dt><dd><a href="games.html">{len(GAMES)} out now</a></dd></div>
    </dl>
  </div>
</section>
"""
    page(out="contact.html", title=f"Contact | {STUDIO}",
         description=f"Contact {STUDIO}: {EMAIL}. Help with a game, press, creators and business.",
         body=body, active="contact", r=r, canonical="contact.html", hint=hints("AP:\\CONTACT"))


def build_404():
    body = f"""
<section class="error">
  <p class="error__code">Error 404</p>
  <h1 class="error__title">Disc not found.</h1>
  <p class="page-lead">There's nothing at this address. The link may be old, or the page moved.</p>
  <p class="actions"><a class="btn btn--primary" href="/index.html">{glyph("B")}Back to home</a><a class="btn" href="/games.html">{glyph("Y")}Games</a></p>
</section>
"""
    page(out="404.html", title=f"Page not found | {STUDIO}", description="Page not found.", body=body, r="/",
         hint=hints("AP:\\404"))


def build_sitemap():
    urls = ["", "games.html", "studio.html", "contact.html"] + [f"games/{g['slug']}.html" for g in GAMES]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += [f"  <url><loc>{SITE_URL}/{u}</loc></url>" for u in urls]
    xml.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8", newline="\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
                                    encoding="utf-8", newline="\n")
    print("wrote site/sitemap.xml, site/robots.txt")


if __name__ == "__main__":
    build_home()
    build_games()
    for game in GAMES:
        build_game(game)
    build_studio()
    build_contact()
    build_404()
    build_sitemap()
