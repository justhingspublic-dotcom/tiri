# TIRI V1 簡易雙語 CMS — 階段 0 前置盤點報告

> 依 `Files/CMS規劃.md` 第 11 節「階段 0」與第 15 節「實作前必須回報的內容」產出。
> 盤點日期：2026-08-10｜基準：`main` @ `e8e351f`（語言切換已移入 navbar header-top；工作區乾淨，僅未追蹤的規劃/盤點文件）
> 狀態：**僅盤點，未修改任何程式碼。** 等待確認後才進入階段 1。

---

## 0. 結論摘要：規劃文件與現況的五個關鍵落差

實作前必須先知道的事實，依影響程度排序：

1. **V1 頁面產生器已經過時，今天重跑會「回退」現站，而不是重建現站。**
   `_archive/scripts/v1build/` 四支腳本仍在，但 v1/html 已手工演進超前：navbar 從烘焙 HTML 改為 runtime web component、join/contact 接上 forms.js 真實後端、contact.html 整頁手工重排、頁尾版權改為 Justhings、以及近期多次顏色與內容修改。重跑產生器會全數回退（詳見 §2.3）。
   → 規劃文件 8.2「需同時修改產生器的來源模板」的前提不成立。**建議本期正式凍結產生器**（README 註記不可重跑），把 `v1/html/*.html` 視為事實源。此為裁決點 A。

2. **頁尾目前沒有聯絡資料。** 規劃文件 4.1 的「全站共用資料：頁尾聯絡資料與社群連結」與現況不符：134 頁的頁尾只有品牌區、4 欄站內連結、語言切換與版權行；電話/地址/Email 在 contact.html、index.html 尾段與 navbar.js 的選單描述字串內；社群連結 5 個全部只在 navbar.js（頁尾沒有）。

3. **導覽列（含社群連結、搜尋文案）是 runtime JS 注入，不是 HTML。**
   每頁只有 `<tiri-navbar variant="v1">` 空殼，內容全部由 `v1/js/navbar.js` 以 `innerHTML` 渲染。**2026-08-10（`e8e351f`）語言切換已從頁尾移入 navbar header-top（社群 icon 右側），134 頁的頁尾版切換器已移除；`v1/js/navbar.js` 自此與 `shared/navbar.js` 刻意分岔——V1 導覽唯一源頭＝`v1/js/navbar.js`，shared 那份只服務 V2，不再同步。** → 導覽文字/社群連結/語言切換若要 CMS 化，無法用 DOM 替換，需改用「伺服器注入 JSON ＋ navbar.js 讀取並 fallback 內建值」（§6.2）。

4. **英文現況遠比預期少。** 9 個核心頁面中只有首頁有「可達」的英文對應（`en.html`，舊版 Weebly 內容）；join/contact 有英文舊頁但被孤立且 `lang` 標錯；about/events/knowledge/news/membership/partners 六頁沒有英文頁，其中 **partners 連原站英文素材都不存在**。navbar 與 footer 完全中文、無 i18n 機制。詳見 §3。

5. **forms.js 以表單 label 文字作為後端欄位 key。**
   `collectRedesign()` 直接拿 `.field > label` 的可見中文當 payload 的 `label`，後台收件匣與 CSV 依此顯示。**任何表單內部文字（label、submit 按鈕）都不得列入 CMS 可編輯欄位**，否則等同改資料 schema。manifest 已將表單內部全數列為禁區（§4.9、§4.10）。

其他值得注意：前台已被 `after_request` 全域加上 `Cache-Control: no-store`（伺服器端套入不會有快取過期問題）；後台目前完全沒有檔案上傳功能（CMS 上傳為全新功能）；`tinymce-helper.js` 等 JustGolf kit 資產存在但未被引用，本期依規劃不使用富文字編輯器。

---

## 1. 現有架構

### 1.1 前台

- `v1/`：**134 頁**靜態 HTML（`v1/html/`）＋ `css/`、`js/`、`images/`、`fonts/`、`documents/`，資料夾完全自足，可整包部署。
- 組成：9 頁重新設計核心頁（build_pages.py 產出後手工演進）＋ contact.html（convert 後整頁手工重排）＋ 36 頁重排歷史頁 ＋ 約 80 頁原站套殼頁 ＋ 7 頁英文舊頁 ＋ board/team 系列。
- `v1/index.html` 是 splash 進場頁（logo 動畫 1.24 秒後 `location.replace("html/index.html")`，noindex），不是內容頁。
- 共用 JS：`navbar.js`（導覽 web component）、`main.js`（動效/抽屜/語言選單開合，無內容注入）、`forms.js?v=20260805-testapi`（僅 join/contact 載入）。
- 表單：`forms.js` 依 hostname 決定 API：localhost→`http://localhost:8000`、含 `-test.`→`https://tiribackend-test.justhings.com.tw`、其餘→`https://tiribackend.justhings.com.tw`。slug 取自檔名（改檔名＝斷表單）。

### 1.2 後台（server/app.py，887 行單檔）

- 路由：`POST /api/submit/<slug>`（唯一公開收件端點，honeypot＋空值檢查）；`/admin` 儀表板、`/admin/inbox`、`/admin/trash`、`/admin/settings`、`/admin/account`、`/admin/export.csv`（皆 `require_auth`）；刪除/還原/測試信 JSON API；`/admin/login|logout`；`/healthz`。
- 樣板：`base.html`（側欄＋toast＋dialog＋SPA 殼層）；側欄項目定義於 `app.py` `nav_items()`（Python 端唯一來源），每個 view 手動傳入。現成 UI 元件：`window.bToast()`、`window.BDialog.confirm/alert/prompt`（`static/js/cms/dialogs.js`）——CMS 後台頁沿用即可，不另建 UI kit。
- 認證：Flask signed-cookie session（`session["admin"]`），`require_auth` 未登入 302 至登入頁。無 CSRF token（既有狀況，CMS 寫入端點沿用現有慣例並以 POST＋登入為底線）。

