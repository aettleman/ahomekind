import json, copy, datetime
P = "data/brands.json"
raw = json.load(open(P)); brands = raw["brands"] if isinstance(raw, dict) else raw
by = {b["slug"]: b for b in brands}
today = datetime.date.today().isoformat()
# --- Daise: certified by Cruelty Free International, vegan varies by product ---
d = next((b for b in brands if b.get("name", "").strip().lower() in ("daise", "daisy")), None)
if d:
    link = {"url": "https://crueltyfreeinternational.org/approved-brands/listing/daise/", "label": "Cruelty Free International"}
    old = [l for l in d.get("links", []) if "crueltyfreeinternational" not in l.get("url", "")]
    d.update(tier="check", vegan="partial", veganConfidence="medium", claim="", evidence="", lastVerified=today,
             note="Certified cruelty-free by Cruelty Free International (Leaping Bunny). Not every product is vegan, so vegan varies by product.",
             links=[link] + old)
    print("Updated:", d["name"])
else:
    print("Daise not found by name")
# --- r.e.m. beauty (its own brand, separate from Ariana Grande Fragrances) ---
if "rem-beauty" not in by and "zoflora" in by:
    regions = {b.get("region") for b in brands if b.get("region")}
    na = [r for r in regions if "america" in r.lower()]
    e = copy.deepcopy(by["zoflora"])
    e.update(slug="rem-beauty", name="r.e.m. beauty", tier="check", vegan="unclear", veganConfidence="low",
             region=na[0] if na else e.get("region"), price="££", claim="", evidence="", parentCompany=None,
             products=[], alternatives=[], category=[], lastVerified=today,
             note="PETA lists r.e.m. beauty as cruelty-free and says its products contain no beeswax, carmine, lanolin or collagen. This is the makeup brand only, not Ariana Grande's fragrances.",
             links=[{"url": "https://www.peta.org/lifestyle/personal-care-fashion/rem-beauty-ariana-grande/", "label": "PETA"}])
    brands.append(e); print("Added: r.e.m. beauty")
json.dump(raw, open(P, "w"), indent=2, ensure_ascii=False); open(P, "a").write("\n")
