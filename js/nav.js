// Register the service worker site-wide so the app shell (styling, this
// script, icons) loads instantly and offline visits get a proper "you're
// offline" screen instead of a browser error. See sw.js for what this
// does and, just as importantly, what it deliberately doesn't do (the
// scanner itself still needs a live connection).
if ('serviceWorker' in navigator) {
window.addEventListener('load', function(){
navigator.serviceWorker.register('/sw.js').catch(function(){});
});
}

// Small, contextual "buy me a coffee" float. Pages call
// window.ahkShowKofiFloat() only after something genuinely useful has
// just happened (a scan verdict, a brand-check match) -- never on load,
// and never more than once per page. The footer link stays the
// permanent, non-contextual way to find it.
(function(){
var KOFI_DISMISS_KEY = 'ahk-kofi-dismissed';
var shown = false;
window.ahkShowKofiFloat = function(){
if (shown) return;
try { if (localStorage.getItem(KOFI_DISMISS_KEY) === '1') return; } catch(e){}
shown = true;
var run = function(){
var el = document.createElement('a');
el.href = 'https://ko-fi.com/ahomekind';
el.target = '_blank';
el.rel = 'noopener';
el.className = 'kofi-float';
el.setAttribute('aria-label', 'Support a home kind on Ko-fi (opens in a new tab)');
el.innerHTML = '<span class="kofi-float-icon" aria-hidden="true">&#9749;</span><span>buy me a coffee</span><span class="kofi-float-x" role="button" tabindex="0" aria-label="dismiss">&times;</span>';
document.body.appendChild(el);
requestAnimationFrame(function(){ el.classList.add('show'); });
var dismiss = function(e){
e.preventDefault();
e.stopPropagation();
el.classList.remove('show');
setTimeout(function(){ el.remove(); }, 280);
try { localStorage.setItem(KOFI_DISMISS_KEY, '1'); } catch(e2){}
};
var x = el.querySelector('.kofi-float-x');
x.addEventListener('click', dismiss);
x.addEventListener('keydown', function(e){ if(e.key === 'Enter' || e.key === ' '){ dismiss(e); } });
};
if (document.readyState === 'loading') {
document.addEventListener('DOMContentLoaded', run);
} else {
run();
}
};
})();

// Subtle scroll-reveal for the homepage service cards. Progressive
// enhancement only: .home-card has no opacity/transform in the base CSS,
// so if this never runs (no JS, old browser, reduced motion) the cards
// are simply visible the whole time, exactly as before this was added.
document.addEventListener('DOMContentLoaded', function(){
var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
var revealables = document.querySelectorAll('.home-card');
if (!reduceMotion && revealables.length && 'IntersectionObserver' in window) {
var io = new IntersectionObserver(function(entries){
entries.forEach(function(entry){
if (entry.isIntersecting) {
var el = entry.target;
el.classList.remove('reveal-pre');
el.classList.add('reveal-in');
io.unobserve(el);
// Once the reveal transition has played, drop reveal-in too -- otherwise
// its "transform: none" rule ties in specificity with :hover/:active and,
// being declared later in the stylesheet, permanently cancels the tile's
// hover-lift and tap-bounce animations.
window.setTimeout(function(){ el.classList.remove('reveal-in'); }, 500);
}
});
}, { threshold: 0.15 });
revealables.forEach(function(el){
el.classList.add('reveal-pre');
io.observe(el);
});
}
});

