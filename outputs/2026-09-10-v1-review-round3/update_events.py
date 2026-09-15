"""Import the upcoming events observed on the organizer's live public page."""
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import json,subprocess
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[1]
SOURCE=OUT/'source/event-pages'; SOURCE.mkdir(exist_ok=True)
IMAGES=ROOT/'v1/images/review-r4/events'; IMAGES.mkdir(parents=True,exist_ok=True)
# Dates, names and URLs read from the live organizer DOM on 2026-09-10.
observed=[
 ('2026-09-10','2606090943198559132000','09/10 【TIRI線上董事、公司治理主管進修課程】職場霸凌防治新制簡介','14:00–17:00｜線上活動'),
 ('2026-09-18','2608180816191935448591','09/18 【TIRI線上董事、公司治理主管進修課程】營業秘密暨資訊安全教育訓練---MJIB偵辦實務分享','14:00–17:00｜線上活動'),
 ('2026-10-02','2608200546411371789803','10/02 【TIRI線上董事、公司治理主管進修課程】用價值觀 & 價值，打造 AI 時代不可複製的企業核心','14:00–17:00｜線上活動'),
 ('2026-10-16','2608261303411628089416','2026/10/16- TIRI 2026年度大會暨IR新溝通時代','14:00–18:00｜台北市'),
 ('2026-10-23','2608310146174838286100','10/23【TIRI線上董事、治理主管進修課程】ESG未來主力戰場：AI的永續治理','14:00–17:00｜線上活動'),
 ('2026-11-13','2608310252071781192101','11/13【TIRI線上董事、治理主管進修課程】商業思維，惠我良多，共創未來','14:00–17:00｜線上活動')
]
old=json.loads((OUT.parent/'2026-09-10-v1-review-round2/活動紀錄.json').read_text())
ids={r.get('href','').split('/')[-1] for r in old}
def fetch(url,dest):
    if not dest.exists():subprocess.run(['curl','--http1.1','-A','Mozilla/5.0','-L','--retry','2','--max-time','40','--fail','--silent','--show-error',url,'-o',str(dest)],check=True)
def get(row):
    date,eventid,title,description=row
    href='https://www.accupass.com/event/'+eventid
    html=SOURCE/(eventid+'.html');fetch(href,html)
    soup=BeautifulSoup(html.read_text(),'html.parser')
    meta=soup.select_one('meta[property="og:image"]')
    assert meta and meta.get('content'),eventid
    banner=meta['content']
    original=SOURCE/(eventid+'.jpg'); fetch(banner,original)
    dest=IMAGES/(eventid+'.jpg')
    if not dest.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(original),'-vf',"scale='min(1200,iw)':-1",'-q:v','2',str(dest)],check=True)
    size=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',str(dest)]))['streams'][0]
    record={'date':date,'title':title,'description':description,'href':href,'image':{'src':'../images/review-r4/events/'+dest.name,'alt':title,**size}}
    return record,{'event':href,'banner':banner,'date':date,'title':title,'source':'Accupass live organizer + original event og:image','localImage':str(dest.relative_to(ROOT))}
new=[]; provenance=[]
with ThreadPoolExecutor(max_workers=4) as pool:
    for record,source in pool.map(get,[r for r in observed if r[1] not in ids]):new.append(record);provenance.append(source)
events=old+new
(OUT/'活動紀錄.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
(OUT/'source/Accupass核對紀錄.json').write_text(json.dumps({'checkedOn':'2026-09-10','organizer':'https://www.accupass.com/organizer/detail/1905200944211623899120','observedUpcoming':observed,'added':provenance,'rule':'date > today in Asia/Taipei; today and earlier stay in archive','originalCount':len(old),'totalCount':len(events)},ensure_ascii=False,indent=2))
path=ROOT/'v1/html/news.html'; soup=BeautifulSoup(path.read_text(),'html.parser')
soup.select_one('#news-events').string=json.dumps(events,ensure_ascii=False).replace('<','\\u003c')
path.write_text(str(soup))
path=ROOT/'v1/js/news-round2.js'
path.write_text(path.read_text().replace('event.date >= today','event.date > today').replace('event.date < today','event.date <= today'))
print('Added',len(new),'events; preserved',len(old),'original records; total',len(events))
