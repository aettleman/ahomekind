import json, copy, datetime
P = 'data/brands.json'
raw = json.load(open(P)); wrap = isinstance(raw, dict)
brands = raw['brands'] if wrap else raw
by = {b['slug']: b for b in brands}
z = by['zoflora']
regions = {b.get('region') for b in brands if b.get('region')}
na = [r for r in regions if 'america' in r.lower()]
us = na[0] if na else z.get('region', 'Europe')
uk = by['ann-summers'].get('region', z.get('region', 'Europe')) if 'ann-summers' in by else z.get('region', 'Europe')
today = datetime.date.today().isoformat()
def L(u, t): return [{"url": u, "label": t}]
NEW = [
 dict(slug='billie-eilish-fragrances', name='Billie Eilish Fragrances', tier='good', vegan='full', veganConfidence='medium', region=us,
  claim='Cruelty-free and vegan, listed by PETA.', note="PETA lists Billie Eilish's fragrance brand, Eilish, as cruelty-free and vegan.",
  links=L('https://www.peta.org/living/personal-care-fashion/billie-eilish-fragrance/', 'Source: PETA')),
 dict(slug='ariana-grande-fragrances', name='Ariana Grande Fragrances', tier='unverified', vegan='unclear', veganConfidence='low', region=us,
  claim='Reported cruelty-free and vegan, not confirmed.', note="Ariana Grande Fragrances was reported as Leaping Bunny certified in 2021 and its perfumes are described as vegan, but I couldn't confirm that it is still certified, so I've listed it as not certified for now.",
  links=L('https://www.crueltyfreekitty.com/?p=23296', 'Source: Cruelty-Free Kitty (2021)')),
 dict(slug='stella-mccartney-fragrances', name='Stella McCartney fragrances', tier='unverified', vegan='full', veganConfidence='low', region=uk,
  claim="Says it's cruelty-free and vegan, not certified.", note="Stella McCartney says its fragrances are never tested on animals and are vegan, and it doesn't sell them in China. It isn't certified by Leaping Bunny or PETA. The fragrances are made under licence by P&G Prestige.",
  links=L('https://www.crueltyfreekitty.com/?p=23384', 'Source: Cruelty-Free Kitty')),
 dict(slug='marc-jacobs-fragrances', name='Marc Jacobs fragrances', tier='bad', vegan='unclear', veganConfidence='low', region=us,
  claim='Fragrance licence held by Coty, which sells in China.', note="Marc Jacobs fragrances are made under licence by Coty, which sells in mainland China, where animal testing can be required by law. Marc Jacobs Beauty (makeup) is a separate company.",
  links=L('https://www.crueltyfreekitty.com/?p=5548', 'Source: Cruelty-Free Kitty (older source)')),
 dict(slug='ted-baker', name='Ted Baker', tier='good', vegan='unclear', veganConfidence='low', region=uk,
  claim='Listed by PETA as cruelty-free.', note="PETA Germany lists Ted Baker as cruelty-free. I couldn't find a vegan claim, so vegan is unclear.",
  links=L('https://tierversuchsfrei.peta-approved.de/company/ted-baker/', 'Source: PETA Germany (in German)')),
]
added = []
for n in NEW:
    if n['slug'] in by: continue
    e = copy.deepcopy(z); e.update(n)
    e.update(parentCompany=None, evidence='', products=[], alternatives=[], category=[], lastVerified=today)
    brands.append(e); added.append(n['slug'])
json.dump(raw, open(P, 'w'), indent=2, ensure_ascii=False); open(P, 'a').write('\n')
print('Added:', added or 'none (already there)')
