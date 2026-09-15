"""Carry forward review history and package the sixth review."""
from pathlib import Path
from bs4 import BeautifulSoup
import copy
import json
import shutil

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[1]
OLD = ROOT / 'outputs/2026-09-11-v1-review-round5'
OUT = ROOT / 'outputs/2026-09-14-v1-review-round6'
(OUT/'source').mkdir(parents=True, exist_ok=True)
data = json.loads((OLD/'source/本輪交付資料.json').read_text())
oldversion = data['version']
fourth = json.loads((ROOT/'outputs/2026-09-10-v1-review-round4/複檢資料.json').read_text())
fourth_by_id = {i['id']:i for i in fourth['items']}
data.update(version='tiri-v1-recheck-20260914-r6', round=6, sourceVersion=oldversion)
data['clientConfirmations'] = [
 {'id':'17','title':'活動花絮版型','question':'會議記錄：排版形式還會再給參考（p.2）。目前已有圖文列表初稿，待驗收／確認採用；若要不同版型，再提供具體參考。','source':'原始會議記錄 p.2'},
 {'id':'23','title':'董事會績效評估 Banner','question':'會議記錄：對方會想用圖方向（p.3）。目前已有圖表評估情境初稿，待驗收／確認採用。','source':'原始會議記錄 p.3'},
 {'id':'25','title':'提升公司治理 Banner','question':'會議記錄：對方會想用圖方向（p.3）。目前已有文件檢視情境初稿，待驗收／確認採用。','source':'原始會議記錄 p.3'},
 {'id':'41','title':'年刊 Banner','question':'會議記錄：對方會再給圖（p.9）。已用資料夾中的紫色年刊底圖完成初稿，待驗收／確認採用。','source':'原始會議記錄 p.9'}
]
data['scopePolicy']='依使用者 2026-09-14 更正：先依原始會議記錄追蹤交付；實作過程發現的缺圖與資料核對疑點另記，最後再檢視，不列為本階段客戶未交資料。'
data['meetingDependencies']=[
 {'id':'05','title':'合作夥伴 Logo','source':'p.1、p.7','status':'已收到，相關版面已通過'},
 {'id':'17','title':'活動花絮版型參考','source':'p.2','status':'已有初稿，待驗收／定稿'},
 {'id':'20','title':'董監事課程 Banner','source':'p.2','status':'照片已收到，九張拼接 Banner 已通過'},
 {'id':'23','title':'績效評估 Banner 方向','source':'p.3','status':'已有初稿，待驗收／定稿'},
 {'id':'25','title':'公司治理 Banner 方向','source':'p.3','status':'已有初稿，待驗收／定稿'},
 {'id':'32','title':'潛力進展獎歷屆內容','source':'p.5','status':'新表已收到，不列未交件；版本核對另記，最後檢視'},
 {'id':'41','title':'年刊 Banner','source':'p.9','status':'已用現有底圖完成初稿，待驗收／定稿'}
]
specs = {
 '17':dict(route='news-971146.html#recap', currentChange='活動花絮改為雙欄圖文列表，加入年度篩選與關鍵字搜尋；手機改單欄。保留中文 11 筆、英文 10 筆原活動名稱、日期及連結，配對各活動原有圖片。2026 尚未舉辦的活動標為活動預告。', currentCheck='確認整體圖文版型；切換 2025 年、搜尋活動名稱、清除條件，再點活動卡片進入原文章。手機查看圖片與長標題是否完整。', currentFocus='新版圖文列表、年份篩選、搜尋', extraLinks=[{'label':'英文活動花絮','route':'news-971146-722067.html#recap'}]),
 '23':dict(route='bodperform.html#service-banner', currentChange='董事會績效評估 Banner 換成核對圖表、計算機與評估資料的 CC0 照片。原圖完整置中，周圍以同圖柔化延展，搭配深色遮罩讓標題清楚。中英文同步。', currentCheck='確認「圖表與資料評估」的用圖方向及桌機／手機標題可讀性。往下查看已通過的四步驟流程圖仍完整。', currentFocus='圖表評估情境 Banner', extraLinks=[{'label':'英文評估服務','route':'bodperform-583064.html#service-banner'}]),
 '25':dict(route='corpperform.html#service-banner', currentChange='提升公司治理 Banner 換成文件檢視、書寫紀錄與筆電工作的 CC0 照片，與績效評估頁使用不同圖片。原圖完整置中並以同圖柔化延展；中英文同步。', currentCheck='確認「文件檢視與工作紀錄」的用圖方向及桌機／手機標題可讀性。往下查看已通過的六步驟流程圖仍完整。', currentFocus='文件檢視情境 Banner', extraLinks=[{'label':'英文公司治理服務','route':'corpperform-750901.html#service-banner'}]),
 '41':dict(route='5th_report-516844.html#yearbook-banner', currentChange='年刊總覽 Banner 使用客戶資料夾的「TIRI七周年年刊背景.png」紫色底圖，以橫幅方式鋪陳並加深左側，保留原標題及已通過的六本封面列表。中英文同步。', currentCheck='確認紫色底圖用於年刊總覽的方向；查看桌機與手機，再確認下方封面與年刊連結仍可開啟。', currentFocus='現有紫色年刊底圖製作橫幅', extraLinks=[{'label':'英文年刊總覽','route':'5th_report-665763.html#yearbook-banner'}])
}
for item in data['items']:
    prior = fourth_by_id.get(item['id'])
    if prior and not any(h['round'].startswith('第四輪') for h in item['reviewHistory']):
        item['reviewHistory'].append({'round':'第四輪複檢結束狀態','sourceVersion':fourth['version'],'confirmed':prior['reviewStatus']=='accepted','confirmationSource':prior.get('confirmationSource','carried-forward'),'deliveryRevision':prior['deliveryRevision'],'deliveredChange':prior.get('currentChange') or prior.get('deliveredChange',''),'check':prior.get('currentCheck') or prior.get('previousCheck',''),'deliveryLimit':prior.get('deliveryLimit',''),'note':'','assistantResponse':prior.get('assistantResponse','')})
    item['reviewHistory'].append({
      'round':'第五輪複檢結束狀態', 'sourceVersion':oldversion,
      'confirmed':item['reviewStatus']=='accepted',
      'confirmationSource':item.get('confirmationSource','carried-forward'),
      'deliveryRevision':item['deliveryRevision'],
      'deliveredChange':item.get('currentChange') or item.get('deliveredChange',''),
      'check':item.get('currentCheck') or item.get('previousCheck',''),
      'deliveryLimit':item.get('deliveryLimit',''), 'note':'',
      'assistantResponse':item.get('assistantResponse','')})
    if item['id'] in specs:
        item.update(specs[item['id']])
        item.update(reviewStatus='followup',deliveryStatus='ready',deliveryRevision='20260914-r6',deliveryLimit='', nextAction='',dependency='',assistantResponse='依這次授權先完成可驗收版本。若本稿可以採用，這項就不必再向客戶索取素材；若要換方向，請在複檢意見註明具體調整。')
    if item['id']=='32':
        item['deliveryLimit']='會議約定的歷屆內容已收到，不列為客戶未交資料。新舊版本與名稱的核對記入「實作備註」，等會議項目收尾再處理；現有版面通過紀錄維持。'
    if item['id'] in ['08','14']:
        item['deliveryLimit']='實作時發現的歷史缺圖另存「實作備註」，依使用者指示最後統一檢視，不列入本階段會議待補件；原版面通過紀錄維持。'
    if item['id']=='42':
        item['deliveryLimit']='首頁圖片輪播維持已通過版本。服務頁的績效評估 Banner 已另完成第 23 項初稿，列本輪待複檢。'

