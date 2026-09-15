"""Apply sixth-review changes from preserved HTML and the audited client data."""
from pathlib import Path
from bs4 import BeautifulSoup
from html import escape
import copy
import hashlib
import json
import re
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
REV = '20260914-r6'
SNAP = OUT / 'source/before'
SNAP.mkdir(parents=True, exist_ok=True)
books = json.loads((ROOT / 'outputs/2026-09-14-material-audit/source/all-workbooks.json').read_text())
changed = []

def read(name):
    path = ROOT / 'v1/html' / name
    saved = SNAP / name
    if not saved.exists():
        shutil.copy2(path, saved)
    return BeautifulSoup(saved.read_text(), 'html.parser')

def fragment(html):
    return BeautifulSoup(html, 'html.parser')

def write(name, soup, script=False):
    soup.head.append(soup.new_tag('link', rel='stylesheet', href=f'../css/round6.css?v={REV}'))
    if script:
        soup.body.append(soup.new_tag('script', attrs={'defer':'', 'src':f'../js/round6.js?v={REV}'}))
    path = ROOT / 'v1/html' / name
    path.write_text(str(soup))
    changed.append(name)

# Banner photographs remain original licensed assets; presentation is CSS only.
banner_specs = [
    ('bodperform.html', '../images/review-r2/financial-analysis.jpg', '核對圖表與評估資料的情境', 'service-banner'),
    ('bodperform-583064.html', '../images/review-r2/financial-analysis.jpg', 'Reviewing charts and evaluation documents', 'service-banner'),
    ('corpperform.html', '../images/review-r2/document-review.jpg', '文件檢視與工作紀錄的情境', 'service-banner'),
    ('corpperform-750901.html', '../images/review-r2/document-review.jpg', 'Reviewing documents and recording work', 'service-banner'),
    ('5th_report-516844.html', '../images/review-r6/yearbook-background.png', '', 'yearbook-banner'),
    ('5th_report-665763.html', '../images/review-r6/yearbook-background.png', '', 'yearbook-banner'),
]
image_dir = ROOT / 'v1/images/review-r6'
image_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(ROOT.parent / 'ref/官網/新官網-資料/文件/8年刊下載/TIRI七周年年刊背景.png', image_dir / 'yearbook-background.png')
for name, src, alt, kind in banner_specs:
    soup = read(name)
    hero = soup.select_one('.page-hero')
    hero['id'] = 'service-banner' if kind == 'service-banner' else 'yearbook-banner'
    hero['class'] += ['round6-banner', kind]
    hero['style'] = f"--hero-img: url('{src}')"
    if kind == 'service-banner':
        hero.insert(0, soup.new_tag('img', attrs={'class':'round6-banner-image', 'src':src, 'alt':alt, 'width':'1200', 'height':'800', 'decoding':'async', 'fetchpriority':'high'}))
    write(name, soup)

# Recap: retain the exact original titles, dates and article links in each language.
recap_sources = []
zh_soup = read('news-971146.html')
zh_rows = zh_soup.select('.event-item')
photo_by_date = {}
for item in zh_rows:
    year = item.select_one('.yr').get_text(strip=True)
    md = item.select_one('.date').contents[0].strip()
    date = year + '-' + md.replace('/', '-')
    article = BeautifulSoup((ROOT / 'v1/html' / item['href']).read_text(), 'html.parser')
    images = article.select('main img[src]')
    if year == '2026':
        src = '../images/events/2608261303411628089416.jpg'
    elif year == '2025':
        src = '../images/event-2025-conference-official.jpg'
    else:
        src = images[0]['src'] if images else ''
    photo_by_date[date] = src
    recap_sources.append({'date':date, 'title':item.h3.get_text(strip=True), 'article':item['href'], 'image':src})

