"""Build the recheck website from the recorded review; never rewrite its sources."""
from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
old = json.loads((OUT.parent / '2026-09-09-v1-revision/驗收資料.json').read_text())
routes = {item['id']: item for item in old}
review = json.loads((OUT / '第一輪驗收整理.json').read_text())
explanations = {
    '08': '我的理解是保留第三屆照片卡片，把任職資訊拆成「公司名稱」和「職稱」，兼任者每家公司各一組。例如郭宗霖：鴻勝會計師事務所／執業會計師；大井泵浦工業股份有限公司／董事。協會的「理事長」職務另外顯示。第一、二屆維持你已確認的表格。',
    '14': '原本「近期活動」和「活動訊息」有兩個入口；上一輪將列表統一到「活動訊息」，舊入口會轉到同一頁，可依年份查看，再進 Accupass 或活動文章。這項不包含 17 的活動花絮新排版。你指出的缺圖確實存在：153 筆中有 19 筆沒配圖，包含 4 筆缺 Accupass 原 Banner、3 筆有內頁但沒配圖、12 筆沒有目的頁卻顯示花絮箭頭。這些都已列入修正。上一輪的「0 缺檔」檢查未涵蓋未配圖和無目的頁的情況。',
    '39': '目前右側文字一區約 268 字、另一區約 897 字，固定大小的左圖就會留下高度落差。建議標題移到圖片上方，再調整圖文比例；較長的合作夥伴優惠整理成分組卡片或雙欄清單，保留全部條件及連結，讓整區比例自然。',
    '29': '你的最新確認是「白底影片 OK，但是播放前沒有圖片」。影片本身已通過；這次只新增播放前封面的檢查，完成封面後再勾選本項。30 的屆次下拉已整項通過，另保留在已完成項目中。',
}
fixes = json.loads((OUT.parent / '2026-09-10-v1-fixes/本輪交付.json').read_text())
items = []
for item in review['items']:
    entry = routes[item['id']]
    route = 'board.html?term=2026' if item['id'] == '08' else entry['route']
    items.append({
        'id': item['id'], 'title': item['title'], 'route': route,
        'reviewStatus': item['reviewStatus'],
        'deliveryStatus': 'waiting' if item['reviewStatus'] == 'waiting' else 'pending' if item['reviewStatus'] == 'followup' else 'accepted',
        'deliveryRevision': '20260910-intake',
        'deliveredChange': entry['change'],
        'previousCheck': entry['note'],
        'nextAction': (item.get('nextAction') or '').replace('名称', '名稱'),
        'assistantExplanation': explanations.get(item['id'], ''),
        'dependency': item.get('dependencies') or '',
        'partialApproval': review['partially_accepted'].get(item['id'], ''),
        'firstReview': {k: item[k] for k in ['confirmed', 'note', 'updatedAt'] if k in item},
    })
for item in items:
    if item['id'] in fixes:
        item.update(fixes[item['id']])
        item['deliveryStatus'] = 'ready'
        item['deliveryRevision'] = '20260910-r2-actual'

data = {'version': 'tiri-v1-recheck-20260910-r1', 'sourceVersion': review['source_version'],
        'sourceExportedAt': review['exportedAt'], 'items': items}
(OUT / '複檢資料.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
encoded = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
template = (OUT / 'recheck.template.html').read_text()
(OUT / '第一輪複檢.html').write_text(template.replace('__RECHECK_DATA__', encoded))
print(f'Built 第一輪複檢.html with {len(items)} items.')