base=dict(reviewStatus='followup',deliveryStatus='ready',deliveryRevision='20260914-r6',deliveredChange='',previousCheck='',nextAction='',assistantExplanation='',dependency='',partialApproval='',firstReview={},reviewHistory=[],previousRecheck={},assistantResponse='',deliveryLimit='')
data['items'] += [
 dict(copy.deepcopy(base),id='44',title='會員類別總表與入會說明',route='membership.html#membership-categories',currentFocus='最新 8 種會員類別、資格、會費與申請附註',currentChange='依「會員類別總表.xlsx」套入 8 種會員類別、完整資格、入會費與常年／一次繳納費用。永久正式個人會員 60,000 元＋入會費 2,000 元；永久正式團體會員 600,000 元＋入會費 6,000 元。補上正式會員需兩位 TIRI 理監事簽名等兩點附註，加入會員頁同步說明，中英文皆更新。',currentCheck='核對 8 種類別及資格；確認永久會員的一次繳納費、另列入會費、免常年會費，以及特殊會員費用維持原表的「-」。確認兩點附註與加入會員說明一致；手機表格改直式卡片。',extraLinks=[{'label':'加入會員說明','route':'join.html#membership-fees'},{'label':'英文會員總覽','route':'membership-567311.html#membership-categories'},{'label':'英文加入會員','route':'join-342161.html#membership-fees'}]),
 dict(copy.deepcopy(base),id='45',title='TIRI Awards 2022–2026 歷屆入圍名單',route='mission-206783.html?term=2025#nominees-2025',currentFocus='五個 Excel 分頁完整套入，入圍與得主分開呈現',currentChange='依最新五個分頁套入 2022 年 150 筆、2023 年 138 筆、2024 年 125 筆、2025 年 136 筆、2026 年 138 筆，共 687 筆。中文保留既有各屆得獎內容，2022–2025 另加可展開的入圍名單；英文新增五年份入圍切換。公司依股票代碼、名稱、上市／上櫃及市值組別排列。',currentCheck='在中文屆次選單切换各年，2022–2025 向下展開「入圍企業名單」，核對分組、人數與公司名稱。2026 直接顯示 138 筆入圍。英文也可選五個年份。確認原有得獎企業與頒獎照片仍保留。',assistantResponse='本項來源明確是 TIRI Awards 主獎「入圍名單」。潛力進展獎新舊得主範圍的差異另列客戶確認，沒有將入圍企業改稱得主。',extraLinks=[{'label':'2026 第五屆','route':'mission-206783.html?term=2026'},{'label':'英文五年入圍名單','route':'mission-206783-803349.html#all-nominees'}])]
