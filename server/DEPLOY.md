# TIRI 表單後端 — 部署指南

> **⚠️ 2026-07-30 起本文件已過時**：資料層已從 SQLite 檔案改為**公司內部 SQL Server**
> （192.168.1.92，正式庫 `TIRI`、開發庫 `TIRI_dev`，連線資訊在 `.env` 的 `DB_*`），
> 不再需要 PythonAnywhere 等外部主機方案，部署＝公司伺服器跑 Flask＋pip 裝 requirements。
> 資料不存在程式資料夾內，**覆蓋更新資料夾不會再弄丟資料**。以下內容僅供歷史參考。

> 目標：把 `server/`（Flask ＋ submissions.db）從本機搬上雲端，
> 前台（GitHub Pages 靜態頁）改打正式 API。
> 本文四部分：方案比較 → 部署教學 → 部署後要改的東西 → 上線前 checklist。

---

## 1. 方案比較與推薦

這個後端有三個硬需求，直接刷掉大部分免費方案：

1. **SQLite 檔案要永久保存** — `submissions.db` 就是全部收件資料＋設定（SMTP 密鑰、文案、後台密碼）
2. **能連 Gmail SMTP（對外 587 埠）** — 通知信靠它
3. **不能睡眠** — 服務睡著時有人送表單，喚醒要近 1 分鐘，前台 fetch 早就 timeout，等於掉單

| 方案 | 月費 | SQLite 保存 | Gmail 寄信 | 睡眠問題 | 操作難度 |
|---|---|---|---|---|---|
| Render 免費版 | $0 | ✗ 每次重啟/重新部署**資料全消失** | ✓ | ✗ 15 分鐘沒流量就睡 | 低 |
| Render Starter＋磁碟 | 約 US$7.25 | ✓ | ✓ | 無 | 低 |
| PythonAnywhere 免費版 | $0 | ✓ | ✗ **免費帳號擋對外 SMTP，寄不了信** | 無（但每 3 個月要手動點一次續期） | 最低 |
| **PythonAnywhere Hacker** | **US$5** | ✓ | ✓ | 無 | **最低** |
| Fly.io | 約 US$3–5，需綁信用卡 | ✓（要另掛 Volume） | ✓ | 可設常駐 | 高（要 CLI＋Docker） |

**推薦：PythonAnywhere Hacker（US$5/月）。** 理由：

- 唯一同時滿足三個硬需求、又不用碰 Docker / CLI 部署的最低價選項
- 全程網頁操作：檔案總管上傳/編輯檔案、瀏覽器裡開終端機，最貼合「會用終端機但不熟伺服器」
- 就是為 Flask＋SQLite 這種小服務設計的，`https://你的帳號.pythonanywhere.com` 自帶 HTTPS
  （前台是 https，API 一定也要 https，不然瀏覽器會擋）
- 真正的免費方案不存在：Render 免費版會**弄丟收件資料**、PythonAnywhere 免費版**寄不了通知信**，
  這兩個缺陷對這個系統都是致命的

---

## 2. 部署教學（PythonAnywhere，一步一步）

### 步驟 1：註冊與付費

1. 到 https://www.pythonanywhere.com 註冊。**帳號名就是網址**
   （例：帳號 `tiriforms` → 網址 `https://tiriforms.pythonanywhere.com`），取個正式一點的
2. 右上角 Account → 升級 **Hacker plan**（US$5/月，信用卡）

以下步驟中 `帳號名` 請自行代換。

### 步驟 2：本機打包上傳

在 Mac 終端機：

```bash
cd "/Users/jonathanyu/Desktop/Travail/投資人協會 TIRI/WEB DEMO"
zip -r ~/Desktop/tiri-server.zip server \
  -x "server/.venv/*" -x "server/server.log" -x "server/__pycache__/*"
```

這個 zip **含 `submissions.db` 和 `.env`**——資料庫和設定（SMTP 密鑰、文案、後台密碼都存在
db 的 settings 表裡）就是這樣帶上去的，不用另外搬。

到 PythonAnywhere 網站 → **Files** 頁 → Upload a file → 選 `~/Desktop/tiri-server.zip`。

### 步驟 3：解壓與安裝套件

**Consoles** 頁 → Start a new console → **Bash**，貼上：

```bash
cd ~
unzip tiri-server.zip
python3.11 -m venv venv
venv/bin/pip install -r server/requirements.txt
```

跑完 `ls ~/server` 應該看到 app.py、submissions.db、templates 等。

### 步驟 4：建立 Web app

1. **Web** 頁 → **Add a new web app** → 網域用預設的 `帳號名.pythonanywhere.com` → Next
2. 選 **Manual configuration**（⚠️ 不要選 Flask 精靈，它會建一個範本專案）→ **Python 3.11** → Next
3. 建好後在同一頁設定三個地方：
   - **Source code**：`/home/帳號名/server`
   - **Virtualenv**：`/home/帳號名/venv`
   - **WSGI configuration file**：點進去，**整個檔案內容換成**下面五行後存檔：

```python
import sys
path = '/home/帳號名/server'
if path not in sys.path:
    sys.path.insert(0, path)
from app import app as application
```

（PythonAnywhere 自己會用正式伺服器跑這個 `application`，不需要裝 gunicorn。）

### 步驟 5：改正式環境設定

**Files** 頁 → 進 `server/` → 點 `.env` 編輯：

1. `SECRET_KEY`：換成隨機字串。在 Bash console 跑這行產一組，貼過去：
   ```bash
   python3.11 -c "import secrets; print(secrets.token_hex(32))"
   ```
