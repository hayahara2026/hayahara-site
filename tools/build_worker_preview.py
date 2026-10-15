import json,mimetypes,os,base64,subprocess
mimetypes.add_type('text/plain','.txt');mimetypes.add_type('application/manifest+json','.webmanifest');mimetypes.add_type('image/webp','.webp');mimetypes.add_type('image/svg+xml','.svg');mimetypes.add_type('font/woff2','.woff2');mimetypes.add_type('video/mp4','.mp4');mimetypes.add_type('video/webm','.webm')
root='hayahara-site';F={}
for r,ds,fs in os.walk(root):
  ds[:]=[d for d in ds if d!='.git']
  for f in fs:
    if f in('CNAME','README.md') or r.startswith(root+'/mapot-src') or r.startswith(root+'/docs') or r.startswith(root+'/tests') or (r==root+'/mapot' and f.startswith('_')):continue
    p=os.path.join(r,f)[len(root):]
    t=mimetypes.guess_type(f)[0] or 'application/octet-stream'
    if t.startswith('text/') or t in('application/xml','application/json','application/manifest+json','image/svg+xml','application/javascript'): t+='; charset=utf-8'
    F[p]=[t,base64.b64encode(open(os.path.join(r,f),'rb').read()).decode()]
sha=subprocess.check_output(['git','-C',root,'rev-parse','--short','HEAD']).decode().strip()
js=open(root+"/mapot-src/api.js").read()+"const PRODUCTS="+open(root+"/mapot/_products.json").read()+";\n"+"""const F=%s;const RD=%s;const C={};
function get(p){const f=F[p];if(!f)return null;if(!C[p]){const s=atob(f[1]);const u=new Uint8Array(s.length);for(let i=0;i<s.length;i++)u[i]=s.charCodeAt(i);C[p]=u;}return [f[0],C[p]];}
export default{async fetch(req,env){const url=new URL(req.url);if(url.pathname.startsWith('/mapot/api/'))return mapotApi(req,env,url,url.pathname);
if(url.hostname==='www.hayahara.co.il'||url.protocol==='http:'&&url.hostname==='hayahara.co.il'){url.hostname='hayahara.co.il';url.protocol='https:';return Response.redirect(url.toString(),301);}
let p=decodeURIComponent(url.pathname);if(RD[p]){url.pathname=RD[p];return Response.redirect(url.toString(),301);}let r=null;
if(p.endsWith('/'))r=get(p+'index.html');else{r=get(p);if(!r&&F[p+'/index.html']){url.pathname=p+'/';return Response.redirect(url.toString(),301);}if(!r)r=get(p+'.html');}
const h={'x-served-by':'cf-pages-hayahara','x-site-rev':'%s'};
if(!r){const n=get('/404.html');return new Response(req.method==='HEAD'?null:n[1],{status:404,headers:{...h,'content-type':n[0]}});}
h['content-type']=r[0];h['cache-control']=r[0].startsWith('text/html')?'public, max-age=600':'public, max-age=86400';
return new Response(req.method==='HEAD'?null:r[1],{status:200,headers:h});}};"""%(json.dumps(F),json.dumps(json.load(open(root+'/mapot/_redirects.json'))),sha+'-preview')
os.makedirs('cfp_out_preview',exist_ok=True);open('cfp_out_preview/_worker.js','w').write(js)
b='----F'+sha
body="\r\n".join([f'--{b}','Content-Disposition: form-data; name="manifest"','','{}',f'--{b}','Content-Disposition: form-data; name="branch"','','mapot-preview',f'--{b}','Content-Disposition: form-data; name="commit_hash"','',sha,f'--{b}','Content-Disposition: form-data; name="_worker.js"; filename="_worker.js"','Content-Type: application/javascript+module','',js,f'--{b}--',''])
code="async () => { const body=%s; const d=await cloudflare.request({method:'POST',path:`/accounts/${accountId}/pages/projects/hayahara-site/deployments`,body,contentType:'multipart/form-data; boundary=%s',rawBody:true}); return {s:d.success,e:d.errors,url:d.result?.url,id:d.result?.id}; }"%(json.dumps(body),b)
open('cfp_deploy_preview.js','w').write(code);print(len(js),sha)
