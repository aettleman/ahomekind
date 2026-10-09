import json, copy, datetime, re, os, time, unicodedata, urllib.request, urllib.parse, subprocess
P = "data/brands.json"
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw
by = {b["slug"]: b for b in brands}
today = datetime.date.today().isoformat()
def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower().replace("&", "and")
    return re.sub(r"[^a-z0-9]", "", s)
def nm(b): return norm(re.sub(r"^the ", "", b.get("name", "").strip(), flags=re.I))

# 1. Daise
d = next((b for b in brands if b.get("name", "").strip().lower() in ("daise", "daisy")), None)
if d:
    link = {"url": "https://crueltyfreeinternational.org/approved-brands/listing/daise/", "label": "Cruelty Free International"}
    old = [l for l in d.get("links", []) if "crueltyfreeinternational" not in l.get("url", "")]
    d.update(tier="check", vegan="partial", veganConfidence="medium", claim="", evidence="", lastVerified=today,
             note="Certified cruelty-free by Cruelty Free International (Leaping Bunny). Not every product is vegan, so vegan varies by product.",
             links=[link] + old)
    print("Daise fixed")
# 2. r.e.m. beauty
if "rem-beauty" not in by and "zoflora" in by:
    regions = {b.get("region") for b in brands if b.get("region")}
    na = [r for r in regions if "america" in r.lower()]
    e = copy.deepcopy(by["zoflora"])
    e.update(slug="rem-beauty", name="r.e.m. beauty", tier="check", vegan="unclear", veganConfidence="low",
             region=na[0] if na else e.get("region"), price="££", claim="", evidence="", parentCompany=None,
             products=[], alternatives=[], category=[], lastVerified=today,
             note="PETA lists r.e.m. beauty as cruelty-free and says its products contain no beeswax, carmine, lanolin or collagen. This is the makeup brand only, not Ariana Grande's fragrances.",
             links=[{"url": "https://www.peta.org/lifestyle/personal-care-fashion/rem-beauty-ariana-grande/", "label": "PETA"}])
    brands.append(e); by["rem-beauty"] = e; print("r.e.m. beauty added")

# 3. Good On You ratings (each checked on its Good On You brand page)
GOY = {1: ["revlon"], 4: ["garnier", "lush", "aesop", "nealsyardremedies"],
 3: ["maybelline", "nyx", "bodyshop", "theordinary", "origins", "toofaced", "dermalogica", "kiehls", "moltonbrown", "yvesrocher", "urbandecay", "weleda"],
 2: ["neutrogena", "olay", "bobbibrown", "paulaschoice", "bareminerals", "theinkeylist", "rimmel", "rimmellondon", "benefit", "esteelauder", "mac", "maccosmetics", "jomalone", "clinique", "charlottetilbury", "tarte", "nars", "glossier", "drunkelephant", "dior", "soldejaneiro"]}
GSLUG = {"paulaschoice": "paulas-choice", "bobbibrown": "bobbi-brown", "theinkeylist": "the-inkey-list", "nyx": "nyx-professional-makeup", "rimmel": "rimmel-london", "rimmellondon": "rimmel-london", "bodyshop": "the-body-shop", "theordinary": "deciem", "mac": "mac-cosmetics", "maccosmetics": "mac-cosmetics",
 "nealsyardremedies": "neals-yard-remedies", "toofaced": "too-faced", "moltonbrown": "molton-brown", "yvesrocher": "yves-rocher",
 "urbandecay": "urban-decay", "esteelauder": "estee-lauder", "jomalone": "jo-malone", "charlottetilbury": "charlotte-tilbury",
 "drunkelephant": "drunk-elephant", "soldejaneiro": "sol-de-janeiro", "kiehls": "kiehls"}
