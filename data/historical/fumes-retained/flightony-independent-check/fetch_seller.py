"""Capture the actual seller pages; do not treat seller claims as measurements."""
from pathlib import Path
from urllib.parse import urljoin
import json,hashlib
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
urls=['https://www.flightony.com/','https://www.flightony.com/stork-vtol/specs','https://www.flightony.com/stork-vtol/performance','https://www.flightony.com/configure/extended-range','https://www.flightony.com/configure/standard']
index=[]
for i,url in enumerate(urls):
    try:
        r=requests.get(url,timeout=25); s=BeautifulSoup(r.text,'html.parser')
        for node in s.select('script,style,nav,footer'):node.decompose()
        text=s.get_text('\n',strip=True)
        path=ROOT/f'seller_{i}.txt'; path.write_text(text)
        (ROOT/f'seller_{i}.html').write_text(r.text)
        links=[{'text':a.get_text(' ',strip=True)[:80],'url':urljoin(r.url,a['href'])} for a in s.select('a[href]')]
        index.append({'url':r.url,'status':r.status_code,'file':path.name,'sha256_html':hashlib.sha256(r.content).hexdigest(),'links':links})
        print(r.status_code,r.url,len(text))
    except requests.RequestException as e:
        index.append({'url':url,'error':type(e).__name__}); print(url,type(e).__name__)
(ROOT/'SELLER_SOURCES.json').write_text(json.dumps(index,indent=2))
