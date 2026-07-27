# TIRI 過渡期表單收件後端

前台六個報名表單（加入會員 join、董監事課程 trainbod、TIRIC 課程 tiric、
董事會績效評估 bodperform、公司治理評估 corpperform、聯絡我們 contact）
送出後由這個服務接收：存進 SQLite（`submissions.db`），並寄 email 通知。

## 本機啟動

```bash
cd server
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env        # 填入 SMTP 帳密與收件人
.venv/bin/python app.py     # http://localhost:8000
```

- `MAIL_DRY_RUN=1` 時不真的寄信，只印在終端機（測試用）；上線改成 `0`。
- 收件列表：`http://localhost:8000/admin`（帳密在 .env 的 ADMIN_USER / ADMIN_PASS）。

## 前端串接

[original/js/forms.js](../original/js/forms.js) 已掛在 12 個含表單的頁面上，
會攔截原本送往 Weebly 的表單，改 POST 到 `{API}/api/submit/<頁面slug>`。

API 位置預設 `http://localhost:8000`。部署後端後，在 forms.js 前面加一行
設定實際網址（或直接改 forms.js 開頭的預設值）：

```html
<script>window.TIRI_FORMS_API = 'https://forms.tiri.tw';</script>
```

## 換版型時怎麼接（可拆換設計）

後端跟版型完全解耦：後端只收「`{label, value}` 欄位陣列」，不在乎前端長怎樣。
[forms.js](../original/js/forms.js) 一支腳本同時支援兩種表單結構——
原版 Weebly 匯出（`.wsite-form-field`）和 V1/V2 改版表單（`.field`＋`data-demo-form`，
需至少 2 個欄位才會綁定，避免誤綁搜尋/訂閱等示意表單）。

之後要把 v1 或 v2 接上（以 v1 為例）只要兩步：

```bash
cp original/js/forms.js v1/js/forms.js
# 對每個含表單的頁面，在 </body> 前加：
#   <script defer src="../js/forms.js?v=<日期>"></script>
```

拆掉也一樣：移除 script 標籤即可，頁面回到純靜態，不留任何痕跡。
表單頁檔名（join / trainbod / tiric / bodperform / corpperform / contact）
就是後端的分類依據，各版檔名相同，所以三個版本收進來會自動歸到同一類。

## 部署注意

1. GitHub Pages 只能放靜態檔，這個 Python 服務要跑在別的主機
   （公司主機、或 Render / Fly.io / PythonAnywhere 之類）。
2. 正式環境用 `gunicorn app:app` 跑，別用 Flask 內建伺服器。
3. `.env` 裡設 `ALLOWED_ORIGINS` 為前台網域（逗號分隔），別留 `*`。
4. `submissions.db` 就是全部收件資料，記得排備份。
