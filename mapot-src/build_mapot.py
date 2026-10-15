# Builds /mapot/ from the copywriter file. Brand: ONLY mapot-src/config.json "brand" ({BRAND} in copy).
import json,os,re,html,shutil
R=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.dirname(R)
C=json.load(open(os.path.join(R,'config.json')));B=C['brand'];BASE=C['base'];WA=C['wa'];PH=C['phone']
SRC=C.get('copy','/workspace/copywriter/mapot-site-texts-2026-10-15.md');shutil.copy(SRC,os.path.join(R,'copy.md'))
md=open(os.path.join(R,'copy.md')).read().replace('{BRAND}',B)
OUT=os.path.join(ROOT,'mapot');shutil.rmtree(OUT,ignore_errors=True)
PEND='<span class="pend">[ממתין לצבי]</span>'
def inl(s):
  s=html.escape(s,quote=False);s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
  s=s.replace('[ממתין לצבי]',PEND).replace('053-2535393',f'<a href="{WA}">053-2535393</a>').replace('office@hayahara.co.il','<a href="mailto:office@hayahara.co.il">office@hayahara.co.il</a>');return s
def md2html(lines):
  o=[];ul=False;tbl=[]
  for l in lines:
    l=l.rstrip()
    if l.startswith('|'):
      if not re.match(r'^\|[-|\s]+\|$',l):tbl.append([c.strip() for c in l.strip('|').split('|')])
      continue
    if tbl:o.append('<table>'+''.join('<tr>'+''.join(f'<{"th" if i==0 else "td"}>{inl(c)}</{"th" if i==0 else "td"}>' for c in r)+'</tr>' for i,r in enumerate(tbl))+'</table>');tbl=[]
    if l.startswith('- '):
      if not ul:o.append('<ul>');ul=True
      o.append(f'<li>{inl(l[2:])}</li>');continue
    if ul:o.append('</ul>');ul=False
    if not l or l.startswith('(') or l=='---':continue
    m=re.match(r'^(#{1,2}) (.*)',l)
    if m:o.append(f'<h{len(m.group(1))}>{inl(m.group(2))}</h{len(m.group(1))}>');continue
    o.append(f'<p>{inl(l)}</p>')
  if ul:o.append('</ul>')
  return '\n'.join(o)
# split pages by headings that carry a /mapot/ URL
P={}
for m in re.finditer(r'^#{2,3} [\d.]+ ([^:\n]+): (/mapot/[^\s]*)\n(.*?)(?=^#{2,3} [\d.]+ |^## שאלות פתוחות|\Z)',md,re.S|re.M):
  name,url,body=m.group(1).strip(),m.group(2),m.group(3)
  t=re.search(r'\*\*title:\*\* (.*)',body).group(1);d=re.search(r'\*\*meta description:\*\* (.*)',body).group(1)
  lines=[x for x in body.split('\n') if not x.startswith('**title') and not x.startswith('**meta')]
  P[url]=dict(name=name,title=t,desc=d,lines=lines)
FOOT=[l[2:] for l in md.split('\n') if l.startswith('> ')]
cart=P.pop('/mapot/order/');cl={k:v for k,v in re.findall(r'\*\*([^*]+):\*\* (.*)','\n'.join(cart['lines']))}
# product template (section 6)
T={}
for m in re.finditer(r'^### 6\.\d (.+?)\n(.*?)(?=^### |^---)',md,re.S|re.M):
  b=m.group(2);T[m.group(1).strip()]=dict(name=re.search(r'\*\*שם מוצר:\*\* (.*)',b).group(1),desc=re.search(r'\*\*תיאור:\*\* (.*)',b).group(1),pts=re.findall(r'^- (.*)',b,re.M),btn=re.search(r'\*\*כפתור:\*\* (.*)',b).group(1),qty=re.search(r'\*\*הערה לשדה הכמות:\*\* (.*)',b).group(1))
