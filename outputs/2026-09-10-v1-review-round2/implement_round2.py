"""Apply round-two feedback once, using the recorded pre-change snapshot."""
from pathlib import Path
from bs4 import BeautifulSoup as B
from html import escape as E
import json, shutil
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
BEFORE=OUT/'source/before-v1'; HTML=ROOT/'v1/html'; assets=ROOT/'v1/images/review-r3'
def read(name): return B((BEFORE/'html'/name).read_text(),'html.parser')
def write(name,s): (HTML/name).write_text(str(s))
def frag(t): return B(t,'html.parser')
# 05: match the ten benefit partners exactly; use original transparent or vector assets.
for name in ['index.html','partners.html']:
 s=read(name);g=s.select_one('.partner-logo-grid')
 for extra in g.select('.partner-logo-item'):extra.decompose()
 for a in g.find_all('a',recursive=False):
  im=a.find('img')
  if im:im['src']=im['src'].replace('review-r2/logos','review-r3/logos')
  else:
   a.select_one('.partner-wordmark').replace_with(frag('<img src="../images/review-r3/logos/amazing.svg" alt="精彩創意整合行銷 Logo" width="140" height="60" loading="lazy">').img)
 write(name,s)
# 04: two specifically rejected theme photos.
s=read('trainbod.html')
for index,src,alt in [(4,'integrity.jpg','辦公桌上的公正天秤，象徵誠信與公平經營'),(7,'press-microphones.jpg','新聞採訪麥克風，象徵媒體應對與危機溝通')]:
 im=s.select('.course-cat img')[index];im['src']='../images/review-r3/'+src;im['alt']=alt;im['width']='1600';im['height']='1067'
write('trainbod.html',s)
# 07 and 10: actual TIRI activity photo; remove repeated decorative committee photos from navigation and detail introductions.
s=read('about.html');im=s.select('.photo-story > img')[-1];im['src']='../images/hero-annual-forum.jpg';im['alt']='TIRI 年度大會座談交流紀錄';im['width']='1100';im['height']='733'
for im in s.select('.revision-cards img'):im.decompose()
write('about.html',s)
for p in (BEFORE/'html').glob('committee-*.html'):
 s=read(p.name)
 for im in s.select('.committee-more img,.committee-feature > img'):im.decompose()
 if s.select_one('.committee-feature'):s.select_one('.committee-feature')['class'].append('committee-introduction')
 write(p.name,s)
# 39: one partner per row, with a compact summary and every original condition intact.
s=read('benefit.html');offers=s.select_one('.benefit-offers-grid');offers['class']=['benefit-rows','partner-offer-list']
labels=['定價 9 折','定價 88 折','法說會 9 折＋顧問諮詢','定價 75 折','定價 9 折＋試用／教學','優惠價再 9 折','住宿優惠＋延後退房','購課滿額贈','會員專屬旅遊優惠','會員專屬服務優惠']
slugs=['mz','writepath','amazing','notified','mpinfo','businessweekly','hubhotel','hi','discovered','interinfo']
for i,row in enumerate(offers.find_all('div',recursive=False)):
 dt=row.find('dt');dd=row.find('dd');row['class']=['partner-offer'];dt['class']=['partner-identity']
 link=dt.a.extract();dt.clear();dt.append(frag(f'<span class="partner-number">{i+1:02}</span>').span)
 ext='svg' if slugs[i]=='amazing' else 'png'
 dt.append(frag(f'<img src="../images/review-r3/logos/{slugs[i]}.{ext}" alt="" loading="lazy" width="240" height="90">').img);dt.append(link)
 dd['class']=['partner-terms'];head=frag(f'<p class="offer-summary">{labels[i]}</p>').p;label=frag('<span class="offer-label">服務內容與優惠條件</span>').span
 dd.insert(0,label);dd.insert(0,head)
 if i==5:
  for br in list(dd.find_all('br')):br.replace_with(frag('<br>'))
