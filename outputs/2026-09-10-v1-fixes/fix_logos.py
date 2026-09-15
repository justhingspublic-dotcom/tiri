from pathlib import Path
from bs4 import BeautifulSoup as B
from html import escape as E
import pymupdf as f,json,shutil
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
ref=ROOT.parent/'ref/官網/新官網-資料/文件/1首頁/合作夥伴LOGO'; assets=ROOT/'v1/images/review-r2/logos'
def find(pattern):return next(ref.rglob(pattern))
# Supplied brand sheets contain multiple variants; render only the chosen logo's PDF region.
specs=[('mz','13.MZ LOGO.png',None),('writepath','雲翻譯-LOGO.png',None),('notified','10.Notified Logo.ai',None),('mpinfo','倍力logo.ai',None),('businessweekly','3.商周-LOGO.ai',(174,320,439,472)),('hubhotel','旅居文旅LOGO.ps',(110,58,328,126)),('hi','Hi家教-LOGO.png',None),('discovered','logo.png',None),('interinfo','英特內_logo.ai',(132,185,410,266)),('pwc','6.資誠 LOGO.psd',None),('kpmg','*RGB*左右.ai',None),('ey','8.EY安永 LOGO.pdf',(178,222,282,325)),('theicons','12.Theicons logo.ai',(8,112,125,230))]
logs=[]
for slug,pattern,box in specs:
 source=find(pattern);d=f.open(source);p=d[0];clip=f.Rect(box) if box else p.rect
 if not box and source.suffix.lower()=='.ai':
  rects=[f.Rect(b) for typ,b in p.get_bboxlog() if f.Rect(b).intersects(p.rect)]
  if rects:
   clip=f.Rect(rects[0])
   for rect in rects[1:]:clip|=rect
   clip=(clip+(-4,-4,4,4))&p.rect
 pix=p.get_pixmap(matrix=f.Matrix(900/clip.width,900/clip.width),clip=clip,alpha=False);dest=assets/(slug+'.png');pix.save(dest)
 logs.append({'brand':slug,'source':str(source.relative_to(ROOT.parent)),'file':str(dest.relative_to(ROOT)),'clip':list(clip),'license':'客戶提供的品牌素材，限本專案展示；非 CC0'})
(OUT/'Logo套用紀錄.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2))
keys=['mz','writepath',None,'notified','mpinfo','businessweekly','hubhotel','hi','discovered','interinfo']
for name in ['index.html','partners.html']:
 p=ROOT/'v1/html'/name;s=B(p.read_text(),'html.parser');grid=s.select_one('.partner-names');grid['class']=['partner-logo-grid']
 for a,slug in zip(grid.select('a'),keys):
  label=a.get_text(' ',strip=True).replace('↗','').strip();a.clear()
  if slug:a.append(B(f'<img src="../images/review-r2/logos/{slug}.png" alt="{E(label)} Logo" loading="lazy">','html.parser').img)
  else:a.append(B(f'<strong class="partner-wordmark">{E(label)}</strong>','html.parser').strong)
  a.append(B(f'<span>{E(label)} <span aria-hidden="true">↗</span></span>','html.parser').span)
 for slug,label in [('pwc','PwC 資誠'),('kpmg','KPMG 安侯建業'),('ey','EY 安永'),('theicons','The Icons')]:
  grid.append(B(f'<div class="partner-logo-item"><img src="../images/review-r2/logos/{slug}.png" alt="{label} Logo" loading="lazy"><span>{label}</span></div>','html.parser').div)
 p.write_text(str(s))
print('13 supplied brand logos applied to homepage and partners; existing 10 benefit links preserved.')
