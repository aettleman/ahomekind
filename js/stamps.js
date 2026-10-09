/* A Home Kind: certification + ethical rating stamps. Plain JS, no dependencies.
   Usage: AHKStamps.row({lb:true, peta:true, vegan:true, goy:{score:3, url:"..."}}) -> HTML string.
   Real logos: set img paths in S below (e.g. img:"/images/stamps/leaping-bunny.png") once permission is given. */
(function () {
  var S = {
    vegan: { short: "V",     img: null, title: "Vegan", who: null,
             means: "The brand says its products are vegan, or a vegan certifier backs that up. Vegan status can vary between products, so check the label.", url: null },
    unk:   { short: "?",    img: null, title: "Not certified", who: null,
             means: "No Leaping Bunny or PETA certification found for this brand. That does not mean it tests on animals, as some brands simply have not applied.", url: null },
    ncf:   { short: "X",     img: null, title: "Tests on animals", who: null,
             means: "This brand, or the company behind it, tests on animals or sells where animal testing is required by law. The source is on the brand page.", url: null },
    lb:    { short: "LB",    img: null, title: "Leaping Bunny", who: "Cruelty Free International (CCIC in the US and Canada)",
             means: "Certified by Leaping Bunny: no animal testing of ingredients or finished products, anywhere in the world, backed by supplier checks and regular audits.", url: "https://www.leapingbunny.org" },
    peta:  { short: "PETA",  img: null, title: "PETA cruelty-free", who: "PETA (Beauty Without Bunnies)",
             means: "Listed by PETA as cruelty-free: the brand has signed a statement that it does not test on animals. PETA does not audit as strictly as Leaping Bunny.", url: "https://crueltyfree.peta.org" }
  };
  var LABELS = { 1: "We Avoid", 2: "Not Good Enough", 3: "It's a Start", 4: "Good", 5: "Great" };
  var MEANS = {
    1: "Little or no concrete information, sometimes vague claims that look like greenwashing.",
    2: "Some information shared, but not enough to know what happens in the supply chain.",
    3: "Good progress on at least one of the main issues.",
    4: "Many positive steps, often leading on a key issue, and usually very transparent.",
    5: "Strong in at least two areas, with certifications, and very transparent."
  };
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function stamp(key) {
    var s = S[key]; if (!s) return "";
    var inner = s.img ? '<img src="' + s.img + '" alt="" width="28" height="28">' : '<span class="ahk-stamp-txt">' + s.short + "</span>";
    return '<button type="button" class="ahk-stamp ahk-stamp-' + key + '" data-stamp="' + key + '" aria-label="' + esc(s.title) + ', tap for details">' + inner + "</button>";
  }
  function rating(g) {
    if (!g || !LABELS[g.score]) return "";  // not rated by Good On You: show nothing
    return '<button type="button" class="ahk-rating ahk-r' + g.score + '" data-stamp="goy" data-score="' + g.score + '" data-url="' + esc(g.url || "https://directory.goodonyou.eco") + '" aria-label="Ethical rating: ' + LABELS[g.score] + ', tap for details">' +
      '<span class="ahk-rating-n">' + g.score + '</span><span class="ahk-rating-t"><b>Ethical rating &middot; Good On You</b>' + LABELS[g.score] + "</span></button>";
  }
  function row(o) {
    var h = ["unk", "ncf", "vegan", "lb", "peta"].filter(function (k) { return o[k]; }).map(stamp).join("");
    return '<div class="ahk-stamps">' + h + rating(o.goy) + "</div>";
  }
  var dlg;
  function open(btn) {
    var k = btn.getAttribute("data-stamp"), t, who, m, u, ex = "";
    if (k === "goy") {
      var n = +btn.getAttribute("data-score");
      t = "Ethical rating: " + LABELS[n] + " (" + n + " out of 5)"; who = "Good On You"; m = MEANS[n]; u = btn.getAttribute("data-url");
      ex = "<p>This looks at how a brand treats people, the planet and animals overall. It is <b>not</b> about animal testing, so it is separate from the cruelty-free stamp.</p><p class=\"ahk-key\">" + [5,4,3,2,1].map(function (k) { return (k === n ? "<b>" : "") + k + " " + LABELS[k] + (k === n ? "</b>" : ""); }).join(" &middot; ") + "</p><p><b>The rating, the 1 to 5 scale and its labels all belong to Good On You, an independent brand rating organisation. They are not my own rating.</b></p>";
    } else { var s = S[k]; t = s.title; who = s.who; m = s.means; u = s.url; }
    if (!dlg) {
      dlg = document.createElement("div"); dlg.className = "ahk-dlg"; dlg.setAttribute("role", "dialog"); dlg.setAttribute("aria-modal", "true"); dlg.hidden = true;
      dlg.addEventListener("click", function (e) { if (e.target === dlg || e.target.hasAttribute("data-close")) close(); });
      document.body.appendChild(dlg);
      document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
    }
    dlg.innerHTML = '<div class="ahk-card"><h3>' + esc(t) + '</h3>' + (who ? '<p class="ahk-who">By ' + esc(who) + "</p>" : "") + "<p>" + esc(m) + "</p>" + ex +
      (u ? '<p><a href="' + esc(u) + '" target="_blank" rel="noopener">' + (k === "goy" ? "See the rating on Good On You" : "Visit " + esc(who.split(" (")[0])) + "</a></p>" : "") +
      '<button type="button" data-close class="ahk-close">Close</button></div>';
    dlg.hidden = false; dlg.querySelector(".ahk-close").focus();
  }
  function close() { if (dlg) dlg.hidden = true; }
  document.addEventListener("click", function (e) { var b = e.target.closest && e.target.closest("[data-stamp]"); if (b) open(b); });
  window.AHKStamps = { row: row, stamp: stamp, rating: rating, config: S };
})();