gp = "data/good-on-you.json"
goy = json.load(open(gp)) if os.path.exists(gp) else {}
added = 0
for b in brands:
    ks = {nm(b), norm(b.get("name", ""))}; k = sorted(ks)[0]
    for score, keys in GOY.items():
        hit = [x for x in keys if x in ks]
        if hit and b["slug"] not in goy:
            k = hit[0]
            goy[b["slug"]] = {"score": score, "url": "https://directory.goodonyou.eco/brand/%s-beauty" % GSLUG.get(k, k)}
            added += 1
json.dump(goy, open(gp, "w"), indent=2, ensure_ascii=False); open(gp, "a").write("\n")
print("Ethical ratings added:", added)

# 4. Owners: only applied when my list AND Wikidata agree
OWN = {"Urban Decay": "L'Oréal", "Kiehl's": "L'Oréal", "Garnier": "L'Oréal", "Maybelline": "L'Oréal", "NYX": "L'Oréal",
 "CeraVe": "L'Oréal", "La Roche-Posay": "L'Oréal", "Vichy": "L'Oréal", "Aesop": "L'Oréal",
 "Clinique": "Estée Lauder Companies", "MAC": "Estée Lauder Companies", "Origins": "Estée Lauder Companies",
 "Jo Malone": "Estée Lauder Companies", "Too Faced": "Estée Lauder Companies", "Bobbi Brown": "Estée Lauder Companies",
 "The Ordinary": "Estée Lauder Companies", "Dove": "Unilever", "Vaseline": "Unilever", "Simple": "Unilever",
 "Dermalogica": "Unilever", "Cif": "Unilever", "Pantene": "Procter & Gamble", "Head & Shoulders": "Procter & Gamble",
 "Olay": "Procter & Gamble", "Gillette": "Procter & Gamble", "Fairy": "Procter & Gamble", "Ariel": "Procter & Gamble",
 "Colgate": "Colgate-Palmolive", "Palmolive": "Colgate-Palmolive", "Nivea": "Beiersdorf", "Neutrogena": "Kenvue",
 "Aveeno": "Kenvue", "Rimmel": "Coty", "Max Factor": "Coty", "Sally Hansen": "Coty", "Covergirl": "Coty",
 "Benefit": "LVMH", "Dior": "LVMH", "Sephora": "LVMH", "Drunk Elephant": "Shiseido", "Dettol": "Reckitt",
 "Harpic": "Reckitt", "Finish": "Reckitt", "Method": "SC Johnson", "Tarte": "Kose"}
OWNN = {norm(k): v for k, v in OWN.items()}
existing = {}
for b in brands:
    if b.get("parentCompany"): existing.setdefault(norm(b["parentCompany"]), b["parentCompany"])
UA = {"User-Agent": "ahomekind-owner-check/1.0 (ahomekind.com)"}
def wd(**p):
    p["format"] = "json"
    u = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(p)
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=15) as r: return json.load(r)
def owners_of(name):
    ids = [x["id"] for x in wd(action="wbsearchentities", search=name, language="en", limit=5).get("search", [])]
    if not ids: return set()
    ents = wd(action="wbgetentities", ids="|".join(ids), props="claims").get("entities", {})
    oq = set()
    for e in ents.values():
        for prop in ("P749", "P127"):
            for c in e.get("claims", {}).get(prop, []):
                try: oq.add(c["mainsnak"]["datavalue"]["value"]["id"])
                except Exception: pass
    if not oq: return set()
    lab = wd(action="wbgetentities", ids="|".join(list(oq)[:50]), props="labels|aliases", languages="en").get("entities", {})
    out = set()
    for e in lab.values():
        out.add(norm(e.get("labels", {}).get("en", {}).get("value", "")))
        for a in e.get("aliases", {}).get("en", []): out.add(norm(a["value"]))
    return out
rep = []; applied = 0
for b in brands:
    if b.get("parentCompany"): continue
    exp = OWNN.get(nm(b)) or OWNN.get(norm(b.get("name", "")))
    if not exp: continue
    try:
        found = owners_of(b["name"]); time.sleep(0.3)
    except Exception as ex:
        rep.append("NOT CHECKED (no connection) %s" % b["name"]); continue
    key = norm(exp)
    if any(key in f or (len(f) >= 5 and f in key) for f in found):
        b["parentCompany"] = existing.get(key, exp); b["parentSource"] = "Wikidata"; applied += 1
        rep.append("APPLIED %s -> %s" % (b["name"], b["parentCompany"]))
    else:
        rep.append("NOT CONFIRMED %s (expected %s)" % (b["name"], exp))