// Instagram's/Facebook's in-app browser (the WebView those apps open
// links in, rather than a real browser) routinely blocks or half-supports
// camera access and native file pickers -- exactly the symptoms reported
// on the barcode/shelf scanners. There's nothing the page can do to fix
// that browser; the real fix is opening the link in Safari/Chrome instead,
// so this just tells people how, on the two pages where it actually
// matters. Shown once per browser session (not permanently dismissed)
// since it's genuinely useful information every time someone lands here
// from an in-app link.
document.addEventListener('DOMContentLoaded', function(){
var CAMERA_PAGES = ['/scan.html', '/shelf.html'];
var IG_DISMISS_KEY = 'ahk-ig-banner-dismissed';
function isInAppBrowser(){
var ua = navigator.userAgent || navigator.vendor || '';
return /Instagram|FBAN|FBAV/i.test(ua);
}
function onCameraPage(){
var p = window.location.pathname.replace(/\/$/, '') || '/';
return CAMERA_PAGES.some(function(cp){ return p === cp || p === cp.replace(/\.html$/, ''); });
}
if (onCameraPage() && isInAppBrowser()) {
try { if (sessionStorage.getItem(IG_DISMISS_KEY) === '1') return; } catch(e){}
var banner = document.createElement('div');
banner.className = 'ig-banner';
banner.innerHTML =
'<span class="ig-banner-text"><strong>Camera not opening?</strong> You\'re viewing this inside Instagram\'s browser, which often blocks it. Tap the &bull;&bull;&bull; menu (top right) and choose &ldquo;open in browser&rdquo; for scanning to work.</span>' +
'<button type="button" class="ig-banner-close" aria-label="dismiss">&times;</button>';
document.body.insertBefore(banner, document.body.firstChild);
banner.querySelector('.ig-banner-close').addEventListener('click', function(){
banner.remove();
try { sessionStorage.setItem(IG_DISMISS_KEY, '1'); } catch(e2){}
});
}
});