CATS=[('tablecloths','מפות','מפה'),('napkins','מפיות','מפית'),('runners','ראנרים','ראנר'),('chair-covers','כיסויי כיסאות','כיסוי כיסא')]
W='[ממתין לצבי]'
# products: only 3x3 confirmed; one marked example per category
PRODUCTS=[dict(slug='tablecloth-3x3',cat='tablecloths',size='3×3',color=W,example=False)]+[dict(slug=f'{c}-example',cat=c,size=W,color=None if c=='chair-covers' else W,example=True) for c,_,_ in CATS]
def fill(s,p):return s.replace('{SIZE}',p['size']).replace(' | {COLOR}','' if p['color'] is None else ' | '+p['color']).replace('{COLOR}',p['color'] or '')
for p in PRODUCTS:
  t=T[[x for c,_,x in CATS if c==p['cat']][0]];p['name']=fill(t['name'],p);p['desc']=fill(t['desc'],p);p['t']=t;p['catname']=[n for c,n,_ in CATS if c==p['cat']][0]
pages=[]
ORG={"@type":"LocalBusiness","@id":BASE+"#business","name":B,"url":BASE,"telephone":"+972-53-2535393","email":"office@hayahara.co.il","parentOrganization":{"@id":"https://hayahara.co.il/#business"},"address":{"@type":"PostalAddress","streetAddress":"פרי גן 16","addressLocality":"מישור אדומים","addressCountry":"IL"}}
NAV=[('/mapot/catalog/','קטלוג'),('/mapot/tablecloths/','מפות'),('/mapot/napkins/','מפיות'),('/mapot/runners/','ראנרים'),('/mapot/chair-covers/','כיסויי כיסאות'),('/mapot/halls-catering/','אולמות וקייטרינג'),('/mapot/service-areas/','אזורי שירות'),('/mapot/faq/','שאלות נפוצות')]
EVENTS=['/mapot/wedding/','/mapot/bar-mitzvah/','/mapot/brit/','/mapot/sheva-brachot/','/mapot/halls-catering/']
def esc(s):return html.escape(s.replace('[ממתין לצבי]','(ממתין לאישור)'))
def page(url,title,desc,crumbs,body,extra=None,noindex=False):
  path=url[len('/mapot/'):];g=[ORG,{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":"https://hayahara.co.il"+u} for i,(n,u) in enumerate([(B,'/mapot/')]+crumbs)]}]+(extra or [])
  cr=' › '.join(f'<a href="{u}">{html.escape(n)}</a>' for n,u in [(B,'/mapot/')]+crumbs)
  rob='<meta name="robots" content="noindex">' if (C['preview'] or noindex) else ''
  h=f"""<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">{rob}<link rel="canonical" href="https://hayahara.co.il{url}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="https://hayahara.co.il{url}"><meta property="og:locale" content="he_IL"><meta property="og:site_name" content="{html.escape(B)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@400;500&family=Heebo:wght@300;400;500&display=swap"><link rel="stylesheet" href="/mapot/assets/mapot.css"><script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@graph":g},ensure_ascii=False)}</script><script src="/mapot/assets/cart.js" defer></script></head><body>
<header><a class="logo" href="/mapot/">{html.escape(B)}</a><a class="cartlink" href="/mapot/order/">סל ההזמנה <span id="cartn">0</span></a>
<nav>{''.join(f'<a href="{u}">{n}</a>' for u,n in NAV)}</nav></header>
<main>{'' if not crumbs else f'<div class="crumb">{cr}</div>'}{body}</main>
<footer><p>{'<br>'.join(html.escape(x) for x in FOOT)}</p><p>טלפון ווואטסאפ: <a href="{WA}">053-2535393</a> | <a href="mailto:office@hayahara.co.il">office@hayahara.co.il</a> | <a href="https://hayahara.co.il/">מכבסת היערה</a></p>
<p>{' · '.join(f'<a href="{u}">{n}</a>' for u,n in NAV+[(e,P[e]["name"]) for e in EVENTS[:4]])}</p></footer>
<a class="fab" href="{WA}" aria-label="וואטסאפ להזמנה">וואטסאפ 053-2535393</a></body></html>"""
  d=os.path.join(OUT,path);os.makedirs(d,exist_ok=True);open(os.path.join(d,'index.html'),'w').write(h)
  if not (noindex) :pages.append((url,title))
ph=lambda t:f'<div class="ph">תמונה תתווסף · {html.escape(t)}</div>'
def card(p):return f'<a class="card" href="/mapot/catalog/{p["slug"]}/" data-type="{p["cat"]}" data-size="{html.escape(p["size"])}"><div class="ph sm">תמונה תתווסף</div>{"<span class=ex>דוגמה</span>" if p["example"] else ""}<strong>{inl(p["name"])}</strong><small>{p["catname"]}</small></a>'
def grid(ps):return '<div class="grid" id="grid">'+''.join(card(p) for p in ps)+'</div>'
catlinks='<div class="chips">'+''.join(f'<a class="chip" href="/mapot/{c}/">{n}</a>' for c,n,_ in CATS)+'</div>'
evlinks='<div class="chips">'+''.join(f'<a class="chip" href="{e}">{P[e]["name"]}</a>' for e in EVENTS)+'</div>'
for url,pg in P.items():
  body=md2html(pg['lines']);crumbs=[] if url=='/mapot/' else [(pg['name'],url)];extra=[]
  c=url.strip('/').split('/')[-1]
  if url=='/mapot/':body=f'<section class="hero"><span class="eyebrow">השכרת טקסטיל לשולחן האירוע</span>{body.split("</h1>")[0]}</h1><a class="btn" href="/mapot/catalog/">לקטלוג</a> <a class="btn wa" href="{WA}">וואטסאפ 053-2535393</a></section>{ph("עמוד הבית")}'+body.split('</h1>',1)[1]+'<h2>הקטלוג</h2>'+grid(PRODUCTS)+'<h2>לפי סוג אירוע</h2>'+evlinks
  elif c in [x for x,_,_ in CATS]:
    crumbs=[('קטלוג','/mapot/catalog/'),(pg['name'],url)];body=ph(pg['name'])+body+'<h2>פריטים</h2>'+grid([p for p in PRODUCTS if p['cat']==c])+catlinks
    extra=[{"@type":"Service","name":pg['name'],"serviceType":"השכרה","provider":{"@id":BASE+"#business"},"url":"https://hayahara.co.il"+url}]
  elif url in EVENTS:body=ph(pg['name'])+body+catlinks+evlinks;extra=[{"@type":"Service","name":re.sub(r'<.*?>','',pg['title'].split('|')[0]).strip(),"provider":{"@id":BASE+"#business"}}]
  elif url=='/mapot/faq/':
    qa=re.findall(r'^## (.+)\n(.+)','\n'.join(pg['lines']),re.M)
    extra=[{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qa if '[ממתין לצבי]' not in a]}]
  elif url=='/mapot/service-areas/':extra=[{"@type":"Service","name":"השכרת מפות ומפיות","provider":{"@id":BASE+"#business"},"areaServed":["השרון","גוש דן","עוטף ירושלים","ים המלח","גוש עציון"]}];body+=catlinks
  page(url,pg['title'],pg['desc'],crumbs,body+f'<p><a class="btn" href="/mapot/catalog/">לקטלוג ולהזמנה</a></p>',extra)
# catalog with filters
sizes=sorted({p['size'] for p in PRODUCTS})
flt='<div class="filters"><label>סוג <select id="ft"><option value="">הכול</option>'+''.join(f'<option value="{c}">{n}</option>' for c,n,_ in CATS)+'</select></label><label>מידה <select id="fs"><option value="">הכול</option>'+''.join(f'<option>{html.escape(s)}</option>' for s in sizes)+'</select></label></div>'
page('/mapot/catalog/',f'קטלוג השכרת מפות, מפיות, ראנרים וכיסויי כיסאות | {B}',f'קטלוג {B}: מפות, מפיות, ראנרים וכיסויי כיסאות להשכרה. בוחרים פריטים וכמויות ושולחים בקשת הזמנה.',[('קטלוג','/mapot/catalog/')],
 '<h1>קטלוג</h1><p>בוחרים פריטים, מוסיפים להזמנה ושולחים. את הכמויות ואת המשלוח מאשרים איתכם בשיחה.</p><p class="note">פריטים המסומנים «דוגמה» הם תבנית לתצוגה; פרטי הפריט <span class="pend">[ממתין לצבי]</span>.</p>'+flt+grid(PRODUCTS)+catlinks)
for p in PRODUCTS:
  t=p['t'];url=f'/mapot/catalog/{p["slug"]}/'
  body=f'<div class="prod"><div class="ph big">תמונה תתווסף</div><div><h1>{inl(p["name"])}</h1>{"<p class=note>דוגמה: פריט לתצוגה, פרטיו ממתינים לאישור.</p>" if p["example"] else ""}<p>{inl(p["desc"])}</p><ul>'+''.join(f'<li>{inl(x)}</li>' for x in t['pts'])+f'</ul><label class="qty">{html.escape(t["qty"])}<input type="number" id="q" min="1" max="10000" value="1" inputmode="numeric"></label><button class="btn" id="add" data-slug="{p["slug"]}" data-name="{html.escape(p["name"])}">{t["btn"]}</button> <span id="added" hidden>נוסף לסל. <a href="/mapot/order/">לסל ההזמנה</a></span></div></div>'
  ex=None if p['example'] else [{"@type":"Product","name":p['name'].replace(W,'').strip(' |'),"description":p['desc'].replace(W,'').replace('  ',' '),"category":p['catname'],"size":p['size'],"brand":{"@type":"Brand","name":B},"url":"https://hayahara.co.il"+url}]
  page(url,f'{p["name"]} | {B}',re.sub(r'\s+',' ',p['desc']),[('קטלוג','/mapot/catalog/'),(p['catname'],f'/mapot/{p["cat"]}/'),(p['name'],url)],body,ex,noindex=p['example'])
labels=cl['תוויות שדות'].split(' | ');names=['business','contact','phone','email','event_date','address','notes'];types=['text','text','tel','email','date','text','textarea']
req={'contact','phone','event_date','address'}
fields=''.join(f'<label>{l}{" *" if n in req else ""}'+(f'<textarea name="{n}" maxlength="1000"></textarea>' if t=='textarea' else f'<input name="{n}" type="{t}" maxlength="200"{" required" if n in req else ""}{" pattern=0?5[0-9]-?[0-9]{{7}}|0[2-9]-?[0-9]{{7}}" if n=="phone" else ""}>')+'</label>' for l,n,t in zip(labels,names,types))
page('/mapot/order/',cart['title'],cart['desc'],[('סל ההזמנה','/mapot/order/')],
 f'<h1>סל ההזמנה</h1><p>{inl(cl["טקסט פתיחה"])}</p><div id="empty" hidden><p>{inl(cl["סל ריק"])}</p><a class="btn" href="/mapot/catalog/">לקטלוג</a></div><div id="cartbox"><table id="cart"></table>'
 f'<form id="orderform" novalidate>{fields}<label class="hp" aria-hidden="true">Website<input name="website" tabindex="-1" autocomplete="off"></label><button class="btn" type="submit">{cl["כפתור"]}</button><p id="err" class="err" hidden></p></form></div><div id="done" hidden><p>{inl(cl["הודעת אישור"])}</p></div>')
os.makedirs(OUT+'/assets',exist_ok=True)
for f in ('mapot.css','cart.js'):shutil.copy(os.path.join(R,f),OUT+'/assets/'+f)
RED={'/services/tablecloth-rental.html':'/mapot/','/services/event-hall-tablecloth-rental.html':'/mapot/halls-catering/','/services/tablecloth-rental-jerusalem.html':'/mapot/service-areas/','/services/tablecloth-rental-gush-etzion.html':'/mapot/service-areas/','/services/tablecloth-rental-sharon.html':'/mapot/service-areas/','/services/table-linen.html':'/mapot/tablecloths/'}
json.dump(RED,open(OUT+'/_redirects.json','w'),ensure_ascii=False,indent=1)
open(OUT+'/sitemap-mapot.txt','w').write('\n'.join('https://hayahara.co.il'+u for u,_ in pages if u!='/mapot/order/'))
open(OUT+'/llms-section.txt','w').write(f'\n## {B}: השכרת מפות, מפיות, ראנרים וכיסויי כיסאות (מבית מכבסת היערה)\nהזמנה: טלפון ווואטסאפ 053-2535393, office@hayahara.co.il\n'+'\n'.join(f'- https://hayahara.co.il{u}: {t.replace(W,"").strip()}' for u,t in pages if u!='/mapot/order/')+'\n')
print(len(pages),'indexable pages;',[u for u,_ in pages])
json.dump({p['slug']:p['name'] for p in PRODUCTS},open(OUT+'/_products.json','w'),ensure_ascii=False)
