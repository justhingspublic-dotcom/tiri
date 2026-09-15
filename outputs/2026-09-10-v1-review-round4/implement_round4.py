"""Use the overview's original images and copy in smaller related-committee cards."""
from pathlib import Path
from bs4 import BeautifulSoup
import copy,json
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[1]; HTML=ROOT/'v1/html'
overview=BeautifulSoup((HTML/'committee.html').read_text(),'html.parser')
cards={card['href']:card for card in overview.select('.revision-cards > .revision-card')}
changes=[]
for route in cards:
    path=HTML/route;soup=BeautifulSoup(path.read_text(),'html.parser')
    more=soup.select_one('.committee-more');more['id']='more-committees'
    grid=more.select_one('.revision-cards');grid.clear()
    for target,original in cards.items():
        if target==route:continue
        card=copy.deepcopy(original)
        img=card.select_one('img')
        if 'blurred-photo' not in img.parent.get('class',[]):
            frame=soup.new_tag('div',attrs={'class':['blurred-photo','card-photo'],'style':f'--scene-image:url("{img["src"]}")'})
            img.wrap(frame)
        grid.append(card)
        changes.append({'page':route,'target':target,'image':img['src']})
    path.write_text(str(soup))
css=ROOT/'v1/css/review-fixes.css'
marker='/* Fourth recheck: smaller image-and-text related committee cards. */'
rules='''
.committee-more .revision-cards{grid-template-columns:repeat(4,minmax(0,1fr));gap:24px}
.committee-more .revision-card{padding:0 0 20px;background:transparent;border-top:0;border-bottom:1px solid var(--line)}
.committee-more .revision-card>.blurred-photo{padding:0;aspect-ratio:3/2}
.committee-more .revision-card>div:not(.blurred-photo){padding-top:16px}
.committee-more .revision-card h3{font-size:20px;margin:8px 0;line-height:1.45}
.committee-more .revision-card p{font-size:14px;line-height:1.75}
.committee-more .revision-card .eyebrow{font-size:11px;line-height:1.6}
.committee-more .revision-card:focus-visible{outline:2px solid var(--purple);outline-offset:5px}
@media(max-width:960px){.committee-more .revision-cards{grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}}
@media(max-width:640px){.committee-more{margin-top:48px}.committee-more .revision-cards{gap:24px 16px}.committee-more .revision-card h3{font-size:18px}.committee-more .revision-card>div:not(.blurred-photo){padding-top:12px}.committee-more .revision-card .eyebrow{min-height:3.2em}}
'''
text=css.read_text()
if marker not in text:css.write_text(text+'\n'+marker+'\n'+rules)
# A new CSS URL ensures prior review tabs also load the actual latest styles.
for path in HTML.glob('*.html'):
    text=path.read_text()
    path.write_text(text.replace('review-fixes.css?v=20260910-r8','review-fixes.css?v=20260910-r9'))
(OUT/'source/修改頁面與圖片對照.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2))
print('Updated 20 related committee cards across five detail pages.')
