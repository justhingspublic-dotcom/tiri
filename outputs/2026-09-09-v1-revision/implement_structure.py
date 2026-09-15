"""Apply the approved structural revisions. Source snapshots make reruns deterministic."""
from pathlib import Path
from bs4 import BeautifulSoup as BS
from html import escape as E
import re, json, subprocess, shutil
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BEFORE = OUT/'source/before-v1'
HTML = ROOT/'v1/html'

def read(name):
    return BS((BEFORE/name).read_text(), 'html.parser')

def fragment(text):
    return BS(text, 'html.parser')

def put(name, soup):
    if not soup.select_one('link[href*="revision.css"]'):
        soup.head.append(fragment('<link rel="stylesheet" href="../css/revision.css?v=20260909">'))
    (HTML/name).write_text(str(soup))

def hero(soup, src, pos='50% 50%'):
    h=soup.select_one('.page-hero')
    h['class']=list(dict.fromkeys(h.get('class',[])+['has-photo']))
    h['style']=f"--hero-img: url('{src}'); background-position: {pos};"

def picker(options, selected=None):
    selected=selected or options[0][0]
    label=dict(options)[selected]
    return fragment('<div class="term-bar"><span class="term-bar-label">屆次 / Year</span><div class="term-picker" data-term-picker><button type="button" class="term-trigger" id="term-trigger" aria-haspopup="listbox" aria-controls="term-menu" aria-expanded="false"><span data-term-label>'+E(label)+'</span><span aria-hidden="true">⌄</span></button><ul class="term-menu" id="term-menu" role="listbox" aria-labelledby="term-trigger" hidden>'+''.join(f'<li class="term-option" role="option" data-value="{value}" aria-selected="{str(value==selected).lower()}">{E(label)}</li>' for value,label in options)+'</ul></div></div>')

def redirect(name, target, label, en=False):
    s=read(name)
    s.head.append(fragment(f'<meta http-equiv="refresh" content="0; url={E(target)}"><link rel="canonical" href="{E(target)}">'))
    s.main.clear()
    s.main.append(fragment(f'<section class="page-section"><div class="container"><h1>{E(label)}</h1><p><a class="btn btn-primary" href="{E(target)}">{E(label)} →</a></p></div></section>'))
    put(name,s)

# Navigation data is evaluated in isolation, not by executing the component.
js=(BEFORE/'navbar.js').read_text()
for name in ['navigation','navigationEn']:
    pat=r'var '+name+r' = (\[.*?\n  \]);'
    source=re.search(pat,js,re.S).group(1)
    nav=json.loads(subprocess.check_output(['node','-e','console.log(JSON.stringify('+source+'))'],text=True))
    en=name.endswith('En')
    idx=next(i for i,x in enumerate(nav) if x['label'] in ['證照獎項','Certification & Awards'])
    old=nav[idx]
    cert=old.copy(); cert['columns']=[old['columns'][0],{'label':'','links':[]}]
    cert.update(href='certificates_en.html' if en else 'certificates.html',label='Certification' if en else '證照')
    links=cert['columns'][0]['links']
    links[1][0]=('certification-388672.html' if en else 'certification.html')+'#scholarship'
    cert['figure']=[links[0][0],'../images/tiric/tiric-2025-class.jpg','International IR certification and practical training.' if en else '國際證照、贊助獎學金與 IR 專業實戰課程。','View Certification' if en else '查看證照']
    awards={'href':'mission-206783-396345-512343.html' if en else 'mission-206783-396345.html','label':'Awards' if en else '獎項','columns':[old['columns'][1],{'label':'','links':[]}],'figure':['mission-206783-803349.html' if en else 'mission-206783.html','../images/awards/awards-trophy.jpg','Recognizing excellence in investor relations.' if en else '肯定企業投資人關係實踐與專業成就。','View Awards' if en else '查看獎項']}
    nav[idx:idx+1]=[cert,awards]
    if not en:
        for item in nav:
            if item['label']=='活動訊息':
                item['columns'][0]['links']=[['news.html','活動訊息','協會公告、課程講座與產業參與紀錄']]
    js=re.sub(pat,'var '+name+' = '+json.dumps(nav,ensure_ascii=False,indent=2).replace('\n','\n  ')+';',js,flags=re.S)
    drawer='drawerLinksEn' if en else 'drawerLinks'
    data=[[item['label'],item['href'],[[link[0],link[1]] for col in item.get('columns',[]) for link in col.get('links',[])]] for item in nav]
    js=re.sub(r'var '+drawer+r' = \[.*?\n  \];','var '+drawer+' = '+json.dumps(data,ensure_ascii=False,indent=2).replace('\n','\n  ')+';',js,flags=re.S)
