import json, os, re, glob, urllib.parse, subprocess, html, datetime, unicodedata
def run(c):
    print(">", c); subprocess.run(c, shell=True, check=False)
run("python3 scripts/add_stamps.py")
raw = json.load(open("data/brands.json")); brands = raw["brands"] if isinstance(raw, dict) else raw
E = html.escape
ALIAS = {"edgewell": "edgewell-personal-care", "estee-lauder": "estee-lauder-companies", "kao": "kao-corporation", "p-g": "procter-gamble", "s-c-johnson": "sc-johnson", "reckitt": "reckitt-benckiser"}
def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return ALIAS.get(s, s)
for _f in glob.glob("parent-*.html"): os.remove(_f)
# ---------- info pages (copied from privacy.html so the look matches) ----------
tpl = open("privacy.html", encoding="utf-8").read()
WRAP = '<div class="ahk-info" style="max-width:640px;margin:28px auto 40px;line-height:1.7;padding:0 4px"><style>.ahk-info ul{padding-left:22px;margin:18px 0}.ahk-info li{margin:0;padding:7px 0}.ahk-info a{color:inherit}</style>%s</div>'
def page(fname, title, kick, h1, body, desc):
    h = tpl
    h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % E(title), h, count=1, flags=re.S)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + E(desc) + m.group(2), h, count=1)
    h = re.sub(r'(<div class="k-ph">).*?(</div>)', lambda m: '%s<p class="k-kick">%s</p><h1 class="k-h1" style="margin-bottom:22px">%s</h1>%s' % (m.group(1), E(kick), E(h1), m.group(2)), h, count=1, flags=re.S)
    h = re.sub(r"(<div class=\"k-ph\">.*?</div>).*?(</main>)", lambda m: m.group(1) + WRAP % body + m.group(2), h, count=1, flags=re.S)
    open(fname, "w", encoding="utf-8").write(h)
H2 = '<h2 style="margin:28px 0 6px">%s</h2>'
decide = (H2 % "Four answers" + "<p>Every brand gets one of four answers.</p>"
 "<p><strong>Certified.</strong> Leaping Bunny or PETA lists the brand as cruelty-free. I link to their listing so you can check it yourself.</p>"
 "<p><strong>Not certified.</strong> I couldn't find a Leaping Bunny or PETA certification. This doesn't mean the brand tests on animals, as many haven't applied. Where the brand says it's cruelty-free, I link to what it says.</p>"
 "<p><strong>Tests on animals.</strong> The brand, or the company behind it, tests on animals or sells where the law requires it. Every one of these has a source.</p>"
 "<p><strong>Vegan</strong> is checked separately, because a brand can be cruelty-free without being vegan.</p>"
 + H2 % "Ethical rating" + "<p>The ethical rating comes from Good On You. It covers how a brand treats people, the planet and animals overall, so it isn't about animal testing. It's their rating, not mine, and each one links to their page.</p>"
 + H2 % "Parent companies" + "<p>A brand can be cruelty-free while the company that owns it isn't. Each parent company has its own page.</p><p><strong>Independent</strong> only appears where the brand says it is independently or family owned. <strong>Unknown</strong> means I couldn't find a parent company yet, so the brand may well be independent. I add owners once I've checked them.</p>"
 + H2 % "Sources" + "<p>Every brand page lists where I checked, which is the Leaping Bunny, Cruelty Free International and PETA lists. Where a brand has its own certification page or statement, I link to that too.</p>"
 + H2 % "Mistakes" + "<p>I check certifier lists, brand websites and public databases, and I check as much as I can by hand. Brands change, so each page shows when I last checked it. If you spot a mistake, email hello@ahomekind.com and I'll fix it.</p>")
funded = ("<p>A Home Kind is just me. No brand pays to be listed or to be rated better, and I don't take brand sponsorship. There are no adverts on the site.</p>"
 + H2 % "Where any income comes from" + "<p>Some links are Amazon affiliate links, which earn me a small commission if you buy, at no extra cost to you. They're marked &quot;paid link&quot; and never change what a brand is shown as.</p>"
 "<p>The shop sells tees and homeware through Teemill that I've checked are cruelty-free and vegan.</p>"
 "<p>That's everything. I haven't earned anything from the site yet.</p>")
