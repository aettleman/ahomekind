#!/usr/bin/env python3
"""Build "The kind list" PDF from data/brands.json.

Usage: python3 build_kind_list.py <brands.json> <out.pdf> [fonts_dir]
Needs Python 3 + Playwright (Chromium). Every page is laid out in HTML,
then paginated in the browser (so long categories flow across pages),
then printed to A4 PDF.
"""
import json, sys, html, datetime, os
from pathlib import Path

src, out = sys.argv[1], sys.argv[2]
fonts = Path(sys.argv[3] if len(sys.argv) > 3 else Path(__file__).parent / 'kind-list-fonts').resolve()
brands = json.load(open(src))
e = html.escape
today = datetime.date.today()
EDITION = today.strftime('%B %Y')
ASOF = f"{today.day} {today.strftime('%b %Y')}"

cf = [b for b in brands if b['tier'] in ('good', 'check')]
good = sorted([b for b in brands if b['tier'] == 'good'], key=lambda b: b['name'].lower())
warn = sorted([b for b in brands if b['tier'] == 'warn'], key=lambda b: b['name'].lower())
notcert = sorted([b for b in brands if b['tier'] == 'unverified'], key=lambda b: b['name'].lower())
CATS = [('skincare', 'Skincare'), ('makeup-beauty', 'Makeup & beauty'), ('haircare', 'Haircare'),
        ('body-shower', 'Body & shower'), ('household-cleaning', 'Household & cleaning'),
        ('laundry', 'Laundry'), ('dental', 'Dental'), ('food-kitchen', 'Food & kitchen'),
        ('period-menstrual', 'Period care')]

def row(b):
    sub = ''
    if b['tier'] == 'check' and b.get('vegan') == 'partial':
        sub = '<small class="vgs">some vegan products</small>'
    return {'t': b['tier'], 'n': b['name'], 's': sub}

def letter(name):
    c = name[0].upper()
    return c if c.isalpha() else '#'

sections = []
small = []
for key, label in CATS:
    items = sorted([b for b in cf if key in (b.get('category') or [])], key=lambda b: b['name'].lower())
    if not items:
        continue
    if len(items) <= 20:
        small.append((label, items)); continue
    rows, cur = [], None
    for b in items:
        L = letter(b['name'])
        if L != cur:
            rows.append({'lt': L}); cur = L
        rows.append(row(b))
    sections.append({'id': key, 'title': label, 'count': len(items), 'rows': rows, 'cols': 3, 'small': len(label) > 16})
if small:
    rows = []
    for label, items in small:
        rows.append({'lt': label.split(' & ')[0] if label.startswith('Food') else label})
        rows += [row(b) for b in items]
    title = 'Laundry, dental, food & more'
    sections.append({'id': 'more', 'title': title, 'count': sum(len(i) for _, i in small), 'rows': rows, 'cols': 3, 'small': True})

owner_rows = [{'t': 'warn', 'n': b['name'], 's': '<small>owned by ' + e(b.get('parentCompany') or 'a company that tests') + '</small>'} for b in warn]
nc_rows = [{'t': 'unverified', 'n': b['name'], 's': ('<small>says it’s cruelty-free</small>' if b.get('claim') else '<small>no certification found</small>')} for b in notcert]

data = {'sections': sections, 'owner': owner_rows, 'notcert': nc_rows}

LEAF = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 18c-1-7 3-12 13-13 .5 9-4 14-11 13.5"/><path d="M6 18c2-3 5-6 8-7.5"/></svg>'
CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>'
ALERT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4 2.8 19.5h18.4L12 4Z"/><path d="M12 10v4.2M12 17.2v.1"/></svg>'
QM = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.2 9a3 3 0 1 1 4.3 2.7c-1 .5-1.5 1.2-1.5 2.3M12 17.5v.1"/></svg>'

good_html = ''.join(f'<li><i class="st st-good">{LEAF}</i><span class="bn">{e(b["name"])}</span></li>' for b in good)

def ff(name, file, w):
    return f"@font-face{{font-family:'{name}';src:url('{(fonts / file).as_uri()}') format('woff2');font-weight:{w};font-style:normal}}"
FONTCSS = ''.join([ff('Gloock', 'gloock-latin-400-normal.woff2', 400), ff('Caveat', 'caveat-latin-600-normal.woff2', 600)]
                  + [ff('Hanken Grotesk', f'hanken-grotesk-latin-{w}-normal.woff2', w) for w in (400, 500, 600, 700)])

