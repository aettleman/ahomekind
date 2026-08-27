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
      var order = { high: 0, medium: 1, low: 2, undefined: 3 };
      pool.sort(function(a, b){
        var byVegan = (order[a.veganConfidence] || 3) - (order[b.veganConfidence] || 3);
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

  function altCardHTML(alt){
    var href = alt.slug ? "brands/" + alt.slug + "/index.html" : "#";
    return "" +
      "<div class=\"kswap-alt-card\" data-name=\"" + alt.name.replace(/\"/g, "&quot;") + "\">" +
      "<p class=\"kswap-alt-name\">" + alt.name + "</p>" +
      (alt.note ? "<p class=\"kswap-alt-note\">" + alt.note + "</p>" : "") +
      "<div class=\"kswap-alt-actions\">" +
      "<a href=\"" + href + "\" class=\"kswap-alt-link\">why this one</a>" +
      "<button type=\"button\" class=\"kswap-swap-btn\">I made the swap</button>" +
      "</div></div>";
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
    loadBrands(basePath).then(function(brands){
      var record = brandLike.slug ? brandLike : findRecord(brands, brandLike.name);
      var alts = record ? findAlternatives(brands, record, 3) : [];
      if(!alts.length){
        containerEl.innerHTML = noAlternativeHTML();
        return;
      }
      var html = "<p class=\"kswap-kicker\">looking for something kinder?</p>";
      html += "<div class=\"kswap-alts\">" + alts.map(altCardHTML).join("") + "</div>";
      containerEl.innerHTML = html;
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

  window.AHKSwap = { render: render, findAlternatives: findAlternatives, findRecord: findRecord };
})();
