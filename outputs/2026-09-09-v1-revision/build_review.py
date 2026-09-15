from pathlib import Path
import html
import json
import shutil

ROOT = Path(__file__).resolve().parent
assets = [
    dict(id='A01', key='accounting', file='f93067af653b27e4.jpg', title='手按計算機與財務作業', author='Wilfred Iven', slug='accounting-finance-JONMP7TPGK', resolution='3785 × 2514', theme='財務與會計', role='會計主管 Banner', priority='主題吻合', note='實際有人操作計算機，符合筆記指定動作。色調偏暖、設備較舊；橫幅以手和計算機為主，保留可讀的標題區。'),
    dict(id='A02', key='financial-report', file='9784221d4afc6a5f.jpg', title='財務圖表與計算機', author='Negative Space', slug='calculator-numbers-Y2GUBQIPXD', resolution='5472 × 3648', theme='財務與會計', role='財稅法律課程、財務文章', priority='主題吻合', note='黑白照片與 v1 的暖白、墨黑、紫色容易搭配。適合財報／會計主題卡片；沒有手部操作，因此不取代 A01 的具體需求。'),
    dict(id='A03', key='business-meeting', file='a2695738fb0eb5d0.jpg', title='企業團隊討論', author='Direct Media', slug='business-meeting-SSKSJIBMMP', resolution='6720 × 4480', theme='企業與治理', role='企業管理、併購實務、到府服務', priority='可用於主題卡片', note='穿著正式、互動自然，適合企業協商與工作討論。以一般情境圖呈現，人物不作為 TIRI 講師或委員介紹。'),
    dict(id='A04', key='capital-market', file='d69d2b9bd6642674.jpg', title='資本市場行情分析', author='Negative Space', slug='stockmarket-charts-G3YOGRBLF3', resolution='3888 × 2592', theme='資本市場', role='資本市場文章、協會簡介配圖', priority='主題吻合', note='股票圖表和筆電直接對應資本市場；適合文章縮圖或簡介側圖。主體在左，橫幅需避免裁掉螢幕上的圖表。'),
    dict(id='A05', key='online-learning', file='66facc93affe0ce2.jpg', title='專業人士線上交流', author='Direct Media', slug='video-meeting-NDASNYJJ6P', resolution='6720 × 4480', theme='課程與交流', role='線上課程、時間彈性、會員服務', priority='可用於主題卡片', note='視訊對談的手勢與電腦符合線上授課場景。與 A03 屬同一拍攝系列，同一頁建議擇一，避免反覆出現同一人物。'),
    dict(id='A06', key='esg-solar', file='0385a95337370cf7.jpg', title='再生能源與企業永續', author='Matt Bango', slug='solar-panels-EFYB8VJXNT', resolution='8192 × 5464', theme='ESG', role='鄧白氏 ESG Banner、ESG 主題', priority='主題吻合', note='太陽能板、植栽與自然光同時呈現科技和環境，適合作為 ESG 環境面情境照。Banner 保留面板與上方天空，避免只剩一般風景。'),
    dict(id='A07', key='office-interior', file='c6982a0fe00ce305.jpg', title='企業辦公與會議空間', author='Matt Moloney', slug='office-interior-NSQTXCLWQ5', resolution='6000 × 4000', theme='企业與治理', role='到府服務配圖備選', priority='備選', note='具有企業空間感，但較接近共享辦公環境。可用於到府服務情境；不列為正式董事會評估 Banner 的首選。'),
    dict(id='A08', key='media-communication', file='7471e79687426996.jpg', title='媒體溝通與發言', author='donterase', slug='microphone-equipment-UOVOJOP3UK', resolution='4896 × 3264', theme='媒體與溝通', role='媒體與危機管理、媒體委員會', priority='主題吻合', note='專業麥克風與留白直接對應媒體、發言及內容製作；不含現場人物，方便用在主題卡片。錄音室風格，並非 TIRI 活動實拍。'),
    dict(id='A09', key='corporate-building', file='ae91111bd5dbf48e.jpg', title='企業建築與專業形象', author='Verne Ho', slug='office-building-7HRFNYC7GU', resolution='4657 × 3105', theme='企業與治理', role='加入會員 Banner、協會簡介', priority='可作 Banner 候選', note='橫式、上方暗部留白充足，适合搭配白色頁面標題；比一般握手照更接近企業受眾。這是一般企業形象情境照，不標成 TIRI 辦公室。'),
]
for a in assets:
    a['theme'] = a['theme'].replace('企业', '企業')
    a['note'] = a['note'].replace('适合', '適合')
    a['source_url'] = 'https://stocksnap.io/photo/' + a['slug']
    a['license'] = 'CC0 1.0'
    a['license_url'] = 'https://creativecommons.org/publicdomain/zero/1.0/'
    a['verified_on'] = '2026-09-09'
    a['verification'] = '已查看作品頁 CC0 連結及下載預覽，已人工視覺檢視。'
    a['download_status'] = '960px 預覽已下載；原尺寸檔待正式選用時下載。'
    a['preview'] = f"candidates/{a['id']}-{a['key']}.jpg"
    source = ROOT / 'candidates' / a['file']
    target = ROOT / a['preview']
    if source.exists():
        source.rename(target)
    if not target.exists():
        raise FileNotFoundError(target)