### 1.3 資料庫

- 驅動 `pymssql`；`init_db()` 於 import 時執行，以 `IF OBJECT_ID(...) IS NULL CREATE TABLE` 冪等建 4 張表：`submissions`、`mail_settings`、`mail_copy`、`users`（時間欄一律 NVARCHAR(19) 台北時間字串）。
- 開發/正式以 `.env` `DB_NAME` 分離：開發 `TIRI_dev`（公司測試機 192.168.1.92）、正式 `TIRI`（AWS RDS 東京，正式站 .env 的 DB_* 換成 PROD 那組）。`migrate_to_prod.py` 為一次性搬遷（只補空，不覆蓋）。
- CMS 新表 `cms_pages` 依規劃文件 §7 加入 `init_db()` 同一套冪等模式即可，不影響既有四張表。

### 1.4 Host 分流（CMS 套用的關鍵位置）

- `app.py:851` `@app.before_request frontend_by_host()`：`FRONTEND_DIR` 有值且 `request.host` ∈ `FRONTEND_HOSTS` 時，**所有請求**（含 /admin、/api）一律以 `send_from_directory(FRONTEND_DIR, path)` 回靜態檔（目錄自動補 index.html，Werkzeug `safe_join` 擋 path traversal，任何例外回純文字 404）。
- 意義：前台網域下後台/API 完全遮蔽（安全邊界）；表單本來就是打後端網域，所以 CMS 在此函式內做「白名單頁面的內容套用」不會碰到表單路徑。
- `after_request add_cors` 對所有回應（含前台靜態檔）加 `Cache-Control: no-store` → 前台本來就不快取。
- 本機 `.env` 未定義 `FRONTEND_DIR/FRONTEND_HOSTS`（分流關閉）；正式站（tiri.justhings.com.tw）由 nginx 反代進同一 Flask 開啟分流。

---

## 2. 核心頁面來源檔與產生器對應

### 2.1 對應表

| CMS 頁面 | 中文基準頁（事實源） | 產生器狀態 | 附註 |
|---|---|---|---|
| 全站共用 | 頁尾：各頁內嵌 HTML（134 份複本）；導覽/社群/語言切換：`v1/js/navbar.js`（已與 shared 分岔，V1 獨立維護） | 頁尾原由 build/convert 烘焙；導覽已脫離 `nav_def.py` | 頁尾無單一來源；shared/navbar.js 僅供 V2 |
| 首頁 | `v1/html/index.html` | **從不在產生器內**（convert SKIP；僅 relink.py 曾補鏈） | 規劃文件所述特例屬實 |
| 關於 | `v1/html/about.html` | build_pages.py 產出後手工演進 | |
| 活動課程 | `v1/html/events.html` | 同上 | |
| 知識資源 | `v1/html/knowledge.html` | 同上 | |
| 最新消息 | `v1/html/news.html` | 同上 | |
| 會員服務 | `v1/html/membership.html` | 同上 | |
| 合作夥伴 | `v1/html/partners.html` | 同上 | |
| 加入會員 | `v1/html/join.html` | build 產出後手工加 forms.js | 表單區＝禁區 |
| 聯絡我們 | `v1/html/contact.html` | **不在 build_pages.py**；convert 產出後整頁手工重排 | 表單區＝禁區 |

### 2.2 產生器現況

- 腳本：`nav_def.py`（導覽資料，已與 navbar.js 分歧）→ `build_pages.py`（9 頁＋外殼）→ `convert_pages.py`（123 頁原站轉換）→ `relink.py`（補鏈）→ `board_pages.py`（board/team 8 頁＋全站 string-patch）。README 標示的執行順序固定。
- 模板全部是腳本內 f-string，無獨立模板檔。輸出路徑硬編碼指向 `v1/`。
- `npm run check` = `_archive/scripts/check_static_site.py`：全 repo 連結/資產完整性檢查（缺檔＋tiri.tw 外漏），不驗證 HTML 或產生器一致性。

### 2.3 重跑產生器會失去（凍結理由）

navbar web component（回退為烘焙 header＋重新出現已停用的會員登入連結、文字 wordmark）、`forms.js` 與 favicon 版本參數、contact.html 手工版面（回退為 Weebly legacy 內容，另約 36 頁重排頁同理）、頁尾 Justhings 版權（回退為統編＋«V1 DESIGN PROPOSAL»）、近期顏色/內容 commit（`ad88242`、`5676c0b` 等）、以及未來加入的一切 `data-cms` 標記。

**裁決點 A（建議）**：本期宣告凍結 `_archive/scripts/v1build/`（於該 README 頂部註記「已凍結：重跑會回退 2026-08 之後的手工修改」），CMS 標記只加在 `v1/html` 事實源；不花工同步產生器模板。若你希望維持產生器可重跑，需另外同步 build/convert 兩份外殼模板＋nav_def.py，工時另計。

---

## 3. 中英文頁面與 URL 對應

### 3.1 現有英文資產（v1/html/，扁平結構，無 /en/ 目錄）