2. `ALLOWED_ORIGINS`：把 `*` 換成前台的網域（見下方第 3 節，格式注意事項也在那）
3. 其他行（SMTP、MAIL_TO 等）不用管——正式值都在 submissions.db 的 settings 表，後台改就好

### 步驟 6：啟動與驗證

1. **Web** 頁 → 綠色 **Reload** 按鈕（以後**每次改 .env、程式或範本檔都要按一次**）
2. 瀏覽器開 `https://帳號名.pythonanywhere.com/healthz` → 顯示 `ok`
3. 開 `https://帳號名.pythonanywhere.com/admin` → 能登入、收件匣/設定資料都在
   （資料跟著 db 檔上來了）
4. 後台 → 郵件設定 → **寄測試信** → 信箱有收到 → 寄信功能在雲端也通了

### 之後要更新程式怎麼辦

小改（改一兩個檔）：Files 頁直接點檔案編輯、或上傳覆蓋 → Web 頁 Reload。
大改：本機重打 zip（**排除 submissions.db 和 .env**，別把雲端資料蓋掉！）→ 上傳解壓 → Reload：

```bash
zip -r ~/Desktop/tiri-update.zip server \
  -x "server/.venv/*" -x "server/server.log" -x "server/__pycache__/*" \
  -x "server/submissions.db" -x "server/.env"
```

---

## 3. 部署後要改的東西

### 3.1 前台 forms.js 的 API 位址

[original/js/forms.js](../original/js/forms.js) 第 3 行：

```js
var API_BASE = window.TIRI_FORMS_API || 'http://localhost:8000';
```

把 `http://localhost:8000` 改成 `https://帳號名.pythonanywhere.com`。
（`window.TIRI_FORMS_API` 的覆寫機制保留著，本機測試時可以在頁面前面塞一行改回 localhost。）

改完 commit ＋ push，讓 GitHub Pages 更新。若表單頁的 `<script src="../js/forms.js?v=...">`
帶版本參數，順手改成新日期，避免瀏覽器用舊快取。

### 3.2 ALLOWED_ORIGINS（雲端 .env）

值＝前台網站的「origin」：**只有 https:// ＋網域，不含路徑、結尾不加斜線**，多個用逗號分隔。

- 前台若是 GitHub Pages 專案頁（repo 是 `justhingspublic-dotcom/tiri`），origin 是
  `https://justhingspublic-dotcom.github.io`（**不含** `/tiri` 路徑）
- 不確定的話：開前台網頁 → 網址列**網域以前**的部分就是
- 之後綁正式網域（如 `https://www.tiri.tw`）記得加進來，逗號分隔，改完 Reload

### 3.3 SECRET_KEY（雲端 .env）

部署步驟 5 已換隨機字串。重點：**別再用預設值** `tiri-transitional-backend`
（它寫在公開 repo 的程式碼裡，等於沒加密，session 可被偽造）。

### 3.4 submissions.db 資料搬移

- 設定（SMTP 密鑰、通知信文案、後台密碼、收件人）**全部存在這個檔的 settings 表**，
  zip 帶上去就完成搬移，不用重設
- 上傳後若又在本機測試過、想以本機為準：Files 頁上傳 `submissions.db` 覆蓋 → Reload
- **上線後方向就反過來了**：雲端的 db 才是正本，本機那份只當歷史備份，別再互相覆蓋
- 備份：每週從 Files 頁下載一次 `submissions.db` 存起來（它就是全部家當）。
  想自動化：Tasks 頁排每日任務
  `cp ~/server/submissions.db ~/backup-$(date +%F).db`（記得偶爾清舊檔）

---

## 4. 上線前 checklist

上線＝告訴大家可以開始用之前，照順序做：

- [ ] **清測試資料**：PythonAnywhere Bash console 執行
  `sqlite3 ~/server/submissions.db "DELETE FROM submissions; DELETE FROM sqlite_sequence WHERE name='submissions';"`
  （只清收件，設定不動）
- [ ] **重產 Gmail 應用程式密碼**：舊的在開發期間出現過，換掉。
  Google 帳戶 → 安全性 → 兩步驟驗證 → 應用程式密碼 → 刪掉舊的 → 新增「TIRI 網站」→
  把新密碼貼到後台「郵件設定」的 SMTP 密碼（有空格沒關係，系統會自己去掉）→ 儲存
- [ ] **收件人換 Judy**：後台郵件設定 → 通知信收件人改成 Judy 的信箱
  （要多人收就逗號分隔，例：`judy@tiri.tw, office@tiri.tw`）
- [ ] **關測試模式**：同頁「測試模式」勾勾拿掉 → 儲存 → 回儀表板確認「測試模式」卡顯示**關**
- [ ] **寄測試信**：按「寄測試信」→ 確認 **Judy 真的收到**（請她回報，順便確認沒進垃圾信）
- [x] **移除快速登入鈕**：已於 2026-07-28 從 `server/templates/login.html` 移除
  （若部署的是更早的版本，開登入頁確認沒有「快速登入」按鈕即可）
- [ ] **後台密碼換正式的**：現在還是 `tiri1234`。後台「帳號設定」改一組 8 字以上的正式密碼，
  記在安全的地方（給 Judy 的話用安全管道傳）
- [ ] **正式流程全跑一次**：用手機**行動網路**（不要連 Wi-Fi，模擬真實訪客）開正式前台網址 →
  填「聯絡我們」送出 → 前台綠色成功訊息 → 後台收件匣有這筆、通知信狀態 sent → Judy 收到信
- [ ] **設定備份習慣**：行事曆排每週提醒「下載 submissions.db」（或設 Tasks 自動備份，見 3.4）
