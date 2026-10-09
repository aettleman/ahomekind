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

# 6. Brands with no listed owner: say "not known as of <date>" instead of "Independent"
g = "scripts/generate-brand-pages.js"; gs = open(g, encoding="utf-8").read(); c0 = gs
UNK = "(function(){return 'not known as of ' + new Date().toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});})()"
gs = gs.replace("line += ' &middot; Independent';", "line += ' &middot; owner not known yet';")
gs = gs.replace(": 'Independent') + (p.price", ": 'owner not known') + (p.price")
gs = gs.replace(": 'Independent') + '</dd></div>'", ": " + UNK + ") + '</dd></div>'")
if gs != c0: open(g, "w", encoding="utf-8").write(gs); print("Owner wording updated")
else: print("Owner wording already updated")

# 7. Searching from the homepage no longer scrolls to the bottom of the page
b = "brand-check.html"; bs = open(b, encoding="utf-8").read()
old = "  searchInput.value = term;\n  searchInput.dispatchEvent(new Event('input', { bubbles: true }));\n})();"
new = "  searchInput.value = term;\n  var _was = restoringState; restoringState = true;\n  searchInput.dispatchEvent(new Event('input', { bubbles: true }));\n  restoringState = _was;\n})();"
if old in bs: open(b, "w", encoding="utf-8").write(bs.replace(old, new, 1)); print("Search jump fixed")
else: print("Search jump: already fixed or code changed")
