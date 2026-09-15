from revision_helpers import *

# Keep licensed photos in an auditable, dedicated directory.
image_dir=ROOT/'v1/images/revision';image_dir.mkdir(exist_ok=True)
photo_records=json.loads((OUT/'圖片來源紀錄.json').read_text())
photos={}
for row in photo_records:
    dst=image_dir/(row['id']+'-'+row['key']+'.jpg')
    if not dst.exists():shutil.copy2(OUT/row['preview'],dst)
    photos[row['id']]='../images/revision/'+dst.name

def pic(src,alt,classes=''):
    return f'<img src="{src}" alt="{E(alt)}" loading="lazy" decoding="async"'+(f' class="{classes}"' if classes else '')+'>'

# Show names and official company links while formal partner logos are pending.
benefits=read('benefit.html')
partner_links=[a for a in benefits.select('main a[href^="http"]') if 'niri.org' not in a['href']]
partners=[{'name':a.get_text(' ',strip=True),'url':a['href']} for a in partner_links]
assert len(partners)==10
(OUT/'source/partner-links.json').write_text(json.dumps(partners,ensure_ascii=False,indent=2))
partner_grid='<div class="partner-names">'+''.join(f'<a href="{E(r["url"])}" target="_blank" rel="noopener">{E(r["name"])} <span aria-hidden="true">↗</span></a>' for r in partners)+'</div>'
s=read('partners.html')
s.select_one('.partners-wall').replace_with(fragment(partner_grid))
for a in s.select('a[href="membership.html#benefits"]'):a['href']='benefit.html'
for row,partner in zip(s.select('.benefit-rows > *'),partners):
    name=row.select_one('h3') or row.select_one('strong')
    if name:
        name.clear();name.append(fragment(f'<a class="u-link" href="{E(partner["url"])}" target="_blank" rel="noopener">{E(partner["name"])}</a>'))
put('partners.html',s)

# Five distinct functional committees; appointments come from the committee source,
# not the third-term board roster (the two sources contain different positions).
tom=[('矽創電子','投資人關係暨永續發展處長暨發言人'),('昇佳電子','投資人關係')]
committees=[
 {'slug':'certification','name':'證照委員會','en':'Certification Committee','purpose':'協助 IRC 證照推廣','img':'../images/tiric/tiric-2025-class.jpg','alt':'TIRIC 課程現場','people':[
  ('召集人','張妍婷',[('仁寶電腦工業股份有限公司','投資人關係部處長')]),('執行委員','張明仁',[('新源生物科技股份有限公司','財務副總')]),('執行委員','黃英記',tom)]},
 {'slug':'awards','name':'獎項委員會','en':'Awards Committee','purpose':'協助投資人關係獎項推廣','img':'../images/awards/awards-trophy.jpg','alt':'TIRI Awards 獎座','people':[
  ('召集人','劉詩亮',[('TPK 宸鴻光電科技股份有限公司','資深副總經理、策略長暨代理發言人')]),('執行委員','周德雲',[('矽創電子股份有限公司','策略投資顧問')]),('執行委員','黃英記',tom)]},
 {'slug':'professional','name':'專業委員會','en':'Professional Committee','purpose':'協助專業資訊內容產出','img':photos['A04'],'alt':'資本市場行情與研究圖表','people':[
  ('召集人','簡世雄',[('東元電機股份有限公司','公司治理中心處長暨發言人')]),('執行委員','陳珮瑛',[('力銘永續發展股份有限公司','永續長')]),('執行委員','涂蕙蘭',[('精英電腦股份有限公司','財會主管暨公司治理主管')]),('執行委員','許碧雲',[('桓達科技股份有限公司','總經理特助暨發言人')])]},
 {'slug':'media','name':'媒體委員會','en':'Media Committee','purpose':'協助媒體溝通合作','img':photos['A08'],'alt':'媒體訪談使用的麥克風','people':[
  ('召集人','王恩國',[('東友科技股份有限公司','副董事長')]),('執行委員','王沈銘',[('圓剛科技股份有限公司','公共關係室資深經理暨發言人')]),('執行委員','陳珮瑛',[('力銘永續發展股份有限公司','永續長')])]},
 {'slug':'outreach','name':'推廣委員會','en':'Outreach Committee','purpose':'協助社群及活動行銷','img':'../images/hero-annual-forum.jpg','alt':'TIRI 年度大會交流現場','people':[
  ('召集人','林男和',[('旗山龍鳳食品股份有限公司','總經理')]),('執行委員','洪健凱',[('經寶精密控股股份有限公司','投資人關係部經理')]),('執行委員','姚文鈞',[('全漢企業股份有限公司','董事長特別助理暨發言人')])]}
]
(OUT/'source/committee-records.json').write_text(json.dumps({'source':'https://www.tiri.tw/html/committee.html','checked':'2026-09-09','note':'委員會公開資料與第三屆理監事任職資料不同，保留委員會來源，不互相覆蓋。','committees':committees},ensure_ascii=False,indent=2))
def committeecards(items):
    return '<div class="revision-cards">'+''.join(f'<a class="revision-card" href="committee-{c["slug"]}.html">'+pic(c['img'],c['alt'])+f'<div><p class="eyebrow">{c["en"]}</p><h3>{c["name"]}</h3><p>{c["purpose"]}</p><p class="u-link">認識委員會 →</p></div></a>' for c in items)+'</div>'
