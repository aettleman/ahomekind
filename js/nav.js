// Site analytics (PostHog) -- page views + custom "scan completed" events.
// Cookie-light, EU-hosted. Wrapped in try/catch so an ad-blocker or an
// analytics outage never breaks the site itself.
!function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.uploaded_event_queue=t.uploaded_event_queue||[],t.uploaded_event_queue.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSurveysLoaded onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
try {
posthog.init('phc_qAqieswX6Zj78X7HuqkLuB87Ts9sMfTFvV95QrAH6vQt', {
api_host: 'https://eu.i.posthog.com',
person_profiles: 'identified_only'
});
} catch(e) {}

// Inline "back to X" link -- replaces an earlier floating circular back
// button, which sat top-left and ended up covering the site logo. This
// is plain text at the top of the page content instead: forest green,
// small arrow, reads "back to brand check" / "back to home" / etc when
// we can tell where the visit came from (via document.referrer), or
// just "back" when we can't (a bookmark, a fresh tab, a link from
// Instagram) -- both cases use real browser history so it always goes
// to wherever you actually were, falling back to the homepage link only
// when there's no usable history at all. Skipped on the homepage
// itself (nothing useful to go "back" to there) and skipped wherever a
// page already has its own hand-written version of this same link
// (every brands/*/ page), matched by the shared .ahk-back-link class.
(function(){
var path = location.pathname;
var isHome = path === '/' || /\/index\.html$/.test(path) || path === '/ahomekind' || path === '';
if(isHome) return;

var PAGE_LABELS = {
'index.html': 'home',
'brand-check.html': 'brand check',
'scan.html': 'scan',
'shelf.html': 'shelf scan',
'ingredient-check.html': 'ingredient check',
'shop.html': 'shop',
'learn.html': 'learn',
'quiz.html': 'quiz',
'impact.html': 'your impact',
'my-swaps.html': 'my swaps',
'brand-watch.html': "what's changed",
'swap-guide.html': 'swap guide',
'food.html': 'food & kitchen',
'fashion.html': 'fashion & accessories',
'about.html': 'about'
};

function labelFromReferrer(){
if(!document.referrer || document.referrer.indexOf(location.origin) !== 0) return null;
var refPath = '';
try { refPath = new URL(document.referrer).pathname; } catch(e){ return null; }
if(refPath === location.pathname) return null;
if(refPath === '/' || /\/index\.html$/.test(refPath)) return PAGE_LABELS['index.html'];
if(/\/journal\/?$/.test(refPath) || /\/journal\/index\.html$/.test(refPath)) return 'journal';
if(/\/journal\//.test(refPath)) return 'journal';
if(/\/brands\//.test(refPath)) return 'brand check';
var file = refPath.split('/').filter(Boolean).pop();
return PAGE_LABELS[file] || null;
}

window.addEventListener('DOMContentLoaded', function(){
if(document.querySelector('.ahk-back-link')) return;
var main = document.getElementById('main');
if(!main) return;
var label = labelFromReferrer();
var p = document.createElement('p');
p.className = 'ahk-back-link';
var a = document.createElement('a');
a.href = '#';
a.innerHTML = '&larr; ' + (label ? ('back to ' + label) : 'back');
a.addEventListener('click', function(e){
e.preventDefault();
var cameFromSite = document.referrer && document.referrer.indexOf(location.origin) === 0;
if(cameFromSite && history.length > 1){ history.back(); }
else { location.href = location.origin + '/index.html'; }
});
p.appendChild(a);
main.insertBefore(p, main.firstChild);
});
})();

// Floating share button -- top-right mirror of the back button, shown
// on every page including the homepage. Matters most in the installed
// home-screen app, which has no browser chrome and so no address bar
// to copy a link from otherwise. Uses the device's real share sheet
// (AirDrop, Messages, Instagram, etc) where the browser supports it,
// and falls back to copying the link with a small toast confirming it
// worked, for the handful of browsers (mainly desktop) that don't.
(function(){
window.addEventListener('DOMContentLoaded', function(){
var btn = document.createElement('button');
btn.type = 'button';
btn.className = 'ahk-share-btn';
btn.setAttribute('aria-label', 'Share this page');
btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="18" cy="5" r="3" stroke="currentColor" stroke-width="1.8"/><circle cx="6" cy="12" r="3" stroke="currentColor" stroke-width="1.8"/><circle cx="18" cy="19" r="3" stroke="currentColor" stroke-width="1.8"/><line x1="8.6" y1="10.6" x2="15.4" y2="6.4" stroke="currentColor" stroke-width="1.8"/><line x1="8.6" y1="13.4" x2="15.4" y2="17.6" stroke="currentColor" stroke-width="1.8"/></svg>';
btn.addEventListener('click', function(){
var shareData = { title: document.title, url: location.href };
if(navigator.share){
navigator.share(shareData).catch(function(){});
return;
}
var fallback = function(){
var toast = document.createElement('div');
toast.className = 'ahk-toast';
toast.textContent = 'Link copied';
document.body.appendChild(toast);
requestAnimationFrame(function(){ toast.classList.add('show'); });
setTimeout(function(){
toast.classList.remove('show');
setTimeout(function(){ toast.remove(); }, 250);
}, 1800);
};
if(navigator.clipboard && navigator.clipboard.writeText){
navigator.clipboard.writeText(location.href).then(fallback).catch(function(){
prompt('Copy this link:', location.href);
});
} else {
prompt('Copy this link:', location.href);
}
});
document.body.appendChild(btn);
});
})();

// Live "X products scanned today" bubble. Says how many scans have
// happened, not "people" or "scans left" -- deliberately worded so it
// can't read as a quota or a headcount, since one person scanning five
// times and five different people scanning once look identical from
// here. Shown next to scanner buttons/links (page-specific slots
// already in the HTML) and, once more, in the footer of every other
// page. Dismissible with the little x -- hides it on that one page for
// the rest of this browser session (not sitewide, not permanently), so
// it's never a nag but still comes back next visit. Pulls from a small
// Cloudflare Worker that asks PostHog on the site's behalf -- the site
// itself never sees or exposes the PostHog account, just a plain
// number. Fails silently (bubble just never appears) if the Worker is
// unreachable, mid-deploy, or not set up yet.
(function(){
var WORKER_URL = 'https://ahomekind-scan-counter.ettlemanash.workers.dev';
var DISMISS_KEY = 'ahk-counter-dismissed:' + location.pathname;
window.addEventListener('DOMContentLoaded', function(){
if(!WORKER_URL) return;
var dismissed = false;
try { dismissed = sessionStorage.getItem(DISMISS_KEY) === '1'; } catch(e){}
if(dismissed) return;

var slots = Array.prototype.slice.call(document.querySelectorAll('.ahk-counter-bubble'));
// Every other page gets one added to its footer, so the bubble isn't
// limited to the handful of pages with a scan button on them.
var footer = document.querySelector('.site-footer');
if(footer && !slots.length){
var footerSlot = document.createElement('span');
footerSlot.className = 'ahk-counter-bubble';
footerSlot.style.marginTop = '14px';
footer.appendChild(footerSlot);
slots.push(footerSlot);
}
if(!slots.length) return;

fetch(WORKER_URL).then(function(r){ return r.json(); }).then(function(data){
if(!data || typeof data.count !== 'number') return;
var text = data.count + (data.count === 1 ? ' product scanned today' : ' products scanned today');
slots.forEach(function(slot){
var label = document.createElement('span');
label.textContent = "🐰 " + text;
var closeBtn = document.createElement('button');
closeBtn.type = 'button';
closeBtn.className = 'ahk-counter-x';
closeBtn.setAttribute('aria-label', 'Dismiss');
closeBtn.textContent = '×';
closeBtn.addEventListener('click', function(){
slot.classList.remove('ahk-visible');
try { sessionStorage.setItem(DISMISS_KEY, '1'); } catch(e){}
});
slot.textContent = '';
slot.appendChild(label);
slot.appendChild(closeBtn);
slot.classList.add('ahk-visible');
});
}).catch(function(){});
});
})();

// "Recently checked" brands: quietly remember the last few brand pages a
// visitor has looked at (name, url, tier) in localStorage, then show them
// as a small strip at the top of brand-check.html so it's easy to go back
// to something you looked up a minute ago. Purely local to the browser --
// nothing is sent anywhere, and it's just a handful of entries.
(function(){
var STORAGE_KEY = 'ahk-recent-brands';
var MAX_ITEMS = 6;

function readRecent(){
try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; } catch(e){ return []; }
}
function writeRecent(list){
try { localStorage.setItem(STORAGE_KEY, JSON.stringify(list)); } catch(e){}
}

// On an individual brand page, record this visit.
var m = location.pathname.match(/\/brands\/([^\/]+)\/?$/);
if (m) {
var run = function(){
var h1 = document.querySelector('main h1, #main h1');
if (!h1) return;
var name = h1.textContent.trim();
if (!name) return;
var ratingEl = document.querySelector('.rating');
var tier = 'neutral';
if (ratingEl) {
if (ratingEl.classList.contains('bad')) tier = 'bad';
else if (ratingEl.classList.contains('warn')) tier = 'warn';
else if (ratingEl.classList.contains('check')) tier = 'neutral';
else if (ratingEl.classList.contains('unverified')) tier = 'neutral';
else if (ratingEl.classList.contains('neutral')) tier = 'neutral';
else if (ratingEl.classList.contains('good')) tier = 'good';
else tier = 'neutral';
}
var list = readRecent().filter(function(item){ return item.slug !== m[1]; });
list.unshift({ slug: m[1], name: name, tier: tier });
if (list.length > MAX_ITEMS) list = list.slice(0, MAX_ITEMS);
writeRecent(list);
};
if (document.readyState === 'loading') {
document.addEventListener('DOMContentLoaded', run);
} else {
run();
}
}

// On brand-check.html, render the strip if we have anything to show.
if (location.pathname.replace(/^\//, '') === 'brand-check.html' || /\/brand-check\.html$/.test(location.pathname)) {
var renderStrip = function(){
var list = readRecent();
if (!list.length) return;
var slot = document.getElementById('main');
if (!slot) return;
var iconFor = { good: '🌿', warn: '⚠️', bad: '❌', neutral: '🐰' };
var wrap = document.createElement('div');
wrap.className = 'ahk-recent-strip';
var html = '<p class="ahk-recent-label">recently checked</p><div class="ahk-recent-pills">';
list.forEach(function(item){
html += '<a class="ahk-recent-pill ahk-recent-' + item.tier + '" href="brands/' + item.slug + '/">' +
'<span aria-hidden="true">' + (iconFor[item.tier] || iconFor.neutral) + '</span> ' + item.name + '</a>';
});
html += '</div>';
wrap.innerHTML = html;
var anchor = slot.querySelector('h1') || slot.firstElementChild;
if (anchor && anchor.parentNode === slot) {
anchor.insertAdjacentElement('afterend', wrap);
} else {
slot.insertBefore(wrap, slot.firstChild);
}
};
if (document.readyState === 'loading') {
document.addEventListener('DOMContentLoaded', renderStrip);
} else {
renderStrip();
}
}
})();

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
// Clean line-art icons (stroke-based SVG, 24x24) instead of emoji glyphs --
// these read consistently across every OS/browser, unlike system emoji fonts.
var bnIcons = {
  home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 10.5 12 3.5l8.5 7"/><path d="M5.5 9.5V20a1 1 0 0 0 1 1H9.5a1 1 0 0 0 1-1v-4.5a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1V20a1 1 0 0 0 1 1H17.5a1 1 0 0 0 1-1V9.5"/></svg>',
  scan: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8V6a2 2 0 0 1 2-2h2"/><path d="M16 4h2a2 2 0 0 1 2 2v2"/><path d="M20 16v2a2 2 0 0 1-2 2h-2"/><path d="M8 20H6a2 2 0 0 1-2-2v-2"/><circle cx="12" cy="12" r="3.2"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="10.5" cy="10.5" r="6.2"/><path d="m19.5 19.5-4.2-4.2"/></svg>',
  shop: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 8.5h11l.9 11a1.5 1.5 0 0 1-1.5 1.6H7.1a1.5 1.5 0 0 1-1.5-1.6z"/><path d="M9 8.5V7a3 3 0 0 1 6 0v1.5"/></svg>',
  more: '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="5.5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="18.5" cy="12" r="1.6"/></svg>'
};
function bnItem(href, icon, label, key){
var active = key === 'home' ? isActive(['/', '/index.html']) : isActive([href]);
return '<a href="' + href + '" class="bn-item' + (key === 'scan' ? ' bn-scan' : '') + (active ? ' active' : '') + '">' +
'<span class="bn-icon-wrap"><span class="bn-icon">' + icon + '</span></span>' +
'<span class="bn-label">' + label + '</span></a>';
}
var bn = document.createElement('div');
bn.className = 'bottom-nav';
bn.innerHTML =
bnItem('/index.html', bnIcons.home, 'Home', 'home') +
bnItem('/scan.html', bnIcons.scan, 'Scan', 'scan') +
bnItem('/brand-check.html', bnIcons.check, 'Brands', 'check') +
bnItem('/shop.html', bnIcons.shop, 'Shop', 'shop') +
'<button type="button" class="bn-item bn-more" id="bn-more-btn">' +
'<span class="bn-icon-wrap"><span class="bn-icon">' + bnIcons.more + '</span></span><span class="bn-label">More</span></button>';
document.body.appendChild(bn);

var sheet = document.createElement('div');
sheet.className = 'bn-sheet';
sheet.id = 'bn-sheet';
sheet.setAttribute('role', 'dialog');
sheet.setAttribute('aria-modal', 'true');
sheet.setAttribute('aria-label', 'more pages');
sheet.innerHTML =
'<div class="bn-sheet-inner">' +
/* Grouped rather than one long list of ten links: four short headed
   groups are far easier to scan than a pile, and it gives the newer
   pages (ingredient checker, food, fashion) somewhere obvious to sit. */
'<p class="bn-sheet-group">check something</p>' +
'<a href="/ingredient-check.html">ingredient checker</a>' +
'<a href="/brand-watch.html">what\'s changed</a>' +
'<p class="bn-sheet-group">explore</p>' +
'<a href="/swap-guide.html">swap guide</a>' +
'<a href="/food.html">food &amp; kitchen</a>' +
'<a href="/fashion.html">fashion &amp; accessories</a>' +
'<p class="bn-sheet-group">yours</p>' +
'<a href="/my-swaps.html">my swaps</a>' +
'<a href="/impact.html">your impact</a>' +
'<p class="bn-sheet-group">read</p>' +
'<a href="/learn.html">learn</a>' +
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
/* Focusing the close button (the last child) makes the browser scroll the
   sheet to reach it, which pushed the first and most-used item off the top.
   Focus without scrolling, then pin the sheet to its top. */
closeBtn.focus({ preventScroll: true });
var inner = sheet.querySelector('.bn-sheet-inner');
if(inner) inner.scrollTop = 0;
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
html += '<div class="myth-card" data-myth="' + i + '">' +
'<button type="button" class="myth-card-btn" id="mythCard' + i + '" aria-expanded="false" aria-controls="mythReality' + i + '">' +
'<span class="myth-img"><img src="images/myth-' + (i + 1) + '.jpg" alt="" loading="lazy" onerror="this.hidden=true"></span>' +
'<span class="myth-body">' +
'<span class="myth-tag">the myth</span>' +
'<span class="myth-claim">' + m.myth + '</span>' +
'<span class="myth-hint">tap to see the reality <span aria-hidden="true">&rarr;</span></span>' +
'</span>' +
'</button>' +
'</div>';
});
grid.innerHTML = html;
grid.classList.add('myth-track');
var cards = Array.prototype.slice.call(grid.querySelectorAll('.myth-card'));