- 正確標示 `lang="en"` 且可達：`en.html`（英文首頁）→ `board_en.html` → `team_en-2018/2022/2026.html`（4 頁島）；`services_en.html` 僅 `mission_en.html` 連入；`mission_en.html` **零入鏈（孤島）**。
- 另有 **35 頁**原站遺留英文內容頁被標成 `lang="zh-Hant"`（V1 轉換時的退化；原站是正確的 `lang="en"`），全部互為孤島、無任何核心頁連入。原站英文雙生頁規則：`X.html` ↔ `X-<6碼數字>.html`（如 `contact.html` ↔ `contact-197913.html`）。
- 語言切換器：**現已移入 navbar header-top（`v1/js/navbar.js` `renderLangSwitch()`，`e8e351f`），頁尾版已自 134 頁移除**——但連結仍硬編碼「中文→`index.html`／English→`en.html`」，永遠跳首頁（違反規劃 5.8），且英文頁上仍顯示「中文」為當前語言。好處：切換器已收斂為單一 JS 函式，階段 2 的「切到當前頁對應語言」只需改一處（依 zh↔en 對應表 rewrite 兩個 href），不必動 134 頁 HTML。

### 3.2 九個核心頁對應表與缺件清單（不自行翻譯，缺件待 TIRI 提供）

| 中文頁 | 英文對應 | 現況 | 需 TIRI 提供 |
|---|---|---|---|
| index.html | `en.html` | 存在、可達，但為舊版 Weebly 內容（非 V1 版型） | V1 首頁全部區塊英文文案（若要與中文同版型） |
| about.html | — | 缺頁。素材散在 `mission_en.html`、`services_en.html`、`committee-817915.html`、`team_en-2026.html`；鄧白氏段無英文 | 整頁英文定稿（含鄧白氏段） |
| events.html | — | 缺頁。素材：`tiric-677070`、`trainbod-329824`、`certification-388672`、`scholarshipirc-952540`、8×`seminar181023-*` 英文版等 | 整頁英文定稿（含 15 個課程主題 chips、費用/退費條款） |
| knowledge.html | — | 缺頁。素材：`irupdatestc-146678` 等 | 整頁英文定稿（27 張卡標題是否翻譯待決） |
| news.html | — | 缺頁。僅 3 則英文舊聞散頁 | 18 則消息標題英文（或決定英文版消息範圍） |
| membership.html | — | 缺頁。素材：`membership-567311`、`benefit-499886` 等 | 整頁英文定稿（6 類別、3 費率卡、13 優惠列） |
| partners.html | — | **缺頁且原站無任何英文素材** | 整頁英文全新供稿 |
| join.html | `join-342161.html` | 英文舊頁存在但孤島、lang 標錯；表單本體不翻（label＝欄位 key） | 頁面文案英文定稿；表單處理方式裁決（見裁決點 B） |
| contact.html | `contact-197913.html` | 同上 | 頁面文案英文定稿 |
| 導覽/頁尾 | — | 全中文、無 i18n | 6 主項＋選單連結＋頁尾 4 欄＋版權英文 |

**裁決點 B（英文版範圍）**：英文內容到位前，建議語言切換維持現狀（切到既有 `en.html`），不預先建立空英文頁；英文頁 URL 命名建議沿 V1 既有慣例 `<name>_en.html`（about_en.html…），保留既有公開 URL（en.html、board_en.html、team_en-*）不重導。表單在英文頁的行為（共用中文表單頁或英文表單頁另計）需與 TIRI 確認——因 label＝欄位 key，英文表單會改變收件資料欄名，牽動收件匣顯示。

---

## 4. CMS Field Manifest（頁面 → 區塊 → 欄位）

- key 規則：`<section>.<field>`，固定清單用 `<section>.items[n].<field>`（n 從 1 起）。頁面即 `page_slug`（global/home/about/events/knowledge/news/membership/partners/join/contact）。
- 類型：`text`（單行）/`textarea`（多行，輸出 escape＋保留換行）/`richtext-limited`（僅允許保留既有 `<br>`/`<strong>`/`<em>`/內嵌 `<a class="u-link">`，以模板重組、非自由 HTML）/`date`/`image`/`file`/`url`/`video`/`toggle`。
- DOM 錨點：列現有 selector；實作時於節點加 `data-cms="<page>:<key>"`（hero 背景圖為 CSS 變數，另用 `data-cms-style="--hero-img"`）。
- 所有清單為**固定長度**（不提供增刪與排序）；`toggle` 僅用於 manifest 明列項目。
- 字數上限依現值長度放寬 20–30% 取整，後台顯示說明。

### 4.0 global（全站共用）— 約 34 欄

| 區塊 | key | 類型/限制 | 對應位置 |
|---|---|---|---|
| 聯絡資料 | `contact.tel`（14）/ `contact.tel_href` 自動生成 / `contact.email`（40）/ `contact.address`（40）/ `contact.access`（richtext-limited 50） | text/url | contact.html `dl` L52-55、index.html closing L503-520、navbar.js 選單描述（JSON 注入） |
| 社群連結 | `social.facebook / linkedin / line / youtube / email` ×5 | url（https/mailto） | navbar.js `renderSocialIcons()`（JSON 注入） |
| 頁尾品牌 | `footer.org_name`（richtext-limited，含 `<br>`，60） | — | 各頁 `footer .footer-brand p` |
| 頁尾連結 | `footer.col[1..4].heading`（8）＋ `footer.col[n].links[m].label/href`（17 條，label 14） | text＋url(站內) | 各頁 `footer .footer-col`；註：index 與 about 已有 2 條漂移，需先統一基準 |
| 版權 | `footer.copyright`（90，年份含在內） | text | 各頁 `.footer-bottom > span` |
| 語言切換 | `lang.zh_href`/`lang.en_href` **本期由對應表程式決定，不開放編輯** | — | navbar header-top（`navbar.js renderLangSwitch()`，非 HTML） |

