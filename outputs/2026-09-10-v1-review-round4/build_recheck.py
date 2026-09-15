"""Carry all 41 items and four review histories into round four."""
from pathlib import Path
import json,copy
OUT=Path(__file__).resolve().parent;prev=OUT.parent/'2026-09-10-v1-review-round3'
old=json.loads((prev/'複檢資料.json').read_text())
raw=json.loads((OUT/'source/第三輪複檢結果原檔.json').read_text())
submitted={x['id']:x for x in raw['items']}
items=[]
for original in old['items']:
    item=copy.deepcopy(original);r=submitted[item['id']]
    item['reviewHistory'].append({'round':'第三輪複檢','sourceVersion':raw['version'],'exportedAt':raw['exportedAt'],
      'confirmed':r['confirmed'],'note':r.get('note',''),'confirmationSource':r.get('confirmationSource',''),
      'recheck':r.get('recheck'),'deliveryRevision':r.get('deliveryRevision',''),
      'deliveredChange':r.get('currentChange',''),'check':r.get('currentCheck',''),
      'deliveryLimit':r.get('deliveryLimit',''),'assistantResponse':r.get('assistantResponse',''),
      'currentFocus':r.get('currentFocus','')})
    item['previousRecheck']={'round':'第三輪複檢','confirmed':r['confirmed'],'note':r.get('note',''),
      'confirmationSource':r.get('confirmationSource',''),'recheck':r.get('recheck')}
    item['reviewStatus']='accepted' if r['confirmed'] else 'waiting' if original['deliveryStatus']=='waiting' else 'followup'
    item['deliveryStatus']='accepted' if r['confirmed'] else 'waiting' if item['reviewStatus']=='waiting' else 'ready'
    item['deliveryRevision']='20260910-r9-round4';item['assistantResponse']='';item['currentFocus']=''
    if r['confirmed']:
        item['currentChange']=r.get('currentChange') or item['deliveredChange']
        item['currentCheck']='';item['partialApproval']=''
    if item['id']=='10':
        item.update(currentFocus='內頁更多委員會：縮小的圖文卡片',route='committee-media.html#more-committees',
          currentChange='五個委員會內頁的「更多委員會」共 20 張卡片，改成與總覽相同的照片、名稱、簡介及入口文字。桌機每列 4 張，比總覽每列 3 張縮小；手機每列 2 張。圖片完整顯示，留邊補上同圖模糊底。',
          currentCheck='從下方連結打開「更多委員會」，確認每張都是圖片＋文字、比總覽小；逐張點入其他委員會，檢查各內頁同樣有另外 4 個圖文入口。',
          assistantResponse='已按這輪意見，將原本的文字卡片恢復為總覽同款圖文卡片，再縮小圖片、標題和間距。這次同圖重複是為了對應同一委員會入口；第三輪的 Banner 與原有名冊保留。',
          deliveryLimit='',partialApproval='')
    if item['id']=='11':item['dependency']='內頁名冊已通過；本輪保留原 Banner，「更多委員會」圖文入口請在 10 複檢。'
    if item['id']=='13':item['dependency']='列表版型與 Accupass 直連已通過；14 的近期活動亦已於第三輪通過，早期缺原圖事項繼續保留。'
    if item['id']=='19':item['dependency']='八大課程主題已通過；04 的授課特色圖片模糊背景也已於第三輪通過。'
    if item['id']=='26':item['dependency']='證照／獎項分類與證照主入口調整已完成，27 已於第三輪確認通過。'
    if item['id']=='28':item['dependency']='講師照片尺寸已通過；27 的照片模糊背景也已於第三輪通過。'
    if item['id']=='35':item['dependency']='文章配圖已通過；06 的全站情境圖片及模糊底也已於第三輪通過。'
    items.append(item)
confirmation_path=OUT/'source/第四輪對話確認.json'
if confirmation_path.exists():
    confirmation=json.loads(confirmation_path.read_text())
    item=next(i for i in items if i['id']==confirmation['id'])
    item['reviewHistory'].append({'round':'第四輪複檢（對話確認）','sourceVersion':'tiri-v1-recheck-20260910-r4',
      'confirmed':True,'note':confirmation['note'],'confirmationSource':'conversation',
      'updatedAt':confirmation['recordedAt'],'deliveredChange':item['currentChange'],
      'check':item['currentCheck'],'deliveryLimit':item['deliveryLimit'],
      'assistantResponse':confirmation['decision'],'deliveryRevision':item['deliveryRevision']})
    item.update(reviewStatus='accepted',deliveryStatus='accepted',currentCheck='',currentFocus='',
      confirmationSource='conversation',confirmedAt=confirmation['recordedAt'],assistantResponse=confirmation['decision'])
    next(i for i in items if i['id']=='11')['dependency']='委員會內頁名冊與第 10 項的圖文入口皆已通過；職能維持現有來源文字。'
