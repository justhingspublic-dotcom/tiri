from pathlib import Path
from bs4 import BeautifulSoup
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
for name in ['trainbod.html','trainbod-329824.html']:
    p=ROOT/'v1/html'/name;soup=BeautifulSoup(p.read_text(),'html.parser')
    hero=soup.select_one('.page-hero');hero['id']='training-banner'
    hero['class']=list(dict.fromkeys(hero['class']+['training-collage-hero']))
    hero['style']='--hero-img:url("../images/review-r5/board-training-collage-nine.png")'
    if not hero.select_one('.training-collage-image'):
        img=soup.new_tag('img',attrs={'class':'training-collage-image','src':'../images/review-r5/board-training-collage-nine.png','alt':'董監事進修與協會活動的九張實拍照片拼接' if name=='trainbod.html' else 'Nine-photo collage of director education and TIRI events','width':'1774','height':'887','fetchpriority':'high','decoding':'async'})
        hero.insert(0,img)
    link=soup.select_one('link[href*="review-fixes.css"]');link['href']='../css/review-fixes.css?v=20260910-r10-banner'
    p.write_text(str(soup))
css=ROOT/'v1/css/review-fixes.css'
marker='/* Director education: keep all nine photos visible, including on phones. */'
rules='''
.page-hero.training-collage-hero{isolation:isolate;overflow:hidden;background:#211b29}
.training-collage-hero::before{content:"";position:absolute;inset:-28px;background-image:var(--hero-img);background-size:cover;background-position:center;filter:blur(24px);opacity:.6;z-index:0;pointer-events:none}
.training-collage-image{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;object-position:center;z-index:1}
.training-collage-hero::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(23,20,31,.48),rgba(23,20,31,.1) 40%,rgba(23,20,31,.84));z-index:2;pointer-events:none}
.training-collage-hero>.container{position:relative;z-index:3}
@media(max-width:640px){body:has(.training-collage-hero) .page-hero.training-collage-hero{min-height:520px}.training-collage-image{object-position:center 42%}.training-collage-hero::after{background:linear-gradient(180deg,rgba(23,20,31,.55),rgba(23,20,31,.05) 34%,rgba(23,20,31,.9) 80%)} }
'''
text=css.read_text()
if marker not in text:css.write_text(text+'\n'+marker+'\n'+rules)
print('Applied nine-photo banner to Chinese and English director education pages.')
