from pathlib import Path
from bs4 import BeautifulSoup
import json
import shutil

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
OLD=ROOT/'outputs/2026-09-14-v1-review-round6'
SRC=OUT/'source'
SRC.mkdir(exist_ok=True)
raw=SRC/'第六輪複檢結果原檔.json'
if not raw.exists():shutil.copy2('/Users/jonathanyu/Downloads/TIRI-v1-第六輪複檢結果.json',raw)
review=json.loads(raw.read_text())
data=json.loads((OLD/'source/本輪交付資料.json').read_text())
assert review['version']==data['version'] and len(review['items'])==len(data['items'])==45
rows={i['id']:i for i in review['items']}
assert len(rows)==45 and set(rows)=={i['id'] for i in data['items']}
for item in data['items']:
    row=rows[item['id']]
    assert isinstance(row['confirmed'],bool)
    assert row['deliveryRevision']==item['deliveryRevision']
    history={'round':'第六輪複檢','sourceVersion':review['version'],'exportedAt':review['exportedAt'],'confirmed':row['confirmed'],'note':row.get('note',''),'confirmationSource':row.get('confirmationSource'),'recheck':row.get('recheck'),'deliveryRevision':item['deliveryRevision'],'deliveredChange':item.get('currentChange') or item['deliveredChange'],'check':item.get('currentCheck',''),'deliveryLimit':item.get('deliveryLimit',''),'assistantResponse':item.get('assistantResponse','')}
    item['reviewHistory'].append(history)
    item['previousRecheck']={k:history[k] for k in ['round','confirmed','note','confirmationSource','recheck']}
    if row['confirmed']:
        if item['reviewStatus']!='accepted':
            item.update(confirmedAt=row['recheck']['updatedAt'],confirmedRound=6,confirmationSource='sixth-recheck')
        item.update(reviewStatus='accepted',deliveryStatus='accepted')
    else:
        item.update(reviewStatus='followup',deliveryStatus='ready')
    item['changedThisRound']=False
    if item['id']=='17':
        item.update(deliveryRevision='20260914-r7',changedThisRound=True,currentFocus='年份選單沿用系統樣式，與搜尋欄同高',currentChange='中英文活動花絮的年份選單改用系統既有 term-picker 下拉樣式，字型、框線、圓角、箭頭及選取狀態一致；年份與搜尋欄皆固定 50px 高。支援滑鼠與鍵盤操作、年份與關鍵字交集篩選。',currentCheck='查看年份按鈕和右側搜尋欄是否同高、上下對齊；展開選單確認樣式。切換年份及搜尋後，確認結果正確；手機也確認高度。',assistantResponse='已依留言改為系統下拉元件的視覺，並使用同一組高度規格。')
    if item['id']=='25':
        item.update(deliveryRevision='20260914-r7',changedThisRound=True,currentFocus='兩個服務流程圖正片疊底；Banner 仍待確認',route='corpperform.html#process',currentChange='公司治理六步驟與董事會績效評估四步驟的流程圖，統一使用 CSS 正片疊底（multiply），並微調顯示亮度去除原圖淺灰底，讓白底融入網頁底色。董事會手機直式流程圖同步適用。圖片、文字與流程順序保持原內容；公司治理 Banner 沿用第六輪初稿。',currentCheck='檢查公司治理六步驟及另一頁董事會四步驟，白色矩形底是否已融入頁面、文字及箭頭是否清楚；手机查看董事會直式版本。此項也請一併確認原公司治理 Banner。',assistantResponse='留言中的處理已套用到兩張服務流程圖，以及董事會的手機圖片。這是網頁上的混色效果；點開原始 PNG 仍是原檔。',extraLinks=[{'label':'董事會流程圖（同樣已調整）','route':'bodperform.html#process'},{'label':'公司治理 Banner','route':'corpperform.html#service-banner'}])
    if item['id']=='23':
        item.update(currentFocus='沿用第六輪 Banner，仍待勾選確認',assistantResponse='第六輪此項未勾選、沒有留言，故保留待確認；本輪沿用原 Banner 初稿。')
    if item['id'] in ['22','24']:
        item['dependency']='本輪留言要求的流程圖正片疊底效果，合併在第 25 項檢查；本卡保留此前流程內容與設計的通過紀錄。'