> 導覽 mega menu 文字（6 主項、34 連結 title/desc、6 圖卡）為第二優先選項：技術上走同一 JSON 注入即可支援，但欄位多、變動低，建議本期後台先不開放，僅在 schema 預留 `nav.*` 命名空間。**global 欄位僅套用於本期 10 頁；其餘 124 頁的頁尾維持靜態現狀**（不一致範圍與緩解見 §8 風險 5）。

### 4.1 home（v1/html/index.html）— 約 230 欄

| 區塊（DOM 錨點） | 欄位 | 數量 |
|---|---|---|
| meta（head） | `meta.title`（70）/`meta.description`（textarea 120） | 2 |
| 主視覺 `section.hero.hero-photo` L41-57 | `hero.image`（CSS 變數）/`hero.eyebrow`（55）/`hero.h1_line1`（16）/`hero.h1_line2`（richtext-limited 含 `<em>`，16）/`hero.summary`（textarea 120）/`hero.cta1_label`（12）+`hero.cta1_url`/`hero.cta2_label`+`hero.cta2_url` | 9 |
| 形象圖帶 `section.hero-figure-band` L60-72 | `figure.image`+`figure.alt`（60）/`figure.caption1`（30）/`figure.caption2`（26） | 4 |
| 數據 `section.stats` L75-96 | `stats.items[1..4].number`（6，`data-count` 為源）/`.suffix`（3）/`.label_zh`（12）/`.label_en`（24） | 16 |
| 服務 `section.services#services` L99-122 | `services.eyebrow`/`services.h2`/`services.items[1..12].label`（12；編號 01-12 程式固定） | 14（與 about 共用同值，見 §5） |
| 焦點 `section.events#events` L125-189 | 標頭 3；精選卡 `featured.image/alt/flag(6)/date_place(20)/title(34)/desc(textarea 100)/tag(8)/url`；清單 `list.items[1..3].date(5)/yr(8)/title(35)/tag(6)/tag_style(enum is-members)/meta(10)/url`；回顧帶 `recap.label`＋`recap.items[1..7].label(32)/url` | 49 |
| 消息 `section.news#news` L192-224 | 標頭 3；`news.items[1..4].date(5)/yr(4)/title(40)/url`（現值全為 `#` 佔位，需真實連結） | 19 |
| 知識 `section.insights#insights` L227-276 | 標頭 3；篩選鈕 label ×5（key 固定不開放）；`cards[1..6].category(enum)/tag(8)/meta(12)/title(34)/source(22)/url` | 44 |
| 關於帶 `section.band#about` L279-287 | `about.image`/`about.eyebrow`(30)/`about.h2`(textarea 85)/`about.body`(textarea 75)/`about.legal`(40，與 about 頁 lede 共用值) | 5 |
| 會員 `section.membership#membership` L290-384 | 前言 6（h2 含 `<br>`）；價值 `values[1..6].icon(enum sprite)/h3(14)/body(70)`；費率 `fees[1..3].type(16)/name(10)/price(12)/unit(8)/init(30)/bullets[1..3](40)` — 費率與 membership 頁共用值（§5） | 45 |
| 課程 `section.courses#courses` L387-448 | 標頭 3；TIRIC `tiric.eyebrow/h3(20)/desc(textarea 160)/meta[1..3](26-70)/cta_label/cta_url/points[1..3].title(14)+small(32)`；課程列 `rows[1..5].h3(10)/body(28)`（編號固定）；`course_note`(80) | 34 |
| 夥伴 `section.partners#partners` L451-470 | 標頭 4；`logos[1..5].image/name(20)/url`；`more_line`(90) | 20 |
| CTA 帶 `section.band.band-cta` L473-484 | image/eyebrow(24)/h2(28)/body(45)/cta1_label+url/cta2_label+url | 8 |
| 尾段 `section.closing#contact` L487-525 | 電子報：eyebrow/h2(16)/lede(50)/placeholder(20)/按鈕 label（表單殼不動）/`newsletter_note`(30，示意文案待刪，裁決點 C)；聯絡：eyebrow/h2＋值引用 global `contact.*`＋`line_id`(10)/`line_note`(20)/`cta_label` | 15 |

### 4.2 about — 約 85 欄

| 區塊 | 欄位 |
|---|---|
| meta | title(40)/description(120) |
| 主視覺 `section.page-hero` L39-45 | image/eyebrow(20)/h1(16)/lede(40，＝global 法定名稱行) |
| 創會緣起 `.page-split`#1 L50-59 | eyebrow/h2(10)/para1(textarea 100)/para2(textarea 45) |
| 成立宗旨 `.page-split`#2 L61-69 | eyebrow/h2/mission(richtext-limited 含 `<strong>`，190) |
| 功能與服務 `.page-split`#3 L71-90 | eyebrow/h2/note_link(label+url)/`services.items[1..12]` 引用 global 共用值 |
| 理監事 `.page-split#team` L92-118 | eyebrow/h2(14)/note1(55，含日期與人數)/link1/link2/`blocks[1..3].role(8)`＋`members[n].name(6)/title(36)`（5 人固定）/cta_label+url |
| 功能委員會 `.page-split#committee` L119-167 | eyebrow/h2/note(70，內含電話引用 global)/`cards[1..5].name(8)/role(14)/convener(26)/members(20)` |
| 鄧白氏 `.page-split#duns` L169-178 | eyebrow(24)/h2(16)/note_link/para1(richtext-limited 120，含 `<strong>` 編碼)/para2(textarea 105) |