// The reality opens in a panel beneath the row -- image beside the
// answer -- rather than on the back of a flip. Flipping hid the myth at
// the moment you wanted to compare it against the correction, and the
// answers are too long to fit a card back on a phone without shrinking
// the type. One panel is reused for whichever card is open.
var reality = document.createElement('div');
reality.className = 'myth-reality';
reality.hidden = true;
reality.innerHTML =
'<span class="myth-reality-img"><img alt="" id="mythRealityImg" hidden></span>' +
'<div class="myth-reality-body">' +
'<p class="myth-reality-tag">the reality</p>' +
'<p class="myth-reality-text" id="mythRealityText"></p>' +
'<button type="button" class="myth-reality-close">close</button>' +
'</div>';
grid.parentNode.insertBefore(reality, grid.nextSibling);
var rText = reality.querySelector('#mythRealityText');
var rImg = reality.querySelector('#mythRealityImg');
var openIndex = null;

function closeReality(){
reality.hidden = true;
if (openIndex !== null) {
var prev = cards[openIndex];
if (prev) {
prev.classList.remove('is-open');
prev.querySelector('.myth-card-btn').setAttribute('aria-expanded', 'false');
}
}
openIndex = null;
}
function openReality(i){
if (openIndex === i) { closeReality(); return; }
closeReality();
openIndex = i;
reality.id = 'mythReality' + i;
rText.textContent = MYTHS[i].reality;
rImg.src = 'images/myth-' + (i + 1) + '.jpg';
rImg.hidden = false;
reality.hidden = false;
cards[i].classList.add('is-open');
cards[i].querySelector('.myth-card-btn').setAttribute('aria-expanded', 'true');
}
cards.forEach(function(card, i){
card.querySelector('.myth-card-btn').addEventListener('click', function(){ openReality(i); });
});
reality.querySelector('.myth-reality-close').addEventListener('click', closeReality);

