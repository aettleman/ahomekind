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

# 21. E45 and Karo Healthcare (Karo's 2025 annual summary and sustainability statement, p.55: "Karo doesn't engage in animal testing unless regulatory authorities require it")
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_KARO = "https://www.karohealthcare.com/wp-content/uploads/2026/04/Karo-Annual-Summary-and-Sustainability-Statement-2025.pdf"
if "e45" in by:
    _e = by["e45"]
    _e.update(tier="bad", parentCompany="Karo Healthcare", parentTestsOnAnimals=True, claim="", lastVerified=today,
              note="Owned by Karo Healthcare, which says it doesn't test on animals unless regulatory authorities require it. That means it can still test on animals where required, so E45 isn't cruelty-free. E45 isn't certified by Leaping Bunny, Cruelty Free International or PETA.",
              sources=[{"label": "Karo Healthcare: annual summary and sustainability statement 2025 (animal welfare, p.55)", "url": _KARO}])
for _b in brands:
    if _b.get("parentCompany") == "Karo Pharma": _b["parentCompany"] = "Karo Healthcare"
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("E45 and Karo Healthcare updated")

# 22. Youth To The People is owned by L'Oréal (L'Oréal press release, announced Dec 2021). Same treatment as NYX / Urban Decay: listed by PETA, parent not cruelty-free
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_LP = "https://www.loreal.com/en/press-release/group/loreal-signs-an-agreement-to-acquire-youth-to-the-people/"
if "youth-to-the-people" in by:
    _y = by["youth-to-the-people"]
    _y.update(tier="warn", parentCompany="L'Oréal", lastVerified=today,
              note="Listed by PETA as not testing on animals, but owned by L'Oréal, which announced the purchase in December 2021. L'Oréal sells in mainland China, where animal testing can still be required, so its parent isn't cruelty-free.",
              sources=[{"label": "PETA Beauty Without Bunnies (search for the brand)", "url": "https://crueltyfree.peta.org/"},
                       {"label": "L'Oréal: press release announcing the purchase of Youth to the People", "url": _LP},
                       {"label": "L'Oréal: its own animal testing policy", "url": "https://www.loreal.com/en/commitments-and-responsibilities/for-our-products/for-beauty-with-no-animal-testing/milestones-in-the-safety-assessment-without-animal/"}])
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Youth To The People updated")

# 23. Brands L'Oréal itself lists as its own in its 2025 annual report (global brands page, read 12 Oct). Licensed fashion names (Prada, Armani, Valentino, Ralph Lauren, Viktor&Rolf, Miu Miu) are NOT set: L'Oréal makes those under licence, so the fashion house isn't owned by L'Oréal
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_AR = "https://www.loreal-finance.com/en/annual-report-2025/global-brands/"
_n = 0
for _s in ("biotherm", "shu-uemura", "helena-rubinstein", "kerastase"):
    if _s in by and not by[_s].get("parentCompany"):
        _b = by[_s]; _b["parentCompany"] = "L'Oréal"; _b["lastVerified"] = today
        _b.setdefault("sources", []).append({"label": "L'Oréal annual report 2025: its global brands", "url": _AR}); _n += 1
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("L'Oréal-owned brands given a parent:", _n)

# 24. Beauty of Joseon (added 12 Oct): says it's cruelty-free on its own FAQ and About pages, no certification found by Ash; five products listed by the brand as containing animal-derived ingredients. Owner not stated on its site, so no parent set.
# Also: Ann Summers note said "to us" (site copy is one person).
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
if "beauty-of-joseon" not in by:
    _boj = {"slug": "beauty-of-joseon", "name": "Beauty of Joseon", "tier": "unverified", "parentCompany": None, "vegan": "partial", "evidence": "", "products": [], "alternatives": [], "links": [], "category": ["skincare"], "veganConfidence": "low", "region": ""}
    brands.append(_boj); by["beauty-of-joseon"] = _boj
by["beauty-of-joseon"].update(
    note="Beauty of Joseon says it's cruelty-free, but it isn't certified by Leaping Bunny, Cruelty Free International or PETA.",
    claim="Its FAQ says all its products are cruelty-free and that it doesn't test on animals. Its About page says it develops all of its products without animal testing.",
    lastVerified=today,
    sources=[{"label": "Beauty of Joseon: its own FAQ (cruelty-free and vegan products)", "url": "https://beautyofjoseon.com/pages/faq-products"},
             {"label": "Beauty of Joseon: its own About page", "url": "https://beautyofjoseon.com/pages/about-page"},
             {"label": "Leaping Bunny: approved brands (search for the brand)", "url": "https://www.leapingbunny.org/shopping-guide"},
             {"label": "PETA Beauty Without Bunnies (search for the brand)", "url": "https://crueltyfree.peta.org/"}])
if "ann-summers" in by:
    by["ann-summers"]["note"] = by["ann-summers"]["note"].replace("It confirmed this to us by email.", "It confirmed this to me by email.")
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Beauty of Joseon added/updated; Ann Summers wording fixed")

# 25. Vanicream and AmLactin (added 12 Oct, from a r/crueltyfree comment): both say they don't test on animals, neither is certified. Owners not set (Vanicream's page names Pharmaceutical Specialties Inc. as the maker; AmLactin's footer names Advantice Health, LLC; neither states "owned by", so no parent page).
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_CERT = [{"label": "Leaping Bunny: approved brands (search for the brand)", "url": "https://www.leapingbunny.org/shopping-guide"},
         {"label": "PETA Beauty Without Bunnies (search for the brand)", "url": "https://crueltyfree.peta.org/"}]
_NEW = {
 "vanicream": dict(name="Vanicream", vegan="unclear",
    note="Vanicream says it doesn't test its products on animals, but it isn't certified by Leaping Bunny, Cruelty Free International or PETA.",
    claim="Its animal testing page says Pharmaceutical Specialties Inc. does not test its products on animals. It doesn't mention suppliers, ingredients or where it sells.",
    sources=[{"label": "Vanicream: its own animal testing page", "url": "https://www.vanicream.com/animal-testing"}] + _CERT),
 "amlactin": dict(name="AmLactin", vegan="partial",
    note="AmLactin says it's cruelty-free, but it isn't certified by Leaping Bunny, Cruelty Free International or PETA.",
    claim="Its FAQ says it is cruelty-free, doesn't test on animals and doesn't sell in markets that require animal testing.",
    sources=[{"label": "AmLactin: its own FAQ (vegan and cruelty-free)", "url": "https://amlactin.com/a/faq"}] + _CERT),
}
for _s, _v in _NEW.items():
    if _s not in by:
        _b = {"slug": _s, "tier": "unverified", "parentCompany": None, "evidence": "", "products": [], "alternatives": [], "links": [], "category": ["skincare"], "veganConfidence": "low", "region": ""}
        brands.append(_b); by[_s] = _b
    by[_s].update(_v, lastVerified=today)
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Vanicream and AmLactin added/updated")

# 26. Biomed (own FAQ, owner SkyLab AG per its FAQ), Avon vegan wording, and a "says it's vegan" stamp
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
if "biomed" in by:
    by["biomed"].update(tier="unverified", parentCompany="SkyLab AG", vegan="partial", veganConfidence="low", lastVerified=today,
        note="Biomed says it's cruelty-free, but it isn't certified by Leaping Bunny, Cruelty Free International or PETA.",
        claim="Its FAQ says its products aren't tested on animals and that its toothpastes and mouthwashes are vegan-friendly.",
        sources=[{"label": "Biomed: its own FAQ (vegan and animal testing)", "url": "https://biomed-pro.com/pages/faq"},
                 {"label": "Leaping Bunny: approved brands (search for the brand)", "url": "https://www.leapingbunny.org/shopping-guide"},
                 {"label": "PETA Beauty Without Bunnies (search for the brand)", "url": "https://crueltyfree.peta.org/"}])
if "avon" in by:
    by["avon"].update(veganBasis="brand", lastVerified=today,
        note="Leaping Bunny certified (Cruelty Free International) since 2024, covering its entire global product range. Avon confirmed to me by email that all of its products are vegan, but it has no vegan certification.")
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
_old_v = 'means: "The brand says its products are vegan, or a vegan certifier backs that up. Vegan status can vary between products, so check the label.", url: null },'
_new_v = ('means: "This brand\'s products are listed as 100% vegan. The source is on the brand page.", url: null },\n'
          '    vegsays: { short: "V", img: null, title: "Says it\'s vegan", who: null,\n'
          '             means: "The brand says all of its products are vegan, but no vegan certification (such as the Vegan Society) has been found. Check the label if you need to be sure.", url: null },')
def _vs(t):
    if "vegsays" in t: return t
    t = t.replace(_old_v, _new_v)
    t = t.replace('["unk", "ncf", "vegan", "lb", "peta"]', '["unk", "ncf", "vegan", "vegsays", "lb", "peta"]')
    t = t.replace('if b.get("vegan") == "full": s.append("vegan")', 'if b.get("vegan") == "full": s.append("vegsays" if b.get("veganBasis") == "brand" else "vegan")')
    return t
_n = _rw("scripts/add_stamps.py", _vs) + _rw("js/stamps.js", _vs)
_n += _rw("js/checker-stamps.js", lambda t: t.replace('if(b.vegan==="full")o.vegan=1;', 'if(b.vegan==="full"){if(b.veganBasis==="brand")o.vegsays=1;else o.vegan=1;}'))
_n += _rw("css/stamps.css", lambda t: t if "ahk-stamp-vegsays" in t else t + "\n.ahk-stamp-vegsays{background:#F4E6DE;color:#3A1F3D;border-style:dashed}\n")
_n += _rw("scripts/generate-brand-pages.js", lambda t: t.replace("brand.vegan === 'full' ? '100% vegan'\n", "brand.vegan === 'full' ? (brand.veganBasis === 'brand' ? \"100% vegan (brand's word)\" : '100% vegan')\n", 1))
print("Biomed and Avon updated; vegan stamp files changed:", _n)

# 27. Certified vegan stamp (Biomed: V-Label, from the V-Label logo on its packs, Ash 12 Oct). veganBasis: "certified" (+ veganCert name) / "brand" (brand's word) / unset (old generic text)
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
if "biomed" in by:
    _bm = by["biomed"]; _bm.update(vegan="full", veganConfidence="high", veganBasis="certified", veganCert="V-Label", lastVerified=today)
    if not any("V-Label" in s.get("label", "") for s in _bm.get("sources", [])):
        _bm.setdefault("sources", []).append({"label": "V-Label: the vegan certification shown on its packs", "url": "https://www.v-label.com"})
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
def _vc(t):
    if "vegcert" in t: return t
    t = t.replace('    lb:    { short: "LB",', '    vegcert: { short: "V", img: null, title: "Certified vegan", who: null,\n             means: "A vegan certifier, such as the Vegan Society or V-Label, has certified this brand\'s products. The certifier is named on the brand page.", url: null },\n    lb:    { short: "LB",', 1)
    t = t.replace('["unk", "ncf", "vegan", "vegsays", "lb", "peta"]', '["unk", "ncf", "vegan", "vegcert", "vegsays", "lb", "peta"]')
    t = t.replace('s.append("vegsays" if b.get("veganBasis") == "brand" else "vegan")', 's.append("vegcert" if b.get("veganBasis") == "certified" else "vegsays" if b.get("veganBasis") == "brand" else "vegan")')
    return t
_n = _rw("scripts/add_stamps.py", _vc) + _rw("js/stamps.js", _vc)
_n += _rw("js/checker-stamps.js", lambda t: t.replace('if(b.veganBasis==="brand")o.vegsays=1;else o.vegan=1;', 'if(b.veganBasis==="brand")o.vegsays=1;else if(b.veganBasis==="certified")o.vegcert=1;else o.vegan=1;') if "vegcert" not in t else t)
_n += _rw("css/stamps.css", lambda t: t if "ahk-stamp-vegcert" in t else t + ".ahk-stamp-vegcert{background:#3A1F3D;color:#F4E6DE}\n")
_n += _rw("scripts/generate-brand-pages.js", lambda t: t if "(certified by " in t else t.replace("(brand.veganBasis === 'brand' ?", "(brand.veganBasis === 'certified' ? '100% vegan (certified by ' + escapeHtml(brand.veganCert || 'a vegan certifier') + ')' : brand.veganBasis === 'brand' ?", 1))
print("Biomed certified vegan; vegan certified stamp files changed:", _n)

# 28. Checker's certification filter: "Vegan certification" (Vegan Society, V-Label and others), not just the Vegan Society
_n = _rw("brand-check.html", lambda t: t.replace('<option value="vegan-society">Vegan Society certified</option>', '<option value="vegan-cert">Vegan certification</option>')
         .replace("certs.push('vegan-society')", "certs.push('vegan-cert')")
         .replace("if (/\\bvegan society\\b/.test(noteLower))", "if (/\\bvegan society\\b|\\bv-label\\b/.test(noteLower))")
         .replace("card.dataset.cert = certs.join(' ');", "if (card.dataset.vegcert === '1' && certs.indexOf('vegan-cert') === -1) certs.push('vegan-cert');\ncard.dataset.cert = certs.join(' ');") if "dataset.vegcert" not in t else t)
_n += _rw("scripts/generate-brand-check.js", lambda t: t if "data-vegcert" in t else t.replace("""(dataRegion ? ' data-region="' + dataRegion + '"' : '') + '>' +""", """(dataRegion ? ' data-region="' + dataRegion + '"' : '') + (brand.veganBasis === 'certified' ? ' data-vegcert="1"' : '') + '>' +""", 1))
print("Checker vegan certification filter files changed:", _n)

# 29. Vegan certification checks by Ash (12 Oct), for the brands in the checker's "Vegan certification" filter. Certifier recorded as Ash found it.
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_VS = "Vegan Society"
for _s in ("bio-d", "little-soap-company", "miniml", "original-source", "phb-ethical-beauty", "salt-of-the-earth", "the-pink-stuff"):
    if _s in by:
        by[_s].update(veganBasis="certified", veganCert=_VS, lastVerified=today)
if "the-pink-stuff" in by:
    by["the-pink-stuff"]["note"] = "Leaping Bunny certified worldwide, and its products are certified vegan by the Vegan Society."
if "the-cheeky-panda" in by:   # added 10 Oct; date it was added, as Ash asked
    by["the-cheeky-panda"].update(veganBasis="certified", veganCert=_VS, lastVerified="2026-10-10")
if "e-l-f-cosmetics" in by:
    _e = by["e-l-f-cosmetics"]
    _e.update(veganBasis="certified", veganCert="PETA", lastVerified=today,
              note="Independently owned. Certified cruelty-free and vegan by PETA (Beauty Without Bunnies).",
              sources=[{"label": "PETA Beauty Without Bunnies (search for the brand)", "url": "https://crueltyfree.peta.org/"}])
if "kingfisher" in by:
    _k = by["kingfisher"]
    _k.update(vegan="full", veganConfidence="medium", veganBasis="brand", lastVerified=today,
              note="Cruelty-free and BUAV certified in the UK, independent toothpaste brand. It says its range is 100% vegan, but no vegan certification has been found.",
              sources=[s for s in _k.get("sources", []) if "vegansociety" not in s.get("url", "")])
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Vegan certification checks recorded")

# 30. Checker filter: "Says it's vegan (not certified)" for brands whose vegan claim is the brand's own word (veganBasis "brand"). Brands with the old generic stamp join once Ash classifies them.
_OPT = '<option value="vegan-says">Says it\'s vegan (not certified)</option>'
def _vsay(t):
    if "vegan-says" in t: return t
    t = t.replace('<option value="vegan-cert">Vegan certification</option>', '<option value="vegan-cert">Vegan certification</option>\n' + _OPT, 1)
    t = t.replace("card.dataset.cert = certs.join(' ');", "if (card.dataset.vegsays === '1') certs.push('vegan-says');\ncard.dataset.cert = certs.join(' ');", 1)
    return t
_n = _rw("brand-check.html", _vsay)
_n += _rw("scripts/generate-brand-check.js", lambda t: t if "data-vegsays" in t else t.replace("""(brand.veganBasis === 'certified' ? ' data-vegcert="1"' : '') +""", """(brand.veganBasis === 'certified' ? ' data-vegcert="1"' : '') + (brand.veganBasis === 'brand' ? ' data-vegsays="1"' : '') +""", 1))
print("Checker 'says it's vegan' filter files changed:", _n)

# 31. Original Source: its own "Vegan and PETA approved" page (read 12 Oct) says every product has carried the Vegan Society logo since 2003, and that it is PETA approved (Beauty without Bunnies). Ash confirmed. Whole range is vegan, so moved from "check" to "good".
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
if "original-source" in by:
    _o = by["original-source"]; _OU = "https://www.original-source.com/uk/about-us/vegan-peta-approved/"
    _o.update(tier="good", vegan="full", veganConfidence="high", veganBasis="certified", veganCert="Vegan Society", lastVerified=today,
              note="PETA approved, and every product carries the Vegan Society logo (since 2003), according to its own page.")
    if not any(s.get("url") == _OU for s in _o.get("sources", [])):
        _o.setdefault("sources", []).insert(0, {"label": "Original Source: its own Vegan and PETA approved page", "url": _OU})
    if not any("peta.org" in s.get("url", "") for s in _o["sources"]):
        _o["sources"].append({"label": "PETA Beauty Without Bunnies (search for the brand)", "url": "https://crueltyfree.peta.org/"})
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Original Source updated")

# 32. Owners added from sources read 12 Oct (Ash supplied the list; each owner checked against a company or press-release page).
#     Not set: Anna Sui (no ownership source found; make-up is made under licence by Albion). Aveeno, Neutrogena, Listerine, Johnson's, Band-Aid and OGX now sit under Kenvue (Kenvue's own brand pages), not Johnson & Johnson.
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
def _own(slug, parent, note, label, url, drop_label=None):
    b = by.get(slug)
    if not b: return
    b["parentCompany"] = parent; b["lastVerified"] = today
    if note: b["note"] = note
    srcs = [s for s in b.get("sources", []) if not (drop_label and drop_label in s.get("label", ""))]
    if not any(s.get("url") == url for s in srcs): srcs.append({"label": label, "url": url})
    b["sources"] = srcs
_PETA = "Listed by PETA as a company that tests on animals."
_own("acuvue", "Johnson & Johnson", "Owned by Johnson & Johnson. " + _PETA, "Acuvue: its own About page (published by Johnson & Johnson Vision)", "https://www.acuvue.com/en-ca/about/")
_CD = "https://churchdwight.com/our-brands/consumer-brands/"
_own("aim", "Church & Dwight", "Owned by Church & Dwight. " + _PETA, "Church & Dwight: its consumer brands page", _CD)
_own("arrid", "Church & Dwight", "Owned by Church & Dwight. " + _PETA, "Church & Dwight: its consumer brands page", _CD)
_own("algenist", "Tengram Capital Partners", "Tengram Capital Partners, a private equity firm, bought a majority stake in 2016. " + _PETA, "Tengram Capital Partners: its 2016 announcement of the Algenist purchase", "https://tengramcapital.com/pressArticles/fundNews/tengram-capital-partners-press-080216.html")
_own("ambi", "L'Oréal", "Owned by L'Oréal, which bought it from Valeant in 2017. " + _PETA, "L'Oréal: press release on finalising the purchase of CeraVe, AcneFree and Ambi (6 March 2017)", "https://www.loreal-finance.com/eng/news-release/loreal-finalizes-acquisition-cerave-acnefree-and-ambi")
_own("aqua-di-parma", "LVMH", "Owned by LVMH. " + _PETA, "LVMH: its Acqua di Parma page", "https://www.lvmh.com/en/our-maisons/perfumes-cosmetics/acqua-di-parma")
if "aqua-di-parma" in by: by["aqua-di-parma"]["name"] = "Acqua di Parma"
_own("aramis", "Estée Lauder Companies", "Owned by the Estée Lauder Companies. " + _PETA, "Estée Lauder Companies: its Aramis page", "https://www.elcompanies.com/en/our-brands/aramis")
_own("atelier-cologne", "L'Oréal", "Owned by L'Oréal, which signed the agreement to buy it in 2016. " + _PETA, "L'Oréal: press release on the Atelier Cologne purchase (30 June 2016)", "https://www.loreal-finance.com/eng/news-release/loreal-signs-agreement-acquire-atelier-cologne")
_own("bain-de-soleil", "MY Imports USA (AMG Brands)", "MY Imports USA (AMG Brands) agreed to buy it in November 2024. " + _PETA, "MY Imports USA: its press release on buying Bain de Soleil", "https://www.businesswire.com/news/home/20241114635589/en")
_own("balenciaga", "Kering", "Owned by Kering. " + _PETA, "Wikipedia: Balenciaga (owned by Kering)", "https://en.wikipedia.org/wiki/Balenciaga")
_KB = "https://www.kenvue.com/brands"; _KP = "https://www.kenvue.com/policies-positions/animal-testing"
for _s in ("aveeno", "neutrogena", "listerine", "johnson-s", "band-aid", "ogx"):
    if _s in by:
        _kn = "Owned by Kenvue, which avoids animal testing for cosmetics unless regulators require it."
        if _s == "ogx": _kn = by[_s]["note"].replace("J&J/Kenvue", "Kenvue")
        _own(_s, "Kenvue", _kn, "Kenvue: its brands page", _KB, drop_label="Johnson & Johnson")
        if not any(s.get("url") == _KP for s in by[_s]["sources"]): by[_s]["sources"].append({"label": "Kenvue: its position on animal testing", "url": _KP})
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
def _kpol(t):
    if '"Kenvue":' in t: return t
    return t.replace('"Church & Dwight": {', '"Kenvue": {"url": "https://www.kenvue.com/policies-positions/animal-testing", "summary": "Kenvue says it avoids animal testing for cosmetics unless regulators require it. For medicines and other regulated health products it treats animal testing as a last resort, and it notes that some countries still require animal testing data to meet their own regulatory requirements."},\n"Church & Dwight": {', 1)
_rw("scripts/site_update.py", _kpol)
print("Owners added for brands from Ash's 12 Oct list")

# 33. Leaping Bunny and Cruelty Free International read as one programme everywhere, plus an explanation on How I decide
_LBO = "Leaping Bunny, Cruelty Free International or PETA"; _LBN = "Leaping Bunny / Cruelty Free International or PETA"
_LBO2 = "PETA, Leaping Bunny or Cruelty Free International"; _LBN2 = "PETA or Leaping Bunny / Cruelty Free International"
def _lbw(t):
    return (t.replace(_LBO, _LBN).replace(_LBO2, _LBN2)
             .replace("the Leaping Bunny, Cruelty Free International and PETA lists", "the Leaping Bunny / Cruelty Free International and PETA lists")
             .replace("I couldn't find a Leaping Bunny or PETA certification", "I couldn't find a Leaping Bunny / Cruelty Free International or PETA certification"))
_n = 0
for _pat in ("*.html", "js/*.js", "scripts/generate-*.js", "scripts/build-kind-list.py", "scripts/site_update.py", "data/brands.json", "data/products.json"):
    for _f in _g.glob(_pat):
        if _f.startswith("brands/"): continue
        _n += _rw(_f, _lbw)
_LBX = ('+ H2 % "Leaping Bunny and Cruelty Free International" + "<p>I treat these as one certification, because a certified brand can be listed on either website. Cruelty Free International is based in the UK and certifies brands headquartered outside the US and Canada. In the US and Canada, Leaping Bunny is run through CCIC, a coalition of animal protection groups. In March 2026 Cruelty Free International renamed its approval programme and gave it a new logo, and it says the approval criteria are unchanged. So you may see either logo on a pack.</p>"\n ')
def _lbx(t):
    if "Leaping Bunny and Cruelty Free International" in t: return t
    return t.replace(' + H2 % "Mistakes"', ' ' + _LBX + '+ H2 % "Mistakes"', 1)
_n += _rw("scripts/site_update.py", _lbx)
print("Leaping Bunny / Cruelty Free International wording unified; files changed:", _n)

