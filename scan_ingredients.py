#!/usr/bin/env python3
"""The scanner already reads ingredients when the barcode database has them.
Two things were missing: the way in was below the fold on a phone, and when
a product came back without an ingredients list nothing offered the camera
route instead."""
import re

t = open("scan.html", encoding="utf-8").read()

# 1. the two pills move above the manual entry, so they're on screen without
#    scrolling on a phone rather than tucked under the barcode field
links = re.search(r'<div class="scan-shell-links">.*?</div>\s*\n', t, re.S)
assert links, "shell links not found"
block = links.group(0)
t = t[:links.start()] + t[links.end():]
anchor = '<p class="scan-or">or</p>'
assert anchor in t
t = t.replace(anchor, block + anchor, 1)

# 2. a product with no ingredients list on file: say so, and offer the camera
old = 'if(product.ingredients_text) out += "<div id=\\"ingredientWatch\\"></div>";'
new = ('if(product.ingredients_text) out += "<div id=\\"ingredientWatch\\"></div>";\n'
       'else out += "<p class=\\"rcard-note\\" style=\\"margin-top:10px;\\">No ingredients list on file for this one, so I can\'t say whether it\'s vegan. '
       '<a href=\\"ingredient-check.html\\">Photograph the label</a> and I\'ll read it directly.</p>";')
assert old in t
t = t.replace(old, new, 1)
open("scan.html", "w", encoding="utf-8").write(t)
print("scan.html: ways in moved above the fold, missing-ingredients case handled")

# 3. brand check is the other place people arrive with a bottle in hand
b = open("brand-check.html", encoding="utf-8").read()
if 'class="xlink ic-from-brand"' not in b:
    m = re.search(r'<p class="hero-lede">.*?</p>\n', b, re.S)
    assert m, "brand check lede not found"
    add = ('<p class="xlink ic-from-brand"><a href="ingredient-check.html">checking a specific product rather than the brand? '
           'read its ingredients list &rarr;</a></p>\n')
    b = b[:m.end()] + add + b[m.end():]
    open("brand-check.html", "w", encoding="utf-8").write(b)
    print("brand-check.html: link to the ingredient checker added under the intro")

sw = open("sw.js", encoding="utf-8").read()
mm = re.search(r"CACHE_VERSION\s*=\s*'([^']*?)v(\d+)'", sw)
if mm:
    v = int(mm.group(2)) + 1
    open("sw.js", "w", encoding="utf-8").write(sw[:mm.start()] + "CACHE_VERSION = '%sv%d'" % (mm.group(1), v) + sw[mm.end():])
    print("cache version -> v%d" % v)