// Dots for the carousel. They only mean anything while the track is
// actually scrollable -- above 900px CSS lays the cards out as a grid
// and hides the dots, so nothing here needs to know the breakpoint.
var dots = document.createElement('div');
dots.className = 'myth-dots';
cards.forEach(function(_, i){
var d = document.createElement('button');
d.type = 'button';
d.className = 'myth-dot' + (i === 0 ? ' active' : '');
d.setAttribute('aria-label', 'Go to myth ' + (i + 1) + ' of ' + cards.length);
d.addEventListener('click', function(){
cards[i].scrollIntoView({ block: 'nearest', inline: 'center' });
});
dots.appendChild(d);
});
grid.parentNode.insertBefore(dots, grid.nextSibling);

// Mark the dot for whichever card is nearest the middle of the track.
var dotEls = Array.prototype.slice.call(dots.children);
var raf = null;
grid.addEventListener('scroll', function(){
if (raf) return;
raf = requestAnimationFrame(function(){
raf = null;
var mid = grid.scrollLeft + grid.clientWidth / 2;
var best = 0, bestDist = Infinity;
cards.forEach(function(card, i){
var centre = card.offsetLeft + card.offsetWidth / 2;
var dist = Math.abs(centre - mid);
if (dist < bestDist) { bestDist = dist; best = i; }
});
dotEls.forEach(function(d, i){ d.classList.toggle('active', i === best); });
});
}, { passive: true });
});

// "One small swap" -- a single instead-of/try pair on the homepage,
// picked from the day of the year so it's stable for the whole visit
// and changes daily rather than reshuffling on every reload. Pairs are
// the same ones already verified on swap-guide.html and brand-check,
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
'<p style="margin-top:22px;"><a href="/swap-guide.html" class="btn">see more swaps</a></p>';
});