for name in ['news-971146.html', 'news-971146-722067.html']:
    soup = read(name)
    en = soup.html.get('lang') == 'en'
    rows = soup.select('.event-item')
    cards = []
    years = []
    for item in rows:
        year = item.select_one('.yr').get_text(strip=True)
        md = item.select_one('.date').contents[0].strip()
        date = year + '-' + md.replace('/', '-')
        years.append(year)
        src = photo_by_date[date]
        title = item.h3.get_text(' ', strip=True)
        # The existing future event is preserved and explicitly labelled as a preview.
        future = date > '2026-09-14'
        status = ('Event preview' if en else '活動預告') if future else ('Event recap' if en else '活動花絮')
        cta = ('View event' if en else '查看活動資訊') if future else ('Read recap' if en else '閱讀活動花絮')
        cards.append(f'''<article class="recap-card" data-recap-year="{year}" data-recap-title="{escape(title, quote=True)}">
          <a href="{escape(item['href'], quote=True)}"><div class="recap-photo" style="--recap-img:url('{src}')"><img src="{src}" alt="{escape(title, quote=True)}" width="1200" height="800" loading="lazy" decoding="async"></div>
          <div class="recap-copy"><div class="recap-meta"><time datetime="{date}">{date.replace('-', '.')}</time><span>{status}</span></div><h3>{escape(title)}</h3><span class="recap-link">{cta} <span aria-hidden="true">↗</span></span></div></a></article>''')
    label_year = 'Year' if en else '年度'
    label_search = 'Search events' if en else '搜尋活動'
    options = ''.join(f'<option value="{year}">{year}</option>' for year in sorted(set(years), reverse=True))
    content = fragment(f'''<section class="page-section recap-section" id="recap" data-recap data-language="{'en' if en else 'zh'}"><div class="container">
      <div class="recap-heading"><div><p class="eyebrow">TIRI in Review</p><h2>{'Conferences &amp; shared moments' if en else '交流與活動紀錄'}</h2></div><p>{'Explore TIRI conferences, forums and professional exchanges.' if en else '回顧年度大會、國際論壇與專業交流，延續每一次相聚的收穫。'}</p></div>
      <div class="recap-toolbar"><div><label for="recap-year">{label_year}</label><select id="recap-year"><option value="all">{'All years' if en else '全部年份'}</option>{options}</select></div><div class="recap-search"><label for="recap-search">{label_search}</label><input id="recap-search" type="search" placeholder="{'Event title or year' if en else '活動名稱或年份'}"></div><p id="recap-count" role="status" aria-live="polite">{len(cards)} {'events' if en else '筆活動'}</p></div>
      <div class="recap-grid">{''.join(cards)}</div><p class="recap-empty" hidden>{'No matching events. Try another year or keyword.' if en else '沒有符合條件的活動，請調整年份或搜尋文字。'}</p>
    </div></section>''')
    soup.select_one('main > .page-section').replace_with(content.section)
    write(name, soup, True)
(OUT / 'source/recap-images.json').write_text(json.dumps(recap_sources, ensure_ascii=False, indent=2))

# Membership: forward-fill only the explicitly merged category/eligibility cells.
book = next(b for b in books if Path(b['file']).name == '會員類別總表.xlsx')
sheet = book['sheets'][0]
cells = {c['ref']:c['value'] for c in sheet['cells']}
for merged in sheet['merged_ranges']:
    start, end = merged.split(':')
    col = re.match('[A-Z]+', start)[0]
    if re.match('[A-Z]+', end)[0] != col:
        continue
    for row in range(int(re.search(r'\d+', start)[0]), int(re.search(r'\d+', end)[0])+1):
        cells.setdefault(f'{col}{row}', cells.get(start, ''))
member_rows = [{k:cells.get(f'{col}{r}', '') for k,col in [('group','A'),('name','B'),('eligibility','C'),('entrance','D'),('annual','E')]} for r in range(2,10)]
english_names = ['Permanent Full Individual Member','Full Individual Member','Associate Individual Member','Permanent Full Group Member','Full Group Member','Associate Group Member','Honorary Member','Sponsoring Member']
english_groups = ['Individual']*3 + ['Group']*3 + ['Special']*2
english_eligibility = [
    "Individuals who support the institute’s objectives, are at least 20 years old, and are company spokespersons or proxy spokespersons, supervisors or staff engaged in investor relations at companies or institutions, or professionals with long-standing involvement in capital-market investor relations.",
    "Individuals who support the institute’s objectives, are at least 20 years old, and are company spokespersons or proxy spokespersons, supervisors or staff engaged in investor relations at companies or institutions, or professionals with long-standing involvement in capital-market investor relations.",
    "Individuals who support the institute’s objectives, are at least 20 years old, are recommended by one member or member representative, and pay membership fees on time.",
    "Public or private agencies, enterprises or groups that support the institute’s objectives. Each appoints one representative to exercise membership rights and may appoint two additional people to participate in activities.",
    "Public or private agencies, enterprises or groups that support the institute’s objectives. Each appoints one representative to exercise membership rights and may appoint two additional people to participate in activities.",
    "Public or private agencies, enterprises or groups that support the institute’s objectives. Each appoints one representative to exercise membership rights and may appoint two additional people to participate in activities.",
    "Those who have made special contributions to the institute and are invited to join following council approval.",
    "Public or private institutions, groups or individuals that support the institute’s objectives and contribute funding to its activities."
]
def fees_en(value):
    if value == '-': return '—'
    return value.replace('元 / 次\n(免繳納常年會費)',' / once\n(No annual dues)').replace('元 / 年',' / year').replace('元','')

