"""Bounded source capture; explicit URLs only; max eight requests."""
from pathlib import Path
import requests,json,hashlib,datetime,sys
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent

def fetch(url,name):
    manifest=ROOT/'SOURCES.json'
    records=json.loads(manifest.read_text()) if manifest.exists() else []
    if len(records)>=8: raise RuntimeError('eight-fetch budget exhausted')
    r=requests.get(url,timeout=50)
    path=ROOT/'data'/name;path.parent.mkdir(exist_ok=True);path.write_bytes(r.content)
    records.append(dict(url=url,final_url=r.url,status=r.status_code,path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(r.content).hexdigest(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    manifest.write_text(json.dumps(records,indent=2)+'\n')
    print(name,r.status_code,len(r.content))
    if not name.endswith('.dat'):
        s=BeautifulSoup(r.content,'html.parser')
        (path.with_suffix('.txt')).write_text(s.get_text(' ',strip=True))
        for x in s.find_all(['a','img']):
            u=x.get('href',x.get('src',''))
            if any(k in u.lower() for k in ['10x6','pdf','discharge','curve','hub','adapter']):print(u,x.get_text()[:60])
if __name__=='__main__':fetch(sys.argv[1],sys.argv[2])