# 34. Owners batch 2 (Ash's list, 12 Oct), each checked against a company or press-release page.
#     Not changed: Bedhead, Biotherm, Bobbi Brown, Bold, Bourjois (already correct). Cacharel: Cacharel licenses its perfumes to L'Oréal (FashionNetwork, 2015) but no page read says who owns Cacharel, so no parent set. Burberry: public company, no parent.
#     Air Wick, Cillit Bang, Woolite still say Reckitt Benckiser, but Reckitt sold its Essential Home division (Air Wick, Calgon, Woolite, Cillit Bang...) to Advent International on 31 Dec 2025, keeping 30%. Left for Ash to decide because their tier rests on Reckitt's policy.
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_PE = "Listed by PETA as a company that tests on animals."
_own("bausch-lomb", "Bausch Health Companies", "About 87% owned by Bausch Health Companies (April 2026). " + _PE, "SEC filing: Bausch Health Companies holds about 87% of Bausch + Lomb (April 2026)", "https://www.sec.gov/Archives/edgar/data/1860742/000186074226000062/R8.htm")
_own("beiersdorf", "Maxingvest", "Maxingvest holds 54.4% of Beiersdorf's shares, according to Beiersdorf's own shareholder page. " + _PE, "Beiersdorf: its shareholder structure", "https://www.beiersdorf.com/investor-relations/shares/shareholder-structure")
_own("bengay", "Kenvue", "Owned by Kenvue, which avoids animal testing for cosmetics unless regulators require it.", "Bengay: its legal notice (published by Kenvue Brands LLC)", "https://www.bengay.com/legal-notice")
if "bengay" in by and not any(s.get("url") == _KP for s in by["bengay"]["sources"]): by["bengay"]["sources"].append({"label": "Kenvue: its position on animal testing", "url": _KP})
_BIC = "https://investors.bic.com/en-us/bic-at-a-glance"; _BN = "Société BIC is publicly traded, and the founding Bich family holds 46% of its capital and 60% of its voting rights (30 June 2026). "
_own("bic", "Société BIC", _BN + by.get("bic", {}).get("note", "").replace(_BN, ""), "BIC: its shareholder structure", _BIC)
_own("bic-corporation", "Société BIC", _BN + _PE, "BIC: its shareholder structure", _BIC)
_own("biotene", "Haleon", "Owned by Haleon. " + _PE, "Haleon: its Biotene page", "https://www.haleonhealthpartner.com/en-us/oral-health/brands/biotene/products/")
_own("blue-buffalo", "General Mills", "Owned by General Mills, which completed the purchase in April 2018. " + _PE, "General Mills: press release on completing the Blue Buffalo purchase", "https://investors.generalmills.com/press-releases/press-release-details/2018/General-Mills-Completes-Acquisition-of-Blue-Buffalo-Pet-Products/default.aspx")
for _s in ("bounce", "bounty", "braun"):
    _own(_s, "Procter & Gamble", "Owned by Procter & Gamble. " + _PE, "Procter & Gamble: its brands page", "https://us.pg.com/brands/")
_own("breathe-right", "Prestige Consumer Healthcare", "Prestige Consumer Healthcare completed the purchase in June 2026. " + _PE, "Prestige Consumer Healthcare: press release on completing the Breathe Right purchase (15 June 2026)", "https://ir.prestigebrands.com/news-releases/news-release-details/prestige-consumer-healthcare-inc-completes-acquisition-breathe")
_own("bvlgari-parfums", "LVMH", "Owned by LVMH. " + _PE, "LVMH: its Bvlgari page", "https://www.lvmh.com/en/our-maisons/watches-jewelry/bulgari")
_own("calvin-klein-cosmetics", "Coty", "Calvin Klein Fragrances is a division of Coty. Calvin Klein itself is owned by PVH, whose animal welfare policy bans fur, angora, mohair and exotic skins but still allows wool and certified down. " + _PE, "Coty: press release naming Calvin Klein Fragrances as a division of Coty", "https://www.coty.com/news/calvin-klein-fragrances-announces-the-return-of-christy-turlington-burns-and-edward-burns")
if "calvin-klein-cosmetics" in by:
    _pu = "https://www.pvh.com/-/media/Files/pvh/responsibility/PVH-Animal-Welfare-Policy-Statement.pdf"
    if not any(s.get("url") == _pu for s in by["calvin-klein-cosmetics"]["sources"]): by["calvin-klein-cosmetics"]["sources"].append({"label": "PVH: its animal welfare policy statement", "url": _pu})
_EH = "Essential Home (Advent International)"; _EHS = [("Reckitt: announcement that Advent International bought Essential Home (completed 31 December 2025)", "https://reckitt.com/news/reckitt-completes-divestment-of-essential-home/"), ("Reckitt: announcement of the Essential Home sale, naming Air Wick, Calgon, Woolite and Cillit Bang", "https://www.investegate.co.uk/announcement/rns/reckitt-benckiser-group--rkt/reckitt-agrees-to-divest-essential-home/8985772")]
for _s in ("calgon", "calgon-water-softener"):
    if _s in by:
        _b = by[_s]; _b["parentCompany"] = _EH; _b["lastVerified"] = today
        _b["note"] = ("Owned by Essential Home, which Advent International bought from Reckitt (completed 31 December 2025). Reckitt kept a 30% stake. " + _b["note"]) if "Essential Home" not in _b["note"] else _b["note"]
        for _l, _u in _EHS:
            if not any(s.get("url") == _u for s in _b["sources"]): _b["sources"].append({"label": _l, "url": _u})
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Owners batch 2 added")

# 35. Essential Home (Reckitt sold it to Advent International, completed 31 Dec 2025) and tidying from Ash's review (12 Oct)
#     Calgon is two different products: the bath and body line (PDC Brands, per Yellow Wood's own article) and the water softener (Reckitt's Essential Home). Both stay listed, each with its own owner.
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_RKP = "https://www.reckitt.com/media/5833/rb-animal-testing-policy-2019.pdf"
_EHN = "Owned by Essential Home since 31 December 2025, when Advent International bought it from Reckitt (which kept a 30% stake). "
_EHP = " I haven't confirmed Essential Home's own animal testing policy."
for _s, _extra in (("air-wick", "Reckitt's policy, which applied while it owned the brand, says it tests where regulators require it."),
                   ("woolite", "Listed by PETA as a company that tests on animals. Reckitt's policy, which applied while it owned the brand, says it tests where regulators require it."),
                   ("cillit-bang", "Reckitt's policy, which applied while it owned the brand, says it tests where regulators require it.")):
    if _s in by:
        _b = by[_s]; _b["parentCompany"] = _EH; _b["lastVerified"] = today
        _b["note"] = _EHN + _extra + _EHP
        for s in _b["sources"]:
            if s.get("url") == _RKP: s["label"] = "Reckitt Benckiser: its animal testing policy (previous owner)"
        for _l, _u in _EHS:
            if not any(s.get("url") == _u for s in _b["sources"]): _b["sources"].append({"label": _l, "url": _u})
if "calgon" in by:
    _c = by["calgon"]; _c["name"] = "Calgon bath & body"; _c["parentCompany"] = "PDC Brands"; _c["lastVerified"] = today
    _c["note"] = "Calgon's bath and body line is part of PDC Brands. The Calgon water softener is a separate product, listed separately. Listed by PETA as not testing on animals."
    _c["sources"] = [s for s in _c["sources"] if "Reckitt" not in s.get("label", "")]
    if not any("yellowwood" in s.get("url", "") for s in _c["sources"]):
        _c["sources"].append({"label": "Yellow Wood Partners: article naming Calgon as part of PDC Brands", "url": "https://www.yellowwoodpartners.com/news-article/parfums-de-coeur-eyes-expansion-with-new-name-headquarters-"})
if "cacharel" in by:
    _k = by["cacharel"]; _k["lastVerified"] = today
    _k["note"] = "Cacharel licenses its perfumes to L'Oréal, which sells in mainland China, where animal testing can still be required. I couldn't find who owns Cacharel itself. Listed by PETA as a company that tests on animals."
    for _l, _u in (("FashionNetwork: Cacharel renews its perfume licence with L'Oréal (2015)", "https://uk.fashionnetwork.com/news/Cacharel-extends-partnership-with-l-oreal,551817.html"),
                   ("L'Oréal: its own animal testing policy", "https://www.loreal.com/en/commitments-and-responsibilities/for-our-products/for-beauty-with-no-animal-testing/milestones-in-the-safety-assessment-without-animal/")):
        if not any(s.get("url") == _u for s in _k["sources"]): _k["sources"].append({"label": _l, "url": _u})
if "burberry" in by:
    by["burberry"]["note"] = "I couldn't find a parent company for Burberry. Listed by PETA as a company that tests on animals."; by["burberry"]["lastVerified"] = today
if "blue-buffalo" in by:
    by["blue-buffalo"]["category"] = ["pet-food"]
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Essential Home brands moved; Calgon, Cacharel, Burberry, Blue Buffalo tidied")

# 36. e.l.f. Beauty, Inc. (NYSE: ELF) owns e.l.f. Cosmetics, Naturium and rhode, per its own 10-K (FY ended 31 Mar 2026, read 12 Oct), which also says Keys Soulcare was transferred to Alicia Keys in May 2026 (so Keys Soulcare is NOT given e.l.f. as parent).
#     Replaced the unsourced "Independently owned" on e.l.f. Cosmetics. Whether any single holder controls e.l.f. Beauty was not checked, so the site only says it's publicly traded.
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_EL = "e.l.f. Beauty"; _ELU = "https://www.sec.gov/Archives/edgar/data/1600033/000160003326000020/elf-20260331.htm"
for _s in ("e-l-f-cosmetics", "naturium", "rhode-skin"):
    if _s in by:
        _b = by[_s]; _b["parentCompany"] = _EL; _b["lastVerified"] = today
        if not any(s.get("url") == _ELU for s in _b["sources"]): _b["sources"].append({"label": "e.l.f. Beauty: its annual report (10-K, year to 31 March 2026)", "url": _ELU})
if "e-l-f-cosmetics" in by:
    by["e-l-f-cosmetics"]["note"] = "Owned by e.l.f. Beauty, Inc., a publicly traded company (NYSE: ELF). Certified cruelty-free and vegan by PETA (Beauty Without Bunnies)."
for _s in ("naturium", "rhode-skin"):
    if _s in by and "e.l.f. Beauty" not in by[_s]["note"]: by[_s]["note"] = "Owned by e.l.f. Beauty, Inc. " + by[_s]["note"]
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
def _elpol(t):
    if '"e.l.f. Beauty":' in t: return t
    return t.replace('"Church & Dwight": {', '"e.l.f. Beauty": {"url": "https://www.sec.gov/Archives/edgar/data/1600033/000160003326000020/elf-20260331.htm", "summary": "In its annual report e.l.f. Beauty describes e.l.f. Cosmetics as double-certified by Leaping Bunny and PETA as cruelty-free, and says it was one of the first mass beauty brands to be vegan and cruelty free. This is the company describing its own brands."},\n"Church & Dwight": {', 1)
_rw("scripts/site_update.py", _elpol)
print("e.l.f. Beauty added as parent of e.l.f. Cosmetics, Naturium and rhode")

# 37. e.l.f. Cosmetics: cruelty-free certified by Leaping Bunny and PETA; vegan certified by PETA (Ash checked 13 Oct; e.l.f. Beauty's 10-K also says "double-certified by Leaping Bunny and PETA")
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
if "e-l-f-cosmetics" in by:
    _e = by["e-l-f-cosmetics"]; _e["lastVerified"] = today
    _e["note"] = "Owned by e.l.f. Beauty, Inc., a publicly traded company (NYSE: ELF). Certified cruelty-free by Leaping Bunny and PETA, and certified vegan by PETA (Beauty Without Bunnies)."
    _lb = "https://www.leapingbunny.org/shopping-guide"
    if not any(s.get("url") == _lb for s in _e["sources"]): _e["sources"].insert(0, {"label": "Leaping Bunny: approved brands (search for the brand)", "url": _lb})
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("e.l.f. Cosmetics certifications updated")

# 38. Batch from Ash (13 Oct): new brands (Tesco, Asda, Cocokind, Necessaire), owners (Origins, Coppertone, Marc Jacobs, St Ives, Radox), the "no information + parent tests = tests on animals" rule, and a visible "Does X test on animals?" answer on every brand page.
#     St Ives is NOT owned by Unilever any more: Yellow Wood Partners bought it (via Elida Beauty) and it now sits in Evermark (Yellow Wood release, 20 Jan 2026; Glossy).
#     Necessaire stays "not certified either way": the claim that it tests on animals (sex gel) could not be verified from any page, so it is not on the site.
#     Marc Jacobs: Ash's claims about WHP Global's and G-III's own animal testing / materials policies are not on any page read (the G-III document only mentions animal welfare in passing), so they are left out.
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
def _new(slug, name, tier, note, **kw):
    b = {"slug": slug, "name": name, "tier": tier, "note": note, "parentCompany": kw.get("parent"), "vegan": kw.get("vegan", "unknown"), "evidence": "", "products": [], "alternatives": [], "links": [],
         "category": kw.get("category", ["skincare"]), "veganConfidence": kw.get("vc", "low"), "region": kw.get("region", ""), "claim": kw.get("claim", ""), "lastVerified": today, "sources": kw["sources"]}
    if kw.get("price"): b["price"] = kw["price"]
    if slug not in by: brands.append(b); by[slug] = b
    return by[slug]
_LBG = {"label": "Leaping Bunny: approved brands (search for the brand)", "url": "https://www.leapingbunny.org/shopping-guide"}
_PETAB = {"label": "PETA Beauty Without Bunnies (search for the brand)", "url": "https://crueltyfree.peta.org/"}
_new("tesco", "Tesco", "unverified", "Tesco says it doesn't test on animals, but its own-brand beauty and toiletries aren't certified by Leaping Bunny / Cruelty Free International or PETA.",
     claim="Tesco says it doesn't support, commission or carry out animal testing on any of its products or the ingredients in them, and that its suppliers don't test on its behalf.",
     category=["makeup-beauty", "skincare", "body-shower", "household-cleaning"], region="Europe", price="£",
     sources=[{"label": "Tesco: its animal health and welfare report 2024/25 (position on animal testing)", "url": "https://www.tescoplc.com/media/pl5brzss/animal-health-welfare-report_202425.pdf"}, _LBG, _PETAB])
_new("asda", "Asda", "unverified", "Asda says it doesn't test its own-brand beauty, toiletries or household products on animals, but they aren't certified by Leaping Bunny / Cruelty Free International or PETA.",
     claim="Asda says it doesn't conduct or commission animal tests on its own-brand beauty, toiletry or household products, and doesn't ask suppliers or anyone else to. It says this applies from fixed cut-off dates: 31 December 2009 for cosmetics and 31 December 2015 for cleaning products.",
     category=["makeup-beauty", "skincare", "body-shower", "household-cleaning"], region="Europe", price="£",
     sources=[{"label": "Asda: its animal welfare page (position on animal testing)", "url": "https://corporate.asda.com/animal-welfare"}, _LBG, _PETAB])
_new("cocokind", "cocokind", "check", "Certified cruelty-free by Leaping Bunny. Its FAQ says all products are vegan except its beeswax ones.",
     vegan="partial", vc="high", region="USA & Canada", price="££",
     sources=[{"label": "Leaping Bunny: its cocokind listing", "url": "https://www.leapingbunny.org/brand/cocokind"}, {"label": "cocokind: its FAQ (vegan products)", "url": "https://www.cocokind.com/pages/faqs"}])
_new("necessaire", "Nécessaire", "unverified", "I couldn't find an animal testing policy for Nécessaire, and it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Its FAQ says its products have no animal-derived ingredients and that it's working on vegan certification.",
     vegan="full", vc="medium", region="USA & Canada", price="££",
     sources=[{"label": "Nécessaire: its FAQ (vegan ingredients and certification)", "url": "https://necessaire.com/pages/faq"}, _LBG, _PETAB])
if "necessaire" in by: by["necessaire"]["veganBasis"] = "brand"
if "cocokind" in by: by["cocokind"]["lastVerified"] = today
# owners
_own("origins", "Estée Lauder Companies", "Owned by the Estée Lauder Companies. " + _PETA, "Estée Lauder Companies: its Origins page", "https://www.elcompanies.com/en/our-brands/origins")
_own("coppertone", "Beiersdorf", "Owned by Beiersdorf, which bought it from Bayer in 2019. " + _PETA, "Bayer: press release on completing the sale of Coppertone to Beiersdorf (2 September 2019)", "https://www.bayer.com/media/en-us/bayer-completes-sale-of-iconic-coppertonetm-brand-to-beiersdorf/")
_own("marc-jacobs-fragrances", "WHP Global / G-III Apparel Group (50/50)", "Marc Jacobs is co-owned 50/50 by WHP Global and G-III Apparel Group (the deal closed on 1 September 2026). " + _PETA, "WHP Global: announcement that it and G-III completed the Marc Jacobs acquisition", "https://www.whp-global.com/blogs/brand-news/whp-global-and-g-iii-apparel-group-complete-acquisition-of-marc-jacobs")
_SI = by.get("st-ives")
if _SI:
    _SI.update(tier="unverified", parentCompany="Evermark", lastVerified=today, vegan="partial",
        claim="Its FAQ says St. Ives was officially PETA-certified cruelty-free across its entire range as of December 2018, and that it is committed to never testing on animals.",
        note="St Ives says it was certified cruelty-free by PETA in December 2018, but I couldn't find it on PETA's cruelty-free list in October 2026, so it isn't currently listed as certified. Owned by Evermark, which is backed by Yellow Wood Partners, after Unilever sold it.",
        sources=[{"label": "St Ives: its FAQ (PETA certification claim and animal-derived ingredients)", "url": "https://www.stives.com/pages/faq"},
                 {"label": "PETA: St Ives company page", "url": "https://crueltyfree.peta.org/company/st-ives/"},
                 {"label": "Yellow Wood Partners: Evermark merger announcement (lists St. Ives), 20 January 2026", "url": "https://yellowwoodpartners.com/news-article/yellow-wood-partners-portfolio-companies-suave-brands-and-elida-beauty-complete-merger-to-create-evermark-a-leading-global-platform-of-personal-care-brands"},
                 {"label": "Glossy: Yellow Wood bought St. Ives and Noxzema (via Elida Beauty) from Unilever", "url": "https://www.glossy.co/beauty/beauty-briefing-under-new-ownership-classic-brands-st-ives-and-noxzema-are-ready-for-a-modern-makeover/"}])
_RX = by.get("radox")
if _RX:
    _RX.update(vegan="partial", vegan_note=None, lastVerified=today,
        note="Radox has no animal testing policy that I could find, and it isn't certified. Owned by Unilever, who sell into markets requiring animal testing.")
    _RX.pop("vegan_note", None)
    for _l, _u in (("Radox: its FAQ (animal-derived ingredients; no animal testing statement)", "https://www.radox.co.uk/faq.html"), ("Radox: its own website (published by Unilever)", "https://www.radox.co.uk/")):
        if not any(s.get("url") == _u for s in _RX["sources"]): _RX["sources"].append({"label": _l, "url": _u})
# rule: no information of its own + parent confirmed to test = "tests on animals"
for _b in brands:
    if _b.get("tier") == "unverified" and not _b.get("claim") and _b.get("parentCompany") and _b.get("parentTestsOnAnimals") is True:
        _b["tier"] = "bad"
        if _b["slug"] == "hawaiian-tropic":
            _b["note"] = "Hawaiian Tropic gives no animal testing information of its own, so it takes its owner's position. Owned by Edgewell Personal Care, which has confirmed it allows animal testing on its products where required by law (for example, to register cosmetics for sale in mainland China)."
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
_rw("scripts/generate-brand-check.js", lambda t: t if "'Tesco'" in t else t.replace("'Aldi', 'Lidl',", "'Aldi', 'Lidl', 'Tesco', 'Asda',", 1))
def _qa(t):
    if "k-qa" in t: return t
    fn = ("function testAnswer(brand) {\n  const n = escapeHtml(brand.name), p = brand.parentCompany ? escapeHtml(brand.parentCompany) : null;\n"
          "  if (brand.tier === 'good' || brand.tier === 'check') return 'No. ' + n + ' is listed as cruelty-free by Leaping Bunny / Cruelty Free International or PETA. The sources are below.';\n"
          "  if (brand.tier === 'warn') return 'Not itself, but its owner does. ' + n + ' is listed as cruelty-free, but ' + (p || 'the company that owns it') + ' tests on animals or sells where the law requires it.';\n"
          "  if (brand.tier === 'bad') return 'Yes, or it sells where animal testing is required. ' + (p ? n + ' is owned by ' + p + '. ' : '') + 'The sources are below.';\n"
          "  if (brand.claim) return n + ' says it doesn\\'t test on animals, but it isn\\'t certified, so nobody independent has checked. What it says is below.';\n"
          "  return 'I couldn\\'t find an animal testing policy or certification for ' + n + ' yet. The sources I checked are below.';\n}\n")
    t = t.replace("function claimBox(brand) {", fn + "function claimBox(brand) {", 1)
    t = t.replace("  if (parentTestFlag) lines.push(parentTestFlag);\n  lines.push('</div>');",
                  "  if (parentTestFlag) lines.push(parentTestFlag);\n  lines.push('</div>');\n  lines.push('<section class=\"k-qa\"><h2 style=\"font-size:1.1rem;margin:22px 0 6px\">Does ' + escapeHtml(brand.name) + ' test on animals?</h2><p style=\"margin:0 0 6px\">' + testAnswer(brand) + '</p></section>');", 1)
    return t
_n = _rw("scripts/generate-brand-pages.js", _qa)
print("Batch 13 Oct applied; generator changed:", _n)

# 39. Ash's own findings and links go on the brand as given (13 Oct)
def _addsrc(b, label, url):
    if b and not any(s.get("url") == url for s in b.get("sources", [])): b.setdefault("sources", []).append({"label": label, "url": url})
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_tk = "https://www.tescoplc.com/sustainability/planet/agriculture"
_new("tesco-kind-pure", "Tesco Kind & Pure", "unverified", "Tesco says its Kind & Pure range is cruelty-free and vegan, but neither claim is certified.",
     vegan="full", vc="medium", claim="Tesco says its Kind & Pure range is cruelty-free and vegan.", category=["skincare", "body-shower"], region="Europe", price="£", parent=None,
     sources=[{"label": "Tesco: its agriculture page (animal testing statement)", "url": _tk}, _LBG, _PETAB])
if "tesco-kind-pure" in by: by["tesco-kind-pure"]["veganBasis"] = "brand"
_addsrc(by.get("tesco"), "Tesco: its agriculture page (animal testing statement)", _tk)
_n = by.get("necessaire")
if _n:
    _n.update(tier="bad", claim="", lastVerified=today,
        note="Nécessaire tests on animals. I couldn't find an animal testing policy for it. A statement it gave an activist by email isn't published on its website, so it can't be verified. Its Sex Gel was reportedly tested on animals as a one-off to meet FDA medical device requirements. It isn't certified by Leaping Bunny / Cruelty Free International or PETA. Its FAQ says its products have no animal-derived ingredients and that it's working on vegan certification.")
_mj = by.get("marc-jacobs-fragrances")
if _mj:
    _mj["note"] = ("Marc Jacobs is co-owned 50/50 by WHP Global and G-III Apparel Group (the deal closed on 1 September 2026). Listed by PETA as a company that tests on animals. "
                   "WHP Global says it tests on animals where required by law. G-III banned fur but still uses leather, wool and down.")
    _addsrc(_mj, "G-III Apparel Group: its animal welfare policy (document)", "https://www.giii.com/wp-content/uploads/2023/05/GIII-Animal-Welfare-Policy.pdf")
_si = by.get("st-ives")
_addsrc(_si, "St Ives: its blog post on products not tested on animals", "https://www.stives.com/blogs/news/products-not-tested-on-animals")
_bal = by.get("balenciaga")
if _bal:
    _bal["note"] = ("Owned by Kering. Listed by PETA as a company that tests on animals. Kering phased out fur across its fashion houses, including Gucci, Saint Laurent, Balenciaga, Alexander McQueen and Bottega Veneta, from autumn 2022. "
                    "It still uses exotic skins such as python and crocodile, plus leather, wool, silk and cashmere, under its own internal animal welfare standards.")
    _addsrc(_bal, "Kering: its animal welfare page", "https://www.kering.com/en/sustainability/safeguarding-the-planet/animal-welfare/")
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
def _kering(t):
    if '"Kering":' in t: return t
    return t.replace('"Kenvue": {"url"', '"Kering": {"url": "https://www.kering.com/en/sustainability/safeguarding-the-planet/animal-welfare/", "summary": "Kering\'s animal welfare page covers the animal materials its fashion houses use. It says fur was phased out across its houses, including Gucci, Saint Laurent, Balenciaga, Alexander McQueen and Bottega Veneta, from autumn 2022, while exotic skins such as python and crocodile, leather, wool, silk and cashmere are still used under its own internal animal welfare standards."},\n"Kenvue": {"url"', 1)
_rw("scripts/site_update.py", _kering)
print("Section 39 applied")

