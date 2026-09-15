from pathlib import Path
from bs4 import BeautifulSoup
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
OLD = ROOT / 'outputs/2026-09-14-v1-review-round7'
SRC = OUT / 'source'
SRC.mkdir(exist_ok=True)
raw = SRC / '第七輪複檢結果原檔.json'
if not raw.exists():
    shutil.copy2('/Users/jonathanyu/Downloads/TIRI-v1-第七輪複檢結果.json', raw)
review = json.loads(raw.read_text())
data = json.loads((OLD / 'source/本輪交付資料.json').read_text())
assert review['version'] == data['version'] and len(review['items']) == len(data['items']) == 45
rows = {item['id']: item for item in review['items']}
assert len(rows) == 45 and set(rows) == {item['id'] for item in data['items']}

for item in data['items']:
    row = rows[item['id']]
    assert isinstance(row['confirmed'], bool) and row['deliveryRevision'] == item['deliveryRevision']
    history = {
        'round': '第七輪複檢', 'sourceVersion': review['version'],
        'exportedAt': review['exportedAt'], 'confirmed': row['confirmed'],
        'note': row.get('note', ''), 'confirmationSource': row.get('confirmationSource'),
        'recheck': row.get('recheck'), 'deliveryRevision': item['deliveryRevision'],
        'deliveredChange': item.get('currentChange') or item['deliveredChange'],
        'check': item.get('currentCheck', ''), 'deliveryLimit': item.get('deliveryLimit', ''),
        'assistantResponse': item.get('assistantResponse', '')
    }
    item['reviewHistory'].append(history)
    item['previousRecheck'] = {key: history[key] for key in ['round', 'confirmed', 'note', 'confirmationSource', 'recheck']}
    if row['confirmed']:
        if item['reviewStatus'] != 'accepted':
            item.update(confirmedAt=row['recheck']['updatedAt'], confirmedRound=7, confirmationSource='seventh-recheck')
        item.update(reviewStatus='accepted', deliveryStatus='accepted')
    else:
        item.update(reviewStatus='followup', deliveryStatus='ready')
    item['changedThisRound'] = False
    if item['id'] == '17':
        item.update(
            deliveryRevision='20260914-r8', changedThisRound=True,
            currentFocus='年份選單內滾動不再帶動整頁',
            currentChange='修正中英文活動花絮年份選單的滾動邊界：滑鼠滾輪或觸控板在選單內滾動時，只捲動年份清單；捲到最上方或最下方繼續滾動，頁面也保持原位置。選單外及關閉後的頁面滾動維持正常，保留同高樣式、年份篩選與搜尋。',
            currentCheck='展開年份選單，把游標放在清單內上下滾動，並在最上方／最下方繼續滾動，確認背景頁面沒有跟著移動。把游標移到選單外或關閉選單，確認整頁可正常捲動；再選年份與搜尋。',
            assistantResponse='已重現原問題：清單到底後繼續滾動，整頁會跟著移動。原因是網站慣性捲動在清單邊界接手；現在會尊重選單的滾動範圍，不再將事件轉成整頁捲動。',
            extraLinks=[{'label': '英文活動花絮（同步修正）', 'route': 'news-971146-722067.html#recap'}]
        )
    if item['id'] == '23':
        item.update(currentFocus='第七輪已通過：董事會績效評估 Banner', currentCheck='', assistantResponse='已依第七輪勾選記錄通過，保留原圖稿與驗收時間。')
    if item['id'] == '25':
        item.update(currentFocus='第七輪已通過：公司治理 Banner 與兩頁流程圖融合效果', currentCheck='', assistantResponse='已依第七輪勾選記錄通過，包含本項 Banner 與兩頁流程圖的正片疊底效果。')
    if item['id'] in ['22', '24']:
        item['dependency'] = '兩頁流程圖的正片疊底效果已於第七輪第 25 項確認通過；此前流程內容與設計通過紀錄保留。'

