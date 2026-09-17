from pathlib import Path
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCE = OUT / 'source/第一輪總複檢結果.json'
PREVIOUS = ROOT / 'outputs/2026-09-17-v1-total-review'
PREVIEW_BASE = 'https://justhingspublic-dotcom.github.io/tiri/v1/html/'

data = json.loads(SOURCE.read_text())
assert len(data['items']) == 46
assert [item['id'] for item in data['items'] if item.get('confirmed')] == [f'{index:02d}' for index in range(1, 46)]
assert data['items'][45]['id'] == '46'
assert data['items'][45].get('note') == '英文版的介面跟中文版的不一樣 icon沒放耶沒有正片疊底'

for item in data['items']:
    first_round_confirmed = bool(item.get('confirmed'))
    first_round_note = item.get('note', '')
    first_round_recheck = item.get('recheck') or {}
    item.setdefault('reviewHistory', []).append({
        'round': '總複檢第一輪',
        'sourceVersion': data['version'],
        'confirmed': first_round_confirmed,
        'confirmationSource': item.get('confirmationSource') or 'total-review',
        'deliveryRevision': item.get('deliveryRevision', ''),
        'deliveredChange': item.get('currentChange') or item.get('deliveredChange') or item['title'],
        'check': item.get('currentCheck') or item.get('previousCheck') or '',
        'deliveryLimit': item.get('deliveryLimit', ''),
        'note': first_round_note,
        'assistantResponse': item.get('assistantResponse', ''),
    })
    item['previousRecheck'] = {
        'round': '總複檢第一輪',
        'confirmed': first_round_confirmed,
        'note': first_round_note,
        'confirmationSource': 'total-review-first',
        'recheck': item.get('recheck'),
    }
    item['note'] = ''
    item['recheck'] = None
    if first_round_confirmed:
        item.update(
            reviewStatus='accepted',
            deliveryStatus='accepted',
            currentFocus='總複檢第一輪已通過',
            changedThisRound=False,
            confirmedAt=first_round_recheck.get('updatedAt'),
            confirmedRound=12,
            confirmationSource='total-review-first',
        )

item46 = data['items'][45]
item46.update(
    reviewStatus='followup',
    deliveryStatus='ready',
    deliveryRevision='20260917-total-r2-icons',
    currentFocus='總複檢第二輪修正',
    currentChange='英文 Membership Benefits 的合作夥伴區已改成與中文版相同的版型：加入合作情境圖、11 家快速入口、11 家逐列 Logo 與優惠內容。The Icons Logo 已放入第 11 列並套用正片疊底，白底會融入頁面底色。',
    currentCheck='檢查英文頁合作夥伴區：應有 11 家快速入口與 11 列完整優惠；每列左側有 Logo。第 11 家 The Icons Logo 應清楚顯示且沒有突兀白色方框；桌機與手機皆不得水平溢出。',
    assistantResponse='已依第一輪留言補齊英文版合作夥伴介面與 Logo，並讓 The Icons 使用與中文版相同的正片疊底處理。',
    extraLinks=[{'label': '中文版對照', 'route': 'benefit.html#benefit-partner-11'}],
    changedThisRound=True,
    confirmedAt=None,
    confirmedRound=None,
    confirmationSource='total-review-round2',
)

def new_item(item_id, title, revision, change, check, route, extra_links=None):
    return {
        'id': item_id,
        'title': title,
        'currentFocus': '總複檢第二輪新增調整',
        'deliveryStatus': 'ready',
        'changedThisRound': True,
        'deliveryRevision': revision,
        'originalReviewStatus': 'new',
        'deliveredChange': change,
        'previousCheck': '',
        'currentChange': change,
        'currentCheck': check,
        'deliveryLimit': '',
        'route': route,
        'extraLinks': extra_links or [],
        'nextAction': '',
        'assistantExplanation': '',
        'firstReview': {},
        'partialApproval': '',
        'previousRecheck': {'round': '新增需求', 'confirmed': False, 'note': '', 'confirmationSource': 'conversation', 'recheck': None},
        'reviewHistory': [],
        'assistantResponse': '',
        'dependency': '',
        'reviewStatus': 'followup',
        'confirmedAt': None,
        'confirmedRound': None,
        'confirmationSource': 'total-review-round2',
    }

