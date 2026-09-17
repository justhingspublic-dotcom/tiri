from pathlib import Path
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
OLD = ROOT / 'outputs/2026-09-16-v1-review-round11'
SRC = OUT / 'source'
SRC.mkdir(exist_ok=True)
TEST_BASE = 'https://tiri-test.justhings.com.tw/html/'

data = json.loads((OLD / '複檢資料.json').read_text())
assert len(data['items']) == 46
assert all(item['reviewStatus'] == 'accepted' for item in data['items'])

for item in data['items']:
    previous_change = item.get('currentChange') or item.get('deliveredChange') or item.get('nextAction') or item['title']
    previous_check = item.get('currentCheck') or item.get('previousCheck') or f'在測試站開啟「{item["title"]}」頁面，確認內容與互動符合最終版本。'
    item.setdefault('reviewHistory', []).append({
        'round': '第十一輪結束狀態',
        'sourceVersion': 'tiri-v1-recheck-20260916-r11',
        'confirmed': True,
        'confirmationSource': item.get('confirmationSource') or 'carried-forward',
        'deliveryRevision': item.get('deliveryRevision', ''),
        'deliveredChange': previous_change,
        'check': previous_check,
        'deliveryLimit': item.get('deliveryLimit', ''),
        'note': '',
        'assistantResponse': item.get('assistantResponse', '')
    })
    item.update(
        reviewStatus='followup',
        deliveryStatus='ready',
        deliveryRevision='20260917-test-site-total',
        currentFocus='測試站全站總複檢',
        currentChange=previous_change,
        currentCheck=previous_check,
        deliveryLimit='',
        partialApproval='',
        changedThisRound=False,
        confirmedAt=None,
        confirmedRound=None,
        confirmationSource='total-review'
    )

# 總複檢現場發現並修正的兩項；只更新各自 revision，讓既有進度保留，這兩項若曾勾選則會重新開放。
items_by_id = {item['id']: item for item in data['items']}
items_by_id['33'].update(
    route='mission-206783-396345.html',
    extraLinks=[
        {'label': 'TIRI Awards 歷屆頁', 'route': 'mission-206783.html'},
        {'label': '英文獎項總覽', 'route': 'mission-206783-396345-512343.html'},
    ],
    deliveryRevision='20260917-total-fix1',
    currentFocus='9/17 總複檢回報修正',
    currentChange='獎項總覽原本誤用台北夜景 Banner，已改為客戶提供的整排 TIRI Awards 獎座照片；中文版與英文版同步。',
    currentCheck='開啟中文獎項總覽，確認 Banner 顯示整排金色 TIRI Awards 獎座；再檢查英文獎項總覽與歷屆頁使用相同獎項主題。',
    assistantResponse='依總複檢回報修正獎項總覽 Banner，不再使用與獎項無關的台北夜景。',
    changedThisRound=True,
)
items_by_id['42'].update(
    deliveryRevision='20260917-total-fix1',
    currentFocus='9/17 總複檢回報修正',
    currentChange='首頁三張輪播維持原圖片、文字與 6.5 秒自動切換；圖片顯示改為滿版填滿 Hero，依螢幕比例裁切，不再完整縮放並露出模糊留邊。',
    currentCheck='停留首頁查看三張輪播：每張圖片都應鋪滿整個首頁 Hero，四周沒有完整顯示造成的留邊；標題、介紹與按鈕維持不變。桌機與手機都請確認。',
    assistantResponse='依總複檢回報把三張首頁輪播圖統一改成滿版填滿。',
    changedThisRound=True,
)

# 這輪是整站重新驗收，不代表前 11 輪通過紀錄失效；歷史已保留在各項 reviewHistory。
data.update(
    version='tiri-v1-total-review-20260917-r1',
    round=12,
    sourceVersion='tiri-v1-recheck-20260916-r11',
    sourceExportedAt=None,
    sourceType='full-site-recheck',
    sourceRecordedAt='2026-09-17',
    testSite={
        'baseUrl': TEST_BASE,
        'requestedByUser': True,
        'note': '所有頁面檢查連結均指向 tiri-test.justhings.com.tw 測試站。'
    }
)
assert sum(item['reviewStatus'] == 'followup' for item in data['items']) == 46
assert sum(item['deliveryStatus'] == 'ready' for item in data['items']) == 46
serialized = json.dumps(data, ensure_ascii=False, indent=2)
(SRC / '本輪交付資料.json').write_text(serialized)
(OUT / '複檢資料.json').write_text(serialized)

