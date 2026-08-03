# V2｜B＋ 友善清爽版（扁平・無襯線）

第二版版型。定調：**Notion 骨架 × 扁平清爽**——歐美科技公司排版感，但明確排除襯線體、發黃暖底、陰影浮卡與漸層。

## 風格定調（2026-07-21，經 A/B/C/B＋ 樣張比稿定案）

- **字體**：全無襯線（PingFang TC / Noto Sans TC / Inter），標題粗體 650–700＋負字距
- **色彩**：純白 `#ffffff`＋淡中性面 `#f7f6f8`＋墨黑 `#1a1820`＋**品牌茄紫 `#7e3268`**（自原紫 #6c1f93 暖化；hover 深端 `#5c2249`）；sticker 柔色（lilac/sky/mint）點綴
- **形狀**：卡片圓角 16/26px、按鈕 pill（999px）
- **深度**：**扁平**——hairline `#eceaef` 邊框與實色色塊；無 box-shadow、無漸層、無 hover 上浮
- **版面**：沿用 V1 滿寬語言（1760px／gutter 3.2vw）
- 風格探索樣張保留於 `styles/`（A=vercel、B=notion、C=stripe、B＋=定案）

## 建置方式

自 V1 完整複製（134 頁＋css/js/fonts/images 自足），再以兩層改造：

1. `css/main.css`：design tokens 全面改寫（色彩/字體/圓角/按鈕 pill 扁平化）＋檔尾「B＋ 覆寫層」（標題字重負字距、淡面區塊、卡片圓角收斂）＋首頁 `hero-clean`
2. `html/index.html`：首頁 hero 改 B＋ 乾淨版（純白、文字左＋圓角照片右），取代 V1 滿版沉浸照片
3. **結構層（scratchpad `v2_restructure.py` 一次 patch 134 頁＋main.css 結構層 CSS）**：
   - header 124px 雙排 → **80px 單排**（工具列移除；搜尋 icon＋登入注入 `.header-actions`；社群 icon 移至 footer `.footer-social`）
   - 內頁 `page-hero has-photo` → **`has-banner`**（白底大標＋`container::after` 圓角照片橫幅；同時讓 V1 沉浸式 `:has` 透明 header 規則失效）
   - stats 帳本 → 圓角框卡；`.band` 滿版深照片 CTA → 淡紫扁平圓卡；`.closing` 深墨 → 淡面

mega 選單、搜尋層、抽屜、View Transitions 沿用 V1 行為（微互動待下一輪調整）。

## 內容區重排（2026-07-31，第一二波 36 頁）

與 V1 同步重排 36 頁（tiric×3、certification×2、certificate、mission/獎項×8、services×2、
benefit×2、membership 子頁×3、contact×2、news×13），內容標記與 V1 共用 snippet，
hero 轉 `has-banner`。另在 main.css 檔尾加「B＋ 內容區差異化層」，讓 V2 不再與 V1 同貌：

- **V1＝左欄 sticky＋hairline 編輯列；V2＝Notion 式堆疊區段＋扁平圓卡**
- page-split 改單欄堆疊（side 不再 sticky）；benefit-rows／step-list／services-list／
  fee-card／info-block／download-row 全改 `--soft` 淡面圓卡；roster 名單卡組名帶
  sticker 色籤（lilac/sky/mint 輪替）；event-item 改 hover 淡面圓卡；article-meta 改 pill 徽章
- 此層作用於全站共用 class，V2 原有 18 頁重設計頁（about/membership/knowledge…）同步變成卡片語言

## 自足部署（2026-08-03）

navbar/forms JS、favicon、原站圖檔與 PDF（`documents/`）全部收在資料夾內，
無任何 `../../` 外部引用——把 v2/ 內容直接放到網站根目錄即可獨立部署。

## 待辦（使用者驗收後）

- 細節微調與微互動（入場、hover、選單節奏）
- footer 舊紫 logo 圖檔（tiri-logo.png 仍為原紫）待決定是否重製
