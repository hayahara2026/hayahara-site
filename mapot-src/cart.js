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

 function pinScroll(el){
  var pin=null;
  function restore(){
   if(pin==null)return;
   if(Math.abs(window.scrollY-pin)>1)window.scrollTo(window.scrollX,pin);
  }
  el.addEventListener('pointerdown',function(e){
   if(e.pointerType==='mouse'&&e.button!==0)return;
   pin=window.scrollY;
  });
  el.addEventListener('focus',function(){
   if(pin==null)return;
   restore();
   requestAnimationFrame(function(){
    restore();
    requestAnimationFrame(function(){restore();pin=null});
   });
  });
 }

 function bindProduct(){
  var add=document.getElementById('add');
  if(!add)return;
  var q=document.getElementById('q');
  var min=parseInt(add.dataset.min||'1',10)||1;
  var max=10000;
  function curMax(){var m=parseInt(q&&q.max,10);return m>=1?m:max}
  document.querySelectorAll('.buy .swatch').forEach(function(b){
   pinScroll(b);
   b.addEventListener('click',function(){
    document.querySelectorAll('.buy .swatch').forEach(function(x){x.setAttribute('aria-checked','false')});
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
   if(f){
    f.qty=Math.min(curMax(),f.qty+qty);
    if(add.dataset.size)f.size=add.dataset.size;
    if(add.dataset.fabric)f.fabric=add.dataset.fabric;
   }else c.push({sku:add.dataset.sku,name:add.dataset.name,size:add.dataset.size||'',fabric:add.dataset.fabric||'',color:color,colorName:colorName,colorHex:colorHex,qty:qty});
   set(c);
   var note=document.getElementById('added');
   if(note){note.hidden=false}
  }
  add.addEventListener('click',addOne);
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
   var bits=['כמות '+i.qty];
   if(i.size)bits.push('מידה '+i.size);
   if(i.fabric)bits.push('בד '+i.fabric);
   if(i.colorName)bits.push(i.colorName);
   return '<tr><td><span class="linename">'+esc(i.name)+'</span>'
    +'<span class="linemeta">'+esc(bits.join(' · '))+'</span></td>'
    +'<td><div class="stepper"><button type="button" data-dec="'+k+'" aria-label="הפחתת כמות">−</button>'
    +'<input type="number" min="1" max="10000" value="'+i.qty+'" data-k="'+k+'" aria-label="כמות">'
    +'<button type="button" data-inc="'+k+'" aria-label="הגדלת כמות">+</button></div></td>'
    +'<td><button type="button" class="line-remove" data-r="'+k+'" aria-label="הסרת '+esc(i.name)+'">הסרה</button></td></tr>';
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

 function monthNames(){
  var field=document.querySelector('.datefield');
  var raw=field&&field.getAttribute('data-months');
  if(raw){
   var parts=raw.split(',');
   if(parts.length===12)return parts;
  }
  return ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'];
 }

 function heDate(iso){
  var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(iso||'');
  if(!m)return '';
  var y=+m[1],mo=+m[2],d=+m[3];
  if(mo<1||mo>12||y<2026||y>2032)return '';
  var dt=new Date(iso+'T00:00:00');
  if(dt.getFullYear()!==y||dt.getMonth()+1!==mo||dt.getDate()!==d)return '';
  return d+' ב'+monthNames()[mo-1]+' '+y;
 }

 function paintDate(){
  var input=document.getElementById('f-event_date');
  var face=document.getElementById('dateface');
  if(!input)return;
  var label=heDate(input.value);
  if(input.value&&!label){
   input.setCustomValidity('תאריך האירוע');
   if(face)face.textContent='בחירת תאריך';
  }else{
   input.setCustomValidity('');
   if(face)face.textContent=label||'בחירת תאריך';
  }
 }

 function bindOrder(){
  var form=document.getElementById('orderform');
  if(!form)return;
  drawCart();
  var wrap=document.querySelector('.datepick');
  if(wrap)wrap.classList.add('is-ready');
  var date=document.getElementById('f-event_date');
  if(date){
   date.addEventListener('input',paintDate);
   date.addEventListener('change',paintDate);
   paintDate();
  }
  form.addEventListener('submit',function(e){
   e.preventDefault();
   var err=document.getElementById('err');
   err.hidden=true;
   paintDate();
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
   pinScroll(b);
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