assert len(data['items'])==45
assert sum(i['deliveryStatus']=='accepted' for i in data['items'])==39
assert sum(i['deliveryStatus']=='ready' for i in data['items'])==6
(OUT/'source/本輪交付資料.json').write_text(json.dumps(data,ensure_ascii=False,indent=2).replace('切换','切換'))
for name in ['recheck.css','build_recheck.py','launch_review.py','開啟複檢.command']:
    content=(OLD/name).read_text().replace('第五輪','第六輪').replace('2026-09-11-v1-review-round5','2026-09-14-v1-review-round6').replace("tiri_recheck_dir='/Users/jonathanyu/Desktop/Travail/Justhings/投資人協會 TIRI/WEB DEMO/outputs/2026-09-10-v1-review-round4'", "tiri_recheck_dir='/Users/jonathanyu/Desktop/Travail/Justhings/投資人協會 TIRI/WEB DEMO/outputs/2026-09-14-v1-review-round6'")
    (OUT/name).write_text(content)
(OUT/'開啟複檢.command').chmod(0o755)
js=(OLD/'recheck.js').read_text().replace('第五輪','第六輪')
js=js.replace("const preview = new URL", "const extraLinks = (item.extraLinks || []).map(link => { const url = new URL('../../v1/html/' + link.route, location.href); url.searchParams.set('review', item.deliveryRevision); return `<a class=\"open\" target=\"_blank\" rel=\"noopener\" href=\"${escapeText(url.href)}\">${escapeText(link.label)} ↗</a>`; }).join('');\n    const preview = new URL")
js=js.replace("${item.id === '08' ?", "${extraLinks}${item.id === '08' ?")
js=js.replace('${waitingItems.length} 項仍等資料。', '會議原項目尚有 17、23、25、41 四項初稿待定稿；實作備註留待最後檢視。')
js=js.replace('const result = {\n      version:', 'const result = {\n      clientConfirmations: data.clientConfirmations, meetingDependencies: data.meetingDependencies, scopePolicy: data.scopePolicy,\n      version:')
js=js.replace("route:item.route,", "route:item.route, extraLinks:item.extraLinks || [],")
js=js.replace('confirmedAt:item.confirmedAt || null,','confirmedAt:item.confirmedAt || null, confirmedRound:item.confirmedRound || null,')
js=js.replace('沿用你這次匯出的通過紀錄','沿用此前已確認的通過紀錄')
(OUT/'recheck.js').write_text(js)
template=(OLD/'recheck.template.html').read_text().replace('第五輪','第六輪').replace('20260911-r5-confirmed42-43','20260914-r6').replace('20260911-r5','20260914-r6').replace('2026.09.11','2026.09.14').replace('REVIEW / 05','REVIEW / 06')
soup=BeautifulSoup(template,'html.parser')
soup.select_one('.intro').string='本輪 6 項可複檢：活動花絮、兩張服務 Banner、年刊 Banner、會員總表、五年 Awards 入圍名單。原先 39 項已通過與歷次留言保留，全部共 45 項。'
for id,value in [('remaining','6'),('rechecked','0'),('accepted','39'),('waiting','0')]: soup.select_one('#'+id).string=value
soup.select_one('#waiting').find_next_sibling('span').string='等資料主項目'
notice=soup.select_one('p.delivery-notice');notice.decompose()
helpnotes=soup.select('.help p');helpnotes[1].string='第六輪獨立保存，不覆蓋前五輪。原有 39 項已通過並預先勾選，包括對話確認的 10、20、42 與 43。新交付的 6 項等你檢查，尚未替你打勾。'
for b in soup.select('[data-filter]'): b.span.string={'todo':'6','done':'0','accepted':'39','waiting':'0','all':'45'}[b['data-filter']]
client=BeautifulSoup('<details class="help client-confirmations" id="client-confirmations" open><summary>依原始會議記錄：4 項待驗收／定稿</summary><p>原會議 41 項中，37 項已通過，剩下 17、23、25、41 四項均已完成初稿。會議明列待提供的 7 組內容中，合作夥伴 Logo、董監事課程 Banner、潛力進展獎歷屆資料已收到。</p>'+''.join('<h3>'+x['id']+' '+x['title']+'</h3><p>'+x['question']+'</p>' for x in data['clientConfirmations'])+'<p>四項初稿若採用即可結案，無須再索取替代素材。42／43 是後續追加且已通過；44／45 是本次補充資料更新，另保留待複檢。</p><p><a href="會議待辦核對.md" target="_blank" rel="noopener">查看原會議 7 組待提供內容的逐項核對 ↗</a> · <a href="需要向客戶確認.md" target="_blank" rel="noopener">查看本階段確認清單 ↗</a></p><p>實作中發現的缺圖與資料核對疑點只記入備註，最後再檢視，不計入本階段會議待補件。</p></details>','html.parser')
soup.header.append(client.details)
footer=soup.select_one('.footer-links');footer.insert(0,BeautifulSoup('<a href="../2026-09-11-v1-review-round5/第五輪複檢.html" target="_blank" rel="noopener">第五輪複檢頁 ↗</a>','html.parser').a)
footer.append(BeautifulSoup('<a href="實作備註-最後檢視.md" target="_blank" rel="noopener">實作備註（最後再看） ↗</a>','html.parser').a)
(OUT/'recheck.template.html').write_text(str(soup).replace('四项','四項'))

