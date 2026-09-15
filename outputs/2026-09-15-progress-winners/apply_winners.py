"""Apply the confirmed 2025 roster, preserving all unrelated page content."""
from pathlib import Path
from bs4 import BeautifulSoup
from html import escape
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
source = json.loads((OUT / 'source/winners-2025.json').read_text())
before = OUT / 'source/before'
cn_name = 'mission-206783-766399.html'
en_name = 'mission-206783-766399-942925.html'
cn = (before / cn_name).read_text()
en = (before / en_name).read_text()
cn_soup = BeautifulSoup(cn, 'html.parser')
en_soup = BeautifulSoup(en, 'html.parser')
en_names = {
    row.select_one('.code').get_text(strip=True): row.select_one('.award-company').get_text(strip=True)
    for row in en_soup.select('.progress-rosters li')
}

for group, cn_roster, en_roster in zip(
    source['groups'], cn_soup.select('#roster-2025 .roster'), en_soup.select('.progress-rosters .roster')
):
    cn_rows = []
    existing_en_rows = {row.select_one('.code').get_text(strip=True): str(row) for row in en_roster.select('li')}
    for company in group['rows']:
        code, name = company['code'], company['name']
        cn_rows.append(f'<li><span class="code">{escape(code)}</span><span class="award-company">{escape(name)}<small>{escape(en_names[code])}</small></span></li>')
    old_cn_ul, old_en_ul = str(cn_roster.ul), str(en_roster.ul)
    assert cn.count(old_cn_ul) == en.count(old_en_ul) == 1
    cn = cn.replace(old_cn_ul, '<ul>\n' + '\n'.join(cn_rows) + '\n</ul>')
    en = en.replace(old_en_ul, '<ul>\n' + '\n'.join(existing_en_rows[row['code']] for row in group['rows']) + '\n</ul>')

cn = cn.replace('>2025 年得獎企業</p>', '>2025 年得獎企業共 20 家<br/>上市 10 家・上櫃 10 家</p>')
en = en.replace('<p class="eyebrow">First Edition</p>', '<p class="eyebrow">2025 · First Edition</p>')
en = en.replace('<p class="eyebrow">Nominees</p>', '<p class="eyebrow">Winners</p>')
en = en.replace('<h2>List of Nominee Companies</h2>', '<h2>2025 Award Winners</h2>\n<p class="note" style="margin-top:8px">20 award winners<br/>10 TWSE-listed · 10 TPEx-listed</p>')
en = en.replace('<div class="roster-grid progress-rosters">', '<div class="roster-grid progress-rosters" id="roster-2025">')

assert str(BeautifulSoup(cn, 'html.parser').select_one('#edition-2026')) == str(cn_soup.select_one('#edition-2026'))
for name, content in [(cn_name, cn), (en_name, en)]:
    (ROOT / 'v1/html' / name).write_text(content)
print('Applied 2025: 10 TWSE + 10 TPEx winners; 2026 section unchanged.')
