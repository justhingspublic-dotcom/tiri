# V1｜精緻歐美專業協會版（精品編輯風）

第一版新版型。定位：**精緻的歐美專業協會網站**——金融產業可信度，拒絕傳統公協會的固定寬、小字、高密度框線。

## 參考組合（依 Files/15國IR網站設計規範與排版架構盤點.md）

1. Swiss IR Club — 精緻度、微互動節奏、icon、字體、標籤與篩選
2. NIRI — 大型內容架構與首頁焦點編排
3. AIR — 精品留白、雙字體系統（Archivo＋Roboto Mono）、黑白 CTA
4. AERI — 歐美影像感與 section 敘事節奏

## 風格定調

- **精品編輯風**：直角 radius 0–2px、hairline 分隔線、大留白
- 色彩：墨黑 `#17141F`＋暖白 `#FBFAF8`＋TIRI 紫 `#6C1F93`（僅用於強調與 hover）
- 版面：內容寬 1200px、section 間距 96/64/48、正文 17px/1.6、H1 56/38
- 微互動：hover 一律只變色（無陰影、無位移、無縮放）；入場 stagger 70ms、
  count-up 900ms 一次性、篩選淡入淡出 350ms；全部支援 `prefers-reduced-motion`

## 結構

```text
v1/
├── html/                    # 132 頁完整站
│   ├── index.html           # 首頁（11 段式骨架）
│   ├── about/events/knowledge/membership/news/partners.html  # 6 大重新設計內頁
│   ├── join/login/search.html                                # 功能頁
│   └── （其餘 122 頁）       # 原站全部內頁套入 V1 外殼（含英文版），檔名與原站相同、互鏈保持
├── css/
│   ├── main.css             # design tokens＋全部樣式
│   ├── legacy-content.css   # 原站內容元素在 V1 內的樣式（標題/相簿/多欄/表單/按鈕）
│   └── legacy-inline.css    # 原站版面資訊（相簿欄寬、背景圖），複製自 original/
├── js/main.js               # 入場、count-up、篩選、抽屜、示意表單防跳頁
├── images/                  # 全部引用圖片已複製（自足）
└── fonts/                   # Archivo 300–700＋Roboto Mono 400/500（latin 子集，本地化）
```

導覽與卡片皆連到真實內頁：文章卡→雙月刊／NIRI 文章頁、精彩回顧→各屆大會頁（含相簿）、
課程區→tiric／trainbod／certification 完整頁。大型 PDF 連 `original/documents/` 或 tiri.tw 原始連結。

## 內容來源

頁面內容全部取自 `original/`（tiri.tw 封存）的真實公開資訊：

- 協會宗旨、創會緣起、統一編號（mission）
- 焦點訊息：2025 年度大會「引領 IR 智慧新時代」（首頁＋精彩回顧）
- 歷屆年度大會 2018–2025 共 8 屆（精彩回顧）
- TIRIC 實戰班：NIRI 授權教材、2026/08/21 起 5 堂、定價與早鳥（tiric）
- IRC 證照：US$1,295、會員折 US$200（certification）
- 會員類別與會費：個人 2,000＋6,000／年、團體 6,000＋60,000／年、永久（membership）
- 會員優惠：課程時數、治理服務 85 折、10 家合作廠商（benefit）
- 功能與服務 12 項（services）、最新消息（news）、知識分享文章標題（news-387131 等）
- 聯絡資訊與社群連結（contact＋footer；email 由 Cloudflare 保護編碼還原為 office@tiri.tw）

版面與排版為改版設計提案；正式對外仍以協會公告為準。