# 40. Rare Beauty ownership, Avon, Superdrug, Reddit list part 1 (Ash's research, 13 Oct)
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
def _src(label, url): return {"label": label, "url": url}
_EW = "https://cdn.shopify.com/s/files/1/0598/9538/2192/files/Corporate_Animal_Testing_Policy.pdf?v=1724093148"
_PEF = "Edgewell Personal Care: its animal testing statement (Playtex FAQ)"; _PEU = "https://www.playtexplayon.ca/pages/frequently-asked-questions"
# Rare Beauty
_rb = by.get("rare-beauty")
if _rb:
    _rb["note"] = ("PETA and Leaping Bunny certified, 100% vegan. Independently owned: Selena Gomez owns the majority, and the rest is held by a small group of private backers whose exact shares aren't public. "
                   "Company filings name New Theory Ventures (Nikki Eslami), CEO Scott Friedman, who previously ran NYX Cosmetics up to its sale to L'Oréal, and Julius Salerno, co-founder of the hair extensions brand Bellamy, as an additional investing partner in Rare Beauty LLC.")
    _rb["lastVerified"] = today
# Avon
_av = by.get("avon")
if _av:
    _av["parentCompany"] = "Regent LP"; _av["lastVerified"] = today
    _av["note"] = ("Leaping Bunny certified (Cruelty Free International) since 2024, covering its entire global product range. Avon confirmed to me by email that all of its products are vegan, but it has no vegan certification. "
                   "Owned by Regent LP, an investment company rather than a manufacturer, so it has no animal testing policy of its own that applies to Avon. What counts is each brand's own policy.")
    _addsrc(_av, "Regent: its website (investment holding company)", "https://www.regentco.com/")
    _addsrc(_av, "Modaes: Natura closes the sale of Avon International to Regent (7 January 2026)", "https://www.modaes.com/global/companies/brazils-natura-closes-the-sale-of-avon-international-to-regent-lp")
# Superdrug own brands
_SD = "Owned by A.S. Watson Group, which allows its products to be sold where animal testing may be required by law. Superdrug says it sets its own brand policies independently."
for _s in ("superdrug", "b-by-superdrug", "superdrug-own-brand-wider-range", "solait-by-superdrug", "superdrug-own-brand-dental", "superdrug-pro-care"):
    _b = by.get(_s)
    if not _b: continue
    _b.update(parentCompany="A.S. Watson Group", parentTestsOnAnimals=True, tier="warn", lastVerified=today)
    if _SD not in _b["note"]: _b["note"] = _b["note"].rstrip() + " " + _SD
    _addsrc(_b, "Superdrug: its corporate governance page (part of A.S. Watson Group)", "https://www.superdrug.com/corporate/governance")
_sdp = by.get("superdrug")
# new brands
_E = _EH if False else None
_m = _new("missha", "Missha", "unverified", "Missha says it doesn't conduct animal testing, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Its own FAQ has no information on animal testing, and older links to it are broken. Apparently it tests where required by law, but I couldn't find that stated publicly. Owned by ABLE C&C.",
     parent="ABLE C&C Co., Ltd", claim="Missha says it doesn't conduct animal testing, and that it is strictly against animal testing for product development.", category=["skincare", "makeup-beauty"], region="Asia",
     sources=[_src("K-Beauty House: its Missha brand page (says it doesn't conduct animal testing)", "https://kbeautyhouse.de/en/brands/missha/"), _src("Missha: its FAQ (no animal testing information)", "https://misshaus.com/pages/faq"), _src("Franchise UK: Missha franchise page (ABLE C&C, anti-animal-testing statement)", "https://www.franchise-uk.co.uk/health-beauty/smile-youve-got-cosmetics-franchise/"), _LBG, _PETAB])
_w = _new("well-people", "Well People", "good", "Certified cruelty-free by Leaping Bunny / Cruelty Free International and PETA. Its FAQ says all its products are 100% vegan, but it has no vegan certification. Owned by e.l.f. Beauty.",
     parent="e.l.f. Beauty", vegan="full", vc="medium", category=["makeup-beauty", "skincare"], price="££",
     sources=[_src("Well People: its FAQ (cruelty-free and vegan statements)", "https://www.wellpeople.com/pages/faqs"), _src("e.l.f. Beauty: its Well People brand page", "https://www.elfbeauty.com/brands/well-people"), _LBG, _PETAB])
if _w: _w["veganBasis"] = "brand"
_new("formula-10-0-6", "Formula 10.0.6", "check", "Certified cruelty-free by PETA. Its FAQ says the majority of its products are vegan, with beeswax in a couple.",
     vegan="partial", vc="high", category=["skincare"],
     sources=[_src("PETA: Formula 10.0.6 company page", "https://crueltyfree.peta.org/company/formula-10-0-6/"), _src("Formula 10.0.6: its FAQ (vegan products)", "https://www.formula1006.com/pages/faqs")])
_l = _new("lume", "Lume", "unverified", "Lume says its products are vegan and cruelty-free, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA.",
     vegan="full", vc="medium", claim="Lume says its products are cruelty-free and vegan.", category=["body-shower"],
     sources=[_src("Lume: its help centre (vegan and cruelty-free statement)", "https://help.lumedeodorant.com/en-US/are-lume-products-skin-safe-vegan-cruelty-free-etc-19475"), _LBG, _PETAB])
if _l: _l["veganBasis"] = "brand"
_new("cosrx", "COSRX", "unverified", "I couldn't find an animal testing policy for COSRX, and it isn't certified by Leaping Bunny / Cruelty Free International or PETA. It isn't vegan either.",
     vegan="no", category=["skincare"], region="Asia",
     sources=[_src("PETA: COSRX company page", "https://crueltyfree.peta.org/company/cosrx/"), _LBG, _PETAB])
_new("rael", "Rael", "check", "Certified cruelty-free by Leaping Bunny. Founded in Los Angeles in 2017 by three Korean American women: Yanghee Paik, Aness An and Binna Won. Not all products are vegan, and its FAQ says vegan status is based on supplier documentation.",
     vegan="partial", vc="high", category=["skincare", "period-menstrual"], region="USA & Canada",
     sources=[_src("Rael: its FAQ (vegan and Leaping Bunny statements)", "https://www.getrael.com/pages/faq"), _src("Leaping Bunny: approved brands (search for the brand)", "https://www.leapingbunny.org/shopping-guide")])
_new("playtex", "Playtex", "bad", "Playtex tests on animals. It's owned by Edgewell Personal Care, which says its products are only tested on animals in markets where the law requires it. It isn't certified by Leaping Bunny / Cruelty Free International or PETA, and isn't vegan either: its FAQ says its feminine care products aren't certified vegan and that it makes an effort not to intentionally source animal-derived ingredients.",
     parent="Edgewell Personal Care", vegan="no", category=["period-menstrual"],
     sources=[_src("PETA: Playtex company page", "https://crueltyfree.peta.org/company/playtex-tampons-playtex-products/"), _src(_PEF, _PEU)])
_new("softsoap", "Softsoap", "bad", "Softsoap tests on animals. Its website doesn't mention animal testing, so it takes its owner's position. Owned by Colgate-Palmolive. It isn't certified by Leaping Bunny / Cruelty Free International or PETA, and not all of its products are vegan.",
     parent="Colgate-Palmolive", vegan="partial", category=["body-shower"],
     sources=[_src("PETA: Softsoap company page", "https://crueltyfree.peta.org/company/softsoap-colgate-palmolive-co/"), _src("Softsoap: its FAQ (vegan products)", "https://www.softsoap.com/en-us/faq#accordion-573eb8dc78-item-8adda9ad87")])
_new("opi", "OPI", "bad", "OPI isn't cruelty-free and isn't certified by Leaping Bunny / Cruelty Free International or PETA. Its FAQ says it doesn't test its ingredients or products on animals and never asks suppliers or contract manufacturers to, and the Wella Company says it doesn't test its products on animals either. Owned by the Wella Company, which also runs Clairol and ghd. OPI and Wella were previously owned by Coty.",
     parent="The Wella Company", category=["makeup-beauty"],
     sources=[_src("OPI: its FAQ (animal testing statement)", "https://www.opi.com/en-GB/faq"), _src("The Wella Company: its FAQ (animal testing statement)", "https://www.wellacompany.com/frequently-asked-questions")])
_st = _new("starface", "Starface", "good", "Certified cruelty-free by Leaping Bunny / Cruelty Free International and PETA. Its FAQ says all its products are vegan, but it has no vegan certification. Independently owned and controlled by its co-founders, Julie Schott and Brian Bordainick.",
     vegan="full", vc="medium", category=["skincare"], region="USA & Canada",
     sources=[_src("Starface: its FAQ (vegan and Leaping Bunny statements)", "https://starface.world/pages/faq"), _LBG, _PETAB])
if _st: _st["veganBasis"] = "brand"
_new("vagisil", "Vagisil", "unverified", "Vagisil says it doesn't test on animals, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. It isn't entirely vegan: some products are, and others contain lanolin. Owned by Combe Incorporated.",
     parent="Combe Incorporated", vegan="partial", claim="Vagisil says it doesn't test on animals.", category=["hygiene"],
     sources=[_src("Vagisil: its FAQ (animal testing statement)", "https://www.vagisil.com/faq"), _LBG, _PETAB])
_new("summers-eve", "Summer's Eve", "unverified", "Summer's Eve says it doesn't test on animals, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. It isn't fully vegan: vegan status varies by product.",
     vegan="partial", claim="Summer's Eve says its products aren't tested on animals.", category=["hygiene"],
     sources=[_src("Summer's Eve: its FAQ (animal testing statement)", "https://www.summerseve.com/faqs#are-summer-s-eve-products-tested-animals"), _LBG, _PETAB])
_new("banana-boat", "Banana Boat", "bad", "Banana Boat doesn't say either way whether it tests on animals, so it takes its owner's position. Owned by Edgewell Personal Care, which tests on animals where required by law or regulation. It isn't certified by Leaping Bunny / Cruelty Free International or PETA, and isn't vegan.",
     parent="Edgewell Personal Care", vegan="no", category=["skincare"],
     sources=[_src(_PEF, _PEU), _src("Edgewell Personal Care: its own animal testing policy", _EW)])
_new("mediheal", "Mediheal", "unverified", "I couldn't find a certification or an animal testing policy for Mediheal anywhere, and nothing on whether its products are vegan. Owned by L&P Cosmetic Co., Ltd, which has no public policy that I could find.",
     parent="L&P Cosmetic Co., Ltd", category=["skincare"], region="Asia",
     sources=[_src("Mediheal fan site: its FAQ (not the brand's own site)", "https://medihealhq.shop/faq"), _LBG, _PETAB])
_new("medicube", "Medicube", "bad", "Medicube isn't cruelty-free and isn't certified by Leaping Bunny / Cruelty Free International or PETA. Its FAQ is vague, saying only that its products are developed with a focus on safe and ethical skincare practices. Owned by APR Corporation (formerly Aprilskin Corporation), whose product safety page promises a no-animal-testing policy except where animal testing is unavoidably required by national regulations. It isn't vegan either.",
     parent="APR Corporation", vegan="no", category=["skincare"], region="Asia",
     sources=[_src("Medicube: its FAQ", "https://medicubeofficial.co.uk/faqs/"), _src("APR Corporation: its product safety page", "https://www.apr-in.com/en/product_safety.html")])
_vc = _new("vacation", "Vacation", "good", "Certified cruelty-free by Leaping Bunny. Its FAQ says its products are 100% vegan, but it has no vegan certification.",
     vegan="full", vc="medium", category=["skincare"], region="USA & Canada",
     sources=[_src("Vacation: its FAQ (vegan and Leaping Bunny statements)", "https://vacation.inc/faq"), _src("Leaping Bunny: approved brands (search for the brand)", "https://www.leapingbunny.org/shopping-guide")])
if _vc: _vc["veganBasis"] = "brand"
_new("zum", "Zum", "unverified", "Zum says its products are never tested on animals, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Its FAQ says all Zum products are vegan except Zum Bars (goat's milk), Zum Kisses (honey) and Zum Body Balm / Zum Rub (goat's milk).",
     vegan="partial", vc="medium", claim="Zum says its products are never tested on animals, only on people at the Zum Factory.", category=["body-shower", "skincare"],
     sources=[_src("Indigo Wild: its FAQ (Zum animal testing and vegan statements)", "https://www.indigowild.com/pages/faq"), _LBG, _PETAB])
_new("kirkland-signature", "Kirkland Signature", "unverified", "Kirkland Signature is Costco's own brand. It isn't certified by Leaping Bunny / Cruelty Free International or PETA, and isn't vegan.",
     parent="Costco Wholesale Corporation", vegan="no", category=["skincare", "household-cleaning"],
     sources=[_LBG, _PETAB])
_new("members-mark", "Member's Mark", "unverified", "Member's Mark is the own brand of Sam's Club, which is owned by Walmart. It isn't certified by Leaping Bunny / Cruelty Free International or PETA.",
     parent="Walmart Inc.", category=["skincare", "household-cleaning"],
     sources=[_LBG, _PETAB])
_new("signature-select", "Signature Select", "unverified", "Signature Select is the main own brand of Safeway, which is owned by Albertsons Companies. It isn't certified by Leaping Bunny / Cruelty Free International or PETA.",
     parent="Albertsons Companies", category=["skincare", "household-cleaning"],
     sources=[_src("Albertsons Companies: its animal well-being page", "https://www.albertsonscompanies.com/about-aci/our-impact/products/animal-well-being/"), _LBG, _PETAB])
_new("up-and-up", "up&up", "unverified", "up&up is Target's own brand. Target doesn't publish an animal testing policy or FAQ for it, and up&up isn't certified by Leaping Bunny / Cruelty Free International or PETA. It isn't vegan.",
     parent="Target Corporation", vegan="no", category=["skincare", "household-cleaning"],
     sources=[_LBG, _PETAB])
_new("beauty-360", "Beauty 360", "unverified", "Beauty 360 is CVS's own beauty brand. I couldn't find an animal testing policy for it, and it isn't certified by Leaping Bunny / Cruelty Free International or PETA. It isn't vegan.",
     parent="CVS Health Corporation", vegan="no", category=["makeup-beauty", "skincare"],
     sources=[_src("CVS Health: its store brand sustainability page", "https://www.cvshealth.com/impact/healthy-planet/store-brand-sustainability.html"), _LBG, _PETAB])
_new("the-yorkshire-soap-company", "The Yorkshire Soap Company", "unverified", "The Yorkshire Soap Company says it's cruelty-free, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. It isn't fully vegan, but it has a vegan range. Independently owned.",
     vegan="partial", claim="The Yorkshire Soap Company says it's cruelty-free.", category=["body-shower"], region="Europe",
     sources=[_LBG, _PETAB])
# parent flags
for _s in ("playtex", "banana-boat"):
    if _s in by: by[_s]["parentTestsOnAnimals"] = True
if "medicube" in by: by["medicube"]["parentTestsOnAnimals"] = True
if "well-people" in by and "e-l-f-cosmetics" in by and "parentTestsOnAnimals" in by["e-l-f-cosmetics"]: by["well-people"]["parentTestsOnAnimals"] = by["e-l-f-cosmetics"]["parentTestsOnAnimals"]
for _s in ("kirkland-signature", "members-mark", "signature-select", "up-and-up", "beauty-360", "missha", "mediheal", "zum", "cosrx", "lume", "vagisil", "summers-eve", "the-yorkshire-soap-company", "formula-10-0-6", "rael", "vacation", "starface", "well-people"):
    if _s in by: by[_s]["lastVerified"] = today
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
def _sm(t):
    if "'Kirkland Signature'" in t: return t
    return t.replace("'Tesco', 'Asda',", "'Tesco', 'Asda', 'Kirkland Signature', \"Member's Mark\", 'Signature Select', 'up&up', 'Beauty 360',", 1)
_rw("scripts/generate-brand-check.js", _sm)
_rw("scripts/generate-brand-pages.js", lambda t: t if "'not vegan'" in t else t.replace("    : brand.vegan === 'partial' ? 'varies by product'\n    : 'not yet confirmed';", "    : brand.vegan === 'partial' ? 'varies by product'\n    : brand.vegan === 'no' ? 'not vegan'\n    : 'not yet confirmed';", 1))
def _regent(t):
    if '"Regent LP":' in t: return t
    t = t.replace("ASH_NOTES = {", 'ASH_NOTES = {"Regent LP": "Regent is an investment company, not a manufacturer, so it has no overall animal testing status. Avon is certified cruelty-free by Leaping Bunny / Cruelty Free International. What matters is each brand\'s own policy.", ', 1)
    old = '    elif True not in flags and False not in flags: polhtml = "<p>I couldn\'t find a published animal testing policy from this company.</p>"\n'
    new = old + '    if not pol:\n        nt = ASH_NOTES.get(name) or next((ASH_NOTES[k] for k in ASH_NOTES if slugify(k) == ps), None)\n        if nt: polhtml = \'<p>%s</p>\' % E(nt)\n'
    return t.replace(old, new, 1)
_rw("scripts/site_update.py", _regent)

for _s in ("superdrug", "superdrug-pro-care"):
    if _s in by and by[_s].get("vegan") == "unknown": by[_s]["vegan"] = "partial"
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
def _indep(t):
    if "ahk-indep" in t: return t
    old = '    if not b.get("parentCompany"):\n        h = re.sub(r"(&middot; )Independent( &middot;)"'
    new = '    if not b.get("parentCompany") and not re.search(r"independently owned|family[- ]owned|founder[- ]owned|independent (?:\\w+ )?(?:company|brand)", b.get("note") or "", re.I):  # ahk-indep\n        h = re.sub(r"(&middot; )Independent( &middot;)"'
    return t.replace(old, new, 1)
_rw("scripts/site_update.py", _indep)
print("Section 40 applied")

# 41. OPI and Wella corrections, Yorkshire Soap Company FAQ (Ash, 13 Oct)
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_o = by.get("opi")
if _o:
    _o.update(tier="unverified", lastVerified=today,
        claim="OPI says it doesn't test its ingredients or products on animals, and never asks its suppliers or contract manufacturers to.",
        note="OPI says it doesn't test its ingredients or products on animals, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Owned by the Wella Company, which also runs Clairol and ghd, and which says it doesn't test its products on animals either. OPI and Wella were previously owned by Coty.")
_wl = by.get("wella")
if _wl:
    _wl.update(parentCompany="The Wella Company", lastVerified=today,
        note="Cruelty Free Kitty lists Wella as testing on animals, most often in mainland China. The Wella Company says it doesn't test its products on animals. Owned by the Wella Company (previously Coty).")
    _addsrc(_wl, "The Wella Company: its FAQ (animal testing statement)", "https://www.wellacompany.com/frequently-asked-questions")
_ys = by.get("the-yorkshire-soap-company")
if _ys:
    _ys.update(claim="The Yorkshire Soap Company says it has never tested on animals.", lastVerified=today,
        note="The Yorkshire Soap Company says it has never tested on animals, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA, so this can't be verified. Its FAQ says it sometimes uses honey, milk or beeswax, so not every product is vegan, though it has a vegan range. Independently owned.")
    _ys["sources"] = [{"label": "The Yorkshire Soap Company: its FAQs (animal testing and animal-derived ingredients)", "url": "https://yorkshiresoap.co.uk/faqs/"}, _LBG, _PETAB]
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Section 41 applied")

# 42. Rael owner (Ash, 13 Oct)
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_ra = by.get("rael")
if _ra:
    _ra.update(parentCompany="TowerBrook Capital Partners", lastVerified=today,
        note="Certified cruelty-free by Leaping Bunny. Founded in Los Angeles in 2017 by three Korean American women: Yanghee Paik, Aness An and Binna Won. Majority-owned by TowerBrook Capital Partners, a US private equity firm that bought a majority stake in August 2026. Not all products are vegan, and its FAQ says vegan status is based on supplier documentation.")
    _addsrc(_ra, "Sidley: Rael's strategic investment from TowerBrook Capital Partners (August 2026)", "https://www.sidley.com/en/newslanding/newsannouncements/2026/08/sidley-represents-rael-in-its-strategic-investment-from-towerbrook-capital-partners")
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Section 42 applied")

# 44. Avon: certified in four regions, not North America (Ash, Reddit, 14 Oct)
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_av = by.get("avon")
if _av:
    _av["region"] = "Africa & The Middle East, Asia, Europe, South & Central America"; _av["lastVerified"] = today
    _av["note"] = ("Certified cruelty-free by Leaping Bunny / Cruelty Free International in Africa & The Middle East, Asia, Europe and South & Central America. North America isn't on its listing. "
                   "Avon's US site says it doesn't conduct animal testing, but that it sells in China, where authorities require animal-based safety testing for some cosmetic categories, and it mentions no certification. "
                   "Avon confirmed to me by email that all of its products are vegan, but it has no vegan certification. "
                   "Owned by Regent LP, an investment company rather than a manufacturer, so it has no animal testing policy of its own that applies to Avon. What counts is each brand's own policy.")
    _addsrc(_av, "Cruelty Free International: Avon listing (regions covered)", "https://www.crueltyfreeinternational.org/approved-brands/listing/avon/")
    _addsrc(_av, "Avon (US): its animal welfare page", "https://www.avon.com/information/animal-welfare.html")
    _av["answer"] = ("In Africa & The Middle East, Asia, Europe and South & Central America, no: Avon is certified cruelty-free there. In North America it isn't certified, and Avon's US site says it sells in China, "
                     "where animal testing is required for some cosmetic categories. The sources are below.")
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
_rw("scripts/generate-brand-pages.js", lambda t: t if "brand.answer" in t else t.replace("function testAnswer(brand) {\n", "function testAnswer(brand) {\n  if (brand.answer) return escapeHtml(brand.answer);\n", 1))
print("Section 44 applied")

# 43. Owner tool page for the laptop: ahomekind.com/owner-tool (not linked, not indexed)
OWNER_TOOL = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="favicon.ico?v=2" sizes="any">
<title>Who owns who - a home kind</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=DM+Sans:wght@400;500;700&family=DM+Mono:wght@400;500&display=swap">
<style>
/* Layout: a brand list on the left, one focus card on the right (stacked on a phone). The card holds quick search buttons, three fields and four answers. */
:root {
  --bg: #f7f3f9;
  --panel: #ffffff;
  --ink: #2a1630;
  --muted: #6d5a75;
  --line: #e4d9e8;
  --accent: #6e4e78;
  --accent-ink: #ffffff;
  --soft: #efe3f1;
  --good: #2f7d4f;
  --good-bg: #e0f1e6;
  --warn: #9a6a12;
  --warn-bg: #f8ecd0;
  --bad: #a3364a;
  --bad-bg: #f7dfe4;
  --focus: #1d6fd1;
  --font-body: "DM Sans", system-ui, sans-serif;
  --font-display: "Caveat", "Bradley Hand", cursive;
  --font-mono: "DM Mono", ui-monospace, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #1c1222; --panel: #271a2e; --ink: #f1e8f4; --muted: #b9a7c2; --line: #3d2d47;
    --accent: #c9a3d6; --accent-ink: #1c1222; --soft: #36263f;
    --good: #7fd1a0; --good-bg: #1f3a2b; --warn: #e6bd6a; --warn-bg: #3b3017; --bad: #f19aab; --bad-bg: #44212b; --focus: #7ab6ff;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #1c1222; --panel: #271a2e; --ink: #f1e8f4; --muted: #b9a7c2; --line: #3d2d47;
  --accent: #c9a3d6; --accent-ink: #1c1222; --soft: #36263f;
  --good: #7fd1a0; --good-bg: #1f3a2b; --warn: #e6bd6a; --warn-bg: #3b3017; --bad: #f19aab; --bad-bg: #44212b; --focus: #7ab6ff;
  color-scheme: dark;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font: 15px/1.5 var(--font-body); padding-inline: 16px; padding-block: 16px 40px; }
