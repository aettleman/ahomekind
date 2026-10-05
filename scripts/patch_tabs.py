import re,sys
p='shop.html'; s=open(p).read()
assert 'k-stabs' not in s, 'already patched'
tabs='''<div class="k-stabs" role="tablist" aria-label="Shop sections">
<button type="button" role="tab" class="on" data-panel="hk" aria-selected="true">a home kind collection</button>
<button type="button" role="tab" class="lou" data-panel="lou" aria-selected="false">Lou Lawrence collection</button>
<button type="button" role="tab" data-panel="picks" aria-selected="false">Cruelty-free picks</button>
</div>
'''
s=s.replace('<main class="page-shell k-page" id="main">\n','<main class="page-shell k-page" id="main">\n'+tabs,1)
s=s.replace('<section class="k-merch" aria-label="The collection">','<section class="k-merch k-spanel" id="panel-hk" role="tabpanel" aria-label="a home kind collection">',1)
lou='''<section class="k-spanel k-lou" id="panel-lou" role="tabpanel" aria-label="Lou Lawrence collection" hidden>
<div class="k-lou-head"><span class="k-lou-port" aria-hidden="true">LL</span><div><h2>Lou Lawrence collection</h2><span class="k-lou-soon">coming soon</span></div></div>
<p class="k-lou-hand">warm characters from everyday moments</p>
<p class="k-lou-sub">Original artwork by illustrator Lou Lawrence, printed on organic cotton.</p>
<a class="k-lou-btn" href="https://loulawrence.com" target="_blank" rel="noopener">See more of Lou's work <span aria-hidden="true">&rarr;</span></a>
</section>
'''
i=s.index('</section>\n<div class="k-shop-head">')+len('</section>\n')
s=s[:i]+lou+'<div class="k-spanel" id="panel-picks" role="tabpanel" aria-label="Cruelty-free picks" hidden>\n'+s[i:]
s=s.replace('earn me a commission, at no extra cost to you.</p>\n</main>','earn me a commission, at no extra cost to you.</p>\n</div>\n</main>',1)
assert s.count('id="panel-picks"')==1 and '</div>\n</main>' in s
js='''<script>
(function(){
  var btns=document.querySelectorAll('.k-stabs button');
  function show(id){
    btns.forEach(function(b){ var on=b.dataset.panel===id; b.classList.toggle('on',on); b.setAttribute('aria-selected',on?'true':'false'); });
    ['hk','lou','picks'].forEach(function(k){ var el=document.getElementById('panel-'+k); if(el) el.hidden=(k!==id); });
  }
  btns.forEach(function(b){ b.addEventListener('click',function(){ show(b.dataset.panel); history.replaceState(null,'',b.dataset.panel==='hk'?location.pathname:'#'+b.dataset.panel); }); });
  var h=location.hash.replace('#','');
  if(/[?&]category=/.test(location.search)) h='picks';
  if(h==='lou'||h==='picks') show(h);
})();
</script>
'''
s=s.replace('</body>',js+'</body>',1)
s=re.sub(r'css/app\.css\?v=\d+','css/app.css?v=15',s)
open(p,'w').write(s)
c=open('css/app.css').read()
assert '.k-stabs' not in c
c+='''
/* shop tabs: a home kind / Lou Lawrence / cruelty-free picks */
.k-stabs { display: flex; gap: 4px; background: #EAD5CB; border-radius: 16px; padding: 4px; margin: 8px 0 18px; }
.k-stabs button { flex: 1; border: 0; background: none; font: 700 12.5px/1.2 'Hanken Grotesk', sans-serif; color: #5A4550; padding: 11px 6px; border-radius: 12px; cursor: pointer; }
.k-stabs button.on { background: #3A1F3D; color: #FBF4EF; }
.k-stabs button.lou.on { background: #6E4E78; }
.k-stabs button:focus-visible { outline: 2px solid #E8804C; outline-offset: 2px; }
.k-spanel[hidden] { display: none !important; }
.k-lou { background: #EFE3F1; border-radius: 22px; padding: 22px 18px 24px; }
.k-lou-head { display: flex; gap: 14px; align-items: center; }
.k-lou-port { width: 60px; height: 60px; border-radius: 50%; background: #DCC7E0; color: #6E4E78; font: 400 22px 'Gloock', serif; display: flex; align-items: center; justify-content: center; flex: none; }
.k-lou h2 { font: 400 26px/1.1 'Gloock', serif; margin: 0; color: #2A1630; }
.k-lou-soon { display: inline-block; margin-top: 8px; background: #6E4E78; color: #FBF4EF; font: 700 10.5px 'Hanken Grotesk', sans-serif; letter-spacing: .08em; text-transform: uppercase; padding: 5px 10px; border-radius: 99px; }
.k-lou-hand { font: 700 23px 'Caveat', cursive; color: #C8622F; margin: 14px 0 0; }
.k-lou-sub { font-size: 14px; color: #5A4550; margin: 4px 0 0; }
.k-lou-btn { display: inline-block; margin-top: 18px; background: #6E4E78; color: #FBF4EF; font-weight: 700; font-size: 15px; padding: 13px 26px; border-radius: 99px; text-decoration: none; }
@media (min-width: 900px) {
  .k-stabs { max-width: 660px; margin: 14px auto 28px; }
  .k-stabs button { font-size: 15px; padding: 13px 8px; }
  .k-lou { padding: 40px 44px; }
  .k-lou-port { width: 84px; height: 84px; font-size: 30px; }
  .k-lou h2 { font-size: 36px; } .k-lou-hand { font-size: 28px; } .k-lou-sub { font-size: 16px; }
}
'''
open('css/app.css','w').write(c)
print('patched')
