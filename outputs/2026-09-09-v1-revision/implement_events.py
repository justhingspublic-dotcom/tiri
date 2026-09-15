from revision_helpers import *
from collections import defaultdict

meta={r['url']:r for r in json.loads((OUT/'source/event-banner-map.json').read_text())}
def data_for(a,category=None):
    d=a.select_one('.date');year=d.select_one('.yr').get_text() if d and d.select_one('.yr') else ''
    y=re.search(r'20\d\d',year)
    date=''.join(t for t in d.find_all(string=True,recursive=False)).strip() if d else ''
    md=re.search(r'(\d\d)[./](\d\d)',date)
    if not y or not md:return None
    url=a.get('href','').split('?')[0];m=meta.get(url,{})
    tag=a.select_one('.tag');loc=a.select_one('.mono-meta')
    row={'year':y.group(),'month':md[1],'day':md[2],'title':a.h3.get_text(' ',strip=True),'href':url,'category':category or (tag.get_text(' ',strip=True) if tag else '活動'),'location':loc.get_text(' ',strip=True) if loc else '', 'image':m.get('image')}
    if row['category']=='報名中':row['category']='董監進修課程'
    for obj in m.get('structured',[]):
        if obj.get('@type')=='Event' and obj.get('startDate'):
            row['date_source']=obj['startDate'];row['year'],row['month'],row['day']=obj['startDate'][:10].split('-')
            row['source_title']=obj.get('name')
    row['date']='-'.join([row['year'],row['month'],row['day']]);return row

rows=[];seen=set()
s=read('news.html')
for a in s.select('.event-item'):
    r=data_for(a)
    if r and (r['href'] or r['title']) not in seen:rows.append(r);seen.add(r['href'] or r['title'])
annualurl='https://www.accupass.com/event/2608261303411628089416'
rows.append({'year':'2026','month':'10','day':'16','date':'2026-10-16','title':'2026 年度大會暨 IR 新溝通時代','href':annualurl,'category':'年度大會','location':'台北','image':meta.get(annualurl,{}).get('image')})
# Preserve annual conference records that only existed on the former events page.
old=read('events.html')
for a in old.select('#recap .event-item'):
    r=data_for(a,'年度大會花絮')
    if r and not any(x['date']==r['date'] and '年度大會' in x['category'] for x in rows):
        linked=read(r['href']);img=linked.select_one('main img')
        if img:r['image']=img['src']
        rows.append(r)
