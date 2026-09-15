"""Apply the six second-recheck notes to v1; keep original photos intact."""
from pathlib import Path
from bs4 import BeautifulSoup
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
HTML=ROOT/'v1/html'
changes=[]

for path in HTML.glob('*.html'):
    original=path.read_text()
    soup=BeautifulSoup(original,'html.parser')
    changed=False
    if path.name=='about.html':
        section=soup.select_one('#regulatory-engagement')
        if section:
            for sibling in list(section.find_next_siblings()): sibling.decompose()
            section.decompose()
            changed=True
    for img in soup.select('img.scene-portrait-safe,img.scene-full-frame,.photo-story>img'):
        if 'blurred-photo' in img.parent.get('class',[]): continue
        parent_classes=img.parent.get('class',[])
        kind='story-photo' if 'photo-story' in parent_classes else 'benefit-photo' if 'benefit-overview' in parent_classes else 'article-photo' if 'insight-card' in parent_classes else 'feature-photo' if img.find_parent(class_='inhouse-features') else 'card-photo'
        frame=soup.new_tag('div',attrs={'class':['blurred-photo',kind],'style':f'--scene-image:url("{img["src"]}")'})
        img.wrap(frame)
        changed=True
    for frame in soup.select('.lecturer-photo-frame'):
        img=frame.img
        frame['class']=list(dict.fromkeys(frame.get('class',[])+['blurred-photo']))
        frame['style']=f'--scene-image:url("{img["src"]}")'
        if 'white-backdrop-blend' in img.get('class',[]):
            img['class']=[c for c in img['class'] if c!='white-backdrop-blend']
        changed=True
    if changed:
        path.write_text(str(soup))
        changes.append(path.name)

overview=BeautifulSoup((HTML/'committee.html').read_text(),'html.parser')
committee_banners=[]
for card in overview.select('.revision-card'):
    img=card.select_one('img'); route=card.get('href')
    if not route or not img: continue
    path=HTML/route
    soup=BeautifulSoup(path.read_text(),'html.parser')
    hero=soup.select_one('.page-hero')
    hero['class']=['page-hero','has-photo','committee-banner']
    hero['style']=f'--scene-image:url("{img["src"]}")'
    if not hero.select_one('.committee-banner-image'):
        photo=soup.new_tag('img',attrs={'class':'committee-banner-image','src':img['src'],'alt':img.get('alt',''),'fetchpriority':'high'})
        for attr in ['width','height']:
            if attr in img: photo[attr]=img[attr]
        hero.insert(0,photo)
    path.write_text(str(soup)); changes.append(path.name)
    committee_banners.append({'page':route,'image':img['src']})

css=ROOT/'v1/css/review-fixes.css'
marker='/* Third recheck: same-image blurred backdrops, complete foreground photos. */'
rules='''
.blurred-photo{position:relative;display:block;isolation:isolate;overflow:hidden;background:#f0edf1;width:100%;min-width:0}
.blurred-photo::before,.committee-banner::before{content:"";position:absolute;inset:-22px;background-image:var(--scene-image);background-size:cover;background-position:center;filter:blur(18px);pointer-events:none;z-index:0}
.blurred-photo>img{position:relative;z-index:1;display:block;width:100%!important;height:100%!important;max-width:100%;margin:0!important;aspect-ratio:auto!important;object-fit:contain!important;object-position:center!important;background:transparent!important;mix-blend-mode:normal}
.story-photo,.benefit-photo{aspect-ratio:4/3}
.feature-photo,.card-photo{aspect-ratio:3/2}
.feature-photo{margin-bottom:24px}
.article-photo{height:200px;margin-bottom:20px}
.lecturer-photo-frame.blurred-photo{width:140px;height:168px}
.lecturer-photo-frame.blurred-photo::before{filter:blur(12px);inset:-15px}
.page-hero.committee-banner{isolation:isolate;overflow:hidden;background:#272331}
.committee-banner::after{content:"";position:absolute;inset:0;z-index:2;background:linear-gradient(180deg,rgba(23,20,31,.4),rgba(23,20,31,.18) 38%,rgba(23,20,31,.84));pointer-events:none}
.committee-banner-image{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;object-position:center;z-index:1}
.committee-banner>.container{position:relative;z-index:3}
@media(max-width:640px){.lecturer-photo-frame.blurred-photo{width:120px;height:145px}.benefit-photo{aspect-ratio:3/2}}
'''
text=css.read_text()
if marker not in text: css.write_text(text+'\n'+marker+'\n'+rules)

for path in HTML.glob('*.html'):
    text=path.read_text()
    text=text.replace('20260910-r7','20260910-r8')
    path.write_text(text)
(OUT/'source/修改頁面.json').write_text(json.dumps({'pages':changes,'committeeBanners':committee_banners},ensure_ascii=False,indent=2))
print('Updated',len(changes),'content pages and bumped shared asset versions.')