for name in ['membership.html','membership-567311.html']:
    soup = read(name)
    en = soup.html.get('lang') == 'en'
    html_rows = []
    labels = ['Category','Eligibility','Entrance fee','Membership dues'] if en else ['會員類別','對象與資格','入會費','常年會費／一次繳納']
    for i,row in enumerate(member_rows):
        values = [english_names[i] if en else row['name'], english_eligibility[i] if en else row['eligibility'], fees_en(row['entrance']) if en else row['entrance'], fees_en(row['annual']) if en else row['annual']]
        group = english_groups[i] if en else row['group']
        html_rows.append('<tr>'+f'<th scope="row"><span class="member-group">{group}</span>{escape(values[0])}</th>'+''.join(f'<td data-label="{labels[j]}">{escape(values[j]).replace(chr(10), "<br>")}</td>' for j in range(1,4))+'</tr>')
    note = ('Full and associate members enjoy the same benefits, except that full members must attend general meetings and vote in director and supervisor elections. Applications for full membership require signatures from two TIRI directors or supervisors; the secretariat submits them to the directors and supervisors meeting for approval.' if en else cells['A11'].removeprefix('註：\n'))
    new = fragment(f'''<section class="membership-categories" id="membership-categories"><p class="eyebrow">Membership Categories</p><div class="membership-heading"><h2>{'Membership categories &amp; fees' if en else '會員類別與會費'}</h2><p>{'All amounts in New Taiwan dollars. Entrance fees are payable once upon joining.' if en else '費用以新臺幣計；入會費僅於入會時收取一次。'}</p></div>
      <table class="membership-table"><caption class="visually-hidden">{'Membership categories, eligibility and fees' if en else '會員類別、申請資格及會費一覽'}</caption><thead><tr>{''.join('<th scope="col">'+label+'</th>' for label in labels)}</tr></thead><tbody>{''.join(html_rows)}</tbody></table>
      <div class="membership-notes"><h3>{'Application notes' if en else '申請說明'}</h3><p>{escape(note).replace(chr(10), '<br>')}</p></div></section>''')
    splits = soup.select('main .page-split')
    splits[0].replace_with(new.section)
    splits[1].decompose()
    write(name, soup)

for name in ['join.html','join-342161.html']:
    soup = read(name)
    en = soup.html.get('lang') == 'en'
    member_page = 'membership-567311.html' if en else 'membership.html'
    text = ('Applications for full membership require signatures from two TIRI directors or supervisors, followed by submission through the secretariat for approval at a directors and supervisors meeting. Entrance fees are separate from annual or one-time dues. Permanent full individual membership: NT$60,000 plus a one-time entrance fee of NT$2,000. Permanent full group membership: NT$600,000 plus a one-time entrance fee of NT$6,000.' if en else '申請正式會員，須由兩位 TIRI 理監事於申請書簽名，由秘書處於理監事會議時報請核准。入會費與常年會費／一次繳納費用分別計列：永久正式個人會員一次繳納 60,000 元，另收入會費 2,000 元；永久正式團體會員一次繳納 600,000 元，另收入會費 6,000 元。')
    section = fragment(f'<section class="page-section member-application-info" id="membership-fees"><div class="container"><p class="eyebrow">Membership &amp; Application</p><h2>{"Membership fees and full-member applications" if en else "會員會費與正式會員申請"}</h2><p>{text}</p><a class="u-link" href="{member_page}#membership-categories">{"View all membership categories and fees" if en else "查看完整會員類別、資格與會費"} →</a></div></section>')
    soup.select_one('main > .page-hero').insert_after(section.section)
    if en:
        for node in soup.find_all(string=lambda t: t and 'Individual permanent membership: Lump-sum' in t):
            node.replace_with('Permanent full individual membership: NT$60,000 payable once, plus a separate NT$2,000 entrance fee; no annual dues. Full membership is subject to the application and approval process described above.')
        label = soup.find('label', string='Permanent')
        if label: label.string = 'Permanent Full (subject to approval)'
    else:
        old_fee = soup.find('p', string=lambda t: t and '即為個人永久會員' in t)
        old_fee.string = '＊個人首次入會費用為 NT$8,000（入會費 2,000＋常年會費 6,000），隔年起常年會費 NT$6,000。永久正式個人會員一次繳納 NT$60,000，另收入會費 NT$2,000，免繳納常年會費；正式會員資格須依上述申請程序核准。'
        option = soup.find('option', string='永久（十年會費一次繳納）')
        if option:
            option['value'] = option.get('value', option.string)
            option.string = '永久正式（須經審核）'
    write(name, soup)

