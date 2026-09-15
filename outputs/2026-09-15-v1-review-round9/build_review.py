from pathlib import Path
from bs4 import BeautifulSoup
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
OLD = ROOT / 'outputs/2026-09-14-v1-review-round8'
SOURCE = ROOT / 'outputs/2026-09-15-progress-winners/source'
SRC = OUT / 'source'
SRC.mkdir(exist_ok=True)
data = json.loads((OLD / 'source/本輪交付資料.json').read_text())
assert len(data['items']) == 45 and all(item['reviewStatus'] == 'accepted' for item in data['items'])
evidence = json.loads((SOURCE / 'winners-2025.json').read_text())
decision = evidence['decision']
shutil.copy2(SOURCE / 'winners-2025.json', SRC / '第一屆名單與對話確認.json')
item = next(item for item in data['items'] if item['id'] == '32')
item['reviewHistory'].append({
    'round': '第八輪結束狀態', 'sourceVersion': data['version'],
    'confirmed': True, 'confirmationSource': 'carried-forward',
    'deliveryRevision': item['deliveryRevision'], 'deliveredChange': item['currentChange'],
    'check': item['currentCheck'], 'deliveryLimit': item['deliveryLimit'],
    'note': '', 'assistantResponse': item['assistantResponse']
})
item['previousRecheck'] = {
    'round': '第八輪結束狀態', 'confirmed': True, 'note': '',
    'confirmationSource': 'carried-forward', 'recheck': None
}
item.update(
    reviewStatus='followup', deliveryStatus='ready', deliveryRevision='20260915-r9',
    changedThisRound=True, currentFocus='2025 第一屆：20 家正式得獎企業',
    currentChange='依新 Excel 更新第一屆正式得獎名單：中文從上市 7 家、上櫃 3 家，補齊為各 10 家，共 20 家。中文名稱與順序依新表，保留股票代碼及英文名稱的分列樣式。英文頁原有 20 家同步改標 Winners，並依新表排序。',
    currentCheck='查看第一屆：標示 2025 得獎共 20 家，上市與上櫃各 10 家；代碼、名稱與排列整齊。英文頁應標示 Winners / 2025 Award Winners。切到第二屆仍顯示入選企業名單。',
    assistantResponse='已依你確認的「那得獎就是20」套用新表。第一屆為正式得獎，第二屆依目前討論維持入選。這次只需複檢第 32 項的新名單，之前通過的版型與留言紀錄保留。',
    route='mission-206783-766399.html?term=2025#roster-2025',
    extraLinks=[
        {'label': '英文第一屆：20 家得獎', 'route': 'mission-206783-766399-942925.html#roster-2025'},
        {'label': '第二屆：維持入選', 'route': 'mission-206783-766399.html?term=2026#edition-2026'}
    ],
    nextAction='', deliveryLimit='', dependency='', partialApproval=''
)
for key in ['confirmedRound', 'confirmedAt', 'confirmationSource']:
    item.pop(key, None)
data.update(
    version='tiri-v1-recheck-20260915-r9', round=9,
    sourceVersion='tiri-v1-recheck-20260914-r8', sourceExportedAt=None,
    sourceType='conversation', sourceRecordedAt=decision['recordedAt'],
    contentDecision=decision, clientConfirmations=[]
)
data.pop('sourceConfirmedAt', None)
for dependency in data['meetingDependencies']:
    if dependency['id'] == '32':
        dependency['status'] = '第一屆新表 20 家已由使用者確認為正式得獎並套用；第二屆維持入選。本輪檢查更新後頁面。'
assert sum(item['reviewStatus'] == 'accepted' for item in data['items']) == 44
assert [item['id'] for item in data['items'] if item['deliveryStatus'] == 'ready'] == ['32']
serialized = json.dumps(data, ensure_ascii=False, indent=2)
(SRC / '本輪交付資料.json').write_text(serialized)
(OUT / '複檢資料.json').write_text(serialized)

for name in ['recheck.css', 'launch_review.py', '開啟複檢.command']:
    (OUT / name).write_text((OLD / name).read_text().replace('第八輪', '第九輪').replace('2026-09-14-v1-review-round8', '2026-09-15-v1-review-round9'))
(OUT / '開啟複檢.command').chmod(0o755)
js = (OLD / 'recheck.js').read_text().replace('TIRI-v1-第八輪複檢結果.json', 'TIRI-v1-第九輪複檢結果.json')
start = js.index("  $('delivery-notice').textContent =")
end = js.index('\n', start)
js = js[:start] + "  $('delivery-notice').textContent = '32 第一屆名單已更新為 20 家正式得獎，待本輪複檢；其餘 44 項已通過，全部 45 項與歷次驗收紀錄保留。';" + js[end:]
js = js.replace('sourceExportedAt:data.sourceExportedAt, exportedAt:timestamp(),', 'sourceExportedAt:data.sourceExportedAt, sourceType:data.sourceType, sourceRecordedAt:data.sourceRecordedAt, contentDecision:data.contentDecision, exportedAt:timestamp(),')
(OUT / 'recheck.js').write_text(js)
soup = BeautifulSoup((OLD / 'recheck.template.html').read_text(), 'html.parser')
soup.title.string = 'TIRI v1｜第九輪複檢'
soup.h1.string = '第九輪複檢'
soup.select_one('.eyebrow').string = 'REVIEW / 09'
soup.select_one('.masthead > span:last-child').string = '驗收工作區 · 2026.09.15'
soup.select_one('.intro').string = '依本次確認，第一屆潛力進展獎更新為 20 家正式得獎企業，第二屆維持入選。本輪只需檢查第 32 項的新名單；其餘 44 項已通過，之前的驗收歷史完整保留。'
for tag in soup.select('link[href*="recheck.css"],script[src*="recheck.js"]'):
    attr = 'href' if tag.name == 'link' else 'src'
    tag[attr] = tag[attr].split('?')[0] + '?v=20260915-r9'