data['items'].append(new_item(
    '47',
    '移除全站滾動慣性',
    '20260917-total-r2-native-scroll',
    '移除全站攔截滑鼠滾輪／觸控板並逐幀補間的自訂慣性程式，同時取消 CSS 平滑捲動；頁面回到瀏覽器原生捲動。',
    '在首頁、英文會員優惠及任一長頁面上下捲動，畫面應直接跟隨輸入，不再有網站額外延長的滑行或慢慢追上目標位置。頁內錨點也會直接定位。',
    'index.html',
    [
        {'label': '英文會員優惠長頁', 'route': 'benefit-499886.html'},
        {'label': '知識資源長頁', 'route': 'knowledge.html'},
    ],
))
data['items'].append(new_item(
    '48',
    '取消內容漸進式顯示',
    '20260917-total-r2-no-reveal',
    '全站內容不再依捲動位置逐段淡入；所有原本標記為 reveal 的標題、段落、卡片與列表會在頁面載入時直接顯示。',
    '重新整理首頁、英文會員優惠及任一長頁面，首屏與下方內容都應立即可見；向下捲動時不會再等待區塊淡入。',
    'index.html',
    [
        {'label': '英文會員優惠', 'route': 'benefit-499886.html#partners'},
        {'label': '董監事課程', 'route': 'trainbod.html'},
    ],
))

data.update(
    version='tiri-v1-total-review-20260917-r2',
    round=13,
    sourceVersion='tiri-v1-total-review-20260917-r1',
    sourceExportedAt=data.get('exportedAt'),
    sourceType='total-review-round2',
    sourceRecordedAt='2026-09-17',
    testSite={
        'baseUrl': PREVIEW_BASE,
        'requestedByUser': True,
        'note': '第二輪檢查連結均指向 GitHub Pages 預覽站。',
    },
)

assert len(data['items']) == 48
assert sum(item['reviewStatus'] == 'accepted' for item in data['items']) == 45
assert [item['id'] for item in data['items'] if item['reviewStatus'] == 'followup'] == ['46', '47', '48']

serialized = json.dumps(data, ensure_ascii=False, indent=2)
(OUT / '複檢資料.json').write_text(serialized)
(OUT / 'source/本輪交付資料.json').write_text(serialized)

shutil.copy2(PREVIOUS / 'recheck.css', OUT / 'recheck.css')
for name in ['launch_review.py', '開啟複檢.command']:
    text = (PREVIOUS / name).read_text()
    text = text.replace('2026-09-17-v1-total-review', '2026-09-17-v1-total-review-round2')
    text = text.replace('總複檢.html', '總複檢第二輪.html')
    (OUT / name).write_text(text)
(OUT / '開啟複檢.command').chmod(0o755)

js = (PREVIOUS / 'recheck.js').read_text()
js = js.replace('TIRI-v1-總複檢結果.json', 'TIRI-v1-總複檢第二輪結果.json')
old_notice = "  $('delivery-notice').textContent = 'GitHub Pages 總複檢：全部 46 項已重新開放；第 33、42 項已依本輪回報修正，請以最新內容檢查。前 11 輪紀錄均保留。';"
new_notice = "  $('delivery-notice').textContent = '第二輪：第一輪 45 項已通過；第 46 項英文優惠介面已修正，另新增第 47、48 項捲動與內容顯示調整，共 3 項待複檢。';"
assert old_notice in js
js = js.replace(old_notice, new_notice)
(OUT / 'recheck.js').write_text(js)

template = (PREVIOUS / 'recheck.template.html').read_text()
replacements = {
    '<title>TIRI v1｜GitHub Pages 總複檢</title>': '<title>TIRI v1｜總複檢第二輪</title>',
    'recheck.css?v=20260917-total-r1': 'recheck.css?v=20260917-total-r2',
    'recheck.js?v=20260917-total-r1': 'recheck.js?v=20260917-total-r2',
    '<p class="eyebrow">FULL REVIEW / 46</p>': '<p class="eyebrow">SECOND REVIEW / 48</p>',
    '<h1>GitHub Pages 總複檢</h1>': '<h1>總複檢第二輪</h1>',
    '<p class="intro">這一頁重新開放全部 46 項，讓你在交付客戶前先用 GitHub Pages 逐項檢查。此前通過紀錄完整保留；本輪勾選會另外保存。</p>': '<p class="intro">第一輪已有 45 項通過。本輪只需複檢英文 The Icons 介面，以及全站原生捲動與內容直接顯示，共 3 項；此前紀錄完整保留。</p>',
    '<strong id="remaining">46</strong>': '<strong id="remaining">3</strong>',
    '<strong id="accepted">0</strong>': '<strong id="accepted">45</strong>',
    '<p>總複檢使用全新的獨立儲存紀錄；46 項起始皆未勾選，不會覆蓋此前十一輪的驗收歷史。</p>': '<p>第二輪使用新的獨立儲存紀錄；第一輪已通過的 45 項保留為「此前已通過」，只重新開放 3 個本輪項目。</p>',
    '<details class="help client-confirmations" id="client-confirmations"><summary>總複檢方式與 GitHub Pages</summary><p>全部 46 項重新檢查；每個「開啟頁面檢查」都會前往 GitHub Pages 預覽站。</p><p>若發現問題，先不要勾選，在該項「新的複檢意見」留言。全部檢查後匯出 JSON 給我。</p><p><a href="https://justhingspublic-dotcom.github.io/tiri/v1/html/index.html" target="_blank" rel="noopener">開啟 GitHub Pages 首頁 ↗</a></p></details>': '<details class="help client-confirmations" id="client-confirmations"><summary>第二輪檢查方式</summary><p>待複檢只有第 46–48 項；每個「開啟頁面檢查」都會前往 GitHub Pages 最新版。</p><p>通過就勾選；有問題不要勾，直接在該項留言。全部檢查後匯出 JSON 給我。</p><p><a href="https://justhingspublic-dotcom.github.io/tiri/v1/html/index.html" target="_blank" rel="noopener">開啟 GitHub Pages 首頁 ↗</a></p></details>',
    '<button aria-pressed="true" data-filter="todo">待複檢 <span>46</span></button>': '<button aria-pressed="true" data-filter="todo">待複檢 <span>3</span></button>',
    '<button aria-pressed="false" data-filter="accepted">原已通過 <span>0</span></button>': '<button aria-pressed="false" data-filter="accepted">原已通過 <span>45</span></button>',
    '<button aria-pressed="false" data-filter="all">全部 <span>46</span></button>': '<button aria-pressed="false" data-filter="all">全部 <span>48</span></button>',
    '<div class="footer-links"><a href="https://justhingspublic-dotcom.github.io/tiri/v1/html/index.html" target="_blank" rel="noopener">GitHub Pages 首頁 ↗</a>': '<div class="footer-links"><a href="https://justhingspublic-dotcom.github.io/tiri/v1/html/index.html" target="_blank" rel="noopener">GitHub Pages 首頁 ↗</a><a href="../2026-09-17-v1-total-review/總複檢.html" target="_blank" rel="noopener">第一輪總複檢頁 ↗</a>',
}
for old, new in replacements.items():
    assert old in template, f'missing template marker: {old[:100]}'
    template = template.replace(old, new, 1)