.wrap { max-width: 1120px; margin: 0 auto; display: grid; gap: 16px; }
h1 { font: 700 34px/1 var(--font-display); margin: 0; letter-spacing: .2px; }
button, input, textarea, select { font: inherit; color: inherit; }
:focus-visible { outline: 3px solid var(--focus); outline-offset: 2px; }
header.top { display: grid; gap: 12px; }
.headrow { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 8px 16px; }
.count { font: 500 14px var(--font-mono); color: var(--muted); font-variant-numeric: tabular-nums; }
.bar { height: 10px; border-radius: 6px; background: var(--soft); overflow: hidden; display: flex; }
.bar i { display: block; height: 100%; }
.bar .b-done { background: var(--good); }
.bar .b-nf { background: var(--warn); }
.bar .b-skip { background: var(--muted); opacity: .5; }
.filters { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.seg { display: inline-flex; flex-wrap: wrap; border: 1px solid var(--line); border-radius: 8px; overflow: hidden; background: var(--panel); }
.seg button { border: 0; background: transparent; padding: 7px 12px; cursor: pointer; color: var(--muted); }
.seg button + button { border-left: 1px solid var(--line); }
.seg button[aria-pressed="true"] { background: var(--accent); color: var(--accent-ink); font-weight: 500; }
select, input[type="search"], input[type="text"], input[type="url"], textarea { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; width: 100%; }
select { width: auto; }
.main { display: grid; grid-template-columns: 290px minmax(0, 1fr); gap: 16px; align-items: start; }
.list { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; display: grid; grid-template-rows: auto minmax(0, 1fr); max-height: 78vh; min-width: 0; }
.list .find { padding: 10px; border-bottom: 1px solid var(--line); }
.items { overflow-y: auto; padding: 4px; }
.item { display: flex; align-items: center; gap: 8px; width: 100%; text-align: left; border: 0; background: transparent; padding: 7px 8px; border-radius: 6px; cursor: pointer; min-width: 0; }
.item:hover { background: var(--soft); }
.item[aria-current="true"] { background: var(--soft); box-shadow: inset 3px 0 0 var(--accent); }
.item span.nm { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.dot { width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--line); flex: none; }
.dot.s-owner, .dot.s-independent { background: var(--good); border-color: var(--good); }
.dot.s-notfound { background: var(--warn); border-color: var(--warn); }
.dot.s-skip { background: var(--muted); border-color: var(--muted); opacity: .5; }
.empty { padding: 20px 12px; color: var(--muted); }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 20px; display: grid; gap: 18px; min-width: 0; }
.namerow { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; }
.card h2 { font: 700 42px/1 var(--font-display); margin: 0; overflow-wrap: anywhere; }
.chip { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 13px; font-weight: 500; }
.t-good, .t-check { background: var(--good-bg); color: var(--good); }
.t-warn, .t-unverified { background: var(--warn-bg); color: var(--warn); }
.t-bad { background: var(--bad-bg); color: var(--bad); }
.cats { color: var(--muted); font-size: 13px; }
.cur { color: var(--muted); font-size: 14px; max-width: 70ch; }
.saved { padding: 8px 12px; border-radius: 8px; background: var(--good-bg); color: var(--good); font-size: 14px; display: none; }
.saved.show { display: block; }
.saved.nf { background: var(--warn-bg); color: var(--warn); }
.saved.sk { background: var(--soft); color: var(--muted); }
.label { font: 500 12px var(--font-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; display: block; }
.searches { display: flex; flex-wrap: wrap; gap: 8px; }
.searches a { text-decoration: none; color: var(--accent); border: 1px solid var(--line); border-radius: 8px; padding: 7px 12px; font-weight: 500; background: var(--panel); }
.searches a:hover { background: var(--soft); }
.fields { display: grid; gap: 14px; max-width: 640px; }
.hint { font-size: 13px; color: var(--muted); margin-top: 4px; }
textarea { min-height: 76px; resize: vertical; }
.actions { display: flex; flex-wrap: wrap; gap: 8px; position: sticky; bottom: 0; background: var(--panel); padding-block: 10px; border-top: 1px solid var(--line); margin-top: -6px; }
.actions button { border: 1px solid var(--line); background: var(--panel); border-radius: 8px; padding: 10px 14px; cursor: pointer; font-weight: 500; }
.actions button:hover { background: var(--soft); }
.actions .primary { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }
.actions .primary:hover { background: var(--accent); filter: brightness(1.08); }
.actions .primary[disabled] { opacity: .45; cursor: not-allowed; }
.nav { display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap; border-top: 1px solid var(--line); padding-top: 12px; }
.nav button, .linkbtn { border: 0; background: transparent; color: var(--muted); cursor: pointer; padding: 6px 4px; text-decoration: underline; }
.kbd { font: 12px var(--font-mono); color: var(--muted); }
.note { font-size: 13px; color: var(--muted); }
.exp { background: var(--soft); border-radius: 8px; padding: 10px 12px; font-size: 14px; display: grid; gap: 8px; }
.exp p { margin: 0; }
.banner { background: var(--warn-bg); color: var(--warn); border-radius: 8px; padding: 8px 12px; font-size: 14px; }
@media (max-width: 800px) {
  .main { grid-template-columns: minmax(0, 1fr); }
  .list { max-height: 260px; order: 2; }
  .card { padding: 16px; }
  .card h2 { font-size: 36px; }
}
@media (prefers-reduced-motion: no-preference) { .bar i { transition: width .25s ease; } }
</style>

</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="headrow">
      <h1>Who owns who</h1>
      <div class="count" id="count" aria-live="polite"></div>
    </div>
    <div class="bar" id="bar" role="img" aria-label="Progress"><i class="b-done"></i><i class="b-nf"></i><i class="b-skip"></i></div>
    <div class="filters">
      <div class="seg" id="statusSeg" role="group" aria-label="Show">
        <button type="button" data-f="todo" aria-pressed="true">To do</button>
        <button type="button" data-f="done" aria-pressed="false">Done</button>
        <button type="button" data-f="notfound" aria-pressed="false">Couldn't find</button>
        <button type="button" data-f="skip" aria-pressed="false">Skipped</button>
        <button type="button" data-f="all" aria-pressed="false">All</button>
      </div>
      <select id="tierSel" aria-label="Filter by label">
        <option value="all">Every label</option>
        <option value="bad">Tests on animals</option>
        <option value="unverified">Not certified</option>
        <option value="warn">Owner isn't</option>
        <option value="check">Cruelty-free</option>
        <option value="good">CF + vegan</option>
      </select>
      <select id="catSel" aria-label="Filter by category"><option value="all">Every category</option></select>
      <button type="button" class="linkbtn" id="cpNew">Copy new answers</button><button type="button" class="linkbtn" id="cpAll">Copy everything</button>
    </div>
    <div class="banner" id="banner" hidden></div>
    <div class="exp" id="exp" hidden><p id="expMsg"></p><textarea id="expBox" readonly rows="4"></textarea></div>
  </header>

  <div class="main">
    <aside class="list" aria-label="Brands">
      <div class="find"><input type="search" id="q" placeholder="Find a brand" autocomplete="off"></div>
      <div class="items" id="items"></div>
    </aside>
    <section class="card" id="card" aria-live="polite"></section>
  </div>
</div>

<script>
(function () {
  var BRANDS = [], OWNERS = [];
  var TIERS = { good: 'CF + vegan', check: 'Cruelty-free', warn: "Owner isn't cruelty-free", bad: 'Tests on animals', unverified: 'Not certified' };
  var answers = {}, cur = null, f = 'todo', tier = 'all', cat = 'all', q = '';
  
  var $ = function (id) { return document.getElementById(id); };
  var bySlug = {};

  // per-device backup, used only when the shared store is unavailable
  function lsGet() { try { return JSON.parse(localStorage.getItem('ahk-owner-answers') || '{}'); } catch (e) { return {}; } }
  function lsSet(o) { try { localStorage.setItem('ahk-owner-answers', JSON.stringify(o)); } catch (e) {} }

  function status(s) { var a = answers[s]; return a ? a.status : 'todo'; }
  function group(s) { var st = status(s); return st === 'owner' || st === 'independent' ? 'done' : st; }

  function filtered() {
    var qq = q.trim().toLowerCase();
    return BRANDS.filter(function (b) {
      if (f !== 'all' && group(b.s) !== f) return false;
      if (tier !== 'all' && b.t !== tier) return false;
      if (cat !== 'all' && b.c.indexOf(cat) < 0) return false;
      if (qq && b.n.toLowerCase().indexOf(qq) < 0) return false;
      return true;
    });
  }

  function renderHead() {
    var n = BRANDS.length, d = 0, nf = 0, sk = 0;
    BRANDS.forEach(function (b) { var g = group(b.s); if (g === 'done') d++; else if (g === 'notfound') nf++; else if (g === 'skip') sk++; });
    $('count').textContent = d + ' done · ' + nf + " couldn't find · " + sk + ' skipped · ' + (n - d - nf - sk) + ' to go';
    var kids = $('bar').children;
    kids[0].style.width = (d / n * 100) + '%'; kids[1].style.width = (nf / n * 100) + '%'; kids[2].style.width = (sk / n * 100) + '%';
    $('bar').setAttribute('aria-label', d + ' of ' + n + ' done');
  }

  function renderList() {
    var list = filtered(), box = $('items');
    box.textContent = '';
    if (!list.length) { var e = document.createElement('div'); e.className = 'empty'; e.textContent = f === 'todo' ? 'Nothing left in this view. Nice.' : 'No brands match.'; box.appendChild(e); return; }
    var frag = document.createDocumentFragment();
    list.forEach(function (b) {
      var btn = document.createElement('button'); btn.type = 'button'; btn.className = 'item'; btn.dataset.s = b.s;
      if (b.s === cur) btn.setAttribute('aria-current', 'true');
      var dot = document.createElement('span'); dot.className = 'dot s-' + status(b.s);
      var nm = document.createElement('span'); nm.className = 'nm'; nm.textContent = b.n;
      btn.appendChild(dot); btn.appendChild(nm); frag.appendChild(btn);
    });
    box.appendChild(frag);
    var c = box.querySelector('[aria-current="true"]'); if (c && c.scrollIntoView) c.scrollIntoView({ block: 'nearest' });
  }

  function link(label, url) { var a = document.createElement('a'); a.href = url; a.target = '_blank'; a.rel = 'noopener'; a.textContent = label; return a; }

  function renderCard() {
    var card = $('card'); card.textContent = '';
    var b = cur && bySlug[cur];
    if (!b) { var p = document.createElement('p'); p.className = 'empty'; p.textContent = filtered().length ? 'Pick a brand on the left.' : 'Nothing to show with these filters.'; card.appendChild(p); return; }
    var a = answers[b.s] || {};
    var en = encodeURIComponent(b.n);
    var el = function (tag, cls, txt) { var x = document.createElement(tag); if (cls) x.className = cls; if (txt != null) x.textContent = txt; return x; };

    var row = el('div', 'namerow'); row.appendChild(el('h2', '', b.n)); row.appendChild(el('span', 'chip t-' + b.t, TIERS[b.t] || b.t)); card.appendChild(row);
    if (b.c.length) card.appendChild(el('div', 'cats', b.c.join(' · ')));
    if (b.d) card.appendChild(el('div', 'cur', 'On the site now: ' + b.d));

    var sv = el('div', 'saved'); sv.id = 'saved'; card.appendChild(sv);

    var sb = el('div'); sb.appendChild(el('span', 'label', 'Look it up'));
    var sr = el('div', 'searches');
    sr.appendChild(link('Who owns it?', 'https://www.google.com/search?q=' + encodeURIComponent('who owns ' + b.n + ' brand')));
    sr.appendChild(link('Parent company', 'https://www.google.com/search?q=' + encodeURIComponent(b.n + ' parent company')));
    sr.appendChild(link('Acquired by?', 'https://www.google.com/search?q=' + encodeURIComponent(b.n + ' acquired by')));
    sr.appendChild(link('Wikipedia', 'https://en.wikipedia.org/w/index.php?search=' + en));
    sr.appendChild(link('Cruelty Free Kitty', 'https://www.crueltyfreekitty.com/?s=' + en));
    sr.appendChild(link('Good On You', 'https://www.google.com/search?q=' + encodeURIComponent('site:directory.goodonyou.eco ' + b.n)));
    sr.appendChild(link('Their site: About us', 'https://www.google.com/search?q=' + encodeURIComponent(b.n + ' official site about us')));
    sb.appendChild(sr); card.appendChild(sb);

    var fields = el('div', 'fields');
    var w1 = el('div'); var l1 = el('label', 'label', 'Owner (parent company)'); l1.htmlFor = 'fOwner';
    var i1 = document.createElement('input'); i1.type = 'text'; i1.id = 'fOwner'; i1.setAttribute('list', 'ownerList'); i1.autocomplete = 'off'; i1.value = a.owner || '';
    var dlst = document.createElement('datalist'); dlst.id = 'ownerList'; OWNERS.forEach(function (o) { var op = document.createElement('option'); op.value = o; dlst.appendChild(op); });
    w1.appendChild(l1); w1.appendChild(i1); w1.appendChild(dlst); w1.appendChild(el('div', 'hint', 'Start typing and pick a name already on the site if there is one, so each company ends up with one page.'));
    var w2 = el('div'); var l2 = el('label', 'label', 'Link where you found it'); l2.htmlFor = 'fSrc';
    var i2 = document.createElement('input'); i2.type = 'url'; i2.id = 'fSrc'; i2.placeholder = 'https://'; i2.value = a.source || '';
    w2.appendChild(l2); w2.appendChild(i2);
    var w3 = el('div'); var l3 = el('label', 'label', 'Anything else you found (optional)'); l3.htmlFor = 'fNote';
    var i3 = document.createElement('textarea'); i3.id = 'fNote'; i3.value = a.note || '';
    w3.appendChild(l3); w3.appendChild(i3); w3.appendChild(el('div', 'hint', 'For example: who owns the rest, what it says about animal testing, or "I couldn’t find a policy".'));
    fields.appendChild(w1); fields.appendChild(w2); fields.appendChild(w3); card.appendChild(fields);

    var act = el('div', 'actions');
    var save = el('button', 'primary', 'Save owner and next'); save.type = 'button'; save.id = 'bSave'; save.disabled = !(a.owner);
    var ind = el('button', '', 'Independent'); ind.type = 'button'; ind.id = 'bInd';
    var nf = el('button', '', "Couldn't find an owner"); nf.type = 'button'; nf.id = 'bNf';
    var sk = el('button', '', 'Skip for now'); sk.type = 'button'; sk.id = 'bSkip';
    act.appendChild(save); act.appendChild(ind); act.appendChild(nf); act.appendChild(sk); card.appendChild(act);
    card.appendChild(el('div', 'note', '"Independent" means founder-owned or family-owned. Put who owns it in the note if you know. Ctrl or Cmd + Enter saves.'));

    var nav = el('div', 'nav');
    var pv = el('button', '', '← Previous'); pv.type = 'button'; pv.id = 'bPrev';
    var cl = el('button', '', 'Clear my answer'); cl.type = 'button'; cl.id = 'bClear'; cl.hidden = !answers[b.s];
    var nx = el('button', '', 'Next →'); nx.type = 'button'; nx.id = 'bNext';
    nav.appendChild(pv); nav.appendChild(cl); nav.appendChild(nx); card.appendChild(nav);
    paintSaved();
  }

  function paintSaved() {
    var sv = $('saved'); if (!sv) return;
    var a = cur && answers[cur];
    sv.className = 'saved';
    if (!a) { sv.textContent = ''; return; }
    if (a.status === 'owner') { sv.className = 'saved show'; sv.textContent = 'Saved: owned by ' + a.owner + '.'; }
    else if (a.status === 'independent') { sv.className = 'saved show'; sv.textContent = 'Saved: independent.'; }
    else if (a.status === 'notfound') { sv.className = 'saved show nf'; sv.textContent = "Saved: couldn't find an owner."; }
    else if (a.status === 'skip') { sv.className = 'saved show sk'; sv.textContent = 'Skipped for now.'; }
  }

  function renderAll() { renderHead(); renderList(); }

  function select(s) { cur = s; renderList(); renderCard(); var i = $('fOwner'); if (i && !('ontouchstart' in window)) i.focus(); }

  function advance(prevIdx) {
    var list = filtered();
    if (!list.length) { cur = null; renderAll(); renderCard(); return; }
    var i = list.findIndex(function (b) { return b.s === cur; });
    // still listed (e.g. "All"): move on to the one after it. Gone from the view: the same position now holds the next brand.
    var next = i >= 0 ? list[Math.min(i + 1, list.length - 1)] : list[Math.min(prevIdx, list.length - 1)];
    cur = next.s; renderAll(); renderCard();
  }

  function persist(slug, data) { var o = lsGet(); if (data) o[slug] = data; else delete o[slug]; lsSet(o); }

  function answer(st) {
    if (!cur) return;
    var b = bySlug[cur];
    var owner = ($('fOwner').value || '').trim(), source = ($('fSrc').value || '').trim(), note = ($('fNote').value || '').trim();
    if (st === 'owner' && !owner) return;
    var idx = filtered().findIndex(function (x) { return x.s === cur; }); if (idx < 0) idx = 0;
    var data = { slug: b.s, name: b.n, status: st, owner: st === 'owner' ? owner : '', source: source, note: note, at: new Date().toISOString().slice(0, 10) };
    answers[b.s] = data;
    persist(b.s, data);
    advance(idx);
  }

  function clearAnswer() {
    if (!cur) return;
    delete answers[cur]; persist(cur, null); renderAll(); renderCard();
  }

  function step(d) {
    var list = filtered(); if (!list.length) return;
    var i = list.findIndex(function (b) { return b.s === cur; });
    var n = list[Math.max(0, Math.min(list.length - 1, (i < 0 ? 0 : i + d)))];
    select(n.s);
  }

  // events
  $('items').addEventListener('click', function (e) { var b = e.target.closest('.item'); if (b) select(b.dataset.s); });
  $('statusSeg').addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return; f = b.dataset.f;
    Array.prototype.forEach.call($('statusSeg').children, function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    var l = filtered(); cur = l.length ? l[0].s : null; renderAll(); renderCard();
  });
  $('tierSel').addEventListener('change', function (e) { tier = e.target.value; var l = filtered(); cur = l.length ? l[0].s : null; renderAll(); renderCard(); });
  $('catSel').addEventListener('change', function (e) { cat = e.target.value; var l = filtered(); cur = l.length ? l[0].s : null; renderAll(); renderCard(); });
  $('q').addEventListener('input', function (e) { q = e.target.value; renderList(); });
  $('card').addEventListener('click', function (e) {
    var id = e.target.id;
    if (id === 'bSave') answer('owner');
    else if (id === 'bInd') answer('independent');
    else if (id === 'bNf') answer('notfound');
    else if (id === 'bSkip') answer('skip');
    else if (id === 'bNext') step(1);
    else if (id === 'bPrev') step(-1);
    else if (id === 'bClear') clearAnswer();
  });
  $('card').addEventListener('input', function (e) { if (e.target.id === 'fOwner') { var s = $('bSave'); if (s) s.disabled = !e.target.value.trim(); } });
  $('card').addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); answer('owner'); }
    else if (e.key === 'Enter' && e.target.id === 'fOwner') { e.preventDefault(); $('fSrc').focus(); }
    else if (e.key === 'Enter' && e.target.id === 'fSrc') { e.preventDefault(); if ($('fOwner').value.trim()) answer('owner'); else $('fOwner').focus(); }
  });

  function exportText(all) {
    var out = Object.keys(answers).map(function (k) { return answers[k]; }).filter(function (a) { return bySlug[a.slug] && a.status !== 'skip' && (all || !a.sent); })
      .map(function (a) { return { slug: a.slug, name: a.name, status: a.status, owner: a.owner, source: a.source, note: a.note }; });
    return out;
  }
  function doCopy(all) {
    var list = exportText(all), box = $('exp'), msg = $('expMsg'), ta = $('expBox');
    box.hidden = false;
    if (!list.length) { msg.textContent = all ? 'No answers yet.' : 'No new answers since the last copy.'; ta.hidden = true; return; }
    var text = JSON.stringify(list);
    ta.hidden = false; ta.value = text;
    var done = function () {
      if (!all) list.forEach(function (x) { if (answers[x.slug]) answers[x.slug].sent = 1; });
      lsSet(answers); msg.textContent = 'Copied ' + list.length + ' answer' + (list.length === 1 ? '' : 's') + '. Paste them into the chat with Claude.';
    };
    var fail = function () { msg.textContent = 'Copying was blocked. The text below is selected: copy it by hand, then paste it into the chat with Claude.'; ta.focus(); ta.select(); };
    try { navigator.clipboard.writeText(text).then(done, fail); } catch (e) { fail(); }
  }
  $('cpNew').addEventListener('click', function () { doCopy(false); });
  $('cpAll').addEventListener('click', function () { doCopy(true); });

  var CATN = { 'skincare': 'Skincare', 'makeup-beauty': 'Makeup', 'household-cleaning': 'Cleaning', 'body-shower': 'Body', 'haircare': 'Hair', 'laundry': 'Laundry', 'dental': 'Dental', 'hygiene': 'Hygiene', 'food-kitchen': 'Food', 'paper-hygiene': 'Paper', 'period-menstrual': 'Period', 'stationery': 'Stationery', 'pet-food': 'Pet food' };
  $('card').textContent = 'Loading brands\u2026';
  fetch('data/brands.json').then(function (r) { return r.json(); }).then(function (j) {
    var all = Array.isArray(j) ? j : (j.brands || []);
    var os = {};
    all.forEach(function (x) { if (x.parentCompany) os[x.parentCompany] = 1; });
    OWNERS = Object.keys(os).sort();
    BRANDS = all.filter(function (x) { return !x.parentCompany; }).map(function (x) {
      return { s: x.slug, n: x.name, t: x.tier, c: (x.category || []).map(function (c) { return CATN[c] || c; }), d: (x.note || '').slice(0, 220) };
    }).sort(function (a, b) { return a.n.toLowerCase() < b.n.toLowerCase() ? -1 : 1; });
    bySlug = {}; BRANDS.forEach(function (b) { bySlug[b.s] = b; });
    var cats = {}; BRANDS.forEach(function (b) { b.c.forEach(function (c) { cats[c] = 1; }); });
    Object.keys(cats).sort().forEach(function (c) { var o = document.createElement('option'); o.value = c; o.textContent = c; $('catSel').appendChild(o); });
    answers = lsGet();
    var first = filtered(); cur = first.length ? first[0].s : null;
    renderAll(); renderCard();
  }).catch(function () {
    $('card').textContent = 'Could not load the brand list. Reload the page.';
  });
})();
</script>
</body>
</html>
"""
open("owner-tool.html", "w", encoding="utf-8").write(OWNER_TOOL)
print("Section 43 applied: owner-tool.html written")

# 45. Avon split by region, Avon (North America), regions shown in the "Does X test on animals?" line, Kmart and Safeway name clashes (14 Oct)
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_av = by.get("avon")
if _av:
    _av["note"] = ("Avon International is certified cruelty-free by Leaping Bunny / Cruelty Free International. Its listing names Africa & The Middle East, Asia, Europe and South & Central America. "
                   "In the US and Canada, Avon is a separate company, The Avon Company, owned by LG Household & Health Care, and isn't on the listing (see Avon (North America)). "
                   "Avon confirmed to me by email that all of its products are vegan, but it has no vegan certification. "
                   "Regent LP, an investment company rather than a manufacturer, owns Avon in Europe, Asia and Africa (it bought Avon International from Natura, reported as closed in January 2026), and Natura keeps Latin America. "
                   "Regent has no animal testing policy of its own that applies to Avon. What counts is each brand's own policy.")
    _av["answer"] = ("In the regions on its listing, no: Avon International is certified cruelty-free. In the US and Canada, Avon is a separate company that isn't certified, and its US site says it sells in China, "
                     "where animal testing is required for some cosmetic categories. The sources are below.")
_new("avon-north-america", "Avon (North America)", "bad",
     "The Avon Company, which sells in the US and Canada, is a separate business from the Avon that holds the Cruelty Free International listing. Its US site says it doesn't conduct animal testing, but that it sells in China, where authorities require animal-based safety testing for some cosmetic categories, and it mentions no certification. Owned by LG Household & Health Care, which bought it in 2019.",
     parent="LG Household & Health Care", category=["makeup-beauty", "skincare", "haircare"], region="USA & Canada", price="£",
     sources=[{"label": "Avon (US): its animal welfare page", "url": "https://www.avon.com/information/animal-welfare.html"},
              {"label": "Cruelty Free International: Avon listing (regions covered)", "url": "https://www.crueltyfreeinternational.org/approved-brands/listing/avon/"},
              {"label": "Cosmetics Design Asia: LG Household & Health Care to acquire Avon North America for $125m (1 May 2019)", "url": "https://cosmeticsdesign-asia.com/Article/2019/05/01/LG-Household-Health-Care-to-acquire-Avon-North-America-for-125m"}])
_km = by.get("Kmart") or by.get("kmart")
if _km and "Australia and New Zealand" not in _km["note"]:
    _km["note"] = _km["note"].rstrip() + " This listing is for Kmart in Australia and New Zealand."
_sf = by.get("safeway")
if _sf and "UK Safeway" not in _sf["note"]:
    _sf["note"] = _sf["note"].rstrip() + " This is the UK Safeway brand, not the US supermarket chain."
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
def _regline(t):
    if "regionSentence" in t: return t
    t = t.replace("function testAnswer(brand) {", "function regionSentence(brand) { return brand.region ? ' Regions on its listing: ' + escapeHtml(brand.region) + '.' : ''; }\nfunction testAnswer(brand) {", 1)
    t = t.replace("or PETA. The sources are below.';\n  if (brand.tier === 'warn')", "or PETA.' + regionSentence(brand) + ' The sources are below.';\n  if (brand.tier === 'warn')", 1)
    t = t.replace("tests on animals or sells where the law requires it.';\n  if (brand.tier === 'bad')", "tests on animals or sells where the law requires it.' + regionSentence(brand);\n  if (brand.tier === 'bad')", 1)
    return t
_rw("scripts/generate-brand-pages.js", _regline)
print("Section 45 applied")

# 46. Avon: two separate listings, each with a plain warning about the other (Ash, 14 Oct)
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_av = by.get("avon"); _an = by.get("avon-north-america")
if _av:
    _av["name"] = "Avon (outside North America)"
    _av["note"] = ("This listing doesn't cover Avon in the US or Canada. Avon there is a different company and isn't certified cruelty-free. "
                   "Avon International is certified cruelty-free by Leaping Bunny / Cruelty Free International. Its listing names Africa & The Middle East, Asia, Europe and South & Central America. "
                   "Avon confirmed to me by email that all of its products are vegan, but it has no vegan certification. "
                   "Regent LP, an investment company rather than a manufacturer, owns Avon in Europe, Asia and Africa (it bought Avon International from Natura, reported as closed in January 2026), and Natura keeps Latin America. "
                   "Regent has no animal testing policy of its own that applies to Avon. What counts is each brand's own policy.")
    _av["answer"] = ("In the regions on its listing, no: Avon International is certified cruelty-free. In the US and Canada, Avon is a separate company that isn't certified, and its US site says it sells in China, "
                     "where animal testing is required for some cosmetic categories. The sources are below.")
if _an:
    _an["name"] = "Avon (North America)"
    _an["note"] = ("If you're buying Avon in the US or Canada, it isn't certified cruelty-free. This is not the same company as the Avon that holds the Cruelty Free International listing in Europe, Africa, Asia and Latin America. "
                   "The Avon Company, which sells in the US and Canada, says on its US site that it doesn't conduct animal testing, but that it sells in China, where authorities require animal-based safety testing for some cosmetic categories, and it mentions no certification. "
                   "Owned by LG Household & Health Care, which bought it in 2019.")
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Section 46 applied")

# 47. Avon: how to tell which Avon you're buying (Ash, 14 Oct)
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_av = by.get("avon"); _an = by.get("avon-north-america")
if _av and "avon.uk.com" not in _av["note"]:
    _av["note"] = _av["note"].rstrip() + (" Not sure which Avon you're buying? Check that it comes from one of Avon's sites outside North America, such as avon.uk.com in the UK or avon.co.in in India, and look for the Leaping Bunny logo. "
                                          "Avon's site for the US and Canada, avon.com, isn't covered. Avon's India site says all of its beauty products are approved under the Leaping Bunny programme.")
    _addsrc(_av, "Avon UK: its website", "https://www.avon.uk.com/")
    _addsrc(_av, "Avon India: its animal testing page (Leaping Bunny approval)", "https://www.avon.co.in/pages/avon-worldwide-1")
if _an and "avon.com" not in _an["note"]:
    _an["note"] = _an["note"].rstrip() + " Not sure which Avon you're buying? If it's from avon.com, it isn't covered by the Cruelty Free International listing. Look for the Leaping Bunny logo, and if it isn't there, check the brand's own site."
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Section 47 applied")

# 48. "Supermarket" category on the checker was empty: no card carried the supermarket tag (14 Oct)
def _sup(t):
    if "'Tesco Kind & Pure'" not in t:
        t = t.replace("'Tesco', 'Asda',", "'Tesco', 'Asda', 'Tesco Kind & Pure', 'Safeway', 'Lidl GB', 'Lidl Ireland & Lidl Northern Ireland', \"Trader Joe's Company\", 'Whole Foods Market 365', 'Cien', 'Lupilu', 'Lacura',", 1)
    if "SUPERMARKET_NAMES.has(brand.name) && seen" not in t:
        t = t.replace("  return seen.join(' ');\n}", "  if (SUPERMARKET_NAMES.has(brand.name) && seen.indexOf('supermarket') === -1) seen.push('supermarket');\n  return seen.join(' ');\n}", 1)
    return t
_rw("scripts/generate-brand-check.js", _sup)
print("Section 48 applied")

# 49. Manhattan and Risqué are Coty brands (Coty's own 26 Sept 2022 release), so they match Rimmel and CoverGirl (14 Oct)
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_cg = by.get("covergirl") or {}
for _s in ("manhattan", "risque"):
    _b = by.get(_s)
    if not _b: continue
    _b.update(parentCompany="Coty", tier="warn", lastVerified=today)
    if "parentTestsOnAnimals" in _cg: _b["parentTestsOnAnimals"] = _cg["parentTestsOnAnimals"]
    _b["note"] = _b["note"].replace(" Cruelty-free approved by Cruelty Free International.", "").rstrip() + " Leaping Bunny / Cruelty Free International certified itself, but owned by Coty, who do test on animals."
    _addsrc(_b, "Coty: Rimmel, Manhattan and Risqué receive Leaping Bunny approval (26 September 2022)", "https://www.businesswire.com/news/home/20220926005006/en")
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Section 49 applied")

# 50. Reddit list part 2 (Ash's research 14 Oct, with her links and findings; PETA searched via crueltyfree.peta.org/?s=).
#     Held back until Ash decides: LORD, Shark, Racer and Dorco (razor blades), Good & Gather (food only).
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
def _vb(slug):
    if slug in by: by[slug]["veganBasis"] = "brand"
_CC = "USA & Canada"
_NC = " Isn't certified by Leaping Bunny / Cruelty Free International or PETA."
# --- certified ---
_new("ecos", "ECOS", "good", "Certified cruelty-free by Leaping Bunny / Cruelty Free International. Its help centre says all its products are vegan, but it has no vegan certification. Made by Earth Friendly Products, which is independently owned by its founding family.",
     vegan="full", vc="medium", category=["household-cleaning", "laundry"], region=_CC,
     sources=[_src("Leaping Bunny: ECOS brand page", "https://www.leapingbunny.org/brand/ecos"), _src("ECOS: its help centre (are your products vegan?)", "https://helpcenter.ecos.com/hc/en-us/articles/23678692646807-Are-your-products-vegan"),
              _src("Cruelty Free International: Earth Friendly Products listing (no parent company)", "https://crueltyfreeinternational.org/node/4342"), _src("ECOS: its FAQ", "https://www.ecos.com/faq/")]); _vb("ecos")
_new("mollys-suds", "Molly's Suds", "check", "Certified cruelty-free by Leaping Bunny / Cruelty Free International. Its detergents and cleaners are made with vegan ingredients, apart from the wool dryer balls, so vegan varies by product. It says it's no longer certified vegan and checks ingredients with its suppliers instead.",
     vegan="partial", vc="medium", category=["laundry", "household-cleaning"], region=_CC,
     sources=[_src("Leaping Bunny: Molly's Suds brand page", "https://www.leapingbunny.org/brand/mollys-suds"), _src("Molly's Suds: its FAQ", "https://mollyssuds.com/pages/faq"), _src("Molly's Suds: certifications and partnerships (vegan ingredients, wool dryer balls)", "https://mollyssuds.com/pages/resources-partnerships"),
              _src("Cruelty Free International: Molly's Suds listing", "https://crueltyfreeinternational.org/node/4577")]); _vb("mollys-suds")
_new("aspenclean", "AspenClean", "good", "Certified cruelty-free by Leaping Bunny / Cruelty Free International and PETA. Its FAQ says its whole product line is 100% vegan, but it has no vegan certification. Independently owned by its founders, Alicia Sokolowski and Chris Solodko.",
     vegan="full", vc="medium", category=["household-cleaning", "laundry"], region=_CC,
     sources=[_src("Leaping Bunny: AspenClean brand page", "https://www.leapingbunny.org/brand/aspenclean"), _src("PETA: AspenClean company page", "https://crueltyfree.peta.org/company/aspenclean/"), _src("AspenClean: cruelty-free cleaning products (100% vegan statement)", "https://aspenclean.com/pages/cruelty-free-cleaning-products-supplies"),
              _src("Cruelty Free International: AspenClean listing (no parent company)", "https://crueltyfreeinternational.org/node/4181")]); _vb("aspenclean")
_new("orly", "Orly", "good", "Certified cruelty-free by Leaping Bunny / Cruelty Free International. Orly says its polishes are fully vegan, but it has no vegan certification. Independently owned: a family-owned company since 1975.",
     vegan="full", vc="medium", category=["makeup-beauty"], region=_CC,
     sources=[_src("Leaping Bunny: Orly brand page", "https://www.leapingbunny.org/brand/orly"), _src("Orly: its vegan nail polish page", "https://www.orlybeauty.co.uk/pages/vegan-nail-polish"), _src("Cruelty Free International: Orly listing", "https://crueltyfreeinternational.org/node/4631")]); _vb("orly")
_new("dropps", "Dropps", "check", "Certified cruelty-free by Leaping Bunny. Its products are vegan apart from the wool dryer balls, which are made from natural wool, so vegan varies by product. Independently owned, with a minority investment from The Craftory in 2020.",
     vegan="partial", vc="high", category=["laundry", "household-cleaning"], region=_CC,
     sources=[_src("Leaping Bunny: Dropps brand page", "https://www.leapingbunny.org/ShopBrandDetail?BrandId=2140"), _src("Dropps: are Dropps products vegan?", "https://info.dropps.com/en-US/are-dropps-products-vegan-417353"), _src("Dropps: are Dropps cruelty-free?", "https://info.dropps.com/en-US/are-dropps-cruelty-free-437953"),
              _src("Private Equity Wire: The Craftory takes a stake in Dropps (19 February 2020)", "https://www.privateequitywire.co.uk/craftory-takes-stake-dropps/")])
_new("cleancult", "Cleancult", "check", "Certified cruelty-free by Leaping Bunny. Most of its liquid and spray products are vegan, but items like the dryer balls contain sheep's wool, so vegan varies by product.",
     vegan="partial", vc="medium", category=["household-cleaning", "laundry"], region=_CC,
     sources=[_src("Leaping Bunny: Cleancult brand page", "https://www.leapingbunny.org/ShopBrandDetail?BrandId=1677")])
_new("lovery", "Lovery", "check", "Certified cruelty-free by Leaping Bunny. Vegan varies by product: some products are labelled 100% vegan, but the brand as a whole isn't vegan. Its FAQ says its products are paraben-free and have never been tested on animals.",
     vegan="partial", vc="medium", category=["body-shower", "skincare"],
     sources=[_src("Leaping Bunny: Lovery brand page", "https://www.leapingbunny.org/brand/lovery"), _src("Lovery: its FAQ", "https://lovery.com/pages/faq")])
# --- says it's cruelty-free, not certified ---
_h = _new("hero-cosmetics", "Hero Cosmetics", "unverified", "Hero Cosmetics says it's cruelty-free and vegan-friendly, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Owned by Church & Dwight, which tests on animals.",
     parent="Church & Dwight", vegan="full", vc="low", claim="Hero Cosmetics says its products are cruelty-free and vegan-friendly.", category=["skincare"],
     sources=[_src("Hero Cosmetics: who is Hero Cosmetics? (cruelty-free and vegan-friendly statement)", "https://www.herocosmetics.us/blogs/news/who-is-hero-cosmetics-the-consciously-clinical-acne-care-company"),
              _src("Cosmetics & Toiletries: Church & Dwight is acquiring Hero Mighty Patch (6 September 2022)", "https://www.cosmeticsandtoiletries.com/news/companies/news/22431732/church-dwight-co-acquiring-hero-mighty-patch"), _LBG, _PETAB]); _vb("hero-cosmetics")
if _h: _h["parentTestsOnAnimals"] = True
_new("suave", "Suave", "unverified", "Suave says it upholds a steadfast no animal testing policy, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. It was on PETA's list in 2020, but isn't listed there now. Not all of its products are vegan. This is the US brand, owned by Evermark. There's also a separate UK brand called Suave Male Grooming.",
     parent="Evermark", vegan="partial", vc="medium", claim="Suave says it upholds a steadfast no animal testing policy.", category=["haircare", "body-shower", "skincare"], region=_CC,
     sources=[_src("Suave: our commitment (no animal testing statement)", "https://www.suave.com/pages/our-commitment"), _src("PETA: announcement that Suave was accredited (12 February 2020)", "https://www.peta.org/?p=952860"),
              _src("Yellow Wood Partners: Suave Brands and Elida Beauty complete merger to create Evermark (20 January 2026)", "https://yellowwoodpartners.com/news-article/yellow-wood-partners-portfolio-companies-suave-brands-and-elida-beauty-complete-merger-to-create-evermark-a-leading-global-platform-of-personal-care-brands"), _LBG, _PETAB])
_new("suave-male-grooming", "Suave Male Grooming (UK)", "unverified", "Suave Male Grooming says it never tests on animals or uses ingredients tested on animals, and that its products are PETA-certified cruelty-free and certified vegan. I couldn't find it on PETA, Leaping Bunny or Cruelty Free International, so it isn't certified by any of them. This is the UK men's grooming brand, not the US brand Suave.",
     vegan="full", vc="low", claim="Suave Male Grooming says it never tests on animals or uses ingredients tested on animals.", category=["haircare", "body-shower"], region="Europe",
     sources=[_src("Suave Products: about us (UK)", "https://suaveproducts.co.uk/about-us/"), _LBG, _PETAB]); _vb("suave-male-grooming")
_new("purito", "Purito", "unverified", "Purito says it's vegan and cruelty-free, and that its suppliers don't test on animals either, but it isn't certified by any organisation.",
     vegan="full", vc="low", claim="Purito says its products are vegan and cruelty-free, and that its suppliers don't test on animals.", category=["skincare"], region="Asia",
     sources=[_src("Purito: its FAQ", "https://purito.com/help/faq/"), _LBG, _PETAB]); _vb("purito")
_new("orange-house", "Orange House", "unverified", "Orange House says it's cruelty-free and 100% vegan, and that it never tests on animals, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Its site links to YFYCPG, but doesn't explain how the two are related.",
     vegan="full", vc="low", claim="Orange House says it's cruelty-free and 100% vegan, and never tests its products on animals.", category=["household-cleaning", "laundry"],
     sources=[_src("Orange House: contact us / FAQ", "https://orangehouseglobal.com/pages/contactus"), _src("Orange House: its liquid laundry detergent page", "https://orangehouseglobal.com/products/orange-house-liquid-laundry-detergent"), _LBG, _PETAB]); _vb("orange-house")
_new("the-clean-people", "The Clean People", "unverified", "The Clean People says it's cruelty-free and vegan, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA.",
     vegan="full", vc="low", claim="The Clean People says its products are cruelty-free and vegan.", category=["laundry", "household-cleaning"],
     sources=[_src("The Clean People: top reasons to switch", "https://www.getcleanpeople.com/top-reasons-switch-clean-people/"), _LBG, _PETAB]); _vb("the-clean-people")
_new("naturewell", "Naturewell", "unverified", "Naturewell says it's cruelty-free and vegan, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Owned by AX Beauty Brands.",
     parent="AX Beauty Brands", vegan="full", vc="low", claim="Naturewell says it's cruelty-free and vegan.", category=["skincare", "body-shower"],
     sources=[_src("Naturewell: the importance of cruelty-free beauty", "https://naturewellbeauty.com/blogs/blog/the-importance-of-cruelty-free-beauty"), _src("Cosmetics Design: Naturewell's lip collection hits 3,000 Walmart stores (AX Beauty Brands)", "https://www.cosmeticsdesign.com/Article/2025/09/04/naturewells-lip-collection-hits-3000-walmart-stores"), _LBG, _PETAB]); _vb("naturewell")
_new("sympli-beautiful", "Sympli Beautiful", "unverified", "Sympli Beautiful is iHerb's own skincare brand. iHerb lists it as cruelty-free and its packaging says so, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Vegan varies by product, so check each product's ingredients. This isn't the Canadian clothing brand Sympli.",
     parent="iHerb", vegan="partial", vc="low", claim="iHerb lists Sympli Beautiful as cruelty-free, and its packaging says so.", category=["skincare"],
     sources=[_src("SkinSort: Sympli Beautiful (cruelty-free brand claim)", "https://skinsort.com/products/sympli-beautiful/serumdipity-pycnogenol-serum"), _LBG, _PETAB])
_new("beloved", "Beloved", "unverified", "Beloved says its products are PETA approved and vegan, but it isn't listed on PETA's cruelty-free list now. It's a spin-off line of Love Beauty and Planet, which is listed by PETA but owned by Unilever.",
     parent="Unilever", vegan="full", vc="low", claim="Beloved says its products are PETA approved and vegan.", category=["body-shower"], region=_CC,
     sources=[_src("Beloved: about us (PETA approved claim)", "https://www.belovedbathandbody.com/us/en/about-beloved/about-us.html"), _src("PETA: Love Beauty and Planet (Unilever) company page", "https://crueltyfree.peta.org/company/love-beauty-and-planet-unilever/"), _PETAB]); _vb("beloved")
_new("safely", "Safely", "unverified", "Safely says it doesn't test on animals at any stage of product development, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. It's marketed as a vegan household and personal care brand. Independently owned.",
     vegan="full", vc="low", claim="Safely says it doesn't test on animals at any stage of product development.", category=["household-cleaning", "body-shower"], region=_CC,
     sources=[_src("Safely: its FAQ", "https://getsafely.com/pages/faq"), _src("Happi: Safely receives B Corp certification (vegan household and personal care brand)", "https://www.happi.com/breaking-news/vegan-household-and-personal-care-brand-safely-receives-b-corp-certification/"), _LBG, _PETAB]); _vb("safely")
_new("native", "Native", "unverified", "Native says it doesn't test on animals, but it isn't certified by Leaping Bunny / Cruelty Free International, and PETA lists it as a company that may not be cruelty-free. Owned by Procter & Gamble, who test where legally required.",
     parent="Procter & Gamble", vegan="full", vc="low", claim="Native says its products are made without animal testing, and that none of their ingredients come from animals.", category=["body-shower", "hygiene"], region=_CC,
     sources=[_src("Native: its FAQ", "https://nativecos.com/pages/faq"), _src("PETA: Native company page (may not be cruelty-free)", "https://crueltyfree.peta.org/company/native/"), _src("CNBC: P&G has acquired Native (15 November 2017)", "https://www.cnbc.com/2017/11/15/pg-has-acquired-native-natural-deodorant-brand.html")]); _vb("native")
if "native" in by: by["native"]["parentTestsOnAnimals"] = True
_new("pop-arazzi", "Pop-arazzi", "unverified", "Pop-arazzi is CVS's own nail polish brand. CVS says it doesn't test its store brand products on animals, and its product page says the polish is vegan, but Pop-arazzi isn't certified by Leaping Bunny / Cruelty Free International or PETA.",
     parent="CVS Health Corporation", vegan="full", vc="low", claim="CVS says it doesn't test any store brand products on animals.", category=["makeup-beauty"],
     sources=[_src("CVS Health: its animal testing policy", "https://www.cvshealth.com/policies/animal-testing"), _src("CVS Health: Pop-arazzi nail polish product page (vegan statement)", "https://static-assets-reg.cvshealth.com/shop/pop-arazzi-nail-polish-prodid-1015173"), _src("PETA: CVS company page (may not be cruelty-free)", "https://crueltyfree.peta.org/company/cvs/"), _LBG]); _vb("pop-arazzi")
# --- certified by PETA only ---
_new("biokleen", "Biokleen", "check", "Listed by PETA as cruelty-free. I couldn't confirm whether its products are vegan. Owned by PurposeBuilt Brands. This is Biokleen (Bi-O-Kleen) the laundry and household cleaning brand, not the industrial cleaner Bio-Kleen or the Swedish wood-care brand BIOkleen.",
     parent="PurposeBuilt Brands", vegan="unknown", category=["laundry", "household-cleaning"], region=_CC,
     sources=[_src("PETA: Biokleen company page", "https://crueltyfree.peta.org/company/biokleen/"), _src("Biokleen: its story (never tested on animals)", "https://biokleenhome.com/our-story"), _src("PurposeBuilt Brands: its brands", "https://purposebuiltbrands.com/brands"), _LBG])
_new("sonett", "Sonett", "check", "Listed by PETA as cruelty-free. Most of its products carry the Vegan Society label, but a few (such as Wool Care and Gall Soap) aren't vegan, so vegan varies by product. Independently owned German company, founded in 1977.",
     vegan="partial", vc="medium", category=["laundry", "household-cleaning"], region="Europe",
     sources=[_src("PETA: SONETT company page", "https://crueltyfree.peta.org/company/sonett/"), _src("Cosh: Sonett brand page (Vegan Society label, non-vegan products)", "https://cosh.eco/en/brands/sonett"), _src("Sonett: about the company (founded 1977)", "https://www.sonett.eu/unternehmen/"), _LBG])
# --- owner tests / sells where required ---
_new("dreft", "Dreft", "bad", "Dreft tests on animals. It has no animal testing policy of its own, so it takes its owner's position: Procter & Gamble tests where required by law. It isn't certified by Leaping Bunny / Cruelty Free International or PETA, and isn't vegan.",
     parent="Procter & Gamble", vegan="no", category=["laundry"], region=_CC,
     sources=[_src("Procter & Gamble: its animal testing position (published on its Downy page)", "https://downy.com/en-us/fabric-softener-tips/how-to-use-downy/does-downy-test-on-animals"), _PETAB])
if "dreft" in by: by["dreft"]["parentTestsOnAnimals"] = True
_new("eucerin", "Eucerin", "bad", "Eucerin tests on animals where required. Its UK page says it avoids animal testing wherever the law allows, but where Chinese law requires official safety registration, state-authorised institutes may test. PETA lists it as a company that may not be cruelty-free, and it isn't certified by Leaping Bunny / Cruelty Free International. Owned by Beiersdorf.",
     parent="Beiersdorf", vegan="unknown", category=["skincare"],
     sources=[_src("Eucerin UK: animal testing", "https://eucerin.co.uk/sustainability/products-and-ingredients/animal-testing"), _src("PETA: Eucerin company page", "https://crueltyfree.peta.org/company/eucerin/"), _LBG])
_new("essie", "Essie", "bad", "Essie tests on animals where required. It isn't certified by Leaping Bunny / Cruelty Free International, and PETA lists it as a company that may not be cruelty-free. Owned by L'Oréal, which says some health authorities, such as China's, may still require animal tests. Essie describes some of its polishes as a vegan formula, but it isn't certified vegan.",
     parent="L'Oréal", vegan="partial", vc="low", category=["makeup-beauty"],
     sources=[_src("PETA: Essie Cosmetics company page", "https://crueltyfree.peta.org/company/essie-cosmetics/"), _src("L'Oréal: its alternative methods to animal testing", "https://www.loreal.com/en/canada/articles/commitments/our-alternative-methods-to-animal-testing/"), _src("L'Oréal: its Essie brand page", "https://www.loreal.com/en/consumer-products-division/essie/"), _LBG])
_new("all-laundry", "all (laundry detergent)", "bad", "all tests on animals where required. Its owner, Henkel, says it doesn't test hair and body care products on animals, but that animal testing is still mandatory in some countries and it can't rule out that an ingredient was tested at some point. It isn't certified by Leaping Bunny / Cruelty Free International or PETA. all is the US and Canada brand, which came to Henkel with its purchase of The Sun Products Corporation.",
     parent="Henkel", vegan="unknown", category=["laundry"], region=_CC,
     sources=[_src("Henkel: its position on test methods", "https://www.henkel.com/sustainability/positions/test-methods"), _src("Henkel: news release on acquiring The Sun Products Corporation (24 June 2016)", "https://www.henkel.com/resource/blob/691590/1e18cb471cb8a545953e696c8237f830/data/news-release-henkel-to-acquire-sun-products.pdf"), _LBG, _PETAB])
# --- no information found ---
_new("klavuu", "Klavuu", "unverified", "I couldn't find an animal testing policy for Klavuu, and it isn't certified by Leaping Bunny / Cruelty Free International or PETA. It has some products sold as vegan and cruelty-free, such as the Real Vegan Collagen Cream, but the brand as a whole isn't certified, so vegan varies by product.",
     vegan="partial", vc="low", category=["skincare"], region="Asia",
     sources=[_src("Klavuu: its website", "https://www.klavuu.com/en"), _LBG, _PETAB])
_new("kumano-cosme", "Kumano Cosme", "unverified", "I couldn't find a published animal testing policy for Kumano Cosme, and it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Owned by Kumanoyushi Co., Ltd. Vegan varies by product: the range includes horse oil and honey-based products.",
     parent="Kumanoyushi Co., Ltd.", vegan="partial", vc="low", category=["haircare", "body-shower", "skincare"], region="Asia",
     sources=[_src("Kumanoyushi: its website", "https://www.kumanoyushi.co.jp/"), _LBG, _PETAB])
_new("fuwa3e", "Fuwa3e", "unverified", "I couldn't find an animal testing policy for Fuwa3e, and it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Made by FUWA Biotech Co., Ltd in Thanh Hoa, Vietnam. Its site says the enzyme comes from plants, but it makes no vegan claim.",
     vegan="unknown", category=["laundry", "household-cleaning"], region="Asia",
     sources=[_src("FUWA: Eco enzyme Fuwa3e", "https://fuwa.com.vn/en/eco-enzyme-fuwa3e/"), _LBG, _PETAB])
_new("equate", "Equate", "unverified", "Equate is Walmart's own health and beauty brand. I couldn't find an animal testing policy for it, and it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Much of the range is pharmacy products.",
     parent="Walmart Inc.", category=["skincare", "hygiene"], region=_CC,
     sources=[_src("Walmart: Equate brand page", "https://www.walmart.com/c/brand/equate-equate-collection"), _LBG, _PETAB])
_new("solimo", "Solimo", "unverified", "Solimo is Amazon's own brand across household, kitchen and personal care. I couldn't find an animal testing policy for it, and it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Some Solimo products are now sold as Amazon Basics.",
     parent="Amazon", category=["household-cleaning", "skincare"],
     sources=[_src("Wikipedia: list of Amazon brands", "https://en.wikipedia.org/wiki/List_of_Amazon_brands"), _LBG, _PETAB])
for _s in ("ecos", "mollys-suds", "aspenclean", "orly", "dropps", "cleancult", "lovery", "hero-cosmetics", "suave", "suave-male-grooming", "purito", "orange-house", "the-clean-people", "naturewell", "sympli-beautiful", "beloved", "safely", "native", "pop-arazzi", "biokleen", "sonett", "dreft", "eucerin", "essie", "all-laundry", "klavuu", "kumano-cosme", "fuwa3e", "equate", "solimo"):
    if _s in by: by[_s]["lastVerified"] = today
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
def _sm2(t):
    if "'Equate'" in t: return t
    return t.replace("'Beauty 360',", "'Beauty 360', 'Equate', 'Solimo', 'Pop-arazzi',", 1)
_rw("scripts/generate-brand-check.js", _sm2)
print("Section 50 applied")

# 51. Razor brands (Ash, 14 Oct): LORD, Shark, Racer (LORD brands) and Dorco. Nothing about animal testing or vegan is on any page read;
#     the Dorco "consumer panels" quote and the stearate / vegan reasoning are from an AI overview with no source, so they are not on the site.
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_LS = _src("LORD: its website (shaving brands)", "https://www.lordshave.net/")
_new("lord-razors", "LORD", "unverified", "I couldn't find an animal testing policy for LORD razor blades, and they aren't certified by Leaping Bunny / Cruelty Free International or PETA. LORD International Co. is based in Alexandria, Egypt, founded in 1930. I couldn't find a vegan claim either. This is the razor blade company, not another brand called Lord.",
     parent="LORD International Co.", category=["hygiene"], region="Europe",
     sources=[_src("LORD: about the company (no animal testing statement)", "https://razorslord.com/?page_id=1209"), _src("LORD: its profile and history", "https://www.lordshave.net/history.php"), _LBG, _PETAB])
_new("shark-razors", "Shark (razor blades)", "unverified", "Shark razor blades are a LORD brand, so I've assumed LORD's position applies. I couldn't find an animal testing policy, and Shark isn't certified by Leaping Bunny / Cruelty Free International or PETA. I couldn't find a vegan claim either. This is the razor brand made by LORD International Co. in Egypt, not the vacuum and hair tools company Shark.",
     parent="LORD International Co.", category=["hygiene"],
     sources=[_src("LORD: Shark razors", "https://www.lordshave.net/category/Shaving/Shark/5"), _LS, _LBG, _PETAB])
_new("racer-razors", "Racer (razor blades)", "unverified", "Racer razor blades are a LORD brand, so I've assumed LORD's position applies. I couldn't find an animal testing policy, and Racer isn't certified by Leaping Bunny / Cruelty Free International or PETA. I couldn't find a vegan claim either.",
     parent="LORD International Co.", category=["hygiene"],
     sources=[_src("LORD: Racer razors", "https://www.lordshave.net/category/Shaving/Racer/4"), _LS, _LBG, _PETAB])
_new("dorco", "Dorco", "unverified", "I couldn't find a published animal testing policy for Dorco, and it isn't certified by Leaping Bunny / Cruelty Free International or PETA. It isn't on PETA's razor guide. I couldn't find a vegan claim or certification either. Dorco Co., Ltd. is based in Seoul, South Korea, and sells in the US as Dorco USA.",
     category=["hygiene"], region="Asia",
     sources=[_src("Dorco USA: about", "https://dorcousa.com/private-label-razors-razor-store-brands-brand-oem-about"), _src("PETA: cruelty-free razors guide (Dorco isn't listed)", "https://peta.org/?p=976374"), _LBG, _PETAB])
for _s in ("lord-razors", "shark-razors", "racer-razors", "dorco"):
    if _s in by: by[_s]["lastVerified"] = today
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Section 51 applied")

# 52. Fuwa3e, Equate, Solimo updated with Ash's findings (14 Oct)
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_f = by.get("fuwa3e")
if _f:
    _f.update(vegan="full", vegan_conf=None, veganConfidence="high", veganBasis="certified", claim="Fuwa3e says: \"We are committed to never testing any products on animals at any stages of research and development.\"", lastVerified=today,
        note="Fuwa3e says it never tests its products on animals at any stage of research and development, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. It's certified vegan by the Vegan Society. Made by FUWA Biotech Co., Ltd in Thanh Hoa, Vietnam.")
    _f.pop("vegan_conf", None)
    _addsrc(_f, "FUWA: about Fuwa (never testing on animals statement)", "https://fuwa.com.vn/en/about-fuwa/")
_e = by.get("equate")
if _e:
    _e["note"] = "Equate is Walmart's own health and beauty brand. I couldn't find an animal testing policy or any vegan information for it, and it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Much of the range is pharmacy products."
    _e["lastVerified"] = today
_s = by.get("solimo")
if _s:
    _s.update(vegan="no", veganConfidence="low", lastVerified=today,
        note="Solimo is Amazon's own brand across household, kitchen and personal care. It has no clear animal testing policy and isn't certified by Leaping Bunny / Cruelty Free International or PETA. It has no clear ingredient information, so it's listed as not vegan. Some Solimo products are now sold as Amazon Basics.")
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Section 52 applied")

# 53. Say which vegan certifier a brand has (Ash, 14 Oct). Brand pages: "100% vegan (certified by X)" already existed; now also in the page text,
#     "brand's word" brands say they have no vegan certification, and brands with no vegan source yet say the certifier isn't confirmed.
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
if "fuwa3e" in by: by["fuwa3e"]["veganCert"] = "Vegan Society"
_nt = by.get("natracare")
if _nt: _nt.update(veganBasis="certified", veganCert="Vegetarian Society", veganConfidence="high", lastVerified=today)
_sn = by.get("sonett")
if _sn: _sn["veganCert"] = "Vegan Society"
for _b in brands:
    if _b.get("veganBasis") == "certified" and _b.get("veganCert") and _b["veganCert"].lower() not in (_b.get("note") or "").lower():
        _b["note"] = (_b.get("note") or "").rstrip() + " Certified vegan by %s." % _b["veganCert"]
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
def _vl(t):
    if "certifier not yet confirmed" in t: return t
    old = "brand.veganBasis === 'brand' ? \"100% vegan (brand's word)\" : '100% vegan')\n    : brand.vegan === 'partial' ? 'varies by product'"
    new = "brand.veganBasis === 'brand' ? \"100% vegan (brand's word, no vegan certification)\" : '100% vegan (certifier not yet confirmed)')\n    : brand.vegan === 'partial' ? (brand.veganCert ? 'varies by product (some certified by ' + escapeHtml(brand.veganCert) + ')' : 'varies by product')"
    return t.replace(old, new, 1)
_rw("scripts/generate-brand-pages.js", _vl)
print("Section 53 applied")

# 54. Biokleen (biokleenhome.com, Bi-O-Kleen): FAQ says never tested on animals and no animal ingredients in any formulation; no vegan certification (Ash, 14 Oct).
#     Not the same company as Bio-Kleen Products, Inc. (Kalamazoo, biokleen.com), whose page says "cruelty-free and vegan" -- not applied to this brand.
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_bk = by.get("biokleen")
if _bk:
    _bk.update(tier="good", vegan="full", veganConfidence="medium", veganBasis="brand", lastVerified=today,
        note="Listed by PETA as cruelty-free. Its FAQ says it has never tested a single Biokleen product on an animal, nor used animal ingredients in any formulation, but it has no vegan certification. Owned by PurposeBuilt Brands. This is Biokleen (Bi-O-Kleen) the laundry and household cleaning brand, not the industrial cleaner Bio-Kleen or the Swedish wood-care brand BIOkleen.")
    _addsrc(_bk, "Biokleen: its FAQ (never tested on animals, no animal ingredients)", "https://biokleenhome.com/faq")
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Section 54 applied")

# 55. Reddit list part 3 (15 Oct). Held back for Ash to check first: Bioré, Mary&May, Patrick Ta, Fenty Beauty, China Glaze, Glamnetic, JASON, Isntree, California Naturals.
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
def _pl(slug, label): return _src("PETA: %s company page" % label, "https://crueltyfree.peta.org/company/%s/" % slug)
_NOPETA = " Isn't certified by Leaping Bunny / Cruelty Free International or PETA."
# --- tests on animals / sells where required ---
_new("aquaphor", "Aquaphor", "bad", "Aquaphor tests on animals where required. Its owner, Beiersdorf, says it doesn't test on animals unless the law specifically requires it, and names China. It isn't certified by Leaping Bunny / Cruelty Free International or PETA, and isn't vegan: it contains lanolin alcohol and beeswax.",
     parent="Beiersdorf", vegan="no", category=["skincare"], region=_CC,
     sources=[_src("Beiersdorf: research for alternatives to animal testing", "https://beiersdorf.com/about-us/research/research-for-alternatives-to-animal-testing"), _PETAB])
_new("laneige", "Laneige", "bad", "Laneige tests on animals where required. PETA lists it as a company that may not be cruelty-free, and it isn't certified by Leaping Bunny / Cruelty Free International. Owned by Amorepacific, whose policy allows animal testing where other countries' regulations require it. It isn't a vegan brand.",
     parent="Amorepacific Group", vegan="no", category=["skincare", "makeup-beauty"], region="Asia",
     sources=[_pl("laneige", "Laneige"), _src("Amorepacific: its declaration on animal testing", "https://www.apgroup.com/int/en/commitments/respect-for-life/declaration-of-prohibition/declaration-of-prohibition.html"), _LBG])
_new("sheamoisture", "SheaMoisture", "bad", "SheaMoisture tests on animals. Its FAQ says it doesn't test its products or ingredients on animals, but that some new US categories, such as antiperspirants and SPF, use ingredients its suppliers tested on animals to meet regulations, so it no longer meets PETA's criteria. It isn't certified by Leaping Bunny / Cruelty Free International or PETA. Owned by Unilever, which bought Sundial Brands in 2017. Only some products are vegan.",
     parent="Unilever", vegan="partial", category=["haircare", "body-shower", "skincare"], region=_CC,
     sources=[_src("SheaMoisture: its FAQ (animal testing statement)", "https://www.sheamoisture.com/faqs.html"), _src("Black Enterprise: Unilever acquires Sundial Brands, owner of SheaMoisture (2017)", "https://blackenterprise.com/unilever-acquires-sundial-brands-owner-of-sheamoisture-in-for-undisclosed-amount/"), _PETAB])
_new("dawn", "Dawn", "bad", "Dawn tests on animals where required. Its own page says Dawn doesn't test its products on animals, that Procter & Gamble stopped animal testing for consumer products unless required by law, and that some cleaning ingredients may face regulator testing requirements. It isn't certified by Leaping Bunny / Cruelty Free International or PETA, and I couldn't find a vegan claim. This is the US dish soap, not the UK P&G brand Fairy.",
     parent="Procter & Gamble", category=["household-cleaning"], region=_CC,
     sources=[_src("Dawn: is Dawn cruelty-free?", "https://dawn-dish.com/en-us/how-to/is-dawn-cruelty-free/"), _PETAB])
_new("biofreeze", "Biofreeze", "bad", "Biofreeze takes its owner's position: Reckitt says it doesn't generally test on animals, but that governments sometimes require animal studies. Its FAQ says nothing on animal testing, and it isn't certified by Leaping Bunny / Cruelty Free International or PETA. I couldn't find a vegan claim. Reckitt bought it from Performance Health in 2021.",
     parent="Reckitt Benckiser", category=["hygiene"], region=_CC,
     sources=[_src("Reckitt: its animal testing policy", "https://www.reckitt.com/media/5833/rb-animal-testing-policy-2019.pdf"), _src("NJBIZ: RB completes Biofreeze and TheraPearl acquisition (12 July 2021)", "https://njbiz.com/rb-completes-biofreeze-therapearl-acquisition/"), _src("Biofreeze: its FAQ", "https://www.biofreeze.com/faq"), _PETAB])
# --- cruelty-free itself, owner isn't ---
_s = _new("secret-deodorant", "Secret", "warn", "Listed by PETA as cruelty-free (Secret deodorant, 2020), but owned by Procter & Gamble, who test on animals where required by law. Its website shows an icon saying cruelty free, paraben free and vegan, which is the brand's own claim and I couldn't tell which products it covers. This is the deodorant, not Victoria's Secret.",
     parent="Procter & Gamble", vegan="partial", vc="low", category=["hygiene", "body-shower"], region=_CC,
     sources=[_pl("secret-procter-gamble", "Secret"), _src("PETA: Secret deodorant is cruelty-free (8 July 2020)", "https://www.peta.org/news/secret-deodorant-cruelty-free/"), _src("Secret: Secret is cruelty-free", "https://secret.com/en-us/about/secret-is-cruelty-free")])
if _s: _s["parentTestsOnAnimals"] = True
_new("innisfree", "Innisfree", "warn", "Listed by PETA as cruelty-free (the brand says it was certified on 1 February 2024), but owned by Amorepacific, whose policy allows animal testing where other countries' regulations require it. It isn't Leaping Bunny certified. Some products are vegan, but no vegan certification is named.",
     parent="Amorepacific Group", vegan="partial", vc="low", category=["skincare"], region="Asia",
     sources=[_pl("innisfree", "Innisfree"), _src("Innisfree: better for Earth (PETA certification)", "https://au.innisfree.com/pages/better-for-earth"), _src("Amorepacific: its declaration on animal testing", "https://www.apgroup.com/int/en/commitments/respect-for-life/declaration-of-prohibition/declaration-of-prohibition.html")])
# --- certified ---
_new("one-with-nature", "One with Nature", "check", "Approved by Leaping Bunny (through CCIC, the US and Canada partner programme) and listed by PETA as cruelty-free. Some products are vegan, but not every one, and no vegan certification is named. No parent company is listed.",
     vegan="partial", vc="low", category=["body-shower", "skincare"], region=_CC,
     sources=[_src("Cruelty Free International: One With Nature listing", "https://www.crueltyfreeinternational.org/cruelty-free-company/one-nature"), _pl("one-with-nature", "One With Nature"), _src("Thrive Market: One With Nature", "https://thrivemarket.com/brand/one-with-nature")])
_new("makeup-by-mario", "Makeup by Mario", "check", "Listed by PETA as cruelty-free. Not every product is vegan, and no vegan certification is named. Founded by Mario Dedivanovic, with minority investment from Provenance and Silas Capital in 2023. It was reported to be exploring a sale in 2024, but I found no completed sale.",
     vegan="partial", vc="low", category=["makeup-beauty"],
     sources=[_pl("makeup-by-mario", "Makeup By Mario"), _src("Cosmetics Business: Makeup by Mario exploring a potential brand sale (18 June 2024)", "https://www.cosmeticsbusiness.com/makeup-by-mario-exploring-potential-brand-sale"), _LBG])
_new("kimchi-chic-beauty", "Kimchi Chic Beauty", "check", "Listed by PETA as cruelty-free. Not every product is vegan, and no vegan certification is named. This is the makeup brand of the drag queen Kim Chi.",
     vegan="partial", vc="low", category=["makeup-beauty"],
     sources=[_pl("kimchi-chic-beauty", "KimChi Chic Beauty"), _LBG])
_new("artnaturals", "Artnaturals", "check", "Listed by PETA as cruelty-free (its PETA page was last updated in 2020). It says its products are vegan, but its lip balm contains beeswax, so vegan varies by product, and no vegan certification is named. Founded by a family of brothers.",
     vegan="partial", vc="low", category=["skincare", "haircare"],
     sources=[_pl("artnaturals", "artnaturals"), _src("RangeMe: Artnaturals supplier spotlight (21 June 2018)", "https://www.rangeme.com/blog/supplier-spotlight-artnaturals-artfully-makes-a-deal-with-meijer/"), _LBG])
_new("skin1004", "SKIN1004", "check", "Listed by PETA as cruelty-free (page last modified 27 April 2026). I couldn't find a vegan certification, and its vegan status isn't confirmed. Made by Craver Corporation, a Korean private company.",
     vegan="unknown", category=["skincare"], region="Asia",
     sources=[_pl("skin1004-co", "SKIN1004 (Craver Corporation)"), _LBG])
_new("raw-sugar", "Raw Sugar", "check", "Listed by PETA as cruelty-free (page last modified 26 October 2022). Its FAQ says its products are PETA-certified animal test-free and vegan, but PETA's page doesn't mention vegan, and I couldn't find a vegan certification. Acquired by WM Partners in August 2021. This is Raw Sugar Living, not Raw Sugar Science.",
     parent="WM Partners LP", vegan="partial", vc="low", category=["body-shower", "skincare"], region=_CC,
     sources=[_pl("raw-sugar-bolero-home-decor", "Raw Sugar (Bolero Home Décor)"), _src("Raw Sugar Living: its FAQ", "https://rawsugarliving.com/pages/faq"), _src("Oaklins: WM Partners acquires Raw Sugar Living", "https://www.oaklins.com/sg/en/deals/107586/")])
_new("summer-fridays", "Summer Fridays", "check", "Certified cruelty-free by Leaping Bunny (since 2018), but PETA lists it as a company that may not be cruelty-free because it hasn't signed PETA's statement. TSG Consumer Partners made a strategic growth investment in July 2024, and the co-founders, Marianna Hewitt and Lauren Ireland, kept a significant stake. I couldn't confirm whether its products are vegan.",
     parent="TSG Consumer Partners", vegan="unknown", category=["skincare"],
     sources=[_src("Leaping Bunny: Summer Fridays brand page", "https://www.leapingbunny.org/brand/summer-fridays"), _pl("summer-fridays", "Summer Fridays"), _src("Business Wire: Summer Fridays announces strategic growth investment from TSG Consumer (25 July 2024)", "https://www.businesswire.com/news/home/20240725229112/en/summer-fridays-announces-strategic-growth-investment-from-tsg-consumer")])
_new("olivella", "Olivella", "good", "Listed by PETA as cruelty-free (Umbria Olii International USA, page last updated 2020). Its website shows a vegan badge but names no vegan certifier. This is the Italian olive oil soap and skincare brand.",
     vegan="full", vc="low", category=["body-shower", "skincare"], region=_CC,
     sources=[_pl("olivella-umbria-olii-international-usa", "Olivella (Umbria Olii International USA)"), _src("Olivella: its website", "https://www.olivellaline.com/")]); _vb("olivella")
_new("dashing-diva", "Dashing Diva", "check", "Listed by PETA as cruelty-free (page last modified 31 August 2020). A 2021 trade interview quotes it as 100% vegan and cruelty-free, but I couldn't find a vegan certification. Founded by John Chang in 2003.",
     vegan="unknown", category=["makeup-beauty"], region=_CC,
     sources=[_pl("dashing-diva", "Dashing Diva"), _src("Chain Drug Review: Dashing Diva benefits from at-home nail care demand (7 June 2021)", "https://digitaledition.chaindrugreview.com/articles/dashing-diva-benefits-from-at-home-nail-care-demand")])
# --- says it's cruelty-free, not certified ---
_new("everspring", "Everspring", "unverified", "Everspring is Target's own soap and household brand. Target's product page says it's never tested on animals and lists it as cruelty-free, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. It isn't certified vegan: some products are listed as animal by-product-free, so vegan varies by product.",
     parent="Target Corporation", vegan="partial", vc="low", claim="Target says its Everspring products are never tested on animals.", category=["body-shower", "household-cleaning"], region=_CC,
     sources=[_src("Target: Everspring hand soap product page", "https://www.target.com/p/-/A-75663156"), _LBG, _PETAB])
_new("aplb", "APLB", "unverified", "APLB says it's proudly cruelty-free and doesn't test on animals, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. I couldn't find its owner or a vegan claim. It's a Korean skincare brand founded in 2017.",
     vegan="unknown", claim="APLB says it's proudly a cruelty-free brand and doesn't test on animals.", category=["skincare"], region="Asia",
     sources=[_src("Skinsider: K-beauty innovators, a conversation with APLB (30 May 2025)", "https://skinsider.co.uk/blog/kbeauty-innovators-a-conversation-with-korean-skincare-brand-aplb/"), _LBG, _PETAB])
_new("palmers", "Palmer's", "unverified", "Palmer's says its products are not tested on animals, but it isn't certified by Leaping Bunny / Cruelty Free International, and PETA lists it as a company that may not be cruelty-free. Family owned and operated since 1840 (E.T. Browne Drug Co.). Some products are vegan, marked with its own Vegan Friendly Bunny seal rather than a vegan certification.",
     parent="E.T. Browne Drug Co.", vegan="partial", vc="low", claim="Palmer's says its products are not tested on animals.", category=["skincare", "body-shower", "haircare"], region=_CC,
     sources=[_src("Palmer's: its FAQ", "https://www.palmers.com/pages/faq"), _pl("palmers", "Palmer's"), _LBG])
_new("mario-badescu", "Mario Badescu", "unverified", "Mario Badescu says it doesn't test its products or ingredients on animals, nor ask others to test on its behalf, but it isn't certified by Leaping Bunny / Cruelty Free International, and PETA lists it as a company that may not be cruelty-free. Family-owned. It says it isn't a vegan line, though some products are vegan friendly.",
     vegan="partial", vc="low", claim="Mario Badescu says it doesn't test its products or ingredients on animals, nor ask others to test on its behalf.", category=["skincare"], region=_CC,
     sources=[_src("Mario Badescu: its FAQ", "https://www.mariobadescu.com/faq"), _pl("mario-badescu", "Mario Badescu"), _src("Success: from the beauty counter to the front office", "https://www.success.com/from-the-beauty-counter-to-the-front-office")])
_new("haus-labs", "Haus Labs", "unverified", "Haus Labs says it's always cruelty-free and vegan, and Sephora's brand page says none of its formulas, ingredients or final products are tested on animals, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA, and no vegan certifier is named. Founded by Lady Gaga and Ben Jones in 2019, with minority investors, and formerly called Haus Laboratories.",
     vegan="full", vc="low", claim="Haus Labs says it's always cruelty-free and vegan, and that none of its formulas, ingredients or final products are tested on animals.", category=["makeup-beauty"],
     sources=[_src("Sephora: Haus Labs by Lady Gaga vegan makeup (brand FAQ)", "https://www.sephora.com/brand/haus-labs-by-lady-gaga/vegan-makeup"), _src("Wikipedia: Haus Labs", "https://en.wikipedia.org/wiki/Haus_Labs"), _LBG, _PETAB]); _vb("haus-labs")
# --- no information found ---
_new("gisou", "Gisou", "unverified", "I couldn't find a cruelty-free claim or certification for Gisou. Its FAQ says animal testing of cosmetics is illegal and that it follows EU regulation. It isn't certified by Leaping Bunny / Cruelty Free International or PETA. Not vegan: it uses honey and propolis. Owned mainly by its founders, Negin Mirsalehi and Maurits Stibbe, with minority investment from Eurazeo.",
     vegan="no", category=["haircare"], region="Europe",
     sources=[_src("Gisou: its FAQ", "https://www.gisou.com/pages/faq"), _src("Beauty Matter: Gisou raises Series B round with Eurazeo Brands", "https://beautymatter.com/articles/haircare-brand-gisou-raises-series-b-round-with-eurazeo-brands"), _LBG, _PETAB])
_new("elizavecca", "Elizavecca", "unverified", "I couldn't find an animal testing policy or certification for Elizavecca. It isn't vegan: some products contain pig collagen and snail secretion. I couldn't find who owns it.",
     vegan="no", category=["skincare"], region="Asia",
     sources=[_src("Buy Beauty Korea: Elizavecca", "https://buybeautykorea.com/collections/elizavecca"), _LBG, _PETAB])
_new("pert", "Pert", "unverified", "I couldn't find an animal testing policy or certification for Pert. In the US it's owned by Sodalis Group (after HRB Brands), but Procter & Gamble kept the brand in other regions. I couldn't find a vegan claim.",
     parent="Sodalis Group", category=["haircare"], region=_CC,
     sources=[_src("PE Professional: HRB Brands acquired by Sodalis Group (October 2024)", "https://peprofessional.com/2024/10/hrb-brands-acquired-by-sodalis-group/"), _src("Progressive Grocer: private equity firm acquires Pert Plus brand from P&G", "https://progressivegrocer.com/private-equity-firm-acquires-pert-plus-brand-pg"), _LBG, _PETAB])
_new("pyunkang-yul", "Pyunkang Yul", "unverified", "I couldn't find an animal testing policy or certification for Pyunkang Yul. It isn't a vegan brand, though it has a range marked vegan with no certifier named. Made by a Korean company founded in 2015 by the Pyunkang Oriental Medicine clinic.",
     vegan="partial", vc="low", category=["skincare"], region="Asia",
     sources=[_src("Pyunkang Yul: its website", "https://pyunkangyul.com/"), _LBG, _PETAB])
_new("round-lab", "Round Lab", "unverified", "I couldn't find an animal testing policy or certification for Round Lab. It isn't a fully vegan brand, and its site shows a vegan label with no certifier named. Its operating company, Seorin Company, was reported to have been acquired by Goodai Global in July 2025.",
     parent="Goodai Global", vegan="partial", vc="low", category=["skincare"], region="Asia",
     sources=[_src("TheVC: Seorin Company (Round Lab)", "https://thevc.kr/seorincompany"), _src("Preqin: Round Lab deal profile", "https://www.preqin.com/data/profile/asset/round-lab/719937"), _src("Round Lab: its website", "https://roundlab.com/"), _LBG, _PETAB])
_new("holika-holika", "Holika Holika", "unverified", "I couldn't find an animal testing policy or certification for Holika Holika, and its websites don't mention animal testing. Owned by Enprani Co., Ltd., a private Korean company. I couldn't find a vegan claim.",
     parent="Enprani Co., Ltd.", category=["makeup-beauty", "skincare"], region="Asia",
     sources=[_src("Holika Holika: its website (Enprani Co., Ltd.)", "https://holikaholika.com/"), _LBG, _PETAB])
_new("tiger-balm", "Tiger Balm", "unverified", "Tiger Balm's FAQ says it isn't officially certified cruelty-free and doesn't mention animal testing, and I couldn't find a policy anywhere. It's a pain relief product, so medicine rules may apply. Owned by Haw Par Corporation, a Singapore-listed company. Its US FAQ says most products contain no animal by-products, but the Arthritis Rub contains glucosamine and chondroitin from animal and shellfish sources.",
     parent="Haw Par Corporation", vegan="partial", vc="low", category=["hygiene"],
     sources=[_src("Tiger Balm: its FAQs", "https://tigerbalm.com/us/tiger-balm-faqs"), _src("Haw Par Corporation: healthcare (owner of Tiger Balm)", "https://www.hawpar.com/our-businesses/healthcare"), _LBG, _PETAB])
_new("bio-oil", "Bio-Oil", "unverified", "I couldn't find an animal testing policy or certification for Bio-Oil, and its FAQ pages say nothing about animal testing. It isn't certified by Leaping Bunny / Cruelty Free International or PETA. I couldn't find a vegan claim. Made by Union Swiss, based in Cape Town, South Africa.",
     category=["skincare"], region="Europe",
     sources=[_src("Bio-Oil: its FAQ", "https://www.bio-oil.com/en-us/faq"), _LBG, _PETAB])
_new("icy-hot", "Icy Hot", "unverified", "I couldn't find an animal testing policy or certification for Icy Hot. It's a pain relief product, so medicine rules may apply. Owned by Opella, which Sanofi sold a controlling stake in to CD&R (completed 30 April 2025). I couldn't find a vegan claim.",
     parent="Opella", category=["hygiene"], region=_CC,
     sources=[_src("Wikipedia: Opella", "https://en.wikipedia.org/wiki/Opella"), _src("DCAT: Sanofi completes sale of controlling stake in Opella", "https://www.dcatvci.org/top-industry-news/sanofi-completes-11-4-bn-sales-of-controlling-stake-in-consumer-healthcare-biz-opella/"), _LBG, _PETAB])
_new("olive-and-june", "Olive & June", "unverified", "I couldn't find an animal testing policy, cruelty-free claim or vegan claim for Olive & June, and it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Owned by Helen of Troy, which completed its acquisition on 17 December 2024.",
     parent="Helen of Troy", category=["makeup-beauty"], region=_CC,
     sources=[_src("SGB Online: Helen of Troy completes acquisition of Olive & June (17 December 2024)", "https://sgbonline.com/helen-of-troy-completes-acquisition-of-olive-june/"), _LBG, _PETAB])
for _s in ("aquaphor", "laneige", "sheamoisture", "dawn", "biofreeze", "secret-deodorant", "innisfree", "one-with-nature", "makeup-by-mario", "kimchi-chic-beauty", "artnaturals", "skin1004", "raw-sugar", "summer-fridays", "olivella", "dashing-diva", "everspring", "aplb", "palmers", "mario-badescu", "haus-labs", "gisou", "elizavecca", "pert", "pyunkang-yul", "round-lab", "holika-holika", "tiger-balm", "bio-oil", "icy-hot", "olive-and-june"):
    if _s in by: by[_s]["lastVerified"] = today
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
def _sm3(t):
    if "'Everspring'" in t: return t
    return t.replace("'Pop-arazzi',", "'Pop-arazzi', 'Everspring',", 1)
_rw("scripts/generate-brand-check.js", _sm3)
print("Section 55 applied")

# 56. Haus Labs is Leaping Bunny certified (Ash's link, 15 Oct); Tierra Verde (reader request, Czech eco household brand)
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_hl = by.get("haus-labs")
if _hl:
    _hl.update(tier="good", claim="", vegan="full", veganBasis="brand", veganConfidence="low", lastVerified=today,
        note="Certified cruelty-free by Leaping Bunny. Haus Labs says it's cruelty-free and vegan, and Sephora's brand page says every product is 100% vegan, but it has no vegan certification and PETA doesn't list it. Founded by Lady Gaga and Ben Jones in 2019, formerly called Haus Laboratories. Independently owned, with minority investors including Lightspeed Venture Partners.")
    _hl["sources"] = [s for s in _hl.get("sources", []) if "leapingbunny.org/shopping-guide" not in s.get("url", "")]
    _addsrc(_hl, "Leaping Bunny: Haus Labs brand page", "https://www.leapingbunny.org/brand/haus-labs-lady-gaga")
    _addsrc(_hl, "Lightspeed Venture Partners: Haus Laboratories (investor)", "https://lsvp.com/company/haus-laboratories/")
_new("tierra-verde", "Tierra Verde (Czech)", "unverified", "I couldn't find an animal testing policy or cruelty-free claim for Tierra Verde, and it isn't certified by Leaping Bunny / Cruelty Free International or PETA. It's a Czech-Slovak eco household and cosmetics brand (TIERRA VERDE s.r.o., near Brno), and most of its products carry the Ecogarantie eco certificate, which isn't a cruelty-free or vegan certification. Some individual products are labelled vegan, so vegan varies by product. This isn't the Spanish organic farmers' association also called Tierra Verde.",
     vegan="partial", vc="low", category=["household-cleaning", "laundry", "body-shower"], region="Europe",
     sources=[_src("Alza: Tierra Verde (Ecogarantie certificate, products labelled vegan)", "https://m.alza.cz/tierra-verde/v15232.htm"), _src("Økofamily: Tierra Verde brand page", "https://okofamily.com/shop/?brand=117-tierra-verde"), _src("Tierra Verde: its Czech website (TIERRA VERDE s.r.o.)", "https://www.tierraverde.cz/"), _LBG, _PETAB])
if "tierra-verde" in by: by["tierra-verde"]["lastVerified"] = today
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Section 56 applied")

# 57. Tierra Verde: Bulgarian site shows a "No tests on animals" icon (Ash's screenshot, 15 Oct); the page text itself doesn't repeat it
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_tv = by.get("tierra-verde")
if _tv:
    _tv.update(claim="Tierra Verde's Bulgarian site shows a \"no tests on animals\" icon beside its Ecogarantie certificate.", lastVerified=today,
        note="Tierra Verde says its products aren't tested on animals (its Bulgarian site shows a \"no tests on animals\" icon), but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. It's a Czech-Slovak eco household and cosmetics brand (TIERRA VERDE s.r.o., near Brno), and most of its products carry the Ecogarantie eco certificate, which isn't a cruelty-free or vegan certification. Some individual products are labelled vegan, so vegan varies by product. This isn't the Spanish organic farmers' association also called Tierra Verde.")
    _addsrc(_tv, "Tierra Verde Bulgaria: about us (\"no tests on animals\" icon)", "https://tierraverde.bg/en/pages/za-nas")
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Section 57 applied")

# 58. The nine held brands, with Ash's findings (15 Oct). China Glaze: her PETA link (company/glaze) is Glaze, the hair brand, not China Glaze, so only Leaping Bunny is used.
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
_KAO = _src("Kao: its animal testing policy (exception where government agencies in particular countries require it)", "https://www.kao.com/global/en/innovation/safety-quality/animal-testing-policy/")
_b = _new("biore", "Bioré", "unverified", "Bioré says it doesn't test its products or the materials within them on animals, and that all its products in western markets are cruelty-free and vegan friendly, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA. Its page notes that laws sometimes require testing of materials outside the cosmetics category. Owned by Kao Corporation, whose policy allows animal testing where government agencies in particular countries require it.",
     parent="Kao Corporation", vegan="full", vc="low", claim="Bioré says it doesn't test its products or the materials within them on animals, and that its products in western markets are cruelty-free and vegan friendly.", category=["skincare"], region="Europe",
     sources=[_src("Bioré UK: transparency (animal testing and vegan statement)", "https://www.biore.com/en-gb/transparency/"), _KAO, _LBG, _PETAB]); _vb("biore")
if _b: _b["parentTestsOnAnimals"] = True
_new("mary-and-may", "Mary&May", "unverified", "Mary&May says some of its products are vegan and cruelty-free on their labels, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA, and I couldn't find an animal testing policy page for it. Owned by AIDKOREA COMPANY INC (also registered as Aid Korea Co., Ltd.), which also has no animal testing policy that I could find. Vegan varies by product.",
     parent="AIDKOREA COMPANY INC", vegan="partial", vc="low", claim="Mary&May says some of its products are vegan and cruelty-free on their labels.", category=["skincare"], region="Asia",
     sources=[_src("SweetCare: Mary&May", "https://www.sweetcare.com/gb/b/maryandmay"), _LBG, _PETAB])
_pt = _new("patrick-ta-beauty", "Patrick Ta Beauty", "unverified", "Patrick Ta Beauty lists its products as cruelty-free, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA, and its help centre doesn't say it doesn't test on animals. Not every product is vegan. Founded in 2019 by the makeup artist Patrick Ta, with a minority growth investment from Stride Consumer Partners in October 2022. This isn't ONE/SIZE by Patrick Starrr.",
     vegan="partial", vc="low", claim="Patrick Ta Beauty lists \"Cruelty Free\" on its product pages.", category=["makeup-beauty"],
     sources=[_src("Patrick Ta Beauty: its help centre", "https://patrickta.com/pages/help-center"), _src("Patrick Ta Beauty: blush collection (\"Cruelty Free\" tag on product pages)", "https://patrickta.com/collections/blush"), _src("Cosmetics Business: Patrick Ta Beauty receives investment from Stride Consumer Partners", "https://cosmeticsbusiness.com/patrick-ta-beauty-receives-investment-from-stride-consumer-partners-backers-of-first-aid-beauty-and-skinfix-204494"), _LBG, _PETAB])
_new("fenty-beauty", "Fenty Beauty", "unverified", "Fenty Beauty says it never tests on animals in any region, and that it doesn't allow suppliers or retailers to test for it, but it isn't certified by Leaping Bunny / Cruelty Free International, and PETA lists it as a company that may not be cruelty-free because it hasn't signed PETA's statement. Fenty Beauty isn't a vegan line (some products contain beeswax and carmine), but Fenty Skin and Fenty Hair say they're fully vegan. A joint venture between LVMH and Rihanna, 50/50. In October 2026 it was reported that LVMH's stake is being sold, but I found no signed deal.",
     parent="LVMH / Rihanna (50/50)", vegan="partial", vc="medium", claim="Fenty Beauty says it never tests products or ingredients on animals, in any region, and doesn't allow suppliers or retailers to test for it.", category=["makeup-beauty", "skincare", "haircare"], region=_CC,
     sources=[_src("Fenty Beauty: help and FAQs (animal testing and vegan statements)", "https://fentybeauty.com/en-gg/pages/help-faqs"), _src("PETA: Fenty Beauty company page", "https://crueltyfree.peta.org/company/fenty-beauty/"), _src("theGrio: Jay-Z's MarcyPen and LVMH's stake in Fenty Beauty (6 October 2026)", "https://thegrio.com/2026/10/06/jay-z-marcypen-fenty-beauty-lvmh-stake/"), _LBG])
_new("china-glaze", "China Glaze", "check", "Certified cruelty-free by Leaping Bunny. Not fully vegan, but it has vegan products, so vegan varies by product. This isn't the hair brand Glaze.",
     vegan="partial", vc="medium", category=["makeup-beauty"], region=_CC,
     sources=[_src("Leaping Bunny: China Glaze brand page", "https://www.leapingbunny.org/brand/china-glaze")])
_new("glamnetic", "Glamnetic", "check", "Certified cruelty-free by Leaping Bunny. Not fully vegan, but it has vegan products, so vegan varies by product. Independently owned: 100% owned by its CEO, Ann McFerran, and co-founder Kevin Gould.",
     vegan="partial", vc="medium", category=["makeup-beauty"], region=_CC,
     sources=[_src("Leaping Bunny: Glamnetic brand page", "https://www.leapingbunny.org/brand/glamnetic"), _src("Glamnetic: about us", "https://www.glamnetic.com/es/pages/about-us")])
_new("california-naturals", "California Naturals", "check", "Certified cruelty-free by Leaping Bunny. Vegan varies by product: not every product is vegan, so check its ingredient glossary. This is the hair and body care brand founded by Shelby Wild, not California Baby or California Pure Naturals. Venture-backed: a Series B led by Align Ventures was announced in June 2026.",
     vegan="partial", vc="medium", category=["haircare", "body-shower"], region=_CC,
     sources=[_src("Leaping Bunny: California Naturals brand page", "https://www.leapingbunny.org/brand/california-naturals"), _src("California Naturals: its ingredient glossary", "https://thecalifornianaturals.com/pages/ingredients"), _src("Beauty Independent: California Naturals Series B", "https://www.beautyindependent.com/?p=190686")])
_new("jason", "JĀSÖN", "unverified", "JĀSÖN says it's cruelty-free, that it doesn't test its products or ingredients on animals or ask others to, and that its products use vegetarian ingredients, but it isn't currently Leaping Bunny certified. It used to be, but isn't any more, even though its FAQ still mentions the Leaping Bunny logo on its labels. It isn't listed by PETA. Vegan varies by product, as it describes its ingredients as vegetarian. Owned by Hain Celestial, which has said it's looking to sell its personal care business.",
     parent="Hain Celestial Group", vegan="partial", vc="low", claim="JĀSÖN says it doesn't test its products or ingredients on animals, nor ask others to, and that its products use vegetarian ingredients and are cruelty-free.", category=["body-shower", "haircare", "skincare"], region=_CC,
     sources=[_src("JĀSÖN: FAQ and contact us", "https://www.jason-personalcare.com/faq-contact-us/"), _src("Hain Celestial: acquires JASON Natural Products (2004)", "https://ir.hain.com/news-releases/news-release-details/hain-celestial-acquires-jason-natural-products-inc"), _LBG, _PETAB])
_new("isntree", "Isntree", "unverified", "Isntree says no products or ingredients are tested on animals, and that it doesn't use animal-derived materials in its formulations, but it isn't certified by Leaping Bunny / Cruelty Free International or PETA, and no vegan certification is named. It's a Korean skincare brand.",
     vegan="full", vc="low", claim="Isntree says no products or ingredients are tested on animals, and that it doesn't use animal-derived materials in its formulations.", category=["skincare"], region="Asia",
     sources=[_src("Isntree: its website (animal testing statement)", "https://www.isntreebeauty.com/"), _LBG, _PETAB]); _vb("isntree")
for _s in ("biore", "mary-and-may", "patrick-ta-beauty", "fenty-beauty", "china-glaze", "glamnetic", "california-naturals", "jason", "isntree"):
    if _s in by: by[_s]["lastVerified"] = today
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
print("Section 58 applied")


# 59. PETA lists import (15 Oct): ~6,000 brands from PETA's "don't test", "vegan" and "do test" lists that weren't on the site.
#     Kept OUT of data/brands.json (so the checker and every page stay fast). They live in data/peta-import.json,
#     get their own brand pages and sitemap entries, and are found by the checker search through a small lazy-loaded index.
#     Also: homepage counts from data/stats.json, and the "Companies that test on animals (2026 list)" page.
import gzip, base64, html as _html
_PB = "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"
_imp = json.loads(gzip.decompress(base64.b64decode(_PB)).decode("utf-8"))
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw; by = {b["slug"]: b for b in brands}
def _nm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower().replace("&", "and")
    s = re.sub(r"\(.*?\)", "", s); s = re.sub(r"^the ", "", s.strip()); return re.sub(r"[^a-z0-9]", "", s)
_have = {_nm(b["name"]) for b in brands}
_PDATE = "2026-10-15"
_full = []
for o in _imp:
    if o["s"] in by or _nm(o["n"]) in _have: continue
    src = [{"label": "PETA: %s company page" % o["f"], "url": o["u"]}]
    b = {"slug": o["s"], "name": o["n"], "parentCompany": o.get("p"), "evidence": "", "products": [], "alternatives": [], "links": [], "category": [], "region": "",
         "claim": "", "lastVerified": _PDATE, "sources": src, "vegan": "unknown", "veganConfidence": "low", "fromPeta": True}
    if o["k"] == "do":
        b["tier"] = "bad"; b["note"] = "Listed by PETA as a company that tests on animals." + (" Owned by %s." % o["p"] if o.get("p") else "")
        if o.get("p"): b["parentTestsOnAnimals"] = True
    else:
        if o.get("v"): b.update(vegan="full", veganBasis="certified", veganCert="PETA", veganConfidence="medium")
        if o.get("pt"):
            b["tier"] = "warn"; b["parentTestsOnAnimals"] = True
            b["note"] = "Listed by PETA as cruelty-free%s, but owned by %s, which PETA lists as a company that tests on animals." % (" and vegan" if o.get("v") else "", o["p"])
        else:
            b["tier"] = "good" if o.get("v") else "check"
            b["note"] = ("Listed by PETA as cruelty-free and vegan." if o.get("v") else "Listed by PETA as cruelty-free. I haven't confirmed whether its products are vegan yet, so check each product.") + (" Owned by %s." % o["p"] if o.get("p") else "")
    if o.get("pl"): b["note"] += " PETA lists it under %s." % o["pl"]
    b["note"] += " Added from PETA's list in October 2026: I haven't researched it beyond that listing yet."
    _full.append(b)
json.dump(_full, open("data/peta-import.json", "w"), ensure_ascii=False, separators=(",", ":")); open("data/peta-import.json", "a").write("\n")
json.dump([[b["name"], b["slug"], b["tier"]] for b in _full], open("data/search-extra.json", "w"), ensure_ascii=False, separators=(",", ":"))
_t = {"good": 0, "check": 0, "warn": 0, "bad": 0, "unverified": 0}
for b in brands + _full:
    if b.get("tier") in _t: _t[b["tier"]] += 1
_st = dict(_t); _st["total"] = len(brands) + len(_full); _st["cf"] = _t["good"] + _t["check"]
json.dump(_st, open("data/stats.json", "w")); print("PETA import:", len(_full), "brands; total", _st["total"])
# brand pages + sitemap
def _gp(t):
    if "peta-import.json" in t: return t
    old = "  fs.writeFileSync(path.join(ROOT, 'sitemap.xml'), buildSitemap(brands), 'utf8');"
    new = ("  let extra = [];\n  try { extra = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'peta-import.json'), 'utf8')); } catch (e) { extra = []; }\n"
           "  const extraMade = [];\n  extra.forEach(function(b) {\n    if (!b.slug || slugs[b.slug]) return;\n    slugs[b.slug] = true;\n"
           "    const dir = path.join(OUT_DIR, b.slug);\n    fs.mkdirSync(dir, { recursive: true });\n    fs.writeFileSync(path.join(dir, 'index.html'), renderBrandPage(b), 'utf8');\n    extraMade.push(b);\n  });\n"
           "  console.log('PETA list pages: ' + extraMade.length);\n  fs.writeFileSync(path.join(ROOT, 'sitemap.xml'), buildSitemap(brands.concat(extraMade)), 'utf8');")
    t = t.replace(old, new, 1)
    t = t.replace("'take-action.html', 'perfume.html'];", "'take-action.html', 'perfume.html', 'companies-that-test-on-animals'];", 1)
    t = t.replace("  if (brand.tier === 'bad') return 'Yes, or it sells where animal testing is required. ' + (p ? n + ' is owned by ' + p + '. ' : '') + 'The sources are below.';",
                  "  if (brand.tier === 'bad') return 'Yes, or it sells where animal testing is required. ' + (p ? n + ' is owned by ' + p + '. ' : '') + 'The sources are below. <a href=\"/companies-that-test-on-animals\">See every company that tests on animals</a>.';", 1)
    return t
_rw("scripts/generate-brand-pages.js", _gp)
# homepage numbers
def _cnt(t):
    if "data/stats.json" in t: return t
    t = t.replace("fetch('data/brands.json').then(function(r){ return r.json(); }).then(function(list){\nvar count = Array.isArray(list) ? list.length : null;",
                  "fetch('data/stats.json').then(function(r){ return r.json(); }).then(function(st){\nvar count = st && st.total ? st.total : null;", 1)
    return t
_rw("js/nav.js", _cnt); _rw("js/site.js", _cnt)
def _idx(t):
    if "data/stats.json" in t: return t
    return re.sub(r"fetch\('data/brands\.json'\)\.then\(function\(r\)\{return r\.json\(\);\}\)\.then\(function\(d\)\{\n  var t=\{good:0,check:0,warn:0,bad:0,unverified:0\};\n  d\.forEach\(function\(b\)\{ if\(t\[b\.tier\]!==undefined\) t\[b\.tier\]\+\+; \}\);\n  var n=\{[^\n]*\};",
                  "fetch('data/stats.json').then(function(r){return r.json();}).then(function(n){", t, count=1)
_rw("index.html", _idx)
# checker search: more brands from PETA's list, loaded only when someone searches
_MORE = r"""<!--ahk-more--><style>#ahkMore{margin:14px 0 6px}#ahkMore h3{font-size:15px;margin:10px 0 8px}#ahkMore a.mr{display:flex;justify-content:space-between;gap:10px;align-items:center;padding:10px 12px;margin:0 0 8px;border:1.5px solid #E5CFC4;border-radius:12px;background:#FBF4EF;color:#2A1630;text-decoration:none}#ahkMore a.mr:focus-visible,#ahkMore a.mr:hover{border-color:#E8804C}#ahkMore .t{font-size:12px;color:#6A535D;text-align:right}#ahkMore .t.bad{color:#9C3A3A}#ahkMore p{font-size:13px;color:#6A535D}</style>
<script>(function(){var inp=document.getElementById('ratingSearch'),nr=document.getElementById('noResults');if(!inp||!nr)return;var box=document.createElement('div');box.id='ahkMore';var ab=document.getElementById('allBrands')||nr;ab.parentNode.insertBefore(box,ab.nextSibling);var data=null,p=null;
var L={good:'cruelty-free and vegan (PETA)',check:'cruelty-free (PETA)',warn:'cruelty-free, but its owner tests',bad:'tests on animals'};
function nz(s){s=(s||'').toLowerCase();try{s=s.normalize('NFKD').replace(/[̀-ͯ]/g,'')}catch(e){}return s.replace(/&/g,'and').replace(/[^a-z0-9]/g,'')}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function load(){if(!p)p=fetch('/data/search-extra.json').then(function(r){return r.json()}).then(function(d){data=d.map(function(x){return [x[0],x[1],x[2],nz(x[0])]});return data}).catch(function(){data=[];return data});return p}
function run(){var q=nz(inp.value);if(q.length<2){box.innerHTML='';return}load().then(function(){if(nz(inp.value)!==q)return;var a=[],b=[];for(var i=0;i<data.length;i++){var k=data[i][3];if(k.indexOf(q)===0)a.push(data[i]);else if(k.indexOf(q)!==-1)b.push(data[i])}var m=a.concat(b);if(!m.length){box.innerHTML='';return}
var h='<h3>More brands from PETA\'s list</h3>';m.slice(0,25).forEach(function(x){h+='<a class="mr" href="/brands/'+x[1]+'/"><span>'+esc(x[0])+'</span><span class="t '+x[2]+'">'+(L[x[2]]||'')+'</span></a>'});if(m.length>25)h+='<p>'+(m.length-25)+' more. Keep typing to narrow it down.</p>';box.innerHTML=h;nr.style.display='none'})}
inp.addEventListener('input',run);if(inp.value)setTimeout(run,400);})();</script>
"""
def _bc(t):
    if "<!--ahk-more-->" in t: return t
    return t.replace("</body>", _MORE + "</body>", 1)
_rw("brand-check.html", _bc)
# "Companies that test on animals (2026 list)" page
def _testpage():
    E = _html.escape
    allb = brands + _full
    bad = sorted([b for b in allb if b.get("tier") == "bad"], key=lambda b: _nm(b["name"]) or b["name"].lower())
    warn = sorted([b for b in allb if b.get("tier") == "warn"], key=lambda b: _nm(b["name"]) or b["name"].lower())
    mon = datetime.date.today().strftime("%B %Y")
    def first(s):
        s = (s or "").strip(); m = re.match(r"(.+?[.!?])(\s|$)", s); s = m.group(1) if m else s
        return s if len(s) <= 220 else s[:217].rsplit(" ", 1)[0] + "..."
    def row(b):
        own = b.get("parentCompany")
        src = (b.get("sources") or [{}])[0]
        srcl = (' <a href="%s" target="_blank" rel="noopener">source</a>' % E(src["url"])) if src.get("url") else ""
        return ('<li><a href="/brands/%s/"><strong>%s</strong></a>%s<br><span class="ct-n">%s%s</span></li>'
                % (b["slug"], E(b["name"]), (' <span class="ct-o">owned by %s</span>' % E(own)) if own else "", E(first(b.get("note"))), srcl))
    groups = {}
    for b in bad:
        L1 = (_nm(b["name"])[:1] or "#").upper(); L1 = L1 if L1.isalpha() else "#"
        groups.setdefault(L1, []).append(b)
    letters = sorted(groups, key=lambda x: (x != "#", x))
    jump = " ".join('<a href="#l-%s">%s</a>' % (x if x != "#" else "num", x) for x in letters)
    body = ("<p><strong>Updated %s.</strong> These %d brands and companies test on animals, or sell where animal testing is required by law. Each one links to its own page, where the source is listed, so you can check it yourself.</p>"
            "<p>A brand goes on this list when it, or the company that owns it, tests on animals, pays for tests, or sells in a country where tests are required. I use Leaping Bunny / Cruelty Free International, PETA and the companies' own animal testing policies. <a href=\"/how-i-decide\">How I decide</a>.</p>"
            "<p>Looking for something kinder? <a href=\"/brand-check\">Search the brand checker</a>.</p>") % (mon, len(bad))
    body += '<p class="ct-jump">%s</p>' % jump
    for x in letters:
        body += '<h2 id="l-%s">%s</h2><ul class="ct-list">%s</ul>' % (x if x != "#" else "num", x, "".join(row(b) for b in groups[x]))
    body += ("<h2 id=\"owned\">Cruelty-free brands owned by companies that test</h2><p>These %d brands are cruelty-free themselves, but the company that owns them tests on animals. Some people still buy them, and some don't, because the money goes to the parent company.</p><ul class=\"ct-list\">%s</ul>"
             % (len(warn), "".join(row(b) for b in warn)))
    faq = [("Which big companies test on animals?", "Companies such as Procter & Gamble, Unilever, L'Oréal, Estée Lauder, Johnson & Johnson, Colgate-Palmolive, Reckitt and Church & Dwight test on animals or sell where testing is required by law. Some of their individual brands are certified cruelty-free; those are listed separately below the main list."),
           ("Is a brand cruelty-free if it says it doesn't test on animals?", "Not always. Many brands say they don't test unless required by law, which means they still sell where animal tests are required. Look for Leaping Bunny / Cruelty Free International or PETA certification."),
           ("How often is this list updated?", "Every time a brand on a home kind changes. The date at the top shows the last update.")]
    body += "<h2>Questions</h2>" + "".join("<h3>%s</h3><p>%s</p>" % (E(q), E(a)) for q, a in faq)
    css = "<style>.ct-list{list-style:none;padding:0!important}.ct-list li{padding:10px 0!important;border-bottom:1px solid #E5CFC4}.ct-n{font-size:13.5px;color:#6A535D}.ct-o{font-size:13px;color:#9C3A3A}.ct-jump a{display:inline-block;padding:4px 8px;margin:2px;border:1px solid #E5CFC4;border-radius:8px;text-decoration:none}</style>"
    tpl = open("privacy.html", encoding="utf-8").read()
    title = "Companies That Test on Animals (%s List) - a home kind" % datetime.date.today().year
    desc = "The %s list of %d brands and companies that test on animals, with sources. Updated %s." % (datetime.date.today().year, len(bad), mon)
    h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % E(title), tpl, count=1, flags=re.S)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + E(desc) + m.group(2), h, count=1)
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "ItemList", "name": "Companies that test on animals", "numberOfItems": len(bad),
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": b["name"], "url": "https://ahomekind.com/brands/%s" % b["slug"]} for i, b in enumerate(bad)]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]}
    head = ('<link rel="canonical" href="https://ahomekind.com/companies-that-test-on-animals">'
            '<meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="https://ahomekind.com/companies-that-test-on-animals">'
            '<script type="application/ld+json">%s</script>%s') % (E(title), E(desc), json.dumps(ld, ensure_ascii=False).replace("</", "<\\/"), css)
    h = h.replace("</head>", head + "</head>", 1)
    h = re.sub(r'(<div class="k-ph">).*?(</div>)', lambda m: '%s<p class="k-kick">the %d list</p><h1 class="k-h1" style="margin-bottom:22px">Companies that test on animals</h1>%s' % (m.group(1), datetime.date.today().year, m.group(2)), h, count=1, flags=re.S)
    h = re.sub(r"(<div class=\"k-ph\">.*?</div>).*?(</main>)", lambda m: m.group(1) + '<div class="ahk-info" style="max-width:720px;margin:28px auto 40px;line-height:1.7;padding:0 4px">' + body + "</div>" + m.group(2), h, count=1, flags=re.S)
    open("companies-that-test-on-animals.html", "w", encoding="utf-8").write(h)
    print("Companies that test page:", len(bad), "brands,", len(warn), "owned by testers")
_testpage()
print("Section 59 applied")

# 60. Only the most popular PETA-list brands for now (Ash, 15 Oct): rank the ~6,000 by Wikipedia page views (last 30 days),
#     keep the top 300 that are clearly a brand/company, plus every "tests on animals" / "owner tests" one. The rest wait.
#     Needs internet once; results are cached in data/popularity.json so later runs are instant.
import shutil, time
_KEEP = 300
_all = json.load(open("data/peta-import.json"))
_cp = "data/popularity.json"
_cache = json.load(open(_cp)) if os.path.exists(_cp) else {}
_todo = [b["name"] for b in _all if b["name"] not in _cache]
_UA2 = {"User-Agent": "ahomekind-popularity/1.0 (https://ahomekind.com; hello@ahomekind.com)"}
def _wq(titles):
    out = {}; red = {}; cont = {}
    for _ in range(20):
        p = {"action": "query", "titles": "|".join(titles), "redirects": 1, "prop": "pageviews|pageprops|description", "pvipdays": 30, "format": "json", "formatversion": 2}
        p.update(cont)
        u = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(p)
        with urllib.request.urlopen(urllib.request.Request(u, headers=_UA2), timeout=30) as r: d = json.load(r)
        q = d.get("query", {})
        for x in q.get("normalized", []) + q.get("redirects", []): red[x["from"]] = x["to"]
        for pg in q.get("pages", []):
            o = out.setdefault(pg["title"], {"v": 0})
            if pg.get("missing"): o["m"] = 1
            if "disambiguation" in (pg.get("pageprops") or {}): o["dis"] = 1
            if pg.get("description"): o["d"] = pg["description"]
            for v in (pg.get("pageviews") or {}).values():
                if v: o["v"] += v
        if "continue" not in d: break
        cont = {k: v for k, v in d["continue"].items()}
    return out, red
if _todo:
    print("Checking popularity for", len(_todo), "brands on Wikipedia (only needed once, about 2 minutes)...")
    try:
        for i in range(0, len(_todo), 50):
            chunk = _todo[i:i + 50]
            pages, red = _wq(chunk)
            for n in chunk:
                t = n
                for _ in range(3):
                    if t in red: t = red[t]
                pg = pages.get(t)
                _cache[n] = {"t": t, "v": pg.get("v", 0), "d": pg.get("d", ""), "dis": pg.get("dis", 0), "m": pg.get("m", 0)} if pg else {"m": 1, "v": 0}
            if i % 1000 == 0: print("  ", i + len(chunk), "checked")
            time.sleep(0.3)
    except Exception as e:
        print("Popularity check stopped early (", e, "). Run the command again later to finish it.")
    json.dump(_cache, open(_cp, "w"), ensure_ascii=False, indent=0)
_BRANDY = re.compile(r"brand|company|cosmetic|beauty|skin|hair|makeup|make-up|perfume|fragrance|soap|personal care|toiletr|deodorant|toothpaste|shampoo|nail|lip|cleaning|detergent|household|manufacturer|retailer|products|grooming|razor|sunscreen|pet food|haircare|skincare", re.I)
def _score(b):
    c = _cache.get(b["name"]) or {}
    if c.get("m") or c.get("dis") or not _BRANDY.search(c.get("d", "")): return 0
    return c.get("v", 0)
_must = [b for b in _all if b["tier"] in ("bad", "warn")]
_ranked = sorted([b for b in _all if b["tier"] not in ("bad", "warn") and _score(b) > 0], key=_score, reverse=True)[:_KEEP]
_sel = _must + _ranked
_selslugs = {b["slug"] for b in _sel}
_mainslugs = {b["slug"] for b in brands}
_gone = 0
for b in _all:
    if b["slug"] not in _selslugs and b["slug"] not in _mainslugs and os.path.isdir(os.path.join("brands", b["slug"])):
        shutil.rmtree(os.path.join("brands", b["slug"])); _gone += 1
json.dump(_sel, open("data/peta-import.json", "w"), ensure_ascii=False, separators=(",", ":")); open("data/peta-import.json", "a").write("\n")
json.dump([[b["name"], b["slug"], b["tier"]] for b in _sel], open("data/search-extra.json", "w"), ensure_ascii=False, separators=(",", ":"))
_t = {"good": 0, "check": 0, "warn": 0, "bad": 0, "unverified": 0}
for b in brands + _sel:
    if b.get("tier") in _t: _t[b["tier"]] += 1
_st = dict(_t); _st["total"] = len(brands) + len(_sel); _st["cf"] = _t["good"] + _t["check"]
json.dump(_st, open("data/stats.json", "w"))
open("data/popular-picks.txt", "w", encoding="utf-8").write("\n".join("%s\t%s\t%s" % (b["name"], _score(b), (_cache.get(b["name"]) or {}).get("d", "")) for b in _ranked) + "\n")
print("Popular PETA brands kept:", len(_ranked), "+", len(_must), "that test or whose owner tests; pages removed:", _gone, "; total brands", _st["total"])
print("Section 60 applied")

# 61. Hybrid (Ash, 15 Oct): ALL PETA-list brands are searchable in the checker (linking to PETA's own listing),
#     but only researched brands get a full page. For now that's just the 25 "tests" / "owner tests" ones; the rest get
#     pages batch by batch as they're researched, most popular first (data/popular-picks.txt = top 1,000 by Wikipedia views).
_pages = _must
_pslugs = {b["slug"] for b in _pages}
for b in _all:
    if b["slug"] not in _pslugs and b["slug"] not in _mainslugs and os.path.isdir(os.path.join("brands", b["slug"])):
        shutil.rmtree(os.path.join("brands", b["slug"]))
json.dump(_pages, open("data/peta-import.json", "w"), ensure_ascii=False, separators=(",", ":")); open("data/peta-import.json", "a").write("\n")
def _pslug(b):
    u = (b.get("sources") or [{}])[0].get("url", "")
    return u.replace("https://crueltyfree.peta.org/company/", "").strip("/")
json.dump(sorted([[b["name"], b["slug"] if b["slug"] in _pslugs else "", b["tier"], _pslug(b), int(_score(b))] for b in _all], key=lambda r: -r[4]), open("data/search-extra.json", "w"), ensure_ascii=False, separators=(",", ":"))
_t = {"good": 0, "check": 0, "warn": 0, "bad": 0, "unverified": 0}
for b in brands + _pages:
    if b.get("tier") in _t: _t[b["tier"]] += 1
_st = dict(_t); _st["total"] = len(brands) + len(_pages); _st["cf"] = _t["good"] + _t["check"]
json.dump(_st, open("data/stats.json", "w"))
_top = sorted([b for b in _all if b["tier"] not in ("bad", "warn") and _score(b) > 0], key=_score, reverse=True)[:1000]
open("data/popular-picks.txt", "w", encoding="utf-8").write("".join("%d\t%s\t%s\t%s\t%s\n" % (i + 1, b["name"], _score(b), (_cache.get(b["name"]) or {}).get("d", ""), (b.get("sources") or [{}])[0].get("url", "")) for i, b in enumerate(_top)))
_MORE2 = r"""<!--ahk-more--><!--v2--><style>#ahkMore{margin:14px 0 6px}#ahkMore h3{font-size:15px;margin:10px 0 8px}#ahkMore a.mr{display:flex;justify-content:space-between;gap:10px;align-items:center;padding:10px 12px;margin:0 0 8px;border:1.5px solid #E5CFC4;border-radius:12px;background:#FBF4EF;color:#2A1630;text-decoration:none}#ahkMore a.mr:focus-visible,#ahkMore a.mr:hover{border-color:#E8804C}#ahkMore .t{font-size:12px;color:#6A535D;text-align:right}#ahkMore .t.bad{color:#9C3A3A}#ahkMore p{font-size:13px;color:#6A535D}</style>
<script>(function(){var inp=document.getElementById('ratingSearch'),nr=document.getElementById('noResults');if(!inp||!nr)return;var box=document.createElement('div');box.id='ahkMore';var ab=document.getElementById('allBrands')||nr;ab.parentNode.insertBefore(box,ab.nextSibling);var data=null,p=null;
var L={good:'cruelty-free and vegan',check:'cruelty-free',warn:'cruelty-free, but its owner tests',bad:'tests on animals'};
function nz(s){s=(s||'').toLowerCase();try{s=s.normalize('NFKD').replace(/[̀-ͯ]/g,'')}catch(e){}return s.replace(/&/g,'and').replace(/[^a-z0-9]/g,'')}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function load(){if(!p)p=fetch('/data/search-extra.json').then(function(r){return r.json()}).then(function(d){data=d.map(function(x){return [x[0],x[1],x[2],x[3],nz(x[0])]});return data}).catch(function(){data=[];return data});return p}
function run(){var q=nz(inp.value);if(q.length<2){box.innerHTML='';return}load().then(function(){if(nz(inp.value)!==q)return;var a=[],b=[];for(var i=0;i<data.length;i++){var k=data[i][4];if(k.indexOf(q)===0)a.push(data[i]);else if(k.indexOf(q)!==-1)b.push(data[i])}var m=a.concat(b);if(!m.length){box.innerHTML='';return}
var h='<h3>More brands from PETA\'s list</h3>';m.slice(0,25).forEach(function(x){var href=x[1]?'/brands/'+x[1]+'/':'https://crueltyfree.peta.org/company/'+x[3]+'/';var ext=x[1]?'':' target="_blank" rel="noopener"';h+='<a class="mr" href="'+href+'"'+ext+'><span>'+esc(x[0])+'</span><span class="t '+x[2]+'">'+(L[x[2]]||'')+(x[1]?'':' &middot; PETA')+'</span></a>'});if(m.length>25)h+='<p>'+(m.length-25)+' more. Keep typing to narrow it down.</p>';h+='<p>These come from PETA\'s list. The ones marked PETA open PETA\'s own page, as I haven\'t researched them myself yet.</p>';box.innerHTML=h;nr.style.display='none'})}
inp.addEventListener('input',run);if(inp.value)setTimeout(run,400);})();</script>
"""
def _bc2(t):
    if "<!--v2-->" in t: return t
    t = re.sub(r"<!--ahk-more-->.*?</script>\n", "", t, count=1, flags=re.S)
    return t.replace("</body>", _MORE2 + "</body>", 1)
_rw("brand-check.html", _bc2)
print("Section 61 applied: %d PETA-list brands searchable, %d with full pages; research list in data/popular-picks.txt" % (len(_all), len(_pages)))

# 62. Brand checker: suggestions as you type (Ash, 15 Oct). Type "b" and brands starting with B appear in a list under the box;
#     tap one to open it. Uses the checker's own cards plus the PETA-list index (loaded the first time the box is tapped).
_SUG = r"""<!--ahk-suggest--><style>.ahk-sg{position:absolute;left:0;right:0;top:calc(100% + 6px);z-index:60;background:#FFFDFB;border:1.5px solid #E5CFC4;border-radius:14px;box-shadow:0 10px 28px rgba(42,22,48,.14);overflow:hidden;max-height:60vh;overflow-y:auto}
.ahk-sg[hidden]{display:none}.ahk-sg a{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:11px 14px;color:#2A1630;text-decoration:none;border-bottom:1px solid #F1E3DB;font-size:15px}
.ahk-sg a:last-child{border-bottom:0}.ahk-sg a.on,.ahk-sg a:hover{background:#FBEDE4}.ahk-sg b{font-weight:700}.ahk-sg .t{font-size:12px;color:#6A535D;white-space:nowrap}.ahk-sg .t.bad{color:#9C3A3A}</style>
<script>(function(){var inp=document.getElementById('ratingSearch');if(!inp)return;var wrap=inp.closest('.k-field')||inp.parentNode;if(getComputedStyle(wrap).position==='static')wrap.style.position='relative';
var box=document.createElement('div');box.className='ahk-sg';box.id='ahkSg';box.setAttribute('role','listbox');box.hidden=true;wrap.appendChild(box);
inp.setAttribute('role','combobox');inp.setAttribute('aria-autocomplete','list');inp.setAttribute('aria-controls','ahkSg');inp.setAttribute('aria-expanded','false');
var L={good:'cruelty-free & vegan',check:'cruelty-free',warn:'owner tests',bad:'tests on animals',unverified:'not certified'};
function nz(s){s=(s||'').toLowerCase();try{s=s.normalize('NFKD').replace(/[̀-ͯ]/g,'')}catch(e){}return s.replace(/&/g,'and').replace(/[^a-z0-9 ]/g,'').replace(/\s+/g,' ').trim()}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var list=[],seen={},built=false;function own(){if(built)return;built=true;document.querySelectorAll('#allBrands .card').forEach(function(c){var nm=c.querySelector('.rcard-name')||c.querySelector('h3 a'),ln=c.querySelector('a.rr')||c.querySelector('h3 a');if(!nm||!ln)return;var t='';['good','check','warn','bad','unverified'].forEach(function(k){if(c.classList.contains(k)||c.classList.contains('v-'+k))t=k});var n=nm.textContent.trim(),k=nz(n);if(!k||seen[k])return;seen[k]=1;list.push({n:n,k:k,h:ln.getAttribute('href'),t:t})})}
var extra=false;function more(){own();if(extra)return;extra=true;fetch('/data/search-extra.json').then(function(r){return r.json()}).then(function(d){d.forEach(function(x){var k=nz(x[0]);if(!k||seen[k])return;seen[k]=1;list.push({n:x[0],k:k,h:x[1]?'/brands/'+x[1]+'/':'https://crueltyfree.peta.org/company/'+x[3]+'/',t:x[2],ext:!x[1],v:x[4]||0})});if(document.activeElement===inp)show()}).catch(function(){})}
var cur=-1,items=[];
function hl(n,q){var i=nz(n).indexOf(q);if(i!==0||!q)return esc(n);var c=0,j=0;while(j<n.length&&c<q.length){if(nz(n.charAt(j))!=='')c+=nz(n.charAt(j)).length;j++}return '<b>'+esc(n.slice(0,j))+'</b>'+esc(n.slice(j))}
function show(){var q=nz(inp.value);if(!q){close();return}var a=[],b=[],c=[];for(var i=0;i<list.length;i++){var k=list[i].k;if(k.indexOf(q)===0)a.push(list[i]);else if((' '+k).indexOf(' '+q)!==-1)b.push(list[i]);else if(q.length>2&&k.replace(/ /g,'').indexOf(q.replace(/ /g,''))!==-1)c.push(list[i])}
function s(x,y){var ex=(x.ext?1:0)-(y.ext?1:0);if(ex)return ex;var dv=(y.v||0)-(x.v||0);if(dv)return dv;return x.k<y.k?-1:x.k>y.k?1:0}a.sort(s);b.sort(s);c.sort(s);items=a.concat(b,c).slice(0,8);cur=-1;
if(!items.length){close();return}box.innerHTML=items.map(function(x,i){return '<a role="option" id="ahkSg'+i+'" href="'+x.h+'"'+(x.ext?' target="_blank" rel="noopener"':'')+'><span>'+hl(x.n,q)+'</span><span class="t '+x.t+'">'+(L[x.t]||'')+(x.ext?' &middot; PETA':'')+'</span></a>'}).join('');box.hidden=false;inp.setAttribute('aria-expanded','true')}
function close(){box.hidden=true;inp.setAttribute('aria-expanded','false');inp.removeAttribute('aria-activedescendant');cur=-1}
function mark(){var as=box.querySelectorAll('a');as.forEach(function(e,i){e.classList.toggle('on',i===cur)});if(cur>=0){inp.setAttribute('aria-activedescendant','ahkSg'+cur);as[cur].scrollIntoView({block:'nearest'})}}
inp.addEventListener('focus',function(){window.ahkSuggestOpen=true;more();if(inp.value)show()});inp.addEventListener('blur',function(){window.ahkSuggestOpen=false});inp.addEventListener('input',function(){more();show()});
inp.addEventListener('keydown',function(e){if(box.hidden)return;if(e.key==='ArrowDown'){cur=Math.min(cur+1,items.length-1);mark();e.preventDefault()}else if(e.key==='ArrowUp'){cur=Math.max(cur-1,-1);mark();e.preventDefault()}else if(e.key==='Enter'&&cur>=0){e.preventDefault();box.querySelectorAll('a')[cur].click()}else if(e.key==='Enter'){close();inp.blur();var ab=document.getElementById('allBrands');if(ab)window.scrollTo({top:ab.offsetTop-90,behavior:'smooth'})}else if(e.key==='Escape'){close()}});
document.addEventListener('pointerdown',function(e){if(!wrap.contains(e.target))close()});window.addEventListener('pageshow',close);})();</script>
"""
def _sg(t):
    t = t.replace("if (anyVisible && !restoringState) {\nwindow.scrollTo(", "if (anyVisible && !restoringState && !window.ahkSuggestOpen) {\nwindow.scrollTo(", 1)
    if "<!--ahk-suggest-->" in t: return t
    return t.replace("</body>", _SUG + "</body>", 1)
_rw("brand-check.html", _sg)
print("Section 62 applied")
