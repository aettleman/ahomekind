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
'<a href="/quiz.html">take the quiz</a>' +
'<a href="/journal/">journal</a>' +
'<a href="/what-testing-means.html">what testing means</a>' +
'<a href="/money.html">who gets your money</a>' +
'<a href="/impact.html">your impact</a>' +
'<a href="/start-here.html">start here</a>' +
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