audit=(ROOT/'outputs/2026-09-14-material-audit/最新資料與待辦盤點.md').read_text()
historical=audit.split('## 17 筆早期活動原圖清單')[1].split('## 建議處理順序')[0]
client_md='''# 本階段向客戶確認｜依原始會議記錄

2026-09-14 更正：本階段只依會議記錄追蹤交付。實作時發現的缺圖、名單版本核對等另記，最後再看。

## 可直接轉貼給客戶

您好，依上次會議記錄，以下四項已先完成初稿，請協助確認是否採用：

1. 活動花絮版型：圖文列表及年份篩選。
2. 董事會績效評估 Banner：圖表評估情境。
3. 提升公司治理 Banner：文件檢視情境。
4. 年刊 Banner：使用資料夾中的紫色年刊底圖。

若採用目前初稿，這四項即可定稿；如有不同方向，再請提供具體調整或替代參考。

會議原列待提供的合作夥伴 Logo、董監事課程 Banner 素材與潛力進展獎歷屆資料均已收到。

## 核對範圍

[會議待辦逐項核對與來源頁碼](會議待辦核對.md)。此清單已備妥，未代為傳送。
'''
(OUT/'需要向客戶確認.md').write_text(client_md)
meeting_md='''# 依原始會議記錄核對待辦｜2026-09-14

來源：[9 頁原始會議 PDF](../2026-09-09-v1-revision/source/2026-09-09-v1-meeting-notes.pdf)／[文字抽取紀錄](../2026-09-09-v1-revision/source/notes-extracted.txt)。狀態依第六輪交付與此前驗收確認更新。

原會議共有 41 個修改項目：37 項已通過，剩下 17、23、25、41 四項已完成初稿，待驗收／定稿。這不表示客戶仍欠四份檔案；採用現有初稿就不必再交替代素材。

## 會議明列由客戶後續提供的 7 組內容

| 編號 | 會議待提供內容 | 筆記頁碼 | 現況 |
|---|---|---|---|
'''+''.join(f"| {i['id']} | {i['title']} | {i['source']} | {i['status']} |\n" for i in data['meetingDependencies'])+'''
## 與會議待補件分開的事項

- 7 位歷屆理監事照片與 17 筆活動原圖：原會議沒有把這兩批數量／名單單列為客戶需補交的資料。會議有理監事放照片、活動使用 Banner 的版面要求；這兩批缺件是實作比對後發現的，依使用者指示留到最後再看。
- 潛力進展獎原本要求補歷屆內容，新檔已收到。2025 新舊名單數量及 2026 名稱屬收到資料後的核對疑點，不再當作會議漏交資料。
- 42／43 首頁輪播與地圖屬後續追加，已通過。
- 44／45 會員總表及 Awards 主獎五年入圍資料是本次補充更新，已實作、待複檢；不回算為原會議尚缺的項目。

原有驗收與留言完整保留；歷史內容中的「待補」只記錄當時判斷，目前追蹤範圍以此份更正為準。

[實作備註（最後再檢視）](實作備註-最後檢視.md)
'''
(OUT/'會議待辦核對.md').write_text(meeting_md)
(OUT/'剩餘待辦與補件.md').write_text('# 本階段待辦｜以會議記錄為準\n\n- 原會議 41 項：37 項已通過；17、23、25、41 四項初稿待驗收／定稿。\n- 會議原列待提供的 Logo、董監事 Banner 素材、潛力進展獎歷屆資料已收到。\n- 後續追加：42、43 已通過；44、45 補充資料更新已實作、待複檢。合計仍為 39 已通過＋6 待複檢，共 45 項。\n- 實作缺圖與資料核對疑點最後再看，不納入本階段客戶待補件。\n\n[會議逐項核對](會議待辦核對.md) · [本階段確認清單](需要向客戶確認.md)\n\n[實作備註（最後再檢視）](實作備註-最後檢視.md)\n')
(OUT/'實作備註-最後檢視.md').write_text('''# 實作備註｜會議項目收尾後再檢視

依使用者 2026-09-14 指示：此檔只保存實作時發現的缺件與疑點；不當作原會議未交資料，不在本階段要求客戶補件，也不撤銷已通過的版面。

## 08 歷史成員照片

7 位：余宛如、呂政達、呂軍甫、徐美華、烏恩婷、藍世旻、邱榮振。原始會議要求照片欄，但沒有單列這 7 位的補交名單。之後再決定是否補圖。

## 32 已收到名單的核對疑點

- 2025 潛力進展獎新表 20 家，舊得主表／現站 10 家；新表表頭「市值成長前10名」。之後核對是否替換或分入選／得獎呈現。
- 新表較舊得主多：4583 台灣精銳、8021 尖點、1419 新紡、5314 世紀*、6499 益安、8111 立碁、3434 哲固、4303 信立、3147 大綜、3709 鑫聯大投控。
- 2026 的 20 個代碼與現站一致；之後核對是否已正式得獎、需要修改名稱。
- 來源：`歷年潛力進展獎得獎名單.xlsx`／`2025(第一屆)!A1:B12、E1:F12`、`2026(第二屆)`；`歷年得主名單.xlsx`／`2025!B2:B3`。收到資料的事實與內容套用核對分開記錄。

## 14 早期活動原圖

以下 17 筆是實作時發現，沒有在會議中單列此補交清單。先保留文字呈現，最後再檢视。

'''+historical)
changes='# 第六輪修改紀錄｜2026-09-14\n\n'
for item in data['items']:
    if item['deliveryStatus']=='ready': changes += f"## {item['id']} {item['title']}\n\n{item['currentChange']}\n\n驗收：{item['currentCheck']}\n\n"
