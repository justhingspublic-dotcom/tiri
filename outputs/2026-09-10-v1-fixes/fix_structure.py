"""Apply actual first-review changes to v1; preserve a pre-fix snapshot."""
from pathlib import Path
from bs4 import BeautifulSoup as BS
from html import escape as E
import copy
import hashlib
import json
import re
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
HTML = ROOT / 'v1/html'
SOURCE = OUT / 'source'
BEFORE = SOURCE / 'before-v1'
BEFORE.mkdir(parents=True, exist_ok=True)
for folder in ['html', 'css', 'js']:
    for path in (ROOT / 'v1' / folder).glob('*'):
        if path.is_file():
            target = BEFORE / folder / path.name
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)

def read(name):
    return BS((BEFORE / 'html' / name).read_text(), 'html.parser')

def frag(markup):
    return BS(markup, 'html.parser')

def put(name, soup):
    if not soup.select_one('link[href*="review-fixes.css"]'):
        soup.head.append(frag('<link rel="stylesheet" href="../css/review-fixes.css?v=20260910-r2">'))
    (HTML / name).write_text(str(soup))

# 02 / 27: shared desktop, mobile and footer navigation.
nav = (BEFORE / 'js/navbar.js').read_text()
nav = nav.replace('certificates_en.html', 'certification-388672.html').replace('certificates.html', 'certification.html')
nav = nav.replace('["login.html", "會員登入"]', '[null, "會員登入"]')
nav = re.sub(r'\[\s*"certification.html#scholarship",\s*"IRC 贊助獎學金"(?:,\s*"填寫申請表取得贊助資格")?\s*\],?\s*', '', nav)
nav = re.sub(r'\[\s*"certification-388672.html#scholarship",\s*"[^"]*"(?:,\s*"[^"]*")?\s*\],?\s*', '', nav)
nav = nav.replace('"IRC 國際證照"', '"國際證照"').replace('"TIRIC IR 專業實戰班"', '"專業實戰班"')
old = "return '<li><a href=\"' + link[0] + '\">' + link[1] + '</a></li>';"
new = "return link[0] ? '<li><a href=\"' + link[0] + '\">' + link[1] + '</a></li>' : '<li><span class=\"footer-label\">' + link[1] + '</span></li>';"
assert old in nav
nav = nav.replace(old, new)
(ROOT / 'v1/js/navbar.js').write_text(nav)
for name, target in [('certificates.html', 'certification.html'), ('certificates_en.html', 'certification-388672.html')]:
    soup = read(name)
    for tag in soup.select('meta[http-equiv=refresh],link[rel=canonical]'):
        tag.decompose()
    soup.head.append(frag(f'<meta http-equiv="refresh" content="0; url={target}"><link rel="canonical" href="{target}">'))
    soup.main.clear()
    soup.main.append(frag(f'<section class="page-section"><div class="container"><h1>IRC</h1><a class="btn btn-primary" href="{target}">IRC →</a></div></section>'))
    put(name, soup)

# 04: all nine inner-page courses use the same image cards as the homepage.
def norm(text):
    text = re.sub(r'^【[^】]+】', '', text)
    return re.sub(r'[\W_]+', '', text).lower()
events = read('news.html').select('.event-banner-row')
catalog = [(norm(row.h3.get_text(' ', strip=True)), row) for row in events]
course_log = []
for name in ['trainbod.html']:
    soup = read(name)
    old_list = soup.select_one('#open .event-list')
    cards = soup.new_tag('div', attrs={'class': 'revision-cards course-review-cards'})
    records = []
    for old_card in old_list.select('.event-item'):
        title = old_card.h3.get_text(' ', strip=True)
        matches = [row for key, row in catalog if norm(title) in key or key in norm(title)]
        assert len(matches) == 1, (title, len(matches))
        event = matches[0]
        assert event.img and event.get('href')
        date = event.time['datetime']
        state = '已結束' if date < '2026-09-10' else '課程資訊'
        card = frag(f'<a class="revision-card" href="{E(event["href"])}" target="_blank" rel="noopener"><img src="{E(event.img["src"])}" alt="{E(title)}課程主視覺" loading="lazy"><div><p class="eyebrow">{date} · 線上</p><h3>{E(re.sub(r"^【[^】]+】", "", title))}</h3><p>{state} · 查看課程資訊 ↗</p></div></a>').a
        records.append((date, card))
        course_log.append({'date': date, 'title': title, 'href': event['href'], 'image': event.img['src']})
    for _, card in sorted(records, key=lambda row: row[0], reverse=True):
        cards.append(card)
    old_list.replace_with(cards)
    put(name, soup)
