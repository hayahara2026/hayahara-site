(function(){
 var K='mapot_cart_v2';
 function get(){try{return JSON.parse(localStorage.getItem(K))||[]}catch(e){return[]}}
 function set(c){localStorage.setItem(K,JSON.stringify(c));cnt()}
 function esc(s){var d=document.createElement('div');d.textContent=s==null?'':String(s);return d.innerHTML}
 function cnt(){
  var n=document.getElementById('cartn');
  var total=get().reduce(function(a,i){return a+(i.qty||0)},0);
  if(n)n.textContent=String(total);
 }
 function selectedSwatch(){return document.querySelector('.swatch[aria-checked="true"]')}
 function clampQty(v,min,max){v=parseInt(v,10);if(!(v>=min))v=min;if(v>max)v=max;return v}

 function bindMenu(){
  var toggle=document.getElementById('navtoggle'),nav=document.getElementById('sitenav');
  if(!toggle||!nav)return;
  toggle.addEventListener('click',function(){
   var open=nav.classList.toggle('open');
   toggle.setAttribute('aria-expanded',open?'true':'false');
   toggle.textContent=open?'סגירה':'תפריט';
   document.body.classList.toggle('nav-open',open);
  });
 }

 function bindFilters(){
  var root=document.getElementById('filters');
  var grid=document.getElementById('grid');
  if(!root||!grid)return;
  var lock=root.dataset.lock||'';
  var state={type:lock,size:'',fabric:'',color:''};
  var params=new URLSearchParams(location.search);
  ['size','fabric','color'].forEach(function(k){if(params.get(k))state[k]=params.get(k)});
  if(!lock&&params.get('type'))state.type=params.get('type');

  function paint(){
   root.querySelectorAll('[data-filter]').forEach(function(b){
    var on=(state[b.dataset.filter]||'')===b.dataset.value;
    b.setAttribute('aria-pressed',on?'true':'false');
   });
   var n=0,active=0;
   ['size','fabric','color'].forEach(function(k){if(state[k])active++});
   if(!lock&&state.type)active++;
   grid.querySelectorAll('.item').forEach(function(el){
    var ok=true;
    if(state.type&&el.dataset.type!==state.type)ok=false;
    if(state.size&&el.dataset.size!==state.size)ok=false;
    if(state.fabric&&el.dataset.fabric!==state.fabric)ok=false;
    if(state.color&&el.dataset.colors.split(/\s+/).indexOf(state.color)<0)ok=false;
    el.hidden=!ok;
    if(ok)n++;
   });
   var live=document.getElementById('resultn');
   if(live)live.textContent=n?(n===1?'פריט אחד':n+' פריטים'):'לבחירה הזו אין פריטים';
   var empty=document.getElementById('emptyf');
   if(empty)empty.hidden=n>0;
   var open=document.getElementById('openf');
   if(open)open.textContent=active?('סינון · '+active):'סינון';
   var q=new URLSearchParams();
   if(!lock&&state.type)q.set('type',state.type);
   if(state.size)q.set('size',state.size);
   if(state.fabric)q.set('fabric',state.fabric);
   if(state.color)q.set('color',state.color);
   var next=q.toString();
   history.replaceState(null,'',next?('?'+next):location.pathname);
  }
  root.addEventListener('click',function(e){
   var b=e.target.closest('[data-filter]');
   if(!b||!root.contains(b))return;
   var k=b.dataset.filter,v=b.dataset.value;
   state[k]=state[k]===v?'':v;
   if(lock)state.type=lock;
   paint();
  });
  var reset=document.getElementById('resetf');
  if(reset)reset.addEventListener('click',function(){
   state={type:lock,size:'',fabric:'',color:''};
   paint();
  });
  var panel=document.getElementById('filterpanel');
  var opener=document.getElementById('openf');
  var closer=document.getElementById('closef');
  function setOpen(on){
   if(!panel)return;
   panel.classList.toggle('open',on);
   if(opener)opener.setAttribute('aria-expanded',on?'true':'false');
   document.body.classList.toggle('filters-open',on);
   var desktop=window.matchMedia('(min-width:960px)').matches;
   panel.inert=!desktop&&!on;
   if(on&&closer)closer.focus();
  }
  if(opener)opener.addEventListener('click',function(){setOpen(true)});
  if(closer)closer.addEventListener('click',function(){setOpen(false)});
  document.addEventListener('keydown',function(e){
   if(e.key==='Escape'&&panel&&panel.classList.contains('open'))setOpen(false);
  });
  var mq=window.matchMedia('(min-width:960px)');
  function syncInert(){if(panel)panel.inert=!mq.matches&&!panel.classList.contains('open')}
  if(mq.addEventListener)mq.addEventListener('change',syncInert);
  syncInert();
  paint();
 }

 function bindProduct(){
  var add=document.getElementById('add');
  if(!add)return;
  var q=document.getElementById('q');
  var min=parseInt(add.dataset.min||'1',10)||1;
  var max=10000;
  function curMax(){var m=parseInt(q&&q.max,10);return m>=1?m:max}
  document.querySelectorAll('.swatch').forEach(function(b){
   b.addEventListener('click',function(){
    document.querySelectorAll('.swatch').forEach(function(x){x.setAttribute('aria-checked','false')});
    b.setAttribute('aria-checked','true');
    var stage=document.getElementById('stage');
    if(stage)stage.style.setProperty('--cloth',b.dataset.hex);
    var name=document.getElementById('cname');
    if(name)name.textContent=b.dataset.name;
    refreshAvail();
   });
  });
  var dec=document.getElementById('qdec'),inc=document.getElementById('qinc');
  if(dec)dec.addEventListener('click',function(){if(q)q.value=clampQty((parseInt(q.value,10)||min)-1,min,curMax())});
  if(inc)inc.addEventListener('click',function(){if(q)q.value=clampQty((parseInt(q.value,10)||min)+1,min,curMax())});
  function addOne(){
   var qty=clampQty(q?q.value:1,min,curMax());
   if(q)q.value=qty;
   var sw=selectedSwatch();
   var needs=add.dataset.needsColor==='1';
   if(needs&&!sw)return;
   var color=sw?sw.dataset.color:'';
   var colorName=sw?sw.dataset.name:'';
   var colorHex=sw?sw.dataset.hex:'';
   var c=get();
   var f=c.find(function(i){return i.sku===add.dataset.sku&&(i.color||'')===color});
   if(f)f.qty=Math.min(curMax(),f.qty+qty);
   else c.push({sku:add.dataset.sku,name:add.dataset.name,color:color,colorName:colorName,colorHex:colorHex,qty:qty});
   set(c);
   var note=document.getElementById('added');
   if(note){note.hidden=false}
  }
  add.addEventListener('click',addOne);
  var dock=document.getElementById('adddock');
  if(dock)dock.addEventListener('click',addOne);
  refreshAvail();
 }

 function refreshAvail(){
  if(document.documentElement.dataset.avail!=='1')return;
  var add=document.getElementById('add');
  var note=document.getElementById('availnote');
  var input=document.getElementById('q');
  if(!add)return;
  var sw=selectedSwatch();
  var qs=new URLSearchParams({sku:add.dataset.sku});
  if(sw&&sw.dataset.color)qs.set('color',sw.dataset.color);
  fetch('/mapot/api/availability?'+qs.toString()).then(function(r){return r.json()}).then(function(j){
   if(!j||j.available==null||typeof j.available!=='number'){
    if(note)note.textContent='';
    if(input)input.max=10000;
    return;
   }
   if(note)note.textContent='ניתן להזמין עד '+j.available;
   if(input){
    input.max=String(j.available);
    if(parseInt(input.value,10)>j.available)input.value=String(j.available);
   }
  }).catch(function(){if(note)note.textContent=''});
 }

 function drawCart(){
  var form=document.getElementById('orderform');
  if(!form)return;
  var c=get();
  var empty=document.getElementById('empty');
  var box=document.getElementById('cartbox');
  var t=document.getElementById('lines');
  if(empty)empty.hidden=c.length>0;
  if(box)box.hidden=c.length===0;
  if(!t)return;
  t.innerHTML=c.map(function(i,k){
   var dot=i.colorHex?'<span class="linedot" style="--sw:'+esc(i.colorHex)+'" aria-hidden="true"></span>':'';
   var col=i.colorName?'<span class="linecolor">'+esc(i.colorName)+'</span>':'';
   return '<tr><td>'+dot+'<span class="linename">'+esc(i.name)+'</span>'+col+'</td>'
    +'<td><div class="stepper"><button type="button" data-dec="'+k+'" aria-label="הפחתת כמות">−</button>'
    +'<input type="number" min="1" max="10000" value="'+i.qty+'" data-k="'+k+'" aria-label="כמות">'
    +'<button type="button" data-inc="'+k+'" aria-label="הגדלת כמות">+</button></div></td>'
    +'<td><button type="button" data-r="'+k+'">הסרה</button></td></tr>';
  }).join('');
  t.querySelectorAll('input').forEach(function(x){
   x.addEventListener('change',function(){
    var cart=get(),v=parseInt(x.value,10);
    if(v>=1&&v<=10000){cart[x.dataset.k].qty=v;set(cart);drawCart()}
   });
  });
  t.querySelectorAll('[data-r]').forEach(function(b){
   b.addEventListener('click',function(){var cart=get();cart.splice(+b.dataset.r,1);set(cart);drawCart()});
  });
  t.querySelectorAll('[data-dec]').forEach(function(b){
   b.addEventListener('click',function(){var cart=get(),i=cart[+b.dataset.dec];if(i.qty>1){i.qty--;set(cart);drawCart()}});
  });
  t.querySelectorAll('[data-inc]').forEach(function(b){
   b.addEventListener('click',function(){var cart=get(),i=cart[+b.dataset.inc];if(i.qty<10000){i.qty++;set(cart);drawCart()}});
  });
 }

 function syncDate(){
  var day=document.getElementById('f-day');
  var month=document.getElementById('f-month');
  var year=document.getElementById('f-year');
  var hidden=document.getElementById('f-event_date');
  if(!hidden)return;
  var iso='';
  if(day&&month&&year&&day.value&&month.value&&year.value){
   iso=year.value+'-'+month.value+'-'+day.value;
   var dt=new Date(iso+'T00:00:00');
   var real=dt.getFullYear()===+year.value&&(dt.getMonth()+1)===+month.value&&dt.getDate()===+day.value;
   if(!real)iso='';
  }
  hidden.value=iso;
  if(hidden.setCustomValidity)hidden.setCustomValidity(iso?'':'תאריך האירוע');
 }

 function bindOrder(){
  var form=document.getElementById('orderform');
  if(!form)return;
  drawCart();
  ['f-day','f-month','f-year'].forEach(function(id){
   var el=document.getElementById(id);
   if(el)el.addEventListener('change',syncDate);
  });
  form.addEventListener('submit',function(e){
   e.preventDefault();
   var err=document.getElementById('err');
   err.hidden=true;
   syncDate();
   if(!get().length){err.textContent='הסל מחכה לפריט הראשון.';err.hidden=false;return}
   if(!form.checkValidity()){err.textContent='נא למלא איש קשר, טלפון תקין, תאריך אירוע וכתובת למשלוח.';err.hidden=false;return}
   var d={};
   new FormData(form).forEach(function(v,k){d[k]=v});
   d.items=get().map(function(i){return{sku:i.sku,color:i.color||'',qty:i.qty}});
   var b=form.querySelector('button[type=submit]');
   b.disabled=true;
   fetch('/mapot/api/order',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(d)})
    .then(function(r){return r.json().then(function(j){return{ok:r.ok,j:j}})})
    .then(function(r){
     b.disabled=false;
     if(r.ok&&r.j&&r.j.ok){
      localStorage.removeItem(K);cnt();
      document.getElementById('cartbox').hidden=true;
      var done=document.getElementById('done');
      done.hidden=false;
      done.focus();
     }else{
      err.textContent=(r.j&&r.j.error)||'משהו השתבש. אפשר להתקשר: 053-2535393';
      err.hidden=false;
     }
    })
    .catch(function(){b.disabled=false;err.textContent='משהו השתבש. אפשר להתקשר: 053-2535393';err.hidden=false});
  });
 }

 function motionReduced(){
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 }

 function bindMotion(){
  if(!motionReduced())return;
  document.querySelectorAll('.gallery video,.range video').forEach(function(v){
   v.removeAttribute('autoplay');
   v.pause();
  });
 }

 function showView(g,id){
  g.querySelectorAll('.g-view').forEach(function(v){
   var show=v.getAttribute('data-view')===id;
   v.hidden=!show;
   v.classList.toggle('is-on',show);
   v.querySelectorAll('video').forEach(function(vid){
    if(!show||motionReduced())vid.pause();
    else{var play=vid.play();if(play&&play.catch)play.catch(function(){});}
   });
  });
 }

 function bindGallery(){
  var g=document.querySelector('.gallery');
  if(!g)return;
  var zoom=g.querySelector('.zoom');
  if(zoom)zoom.addEventListener('click',function(){
   var on=g.classList.toggle('is-zoom');
   zoom.setAttribute('aria-pressed',on?'true':'false');
  });
  g.querySelectorAll('[data-go]').forEach(function(b){
   b.addEventListener('click',function(){
    var id=b.getAttribute('data-go');
    showView(g,id);
    g.querySelectorAll('[data-go]').forEach(function(x){
     x.setAttribute('aria-selected',x===b?'true':'false');
    });
   });
  });
 }

 document.addEventListener('DOMContentLoaded',function(){
  cnt();
  bindMenu();
  bindFilters();
  bindProduct();
  bindMotion();
  bindGallery();
  bindOrder();
 });
})();