data.update(version='tiri-v1-recheck-20260914-r7',round=7,sourceVersion=review['version'],sourceExportedAt=review['exportedAt'])
data['clientConfirmations']=[i for i in data['clientConfirmations'] if i['id']!='41']
for dependency in data['meetingDependencies']:
    if dependency['id']=='41':dependency['status']='紫色年刊 Banner 已於第六輪確認通過'
assert sum(i['reviewStatus']=='accepted' for i in data['items'])==42
assert [i['id'] for i in data['items'] if i['deliveryStatus']=='ready']==['17','23','25']
(SRC/'本輪交付資料.json').write_text(json.dumps(data,ensure_ascii=False,indent=2).replace('手机','手機'))
(OUT/'複檢資料.json').write_text((SRC/'本輪交付資料.json').read_text())
for name in ['recheck.css','launch_review.py','開啟複檢.command']:
    (OUT/name).write_text((OLD/name).read_text().replace('第六輪','第七輪').replace('2026-09-14-v1-review-round6','2026-09-14-v1-review-round7'))
(OUT/'開啟複檢.command').chmod(0o755)
js=(OLD/'recheck.js').read_text().replace("link.download='TIRI-v1-第六輪複檢結果.json'", "link.download='TIRI-v1-第七輪複檢結果.json'")
start=js.index("  $('delivery-notice').textContent =")
end=js.index('\n',start)
js=js[:start]+"  $('delivery-notice').textContent = '本輪修正 17、25 兩項；23 沿用前輪 Banner 待確認。42 項已通過、3 項可複檢，全部 45 項與歷次留言保留。';"+js[end:]
js=js.replace("currentFocus:item.currentFocus || '', deliveryStatus:item.deliveryStatus,", "currentFocus:item.currentFocus || '', deliveryStatus:item.deliveryStatus, changedThisRound:item.changedThisRound || false,")
js=js.replace("item.currentChange ? '這次已實際修改的內容'", "item.id === '23' ? '目前待確認的內容' : item.currentChange ? '這次已實際修改的內容'")
js=js.replace("item.deliveryLimit ? '本輪已修改部分通過'", "item.id === '23' ? '我已複檢，這項通過' : item.deliveryLimit ? '本輪已修改部分通過'")
(OUT/'recheck.js').write_text(js)
soup=BeautifulSoup((OLD/'recheck.template.html').read_text(),'html.parser')
soup.title.string='TIRI v1｜第七輪複檢'
soup.h1.string='第七輪複檢'
soup.select_one('.eyebrow').string='REVIEW / 07'
soup.select_one('.intro').string='依第六輪結果修正年份下拉與兩張流程圖白底；23 Banner 延續待確認。41 年刊、44 會員總表、45 Awards 名單已通過。全部保留 45 項：42 項通過、3 項可複檢。'
for tag in soup.select('link[href*="recheck.css"],script[src*="recheck.js"]'):
    key='href' if tag.name=='link' else 'src';tag[key]=tag[key].replace('20260914-r6','20260914-r7')
for id,value in [('remaining','3'),('rechecked','0'),('accepted','42'),('waiting','0')]:soup.select_one('#'+id).string=value
for button in soup.select('[data-filter]'):button.span.string={'todo':'3','done':'0','accepted':'42','waiting':'0','all':'45'}[button['data-filter']]
soup.select('.help p')[1].string='第七輪独立保存，不覆蓋前六輪。已匯入第六輪的 41、44、45 通過紀錄及 17、25 原留言，42 項此前通過預先勾選。本輪三項仍等你確認。'.replace('独','獨')
section=soup.select_one('#client-confirmations');section.clear();section.attrs.pop('open',None)
section.append(BeautifulSoup('<summary>依原始會議記錄：3 項待驗收／定稿</summary><p>原會議 41 項中，38 項已通過；剩下 17 活動花絮、23 績效評估 Banner、25 公司治理 Banner／本次流程圖調整。41 年刊 Banner 已於第六輪通過。</p><p>後續追加的 42–45 皆已通過。合作夥伴 Logo、董監事課程 Banner 素材、潛力進展獎歷屆資料已收到。實作缺圖與資料核對疑點繼續留待最後檢視，不增加客戶待補件。</p><p><a href="會議待辦核對.md" target="_blank" rel="noopener">會議待辦核對 ↗</a></p>','html.parser'))
footer=soup.select_one('.footer-links');footer.insert(0,BeautifulSoup('<a href="../2026-09-14-v1-review-round6/第六輪複檢.html" target="_blank" rel="noopener">第六輪複檢頁 ↗</a>','html.parser').a)
(OUT/'recheck.template.html').write_text(str(soup))
encoded=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('手机','手機')
(OUT/'第七輪複檢.html').write_text(str(soup).replace('__RECHECK_DATA__',encoded))
for name in ['實作備註-最後檢視.md','圖片來源與處理紀錄.md']:
    shutil.copy2(OLD/name,OUT/name)