# Preserve the in-round conversation correction without replacing the uploaded history.
feedback = json.loads((SRC / '第八輪對話補充.json').read_text())
item = next(item for item in data['items'] if item['id'] == '17')
item['reviewHistory'].append({
    'round': '第八輪對話補充', 'sourceVersion': 'tiri-v1-recheck-20260914-r8',
    'exportedAt': feedback['receivedAt'], 'confirmed': False,
    'note': feedback['note'], 'confirmationSource': 'conversation',
    'deliveryRevision': '20260914-r8', 'deliveredChange': item['currentChange'],
    'check': item['currentCheck'], 'assistantResponse': item['assistantResponse']
})
item.update(
    deliveryRevision='20260914-r8b',
    currentFocus='年份選單可再次點擊收起，滾動不帶動整頁',
    currentChange=item['currentChange'] + '另修正點擊關閉：再次點年份按鈕可收起，選取年份也會關閉；失焦事件不再干擾點擊。',
    currentCheck='點開年份選單，再點同一按鈕應收起；重新開啟後點任一年份，清單應關閉並完成篩選。也請確認清單內捲到底／頂時不帶動整頁，點外部及鍵盤 Escape 仍能關閉。',
    assistantResponse='已補上對話回報的關閉修正，避免點擊時暫時失焦造成選單先關閉再打開；中英文同步。原滾動修正一起保留。'
)

data.update(version='tiri-v1-recheck-20260914-r8', round=8, sourceVersion=review['version'], sourceExportedAt=review['exportedAt'])
data['clientConfirmations'] = [item for item in data['clientConfirmations'] if item['id'] == '17']
data['clientConfirmations'][0]['question'] = '活動花絮已有版型，剩本次年份選單滾動修正待複檢；沒有新增資料待提供。'
for item in data['meetingDependencies']:
    if item['id'] in ['23', '25']:
        item['status'] = '已於第七輪確認通過'
    if item['id'] == '17':
        item['status'] = '已有版型；年份選單滾動修正待第八輪複檢'
assert sum(item['reviewStatus'] == 'accepted' for item in data['items']) == 44
assert [item['id'] for item in data['items'] if item['deliveryStatus'] == 'ready'] == ['17']
approval_path = SRC / '第八輪對話通過.json'
approved = approval_path.exists()
if approved:
    approval = json.loads(approval_path.read_text())
    item = next(item for item in data['items'] if item['id'] == approval['id'])
    assert approval['confirmed'] is True and approval['deliveryRevision'] == item['deliveryRevision']
    history = {
        'round': '第八輪對話確認通過', 'sourceVersion': data['version'],
        'recordedAt': approval['recordedAt'], 'confirmed': True,
        'note': approval['note'], 'confirmationSource': 'conversation',
        'deliveryRevision': item['deliveryRevision'], 'deliveredChange': item['currentChange'],
        'check': item['currentCheck'], 'assistantResponse': item['assistantResponse']
    }
    item['reviewHistory'].append(history)
    item.update(reviewStatus='accepted', deliveryStatus='accepted', confirmedRound=8,
                confirmedAt=approval['recordedAt'], confirmationSource='conversation',
                currentFocus='第八輪已通過：年份選單滾動與點擊收起', currentCheck='',
                assistantResponse='已依你在對話中的「Ok我已打勾」記錄第 17 項通過。')
    data['clientConfirmations'] = []
    for dependency in data['meetingDependencies']:
        if dependency['id'] == '17':
            dependency['status'] = '已於第八輪由使用者對話確認通過'
    assert all(item['reviewStatus'] == 'accepted' for item in data['items'])
serialized = json.dumps(data, ensure_ascii=False, indent=2)
(SRC / '本輪交付資料.json').write_text(serialized)
(OUT / '複檢資料.json').write_text(serialized)

for name in ['recheck.css', 'launch_review.py', '開啟複檢.command']:
    (OUT / name).write_text((OLD / name).read_text().replace('第七輪', '第八輪').replace('2026-09-14-v1-review-round7', '2026-09-14-v1-review-round8'))
(OUT / '開啟複檢.command').chmod(0o755)
js = (OLD / 'recheck.js').read_text().replace("link.download='TIRI-v1-第七輪複檢結果.json'", "link.download='TIRI-v1-第八輪複檢結果.json'")
start = js.index("  $('delivery-notice').textContent =")
end = js.index('\n', start)
js = js[:start] + "  $('delivery-notice').textContent = '本輪修正 17 年份選單滾動與點擊收起；23、25 已於第七輪通過。44 項已通過、1 項可複檢，全部 45 項與歷次留言保留。';" + js[end:]
if approved:
    js = js.replace('本輪修正 17 年份選單滾動與點擊收起；23、25 已於第七輪通過。44 項已通過、1 項可複檢，全部 45 項與歷次留言保留。',
                    '17 已依本輪對話確認通過。全部 45 項已通過，0 項待複檢；歷次留言、修改與通過紀錄完整保留。')
