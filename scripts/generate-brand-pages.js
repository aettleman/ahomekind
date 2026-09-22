// generate-brand-pages.js
// Reads data/brands.json and generates one static, SEO-friendly page per brand
// at brands/[slug]/index.html, plus a sitemap.xml listing every URL.
//
// Run from the repo root with: node scripts/generate-brand-pages.js
// Requires nothing beyond Node.js itself (no npm install needed).
//
// To add a new brand: add one object to data/brands.json, then re-run this
// script. It will create (or update) that brand's page automatically.

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const DATA_PATH = path.join(ROOT, 'data', 'brands.json');
const OUT_DIR = path.join(ROOT, 'brands');
const SITE_URL = 'https://ahomekind.com';

const TIER_META = {
  good:  { emoji: '&#127807;', label: 'fully cruelty-free &amp; vegan', className: 'good', ratingClass: 'good', shareImage: 'share-good.jpg' },
  check: { emoji: '&#128048;', label: 'cruelty-free, check vegan status per product', className: 'check', ratingClass: 'check', shareImage: 'share-check.jpg' },
  warn:  { emoji: '&#9888;&#65039;', label: 'cruelty-free itself, parent company isn\'t', className: 'warn', ratingClass: 'warn', shareImage: 'share-warn.jpg' },
  bad:   { emoji: '&#10060;', label: 'tested on animals', className: 'bad', ratingClass: 'bad', shareImage: 'share-bad.jpg' },
  unverified: { emoji: '&#128269;', label: 'not certified - no evidence either way', className: 'unverified', ratingClass: 'unverified', shareImage: 'share-default.jpg' },
  unknown: { emoji: '&#10067;', label: 'status not known yet', className: 'unverified', ratingClass: 'unverified', shareImage: 'share-default.jpg' }
};

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .split('&').join('&amp;')
    .split('<').join('&lt;')
    .split('>').join('&gt;')
    .split('\"').join('&quot;');
}

function pageTitle(brand) {
  return 'Is ' + brand.name + ' Cruelty-Free? - a home kind';
}

var MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
function formatVerifiedDate(iso) {
  var parts = String(iso).split('-');
  if (parts.length !== 3) return iso;
  var y = parts[0], m = parseInt(parts[1], 10) - 1, d = parseInt(parts[2], 10);
  return d + ' ' + (MONTHS[m] || '') + ' ' + y;
}

function pageDescription(brand) {
  return escapeHtml(brand.note || ('Find out whether ' + brand.name + ' is cruelty-free and vegan.'));
}

function renderSection(title, items, emptyNote) {
  if (!items || items.length === 0) {
    return '<p class="section-label">' + title + '</p>\n<p style="color:#80686F; font-size:13.5px;">' + emptyNote + '</p>';
  }
  const rows = items.map(function(i){ return '<li>' + escapeHtml(i) + '</li>'; }).join('\n');
  return '<p class="section-label">' + title + '</p>\n<ul style="margin:0 0 20px 20px; font-size:14px; line-height:1.9;">\n' + rows + '\n</ul>';
}

function renderLinks(links) {
  if (!links || links.length === 0) return '';
  const rows = links.map(function(l){ return '<a href="' + escapeHtml(l.url) + '" target="_blank" rel="noopener">' + escapeHtml(l.label || l.url) + '</a>'; }).join(' &middot; ');
  return '<p class="section-label">sources &amp; links</p>\n<p style="font-size:13.5px;">' + rows + '</p>';
}

// Round stamp icons, shared with brand-check.html's rows -- leaf for
// good, check for check, alert-triangle for warn, x for bad, question
// mark circle for unverified.
const STAMP_ICONS = {
  good: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 4 13a7 7 0 0 1 7-7c0 5-3 9-3 9s6-1 8-6a9 9 0 0 1-2 11 7 7 0 0 1-6 0Z"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
  warn: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v4M12 17h.01M10.3 3.9 2.7 17.3A1.6 1.6 0 0 0 4.1 20h15.8a1.6 1.6 0 0 0 1.4-2.7L13.7 3.9a1.6 1.6 0 0 0-2.8 0Z"/></svg>',
  bad: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>',
  unverified: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8"/><path d="M12 16h.01M9.5 9.5a2.5 2.5 0 0 1 4.6-1.4c.4.7.3 1.5-.3 2.1L12 12v1"/></svg>'
};
// One plain-English headline per tier, for the big verdict card -- the
// same four answers as the homepage's "four possible answers" grid, plus
// the fifth unverified case.
const VERDICT_HEADLINE = {
  good: 'Cruelty-free and vegan.',
  check: "Cruelty-free. Vegan status varies by product.",
  warn: "This brand's fine. Its owner isn't.",
  bad: 'Tests on animals, or sells where it\'s required.',
  unverified: 'Not certified either way, yet.'
};

