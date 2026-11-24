/* Armored Pig Studios: small console-style touches. Every page works without this file. */
(() => {
  'use strict';
  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
  const isTyping = (el) => el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName));
  const script = document.currentScript;

  // Clock in the top bar, like a console's status bar.
  const clocks = $$('[data-clock]');
  if (clocks.length) {
    const fmt = new Intl.DateTimeFormat(undefined, { hour: '2-digit', minute: '2-digit' });
    const tick = () => {
      const now = new Date();
      clocks.forEach((c) => { c.textContent = fmt.format(now); c.dateTime = now.toISOString(); });
    };
    tick();
    setTimeout(() => { tick(); setInterval(tick, 60000); }, (60 - new Date().getSeconds()) * 1000);
  }

  // Review counts. Pages are built with the counts the store had then; data/reviews.json is refreshed from the
  // store every hour, so read it when the page opens and again every few minutes while it stays open.
  const nf = new Intl.NumberFormat('en-US');
  let counts = null;                           // slug -> { reviews, ratings } once data/reviews.json has loaded
  const reviewsOf = (slug) => {
    const c = counts && counts[slug];
    return c && Number.isFinite(c.reviews) ? c.reviews : null;
  };
  const paintCounts = () => {
    $$('[data-reviews]').forEach((el) => {
      const n = reviewsOf(el.dataset.reviews);
      if (n !== null) el.textContent = nf.format(n);
    });
    $$('[data-count]').forEach((row) => {      // games library rows, for sorting by reviews
      const n = reviewsOf(row.dataset.slug);
      if (n !== null) row.dataset.count = String(n);
    });
    const total = Object.values(counts).reduce((sum, c) => sum + (Number.isFinite(c.reviews) ? c.reviews : 0), 0);
    $$('[data-reviews-total]').forEach((el) => { el.textContent = nf.format(total); });
  };
  if (script && $('[data-reviews], [data-reviews-total]')) {
    const url = new URL('../../data/reviews.json', script.src);
    let loadedAt = 0;
    const load = async () => {
      if (Date.now() - loadedAt < 60000) return;
      loadedAt = Date.now();
      try {
        const res = await fetch(url, { cache: 'no-cache' });
        if (!res.ok) return;
        const data = await res.json();
        if (data && data.games) {
          counts = data.games;
          paintCounts();
        }
      } catch {
        // Offline, or the page was opened from disk: the counts it was built with stay.
      }
    };
    load();
    setInterval(() => { if (!document.hidden) load(); }, 10 * 60 * 1000);
    document.addEventListener('visibilitychange', () => { if (!document.hidden) load(); });
  }

  // Home: point at a game on the shelf to show it above; click (or Enter) opens it.
  const featured = $('[data-featured]');
  const featuredData = $('#featured-data');
  if (featured && featuredData) {
    const games = JSON.parse(featuredData.textContent);
    const tiles = $$('.tile', featured);
    const art = $('[data-feat-img]', featured);
    const reviews = $('[data-feat-reviews]', featured);
    let current = 0;

    const show = (i) => {
      if (i === current || !games[i]) return;
      current = i;
      const g = games[i];
      tiles.forEach((t, j) => {
        const on = j === i;
        t.classList.toggle('is-selected', on);
        t.tabIndex = on ? 0 : -1;
        if (on) t.setAttribute('aria-current', 'true'); else t.removeAttribute('aria-current');
      });
      $('[data-feat-count]', featured).textContent = String(i + 1).padStart(2, '0');
      $('[data-feat-kicker]', featured).innerHTML = g.kicker;
      $('[data-feat-name]', featured).textContent = g.name;
      const sub = $('[data-feat-sub]', featured);
      sub.textContent = g.sub;
      sub.hidden = !g.sub;
      $('[data-feat-tags]', featured).innerHTML = g.tags;
      $('[data-feat-text]', featured).textContent = g.text;
      if (reviews) {
        const n = reviewsOf(g.slug) ?? g.reviews;
        reviews.dataset.reviews = g.slug;
        reviews.textContent = n == null ? '' : nf.format(n);
        reviews.parentElement.hidden = n == null;
      }
      $$('[data-feat-link]', featured).forEach((a) => { a.href = g.href; });
      $('[data-feat-store]', featured).href = g.store;
      art.style.opacity = '0.25';
      const next = new Image();
      next.onload = next.onerror = () => {
        if (current !== i) return;
        art.src = g.cover;
        art.alt = g.alt;
        art.style.opacity = '';
      };
      next.src = g.cover;
    };

    tiles.forEach((t, i) => {
      t.tabIndex = i === 0 ? 0 : -1;
      t.addEventListener('mouseenter', () => show(i));
      t.addEventListener('focus', () => show(i));
      t.addEventListener('keydown', (ev) => {
        const last = tiles.length - 1;
        const to = { ArrowRight: i === last ? 0 : i + 1, ArrowLeft: i === 0 ? last : i - 1, Home: 0, End: last }[ev.key];
        if (to === undefined) return;
        ev.preventDefault();
        tiles[to].focus();
      });
    });

    // Fetch the big covers once the page has settled so switching is instant.
    window.addEventListener('load', () => {
      setTimeout(() => games.forEach((g) => { const im = new Image(); im.src = g.cover; }), 400);
    });
  }

  // Games: sort the library, and move between games with the up and down arrows.
  const library = $('[data-library]');
  if (library) {
    const rows = $$('.row', library);
    const buttons = $$('[data-sort]');
    const order = {
      date: (a, b) => b.dataset.date.localeCompare(a.dataset.date),
      name: (a, b) => a.dataset.name.localeCompare(b.dataset.name),
      reviews: (a, b) => (Number(b.dataset.count) || 0) - (Number(a.dataset.count) || 0),
    };
    buttons.forEach((b) => b.addEventListener('click', () => {
      buttons.forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      rows.slice().sort(order[b.dataset.sort]).forEach((r) => library.appendChild(r));
    }));
    library.addEventListener('keydown', (ev) => {
      if (ev.key !== 'ArrowDown' && ev.key !== 'ArrowUp') return;
      const links = $$('.row__name a', library);
      const i = links.indexOf(document.activeElement);
      if (i < 0) return;
      ev.preventDefault();
      links[Math.max(0, Math.min(links.length - 1, i + (ev.key === 'ArrowDown' ? 1 : -1)))].focus();
    });
  }

  // Game pages: screenshots open in a viewer; arrows step through them.
  const viewer = $('[data-viewer]');
  if (viewer && typeof viewer.showModal === 'function') {
    const links = $$('[data-shot]');
    const big = $('[data-viewer-img]', viewer);
    const count = $('[data-viewer-count]', viewer);
    let at = 0;
    const show = (i) => {
      at = (i + links.length) % links.length;
      big.src = links[at].href;
      big.alt = $('img', links[at]).alt;
      count.textContent = `${at + 1} / ${links.length}`;
    };
    links.forEach((a, i) => a.addEventListener('click', (ev) => {
      ev.preventDefault();
      show(i);
      viewer.showModal();
    }));
    $('[data-viewer-prev]', viewer).addEventListener('click', () => show(at - 1));
    $('[data-viewer-next]', viewer).addEventListener('click', () => show(at + 1));
    $('[data-viewer-close]', viewer).addEventListener('click', () => viewer.close());
    viewer.addEventListener('keydown', (ev) => {
      if (ev.key === 'ArrowRight') { ev.preventDefault(); show(at + 1); }
      if (ev.key === 'ArrowLeft') { ev.preventDefault(); show(at - 1); }
    });
    viewer.addEventListener('click', (ev) => { if (ev.target === viewer) viewer.close(); });
    viewer.addEventListener('close', () => links[at].focus());
  }

  // Game pages: Esc goes back to the library, like B on a controller.
  const back = document.body.dataset.back;
  if (back) {
    document.addEventListener('keydown', (ev) => {
      if (ev.key !== 'Escape' || ev.defaultPrevented || isTyping(ev.target) || $('dialog[open]')) return;
      window.location.href = back;
    });
  }

  // Contact: copy the email address.
  $$('[data-copy]').forEach((b) => b.addEventListener('click', async () => {
    const label = $('[data-copy-label]', b) || b;
    const was = label.textContent;
    try {
      await navigator.clipboard.writeText(b.dataset.copy);
      label.textContent = 'Copied';
    } catch {
      label.textContent = 'Select and copy';
    }
    setTimeout(() => { label.textContent = was; }, 1800);
  }));
})();