### 4.3 events — 約 120 欄

| 區塊 | 欄位 |
|---|---|
| meta＋主視覺 L39-45 | title/description/image/eyebrow(30)/h1(12)/lede(60) |
| 精選＋近期 L47-90 | `featured.url/image/alt(60)/flag(6)/date_place(24)/title(40)/desc(textarea 160)/tag(8)`；`list.items[1..3]` 同 home 結構（7 欄×3；date 為自由字串，容納「全年/隨時」） |
| 課程區 `#tiric` L92-152 | 標頭 2；`tiric.eyebrow/h3(25)/desc(180)/meta[1..3](70/50/45)/cta_label(12)/cta_url`；`points[1..3].title+small`；`rows[1..5].h3(10)/body(40)`；`course_note`(40) |
| 董監事進修 `#training` L156-190 | eyebrow/h2(20)/page_link(label+url)/`contact_note`(35，含窗口姓名電話)/prose(richtext-limited 140，含 3 個 `<strong>`)/`chips[1..15]`(20)/`rows[1..4].dt(6)+dd(60)` |
| IRC `#irc` L192-212 | eyebrow/h2/link1/link2/`contact_note`(35)/prose(richtext-limited 140)/`rows[1..7].dt(6)+dd(70)` |
| 獎項 `#awards` L214-226 | eyebrow/h2/link1/link2/`deadline_note`(date+text 50，時效性內容)/para1/para2(richtext-limited 140，para1 含內嵌連結) |
| 精彩回顧 `#recap` L230-249 | 標頭 2；`items[1..8].date(5)/yr(4)/title(40)/url` |

### 4.4 knowledge — 約 190 欄

| 區塊 | 欄位 |
|---|---|
| meta＋主視覺 L39-46 | title/description/image/eyebrow/h1/lede1(70)/lede2(90) |
| 篩選列 L50-56 | `filters[1..5].label`(10)——`data-filter` key 固定不開放 |
| 文章卡 L57-193 | `cards[1..27].category(enum bimonthly/niri/article/interview)/tag(8)/meta(12，日期或「NIRI × TIRI」自由字串)/title(35)/source(18)/url`（27×6=162；順序為人工編排，不做日期自動排序） |
| 年刊 `#yearbook` L197-226 | eyebrow/h2(10)/note(30)/prose(90)/`reports[1..3].title(20)+title_url/subtitle(50)/cta_label(6)/pdf`(file) |

### 4.5 news — 約 80 欄

| 區塊 | 欄位 |
|---|---|
| meta＋主視覺 L39-45 | title/description/image/eyebrow/h1/lede(40) |
| 消息列表 L47-70 | `items[1..18].date(5)/yr(4)/title(45)/url(optional)`——url 有值渲染 `<a>`＋箭頭、空值渲染 `<div>`（現狀 4/18 有連結；第 6 則連到 index.html 屬佔位） |

### 4.6 membership — 約 65 欄

| 區塊 | 欄位 |
|---|---|
| meta＋主視覺 L39-45 | title/description(80)/image/eyebrow(24)/h1(12)/lede(45) |
| 會員類別 L50-64 | eyebrow/h2/note(50)/`categories[1..6].term(8)+desc(80)` |
| 會費標準 L66-104 | eyebrow/h2/`plans[1..3].type(16)/name(10)/price(14)/unit(8)/init(30)/features[n](40)`（features 2/3/2 固定） |
| 專屬優惠 `#benefits` L106-127 | eyebrow/h2/link_note(label+url)/note(60)/`benefits[1..13].name(12)+desc(60)` |
| 治理服務 `#governance` L129-146 | eyebrow/h2(richtext-limited 含 `<br>`，20)/link1/link2/`contact_note`(35)/intro(textarea 90)/`features[1..4].dt(10)+dd(45)` |
| 加入 CTA L148-160 | eyebrow/h2(12)/body(60)/cta1_label+url/cta2_label+url |

### 4.7 partners — 約 45 欄

| 區塊 | 欄位 |
|---|---|
| meta＋主視覺 L39-45 | title/description/image/eyebrow(24)/h1/lede(40) |
| Logo 牆 L49-55 | `logos[1..5].image+name(20)`（現況無連結；alt 與 aria-label 同步寫入） |
| 優惠夥伴 L57-75 | eyebrow/h2/note(richtext-limited 含內嵌連結)/`partners[1..10].name(12)+desc(40)` |
| 贊助方案 `#sponsor` L77-112 | eyebrow/h2/note(50)/`tiers[1..3].type(20)/name(10)/price(10)/unit(4)/features[n](40)`（3/2/1 固定） |
| CTA L114-126 | eyebrow/h2/body(40)/cta_label+cta_url(mailto)/`contact_meta` 拆為引用 global tel/email |

### 4.8 join — 約 25 欄（表單本體禁區）