(ROOT / '圖片來源紀錄.json').write_text(json.dumps(assets, ensure_ascii=False, indent=2))

e = html.escape
cards = []
for a in assets:
    cards.append(f'''<article class="card" data-theme="{e(a['theme'])}">
      <a class="photo" href="{e(a['preview'])}" target="_blank" aria-label="放大 {e(a['title'])}"><img src="{e(a['preview'])}" alt="{e(a['title'])}" width="960" height="640" loading="lazy"></a>
      <div class="card-body"><div class="eyebrow">{a['id']} · {e(a['theme'])} <span>{e(a['priority'])}</span></div>
      <h2>{e(a['title'])}</h2><p class="role">{e(a['role'])}</p><p>{e(a['note'])}</p>
      <div class="meta">{e(a['author'])} · 原圖 {e(a['resolution'])}<br>CC0 1.0 · 2026-09-09 核對</div>
      <div class="links"><a href="{e(a['source_url'])}" target="_blank" rel="noopener">作品與原圖下載 ↗</a><a href="{e(a['license_url'])}" target="_blank" rel="noopener">查看授權 ↗</a></div></div></article>''')

themes = list(dict.fromkeys(a['theme'] for a in assets))
options = ''.join(f'<option>{e(t)}</option>' for t in themes)
page = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TIRI v1 圖片候選預覽</title>
<style>
:root{{font-family:-apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC",sans-serif;color:#211c2b;background:#f7f5f1;line-height:1.65;color-scheme:light}}
*{{box-sizing:border-box}}body{{margin:0}}a{{color:#642286;text-underline-offset:4px}}:focus-visible{{outline:3px solid #7c3ead;outline-offset:4px}}
main{{max-width:1320px;margin:0 auto;padding:58px 28px 64px}}header{{max-width:850px;margin-bottom:36px}}.brand{{font-size:13px;font-weight:650;letter-spacing:.12em;color:#6c3986}}
h1{{font-size:clamp(28px,4vw,44px);line-height:1.25;font-weight:600;margin:14px 0 20px;letter-spacing:-.03em}}p{{margin:0 0 14px}}header p{{color:#57525d;font-size:17px}}
.nav{{display:flex;gap:24px;flex-wrap:wrap;font-size:14px;margin-top:22px}}.filterbar{{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:20px 0;border-top:1px solid #dcd6df;border-bottom:1px solid #dcd6df;margin-bottom:28px}}
label{{font-size:14px}}select{{font:inherit;color:inherit;min-height:44px;padding:8px 35px 8px 12px;border:1px solid #a79daf;background:white;margin-left:12px;border-radius:3px}}.count{{font-size:14px;color:#645c6b}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:26px}}.card{{min-width:0;background:white;border:1px solid #e5dfe8;border-radius:4px;overflow:hidden}}.card[hidden]{{display:none}}
.photo{{display:block;background:#eee9e4}}.photo img{{width:100%;height:auto;aspect-ratio:3/2;object-fit:contain;display:block}}.card-body{{padding:22px}}.eyebrow{{font-size:12px;color:#725086;display:flex;flex-wrap:wrap;gap:8px;justify-content:space-between}}.eyebrow span{{color:#6b6271}}
h2{{font-size:22px;font-weight:600;line-height:1.35;margin:12px 0 8px}}.role{{font-size:14px;font-weight:600;color:#655075}}.card-body>p:not(.role){{font-size:14px;color:#5d5663;min-height:92px}}.meta{{font-size:12px;color:#6e6873;margin-top:18px}}.links{{display:flex;gap:18px;flex-wrap:wrap;margin-top:16px;font-size:13px}}.links a{{min-height:32px;display:flex;align-items:center}}
.next{{margin-top:38px;padding:24px;border-left:3px solid #6c3986;background:#efeaf2;font-size:15px}}.next strong{{display:block;margin-bottom:8px}}.next p:last-child{{margin-bottom:0}}footer{{margin-top:30px;font-size:13px;color:#746d7a}}
@media(max-width:1050px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}@media(max-width:650px){{main{{padding:32px 18px}}.grid{{grid-template-columns:1fr}}.filterbar{{align-items:flex-start;flex-direction:column}}.card-body>p:not(.role){{min-height:0}}select{{max-width:230px}}}}
</style></head><body><main>
<header><div class="brand">TIRI / V1 REVISION / 2026.09.09</div><h1>把圖片對上頁面主題。</h1>
<p>第一輪 9 張 CC0 候選，附適用頁面、作者與授權來源。點圖片可放大，選圖時可以直接回覆編號。</p>
<p>目前是 960px 預覽；正式使用時再下載同一作品的原尺寸檔。這份是選圖整理，尚未套用到 v1。</p>
<div class="nav"><a href="修改清單.md">41 項修改清單</a><a href="圖片選用表.md">各頁配圖與待補素材</a><a href="source/2026-09-09-v1-meeting-notes.pdf">原始會議備忘錄</a></div></header>
<div class="filterbar"><label for="theme">依主題查看<select id="theme"><option value="">全部主題</option>{options}</select></label><div class="count" role="status" aria-live="polite">顯示 9 張候選</div></div>
<div class="grid">{''.join(cards)}</div>
<aside class="next"><strong>後續配圖方向已整理</strong><p>資訊安全主題與誠信經營的專屬照片還需補找；治理 Banner 等客戶提出方向。27 篇知識文章先檢查原圖、年刊封面與受訪者照片，再用主題情境圖補足。</p><p>TIRI Awards 獎座、潛力進展獎獎狀、TIRIC 人像與六本中英文年刊已有本機素材，使用本案檔案即可。</p></aside>
<footer>每張候選的作品頁均已核對 CC0 連結。<a href="https://stocksnap.io/license" target="_blank" rel="noopener">StockSnap 授權說明</a> · <a href="圖片來源紀錄.json">完整來源紀錄</a></footer>
</main><script>const select=document.querySelector('#theme');select.addEventListener('change',()=>{{let count=0;document.querySelectorAll('.card').forEach(card=>{{card.hidden=Boolean(select.value&&card.dataset.theme!==select.value);if(!card.hidden)count++;}});document.querySelector('.count').textContent=`顯示 ${{count}} 張候選`;}});</script></body></html>'''
(ROOT / '圖片候選預覽.html').write_text(page)

lines = ['# TIRI v1 圖片選用表', '', '整理日期：2026-09-09。第一輪以 **CC0 1.0** 為標準，尚未得到「其他免費商用授權也可」的答覆，因此本批未混入其他授權。', '', '看圖請開 [圖片候選預覽](圖片候選預覽.html)。所有作品頁均已核對 CC0 連結並下載 960px 預覽，9 張已做視覺檢視；完整原圖尚未下載，候選尚未套用到網站。', '', '## 授權怎麼記', '', 'StockSnap 的作品頁會個別標示 CC0，官方說明允許免費下載、修改及商業使用，無須署名。仍保留作者、作品頁、授權頁與核對日期，方便日後交付與追溯。[StockSnap 授權說明](https://stocksnap.io/license)、[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)。', '', 'Unsplash、Pexels 等免費圖庫有各自授權，不直接寫成 CC0。若後續擴大到其他免費商用圖庫，會逐張記錄實際授權名稱。[Unsplash 授權](https://unsplash.com/license)、[Pexels 授權](https://www.pexels.com/license/)。', '', '## 第一輪候選', '', '| 編號 | 適用位置 | 照片／作者 | 判斷 | 原圖尺寸 |', '|---|---|---|---|---|']
for a in assets:
    lines.append(f"| {a['id']} | {a['role']} | [{a['title']}]({a['source_url']})／{a['author']} | {a['priority']}；{a['note']} | {a['resolution']} |")
lines += ['', '## 按頁面安排圖片工作', '', '| 位置 | 需要什麼 | 數量／現況 | 來源與下一步 |', '|---|---|---|---|',
'| 全站 Banner／協會簡介 | 資本市場、上市櫃企业、IR 專業 | 依具體區塊配置，不先全站換圖 | A04、A09 可做方向候選；每張套入版面後才決定裁切。 |',
'| 五個委員會總覽／內頁 | 證照、獎項、專業、媒體、推廣 | 五組主題；卡片與內頁可共用 | 獎項用本案獎座圖；媒體可用 A08；其餘優先既有課程／交流照片。人像用真實委員照片。 |',
'| 鄧白氏雙標章 | ESG 感 Banner | 1 張需找 | A06 為第一輪候選；標章與證書仍用原素材。 |',
'| 活動訊息 | 各活動自己的 Banner | 依活動數量 | 從對應 Accupass 活動取本案活動圖；不用替活動逐張找泛用圖庫圖。 |',
'| 到府授課三個特色 | 內容多元、到府服務、時間彈性 | 3 個配圖位置 | 內容多元優先 TIRI 課程實拍；到府服務 A03／A07；時間彈性 A05。同頁避免重複人物。 |',
'| 董監事八大主題 | 八個正式課程分類 | 8 個配圖位置 | 併購／管理 A03；財稅 A02；ESG A06；媒體 A08。治理／誠信優先真實會議與文件情境，資訊安全專屬圖待補。 |',
'| 會計主管 | 有人操作計算機 | 1 張需找 | A01 動作吻合；A02 只作財務文章或不要求有人操作時的備選。 |',
'| 兩個治理服務 | 績效評估／治理提升 Banner | 2 張待客戶方向 | 流程圖可先設計；不把 A07 共享辦公照直接當成最終董事會視覺。 |',
'| TIRI Awards | 整排 TIRI 獎座 | 原圖已有 | 使用 `v1/images/awards/awards-trophy.jpg` 或客戶同名原圖。 |',
'| 潛力進展獎 | 桌上獎狀 | 原圖已有 | 使用客戶資料夾 `獎狀-進步獎.jpg`。 |',
'| 知識資源 | 每篇文章縮圖 | 27 個呈現位置 | 先查原文圖片、封面、人物照片；其餘用財務／治理／ESG／溝通等主題庫。同分類可適量共用，不把泛用圖當文章實拍。 |',
'| 加入會員 | 專業社群／企業連結 | 1 張需換 | A09 可作企業形象候選；若希望更有協會感，優先 TIRI 真實會員交流合照。 |',
'| 會員權利 | 協會服務、合作夥伴兩大區塊 | 2 個配圖位置 | 協會服務優先課程／會員交流實拍；合作夥伴可用企業協作情境 A03。 |',
'| 年刊 | 中英文分開的實際封面 | 2023–2025，中英各 3 本 | 從本案六本 PDF 首頁製作封面；不找替代圖庫照。 |',
'| 客戶會補的圖 | Logo、董監事 Banner、年刊 Banner | 待提供 | 記入交付缺件，不臆造 Logo、不抓其他企業圖片充當正式素材。 |',
'', '## 素材來源分類', '', '- **本案素材**：TIRI 活動、人物、Logo、獎座／獎狀、證書、年刊、客戶影片。保留本機原始路徑與用途，不把它們標成 CC0。', '- **CC0 情境照片**：本批 A01–A09，保留作品頁、作者、授權、核對日期與下載狀態。', '- **待補**：資訊安全、誠信經營等更精準主題圖，及客戶尚未提供的圖片。', '', '## 下載與套版要求', '', '- 目前預覽保留原構圖，方便選圖；正式 Banner 需另檢查桌機橫幅與手機直幅裁切。', '- 正式原圖從作品頁的免費下載取得，不使用旁邊 Shutterstock 贊助圖。', '- 下載後放到本機 v1 圖片資料夾，以壓縮圖片提供，不依賴圖庫外部熱連結。', '- 記錄原始檔與實際上線檔的對應；來源資料已整理為 [圖片來源紀錄.json](圖片來源紀錄.json)。', '']
(ROOT / '圖片選用表.md').write_text('\n'.join(lines).replace('上市櫃企业','上市櫃企業'))

# Copy the two user-supplied award originals into the review source folder for later implementation.
provided = ROOT.parent.parent.parent / 'ref/官網/新官網-資料/文件/5證照獎項/TIRI Awards獎項'
if provided.exists():
    for filename in ['TIRI Awards.jpg', '獎狀-進步獎.jpg']:
        shutil.copy2(provided / filename, ROOT / 'source' / filename)
print('Created 9-image preview, selection table, and provenance JSON.')
