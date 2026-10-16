/* a home kind: brand suggestions as you type. AHKSuggest('inputId') */
(function(){window.AHKSuggest=function(id){var inp=document.getElementById(id);if(!inp)return;var wrap=inp.closest('form')||inp.parentNode;if(getComputedStyle(wrap).position==='static')wrap.style.position='relative';
var box=document.createElement('div');box.className='ahk-sg';box.id=id+'Sg';box.setAttribute('role','listbox');box.hidden=true;wrap.appendChild(box);
inp.setAttribute('role','combobox');inp.setAttribute('aria-autocomplete','list');inp.setAttribute('aria-controls',box.id);inp.setAttribute('aria-expanded','false');
var L={good:'cruelty-free & vegan',check:'cruelty-free',warn:'owner tests',bad:'tests on animals',unverified:'not certified'};
function nz(s){s=(s||'').toLowerCase();try{s=s.normalize('NFKD').replace(/[\u0300-\u036f]/g,'')}catch(e){}return s.replace(/&/g,'and').replace(/[^a-z0-9 ]/g,'').replace(/\s+/g,' ').trim()}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var list=[],seen={},p=null;
function add(x,own){var k=nz(x[0]);var sk=own?k:k+(x[5]?'|lb':'');if(!k||seen[k]===2||seen[sk])return;seen[sk]=own?2:1;if(own)list.push({n:x[0],k:k,h:'/brands/'+x[1]+'/',t:x[2]});else list.push({n:x[0],k:k,h:x[1]?'/brands/'+x[1]+'/':(x[5]||'https://crueltyfree.peta.org/company/'+x[3]+'/'),t:x[2],ext:!x[1],lb:!!x[5],v:x[4]||0})}
function load(){if(!p)p=fetch('/data/search-own.json').then(function(r){return r.json()}).then(function(d){d.forEach(function(x){add(x,1)})}).catch(function(){}).then(function(){return fetch('/data/search-extra.json')}).then(function(r){return r.json()}).then(function(d){d.forEach(function(x){add(x,0)})}).catch(function(){});return p}
var cur=-1,items=[];
function hl(n,q){if(!q||nz(n).indexOf(q)!==0)return esc(n);var c=0,j=0;while(j<n.length&&c<q.length){c+=nz(n.charAt(j)).length;j++}return '<b>'+esc(n.slice(0,j))+'</b>'+esc(n.slice(j))}
function show(){var q=nz(inp.value);if(!q){close();return}var a=[],b=[];for(var i=0;i<list.length;i++){var k=list[i].k;if(k.indexOf(q)===0)a.push(list[i]);else if((' '+k).indexOf(' '+q)!==-1)b.push(list[i])}
function s(x,y){var ex=(x.ext?1:0)-(y.ext?1:0);if(ex)return ex;var dv=(y.v||0)-(x.v||0);if(dv)return dv;return x.k<y.k?-1:x.k>y.k?1:0}a.sort(s);b.sort(s);items=a.concat(b).slice(0,8);cur=-1;
if(!items.length){close();return}box.innerHTML=items.map(function(x,i){return '<a role="option" id="'+box.id+i+'" href="'+x.h+'"'+(x.ext?' target="_blank" rel="noopener"':'')+'><span>'+hl(x.n,q)+'</span><span class="t '+x.t+'">'+(L[x.t]||'')+(x.ext?(x.lb?' &middot; Leaping Bunny':' &middot; PETA'):'')+'</span></a>'}).join('');box.hidden=false;inp.setAttribute('aria-expanded','true')}
function close(){box.hidden=true;inp.setAttribute('aria-expanded','false');inp.removeAttribute('aria-activedescendant');cur=-1}
function mark(){var as=box.querySelectorAll('a');as.forEach(function(e,i){e.classList.toggle('on',i===cur)});if(cur>=0){inp.setAttribute('aria-activedescendant',box.id+cur);as[cur].scrollIntoView({block:'nearest'})}}
inp.addEventListener('focus',function(){load().then(function(){if(document.activeElement===inp&&inp.value)show()})});
inp.addEventListener('input',function(){if(list.length)show();load().then(show)});
inp.addEventListener('keydown',function(e){if(box.hidden)return;if(e.key==='ArrowDown'){cur=Math.min(cur+1,items.length-1);mark();e.preventDefault()}else if(e.key==='ArrowUp'){cur=Math.max(cur-1,-1);mark();e.preventDefault()}else if(e.key==='Enter'&&cur>=0){e.preventDefault();box.querySelectorAll('a')[cur].click()}else if(e.key==='Escape'){close()}});
document.addEventListener('pointerdown',function(e){if(!wrap.contains(e.target))close()});window.addEventListener('pageshow',close);};})();