js=js.replace('about.html#committee','committee.html').replace('會員中心','會員服務').replace('會員專屬優惠','會員權利').replace('精彩回顧','活動花絮')
js=js.replace('["certification.html", "證照獎項"]','["certificates.html", "證照"],\n          ["mission-206783-396345.html", "獎項"]')
js=js.replace('["certification-388672.html", "Certification & Awards"]','["certificates_en.html", "Certification"],\n          ["mission-206783-396345-512343.html", "Awards"]')
js=js.replace('{ label: "會員服務", links: [\n          ["join.html", "加入會員"]','{ label: "會員服務", links: [\n          ["login.html", "會員登入"]')
(ROOT/'v1/js/navbar.js').write_text(js)

# A shared search control combines keyword and category instead of competing filters.
js=(BEFORE/'main.js').read_text()
js=js.replace('var filterTimer = null;', '''var filterTimer = null;
  var librarySearch = document.querySelector('[data-library-search]');
  var libraryCount = document.querySelector('[data-library-count]');
  var libraryEmpty = document.querySelector('[data-library-empty]');
  function currentCategory() {
    var selected = document.querySelector('.filter-btn[aria-pressed="true"]');
    return selected ? selected.getAttribute('data-filter') : 'all';
  }
  if (librarySearch) {
    librarySearch.addEventListener('input', function () { applyFilter(currentCategory()); });
    document.querySelector('[data-library-clear]').addEventListener('click', function () {
      librarySearch.value = '';
      filterButtons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-filter') === 'all')); });
      applyFilter('all'); librarySearch.focus();
    });
    applyFilter('all');
  }''')
js=js.replace('function swap() {\n      insightCards', 'function swap() {\n      var count = 0;\n      var query = librarySearch ? librarySearch.value.trim().toLocaleLowerCase() : "";\n      insightCards')
js=js.replace('var match = category === "all" || card.getAttribute("data-category") === category;','var match = (category === "all" || card.getAttribute("data-category") === category) && (!query || card.textContent.toLocaleLowerCase().includes(query));\n        if (match) count++;')
js=js.replace('card.classList.remove("is-hiding");\n      });','card.classList.remove("is-hiding");\n      });\n      if (libraryCount) libraryCount.textContent = "共 " + count + " 篇文章";\n      if (libraryEmpty) libraryEmpty.hidden = count !== 0;')
js=js.replace('window.location.hash.replace("#", "")','window.location.hash.replace(/^#(?:edition-)?/, "")')
(ROOT/'v1/js/main.js').write_text(js)

# Unify page names, preserve application forms and page URLs.
for path in HTML.glob('*.html'):
    text=path.read_text().replace('會員中心','會員服務').replace('會員專屬優惠','會員權利').replace('精彩回顧','活動花絮').replace('about.html#committee','committee.html')
    path.write_text(text)

# IRC + scholarship, with dedicated certification overviews in both languages.
for en,cert,sch,overview,tiric in [(False,'certification.html','scholarshipirc.html','certificates.html','tiric.html'),(True,'certification-388672.html','scholarshipirc-952540.html','certificates_en.html','tiric-677070.html')]:
    s=read(cert); scholarship=read(sch)
    sec=s.new_tag('section',attrs={'class':'page-section','id':'scholarship'})
    sec.append(fragment('<div class="container"><div class="section-head"><h2>'+('IRC Sponsorship' if en else 'IRC 贊助獎學金')+'</h2></div></div>'))
    dest=sec.select_one('.container')
    for content in scholarship.select('main > section:not(.page-hero)'):
        inner=content.select_one('.container') or content
        for child in list(inner.contents):dest.append(child.extract())
    s.main.append(sec);put(cert,s)
    redirect(sch,cert+'#scholarship','IRC Sponsorship' if en else 'IRC 贊助獎學金')
    o=read(cert);o.main.clear()
    title='Certification' if en else '證照'
    o.title.string=title+'｜TIRI'
    o.main.append(fragment(f'<section class="page-hero"><div class="container"><p class="eyebrow">Professional Certification</p><h1>{title}</h1><p class="lede">'+('Develop professional IR expertise through international certification and practical training.' if en else '從國際認證到實務培訓，建立投資人關係專業能力。')+'</p></div></section>'))
    o.main.append(fragment(f'<section class="page-section"><div class="container"><div class="revision-cards two"><a class="revision-card" href="{cert}"><img src="../images/tiric/tiric-2025-class.jpg" alt="" loading="lazy"><div><p class="eyebrow">IRC</p><h2>'+('IRC International Certification' if en else 'IRC 國際證照')+'</h2><p>'+('Certification requirements, fees and scholarship applications.' if en else '證照介紹、報考條件、費用與贊助獎學金申請。')+f'</p></div></a><a class="revision-card" href="{tiric}"><img src="../images/tiric/tiric-2025-students.jpg" alt="" loading="lazy"><div><p class="eyebrow">TIRIC</p><h2>'+('TIRI Elite Program' if en else 'TIRIC IR 專業實戰班')+'</h2><p>'+('Practical IR training with NIRI-authorized teaching materials.' if en else '採 NIRI 授權教材，結合理論與台灣 IR 實務。')+'</p></div></a></div></div></section>'))
    put(overview,o)

