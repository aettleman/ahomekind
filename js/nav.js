document.addEventListener('DOMContentLoaded', function(){
var dds = document.querySelectorAll('nav.main-nav .dd');
dds.forEach(function(dd){
var toggle = function(e){
if(e.target.closest('.dd-m')) return;
e.preventDefault();
var wasOpen = dd.classList.contains('open');
dds.forEach(function(other){ other.classList.remove('open'); });
if(!wasOpen){ dd.classList.add('open'); }
};
dd.addEventListener('click', toggle);
});
document.addEventListener('click', function(e){
if(!e.target.closest('nav.main-nav .dd')){
dds.forEach(function(dd){ dd.classList.remove('open'); });
}
});

// App-style bottom nav (mobile only) -- injected here so it applies site-wide
// without editing every page. Uses root-relative paths so it works at any
// folder depth.
var current = window.location.pathname.replace(/\/index\.html$/, '/').replace(/\/$/, '/');
function isActive(paths){
return paths.some(function(p){ return current === p || current.indexOf(p) === 0; });
}
var bn = document.createElement('div');
bn.className = 'bottom-nav';
bn.innerHTML =
'<a href="/index.html" class="bn-item' + (isActive(['/', '/index.html']) ? ' active' : '') + '">' +
'<span class="bn-icon">&#8962;</span><span class="bn-label">Home</span></a>' +
'<a href="/scan.html" class="bn-item bn-scan' + (isActive(['/scan.html']) ? ' active' : '') + '">' +
'<span class="bn-scan-circle">&#128247;</span><span class="bn-label">Scan</span></a>' +
'<a href="/brand-check.html" class="bn-item' + (isActive(['/brand-check.html']) ? ' active' : '') + '">' +
'<span class="bn-icon">&#128269;</span><span class="bn-label">Check</span></a>' +
'<a href="/shop.html" class="bn-item' + (isActive(['/shop.html']) ? ' active' : '') + '">' +
'<span class="bn-icon">&#128717;</span><span class="bn-label">Shop</span></a>' +
'<button type="button" class="bn-item bn-more" id="bn-more-btn">' +
'<span class="bn-icon">&#8942;</span><span class="bn-label">More</span></button>';
document.body.appendChild(bn);

var sheet = document.createElement('div');
sheet.className = 'bn-sheet';
sheet.id = 'bn-sheet';
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
function openSheet(){ sheet.classList.add('open'); document.body.classList.add('bn-sheet-lock'); }
function closeSheet(){ sheet.classList.remove('open'); document.body.classList.remove('bn-sheet-lock'); }
moreBtn.addEventListener('click', openSheet);
closeBtn.addEventListener('click', closeSheet);
sheet.addEventListener('click', function(e){ if(e.target === sheet) closeSheet(); });
});
