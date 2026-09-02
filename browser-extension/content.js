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

  // Per-site: how to find the product title text, and which element to
  // anchor the badge near (usually just above the buy box). Falls back
  // to <title> and <body> if a selector doesn't match on a given page --
  // meaning it still works, just less precisely placed.
  var SELECTORS = {
    "www.amazon.co.uk": {
      title: "#productTitle, #title",
      anchor: "#addToCart, #buybox, #productTitle",
    },
    "www.boots.com": {
      title: "h1, .product-title, [data-test='product-title']",
      anchor: "h1, .product-title, [data-test='product-title']",
    },
    "www.superdrug.com": {
      title: "h1, .pdp-title, [data-testid='product-title']",
      anchor: "h1, .pdp-title, [data-testid='product-title']",
    },
    "www.ocado.com": {
      title: "h1, [data-testid='product-title']",
      anchor: "h1, [data-testid='product-title']",
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

  function getPageText() {
    var conf = SELECTORS[location.hostname];
    var titleEl = conf ? firstMatch(conf.title) : null;
    var text = titleEl ? titleEl.textContent : document.title;
    return (text || "").trim();
  }

  function getAnchor() {
    var conf = SELECTORS[location.hostname];
    var el = conf ? firstMatch(conf.anchor) : null;
    return el || document.querySelector("h1") || document.body;
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

  function insertBadge(match) {
    if (document.querySelector(".ahk-badge")) return; // already shown for this page
    var anchor = getAnchor();
    var badge = buildBadge(match);
    if (anchor && anchor.parentNode) {
      anchor.parentNode.insertBefore(badge, anchor.nextSibling);
    } else {
      document.body.insertBefore(badge, document.body.firstChild);
    }
  }

  function checkAndRender() {
    var text = getPageText();
    if (!text || text.length < 3) return;
    chrome.runtime.sendMessage({ type: "ahk-check-brand", text: text }, function (response) {
      if (chrome.runtime.lastError) return; // extension context gone (page navigated away, etc.)
      if (response && response.match) insertBadge(response.match);
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
