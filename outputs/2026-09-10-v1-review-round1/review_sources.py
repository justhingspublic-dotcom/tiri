"""Preserve round-one feedback and compare new source files without editing them."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
OLD = ROOT / 'outputs/2026-09-09-v1-revision'
SOURCE = OUT / 'source'
SOURCE.mkdir(exist_ok=True)

feedback = Path('/Users/jonathanyu/Downloads/TIRI-v1-驗收結果.json')
copy = SOURCE / feedback.name
if not copy.exists():
    shutil.copyfile(feedback, copy)
assert copy.read_bytes() == feedback.read_bytes()
before = SOURCE / 'checklist-before-round1.md'
if not before.exists():
    shutil.copyfile(ROOT / 'V1修改Checklist.md', before)

extractor = OLD / 'inventory_sources.py'
env = {'__file__': str(extractor)}
exec(compile(extractor.read_text().split('files = sorted(CLIENT')[0], str(extractor), 'exec'), env)
env['OUT'] = SOURCE
baseline = json.loads((OLD / 'source/all-workbooks.json').read_text())
changed = []

for index, old in enumerate(baseline, 1):
    path = ROOT.parent / old['file']
    if hashlib.sha256(path.read_bytes()).hexdigest() == old['sha256']:
        continue
    new = env['read_book'](path, index)
    previous = {sheet['name']: sheet for sheet in old['sheets']}
    current = {sheet['name']: sheet for sheet in new['sheets']}
    changes = []
    for name in dict.fromkeys([*previous, *current]):
        left, right = previous.get(name, {}), current.get(name, {})
        for field, key in [('cells', 'ref'), ('hyperlinks', 'ref')]:
            a = {v[key]: v for v in left.get(field, [])}
            b = {v[key]: v for v in right.get(field, [])}
            for ref in sorted(set(a) | set(b)):
                if a.get(ref) != b.get(ref):
                    changes.append({'sheet': name, 'field': field, 'ref': ref,
                                    'before': a.get(ref), 'after': b.get(ref)})
        for field in ['state', 'merged_ranges', 'images']:
            if left.get(field) != right.get(field):
                changes.append({'sheet': name, 'field': field, 'before': left.get(field), 'after': right.get(field)})
    media_changes = []
    old_media = {m['part']: m for m in old['media']}
    new_media = {m['part']: m for m in new['media']}
    for part in sorted(set(old_media) | set(new_media)):
        old_file = OLD / 'source' / old_media[part]['file'] if part in old_media else None
        new_file = SOURCE / new_media[part]['file'] if part in new_media else None
        a = hashlib.sha256(old_file.read_bytes()).hexdigest() if old_file and old_file.exists() else None
        b = hashlib.sha256(new_file.read_bytes()).hexdigest() if new_file and new_file.exists() else None
        if a != b:
            media_changes.append({'part': part, 'before_sha256': a, 'after_sha256': b})
    changed.append({'file': old['file'], 'before_sha256': old['sha256'], 'after_sha256': new['sha256'],
                    'changes': changes, 'media_changes': media_changes, 'current_workbook': new})

(SOURCE / 'workbook-changes.json').write_text(json.dumps(changed, ensure_ascii=False, indent=2))
logos = ROOT.parent / 'ref/官網/新官網-資料/文件/1首頁/合作夥伴LOGO'
logo_files = [{'file': str(p.relative_to(ROOT.parent)), 'bytes': p.stat().st_size,
               'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
              for p in sorted(logos.rglob('*')) if p.is_file() and not p.name.startswith('.')]
(SOURCE / 'logo-files.json').write_text(json.dumps(logo_files, ensure_ascii=False, indent=2))
print(json.dumps({'logo_files': len(logo_files), 'workbooks_with_hash_changes': len(changed),
                  'feedback_sha256': hashlib.sha256(feedback.read_bytes()).hexdigest()}, ensure_ascii=False))
for book in changed:
    print(json.dumps({k: v for k, v in book.items() if k != 'current_workbook'}, ensure_ascii=False))
