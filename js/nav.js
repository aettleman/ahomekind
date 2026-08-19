document.addEventListener('DOMContentLoaded', function(){
var dds = document.querySelectorAll('nav.main-nav .dd');
dds.forEach(function(dd){
var toggle = function(e){
if(e.target.closest('.dd-m')) return;
e.preventDefault();
var wasOpen = dd.classList.contains('open');
dds.forEach(function(other){ other.classList.remove('open'); });
if(!wasOpen){ dd.classList.add('open'); }
};
dd.addEventListener('click', toggle);
});
document.addEventListener('click', function(e){
if(!e.target.closest('nav.main-nav .dd')){
dds.forEach(function(dd){ dd.classList.remove('open'); });
}
});
});
