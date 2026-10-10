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
# 4d. Cushelle (Essity) and Pampers (Procter & Gamble)
if _axe and "cushelle" not in by:
    e = copy.deepcopy(_axe)
    e.update(slug="cushelle", name="Cushelle", tier="bad", parentCompany="Essity", parentTestsOnAnimals=True, vegan="unknown", veganConfidence="low",
             price="£", category=["paper-hygiene"], claim="", evidence="", lastVerified=today,
             note="Owned by Essity, which says it tests on animals where the law requires it, such as in parts of China and Brazil, and where the medical device standard ISO 10993 calls for it. Toilet paper.",
             links=[{"url": "https://www.essityusa.com/Images/STM-30765-v4-0-Essity-Position-on-Animal-Testing_tcm341-47956.pdf", "label": "Essity position on animal testing"},
                    {"url": "https://thegoodshoppingguide.com/brand-directory/cushelle", "label": "The Good Shopping Guide"}])
    brands.append(e); by["cushelle"] = e; print("Cushelle added")
if "pampers" in by:
    by["pampers"].update(parentCompany="Procter & Gamble", category=["paper-hygiene"])
    by["pampers"].setdefault("parentTestsOnAnimals", True)

# 4e. Naked Paper and Who Gives A Crap: say they are cruelty-free and vegan, not certified
_NP = [("naked-paper", "Naked Paper", "Europe", "Says its toilet rolls, kitchen rolls and tissues have never been tested on animals and never will be, and that its range is vegan (the glue is pine sap, not animal-derived gelatine).",
        "Says its toilet rolls, kitchen rolls and tissues have never been tested on animals, and that its range is vegan. The glue is pine sap, not animal-derived gelatine. Toilet paper, kitchen roll and tissues.",
        [{"url": "https://uk.nakedpaper.com/blogs/news/are-toilet-rolls-vegan", "label": "Naked Paper: are toilet rolls vegan?"}, {"url": "https://thegoodshoppingguide.com/brand-directory/naked-paper/", "label": "The Good Shopping Guide"}]),
       ("who-gives-a-crap", "Who Gives A Crap", "Australia & New Zealand, Europe, USA & Canada", "Says it doesn't test on animals and that its products are vegan: no virgin trees or animal-derived ingredients, and the glue is just starch and water.",
        "Says it doesn't test on animals and that its products are vegan, with no animal-derived ingredients. Toilet paper, tissues and kitchen roll.",
        [{"url": "https://support.whogivesacrap.org/hc/en-gb/articles/11902182808217-Are-your-products-vegan", "label": "Who Gives A Crap: are your products vegan?"}, {"url": "https://thegoodshoppingguide.com/brand-directory/who-gives-a-crap/", "label": "The Good Shopping Guide"}])]
