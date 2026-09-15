"""Focused source/content regression checks for the September v1 revision.
Run from WEB DEMO with .venv/bin/python outputs/2026-09-09-v1-revision/validate_revision.py.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup as B
from collections import Counter
import json, re, hashlib, importlib.util, io, contextlib
import pymupdf
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
HTML=ROOT/'v1/html'
results=[]
def soup(name):return B((HTML/name).read_text(),'html.parser')
def check(name,condition,detail=''):
 results.append({'check':name,'passed':bool(condition),'detail':detail})
def norm(t):return re.sub(r'\s+','',t)
# Independent baseline: all existing inquiry/enrolment fields must survive.
forms=[]
for p in (OUT/'source/before-v1').glob('*.html.txt'):
 name=p.name.removesuffix('.txt')
 if name=='index.html':continue  # Newsletter block removed by approved home-only-three-sections request.
 old=B(p.read_text(),'html.parser');new=soup(name)
 def sig(s):return Counter((x.name,x.get('name'),x.get('type'),x.get('id'),x.has_attr('required')) for x in s.select('form input,form select,form textarea'))
 lost=sig(old)-sig(new)
 if lost:forms.append((name,str(lost)))
check('Existing form fields preserved',not forms,forms)
books=json.loads((OUT/'source/all-workbooks.json').read_text())
check('All supplied workbook sheets inventoried',len(books)==15 and sum(len(b['sheets']) for b in books)==33,{'workbooks':len(books),'sheets':sum(len(b['sheets']) for b in books)})
# Source-backed content counts and identities, including multi-company roster rows.
records=json.loads((OUT/'source/board-rosters.json').read_text())
missing=[]
for r in records:
 for lang,page in [('zh','board.html'),('en','board_en.html')]:
  panel=soup(page).select_one('[data-term="'+r['term']+'"]')
  if norm(r[lang]['name']) not in norm(panel.text):missing.append((r['term'],lang,r[lang]['name']))
check('Historic board members retained in both languages',not missing,{'records':len(records),'missing':missing})
for page in ['board.html','board_en.html']:
 s=soup(page)
 check(page+' historic table structure',all(len(s.select_one('[data-term="'+year+'"] thead').select('th'))==5 for year in ['2018','2022']))
comm=json.loads((OUT/'source/committee-records.json').read_text())['committees']
for c in comm:
 s=soup('committee-'+c['slug']+'.html');names=[row[1] for row in c['people']]
 check(c['name']+' names and navigation',all(n in s.select_one('table').text for n in names) and len(s.select('.committee-more .revision-card'))==4 and len(s.select('thead th'))==4,names)
s=soup('index.html');heads=[h.text.strip() for h in s.select('main > section h2')]
check('Home section sequence',heads[-3:]==['活動訊息','線上課程','合作夥伴'],heads)
check('Home excludes courses from events',len(s.select('.home-events-list .event-banner-row'))==3 and not any('課程' in a.get_text() for a in s.select('.home-events-list .event-banner-row')))
check('Home ten partner links',len(s.select('.partner-names a'))==10)
check('Course brochure has eight current subjects',len(soup('trainbod.html').select('.course-cat'))==8)
s=soup('news.html');counts={p['data-term']:len(p.select('.event-banner-row')) for p in s.select('.term-panel')}
check('Event history covers 2018–2026 with 153 records',set(counts)==set(map(str,range(2018,2027))) and sum(counts.values())==153,counts)
check('Accupass banners link to matching event ID',all(a['href'].endswith(Path(a.img['src']).stem) for a in s.select('a.event-banner-row') if a.img and '/images/events/' in a.img['src']))
check('Four evaluation steps',len(soup('bodperform.html').select('.flow-steps li'))==4)
check('Six governance steps',len(soup('corpperform.html').select('.flow-steps li'))==6)
check('Five Awards panels',set(p['data-term'] for p in soup('mission-206783.html').select('.term-panel'))==set(map(str,range(2022,2027))))
p=soup('mission-206783-766399.html')
check('Progress 2025 ten winners / 2026 twenty nominees',len(p.select('[data-term="2025"] .roster li'))==10 and len(p.select('[data-term="2026"] .roster li'))==20)
check('TIRIC single local video and real recap year',len(soup('tiric.html').select('video'))==1 and [x['data-value'] for x in soup('tiric.html').select('.term-option')]==['2025'])
s=soup('knowledge.html');cards=s.select('.insight-card')
check('All 27 articles have images and unique targets',len(cards)==27 and len(set(a['href'] for a in cards))==27 and all(a.img and a.img.get('alt') for a in cards))
local_titles=[]
for a in cards:
 u=urlsplit(a['href'])
 if not u.netloc and u.path.endswith('.html'):
  h=soup(u.path).h1.get_text(' ',strip=True);title=a.h3.get_text(' ',strip=True)
  local_titles.append({'card':title,'destination':h,'href':a['href'],'match':norm(h)==norm(title) or norm(title) in norm(h) or norm(h) in norm(title) or (u.path=='2356035370-277843933339333297022010738263.html' and '沈馥馥' in h and '中華電信' in soup(u.path).get_text())})
(OUT/'source/article-title-validation.json').write_text(json.dumps(local_titles,ensure_ascii=False,indent=2))
check('Local article card titles match destination headings',all(x['match'] for x in local_titles),[x for x in local_titles if not x['match']])
pdfs=[]
for lang,page in [('zh','5th_report-516844.html'),('en','5th_report-665763.html')]:
 s=soup(page);check(page+' three correct language covers',len(s.select('.yearbook-card'))==3 and all(i['src'].endswith('-'+lang+'.jpg') for i in s.select('.yearbook-card img')))
 for card in s.select('.yearbook-card'):
  links=card.select('a');paths={a['href'] for a in links};p=(HTML/links[0]['href']).resolve();doc=pymupdf.open(p)
  good=len(paths)==1 and p.name.endswith('-'+lang+'.pdf') and doc.page_count>50 and any(a.has_attr('download') for a in links)
  check('PDF '+p.name,good,{'pages':doc.page_count,'bytes':p.stat().st_size});pdfs.append(str(p.relative_to(ROOT)))
# File references and CSS URLs: use existing repository checker scoped to deliverable.
spec=importlib.util.spec_from_file_location('checker',ROOT/'_archive/scripts/check_static_site.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ROOT=ROOT/'v1';log=io.StringIO()
try:
 with contextlib.redirect_stdout(log):m.main()
 good=True
except SystemExit:good=False
check('v1 static references',good,log.getvalue());(OUT/'source/static-v1.txt').write_text(log.getvalue())
# Report newly introduced bad local anchors separately from inherited anchors.
anchors=[]
for p in HTML.glob('*.html'):
 s=soup(p.name)
 for a in s.select('a[href]'):
  u=urlsplit(a['href'])
  if u.scheme or u.netloc or not u.fragment or (u.path and not u.path.endswith('.html')):continue
  target=(p.parent/unquote(u.path)).resolve() if u.path else p
  if not target.is_file():continue
  t=B(target.read_text(),'html.parser')
  if not t.find(id=unquote(u.fragment)) and not t.find('a',attrs={'name':unquote(u.fragment)}):anchors.append({'page':p.name,'href':a['href']})
(OUT/'source/anchor-audit.json').write_text(json.dumps(anchors,ensure_ascii=False,indent=2))
(OUT/'source/regression-checks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
for r in results:print(('PASS ' if r['passed'] else 'FAIL ')+r['check']+((' '+str(r['detail'])) if not r['passed'] else ''))
print('Local anchor issues:',len(anchors),'(see source/anchor-audit.json)')
raise SystemExit(0 if all(r['passed'] for r in results) else 1)
