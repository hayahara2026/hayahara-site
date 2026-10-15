async function sha(s){const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('')}
const J=(o,s=200)=>new Response(JSON.stringify(o),{status:s,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-robots-tag':'noindex'}});
async function limited(key,max,win){const cache=caches.default;const k='https://rl.hayahara.internal/'+key;let n=0;try{const c=await cache.match(k);if(c)n=parseInt(await c.text())||0}catch(e){}
 if(n>=max)return true;try{await cache.put(k,new Response(String(n+1),{headers:{'cache-control':'max-age='+win}}))}catch(e){}return false}
const S=(v,m)=>typeof v==='string'?v.trim().slice(0,m):'';
async function nullProvider(){return null}
async function remoteProvider(env,q){
 const u=new URL(env.INVENTORY_URL);
 u.searchParams.set('sku',q.sku);
 if(q.color)u.searchParams.set('color',q.color);
 if(q.from)u.searchParams.set('from',q.from);
 if(q.to)u.searchParams.set('to',q.to);
 const headers={accept:'application/json'};
 if(env.INVENTORY_TOKEN)headers.authorization='Bearer '+env.INVENTORY_TOKEN;
 const r=await fetch(u.toString(),{headers});
 if(!r.ok)return null;
 const j=await r.json();
 if(j&&Number.isInteger(j.available)&&j.available>=0)return j.available;
 return null;
}
function providerFor(env){return (env&&env.INVENTORY_URL)?remoteProvider:nullProvider}
async function availability(req,env,url){
 const ip=await sha((req.headers.get('cf-connecting-ip')||'')+'mapot');
 if(await limited('a'+ip,60,3600))return J({error:'נשלחו כמה בקשות ברצף. לשיחה ישירה: 053-2535393'},429);
 const sku=S(url.searchParams.get('sku'),40);
 const color=S(url.searchParams.get('color'),16);
 const from=S(url.searchParams.get('from'),10);
 const to=S(url.searchParams.get('to'),10);
 const dateOk=s=>!s||/^\d{4}-\d{2}-\d{2}$/.test(s);
 if(!dateOk(from)||!dateOk(to))return J({error:'בקשה לא תקינה'},400);
 const p=PRODUCTS[sku];
 if(!p)return J({error:'not found'},404);
 const cols=Array.isArray(p.colors)?p.colors:[];
 if(color&&cols.length&&!cols.includes(color))return J({error:'בקשה לא תקינה'},400);
 if(color&&!cols.length)return J({error:'בקשה לא תקינה'},400);
 let available=null;
 try{available=await providerFor(env)(env,{sku,color,from,to})}catch(e){available=null}
 if(available!==null&&(!Number.isInteger(available)||available<0))available=null;
 return J({sku,available});
}
async function order(req,env){
 if(!env||!env.MAILER)return J({error:'השירות זמין כרגע בוואטסאפ ובטלפון: 053-2535393'},503);
 const ip=await sha((req.headers.get('cf-connecting-ip')||'')+'mapot');
 const ct=req.headers.get('content-type')||'';if(!ct.includes('application/json'))return J({error:'בקשה לא תקינה'},415);
 const raw=await req.text();if(raw.length>20000)return J({error:'בקשה גדולה מדי'},413);
 let d;try{d=JSON.parse(raw)}catch(e){return J({error:'בקשה לא תקינה'},400)}
 if(S(d.website,100))return J({ok:true});
 if(await limited('o'+ip,5,3600))return J({error:'נשלחו כמה בקשות ברצף. לשיחה ישירה: 053-2535393'},429);
 const o={business:S(d.business,120),name:S(d.contact,80),phone:S(d.phone,20).replace(/[\s-]/g,''),email:S(d.email,120),event_date:S(d.event_date,10),address:S(d.address,200),notes:S(d.notes,1000)};
 const bad=[];if(o.name.length<2)bad.push('איש קשר');if(!/^0(5\d|[2-9])\d{7}$/.test(o.phone))bad.push('טלפון');
 if(o.email&&!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(o.email))bad.push('מייל');
 if(!/^\d{4}-\d{2}-\d{2}$/.test(o.event_date)||isNaN(Date.parse(o.event_date)))bad.push('תאריך האירוע');if(o.address.length<3)bad.push('כתובת למשלוח');
 const rawItems=Array.isArray(d.items)?d.items.slice(0,50):[];
 const items=[];
 for(const i of rawItems){
  const sku=S(i&&i.sku,40),color=S(i&&i.color,16),qty=parseInt(i&&i.qty,10);
  const p=PRODUCTS[sku];
  if(!p||!(qty>=1&&qty<=10000))continue;
  const cols=Array.isArray(p.colors)?p.colors:[];
  if(cols.length){if(!cols.includes(color))continue}
  else if(color)continue;
  const color_name=(p.color_names&&p.color_names[color])||'';
  items.push({sku,color,color_name,qty,name:p.name});
 }
 if(rawItems.length!==items.length||!items.length)bad.push('פריטים בסל');
 if(bad.length)return J({error:'נא לבדוק: '+bad.join(', ')},400);
 const created=new Date().toISOString();
 const id=Date.now().toString(36).toUpperCase().slice(-6);
 if(env.DB){try{await env.DB.prepare('INSERT INTO orders(created_at,business,name,phone,email,event_date,address,notes,items,ip_hash) VALUES(?,?,?,?,?,?,?,?,?,?)').bind(created,o.business,o.name,o.phone,o.email,o.event_date,o.address,o.notes,JSON.stringify(items),ip.slice(0,16)).run()}catch(e){}}
 const text=`בקשת הזמנה חדשה #${id}\nעסק: ${o.business}\nאיש קשר: ${o.name}\nטלפון: ${o.phone}\nמייל: ${o.email}\nתאריך האירוע: ${o.event_date}\nכתובת: ${o.address}\nהערות: ${o.notes}\n\nפריטים:\n`+items.map(i=>`- ${i.name}${i.color_name?' · '+i.color_name:''} × ${i.qty}`).join('\n');
 const test=/^TEST\b/i.test(o.notes);
 let mail='fail';try{const m=await env.MAILER.fetch('https://mailer/send',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({subject:(test?'[TEST] ':'')+`בקשת הזמנה #${id} – מפות`,text,from_name:'הזמנות מפות',reply_to:o.email||undefined})});mail=m.ok?'sent':'fail:'+m.status}catch(e){}
 if(mail!=='sent')return J({error:'השליחה לא הושלמה. אפשר להזמין בוואטסאפ או בטלפון: 053-2535393'},502);
 return J({ok:true,id,mail});
}
async function mapotApi(req,env,url,p){
 if(p==='/mapot/api/availability'&&req.method==='GET')return availability(req,env,url);
 if(p==='/mapot/api/order'&&req.method==='POST')return order(req,env);
 return J({error:'not found'},404);
}