rows.sort(key=lambda r:r['date'],reverse=True)
(OUT/'source/merged-events.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))

def render_row(r,home=False):
    external=r['href'].startswith('http');attrs=' target="_blank" rel="noopener"' if external else ''
    image=f'<img src="{r["image"]}" alt="{E(r["title"])}活動主視覺" loading="lazy" decoding="async">' if r.get('image') else ''
    date=(r['month']+'.'+r['day']+f'<small>{r["year"]}</small>') if home else r['day']
    time=f'<time datetime="{r["date"]}" aria-label="{r["date"]}">{date}</time>'
    tag='a' if r['href'] else 'article'
    return f'<{tag} class="event-banner-row'+(' no-banner' if not image else '')+f'" href="{E(r["href"])}"{attrs}>{image}{time}<div><h3>{E(r["title"])}</h3><p>{E(r["category"])}'+(' · '+E(r['location']) if r['location'] else '')+(' · 活動資訊 ↗' if external else ' · 活動花絮 →')+f'</p></div></{tag}>'

s=read('news.html');s.h1.string='活動訊息';s.title.string='活動訊息｜台灣投資人關係協會 TIRI'
for sec in s.select('main > section:not(.page-hero)'):sec.decompose()
years=sorted(set(r['year'] for r in rows),reverse=True)
section=fragment('<section class="page-section" id="archive"><div class="container"><div class="section-head"><div><p class="eyebrow">News &amp; Events</p><h2>活動與歷年紀錄</h2></div><a class="u-link" href="news-971146.html">活動花絮 →</a></div></div></section>').section
container=section.select_one('.container');pick=picker([(y,y+' 年') for y in years]);pick.select_one('.term-bar-label').string='年度';container.append(pick)
for y in years:
    groups=defaultdict(list)
    for r in rows:
        if r['year']==y:groups[r['month']].append(r)
    panel=fragment(f'<div class="term-panel" data-term="{y}" id="year-{y}"'+(' hidden' if y!=years[0] else '')+'></div>').div
    for month,items in sorted(groups.items(),reverse=True):panel.append(fragment(f'<section class="month-group"><h3 class="month-heading">{y}<strong>{month}<small>月</small></strong></h3><div>'+''.join(render_row(r) for r in items)+'</div></section>'))
    container.append(panel)
container.append(fragment('<p class="note"><a class="u-link" href="https://www.accupass.com/organizer/detail/1905200944211623899120" target="_blank" rel="noopener">更多活動與報名資訊（Accupass）↗</a></p>'))
s.main.append(section)
# Preserve useful legacy course anchors as explicit links, without a second listing.
s.main.append(fragment('<section class="page-section"><div class="container"><div class="revision-cards"><div id="tiric"><h2>TIRIC</h2><p><a class="u-link" href="tiric.html">IR 專業實戰班 →</a></p></div><div id="training"><h2>課程與服務</h2><p><a class="u-link" href="trainbod.html">董監事與公司治理主管進修 →</a></p></div><div id="irc"><h2>IRC</h2><p><a class="u-link" href="certification.html">國際證照與獎學金 →</a></p></div></div><p id="recap" style="margin-top:40px"><a class="u-link" href="news-971146.html">查看歷年活動花絮 →</a></p></div></section>'))
put('news.html',s)
redirect('events.html','news.html','活動訊息')
# Retain the meaningful old hash when someone follows a saved course anchor.
e=BS((HTML/'events.html').read_text(),'html.parser');e.body.append(fragment('<script>location.replace("news.html" + location.hash);</script>'));put('events.html',e)

s=read('index.html');sections=s.select('main > section')
for sec in sections[2:]:sec.decompose()
for a in s.select('a[href="#events"]'):a['href']='news.html'
event_rows=[r for r in rows if not any(t in r['category'] for t in ['課程','TIRIC','講座']) and '課程' not in r['title']][:3]
s.main.append(fragment('<section class="home-section" id="events"><div class="container"><div class="section-head"><div><p class="eyebrow">News &amp; Events</p><h2>活動訊息</h2></div><a class="head-link u-link" href="news.html">所有活動 →</a></div><div class="home-events-list">'+''.join(render_row(r,True) for r in event_rows)+'</div></div></section>'))
course_rows=[r for r in rows if '課程' in r['category'] and '線上' in r['location']][:6]
s.main.append(fragment('<section class="home-section" id="courses"><div class="container"><div class="section-head"><div><p class="eyebrow">Online Courses</p><h2>線上課程</h2></div><a class="head-link u-link" href="trainbod.html#open">所有課程 →</a></div><div class="revision-cards">'+''.join(f'<a class="revision-card" href="{E(r["href"])}" target="_blank" rel="noopener"><img src="{r["image"]}" alt="{E(r["title"])}課程主視覺" style="object-fit:contain;background:#fff" loading="lazy"><div><p class="eyebrow">{r["date"]} · 線上</p><h3>{E(r["title"])}</h3><p>查看課程資訊 ↗</p></div></a>' for r in course_rows)+'</div></div></section>'))
partners=json.loads((OUT/'source/partner-links.json').read_text())
s.main.append(fragment('<section class="home-section" id="partners"><div class="container"><div class="section-head"><div><p class="eyebrow">Our Partners</p><h2>合作夥伴</h2></div><a class="head-link u-link" href="partners.html">了解合作夥伴 →</a></div><div class="partner-names">'+''.join(f'<a href="{E(r["url"])}" target="_blank" rel="noopener">{E(r["name"])} <span aria-hidden="true">↗</span></a>' for r in partners)+'</div></div></section>'))
put('index.html',s)
print('Merged events:',len(rows),'years',years,'home activities',len(event_rows),'online courses',len(course_rows))
