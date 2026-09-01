// Live-estimate counter: "roughly how many land animals are being
// slaughtered for meat worldwide, right now, while you have this page
// open." The rate is fixed and real, not fabricated -- 83 billion land
// animals slaughtered for meat globally in 2022 per the UN Food and
// Agriculture Organization (via Our World in Data), divided evenly
// across a year. It excludes sea life, hunting, and deaths in the egg
// and dairy industries (male chicks culled, spent dairy cows, etc.) --
// all things nobody has a solid global figure for -- so if anything
// this understates the real number. That honesty matters more than
// making the number bigger.
//
// The counter itself starts at zero on page load and counts up at that
// real-world rate for as long as the page stays open. It is not a feed
// of live events -- nobody knows the exact animal killed at the exact
// second you're reading this -- it's the published annual rate turned
// into a running total, which is the same maths as "per second"
// statistics widely cited elsewhere, just kept ticking instead of
// frozen as a single number.
//
// Usage: call window.ahkShowImpactCounter() once, any time after the
// page has settled. Dismissing it (the x) only hides it for this page
// view -- it isn't a permanent, sitewide dismissal, since the whole
// point is tied to "since you opened this page."
(function(){
var RATE_PER_SECOND = 83000000000 / (365.25 * 24 * 3600); // ~2,630/sec
var SOURCE_URL = 'https://ourworldindata.org/data-insights/billions-of-chickens-ducks-and-pigs-are-slaughtered-for-meat-every-year';
var shown = false;
var timer = null;

window.ahkShowImpactCounter = function(){
if (shown) return;
shown = true;
var run = function(){
var el = document.createElement('div');
el.className = 'impact-counter';
el.setAttribute('role', 'status');
el.setAttribute('aria-label', 'Live estimate of land animals slaughtered for meat worldwide since you opened this page');
el.innerHTML =
'<button type="button" class="impact-counter-x" aria-label="dismiss">&times;</button>' +
'<div class="impact-counter-num" id="impactCounterNum">0</div>' +
'<div class="impact-counter-label">land animals killed for meat worldwide, since you opened this page</div>' +
'<div class="impact-counter-line">This isn\'t a hypothetical. It\'s the rate right now, everywhere, while you read this. I can\'t make the choice for you, but you get to decide whether your money keeps feeding it.</div>' +
'<a href="' + SOURCE_URL + '" target="_blank" rel="noopener" class="impact-counter-source">based on FAO data via Our World in Data &rarr;</a>';
document.body.appendChild(el);
requestAnimationFrame(function(){ el.classList.add('show'); });

var numEl = el.querySelector('#impactCounterNum');
var start = performance.now();
function tick(){
var elapsedSeconds = (performance.now() - start) / 1000;
var count = Math.floor(elapsedSeconds * RATE_PER_SECOND);
numEl.textContent = count.toLocaleString();
timer = requestAnimationFrame(tick);
}
timer = requestAnimationFrame(tick);

var closeBtn = el.querySelector('.impact-counter-x');
closeBtn.addEventListener('click', function(){
if (timer) cancelAnimationFrame(timer);
el.classList.remove('show');
setTimeout(function(){ if (el.parentNode) el.parentNode.removeChild(el); }, 300);
});
};
if (document.readyState === 'complete' || document.readyState === 'interactive') {
setTimeout(run, 400);
} else {
window.addEventListener('DOMContentLoaded', function(){ setTimeout(run, 400); });
}
};
})();