open("data/owner-report.txt", "w").write("\n".join(rep) + "\n")
print("Owners added (verified):", applied, "| report: data/owner-report.txt")
# 4b. Kimberly-Clark brands (parent says it tests on animals where required by law)
_axe = by.get("axe")
_kc = [("andrex", "Andrex", "Toilet paper and flushable wipes.", []), ("kleenex", "Kleenex", "Tissues.", []), ("huggies", "Huggies", "Nappies and baby wipes.", []),
       ("cottonelle", "Cottonelle", "Toilet paper and wipes.", []), ("kotex", "Kotex", "Period products.", ["period-menstrual"]),
       ("depend", "Depend", "Incontinence products.", []), ("goodnites", "Goodnites", "Bedtime pants for children.", []), ("pull-ups", "Pull-Ups", "Potty training pants.", [])]
if _axe:
    _n = 0
    for sl, nm_, what, cat in _kc:
        if sl in by or any(norm(b.get("name", "")) == norm(nm_) for b in brands): continue
        e = copy.deepcopy(_axe)
        e.update(slug=sl, name=nm_, tier="bad", parentCompany="Kimberly-Clark", parentTestsOnAnimals=True, vegan="unknown", veganConfidence="low",
                 price="£", category=cat, claim="", evidence="", lastVerified=today,
                 note="Owned by Kimberly-Clark, which says it tests on animals where required by law, regulation or government authorities. Kimberly-Clark isn't listed as cruelty-free by PETA. " + what,
                 links=[{"url": "https://kimberly-clark.com/es-us/suppliers/standards-and-requirements/animal-testing", "label": "Kimberly-Clark animal testing statement"},
                        {"url": "https://crueltyfree.peta.org/?s=kimberly-clark", "label": "PETA"}])
        brands.append(e); by[sl] = e; _n += 1
    print("Kimberly-Clark brands added:", _n)
    for sl in ("andrex", "kleenex", "cottonelle", "huggies"): by[sl]["category"] = ["paper-hygiene"]
# 4c. The Cheeky Panda: certified, and the kinder swap for toilet paper and tissues
_cp = by.get("the-cheeky-panda")
if _cp:
    _cp.update(tier="good", vegan="full", veganConfidence="high", claim="", evidence="", lastVerified=today, price="££", category=["paper-hygiene", "body-shower"], stockists=["Waitrose", "Ocado", "Boots", "Tesco", "Morrisons"],
               note="Certified cruelty-free by Cruelty Free International (Leaping Bunny) and certified vegan by The Vegan Society. Bamboo toilet roll, tissues and wipes.",
               links=[{"url": "https://crueltyfreeinternational.org/node/3468", "label": "Cruelty Free International"},
                      {"url": "https://uk.cheekypanda.com/products/bamboo-24-toilet-rolls", "label": "The Cheeky Panda (Vegan Society certified)"}])
    print("Cheeky Panda updated")
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")

