"""Record the user's first review. Updates tracking only, never website files."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import shutil
from bs4 import BeautifulSoup

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCE = OUT / 'source'
latest_path = Path('/Users/jonathanyu/Downloads/TIRI-v1-驗收結果-2.json')
raw_path = SOURCE / latest_path.name
if not raw_path.exists():
    shutil.copyfile(latest_path, raw_path)
assert raw_path.read_bytes() == latest_path.read_bytes()
raw = json.loads(raw_path.read_text())
items = raw['items']
assert len(items) == len({item['id'] for item in items}) == 41

actions = {
 '02': 'Footer「會員登入」改成不可點擊的純文字；登入頁保留，登入功能延後製作。',
 '04': '從首頁線上課程「所有課程／查看更多」進入的課程列表，改成與首頁課程卡片一致的樣式。現有目的地是 trainbod.html#open；需核對圖片、日期、資訊層級及手機排列。',
 '05': '已找到合作夥伴 LOGO 資料夾的 15 個檔案。核對品牌、展示分類、名稱與官網，將 AI／PSD／PDF／PS 等來源轉成適合網頁的圖檔後套用首頁及合作夥伴頁，再整項驗收。',
 '06': '全站人物情境圖以東亞臉孔為主，逐頁減少重複使用，保持圖片與各頁主題相符。逐張核對可用授權、尺寸、來源與裁切；本案實拍及人物專訪仍須對應正確活動／本人。',
 '07': '協會簡介配圖依 06 換成以東亞人物為主、符合各段內容的照片，盡量避免同頁和其他主要頁面重複。',
 '08': '第一、二屆版型已獲文字確認。第三屆保留照片卡片，將公司名稱與職稱分開呈現；兼任者逐組配對公司／職稱。這是對留言的版面解讀，尚未完成第三屆新版驗收；7 位歷屆照片仍待補。',
 '10': '媒體委員會改用一人採訪另一人的情境，人物以東亞臉孔為主；同步總覽、媒體內頁及其他委員會交叉入口中的同一張圖。',
 '12': '鄧白氏 Banner 重新選圖，候選方向是綠植、孩童雙手／照顧幼苗的永續意象。留言尚未指定確切構圖，按此方向製作候選；新人物圖同樣遵守 06。',
 '14': '說明近期活動與活動訊息合併的入口差異，逐筆處理活動列表缺圖並核對目的頁。已查到 19 筆未配圖，其中 12 筆是無目的頁的 article，卻顯示「活動花絮 →」，需一併修正。',
 '18': '到府授課三特色圖片依 06 調整，以東亞人物為主，符合內容多元／到府服務／時間彈性，重新檢查裁切與重複使用。',
 '19': '八大課程主題保留正確課綱與分類，配圖依 06 調整；人物以東亞臉孔為主，逐類貼合內容並減少重複。',
 '22': '四步驟流程改成直接製作的正式圖片，增加視覺設計感。以原需求「企業自評 → 協會書審 → 實地訪談 → 擬撰報告」核對文字；不沿用 HTML／CSS 步驟卡作為交付圖。',
 '24': '六步驟流程改成直接製作的正式圖片，與 22 統一設計。保留提出申請、提交文件、現況評估、公司訪談、提出改善策略及規劃、後續諮詢六步及正確順序。',
 '27': '重排 IRC 贊助獎學金；點「證照」略過中間總覽頁，下拉只留「國際證照」「專業實戰班」。按現有內容及新版 Excel，建議主入口直接進 IRC certification.html，實戰班進 tiric.html，中英文與手機入口同步。',
 '29': '白底影片本身已確認通過；補上播放前顯示的封面圖。已確認目前 video 沒有 poster；可從這支影片選清楚、有標題的畫格作封面，檢查尚未播放時及手機載入畫面。',
 '32': '重排潛力進展獎企業名單，對齊代碼、公司名称及行距，處理長名稱換行。保留 2025 得獎／2026 入選差異與屆次切換；缺少的正式資料另追蹤 32-B。',
 '37': '加入會員 Banner 改為簽署合約／合作協議情境；若畫面有人物，以東亞臉孔為主，檢查橫幅與手機裁切。',
 '39': '兩個會員權利區塊的標題放到圖片上方；人物圖片依 06 更新。重排左右欄以改善高度落差，合作夥伴優惠整理成清楚分組，保留完整條件與連結。',
}
dependencies = {
 '11': '本項內頁與名冊已通過；10 更換媒體委員會圖時，相關內頁配圖仍需檢查。',
 '13': '列表版型與 Accupass 直連已通過；缺圖和無目的頁的歷史列集中追蹤 14。',
 '26': '證照／獎項分類拆分已通過；27 的證照主入口及下拉項目另調整。',
 '35': '本項文章配圖交付已通過；06 是全站新要求，若此區人物圖或重複圖被更換，新圖片需再驗收，不改寫本輪通過紀錄。',
}

def status(item):
    if item.get('note', '').strip():
        return 'followup'
    if item.get('confirmed') is True:
        return 'accepted'
    if item['deliveredStatus'] == 'waiting':
        return 'waiting'
    return 'unreviewed'

groups = {key: [i['id'] for i in items if status(i) == key]
          for key in ['accepted', 'followup', 'unreviewed', 'waiting']}
assert [len(v) for v in groups.values()] == [18, 18, 0, 5]
assert set(actions) == set(groups['followup'])

# Current HTML evidence: distinguish missing image elements from broken image URLs.
page = ROOT / 'v1/html/news.html'
soup = BeautifulSoup(page.read_text(), 'html.parser')
rows = soup.select('.event-banner-row')
missing = []
for row in rows:
    if row.find('img'):
        continue
    missing.append({'date': row.find('time').get('datetime'),
                    'title': row.find('h3').get_text(' ', strip=True),
                    'element': row.name, 'href': row.get('href', ''),
                    'display_text': row.get_text(' ', strip=True)})
assert len(rows) == 153 and len(missing) == 19
assert sum(not row['href'] for row in missing) == 12
evidence = {'page': str(page), 'sha256': hashlib.sha256(page.read_bytes()).hexdigest(),
            'rows': len(rows), 'rows_without_image': missing,
            'note': '未配圖是沒有 img 元素；本次未以瀏覽器重新檢查所有圖片載入。12 筆無目的頁均為 article，含空 href 屬性與指向花絮的箭頭文案。'}
(SOURCE / 'activity-review.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2))

receipt = {'source_version': raw['version'], 'exportedAt': raw['exportedAt'],
           'source_sha256': hashlib.sha256(raw_path.read_bytes()).hexdigest(),
           'source_file': raw_path.name, 'raw_confirmed_count': 19,
           'partially_accepted': {'08': '第一、二屆版型已確認', '29': '影片已確認；封面待補'},
           'groups': groups, 'website_edits_in_this_review': False,
           'items': [{**i, 'reviewStatus': status(i), 'nextAction': actions.get(i['id']),
                      'dependencies': dependencies.get(i['id'])} for i in items]}
(OUT / '第一輪驗收整理.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2))

report = ['# TIRI v1 第一輪驗收整理', '',
 '2026-09-10。已併入 10:30 的第二份匯出。18 項整項確認通過、18 項有後續意見、0 項未確認、5 項等資料。JSON 有 19 項勾選，其中 29 的影片通過，但仍需補播放前封面，列入後續處理。此輪完成回饋整理與 checklist 更新；第二輪網站修改尚未實作。', '',
 '## 第一輪結果', '',
 '| 狀態 | 項數 | 編號 |', '|---|---:|---|']
for key, label in [('accepted', '你已確認'), ('followup', '需調整／補充說明'), ('unreviewed', '未勾選、未留言'), ('waiting', '仍等資料')]:
    report.append(f"| {label} | {len(groups[key])} | {'、'.join(groups[key])} |")
report += ['', '08 的第一、二屆已由留言確認通過，第三屆文字仍需調整。29 的影片已确认、播放前封面待補；30 已整項確認通過。兩份匯出逐項比對，只有 29／30 更新，其他 39 項相同。', '',
 '## 第二輪修改清單', '', '以下是對驗收意見的整理；屬於下一輪工作，不表示已改好。']
for item in items:
    if item['id'] in actions:
        report += ['', f"- [ ] **{item['id']}｜{item['title']}**：{actions[item['id']]}"]
report += ['', '## 08：第三屆公司與職稱怎麼分開', '',
 '我的理解是保留現有照片卡片，只把目前混在一長串文字的任職資訊拆開。例如郭宗霖的資料可以排成：', '',
 '**郭宗霖｜理事長**', '',
 '| 公司 | 職稱 |', '|---|---|', '| 鴻勝會計師事務所 | 執業會計師 |', '| 大井泵浦工業股份有限公司 | 董事 |', '',
 '這裡的表格是欄位示意，網頁可放在照片下方分成兩組文字。協會職務與公司職稱也要分清楚。第一、二屆維持你已確認的表格。7 位尚缺的歷屆照片仍是另一項補件。', '',
 '## 14：近期活動整合是什麼', '',
 '原本近期活動（events.html）與活動訊息（news.html）是兩個入口。9/09 把列表統整到活動訊息 news.html，舊近期活動入口會轉到同一頁，讓使用者在一個地方依年份查看活動，再連到 Accupass 或原活動文章。活動花絮的新排版仍是 17，另等參考資料。', '',
 '你指出缺圖是對的。這次檢查目前 153 筆列表，有 19 筆尚未配圖：4 筆沒有取得原 Accupass Banner、3 筆已有內部目的頁但沒配圖、12 筆歷史消息既沒配圖也沒有目的頁。後者目前是不可點的 article，卻有「活動花絮 →」，會讓人誤以為能點。應逐筆找回原素材／原文章，查不到時用清楚的純文字紀錄版型；不捏造活動照片或連結。', '',
 '9/09 的「0 缺檔」靜態檢查只檢查已填入的檔案路徑，沒有涵蓋這些未配圖、沒有目的頁的列。下一輪需補上這兩種情況的檢查。', '',
 '| 日期 | 未配圖活動 | 目的頁狀況 |', '|---|---|---|']
for row in missing:
    destination = row['href'] or '無目的頁；需處理箭頭文案'
    report.append(f"| {row['date']} | {row['title']} | {destination} |")
report += ['', '## 39：左右高度落差怎麼處理', '',
 '目前兩區右欄約有 268 字與 897 字，固定大小的左圖很難自然對齊長清單。建議把標題移到圖片上方，重新安排圖文比例；較長的合作夥伴優惠用分組卡片或雙欄清單，減少單欄往下堆疊。以整個區塊的視覺平衡調整，圖片保持合理比例，優惠条件與連結保留。', '',
 '## 新素材與 Excel 差異', '',
 'Logo 位於 ref/官網/新官網-資料/文件/1首頁/合作夥伴LOGO，共 15 個檔案，含 PNG、AI、PSD、PDF、PS。已改記為「收到素材／待核對套用」。同一品牌有不同版本，且資料夾名單與現有 10 家合作夥伴不完全相同，須先核對展示用途及品牌對應，不能直接把每個檔案當一家合作夥伴。', '',
 '與 9/09 的 15 份工作簿快照比較，5 份檔案雜湊有變更；逐分頁、儲存格、連結與嵌入圖片核對後：', '',
 '- 天＋地的內容：分頁從「工作表1」改為「工作表」，下方新增一份導覽／Footer 排列；新排列頂層沒有會員登入，其他舊名稱仍在。實作仍以你已確認的會員服務／會員權利及本輪證照入口意見為準。',
 '- 首頁內容：分頁改名「中文」，D2 的 6300+場 改成 6300+人，與已通過 03 一致。',
 '- 簡介：上述內容層面未查到差異；不能只因檔案雜湊不同就當成新增文案。',
 '- 消息活動：「工作表1」A10 新增 Accupass 主辦頁連結；目前活動頁已有同一個主辦頁入口。',
 '- 證照獎項：「證照」A2、A7 分別新增 IRC、TIRIC 超連結，與 27 的兩個項目方向一致。', '',
 '來源 Excel 全部保持原檔；差異與 Logo 檔案清單保存在本次 source 目錄。', '',
 '## 已通過項目的相依調整', '']
for key, description in dependencies.items():
    report.append(f'- **{key}**：{description}')
report += ['', '## 紀錄', '',
 '- [主 checklist](../../V1修改Checklist.md)',
 '- [原始驗收匯出（未改動）](source/TIRI-v1-驗收結果.json)',
 '- [29／30 更新後的匯出（目前依據）](source/TIRI-v1-驗收結果-2.json)',
 '- [結構化驗收整理](第一輪驗收整理.json)',
 '- [第一輪驗收頁](../2026-09-09-v1-revision/驗收入口.html) 保留原樣；本次没有清除或寫入瀏覽器內的勾選。', '']
(OUT / '第一輪驗收整理.md').write_text('\n'.join(report).replace('反馈', '回饋').replace('名称', '名稱').replace('条件', '條件').replace('没有', '沒有').replace('确认', '確認'))

# Patch the canonical checklist from a preserved snapshot. Idempotent for this receipt.
text = (SOURCE / 'checklist-before-round1.md').read_text()
old_intro = text.split('\n\n')[1]
text = text.replace(old_intro, '更新：2026-09-10｜已併入 29／30 的更新。**18 項整項已確認、18 項需調整／補充說明、0 項未確認、5 項等資料**。JSON 有 19 項勾選，其中 29 影片已通過，仍須補封面，列入後續處理。主項勾選代表實作完成，驗收結果另列；第二輪修改尚未實作。', 1)
review_intro = '''## 第一輪驗收結果

[完整意見、08／14／39 說明與新素材盤點](outputs/2026-09-10-v1-review-round1/第一輪驗收整理.md)

- **整項已確認 18 項**：01、03、09、11、13、15、16、21、26、28、30、31、33、34、35、36、38、40。
- **有後續意見 18 項**：02、04、05、06、07、08、10、12、14、18、19、22、24、27、29、32、37、39。08 第一、二屆已確認；29 影片已確認，封面待補。
- **未確認 0 項**：29／30 已於第二份匯出補充，其他 39 項結果與第一份一致。
- **等資料 5 項**：17、20、23、25、41。08 的 7 位照片、32 的正式缺件另追蹤。
- **全站配圖要求**：人物以東亞臉孔為主、盡量減少重複，保留來源／授權紀錄。已通過項目若因此換圖，新圖片仍需再確認。
- **05 Logo 已收到素材**：共 15 個檔案，待品牌對應、轉檔、套用後重新驗收。

## 9/09 交付內容與第一輪確認

下表「改了什麼／自測」記錄 9/09 交付；最後一欄已同步 9/10 的驗收結果。需再調整的新版尚未交付。
'''
text = text.replace('## 現在可以檢查的改動', review_intro.rstrip(), 1)
text = text.replace('若明天伺服器未啟動', '若伺服器未啟動')

labels = {'accepted': '你已確認', 'followup': '需再調整／補充說明', 'unreviewed': '待你確認（本輪無勾選／留言）', 'waiting': '待資料'}
item_map = {i['id']: i for i in items}
def table_row(match):
    line, key = match.group(0), match.group(1)
    label = labels[status(item_map[key])]
    if key == '08':
        label = '第一、二屆已確認；第三屆需調整'
    if key == '29':
        label = '影片已確認；播放前封面待補'
    return re.sub(r'待你確認(?= \|$)', label, line)
text = re.sub(r'^\| (\d{2})[^\n]*$', table_row, text, flags=re.M)
text = text.replace('05-B 正式 Logo 待補。', '9/10 已收到 15 個 Logo 檔案，待核對套用。')
text = text.replace('## 本輪共通檢查', '## 9/09 交付自測紀錄')
text = text.replace('本輪結果：', '9/09 交付：')

def task_block(match):
    block, key = match.group(0), match.group(1)
    lines = block.splitlines()
    old_head = lines[0]
    degree = old_head.split(' — ')[1].split('｜')[0]
    current = labels[status(item_map[key])]
    if key == '08':
        current = '第一、二屆已確認；第三屆需調整／照片待補'
    if key == '29':
        current = '影片已確認；播放前封面待補'
    check = ' ' if status(item_map[key]) in ['followup', 'waiting'] else 'x'
    lines[0] = re.sub(r'^- \[[ x]\]', f'- [{check}]', old_head.split(' — ')[0]) + f' — {degree}｜{current}'
    if key in actions:
        lines.insert(1, f'  - **9/10 驗收後續（優先於下方原需求）**：{actions[key]}')
    if key in dependencies:
        lines.insert(1, f'  - **9/10 相依事項**：{dependencies[key]}')
    if key == '30':
        lines.insert(1, '  - 9/10 補充驗收：已於第二份匯出勾選通過。')
    return '\n'.join(lines) + '\n'
text = re.sub(r'^- \[[ x]\] \*\*(\d{2})｜.*?(?=^- \[[ x]\] \*\*\d{2}｜|^## |\Z)', task_block, text, flags=re.S | re.M)
reopen = ['05-A', '06-A', '06-B', '06-C', '06-D', '18-A', '18-B', '18-C', '18-D',
          *['19-' + c for c in 'BCDEFGHIJ'], '39-A', '39-B', '39-C']
for sub in reopen:
    text = text.replace(f'- [x] {sub} ', f'- [ ] {sub} ')
text = text.replace('05-B 等客戶：收到正式 Logo 後補入並檢查尺寸與清晰度。', '05-B 已收到素材：核對版本並轉檔、補入正式 Logo，檢查透明背景、尺寸與清晰度。')
text = text.replace('  - 範圍：第三屆未明確要求全部改表格，先保留其展示方式。', '  - [ ] 08-E 第三屆保留照片卡片，將公司／職稱逐組分開，中英文對應並檢查長名稱與手機版。')
text = text.replace('  - [x] 29-C 檢查播放、音訊、載入及手機顯示。', '  - [x] 29-C 檢查播放、音訊、載入及手機顯示。\n  - [ ] 29-D 補上影片播放前封面，檢查尚未播放時及手機載入顯示。')
text = text.replace('  - 檢查：[潛力進展獎](v1/html/mission-206783-766399.html) 切換到各自正確名單；', '  - [ ] 32-C 整理公司代碼、名稱與長文字換行，桌機／手機名單對齊。\n  - 檢查：[潛力進展獎](v1/html/mission-206783-766399.html) 切換到各自正確名單；')
text = text.replace('- [ ] 合作夥伴正式 Logo → 05-B。', '- [x] 合作夥伴 Logo 素材已找到 15 個檔案 → 05；品牌對應及完整性待核對，轉檔／套用仍未完成。')
text = text.replace('05 合作夥伴 Logo、08 歷屆照片、32 正式／缺少獎項資料；可交付部分已完成。', '05 Logo 已到待核對套用；08 第一、二屆已確認、第三屆需調整與照片待補；32 名單排版需調整、正式缺件另追蹤。')
text = text.replace('- [x] 本輪可驗收部分已列於頂端；「你已確認」全部留待你操作。', '- [x] 9/10 兩份第一輪 JSON 已合併：18 項整項通過，29 影片通過但封面待補，原始勾選與留言完整保留。\n- [ ] 第二輪補查活動列表的未配圖、無目的頁及誤導箭頭；9/09 的 0 缺檔不涵蓋這些情況。')
text = text.replace('  - 現況：原檔已找到；先前只比對過 2 秒畫面，尚不能當作整段影片已核對完成。', '  - 前期曾僅比對 2 秒；9/09 交付已補全片影格比對，見上方自測。')
text = text.replace('沒有代替確認。', '沒有代替確認。')
text += '\n| 2026-09-10 | 匯入兩份第一輪驗收：18 項整項確認、18 項後續處理、5 項等資料。29 影片通過但封面待補，30 已通過。找到 15 個 Logo 檔案並比對新版 Excel；補記 19 筆活動未配圖、12 筆無目的頁。 | 更新追蹤文件與補件狀態；第二輪網站修改尚未實作，未部署。 |\n'
text = text.replace('名称', '名稱').replace('没有', '沒有').replace('验收', '驗收')
assert len(re.findall(r'^- \[[ x]\] \*\*\d{2}｜', text, re.M)) == 41
assert len(re.findall(r'^- \[x\] \*\*\d{2}｜', text, re.M)) == 18
(ROOT / 'V1修改Checklist.md').write_text(text)
print(json.dumps({'counts': {k: len(v) for k, v in groups.items()}, 'checklist_items': 41,
                  'no_image': len(missing), 'no_destination': 12, 'website_files_changed': 0}, ensure_ascii=False))
