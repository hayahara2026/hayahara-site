async function sha(s){const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('')}
const J=(o,s=200)=>new Response(JSON.stringify(o),{status:s,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-robots-tag':'noindex'}});
async function limited(env,key,max,win){const now=Math.floor(Date.now()/1000);const r=await env.DB.prepare('SELECT n,ts FROM rate WHERE k=?').bind(key).first();
 if(!r||now-r.ts>win){await env.DB.prepare('INSERT OR REPLACE INTO rate(k,n,ts) VALUES(?,1,?)').bind(key,now).run();return false}
 if(r.n>=max)return true;await env.DB.prepare('UPDATE rate SET n=n+1 WHERE k=?').bind(key).run();return false}
function teq(a,b){if(a.length!==b.length)return false;let d=0;for(let i=0;i<a.length;i++)d|=a.charCodeAt(i)^b.charCodeAt(i);return d===0}
const S=(v,m)=>typeof v==='string'?v.trim().slice(0,m):'';
async function mapotApi(req,env,url,p){
 if(!env||!env.DB)return J({error:'השירות יופעל בקרוב. להזמנה: 053-2535393'},503);
 const ip=await sha((req.headers.get('cf-connecting-ip')||'')+'mapot');
 if(p==='/mapot/api/order'&&req.method==='POST'){
  const ct=req.headers.get('content-type')||'';if(!ct.includes('application/json'))return J({error:'בקשה לא תקינה'},415);
  const raw=await req.text();if(raw.length>20000)return J({error:'בקשה גדולה מדי'},413);
  let d;try{d=JSON.parse(raw)}catch(e){return J({error:'בקשה לא תקינה'},400)}
  if(S(d.website,100))return J({ok:true});
  if(await limited(env,'o:'+ip,5,3600))return J({error:'נשלחו כמה בקשות ברצף. לשיחה ישירה: 053-2535393'},429);
  const o={business:S(d.business,120),name:S(d.contact,80),phone:S(d.phone,20).replace(/[\s-]/g,''),email:S(d.email,120),event_date:S(d.event_date,10),address:S(d.address,200),notes:S(d.notes,1000)};
  const bad=[];if(o.name.length<2)bad.push('איש קשר');if(!/^0(5\d|[2-9])\d{7}$/.test(o.phone))bad.push('טלפון');
  if(o.email&&!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(o.email))bad.push('מייל');
  if(!/^\d{4}-\d{2}-\d{2}$/.test(o.event_date)||isNaN(Date.parse(o.event_date)))bad.push('תאריך האירוע');if(o.address.length<3)bad.push('כתובת למשלוח');
  const items=Array.isArray(d.items)?d.items.slice(0,50).map(i=>({slug:S(i&&i.slug,60),qty:parseInt(i&&i.qty,10)})).filter(i=>PRODUCTS[i.slug]&&i.qty>=1&&i.qty<=10000).map(i=>({...i,name:PRODUCTS[i.slug]})):[];
  if(!items.length)bad.push('פריטים בסל');
  if(bad.length)return J({error:'נא לבדוק: '+bad.join(', ')},400);
  const created=new Date().toISOString();
  const r=await env.DB.prepare('INSERT INTO orders(created_at,business,name,phone,email,event_date,address,notes,items,ip_hash) VALUES(?,?,?,?,?,?,?,?,?,?)').bind(created,o.business,o.name,o.phone,o.email,o.event_date,o.address,o.notes,JSON.stringify(items),ip.slice(0,16)).run();
  const id=r.meta&&r.meta.last_row_id;
  const text=`בקשת הזמנה חדשה #${id}\nעסק: ${o.business}\nאיש קשר: ${o.name}\nטלפון: ${o.phone}\nמייל: ${o.email}\nתאריך האירוע: ${o.event_date}\nכתובת: ${o.address}\nהערות: ${o.notes}\n\nפריטים:\n`+items.map(i=>`- ${i.name} × ${i.qty}`).join('\n')+`\n\nניהול: ${url.origin}/mapot/admin/`;
  let mail='none';try{if(env.MAILER){const m=await env.MAILER.fetch('https://mailer/send',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({subject:`בקשת הזמנה #${id} – מפות`,text})});mail=m.ok?'sent':'fail:'+m.status}}catch(e){mail='fail'}
  return J({ok:true,id,mail});
 }
 if(p.startsWith('/mapot/api/admin/')){
  if(await limited(env,'a:'+ip,30,900))return J({error:'too many'},429);
  const h=req.headers.get('authorization')||'';let ok=false;
  if(h.startsWith('Basic ')&&env.ADMIN_PASS){try{const [u,...pw]=atob(h.slice(6)).split(':');ok=teq(await sha(u),await sha(env.ADMIN_USER||'admin'))&&teq(await sha(pw.join(':')),await sha(env.ADMIN_PASS))}catch(e){}}
  if(!ok)return J({error:'unauthorized'},401);
  if(p==='/mapot/api/admin/orders'&&req.method==='GET'){const r=await env.DB.prepare('SELECT * FROM orders ORDER BY id DESC LIMIT 200').all();return J({orders:r.results})}
  const m=p.match(/^\/mapot\/api\/admin\/orders\/(\d+)$/);
  if(m&&req.method==='DELETE'){await env.DB.prepare('DELETE FROM orders WHERE id=?').bind(+m[1]).run();return J({ok:true})}
 }
 return J({error:'not found'},404);
}
