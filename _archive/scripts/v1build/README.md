# V1 頁面產生器

V1（`v1/html/`）的 131 頁由這裡的腳本產生；**改 shell（header／nav／footer）請改腳本再重跑，不要手改各頁**。

## 重跑順序（四步，順序不可換）

```bash
# 1. 產生 10 個重新設計頁（about/events/knowledge/news/membership/partners/join/login/search）
python3 scripts/v1build/build_pages.py

# 2. 轉換原站 122 頁進 V1 外殼（需 beautifulsoup4；圖片自動複製到 v1/images/）
python3 -m venv .venv && .venv/bin/pip install beautifulsoup4   # 首次
.venv/bin/python scripts/v1build/convert_pages.py

# 3. 連結對接（策展頁卡片 → 真實文章／回顧頁）＋補丁
.venv/bin/python scripts/v1build/relink.py

# 4. 理監事名冊頁（覆寫 convert 產出的 team*.html＋建 board.html／board_en.html＋接導覽）
python3 scripts/v1build/board_pages.py
```

之後手動補丁（relink 未涵蓋）：knowledge.html 的 191118 文章卡、news.html 的 5/30 講座連結、
專訪卡改中文頁 `2356035370-….html`——詳見 git log 或直接 grep。

## 檔案

- `build_pages.py`：策展頁內容＋shell（含 NAV 下拉結構 `NAV = [...]`）
- `convert_pages.py`：原站→V1 轉換器（同一份 NAV；`SKIP` 集合是策展頁佔用的檔名）
- `nav_def.py`：NAV 結構參考副本（兩支腳本內已內嵌同邏輯，改選單時三處同步）
- `relink.py`：由原站列表頁解析 title→href 對照，改寫策展頁連結
- `board_pages.py`：理監事名冊頁。convert_pages.py 會把 `team*.html` 從原站的 Weebly
  multicol table 轉進來，本步驟以設計版覆寫之，並產生歷屆索引 `board.html`／`board_en.html`。
  名冊資料以 dict 常數維護（`ZH` / `EN`）——**改名單改這裡，不要手改 HTML**。
  照片在 `v1/images/board-*.jpg`（原檔最大僅 617×412，版面已據此限寬，勿放大）。

## 注意

- `index.html` 不在產生器內；改 shell 後需另外把 header 區塊同步進 index.html
  （見 relink 流程或用 python 以 build_pages.shell 摘出頭部替換）。
- 驗收：`npm run check`（全站本地連結零缺失）。