# Awards use the same accessible edition selector as the board.
s=read('mission-206783.html')
s.select_one('.term-switch').replace_with(picker([(str(y),f'第{n}屆（{y}）') for y,n in [(2026,'五'),(2025,'四'),(2024,'三'),(2023,'二'),(2022,'一')]]))
for script in s.find_all('script'):
    if 'page-specific: TIRI Awards' in script.get_text():script.decompose()
hero(s,'../images/awards/awards-trophy.jpg','50% 55%');put('mission-206783.html',s)

# The 2025 award material already includes the first Progress Award winners.
p=read('mission-206783-766399.html')
body=p.select_one('main > .page-section > .container')
existing=fragment('<section class="term-panel" data-term="2026" id="edition-2026"></section>').section
for el in list(body.contents):existing.append(el.extract())
body.append(picker([('2026','第二屆（2026）'),('2025','第一屆（2025）')]))
body.append(existing)
first=fragment('<section class="term-panel" data-term="2025" id="edition-2025" hidden><h2>第一屆 TIRI 潛力進展獎</h2><p class="lede">2025 年得獎企業</p></section>').section
award2025=s.select_one('[data-term="2025"]')
heading=next(h for h in award2025.select('h2') if '潛力進展' in h.get_text())
for el in list(heading.next_siblings): first.append(fragment(str(el)))
body.append(first)
hero(p,'../images/awards/awards-progress-certificate.jpg','50% 65%')
put('mission-206783-766399.html',p)

# TIRIC: one local video, smaller lecturer portraits, real available recap year.
s=read('tiric.html'); video=s.select_one('video');video['playsinline']='';video['aria-label']='TIRIC IR 專業實戰班課程介紹影片'
video.parent['id']='intro-video'
iframe=s.select_one('iframe[src*="youtube"]')
if iframe:
    box=iframe.parent
    box.replace_with(fragment('<p class="video-link"><a class="btn btn-outline" href="#intro-video">觀看 TIRIC 課程介紹影片 ↑</a></p>'))
h=next(x for x in s.select('h2') if '2025 TIRIC 回顧' in x.get_text())
row=h.find_parent(class_='page-split')
row['id']='recap'; h.string='TIRIC 課程回顧'
content=row.find_all(recursive=False)[-1]
panel=s.new_tag('div',attrs={'class':'term-panel','data-term':'2025'})
for el in list(content.contents):panel.append(el.extract())
content.append(picker([('2025','2025 TIRIC 回顧')]))
content.append(panel);put('tiric.html',s)

# Search is confined to the article library.
s=read('knowledge.html');filters=s.select_one('.filter-bar') or s.select_one('.filter-btn').parent
filters.insert_before(fragment('<form class="library-search" role="search" aria-label="知識資源文章搜尋"><label for="library-keyword">搜尋文章</label><div class="library-input"><input id="library-keyword" type="search" placeholder="輸入標題或摘要關鍵字" data-library-search autocomplete="off"><button type="button" class="btn btn-outline" data-library-clear>清除篩選</button></div></form>'))
filters.insert_after(fragment('<p class="library-count" data-library-count role="status" aria-live="polite">共 27 篇文章</p>'))
s.select_one('.insights-grid').insert_after(fragment('<p class="library-empty" data-library-empty hidden>沒有符合條件的文章，請調整關鍵字或清除篩選。</p>'))
put('knowledge.html',s)

# Render real covers from all six language-specific source PDFs.
coverdir=ROOT/'v1/images/annual';coverdir.mkdir(exist_ok=True)
pdfs=sorted((ROOT/'v1/files/annual').glob('*.pdf'))
assert len(pdfs)==6, len(pdfs)
records=[]
for pdf in pdfs:
    d=pymupdf.open(pdf);page=d[0];pix=page.get_pixmap(matrix=pymupdf.Matrix(600/page.rect.width,600/page.rect.width),alpha=False)
    cover=coverdir/(pdf.stem+'.jpg');pix.save(str(cover),jpg_quality=85)
    lang='en' if pdf.stem.endswith('-en') else 'zh';year=re.search(r'20\d\d',pdf.name).group()
    records.append({'year':year,'lang':lang,'pdf':'../files/annual/'+pdf.name,'cover':'../images/annual/'+cover.name,'pages':len(d),'bytes':pdf.stat().st_size})
