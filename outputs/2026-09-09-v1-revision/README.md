# TIRI v1｜2026-09-09 驗收版 r1

1. 雙擊 **開啟驗收.command**，會重用或啟動本機 4173 預覽並開啟驗收頁。
2. 從「可驗收」查看 33 個整項與 3 個部分完成項目。可自行勾選、留意見及匯出 JSON。
3. 工作追蹤仍以專案根目錄 `V1修改Checklist.md` 為準；瀏覽器勾選不會自動改寫 Markdown。

- 本輪改動在 `WEB DEMO/v1`，本機預覽已可用；沒有部署到線上測試站。
- 實作、自測、原始資料與缺件分別見 Checklist、QA報告.md、Excel分頁盤點.md、圖片選用表.md。
- 可執行的檢查：`validate_revision.py`；預覽啟動器：`launch_review.py`。
- `implement_*.py`、`build_acceptance.py` 等是這一批從舊快照產出初版的工作紀錄，後續還有人工修正。不要當成日常增量建置重跑，否則會覆蓋後續修改與驗收紀錄。
- 原始 HTML 快照保存在 `source`，副檔名為 `.html.txt`。不是待部署檔案。