| 區塊 | 欄位 |
|---|---|
| meta＋主視覺 L39-46 | title/description/image/eyebrow(12)/h1/lede1(textarea 90，內含 email)/lede2(textarea 70，與費率共用值) |
| 申請區文案 L51-56 | eyebrow/h2(12)/note(textarea 110，四個價格數字與 membership 共用值) |
| `form_note` L78 | 「本頁為改版設計示意…」**錯誤文案（表單實際會送出），列裁決點 C** |
| 下載表格 L82-103 | eyebrow/h2/note(70)/intro(richtext-limited 90，含 `<strong>` 郵寄地址)/`downloads[1..2].name(20)/size_label(上傳時自動計算)/file`(docx) |
| 匯款資訊 L105-118 | `payment.bank(30)/account_name(20)/account_no(20)/bank_address(20)`——高敏感欄位，後台加二次確認 |
| **禁區** | `form[data-demo-form]` 內全部（13 個欄位 label、placeholder、submit 按鈕）；`forms.js` 一切 |

### 4.9 contact — 約 20 欄（表單本體禁區）

| 區塊 | 欄位 |
|---|---|
| meta＋主視覺 L33-39 | title/description(建議擴寫，60)/image/eyebrow(現值 About TIRI 為誤植，裁決點 C)/h1/lede(40) |
| 聯絡資訊 L44-62 | eyebrow/h2＋`contact.*` 引用 global（tel/email/address/access）＋`map.embed_url`（僅允許 maps.google.com embed 網址；地址改了地圖不會跟動，後台加提示） |
| 留言區文案 L64-70 | eyebrow/h2/note(40，現值「尚未串接」為錯誤文案，裁決點 C) |
| **禁區** | `form[aria-label="留言表單"]` 內全部；`forms.js` |

### 4.10 欄位總量與明確排除

- 總量級：10 個 page_slug、約 60 個區塊、**約 850–900 個中文欄位值**（雙語即約 1,700–1,800 筆值，JSON 儲存無 schema 負擔；後台依區塊分組呈現）。
- 明確排除（不進 manifest）：表單內部一切（label/placeholder/submit/隱藏欄）；`data-filter`/`data-category` key 與篩選機制；卡片/清單的數量與順序；icon sprite；`login.html`/`search.html`；所有歷史頁；動效與 `data-reveal` 屬性；navbar mega 選單結構（文字列第二優先）。

---

## 5. 跨頁共用值與內容問題清單（需 TIRI/你裁決）

**共用值（CMS 存一份、多處套用）**：聯絡資料（contact.html＋index 尾段＋partners CTA＋navbar 描述）；12 項服務清單（index＝about，逐字相同）；法定名稱＋統編行（index band＝about lede）；會費三卡（membership＝index，join 文案內數字亦引用）；13/10/5 三份夥伴清單（membership 優惠 13 ⊃ partners 優惠 10；logo 牆 5——manifest 各自獨立但後台放提示互鏈）。

**裁決點 C — 現值錯誤/衝突（建議在階段 3 塞初始值時一併修正，逐項需確認）**：
1. join.html L78「本頁為改版設計示意，表單不會實際送出」與 contact.html L68「送出功能尚未串接」——**與事實相反**（兩表單都已接真實後端），上線前必改。
2. 兩個不同辦公地址並存：重慶南路一段 57 號 13 樓之 13（contact/index/navbar）vs 忠孝東路二段 88 號 10 樓（TIRIC 上課地點）——後者是課程場地，不是錯誤，但 manifest 分為 `contact.address` 與 `tiric.meta[2]` 兩欄避免誤併。
3. about.html 王恩國職稱兩處不一致（L111 南昌菱光/今皓 vs L154 東友科技副董事長）。
4. 首頁 4 則消息 `href="#"`、知識頁 12/27 卡連到同一佔位頁 `news-387131.html`、news 第 6 則連 index.html、knowledge 年刊列 2「6 周年」連到 5th_report slug。
5. contact.html hero eyebrow 誤植「About TIRI」。
6. 頁尾 index 與 about 有 2 條連結漂移（IRC 贊助獎學金 vs 2026 熱門課程；專訪 vs 最新消息）——CMS 統一前需先選定基準。
7. 頁尾版權年份 2026、鄧白氏「180 年」等時效字串——維持文字欄位、後台加說明。

---

## 6. 前台內容套用方式（建議：伺服器端套入）

### 6.1 方案與理由

採規劃文件 8.2 的**伺服器端套入**，經現況驗證可行且改動面小：

1. `frontend_by_host()`（app.py:851）是前台唯一出口，已集中處理 Host 判斷；在其中加一個攔截：`path` 命中 CMS 白名單（`/`、`/index.html`、`/html/index.html`、`/html/about.html` 等 10 頁映射）時改走 `render_cms_page(page_slug, locale)`——讀 `FRONTEND_DIR` 靜態檔 → 依 manifest 把 DB 值套進 `data-cms` 節點（文字 escape、URL 分類驗證）→ 回應；**任何異常或無資料一律回原始 `send_from_directory`（fallback 保證）**。其餘 124 頁與所有資產完全不變。
2. 前台已全域 `Cache-Control: no-store`（app.py:263），無快取過期問題；SEO 與首屏直接是套用後 HTML，無閃動。可另做行程內 cache（套用後 HTML 存記憶體，儲存時依 page+locale 失效）——規劃文件允許。
3. 表單完全不受影響：表單打的是後端網域（`tiribackend*`），不經前台分流；套用只動白名單頁的指定節點，不碰 `<form>` 子樹。
4. 客戶端方案的缺點（閃動、SEO 基準過期、要跨網域打 API、134 頁共用 JS 載入邏輯）在此架構下都不必承受——故不採用。

### 6.2 例外：導覽/社群（JS 渲染內容）

