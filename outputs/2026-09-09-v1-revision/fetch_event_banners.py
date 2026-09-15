from revision_helpers import *
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor,as_completed

cache=OUT/'source/event-pages';cache.mkdir(exist_ok=True)
images=ROOT/'v1/images/events';images.mkdir(exist_ok=True)
sources={'https://www.accupass.com/event/2608261303411628089416':'2026.10.16 2026 年度大會暨 IR 新溝通時代'}
for name in ['news.html','events.html','trainbod.html','index.html']:
    s=read(name)
    for a in s.select('main a[href*="accupass.com/event/"]'):
        sources[a['href'].split('?')[0]]=a.get_text(' ',strip=True)

def fetch(url,title):
    eid=url.rsplit('/',1)[-1];path=cache/(eid+'.json')
    if path.exists():
        old=json.loads(path.read_text())
        if old.get('ok'):return old
    result={'url':url,'local_label':title,'id':eid}
    try:
        data=urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=15).read()
        soup=BS(data,'html.parser');meta=soup.select_one('meta[property="og:image"]');name=soup.select_one('meta[property="og:title"]')
        assert meta and '/eventbanner/' in meta['content'],'No event banner'
        result.update(source_title=name['content'] if name else '',image_url=meta['content'])
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                obj=json.loads(script.string or script.get_text());result.setdefault('structured',[]).append(obj)
            except ValueError:pass
        original=cache/(eid+'.jpg')
        if not original.exists():original.write_bytes(urlopen(Request(meta['content'],headers={'User-Agent':'Mozilla/5.0'}),timeout=15).read())
        dest=images/(eid+'.jpg')
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(original),'-vf',"scale='min(1000,iw)':-2",'-q:v','3','-frames:v','1',str(dest)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        result.update(ok=True,image='../images/events/'+dest.name)
    except Exception as e:result.update(ok=False,error=str(e))
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2));return result

results=[]
with ThreadPoolExecutor(max_workers=5) as pool:
    futures=[pool.submit(fetch,u,t) for u,t in sources.items()]
    for f in as_completed(futures):
        result=f.result();results.append(result)
        print(result['id'],result['ok'],flush=True)
(OUT/'source/event-banner-map.json').write_text(json.dumps(sorted(results,key=lambda r:r['id']),ensure_ascii=False,indent=2))
print('COMPLETE',len(results),'OK',sum(r['ok'] for r in results),flush=True)