(OUT/'source/yearbook-covers.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
def covercards(lang):
    result='<div class="yearbook-grid">'
    for r in sorted((r for r in records if r['lang']==lang),key=lambda r:r['year'],reverse=True):
        title=f"{r['year']} TIRI "+('Annual Report' if lang=='en' else '年刊')
        result+=f'<article class="yearbook-card"><a href="{r["pdf"]}" target="_blank" rel="noopener" aria-label="{title}"><img src="{r["cover"]}" alt="{title}'+(' English cover' if lang=='en' else '中文版封面')+f'" loading="lazy"></a><p class="eyebrow">{r["year"]} · '+('English' if lang=='en' else '繁體中文')+f'</p><h3>{title}</h3><p class="mono-meta">PDF · {r["pages"]} '+('pages' if lang=='en' else '頁')+f' · {r["bytes"]/1e6:.1f} MB</p><div class="yearbook-actions"><a class="u-link" href="{r["pdf"]}" target="_blank" rel="noopener">'+('Read online' if lang=='en' else '線上閱覽')+f' ↗</a><a class="u-link" href="{r["pdf"]}" download>'+('Download PDF' if lang=='en' else '下載 PDF')+'</a></div></article>'
    return result+'</div>'
for name,lang in [('5th_report-516844.html','zh'),('5th_report-665763.html','en')]:
    s=read(name)
    if s.select_one('#archive'):s.select_one('#archive').decompose()
    s.main.append(fragment('<section class="page-section" id="archive"><div class="container"><div class="section-head"><h2>'+('Annual Reports' if lang=='en' else '歷年年刊')+'</h2><a class="u-link" href="'+('5th_report-516844.html#archive' if lang=='en' else '5th_report-665763.html#archive')+'">'+('中文版' if lang=='en' else 'English editions')+'</a></div>'+covercards(lang)+'</div></section>'))
    put(name,s)
s=BS((HTML/'knowledge.html').read_text(),'html.parser')
s.select_one('#yearbook').replace_with(fragment('<section class="page-section" id="yearbook"><div class="container"><div class="section-head"><h2>TIRI 年刊</h2><a class="u-link" href="5th_report-665763.html#archive">English editions →</a></div>'+covercards('zh')+'</div></section>'))
put('knowledge.html',s)

# Latest course catalogue replaces the old seven-topic grouping.
latest=next((ROOT.parent/'ref').rglob('*2026.07.17*pdf'))
shutil.copy2(latest,ROOT/'v1/documents/tiri-courses-2026-07-17.pdf')
s=read('trainbod.html')
for a in s.select('a[href*="2026.05.11"]'):a['href']='../documents/tiri-courses-2026-07-17.pdf'
topics=[('併購實務',['國內外併購實務大解析','台灣敵意併購及內線交易實務'],1),('企業管理',['董事會如何掌握另類投資的風險與機會','系統思考導向的組織診斷與優化'],1),('公司治理',['公司治理與新版 ESG 評鑑之因應','2026 年新版公司治理暨董事會績效評鑑實務解析'],4),('財稅法律',['跨國企業法律風險管理與公司治理觀點','企業財務資訊之解析及決策運用'],5),('誠信經營',['董事會誠信經營與反賄賂管理實務研習','上市上櫃公司誠信經營守則實務及應用'],7),('ESG 議題',['從永續報告書到 IFRS 永續揭露準則','董事會該關心的 ESG 核心議題'],8),('資訊安全',['漫談資安治理的盲點與對策','從 AI 浪潮看 2026 資安挑戰與治理策略'],11),('媒體與危機管理',['企業危機管理','治理視角的公關策略'],12)]
cats=s.select_one('.course-cats');cats.clear()
for i,(title,items,page) in enumerate(topics,1):
    cats.append(fragment(f'<div class="course-cat"><div class="cat-head"><span class="no">{i:02}</span><h4>{title}</h4></div><ul>'+''.join('<li>'+x+'</li>' for x in items)+f'</ul><a class="u-link" href="../documents/tiri-courses-2026-07-17.pdf#page={page}" target="_blank" rel="noopener">完整課程與大綱 ↗</a></div>'))
s.select_one('#inhouse .sub-head').string='八大課程主題'
s.select_one('#inhouse .sub-lede').string='依 2026 年 7 月 17 日課程資料，提供以下八大主題。可依企業需求安排講師與課程；完整名稱、課綱及講師詳見課程列表。'
put('trainbod.html',s)

# Remove local legacy flow styles so both diagrams follow the shared design.
for name in ['bodperform.html','corpperform.html']:
    s=read(name)
    for style in s.find_all('style'):
        if 'flow-steps' in style.get_text():style.decompose()
    put(name,s)

print('Structural pages, navigation, selectors, library search, course catalogue and 6 covers written.')
