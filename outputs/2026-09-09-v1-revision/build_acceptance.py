from pathlib import Path
from html import escape as E
import re,json
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
checklist=ROOT/'V1修改Checklist.md'
original=OUT/'source/checklist-before-implementation.md'
if not original.exists():original.write_text(checklist.read_text())
text=original.read_text()
titles={int(i):title for i,title in re.findall(r'\*\*(\d{2})｜(.*?)\*\*',text)}
# These are delivered scope descriptions, not future tasks.
data={
1:('index.html','桌機、手機及搜尋分類同步為「會員服務」。','中文桌機與手機頁面已讀取；搜尋索引同步。'),
2:('index.html','Footer 會員服務欄改為會員登入，連到登入頁。','品牌欄的加入會員入口仍保留。'),
3:('index.html','核對原有統計顯示為 6300＋人。','這是既有內容驗證，沒有重複計為新增功能。'),
4:('index.html','首頁主內容依序活動訊息、線上課程、合作夥伴；保留 Banner 與統計。','活動區 3 筆非課程活動；線上課程 6 筆；合作夥伴 10 家。'),
5:('partners.html','05-A：10 家合作夥伴名稱、展示區與官網連結完成。','05-B 正式 Logo 待補。商周官網目前導向其系統中斷公告；本案不替外部網站填假內容。'),
6:('knowledge.html','本輪 13 張 CC0 情境圖已套用，另使用原活動、協會實拍及年刊封面。','Banner 用 1920px；A02 側圖 1440px；A03–A09 為 960px 卡片／側圖，未取得平台最高解析度。完整來源、尺寸及頁面對照已保存。'),
7:('about.html','協會簡介 7 段改左圖右文，約 4:6；手機圖上文下。','保留原有段落內容，使用符合段落的企業、市場與協會實拍。'),
8:('board.html?term=2022','08-A/B/C：第一、二屆中英文照片表格、姓名及公司／職稱分欄完成。','08-D 尚缺 7 位照片：余宛如、呂政達、呂軍甫、徐美華、烏恩婷、藍世旻、邱榮振。第三屆維持原展示。'),
9:('board.html','各理監事入口直接顯示第三屆；頁內可切換第一、二屆。','第三屆預設及第一、二屆切換實測；以鍵盤 End / Enter 選取第一屆通過。'),
10:('committee.html','五個委員會改為圖文卡片，分別連到各自內頁。','證照、獎項、專業、媒體、推廣五頁皆已建立。'),
11:('committee-professional.html','五個委員會各有職能、四欄名冊及其他四個委員會入口。','依委員會來源核對任職，沒有以第三屆理監事職称覆蓋委員會資料。'),
12:('certificate.html','鄧白氏雙標章 Banner 換成屋頂太陽能 ESG 照。','CC0 來源及 1920px 網站檔已記錄；保留既有證書／標章。'),
13:('news.html','活動改月份分組與橫向圖文列；Accupass 活動直接進原活動頁。','取得 127 個原 Banner；4 個 2019 Accupass 頁無原圖，保留文字；歷史文章維持原文章入口。'),
14:('news.html?term=2018','最新活動與活動訊息整合；舊 events.html 轉到 news.html 並保留章節。','2018–2026 共 153 筆；2018 與舊 #recap 轉址已實測。'),
15:('news.html','活動日期放大；月份與日期分開、層級清楚。','桌機日期 34px、手機 28px；首頁日期另依版面縮為 30 / 24px。'),
16:('news.html#recap','「精彩回顧」同步改為「活動花絮」。','v1 HTML、JS 已查無舊稱；本項只有名稱，新的花絮版型另等 17。'),
17:('news.html#recap','等待活動花絮版面參考。','現有歷史內容保留，尚未實作未提供的新參考版型。'),
18:('trainbod.html#inhouse','內容多元、到府服務、時間彈性三區加入對應圖片。','實際授課照片、企業空間、視訊學習；桌機三欄／手機排列已檢查。'),
19:('trainbod.html#inhouse','八大課程主題依 2026/7/17 PDF 更新，加入圖片及完整課綱入口。','八類名稱、範例課程與 PDF 頁碼對照完成，主下載入口也是同一版 PDF。'),
20:('trainbod.html','等待董監事課程正式 Banner。','不影響 18、19 的課程版面與內容。'),
21:('trainbod-384680.html','會計主管 Banner 換成手按計算機的照片。','1920px 網站檔；手機已確認手與計算機主體及白色標題。'),
22:('bodperform.html#process','績效評估改為四步驟：企業自評、文件審查、實地訪談、出具報告。','四步驟內容核對通過；手機轉為直列。Banner 另待 23。'),
23:('bodperform.html','等待董事會績效評估 Banner 方向／圖片。','流程已先完成，見 22。'),
24:('corpperform.html#process','公司治理輔導改六步驟，順序與箭頭一致。','桌機 3×2、手機直列，已實際檢查排列。Banner 另待 25。'),
25:('corpperform.html','等待公司治理 Banner 方向／圖片。','六步驟流程已先完成，見 24。'),
26:('certificates.html','「證照」與「獎項」拆開，中英文導覽、Footer 與總覽入口同步。','中文桌機及英文手機可見獨立入口；英文桌機不同寬度尚未補做視覺巡檢。'),
27:('certification.html#scholarship','IRC 證照與贊助獎學金合併於同頁，中英文同步、舊獎學金網址轉址。','保留原有條件、費用與申請連結；修正手機長網址造成的橫向溢出。'),
28:('tiric.html','TIRIC 講師照片縮小，維持完整人像與課程主題文字。','桌機 140×168、手機最大 120×145；原有 10 位講師資料保留。'),
29:('tiric.html#intro-video','保留單一白底介紹影片；第二個觀看入口改回同一影片。','原始 4K 與網站 1080p 全片 1,164 影格對照；SSIM 0.984248。瀏覽器實播至 34.1 秒未報錯，全長 38.846 秒。'),
30:('tiric.html#recap','TIRIC 課程回顧加入屆次下拉，保留已提供的 2025 回顧。','只有 2025 一項；沒有虛構其他年度。授證海報與年度大會照片保留並修正描述。'),
31:('mission-206783.html','TIRI Awards 第一至第五屆按鈕改為下拉，網址保存所選屆次。','五屆逐一切換實測，重整後能維持所選屆次。'),
32:('mission-206783-766399.html?term=2025','32-A：2026 第二屆與 2025 第一屆下拉，以及目前資料已完成。','2025 顯示 10 家得獎企業與頒獎照；2026 是 20 家入選企業，未寫成最終得獎。32-B 待缺少／正式資料。'),
33:('mission-206783.html','TIRI Awards Banner 使用指定整排獎座照。','使用本案照片，保留獎座主體。'),
34:('mission-206783-766399.html','潛力進展獎 Banner 使用指定桌上獎狀照。','使用本案照片，非一般素材圖替代。'),
35:('knowledge.html','27 篇文章加入主題圖；人物專訪核對人物；修正卡片錯篇連結。','本機文章逐篇核對標題，4 個外部原文核對；圖文對照表已保存。郭宗霖人物以會計研究月刊原文與 TIRI 資料確認。'),
36:('knowledge.html','加入頁內關鍵字搜尋、分類交集、結果數、清除及無結果提示。','ESG → 2 筆；加專訪 → 0 筆；清除 → 27 筆，瀏覽器實測通過。'),
37:('join.html','加入會員 Banner 換企業玻璃大樓形象照。','1920px CC0 網站檔，與會員／企業專業主題對應。'),
38:('benefit.html','「會員專屬優惠」同步改為「會員權利」。','頁名、各入口與 Footer 同步；v1 已查無舊稱。'),
39:('benefit.html','會員權利兩大區塊改左圖右文：協會服務、合作夥伴優惠。','原有服務內容及優惠條件保留；不是每一行優惠各放一圖。'),
40:('5th_report-516844.html#yearbooks','2023–2025 中英文六本年刊顯示完整封面，同步知識資源年刊區。','六本 PDF 可讀、年份／語言／封面／閱覽與下載目標核對一致；封面六宮格已人工檢查。'),
41:('5th_report-516844.html','等待年刊正式 Banner。','六本封面列表已完成，見 40。')}
wait={17,20,23,25,41};partial={5,8,32};rows=[]
for n in range(1,42):
 route,change,note=data[n];rows.append({'id':f'{n:02}','title':titles[n],'route':route,'status':'waiting' if n in wait else 'partial' if n in partial else 'ready','change':change,'note':note})
