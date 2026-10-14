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