if _axe:
    for sl, nm_, reg, claim, note, links in _NP:
        if sl in by or any(norm(b.get("name", "")) == norm(nm_) for b in brands): continue
        e = copy.deepcopy(_axe)
        e.update(slug=sl, name=nm_, tier="unverified", parentCompany=None, vegan="full", veganConfidence="medium", category=["paper-hygiene"], region=reg,
                 claim=claim, evidence="", note=note, lastVerified=today, links=links)
        e.pop("price", None); e.pop("parentTestsOnAnimals", None)
        brands.append(e); by[sl] = e; print(nm_, "added")

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
  var brands=null,goy={},gsgd={};
  function rules(b){var t=b.tier,n=(b.note||"")+" "+(b.claim||""),o={};
    if(t==="unverified")o.unk=1; if(t==="bad")o.ncf=1; if(b.vegan==="full")o.vegan=1;
    if((t==="good"||t==="check"||t==="warn")&&/Leaping Bunny|Cruelty Free International/.test(n))o.lb=1;
    if((t==="good"||t==="check"||t==="warn")&&/PETA/.test(n))o.peta=1;
    if(goy[b.slug])o.goy=goy[b.slug]; if(gsgd[b.slug])o.gsg=gsgd[b.slug]; return o;}
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
    fetch("data/good-on-you.json").then(function(r){return r.ok?r.json():{}}).catch(function(){return{}}),
    fetch("data/good-shopping-guide.json").then(function(r){return r.ok?r.json():{}}).catch(function(){return{}})]).then(function(a){
    var l=Array.isArray(a[0])?a[0]:a[0].brands; brands={}; l.forEach(function(b){brands[norm(b.name)]=b;});
    Object.keys(a[1]).forEach(function(k){if(k[0]!=="_")goy[k]=a[1][k];}); Object.keys(a[2]).forEach(function(k){if(k[0]!=="_")gsgd[k]=a[2][k];});
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

# 10. Toilet paper and tissues count as household in the brand checker
g = "scripts/generate-brand-check.js"; gs = open(g, encoding="utf-8").read(); c0 = gs
gs = gs.replace("const HOUSEHOLD_CATS = new Set(['household-cleaning', 'laundry']);", "const HOUSEHOLD_CATS = new Set(['household-cleaning', 'laundry', 'paper-hygiene']);")
gs = gs.replace("  'laundry': 'household',\n", "  'laundry': 'household',\n  'paper-hygiene': 'household',\n", 1) if "'paper-hygiene': 'household'" not in gs else gs
if gs != c0: open(g, "w", encoding="utf-8").write(gs); print("Checker: toilet paper and tissues added under household")

# 11. Consistency report: catches brands that would be hard to find
issues = []
for b in brands:
    if not b.get("category"): issues.append("no category (only shows under 'other'): " + b["name"])
    if b.get("tier") == "good" and b.get("vegan") != "full": issues.append("tier good but vegan not full: " + b["name"])
    if b.get("vegan") == "full" and b.get("tier") == "check": issues.append("vegan full but tier check: " + b["name"])
    if b.get("tier") == "bad" and not b.get("links") and not b.get("parentCompany"): issues.append("tests on animals with no source: " + b["name"])
open("data/consistency-report.txt", "w").write("\n".join(issues) + "\n")
print("Consistency check:", len(issues), "things to look at (data/consistency-report.txt)")

# 12. Friendlier "says it's cruelty-free, not certified yet" look, and those brands can be swaps
g = "scripts/generate-brand-pages.js"; gs = open(g, encoding="utf-8").read(); c0 = gs
gs = gs.replace("const CLAIM_HEADLINE = 'Says it\\'s cruelty-free. Not certified.';", "const CLAIM_HEADLINE = 'Says it\\'s cruelty-free. Not certified yet.';")
gs = re.sub(r"\+ '<p style=\"margin:0;\"><strong style=\"color:#2A1630;\">The reality:</strong>.*?</p>'", 
  "+ '<p style=\"margin:0;\"><strong style=\"color:#2A1630;\">What that means:</strong> ' + escapeHtml(brand.name) + ' isn\\'t certified by Leaping Bunny, Cruelty Free International or PETA yet, so nobody independent has checked this. Plenty of honest brands haven\\'t applied, and some products, like paper goods, don\\'t fit the main schemes well. It\\'s the brand\\'s word, so the choice is yours.</p>'", gs, count=1, flags=re.S)
gs = gs.replace("(STAMP_TEXT[brand.tier] || STAMP_TEXT.unverified)", "(brand.tier === 'unverified' && brand.claim ? '<b>says</b>CF' : (STAMP_TEXT[brand.tier] || STAMP_TEXT.unverified))", 1)
gs = gs.replace("if (b.tier !== 'good' && b.tier !== 'check') return false;\n    if (cat", "if (b.tier !== 'good' && b.tier !== 'check' && !(b.tier === 'unverified' && b.claim)) return false;\n    if (cat", 1)
gs = gs.replace("(y.tier === 'good' ? 1 : 0)) - ((x.price", "(y.tier === 'good' ? 1 : 0) - (y.tier === 'unverified' ? 5 : 0)) - ((x.price", 1)
gs = gs.replace("(x.tier === 'good' ? 1 : 0)); });", "(x.tier === 'good' ? 1 : 0) - (x.tier === 'unverified' ? 5 : 0)); });", 1)
gs = gs.replace("(p.parentCompany ? TIER_SHORT[p.tier] : ownerWord(p)", "(p.tier === 'unverified' ? 'says cruelty-free' : p.parentCompany ? TIER_SHORT[p.tier] : ownerWord(p)", 1)
if gs != c0: open(g, "w", encoding="utf-8").write(gs); print("Says-cruelty-free look updated")
else: print("Says-cruelty-free look already updated")

# 13. Good Shopping Guide scores (second ethical rating, out of 100)
GSGP = "data/good-shopping-guide.json"
GSG = {"naked-paper": 100, "the-cheeky-panda": 93, "who-gives-a-crap": 84, "cushelle": 50, "andrex": 35}
gsg = json.load(open(GSGP)) if os.path.exists(GSGP) else {}
_n = 0
for sl, sc in GSG.items():
    if sl in by and sl not in gsg:
        gsg[sl] = {"score": sc, "url": "https://thegoodshoppingguide.com/brand-directory/%s/" % sl}; _n += 1
json.dump(gsg, open(GSGP, "w"), indent=2); open(GSGP, "a").write("\n")
print("Good Shopping Guide scores added:", _n)
_css = open("css/stamps.css").read()
if ".ahk-g-mid" not in _css:
    open("css/stamps.css", "a").write("\n.ahk-g{--rc:#4C7A3A}.ahk-g-mid{--rc:#8A6A00}.ahk-g-lo{--rc:#B4601F}.ahk-g .ahk-rating-n{width:38px;font-size:14px}\n")

# 14. Small wording fixes
gs = open(g, encoding="utf-8").read(); c1 = gs
gs = gs.replace(".replace('makeup beauty', 'makeup')", ".replace('makeup beauty', 'makeup').replace('paper hygiene', 'toilet paper and tissues')", 1) if "toilet paper and tissues" not in gs else gs
gs = gs.replace("const parentTestFlag = brand.tier === 'unverified'\n", "const parentTestFlag = (brand.tier === 'unverified' && brand.parentCompany)\n", 1)
if gs != c1: open(g, "w", encoding="utf-8").write(gs); print("Category label and parent flag fixed")
for _sl, _note in (("naked-paper", "Toilet paper, kitchen roll and tissues."), ("who-gives-a-crap", "Toilet paper, tissues and kitchen roll.")):
    if _sl in by: by[_sl]["note"] = _note
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")

# 15. No "parent company's testing policy" line for unverified brands that have no parent (checker cards)
g2 = "scripts/generate-brand-check.js"; g2s = open(g2, encoding="utf-8").read()
if "if (brand.tier === 'unverified') {\n    parentNote" in g2s:
    open(g2, "w", encoding="utf-8").write(g2s.replace("if (brand.tier === 'unverified') {\n    parentNote", "if (brand.tier === 'unverified' && brand.parentCompany) {\n    parentNote", 1)); print("Checker parent line fixed")

# 16. Hygiene category (period care, toilet paper, nappies, continence)
raw = json.load(open(P)); by = {b["slug"]: b for b in raw}
_h = 0
for b in raw:
    c = b.get("category") or []
    want = bool({"paper-hygiene", "period-menstrual"} & set(c)) or b["slug"] in ("depend", "goodnites", "pull-ups")
    if want and "hygiene" not in c:
        b["category"] = c + ["hygiene"]; _h += 1
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
g2 = "scripts/generate-brand-check.js"; g2s = open(g2, encoding="utf-8").read(); g2o = g2s
g2s = g2s.replace("  'paper-hygiene': 'household',\n", "  'paper-hygiene': 'hygiene',\n  'hygiene': 'hygiene',\n", 1)
g2s = g2s.replace("  'period-menstrual': 'body-shower',\n", "  'period-menstrual': 'hygiene',\n", 1)
g2s = g2s.replace("new Set(['household-cleaning', 'laundry', 'paper-hygiene'])", "new Set(['household-cleaning', 'laundry', 'paper-hygiene', 'hygiene'])", 1)
if g2s != g2o: open(g2, "w", encoding="utf-8").write(g2s)
bc = open("brand-check.html", encoding="utf-8").read(); bco = bc
bc = bc.replace('<button type="button" class="k-tag" data-cat="mouth-care">Mouth</button>', '<button type="button" class="k-tag" data-cat="mouth-care">Mouth</button><button type="button" class="k-tag" data-cat="hygiene">Hygiene</button>', 1) if 'data-cat="hygiene"' not in bc else bc
bc = bc.replace('<option value="mouth-care">mouth care</option>', '<option value="mouth-care">mouth care</option>\n<option value="hygiene">hygiene (period, toilet paper, nappies)</option>', 1) if 'value="hygiene"' not in bc else bc
bc = bc.replace("{ key: 'mouth-care', icon: '🦷', label: 'mouth care', img: 'cat-mouth.jpg' },", "{ key: 'mouth-care', icon: '🦷', label: 'mouth care', img: 'cat-mouth.jpg' },\n{ key: 'hygiene', icon: '🧻', label: 'hygiene', img: 'cat-body.jpg' },", 1) if "key: 'hygiene'" not in bc else bc
if bc != bco: open("brand-check.html", "w", encoding="utf-8").write(bc)
g3 = "scripts/generate-brand-pages.js"; g3s = open(g3, encoding="utf-8").read(); g3o = g3s
g3s = g3s.replace(".replace('paper hygiene', 'toilet paper and tissues')", ".replace('paper hygiene', 'toilet paper and tissues').replace('period menstrual', 'period care')", 1) if "'period care'" not in g3s else g3s
if g3s != g3o: open(g3, "w", encoding="utf-8").write(g3s)
print("Hygiene category: brands tagged", _h)

# 17. Verified Good Shopping Guide and Good On You scores (each read from the brand's own page, 10 Oct)
_GSG17 = {"aesop": [27, "aesop"], "alberto-balsam": [61, "alberto-balsam"], "always": [25, "always"], "ariel": [13, "ariel"], "arm-and-hammer": [36, "arm-hammer"], "aussie": [30, "aussie"], "avalon-organics": [58, "avalon-organics"], "aveda": [19, "aveda-skincare"], "aveeno": [20, "aveeno"], "avon": [43, "avon-skincare"], "bali-body": [65, "bali-body"], "bareminerals": [18, "bareminerals"], "baylis-and-harding": [69, "baylis-harding"], "beauty-without-cruelty": [91, "beauty-without-cruelty"], "benefit": [22, "benefit"], "bio-d": [98, "bio-d-cleaning-products"], "bobbi-brown": [19, "bobbi-brown"], "bold": [13, "bold"], "bondi-sands": [46, "bondi-sands-sun-protection"], "bulldog": [50, "bulldog"], "burts-bees": [54, "burts-bees"], "cantu": [65, "cantu"], "carex": [62, "carex"], "charles-worthington": [58, "charles-worthington"], "childs-farm": [62, "childs-farm"], "cif": [20, "cif"], "clarins": [43, "clarins-skincare"], "clean-and-clear": [19, "clean-clear"], "clinique": [16, "clinique-skincare"], "colgate": [25, "colgate"], "corsodyl": [21, "corsodyl"], "daise": [69, "daise"], "dame": [98, "dame"], "daz": [54, "daz"], "delphis-eco": [71, "delphis-cleaning-products"], "dettol": [23, "dettol-cleaning-products"], "dior": [22, "dior"], "domestos": [20, "domestos"], "dove": [17, "dove-soap"], "dr-bronners": [79, "dr-bronners"], "dr-hauschka-skin-care": [95, "dr-hauschka-skincare"], "dr-organic": [83, "dr-organic"], "ecoleaf-by-suma": [91, "suma-cleaning-products"], "ecover": [23, "ecover-cleaning-products"], "ecozone": [79, "ecozone-cleaning-products"], "elemis": [36, "elemis"], "elizabeth-arden": [29, "elizabeth-arden"], "elvive": [23, "elvive"], "estee-lauder": [16, "estee-lauder-skincare"], "fairy": [13, "fairy-laundry-detergents"], "faith-in-nature": [91, "faith-in-nature-soap"], "filter-by-molly-mae": [69, "filter-by-molly-mae"], "flash": [13, "flash"], "fushi": [100, "fushi-wellbeing-skincare"], "fussy": [91, "fussy"], "garnier": [31, "garnier-skincare"], "green-people": [100, "green-people-skincare"], "greenscents": [100, "greenscents-cleaning-products"], "hawaiian-tropic": [42, "hawaiian-tropic"], "head-and-shoulders": [27, "head-shoulders"], "herbal-essences": [27, "herbal-essences"], "hismile": [64, "hismile"], "huggies": [32, "huggies"], "imperial-leather": [62, "imperial-leather"], "isle-of-paradise": [73, "isle-of-paradise"], "john-frieda": [46, "john-frieda"], "kerastase": [23, "kerastase"], "kiehl-s": [25, "kiehls"], "kingfisher": [88, "kingfisher-toothpaste"], "kotex": [32, "kotex"], "l-occitane": [36, "loccitane-skincare"], "l-oreal": [22, "loreal-skincare"], "la-roche-posay": [22, "la-roche-posay-skincare"], "lancome": [22, "lancome"], "lavera-naturkosmetik": [81, "lavera-make-up"], "little-soap-company": [91, "little-soap-company"], "liz-earle": [25, "liz-earle"], "love-ethical-beauty": [98, "love-ethical-beauty-skincare"], "lucy-bee": [98, "lucy-bee-soap"], "lush": [84, "lush-skincare"], "lynx": [23, "lynx"], "mac": [16, "mac"], "macleans": [21, "macleans"], "max-factor": [31, "max-factor"], "maybelline": [25, "maybelline"], "method": [27, "method-cleaning-products"], "miniml": [98, "miniml-laundry-detergent"], "mitchum": [15, "mitchum"], "molton-brown": [50, "molton-brown"], "mr-muscle": [27, "mr-muscle"], "mumandyou": [79, "mum-you"], "nars": [34, "nars"], "natracare": [100, "natracare"], "neals-yard-remedies": [100, "neals-yard-remedies-skincare"], "neutrogena": [19, "neutrogena-skincare"], "nivea": [36, "nivea-skincare"], "no7": [22, "no7-skincare"], "nyx": [25, "nyx"], "oceansaver": [75, "oceansaver"], "ogx": [20, "ogx"], "old-spice": [27, "old-spice"], "oral-b": [25, "oral-b"], "original-source": [62, "original-source"], "origins": [19, "origins-skincare"], "palmolive": [27, "palmolive"], "pampers": [21, "pampers"], "pantene": [27, "pantene"], "pearl-drops": [36, "pearl-drops"], "persil": [19, "persil"], "piz-buin": [23, "piz-buin"], "planted-skincare": [85, "planted"], "pledge": [27, "pledge"], "radox": [17, "radox"], "raven-botanicals": [98, "raven-botanicals"], "redken": [23, "redken"], "refy": [64, "refy"], "revlon": [29, "revlon"], "riemann-p20": [77, "riemann-p20"], "right-guard": [61, "right-guard"], "rimmel": [31, "rimmel"], "sally-hansen": [30, "sally-hansen"], "sanex": [27, "sanex"], "schwarzkopf": [19, "schwarzkopf"], "sensodyne": [25, "sensodyne"], "seventh-generation": [19, "seventh-generation"], "simple": [19, "simple"], "smol": [89, "smol-cleaning-products"], "soap-glory": [27, "soap-glory"], "solait-by-superdrug": [60, "solait"], "stardrops": [50, "stardrops"], "supergoop": [38, "supergoop"], "sure": [20, "sure-deodorant"], "surf": [19, "surf"], "tampax": [25, "tampax"], "tan-luxe": [65, "tan-luxe"], "tanorganic": [100, "tanorganic-skincare"], "the-body-shop": [73, "the-body-shop-skincare"], "the-inkey-list": [71, "inkey"], "the-ordinary": [19, "the-ordinary-skincare"], "the-pink-stuff": [50, "the-pink-stuff-cleaning-products"], "too-faced": [19, "too-faced"], "totm": [100, "totm"], "treaclemoon": [61, "treaclemoon"], "tresemm": [17, "tresemme"], "tropic": [100, "tropic-skincare-skincare"], "urban-decay": [25, "urban-decay"], "vegantan": [100, "vegantan"], "vicks": [21, "vicks"], "vosene": [46, "vosene"], "waken": [99, "waken"], "wella": [10, "wella"], "wet-n-wild": [61, "wet-n-wild"], "wild": [32, "wild"], "woolite": [22, "woolite"]}
_GOY17 = {"aveda": [3, "aveda-beauty"], "beauty-kitchen": [4, "beauty-kitchen-beauty"], "covergirl": [2, "covergirl-beauty"], "dr-bronners": [4, "dr-bronner-beauty"], "dr-hauschka-skin-care": [3, "dr-hauschka-beauty"], "ethique": [2, "ethique-beauty"], "gucci": [2, "gucci-beauty"], "herbivore-botanicals": [4, "herbivore-botanicals-beauty"], "kadalys": [4, "kadalys-beauty"], "kora-organics": [4, "kora-organics-beauty"], "krave-beauty": [4, "krave-beauty-beauty"], "la-roche-posay": [3, "la-roche-posay-beauty"], "lancome": [3, "lancome-beauty"], "lucy-bee": [4, "lucy-bee-beauty"], "nyx-professional-makeup": [3, "nyx-professional-makeup-beauty"], "pai-skincare": [4, "pai-skincare-beauty"], "redken": [3, "redken-beauty"], "ren": [3, "ren-beauty"], "tarte-cosmetics": [2, "tarte-beauty"], "tata-harper-skincare": [3, "tata-harper-beauty"], "tropic": [4, "tropic-beauty"], "upcircle-beauty": [4, "upcircle-beauty-beauty"], "youth-to-the-people": [4, "youth-to-the-people-beauty"]}
_gsgd = json.load(open("data/good-shopping-guide.json")); _goyd = json.load(open("data/good-on-you.json")); _a = _b = 0
for _s, (_sc, _u) in _GSG17.items():
    if _s in by and _s not in _gsgd: _gsgd[_s] = {"score": _sc, "url": "https://thegoodshoppingguide.com/brand-directory/" + _u + "/"}; _a += 1
for _s, (_sc, _u) in _GOY17.items():
    if _s in by and _s not in _goyd: _goyd[_s] = {"score": _sc, "url": "https://directory.goodonyou.eco/brand/" + _u}; _b += 1
json.dump(_gsgd, open("data/good-shopping-guide.json", "w"), indent=2); open("data/good-shopping-guide.json", "a").write("\n")
json.dump(_goyd, open("data/good-on-you.json", "w"), indent=2); open("data/good-on-you.json", "a").write("\n")
print("Verified ratings added: Good Shopping Guide", _a, "| Good On You", _b)

# 18. Sources: per-brand "sources" list (never mixes in shop links) and honest wording when there is none
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_ns = 0
def _src(b):
    out = []; n = b.get("note") or ""; ev = b.get("evidence") or ""
    if ev.startswith("http"):
        if "crueltyfree.peta.org/companies-do-test" in ev: out.append({"label": "PETA: companies that test on animals", "url": ev})
        elif "peta.org" in ev: out.append({"label": "PETA: cruelty-free brand list", "url": ev})
        elif "crueltyfreekitty" in ev: out.append({"label": "Cruelty Free Kitty", "url": ev})
        else: out.append({"label": "Source", "url": ev})
    if re.search(r"leaping bunny", n, re.I): out.append({"label": "Leaping Bunny: approved brands (search for the brand)", "url": "https://www.leapingbunny.org/shopping-guide"})
    if re.search(r"cruelty free international", n, re.I): out.append({"label": "Cruelty Free International", "url": "https://crueltyfreeinternational.org"})
    if re.search(r"listed by peta as not testing|peta certified|peta-certified|peta beauty without bunnies", n, re.I): out.append({"label": "PETA Beauty Without Bunnies (search for the brand)", "url": "https://crueltyfree.peta.org/"})
    if re.search(r"vegan society", n, re.I): out.append({"label": "The Vegan Society trademark", "url": "https://www.vegansociety.com/"})
    seen = set(); res = []
    for s in out:
        if s["url"] not in seen: seen.add(s["url"]); res.append(s)
    return res
for b in brands:
    if not b.get("sources"):
        s = _src(b)
        if s: b["sources"] = s; _ns += 1
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Sources added:", _ns, "| still without a source:", sum(1 for b in brands if not b.get("sources")))
g = "scripts/generate-brand-pages.js"; gs = open(g, encoding="utf-8").read(); c0 = gs
if "renderSources" not in gs:
    gs = gs.replace("function renderLinks(links) {", '''function renderSources(b) {
  const s = b.sources || [];
  if (!s.length) {
    const msg = b.tier === 'unverified' ? 'No certification or animal-testing statement could be found for this brand, so its status can\\'t be verified.' : 'No source link has been added for this brand yet.';
    return '<p class="section-label">sources</p><p style="font-size:13.5px;">' + msg + ' Know of one? <a href="mailto:hello@ahomekind.com?subject=source%20for%20' + encodeURIComponent(b.name) + '">Let me know</a>.</p>';
  }
  return '<p class="section-label">sources</p><p style="font-size:13.5px;">' + s.map(function(l){ return '<a href="' + escapeHtml(l.url) + '" target="_blank" rel="noopener">' + escapeHtml(l.label) + '</a>'; }).join(' &middot; ') + '</p>';
}
function renderLinks(links) {''', 1)
    gs = gs.replace("return '<p class=\"section-label\">sources &amp; links</p>\\n<p style=\"font-size:13.5px;\">' + rows", "return '<p class=\"section-label\">where to buy</p>\\n<p style=\"font-size:13.5px;\">' + rows", 1)
    gs = gs.replace("renderLinks(brand.links) + renderChecked(!!(brand.links && brand.links.length))", "renderSources(brand) + renderLinks(brand.links)", 1)
if gs != c0: open(g, "w", encoding="utf-8").write(gs); print("Sources section updated")

# 19. One spelling per parent company (so each gets one parent page, not two)
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw
_PN = {"L'Oreal": "L'Oréal", "Estee Lauder Companies": "Estée Lauder Companies", "Estée Lauder": "Estée Lauder Companies", "Kao": "Kao Corporation", "Reckitt": "Reckitt Benckiser", "S.C. Johnson": "SC Johnson", "P&G": "Procter & Gamble", "Edgewell": "Edgewell Personal Care", "J&J/Kenvue": "J&J / Kenvue"}
_nn = 0
for b in brands:
    pc = b.get("parentCompany")
    if pc in _PN: b["parentCompany"] = _PN[pc]; _nn += 1
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Parent names tidied:", _nn)

# 20. Parent companies' own published animal-testing policies as sources (10 Oct, each page read), and more Good On You scores
_PP = {
"Beiersdorf": "https://reports.beiersdorf.com/annual-report/2023/combined-management-report/non-financial-statement/other-issues.html",
"Church & Dwight": "https://churchdwight.com/our-brands/animal-testing-policy.aspx",
"Clorox": "https://www.thecloroxcompany.com/company/policies-and-practices/animal-testing/",
"Colgate-Palmolive": "https://www.colgatepalmolive.com/en-us/who-we-are/blog/our-commitment-to-animal-welfare",
"Coty": "https://www.coty.com/faq",
"Edgewell Personal Care": "https://cdn.shopify.com/s/files/1/0598/9538/2192/files/Corporate_Animal_Testing_Policy.pdf?v=1724093148",
"Essity": "https://www.essity.com/sustainability/improving-well-being-for-people-and-societies/product-safety-and-transparency/for-us-its-personal/faq/",
"Est\u00e9e Lauder Companies": "https://www.elcompanies.com/en/our-impact/viewpoints/animal-testing",
"Hain Celestial": "https://www.hain.com/wp-content/uploads/ESG/Hain-Animal-Welfare2020.pdf",
"Haleon": "https://www.haleon.com/content/dam/haleon/corporate/documents/who-we-are/governance/Haleon-The-use-of-animals-in-research.pdf.downloadasset.pdf",
"Henkel": "https://www.henkel.com/sustainability/positions/test-methods",
"J&J / Kenvue": "https://kenvue.com/animal-testing-pdf",
"Johnson & Johnson": "https://www.jnj.com/policies-reports/animal-welfare-policy",
"Kao Corporation": "https://www.kao.com/global/en/innovation/safety-quality/animal-testing-policy/",
"Kimberly-Clark": "https://kimberly-clark.com/es-us/suppliers/standards-and-requirements/animal-testing",
"Kos\u00e9 Corporation": "https://koseholdings.co.jp/en/kose/research/secretstory/safety/",
"L'Occitane": "https://group.loccitane.com/sites/default/files/20120806_Statement_from_LOccitane_onAnimal_Testing_EN.pdf",
"L'Or\u00e9al": "https://www.loreal.com/en/commitments-and-responsibilities/for-our-products/for-beauty-with-no-animal-testing/milestones-in-the-safety-assessment-without-animal/",
"OSEA Malibu": "https://oseamalibu.com/pages/cruelty-free-skincare",
"Paul Mitchell": "https://www.paulmitchell.com/pages/faq",
"Procter & Gamble": "https://us.pg.com/cruelty-free/",
"Reckitt Benckiser": "https://www.reckitt.com/media/5833/rb-animal-testing-policy-2019.pdf",
"Revlon": "https://www.revlon.com/pages/animal-testing",
"SC Johnson": "https://scjohnson.com/en/news-stories/official-communications/sc-johnson-point-of-view-on-animal-testing",
"Shiseido": "https://corp.shiseido.com/en/sustainability/consumer/experiment/",
"Unilever": "https://www.unilever.com/files/glo-alternative-approaches-to-animal-testing.pdf"
}
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw
_np = 0
for b in brands:
    u = _PP.get(b.get("parentCompany"))
    if u:
        ss = b.setdefault("sources", [])
        if not any(s.get("url") == u for s in ss):
            ss.append({"label": b["parentCompany"] + ": its own animal testing policy", "url": u}); _np += 1
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
_goyd = json.load(open("data/good-on-you.json")); _nb = 0
for _s, (_sc, _u) in {"avon": [3, "avon-beauty"], "butter-london": [2, "butter-london-beauty"], "byoma": [2, "byoma-beauty"], "carols-daughter": [2, "carols-daughter-beauty"], "colourpop-cosmetics": [2, "colourpop-cosmetics-beauty"]}.items():
    if _s not in _goyd: _goyd[_s] = {"score": _sc, "url": "https://directory.goodonyou.eco/brand/" + _u}; _nb += 1
json.dump(_goyd, open("data/good-on-you.json", "w"), indent=2); open("data/good-on-you.json", "a").write("\n")
print("Parent policy sources added:", _np, "| more Good On You:", _nb)
