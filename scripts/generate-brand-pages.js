92
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
  good:  { emoji: '&#127807;', label: 'fully cruelty-free &amp; vegan', className: '', ratingClass: '' },
  check: { emoji: '&#128048;', label: 'cruelty-free, check vegan status per product', className: '', ratingClass: 'neutral' },
  warn:  { emoji: '&#9888;&#65039;', label: 'cruelty-free itself, parent company isn\'t', className: 'warn', ratingClass: 'warn' },
  bad:   { emoji: '&#10060;', label: 'tested on animals', className: 'bad', ratingClass: 'bad' },
  unknown: { emoji: '&#10067;', label: 'status not known yet', className: '', ratingClass: 'neutral' }
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
  return 'Is ' + brand.name + ' Cruelty-Free? \u2014 a home kind';
}

function pageDescription(brand) {
  return escapeHtml(brand.note || ('Find out whether ' + brand.name + ' is cruelty-free and vegan.'));
}

function renderSection(title, items, emptyNote) {
  if (!items || items.length === 0) {
    return '<p class="section-label">' + title + '</p>\n<p style="color:#7a7561; font-size:13.5px;">' + emptyNote + '</p>';
  }
  const rows = items.map(function(i){ return '<li>' + escapeHtml(i) + '</li>'; }).join('\n');
  return '<p class="section-label">' + title + '</p>\n<ul style="margin:0 0 20px 20px; font-size:14px; line-height:1.9;">\n' + rows + '\n</ul>';
}

function renderLinks(links) {
  if (!links || links.length === 0) return '';
  const rows = links.map(function(l){ return '<a href="' + escapeHtml(l.url) + '" target="_blank" rel="noopener">' + escapeHtml(l.label || l.url) + '</a>'; }).join(' &middot; ');
  return '<p class="section-label">sources &amp; links</p>\n<p style="font-size:13.5px;">' + rows + '</p>';
}

