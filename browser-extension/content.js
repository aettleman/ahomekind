// Reads the product title/brand off a retailer's page and asks the
// background worker whether it matches a brand in the site's own
// brands.json. If it does, drops a small badge onto the page -- same
// verdict colours and wording as everywhere else on ahomekind.com, just
// here, before checkout, instead of requiring a separate lookup.
//
// NOTE for whoever's maintaining this: retailer page markup changes
// without warning and differs by page type (search results vs a single
// product page, desktop vs mobile layout, A/B tests). The selectors
// below are a reasonable first pass, not a guarantee -- if the badge
// stops appearing on a site it previously worked on, that site's HTML
// structure has probably changed and SELECTORS below needs updating to
// match. Test on a handful of real product pages after any retailer
// redesign.

(function () {
  "use strict";

  var TIER_META = {
    good: { emoji: "🍃", label: "cruelty-free & vegan", cls: "ahk-good" },
    check: { emoji: "🐰", label: "cruelty-free, check vegan status", cls: "ahk-check" },
    warn: { emoji: "⚠️", label: "cruelty-free itself, parent company isn't", cls: "ahk-warn" },
    bad: { emoji: "❌", label: "tested on animals", cls: "ahk-bad" },
    unverified: { emoji: "🔍", label: "not certified - no evidence either way", cls: "ahk-unverified" },
  };

  // Per-site: a regex the URL path must match for this to be treated as a
  // single product page at all (as opposed to search results, a category
  // listing, the basket, etc.), plus how to find the product title text
  // and which element to anchor the badge near (usually just above the
  // buy box).
  //
  // Earlier versions of this fell back to <title> and <body> when a
  // selector didn't match, on the theory that "less precisely placed" is
  // better than nothing. In practice that backfired badly: on an Amazon
  // *search results* page for "dove", none of the product selectors
  // matched, so it fell back to the page's <title> tag -- which is
  // literally "Amazon.co.uk : dove" -- matched the Dove brand, and then
  // fell back to inserting the badge at the top of <body>, where it
  // landed wedged into the basket sidebar looking broken. Rule now: no
  // confirmed product page and no confirmed title/anchor element means
  // no badge, full stop -- wrong silence beats wrong badge in the wrong
  // place.
  var SELECTORS = {
    "www.amazon.co.uk": {
      productPath: /\/(dp|gp\/product)\//,
      title: "#productTitle",
      anchor: "#addToCart, #buybox, #productTitle",
    },
    "www.boots.com": {
      productPath: /\/p\//,
      title: ".product-title, [data-test='product-title']",
      anchor: ".product-title, [data-test='product-title']",
    },
    "www.superdrug.com": {
      productPath: /\/p\//,
      title: ".pdp-title, [data-testid='product-title']",
      anchor: ".pdp-title, [data-testid='product-title']",
    },
    "www.ocado.com": {
      productPath: /\/products\//,
      title: "[data-testid='product-title']",
      anchor: "[data-testid='product-title']",
    },
  };

  function firstMatch(selectorList) {
    var selectors = selectorList.split(",").map(function (s) { return s.trim(); });
    for (var i = 0; i < selectors.length; i++) {
      var el = document.querySelector(selectors[i]);
      if (el) return el;
    }
    return null;
  }

  function isProductPage(conf) {
    return !!conf && conf.productPath.test(location.pathname);
  }

  function getPageText(conf) {
    var titleEl = firstMatch(conf.title);
    return titleEl ? titleEl.textContent.trim() : "";
  }

  function getAnchor(conf) {
    return firstMatch(conf.anchor);
  }

  function buildBadge(match) {
    var meta = TIER_META[match.tier] || TIER_META.check;
    var wrap = document.createElement("div");
    wrap.className = "ahk-badge " + meta.cls;
    wrap.innerHTML =
      '<span class="ahk-badge-emoji" aria-hidden="true">' + meta.emoji + "</span>" +
      '<span class="ahk-badge-text"><strong>' + escapeHtml(match.name) + "</strong> — " + escapeHtml(meta.label) + "</span>" +
      '<a class="ahk-badge-link" href="https://ahomekind.com/brands/' + encodeURIComponent(match.slug) + '/" target="_blank" rel="noopener">details</a>' +
      '<button type="button" class="ahk-badge-close" aria-label="dismiss">&times;</button>';
    wrap.querySelector(".ahk-badge-close").addEventListener("click", function () {
      wrap.remove();
    });
    return wrap;
  }

  function escapeHtml(s) {
    return String(s || "")
      .split("&").join("&amp;")
      .split('"').join("&quot;")
      .split("<").join("&lt;")
      .split(">").join("&gt;");
  }

  function insertBadge(match, anchor) {
    if (document.querySelector(".ahk-badge")) return; // already shown for this page
    if (!anchor || !anchor.parentNode) return; // nowhere sensible to put it -- skip rather than guess
    var badge = buildBadge(match);
    anchor.parentNode.insertBefore(badge, anchor.nextSibling);
  }

  // TEMPORARY: traces every step to the page console so a stuck badge can
  // be diagnosed from what's actually happening rather than guessed at.
  // Remove once the extension is confirmed working reliably.
  function log() {
    var args = Array.prototype.slice.call(arguments);
    args.unshift("[AHK]");
    console.log.apply(console, args);
  }

  function checkAndRender() {
    var conf = SELECTORS[location.hostname];
    if (!isProductPage(conf)) {
      log("skip: not a recognised product page for", location.hostname, location.pathname);
      return;
    }
    var text = getPageText(conf);
    var anchor = getAnchor(conf);
    if (!text || text.length < 3 || !anchor) {
      log("skip: title/anchor not confidently found", { text: text, hasAnchor: !!anchor });
      return;
    }
    log("checking text:", text);
    chrome.runtime.sendMessage({ type: "ahk-check-brand", text: text }, function (response) {
      if (chrome.runtime.lastError) {
        log("sendMessage failed:", chrome.runtime.lastError.message);
        return;
      }
      log("response:", response);
      if (response && response.match) insertBadge(response.match, anchor);
    });
  }

  // Product pages on these sites are frequently rendered/updated after
  // the initial load (React/Vue single-page navigation, lazy content),
  // so a single check on page load misses a lot. This re-checks a few
  // times over the following seconds, and again on SPA-style URL
  // changes, without hammering the background worker on every scroll.
  checkAndRender();
  [800, 2000, 4000].forEach(function (delay) {
    setTimeout(checkAndRender, delay);
  });

  var lastUrl = location.href;
  new MutationObserver(function () {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      var existing = document.querySelector(".ahk-badge");
      if (existing) existing.remove();
      setTimeout(checkAndRender, 600);
    }
  }).observe(document.body, { childList: true, subtree: true });
})();
