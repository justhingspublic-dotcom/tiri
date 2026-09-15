from revision_helpers import *

zh=read('board.html');en=read('board_en.html')
def people(panel):
    result=[]
    for name in panel.select('.name'):
        card=name.parent
        title=card.select_one('.title')
        role=card.select_one('.role')
        group=card.find_parent(class_='board-group')
        if not role:
            lead=card.find_parent(class_='board-lead')
            role=lead.select_one('.role') if lead else None
        role=role.get_text(' ',strip=True) if role else (group.h2.get_text(' ',strip=True) if group else '')
        result.append({'name':name.get_text(' ',strip=True),'title':title.get_text(' ',strip=True) if title else '', 'role':role})
    return result

portraits={}
for soup in [zh,en]:
    for name in soup.select('[data-term="2026"] .name'):
        card=name.parent;img=card.select_one('img') or card.parent.select_one('img')
        if img:portraits[name.get_text(' ',strip=True)]=img['src']

def split_zh(title,name):
    if name=='郭宗霖' and '鴻勝' in title:
        return [('鴻勝會計師事務所','執業會計師'),('大井泵浦工業股份有限公司','董事')]
    if name=='楊朝榮' and '聯茂' in title:
        return [('中華民國證券期貨分析協會','理事'),('聯茂、虎航、泰博等公司','獨立董事')]
    if name=='余凱文':return [('—',title)]
    if title in ['秘書長','前立法委員','']:return [('—',title or '—')]
    if ' ' in title:
        company,job=title.split(' ',1)
        if company=='TPK':
            if job.startswith('宸鴻光電科技股份有限公司 '):return [('TPK 宸鴻光電科技股份有限公司',job.split(' ',1)[1])]
            return [('TPK',job)]
        if company=='1919':return [('1919 食物銀行',job.replace('食物銀行 ','',1))]
        return [(company,job)]
    raise ValueError((name,title))

records=[]
for term in ['2022','2018']:
    zr=people(zh.select_one('[data-term="'+term+'"]'))
    er=people(en.select_one('[data-term="'+term+'"]'))
    assert len(zr)==len(er)
    for z,e in zip(zr,er):
        z['jobs']=split_zh(z['title'],z['name']);z['photo']=portraits.get(z['name'])
        # Fix a copied identity: the Chinese second-term source identifies Paul Yao,
        # while the old English page accidentally repeated first-term Jack Lu.
        if term=='2022' and z['name']=='姚文鈞':
            e['name']='Paul Yao';e['title']='FSP Technology Inc. — Special Assistant to the Chairman & Spokesman'
        if term=='2018' and z['name']=='烏恩婷':
            e['title']='瑞鼎科技 — Senior Project Manager'
        if term=='2018' and z['name']=='張妍婷':
            e['title']='Compal Electronics, Inc. — Deputy Director, Investor Relations'
        if z['name']=='郭宗霖' and term=='2022':e['jobs']=[('BigWin CPA Firm','Certified Public Accountant'),('Walrus Pump Co., Ltd.','Director')]
        elif ' — ' in e['title']:e['jobs']=[e['title'].split(' — ',1)]
        elif z['name']=='陳珮瑛':e['jobs']=[('Liming-ESG Corporation','Chief Sustainability Officer')]
        else:e['jobs']=[('—',e['title'] or '—')]
        e['photo']=z['photo']
        records.append({'term':term,'zh':z,'en':e})
    for soup,items,lang in [(zh,zr,'zh'),(en,er,'en')]:
        panel=soup.select_one('[data-term="'+term+'"]');panel.clear()
        note='歷屆任職資訊依該屆名冊呈現；人物照片使用已取得的同一人照片，非任期當年的拍攝紀錄。尚無個別照片者保留空位。' if lang=='zh' else 'Positions follow the historical roster. Available portraits identify the same person and may have been taken outside the term. Unavailable portraits are left blank.'
        panel.append(fragment('<p class="board-roster-note">'+note+'</p>'))
        headers=['照片','協會職務','姓名','公司名稱','公司職稱'] if lang=='zh' else ['Photo','TIRI Position','Name','Company','Company Title']
        rows=''
        for person in items:
            n=len(person['jobs']);photo=('<img class="member-portrait" src="'+person['photo']+'" alt="'+E(person['name'])+'" loading="lazy">') if person['photo'] else '<span class="portrait-missing" aria-label="'+('尚無照片' if lang=='zh' else 'No portrait available')+'">—</span>'
            for i,(company,title) in enumerate(person['jobs']):
                rows+='<tr>'
                if i==0:rows+=f'<td class="portrait-cell" rowspan="{n}">{photo}</td><td rowspan="{n}">{E(person["role"])}</td><th scope="row" class="member-name" rowspan="{n}">{E(person["name"])}</th>'
                rows+=f'<td class="member-company">{E(company)}</td><td>{E(title)}</td></tr>'
        panel.append(fragment('<div class="member-table-wrap" role="region" aria-label="'+term+(' 年理監事名冊' if lang=='zh' else ' board roster')+'" tabindex="0"><table class="member-table"><thead><tr>'+''.join('<th scope="col">'+h+'</th>' for h in headers)+'</tr></thead><tbody>'+rows+'</tbody></table></div>'))
put('board.html',zh);put('board_en.html',en)
(OUT/'source/board-rosters.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('Historical rosters written; missing portraits:',sorted(set(r['zh']['name'] for r in records if not r['zh']['photo'])))

# Correct the library's existing mislinked titles using the local source catalogues.
s=BS((HTML/'knowledge.html').read_text(),'html.parser')
def norm(text):return re.sub(r'[\s\u200b，,：:？?\-—_～~（）()「」©－─！!]', '',text).lower()
catalog={}
for name in ['news-387131.html','irupdatestc.html']:
    source=read(name)
    for a in source.select('main a[href]'):
        catalog[norm(a.get_text(' ',strip=True))]=a['href']
log=[]
for card in s.select('.insight-card'):
    title=card.h3.get_text(' ',strip=True);key=norm(title)
    if '專訪創會理事長沈馥馥' in title:target='2356035370-277843933339333297022010738263.html'
    else:
        matches=[v for k,v in catalog.items() if key in k]
        assert len(set(matches))==1,(title,matches)
        target=matches[0]
    before=card.get('href');card['href']=target
    if target.startswith('http') or '.pdf' in target:card['target']='_blank';card['rel']='noopener'
    if '霹靂' in title:
        # The title names a company, not an interviewee; avoid implying an identity.
        img=card.select_one('img');img['src']='../images/revision/A04-capital-market.jpg';img['alt']='資本市場與企業價值';img['class']=['article-thumb']
    log.append({'title':title,'old_href':before,'href':target,'image':card.img['src']})
put('knowledge.html',s)
(OUT/'source/article-link-audit.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))
print('Verified article destinations:',len(log))
