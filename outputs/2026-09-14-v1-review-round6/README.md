# TIRI v1 第六輪複檢

雙擊「開啟複檢.command」，或在瀏覽器開啟：

http://localhost:4173/outputs/2026-09-14-v1-review-round6/第六輪複檢.html

原有 39 項通過＋本輪 6 項待複檢＝45 項。可勾選、留言、自動儲存、匯出 JSON；換瀏覽器請用匯出／匯入。測試網址加 `?test=1` 可使用獨立 sessionStorage，正式紀錄不受影響。

建置：以具 bs4 的 Python 執行 `../2026-09-14-v1-round6/apply_round6.py`、`../2026-09-14-v1-round6/build_delivery.py`，最後執行本目錄 `build_recheck.py`。網頁內容與複檢來源分開保留，建置不寫入任何使用者驗收勾選。
