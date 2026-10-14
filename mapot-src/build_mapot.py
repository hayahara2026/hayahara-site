# Generates /mapot/ sub-site. Brand name: change ONLY mapot-src/config.json -> "brand".
import json,os,html
R=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.dirname(R)
C=json.load(open(os.path.join(R,'config.json')));B=C['brand'];BASE=C['base'];WA=C['wa'];PH=C['phone']
OUT=os.path.join(ROOT,'mapot')
CATS=[('tablecloths','מפות','מפות לאירועים לפי מידה. כל סט מגיע נקי ומגוהץ.'),
('napkins','מפיות','מפיות בד לאירועים.'),('runners','ראנרים','ראנרים לשולחנות אירוע.'),
('chair-covers','כיסויי כיסאות','כיסויי כיסאות לאירועים.'),('bedding','מצעים','מצעים להשכרה.'),('towels','מגבות','מגבות להשכרה.')]
ITEMS={'tablecloths':[('3x3','מפה 3×3','מפה במידה 3×3 מטר, נקייה ומגוהצת.',False),('size-todo-1','מפה – מידה נוספת (TODO)','TODO: מידה, תיאור וזמינות ימולאו לאחר אישור צבי.',True)],
'napkins':[('napkin-todo','מפית בד (TODO)','TODO: מידות ופרטים לאישור.',True)],'runners':[('runner-todo','ראנר (TODO)','TODO: מידות ופרטים לאישור.',True)],
'chair-covers':[('chair-cover-todo','כיסוי כיסא (TODO)','TODO: דגם ופרטים לאישור.',True)],'bedding':[('bedding-todo','סט מצעים (TODO)','TODO: מידות ופרטים לאישור.',True)],
'towels':[('towel-todo','מגבת (TODO)','TODO: מידות ופרטים לאישור.',True)]}
AREAS=[('jerusalem','ירושלים'),('gush-etzion','גוש עציון'),('kfar-saba','כפר סבא'),('raanana','רעננה'),('netanya','נתניה'),('beit-shemesh','בית שמש'),('beitar-illit','ביתר עילית'),('modiin-illit','מודיעין עילית'),('bnei-brak','בני ברק'),('elad','אלעד')]
EVENTS=[('weddings','חתונות'),('bar-mitzvah','בר מצווה'),('halls','אולמות אירועים'),('catering','קייטרינג')]
FAQ=[('אילו פריטים אפשר לשכור?','מפות, מפיות, ראנרים, כיסויי כיסאות, מצעים ומגבות לאירועים.'),
('באיזה מצב מגיעות המפות?','כל סט מגיע נקי ומגוהץ.'),('איך מזמינים?',f'שולחים הודעת וואטסאפ ל־{PH} ומקבלים מענה עם פרטי ההזמנה.'),
('מי עומד מאחורי {B}?'.replace('{B}',B),f'{B} הוא שירות השכרת המפות של מכבסת היערה, הפועלת מאז 1980.'),
('לאילו אזורים יש משלוח?','TODO: רשימת אזורי המשלוח ממתינה לאישור.')]
pages=[]
ORG={"@type":"LocalBusiness","@id":BASE+"#business","name":B,"url":BASE,"telephone":"+972-53-2535393","parentOrganization":{"@id":"https://hayahara.co.il/#business"},"address":{"@type":"PostalAddress","streetAddress":"פרי גן 16","addressLocality":"מישור אדומים","addressCountry":"IL"}}
CSS="""*{box-sizing:border-box}body{margin:0;font-family:'Assistant','Rubik',system-ui,sans-serif;background:#fbf7f0;color:#2b2233;line-height:1.7}
a{color:#7a2e5a}header{background:#2b2233;color:#fbf7f0;padding:14px 16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}
.logo{font-family:Georgia,'Frank Ruhl Libre',serif;font-size:1.5rem;letter-spacing:.04em;color:#e8c27a;text-decoration:none;border:2px solid #e8c27a;padding:2px 12px;border-radius:30px}
nav a{color:#fbf7f0;margin-inline-start:12px;text-decoration:none;font-size:.95rem}main{max-width:960px;margin:auto;padding:16px}
.hero{background:linear-gradient(135deg,#7a2e5a,#2b2233);color:#fff;border-radius:18px;padding:32px 20px;margin:12px 0}
.hero h1{font-family:Georgia,serif;margin:0 0 8px}.btn{display:inline-block;background:#25d366;color:#08311a;font-weight:700;padding:12px 22px;border-radius:30px;text-decoration:none}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}.card{background:#fff;border:1px solid #eadfcc;border-radius:14px;padding:14px;text-decoration:none;color:inherit}
.ph{background:repeating-linear-gradient(45deg,#f1e8d8,#f1e8d8 10px,#fbf7f0 10px,#fbf7f0 20px);border:2px dashed #c9b48a;border-radius:12px;min-height:150px;display:flex;align-items:center;justify-content:center;color:#8a7650;font-size:.9rem;margin:10px 0}
.todo{background:#fff3cd;border:1px dashed #d4a017;padding:6px 10px;border-radius:8px}.crumb{font-size:.85rem}footer{background:#2b2233;color:#cfc3d6;padding:20px 16px;margin-top:30px;font-size:.9rem}footer a{color:#e8c27a}
.fab{position:fixed;bottom:16px;left:16px;background:#25d366;color:#08311a;border-radius:30px;padding:12px 18px;font-weight:700;text-decoration:none;box-shadow:0 4px 12px #0003}"""
def page(path,title,desc,crumbs,body,extra=None):
  url=BASE+path;g=[ORG]
  bl={"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":BASE+p} for i,(n,p) in enumerate([(B,'')]+crumbs)]};g.append(bl)
  if extra:g+=extra
  cr=' › '.join(f'<a href="/mapot/{p}">{html.escape(n)}</a>' for n,p in [(B,'')]+crumbs)
  rob='<meta name="robots" content="noindex">' if C['preview'] else ''
  h=f"""<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} | {B}</title><meta name="description" content="{html.escape(desc)}">{rob}<link rel="canonical" href="{url}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{url}"><meta property="og:locale" content="he_IL">
<link rel="stylesheet" href="/mapot/assets/mapot.css"><script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@graph":g},ensure_ascii=False)}</script></head><body>
<header><a class="logo" href="/mapot/">{B}</a><nav><a href="/mapot/catalog/">קטלוג</a><a href="/mapot/events/">אירועים</a><a href="/mapot/areas/">אזורי משלוח</a><a href="/mapot/faq/">שאלות נפוצות</a></nav></header>
<main><div class="crumb">{cr}</div>{body}<p><a class="btn" href="{WA}">הזמנה בוואטסאפ {PH}</a></p></main>
<footer>{B} – השכרת מפות, מפיות, ראנרים, כיסויי כיסאות, מצעים ומגבות לאירועים. חלק ממכבסת <a href="https://hayahara.co.il/">היערה</a>, הפועלת מאז 1980. וואטסאפ: <a href="{WA}">{PH}</a></footer>
<a class="fab" href="{WA}">וואטסאפ להזמנה</a></body></html>"""
  d=os.path.join(OUT,path);os.makedirs(d,exist_ok=True);open(os.path.join(d,'index.html'),'w').write(h);pages.append((path,title))