PAGE = r'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>The kind list - a home kind</title>
<style>
''' + FONTCSS + r'''
@page{size:A4;margin:0}
:root{--bg:#F4E6DE;--paper:#FBF4EF;--surface:#EFDDD3;--line:#EBDAD1;--text:#5A4550;--muted:#80686F;--ink:#2A1630;--plum:#3A1F3D;
--apricot:#E8804C;--apricot-deep:#C8622F;--apricot-soft:#F6C6A8;--apricot-wash:#FBE3D3;--sage:#7C9A78;--sage-wash:#DCE6D6;--sage-ink:#3f6a3d;--on-dark:#FBF4EF;--on-dark-muted:#D9C3CF}
*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
html,body{margin:0;background:#fff}
body{color:var(--text);font-family:'Hanken Grotesk',sans-serif}
.sheet{width:210mm;height:297mm;container-type:inline-size;background:var(--paper);position:relative;overflow:hidden;break-after:page}
.pg{position:absolute;inset:0;padding:7cqw 7cqw 9cqw;display:flex;flex-direction:column;font-size:2.15cqw;line-height:1.5}
.foot{position:absolute;left:7cqw;right:7cqw;bottom:4.2cqw;display:flex;justify-content:space-between;font-size:1.7cqw;color:var(--muted);letter-spacing:.06em}
.foot b{color:var(--ink);font-weight:600}
.run{display:flex;justify-content:space-between;align-items:baseline;font-size:1.7cqw;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);padding-bottom:2.4cqw;border-bottom:1px solid var(--line);margin-bottom:3.4cqw;flex:0 0 auto}
.run .wm{font-family:'Gloock',serif;letter-spacing:0;text-transform:none;font-size:2.4cqw;color:var(--ink)}
.wm i{font-style:normal;color:var(--apricot)}
.kick{font-size:1.75cqw;letter-spacing:.3em;text-transform:uppercase;color:var(--apricot-deep);font-weight:600;margin:0 0 1.6cqw}
h2{font-family:'Gloock',serif;font-weight:400;color:var(--ink);font-size:6.4cqw;line-height:1.05;margin:0 0 2.4cqw}
.lede{margin:0 0 3.4cqw;color:var(--text)}
.st{display:inline-grid;place-items:center;width:3.1cqw;height:3.1cqw;border-radius:50%;flex:0 0 auto}
.st svg{width:62%;height:62%}
.st-good{background:var(--sage);color:#fff}.st-check{background:var(--sage-wash);color:var(--sage-ink)}
.st-warn{background:var(--apricot-wash);color:#A85523}.st-unverified{background:var(--surface);color:var(--muted)}
.cover{background:var(--plum);color:var(--on-dark)}
.cover .pg{padding:8cqw}
.cover .wm{font-family:'Gloock',serif;font-size:4cqw;color:var(--on-dark)}
.arch{margin:6cqw auto 0;width:58cqw;height:58cqw;background:var(--apricot-soft);border-radius:29cqw 29cqw 3cqw 3cqw;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding-bottom:7cqw;position:relative}
.arch .n{font-family:'Gloock',serif;font-size:20cqw;line-height:.9;color:var(--plum)}
.arch .l{font-size:2.2cqw;letter-spacing:.25em;text-transform:uppercase;color:var(--plum);font-weight:600;margin-top:1.4cqw}
.arch .leaf{position:absolute;top:9cqw;width:9cqw;height:9cqw;color:var(--sage)}
.cover h1{font-family:'Gloock',serif;font-weight:400;font-size:11cqw;line-height:1;margin:6cqw 0 2.4cqw;color:var(--on-dark)}
.cover h1 i{font-style:normal;color:var(--apricot)}
.cover .sub{font-size:2.7cqw;line-height:1.5;color:var(--on-dark-muted);max-width:40ch;margin:0}
.cover .hand{font-family:'Caveat',cursive;font-size:4.8cqw;color:var(--apricot-soft);transform:rotate(-3deg);margin-top:auto}
.cover .ed{display:flex;justify-content:space-between;font-size:1.8cqw;letter-spacing:.14em;text-transform:uppercase;color:var(--on-dark-muted);border-top:1px solid rgba(251,244,239,.2);padding-top:2.6cqw;margin-top:2.6cqw}
.key{display:grid;gap:1.2cqw;margin:0 0 2.4cqw}
.key div{display:grid;grid-template-columns:auto 1fr;gap:2.2cqw;align-items:start;background:var(--bg);border-radius:2.4cqw;padding:1.5cqw 3cqw}
.key .st{width:5cqw;height:5cqw}
.key p{margin:0}.key b{display:block;color:var(--ink);font-size:2.4cqw;font-weight:600}.key span{color:var(--text);font-size:1.95cqw}
.note{background:var(--plum);color:var(--on-dark);border-radius:2.4cqw;padding:2.4cqw 3.4cqw;font-size:1.95cqw;line-height:1.55;margin-bottom:3cqw}
.note b{color:var(--apricot-soft)}
.toc{list-style:none;margin:0;padding:0;columns:2;column-gap:5cqw;font-size:1.9cqw}
.toc li{display:flex;align-items:baseline;gap:1.4cqw;padding:.35cqw 0;break-inside:avoid;font-size:1.9cqw}
.toc li span{color:var(--ink)}.toc li i{flex:1;border-bottom:1px dotted var(--muted);transform:translateY(-.5cqw)}
.toc li b{font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
.toch{font-family:'Gloock',serif;font-size:3.4cqw;color:var(--ink);margin:0 0 1.4cqw}
.band{display:flex;align-items:flex-end;justify-content:space-between;gap:3cqw;background:var(--surface);border-radius:3cqw 3cqw 1.2cqw 1.2cqw;padding:4cqw 4cqw 3.4cqw;margin-bottom:3cqw;flex:0 0 auto}
.band h2{margin:0;font-size:7cqw}.band .kick{margin-bottom:1cqw}
.band .cnt{text-align:right;font-size:1.8cqw;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.band .cnt b{display:block;font-family:'Gloock',serif;font-size:6cqw;letter-spacing:0;color:var(--ink);font-weight:400;line-height:1}
.cols{flex:1 1 auto;display:grid;gap:4cqw;min-height:0}
.cols.c3{grid-template-columns:1fr 1fr 1fr}.cols.c2{grid-template-columns:1fr 1fr}
.cols ul{list-style:none;margin:0;padding:0;overflow:hidden;min-height:0;font-size:1.85cqw}
.cols li{display:flex;align-items:center;gap:1.2cqw;padding:.33cqw 0;color:var(--ink);line-height:1.25}
.cols .st{width:2.4cqw;height:2.4cqw}
.cols .who{display:flex;flex-direction:column}.cols .who small{font-size:1.45cqw;color:var(--muted)}.cols .who small.vgs{color:var(--sage-ink)}
.cols li.lt{font-family:'Gloock',serif;font-size:3.1cqw;color:var(--apricot-deep);padding:1.2cqw 0 .2cqw}
.band.sm h2{font-size:5cqw}
.list{list-style:none;margin:0;padding:0;columns:3;column-gap:4cqw;font-size:2.5cqw}
.list li{display:flex;align-items:center;gap:1.3cqw;padding:.85cqw 0;break-inside:avoid;color:var(--ink)}
.list .st{width:3cqw;height:3cqw}
.cta{margin-top:auto;display:grid;grid-template-columns:1fr 1fr;gap:2.4cqw}
.cta div{background:var(--bg);border-radius:2.4cqw;padding:3cqw}
.cta b{display:block;font-family:'Gloock',serif;font-weight:400;font-size:3cqw;color:var(--ink);margin-bottom:.8cqw}
.cta span{font-size:1.85cqw}.cta .u{display:block;margin-top:1.2cqw;color:var(--apricot-deep);font-weight:600;font-size:1.85cqw}
.sign{font-family:'Caveat',cursive;font-size:4.4cqw;color:var(--apricot-deep);margin:3cqw 0 0}
.why{display:grid;gap:2cqw;margin:0 0 3cqw}
.why p{margin:0;background:var(--bg);border-radius:2.4cqw;padding:2.4cqw 3cqw;font-size:1.95cqw}
.why b{color:var(--ink)}
</style></head><body>

<section class="sheet cover"><div class="pg">
<div class="wm">a home kind<i style="color:var(--apricot)">.</i></div>
<div class="arch"><svg class="leaf" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M6 18c-1-7 3-12 13-13 .5 9-4 14-11 13.5"/><path d="M6 18c2-3 5-6 8-7.5"/></svg>
<div class="n">{{CF}}</div><div class="l">cruelty-free brands</div></div>
<h1>The kind list<i>.</i></h1>
<p class="sub">Every certified cruelty-free brand checked so far, sorted by what you&rsquo;re buying. Free to print, save and share.</p>
<div class="hand">your annoying vegan friend x</div>
<div class="ed"><span>{{EDITION}} edition</span><span>correct as of {{ASOF}}</span></div>
</div></section>

<section class="sheet" id="p-key"><div class="pg">
<div class="run"><span class="wm">a home kind<i>.</i></span><span>how to read this</span></div>
<p class="kick">before you start</p>
<h2>How to read this.</h2>
<div class="key">
<div><i class="st st-good">{{LEAF}}</i><p><b>Cruelty-free &amp; vegan</b><span>Certified cruelty-free, and nothing from animals across the whole range.</span></p></div>
<div><i class="st st-check">{{CHECK}}</i><p><b>Cruelty-free</b><span>Certified cruelty-free. Vegan varies by product, so check the label.</span></p></div>
<div><i class="st st-warn">{{ALERT}}</i><p><b>Owner isn&rsquo;t</b><span>The brand is cruelty-free, but its parent company tests. Listed near the back so you can decide.</span></p></div>
<div><i class="st st-unverified">{{QM}}</i><p><b>Not certified</b><span>Says it&rsquo;s cruelty-free, or there&rsquo;s no evidence either way, but no independent scheme has checked it. Listed at the back.</span></p></div>
</div>
<div class="note"><b>Certified means</b> checked by Leaping Bunny / Cruelty Free International or PETA. <b>Not in here:</b> brands that test on animals, or sell where it&rsquo;s legally required. Look any brand up, or scan a barcode, at ahomekind.com.</div>
<p class="toch">Contents</p>
<ul class="toc" id="toc"></ul>
</div></section>

<section class="sheet" data-sec="good"><div class="pg">
<div class="run"><span class="wm">a home kind<i>.</i></span><span>start here</span></div>
<p class="kick">start here</p>
<h2>The fully vegan {{NG}}.</h2>
<p class="lede">If you only keep one page, keep this one. Certified cruelty-free, and nothing from animals across everything they make.</p>
<ul class="list">{{GOOD}}</ul>
</div></section>

<div id="flow"></div>

<section class="sheet back" data-sec="back"><div class="pg">
<div class="run"><span class="wm">a home kind<i>.</i></span><span>keep checking</span></div>
<p class="kick">why certified</p>
<h2>Why only certified brands?</h2>
<div class="why">
<p><b>Anyone can print &ldquo;cruelty-free&rdquo; on a pack.</b> There&rsquo;s no UK law defining it, so the word on its own doesn&rsquo;t mean anyone has checked.</p>
<p><b>Certification is how you know.</b> Leaping Bunny / Cruelty Free International and PETA check the brand&rsquo;s whole supply chain, and getting listed costs a brand nothing.</p>
<p><b>So if a brand isn&rsquo;t certified, it isn&rsquo;t on the cruelty-free pages here</b>, however kind its marketing sounds. You&rsquo;d be taking their word for it.</p>
</div>
<div class="cta">
<div><b>Not on the list?</b><span>Search any brand, or scan the barcode while you&rsquo;re in the shop.</span><span class="u">ahomekind.com</span></div>
<div><b>A new edition every month.</b><span>Brands are added and rechecked all the time. The latest list always lives at the same link.</span><span class="u">ahomekind.com/downloads/the-kind-list.pdf</span></div>
</div>
<p class="sign">your annoying vegan friend, Ash x</p>
</div></section>

<script>
var DATA = {{DATA}};
var ICON = {good:'{{LEAF}}', check:'{{CHECK}}', warn:'{{ALERT}}', unverified:'{{QM}}'};
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')}
var flow = document.getElementById('flow');
function li(r){
  if (r.lt) return '<li class="lt">' + r.lt + '</li>';
  var name = r.s ? '<span class="who">' + esc(r.n) + r.s + '</span>' : '<span>' + esc(r.n) + '</span>';
  return '<li><i class="st st-' + r.t + '">' + ICON[r.t] + '</i>' + name + '</li>';
}
function newPage(sec, first, runLabel){
  var s = document.createElement('section'); s.className = 'sheet'; s.dataset.sec = sec.id;
  var h = '<div class="pg"><div class="run"><span class="wm">a home kind<i>.</i></span><span>' + runLabel + (first ? '' : ', continued') + '</span></div>';
  if (first) h += sec.head;
  h += '<div class="cols c' + sec.cols + '">' + new Array(sec.cols + 1).join('<ul></ul>') + '</div></div>';
  s.innerHTML = h; flow.appendChild(s);
  return Array.prototype.slice.call(s.querySelectorAll('.cols ul'));
}
function paginate(sec, rows, runLabel){
  var cols = newPage(sec, true, runLabel), c = 0;
  rows.forEach(function(r){
    var tmp = document.createElement('div'); tmp.innerHTML = li(r); var el = tmp.firstChild;
    cols[c].appendChild(el);
    while (cols[c].scrollHeight > cols[c].clientHeight + 1) {
      cols[c].removeChild(el);
      // never leave a letter heading stranded at the bottom of a column
      var carry = [];
      var last = cols[c].lastElementChild;
      if (last && last.classList.contains('lt')) { cols[c].removeChild(last); carry.push(last); }
      c++;
      if (c >= cols.length) { cols = newPage(sec, false, runLabel); c = 0; }
      carry.forEach(function(x){ cols[c].appendChild(x); });
      cols[c].appendChild(el);
    }
  });
}
Promise.all(["400 10px 'Gloock'","400 10px 'Hanken Grotesk'","500 10px 'Hanken Grotesk'","600 10px 'Hanken Grotesk'","600 10px 'Caveat'"].map(function(f){ return document.fonts.load(f); })).then(function(){
DATA.sections.forEach(function(sec){
  sec.head = '<div class="band' + (sec.small ? ' sm' : '') + '"><div><p class="kick">by category</p><h2>' + esc(sec.title) + '</h2></div><div class="cnt"><b>' + sec.count + '</b>brands</div></div>';
  paginate(sec, sec.rows, esc(sec.title).toLowerCase());
});
var own = {id:'owner', title:"When the owner isn’t", cols:2, head:'<p class="kick">worth knowing</p><h2>When the owner isn’t.</h2><p class="lede">These ' + DATA.owner.length + ' brands are cruelty-free themselves, but the company that owns them tests on animals. Buying them is still better than buying a tested brand. Where your money ends up is your call.</p>'};
paginate(own, DATA.owner, 'when the owner isn’t');
var nc = {id:'notcert', title:'Not certified', cols:2, head:'<p class="kick">buy at your own risk</p><h2>Not certified.</h2><p class="lede">These ' + DATA.notcert.length + ' brands aren’t certified by Leaping Bunny, Cruelty Free International or PETA. Some say they’re cruelty-free; for others there’s no evidence either way. Until one of those schemes checks them, a home kind can’t call them cruelty-free.</p>'};
paginate(nc, DATA.notcert, 'not certified');

// page numbers + contents
var sheets = Array.prototype.slice.call(document.querySelectorAll('.sheet'));
var firstPage = {};
sheets.forEach(function(s, i){
  var n = i + 1;
  if (s.dataset.sec && !(s.dataset.sec in firstPage)) firstPage[s.dataset.sec] = n;
  if (i > 0) { var f = document.createElement('div'); f.className = 'foot'; f.innerHTML = '<span>ahomekind.com</span><b>' + n + '</b>'; s.firstChild.appendChild(f); }
});
var toc = [['The fully vegan {{NG}}', 'good']];
DATA.sections.forEach(function(sec){ toc.push([sec.title, sec.id]); });
toc.push(["When the owner isn’t", 'owner'], ['Not certified', 'notcert'], ['Why only certified brands?', 'back']);
document.getElementById('toc').innerHTML = toc.map(function(t){ return '<li><span>' + esc(t[0]) + '</span><i></i><b>' + firstPage[t[1]] + '</b></li>'; }).join('');
document.body.dataset.pages = sheets.length;
document.body.dataset.ready = '1';
});
</script>
</body></html>'''

page = (PAGE.replace('{{CF}}', str(len(cf))).replace('{{NG}}', str(len(good))).replace('{{EDITION}}', EDITION)
        .replace('{{ASOF}}', ASOF).replace('{{GOOD}}', good_html).replace('{{DATA}}', json.dumps(data))
        .replace('{{LEAF}}', LEAF).replace('{{CHECK}}', CHECK).replace('{{ALERT}}', ALERT).replace('{{QM}}', QM))
html_path = Path(out).with_suffix('.html')
html_path.write_text(page)

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto(html_path.resolve().as_uri())
    pg.wait_for_function('document.body.dataset.ready === "1"')
    pg.evaluate('document.fonts.ready')
    pages = pg.evaluate('document.body.dataset.pages')
    pg.pdf(path=out, format='A4', print_background=True, margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
    b.close()
print(f'{out}: {pages} pages, {len(cf)} cruelty-free brands, edition {EDITION}')