function buildOwnershipChain(brand, allBrands) {
  if (!brand.parentCompany) return '';
  const siblings = allBrands.filter(function(b){ return b.parentCompany === brand.parentCompany && b.slug !== brand.slug; });
  const tier = TIER_META[brand.tier] || TIER_META.check;
  let html = '<div class="chain">';
  html += '<p class="chain-kick">who owns who</p>';
  html += '<div class="chain-node"><span class="ahk-stamp tier-' + tier.className + '">' + (STAMP_ICONS[brand.tier] || STAMP_ICONS.unverified) + '</span><b>' + escapeHtml(brand.name) + '</b><span>' + tier.label + '</span></div>';
  html += '<div class="chain-link">owned by</div>';
  html += '<div class="chain-node"><b>' + escapeHtml(brand.parentCompany) + '</b><span>' + siblings.length + ' other brand' + (siblings.length === 1 ? '' : 's') + ' on here</span></div>';
  html += '</div>';
  return html;
}

function buildSwaps(brand, allBrands) {
  if (brand.tier === 'good' || brand.tier === 'check') return '';
  const cat = (brand.category && brand.category[0]) || null;
  const pool = allBrands.filter(function(b){
    if (b.slug === brand.slug) return false;
    if (b.tier !== 'good' && b.tier !== 'check') return false;
    if (cat && b.category && b.category.indexOf(cat) === -1) return false;
    return true;
  });
  if (!pool.length) return '';
  // Stable pick rather than random, so the page doesn't change on every
  // rebuild -- based on the brand's own slug.
  let seed = 0;
  for (let i = 0; i < brand.slug.length; i++) seed += brand.slug.charCodeAt(i);
  const picks = [];
  for (let i = 0; i < Math.min(2, pool.length); i++) {
    picks.push(pool[(seed + i * 7) % pool.length]);
  }
  if (!picks.length) return '';
  let html = '<div class="swaps"><p class="swaps-kick">kinder swaps</p><div class="swaps-row">';
  picks.forEach(function(p){
    const ptier = TIER_META[p.tier] || TIER_META.check;
    html += '<a class="swap-card" href="../' + p.slug + '/index.html">';
    html += '<span class="ahk-stamp tier-' + ptier.className + '">' + (STAMP_ICONS[p.tier] || STAMP_ICONS.check) + '</span>';
    html += '<b>' + escapeHtml(p.name) + '</b><span>' + ptier.label + '</span>';
    html += '</a>';
  });
  html += '</div></div>';
  return html;
}

let ALL_BRANDS = [];