(OUT / 'recheck.template.html').write_text(template)
(OUT / '總複檢第二輪.html').write_text(template.replace('__RECHECK_DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')))

(OUT / 'README.md').write_text('''# TIRI 總複檢第二輪

第二輪以 GitHub Pages 為驗收站，共 48 項：第一輪 45 項維持通過，3 項待複檢。

- 46：英文會員優惠改成與中文版相同的 11 家列式介面，補齊 Logo 與 The Icons 正片疊底。
- 47：移除全站自訂滾動慣性與 CSS 平滑捲動。
- 48：取消全站內容漸進淡入，內容直接顯示。
''')
(OUT / '剩餘待辦與補件.md').write_text('''# 剩餘待辦與補件

第一輪總複檢第 1–45 項已通過。本輪只有第 46–48 項待複檢，沒有等待客戶補件的項目。
''')
(OUT / '本輪修改紀錄.md').write_text('''# 第二輪修改紀錄

- 讀取第一輪總複檢結果：第 1–45 項通過，第 46 項需修正。
- 英文 Membership Benefits 改成與中文版相同的合作夥伴版型，顯示 11 家 Logo、快速入口與逐列優惠。
- The Icons Logo 使用 `mix-blend-mode: multiply` 融入頁面底色。
- 移除 `main.js` 的 wheel 慣性接管，恢復瀏覽器原生捲動。
- `html` 改用 `scroll-behavior: auto`。
- `.reveal` 改為直接顯示，不再透過 IntersectionObserver 逐段淡入。
- 136 個載入新版 `main.css`／`main.js` 的頁面更新快取版本。
''')
for name in ['圖片來源與處理紀錄.md', '實作備註-最後檢視.md']:
    shutil.copy2(PREVIOUS / name, OUT / name)
(OUT / '驗證紀錄.md').write_text('''# 總複檢第二輪驗證紀錄

驗證日期：2026-09-17

- 第一輪匯入 46 項：45 項通過，第 46 項含一則修正留言。
- 第二輪共 48 項：45 項此前已通過，3 項待複檢。
- 驗收頁預設只顯示第 46–48 項；68 個項目／延伸檢查連結全部指向 GitHub Pages。
- 英文優惠頁顯示 11 個快速入口及 11 列合作夥伴；The Icons Logo 實際尺寸 160 × 64，`mix-blend-mode` 為 `multiply`。
- `html` 的計算樣式為 `scroll-behavior: auto`。
- `.reveal` 的計算樣式為 `opacity: 1`、`transition-duration: 0s`。
- 獨立 `?test=1` 模式勾選第 46 項並輸入留言後重新整理，勾選、留言及 45／1／2 統計皆正確保留。
- 英文優惠頁與第二輪驗收頁的瀏覽器主控台均無 warning 或 error。
- `node --check v1/js/main.js` 與 `node --check recheck.js` 通過。
''')
print('Round 2: 45 accepted, 3 ready against', PREVIEW_BASE)
