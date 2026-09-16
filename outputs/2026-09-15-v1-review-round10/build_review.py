from pathlib import Path
from bs4 import BeautifulSoup
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
OLD = ROOT / 'outputs/2026-09-15-v1-review-round9'
SRC = OUT / 'source'
SRC.mkdir(exist_ok=True)
data = json.loads((OLD / 'source/本輪交付資料.json').read_text())
assert len(data['items']) == 45
assert [item['id'] for item in data['items'] if item['deliveryStatus'] == 'ready'] == ['32']

item32 = next(item for item in data['items'] if item['id'] == '32')
item32['changedThisRound'] = False

change = '在中文會員專屬優惠新增第 11 家合作夥伴「The Icons 英國艾肯仕國際媒體集團」。完整呈現全球聲譽與國際媒體操盤、跨國 AI 搜尋與生成式引擎優化兩項服務，以及專案 85 折和一次免費 45 分鐘診斷；官網連結與既有 Logo 已加入，Logo 使用正片疊底融入背景。'
check = '檢查中文版：確認合作夥伴索引新增 The Icons，點擊可跳到第 11 項；核對公司名稱、兩項服務、85 折與免費 45 分鐘診斷文字。點公司名稱應在新分頁開啟 https://theicons.com/；Logo 白底應以正片疊底自然融入卡片背景，手機版文字與 Logo 不應超出畫面。'
data['items'].append({
    'id': '46',
    'title': 'The Icons 會員專屬優惠',
    'route': 'benefit.html#benefit-partner-11',
    'reviewStatus': 'followup',
    'deliveryStatus': 'partial',
    'deliveryRevision': '20260915-theicons-zh',
    'deliveredChange': '本次新增項目。',
    'previousCheck': '',
    'nextAction': '',
    'assistantExplanation': '',
    'dependency': '',
    'partialApproval': '',
    'firstReview': {},
    'reviewHistory': [{
        'round': '2026-09-15 新增需求',
        'sourceVersion': 'conversation-20260915-theicons',
        'confirmed': False,
        'confirmationSource': 'conversation',
        'note': '請在會員專屬優惠新增 The Icons 英國艾肯仕國際媒體集團、服務說明、專案 85 折及免費 45 分鐘診斷。',
        'deliveryRevision': '20260915-theicons-zh',
        'deliveredChange': change,
        'check': check,
        'assistantResponse': '已依提供內容完成中文會員優惠頁，沿用專案既有 The Icons Logo，並以正片疊底融入背景。'
    }, {
        'round': '2026-09-15 英文範圍更正',
        'sourceVersion': 'conversation-20260915-theicons-en-pending',
        'confirmed': False,
        'confirmationSource': 'conversation',
        'note': '英文版他說明天會再給我',
        'deliveryRevision': '20260915-theicons-zh',
        'deliveredChange': change,
        'check': check,
        'deliveryLimit': '英文內容等待客戶正式提供。',
        'assistantResponse': '先前暫加的英文翻譯已撤回；英文頁維持原本 10 家，收到正式資料後再新增。'
    }],
    'previousRecheck': {
        'round': '新增需求', 'confirmed': False, 'note': '',
        'confirmationSource': 'conversation', 'recheck': None
    },
    'assistantResponse': '已加入中文第 11 家合作夥伴；內容依你提供的文字，公司名稱連往 The Icons 官網，Logo 使用正片疊底。英文頁等待客戶正式資料。',
    'currentFocus': 'The Icons 中文會員優惠；英文待正式資料',
    'currentChange': change,
    'currentCheck': check,
    'deliveryLimit': '英文版說明由客戶預計明日提供；本輪未使用自行翻譯內容，英文頁維持原本 10 家合作夥伴。',
    'extraLinks': [],
    'changedThisRound': True
})