ph=lambda t:f'<div class="ph">מקום לתמונה אמיתית: {t} (TODO)</div>'
cards=lambda L:'<div class="grid">'+''.join(f'<a class="card" href="/mapot/{p}"><strong>{n}</strong><br><small>{s}</small></a>' for p,n,s in L)+'</div>'
catcards=cards([(f'catalog/{c}/',n,d) for c,n,d in CATS])
page('',f'{B} – השכרת מפות ומפיות לאירועים',f'{B}: השכרת מפות, מפיות, ראנרים, כיסויי כיסאות, מצעים ומגבות לאירועים. סט נקי ומגוהץ, הזמנה בוואטסאפ.',[],
 f'<section class="hero"><h1>{B}</h1><p>השכרת מפות, מפיות, ראנרים, כיסויי כיסאות, מצעים ומגבות לאירועים. כל סט מגיע נקי ומגוהץ.</p><a class="btn" href="{WA}">להזמנה בוואטסאפ</a></section>{ph("עמוד הבית")}<h2>הקטלוג</h2>{catcards}<h2>לפי סוג אירוע</h2>'+cards([(f'events/{e}/',n,'') for e,n in EVENTS])+'<h2>אזורי משלוח</h2>'+cards([(f'areas/{a}/',n,'') for a,n in AREAS])+'<p class="todo">TODO: טקסט עמוד הבית יגיע מהקופירייטר.</p>')