changes+='## 保留與追溯\n\n共更新 14 個中英文頁面，另新增本輪獨立 CSS／JS。來源拆解及修改前 HTML 保存在 `../2026-09-14-v1-round6/source/`；可重跑同資料夾 `apply_round6.py` 還原本輪建置。會員表來源 A1:E11；Awards 使用全五分頁，不讀單一預設分頁。\n\n原有 39 項通過與留言帶入本輪；新增內容以 44／45 另行追蹤。首頁輪播與地圖、兩張流程圖、潛力進展獎現有名單均保留。\n'
(OUT/'本輪修改紀錄.md').write_text(changes)
(OUT/'圖片來源與處理紀錄.md').write_text('''# 第六輪圖片來源與處理

| 用途 | 素材 | 來源／授權 | 呈現方式 |
|---|---|---|---|
| 23 董事會績效評估 | financial-analysis.jpg | [PxHere / asawin](https://pxhere.com/en/photo/1575617)，CC0 1.0；沿用 9/10 已核對素材 | 原圖完整置中、同圖 CSS 模糊延展、深色遮罩 |
| 25 提升公司治理 | document-review.jpg | [PxHere / rawpixel.com](https://pxhere.com/en/photo/1437661)，CC0 1.0；沿用 9/10 已核對素材 | 原圖完整置中、同圖 CSS 模糊延展、深色遮罩 |
| 41 年刊 | TIRI七周年年刊背景.png | 客戶提供，1054 × 1492 | 原始直式底圖以 CSS cover 填滿橫幅，部分上下裁切，左側加深 |
| 17 花絮列表 | 各活動既有圖片 | 客戶既有網站活動素材；不是 CC0 素材 | 對應各自活動，2025 使用已確認團體照，2026 使用既有活動圖，完整置中 |

前兩張沿用既存素材，不是新拍攝或 AI 生成人物。原始照片與年刊底圖未做點陣改寫；所有遮罩、比例及延展由網頁 CSS 呈現。花絮圖片對應明細見 `../2026-09-14-v1-round6/source/recap-images.json`。既有授權紀錄見 `../2026-09-10-v1-fixes/本輪圖片來源與授權.json`。
''')
(OUT/'README.md').write_text('''# TIRI v1 第六輪複檢

雙擊「開啟複檢.command」，或在瀏覽器開啟：

http://localhost:4173/outputs/2026-09-14-v1-review-round6/第六輪複檢.html

原有 39 項通過＋本輪 6 項待複檢＝45 項。可勾選、留言、自動儲存、匯出 JSON；換瀏覽器請用匯出／匯入。測試網址加 `?test=1` 可使用獨立 sessionStorage，正式紀錄不受影響。

建置：以具 bs4 的 Python 執行 `../2026-09-14-v1-round6/apply_round6.py`、`../2026-09-14-v1-round6/build_delivery.py`，最後執行本目錄 `build_recheck.py`。網頁內容與複檢來源分開保留，建置不寫入任何使用者驗收勾選。
''')
print('Packaged',OUT)
