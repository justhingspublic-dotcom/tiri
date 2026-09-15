from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
data = json.loads((OUT / 'source/本輪交付資料.json').read_text())
(OUT / '複檢資料.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
encoded = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
(OUT / '第五輪複檢.html').write_text((OUT / 'recheck.template.html').read_text().replace('__RECHECK_DATA__', encoded))
print({s: sum(i['deliveryStatus'] == s for i in data['items']) for s in ['accepted', 'ready', 'waiting']})
