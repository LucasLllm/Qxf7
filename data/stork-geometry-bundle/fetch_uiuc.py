"""Download primary UIUC coordinate archive discovered from its index. No aircraft inference."""
from pathlib import Path
import requests,hashlib,json,zipfile,io
from bs4 import BeautifulSoup
from urllib.parse import urljoin
D=Path(__file__).resolve().parent/'uiuc-sources';D.mkdir(exist_ok=True)
index='https://m-selig.ae.illinois.edu/ads/coord_database.html'
r=requests.get(index,timeout=40);r.raise_for_status();(D/'coord_database.html').write_bytes(r.content)
s=BeautifulSoup(r.text,'html.parser');links=[urljoin(index,a['href']) for a in s.select('a[href]') if 'coord_seligFmt.zip' in a['href']];assert len(links)==1
u=links[0];q=requests.get(u,timeout=60);q.raise_for_status();(D/'coord_seligFmt.zip').write_bytes(q.content)
z=zipfile.ZipFile(io.BytesIO(q.content));dat=[n for n in z.namelist() if n.lower().endswith('.dat')];assert len(dat)>1000
j={'index_url':index,'index_sha256':hashlib.sha256(r.content).hexdigest(),'archive_url':u,'archive_sha256':hashlib.sha256(q.content).hexdigest(),'archive_bytes':len(q.content),'archive_dat_members':len(dat),'http_status':[r.status_code,q.status_code],'retrieval_date_header':q.headers.get('Date'),'scope':'official archive linked by current UIUC index; post-archive update files are not in this comparison corpus'}
(D/'source_receipt.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(j,indent=2))