for key, value in [('remaining', '1'), ('rechecked', '0'), ('accepted', '44'), ('waiting', '0')]:
    soup.select_one('#' + key).string = value
for button in soup.select('[data-filter]'):
    button.span.string = {'todo': '1', 'done': '0', 'accepted': '44', 'waiting': '0', 'all': '45'}[button['data-filter']]
    button['aria-pressed'] = str(button['data-filter'] == 'todo').lower()
soup.select('.help p')[1].string = '第九輪使用獨立儲存紀錄；第 32 項原版型的通過歷史保留，新名單待本輪勾選。其餘 44 項沿用已通過紀錄。'
section = soup.select_one('#client-confirmations')
section.clear()
section.append(BeautifulSoup('<summary>會議驗收與本次資料確認</summary><p>原會議 41 項與後續追加 4 項，已於第八輪全部通過。本次將第 32 項的新名單列入複檢，其餘 44 項維持通過。</p><p>第一屆的 20 家已確認為正式得獎企業並套用，第二屆維持入選；目前沒有新增會議資料待提供。</p><p><a href="會議待辦核對.md" target="_blank" rel="noopener">會議待辦核對 ↗</a></p>', 'html.parser'))
soup.select_one('.footer-links').insert(0, BeautifulSoup('<a href="../2026-09-14-v1-review-round8/第八輪複檢.html" target="_blank" rel="noopener">第八輪複檢頁 ↗</a>', 'html.parser').a)
(OUT / 'recheck.template.html').write_text(str(soup))
(OUT / '第九輪複檢.html').write_text(str(soup).replace('__RECHECK_DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')))
shutil.copy2(OLD / '圖片來源與處理紀錄.md', OUT / '圖片來源與處理紀錄.md')
notes = (OLD / '實作備註-最後檢視.md').read_text()
start = notes.index('## 32 ')
end = notes.index('## 14 ', start)
notes = notes[:start] + '''## 32 名單已依 2026-09-15 對話確認更新

- 第一屆：使用者確認「那得獎就是20」，已採新 Excel 的 20 家正式得獎企業，上市、上櫃各 10 家；新舊名單數量疑點已解決。
- 第二屆：使用者認為尚未得獎但不確定，現階段保留 20 家入選，不改為得獎。
- 中文名與排列依新表；英文簡稱沿用既有英文頁，不推造未提供的英文全名。中英文以股票代碼對應。
- 本次新名單待第九輪第 32 項複檢。來源及對話記錄見 source/第一屆名單與對話確認.json。

''' + notes[end:]
(OUT / '實作備註-最後檢視.md').write_text(notes)
(OUT / '會議待辦核對.md').write_text('''# 第九輪會議與複檢狀態

第八輪已完成原會議 41 項與追加 4 項的驗收。本次第一屆得獎 20 家已確認並套用，只將第 32 項的新內容列入複檢；44 項維持通過，1 項可複檢，共 45 項。

目前沒有新增會議資料待提供。第二屆維持入選。照片及早期活動原圖依使用者指定，仍放在[實作備註](實作備註-最後檢視.md)，最後再檢視。
''')
(OUT / '剩餘待辦與補件.md').write_text('''# 目前待辦

- 第 32 項：2025 第一屆得獎 20 家，中英文已更新，等待本輪複檢。
- 其餘 44 項維持通過；沒有新增會議資料待提供。
- 第二屆維持入選。非會議缺圖仍留在[實作備註](實作備註-最後檢視.md)。
''')
(OUT / '本輪修改紀錄.md').write_text('''# 第九輪修改紀錄

依 2026-09-15 使用者「那得獎就是20」的對話確認：第一屆 2025 潛力進展獎採新 Excel 的 20 家正式得獎企業。

- 中文第一屆：上市 7 家、上櫃 3 家補齊為各 10 家，依 Excel 股票代碼、中文簡稱與順序；英文簡稱沿用既有英文頁。保留雙欄與代碼／名稱分列，以及原頒獎照片。
- 英文第一屆：原已列 20 家，將 Nominees 改為 Winners / 2025 Award Winners，標明 2025、兩組各 10 家，順序與 Excel 一致。
- 中文第二屆區塊完整保留，仍為 20 家入選企業。
- 依 v1 README 重建搜尋索引。
- 第 32 項新名單待本輪驗收，其餘 44 項通過紀錄保留；不把資料確認當成修改後頁面的驗收通過。

原始資料與頁面快照在 ../2026-09-15-progress-winners/source；來源 workbook 未修改。本輪對話與名單記錄在 source/第一屆名單與對話確認.json。
''')
(OUT / 'README.md').write_text('''# TIRI 第九輪複檢

開啟 localhost 的「第九輪複檢.html」，或雙擊「開啟複檢.command」。支援勾選、留言、自動保存、JSON 匯出與匯入。

44 項維持通過，第 32 項新名單可複檢。加 ?test=1 使用獨立 sessionStorage 測試，不影響正式紀錄。

使用專案 .venv/bin/python 執行此目錄 build_review.py 可重建本輪網站；不覆蓋之前各輪驗收檔案。
''')
print('Round 9: 44 accepted / 1 ready (32).')
