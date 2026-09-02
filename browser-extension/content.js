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
  // listing, the basket, etc.), plus where to read the product title text
  // from and two separate places to put a badge: right by the title
  // (where it's seen straight away) and right by the buy button (a second
  // reminder at the actual moment of deciding to buy, since that's often
  // a scroll away from the title on a long product page). Both are
  // optional -- if only one is found, the badge just appears there.
  //
  // Earlier versions of this fell back to <title> and <body> when a
  // selector didn't match, on the theory that "less precisely placed" is
  // better than nothing. In practice that backfired badly: on an Amazon
  // *search results* page for "dove", none of the product selectors
  // matched, so it fell back to the page's <title> tag -- which is
  // literally "Amazon.co.uk : dove" -- matched the Dove brand, and then
  // fell back to inserting the badge at the top of <body>, where it
  // landed wedged into the basket sidebar looking broken. Rule now: no
  // confirmed product page and no confirmed anchor element means no
  // badge there, full stop -- wrong silence beats wrong badge in the
  // wrong place.
  //
  // The buyAnchor selectors are the least tested part of this file --
  // they're a reasonable guess at each site's "add to basket" button, not
  // confirmed against a live page the way the Amazon ones are. See the
  // README.
  var SELECTORS = {
    "www.amazon.co.uk": {
      productPath: /\/(dp|gp\/product)\//,
      title: "#productTitle",
      titleAnchor: "#productTitle",
      buyAnchor: "#addToCart, #buybox",
    },
    "www.boots.com": {
      productPath: /\/p\//,
      title: ".product-title, [data-test='product-title']",
      titleAnchor: ".product-title, [data-test='product-title']",
      buyAnchor: "[data-test='add-to-basket'], .add-to-basket, button[name='add-to-basket']",
    },
    "www.superdrug.com": {
      productPath: /\/p\//,
      title: ".pdp-title, [data-testid='product-title']",
      titleAnchor: ".pdp-title, [data-testid='product-title']",
      buyAnchor: "[data-testid='add-to-basket-button'], .add-to-basket",
    },
    "www.ocado.com": {
      productPath: /\/products\//,
      title: "[data-testid='product-title']",
      titleAnchor: "[data-testid='product-title']",
      buyAnchor: "[data-testid='add-to-trolley-button'], .bl-add-to-trolley__button",
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

  function buildBadge(match, locationKey) {
    var meta = TIER_META[match.tier] || TIER_META.check;
    var wrap = document.createElement("div");
    wrap.className = "ahk-badge " + meta.cls;
    wrap.setAttribute("data-ahk-loc", locationKey);
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

  // locationKey distinguishes the two badge spots ("title", "buy") so each
  // is inserted at most once even though checkAndRender runs several
  // times as a page finishes loading.
  function insertBadge(match, anchor, locationKey) {
    if (!anchor || !anchor.parentNode) return; // nowhere sensible to put it -- skip rather than guess
    if (anchor.parentNode.querySelector('.ahk-badge[data-ahk-loc="' + locationKey + '"]')) return;
    var badge = buildBadge(match, locationKey);
    anchor.parentNode.insertBefore(badge, anchor.nextSibling);
  }

  function checkAndRender() {
    var conf = SELECTORS[location.hostname];
    if (!isProductPage(conf)) return; // search results, category pages, basket, etc. -- not our business
    var text = getPageText(conf);
    var titleAnchor = firstMatch(conf.titleAnchor);
    var buyAnchor = firstMatch(conf.buyAnchor);
    if (!text || text.length < 3 || (!titleAnchor && !buyAnchor)) return; // couldn't confidently find the product
    chrome.runtime.sendMessage({ type: "ahk-check-brand", text: text }, function (response) {
      if (chrome.runtime.lastError) return; // background service worker asleep/unreachable
      if (!response || !response.match) return;
      // Both are shown when both are found -- one right where the title is
      // seen straight away, one right by the buy button for a reminder at
      // the actual moment of deciding to buy. If the buy button and the
      // title happen to be the very same element (unlikely, but cheap to
      // guard against), only show it once.
      if (titleAnchor) insertBadge(response.match, titleAnchor, "title");
      if (buyAnchor && buyAnchor !== titleAnchor) insertBadge(response.match, buyAnchor, "buy");
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
      document.querySelectorAll(".ahk-badge").forEach(function (el) { el.remove(); });
      setTimeout(checkAndRender, 600);
    }
  }).observe(document.body, { childList: true, subtree: true });
})();
