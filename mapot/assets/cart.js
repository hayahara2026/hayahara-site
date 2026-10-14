(function(){var K='mapot_cart';function get(){try{return JSON.parse(localStorage.getItem(K))||[]}catch(e){return[]}}function set(c){localStorage.setItem(K,JSON.stringify(c));cnt()}
function cnt(){var n=document.getElementById('cartn');if(n)n.textContent=get().reduce(function(a,i){return a+i.qty},0)}
function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML}
document.addEventListener('DOMContentLoaded',function(){cnt();
var ft=document.getElementById('ft'),fs=document.getElementById('fs');function flt(){document.querySelectorAll('#grid .card').forEach(function(c){c.hidden=(ft.value&&c.dataset.type!==ft.value)||(fs.value&&c.dataset.size!==fs.value)})}
if(ft){ft.onchange=flt;fs.onchange=flt;var u=new URLSearchParams(location.search);if(u.get('type')){ft.value=u.get('type');flt()}}
var add=document.getElementById('add');if(add)add.onclick=function(){var q=parseInt(document.getElementById('q').value,10);if(!(q>=1&&q<=10000))return;var c=get(),s=add.dataset.slug,f=c.find(function(i){return i.slug===s});if(f)f.qty=Math.min(10000,f.qty+q);else c.push({slug:s,name:add.dataset.name,qty:q});set(c);document.getElementById('added').hidden=false};
var form=document.getElementById('orderform');if(!form)return;
function draw(){var c=get(),t=document.getElementById('cart');document.getElementById('empty').hidden=c.length>0;document.getElementById('cartbox').hidden=c.length===0;
t.innerHTML='<tr><th>פריט</th><th>כמות</th><th></th></tr>'+c.map(function(i,k){return '<tr><td>'+esc(i.name)+'</td><td><input type="number" min="1" max="10000" value="'+i.qty+'" data-k="'+k+'"></td><td><button type="button" data-r="'+k+'">הסרה</button></td></tr>'}).join('');
t.querySelectorAll('input').forEach(function(x){x.onchange=function(){var c=get(),v=parseInt(x.value,10);if(v>=1&&v<=10000){c[x.dataset.k].qty=v;set(c)}}});
t.querySelectorAll('button').forEach(function(b){b.onclick=function(){var c=get();c.splice(b.dataset.r,1);set(c);draw()}})}
draw();
form.onsubmit=function(e){e.preventDefault();var err=document.getElementById('err');err.hidden=true;if(!form.checkValidity()){err.textContent='נא למלא איש קשר, טלפון תקין, תאריך אירוע וכתובת למשלוח.';err.hidden=false;return}
var d={};new FormData(form).forEach(function(v,k){d[k]=v});d.items=get().map(function(i){return{slug:i.slug,qty:i.qty}});
var b=form.querySelector('button[type=submit]');b.disabled=true;
fetch('/mapot/api/order',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(d)}).then(function(r){return r.json().then(function(j){return{ok:r.ok,j:j}})}).then(function(r){b.disabled=false;
if(r.ok){localStorage.removeItem(K);cnt();document.getElementById('cartbox').hidden=true;document.getElementById('done').hidden=false}else{err.textContent=r.j.error||'משהו השתבש. אפשר להתקשר: 053-2535393';err.hidden=false}}).catch(function(){b.disabled=false;err.textContent='משהו השתבש. אפשר להתקשר: 053-2535393';err.hidden=false})}})})();
