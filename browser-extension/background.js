// Fetches and caches data/brands.json from ahomekind.com, and answers
// "does this text mention a brand I know about" questions from the
// content script. Kept deliberately dumb: no new data format, no local
// copy of the brand list to keep in sync by hand -- it always reads the
// same JSON the website itself uses, so anything added or corrected on
// the site (via the usual admin-scan -> brands.json workflow) shows up
// here automatically next time the cache refreshes.

const BRANDS_URL = "https://ahomekind.com/data/brands.json";
const CACHE_KEY = "ahk_brands_cache";
const CACHE_META_KEY = "ahk_brands_cache_meta";
const REFRESH_MS = 24 * 60 * 60 * 1000; // once a day is plenty -- brand tiers don't change hourly

function normalize(s) {
  return (s || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").replace(/\s+/g, " ").trim();
}

// Builds a lookup index once per fetch rather than re-normalizing every
// brand name on every single page-text check -- pages get checked a lot
// as someone browses, the brand list only changes once a day.
function buildIndex(brands) {
  return (brands || [])
    .filter(function (b) { return b && b.name && b.slug; })
    .map(function (b) {
      return {
        slug: b.slug,
        name: b.name,
        tier: b.tier,
        note: b.note || "",
        normalizedName: normalize(b.name),
      };
    })
    // Longest name first, so "Superdrug Pro Care" gets first refusal
    // over the shorter, more false-positive-prone "Superdrug" if a page
    // happens to mention both.
    .sort(function (a, b) { return b.normalizedName.length - a.normalizedName.length; });
}

async function refreshCache(force) {
  const meta = (await chrome.storage.local.get(CACHE_META_KEY))[CACHE_META_KEY];
  if (!force && meta && Date.now() - meta.fetchedAt < REFRESH_MS) return;
  try {
    const res = await fetch(BRANDS_URL, { cache: "no-store" });
    const brands = await res.json();
    const index = buildIndex(brands);
    await chrome.storage.local.set({
      [CACHE_KEY]: index,
      [CACHE_META_KEY]: { fetchedAt: Date.now(), count: index.length, ok: true },
    });
  } catch (e) {
    // Leave whatever's already cached in place -- a stale list beats no
    // list at all, and the meta record still lets the popup say when the
    // last successful refresh was.
    await chrome.storage.local.set({
      [CACHE_META_KEY]: Object.assign({ fetchedAt: Date.now(), ok: false }, meta || {}),
    });
  }
}

// Matching is deliberately conservative: a brand name has to appear as
// whole words in the page text (not just as a substring, which is how
// "Dove" would wrongly match "Dovetail" or "Dove Cottage"), and very
// short names (<4 characters) are skipped entirely -- too many false
// positives on retail pages full of unrelated words for too little
// payoff. Returns the single longest/most specific match, or null.
function findBrandMatch(pageText, index) {
  const text = normalize(pageText);
  if (!text) return null;
  for (let i = 0; i < index.length; i++) {
    const entry = index[i];
    if (entry.normalizedName.length < 4) continue;
    const pattern = new RegExp("(^|\\s)" + entry.normalizedName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "(\\s|$)");
    if (pattern.test(text)) return entry;
  }
  return null;
}

chrome.runtime.onInstalled.addListener(function () { refreshCache(true); });
chrome.runtime.onStartup.addListener(function () { refreshCache(false); });

chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
  if (!msg) return;
  if (msg.type === "ahk-check-brand") {
    refreshCache(false).then(function () {
      chrome.storage.local.get(CACHE_KEY).then(function (data) {
        const index = data[CACHE_KEY] || [];
        const match = findBrandMatch(msg.text, index);
        sendResponse({ match: match });
      });
    });
    return true; // keep the message channel open for the async response
  }
  if (msg.type === "ahk-refresh-now") {
    refreshCache(true).then(function () { sendResponse({ ok: true }); });
    return true;
  }
});
