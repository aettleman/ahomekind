import json, os, re, glob, subprocess
GOY = {"ted-baker": (2, "https://directory.goodonyou.eco/brand/ted-baker")}
MARK = "<!--ahk-stamps-->"
def run(c):
    print(">", c); subprocess.run(c, shell=True, check=False)
run("node scripts/generate-brand-pages.js"); run("node scripts/generate-brand-check.js")
raw = json.load(open("data/brands.json")); brands = raw["brands"] if isinstance(raw, dict) else raw
MOUNT = ("<script>document.querySelectorAll('.ahk-stamps-mount').forEach(function(e){var o={};"
 "(e.dataset.s||'').split(',').forEach(function(x){if(x)o[x]=1});"
 "if(e.dataset.g)o.goy={score:+e.dataset.g,url:e.dataset.u};e.innerHTML=AHKStamps.row(o)});</script>")
done = skipped = 0
for b in brands:
    files = glob.glob("*/%s/index.html" % b["slug"]) or glob.glob("%s/index.html" % b["slug"])
    if not files: skipped += 1; continue
    f = files[0]; h = open(f, encoding="utf-8").read()
    if MARK in h or "</h1>" not in h: skipped += 1; continue
    t = b.get("tier", ""); n = (b.get("note") or "") + " " + (b.get("claim") or "")
    s = []
    if t == "good": s.append("cf")
    if t == "unverified": s.append("unk")
    if t == "bad": s.append("ncf")
    if b.get("vegan") == "full": s.append("vegan")
    if t == "good" and re.search("Leaping Bunny|Cruelty Free International", n): s.append("lb")
    if t == "good" and "PETA" in n: s.append("peta")
    g = GOY.get(b["slug"]); ga = (' data-g="%d" data-u="%s"' % g) if g else ""
    div = '%s<div class="ahk-stamps-mount" data-s="%s"%s></div>' % (MARK, ",".join(s), ga)
    h = h.replace("</h1>", "</h1>" + div, 1)
    d = os.path.relpath(".", os.path.dirname(f))
    h = h.replace("</head>", '<link rel="stylesheet" href="%s/css/stamps.css"></head>' % d, 1)
    h = h.replace("</body>", '<script src="%s/js/stamps.js"></script>%s</body>' % (d, MOUNT), 1)
    open(f, "w", encoding="utf-8").write(h); done += 1
print("Stamps added to", done, "pages; skipped", skipped)
run("sed -i '' 's/ahk-shell-v56/ahk-shell-v57/' sw.js")
run('git add -A . && git commit -m "Add certification stamps, ethical rating and not-certified stamps to brand pages"')
