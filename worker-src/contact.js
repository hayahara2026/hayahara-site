// POST /api/contact -> email via service binding MAILER (Worker "mapot-mailer", Cloudflare send_email). No secrets in code.
const CJ=(o,s=200)=>new Response(JSON.stringify(o),{status:s,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-robots-tag':'noindex'}});
const CS=(v,m)=>typeof v==='string'?v.replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g,'').trim().slice(0,m):'';
const WA='053-2535393';
async function contactApi(req,env,url){
 if(req.method!=='POST')return CJ({error:'שיטה לא נתמכת'},405);
 const o=req.headers.get('origin');if(o&&o!==url.origin&&!/^https:\/\/([a-z0-9-]+\.)?hayahara-site\.pages\.dev$/.test(o))return CJ({error:'בקשה לא תקינה'},403);
 const ct=req.headers.get('content-type')||'';if(!ct.includes('application/json'))return CJ({error:'בקשה לא תקינה'},415);
 const raw=await req.text();if(raw.length>8000)return CJ({error:'ההודעה ארוכה מדי'},413);
 let d;try{d=JSON.parse(raw)}catch(e){return CJ({error:'בקשה לא תקינה'},400)}
 if(CS(d.website,100))return CJ({ok:true}); // honeypot: pretend success
 const age=Date.now()-Number(d.t||0);if(!(age>=3000&&age<=86400000*2))return CJ({error:'כדאי לנסות שוב בעוד רגע. אפשר גם לשלוח הודעה בוואטסאפ: '+WA},400);
 const f={name:CS(d.name,80),phone:CS(d.phone,20).replace(/[^\d+\-\s()]/g,''),email:CS(d.email,120),business:CS(d.business,120),type:CS(d.type,60),message:CS(d.message,2000)};
 const bad=[];if(f.name.length<2)bad.push('שם');if(f.phone.replace(/\D/g,'').length<7)bad.push('טלפון');
 if(f.email&&!/^[^@\s<>,;]+@[^@\s<>,;]+\.[^@\s<>,;]+$/.test(f.email))bad.push('מייל');
 if(bad.length)return CJ({error:'כדאי לבדוק את השדות: '+bad.join(', ')},422);
 if(!env||!env.MAILER)return CJ({error:'השירות זמין כרגע בוואטסאפ ובטלפון: '+WA},503);
 // basic rate limit per IP (Cache API, per data-centre): 5 messages / hour
 const ip=req.headers.get('cf-connecting-ip')||'x';const hb=new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(ip+'contact')));
 const key='https://rl.hayahara.internal/'+[...hb.slice(0,8)].map(x=>x.toString(16).padStart(2,'0')).join('');
 const cache=caches.default;let n=0;try{const c=await cache.match(key);if(c)n=parseInt(await c.text())||0}catch(e){}
 if(n>=5)return CJ({error:'התקבלו כמה פניות ברצף. לשיחה מיידית: '+WA},429);
 try{await cache.put(key,new Response(String(n+1),{headers:{'cache-control':'max-age=3600'}}))}catch(e){}
 const test=/^TEST\b/i.test(f.message);
 const text=`פנייה חדשה מהאתר hayahara.co.il\n\nשם: ${f.name}\nטלפון: ${f.phone}\nמייל: ${f.email}\nשם העסק: ${f.business}\nסוג העסק: ${f.type}\n\nהודעה:\n${f.message}\n\n— נשלח מטופס צור קשר, ${new Date().toLocaleString('he-IL',{timeZone:'Asia/Jerusalem'})}`;
 const subject=(test?'[TEST] ':'')+`פנייה מהאתר – ${f.name}${f.business?' ('+f.business+')':''}`;
 try{const m=await env.MAILER.fetch('https://mailer/send',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({subject,text,from_name:'אתר מכבסת היערה',reply_to:f.email||undefined})});
  if(!m.ok)return CJ({error:'השליחה לא הושלמה. אפשר לפנות אלינו בוואטסאפ או בטלפון: '+WA},502);}
 catch(e){return CJ({error:'השליחה לא הושלמה. אפשר לפנות אלינו בוואטסאפ או בטלפון: '+WA},502)}
 return CJ({ok:true});
}
