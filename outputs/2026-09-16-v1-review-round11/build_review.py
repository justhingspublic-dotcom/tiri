from pathlib import Path
from bs4 import BeautifulSoup
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
OLD = ROOT / 'outputs/2026-09-15-v1-review-round10'
SRC = OUT / 'source'
SRC.mkdir(exist_ok=True)

data = json.loads((OLD / '複檢資料.json').read_text())
assert len(data['items']) == 46
assert sum(item['reviewStatus'] == 'accepted' for item in data['items']) == 46

for item in data['items']:
    item['changedThisRound'] = False

item46 = next(item for item in data['items'] if item['id'] == '46')
change = ('依客戶正式英文資料，在英文 Membership Benefits 新增第 11 家合作夥伴 The Icons Media Group。'
          '完整加入公司簡介、Global Reputation and International Media Strategy、Global AI Search and Generative Engine Optimisation，'
          '以及 selected projects 15% off 和免費 45-minute Global Reputation and AI Recommendation Assessment；'
          '公司名稱連往 The Icons 官網，沿用已通過的 Logo 正片疊底效果。')
check = ('檢查英文頁：頁首應顯示 11 partner companies；最下方第 11 項應完整呈現客戶提供的公司名稱、簡介、兩項服務與會員優惠。'
         '確認 15% off selected projects、complimentary 45-minute assessment 文字正確；公司名稱連往 https://theicons.com/，'
         'Logo 白底應融入背景，手機版不得水平溢出。')
item46['reviewHistory'].append({
    'round': '2026-09-16 正式英文資料',
    'sourceVersion': 'conversation-20260916-theicons-en',
    'confirmed': False,
    'confirmationSource': 'conversation',
    'note': '客戶提供 The Icons Media Group 正式英文公司簡介、兩項服務及會員優惠內容。',
    'deliveryRevision': '20260916-theicons-en',
    'deliveredChange': change,
    'check': check,
    'deliveryLimit': '',
    'assistantResponse': '已依客戶原文加入英文會員優惠頁；中文已通過內容未更動。'
})
item46.update(
    reviewStatus='followup', deliveryStatus='ready',
    deliveryRevision='20260916-theicons-en',
    route='benefit-499886.html#benefit-partner-11',
    currentFocus='The Icons 正式英文會員優惠',
    currentChange=change,
    currentCheck=check,
    deliveryLimit='',
    assistantResponse='已使用客戶提供的正式英文原文，沒有自行改寫；Logo 與中文版一致使用正片疊底。',
    partialApproval='',
    extraLinks=[{'label': '已通過的中文版', 'route': 'benefit.html#benefit-partner-11'}],
    changedThisRound=True,
    confirmedAt=None,
    confirmedRound=None,
    confirmationSource='conversation'
)

# 使用者於對話確認英文版沒有問題，將第十一輪正式英文交付記錄為通過。
confirmed_at = '2026-09-16T02:37:52Z'
confirmation_note = 'ok 英文版我確認沒問題'
item46.update(
    reviewStatus='accepted', deliveryStatus='accepted', confirmedAt=confirmed_at,
    confirmedRound=11, confirmationSource='conversation'
)
item46['reviewHistory'].append({
    'round': '第十一輪複檢（對話確認）',
    'sourceVersion': 'tiri-v1-recheck-20260916-r11',
    'confirmed': True,
    'confirmationSource': 'conversation',
    'updatedAt': confirmed_at,
    'note': confirmation_note,
    'deliveryRevision': item46['deliveryRevision'],
    'deliveredChange': change,
    'check': check,
    'deliveryLimit': '',
    'assistantResponse': '第 46 項正式英文會員優惠已依使用者對話確認通過。'
})
data.setdefault('clientConfirmations', []).append({
    'round': 11,
    'recordedAt': confirmed_at,
    'source': 'conversation',
    'note': confirmation_note,
    'confirmedItems': ['46'],
    'scope': 'The Icons Media Group 正式英文會員優惠完整通過。'
})

data.update(
    version='tiri-v1-recheck-20260916-r11', round=11,
    sourceVersion='tiri-v1-recheck-20260915-r10b', sourceExportedAt=None,
    sourceType='conversation', sourceRecordedAt='2026-09-16',
    pendingEnglishSource={
        'id': '46', 'status': 'implemented_and_confirmed', 'receivedAt': '2026-09-16',
        'note': '客戶正式英文內容已由使用者提供、完成套版並確認通過。'
    },
    officialEnglishRequest={
        'id': '46', 'source': 'conversation',
        'record': '../2026-09-16-theicons-english/source/需求內容.md'
    }
)
assert sum(item['reviewStatus'] == 'accepted' for item in data['items']) == 46
assert [item['id'] for item in data['items'] if item['deliveryStatus'] == 'ready'] == []
serialized = json.dumps(data, ensure_ascii=False, indent=2)
(SRC / '本輪交付資料.json').write_text(serialized)
(OUT / '複檢資料.json').write_text(serialized)

for name in ['recheck.css', 'launch_review.py', '開啟複檢.command']:
    text = (OLD / name).read_text()
    text = text.replace('第十輪', '第十一輪').replace('2026-09-15-v1-review-round10', '2026-09-16-v1-review-round11')
    (OUT / name).write_text(text)