document.addEventListener('DOMContentLoaded', function(){
var dds = document.querySelectorAll('nav.main-nav .dd');
function setOpen(dd, open){
dd.classList.toggle('open', open);
dd.setAttribute('aria-expanded', open ? 'true' : 'false');
}
dds.forEach(function(dd){
var toggle = function(e){
if(e.target.closest('.dd-m')) return;
e.preventDefault();
var wasOpen = dd.classList.contains('open');
dds.forEach(function(other){ setOpen(other, false); });
if(!wasOpen){ setOpen(dd, true); }
};
dd.addEventListener('click', toggle);
// Enter/Space activate it like a real button, since it's a span with role="button".
dd.addEventListener('keydown', function(e){
if(e.key === 'Enter' || e.key === ' '){ toggle(e); }
});
});
document.addEventListener('click', function(e){
if(!e.target.closest('nav.main-nav .dd')){
dds.forEach(function(dd){ setOpen(dd, false); });
}
});
document.addEventListener('keydown', function(e){
if(e.key === 'Escape'){
dds.forEach(function(dd){ setOpen(dd, false); });
}
});

// App-style bottom nav (mobile only) -- injected here so it applies site-wide
// without editing every page. Uses root-relative paths so it works at any
// folder depth.
// Cloudflare serves clean URLs (e.g. "/scan" instead of "/scan.html"), so the
// live pathname often has no ".html" on it even though our links do. Strip
// ".html"/"index" and any trailing slash from both sides before comparing,
// so active-tab detection works whether or not the extension is present.
function normalizePath(p){
p = p.replace(/index\.html$/, '').replace(/\.html$/, '');
if (p.length > 1) p = p.replace(/\/$/, '');
if (p === '') p = '/';
return p;
}
var current = normalizePath(window.location.pathname);
function isActive(paths){
return paths.some(function(p){ return normalizePath(p) === current; });
}
function bnItem(href, icon, label, key){
var active = key === 'home' ? isActive(['/', '/index.html']) : isActive([href]);
return '<a href="' + href + '" class="bn-item' + (key === 'scan' ? ' bn-scan' : '') + (active ? ' active' : '') + '">' +
'<span class="bn-icon-wrap"><span class="bn-icon">' + icon + '</span></span>' +
'<span class="bn-label">' + label + '</span></a>';
}
var bn = document.createElement('div');
bn.className = 'bottom-nav';
bn.innerHTML =
bnItem('/index.html', '&#8962;', 'Home', 'home') +
bnItem('/scan.html', '&#128247;', 'Scan', 'scan') +
bnItem('/brand-check.html', '&#128269;', 'Check', 'check') +
bnItem('/shop.html', '&#128717;', 'Shop', 'shop') +
'<button type="button" class="bn-item bn-more" id="bn-more-btn">' +
'<span class="bn-icon">&#8942;</span><span class="bn-label">More</span></button>';
document.body.appendChild(bn);

var sheet = document.createElement('div');
sheet.className = 'bn-sheet';
sheet.id = 'bn-sheet';
sheet.setAttribute('role', 'dialog');
sheet.setAttribute('aria-modal', 'true');
sheet.setAttribute('aria-label', 'more pages');
sheet.innerHTML =
'<div class="bn-sheet-inner">' +
'<a href="/shelf.html">scan a shelf</a>' +
'<a href="/start-here.html">start here</a>' +
'<a href="/quiz.html">take the quiz</a>' +
'<a href="/impact.html">your impact</a>' +
'<a href="/what-testing-means.html">what testing means</a>' +
'<a href="/money.html">who gets your money</a>' +
'<a href="/instead-of.html">popular swaps</a>' +
'<a href="/food.html">food &amp; kitchen</a>' +
'<a href="/fashion.html">fashion &amp; accessories</a>' +
'<a href="/journal/">journal</a>' +
'<a href="/about.html">about</a>' +
'<button type="button" class="bn-sheet-close" id="bn-sheet-close">close</button>' +
'</div>';
document.body.appendChild(sheet);

var moreBtn = document.getElementById('bn-more-btn');
var closeBtn = document.getElementById('bn-sheet-close');
moreBtn.setAttribute('aria-haspopup', 'true');
moreBtn.setAttribute('aria-expanded', 'false');
function openSheet(){
sheet.classList.add('open');
document.body.classList.add('bn-sheet-lock');
moreBtn.setAttribute('aria-expanded', 'true');
closeBtn.focus(); // move focus into the sheet, since it behaves like a modal dialog
}
function closeSheet(){
sheet.classList.remove('open');
document.body.classList.remove('bn-sheet-lock');
moreBtn.setAttribute('aria-expanded', 'false');
moreBtn.focus(); // return focus to where it came from
}
moreBtn.addEventListener('click', openSheet);
closeBtn.addEventListener('click', closeSheet);
sheet.addEventListener('click', function(e){ if(e.target === sheet) closeSheet(); });
document.addEventListener('keydown', function(e){
if(e.key === 'Escape' && sheet.classList.contains('open')){ closeSheet(); }
});
});

