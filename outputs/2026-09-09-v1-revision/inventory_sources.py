"""Read every worksheet and embedded image in the relevant client workbooks.

Source files are never modified. Credentials workbooks are outside the selected
website content directories and are not inspected.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import posixpath
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
CLIENT = ROOT.parent / 'ref/官網/新官網-資料/文件'
OUT = Path(__file__).resolve().parent / 'source'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'p': 'http://schemas.openxmlformats.org/package/2006/relationships',
      'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}

def rels(z, part):
    rp = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part) + '.rels')
    if rp not in z.namelist():
        return {}
    return {n.get('Id'): dict(n.attrib) for n in ET.fromstring(z.read(rp))}

def resolve(part, target):
    return posixpath.normpath(posixpath.join(posixpath.dirname(part), target)).lstrip('/')

def read_book(path, index):
    book = {'file': str(path.relative_to(ROOT.parent)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'sheets': [], 'media': []}
    with ZipFile(path) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(si.itertext()) for si in []]
            strings = [''.join(n.text or '' for n in si.findall('.//m:t', NS))
                       for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        wb = ET.fromstring(z.read('xl/workbook.xml'))
        wr = rels(z, 'xl/workbook.xml')
        media_map = {}
        for name in z.namelist():
            if name.startswith('xl/media/') and not name.endswith('/'):
                dest = OUT / 'workbook-media' / f'{index:02d}' / Path(name).name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(z.read(name))
                media_map[name] = str(dest.relative_to(OUT))
                book['media'].append({'part': name, 'file': media_map[name]})
        for sh in wb.findall('m:sheets/m:sheet', NS):
            part = resolve('xl/workbook.xml', wr[sh.get('{'+NS['r']+'}id')]['Target'])
            xml = ET.fromstring(z.read(part))
            sr = rels(z, part)
            sheet = {'name': sh.get('name'), 'state': sh.get('state', 'visible'), 'cells': [],
                     'merged_ranges': [x.get('ref') for x in xml.findall('m:mergeCells/m:mergeCell', NS)],
                     'hyperlinks': [], 'images': []}
            for c in xml.findall('.//m:sheetData/m:row/m:c', NS):
                value = c.findtext('m:v', default='', namespaces=NS)
                if c.get('t') == 's' and value:
                    value = strings[int(value)]
                elif c.get('t') == 'inlineStr':
                    value = ''.join(t.text or '' for t in c.findall('.//m:t', NS))
                formula = c.findtext('m:f', default='', namespaces=NS)
                if value or formula:
                    cell = {'ref': c.get('r'), 'value': value}
                    if formula: cell['formula'] = formula
                    sheet['cells'].append(cell)
            for h in xml.findall('m:hyperlinks/m:hyperlink', NS):
                rid = h.get('{'+NS['r']+'}id')
                sheet['hyperlinks'].append({'ref': h.get('ref'), 'target': sr.get(rid, {}).get('Target', h.get('location', ''))})
            for d in xml.findall('m:drawing', NS):
                dp = resolve(part, sr[d.get('{'+NS['r']+'}id')]['Target'])
                dr = rels(z, dp)
                for anchor in ET.fromstring(z.read(dp)):
                    for blip in anchor.findall('.//a:blip', NS):
                        rid = blip.get('{'+NS['r']+'}embed')
                        if rid not in dr: continue
                        ip = resolve(dp, dr[rid]['Target'])
                        sheet['images'].append({'file': media_map.get(ip, ip),
                            'row_1based': int(anchor.findtext('xdr:from/xdr:row', default='0', namespaces=NS))+1,
                            'col_1based': int(anchor.findtext('xdr:from/xdr:col', default='0', namespaces=NS))+1})
            book['sheets'].append(sheet)
    return book

files = sorted(CLIENT.rglob('*.xlsx')) + [ROOT / '2理監事成員/理監事成員.xlsx']
books = [read_book(p, i) for i, p in enumerate(files, 1)]
(OUT / 'all-workbooks.json').write_text(json.dumps(books, ensure_ascii=False, indent=2))
lines = ['# 本機 Excel 分頁盤點', '', '2026-09-09。僅讀取網站內容資料；保留原檔。所有分頁（含隱藏狀態）、儲存格、連結、合併範圍與嵌入圖片已抽取；逐項採用與核對另記於實作紀錄。', '',
         '| 檔案 | 分頁 | 狀態 | 非空儲存格 | 超連結 | 圖片 |', '|---|---|---|---:|---:|---:|']
for b in books:
    for s in b['sheets']:
        lines.append(f"| {b['file']} | {s['name']} | {s['state']} | {len(s['cells'])} | {len(s['hyperlinks'])} | {len(s['images'])} |")
(OUT.parent / 'Excel分頁盤點.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'books':len(books),'sheets':sum(len(b['sheets']) for b in books),
                  'embedded_images':sum(len(b['media']) for b in books)}, ensure_ascii=False))
for b in books:
    print(Path(b['file']).name, ' / '.join(f"{s['name']}({len(s['cells'])} cells, {len(s['images'])} images)" for s in b['sheets']))