function renderBrandPage(brand) {
  const tier = TIER_META[brand.tier] || TIER_META.check;
  const title = pageTitle(brand);
  const description = pageDescription(brand);
  const canonical = SITE_URL + '/brands/' + brand.slug;
  const veganLine = brand.vegan === 'full' ? '100% vegan'
    : brand.vegan === 'partial' ? 'varies by product'
    : 'not yet confirmed';
  const veganPillClass = brand.vegan === 'full' ? 'vegan-yes'
    : brand.vegan === 'partial' ? 'vegan-partial'
    : 'vegan-unknown';
  const parentPillClass = brand.tier === 'bad' ? 'parent-bad' : 'parent-neutral';
  const parentLine = brand.parentCompany ? ('<span class="status-pill ' + parentPillClass + '"><span class="status-pill-label">parent company</span> ' + escapeHtml(brand.parentCompany) + '</span>') : '';
  const parentTestFlag = brand.tier === 'unverified'
    ? (brand.parentTestsOnAnimals === true
        ? '<p class="parent-test-flag bad">&#10060; parent company tests on animals</p>'
        : brand.parentTestsOnAnimals === false
        ? '<p class="parent-test-flag good">&#127807; parent company doesn\'t test on animals</p>'
        : '<p class="parent-test-flag unverified">&#128269; parent company\'s testing policy is also unverified</p>')
    : '';
  const veganButNotCrueltyFreeWarning = (brand.tier === 'bad' && (brand.vegan === 'partial' || brand.vegan === 'full'))
    ? '<div style="margin-top:16px; padding:14px 16px; background:#F5D3D6; border:0.5px solid #d9b9b3; border-radius:8px; font-size:13.5px; color:#7a4640; line-height:1.7;"><strong>a vegan label here doesn\'t make it cruelty-free.</strong> ' + escapeHtml(brand.name) + ' isn\'t on the cruelty-free list because of the company\'s wider testing policy, not because of what\'s in any one product. Buying a vegan-labelled item from them still puts money behind a company that tests on animals elsewhere in its business.</div>'
    : '';

  const lines = [];
  lines.push('<!DOCTYPE html>');
  lines.push('<html lang="en">');
  lines.push('<head>');
  lines.push('<meta charset="UTF-8">');
  lines.push('<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">');
  lines.push('<title>' + escapeHtml(title) + '</title>');
  lines.push('<meta name="description" content="' + description + '">');
  lines.push('<link rel="canonical" href="' + canonical + '">');
  lines.push('<meta property="og:title" content="' + escapeHtml(title) + '">');
  lines.push('<meta property="og:description" content="' + description + '">');
  lines.push('<meta property="og:type" content="article">');
  lines.push('<meta property="og:url" content="' + canonical + '">');
  // Without an image a shared brand link previews as a bare URL, which is
  // the least persuasive possible version of it. Each tier gets its own
  // card, so the preview already says cruelty-free or tested-on-animals
  // before anyone taps through.
  lines.push('<meta property="og:image" content="' + SITE_URL + '/images/' + tier.shareImage + '">');
  lines.push('<meta property="og:image:alt" content="' + escapeHtml(brand.name) + ' on a home kind">');
  lines.push('<meta property="og:site_name" content="a home kind">');
  lines.push('<meta name="twitter:card" content="summary_large_image">');
  lines.push('<link href="https://fonts.googleapis.com/css2?family=Gloock&family=Hanken+Grotesk:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Caveat:wght@500;700&display=swap" rel="stylesheet">');
  lines.push('<link rel="stylesheet" href="../../css/app.css?v=5">');
  lines.push('<link rel="manifest" href="../../manifest.json">');
  lines.push('<meta name="theme-color" content="#3A1F3D">');
  lines.push('<link rel="icon" href="../../favicon.ico" sizes="any">');
  lines.push('<link rel="icon" type="image/png" sizes="32x32" href="../../icons/favicon-32.png">');
  lines.push('<link rel="icon" type="image/png" sizes="16x16" href="../../icons/favicon-16.png">');
  lines.push('<link rel="apple-touch-icon" href="../../icons/apple-touch-icon.png">');
  lines.push('<meta name="apple-mobile-web-app-capable" content="yes">');
  lines.push('<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">');
  lines.push('<meta name="apple-mobile-web-app-title" content="A Home Kind">');
  lines.push('<style>');
  lines.push('.card.bad { border-color:#C9546A; background:#F5D3D6; }');
  lines.push('.rating.bad { color:#A8324E; }');
  lines.push('.bp-head { display:flex; gap:14px; align-items:center; margin:12px 0 0; }');
  lines.push('.bp-head .arch { width:64px; height:78px; flex:none; border-radius:999px 999px 22px 22px; background:var(--ahk-surface,#EFDDD3); display:flex; align-items:center; justify-content:center; color:var(--ahk-heading); font:400 26px \'Gloock\',serif; }');
  lines.push('.bp-head h1 { font:400 32px/1 \'Gloock\',serif; margin:0; }');
  lines.push('.bp-head p { font-size:12.5px; color:var(--ahk-text-muted,#80686F); margin:4px 0 0; text-transform:capitalize; }');
  lines.push('.vcard { margin:18px 0 0; border-radius:24px; padding:22px; position:relative; overflow:hidden; }');
  lines.push('.vcard.tier-good, .vcard.tier-check { background:var(--ahk-sage-soft,#DCE6D6); }');
  lines.push('.vcard.tier-warn { background:var(--ahk-clay-soft,#FBE3D3); }');
  lines.push('.vcard.tier-bad { background:#F5D3D6; }');
  lines.push('.vcard.tier-unverified { background:var(--ahk-surface,#EFDDD3); }');
  lines.push('.vcard .bigst { float:right; margin:-4px -4px 10px 12px; width:64px; height:64px; border-radius:50%; display:grid; place-items:center; color:#fff; box-shadow:0 8px 18px -8px rgba(42,22,48,.5); }');
  lines.push('.vcard.tier-good .bigst, .vcard.tier-check .bigst { background:#3f6a3d; }');
  lines.push('.vcard.tier-warn .bigst { background:var(--ahk-warm-deep,#A0582E); }');
  lines.push('.vcard.tier-bad .bigst { background:#A8324E; }');
  lines.push('.vcard.tier-unverified .bigst { background:var(--ahk-text-muted,#80686F); }');
  lines.push('.vcard .bigst svg { width:24px; height:24px; }');
  lines.push('.vcard h2 { font:400 24px/1.2 \'Gloock\',serif; margin:0; clear:none; color:var(--ahk-heading,#2A1630); }');
  lines.push('.vcard p.vnote { font-size:14px; line-height:1.7; margin:10px 0 0; clear:both; color:var(--ahk-heading,#2A1630); }');
  lines.push('.chain { margin:16px 0 0; background:var(--ahk-card,#FBF4EF); border:1px solid var(--ahk-border-soft,#EBDAD1); border-radius:22px; padding:16px; }');
  lines.push('.chain-kick { font:700 10.5px \'Hanken Grotesk\',sans-serif; letter-spacing:.12em; text-transform:uppercase; color:var(--ahk-text-muted,#80686F); margin:0 0 10px; }');
  lines.push('.chain-node { display:flex; align-items:center; gap:12px; padding:10px 12px; border-radius:16px; background:var(--ahk-bg,#F4E6DE); }');
  lines.push('.chain-node b { flex:1; font:400 18px \'Gloock\',serif; }');
  lines.push('.chain-node span { font-size:11.5px; color:var(--ahk-text-muted,#80686F); }');
  lines.push('.chain-link { display:flex; align-items:center; gap:10px; padding:6px 0 6px 28px; font:600 11px \'Hanken Grotesk\',sans-serif; letter-spacing:.12em; text-transform:uppercase; color:var(--ahk-text-muted,#80686F); }');
  lines.push('.chain-link::before { content:""; width:2px; height:22px; background:repeating-linear-gradient(var(--ahk-text-muted,#80686F) 0 3px, transparent 3px 6px); display:inline-block; }');
  lines.push('.swaps { margin:18px 0 0; }');
  lines.push('.swaps-kick { font:700 10.5px \'Hanken Grotesk\',sans-serif; letter-spacing:.12em; text-transform:uppercase; color:var(--ahk-text-muted,#80686F); margin:0 0 10px; }');
  lines.push('.swaps-row { display:flex; gap:10px; }');
  lines.push('.swap-card { flex:1; background:var(--ahk-card,#FBF4EF); border:1px solid var(--ahk-border-soft,#EBDAD1); border-radius:18px; padding:14px; text-decoration:none; display:flex; flex-direction:column; gap:8px; }');
  lines.push('.swap-card b { font:400 16px \'Gloock\',serif; color:var(--ahk-heading,#2A1630); }');
  lines.push('.swap-card span { font-size:11px; color:var(--ahk-text-muted,#80686F); }');
  lines.push('.signed { display:flex; align-items:center; justify-content:space-between; margin:20px 0 0; padding:14px 16px; border-radius:16px; border:1px dashed var(--ahk-border,#E4D0C6); }');
  lines.push('.signed .ahk-hand { font-size:24px; }');
  lines.push('.signed small { display:block; font:700 10px \'Hanken Grotesk\',sans-serif; letter-spacing:.12em; text-transform:uppercase; color:var(--ahk-text-muted,#80686F); }');
  lines.push('</style>');
  lines.push('</head>');
  lines.push('<body>');
  lines.push('<a href="#main" class="skip-link">skip to content</a>');
  lines.push('<header class="site-header">');
  lines.push('<div class="wrap">');
  lines.push('<a href="../../index.html" class="logo">');
  lines.push('<span>a home kind</span>');
  lines.push('</a>');
  lines.push('<nav class="main-nav">');
  lines.push('<a href="../../scan.html">scan</a>');
  lines.push('<a href="../../brand-check.html">check a brand</a>');
  lines.push('<a href="../../learn.html">learn</a>');
  lines.push('<a href="../../impact.html">your impact</a>');
  lines.push('<a href="../../shop.html" class="nav-shop-btn">shop</a>');
  lines.push('</nav>');
  lines.push('</div>');
  lines.push('</header>');
  lines.push('');
  lines.push('<main class="page-shell" id="main">');
  lines.push('<p class="ahk-back-link"><a href="../../brand-check.html" id="ahkBackLink">&larr; back to brand check</a></p>');
  lines.push('<script>(function(){var a=document.getElementById("ahkBackLink");if(a&&document.referrer&&document.referrer.indexOf("brand-check.html")!==-1){a.addEventListener("click",function(e){e.preventDefault();history.back();});}})();</script>');
  lines.push('');
  const priceBadge = brand.price ? ('<span style="display:inline-block; margin-left:10px; padding:2px 9px; background:var(--ahk-gold-soft,#F6C6A8); border-radius:12px; font-size:12px; color:var(--ahk-heading,#2A1630); vertical-align:middle;">' + escapeHtml(brand.price) + '</span>') : '';
  const catLabel = (brand.category && brand.category.length) ? brand.category.map(escapeHtml).join(' &middot; ') : '';
  const initial = (brand.name.replace(/[^A-Za-z0-9]/g, '').charAt(0) || '?').toUpperCase();

  lines.push('<div class="bp-head">');
  lines.push('<div class="arch">' + initial + '</div>');
  lines.push('<div><p style="margin:0; font:700 10.5px \'Hanken Grotesk\',sans-serif; letter-spacing:.12em; text-transform:uppercase; color:var(--ahk-text-muted,#80686F);">' + catLabel + '</p><h1>' + escapeHtml(brand.name) + '</h1><p>' + (brand.price ? escapeHtml(brand.price) : '') + '</p></div>');
  lines.push('</div>');
  lines.push('');

  lines.push('<div class="vcard tier-' + tier.className + '">');
  lines.push('<div class="bigst">' + (STAMP_ICONS[brand.tier] || STAMP_ICONS.unverified) + '</div>');
  lines.push('<h2>' + (VERDICT_HEADLINE[brand.tier] || VERDICT_HEADLINE.unverified) + '</h2>');
  lines.push('<p class="vnote">' + escapeHtml(brand.note) + priceBadge + '</p>');
  if (parentTestFlag) lines.push(parentTestFlag);
  lines.push('</div>');
  lines.push('');
  lines.push(veganButNotCrueltyFreeWarning);
  lines.push('');

  lines.push('<div class="status-facts" style="margin-top:18px;">');
  lines.push('<span class="status-pill ' + veganPillClass + '"><span class="status-pill-label">vegan status</span> ' + veganLine + '</span>');
  lines.push(parentLine);
  lines.push('</div>');
  lines.push('');

  lines.push(buildOwnershipChain(brand, ALL_BRANDS));
  lines.push('');

  lines.push('<div style="margin-top:24px;">');
  lines.push(renderLinks(brand.links));
  lines.push('</div>');
  lines.push('');

  lines.push('<div style="margin-top:32px;">');
  lines.push(renderSection('products checked', brand.products, 'I haven\'t listed specific products for ' + escapeHtml(brand.name) + ' yet - check back soon.'));
  lines.push('</div>');
  lines.push('');

  lines.push(buildSwaps(brand, ALL_BRANDS));
  lines.push('');

  lines.push('<div class="signed">');
  lines.push('<div><small>checked by</small><span class="ahk-hand">Ash</span></div>');
  lines.push('</div>');
  lines.push('');

  lines.push('<div style="margin-top:20px; padding:18px 20px; background:var(--ahk-surface,#EFDDD3); border:0.5px solid var(--ahk-border,#E4D0C6); border-radius:16px; font-size:13px; color:var(--ahk-text-muted,#80686F);">');
  if (brand.lastVerified) {
    lines.push('<p style="margin:0 0 8px;"><strong>Last updated ' + formatVerifiedDate(brand.lastVerified) + '.</strong> Checked against the source directory on that date.</p>');
  } else {
    lines.push('<p style="margin:0 0 8px;"><strong>Last updated date not recorded for this brand yet.</strong></p>');
  }
  lines.push('Spotted something out of date? <a href="mailto:hello@ahomekind.com?subject=brand%20page%20correction:%20' + encodeURIComponent(brand.name) + '">let me know</a>.');
  lines.push('</div>');
  lines.push('</main>');
  lines.push('');
  lines.push('<div class="newsletter">');
  lines.push('<p class="label3">stay in the loop</p>');
  lines.push('<p class="sub2">occasional updates, brand-check updates and cruelty-free finds - no inbox spam, unsubscribe whenever you like.</p>');
  lines.push('<form class="newsletter-form" id="nf-' + brand.slug + '" action="https://buttondown.com/api/emails/embed-subscribe/ahomekind" method="post" target="_blank" novalidate>');
  lines.push('<input type="hidden" value="1" name="embed">');
  lines.push('<div class="nf-row">');
  lines.push('<label for="nf-email-' + brand.slug + '" class="visually-hidden">Email address</label>');
  lines.push('<input type="email" id="nf-email-' + brand.slug + '" name="email" placeholder="you@example.com" autocomplete="email" required>');
  lines.push('<button type="submit" class="btn">join the list</button>');
  lines.push('</div>');
  lines.push('<label class="nf-consent">');
  lines.push('<input type="checkbox" id="nf-consent-' + brand.slug + '" required>');
  lines.push('<span>I\'d like to receive emails from a home kind. See the <a href="../../privacy.html">privacy policy</a>.</span>');
  lines.push('</label>');
  lines.push('<p class="nf-msg" id="nf-msg-' + brand.slug + '" role="status" aria-live="polite"></p>');
  lines.push('</form>');
  lines.push('</div>');
  lines.push('<footer class="site-footer">a home kind. &middot; est. 2026 &middot; <a href="../../about.html">about</a> &middot; <a href="../../take-action.html">take action</a> &middot; <a href="../../privacy.html">privacy</a> &middot; <a href="https://ko-fi.com/ahomekind" target="_blank" rel="noopener">support a home kind</a></footer>');
  lines.push('<script src="../../js/site.js?v=5"></' + 'script>');
  lines.push('<script src="../../js/newsletter.js"></' + 'script>');
  lines.push('</body>');
  lines.push('</html>');
  lines.push('');

  return lines.join('\n');
}