# 使用者於本輪對話確認「兩項都通過」。第 32 項完整通過；第 46 項
# 以本輪已交付的中文內容與 Logo 為通過範圍，英文正式文字仍另行等待客戶。
confirmed_at = '2026-09-15T09:55:15Z'
confirmation_note = '兩項都通過'
item46 = next(item for item in data['items'] if item['id'] == '46')
item32.update(
    reviewStatus='accepted', deliveryStatus='accepted', confirmedAt=confirmed_at,
    confirmedRound=10, confirmationSource='conversation'
)
item32['reviewHistory'].append({
    'round': '第十輪複檢（對話確認）',
    'sourceVersion': 'tiri-v1-recheck-20260915-r10b',
    'confirmed': True,
    'confirmationSource': 'conversation',
    'updatedAt': confirmed_at,
    'note': confirmation_note,
    'deliveryRevision': item32['deliveryRevision'],
    'deliveredChange': item32['currentChange'],
    'check': item32['currentCheck'],
    'deliveryLimit': item32['deliveryLimit'],
    'assistantResponse': '第 32 項第一屆 20 家正式得獎名單已依使用者對話確認通過。'
})
item46.update(
    reviewStatus='accepted', confirmedAt=confirmed_at, confirmedRound=10,
    confirmationSource='conversation',
    partialApproval='中文版 The Icons 優惠內容與 Logo 正片疊底已通過；英文正式內容等待客戶提供。'
)
item46['reviewHistory'].append({
    'round': '第十輪複檢（對話確認）',
    'sourceVersion': 'tiri-v1-recheck-20260915-r10b',
    'confirmed': True,
    'confirmationSource': 'conversation',
    'updatedAt': confirmed_at,
    'note': confirmation_note,
    'deliveryRevision': item46['deliveryRevision'],
    'deliveredChange': change,
    'check': check,
    'deliveryLimit': item46['deliveryLimit'],
    'assistantResponse': '第 46 項本輪已交付的中文內容與 Logo 已確認通過；英文正式資料收到後再另輪補上。'
})
data.setdefault('clientConfirmations', []).append({
    'round': 10,
    'recordedAt': confirmed_at,
    'source': 'conversation',
    'note': confirmation_note,
    'confirmedItems': ['32', '46'],
    'scope': '32 完整通過；46 中文優惠內容與 Logo 通過，英文正式內容仍待客戶提供。'
})

data.update(
    version='tiri-v1-recheck-20260915-r10b', round=10,
    sourceVersion='tiri-v1-recheck-20260915-r9', sourceExportedAt=None,
    sourceType='conversation', sourceRecordedAt='2026-09-15',
    additionalRequest={'id': '46', 'source': 'conversation', 'record': '../2026-09-15-theicons-benefit/source/需求內容.md'},
    pendingEnglishSource={'id': '46', 'status': 'waiting_customer', 'expected': '2026-09-16', 'note': '客戶表示英文版說明將於明日提供。'}
)
assert len(data['items']) == 46
assert sum(item['reviewStatus'] == 'accepted' for item in data['items']) == 46
assert [item['id'] for item in data['items'] if item['deliveryStatus'] == 'ready'] == []
assert [item['id'] for item in data['items'] if item['deliveryStatus'] == 'partial'] == ['46']
serialized = json.dumps(data, ensure_ascii=False, indent=2)
(SRC / '本輪交付資料.json').write_text(serialized)
(OUT / '複檢資料.json').write_text(serialized)

for name in ['recheck.css', 'launch_review.py', '開啟複檢.command']:
    (OUT / name).write_text((OLD / name).read_text().replace('第九輪', '第十輪').replace('2026-09-15-v1-review-round9', '2026-09-15-v1-review-round10'))
(OUT / '開啟複檢.command').chmod(0o755)
js = (OLD / 'recheck.js').read_text().replace('TIRI-v1-第九輪複檢結果.json', 'TIRI-v1-第十輪複檢結果.json')
start = js.index("  $('delivery-notice').textContent =")
end = js.index('\n', start)
js = js[:start] + "  $('delivery-notice').textContent = '第 32 項與第 46 項本輪交付內容均已通過；46 英文正式說明等待客戶提供。其餘 44 項維持通過。';" + js[end:]
js = js.replace('contentDecision:data.contentDecision, exportedAt:timestamp(),', 'contentDecision:data.contentDecision, additionalRequest:data.additionalRequest, pendingEnglishSource:data.pendingEnglishSource, exportedAt:timestamp(),')
(OUT / 'recheck.js').write_text(js)