# 沿用已驗證的複檢介面，只改為總複檢入口。
shutil.copy2(OLD / 'recheck.css', OUT / 'recheck.css')
for name in ['launch_review.py', '開啟複檢.command']:
    text = (OLD / name).read_text()
    text = text.replace('2026-09-16-v1-review-round11', '2026-09-17-v1-total-review')
    text = text.replace('第十一輪複檢.html', '總複檢.html')
    (OUT / name).write_text(text)
(OUT / '開啟複檢.command').chmod(0o755)

js = (OLD / 'recheck.js').read_text().replace('TIRI-v1-第十一輪複檢結果.json', 'TIRI-v1-總複檢結果.json')
js = js.replace("  const items = data.items;", "  const items = data.items;\n  const testSiteBase = data.testSite.baseUrl;")
js = js.replace("new URL('../../v1/html/' + link.route, location.href)", "new URL(link.route, testSiteBase)")
js = js.replace("new URL('../../v1/html/' + item.route, location.href)", "new URL(item.route, testSiteBase)")
js = js.replace("href=\"../../v1/html/board.html?term=2022\"", "href=\"https://tiri-test.justhings.com.tw/html/board.html?term=2022\"")
start = js.index("  $('delivery-notice').textContent =")
end = js.index('\n', start)
js = js[:start] + "  $('delivery-notice').textContent = '測試站總複檢：全部 46 項已重新開放；第 33、42 項已依本輪回報修正，請以最新內容檢查。前 11 輪紀錄均保留。';" + js[end:]
js = js.replace('officialEnglishRequest:data.officialEnglishRequest, exportedAt:timestamp(),', 'officialEnglishRequest:data.officialEnglishRequest, testSite:data.testSite, exportedAt:timestamp(),')
(OUT / 'recheck.js').write_text(js)

template = (OLD / 'recheck.template.html').read_text().replace('2026.09.16', '2026.09.17')
replacements = {
    '<title>TIRI v1｜第十一輪複檢</title>': '<title>TIRI v1｜測試站總複檢</title>',
    'recheck.css?v=20260916-r11': 'recheck.css?v=20260917-total-r1',
    'recheck.js?v=20260916-r11': 'recheck.js?v=20260917-total-r1',
    '<p class="eyebrow">REVIEW / 11</p>': '<p class="eyebrow">FULL REVIEW / 46</p>',
    '<h1>第十一輪複檢</h1>': '<h1>測試站總複檢</h1>',
    '<p class="intro">第 46 項 The Icons 正式英文會員優惠已由使用者確認通過；中文版與其餘 45 項維持通過，目前全部 46 項均已完成驗收。</p>': '<p class="intro">這一頁重新開放全部 46 項，讓你在交付客戶前逐項檢查測試站。此前通過紀錄完整保留；本輪勾選會另外保存。</p>',
    '<strong id="remaining">0</strong>': '<strong id="remaining">46</strong>',
    '<strong id="rechecked">1</strong>': '<strong id="rechecked">0</strong>',
    '<strong id="accepted">45</strong>': '<strong id="accepted">0</strong>',
    '<p>第 46 項正式英文內容已依使用者對話確認通過；其餘 45 項沿用已通過紀錄。</p>': '<p>總複檢使用全新的獨立儲存紀錄；46 項起始皆未勾選，不會覆蓋此前十一輪的驗收歷史。</p>',
    '<details class="help client-confirmations" id="client-confirmations"><summary>本輪 1 項已確認通過</summary><p>46：The Icons Media Group 正式英文公司簡介、兩項服務、15% off selected projects 與免費 45 分鐘評估已確認通過。</p><p>中文版與 Logo 正片疊底已於第十輪通過；目前全部 46 項均已完成驗收。</p></details>': '<details class="help client-confirmations" id="client-confirmations"><summary>總複檢方式與測試站</summary><p>全部 46 項重新檢查；每個「開啟頁面檢查」都會前往 tiri-test.justhings.com.tw 測試站。</p><p>若發現問題，先不要勾選，在該項「新的複檢意見」留言。全部檢查後匯出 JSON 給我。</p><p><a href="https://tiri-test.justhings.com.tw/html/index.html" target="_blank" rel="noopener">開啟測試站首頁 ↗</a></p></details>',
    '<button aria-pressed="false" data-filter="todo">待複檢 <span>0</span></button>': '<button aria-pressed="true" data-filter="todo">待複檢 <span>46</span></button>',
    '<button aria-pressed="true" data-filter="done">本輪已通過 <span>1</span></button>': '<button aria-pressed="false" data-filter="done">本輪已通過 <span>0</span></button>',
    '<button aria-pressed="false" data-filter="accepted">原已通過 <span>45</span></button>': '<button aria-pressed="false" data-filter="accepted">原已通過 <span>0</span></button>',
    '<div class="footer-links">': '<div class="footer-links"><a href="https://tiri-test.justhings.com.tw/html/index.html" target="_blank" rel="noopener">測試站首頁 ↗</a><a href="../2026-09-16-v1-review-round11/第十一輪複檢.html" target="_blank" rel="noopener">第十一輪複檢頁 ↗</a>',
}
for old, new in replacements.items():
    assert old in template, f'missing template marker: {old[:80]}'
    template = template.replace(old, new, 1)
