from pathlib import Path
from bs4 import BeautifulSoup as B
from urllib.parse import urlsplit,unquote
from collections import defaultdict
import json,re,hashlib,pymupdf,subprocess
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent; SRC=OUT/'source'; HTML=ROOT/'v1/html'
usage=defaultdict(set)
for p in HTML.glob('*.html'):
 s=B(p.read_text(),'html.parser')
 for i in s.select('img[src]'):
  src=i['src']
  if src.startswith('../images/'):usage[src].add(p.name)
 for src in re.findall(r'url\([\'"]?(\.\./images/[^\)\'\"]+)',p.read_text()):usage[src].add(p.name)
for src in re.findall(r'"(\.\./images/[^\"]+)"',(ROOT/'v1/js/navbar.js').read_text()):usage[src].add('共用導覽')
stock=json.loads((OUT/'圖片來源紀錄.json').read_text());records=[]
mirrors={
 'A01':'https://www.sienkiewicz-kancelaria.com.pl/wp-content/uploads/2016/07/JONMP7TPGK-2-scaled.jpg',
 'A02':'https://www.sienkiewicz-kancelaria.com.pl/wp-content/uploads/2015/12/Y2GUBQIPXD-1-scaled.jpg'}
for r in stock:
 web='../images/revision/'+r['id']+'-'+r['key']+'.jpg';path=HTML/web;pm=pymupdf.Pixmap(str(path));r.update({'website_file':str(path.resolve().relative_to(ROOT)),'website_dimensions':[pm.width,pm.height],'website_bytes':path.stat().st_size,'used_pages':sorted(usage[web]),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 if r['id'] in mirrors:
  original=SRC/(r['id']+'-original-2560.jpg');q=pymupdf.Pixmap(str(original));r['saved_source']=str(original.relative_to(OUT));r['saved_source_dimensions']=[q.width,q.height];r['download_url']=mirrors[r['id']];r['download_status']='已保存同圖 2560px 來源檔，視覺比對與 StockSnap 圖片一致；CC0 依據為 StockSnap 作者作品頁，下載位置為公開鏡像。'
 else:
  r['saved_source']=r['preview'];r['saved_source_dimensions']=[960,640];r['download_status']='目前保存 960px 檔，已用於實際卡片／側圖並核對顯示；未取回平台列示的最高解析度。不可用作大幅印刷或全寬 Banner 原稿。'
 records.append(r)
(OUT/'圖片來源紀錄.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
for r in json.loads((SRC/'additional-photos.json').read_text()):
 web='../images/revision/'+r['name']+'.jpg'
 if web not in usage:continue
 path=HTML/web;pm=pymupdf.Pixmap(str(path));orig=SRC/(r['name']+'-original.jpg');q=pymupdf.Pixmap(str(orig))
 records.append({'id':r['name'].split('-')[0],'title':{'B02-security':'網路線與資訊基礎設施','B03-solar':'屋頂太陽能與再生能源','B04-building':'企業玻璃大樓','B06-contract':'契約文件與責任承諾'}[r['name']],'author':'PxHere 作品頁未列名','source_url':r['source'],'license':'CC0 1.0','license_url':'https://creativecommons.org/publicdomain/zero/1.0/','verified_on':'2026-09-09','saved_source':str(orig.relative_to(OUT)),'saved_source_dimensions':[q.width,q.height],'website_file':str(path.resolve().relative_to(ROOT)),'website_dimensions':[pm.width,pm.height],'website_bytes':path.stat().st_size,'used_pages':sorted(usage[web]),'download_url':r['original_url'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(OUT/'正式圖片使用紀錄.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
stockby={str((ROOT/r['website_file']).resolve()):r for r in records};inventory=[]
for web,pages in sorted(usage.items()):
 path=(HTML/web).resolve();r=stockby.get(str(path));kind='本案既有素材；本輪未重新認定為 CC0'
 if r:kind='本輪選用 CC0 情境圖'
 elif '/images/events/' in web:kind='TIRI 原活動頁 Banner；對應 Accupass 來源，不屬於 CC0 圖庫'
 elif '/images/annual/' in web:kind='本案年刊 PDF 首頁封面，不屬於 CC0 圖庫'
 item={'file':str(path.relative_to(ROOT)),'pages':sorted(pages),'type':kind,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 if r:item['source']=r['source_url']
 if web=='../images/seminar-room.jpg':item['source']='本案 original/html/news-121049.html；19/5/30 雙主題講座；與 original/images/uploads-1-1-9-9-119925991-589604-res_1_orig-7d16d70.jpg 位元相同。原圖 https://www.tiri.tw/uploads/1/1/9/9/119925991/589604-res_1_orig.jpg'
 inventory.append(item)
(OUT/'全站圖片盤點.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2))
lines=['# 本輪正式圖片選用表','', '更新：2026-09-09。下列圖片已套用 v1；來源、保存尺寸、網站尺寸及 SHA-256 詳見 [正式圖片使用紀錄](正式圖片使用紀錄.json)。CC0 圖片與協會既有素材分別記錄，不把客戶照片、人物照片、活動 Banner、年刊封面宣稱為 CC0。','', 'A01、A02 已取得同圖的 2560px 公開鏡像並比對；授權仍以 StockSnap 作者作品頁為準。A03–A09 目前使用 960px 檔，限本輪卡片／側圖，不宣稱已取得平台最高解析度；全寬新 Banner 使用 1920px 網站檔。','', '| ID | 主題／作者 | 實際網站尺寸 | 使用頁面 | 來源與授權 |','|---|---|---|---|---|']
for r in records:
 dims=' × '.join(map(str,r['website_dimensions']));pages='、'.join('共用導覽' if p=='共用導覽' else p for p in r['used_pages'])
 lines.append(f'| {r["id"]} | {r["title"]}／{r["author"]} | {dims} | {pages} | [作品頁]({r["source_url"]}) · [CC0]({r["license_url"]}) |')
lines+=['','## 本案內容圖片','', '- 授課情境使用本案既有「2019/5/30 雙主題講座」實拍，已比對原站封存檔；沒有把 TIRIC 授證海報裁成教室照。','- TIRI Awards 與潛力進展獎使用指定獎座／獎狀照片；第一屆進展獎頒獎照來自既有 2025 Awards 資料。','- 人物專訪只用可確認的沈馥馥、郭宗霖、劉詩亮照片；未以同名或未確認人物替代。第一、二屆 7 位成員照片仍缺件。','- 活動：131 個 Accupass 來源中取得 127 個原 Banner；4 個舊來源無 Banner。其餘歷史紀錄保留原文章／活動入口。','- 年刊：2023–2025 中英文 6 本 PDF 直接產生封面，封面完整顯示。','', '## 對照與範圍','', '- [27 篇文章配圖／連結對照](source/article-image-map.json)','- [全站圖片盤點（含既有保留圖片）](全站圖片盤點.json)','- [Accupass Banner 取得紀錄](source/event-banner-map.json)','- [六本年刊封面及 PDF 對照](source/yearbook-covers.json)','- 未取得的最高解析度、既有素材授權、缺件照片均依以上記錄，不視為新 CC0 原稿。']
(OUT/'圖片選用表.md').write_text('\n'.join(lines)+'\n')
# Visual proof sheet for the six original PDF cover extractions.
doc=pymupdf.open();page=doc.new_page(width=960,height=920)
for n,r in enumerate(json.loads((SRC/'yearbook-covers.json').read_text())):
 col=n%3;row=n//3;x=col*320+20;y=row*455+25
 page.insert_text((x,y),r['year']+' '+r['lang'].upper()+' | '+str(r['pages'])+' pages',fontsize=14)
 page.insert_image(pymupdf.Rect(x,y+15,x+280,y+405),filename=str((HTML/r['cover']).resolve()),keep_proportion=True)
doc.save(SRC/'six-yearbook-covers.pdf');page.get_pixmap().save(SRC/'six-yearbook-covers.png')
print('CC0 files:',len(records),'all referenced image files:',len(inventory))