(OUT / 'recheck.js').write_text(js)
soup = BeautifulSoup((OLD / 'recheck.template.html').read_text(), 'html.parser')
soup.title.string = 'TIRI v1｜第八輪複檢'
soup.h1.string = '第八輪複檢'
soup.select_one('.eyebrow').string = 'REVIEW / 08'
soup.select_one('.intro').string = '修正年份選單滾動與點擊收起問題，並保留本輪對話補充。23 績效評估 Banner、25 公司治理 Banner 與流程圖效果已通過；目前 44 項通過，只剩 17 可複檢。'
for tag in soup.select('link[href*="recheck.css"],script[src*="recheck.js"]'):
    attr = 'href' if tag.name == 'link' else 'src'
    tag[attr] = tag[attr].replace('20260914-r7', '20260914-r8b')
for key, value in [('remaining', '1'), ('rechecked', '0'), ('accepted', '44'), ('waiting', '0')]:
    soup.select_one('#' + key).string = value
for button in soup.select('[data-filter]'):
    button.span.string = {'todo': '1', 'done': '0', 'accepted': '44', 'waiting': '0', 'all': '45'}[button['data-filter']]
soup.select('.help p')[1].string = '第八輪獨立保存，不覆蓋前七輪。已帶入 23、25 的第七輪通過紀錄及 17 原留言；44 項此前通過預先勾選，本輪只剩 17 待你確認。'
section = soup.select_one('#client-confirmations')
section.clear()
section.attrs.pop('open', None)
section.append(BeautifulSoup('<summary>依原始會議記錄：1 項待複檢</summary><p>原會議 41 項中，40 項已通過；剩下 17 活動花絮的年份選單滾動修正。後續追加 42–45 皆已通過。</p><p>目前沒有新增會議資料待提供；實作缺圖與資料核對疑點繼續留待最後檢視。</p><p><a href="會議待辦核對.md" target="_blank" rel="noopener">會議待辦核對 ↗</a></p>', 'html.parser'))
soup.select_one('.footer-links').insert(0, BeautifulSoup('<a href="../2026-09-14-v1-review-round7/第七輪複檢.html" target="_blank" rel="noopener">第七輪複檢頁 ↗</a>', 'html.parser').a)
if approved:
    soup.select_one('.intro').string = '第 17 項年份選單滾動與點擊收起已確認通過。原會議 41 項與後續追加 4 項，合計 45 項全部通過；驗收與修改歷史完整保留。'
    soup.select_one('#remaining').string = '0'
    soup.select_one('#rechecked').string = '1'
    for button in soup.select('[data-filter]'):
        button.span.string = {'todo': '0', 'done': '1', 'accepted': '44', 'waiting': '0', 'all': '45'}[button['data-filter']]
        button['aria-pressed'] = str(button['data-filter'] == 'done').lower()
    soup.select('.help p')[1].string = '第 17 項已依你在對話中的確認記錄通過，連同此前 44 項共 45 項。可查看各項歷史、留言或匯出完整驗收紀錄。'
    section.clear()
    section.append(BeautifulSoup('<summary>依原始會議記錄：全部通過</summary><p>原會議 41 項與後續追加 42–45 全部通過，沒有待複檢主項目。</p><p>實作缺圖與名單核對疑點依先前指定保留在實作備註，留待最後檢視。</p><p><a href="會議待辦核對.md" target="_blank" rel="noopener">會議待辦核對 ↗</a></p>', 'html.parser'))
    for tag in soup.select('link[href*="recheck.css"],script[src*="recheck.js"]'):
        attr = 'href' if tag.name == 'link' else 'src'
        tag[attr] = tag[attr].replace('20260914-r8b', '20260914-r8-approved')
(OUT / 'recheck.template.html').write_text(str(soup))
encoded = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
(OUT / '第八輪複檢.html').write_text(str(soup).replace('__RECHECK_DATA__', encoded))
for name in ['實作備註-最後檢視.md', '圖片來源與處理紀錄.md']:
    shutil.copy2(OLD / name, OUT / name)