# 5. Checker result-card stamps
JS = r'''(function(){
  function norm(s){return (s||"").normalize("NFKD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/&/g,"and").replace(/[^a-z0-9]/g,"");}
  var brands=null,goy={};
  function rules(b){var t=b.tier,n=(b.note||"")+" "+(b.claim||""),o={};
    if(t==="unverified")o.unk=1; if(t==="bad")o.ncf=1; if(b.vegan==="full")o.vegan=1;
    if((t==="good"||t==="check"||t==="warn")&&/Leaping Bunny|Cruelty Free International/.test(n))o.lb=1;
    if((t==="good"||t==="check"||t==="warn")&&/PETA/.test(n))o.peta=1;
    if(goy[b.slug])o.goy=goy[b.slug]; return o;}
  function find(card){
    var hs=card.querySelectorAll(".rcard-name,h1,h2,h3,h4,.rr-name,.rname,strong"),i,k;
    for(i=0;i<hs.length;i++){k=norm(hs[i].textContent);if(k&&brands[k])return {b:brands[k],el:hs[i]};}
    return null;}
  function deco(c){
    if(c.getAttribute("data-ahk"))return; var f=find(c); if(!f)return; c.setAttribute("data-ahk","1");
    var d=document.createElement("div"); d.innerHTML=AHKStamps.row(rules(f.b));
    var t=f.el.closest("a")||f.el,r=d.firstChild;r.style.margin="0 16px 12px";t.parentNode.insertBefore(r,t.nextSibling);}
  var io=window.IntersectionObserver?new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){io.unobserve(e.target);deco(e.target);}});},{rootMargin:"300px"}):null;
  function run(){
    if(!brands||!window.AHKStamps)return;
    document.querySelectorAll(".rcard:not([data-ahk-o]),.card:not([data-ahk-o])").forEach(function(c){
      c.setAttribute("data-ahk-o","1"); if(io)io.observe(c); else deco(c);});}
  Promise.all([fetch("data/brands.json").then(function(r){return r.json()}),
    fetch("data/good-on-you.json").then(function(r){return r.ok?r.json():{}}).catch(function(){return{}})]).then(function(a){
    var l=Array.isArray(a[0])?a[0]:a[0].brands; brands={}; l.forEach(function(b){brands[norm(b.name)]=b;});
    Object.keys(a[1]).forEach(function(k){if(k[0]!=="_")goy[k]=a[1][k];});
    new MutationObserver(run).observe(document.body,{childList:true,subtree:true}); run();
  }).catch(function(){});
})();
'''
open("js/checker-stamps.js", "w", encoding="utf-8").write(JS)
g = "brand-check.html"; gs = open(g, encoding="utf-8").read()
TAGS = '<link rel="stylesheet" href="css/stamps.css"><script src="js/stamps.js"></script><script src="js/checker-stamps.js"></script>'
if "checker-stamps.js" in gs: print("Checker stamps already wired")
elif "</body>" in gs:
    i = gs.rindex("</body>"); open(g, "w", encoding="utf-8").write(gs[:i] + TAGS + gs[i:]); print("Checker stamps wired")
else: print("CHECKER: no </body> found - tell Claude")

# 6. Owner wording: "Independent" only when the note says so, otherwise "Unknown" (short)
g = "scripts/generate-brand-pages.js"; gs = open(g, encoding="utf-8").read(); c0 = gs
if "function ownerWord" not in gs:
    gs = gs.replace("function renderLinks(links) {", """function ownerWord(b) {
  return /independently owned|family[- ]owned|founder[- ]owned|independent (?:\\w+ )?(?:company|brand)/i.test(b.note || '') ? 'Independent' : 'Unknown';
}
function renderChecked(hasLinks) {
  return (hasLinks ? '' : '<p class="section-label">sources &amp; links</p>') + '<p style="font-size:13.5px;">Checked against <a href="https://www.leapingbunny.org" target="_blank" rel="noopener">Leaping Bunny</a>, <a href="https://crueltyfreeinternational.org" target="_blank" rel="noopener">Cruelty Free International</a> and <a href="https://www.peta.org/living/personal-care-fashion/beauty-without-bunnies/" target="_blank" rel="noopener">PETA</a>.</p>';
}
function renderLinks(links) {""", 1)
gs = re.sub(r"line \+= ' &middot; (?:Independent|owner not known yet)';", "line += ' &middot; ' + (ownerWord(brand) === 'Independent' ? 'Independent' : 'owner unknown');", gs)
gs = re.sub(r": '(?:Independent|owner not known)'\) \+ \(p\.price", ": ownerWord(p).toLowerCase() === 'unknown' ? 'owner unknown' : 'independent') + (p.price", gs)
gs = re.sub(r"\(brand\.parentCompany \? escapeHtml\(brand\.parentCompany\) : .*?\) \+ '</dd></div>'", "(brand.parentCompany ? escapeHtml(brand.parentCompany) : ownerWord(brand)) + '</dd></div>'", gs)
gs = gs.replace("if (brand.links && brand.links.length) lines.push('<div class=\"k-sec\">' + renderLinks(brand.links) + '</div>');",
  "lines.push('<div class=\"k-sec\">' + renderLinks(brand.links) + renderChecked(!!(brand.links && brand.links.length)) + '</div>');")
