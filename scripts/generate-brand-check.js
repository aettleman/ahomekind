#!/usr/bin/env node
// generate-brand-check.js
//
// Regenerates the brand cards and the priceMap object inside brand-check.html
// from data/brands.json, so that file is the single source of truth for the
// brand-check page too (previously every card was hand-typed directly into
// the HTML and could silently drift out of sync with data/brands.json).
//
// Run from the repo root with: node scripts/generate-brand-check.js
// (companion to `node scripts/generate-brand-pages.js`, same invocation style)
//
// To add/update a brand shown on brand-check.html: edit data/brands.json,
// then re-run this script (and generate-brand-pages.js if you want that
// brand's own static page regenerated too).

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const DATA_PATH = path.join(ROOT, 'data', 'brands.json');
const OUT_PATH = path.join(ROOT, 'brand-check.html');

// brand-check.html's own tier -> markup convention. This is deliberately
// separate from generate-brand-pages.js's TIER_META: brand-check.html has
// long used "warn" styling (orange warning triangle) for BOTH the
// "cruelty-free itself, parent company isn't" case (tier: warn) and the
// "unverified claim" case (tier: unverified) - only the label text differs.
// The client-side JS further down in brand-check.html reads these exact
// classes/labels to build the interactive result-card UI, so this mapping
// must keep producing byte-for-byte the same shapes it always has.
const TIER_META = {
  good:       { cardClass: '', ratingClass: '', emoji: '&#127807;', label: 'fully cruelty-free &amp; vegan' },
  check:      { cardClass: '', ratingClass: 'neutral', emoji: '&#128048;', label: 'cruelty-free, check vegan status per product' },
  warn:       { cardClass: 'warn', ratingClass: 'warn', emoji: '&#9888;&#65039;', label: 'cruelty-free itself, parent company isn\'t' },
  unverified: { cardClass: 'warn', ratingClass: 'warn', emoji: '&#9888;&#65039;', label: 'unverified claim' },
  bad:        { cardClass: 'bad', ratingClass: 'bad', emoji: '&#10060;', label: 'tested on animals' }
};

// data/brands.json category slugs -> brand-check.html's own data-category
// vocabulary (the CATEGORIES list + filter pills further down the page use
// this second, older vocabulary, so we translate into it rather than change
// the page's existing filtering behaviour).
//
// Notes on lossy/approximate mappings, called out here so they're easy to
// find later:
//  - "laundry" has no separate brand-check tile of its own; it has always
//    been folded into the broader "household" tag (see original Ariel/Bold/
//    Daz/etc. cards, which predate this script and were tagged "household").
//  - "period-menstrual" has no separate tile either; period-care brands
//    (Natracare, TOTM, DAME, ...) have always been tagged "body-shower".
//  - "food-kitchen" has no equivalent tile at all on brand-check.html today
//    (food & kitchen brands aren't covered by this page yet) - it's dropped.
const CATEGORY_MAP = {
  'makeup-beauty': 'makeup',
  'skincare': 'skin-care',
  'haircare': 'hair-care',
  'body-shower': 'body-shower',
  'dental': 'mouth-care',
  'household-cleaning': 'household',
  'laundry': 'household',
  'period-menstrual': 'body-shower',
  'food-kitchen': null
};

// data/brands.json has no field marking "this is a supermarket's own-brand
// range" - that's a retail concept, not a cruelty-free/vegan-status
// concept, so nothing in the schema captures it. brand-check.html has
// always special-cased these seven into their own section/tile by name;
// we keep doing that here by name since there's nowhere else to source it
// from. If more supermarket own-brand entries are added to brands.json in
// future, add their exact `name` to this list too.
const SUPERMARKET_NAMES = new Set([
  'Aldi', 'Lidl', 'Co-op', "Sainsbury's", 'Morrisons', 'Waitrose', 'Marks & Spencer'
]);

const BEAUTY_CATS = new Set(['makeup-beauty', 'skincare', 'haircare', 'body-shower', 'period-menstrual']);
const HOUSEHOLD_CATS = new Set(['household-cleaning', 'laundry']);

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .split('&').join('&amp;')
    .split('<').join('&lt;')
    .split('>').join('&gt;')
    .split('"').join('&quot;');
}

function dataCategoryAttr(brand) {
  const seen = [];
  (brand.category || []).forEach(function (c) {
    const mapped = CATEGORY_MAP[c];
    if (mapped && seen.indexOf(mapped) === -1) seen.push(mapped);
  });
  return seen.join(' ');
}

function renderCard(brand) {
  const tier = TIER_META[brand.tier] || TIER_META.check;
  const cardClass = 'card' + (tier.cardClass ? ' ' + tier.cardClass : '');
  const ratingClass = 'rating' + (tier.ratingClass ? ' ' + tier.ratingClass : '');
  const dataCategory = dataCategoryAttr(brand);
  const nameHtml = brand.slug
    ? '<a href="brands/' + brand.slug + '/">' + escapeHtml(brand.name) + '</a>'
    : escapeHtml(brand.name);
  return '<div class="' + cardClass + '" data-category="' + dataCategory + '">' +
    '<p class="' + ratingClass + '">' + tier.emoji + ' ' + tier.label + '</p>' +
    '<h3>' + nameHtml + '</h3>' +
    '<p>' + escapeHtml(brand.note) + '</p></div>';
}