// Ambient impact counter, in-flow, just above the footer on every page
// except impact.html (which already has the full, dismissible version).
// Same rate/source as js/impact-counter.js: 83 billion land animals
// slaughtered for meat globally in 2022 (UN FAO via Our World in Data),
// spread evenly across the year. This one never overlays the page and
// is never dismissed -- it's meant to be a quiet, constant fact of the
// site's footer, not an interruption.
document.addEventListener('DOMContentLoaded', function(){
var path = window.location.pathname;
if (/impact\.html$/.test(path)) return; // already has the full counter
var footer = document.querySelector('footer.site-footer');
if (!footer) return;
var RATE_PER_SECOND = 83000000000 / (365.25 * 24 * 3600);
var wrap = document.createElement('div');
wrap.className = 'ambient-counter';
wrap.setAttribute('role', 'status');
wrap.setAttribute('aria-label', 'Live estimate of land animals slaughtered for meat worldwide since this page loaded');
wrap.innerHTML =
'<div class="ambient-counter-inner">' +
'<span class="ambient-counter-num" id="ambientCounterNum">0</span>' +
'<p class="ambient-counter-label">land animals killed for meat worldwide, since this page loaded &middot; <a href="/impact.html">see the full picture</a></p>' +
'</div>';
footer.parentNode.insertBefore(wrap, footer);
var numEl = wrap.querySelector('#ambientCounterNum');
var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (reduceMotion) {
// Still an honest, real number -- just not animated: a running count
// for the time an average visitor spends on a page (roughly a minute).
numEl.textContent = Math.floor(60 * RATE_PER_SECOND).toLocaleString();
return;
}
var start = performance.now();
function tick(){
var elapsedSeconds = (performance.now() - start) / 1000;
numEl.textContent = Math.floor(elapsedSeconds * RATE_PER_SECOND).toLocaleString();
requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
});

// Myth vs reality flip cards -- homepage only, built from a container
// div id="mythGrid" left empty in the markup. Click, tap or Enter/Space
// flips a card between the common belief and the fuller truth. Kept as
// plain, sourceable statements -- nothing here is a "gotcha", just the
// more complete version of something a lot of people have heard.
document.addEventListener('DOMContentLoaded', function(){
var grid = document.getElementById('mythGrid');
if (!grid) return;
var MYTHS = [
{
myth: '"Cruelty-free" means a product was never tested on animals, full stop.',
reality: 'Usually it just means the finished product wasn’t tested by that brand. The individual ingredients, or the wider parent company, can still be tested elsewhere, especially if the brand also sells in mainland China, where animal testing on cosmetics can be legally required. That’s why a certification (Leaping Bunny, PETA, Cruelty Free International) matters more than the words on the label.'
},
{
myth: 'Vegan and cruelty-free are basically the same thing.',
reality: 'They’re answering two different questions. Vegan means no animal-derived ingredients, cruelty-free means not tested on animals. A product can be vegan and still tested on animals, or cruelty-free and still contain things like beeswax, lanolin or carmine. Checking one tells you nothing about the other.'
},
{
myth: 'Leather is just a by-product of the meat industry, so it doesn’t really add to the harm.',
reality: 'For cattle it’s more accurately a co-product: the hide is sold alongside the meat and adds to what the animal is worth, which supports the overall economics of slaughter. For some animals, like exotic reptiles or certain cattle raised specifically for premium hides, leather is the primary product and meat is the secondary one.'
},
{
myth: '"Natural" or "organic" on the label means it’s cruelty-free.',
reality: 'Natural and organic describe where the ingredients came from, not whether the finished product or its ingredients were tested on animals, or whether the company sells somewhere that requires it. They’re unrelated claims. The only reliable way to know is a genuine third-party certification.'
},
{
myth: 'If it’s legal to sell here, it can’t have been tested on animals.',
reality: 'The UK and EU ban animal testing on finished cosmetics and most ingredients sold here. But a brand that also sells in a country with its own testing requirements can still commission tests on the same formula for that market, and the UK/EU ban doesn’t stop that happening elsewhere.'
},
{
myth: 'Unless I go fully vegan and cruelty-free overnight, it doesn’t really make a difference.',
reality: 'Every swap is a real, cumulative reduction, not an all-or-nothing switch. Cutting meat a few days a week or swapping a couple of bathroom products both add up over a year, in ways you can actually see for yourself on the impact calculator. Perfection was never the bar.'
}
];
var html = '';
MYTHS.forEach(function(m, i){
html += '<div class="flip-card">' +
'<button type="button" class="flip-card-btn" id="mythCard' + i + '" aria-label="Flip to see the reality">' +
'<div class="flip-card-inner">' +
'<div class="flip-front"><p class="flip-label">the myth</p><p class="flip-text">' + m.myth + '</p><p class="flip-hint">tap to see the reality &rarr;</p></div>' +
'<div class="flip-back"><p class="flip-label">the reality</p><p class="flip-text">' + m.reality + '</p><p class="flip-hint">tap to flip back</p></div>' +
'</div>' +
'</button>' +
'</div>';
});
grid.innerHTML = html;
grid.querySelectorAll('.flip-card').forEach(function(card){
var btn = card.querySelector('.flip-card-btn');
btn.addEventListener('click', function(){ card.classList.toggle('flipped'); });
});
});

// "One small swap" -- a single instead-of/try pair on the homepage,
// picked from the day of the year so it's stable for the whole visit
// and changes daily rather than reshuffling on every reload. Pairs are
// the same ones already verified on instead-of.html and brand-check,
// nothing new is claimed here.
document.addEventListener('DOMContentLoaded', function(){
var el = document.getElementById('swapOfDay');
if (!el) return;
var SWAPS = [
{ insteadName: 'Head &amp; Shoulders', insteadHref: '/brands/head-and-shoulders/index.html', insteadNote: 'Owned by Procter &amp; Gamble, who test where legally required.', tryName: 'Noughty', tryHref: '/brands/noughty/index.html', tryNote: 'Leaping Bunny certified, vegan, independent.' },
{ insteadName: 'Pantene', insteadHref: '/brands/pantene/index.html', insteadNote: 'Owned by Procter &amp; Gamble, who test where legally required.', tryName: 'Umberto Giannini', tryHref: '/brands/umberto-giannini/index.html', tryNote: 'PETA certified cruelty-free, 100% vegan.' },
{ insteadName: "L'Oréal", insteadHref: '/brands/l-oreal/index.html', insteadNote: 'The world’s largest cosmetics company, sells into mainland China where testing can be required.', tryName: 'Faith in Nature', tryHref: '/brands/faith-in-nature/index.html', tryNote: 'UK, Leaping Bunny certified, budget-friendly.' },
{ insteadName: 'Maybelline', insteadHref: '/brands/maybelline/index.html', insteadNote: 'Owned by L’Oréal, who sell into markets requiring animal testing.', tryName: 'e.l.f. Cosmetics', tryHref: '/brands/e-l-f-cosmetics/index.html', tryNote: 'Independently owned, PETA and Vegan Society certified.' },
{ insteadName: 'Vaseline', insteadHref: '/brands/vaseline/index.html', insteadNote: 'Owned by Unilever, who sell into markets requiring animal testing.', tryName: 'Superdrug own-brand lip balm', tryHref: '/brands/superdrug-own-brand-wider-range/index.html', tryNote: 'Leaping Bunny approved, and an easy like-for-like swap - in almost any Superdrug store, or on superdrug.com if you’d rather order it in.' },
{ insteadName: 'Nivea', insteadHref: '/brands/nivea/index.html', insteadNote: 'Owned by Beiersdorf, who test where required by law.', tryName: 'Dr Organic', tryHref: '/brands/dr-organic/index.html', tryNote: 'Certified cruelty-free (Leaping Bunny / Cruelty Free International).' },
{ insteadName: 'CeraVe', insteadHref: '/brands/cerave/index.html', insteadNote: 'Owned by L’Oréal, sold in mainland China where testing can be required, and not fully vegan either.', tryName: 'BYOMA', tryHref: '/brands/byoma/index.html', tryNote: 'UK, Leaping Bunny certified – similar ceramide-focused formulas.' },
{ insteadName: 'Olay', insteadHref: '/brands/olay/index.html', insteadNote: 'Owned by Procter &amp; Gamble, who sell into markets requiring animal testing.', tryName: 'Sukin', tryHref: '/brands/sukin/index.html', tryNote: 'Leaping Bunny certified and 100% vegan.' },
{ insteadName: 'Axe', insteadHref: '/brands/axe/index.html', insteadNote: 'Owned by Unilever, who sell into markets requiring animal testing.', tryName: 'The Natural Deodorant Co', tryHref: '/brands/the-natural-deodorant-co/index.html', tryNote: 'Cruelty Free International certified, 100% vegan, independent UK brand.' },
{ insteadName: 'Sure', insteadHref: '/brands/sure/index.html', insteadNote: 'Owned by Unilever, who sell into markets requiring animal testing.', tryName: 'Salt of the Earth', tryHref: '/brands/salt-of-the-earth/index.html', tryNote: 'Vegan Society and Leaping Bunny approved, sold in Holland &amp; Barrett and Boots.' },
{ insteadName: 'Always', insteadHref: '/brands/always/index.html', insteadNote: 'Owned by Procter &amp; Gamble, who test where legally required.', tryName: 'Natracare', tryHref: '/brands/natracare/index.html', tryNote: 'Vegetarian Society Vegan Approved and PETA Business Friend.' },
{ insteadName: 'Tampax', insteadHref: '/brands/tampax/index.html', insteadNote: 'Owned by Procter &amp; Gamble, who test where legally required.', tryName: 'TOTM', tryHref: '/brands/totm/index.html', tryNote: 'PETA certified cruelty-free and vegan organic period care, B Corp certified.' },
{ insteadName: 'Colgate', insteadHref: '/brands/colgate/index.html', insteadNote: 'Parent company Colgate-Palmolive sells in mainland China and hasn’t adopted a full end to animal testing globally.', tryName: 'Kingfisher', tryHref: '/brands/kingfisher/index.html', tryNote: 'Cruelty-free and BUAV/Vegan Society certified in the UK, independent brand.' },
{ insteadName: 'Fairy', insteadHref: '/brands/fairy/index.html', insteadNote: 'Owned by Procter &amp; Gamble, who test where legally required.', tryName: 'Bio-D', tryHref: '/brands/bio-d/index.html', tryNote: 'Vegan Society and Cruelty Free International certified.' },
{ insteadName: 'Persil', insteadHref: '/brands/persil/index.html', insteadNote: 'Owned by Unilever, who sell into markets requiring animal testing.', tryName: 'Smol', tryHref: '/brands/smol/index.html', tryNote: 'Confirms no animal testing, listed on PETA’s database.' },
{ insteadName: 'Domestos', insteadHref: '/brands/domestos/index.html', insteadNote: 'Owned by Unilever, who sell into markets requiring animal testing.', tryName: 'Zoflora', tryHref: '/brands/zoflora/index.html', tryNote: 'Confirms no animal testing.' }
];
var now = new Date();
var startOfYear = new Date(now.getFullYear(), 0, 0);
var dayOfYear = Math.floor((now - startOfYear) / 86400000);
var pick = SWAPS[dayOfYear % SWAPS.length];
el.innerHTML =
'<p class="swap-of-day-kicker" style="color:#4d6b4f; font-size:10.5px; letter-spacing:3px; text-transform:uppercase; margin-bottom:12px;">one small swap</p>' +
'<h2 class="myth-heading" style="font-size:24px;">today’s swap, made for you</h2>' +
'<p class="myth-sub" style="margin-bottom:0;">A different genuine, certified alternative each day, straight from the brand check &mdash; no need to change everything at once.</p>' +
'<div class="swap-of-day-card">' +
'<div class="swap-of-day-row">' +
'<div class="swap-of-day-side"><p class="swap-label instead">instead of</p><p class="swap-name"><a href="' + pick.insteadHref + '">' + pick.insteadName + '</a></p><p class="swap-note">' + pick.insteadNote + '</p></div>' +
'<span class="swap-of-day-arrow" aria-hidden="true">&#8594;</span>' +
'<div class="swap-of-day-side"><p class="swap-label try">try</p><p class="swap-name"><a href="' + pick.tryHref + '">' + pick.tryName + '</a></p><p class="swap-note">' + pick.tryNote + '</p></div>' +
'</div>' +
'</div>' +
'<p style="margin-top:22px;"><a href="/instead-of.html" class="btn">see more swaps</a></p>';
});