gs = gs.replace("const cat = (brand.category && brand.category[0]) || null;\n  const pool", "const cat = (brand.category && brand.category[0]) || null;\n  if (!cat) return '';\n  const pool", 1)
if gs != c0: open(g, "w", encoding="utf-8").write(gs); print("Owner wording and sources line updated")
else: print("Owner wording and sources line already updated")

# 7. Searching from the homepage no longer scrolls to the bottom of the page
b = "brand-check.html"; bs = open(b, encoding="utf-8").read()
old = "  searchInput.value = term;\n  searchInput.dispatchEvent(new Event('input', { bubbles: true }));\n})();"
new = "  searchInput.value = term;\n  var _was = restoringState; restoringState = true;\n  searchInput.dispatchEvent(new Event('input', { bubbles: true }));\n  restoringState = _was;\n})();"
if old in bs: open(b, "w", encoding="utf-8").write(bs.replace(old, new, 1)); print("Search jump fixed")
else: print("Search jump: already fixed or code changed")

# 8. Friendly "brand not found" screen
b = "brand-check.html"; bs = open(b, encoding="utf-8").read()
OLDNF = '<p id="noResults" style="display:none; text-align:center; color:#80686F; font-size:14px; padding:24px 0;">Nothing here yet for that one.</p>'
NEWNF = '''<div id="noResults" class="ahk-nf" style="display:none" role="status">
<svg class="ahk-nf-i" viewBox="0 0 64 64" width="64" height="64" fill="none" stroke="#3A1F3D" stroke-width="3" stroke-linecap="round" aria-hidden="true"><circle cx="27" cy="27" r="16" fill="#FBE3D3"/><path d="M39 39l14 14"/><path d="M21 27c2-4 10-4 12 0" stroke="#E8804C"/><circle cx="22" cy="23" r="1.5" fill="#3A1F3D"/><circle cx="32" cy="23" r="1.5" fill="#3A1F3D"/></svg>
<p class="ahk-nf-h" id="ahkNfH">Hmm, I haven't got that one yet.</p>
<p class="ahk-nf-p" id="ahkNfP">Tell me the brand and I'll check it for you.</p>
<a class="ahk-nf-b" id="ahkNfB" href="mailto:hello@ahomekind.com?subject=Please%20add%20a%20brand">Send me this brand</a>
<p class="ahk-nf-s">Want to look yourself? Try <a href="https://crueltyfree.peta.org" target="_blank" rel="noopener">PETA</a> or <a href="https://www.leapingbunny.org" target="_blank" rel="noopener">Leaping Bunny</a>.</p>
</div>
<style>.ahk-nf{text-align:center;padding:28px 18px;margin:18px 0;border:2px dashed #E5CFC4;border-radius:20px;background:#FBF4EF;color:#2A1630}
.ahk-nf-i{display:block;margin:0 auto 6px}.ahk-nf-h{font:400 24px/1.2 Gloock,Georgia,serif;margin:6px 0}.ahk-nf-p{margin:0 0 16px;font-size:15px;opacity:.8}
.ahk-nf-b{display:inline-block;background:#3A1F3D;color:#FBF4EF;border-radius:999px;padding:12px 24px;font:600 15px "Hanken Grotesk",system-ui,sans-serif;text-decoration:none}
.ahk-nf-b:hover,.ahk-nf-b:focus-visible{background:#2A1630;outline:3px solid #E8804C;outline-offset:2px}.ahk-nf-s{margin:16px 0 0;font-size:13px;opacity:.75}.ahk-nf-s a{color:inherit}</style>
<script>window.ahkNoResults=function(){var i=document.getElementById('ratingSearch'),t=(i&&i.value||'').trim(),h=document.getElementById('ahkNfH'),p=document.getElementById('ahkNfP'),a=document.getElementById('ahkNfB');if(!h)return;
if(t){h.textContent="Hmm, I haven't got that one yet.";p.textContent="Tell me about \\u201c"+t.slice(0,60)+"\\u201d and I'll check it for you.";a.textContent="Send me this brand";a.href="mailto:hello@ahomekind.com?subject="+encodeURIComponent("Please add a brand: "+t.slice(0,80))+"&body="+encodeURIComponent("Please check this brand: "+t.slice(0,80)+"\\n\\nWhere I buy it (optional): ");}
else{h.textContent="Nothing here yet.";p.textContent="Is there a brand missing? Tell me and I'll check it.";a.textContent="Suggest a brand";a.href="mailto:hello@ahomekind.com?subject=Please%20add%20a%20brand";}};</script>'''
if "ahk-nf" in bs: print("Not-found screen already added")
elif OLDNF in bs:
    bs = bs.replace(OLDNF, NEWNF, 1)
    for old in ["document.getElementById('noResults').style.display = matches.length ? 'none' : 'block';", "document.getElementById('noResults').style.display = (anyVisible || q === '') ? 'none' : 'block';"]:
        bs = bs.replace(old, old + " if (window.ahkNoResults) window.ahkNoResults();")
    open(b, "w", encoding="utf-8").write(bs); print("Not-found screen added")