(OUT / 'recheck.template.html').write_text(template)
(OUT / '總複檢.html').write_text(template.replace('__RECHECK_DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')))

for name in ['實作備註-最後檢視.md', '圖片來源與處理紀錄.md']:
    shutil.copy2(OLD / name, OUT / name)
(OUT / 'README.md').write_text('''# TIRI 測試站總複檢

開啟 localhost 的「總複檢.html」，或雙擊「開啟複檢.command」。

- 全部 46 項重新開始，起始皆未勾選。
- 所有頁面檢查連結指向 `https://tiri-test.justhings.com.tw/html/`。
- 保留前十一輪交付、留言與通過紀錄。
- 第 33 項獎項總覽 Banner、第 42 項首頁滿版輪播已依總複檢回報更新。
- 支援自動保存、留言、搜尋、篩選、JSON 匯出與匯入。
- 加上 `?test=1` 可用獨立 sessionStorage 測試，不影響正式總複檢紀錄。
''')
(OUT / '總複檢說明.md').write_text('''# 總複檢說明

這一輪沒有新增網站需求，而是交付客戶前的完整自檢。全部 46 項重新開放，每項按鈕直接連到 TIRI 測試站。

總複檢進行中追加修正：第 33 項獎項總覽改用 TIRI Awards 獎座 Banner；第 42 項首頁三張輪播改為滿版填滿。

檢查方式：

1. 開啟項目連結，在測試站確認桌機與手機畫面、文字、圖片、連結與互動。
2. 通過就勾選；有問題不要勾，直接在同一項留言。
3. 進度會保存在目前瀏覽器。
4. 完成後按「匯出複檢結果」，把 JSON 檔交回處理。
''')
(OUT / '剩餘待辦與補件.md').write_text('''# 剩餘待辦與補件

依照第十一輪結束狀態，會議紀錄內的 46 項皆已完成並通過。

本輪沒有列為等待客戶資料的項目；若總複檢時在測試站發現缺漏，請直接留在該項的「新的複檢意見」，匯出後再統一處理。
''')
(OUT / '本輪修改紀錄.md').write_text('''# 本輪修改紀錄

- 建立交付客戶前的全站總複檢頁。
- 將 46 項全部重新設為未勾選，使用獨立的本輪儲存紀錄。
- 保留前十一輪的通過、修改與留言歷史。
- 所有「開啟頁面檢查」連結改指向 `https://tiri-test.justhings.com.tw/html/`。
- 第 33 項：中文／英文獎項總覽 Banner 從台北夜景改為客戶提供的整排 TIRI Awards 獎座照。
- 第 42 項：首頁三張輪播圖片改為滿版填滿，依版面比例裁切，不再完整顯示並露出模糊留邊。
- 保留搜尋、狀態篩選、留言、自動保存、JSON 匯入與匯出功能。
''')
print('Total review: 46 items reopened against', TEST_BASE)
