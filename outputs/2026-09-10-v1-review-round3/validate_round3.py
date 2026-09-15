from pathlib import Path
from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urlsplit,unquote
import json,hashlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];HTML=ROOT/'v1/html';BEFORE=OUT/'source/before-v1/html'
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
def read(path):return BeautifulSoup(path.read_text(),'html.parser')
raw=json.loads((OUT/'source/第二輪複檢結果原檔.json').read_text())
data=json.loads((OUT/'複檢資料.json').read_text())
old=json.loads((OUT.parent/'2026-09-10-v1-review-round2/複檢資料.json').read_text())
check((OUT/'source/第二輪複檢結果原檔.json').read_bytes()==Path('/Users/jonathanyu/Downloads/TIRI-v1-第二輪複檢結果.json').read_bytes(),'User input preserved byte-for-byte')
check(len(data['items'])==41 and len({i['id'] for i in data['items']})==41,'All 41 stable item IDs')
check(Counter(i['deliveryStatus'] for i in data['items'])=={'accepted':30,'ready':6,'waiting':5},'30 accepted / 6 ready / 5 waiting')
check({i['id'] for i in data['items'] if i['deliveryStatus']=='ready'}=={'04','06','07','10','14','27'},'Exactly the six feedback items reopened')
for i,r,p in zip(data['items'],raw['items'],old['items']):
    check(i['id']==r['id']==p['id'] and i['reviewHistory'][:2]==p['reviewHistory'],'Prior history intact '+i['id'])
    check(i['previousRecheck']['note']==r['note'] and i['reviewHistory'][2]['assistantResponse']==r['assistantResponse'],'Latest user note and previous response intact '+i['id'])
    route=urlsplit(i['route']); dest=HTML/unquote(route.path)
    check(dest.exists(),'Review destination exists '+i['id'])
    if route.fragment:
        anchor=read(dest).find(id=route.fragment) is not None
        if route.fragment=='footer':anchor='id="footer"' in (ROOT/'v1/js/navbar.js').read_text()
        check(anchor,'Review destination anchor exists '+i['id'])
check(next(i for i in data['items'] if i['id']=='27')['deliveryLimit']=='','Superseded cutout limitation removed from current delivery')
about=read(HTML/'about.html');before=read(BEFORE/'about.html')
check(len(about.select('.photo-story'))==6,'About stops after the sixth section')
check(not about.select('#regulatory-engagement,#team,#committee,#duns'),'Specified about tail removed')
check([x.get_text(' ',strip=True) for x in about.select('.photo-story')]==[x.get_text(' ',strip=True) for x in before.select('.photo-story')[:6]],'Kept about copy unchanged')
overview=read(HTML/'committee.html')
for card in overview.select('.revision-card'):
    route=card.get('href');img=card.select_one('img')
    if not route or not img:continue
    s=read(HTML/route);oldpage=read(BEFORE/route)
    check(s.select_one('.committee-banner-image')['src']==img['src'],'Banner matches overview '+route)
    check(s.select_one('.page-section').get_text(' ',strip=True)==oldpage.select_one('.page-section').get_text(' ',strip=True),'Roster and other committee links preserved '+route)
    check(len(s.select('.committee-more img'))==0,'Other committee navigation stays text '+route)
frames=0
for name in ['trainbod.html','knowledge.html','about.html','committee.html','benefit.html']:
    soup=read(HTML/name)
    for frame in soup.select('.blurred-photo'):
        check(frame.img['src'] in frame['style'],'Same-image blur '+name)
        frames+=1
check(frames==23,'All 23 scene frames updated')
soup=read(HTML/'tiric.html');oldtiric=read(BEFORE/'tiric.html')
check(len(soup.select('.lecturer-photo-frame.blurred-photo'))==10,'Ten lecturer frames updated')
check([(i['src'],i['alt']) for i in soup.select('.lecturer-photo-frame img')]==[(i['src'],i['alt']) for i in oldtiric.select('.lecturer-photo-frame img')],'Lecturer identities and source photos unchanged')
news=read(HTML/'news.html')
check(len(news.select('.news-recent-card'))==5,'Five future static fallback cards')
check(len(news.select('.event-banner-row'))==152,'152 archived static fallback rows')
check('即將舉行與今日活動' not in news.get_text(),'Upcoming wording matches strict date rule')
modified=set(json.loads((OUT/'source/修改頁面.json').read_text())['pages'])|{'news.html'}
for path in HTML.glob('*.html'):
    if path.name not in modified:
        check(path.read_text().replace('20260910-r8','20260910-r7')==(BEFORE/path.name).read_text(),'Unrelated page content preserved '+path.name)
    else:
        for img in read(path).select('img[src]'):
            src=img['src']
            if not src.startswith(('http','data:')):check((path.parent/unquote(urlsplit(src).path)).resolve().exists(),'Local image exists '+src)
css=(ROOT/'v1/css/review-fixes.css').read_text()
check('background-image:var(--scene-image)' in css and 'filter:blur(18px)' in css,'Blur layer rule present')
check('object-fit:contain!important' in css,'Complete foreground framing')
check('TIRI-v1-第三輪複檢結果.json' in (OUT/'recheck.js').read_text(),'Third-round export filename')
check('round:data.round' in (OUT/'recheck.js').read_text(),'Export round follows embedded data')
(OUT/'驗證結果.json').write_text(json.dumps({'passed':len(checks),'checks':checks},ensure_ascii=False,indent=2))
print(len(checks),'source, preservation, link and delivery assertions passed.')
