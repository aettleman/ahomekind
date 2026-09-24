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
  good: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 18c-1-7 3-12 13-13 .5 9-4 14-11 13.5"/><path d="M6 18c2-3 5-6 8-7.5"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>',
  warn: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4 2.8 19.5h18.4L12 4Z"/><path d="M12 10v4.2M12 17.2v.1"/></svg>',
  bad: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/></svg>',
  unverified: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.2 9a3 3 0 1 1 4.3 2.7c-1 .5-1.5 1.2-1.5 2.3M12 17.5v.1"/></svg>'
};
// One plain-English headline per tier, for the big verdict card -- the
// same four answers as the homepage's "four possible answers" grid, plus
// the fifth unverified case.
const VERDICT_HEADLINE = {
  good: 'Cruelty-free and vegan.',
  check: "Cruelty-free. Vegan status varies by product.",
  warn: "Cruelty-free, but its owner isn't.",
  bad: 'Tests on animals, or sells where it\'s required.',
  unverified: 'Not certified either way, yet.'
};

const STAMP_TEXT = {
  good: '<b>CF +</b>vegan', check: '<b>cruelty</b>free', warn: '<b>owner</b>isn\'t', bad: '<b>tested</b>', unverified: '<b>not</b>certified'
};
const TIER_SHORT = { good: 'CF + vegan', check: 'Cruelty-free', warn: 'Owner isn\'t', bad: 'Tested', unverified: 'Not certified' };
const TIER_WASH = { good: '#DCE6D6', check: '#DCE6D6', warn: '#FBE3D3', bad: '#F5D3D6', unverified: '#EFDDD3' };
const PK_COLOURS = ['#6E9B5B', '#F2C94C', '#F6C9B8', '#D9B98A', '#8FB3D9', '#E8A57A', '#B9A3D0', '#9DBB98', '#7C9A78', '#C9546A'];
function norm(t) { return String(t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]/g, ''); }
function hashOf(t) { let h = 0; for (let i = 0; i < t.length; i++) h = (h * 31 + t.charCodeAt(i)) >>> 0; return h; }
function pkHtml(brand) {
  const cat = (brand.category || [])[0] || '';
  const shape = cat === 'skincare' ? 'jar' : cat === 'makeup-beauty' ? 'tube' : cat === 'body-shower' ? 'pump'
    : (cat === 'household-cleaning' || cat === 'laundry') ? 'spray' : cat === 'dental' ? 'tube' : 'bottle';
  const h = hashOf(brand.slug);
  const col = PK_COLOURS[h % PK_COLOURS.length];
  return '<div class="pk ' + shape + '" style="--c:' + col + ';--cap:#3A1F3D"><i></i></div>';
}
function certLine(brand) {
  const n = String(brand.note || '').toLowerCase();
  const out = [];
  if (brand.tier === 'bad') out.push('Tests, or sells where required');
  else {
    if (/leaping bunny/.test(n)) out.push('Leaping Bunny');
    else if (/cruelty free international/.test(n)) out.push('Cruelty Free International');
    if (/\bpeta\b/.test(n) && !/company that tests/.test(n)) out.push('PETA');
    if (/vegan society/.test(n)) out.push('Vegan Society');
  }
  let line = out.length ? (out.length === 1 && brand.tier !== 'bad' ? out[0] + ' certified' : out.join(' &middot; ')) : TIER_SHORT[brand.tier] || '';
  if (!brand.parentCompany && brand.tier !== 'bad' && brand.tier !== 'unverified') line += ' &middot; Independent';
  if (brand.price) line += ' &middot; ' + escapeHtml(brand.price);
  return line;
}
function stampSpan(tier, size) {
  const t = TIER_META[tier] ? tier : 'unverified';
  return '<span class="ahk-stamp tier-' + t + '"' + (size ? ' style="width:' + size + 'px;height:' + size + 'px"' : '') + '>' + (STAMP_ICONS[t] || STAMP_ICONS.unverified) + '</span>';
}
function buildOwnershipChain(brand, allBrands) {
  if (!brand.parentCompany) return '';
  const pn = norm(brand.parentCompany);
  const family = allBrands.filter(function(b){ return norm(b.parentCompany) === pn; });
  const parentRec = allBrands.find(function(b){ return norm(b.name) === pn; });
  const parentTier = parentRec ? parentRec.tier : (brand.tier === 'warn' || brand.tier === 'bad' ? 'bad' : null);
  let html = '<div class="chain">';
  html += '<p class="chain-kick">who owns who</p>';
  html += '<div class="chain-node">' + stampSpan(brand.tier, 34) + '<b>' + escapeHtml(brand.name) + '</b><span>' + (TIER_SHORT[brand.tier] || '') + '</span></div>';
  html += '<div class="chain-link">owned by</div>';
  const inner = (parentTier ? stampSpan(parentTier, 34) : '<span class="chain-dot"></span>') + '<b>' + escapeHtml(brand.parentCompany) + '</b><span>' + family.length + ' brand' + (family.length === 1 ? '' : 's') + ' on here</span>';
  html += parentRec ? '<a class="chain-node" href="../' + parentRec.slug + '/">' + inner + '</a>' : '<div class="chain-node">' + inner + '</div>';
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
  // Prefer brands with a known price and an independent owner: the kind of
  // swap someone can actually pick up in a UK shop.
  pool.sort(function(x, y){ return ((y.price ? 2 : 0) + (y.parentCompany ? 0 : 1) + (y.tier === 'good' ? 1 : 0)) - ((x.price ? 2 : 0) + (x.parentCompany ? 0 : 1) + (x.tier === 'good' ? 1 : 0)); });
  const top = pool.slice(0, 12);
  if (!top.length) return '';
  const h = hashOf(brand.slug);
  const picks = [top[h % top.length]];
  if (top.length > 1) { let j = (h + 5) % top.length; if (top[j] === picks[0]) j = (j + 1) % top.length; picks.push(top[j]); }
  let html = '<p class="swaps-kick">kinder swaps</p><div class="swp">';
  picks.forEach(function(p){
    html += '<a href="../' + p.slug + '/"><div class="k-arch-box" style="background:' + TIER_WASH[p.tier] + '">' + pkHtml(p) + '</div>';
    html += '<b>' + escapeHtml(p.name) + '</b><span>' + (p.parentCompany ? TIER_SHORT[p.tier] : 'Independent') + (p.price ? ' &middot; ' + escapeHtml(p.price) : '') + '</span></a>';
  });
  html += '</div>';
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
  lines.push('<meta property="og:image" content="' + SITE_URL + '/images/' + tier.shareImage + '?v=2">');
  lines.push('<meta property="og:image:alt" content="' + escapeHtml(brand.name) + ' on a home kind">');
  lines.push('<meta property="og:site_name" content="a home kind">');
  lines.push('<meta name="twitter:card" content="summary_large_image">');
  lines.push('<script type="application/ld+json">' + JSON.stringify({
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + '/' },
      { "@type": "ListItem", "position": 2, "name": "Check a brand", "item": SITE_URL + '/brand-check.html' },
      { "@type": "ListItem", "position": 3, "name": brand.name, "item": canonical }
    ]
  }) + '</script>');
  lines.push('<link href="https://fonts.googleapis.com/css2?family=Gloock&family=Hanken+Grotesk:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Caveat:wght@500;700&display=swap" rel="stylesheet">');
  lines.push('<link rel="stylesheet" href="../../css/app.css?v=6">');
  lines.push('<link rel="manifest" href="../../manifest.json?v=2">');
  lines.push('<meta name="theme-color" content="#3A1F3D">');
  lines.push('<link rel="icon" href="../../favicon.ico?v=2" sizes="any"><link rel="icon" type="image/svg+xml" href="../../icons/favicon.svg">');
  lines.push('<link rel="icon" type="image/png" sizes="32x32" href="../../icons/favicon-32-v2.png">');
  lines.push('<link rel="icon" type="image/png" sizes="16x16" href="../../icons/favicon-16-v2.png">');
  lines.push('<link rel="apple-touch-icon" href="../../icons/apple-touch-icon-v2.png">');
  lines.push('<meta name="apple-mobile-web-app-capable" content="yes">');
  lines.push('<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">');
  lines.push('<meta name="apple-mobile-web-app-title" content="A Home Kind">');
  lines.push('<style>.card.bad { border-color:#C9546A; background:#F5D3D6; } .rating.bad { color:#A8324E; }</style>');
  lines.push('</head>');
  lines.push('<body>');
  lines.push('<a href="#main" class="skip-link">skip to content</a>');
  lines.push('<header class="site-header">');
  lines.push('<div class="wrap">');
  lines.push('<a href="/" class="logo" aria-label="a home kind, home">');
  lines.push('<span>a home kind</span>');
  lines.push('</a>');
  lines.push('<nav class="main-nav">\n<a href="/brand-check.html">Check</a>\n<a href="/learn.html">Learn</a>\n<a href="/impact.html">Impact</a>\n<a href="/shop.html">Shop</a>\n<a href="/take-action.html">Take action</a>\n<a href="/scan.html" class="nav-scan-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M7 8v8M10 8v8M13.5 8v8M17 8v8"/></svg>Scan a product</a>\n</nav>');
  lines.push('</div>');
  lines.push('</header>');
  lines.push('');
  lines.push('<main class="page-shell k-page k-brand" id="main">');
  lines.push('<div class="bnav"><a class="ib" href="../../brand-check.html" id="ahkBackLink" aria-label="Back"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m14.5 6-6 6 6 6"/></svg></a><span class="k-kick bnav-k" id="bnavKick">brand check</span><button type="button" class="ib" id="bpShare" aria-label="Share this brand"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3.5v11M8 7.5l4-4 4 4"/><path d="M6 11.5H5v8.5h14v-8.5h-1"/></svg></button></div>');
  lines.push('<script>(function(){var a=document.getElementById("ahkBackLink");var r=document.referrer||"";if(/scan|ingredient-check|shelf/.test(r)){document.getElementById("bnavKick").textContent="scan result";}if(r.indexOf(location.origin)===0&&r!==location.href){a.addEventListener("click",function(e){e.preventDefault();history.back();});}})();</' + 'script>');
  const catLabel = (brand.category && brand.category.length) ? brand.category.map(function(c){ return escapeHtml(c.replace(/-/g, ' ').replace('makeup beauty', 'makeup').replace('household cleaning', 'household')); }).join(' &middot; ') : '';
  lines.push('<div class="k-bp-grid"><div class="k-bp-l">');
  lines.push('<div class="bp"><div class="k-arch-box" style="background:' + TIER_WASH[brand.tier === 'unknown' ? 'unverified' : brand.tier] + '">' + pkHtml(brand) + '</div><div><p class="k-kick bp-k">' + catLabel + '</p><h1>' + escapeHtml(brand.name) + '</h1><p>' + certLine(brand) + '</p></div></div>');
  lines.push('<div class="vcard tier-' + tier.className + '"><div class="bigst"><span>' + (STAMP_TEXT[brand.tier] || STAMP_TEXT.unverified) + '</span></div>');
  lines.push('<h2>' + (VERDICT_HEADLINE[brand.tier] || VERDICT_HEADLINE.unverified) + '</h2>');
  lines.push('<p>' + escapeHtml(brand.note) + '</p>');
  if (parentTestFlag) lines.push(parentTestFlag);
  lines.push('</div>');
  lines.push(veganButNotCrueltyFreeWarning);
  lines.push('<dl class="k-facts"><div><dt>Vegan</dt><i></i><dd>' + veganLine + '</dd></div><div><dt>Owner</dt><i></i><dd>' + (brand.parentCompany ? escapeHtml(brand.parentCompany) : 'Independent') + '</dd></div>' + (brand.price ? '<div><dt>Price</dt><i></i><dd>' + escapeHtml(brand.price) + '</dd></div>' : '') + '</dl>');
  lines.push('</div><div class="k-bp-r">');
  lines.push(buildOwnershipChain(brand, ALL_BRANDS));
  lines.push(buildSwaps(brand, ALL_BRANDS));
  if (brand.products && brand.products.length) lines.push('<div class="k-sec">' + renderSection('products checked', brand.products, '') + '</div>');
  if (brand.links && brand.links.length) lines.push('<div class="k-sec">' + renderLinks(brand.links) + '</div>');
  lines.push('<div class="signed"><div><span class="k-kick" style="display:block">checked by</span><span class="ahk-hand">Ash</span></div><button type="button" class="k-btn-p" id="bpSave" data-slug="' + brand.slug + '" data-name="' + escapeHtml(brand.name) + '"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M6.5 4h11v16.5L12 16.5l-5.5 4V4Z"/></svg><span>Save</span></button></div>');
  lines.push('<p class="k-fn">' + (brand.lastVerified ? 'Last updated ' + formatVerifiedDate(brand.lastVerified) + ', checked against the source directory that day. ' : '') + 'Spotted something out of date? <a href="mailto:hello@ahomekind.com?subject=brand%20page%20correction:%20' + encodeURIComponent(brand.name) + '">Let me know</a>.</p>');
  lines.push('</div></div>');
  lines.push('<script>(function(){var b=document.getElementById("bpSave"),k="ahk-saved-brands";function get(){try{return JSON.parse(localStorage.getItem(k)||"[]")}catch(e){return[]}}function paint(){var on=get().some(function(x){return x.slug===b.dataset.slug});b.classList.toggle("is-saved",on);b.querySelector("span").textContent=on?"Saved":"Save";}b.addEventListener("click",function(){var l=get().filter(function(x){return x.slug!==b.dataset.slug});if(!b.classList.contains("is-saved"))l.unshift({slug:b.dataset.slug,name:b.dataset.name});try{localStorage.setItem(k,JSON.stringify(l.slice(0,50)))}catch(e){}paint();});paint();var s=document.getElementById("bpShare");s.addEventListener("click",function(){var d={title:document.title,url:location.href};if(navigator.share){navigator.share(d).catch(function(){})}else if(navigator.clipboard){navigator.clipboard.writeText(location.href);s.classList.add("is-copied");setTimeout(function(){s.classList.remove("is-copied")},1500);}});})();</' + 'script>');
  lines.push('</main>');
  lines.push('');
  lines.push('<footer class="site-footer">a home kind. &middot; est. 2026 &middot; <a href="../../about.html">about</a> &middot; <a href="../../take-action.html">take action</a> &middot; <a href="../../privacy.html">privacy</a> &middot; <a href="https://ko-fi.com/ahomekind" target="_blank" rel="noopener">support a home kind</a></footer>');
  lines.push('<script src="../../js/site.js?v=6"></' + 'script>');
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
