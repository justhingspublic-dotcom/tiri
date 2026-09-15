"""Build second recheck with the user's completed first-recheck history intact."""
from pathlib import Path
import json,copy
OUT=Path(__file__).resolve().parent;prev=OUT.parent/'2026-09-10-v1-review-round1'
old=json.loads((prev/'複檢資料.json').read_text());raw=json.loads((OUT/'source/第一輪複檢結果原檔.json').read_text());submitted={x['id']:x for x in raw['items']}
fixes=json.loads((OUT/'第二輪修改對照.json').read_text());items=[]
for original in old['items']:
 item=copy.deepcopy(original);r=submitted[item['id']]
 item['reviewHistory']=[{'round':'第一輪驗收','sourceVersion':old['sourceVersion'],'exportedAt':old['sourceExportedAt'],'confirmed':item['firstReview'].get('confirmed',False),'note':item['firstReview'].get('note',''),'updatedAt':item['firstReview'].get('updatedAt'),'deliveredChange':item['deliveredChange'],'check':item['previousCheck'],'assistantExplanation':item.get('assistantExplanation','')},{'round':'第一輪複檢','sourceVersion':raw['version'],'exportedAt':raw['exportedAt'],'confirmed':r['confirmed'],'note':r.get('note',''),'confirmationSource':r.get('confirmationSource',''),'recheck':r.get('recheck'),'deliveryRevision':r.get('deliveryRevision',''),'deliveredChange':r.get('currentChange',''),'check':r.get('currentCheck',''),'deliveryLimit':r.get('deliveryLimit','')}]
 item['previousRecheck']={'confirmed':r['confirmed'],'note':r.get('note',''),'confirmationSource':r.get('confirmationSource',''),'recheck':r.get('recheck')}
 item['reviewStatus']='accepted' if r['confirmed'] else 'waiting' if item['deliveryStatus']=='waiting' else 'followup'
 item['deliveryStatus']='accepted' if r['confirmed'] else 'waiting' if item['reviewStatus']=='waiting' else 'pending'
 item['deliveryRevision']='20260910-r3-round2';item['assistantResponse']=''
 # Newly accepted fixes become history; no stale instructions to recheck the prior round.
 if r['confirmed']:
  item['currentChange']=r.get('currentChange') or item.get('deliveredChange','');item['currentCheck']='';item['deliveryLimit']='';item['partialApproval']=''
 if item['id'] in fixes:
  item.update(fixes[item['id']]);item['reviewStatus']='followup';item['deliveryStatus']=fixes[item['id']].get('deliveryStatus','ready')
  if 'deliveryLimit' not in fixes[item['id']]:item['deliveryLimit']=''
  item['partialApproval']=''
 # Dependencies can remain after acceptance of the available presentation.
 if item['id'] in ['08','32']:item['deliveryLimit']=r.get('deliveryLimit','')
 if item['id']=='19':item['dependency']='本項八大主題內容與版型已通過；這次第 05、08 張圖的更新請在 04 複檢。'
 if item['id']=='28':item['dependency']='講師照片尺寸已通過；這次淺色框與背景處理請在 27 複檢。'
 items.append(item)
data={'version':'tiri-v1-recheck-20260910-r2','round':2,'sourceVersion':raw['version'],'sourceExportedAt':raw['exportedAt'],'items':items}
(OUT/'複檢資料.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
encoded=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
(OUT/'第二輪複檢.html').write_text((OUT/'recheck.template.html').read_text().replace('__RECHECK_DATA__',encoded))
print({s:sum(i['deliveryStatus']==s for i in items) for s in ['accepted','ready','partial','waiting','pending']})