page('catalog/','קטלוג השכרת מפות ומפיות','קטלוג פריטים להשכרה לאירועים: מפות לפי מידה, מפיות, ראנרים, כיסויי כיסאות, מצעים ומגבות.',[('קטלוג','catalog/')],'<h1>קטלוג</h1>'+catcards)
for c,n,d in CATS:
  its=ITEMS[c];base=f'catalog/{c}/'
  page(base,f'השכרת {n} לאירועים',f'השכרת {n} לאירועים מבית {B}. {d}',[('קטלוג','catalog/'),(n,base)],f'<h1>השכרת {n}</h1><p>{d}</p>{ph(n)}'+cards([(base+s+'/',t,ds) for s,t,ds,_ in its]),
   [{"@type":"Service","name":f"השכרת {n}","provider":{"@id":BASE+"#business"},"url":BASE+base}])
  for s,t,ds,todo in its:
    p=base+s+'/'
    page(p,f'{t} להשכרה',f'{t} להשכרה לאירועים. {ds}',[('קטלוג','catalog/'),(n,base),(t,p)],f'<h1>{t}</h1>'+(f'<p class="todo">{ds}</p>' if todo else f'<p>{ds}</p>')+ph(t)+'<p class="todo">TODO: מחיר וזמינות – לפי פנייה בוואטסאפ; טקסט מהקופירייטר.</p>',
     None if todo else [{"@type":"Product","name":t,"description":ds,"category":n,"brand":{"@type":"Brand","name":B},"url":BASE+p}])
page('areas/','אזורי משלוח','אזורי משלוח להשכרת מפות ומפיות לאירועים.',[('אזורי משלוח','areas/')],'<h1>אזורי משלוח</h1><p class="todo">TODO: רשימת האזורים ממתינה לאישור צבי.</p>'+cards([(f'areas/{a}/',n,'') for a,n in AREAS]))
for a,n in AREAS:
  page(f'areas/{a}/',f'השכרת מפות ומפיות ב{n}',f'השכרת מפות, מפיות, ראנרים וכיסויי כיסאות לאירועים ב{n}. הזמנה בוואטסאפ.',[('אזורי משלוח','areas/'),(n,f'areas/{a}/')],f'<h1>השכרת מפות ומפיות ב{n}</h1><p>{B} משכירה מפות, מפיות, ראנרים, כיסויי כיסאות, מצעים ומגבות לאירועים ב{n}.</p><p class="todo">TODO: אזור ממתין לאישור; פרטי משלוח וטקסט מהקופירייטר.</p>'+catcards,
   [{"@type":"Service","name":f"השכרת מפות ב{n}","provider":{"@id":BASE+"#business"},"areaServed":n}])
page('events/','השכרת מפות לפי סוג אירוע','השכרת מפות ומפיות לחתונות, בר מצווה, אולמות וקייטרינג.',[('אירועים','events/')],'<h1>לפי סוג אירוע</h1>'+cards([(f'events/{e}/',n,'') for e,n in EVENTS]))
for e,n in EVENTS:
  page(f'events/{e}/',f'השכרת מפות ומפיות ל{n}',f'השכרת מפות, מפיות, ראנרים וכיסויי כיסאות ל{n}. סט נקי ומגוהץ.',[('אירועים','events/'),(n,f'events/{e}/')],f'<h1>השכרת מפות ומפיות ל{n}</h1><p>מפות, מפיות, ראנרים וכיסויי כיסאות ל{n}. כל סט מגיע נקי ומגוהץ.</p>{ph(n)}<p class="todo">TODO: טקסט מהקופירייטר.</p>'+catcards,
   [{"@type":"Service","name":f"השכרת מפות ל{n}","provider":{"@id":BASE+"#business"}}])
page('faq/','שאלות נפוצות',f'שאלות נפוצות על השכרת מפות ומפיות ב{B}.',[('שאלות נפוצות','faq/')],'<h1>שאלות נפוצות</h1>'+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ),
 [{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]}])
os.makedirs(OUT+'/assets',exist_ok=True);open(OUT+'/assets/mapot.css','w').write(CSS)
RED={'/services/tablecloth-rental.html':'/mapot/','/services/event-hall-tablecloth-rental.html':'/mapot/events/halls/','/services/tablecloth-rental-jerusalem.html':'/mapot/areas/jerusalem/','/services/tablecloth-rental-gush-etzion.html':'/mapot/areas/gush-etzion/','/services/tablecloth-rental-sharon.html':'/mapot/areas/','/services/table-linen.html':'/mapot/catalog/tablecloths/'}
json.dump(RED,open(OUT+'/_redirects.json','w'),ensure_ascii=False,indent=1)
open(OUT+'/sitemap-mapot.txt','w').write('\n'.join(BASE+p for p,_ in pages))
open(OUT+'/llms-section.txt','w').write(f'\n## {B} – השכרת מפות לאירועים (חלק ממכבסת היערה)\n'+'\n'.join(f'- {BASE}{p}: {t}' for p,t in pages)+'\n')
print(len(pages))
