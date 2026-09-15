from pathlib import Path
from bs4 import BeautifulSoup
from html import escape
import json
import shutil

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
SNAP=OUT/'source/before'
SNAP.mkdir(parents=True,exist_ok=True)
pages=['news-971146.html','news-971146-722067.html','bodperform.html','corpperform.html']
for name in pages:
    path=ROOT/'v1/html'/name
    backup=SNAP/name
    if not backup.exists():shutil.copy2(path,backup)
    soup=BeautifulSoup(backup.read_text(),'html.parser')
    if name.startswith('news-'):
        select=soup.select_one('#recap-year')
        label=soup.select_one('label[for="recap-year"]').get_text()
        options=select.select('option')
        choices=''.join(f'<li class="term-option" role="option" tabindex="-1" data-year="{o["value"]}" aria-selected="{str(o["value"]=="all").lower()}">{escape(o.get_text())}</li>' for o in options)
        field=BeautifulSoup(f'<div class="recap-year-field"><span id="recap-year-label" class="recap-year-label">{escape(label)}</span><div class="term-picker" data-recap-picker><button class="term-trigger" id="recap-year" type="button" value="all" aria-labelledby="recap-year-label recap-year-value" aria-haspopup="listbox" aria-expanded="false" aria-controls="recap-year-options"><span id="recap-year-value" data-recap-year-value>{escape(options[0].get_text())}</span><svg class="term-caret" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="m4 6 4 4 4-4" stroke="currentColor" stroke-width="1.5"/></svg></button><ul class="term-menu" role="listbox" aria-labelledby="recap-year-label" id="recap-year-options" hidden>{choices}</ul></div></div>','html.parser')
        select.parent.replace_with(field.div)
        soup.select_one('script[src*="round6.js"]')['src']='../js/recap-round7.js?v=20260914-r7'
    soup.head.append(soup.new_tag('link',rel='stylesheet',href='../css/round7.css?v=20260914-r7'))
    path.write_text(str(soup))
(OUT/'source/changed-pages.json').write_text(json.dumps(pages,indent=2))
print('Updated',len(pages),'pages')
