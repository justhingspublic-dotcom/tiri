from pathlib import Path
from bs4 import BeautifulSoup as B
from urllib.parse import urlsplit,unquote
import json,re,xml.etree.ElementTree as ET,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;old=OUT/'source/before-v1';checks=[]
def check(ok,label):
 checks.append({'check':label,'passed':bool(ok)})
 if not ok:print('FAIL',label)
def read(base,page):return B((base/'html'/page).read_text(),'html.parser')
def norm(s):return re.sub(r'\s+','',s)
raw=json.loads((OUT/'source/第一輪複檢結果原檔.json').read_text());data=json.loads((OUT/'複檢資料.json').read_text());by={x['id']:x for x in data['items']}
check(len(by)==41,'41 unique review items')
check([x['id'] for x in raw['items'] if x['confirmed']]==[x['id'] for x in data['items'] if x['reviewStatus']=='accepted'],'All 25 prior approvals retained')
for r in raw['items']:
 x=by[r['id']];check(x['previousRecheck']['note']==r.get('note','') and x['previousRecheck']['confirmed']==r['confirmed'],'Review note and confirmation retained '+r['id'])
check([x['id'] for x in data['items'] if x['reviewStatus']=='waiting']==['17','20','23','25','41'],'Same five waiting items')
for page in ['index.html','partners.html']:
 a=read(ROOT/'v1',page).select('.partner-logo-grid > a');check(len(a)==10 and all(x.img for x in a),'Ten linked logos '+page)
check({Path(i['src']).name for i in read(ROOT/'v1','partners.html').select('.partner-logo-grid img')}=={'mz.png','writepath.png','amazing.svg','notified.png','mpinfo.png','businessweekly.png','hubhotel.png','hi.png','discovered.png','interinfo.png'},'Exact ten benefit partners')
a=read(old,'benefit.html');b=read(ROOT/'v1','benefit.html')
for n in range(1,11):
 sel='#benefit-partner-'+str(n);previous=a.select_one(sel);current=b.select_one(sel)
 for e in current.select('.offer-summary,.offer-label'):e.decompose()
 check(norm(previous.dd.get_text())==norm(current.dd.get_text()) and previous.dt.a['href']==current.dt.a['href'],'Benefit terms and official link unchanged '+str(n))
for page in ['board.html','board_en.html','certification.html','certification-388672.html','mission-206783-766399.html']:
 a=read(old,page);b=read(ROOT/'v1',page);check(a.get_text()==b.get_text(),'Accepted page text preserved '+page)
for page in ['committee-certification.html','committee-awards.html','committee-professional.html','committee-media.html','committee-outreach.html']:
 a=read(old,page);b=read(ROOT/'v1',page);check([x.get_text() for x in a.select('table')]==[x.get_text() for x in b.select('table')],'Committee roster preserved '+page)
 check(len(b.select('.committee-more a'))==4 and not b.select('.committee-more img,.committee-feature img'),'Four committee links without repeated photos '+page)
for page,slug,count in [('bodperform.html','board-flow',4),('corpperform.html','governance-flow',6)]:
 a=read(old,page);labels=[e.get_text(strip=True) for e in a.select('.flow-text-equivalent .label')]
 check(len(labels)==count,'Original flow labels '+slug)
 for suffix in ['', '-mobile']:
  xml=ET.parse(ROOT/'v1/images/review-r3'/(slug+suffix+'.svg'));texts=[e.text for e in xml.findall('.//{http://www.w3.org/2000/svg}text')]
  check(all(t in texts for t in labels),'Flow text intact '+slug+suffix)
orig=read(old,'tiric.html');now=read(ROOT/'v1','tiric.html')
check(len(now.select('.lecturer-photo-frame'))==10,'Ten lecturer frames')
check([x.get_text() for x in orig.select('.lecturer-grid figcaption')]==[x.get_text() for x in now.select('.lecturer-grid figcaption')],'Lecturer names and topics unchanged')
check(dict(orig.video.attrs)==dict(now.video.attrs),'Approved TIRIC video and poster unchanged')
news=json.loads((OUT/'活動紀錄.json').read_text());source=read(old,'news.html')
check(len(news)==len(source.select('.event-banner-row'))==153,'153 activity records retained')
check(sum(not x['image'] for x in news)==17,'17 actual missing original images disclosed')
# Verify local preview routes, images and resources. External URLs are not rewritten or downloaded here.
missing=[]
for page in (ROOT/'v1/html').glob('*.html'):
 s=B(page.read_text(),'html.parser')
 for e,attr in [(e,a) for a in ['src','href','srcset'] for e in s.select('['+a+']')]:
  value=e[attr];u=urlsplit(value)
  if u.scheme or u.netloc or not u.path or value.startswith('#'):continue
  target=ROOT/unquote(u.path[1:]) if u.path.startswith('/') else page.parent/unquote(u.path)
  if not target.exists():missing.append((page.name,attr,value))
check(not missing,'All v1 local referenced files exist')
(OUT/'source/missing-references.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2))
(OUT/'驗證結果.json').write_text(json.dumps({'passed':sum(x['passed'] for x in checks),'total':len(checks),'checks':checks},ensure_ascii=False,indent=2))
print('Checks',sum(x['passed'] for x in checks),'/',len(checks),'missing',len(missing))
if not all(x['passed'] for x in checks):raise SystemExit(1)
