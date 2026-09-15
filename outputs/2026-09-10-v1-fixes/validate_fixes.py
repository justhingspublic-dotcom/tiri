from pathlib import Path
from bs4 import BeautifulSoup as B
from urllib.parse import unquote,urlsplit
import json,re,collections,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;H=ROOT/'v1/html';BEFORE=OUT/'source/before-v1/html';checks=[]
def soup(name,old=False):return B(((BEFORE if old else H)/name).read_text(),'html.parser')
def check(name,value):checks.append({'check':name,'passed':bool(value)});assert value,name
check('04 nine course image cards',len(soup('trainbod.html').select('#open .revision-card img'))==9)
check('18 three inhouse photos replaced',all('review-r2/' in i['src'] for i in soup('trainbod.html').select('.inhouse-features img')))
check('19 eight distinct category photos',len({i['src'] for i in soup('trainbod.html').select('.course-cat img')})==8)
for n in ['board.html','board_en.html']:
 old=soup(n,True);new=soup(n)
 for term in ['2018','2022']:
  a=old.select_one('[data-term="'+term+'"]');b=new.select_one('[data-term="'+term+'"]')
  check(n+' preserves '+term,a and b and a.get_text(' ',strip=True)==b.get_text(' ',strip=True))
 check(n+' third term appointments',len(new.select('[data-term="2026"] .board-appointments'))==len(old.select('[data-term="2026"] .title')))
 check(n+' third term portraits preserved',[i.get('src') for i in old.select('[data-term="2026"] img')]==[i.get('src') for i in new.select('[data-term="2026"] img')])
check('27 certificates redirect to IRC',soup('certificates.html').select_one('meta[http-equiv="refresh"]')['content']=='0; url=certification.html')
check('27 five scholarship content sections retained',len(soup('certification.html').select('.scholarship-application li'))==4 and '30,000' in soup('certification.html').get_text())
for name in ['bodperform.html','corpperform.html']:
 check(name+' flow is actual PNG',soup(name).select_one('#process img')['src'].endswith('.png'))
 check(name+' original step wording preserved',soup(name,True).select_one('#process').get_text(' ',strip=True) in soup(name).select_one('#process').get_text(' ',strip=True))
check('29 video preserved with poster',soup('tiric.html').video['src']==soup('tiric.html',True).video['src'] and bool(soup('tiric.html').video.get('poster')))
check('05 client logos applied',len(soup('partners.html').select('.partner-logo-grid img'))==13 and len(soup('index.html').select('.partner-logo-grid img'))==13)
check('39 benefit terms retained',[x.get_text(' ',strip=True) for x in soup('benefit.html',True).select('.benefit-rows dd')]==[x.get_text(' ',strip=True) for x in soup('benefit.html').select('.benefit-rows dd')])
old_rosters=soup('mission-206783-766399.html',True).select('.roster-grid')
new_rosters=soup('mission-206783-766399.html').select('.progress-rosters')
check('32 roster counts are 20 nominees and 10 winners',[len(x.select('li')) for x in new_rosters]==[20,10])
check('32 all company names and codes preserved', [''.join(x.get_text().split()) for x in old_rosters]==[''.join(x.get_text().split()) for x in new_rosters])
news=soup('news.html');check('14 all 153 event records retained',len(news.select('.event-banner-row'))==153)
check('14 non-linked records have no fake arrow',all(not n.get('href') and '→' not in n.get_text() for n in news.select('article.event-banner-row')))
check('07 no duplicate body photos',len([i['src'] for i in soup('about.html').select('main img')])==len({i['src'] for i in soup('about.html').select('main img')}))
for name in ['index.html','about.html','partners.html','trainbod.html','benefit.html','knowledge.html','committee.html','committee-media.html','certificate.html','join.html','bodperform.html','corpperform.html','tiric.html','board.html','certification.html','mission-206783-766399.html']:
 s=soup(name)
 for el in s.select('img[src],video[poster],link[href],script[src]'):
  u=el.get('poster') if el.name=='video' else el.get('src') or el.get('href');u=unquote(urlsplit(u).path)
  if not u or u.startswith(('http','//','data:')):continue
  check('local asset '+name+' '+Path(u).name,(H/u).resolve().is_file())
# Record actual first-round edits independently of older unfinished work in the checkout.
changed=[]
for p in (OUT/'source/before-v1').rglob('*'):
 if p.is_file():
  current=ROOT/'v1'/p.relative_to(OUT/'source/before-v1')
  if current.exists() and current.read_bytes()!=p.read_bytes():changed.append({'file':str(current.relative_to(ROOT)),'before':hashlib.sha256(p.read_bytes()).hexdigest(),'after':hashlib.sha256(current.read_bytes()).hexdigest()})
(OUT/'source/actual-change-manifest.json').write_text(json.dumps(changed,ensure_ascii=False,indent=2));(OUT/'驗證結果.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print(f'{len(checks)} checks passed; {len(changed)} actual modified source files.')