page("how-i-decide.html", "How I decide - a home kind", "how it works", "How I decide", decide, "How I decide whether a brand is certified, not certified or tests on animals.")
page("how-this-site-is-funded.html", "How this site is funded - a home kind", "the small print", "How this site is funded", funded, "No brand pays to be listed. Here is how a home kind is funded.")
FOOT = re.compile(r'<a href="((?:\.\./)*)about\.html">about</a>')
def foot(m):
    p = m.group(1)
    return m.group(0) + ' &middot; <a href="%show-i-decide.html">how I decide</a> &middot; <a href="%sparent-companies.html">parent companies</a> &middot; <a href="%show-this-site-is-funded.html">how this site is funded</a>' % (p, p, p)
for f in glob.glob("**/*.html", recursive=True):
    h = open(f, encoding="utf-8").read()
    if "how-i-decide" in h or not FOOT.search(h): continue
    open(f, "w", encoding="utf-8").write(FOOT.sub(foot, h, count=1))
# ---------- brand page extras ----------
gsgd = {}
if os.path.exists("data/good-shopping-guide.json"):
    gsgd = {k: v for k, v in json.load(open("data/good-shopping-guide.json")).items() if not k.startswith("_")}
goy = {}
if os.path.exists("data/good-on-you.json"):
    goy = {k: v for k, v in json.load(open("data/good-on-you.json")).items() if not k.startswith("_")}
paths = {}
for b in brands:
    fl = glob.glob("*/%s/index.html" % b["slug"])
    if fl: paths[b["slug"]] = fl[0]
good = [b for b in brands if b.get("tier") == "good" and b["slug"] in paths]
pslugs = {b["parentCompany"]: slugify(b["parentCompany"]) for b in brands if b.get("parentCompany")}
EX = "<!--ahk-extras-->"; n = 0
for b in brands:
    f = paths.get(b["slug"])
    if not f: continue
    h = open(f, encoding="utf-8").read()
    if EX in h: continue
    g = goy.get(b["slug"])
    gg = gsgd.get(b["slug"])
    if gg and "data-gs=" not in h:
        h = re.sub(r'(class="ahk-stamps-mount" data-s="[a-z,]*")', lambda m: '%s data-gs="%d" data-gu="%s"' % (m.group(1), gg["score"], gg["url"]), h, count=1)
    if g and "data-g=" not in h:
        h = re.sub(r'(class="ahk-stamps-mount" data-s="[a-z,]*")', lambda m: '%s data-g="%d" data-u="%s"' % (m.group(1), g["score"], g["url"]), h, count=1)
    if b.get("parentCompany"):
        h = re.sub(r'(<span class="status-pill-label">parent company</span> )' + re.escape(E(b["parentCompany"])) + r"(</span>)",
            lambda m: '%s<a href="/parent-%s" style="color:inherit;text-decoration:underline">%s</a>%s' % (m.group(1), pslugs[b["parentCompany"]], E(b["parentCompany"]), m.group(2)), h, count=1)
    if not b.get("parentCompany"):
        h = re.sub(r"(&middot; )Independent( &middot;)", r"\1Owner not listed yet\2", h, count=1)
    add = EX
    if b.get("lastVerified"):
        add += '<p style="font-size:13px;opacity:.7;margin:4px 0">Last checked: %s &middot; <a href="/how-i-decide">How I decide</a></p>' % E(str(b["lastVerified"]))
    h = h.replace("</h1><!--ahk-stamps-->", "</h1><!--ahk-stamps-->", 1)
    h = re.sub(r'(<div class="ahk-stamps-mount"[^>]*></div>)', lambda m: m.group(1) + add, h, count=1)
    if b.get("tier") in ("unverified", "bad") and b.get("category"):
        alts = [x for x in good if x["slug"] != b["slug"] and set(x.get("category") or []) & set(b["category"])][:3]
        if alts:
            ul = "".join('<li><a href="../%s/">%s</a></li>' % (x["slug"], E(x["name"])) for x in alts)
            h = h.replace("</main>", '<div style="margin:24px 0"><h2>Cruelty-free alternatives</h2><ul>%s</ul></div></main>' % ul, 1)
    if b.get("parentCompany"):
        pj = json.dumps([b["parentCompany"], "/parent-" + pslugs[b["parentCompany"]]]).replace("</", "<\\/")
        h = h.replace("</body>", "<script>(function(p){var w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT),a=[],t;while(t=w.nextNode())if(t.nodeValue.trim()===p[0]&&!t.parentNode.closest('a,footer,nav,script,title,h1'))a.push(t);a.forEach(function(t){var l=document.createElement('a');l.href=p[1];l.style.cssText='color:inherit;text-decoration:underline';t.parentNode.insertBefore(l,t);l.appendChild(t)})})(" + pj + ")</script></body>", 1)
    SHOPS = {"Boots": "https://www.boots.com/sitesearch?searchTerm=%s", "Superdrug": "https://www.superdrug.com/search?text=%s", "Sephora UK": "https://www.sephora.co.uk/search?q=%s",
             "Waitrose": "https://www.waitrose.com/ecom/shop/search?&searchTerm=%s", "Ocado": "https://www.ocado.com/search?entry=%s",
             "Tesco": "https://www.tesco.com/groceries/en-GB/search?query=%s", "Morrisons": "https://groceries.morrisons.com/search?entry=%s"}
    shops = b.get("stockists") or (["Boots", "Superdrug", "Sephora UK"] if set(b.get("category") or []) & {"skincare", "makeup-beauty", "body-shower", "haircare", "dental", "period-menstrual"} else [])
    shops = [x for x in shops if x in SHOPS]
    if b.get("tier") in ("good", "check", "warn") and shops:
        q = urllib.parse.quote(b["name"])
        links = " &middot; ".join('<a href="%s" target="_blank" rel="noopener">%s</a>' % (SHOPS[x] % q, x) for x in shops)
        shop = ('<div class="k-sec" style="margin:24px 0"><p class="section-label">where to look in the UK</p><p style="font-size:13.5px;margin:0 0 8px">Search for %s at: %s</p>'
          '<p style="font-size:12.5px;color:#6A535D;margin:0">These are plain search links. I earn nothing from them, and not every shop stocks every brand.</p></div>') % (E(b["name"]), links)
        h = h.replace('<div class="signed">', shop + '<div class="signed">', 1)
    open(f, "w", encoding="utf-8").write(h); n += 1
