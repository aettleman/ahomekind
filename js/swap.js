// Kind Swaps + Cruelty Freebies -- shared logic.
//
// This deliberately does NOT keep its own list of brands or alternatives.
// It reads data/brands.json (the same file brand-check.html and the brand
// pages already use) so there is one source of truth, and "alternatives"
// for a brand come from that brand's own "alternatives" field where it's
// been filled in, or are worked out automatically from shared categories
// when it hasn't.
//
// Everything here is plain data + DOM -- no backend, no accounts. "I made
// the swap" and freebie claims are recorded in localStorage, on this
// device only. That's fine for this phase: the point is the flow works
// end to end, not that it syncs anywhere yet.
//
// Usage (see scan.html):
//   AHKSwap.render(container, { name: brand.name, tier: brand.tier });
//
// basePath lets this same script be dropped into a nested page later
// (e.g. a brand page under /brands/slug/) without rewriting the fetch
// paths -- pass {basePath:"../../"} in that case. Root-level pages can
// leave it out.

(function(){
  var SWAPS_KEY = "ahk-kind-swaps";
  var CLAIMS_KEY = "ahk-freebie-claims";
  var brandsPromise = null;
  var freebiesPromise = null;

  function normalize(s){
    return String(s || "")
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .replace(/own brand.*$/, '')
      .replace(/[^a-z0-9]/g, '');
  }

  function loadBrands(basePath){
    if(!brandsPromise){
      brandsPromise = fetch((basePath || "") + "data/brands.json")
        .then(function(r){ return r.json(); })
        .catch(function(){ return []; });
    }
    return brandsPromise;
  }

  function loadFreebies(basePath){
    if(!freebiesPromise){
      freebiesPromise = fetch((basePath || "") + "data/freebies.json")
        .then(function(r){ return r.json(); })
        .catch(function(){ return []; });
    }
    return freebiesPromise;
  }

  // Hand-curated, verified ingredient-level comparisons between a
  // specific "from" brand and a specific "to" alternative -- see
  // data/comparisons.json. Deliberately NOT auto-generated from raw
  // ingredient lists: whether two products actually do the same job is
  // a judgement call (an anti-dandruff active vs. a moisture treatment
  // aren't interchangeable just because both are "shampoo"), so every
  // entry here has been checked by hand before it's shown as fact.
  var comparisonsPromise = null;
  function loadComparisons(basePath){
    if(!comparisonsPromise){
      comparisonsPromise = fetch((basePath || "") + "data/comparisons.json")
        .then(function(r){ return r.json(); })
        .catch(function(){ return []; });
    }
    return comparisonsPromise;
  }
  function findComparison(comparisons, fromSlug, toSlug){
    if(!fromSlug || !toSlug) return null;
    for(var i=0;i<comparisons.length;i++){
      if(comparisons[i].from === fromSlug && comparisons[i].to === toSlug) return comparisons[i];
    }
    return null;
  }

  function findRecord(brands, name){
    var n = normalize(name);
    if(!n) return null;
    for(var i=0;i<brands.length;i++){
      if(normalize(brands[i].name) === n) return brands[i];
    }
    // loose fallback -- handles small punctuation/casing differences
    // between the scanner's own brand list and data/brands.json
    for(var j=0;j<brands.length;j++){
      var bn = normalize(brands[j].name);
      if(bn && (n.indexOf(bn) !== -1 || bn.indexOf(n) !== -1)) return brands[j];
    }
    return null;
  }

  // Picks up to `max` kinder alternatives for a brand. Prefers the
  // brand's own hand-picked "alternatives" list (names); falls back to
  // any fully cruelty-free & vegan-friendly brand sharing a category.
  function findAlternatives(brands, record, max){
    max = max || 3;
    var results = [];
    var seen = {};
    function add(b){
      if(!b || seen[b.slug] || b.tier !== "good") return;
      seen[b.slug] = true;
      results.push(b);
    }
    if(record && record.alternatives && record.alternatives.length){
      record.alternatives.forEach(function(altName){
        add(findRecord(brands, altName));
      });
    }
    if(results.length < max && record && record.category && record.category.length){
      var pool = brands.filter(function(b){
        return b.tier === "good" && b.slug !== record.slug &&
          (b.category || []).some(function(c){ return record.category.indexOf(c) !== -1; });
      });
      // high vegan confidence and cheaper first, otherwise keep list order
      var order = { high: 0, medium: 1, low: 2 };
      function rank(b){ return order.hasOwnProperty(b.veganConfidence) ? order[b.veganConfidence] : 3; }
      pool.sort(function(a, b){
        var byVegan = rank(a) - rank(b);
        if(byVegan !== 0) return byVegan;
        return (a.price || "").length - (b.price || "").length;
      });
      pool.forEach(add);
    }
    return results.slice(0, max);
  }

  function readList(key){
    try { return JSON.parse(localStorage.getItem(key) || "[]"); } catch(e){ return []; }
  }
  function writeList(key, list){
    try { localStorage.setItem(key, JSON.stringify(list)); } catch(e){}
  }

  function freebieCardHTML(freebie){
    if(!freebie){
      return "" +
        "<div class=\"kswap-freebie-card\">" +
        "<p class=\"kswap-freebie-title\">your cruelty freebie is on its way</p>" +
        "<p class=\"kswap-freebie-body\">I haven't finished designing these yet &mdash; wallpapers, little animal illustrations, that sort of thing. The moment the first batch is ready, this is where you'll find it. Thank you for making the kinder choice in the meantime.</p>" +
        "</div>";
    }
    var body = freebie.description ? "<p class=\"kswap-freebie-body\">" + freebie.description + "</p>" : "";
    var link = freebie.fileUrl
      ? "<a class=\"btn\" href=\"" + freebie.fileUrl + "\" target=\"_blank\" rel=\"noopener\">save my freebie</a>"
      : "";
    return "" +
      "<div class=\"kswap-freebie-card\">" +
      "<p class=\"kswap-freebie-title\">" + (freebie.title || "a little cruelty freebie") + "</p>" +
      body + link +
      "</div>";
  }

  function claimFreebie(basePath, containerEl){
    var claimed = readList(CLAIMS_KEY);
    loadFreebies(basePath).then(function(freebies){
      var next = (freebies || []).filter(function(f){ return claimed.indexOf(f.id) === -1; })[0];
      if(next) { claimed.push(next.id); writeList(CLAIMS_KEY, claimed); }
      containerEl.innerHTML = freebieCardHTML(next);
    });
  }

  function unlockedHTML(){
    return "" +
      "<div class=\"kswap-unlock\">" +
      "<p class=\"kswap-unlock-title\">you made a kinder swap</p>" +
      "<p class=\"kswap-unlock-body\">You've unlocked a Cruelty Freebie &mdash; a little thank-you from me, one kind choice at a time.</p>" +
      "<button type=\"button\" class=\"btn\" id=\"kswap-claim-btn\">claim your freebie</button>" +
      "<div id=\"kswap-freebie-slot\"></div>" +
      "</div>";
  }

  // The "worried it won't work the same?" section under an alternative:
  // a real, verified comparison when one exists (data/comparisons.json),
  // otherwise an honest general reassurance line -- never a fabricated
  // ingredient claim -- plus a way to help build the real comparison.
  function comparisonHTML(fromBrand, alt, comparison){
    var mailBody = "From brand: " + fromBrand.name + "\n" +
      "Alternative: " + alt.name + "\n\n" +
      "I'd like to compare these two properly, but don't have verified ingredient data for one or both yet.\n\n" +
      "If you can, please attach:\n- a clear photo of the full ingredients list for " + fromBrand.name + " (the specific product you use)\n- a clear photo of the full ingredients list for " + alt.name + " (or the barcode, if you've already got it)\n\nAnything else you know about either product:\n";
    var mailHref = "mailto:hello@ahomekind.com?subject=" + encodeURIComponent("Ingredient comparison: " + fromBrand.name + " vs " + alt.name) + "&body=" + encodeURIComponent(mailBody);
    if(comparison){
      return "" +
        "<div class=\"kswap-compare kswap-compare-verified\">" +
        "<p class=\"kswap-compare-title\">how they actually compare</p>" +
        "<p class=\"kswap-compare-body\">" + comparison.note + "</p>" +
        "</div>";
    }
    return "" +
      "<div class=\"kswap-compare\">" +
      "<p class=\"kswap-compare-title\">worried it won't work the same?</p>" +
      "<p class=\"kswap-compare-body\">That's a completely fair thing to wonder before switching something that already works for you. I haven't done a verified ingredient-by-ingredient comparison for this exact pair yet, but both are made to do the same job -- there's no reason a cruelty-free version can't perform just as well.</p>" +
      "<a href=\"" + mailHref + "\" class=\"kswap-compare-link\">help me compare these properly &rarr;</a>" +
      "</div>";
  }

  // Picks the alternative's affiliate link, where one genuinely exists.
  // Reads straight off the brand record's own "links" array in
  // data/brands.json (the same field the brand pages already render under
  // "sources & links") -- nothing here invents a link or a relationship.
  // A link only counts if it's explicitly flagged affiliate:true and
  // hasn't been switched off with active:false, so removing or pausing
  // one later is a one-line data edit, not a code change.
  function pickAffiliateLink(alt){
    if(!alt || !alt.links) return null;
    for(var i=0;i<alt.links.length;i++){
      var l = alt.links[i];
      if(l && l.affiliate && l.active !== false && l.url) return l;
    }
    return null;
  }

  function affiliateRowHTML(alt){
    var link = pickAffiliateLink(alt);
    if(!link) return "";
    var retailer = link.retailer || "the retailer";
    return "" +
      "<p class=\"kswap-affiliate-row\">" +
      "<a href=\"" + link.url + "\" class=\"kswap-shop-link\" target=\"_blank\" rel=\"nofollow sponsored noopener\">shop " + alt.name + " on " + retailer + " &rarr;</a>" +
      "<span class=\"kswap-affiliate-note\">affiliate link &mdash; a small commission may support A Home Kind, at no extra cost to you</span>" +
      "</p>";
  }

  function altCardHTML(alt, fromBrand, comparison){
    var href = alt.slug ? "brands/" + alt.slug + "/index.html" : "#";
    return "" +
      "<div class=\"kswap-alt-card\" data-name=\"" + alt.name.replace(/\"/g, "&quot;") + "\">" +
      "<p class=\"kswap-alt-name\">" + alt.name + "</p>" +
      (alt.note ? "<p class=\"kswap-alt-note\">" + alt.note + "</p>" : "") +
      (fromBrand ? comparisonHTML(fromBrand, alt, comparison) : "") +
      "<div class=\"kswap-alt-actions\">" +
      "<a href=\"" + href + "\" class=\"kswap-alt-link\">why this one</a>" +
      "<button type=\"button\" class=\"kswap-swap-btn\">I made the swap</button>" +
      "</div>" +
      affiliateRowHTML(alt) +
      "</div>";
  }

  function noAlternativeHTML(){
    return "" +
      "<div class=\"kswap-none\">" +
      "<p class=\"kswap-none-title\">no easy swap right now &mdash; and that's alright</p>" +
      "<p class=\"kswap-none-body\">Sometimes you're just stood in a shop late at night with one option in your hand. That's a completely normal way to live, not a failure. Have a browse when you've got a minute and I'll help you find a kinder option for next time.</p>" +
      "<a href=\"brand-check.html\" class=\"btn\">browse cruelty-free brands</a>" +
      "</div>";
  }

  // Renders the whole "looking for something kinder?" flow into
  // containerEl for the given brand-like object ({name, tier, slug?}).
  // Does nothing if the brand is already on the good list.
  function render(containerEl, brandLike, opts){
    if(!containerEl || !brandLike) return;
    if(brandLike.tier === "good") { containerEl.innerHTML = ""; return; }
    var basePath = (opts && opts.basePath) || "";
    containerEl.innerHTML = "<p class=\"kswap-loading\">looking for something kinder&hellip;</p>";
    Promise.all([loadBrands(basePath), loadComparisons(basePath)]).then(function(results){
      var brands = results[0], comparisons = results[1];
      var record = brandLike.slug ? brandLike : findRecord(brands, brandLike.name);
      var alts = record ? findAlternatives(brands, record, 3) : [];
      // Collapsed by default behind a button-styled summary -- this sits
      // right under the "why" disclosure on brand-check, so it needs its
      // own clear space and shouldn't force itself on anyone who just
      // wanted the why explanation and nothing else.
      if(!alts.length){
        containerEl.innerHTML = "<details class=\"kswap-details\"><summary class=\"kswap-summary\">looking for something kinder?</summary><div class=\"kswap-details-body\">" + noAlternativeHTML() + "</div></details>";
        return;
      }
      var altsHtml = "<div class=\"kswap-alts\">" + alts.map(function(alt){
        var comparison = record ? findComparison(comparisons, record.slug, alt.slug) : null;
        return altCardHTML(alt, record, comparison);
      }).join("") + "</div>";
      containerEl.innerHTML = "<details class=\"kswap-details\"><summary class=\"kswap-summary\">looking for something kinder?</summary><div class=\"kswap-details-body\">" + altsHtml + "</div></details>";
      containerEl.querySelectorAll(".kswap-swap-btn").forEach(function(btn){
        btn.addEventListener("click", function(){
          var card = btn.closest(".kswap-alt-card");
          var toName = card ? card.getAttribute("data-name") : "";
          var swaps = readList(SWAPS_KEY);
          swaps.push({ from: brandLike.name, to: toName, ts: Date.now() });
          writeList(SWAPS_KEY, swaps);
          containerEl.innerHTML = unlockedHTML();
          var claimBtn = document.getElementById("kswap-claim-btn");
          if(claimBtn){
            claimBtn.addEventListener("click", function(){
              claimBtn.disabled = true;
              claimFreebie(basePath, document.getElementById("kswap-freebie-slot"));
            });
          }
        });
      });
    });
  }

  window.AHKSwap = { render: render, findAlternatives: findAlternatives, findRecord: findRecord, pickAffiliateLink: pickAffiliateLink };
})();
