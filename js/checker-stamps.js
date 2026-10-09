(function(){
  function norm(s){return (s||"").normalize("NFKD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/&/g,"and").replace(/[^a-z0-9]/g,"");}
  var brands=null,goy={};
  function rules(b){var t=b.tier,n=(b.note||"")+" "+(b.claim||""),o={};
    if(t==="unverified")o.unk=1; if(t==="bad")o.ncf=1; if(b.vegan==="full")o.vegan=1;
    if((t==="good"||t==="check"||t==="warn")&&/Leaping Bunny|Cruelty Free International/.test(n))o.lb=1;
    if((t==="good"||t==="check"||t==="warn")&&/PETA/.test(n))o.peta=1;
    if(goy[b.slug])o.goy=goy[b.slug]; return o;}
  function find(card){
    var hs=card.querySelectorAll(".rcard-name,h1,h2,h3,h4,.rr-name,.rname,strong"),i,k;
    for(i=0;i<hs.length;i++){k=norm(hs[i].textContent);if(k&&brands[k])return {b:brands[k],el:hs[i]};}
    return null;}
  function deco(c){
    if(c.getAttribute("data-ahk"))return; var f=find(c); if(!f)return; c.setAttribute("data-ahk","1");
    var d=document.createElement("div"); d.innerHTML=AHKStamps.row(rules(f.b));
    var t=f.el.closest("a")||f.el,r=d.firstChild;r.style.margin="0 16px 12px";t.parentNode.insertBefore(r,t.nextSibling);}
  var io=window.IntersectionObserver?new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){io.unobserve(e.target);deco(e.target);}});},{rootMargin:"300px"}):null;
  function run(){
    if(!brands||!window.AHKStamps)return;
    document.querySelectorAll(".rcard:not([data-ahk-o]),.card:not([data-ahk-o])").forEach(function(c){
      c.setAttribute("data-ahk-o","1"); if(io)io.observe(c); else deco(c);});}
  Promise.all([fetch("data/brands.json").then(function(r){return r.json()}),
    fetch("data/good-on-you.json").then(function(r){return r.ok?r.json():{}}).catch(function(){return{}})]).then(function(a){
    var l=Array.isArray(a[0])?a[0]:a[0].brands; brands={}; l.forEach(function(b){brands[norm(b.name)]=b;});
    Object.keys(a[1]).forEach(function(k){if(k[0]!=="_")goy[k]=a[1][k];});
    new MutationObserver(run).observe(document.body,{childList:true,subtree:true}); run();
  }).catch(function(){});
})();