(SOURCE / 'course-card-map.json').write_text(json.dumps(course_log, ensure_ascii=False, indent=2))

# 08: third-term portraits remain; company and title become paired text rows.
def jobs_zh(name, title):
    special = {
        '郭宗霖': [('鴻勝會計師事務所', '執業會計師'), ('大井泵浦工業股份有限公司', '董事')],
        '王恩國': [('南昌菱光科技有限公司', '董事長'), ('今皓實業股份有限公司', '獨立董事')],
        '楊朝榮': [('中華民國證券期貨分析協會', '理事'), ('聯茂、虎航、泰博等公司', '獨立董事')],
        '劉詩亮': [('TPK 宸鴻光電科技股份有限公司', '資深副總經理策略長暨代理發言人')],
        '王沈銘': [('1919 食物銀行', '特約顧問')],
    }
    if name in special: return special[name]
    if name in ['余凱文', '許育綾']: return [('', title)]
    assert ' ' in title, (name, title)
    return [title.split(' ', 1)]

def jobs_en(name, title):
    if name == 'Jonny Kuo':
        return [('BigWin CPA Firm', 'Certified Public Accountant'), ('Walrus Pump Co., Ltd.', 'Director')]
    if name == 'Kevin Wang':
        return [('Nanchang Creative Sensor Technology Co., Ltd.', 'Chairman'), ('Ji-Haw Industrial Co., Ltd.', 'Independent Director')]
    if name == 'David Yang':
        return [('Securities Analysts Association, Chinese Taipei', 'Director'), ('ITEQ, Tigerair Taiwan and TaiDoc', 'Independent Director')]
    return [title.split(' — ', 1)] if ' — ' in title else [('', title)]

rosters = []
for name, language in [('board.html','zh'), ('board_en.html','en')]:
    soup = read(name)
    for old_title in soup.select('[data-term="2026"] .title'):
        person = old_title.find_previous_sibling(class_='name').get_text(' ', strip=True)
        jobs = (jobs_zh if language == 'zh' else jobs_en)(person, old_title.get_text(' ', strip=True))
        markup = '<div class="board-appointments">' + ''.join('<div class="board-appointment">' + (f'<p class="company">{E(company)}</p>' if company else '') + f'<p class="position">{E(position)}</p></div>' for company, position in jobs) + '</div>'
        old_title.replace_with(frag(markup))
        rosters.append({'language': language, 'name': person, 'jobs': jobs})
    put(name, soup)
(SOURCE / 'third-term-appointments.json').write_text(json.dumps(rosters, ensure_ascii=False, indent=2))