# Parse every nomination entry directly from the five source worksheets.
nom_book = next(b for b in books if Path(b['file']).name == '歷年TIRI_Awards入圍名單.xlsx')
nominees = {}
for sh in nom_book['sheets']:
    year = sh['name'][:4]
    cell = {c['ref']:str(c['value']).strip() for c in sh['cells']}
    groups = []
    columns = [('A','B','C'),('E','F','G'),('I','J','K'),('M','N','O'),('Q','R','S')] if year != '2026' else [(x,'','') for x in 'ABCDE']
    for code_col,cn_col,en_col in columns:
        rows = []
        for row in range(2,100):
            value = cell.get(f'{code_col}{row}','')
            if not value: continue
            if year == '2026':
                match = re.fullmatch(r'(\d{4})\s+(\S+)\s+(.+)', value)
                assert match, (sh['name'],row,value)
                code,cn,eng = match.groups()
            else:
                code = str(int(float(value)))
                cn,eng = cell[f'{cn_col}{row}'],cell[f'{en_col}{row}']
            rows.append({'code':code,'zh':cn,'en':eng,'sourceCell':f'{code_col}{row}'})
        title = cell[code_col+'1']
        title_match = re.match(r'(.+?)\s+(Listed|Large-sized|Small and).*',title)
        cn_title = title.split(' ')[0]
        en_title = title[len(cn_title):].strip()
        groups.append({'zh':cn_title,'en':en_title,'rows':rows})
    nominees[year] = groups

def roster(year,en):
    cards = []
    for group in nominees[year]:
        rows = ''.join(f'<li><span class="nominee-code">{r["code"]}</span><span class="nominee-company">{escape(r["en"] if en else r["zh"])}</span>'+('' if en else f'<span class="nominee-english">{escape(r["en"])}</span>')+'</li>' for r in group['rows'])
        cards.append(f'<section class="nominee-group"><h3>{escape(group["en"] if en else group["zh"])}</h3><ul class="nominee-list">{rows}</ul></section>')
    return '<div class="nominee-grid">'+''.join(cards)+'</div>'

soup = read('mission-206783.html')
for year in nominees:
    panel = soup.select_one('#edition-'+year)
    assert panel
    if year == '2026':
        panel.select_one('.roster-grid').replace_with(fragment(roster(year,False)).div)
    else:
        count = sum(len(g['rows']) for g in nominees[year])
        panel.append(fragment(f'<details class="nominee-disclosure" id="nominees-{year}"><summary>{year} 入圍企業名單 <span>{count} 家</span></summary><p class="nominee-note">依上市／上櫃與市值分組；得獎結果請見上方獲獎名單。</p>{roster(year,False)}</details>').details)
write('mission-206783.html',soup)
soup = read('mission-206783-803349.html')
old_grid = soup.select_one('.roster-grid')
split = old_grid.find_parent(class_='page-split')
new = fragment('<section class="all-nominees" id="all-nominees" data-nominees><div class="nominees-heading"><div><p class="eyebrow">Nominees</p><h2>Shortlisted companies</h2></div><div><label for="nominee-year">Year</label><select id="nominee-year">'+''.join(f'<option value="{y}">{y}</option>' for y in sorted(nominees,reverse=True))+'</select></div></div>'+''.join(f'<div class="nominee-panel" data-nominee-year="{y}"'+(' hidden' if y!='2026' else '')+'>'+roster(y,True)+'</div>' for y in sorted(nominees,reverse=True))+'</section>')
split.replace_with(new.section)
write('mission-206783-803349.html',soup,True)

(OUT/'source/nominees.json').write_text(json.dumps(nominees,ensure_ascii=False,indent=2))
(OUT/'source/membership.json').write_text(json.dumps(member_rows,ensure_ascii=False,indent=2))
(OUT/'source/changed-pages.json').write_text(json.dumps(changed,ensure_ascii=False,indent=2))
print('Updated pages:',len(changed),'; nominees:',{y:sum(len(g['rows']) for g in groups) for y,groups in nominees.items()})