navbar 內容不在 HTML，DOM 替換無效。若 global 的社群連結與（未來）導覽文字要生效：伺服器端套入時在 `<head>` 注入 `<script type="application/json" id="tiri-cms-global">{…僅白名單 key…}</script>`，`v1/js/navbar.js` 啟動時讀取、逐 key 覆蓋內建預設值（讀不到＝維持現狀，天然 fallback）。**只改 `v1/js/navbar.js`——它已與 shared 分岔（`e8e351f`），V1 獨立維護，shared 那份屬 V2 不動。** 歷史頁不經套用、無注入 → navbar 顯示內建值（見風險 5）。語言切換的「切到當前頁對應語言」也在同一支檔案處理（依注入的 zh↔en 對應或內建表 rewrite `renderLangSwitch()` 兩個 href）。

### 6.3 雙語資料如何輸入與儲存（後台編輯流程）

**資料模型**：`cms_pages (page_slug, locale, content_json)`——每頁每語系一列 JSON；`locale` 僅 `zh-Hant`/`en`，兩語系共用同一套 manifest 欄位、分開儲存、互不覆蓋（符合規劃 §5.2–5.4）。

**後台操作流程**（管理者視角）：
1. 側欄「網站內容」→ 頁面清單（10 項，§4 的 page_slug）→ 進入單頁編輯。
2. 頁首「中文｜English」頁籤切換語系；欄位依前台區塊分組，標籤用白話（「首頁主視覺／主標題」），不露程式 key。
3. **中文頁籤**：每個欄位以「目前前台顯示值」為預設呈現——DB 無值時顯示的就是靜態 HTML 現值（即 fallback 本身），存檔才寫入 DB。所以不需要預先把全站中文塞進資料庫（階段 3 採此策略）。
4. **English 頁籤**：只對「英文對應頁已存在」的頁面開放（初期僅首頁 en.html；其餘顯示「此頁英文版尚未建立，待英文定稿後開放」）。欄位空白＝尚未提供英文；**空白不會用中文補**（規劃 5.6），英文頁顯示的是該英文頁自己的靜態基準內容。
5. 圖片/附件欄：兩語系各自存路徑；English 頁籤提供「沿用中文檔案」按鈕（複製同一路徑，符合規劃 5.4 共用圖片），也可另傳英文版圖（如含中文字的視覺）。
6. 單一「儲存」動作（POST、登入必要），成功/失敗用既有 `bToast`；儲存即生效（無草稿/排程），並使該 page+locale 的伺服器 cache 失效。

**英文頁的產生方式（重要設計決策）**：英文值必須有「英文靜態基準頁」作為落點與 fallback，才能保證缺欄位時不會露出中文或空白。因此每當 TIRI 提供某頁英文定稿：
1. 開發者以中文頁為模板建立英文靜態頁（同版型同區塊、同 `data-cms` key、`lang="en"`），內容填入 TIRI 定稿——這份靜態頁本身就是英文 fallback；
2. URL：首頁沿用既有 `en.html`（重建為 V1 版型、保留公開 URL）；其他頁採 `<name>_en.html`（沿 V1 既有 board_en/team_en 慣例）；
3. 之後管理者在 English 頁籤的修改走 CMS 覆蓋，機制與中文完全相同；
4. zh↔en 對應表（manifest 內建）同時驅動語言切換連結 rewrite——切換一律前往當前頁的對應語言頁（修復現況「一律跳 en.html/index.html」，符合規劃 5.8），沒有英文對應的頁面暫時維持指向 en.html。

**給 TIRI 的內容收集**：§4 的 manifest 可直接匯出成「欄位收集表」（頁面/區塊/欄位/中文現值/英文欄空白），作為 2026-08-28 英文定稿的交付格式，避免收到整篇散文再人工拆欄位。

### 6.4 標記策略

- 10 頁核心 HTML 加 `data-cms="page:key"`（文字節點）與 `data-cms-attr`（href/src/alt）、`data-cms-style="--hero-img"`（hero 背景），純屬性、零視覺影響；`npm run check` 不受影響。
- 產生器凍結（裁決點 A）後不需同步產生器；於 v1build README 註記「若復活產生器，需把 data-cms 標記併入模板」。

---

## 7. 圖片與附件：持久化、公開路徑、備份

| 項目 | 開發 | 正式（EC2＋RDS） |
|---|---|---|
| 儲存目錄 | `.env` `CMS_UPLOAD_DIR` 指向 repo 外（例 `~/tiri-cms-uploads-dev`），避免誤入版控/打包 | `CMS_UPLOAD_DIR=/srv/tiri-cms-uploads`（獨立於 `FRONTEND_DIR` 與程式目錄，frontend.zip 部署覆蓋不到） |
| 公開路徑 | 前台 Host `/uploads/<uuid>.<ext>`：`frontend_by_host()` 加分支，經白名單副檔名＋`safe_join` 檢查後 `send_from_directory(CMS_UPLOAD_DIR, …)`；後端網域同一 route 供後台預覽 | 同左 |
| DB | `cms_pages.content_json` 只存相對路徑（`/uploads/xxx.webp`）＋原始檔名/alt 等顯示資訊，不存二進位 | 同左 |
| 驗證 | 圖片 JPG/PNG/WebP、附件 PDF/DOC(X)/XLS(X)/PPT(X)；副檔名＋magic bytes 雙驗證；拒 SVG 與可執行檔；單檔 10MB（join 現有 docx 僅 ~208KB、年刊 PDF 在既有 documents/ 不需搬移，10MB 足夠）；UUID 檔名；上傳/刪除一律登入＋POST | 同左 |
| 備份 | 不需 | **DB＝RDS 自動快照；`CMS_UPLOAD_DIR` 需另外納入備份（cron tar → S3 或 EBS snapshot），上線前與 Will 確認排程**——規劃文件 9.1 的必要條件 |
| 既有檔案 | v1/documents/、v1/images/ 維持隨 frontend.zip 部署；CMS「更換」的新檔一律進 uploads，不覆蓋原檔（原檔即 fallback） | 同左 |

