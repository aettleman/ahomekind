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
    if b.get("tier") in ("good", "check", "warn") and set(b.get("category") or []) & {"skincare", "makeup-beauty", "body-shower", "haircare", "dental", "period-menstrual"}:
        q = urllib.parse.quote(b["name"])
        shop = ('<div class="k-sec" style="margin:24px 0"><p class="section-label">where to look in the UK</p><p style="font-size:13.5px;margin:0 0 8px">Search for %s at: '
          '<a href="https://www.boots.com/sitesearch?searchTerm=%s" target="_blank" rel="noopener">Boots</a> &middot; '
          '<a href="https://www.superdrug.com/search?text=%s" target="_blank" rel="noopener">Superdrug</a> &middot; '
          '<a href="https://www.sephora.co.uk/search?q=%s" target="_blank" rel="noopener">Sephora UK</a></p>'
          '<p style="font-size:12.5px;color:#6A535D;margin:0">These are plain search links. I earn nothing from them, and not every shop stocks every brand.</p></div>') % (E(b["name"]), q, q, q)
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
    return '<a class="pc-chip" href="/%s/"><span class="pc-name">%s</span><span class="pc-st">%s</span><span class="pc-tag">%s</span></a>' % (os.path.dirname(paths[b["slug"]]), E(b["name"]), "".join(st), TAGS.get(t, ""))
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
    li = "".join(chip(b) for b in sorted(kids, key=lambda x: x["name"].lower()) if b["slug"] in paths)
    body = PCSS + "<p><strong>%s</strong></p><p>A brand can be cruelty-free while the company that owns it isn't, so I show both.</p>%s<div class=\"pc-grid\">%s</div>" % (E(st), H2 % "Brands I list from this company", li)
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