function renderBrandPage(brand) {
  const tier = TIER_META[brand.tier] || TIER_META.check;
  const title = pageTitle(brand);
  const description = pageDescription(brand);
  const canonical = SITE_URL + '/brands/' + brand.slug;
  const veganLine = brand.vegan === 'full' ? '100% vegan'
    : brand.vegan === 'partial' ? 'vegan status varies by product'
    : 'vegan status not yet confirmed';
  const parentLine = brand.parentCompany ? ('<p><strong>parent company:</strong> ' + escapeHtml(brand.parentCompany) + '</p>') : '';
  const veganButNotCrueltyFreeWarning = (brand.tier === 'bad' && (brand.vegan === 'partial' || brand.vegan === 'full'))
    ? '<div style="margin-top:16px; padding:14px 16px; background:#f3e2df; border:0.5px solid #d9b9b3; border-radius:8px; font-size:13.5px; color:#7a4640; line-height:1.7;"><strong>a vegan label here doesn\'t make it cruelty-free.</strong> ' + escapeHtml(brand.name) + ' isn\'t on the cruelty-free list because of the company\'s wider testing policy, not because of what\'s in any one product. Buying a vegan-labelled item from them still puts money behind a company that tests on animals elsewhere in its business.</div>'
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
  lines.push('<meta name="twitter:card" content="summary">');
  lines.push('<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500&family=Karla:wght@400;500&display=swap" rel="stylesheet">');
  lines.push('<link rel="stylesheet" href="../../css/style.css?v=20260908">');
  lines.push('<link rel="manifest" href="../../manifest.json">');
  lines.push('<meta name="theme-color" content="#3d4a3a">');
  lines.push('<link rel="icon" href="../../favicon.ico" sizes="any">');
  lines.push('<link rel="icon" type="image/png" sizes="32x32" href="../../icons/favicon-32.png">');
  lines.push('<link rel="icon" type="image/png" sizes="16x16" href="../../icons/favicon-16.png">');
  lines.push('<link rel="apple-touch-icon" href="../../icons/apple-touch-icon.png">');
  lines.push('<meta name="apple-mobile-web-app-capable" content="yes">');
  lines.push('<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">');
  lines.push('<meta name="apple-mobile-web-app-title" content="A Home Kind">');
  lines.push('<style>');
  lines.push('.card.bad { border-color:#a5453d; background:#f3e2df; }');
  lines.push('.rating.bad { color:#8a332c; }');
  lines.push('</style>');
  lines.push('</head>');
  lines.push('<body>');
  lines.push('<a href="#main" class="skip-link">skip to content</a>');
  lines.push('<header class="site-header">');
  lines.push('<div class="wrap">');
  lines.push('<a href="../../index.html" class="logo">');
  lines.push('<img src="../../icons/logo-mark.png" alt="" width="30" height="30" style="display:block;">');
  lines.push('<span>a home kind</span>');
  lines.push('</a>');
  lines.push('<nav class="main-nav">');
  lines.push('<a href="../../index.html">home</a>');
  lines.push('<a href="../../scan.html">scan</a>');
  lines.push('<a href="../../brand-check.html">check</a>');
  lines.push('<a href="../../shop.html">shop</a>');
  lines.push('<a href="../../start-here.html">start here</a>');
  lines.push('<span class="dd" tabindex="0" role="button" aria-haspopup="true" aria-expanded="false">explore more<span class="caret">&#9660;</span>');
  lines.push('<span class="dd-m">');
  lines.push('<a href="../../quiz.html">take the quiz</a>');
  lines.push('<a href="../../shelf.html">scan a shelf</a>');
  lines.push('<a href="../../journal/">journal</a>');
  lines.push('<a href="../../what-testing-means.html">what testing means</a>');
  lines.push('<a href="../../money.html">who gets your money</a>');
  lines.push('<a href="../../impact.html">your impact</a>');
  lines.push('<a href="../../about.html">about</a>');
  lines.push('</span></span>');
  lines.push('</nav>');
  lines.push('</div>');
  lines.push('</header>');
  lines.push('');
  lines.push('<main class="wrap" id="main">');
  lines.push('<p style="font-size:12px; margin-top:24px;"><a href="../../brand-check.html">&larr; back to brand check</a></p>');
  lines.push('');
  const priceBadge = brand.price ? ('<span style="display:inline-block; margin-left:10px; padding:2px 9px; background:#e6d4a8; border-radius:12px; font-size:12px; color:#3d4a3a; vertical-align:middle;">' + escapeHtml(brand.price) + '</span>') : '';

  lines.push('<div class="card ' + tier.className + '" style="margin-top:16px;">');
  lines.push('<p class="rating ' + tier.ratingClass + '">' + tier.emoji + ' ' + tier.label + priceBadge + '</p>');
  lines.push('<h1 style="font-size:26px; margin:6px 0 14px;">' + escapeHtml(brand.name) + '</h1>');
  lines.push('<p style="font-size:15px; line-height:1.8;">' + escapeHtml(brand.note) + '</p>');
  lines.push('</div>');
  lines.push('');
  lines.push('<div style="margin-top:24px; display:flex; gap:24px; flex-wrap:wrap; font-size:13.5px; color:#5c5c4f;">');
  lines.push('<p><strong>vegan status:</strong> ' + veganLine + '</p>');
  lines.push(parentLine);
  lines.push('</div>');
  lines.push(veganButNotCrueltyFreeWarning);
  lines.push('');
  lines.push('<div style="margin-top:24px;">');
  lines.push(renderLinks(brand.links));
  lines.push('</div>');
  lines.push('');

  lines.push('<div style="margin-top:32px;">');
  lines.push(renderSection('products checked', brand.products, 'I haven\'t listed specific products for ' + escapeHtml(brand.name) + ' yet &mdash; check back soon.'));
  lines.push('</div>');
  lines.push('');

  if (brand.tier !== 'good') {
  lines.push('<div style="margin-top:24px;">');
    lines.push(renderSection('cruelty-free alternatives', brand.alternatives, 'I\'m still building out alternatives for this brand.'));
    lines.push('</div>');
    lines.push('');
  }

  
  lines.push('<div style="margin-top:36px; padding:18px 20px; background:#ece5d5; border:0.5px solid #cfc4a9; border-radius:10px; font-size:13px; color:#7a7561;">');
  lines.push('Spotted something out of date? <a href="mailto:hello@ahomekind.com?subject=brand%20page%20correction:%20' + encodeURIComponent(brand.name) + '">let me know</a>.');
  lines.push('</div>');
  lines.push('</main>');
  lines.push('');
  lines.push('<div class="newsletter">');
  lines.push('<p class="label3">stay in the loop</p>');
  lines.push('<p class="sub2">occasional updates, new journal posts, brand-check updates and cruelty-free finds &mdash; no inbox spam, unsubscribe whenever you like.</p>');
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
  lines.push('<footer class="site-footer">a home kind is the right kind &middot; est. 2026 &middot; <a href="../../privacy.html">privacy</a> &middot; <a href="https://ko-fi.com/ahomekind" target="_blank" rel="noopener">support a home kind</a></footer>');
  lines.push('<script src="../../js/nav.js?v=20260909"></' + 'script>');
  lines.push('<script src="../../js/newsletter.js"></' + 'script>');
  lines.push('</body>');
  lines.push('</html>');
  lines.push('');

  return lines.join('\n');
}

function buildSitemap(brands) {
  const staticPages = ['', 'about.html', 'start-here.html', 'what-testing-means.html', 'money.html', 'impact.html', 'brand-check.html', 'scan.html', 'shelf.html', 'quiz.html', 'shop.html', 'journal/'];
  const urls = staticPages.map(function(p){ return SITE_URL + '/' + p; })
    .concat(brands.map(function(b){ return SITE_URL + '/brands/' + b.slug; }));
  const body = urls.map(function(u){ return '  <url><loc>' + u + '</loc></url>'; }).join('\n');
  return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + '\n</urlset>\n';
}

function main() {
  const brands = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
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
  console.log('sitemap.xml written with ' + (brands.length + 12) + ' URLs.');
}

main();