function buildSitemap(brands) {
  const staticPages = ['', 'about.html', 'learn.html', 'impact.html', 'brand-check.html', 'scan.html', 'shelf.html', 'ingredient-check.html', 'shop.html', 'take-action.html', 'perfume.html'];
  const urls = staticPages.map(function(p){ return SITE_URL + '/' + p; })
    .concat(brands.map(function(b){ return SITE_URL + '/brands/' + b.slug; }));
  const body = urls.map(function(u){ return '  <url><loc>' + u + '</loc></url>'; }).join('\n');
  return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + '\n</urlset>\n';
}

function main() {
  const brands = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
  ALL_BRANDS = brands;
  const slugs = {};
  let created = 0, updated = 0;

  brands.forEach(function(brand) {
    if (!brand.slug) { console.warn('Skipping brand with no slug:', brand.name); return; }
    if (slugs[brand.slug]) { console.warn('Duplicate slug, skipping:', brand.slug); return; }
    slugs[brand.slug] = true;

    const dir = path.join(OUT_DIR, brand.slug);
    const filePath = path.join(dir, 'index.html');
    const existed = fs.existsSync(filePath);

    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(filePath, renderBrandPage(brand), 'utf8');

    if (existed) updated++; else created++;
  });

  fs.writeFileSync(path.join(ROOT, 'sitemap.xml'), buildSitemap(brands), 'utf8');

  console.log('Done. ' + created + ' pages created, ' + updated + ' pages updated, ' + brands.length + ' total brands.');
  console.log('sitemap.xml written with ' + (brands.length + 14) + ' URLs.');
}

main();
