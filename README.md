# TIRI 官網 UI 改版專案

以 `https://www.tiri.tw` 的靜態封存為基準，進行 UI/UX 改版。原版與各新版版型以資料夾完全區隔，
每個版型資料夾內都有自己的 `html/`、`css/`、`js/`、`images/`；V1、V2 的導覽資料與標記共用 `shared/navbar.js`，以 `variant` 保留各版外觀。

客戶提供的原始文件位於上層 `../ref/`；研究與專案文件位於 `Files/`。

## 使用方式

```bash
npm run dev
```

啟動後開啟 `http://localhost:4173/`，根目錄 `index.html` 是版本入口，可切換：

| 版本 | 路徑 | 說明 |
|---|---|---|
| 原版 | `original/` | tiri.tw 靜態封存基準（126 頁） |
| V1 | `v1/` | 精緻歐美專業協會版（精品編輯風）：**完整站**——10 頁重新設計＋122 頁原站內頁全部套入 V1 版型（含英文版），內部連結互通 |
| V2 | `v2/` | 第二版版型，資料夾已建立，風格待定調 |

註：V1 的圖片已複製為獨立資產（`v1/images/`）；大型 PDF（年刊、雙月刊等）不重複複製。
V1、V2 的共用文件與後續補齊的原站圖片指向 `original/documents/` 與 `original/images/`；
只有 SurveyCake、Accupass、YouTube、Weebly 表單等原本就屬於第三方的服務保留外連。

## 檔案結構

```text
WEB DEMO/
├── index.html   # 版本切換入口（根目錄僅保留此檔＋README＋package.json）
├── original/    # 原版靜態封存（html/css/js/images/documents）
├── v1/          # 新版 V1 精品風（html/css/js/images/fonts）
├── v2/          # 新版 V2 骨架（html/css/js/images）
├── shared/      # V1/V2 共用元件（navbar 選單資料、桌面 mega menu、行動抽屜）
├── Files/       # 專案背景、研究、設計規範、design-qa 文件
├── _archive/    # 同步、整理、檢查、本地預覽工具與歷史資料
├── README.md
└── package.json
```

## 共用導覽

V1、V2 的每個 HTML 頁面只保留 `<tiri-navbar variant="v1|v2">`。要調整選單名稱、連結、說明文字、圖片或行動版項目，統一編輯 `shared/navbar.js`，不再逐頁修改。

## V1 設計依據

- `Files/15國IR網站設計規範與排版架構盤點.md`：design tokens、微互動、icon、字體與轉場規格
- 精品編輯風：直角（radius 0–2px）、內容寬 1200px、正文 17px/1.6、按鈕高 50px
- 字體：Archivo（英數）＋ Roboto Mono（功能字）＋系統繁中字體；字檔已本地化於 `v1/fonts/`
- 所有動效支援 `prefers-reduced-motion`

## 重新同步公開網站（更新 original/）

```bash
python3 -m pip install -r _archive/scripts/requirements.txt
npm run mirror
npm run organize
npm run localize
```

鏡像輸出至 `original/`。表單送出、站內搜尋、Google Maps、YouTube 等第三方服務仍需連線，
不含原網站後台與會員資料。`npm run check` 會檢查全部版本的本地連結完整性。