s=read('committee.html')
sections=s.select('main > section:not(.page-hero)')
for sec in sections:sec.decompose()
s.main.append(fragment('<section class="page-section"><div class="container">'+committeecards(committees)+'<p class="note" style="margin-top:40px">加入功能委員會，可與 IR 領域先進交流並促進職涯發展。歡迎聯絡秘書處：<a class="u-link" href="contact.html">(02) 2381-9248</a>。</p></div></section>'))
put('committee.html',s)
for c in committees:
    s=read('committee.html');s.title.string=c['name']+'｜TIRI';s.main.clear()
    s.main.append(fragment(f'<section class="page-hero"><div class="container"><p class="eyebrow">{c["en"]}</p><h1>{c["name"]}</h1><p class="lede">{c["purpose"]}</p></div></section>'))
    rows=''
    for role,name,jobs in c['people']:
        for i,(company,title) in enumerate(jobs):
            rows+='<tr>'+(f'<td rowspan="{len(jobs)}">{role}</td><th class="member-name" scope="row" rowspan="{len(jobs)}">{name}</th>' if i==0 else '')+f'<td>{company}</td><td>{title}</td></tr>'
    s.main.append(fragment('<section class="page-section"><div class="container"><div class="committee-feature">'+pic(c['img'],c['alt'])+f'<div><p class="eyebrow">Our Function</p><h2>委員會職能</h2><p>{c["purpose"]}。</p><p style="margin-top:24px"><a class="u-link" href="contact.html">聯絡秘書處，了解如何參與 →</a></p></div></div><div class="member-table-wrap" role="region" aria-label="{c["name"]}名冊" tabindex="0"><table class="member-table"><caption>委員會成員</caption><thead><tr><th scope="col">委員會職務</th><th scope="col">姓名</th><th scope="col">公司</th><th scope="col">公司職稱</th></tr></thead><tbody>{rows}</tbody></table></div><div class="committee-more"><h2>更多委員會</h2>'+committeecards([o for o in committees if o!=c])+'</div></div></section>'))
    put('committee-'+c['slug']+'.html',s)

# About: repeated left-image, right-text rows, including all supplied content.
s=read('about.html')
storypics=[(photos['A09'],'企業辦公大樓'),(photos['A04'],'資本市場行情'),('../images/hero-annual-forum.jpg','TIRI 年度大會'),('../images/tiric/tiric-2025-class.jpg','TIRIC 課程現場'),('../images/tiric/tiric-2025-group-1.jpg','TIRI 專業交流'),(photos['A02'],'財務資訊與知識研究'),('../images/hero-recap.jpg','TIRI 交流活動')]
for row,(src,alt) in zip(s.select('.page-section .page-split')[:7],storypics):
    row['class']=['photo-story']; content=s.new_tag('div')
    for el in list(row.contents):content.append(el.extract())
    row.append(fragment(pic(src,alt)));row.append(content)
block=s.select_one('#committee .committee-grid')
block.replace_with(fragment(committeecards(committees)))
put('about.html',s)

for name,src,pos in [('certificate.html',photos['A06'],'50% 60%'),('trainbod-384680.html',photos['A01'],'50% 60%'),('join.html',photos['A09'],'50% 50%')]:
    s=read(name);hero(s,src,pos);put(name,s)