else: print("Not-found screen: could not find old text")

# 9. Accessibility pass: text contrast, scan button name, fact list markup, keyboard-scrollable strip
import glob as _g
def _rw(path, fn):
    t = open(path, encoding="utf-8").read(); n = fn(t)
    if n != t: open(path, "w", encoding="utf-8").write(n); return 1
    return 0
_col = re.compile(r"#80686f|#88757b|#8c7580", re.I)
changed = 0
for pat in ("css/*.css", "js/*.js", "scripts/generate-*.js", "*.html"):
    for f in _g.glob(pat):
        changed += _rw(f, lambda t: _col.sub("#6A535D", t))
changed += _rw("scripts/generate-brand-pages.js", lambda t: t.replace("<i></i>", ""))
for _n in ("js/nav.js", "js/site.js"):
  changed += _rw(_n, lambda t: t.replace("(active ? ' active' : '') + '\">'", "(active ? ' active' : '') + '\"' + (key === 'scan' ? ' aria-label=\"Scan a barcode\"' : '') + '>'"))
_c2 = {"#c8622f": "#B0501D", "#a0582e": "#8F4E27"}
_col2 = re.compile("|".join(_c2), re.I)
for pat in ("css/*.css", "js/*.js", "scripts/generate-*.js", "*.html"):
    for f in _g.glob(pat):
        changed += _rw(f, lambda t: _col2.sub(lambda m: _c2[m.group(0).lower()], t))
changed += _rw("index.html", lambda t: t.replace("h1 em { font-style:normal; color:#E8804C; }", "h1 em { font-style:normal; color:#C0521F; }"))
changed += _rw("index.html", lambda t: t.replace('<div class="k-strip">', '<div class="k-strip" tabindex="0" role="region" aria-label="Animal facts">', 1) if 'k-strip" tabindex' not in t else t)
A11Y = "/*a11y*/.k-facts dt{flex:1;display:flex;align-items:baseline;gap:8px}.k-facts dt::after{content:\"\";flex:1;border-bottom:1.5px dotted rgba(42,22,48,.25);transform:translateY(-4px)}.ahk-hand,.k-hero em{color:#C0521F}\n"
changed += _rw("css/app.css", lambda t: t if "/*a11y*/" in t else t + "\n" + A11Y)
print("Accessibility fixes applied to", changed, "files")
