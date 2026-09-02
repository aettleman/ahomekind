# A Home Kind — Cruelty-Free Check (browser extension, v0.1.0)

An early build. It quietly checks whether the brand on the product page you're
looking at is cruelty-free/vegan according to [ahomekind.com](https://ahomekind.com)'s
own brand list, and drops a small badge near the title if it recognises it.

It reads the exact same `data/brands.json` the website uses — nothing is
duplicated or hand-copied, so any brand added or corrected on the site shows
up here automatically (the cache refreshes once a day).

## What it does right now

- Works on product pages on **amazon.co.uk**, **boots.com**, **superdrug.com**
  and **ocado.com**.
- Reads the product title, checks it against the brand list, and shows a
  badge (🍃 cruelty-free & vegan / 🐰 cruelty-free, check vegan status /
  ⚠️ parent company isn't cruelty-free / ❌ tested on animals / 🔍 not
  certified, no evidence either way) with a link through to the full brand
  page and a dismiss button.
- The toolbar icon shows how many brands are loaded and when the list last
  refreshed, with a manual refresh button.

## What it does NOT do yet

- It is **not published to the Chrome Web Store** — it has to be loaded
  manually (see below), which also means Chrome will show an "unpacked
  extension" warning. That's expected for a build at this stage.
- The CSS selectors used to find the product title/price area on each
  retailer's page (in `content.js`) are a **first-pass guess**, written
  without being able to browse the live sites from where this was built.
  They're the standard selectors those sites have used, but retailers change
  their markup without warning — if the badge doesn't show up on a page it
  should, that's the most likely reason. Treat this as a starting point that
  needs a real run against live pages before relying on it day to day.
- Brand matching is name-based (whole-word match against the product title),
  so it can miss brands that only appear in the product description, or
  occasionally mis-fire on a brand name that's also an ordinary word — it
  skips anything under 4 characters to keep that risk down, but it isn't
  perfect.
- No Firefox/Safari build — this is Chrome (and other Chromium browsers:
  Edge, Brave) only for now, using Manifest V3.

## How to try it (Chrome "load unpacked")

1. Open `chrome://extensions` in Chrome.
2. Turn on **Developer mode** (top-right toggle).
3. Click **Load unpacked** and select the `browser-extension` folder from
   this repo.
4. Visit a product page on one of the four supported sites. Give it a couple
   of seconds — the badge appears after the page settles, and again if the
   page updates itself without a full reload.
5. Click the toolbar icon any time to see how many brands are loaded and
   force a refresh.

## Reporting a site that's stopped working

If a retailer redesigns their product page and the badge stops appearing,
the fix is almost always updating the `SELECTORS` object at the top of
`content.js` to match the new markup — open the page's dev tools, find the
new selector for the title and the area just above the buy box, and swap it
in.
