import json, os, re, glob, subprocess, html, datetime
def run(c):
    print(">", c); subprocess.run(c, shell=True, check=False)
run("python3 scripts/add_stamps.py")
raw = json.load(open("data/brands.json")); brands = raw["brands"] if isinstance(raw, dict) else raw
E = html.escape
def slugify(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
# ---------- info pages (copied from privacy.html so the look matches) ----------
tpl = open("privacy.html", encoding="utf-8").read()
WRAP = '<div style="max-width:640px;margin:0 auto 40px;line-height:1.7">%s</div>'
def page(fname, title, kick, h1, body, desc):
    h = tpl
    h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % E(title), h, count=1, flags=re.S)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + E(desc) + m.group(2), h, count=1)
    h = re.sub(r'(<div class="k-ph">).*?(</div>)', lambda m: '%s<p class="k-kick">%s</p><h1 class="k-h1">%s</h1>%s' % (m.group(1), E(kick), E(h1), m.group(2)), h, count=1, flags=re.S)
    h = re.sub(r"(<div class=\"k-ph\">.*?</div>).*?(</main>)", lambda m: m.group(1) + WRAP % body + m.group(2), h, count=1, flags=re.S)
    open(fname, "w", encoding="utf-8").write(h)
H2 = '<h2 style="margin:28px 0 6px">%s</h2>'
decide = (H2 % "Four answers" + "<p>Every brand gets one of four answers.</p>"
 "<p><strong>Certified.</strong> Leaping Bunny or PETA lists the brand as cruelty-free. I link to their listing so you can check it yourself.</p>"
 "<p><strong>Not certified.</strong> I couldn't find a Leaping Bunny or PETA certification. This doesn't mean the brand tests on animals, as many haven't applied. Where the brand says it's cruelty-free, I link to what it says.</p>"
 "<p><strong>Tests on animals.</strong> The brand, or the company behind it, tests on animals or sells where the law requires it. Every one of these has a source.</p>"
 "<p><strong>Vegan</strong> is checked separately, because a brand can be cruelty-free without being vegan.</p>"
 + H2 % "Ethical rating" + "<p>The ethical rating comes from Good On You. It covers how a brand treats people, the planet and animals overall, so it isn't about animal testing. It's their rating, not mine, and each one links to their page.</p>"
 + H2 % "Parent companies" + "<p>A brand can be cruelty-free while the company that owns it isn't. Each parent company has its own page.</p>"
 + H2 % "Mistakes" + "<p>I check certifier lists, brand websites and public databases, and I check as much as I can by hand. Brands change, so each page shows when I last checked it. If you spot a mistake, email hello@ahomekind.com and I'll fix it.</p>")
funded = ("<p>A Home Kind is just me. No brand pays to be listed or to be rated better, and I don't take brand sponsorship. There are no adverts on the site.</p>"
 + H2 % "Where any income comes from" + "<p>Some links are Amazon affiliate links, which earn me a small commission if you buy, at no extra cost to you. They're marked &quot;paid link&quot; and never change what a brand is shown as.</p>"
 "<p>The shop sells tees and homeware through Teemill that I've checked are cruelty-free and vegan.</p>"
 "<p>That's everything. I haven't earned anything from the site yet.</p>")
page("how-i-decide.html", "How I decide - a home kind", "how it works", "How I decide", decide, "How I decide whether a brand is certified, not certified or tests on animals.")
page("how-this-site-is-funded.html", "How this site is funded - a home kind", "the small print", "How this site is funded", funded, "No brand pays to be listed. Here is how a home kind is funded.")
for f in glob.glob("*.html"):
    h = open(f, encoding="utf-8").read(); a = '<a href="about.html">about</a>'
    if a in h and "how-i-decide" not in h:
        h = h.replace(a, a + ' &middot; <a href="how-i-decide.html">how I decide</a> &middot; <a href="how-this-site-is-funded.html">how this site is funded</a>', 1)
        open(f, "w", encoding="utf-8").write(h)
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
            lambda m: '%s<a href="/parent-%s">%s</a>%s' % (m.group(1), pslugs[b["parentCompany"]], E(b["parentCompany"]), m.group(2)), h, count=1)
    add = EX
    if b.get("lastVerified"):
        add += '<p style="font-size:13px;opacity:.7;margin:4px 0">Last checked: %s</p>' % E(str(b["lastVerified"]))
    h = h.replace("</h1><!--ahk-stamps-->", "</h1><!--ahk-stamps-->", 1)
    h = re.sub(r'(<div class="ahk-stamps-mount"[^>]*></div>)', lambda m: m.group(1) + add, h, count=1)
    if b.get("tier") in ("unverified", "bad") and b.get("category"):
        alts = [x for x in good if x["slug"] != b["slug"] and set(x.get("category") or []) & set(b["category"])][:3]
        if alts:
            ul = "".join('<li><a href="../%s/">%s</a></li>' % (x["slug"], E(x["name"])) for x in alts)
            h = h.replace("</main>", '<div style="margin:24px 0"><h2>Cruelty-free alternatives</h2><ul>%s</ul></div></main>' % ul, 1)
    open(f, "w", encoding="utf-8").write(h); n += 1
print("Extras added to", n, "brand pages")
# ---------- parent company pages ----------
made = 0
for name, ps in pslugs.items():
    kids = [b for b in brands if b.get("parentCompany") == name]
    flags = [b.get("parentTestsOnAnimals") for b in kids if "parentTestsOnAnimals" in b]
    if True in flags: st = "This company tests on animals, or sells where animal testing is required."
    elif False in flags: st = "This company doesn't test on animals."
    else: st = "I haven't confirmed this company's animal testing policy yet."
    li = "".join('<li><a href="/%s/">%s</a></li>' % (os.path.dirname(paths[b["slug"]]), E(b["name"])) for b in kids if b["slug"] in paths)
    body = "<p><strong>%s</strong></p><p>A brand can be cruelty-free while the company that owns it isn't, so I show both.</p>%s<ul>%s</ul>" % (E(st), H2 % "Brands I list from this company", li)
    page("parent-%s.html" % ps, "%s - a home kind" % name, "parent company", name, body, "Animal testing policy of %s and the brands I list from it." % name)
    made += 1
print("Parent pages:", made)
run('git add -A . && git commit -m "Add How I decide, funding page, parent company pages, last checked dates and alternatives"')