(OUT/'驗收資料.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
# Canonical markdown checklist: retain detailed requirements, add actual delivery evidence.
start=text.index('## 如何追蹤');body=text[start:]
body=body.replace('下列頁面連結目前指向現有本機檔案，用於定位，不代表已修改或已更新測試站。完成後在上方另填可用的預覽入口與日期。','下列原始頁面連結供定位；本輪實際預覽請使用上方 HTTP 入口。測試站尚未部署本輪版本。')
body=body.replace('| 可先動 | 33 |','| 可先動 | 32 |').replace('| 部分可先動 | 2 | 05 合作夥伴、32 潛力進展獎，先做可交付部分。 |','| 部分可先動 | 3 | 05 合作夥伴 Logo、08 歷屆照片、32 正式／缺少獎項資料；可交付部分已完成。 |')
blocks=re.split(r'(?=^- \[ \] \*\*\d{2}｜)',body,flags=re.M)
for k,block in enumerate(blocks):
 m=re.match(r'- \[ \] \*\*(\d{2})｜',block)
 if not m:continue
 n=int(m.group(1));r=rows[n-1]
 if n in wait:
  block=block.replace('等客戶｜未開始','等客戶｜待資料',1)
 elif n in partial:
  block=block.replace('部分可先動｜未開始','部分可先動｜已完成部分待你檢查',1).replace('可先動｜未開始','部分可先動｜已完成部分待你檢查',1)
  for child in {'5':['05-A'],'8':['08-A','08-B','08-C'],'32':['32-A']}[str(n)]:block=block.replace('- [ ] '+child,'- [x] '+child)
  if n==8:block=block.replace('  - 範圍：','  - [ ] 08-D 待補上述 7 位歷屆成員照片；目前顯示明確缺件位置。\n  - 範圍：',1)
 else:
  block=block.replace('- [ ] **','- [x] **',1).replace('可先動｜未開始','可先動｜待你檢查',1).replace('本機已有｜待核對','本機已有｜核對通過，待你檢查',1)
  block=re.sub(r'(- )\[ \]( \d{2}-[A-Z])',r'\1[x]\2',block)
 # Insert the concrete delivered behavior immediately under its title.
 first,sep,rest=block.partition('\n');block=first+'\n  - 本輪結果：'+r['change']+'\n  - 自測／限制：'+r['note']+'\n'+rest
 if n==6:block=block.replace('已有 [9 張候選預覽](outputs/2026-09-09-v1-revision/圖片候選預覽.html)，僅為 960px 預覽，不能因此勾選正式換圖完成。','13 張 CC0 圖已實際套版，詳見正式使用紀錄；A03–A09 的保存檔為 960px，限卡片／側圖使用，未宣稱取得平台最高解析度。')
 if n==9:block=block.replace('其餘入口尚未逐一核對，不能因此勾選整項完成。','本輪另完成共用入口靜態核對及本機屆次互動驗證。')
 blocks[k]=block
body=''.join(blocks)
body=body.replace('- [ ] 合作夥伴正式 Logo → 05-B。','- [ ] 合作夥伴正式 Logo → 05-B。\n- [ ] 7 位歷屆理監事照片 → 08-D（余宛如、呂政達、呂軍甫、徐美華、烏恩婷、藍世旻、邱榮振）。')
common_start=body.index('## 每批完成後的共通檢查');common_end=body.index('## 來源及維護紀錄',common_start)
body=body[:common_start]+'''## 本輪共通檢查

- [x] 15 份 Excel、33 個分頁已盤點；採用資料與缺件有記錄。
- [x] 主要頁面桌機／手機及互動檢查；修正 IRC 與潛力進展獎手機溢出。完整範圍與鎖定後未補測項見 QA 報告。
- [x] v1 143 個 HTML、5 個 CSS 靜態連結檢查：0 缺檔、0 指向正式 TIRI 的執行期引用；JavaScript 語法檢查通過。
- [x] 內容回歸檢查通過；原有詢問／報名欄位保留（首頁訂閱區依要求移除）。
- [x] 搜尋、五屆 Awards、理監事下拉及歷史轉址已實測；影片全片影格比對、PDF 六本檔案與連結核對完成。
- [x] 實際使用圖片、來源、尺寸、SHA-256 與逐篇配圖紀錄已保存；960px 圖與最高解析度未取回的限制已標示。
- [x] 搜尋索引已更新為 131 頁；新增委員會與證照／獎項分類已納入。
- [x] 本輪可驗收部分已列於頂端；「你已確認」全部留待你操作。
- [ ] 解鎖後補做英文桌機各寬度、手機導覽點擊及最新驗收入口畫面的完整巡檢；目前不宣稱這些補測已通過。

'''+body[common_end:]
body+='\n| 2026-09-09 | 完成可動部分並建立驗收入口；33 項整項可驗收、05／08／32 部分可驗收、5 項待資料。附來源、Excel 盤點與 QA 紀錄；電腦鎖定後未補做的視覺檢查明列。 | 本機 v1 已改；未部署測試站；待使用者驗收。 |\n'
intro='''# TIRI v1 修改 Checklist

更新：2026-09-09｜驗收版 r1。**33 項整項可驗收、3 項部分可驗收、5 項等資料**。本檔仍是 41 項工作的主要追蹤清單；勾選代表已實作／核對，沒有替你做驗收確認。

## 現在可以檢查的改動

先開 [驗收入口](http://localhost:4173/outputs/2026-09-09-v1-revision/驗收入口.html)，可依待驗收／等資料篩選、逐項記錄意見並匯出。若明天伺服器未啟動，雙擊 [開啟驗收.command](outputs/2026-09-09-v1-revision/開啟驗收.command)。本輪改動在本機 `v1`；線上測試站尚未更新。

[QA 報告](outputs/2026-09-09-v1-revision/QA報告.md) · [Excel 全部分頁盤點](outputs/2026-09-09-v1-revision/Excel分頁盤點.md) · [圖片來源與實際選用](outputs/2026-09-09-v1-revision/圖片選用表.md) · [參考版型分析](outputs/2026-09-09-v1-revision/參考版型分析.md)

| 編號／完成部分 | 改了什麼 | 預覽入口 | 自測結果與已知限制 | 你的確認 |
|---|---|---|---|---|
'''
for r in rows:
 if r['status']=='waiting':continue
 label=r['id']+({'05':'-A','08':'-A/B/C','32':'-A'}.get(r['id'],''))
 intro+=f'| {label} | {r["change"]} | [開啟頁面](http://localhost:4173/v1/html/{r["route"]}) | {r["note"]} | 待你確認 |\n'
checklist.write_text(intro+'\n'+body)
# Static review artifact works over the existing local preview server; no site navigation entry is added.
cards=[]
status_text={'ready':'可驗收','partial':'部分可驗收','waiting':'等資料'}
for r in rows:
 waiting=r['status']=='waiting'
 control='' if waiting else f'<label class="accept"><input type="checkbox" data-confirm="{r["id"]}"> 我已檢查這個完成部分</label>'
 cards.append(f'''<article class="item" data-status="{r['status']}" data-id="{r['id']}"><div class="item-top"><span class="number">{r['id']}</span><span class="badge {r['status']}">{status_text[r['status']]}</span></div><h2>{E(r['title'])}</h2><p>{E(r['change'])}</p><p class="note">{E(r['note'])}</p><a class="open" href="../../v1/html/{E(r['route'])}" target="_blank" rel="noopener">開啟頁面 ↗</a>{control}<details><summary>記錄檢查意見</summary><label class="sr" for="note-{r['id']}">{E(r['title'])}的檢查意見</label><textarea id="note-{r['id']}" rows="3" data-note="{r['id']}" placeholder="例如：第 2 張圖想換成……"></textarea></details></article>''')
html='''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>TIRI v1｜本輪驗收</title><style>
:root{--bg:#faf9f6;--ink:#211c28;--muted:#68606e;--line:#ddd7df;--purple:#6c1f93}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.75 -apple-system,BlinkMacSystemFont,'Noto Sans TC',sans-serif}main{max-width:1240px;margin:auto;padding:54px 32px 100px}a{color:var(--purple);text-underline-offset:4px}header{padding:0 0 36px;border-bottom:1px solid var(--line)}.eyebrow{font:12px/1.5 ui-monospace,monospace;letter-spacing:.16em;color:var(--purple)}h1{font-size:clamp(34px,5vw,60px);font-weight:550;letter-spacing:-.04em;margin:12px 0 14px;line-height:1.2}.intro{max-width:840px;color:var(--muted)}.stats{display:flex;gap:48px;margin:32px 0}.stats strong{font:36px/1.1 ui-monospace,monospace}.stats span{display:block;color:var(--muted);font-size:13px;margin-top:10px}.links{display:flex;flex-wrap:wrap;gap:12px 24px;font-size:14px}.toolbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:32px 0 20px}button{background:none;border:1px solid var(--line);font:inherit;padding:10px 18px;cursor:pointer;color:inherit}button[aria-pressed="true"],button.primary{background:var(--ink);color:white;border-color:var(--ink)}input[type="search"]{flex:1;min-width:180px;padding:12px;background:white;border:1px solid var(--line);font:inherit}.count{font-size:14px;color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}.item{border:1px solid var(--line);padding:28px;background:white;display:flex;flex-direction:column;min-width:0}.item[hidden]{display:none}.item-top{display:flex;align-items:center;justify-content:space-between}.number{font:24px/1 ui-monospace,monospace;color:var(--purple)}.badge{font-size:12px;padding:3px 10px;background:#f0eaf4;color:#632786}.badge.partial{background:#fff3d7;color:#795615}.badge.waiting{background:#eee;color:#555}h2{font-size:23px;line-height:1.45;font-weight:550;margin:20px 0 8px}p{margin:10px 0}.note{font-size:14px;color:var(--muted)}.open{display:block;margin:18px 0 24px;font-weight:550}.accept{display:flex;align-items:flex-start;gap:10px;font-size:14px;margin-top:auto;padding-top:20px;border-top:1px solid var(--line);cursor:pointer}input[type="checkbox"]{width:18px;height:18px;accent-color:var(--purple);margin:4px 0;flex-shrink:0}details{margin-top:18px;font-size:14px}summary{cursor:pointer;color:var(--muted)}textarea{display:block;width:100%;margin-top:12px;padding:12px;border:1px solid var(--line);font:inherit;resize:vertical}.sr{position:absolute;clip:rect(0,0,0,0);width:1px;height:1px;overflow:hidden}.completed{border-left:4px solid var(--purple)}.notice{padding:18px 22px;background:#f0ebf2;font-size:14px;margin-top:26px}.empty{padding:40px;border:1px solid var(--line);text-align:center}footer{font-size:13px;color:var(--muted);margin-top:40px}.end-actions{display:flex;gap:14px;align-items:center;margin-top:30px;flex-wrap:wrap}:focus-visible{outline:2px solid var(--purple);outline-offset:4px}@media(max-width:700px){main{padding:32px 18px 70px}.grid{grid-template-columns:1fr}.item{padding:22px}.stats{gap:30px}.toolbar input{flex-basis:100%}h2{font-size:21px}}@media print{.toolbar,.end-actions,textarea{display:none}.grid{display:block}.item{break-inside:avoid;margin-bottom:16px}.item[hidden]{display:block}}
</style></head><body><main><header><p class="eyebrow">TIRI · V1 REVISION · 2026.09.09 / R1</p><h1>明天從這裡驗收。</h1><p class="intro">已把可動部分套進 v1，下面每項都連到實際頁面。可以先看首頁、委員會、活動、課程、獎項與知識資源，再逐項留意見。勾選由你操作；「部分可驗收」只代表本輪已完成的部分。</p><div class="stats"><div><strong>33</strong><span>整項可驗收</span></div><div><strong>3</strong><span>部分可驗收</span></div><div><strong>5</strong><span>等待資料</span></div></div><div class="links"><a href="../../v1/html/index.html" target="_blank" rel="noopener">從首頁開始 ↗</a><a href="../../V1修改Checklist.md">完整 41 項 Checklist</a><a href="QA報告.md">QA 與已知限制</a><a href="圖片選用表.md">圖片來源</a><a href="參考版型分析.md">參考版型對照</a></div><div class="notice">這是本機驗收版，測試站尚未部署。本次有 7 位歷屆照片、正式 Logo、部分獎項資料與 5 項指定素材待補。最後一輪因電腦鎖定而未補跑的視覺檢查，已列於 QA 報告。</div></header><section aria-label="驗收項目"><div class="toolbar"><button data-filter="ready" aria-pressed="true">可驗收</button><button data-filter="waiting" aria-pressed="false">等資料</button><button data-filter="all" aria-pressed="false">全部 41 項</button><label for="q" class="sr">搜尋編號或項目</label><input id="q" type="search" placeholder="搜尋編號、頁面或改動"></div><p class="count" id="count" aria-live="polite"></p><div class="grid">'''+''.join(cards)+'''</div><p class="empty" hidden>沒有符合的項目，試試其他關鍵字。</p></section><div class="end-actions"><button class="primary" id="export">匯出我的檢查結果</button><span class="count" id="confirmed" aria-live="polite"></span></div><footer>勾選和意見會儲存在這個瀏覽器；可匯出成 JSON 留存。這些操作不會自動修改 Markdown Checklist。若明天預覽未啟動，雙擊同資料夾的「開啟驗收.command」。</footer></main><script>
const version='tiri-v1-review-20260909-r1';let saved={};try{saved=JSON.parse(localStorage.getItem(version)||'{}')}catch{};let filter='ready';const items=[...document.querySelectorAll('.item')];
function persist(){try{localStorage.setItem(version,JSON.stringify(saved))}catch{};document.getElementById('confirmed').textContent='已確認 '+Object.values(saved).filter(r=>r.confirmed).length+' 個完成部分';}
for(const card of items){const id=card.dataset.id;const box=card.querySelector('[data-confirm]');const note=card.querySelector('textarea');const row=saved[id]||{};if(box){box.checked=!!row.confirmed;card.classList.toggle('completed',box.checked);box.addEventListener('change',()=>{saved[id]={...(saved[id]||{}),confirmed:box.checked,updatedAt:new Date().toISOString()};card.classList.toggle('completed',box.checked);persist()})}note.value=row.note||'';note.addEventListener('input',()=>{saved[id]={...(saved[id]||{}),note:note.value,updatedAt:new Date().toISOString()};persist()})}
function render(){const q=document.getElementById('q').value.trim().toLowerCase();let n=0;for(const c of items){const inGroup=filter==='all'||(filter==='ready'?c.dataset.status!=='waiting':c.dataset.status==='waiting'||c.dataset.status==='partial');const show=inGroup&&c.textContent.toLowerCase().includes(q);c.hidden=!show;if(show)n++}document.getElementById('count').textContent='顯示 '+n+' 項'+(filter==='waiting'?'（含部分完成項目的缺件）':'');document.querySelector('.empty').hidden=n!==0;for(const b of document.querySelectorAll('[data-filter]'))b.setAttribute('aria-pressed',String(b.dataset.filter===filter))}
for(const b of document.querySelectorAll('[data-filter]'))b.addEventListener('click',()=>{filter=b.dataset.filter;render()});document.getElementById('q').addEventListener('input',render);document.getElementById('export').addEventListener('click',()=>{const result={version,exportedAt:new Date().toISOString(),items:items.map(c=>({id:c.dataset.id,title:c.querySelector('h2').textContent,deliveredStatus:c.dataset.status,...saved[c.dataset.id]}))};const url=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='TIRI-v1-驗收結果.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)});persist();render();
</script></body></html>'''
(OUT/'驗收入口.html').write_text(html)
print('Review generated:',len(rows),'items;',sum(r['status']=='ready' for r in rows),'ready;',sum(r['status']=='partial' for r in rows),'partial')