# 27: replace nested legacy layout with a readable scholarship section.
for name, en in [('certification.html',False), ('certification-388672.html',True)]:
    soup = read(name)
    section = soup.select_one('#scholarship')
    groups = []
    for heading in section.select('.wsite-content-title'):
        paragraph = heading.find_next_sibling('div', class_='paragraph')
        if paragraph:
            groups.append((heading.get_text(' ',strip=True), copy.deepcopy(paragraph)))
    assert len(groups) == 5, (name, len(groups))
    intro, application, conditions, intro_links, why = [paragraph for _, paragraph in groups]
    for index, li in enumerate(application.select('ol > li'), 1):
        li.insert(0, frag(f'<span class="scholarship-step-number">{index:02d}</span>'))
    for paragraph in [intro, application, conditions, intro_links, why]:
        for link in paragraph.select('a'):
            href = link.get('href', '')
            if 'forms.gle' in href: link.clear(); link.append('Application form ↗' if en else '填寫獎學金申請表 ↗')
            elif 'portal.niri.org' in href: link.clear(); link.append('Register for the IRC exam ↗' if en else '前往 NIRI 報名 IRC 測驗 ↗')
            elif link.get_text(strip=True).startswith('www.'):
                link.clear(); link.append(('NIRI IRC ↗' if 'niri.org' in href else 'TIRI IRC ↗'))
        for font in paragraph.select('font'): font.unwrap()
    heading = 'IRC Sponsorship' if en else 'IRC 贊助獎學金'
    section.clear()
    box = frag(f'<div class="container scholarship-layout"><div class="scholarship-intro"><p class="eyebrow">IRC SCHOLARSHIP · 2024</p><h2>{heading}</h2></div><div class="scholarship-facts"><div><span>{"Per recipient" if en else "每名獎學金"}</span><strong>NT$30,000</strong></div><div><span>{"Available places" if en else "贊助名額"}</span><strong>2 <small>{"recipients" if en else "名"}</small></strong></div></div><div class="scholarship-application"><h3>{E(groups[1][0])}</h3></div><div class="scholarship-details"><div class="scholarship-conditions"><h3>{E(groups[2][0])}</h3></div><div class="scholarship-links"><h3>{E(groups[3][0])}</h3></div></div><details class="scholarship-why"><summary>{E(groups[4][0])}</summary></details></div>')
    box.select_one('.scholarship-intro').append(intro)
    box.select_one('.scholarship-application').append(application)
    box.select_one('.scholarship-conditions').append(conditions)
    box.select_one('.scholarship-links').append(intro_links)
    box.select_one('.scholarship-why').append(why)
    section.append(box)
    put(name, soup)

# 32: stable columns and separate company names, English names and codes.
for name in ['mission-206783-766399.html', 'mission-206783-766399-942925.html']:
    soup = read(name)
    for grid in soup.select('.roster-grid'):
        grid.attrs.pop('style', None)
        grid['class'] = list(dict.fromkeys(grid.get('class', []) + ['progress-rosters']))
        for row in grid.select('.roster li'):
            code = row.select_one('.code')
            if not code: continue
            code.extract()
            company = row.get_text(' ',strip=True)
            split = re.match(r'^(.*?股份有限公司)\s+([A-Za-z].*)$', company)
            row.clear(); row.append(code)
            name_box = soup.new_tag('span', attrs={'class': 'award-company'})
            name_box.append(split[1] if split else company)
            if split:
                small = soup.new_tag('small'); small.string = split[2]; name_box.append(small)
            row.append(name_box)
    put(name, soup)

# 39: headings above images; long benefits sit in a full-width grid below an overview.
soup = read('benefit.html')
for index, story in enumerate(soup.select('.photo-story')):
    image = story.find('img', recursive=False).extract()
    side = story.select_one('.side').extract()
    benefits = story.select_one('.benefit-rows').extract()
    story.clear(); story['class'] = ['benefit-review-section']
    side['class'] = ['benefit-review-heading']; story.append(side)
    overview = soup.new_tag('div', attrs={'class':'benefit-overview'})
    overview.append(image)
    if index == 0:
        overview.append(benefits)
    else:
        links = soup.new_tag('div', attrs={'class':'benefit-partner-index'})
        for i, item in enumerate(benefits.find_all('div', recursive=False), 1):
            item['id'] = f'benefit-partner-{i}'
            title = item.find('dt').get_text(' ',strip=True)
            links.append(frag(f'<a href="#benefit-partner-{i}">{E(title)} <span aria-hidden="true">↓</span></a>'))
        overview.append(links)
        benefits['class'] = ['benefit-rows','benefit-offers-grid']
    story.append(overview)
    if index: story.append(benefits)
put('benefit.html', soup)

# Cache-bust shared resources and eliminate all intermediate certification links.
for path in HTML.glob('*.html'):
    text = path.read_text()
    text = re.sub(r'(\b(?:src|href)="\.\./js/navbar\.js)(?:\?[^\"]*)?(\")', r'\1?v=20260910-r2\2', text)
    text = text.replace('href="certificates.html"','href="certification.html"').replace('href="certificates_en.html"','href="certification-388672.html"')
    if 'review-fixes.css' not in text:
        text = text.replace('</head>', '<link rel="stylesheet" href="../css/review-fixes.css?v=20260910-r2"></head>')
    path.write_text(text)
print('Applied layout/navigation changes: 02, 04, 08, 27, 32 and 39. Photos and final verification follow.')
