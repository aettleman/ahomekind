// A Home Kind -- minimal service worker.
//
// This exists to satisfy PWA installability (Chrome/Android require one)
// and to give the site a graceful offline screen. It deliberately does NOT
// try to make the scanner work offline -- barcode lookups need Open Food
// Facts / Open Beauty Facts over the network, so there's nothing useful to
// cache for that. This only caches the small static "shell" (styling,
// nav script, icons, the offline page itself) so the app frame loads
// instantly and a missing connection fails politely instead of showing a
// browser error page.
//
// Bump CACHE_VERSION whenever the shell files below change so old caches
// are cleared out on the next visit.
var CACHE_VERSION = 'ahk-shell-v5';
var SHELL_URLS = [
'/offline.html',
'/css/style.css?v=20260903',
'/js/nav.js?v=20260903',
'/manifest.json',
'/icons/icon-192.png',
'/icons/icon-512.png',
'/favicon.ico'
];

self.addEventListener('install', function(event){
event.waitUntil(
caches.open(CACHE_VERSION).then(function(cache){
return cache.addAll(SHELL_URLS);
}).then(function(){
return self.skipWaiting();
})
);
});

self.addEventListener('activate', function(event){
event.waitUntil(
caches.keys().then(function(keys){
return Promise.all(
keys.filter(function(key){ return key !== CACHE_VERSION; })
.map(function(key){ return caches.delete(key); })
);
}).then(function(){
return self.clients.claim();
})
);
});

self.addEventListener('fetch', function(event){
var req = event.request;
if (req.method !== 'GET') return;

var url = new URL(req.url);
if (url.origin !== self.location.origin) return; // let cross-origin (API, CDN, fonts) pass straight through

// Page navigations: try the network first (so pages stay fresh), and only
// fall back to the offline screen if the network genuinely fails.
if (req.mode === 'navigate') {
event.respondWith(
fetch(req).catch(function(){
return caches.match('/offline.html');
})
);
return;
}

// Static shell assets: serve from cache first for speed, refresh in the
// background, and fall back to cache if the network is unavailable.
if (SHELL_URLS.indexOf(url.pathname + url.search) !== -1 || SHELL_URLS.indexOf(url.pathname) !== -1) {
event.respondWith(
caches.match(req).then(function(cached){
var fetchPromise = fetch(req).then(function(res){
if (res && res.status === 200) {
caches.open(CACHE_VERSION).then(function(cache){ cache.put(req, res.clone()); });
}
return res;
}).catch(function(){ return cached; });
return cached || fetchPromise;
})
);
}
});