(OUT / '開啟複檢.command').chmod(0o755)

js = (OLD / 'recheck.js').read_text().replace('TIRI-v1-第十輪複檢結果.json', 'TIRI-v1-第十一輪複檢結果.json')
start = js.index("  $('delivery-notice').textContent =")
end = js.index('\n', start)
js = js[:start] + "  $('delivery-notice').textContent = '第 46 項 The Icons 正式英文會員優惠已確認通過；目前全部 46 項均已通過。';" + js[end:]
js = js.replace('pendingEnglishSource:data.pendingEnglishSource, exportedAt:timestamp(),', 'pendingEnglishSource:data.pendingEnglishSource, officialEnglishRequest:data.officialEnglishRequest, exportedAt:timestamp(),')
(OUT / 'recheck.js').write_text(js)

soup = BeautifulSoup((OLD / 'recheck.template.html').read_text().replace('2026.09.15', '2026.09.16'), 'html.parser')
soup.title.string = 'TIRI v1｜第十一輪複檢'
soup.h1.string = '第十一輪複檢'
soup.select_one('.eyebrow').string = 'REVIEW / 11'
soup.select_one('.intro').string = '第 46 項 The Icons 正式英文會員優惠已由使用者確認通過；中文版與其餘 45 項維持通過，目前全部 46 項均已完成驗收。'
for tag in soup.select('link[href*="recheck.css"],script[src*="recheck.js"]'):
    attr = 'href' if tag.name == 'link' else 'src'
    tag[attr] = tag[attr].split('?')[0] + '?v=20260916-r11'
for key, value in [('remaining', '0'), ('rechecked', '1'), ('accepted', '45'), ('waiting', '0')]:
    soup.select_one('#' + key).string = value
for button in soup.select('[data-filter]'):
    button.span.string = {'todo': '0', 'done': '1', 'accepted': '45', 'waiting': '0', 'all': '46'}[button['data-filter']]
    button['aria-pressed'] = str(button['data-filter'] == 'done').lower()
soup.select('.help p')[1].string = '第 46 項正式英文內容已依使用者對話確認通過；其餘 45 項沿用已通過紀錄。'
section = soup.select_one('#client-confirmations')
section.clear()
section.append(BeautifulSoup('<summary>本輪 1 項已確認通過</summary><p>46：The Icons Media Group 正式英文公司簡介、兩項服務、15% off selected projects 與免費 45 分鐘評估已確認通過。</p><p>中文版與 Logo 正片疊底已於第十輪通過；目前全部 46 項均已完成驗收。</p>', 'html.parser'))
soup.select_one('.footer-links').insert(0, BeautifulSoup('<a href="../2026-09-15-v1-review-round10/第十輪複檢.html" target="_blank" rel="noopener">第十輪複檢頁 ↗</a>', 'html.parser').a)
(OUT / 'recheck.template.html').write_text(str(soup))
(OUT / '第十一輪複檢.html').write_text(str(soup).replace('__RECHECK_DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')))

for name in ['實作備註-最後檢視.md', '圖片來源與處理紀錄.md']:
    shutil.copy2(OLD / name, OUT / name)
(OUT / '本輪修改紀錄.md').write_text('''# 第十一輪修改紀錄

- 46：依客戶 2026-09-16 提供的正式英文內容，在英文 Membership Benefits 新增第 11 家合作夥伴 The Icons Media Group。
- 完整加入公司簡介、兩項英文服務說明、selected projects 15% off，以及免費 45-minute Global Reputation and AI Recommendation Assessment。
- 公司名稱連至 https://theicons.com/，沿用已通過的 The Icons Logo 與正片疊底效果。
- 英文頁首合作夥伴數量由 10 更新為 11。
- 中文版及其餘 45 項維持已通過狀態。
- 重建站內搜尋索引。
- 使用者於第十一輪對話確認英文版沒有問題，第 46 項正式英文內容已通過。
''')
(OUT / '會議待辦核對.md').write_text('''# 第十一輪複檢狀態

客戶正式英文內容已收到、完成套版並由使用者確認通過。中文版與其餘 45 項維持通過。

原先「等待英文資料」已解除，目前 46 項均已通過，沒有本項資料缺口。
''')
(OUT / '剩餘待辦與補件.md').write_text('''# 目前待辦

- 46：The Icons 正式英文會員優惠已完成並確認通過。
- 中文版與其餘 45 項維持通過。
- 目前沒有待客戶補件或待複檢項目。
''')
(OUT / 'README.md').write_text('''# TIRI 第十一輪複檢

開啟 localhost 的「第十一輪複檢.html」，或雙擊「開啟複檢.command」。支援勾選、留言、自動保存、JSON 匯出與匯入。

45 項維持通過，第 46 項正式英文內容已於本輪確認通過，目前全部 46 項均已通過。加 ?test=1 使用獨立 sessionStorage 測試，不影響正式紀錄。
''')
print('Round 11 confirmed: 45 carried / 1 confirmed this round; all 46 accepted.')