s=BS((HTML/'trainbod.html').read_text(),'html.parser')
for li,(src,alt) in zip(s.select('.inhouse-features > li'),[('../images/tiric/tiric-2025-class.jpg','專業課程授課現場'),(photos['A03'],'企業辦公室中的討論情境'),(photos['A05'],'透過電腦進行線上交流')]):li.insert(0,fragment(pic(src,alt)))
topicphotos=[(photos['A03'],'企業協商情境'),('../images/tiric/tiric-2025-group-1.jpg','專業管理交流'),(photos['A09'],'企業治理與組織'),(photos['A02'],'財務報表與計算機'),('../images/revision/B01-document.jpg','簽署文件與責任承諾'),(photos['A06'],'太陽能板與再生能源'),('../images/revision/B02-security.jpg','企業網路設備'),(photos['A08'],'媒體溝通麥克風')]
for cat,(src,alt) in zip(s.select('.course-cat'),topicphotos):cat.insert(0,fragment(pic(src,alt)))
put('trainbod.html',s)

s=read('benefit.html')
for row,(src,alt) in zip(s.select('.page-split')[:2],[('../images/tiric/tiric-2025-class.jpg','TIRI 專業課程'),(photos['A03'],'企業合作討論情境')]):
    row['class']=['photo-story'];content=s.new_tag('div')
    for el in list(row.contents):content.append(el.extract())
    row.append(fragment(pic(src,alt)));row.append(content)
put('benefit.html',s)

# Exact per-article image choices. Portraits identify real interviewees only.
s=BS((HTML/'knowledge.html').read_text(),'html.parser')
article_images=[
 ('../images/board-2026-fufu-shen.jpg','沈馥馥理事長','portrait'),
 (photos['A08'],'媒體溝通與發言',''),(photos['A04'],'投資資訊與分析',''),
 (photos['A03'],'機構法人交流情境',''),(photos['A04'],'資本市場分析',''),
 ('../images/tiric/tiric-2025-class.jpg','IR 專業培訓現場',''),(photos['A02'],'財務報表與計算機',''),
 (photos['A05'],'遠距溝通與線上會議',''),(photos['A06'],'再生能源與 ESG',''),
 ('../images/tiric/tiric-2025-group-1.jpg','專業團隊交流',''),('../images/revision/B01-document.jpg','董事會文件與報告',''),
 (photos['A02'],'企業財報資料',''),(photos['A06'],'企業永續與能源轉型',''),(photos['A08'],'企業公共關係與媒體溝通',''),
 (photos['A04'],'資本市場資訊',''),(photos['A05'],'跨部門遠距協作',''),(photos['A03'],'跨部門溝通情境',''),
 ('../images/hero-annual-forum.jpg','TIRI 專業溝通交流',''),('../images/revision/B01-document.jpg','投資人關係工作文件',''),
 (photos['A04'],'IR 專業市場分析',''),(photos['A09'],'企業與資本市場',''),('../images/tiric/tiric-2025-class.jpg','IR 專業能力培訓',''),
 (photos['A09'],'企業組織與管理',''),('../images/revision/B01-document.jpg','董事會議事與報告',''),
 ('../images/board-2026-jonny-kuo.jpg','霹靂前財務長郭宗霖','portrait'),(photos['A04'],'台灣企業與投資人關係',''),
 ('../images/board-2026-freddie-liu.jpg','投資人關係專家劉詩亮','portrait')]
cards=s.select('.insight-card');assert len(cards)==len(article_images)==27
article_log=[]
for card,(src,alt,kind) in zip(cards,article_images):
    card.insert(0,fragment(pic(src,alt,'article-thumb '+kind)))
    article_log.append({'title':card.h3.get_text(' ',strip=True),'href':card.get('href'),'image':src,'alt':alt,'basis':'本案具名照片' if kind else ('CC0 情境圖' if '/revision/' in src else '本案活動實拍')})
(OUT/'source/article-image-map.json').write_text(json.dumps(article_log,ensure_ascii=False,indent=2))
put('knowledge.html',s)

# Naming replacements also cover pages reconstructed from the pre-change snapshot.
for path in HTML.glob('*.html'):
    text=path.read_text().replace('會員中心','會員服務').replace('會員專屬優惠','會員權利').replace('精彩回顧','活動花絮').replace('about.html#committee','committee.html')
    path.write_text(text)
print('Partner links, 5 committee pages, photo stories and 27 article images written.')