print("Extras added to", n, "brand pages")
# ---------- parent company pages ----------
# ---------- parent page brand chips ----------
PCSS = ('<style>.pc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin:14px 0}'
 '.pc-chip{display:flex;flex-direction:column;gap:6px;padding:10px 12px;border:1.5px solid #E5CFC4;border-radius:14px;background:#FBF4EF;text-decoration:none;color:#2A1630;line-height:1.25}'
 '.pc-chip:hover,.pc-chip:focus-visible{border-color:#E8804C}'
 '.pc-name{font-weight:600;font-size:15px}.pc-tag{font-size:12px;color:#6A535D}'
 '.pc-st{display:flex;gap:5px;align-items:center;flex-wrap:wrap;min-height:26px}'
 '.pc-s{width:26px;height:26px;border-radius:50%;border:1.5px solid #3A1F3D;background:#F4E6DE;color:#3A1F3D;display:grid;place-items:center;font:700 9px/1 system-ui,sans-serif}'
 '.pc-s.v{background:#3A1F3D;color:#F4E6DE}.pc-s.u{border-style:dashed;font-size:13px}.pc-s.x{background:#9C3A3A;border-color:#9C3A3A;color:#fff;font-size:13px}'
 '.pc-r{font:700 11px/1 system-ui,sans-serif;color:#fff;border-radius:999px;padding:7px 8px;background:#8A6A00}.pc-r4,.pc-r5{background:#4C7A3A}.pc-r1{background:#9C3A3A}.pc-r2{background:#B4601F}</style>')
