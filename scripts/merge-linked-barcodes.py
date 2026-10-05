#!/usr/bin/env python3
"""Add barcode -> brand links collected from visitors to data/barcodes.json.

Every time someone scans a barcode that isn't recognised and then finds the
brand by name on the scan page, the site sends an anonymous 'barcode_linked'
event to PostHog. This script gathers those events and adds the links.

Run from the repo root:
    POSTHOG_KEY=phx_yourkey python3 scripts/merge-linked-barcodes.py          # fetch from PostHog
    python3 scripts/merge-linked-barcodes.py --csv export.csv                  # or use a CSV export
Options:
    --min N   how many separate visitors must agree before a link is added (default 2)
    --dry     show what would change without writing

Safety: a link is only added when at least --min events agree on ONE brand,
the brand exists in data/brands.json, and the barcode isn't already listed.
Disagreements and one-off links are printed for you to review, never added.
"""
import csv, json, os, sys, urllib.request
from collections import defaultdict, Counter

HOST = "https://eu.posthog.com"; PROJECT = "268720"
args = sys.argv[1:]
def opt(name, default=None):
    return args[args.index(name) + 1] if name in args else default
MIN = int(opt("--min", 2)); DRY = "--dry" in args

def fetch_events():
    key = os.environ.get("POSTHOG_KEY")
    if not key: sys.exit("Set POSTHOG_KEY=phx_... or pass --csv export.csv")
    q = {"query": {"kind": "HogQLQuery", "query":
        "select properties.barcode, properties.brand, properties.product_name, distinct_id from events "
        "where event = 'barcode_linked' and timestamp > now() - interval 365 day limit 10000"}}
    req = urllib.request.Request(f"{HOST}/api/projects/{PROJECT}/query/", json.dumps(q).encode(),
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    rows = json.load(urllib.request.urlopen(req))["results"]
    return [dict(barcode=r[0], brand=r[1], product=r[2], who=r[3]) for r in rows]

def csv_events(path):
    out = []
    for r in csv.DictReader(open(path, newline="", encoding="utf-8")):
        g = lambda *k: next((r[x] for x in k if r.get(x)), "")
        out.append(dict(barcode=g("properties.barcode", "barcode"), brand=g("properties.brand", "brand"),
                        product=g("properties.product_name", "product_name"), who=g("distinct_id", "person")))
    return out

events = csv_events(opt("--csv")) if "--csv" in args else fetch_events()
brands = {b["name"].lower(): b for b in json.load(open("data/brands.json"))}
barcodes = json.load(open("data/barcodes.json"))

by_code = defaultdict(list)
for e in events:
    code = "".join(c for c in str(e["barcode"] or "") if c.isdigit())
    if len(code) >= 6 and e["brand"]: by_code[code].append(e)

added, review = 0, []
for code, evs in by_code.items():
    if code in barcodes: continue
    votes = Counter(e["brand"] for e in evs)
    voters = defaultdict(set)
    for e in evs: voters[e["brand"]].add(e["who"])
    top, _ = votes.most_common(1)[0]
    if len(votes) > 1:
        review.append((code, f"visitors disagree: {dict(votes)}")); continue
    if len(voters[top]) < MIN:
        review.append((code, f"only {len(voters[top])} visitor(s) linked it to {top}")); continue
    b = brands.get(top.lower())
    if not b:
        review.append((code, f"brand '{top}' not in brands.json")); continue
    product = next((e["product"] for e in evs if e["product"]), "")
    barcodes[code] = {"brand": b["name"], "product": product, "tier": b["tier"], "note": b.get("note", "")}
    added += 1; print("ADD", code, "->", b["name"])

for code, why in review: print("REVIEW", code, why)
if added and not DRY:
    json.dump(barcodes, open("data/barcodes.json", "w"), indent=2, ensure_ascii=False)
print(f"{added} added" + (" (dry run, nothing written)" if DRY else "") + f", {len(review)} to review")
