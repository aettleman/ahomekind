#!/usr/bin/env python3
"""Find FREE-TO-REUSE brand logos on Wikidata / Wikimedia Commons.

Strict rules (nothing is added to the site by this script):
  1. The Wikidata item's English label must match the brand name exactly
     (ignoring capitals, accents and punctuation). Several matches = skipped.
  2. The item must have a logo image (property P154) and look like a brand/company.
  3. The logo file on Wikimedia Commons must be public domain or CC0.
     Logos under licences that need credit (CC BY etc.) are only listed, never saved.
Run:  cd ~/Documents/ahomekind && python3 scripts/find-brand-logos.py
Writes: scripts/logo-report.json  and  scripts/logo-candidates/<slug>.png (previews only)
"""
import json, os, re, sys, time, unicodedata, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "scripts", "logo-candidates")
REPORT = os.path.join(ROOT, "scripts", "logo-report.json")
CACHE = os.path.join(ROOT, "scripts", ".logo-cache.json")
UA = "ahomekind-logo-check/1.0 (https://ahomekind.com; hello@ahomekind.com)"
WD = "https://www.wikidata.org/w/api.php"
CM = "https://commons.wikimedia.org/w/api.php"
BRANDISH = re.compile(r"brand|company|cosmetic|manufactur|retail|skin|beauty|fashion|food|cloth|chain|personal care|product|label|perfume|fragrance|hair|soap|clean|detergent|supermarket|drink|confection|footwear|apparel|toiletr", re.I)

def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("&", "and")
    return re.sub(r"[^a-z0-9]", "", s)

def get(url, params=None, binary=False, tries=4):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            return data if binary else json.loads(data)
        except Exception as e:
            if i == tries - 1:
                print("  request failed:", e)
                return None
            time.sleep(1.5 * (i + 1))

def load_cache():
    try:
        return json.load(open(CACHE))
    except Exception:
        return {}

def main():
    brands = json.load(open(os.path.join(ROOT, "data", "brands.json")))
    os.makedirs(OUT_DIR, exist_ok=True)
    cache = load_cache()
    results = []
    counts = {"saved": 0, "needs_credit": 0, "no_match": 0, "ambiguous": 0, "no_logo": 0, "not_brand": 0, "error": 0}
    for n, b in enumerate(brands, 1):
        slug, name = b["slug"], b["name"]
        key = norm(name)
        if not key:
            continue
        if key in cache and cache[key].get("done"):
            res = cache[key]["res"]
        else:
            res = lookup(name)
            cache[key] = {"done": res.get("status") != "error", "res": res}
            if n % 25 == 0:
                json.dump(cache, open(CACHE, "w"))
            time.sleep(0.2)
        res = dict(res, slug=slug, name=name)
        if res["status"] == "saved":
            path = os.path.join(OUT_DIR, slug + ".png")
            if not os.path.exists(path) and res.get("thumb"):
                data = get(res["thumb"], binary=True)
                if data:
                    open(path, "wb").write(data)
                else:
                    res["status"] = "error"
            res["file"] = "scripts/logo-candidates/%s.png" % slug
        counts[res["status"]] = counts.get(res["status"], 0) + 1
        results.append(res)
        if n % 50 == 0:
            print("%d / %d done  (free logos so far: %d)" % (n, len(brands), counts["saved"]))
    json.dump(cache, open(CACHE, "w"))
    json.dump({"counts": counts, "total": len(brands), "results": results}, open(REPORT, "w"), indent=1)
    print("\nDONE. Brands checked: %d" % len(brands))
    for k, v in counts.items():
        print("  %-13s %d" % (k, v))
    print("Report: scripts/logo-report.json   Previews: scripts/logo-candidates/")

def lookup(name):
    s = get(WD, {"action": "wbsearchentities", "search": name, "language": "en", "type": "item", "limit": 7, "format": "json"})
    if s is None:
        return {"status": "error"}
    ids = [x["id"] for x in s.get("search", [])
           if norm(x.get("label", "")) == norm(name)]
    if not ids:
        return {"status": "no_match"}
    ents = get(WD, {"action": "wbgetentities", "ids": "|".join(ids), "props": "descriptions|claims", "languages": "en", "format": "json"})
    if ents is None:
        return {"status": "error"}
    cands = []
    for qid in ids:
        e = ents.get("entities", {}).get(qid, {})
        desc = (e.get("descriptions", {}).get("en", {}) or {}).get("value", "")
        if not BRANDISH.search(desc):
            continue
        cands.append((qid, desc, e.get("claims", {})))
    if not cands:
        return {"status": "not_brand"}
    if len(cands) > 1:
        return {"status": "ambiguous", "wikidata": [c[0] for c in cands]}
    qid, desc, claims = cands[0]
    logo = None
    for prop in ("P154", "P8972"):
        for c in claims.get(prop, []):
            if c.get("rank") == "deprecated":
                continue
            v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
            if v:
                logo = v
                break
        if logo:
            break
    if not logo:
        return {"status": "no_logo", "wikidata": qid, "description": desc}
    info = get(CM, {"action": "query", "titles": "File:" + logo, "prop": "imageinfo", "iiprop": "url|extmetadata|mime", "iiurlwidth": 300, "format": "json"})
    if info is None:
        return {"status": "error"}
    page = next(iter(info.get("query", {}).get("pages", {}).values()), {})
    ii = (page.get("imageinfo") or [{}])[0]
    meta = ii.get("extmetadata", {})
    lic = (meta.get("LicenseShortName", {}) or {}).get("value", "")
    copyrighted = (meta.get("Copyrighted", {}) or {}).get("value", "")
    restrictions = (meta.get("Restrictions", {}) or {}).get("value", "")
    artist = re.sub(r"<[^>]+>", "", (meta.get("Artist", {}) or {}).get("value", ""))[:120]
    free = bool(re.match(r"^(public domain|pd|cc0)", lic, re.I)) or copyrighted.lower() == "false"
    base = {"wikidata": qid, "description": desc, "commons_file": logo, "license": lic,
            "page": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(logo.replace(" ", "_")),
            "author": artist, "restrictions": restrictions}
    if free:
        return dict(base, status="saved", thumb=ii.get("thumburl"))
    return dict(base, status="needs_credit")

if __name__ == "__main__":
    main()