TAGS = {"good": "cruelty-free and vegan", "check": "cruelty-free", "warn": "owner isn't", "bad": "tests on animals", "unverified": "not certified"}
def chip(b):
    t = b.get("tier", ""); n = (b.get("note") or "") + " " + (b.get("claim") or ""); st = []
    if t == "unverified": st.append('<span class="pc-s u" title="Not certified">?</span>')
    if t == "bad": st.append('<span class="pc-s x" title="Tests on animals">X</span>')
    if b.get("vegan") == "full": st.append('<span class="pc-s v" title="Vegan">V</span>')
    if t in ("good", "check", "warn") and re.search("Leaping Bunny|Cruelty Free International", n): st.append('<span class="pc-s" title="Leaping Bunny">LB</span>')
    if t in ("good", "check", "warn") and "PETA" in n: st.append('<span class="pc-s" title="PETA">PETA</span>')
    g = goy.get(b["slug"])
    if g: st.append('<span class="pc-r pc-r%d" title="Good On You rating">%d/5</span>' % (g["score"], g["score"]))
    gq = gsgd.get(b["slug"])
    if gq: st.append('<span class="pc-r pc-r%d" title="Good Shopping Guide score">%d/100</span>' % (4 if gq["score"] >= 80 else 3 if gq["score"] >= 60 else 2, gq["score"]))
    return '<a class="pc-chip" href="/%s/"><span class="pc-name">%s</span><span class="pc-st">%s</span><span class="pc-tag">%s</span></a>' % (os.path.dirname(paths[b["slug"]]), E(b["name"]), "".join(st), TAGS.get(t, ""))