// Classify each brand into exactly one of brand-check.html's existing
// section groupings, in the same priority order the hand-written page
// followed (see comment above each bucket).
function classify(brand) {
  const cats = brand.category || [];

  // 1. Named supermarket own-brand ranges get their own section regardless
  //    of category tags, matching the original page.
  if (SUPERMARKET_NAMES.has(brand.name)) return 'supermarket';

  // 2. Dental/mouth-care brands of every tier live together in one section
  //    (the original page never split dental into a separate "tested on
  //    animals" bucket the way it did for every other category).
  if (cats.indexOf('dental') !== -1) return 'dental';

  // 3. Every other "bad" tier brand (any remaining category) goes into the
  //    single big "tested on animals" section at the end, regardless of
  //    what kind of product it is - matches the original page's layout.
  if (brand.tier === 'bad') return 'bad-all';

  // 4. Beauty/personal-care categories.
  if (cats.some(function (c) { return BEAUTY_CATS.has(c); })) {
    return (brand.tier === 'warn' || brand.tier === 'unverified') ? 'beauty-disclaimer' : 'beauty';
  }

  // 5. Household/laundry categories.
  if (cats.some(function (c) { return HOUSEHOLD_CATS.has(c); })) {
    return (brand.tier === 'warn' || brand.tier === 'unverified') ? 'household-disclaimer' : 'household';
  }

  // 6. Anything left over (e.g. food-kitchen-only brands, or brands with no
  //    category tags at all) has no matching section on this page yet.
  return 'other';
}

function buildCardsMarkup(brands) {
  const buckets = {
    beauty: [], 'beauty-disclaimer': [], household: [], 'household-disclaimer': [],
    dental: [], supermarket: [], 'bad-all': [], other: []
  };
  const unclassified = [];

  brands.forEach(function (brand) {
    const bucket = classify(brand);
    buckets[bucket].push(brand);
    if (bucket === 'other') unclassified.push(brand.name);
  });

  const out = [];

  out.push('<p class="section-label">beauty &amp; skincare</p>');
  buckets.beauty.forEach(function (b) { out.push(renderCard(b)); });

  out.push('<p class="section-label warn">worth a disclaimer - beauty &amp; haircare</p>');
  buckets['beauty-disclaimer'].forEach(function (b) { out.push(renderCard(b)); });

  out.push('<p class="section-label">household &amp; cleaning</p>');
  buckets.household.forEach(function (b) { out.push(renderCard(b)); });

  out.push('<p class="section-label warn">worth a disclaimer - household &amp; cleaning</p>');
  buckets['household-disclaimer'].forEach(function (b) { out.push(renderCard(b)); });

  out.push('<p class="section-label">dental &amp; oral care</p>');
  out.push('<div id="dentalDisclaimer" style="display:none; background:#ece5d5; border:0.5px solid #cfc4a9; border-radius:10px; padding:16px 18px; margin-bottom:16px; font-size:13px; color:#5c5c4f; line-height:1.8;">');
  out.push("Buying floss, toothbrushes, toothpaste, mouthwash or interdental brushes from a company that isn't cruelty-free still financially supports that company - even though these are non-edible, everyday items. That's a different claim from saying any specific product was itself personally tested on an animal: it's about where your money goes, not a claim about that individual item's testing history.");
  out.push('</div>');
  buckets.dental.forEach(function (b) { out.push(renderCard(b)); });

  out.push('<p class="section-label">supermarket own brand</p>');
  buckets.supermarket.forEach(function (b) { out.push(renderCard(b)); });

  out.push('<p class="section-label" style="color:#8a332c;">tested on animals</p>');
  out.push('<p style="font-size:13.5px; color:#7a7561; margin-bottom:18px;">These parent companies confirm they test where legally required, most commonly to sell into mainland China.</p>');
  buckets['bad-all'].forEach(function (b) { out.push(renderCard(b)); });

  if (buckets.other.length) {
    out.push('<p class="section-label">other</p>');
    buckets.other.forEach(function (b) { out.push(renderCard(b)); });
  }

  return { markup: out.join('\n'), unclassified: unclassified };
}

function buildPriceMap(brands) {
  const map = {};
  brands.forEach(function (b) {
    if (b.price) map[b.name] = b.price;
  });
  return 'var priceMap = ' + JSON.stringify(map) + ';';
}

function main() {
  const brands = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
  let html = fs.readFileSync(OUT_PATH, 'utf8');

  const cardsResult = buildCardsMarkup(brands);

  const cardsStart = '<!-- GENERATED:BRAND-CARDS:START -->';
  const cardsEnd = '<!-- GENERATED:BRAND-CARDS:END -->';
  const cardsRe = new RegExp(cardsStart + '[\\s\\S]*?' + cardsEnd);
  const cardsBlock = cardsStart + '\n' + cardsResult.markup + '\n' + cardsEnd;
  if (!cardsRe.test(html)) {
    throw new Error('Could not find GENERATED:BRAND-CARDS markers in brand-check.html');
  }
  html = html.replace(cardsRe, cardsBlock);

  const priceStart = '// GENERATED:PRICEMAP:START';
  const priceEnd = '// GENERATED:PRICEMAP:END';
  const priceRe = new RegExp(priceStart + '[\\s\\S]*?' + priceEnd);
  const priceBlock = priceStart + '\n' + buildPriceMap(brands) + '\n' + priceEnd;
  if (!priceRe.test(html)) {
    throw new Error('Could not find GENERATED:PRICEMAP markers in brand-check.html');
  }
  html = html.replace(priceRe, priceBlock);

  fs.writeFileSync(OUT_PATH, html, 'utf8');

  console.log('Done. ' + brands.length + ' brands rendered into brand-check.html.');
  if (cardsResult.unclassified.length) {
    console.log('Brands with no matching section (shown under "other"): ' + cardsResult.unclassified.join(', '));
  }
}

main();