# Use a semantic definition list, retaining the existing IDs and outbound URLs.
offers.name='dl'
write('benefit.html',s)
# Flow images: deterministic SVG diagrams with selectable text; full-size exports and mobile versions.
def flow_svg(labels,title,vertical):
 n=len(labels);w=640 if vertical else 1440;h=112+n*120 if vertical else 320
 a=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title"><title id="title">{E(title)}</title><rect width="100%" height="100%" fill="#faf9fb"/><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="#846791" stroke-width="1.5"/></marker></defs><g font-family="Noto Sans TC, PingFang TC, Microsoft JhengHei, sans-serif"><text x="32" y="46" fill="#503660" font-size="23" font-weight="600">{E(title)}</text><path d="M32 65H{w-32}" stroke="#d9cedf"/>']
 for i,label in enumerate(labels):
  if vertical:
   x=32;y=88+i*120;bw=w-64;bh=88
   if i<n-1:a.append(f'<path d="M{w/2} {y+bh}V{y+110}" stroke="#846791" stroke-width="1.8" marker-end="url(#arrow)"/>')
   a.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="3" fill="white" stroke="#cfc0d7"/><rect x="{x}" y="{y}" width="72" height="{bh}" fill="#ede5f1"/><text x="{x+36}" y="{y+53}" text-anchor="middle" fill="#59396b" font-size="25">{i+1:02}</text><text x="{x+96}" y="{y+51}" fill="#29232e" font-size="22">{E(label)}</text>')
  else:
   bw=(w-64-(n-1)*42)/n;x=32+i*(bw+42);y=102;bh=150
   if i<n-1:a.append(f'<path d="M{x+bw+6} {y+75}H{x+bw+32}" stroke="#846791" stroke-width="1.8" marker-end="url(#arrow)"/>')
   a.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="3" fill="white" stroke="#cfc0d7"/><path d="M{x} {y}h{bw}" stroke="#614373" stroke-width="4"/><text x="{x+24}" y="{y+49}" fill="#8a7098" font-size="25">{i+1:02}</text><text x="{x+24}" y="{y+106}" fill="#29232e" font-size="27" font-weight="500">{E(label)}</text>')
 a.append('</g></svg>');return ''.join(a)
for name,slug,title in [('bodperform.html','board-flow','董事會績效評估流程'),('corpperform.html','governance-flow','提升公司治理服務流程')]:
 s=read(name);labels=[x.get_text(strip=True) for x in s.select('.flow-text-equivalent .label')];vertical=len(labels)>4
 for suffix,v in [('',vertical),('-mobile',True)]: (assets/(slug+suffix+'.svg')).write_text(flow_svg(labels,title,v))
 f=s.select_one('.flow-figure');f.clear();f.append(frag(f'<a href="../images/review-r3/{slug}.svg" target="_blank" rel="noopener" aria-label="開啟{title}完整圖片"><picture><source media="(max-width: 640px)" srcset="../images/review-r3/{slug}-mobile.svg"><img class="flow-image professional-flow" src="../images/review-r3/{slug}.svg" width="{640 if vertical else 1440}" height="{832 if vertical else 320}" alt="{title}：'+ ' → '.join(labels)+'"></picture></a>').a)
 f.append(frag('<figcaption>依編號順序進行。點選流程圖可開啟完整圖片。</figcaption>').figcaption);write(name,s)
# 06: protect faces in scene photos. Apply layout rules through classes instead of editing the originals.
portrait=['professional-training.jpg','remote-work.jpg','corporate-training.jpg','online-learning.jpg']
for p in HTML.glob('*.html'):
 s=B(p.read_text(),'html.parser');changed=False
 for im in s.select('img[src*="review-r2/"]'):
  if '/logos/' in im['src']:continue
  if any(im['src'].endswith(x) for x in portrait):
   im['class']=list(set(im.get('class',[])+['scene-portrait-safe']));changed=True
  elif im.parent.get('class') and any(x in im.parent['class'] for x in ['photo-story','inhouse-feature','insight-card']):
   im['class']=list(set(im.get('class',[])+['scene-full-frame']));changed=True
 if changed:p.write_text(str(s))
print('Applied pages, logos, partner layout, formal flow diagrams and crop protection.')