with (OUT/'圖片來源與處理紀錄.md').open('a') as f:f.write('\n## 第七輪補充\n\n兩張流程圖沿用現有 PNG（董事會含手機版），網頁 CSS 改正片疊底，搭配 brightness(1.05) 將原圖接近白色的底色提為白色，避免混色後仍留下淡色方框。沒有重新生成圖片或改寫點陣檔。原檔連結保留原本白底；網頁呈現由 CSS 混色。\n')
(OUT/'會議待辦核對.md').write_text('# 第七輪會議待辦\n\n原會議 41 項：38 項已通過，17、23、25 待複檢。41 年刊 Banner 本次確認通過。後續追加 42–45 全部通過，合計 42 通過＋3 待複檢＝45。\n\n17 年份選單與 25 兩張流程圖依留言修正；23 未勾選也未留言，沿用前輪初稿待確認。\n\n會議原列待提供的 Logo、董監事 Banner 素材、潛力進展獎歷屆資料均已收到。[原會議來源與逐項核對](../2026-09-14-v1-review-round6/會議待辦核對.md)保留供追溯。\n\n實作缺圖與名單核對疑點依使用者要求留待最後：[實作備註](實作備註-最後檢視.md)。\n')
(OUT/'剩餘待辦與補件.md').write_text('# 第七輪目前待辦\n\n- 17：下拉系統樣式與搜尋同高，已修正待複檢。\n- 23：第六輪未勾選、無留言，Banner 延續待確認。\n- 25：两頁流程圖正片疊底已修正，與公司治理 Banner 一併確認。\n- 41、44、45 新增通過，現有 42 項通過保留。\n\n[會議核對](會議待辦核對.md) · [實作備註，最後再看](實作備註-最後檢視.md)\n'.replace('两','兩'))
(OUT/'本輪修改紀錄.md').write_text('''# 第七輪修改紀錄

依 2026-09-14 14:57 匯出的第六輪複檢结果處理。

- 17：中英文活動花絮使用既有 term-picker 視覺類別；按鈕與搜尋欄固定 50px，統一字型、框線、圓角、箭頭。保留篩選，加入完整鍵盤選單操作。
- 25：`corpperform.html` 及 `bodperform.html` 的 `.flow-image` 套用正片疊底及 brightness(1.05) 消除原圖淺色紙底，圖片祖先容器背景透明；董事會手機直式圖片同樣適用。原始 PNG 不改写。22／24 歷史通過保留，本次效果在 25 驗收。
- 23：無勾選、無留言，沿用第六輪圖稿，沒有自動通過。
- 41、44、45：正式記錄第六輪通過，保留時間、来源與歷史。

交付含 42 項已通過、3 項可複檢；其中 2 項本輪修正、1 項前輪延續。變更頁面 4 個，沒有重做已通過的名單與 Banner。
'''.replace('结果','結果').replace('改写','改寫').replace('来源','來源'))
(OUT/'README.md').write_text('# TIRI 第七輪複檢\n\n開啟「第七輪複檢.html」的 localhost 網址，或雙擊「開啟複檢.command」。支援勾選、留言、儲存、JSON 匯出／匯入。\n\n本轮 42 已通過、3 可複檢。測試加 `?test=1` 使用獨立 sessionStorage。\n\n使用專案 `.venv/bin/python` 執行 `apply_round7.py` 與 `build_review.py` 可重新建置。使用者第六輪原始匯出保存於 `source/第六輪複檢結果原檔.json`，第七輪交付資料保存於 `source/本輪交付資料.json`。\n'.replace('本轮','本輪'))
print('Round 7 ready: 42 accepted / 3 review / 2 changed + 1 carried forward')