material_path=OUT/'source/新增素材交付.json'
if material_path.exists():
    material=json.loads(material_path.read_text())
    item=next(i for i in items if i['id']==material['id'])
    item['reviewHistory'].append({'round':'第四輪補件需求','confirmed':False,'note':material['sourceNote'],
      'updatedAt':material['receivedAt'],'deliveredChange':'原列等資料，現已收到九張照片。',
      'assistantResponse':'依最新素材及對話指示製作拼接 Banner。'})
    item.update(material['updates'])
banner_confirmation_path=OUT/'source/Banner對話確認.json'
if banner_confirmation_path.exists():
    banner_confirmation=json.loads(banner_confirmation_path.read_text())
    item=next(i for i in items if i['id']==banner_confirmation['id'])
    item['reviewHistory'].append({'round':'第四輪複檢（Banner 對話確認）','sourceVersion':'tiri-v1-recheck-20260910-r4',
      'confirmed':True,'note':banner_confirmation['note'],'confirmationSource':'conversation',
      'updatedAt':banner_confirmation['recordedAt'],'deliveredChange':item['currentChange'],
      'check':item['currentCheck'],'deliveryLimit':item['deliveryLimit'],
      'assistantResponse':banner_confirmation['decision'],'deliveryRevision':item['deliveryRevision']})
    item.update(reviewStatus='accepted',deliveryStatus='accepted',currentCheck='',currentFocus='',
      confirmationSource='conversation',confirmedAt=banner_confirmation['recordedAt'],assistantResponse=banner_confirmation['decision'])
data={'version':'tiri-v1-recheck-20260910-r4','round':4,'sourceVersion':raw['version'],'sourceExportedAt':raw['exportedAt'],'items':items}
(OUT/'複檢資料.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
encoded=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
(OUT/'第四輪複檢.html').write_text((OUT/'recheck.template.html').read_text().replace('__RECHECK_DATA__',encoded))
item=next(i for i in items if i['id']=='10')
(OUT/'本輪修改紀錄.md').write_text('\n'.join([
 '# 第四輪修改紀錄','', '依 2026/9/10 13:37 匯出的第三輪結果更新。41 項保留：35 項已通過、1 項可複檢、5 項等資料。',
 '', '## 10｜內頁更多委員會', '', '你的第三輪留言：', '', '> '+item['previousRecheck']['note'], '', item['currentChange'],
 '', '請檢查：'+item['currentCheck'], '', '回覆：'+item['assistantResponse'],
 '', '## 先前完成紀錄', '', '第三輪的 04、06、07、14、27 已通過，連同此前 30 項，共 35 項預先勾選。',
 '', '17、20、23、25、41 仍等資料。08、14、32 的原素材保留事項仍記錄在對應卡片。',
 '', '每項完整保留第一輪驗收、第一輪複檢、第二輪複檢、第三輪複檢的留言、交付與回覆。','']) )
if confirmation_path.exists():
    report=OUT/'本輪修改紀錄.md'
    report.write_text(report.read_text().replace('35 項已通過、1 項可複檢、5 項等資料','36 項已通過、0 項待複檢、5 項等資料')+'\n## 第四輪對話確認\n\n使用者已在對話確認第 10 項通過。委員會職能維持現有文字，不另補寫。\n\n原話：'+confirmation['note']+'\n')
print({s:sum(i['deliveryStatus']==s for i in items) for s in ['accepted','ready','waiting']})
if material_path.exists():
    item=next(i for i in items if i['id']==material['id'])
    report=OUT/'本輪修改紀錄.md'
    report.write_text(report.read_text().replace('36 項已通過、0 項待複檢、5 項等資料','36 項已通過、1 項可複檢、4 項等資料').replace('17、20、23、25、41 仍等資料。','17、23、25、41 仍等資料；20 已收到照片並完成拼接，請複檢。').replace('\n請檢查：\n','\n狀態：已在對話中確認通過。\n')+'\n## 20｜新素材補件交付\n\n'+item['currentChange']+'\n\n請檢查：'+item['currentCheck']+'\n\n'+item['assistantResponse']+'\n')
if banner_confirmation_path.exists():
    report=OUT/'本輪修改紀錄.md'
    report.write_text(report.read_text().replace('36 項已通過、1 項可複檢、4 項等資料','37 項已通過、0 項待複檢、4 項等資料').replace('20 已收到照片並完成拼接，請複檢。','20 的九張拼接 Banner 已在對話確認通過。').replace('\n請檢查：\n','\n狀態：已在對話中確認通過。\n')+'\n## Banner 對話確認\n\n原話：'+banner_confirmation['note']+'\n\n'+banner_confirmation['decision']+'\n\n尚待項目與補件詳見 [剩餘待辦與補件](剩餘待辦與補件.md)。\n')
