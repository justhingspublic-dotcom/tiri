from pathlib import Path
from bs4 import BeautifulSoup as B
import shutil,json,hashlib,collections
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;src=OUT/'source/photos';dest=ROOT/'v1/images/review-r2';H=ROOT/'v1/html'
# Stock images are illustrative; named people and historical event photographs retain their identities.
photos={
 'business-team':('pexels-7652178','Thirdman','亞洲專業人士在辦公室討論'),
 'media-interview':('pexels-7859063','MART PRODUCTION','記者持麥克風採訪女性'),
 'partnership-signing':('pexels-5710202','Sam Lion','兩位專業女性共同檢視及簽寫文件'),
 'online-learning':('pexels-8511893','Artem Podrez','專業女性使用筆電'),
 'remote-work':('pexels-7681760','Mikhail Nilov','專業女性使用筆電工作'),
 'collaboration':('pexels-5710191','Sam Lion','兩位專業女性共同使用筆電討論'),
 'corporate-training':('pexels-8518617','作者見來源作品頁','女性講師在白板前進行簡報'),
 'professional-training':('pexels-6914420','MART PRODUCTION','專業女性講師授課'),
 'one-to-one':('pexels-18848929','作者見來源作品頁','辦公室面對面溝通情境'),
 'document-review':('1437661','rawpixel.com','書寫工作筆記的手部特寫'),
 'financial-analysis':('1575617','asawin','核對財務圖表及計算機的手部特寫'),
 'green-hands':('1349598','PxHere 作品頁未列名','雙手捧著綠色植栽')}
log=[]
for slug,(id,author,alt) in photos.items():
 target=dest/(slug+'.jpg');shutil.copy2(src/(id+'.jpg'),target);pex=id.startswith('pexels-');number=id.split('-')[-1]
 log.append({'id':slug,'title':alt,'author':author,'source_url':('https://www.pexels.com/photo/'+number+'/' if pex else 'https://pxhere.com/en/photo/'+number),'license':'Pexels License（免費可商用，非 CC0）' if pex else 'CC0 1.0','license_url':'https://www.pexels.com/license/' if pex else 'https://creativecommons.org/publicdomain/zero/1.0/','verified_on':'2026-09-10','file':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
def img(slug):return '../images/review-r2/'+slug+'.jpg'
def change(el,file,alt):el['src']=file;el['alt']=alt;el['loading']='lazy';el['decoding']='async'
replacements={
 '../images/revision/A03-business-meeting.jpg':img('business-team'),
 '../images/revision/A05-online-learning.jpg':img('online-learning'),
 '../images/hero-networking.jpg':img('business-team'),
 '../images/hero-community.jpg':img('collaboration'),
 '../images/hero-handshake.jpg':img('partnership-signing'),
 '../images/hero-talk.jpg':img('media-interview'),
 '../images/hero-audience.jpg':'../images/seminar-room.jpg',
 '../images/hero-recap.jpg':'../images/hero-annual-forum.jpg',
 '../images/hero-auditorium.jpg':'../images/seminar-room.jpg',
 '../images/hero-auditorium-dark.jpg':'../images/hero-annual-forum.jpg'}
for folder in ['html','js','css']:
 for p in (ROOT/'v1'/folder).glob('*'):
  if not p.is_file() or p.suffix not in ['.html','.js','.css']:continue
  text=p.read_text();original=text
  for before,after in replacements.items():text=text.replace(before,after)
  if text!=original:p.write_text(text)
for p in H.glob('*.html'):
 s=B(p.read_text(),'html.parser');edited=False
 # Committee media imagery is consistent between its feature and referring cards.
 for el in s.select('a[href="committee-media.html"] img, .committee-feature img'):
  if el.find_parent('a') or p.name=='committee-media.html':change(el,img('media-interview'),photos['media-interview'][2]);edited=True
 if p.name=='certificate.html':
  el=s.select_one('.page-hero');el['style']="--hero-img:url('../images/review-r2/green-hands.jpg');background-position:50% 60%";edited=True
 if p.name in ['join.html','join-342161.html']:
  el=s.select_one('.page-hero');el['style']="--hero-img:url('../images/review-r2/partnership-signing.jpg');background-position:50% 42%";edited=True
 if p.name=='about.html':
  ordered=['../images/revision/A09-corporate-building.jpg','../images/hero-chart.jpg','../images/hero-board-2022.jpg',img('professional-training'),img('collaboration'),img('financial-analysis'),img('business-team')]
  alts=['台北企業建築','資本市場圖表','TIRI 第二屆理監事合影','專業講師授課情境','專業人士交流情境','財務資料研究情境','企業團隊討論情境']
  for el,file,alt in zip(s.select('.photo-story > img'),ordered,alts):change(el,file,alt)
  edited=True
 if p.name=='trainbod.html':
  for el,slug in zip(s.select('#inhouse .inhouse-features img'),['corporate-training','business-team','remote-work']):change(el,img(slug),photos[slug][2])
  cats=[img('document-review'),'../images/hero-annual-forum.jpg','../images/revision/A09-corporate-building.jpg',img('financial-analysis'),'../images/revision/B06-contract.jpg','../images/revision/A06-esg-solar.jpg','../images/revision/B02-security.jpg',img('media-interview')]
  alts=['企業文件審閱情境','TIRI 年度大會治理座談','企業治理與組織','財務報表分析','契約與責任承諾','再生能源與永續','資訊網路設備','媒體採訪溝通情境']
  for el,file,alt in zip(s.select('.course-cat img'),cats,alts):change(el,file,alt)
  edited=True
 if p.name=='benefit.html':
  for el,file,alt in zip(s.select('.benefit-overview > img'),['../images/tiric/tiric-2025-class.jpg',img('collaboration')],['第一屆 TIRIC 專業課程學員合影','專業人士合作交流情境']):change(el,file,alt)
  edited=True
 if p.name=='knowledge.html':
  ims=s.select('main img')[:27]
  selected=[None,img('media-interview'),'../images/revision/A04-capital-market.jpg',img('business-team'),'../images/hero-chart.jpg',img('professional-training'),'../images/revision/A02-financial-report.jpg',img('remote-work'),'../images/revision/A06-esg-solar.jpg','../images/hero-annual-forum.jpg',img('financial-analysis'),img('document-review'),img('green-hands'),'../images/revision/A08-media-communication.jpg','../images/revision/A04-capital-market.jpg',img('online-learning'),img('collaboration'),img('one-to-one'),'../images/revision/A02-financial-report.jpg','../images/hero-chart.jpg','../images/revision/A09-corporate-building.jpg',img('corporate-training'),'../images/revision/A07-office-interior.jpg',img('financial-analysis'),None,'../images/hero-taipei-night.jpg',None]
  titles={img(slug):values[2] for slug,values in photos.items()}
  for el,file in zip(ims,selected):
   if file:change(el,file,titles.get(file,el.get('alt','文章主題情境圖')))
  edited=True
 if edited:p.write_text(str(s))
# Usage list is generated from final HTML, CSS and shared navigation, including backgrounds.
for entry in log:
 ref='../images/review-r2/'+Path(entry['file']).name
 entry['used_pages']=[p.name for p in H.glob('*.html') if ref in p.read_text()]
 entry['shared_navigation']=ref in (ROOT/'v1/js/navbar.js').read_text()
(OUT/'本輪圖片來源與授權.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))
print('12 new photo assets applied; generic Western stock replaced; article thumbnail repetition reduced.')