PARENT_POLICY = {
"Beiersdorf": {
"url": "https://reports.beiersdorf.com/annual-report/2023/combined-management-report/non-financial-statement/other-issues.html",
"summary": "Page says Beiersdorf does not conduct animal tests for any of its cosmetic products or their ingredients unless required to do so by the authorities, and that any animal testing for medical devices and pharmaceuticals is limited to the absolute minimum necessary."
},
"Church & Dwight": {
"url": "https://churchdwight.com/our-brands/animal-testing-policy.aspx",
"summary": "Page says it is the company's policy not to test on animals, and asks suppliers not to test on animals unless required by law or regulation, using accredited contract labs when testing is legally necessary."
},
"Clorox": {
"url": "https://www.thecloroxcompany.com/company/policies-and-practices/animal-testing/",
"summary": "Page says Clorox does not conduct or ask third parties to conduct animal testing unless required by law with no available alternative, and notes Burt's Bees is Leaping Bunny certified."
},
"Colgate-Palmolive": {
"url": "https://www.colgatepalmolive.com/en-us/who-we-are/blog/our-commitment-to-animal-welfare",
"summary": "Page says a voluntary moratorium on animal testing of adult Personal Care Products has applied worldwide since 1999, and that animal testing is only conducted where specifically required by regulatory agencies; no third-party certification is named."
},
"Coty": {
"url": "https://www.coty.com/faq",
"summary": "Page says Coty does not test its products on animals, acknowledges some governments or agencies still require animal testing of certain products and that it uses China's exemptions for general cosmetics, and states COVERGIRL, Rimmel and Manhattan are Leaping Bunny approved."
},
"Edgewell Personal Care": {
"url": "https://cdn.shopify.com/s/files/1/0598/9538/2192/files/Corporate_Animal_Testing_Policy.pdf?v=1724093148",
"summary": "Policy PDF linked from edgewell.com says Edgewell products are only tested on animals in those markets where required to do so by law, and that non-animal methods are chosen whenever possible; no certification is mentioned."
},
"Essity": {
"url": "https://www.essity.com/sustainability/improving-well-being-for-people-and-societies/product-safety-and-transparency/for-us-its-personal/faq/",
"summary": "Page says Essity never tests its products on animals unless there is no way to avoid it, for instance in some countries like China where the law requires it; no certification is mentioned."
},
"Estée Lauder Companies": {
"url": "https://www.elcompanies.com/en/our-impact/viewpoints/animal-testing",
"summary": "Page says it does not test its products on animals and does not ask others to test for it, acknowledges that animal testing exists where a regulatory body demands it, and lists brands with PETA certification and some also Leaping Bunny approved."
},
"Hain Celestial": {
"url": "https://www.hain.com/wp-content/uploads/ESG/Hain-Animal-Welfare2020.pdf",
"summary": "Policy says Hain is committed to never testing personal care products on animals and that its personal care brands (Alba Botanica, Avalon Organics, JASON, Live Clean, Queen Helene) are Leaping Bunny certified; it does not address other product categories."
},
"Haleon": {
"url": "https://www.haleon.com/content/dam/haleon/corporate/documents/who-we-are/governance/Haleon-The-use-of-animals-in-research.pdf.downloadasset.pdf",
"summary": "Position says Haleon only uses animals in developing new products where alternative forms of testing do not exist or where there is a scientific, legal or regulatory requirement, has a zero-tolerance commitment on animal testing for cosmetic purposes, and uses AAALAC-accredited outside partners."
},
"Henkel": {
"url": "https://www.henkel.com/sustainability/positions/test-methods",
"summary": "Page says Henkel does not test its hair and body care products, detergents and cleaning products, or adhesives on animals, but that some countries still make animal testing mandatory for approval and REACH can require it by law."
},
"J&J / Kenvue": {
"url": "https://kenvue.com/animal-testing-pdf",
"summary": "Page says Kenvue does not test cosmetics on animals unless required by regulators, uses animal testing only as a last resort following the 3Rs, and that its Scientific Committee approves all instances; no certification is named."
},
"Johnson & Johnson": {
"url": "https://www.jnj.com/policies-reports/animal-welfare-policy",
"summary": "Policy covers animal work in research and safety testing, requires ethics committee approval and AAALAC-accredited facilities, and advocates non-animal alternatives whenever feasible; it does not mention cosmetics or state animal testing is only legally required."
},
"Kao Corporation": {
"url": "https://www.kao.com/global/en/innovation/safety-quality/animal-testing-policy/",
"summary": "Page says Kao does not and will not conduct animal testing in cosmetics development nor outsource it, except where required by government agencies in particular countries, and for other products avoids it unless unavoidable due to lack of alternatives or regulatory requirements."
},
"Kimberly-Clark": {
"url": "https://kimberly-clark.com/es-us/suppliers/standards-and-requirements/animal-testing",
"summary": "The page says Kimberly-Clark does not test products or ingredients on animals unless required, with animal testing undertaken only where required by law, regulation or government authority, and it names no certifications."
},
"Kosé Corporation": {
"url": "https://koseholdings.co.jp/en/kose/research/secretstory/safety/",
"summary": "The page states a policy of not conducting animal testing, with exceptions when society holds the company responsible for evidence of product safety or when required by administrations in particular countries, and it names no third-party certification."
},
"L'Occitane": {
"url": "https://group.loccitane.com/sites/default/files/20120806_Statement_from_LOccitane_onAnimal_Testing_EN.pdf",
"summary": "A 2012 statement says L'Occitane does not and never has tested its products on animals, notes that China requires tests, and says it is working with BUAV and Chinese authorities on alternatives, with no third-party certification named."
},
"L'Oréal": {
"url": "https://www.loreal.com/en/commitments-and-responsibilities/for-our-products/for-beauty-with-no-animal-testing/milestones-in-the-safety-assessment-without-animal/",
"summary": "The page says L'Oréal stopped testing its finished products on animals in 1989 and lists China milestones (2014, 2021) after which certain products there are no longer animal tested, without stating whether any testing occurs today and naming no certification."
},
"OSEA Malibu": {
"url": "https://oseamalibu.com/pages/cruelty-free-skincare",
"summary": "The page says products are never tested for safety or efficacy on animals and no ingredients tested on animals are used, that it is Leaping Bunny certified (since 2000) and PETA vegan-certified."
},
"Paul Mitchell": {
"url": "https://www.paulmitchell.com/pages/faq",
"summary": "The FAQ says the products are cruelty-free and that it was the first professional beauty company to announce it does not conduct or endorse animal testing, with no circumstances or certifications mentioned."
},
"Procter & Gamble": {
"url": "https://us.pg.com/cruelty-free/",
"summary": "The page says P&G no longer animal tests any consumer product unless required by law, and names no certification body."
},
"Reckitt Benckiser": {
"url": "https://www.reckitt.com/media/5833/rb-animal-testing-policy-2019.pdf",
"summary": "The 2019 policy says animal testing is not routine and is only done where required by government agencies, plus limited cases for infant nutrition safety and rodent and insect tests for pest control products, with no certifications named."
},
"Revlon": {
"url": "https://www.revlon.com/pages/animal-testing",
"summary": "The page says Revlon does not conduct animal testing and has not done so for decades, and that where some countries' regulators run their own animal tests for registration this is done by the regulators, with no certifications mentioned."
},
"SC Johnson": {
"url": "https://scjohnson.com/en/news-stories/official-communications/sc-johnson-point-of-view-on-animal-testing",
"summary": "The page says SC Johnson chooses non-animal testing methods wherever possible and follows legal requirements in countries that require testing for certain products, with no certifications mentioned."
},
"Shiseido": {
"url": "https://corp.shiseido.com/en/sustainability/consumer/experiment/",
"summary": "The page says Shiseido has completely abolished animal testing (marked with an unexplained asterisk) and has run a safety assurance system without animal testing since 2013, naming no third-party certification."
},
"Unilever": {
"url": "https://www.unilever.com/files/glo-alternative-approaches-to-animal-testing.pdf",
"summary": "The document says Unilever does not test on animals, but that suppliers may need to test some ingredients and some government authorities test certain product types on animals to meet legal requirements, and it notes certain brands are certified by animal protection groups and PETA lists Unilever as a company working for regulatory change."
}
}
ASH_NOTES = {"Unilever": "I read this properly. It says Unilever doesn't test on animals, and also that some governments still require testing and some suppliers may still test ingredients. It never says plainly whether its own products are tested. Their 'Safety Without Animal Testing' page sent me to a general sustainability page with nothing on animals. That reads as vague to me, so read it and decide."}
made = 0
groups = {}
for b in brands:
    if b.get("parentCompany"): groups.setdefault(slugify(b["parentCompany"]), []).append(b)