(OUT / '會議待辦核對.md').write_text('''# 第八輪會議待辦

原會議 41 項：40 項已通過，只剩 17 活動花絮年份選單滾動修正待複檢。23、25 已於第七輪通過。後續追加 42–45 皆通過，合計 44 通過、1 待複檢，共 45 項。

目前沒有新增會議資料待提供。既有照片、活動原圖與名單核對疑點，依使用者指定繼續記於[實作備註（最後再檢視）](實作備註-最後檢視.md)。

[原會議來源與逐項核對](../2026-09-14-v1-review-round6/會議待辦核對.md)保留供追溯。
''')
(OUT / '剩餘待辦與補件.md').write_text('''# 第八輪目前待辦

- 17：年份選單內滾動及頂／底邊界不再帶動整頁；再次點按鈕及選取年份可收起，已修正待複檢。
- 23、25 第七輪通過已記錄，合計 44 項通過。
- 沒有新增會議資料待提供。[實作備註留待最後檢視](實作備註-最後檢視.md)。
''')
(OUT / '本輪修改紀錄.md').write_text('''# 第八輪修改紀錄

依 2026-09-14 16:36 匯出的第七輪結果處理。

- 17：修正共用 main.js 慣性捲動接管邏輯。可捲動容器設定 overscroll-behavior: contain／none 時，頂部與底部仍交由原生容器處理，不再轉成整頁慣性捲動。樣式、清單、年份選取與搜尋維持原內容。
- 對話追加：recap-round7.js 改以焦點進入外部元素及點擊外部判斷關閉，避免 focusout 的空 relatedTarget 在 click 前搶先收起。再次點按鈕、選取年份、Escape 及外部關閉一併檢查。中英文頁更新該腳本版本為 r8b。
- 中英文活動花絮更新 main.js 版本參數，確保預覽載入修正。未新增全頁鎖定；游標在選單外或關閉後可正常捲動。
- 23、25：記錄第七輪通過時間與來源，全部歷史保留；44 通過、1 待複檢。

本輪修改共用捲動 JavaScript、活動花絮選單 JavaScript 與兩個活動花絮頁面的資源版本參數。原圖檔未更動。
''')
(OUT / 'README.md').write_text('''# TIRI 第八輪複檢

開啟 localhost 的「第八輪複檢.html」，或雙擊「開啟複檢.command」。支援勾選、留言、自動保存與 JSON 匯出／匯入。

44 項已通過，1 項可複檢。加 ?test=1 使用獨立 sessionStorage 進行測試，不影響正式紀錄。

使用專案 .venv/bin/python 執行本資料夾 build_review.py 可重新產生交付頁。第七輪原始匯出與交付前原始程式保存於 source。
''')
if approved:
    (OUT / '會議待辦核對.md').write_text('''# 第八輪會議驗收完成

原會議 41 項與後續追加 42–45，合計 45 項全部通過；0 項待複檢。

第 17 項已依使用者「Ok我已打勾」的對話確認記錄通過，來源保存於 source/第八輪對話通過.json；此前紀錄完整保留。

[實作備註（最後再檢視）](實作備註-最後檢視.md)維持原紀錄，尚未處理的素材與名單核對另列，不混入已完成的會議驗收。
''')
    (OUT / '剩餘待辦與補件.md').write_text('''# 會議驗收已全部通過

45 項全部通過，0 項待複檢。第 17 項年份選單滾動與點擊收起已由使用者對話確認。

先前另記的[實作備註](實作備註-最後檢視.md)仍保留，依使用者指定留待最後檢視。
''')
    with (OUT / '本輪修改紀錄.md').open('a') as file:
        file.write('\n## 第八輪通過確認\n\n使用者對話：「Ok我已打勾」。第 17 項已記錄通過，累計 45 項全部通過、0 待複檢。對話來源與記錄時間已保存；歷次交付與留言保留。\n')
    readme = OUT / 'README.md'
    readme.write_text(readme.read_text().replace('44 項已通過，1 項可複檢。', '45 項全部通過，0 項待複檢。'))
print('Round 8: 45 accepted / 0 ready' if approved else 'Round 8: 44 accepted / 1 ready (17)')
