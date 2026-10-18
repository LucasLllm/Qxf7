from pathlib import Path
import requests,bs4,json,hashlib,datetime
from urllib.parse import quote,urljoin
O=Path(__file__).resolve().parent;p=O/'RESEARCH_RECEIPTS.json';d=json.loads(p.read_text())
for q in ['T-Motor F90 CAD STEP','BrotherHobby Avenger 2812 V5 CAD STEP']:
 u='https://www.bing.com/search?q='+quote(q);rec={'requested_url':u,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  r=requests.get(u,timeout=25,headers={'User-Agent':'Mozilla/5.0'});dest=O/'sources'/(hashlib.sha256(u.encode()).hexdigest()[:16]+'.html');dest.write_bytes(r.content);s=bs4.BeautifulSoup(r.text,'html.parser');links=[{'text':a.get_text(' ',strip=True),'url':urljoin(r.url,a['href'])} for a in s.select('a[href]')]
  rec.update(status=r.status_code,final_url=r.url,path=str(dest),sha256=hashlib.sha256(r.content).hexdigest(),bytes=len(r.content),links=links)
 except Exception as e:rec['error']=str(e)
 d['records'].append(rec);print(q,rec.get('status'),[(x['text'][:120],x['url']) for x in rec.get('links',[]) if any(k in (x['url']+' '+x['text']).lower() for k in ['f90','2812','grabcad','step','download'])][:15])
d['search_limitations']='Google HTTP200 search interstitials; Bing fallback results retained. Product pages had no CAD links. No login/private CAD/vendor contact attempted.'
for r in d['records']:
 if any(x in r['requested_url'] for x in ['goods-1057','p00234']):print('Drawing discovered in actual page',r['requested_url'],[x for x in r.get('images',[]) if '913747' in x or '1638150063356533' in x])
p.write_text(json.dumps(d,indent=2))