for ps, kids in groups.items():
    name = max({b["parentCompany"] for b in kids}, key=len)
    flags = [b.get("parentTestsOnAnimals") for b in kids if "parentTestsOnAnimals" in b]
    if True in flags: st = "This company tests on animals, or sells where animal testing is required."
    elif False in flags: st = "This company doesn't test on animals."
    else: st = "I haven't confirmed this company's animal testing policy yet."
    pol = PARENT_POLICY.get(name) or next((PARENT_POLICY[k] for k in PARENT_POLICY if slugify(k) == ps), None)
    polhtml = ""
    if pol and True not in flags and False not in flags: st = "Their own published statement is below."
    if pol:
        polhtml = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@700&display=swap"><div class="pc-pol"><h2>What their own policy says</h2><p>%s</p><p><a href="%s" target="_blank" rel="noopener">Read the company\'s own page</a></p>' % (E(pol["summary"]), E(pol["url"]))
        nt = ASH_NOTES.get(name) or next((ASH_NOTES[k] for k in ASH_NOTES if slugify(k) == ps), None)
        if nt: polhtml += '<p class="ahk-hand pc-note" style="font-family:Caveat,cursive;font-size:23px;line-height:1.3;margin:14px 0 0">%s</p>' % E(nt)
        polhtml += "</div>"
    elif True not in flags and False not in flags: polhtml = "<p>I couldn't find a published animal testing policy from this company.</p>"
    li = "".join(chip(b) for b in sorted(kids, key=lambda x: x["name"].lower()) if b["slug"] in paths)
    body = PCSS + "<p><strong>%s</strong></p><p>A brand can be cruelty-free while the company that owns it isn't, so I show both.</p>%s%s<div class=\"pc-grid\">%s</div>" % (E(st), polhtml, H2 % "Brands I list from this company", li)
    page("parent-%s.html" % ps, "%s - a home kind" % name, "parent company", name, body, "Animal testing policy of %s and the brands I list from it." % name)
    made += 1
idx = "".join('<li><a href="/parent-%s">%s</a></li>' % (ps, E(max({b["parentCompany"] for b in kids}, key=len))) for ps, kids in sorted(groups.items()))
page("parent-companies.html", "Parent companies - a home kind", "who owns who", "Parent companies", "<p>A brand can be cruelty-free while the company that owns it isn't. Each company below has its own page with the brands I list from it.</p><ul>%s</ul>" % idx, "Every parent company on a home kind and its animal testing policy.")
if os.path.exists("sitemap.xml"):
    sm = open("sitemap.xml", encoding="utf-8").read()
    mm = re.search(r"<loc>(https?://[^/<]+)", sm)
    if mm:
        base = mm.group(1)
        new = ["how-i-decide", "how-this-site-is-funded", "parent-companies"] + ["parent-" + ps for ps in groups]
        add_ = "".join("<url><loc>%s/%s</loc></url>" % (base, u) for u in new if "/%s</loc>" % u not in sm)
        if add_: open("sitemap.xml", "w", encoding="utf-8").write(sm.replace("</urlset>", add_ + "</urlset>"))
print("Parent pages:", made)
run('git add -A . && git commit -m "Add How I decide, funding page, parent company pages, last checked dates and alternatives"')
