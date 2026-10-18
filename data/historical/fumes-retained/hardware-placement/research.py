from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin,quote
import requests,bs4,json,hashlib,datetime,re
O=Path(__file__).resolve().parent; S=O/'sources';S.mkdir(exist_ok=True)
R=O.parents[1]
old=json.loads((R/'cfd-corrections-v1/hardware/web_sources.json').read_text())
seeds=[x['url'] for x in old if 'brotherhobby' in x['url']]
seeds+=['https://www.hobbyrc.co.uk/t-motor-f90-brushless-long-range-motors']
# Bounded search requests, no guessed product/CAD URLs. Discovery via search results.
queries=['T-Motor F90 motor STEP CAD dimension drawing','BrotherHobby Avenger 2812 V5 STEP CAD model']
seeds += ['https://www.google.com/search?q='+quote(q) for q in queries]
records=[]
def fetch(u):
 h=hashlib.sha256(u.encode()).hexdigest()[:16];rec={'requested_url':u,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  r=requests.get(u,timeout=25,headers={'User-Agent':'Mozilla/5.0'}); p=S/(h+('.jpg' if 'image/' in r.headers.get('Content-Type','') else '.html'));p.write_bytes(r.content)
  rec.update(status=r.status_code,final_url=r.url,path=str(p),bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest(),content_type=r.headers.get('Content-Type'))
  if 'image/' not in r.headers.get('Content-Type',''):
   soup=bs4.BeautifulSoup(r.text,'html.parser'); rec['title']=soup.title.get_text() if soup.title else None
   rec['links']=[{'text':x.get_text(' ',strip=True),'url':urljoin(r.url,x['href'])} for x in soup.select('a[href]')]
   rec['images']=list(dict.fromkeys(urljoin(r.url,x.get(k)) for x in soup.select('img') for k in ['src','data-src'] if x.get(k)))
   rec['cad_links']=[x for x in rec['links'] if re.search(r'\.(step|stp|iges|igs|stl|zip|sldprt)(?:$|\?)|download|cad',x['url'],re.I)]
   (S/(h+'.txt')).write_text(soup.get_text(' ',strip=True))
 except Exception as e:rec['error']=str(e)
 return rec
records += list(ThreadPoolExecutor(4).map(fetch,seeds))
# One manufacturer page if actually discoverable from saved/current search HTML.
found=[]
for r in records:
 for x in r.get('links',[]):
  u=x['url']
  if 'tmotorhobby.com' in u and not '/images/' in u and ('f90' in (u+' '+x['text']).lower()):found.append(u)
# Retained research is authoritative page discovery, not a new guessed route.
for p in (R/'performance-scenarios/range-first/worst-case/lift-research').glob('*.json'):
 try:
  d=p.read_text()
  for u in re.findall(r'https://www\.tmotorhobby\.com/[^\s"<>]+',d):
   if 'goods-' in u or 'product' in u:found.append(u)
 except Exception:pass
for u in list(dict.fromkeys(found))[:2]:records.append(fetch(u))
# Drawing assets found in actual manufacturer page, or retained documentary receipt.
drawings=['https://www.tmotorhobby.com/images/20211129/1638150063356533.jpg','https://ueeshop.ly200-cdn.com/u_file/UPAI/UPAI594/2410/photo/913747b78f.jpg']
for u in drawings:records.append(fetch(u))
(O/'RESEARCH_RECEIPTS.json').write_text(json.dumps({'bounded_search_queries':queries,'records':records,'retained_drawing_provenance':'cfd-corrections-v1/hardware/EVIDENCE.json and f90-spec-assets.json; refreshed actual assets','cad_found':None},indent=2))
for r in records:print(r['requested_url'],r.get('status',r.get('error')),'CAD:',r.get('cad_links',[]))
print('manufacturer found',found)