soup = BeautifulSoup((OLD / 'recheck.template.html').read_text(), 'html.parser')
soup.title.string = 'TIRI v1｜第十輪複檢'
soup.h1.string = '第十輪複檢'
soup.select_one('.eyebrow').string = 'REVIEW / 10'
soup.select_one('.intro').string = '第 32 項第一屆 20 家正式得獎名單，以及第 46 項 The Icons 中文會員優惠與 Logo 均已確認通過。英文正式資料等待客戶提供，其餘 44 項維持通過。'
for tag in soup.select('link[href*="recheck.css"],script[src*="recheck.js"]'):
    attr = 'href' if tag.name == 'link' else 'src'
    tag[attr] = tag[attr].split('?')[0] + '?v=20260915-r10b'
for key, value in [('remaining', '0'), ('rechecked', '2'), ('accepted', '44'), ('waiting', '0')]:
    soup.select_one('#' + key).string = value
for button in soup.select('[data-filter]'):
    button.span.string = {'todo': '0', 'done': '2', 'accepted': '44', 'waiting': '0', 'all': '46'}[button['data-filter']]
    button['aria-pressed'] = str(button['data-filter'] == 'done').lower()
soup.select('.help p')[1].string = '第 32 項與第 46 項本輪交付內容已依使用者對話確認通過；其餘 44 項沿用已通過紀錄。'
section = soup.select_one('#client-confirmations')
section.clear()
section.append(BeautifulSoup('<summary>本輪 2 項已確認通過</summary><p>32：第一屆潛力進展獎 20 家正式得獎企業已通過；第二屆維持入選。</p><p>46：The Icons 中文會員優惠與 Logo 正片疊底已通過。</p><p>英文說明等待客戶正式提供；英文頁目前維持原本 10 家，未使用自行翻譯內容。</p>', 'html.parser'))
soup.select_one('.footer-links').insert(0, BeautifulSoup('<a href="../2026-09-15-v1-review-round9/第九輪複檢.html" target="_blank" rel="noopener">第九輪複檢頁 ↗</a>', 'html.parser').a)
(OUT / 'recheck.template.html').write_text(str(soup))
(OUT / '第十輪複檢.html').write_text(str(soup).replace('__RECHECK_DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')))

for name in ['實作備註-最後檢視.md', '圖片來源與處理紀錄.md']:
    shutil.copy2(OLD / name, OUT / name)
(OUT / '本輪修改紀錄.md').write_text('''# 第十輪修改紀錄

- 46：會員專屬優惠新增第 11 家合作夥伴 The Icons 英國艾肯仕國際媒體集團。
- 完整加入全球聲譽與國際媒體操盤、跨國 AI 搜尋與生成式引擎優化，以及 TIRI 會員專案 85 折和免費一次 45 分鐘診斷。
- 公司名稱連至 https://theicons.com/，使用專案既有 The Icons Logo，並以正片疊底融入背景。
- 中文採客戶提供原文；先前暫加的英文翻譯已撤回，英文頁維持原本 10 家，等待客戶正式資料。
- 頁首合作夥伴數量改為 11，中文快速索引新增 The Icons。
- 使用者於第十輪對話確認第 32 項及第 46 項本輪中文交付內容均通過。
- 46 英文正式說明仍等待客戶提供；其餘 44 項維持通過。
- 重建站內搜尋索引。
''')
(OUT / '會議待辦核對.md').write_text('''# 第十輪複檢狀態

原會議與此前追加項目的歷史完整保留。第 32 項第一屆 20 家正式得獎名單，以及第 46 項 The Icons 中文會員專屬優惠與 Logo，已於本輪由使用者確認通過。

46 英文說明等待客戶明日提供；英文頁維持原本 10 家。其餘 44 項維持通過。
''')
(OUT / '剩餘待辦與補件.md').write_text('''# 目前待辦

- 32：2025 第一屆得獎 20 家，中英文已更新並確認通過。
- 46：The Icons 中文會員優惠與 Logo 正片疊底已確認通過；英文說明等待客戶明日提供。
- 其餘 44 項維持通過。
''')
(OUT / 'README.md').write_text('''# TIRI 第十輪複檢

開啟 localhost 的「第十輪複檢.html」，或雙擊「開啟複檢.command」。支援勾選、留言、自動保存、JSON 匯出與匯入。

44 項維持通過，第 32 項與 46 中文部分已於本輪確認通過。46 英文說明等待客戶提供。加 ?test=1 使用獨立 sessionStorage 測試，不影響正式紀錄。
''')
print('Round 10 confirmed: 44 carried / 2 confirmed this round; item 46 English pending.')