---

## 8. 風險清單

| # | 風險 | 影響 | 緩解 |
|---|---|---|---|
| 1 | **誤跑產生器**把 134 頁回退（含 data-cms 標記全失） | 高 | 裁決點 A 凍結＋README 警語；標記加入後立即 commit 作為還原點 |
| 2 | **表單 label＝後端欄位 key**；CMS 誤開放表單文字 | 高（收件資料 schema 被改） | manifest 硬性排除表單子樹；render 端跳過 `<form>` 內節點的雙保險 |
| 3 | **改壞 `frontend_by_host()`** → 前台全站掛 | 高 | 套用邏輯包在 try/except、失敗回原始靜態檔；白名單以外路徑走原碼路徑不動；上線前以正式 Host 全頁抽測＋`npm run check` |
| 4 | CMS 查詢拖慢前台（每請求讀檔＋套值＋DB） | 中 | 行程內 cache（儲存時失效）；DB 失敗計數短路（連續失敗直接回靜態） |
| 5 | **global 欄位只套 10 頁**，124 歷史頁頁尾/導覽維持舊值 → 不一致 | 中 | 向 TIRI 說明範圍；聯絡資料等若真的變更，另跑一次性 string-patch 腳本（board_pages.py 已有先例）同步歷史頁 |
| 6 | navbar.js 已分岔（v1/js＝V1 唯一源頭、shared＝V2）；誤把 shared 蓋回 v1 會退掉語言切換移位 | 中 | 文件化分岔事實（本文件＋memory 已記）；CMS 改動只碰 v1/js/navbar.js |
| 7 | `init_db()` import 時執行；加表失敗會擋 app 啟動 | 中 | `cms_pages` 沿用同一 `IF OBJECT_ID` 冪等寫法；migrate_to_prod.py 補上 cms_pages（上線檢查項） |
| 8 | 測試站（82）與正式站內容/上傳分離 | 低 | 天然分離（DB_NAME＋各自 CMS_UPLOAD_DIR）；階段 4 於兩站各驗一輪 |
| 9 | 語言切換現狀違反規劃 5.8（一律跳首頁） | 低 | 階段 2 以 zh↔en 對應表 rewrite 切換連結；無對應英文頁時維持指向 en.html，不發明新 URL |
| 10 | 後台無 CSRF（既有） | 低（沿用現況） | CMS 寫入沿用 require_auth＋POST＋JSON；不在本期擴大處理，如要補齊另開工項 |

---

## 9. 分階段實作與測試計畫

**階段 1（縱向切片）**：`init_db()` 冪等加 `cms_pages`；新增 `server/cms_schema.py`（先只含 home.hero 5 欄）＋`server/cms_service.py`（讀/驗/存/fallback）；後台「網站內容」頁（`nav_items()` 加項、`cms_content.html` extends base、中文｜English 頁籤、bToast 回饋）；`frontend_by_host()` 套用 home；`v1/html/index.html` hero 加 data-cms。
驗證：後台改主標題→前台 Host 立現；清空 DB 記錄→顯示原始靜態內容；後台/收件匣回歸不受影響。

**階段 2**：上傳功能（CMS_UPLOAD_DIR＋/uploads route＋雙重驗證）；其餘 9 頁＋global 依 §4 分批加標記與 schema（每批跑 `npm run check`）；navbar.js JSON 注入（同步 shared 副本）；zh↔en 對應表定案（裁決點 B）。

**階段 3**：中文初始值＝**不預塞 DB**（DB 無值即 fallback 靜態現值，本來就是已確認中文內容），只把 §5 裁決點 C 的修正寫入；英文內容到位後建立英文頁與 en 值，缺件持續列表；逐型別×語系×fallback 測試；六表單＋收件匣＋郵件＋帳號回歸；桌機/手機版型抽測；`npm run check`。

**階段 4**：正式 `.env` 加 `CMS_UPLOAD_DIR`；`migrate_to_prod.py` 確認 cms_pages；重打包 frontend.zip（含 data-cms 標記）部署兩站；RDS 快照＋uploads 備份排程確認（Will）；正式 Host 改一組測試內容→驗證→復原→清除。

---

## 10. 預計新增與修改的檔案

**新增**：`server/cms_schema.py`（manifest 唯一定義處）；`server/cms_service.py`（驗證/儲存/套用/上傳）;`server/templates/cms_content.html`；本文件。
**修改**：`server/app.py`（init_db 加表、nav_items 加項、/admin/content 路由群、frontend_by_host 套用＋/uploads 分支）；`v1/html/` 10 個核心頁（僅加 data-cms 屬性）；`v1/js/navbar.js`（JSON 注入讀取＋語言切換對應表；已與 shared 分岔，只動 v1 這份）；`server/.env`/`.env.example`（CMS_UPLOAD_DIR）；`_archive/scripts/v1build/README.md`（凍結警語）。
**不動**：`v1/js/forms.js`、六表單流程、`migrate_to_mssql.py`、其他後台 template、124 頁歷史頁、`v2/`。

---

*等待確認事項：裁決點 A（凍結產生器）、B（英文版範圍與 URL 慣例）、C（§5 內容錯誤修正清單）。確認後進入階段 1。*
