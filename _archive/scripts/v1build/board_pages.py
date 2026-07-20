#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V1 建置第 4 步（在 relink.py 之後跑）：
以設計版名冊頁覆寫 convert_pages.py 產出的 team*.html，
並建立 board.html / board_en.html、接上全站導覽與頁尾入口。
資料一律取自原站各屆頁面，不跨屆補寫、不臆造頭銜。"""
import re, pathlib, html as H

ROOT = pathlib.Path(__file__).resolve()
HTML = pathlib.Path("/Users/jonathanyu/Desktop/Travail/投資人協會 TIRI/WEB DEMO/v1/html")

# ---------------------------------------------------------------- 資料
# (姓名, 職稱)；職稱為 "" 代表原始資料未提供公司職稱，不臆造。
# also 欄位標記兼任，避免理事長/副理事長在常務理事重複出現時看似錯誤。

ZH = {
 2026: dict(
  term="第三屆", ordinal="Third", date="2026 年 3 月 20 日",
  honorary=("孫又文", "前台灣積體電路製造股份有限公司 企業訊息處資深處長"),
  chair=("郭宗霖", "鴻勝會計師事務所執業會計師暨大井泵浦工業股份有限公司董事"),
  vice=[("王恩國","南昌菱光科技有限公司董事長、今皓實業股份有限公司獨立董事"),
        ("簡世雄","東元電機股份有限公司 公司治理中心處長暨發言人"),
        ("張明仁","新加坡商睿智先鋒有限公司 財務長")],
  exec_dir=[("郭宗霖","鴻勝會計師事務所執業會計師暨大井泵浦工業股份有限公司董事","兼理事長"),
            ("王恩國","南昌菱光科技有限公司董事長、今皓實業股份有限公司獨立董事","兼副理事長"),
            ("簡世雄","東元電機股份有限公司 公司治理中心處長暨發言人","兼副理事長"),
            ("張明仁","新加坡商睿智先鋒有限公司 財務長","兼副理事長"),
            ("黃奕誠","鴻海精密股份有限公司 投資人關係暨永續委員會經理","")],
  dirs=[("沈馥馥","中華電信股份有限公司 前財務處副總暨代理發言人"),
        ("張妍婷","仁寶電腦工業股份有限公司 投資人關係暨品牌辦公室資深處長、代理發言人"),
        ("張真卿","立隆電子工業股份有限公司 董事長特助暨發言人"),
        ("姚文鈞","全漢企業股份有限公司 董事長特別助理暨發言人"),
        ("許碧雲","桓達科技股份有限公司 總經理特助暨發言人"),
        ("黃英記","矽創電子股份有限公司 投資人關係暨永續辦公室處長"),
        ("林男和","旗山龍鳳食品股份有限公司 總經理"),
        ("洪健凱","經寶精密控股股份有限公司 投資人關係部經理"),
        ("趙元祥","群聯電子股份有限公司 董事長特助"),
        ("張登溪","大井泵浦工業股份有限公司 財務長")],
  exec_sup=[("涂蕙蘭","")],
  sups=[("萬心寧","圓裕企業股份有限公司 獨立董事"),
        ("陳珮瑛","永創數智股份有限公司 資深顧問"),
        ("葉文燦","宇峻奧汀科技股份有限公司 管理處協理暨發言人"),
        ("鄭可人","佳能企業 投資人關係經理暨永續發展暨風險管理執行委員會委員")],
  hon_adv=[("楊朝榮","中華民國證券期貨分析協會理事及聯茂、虎航、泰博等公司獨立董事"),
           ("周德雲","矽創電子股份有限公司 前策略投資顧問"),
           ("劉詩亮","TPK 宸鴻光電科技股份有限公司 資深副總經理策略長暨代理發言人"),
           ("王沈銘","1919 食物銀行 特約顧問")],
  chief_adv=[("余凱文","自 2004 年以來台灣投資人關係的推動者和革新者")],
  sec=[("許育綾","秘書長")],
  portrait="board-sun-2026.jpg", group=None, scenes=[],
 ),
 2022: dict(
  term="第二屆", ordinal="Second", date="2022 年 7 月 8 日",
  honorary=("孫又文","前台灣積體電路製造股份有限公司 企業訊息處資深處長"),
  chair=("郭宗霖","鴻勝會計師事務所執業會計師暨大井泵浦工業股份有限公司董事"),
  vice=[("王恩國","東友科技股份有限公司 副董事長")],
  exec_dir=[("郭宗霖","鴻勝會計師事務所執業會計師暨大井泵浦工業股份有限公司董事","兼理事長"),
            ("王恩國","東友科技股份有限公司 副董事長","兼副理事長"),
            ("劉詩亮","TPK 宸鴻光電科技股份有限公司 資深副總經理 策略長暨代理發言人",""),
            ("簡世雄","東元電機股份有限公司 公司治理中心處長暨發言人",""),
            ("張明仁","新加坡商睿智先鋒有限公司 財務長","")],
  dirs=[("沈馥馥","中華電信股份有限公司 前財務處副總暨代理發言人"),
        ("張妍婷","仁寶電腦工業股份有限公司 投資人關係暨品牌辦公室資深處長、代理發言人"),
        ("張真卿","立隆電子工業股份有限公司 董事長特助暨發言人"),
        ("黃奕誠","鴻海精密股份有限公司 投資人關係暨永續委員會經理"),
        ("許碧雲","桓達科技股份有限公司 總經理特助暨發言人"),
        ("黃英記","矽創電子 投資人關係暨永續辦公室處長"),
        ("林男和","旗山龍鳳食品股份有限公司 總經理"),
        ("洪健凱","經寶精密控股股份有限公司 投資人關係部經理"),
        ("藍世旻","安格科技股份有限公司 總經理"),
        ("王沈銘","1919 食物銀行 特約顧問")],
  exec_sup=[("涂蕙蘭","")],
  sups=[("萬心寧","圓裕企業股份有限公司 獨立董事"),
        ("姚文鈞","全漢企業股份有限公司 董事長特別助理暨發言人"),
        ("陳珮瑛","力銘永續發展股份有限公司 永續長"),
        ("葉文燦","宇峻奧汀科技股份有限公司 管理處協理暨發言人")],
  hon_adv=[("楊朝榮","中華民國證券期貨分析協會理事及聯茂、虎航、泰博等公司獨立董事"),
           ("周德雲","矽創電子股份有限公司 前策略投資顧問")],
  chief_adv=[("余凱文","自 2004 年以來台灣投資人關係的推動者和革新者")],
  sec=[("許育綾","秘書長")],
  portrait="board-sun-2022.jpg", group="board-group-2022.jpg", scenes=[],
 ),
 2018: dict(
  term="第一屆", ordinal="First", date="2018 年 5 月 30 日",
  honorary=("孫又文","台灣積體電路製造股份有限公司 企業訊息處資深處長"),
  chair=("沈馥馥","中華電信 公共事務處協理暨代理發言人"),
  vice=[("郭宗霖","霹靂國際 財務長暨代理發言人")],
  exec_dir=[("沈馥馥","中華電信 公共事務處協理暨代理發言人","兼理事長"),
            ("郭宗霖","霹靂國際 財務長暨代理發言人","兼副理事長"),
            ("劉詩亮","TPK 資深副總經理 策略長暨代理發言人",""),
            ("周德雲","矽創電子 資深處長暨發言人",""),
            ("張明仁","新源生物科技 財務副總","")],
  dirs=[("呂軍甫","京鼎精密 發言人"),
        ("張真卿","立隆電子 董事長特助暨發言人"),
        ("簡世雄","東元電機 公司治理中心處長暨發言人"),
        ("藍世旻","安格科技 總經理暨發言人"),
        ("許碧雲","桓達科技 總經理特助暨發言人"),
        ("黃英記","矽創電子 投資人關係暨永續發展資深經理"),
        ("林男和","全球創新技術產業交流協會 理事長"),
        ("烏恩婷","瑞鼎科技 資深專案經理"),
        ("張妍婷","仁寶電腦 投資人關係部 副處長")],
  exec_sup=[("洪健凱","經寶精密 投資人關係經理")],
  sups=[("萬心寧","台驊國際 總經理暨發言人"),
        ("呂政達","威強電 前財務長暨發言人"),
        ("涂蕙蘭","精英電腦(股) 資深經理暨代理發言人"),
        ("徐美華","雅茗天地 投資人關係高級經理暨代理發言人")],
  hon_adv=[("余宛如","前立法委員"),
           ("楊朝榮","中華民國證券分析協會 常務理事及研究發展委員會召集人")],
  chief_adv=[("余凱文","自 2004 年以來台灣投資人關係的推動者和革新者")],
  sec=[("邱榮振","秘書長")],
  portrait="board-sun-2018.jpg", group="board-group-2018.jpg",
  scenes=["board-scene-2018a.jpg","board-scene-2018b.jpg"],
 ),
}

EN = {
 2026: dict(
  term="Third Board", ordinal="Third", date="20 March 2026",
  honorary=("Elizabeth Sun","TSMC — Senior Director of Corporate Communications Division"),
  chair=("Jonny Kuo","Certified Public Accountant at BigWin CPA Firm; Director at Walrus Pump Co., Ltd."),
  vice=[("Kevin Wang","Nanchang Creative Sensor Technology Co., Ltd. — Chairman; Ji-Haw Industrial Co., Ltd. — Independent Director"),
        ("Andy Chien","TECO Electric & Machinery Co., Ltd. — Spokesman & Director of Corporate Governance Center"),
        ("Jack M. Chang","TURBONEXT.AI — CFO")],
  exec_dir=[("Jonny Kuo","CPA, CSIA at BigWin CPA Firm; Director of Walrus Pump Co., Ltd.","also Chairman"),
            ("Kevin Wang","Nanchang Creative Sensor Technology Co., Ltd. — Chairman","also Vice Chairman"),
            ("Andy Chien","TECO Electric & Machinery Co., Ltd. — Spokesman & Director of Corporate Governance Center","also Vice Chairman"),
            ("Jack M. Chang","TURBONEXT.AI — CFO","also Vice Chairman"),
            ("Nick Huang","Hon Hai Precision Industry Co., Ltd. — Manager of Investor Relations, Head of the Sustainability Committee Office","")],
  dirs=[("FuFu Shen","Chunghwa Telecom Co., Ltd. — Former VP of Finance Department & Deputy Spokesperson"),
        ("Tina Chang","Compal Electronics, Inc. — Senior Director, Investor Relations & Branding Office, Deputy Spokesperson"),
        ("Peter Chang","Lelon Electronics Corp. — Spokesman & Assistant to the President"),
        ("Paul Yao","FSP Group — Special Assistant to the Chairman & Spokesman"),
        ("Nancy Hsu","FineTek Co., Ltd. — Special Assistant to the Managing Director & Spokesperson"),
        ("Tom Huang","Sitronix Technology Corp. — Investor Relations and ESG Office Director"),
        ("Nan-Hao Lin","Chi Shan Long Feng Food Co., Ltd. — General Manager"),
        ("Cash Hong","JPP Holding Company Limited — Investor Relations Specialist"),
        ("Vincent Jhao","Phison Electronics Corporation — CEO Special Assistant"),
        ("Allround Chang","Walrus Pump Co., Ltd. — Chief Financial Officer")],
  exec_sup=[("Emily Tu","")],
  sups=[("Echo Wan","Complex Micro Interconnection Co., Ltd. — Independent Director"),
        ("Julia Chen","Vital Collaboration Co., Ltd. — Senior Consultant"),
        ("Paul W.T. Yeh","Userjoy Technology Co., Ltd. — Management Office Associate and Spokesperson"),
        ("KC Cheng","Ability Enterprise Co., Ltd. — IR Manager & Member of Sustainability/Risk Committee")],
  hon_adv=[("David Yang","Securities Analysts Association, Chinese Taipei — Director; Independent Director of ITEQ, Tigerair Taiwan and TaiDoc"),
           ("Jacky Chou","Sitronix Technology Corporation — Former Strategic Investment Advisor"),
           ("Freddie Liu","TPK Holding Co., Ltd. — Chief Strategy Officer and Deputy Spokesman"),
           ("Frank Wang","1919 Food Bank — Special Consultant")],
  chief_adv=[("Kevin Yu","Promoter and innovator of investor relations in Taiwan since 2004")],
  sec=[("Judy Hsu","Secretary General")],
  portrait="board-sun-2026.jpg", group=None, scenes=[],
 ),
 2022: dict(
  term="Second Board", ordinal="Second", date="8 July 2022",
  honorary=("Elizabeth Sun","TSMC — Senior Director of Corporate Communications Division"),
  chair=("Jonny Kuo","Certified Public Accountant at BigWin CPA Firm; Director at Walrus Pump Co., Ltd."),
  vice=[("Kevin Wang","TECO Image Systems Co., Ltd. — Vice Chairman")],
  exec_dir=[("Jonny Kuo","CPA, CSIA at BigWin CPA Firm; Director of Walrus Pump Co., Ltd.","also Chairman"),
            ("Kevin Wang","TECO Image Systems Co., Ltd. — Vice Chairman","also Vice Chairman"),
            ("Freddie Liu","TPK Holding Co., Ltd. — Chief Strategy Officer and Deputy Spokesman",""),
            ("Andy Chien","TECO Electric & Machinery Co., Ltd. — Spokesman & Director of Corporate Governance Center",""),
            ("Jack M. Chang","TURBONEXT.AI — CFO","")],
  dirs=[("Fu-Fu Shen","Chunghwa Telecom Co., Ltd. — Former Deputy Spokesperson & VP of Public Affairs Department"),
        ("Tina Chang","Compal Electronics, Inc. — Senior Director, Investor Relations & Branding Office, Deputy Spokesperson"),
        ("Peter Chang","Lelon Electronics Corp. — Spokesman & Assistant to the President"),
        ("Nick Huang","Hon Hai Precision Industry Co., Ltd. — Manager of Investor Relations, Head of the Sustainability Committee Office"),
        ("Nancy Hsu","FineTek Co., Ltd. — Special Assistant to the Managing Director & Spokesperson"),
        ("Tom Huang","Sitronix Technology Corp. — Investor Relations and ESG Office Director"),
        ("Nan-Hao Lin","Chi Shan Long Feng Food Co., Ltd. — General Manager"),
        ("Cash Hong","JPP Holding Company Limited — Investor Relations Specialist"),
        ("Ant Lan","ALGOLTEK, Inc. — General Manager"),
        ("Frank Wang","1919 Food Bank — Special Consultant")],
  exec_sup=[("Emily Tu","")],
  sups=[("Echo Wan","Complex Micro Interconnection Co., Ltd. — Independent Director"),
        ("Jack Lu","IEI Integration Corp. — Former CFO & Spokesman"),
        ("Julia Chen","Liming-ESG Corporation"),
        ("Paul W.T. Yeh","Userjoy Technology Co., Ltd. — Management Office Associate and Spokesperson")],
  hon_adv=[("David Yang","Securities Analysts Association, Chinese Taipei — Director; Independent Director of ITEQ, Tigerair Taiwan and TaiDoc"),
           ("Jacky Chou","Sitronix Technology Corporation — Former Strategic Investment Advisor")],
  chief_adv=[("Kevin Yu","Promoter and innovator of investor relations in Taiwan since 2004")],
  sec=[("Judy Hsu","Secretary General")],
  portrait="board-sun-2022.jpg", group="board-group-2022.jpg", scenes=[],
 ),
 2018: dict(
  term="First Board", ordinal="First", date="30 May 2018",
  honorary=("Elizabeth Sun","TSMC — Senior Director of Corporate Communications Division"),
  chair=("Fu-Fu Shen","Chunghwa Telecom Co., Ltd. — Deputy Spokesperson & Assistant VP of Public Affairs Department"),
  vice=[("Jonny Kuo","Pili International Multimedia Co., Ltd. — Deputy Spokesman & CFO")],
  exec_dir=[("Fu-Fu Shen","Chunghwa Telecom Co., Ltd. — Deputy Spokesperson & Assistant VP of Public Affairs Department","also Chairman"),
            ("Jonny Kuo","Pili International Multimedia Co., Ltd. — Deputy Spokesman & CFO","also Vice Chairman"),
            ("Freddie Liu","TPK Holding Co., Ltd. — Chief Strategy Officer and Deputy Spokesman",""),
            ("Jacky Chou","Sitronix Technology Corporation — Spokesman & Senior Director",""),
            ("Jack M. Chang","Allgenesis Biotherapeutics Inc. — Vice President of Finance","")],
  dirs=[("Stanley Lu","Foxsemicon Integrated Technology Inc. — Spokesman"),
        ("Peter Chang","Lelon Electronics Corp. — Spokesman & Assistant to the President"),
        ("Andy Chien","TECO Electric & Machinery Co., Ltd. — Deputy Spokesman & Deputy Director of Corporate Governance Center"),
        ("Ant Lan","ALGOLTEK, Inc. — General Manager & Spokesman"),
        ("Nancy Hsu","FineTek Co., Ltd. — Special Assistant to the Managing Director & Spokesperson"),
        ("Tom Huang","Sitronix Technology Corporation — Senior Manager of IR & Sustainability"),
        ("Nan-Hao Lin","Cross Straits New Technology Association — Chairman"),
        ("Entien Wu","Good Way Technology Co., Ltd. — Spokesperson"),
        ("Tina Chang","Compal Electronics, Inc. — Investor Relations, Director")],
  exec_sup=[("Cash Hong","JPP Holding Company Limited — Investor Relations Specialist")],
  sups=[("Echo Wan","T3EX Global Holdings Corp. — General Manager and Spokesperson"),
        ("Jack Lu","IEI Integration Corp. — Former CFO & Spokesman"),
        ("Emily Tu","Elitegroup Computer Systems — Deputy Spokesman & Senior Manager"),
        ("Selina Hsu","Yummy Town (Cayman) Holdings Corporation — Senior Manager of Investor Relations & Deputy Spokesperson")],
  hon_adv=[("Wan-ju Yu","Former Legislator"),
           ("David Yang","Securities Analysts Association — Executive Director")],
  chief_adv=[("Kevin Yu","Promoter and innovator of investor relations in Taiwan since 2004")],
  sec=[("Jonathan","Secretary General")],
  portrait="board-sun-2018.jpg", group="board-group-2018.jpg",
  scenes=["board-scene-2018a.jpg","board-scene-2018b.jpg"],
 ),
}

L = {
 "zh": dict(eyebrow="About TIRI", suffix="理監事成員", hon="榮譽理事長", chair="理事長",
   vice="副理事長", ed="常務理事", d="理事", es="常務監事", s="監事",
   ha="榮譽顧問", ca="首席顧問", sec="秘書處",
   elected="本會於 {d} 召開會員大會選出{t}理、監事。",
   groupcap="{t}理監事合影。", scenecap="{t}會員大會現場。",
   idx_t="歷屆理監事", idx_lede="協會自 2018 年成立以來的三屆理監事名冊。",
   members="{n} 位理監事", nophoto="本屆合影待補。",
   site="台灣投資人關係協會 TIRI"),
 "en": dict(eyebrow="About TIRI", suffix="", hon="Honorary Chairman", chair="Chairman",
   vice="Vice Chairman", ed="Executive Directors", d="Directors", es="Executive Supervisor",
   s="Supervisors", ha="Honorary Advisors", ca="Chief Advisor", sec="Secretariat",
   elected="Elected at the general meeting held on {d}.",
   groupcap="{t} — group photograph.", scenecap="{t} — general meeting.",
   idx_t="Board Archive", idx_lede="The three boards elected since TIRI was founded in 2018.",
   members="{n} members", nophoto="Group photograph pending.",
   site="Taiwan Investor Relations Institute"),
}

def esc(s): return H.escape(s, quote=False)

def people(items, has_also=False):
    out = ['<ul class="board-people" data-reveal-group>']
    for it in items:
        name, title = it[0], it[1]
        also = it[2] if has_also and len(it) > 2 else ""
        row = ['<li class="reveal">']
        if also: row.append(f'<span class="also">{esc(also)}</span>')
        row.append(f'<p class="name">{esc(name)}</p>')
        if title: row.append(f'<p class="title">{esc(title)}</p>')
        row.append('</li>')
        out.append("".join(row))
    out.append('</ul>')
    return "\n        ".join(out)

def group(label, body):
    return f'''      <section class="board-group">
        <h2 class="reveal">{esc(label)}</h2>
        {body}
      </section>'''

def build_main(lang, year):
    d = (ZH if lang == "zh" else EN)[year]
    t = L[lang]
    term = d["term"]
    title = f'{term}{t["suffix"]}' if lang == "zh" else f'{term} of Directors'
    parts = []

    # hero
    parts.append(f'''  <section class="page-hero has-photo" style="--hero-img: url('../images/hero-taipei-night.jpg')">
    <div class="container">
      <p class="eyebrow">{t["eyebrow"]}</p>
      <h1>{esc(title)}</h1>
      <p class="lede">{esc(t["elected"].format(d=d["date"], t=term))}</p>
    </div>
  </section>''')

    body = []
    # 首長 spotlight
    hn, ht = d["honorary"]
    body.append(f'''      <div class="board-lead reveal">
        <figure><img src="../images/{d["portrait"]}" alt="{esc(hn)}" width="272" height="408" loading="lazy"></figure>
        <div>
          <p class="role">{esc(t["hon"])}</p>
          <p class="name">{esc(hn)}</p>
          <p class="title">{esc(ht)}</p>
        </div>
      </div>''')
    cn, ct = d["chair"]
    body.append(f'''      <div class="board-lead no-photo reveal">
        <div>
          <p class="role">{esc(t["chair"])}</p>
          <p class="name">{esc(cn)}</p>
          <p class="title">{esc(ct)}</p>
        </div>
      </div>''')

    body.append(group(t["vice"], people(d["vice"])))
    body.append(group(t["ed"], people(d["exec_dir"], has_also=True)))
    body.append(group(t["d"], people(d["dirs"])))
    body.append(group(t["es"], people(d["exec_sup"])))
    body.append(group(t["s"], people(d["sups"])))
    body.append(group(t["ha"], people(d["hon_adv"])))
    body.append(group(t["ca"], people(d["chief_adv"])))
    body.append(group(t["sec"], people(d["sec"])))

    if d["group"]:
        body.append(f'''      <figure class="board-figure reveal">
        <img src="../images/{d["group"]}" alt="{esc(t["groupcap"].format(t=term))}" width="617" height="412" loading="lazy">
        <figcaption>{esc(t["groupcap"].format(t=term))}</figcaption>
      </figure>''')
    if d["scenes"]:
        imgs = "\n        ".join(
            f'<img src="../images/{s}" alt="{esc(t["scenecap"].format(t=term))}" width="560" height="420" loading="lazy">'
            for s in d["scenes"])
        body.append(f'''      <figure class="board-figure is-set reveal">
        {imgs}
      </figure>''')

    parts.append(f'''
  <section class="page-section">
    <div class="container">
{chr(10).join(body)}
    </div>
  </section>''')
    return "\n".join(parts), title

MAIN_RE = re.compile(r'(<main id="main">).*?(</main>)', re.S)

def splice(path, main_html, title, desc):
    p = HTML / path
    s = p.read_text(encoding="utf-8")
    s = MAIN_RE.sub(lambda m: m.group(1) + "\n" + main_html + "\n" + m.group(2), s, count=1)
    s = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content=".*?">',
               f'<meta name="description" content="{esc(desc)}">', s, count=1, flags=re.S)
    # 這些頁不再有 Weebly 遺留標記，移除 legacy CSS 相依
    s = s.replace('<link rel="stylesheet" href="../css/legacy-inline.css">\n', '')
    s = s.replace('<link rel="stylesheet" href="../css/legacy-content.css">\n', '')
    p.write_text(s, encoding="utf-8")
    return p

files = []
for lang, pre in (("zh", "team{y}.html"), ("en", "team_en-{y}.html")):
    for y in (2026, 2022, 2018):
        m, title = build_main(lang, y)
        full = f'{title}｜{L[lang]["site"]}' if lang == "zh" else f'{title} | {L[lang]["site"]}'
        desc = (f'{title}名單──台灣投資人關係協會。' if lang == "zh"
                else f'{title} of the Taiwan Investor Relations Institute.')
        files.append(splice(pre.format(y=y), m, full, desc))

print("\n".join(str(f.name) for f in files))


# ============================ 索引頁與導覽列 ============================



TERMS = [
    dict(y=2026, term="第三屆", en="Third Board", chair="郭宗霖",
         chair_en="Jonny Kuo",
         title="鴻勝會計師事務所執業會計師暨大井泵浦工業股份有限公司董事",
         title_en="Certified Public Accountant at BigWin CPA Firm; Director at Walrus Pump Co., Ltd.",
         date="2026.03.20", n=25, n_en=25),
    dict(y=2022, term="第二屆", en="Second Board", chair="郭宗霖",
         chair_en="Jonny Kuo",
         title="鴻勝會計師事務所執業會計師暨大井泵浦工業股份有限公司董事",
         title_en="Certified Public Accountant at BigWin CPA Firm; Director at Walrus Pump Co., Ltd.",
         date="2022.07.08", n=22, n_en=22),
    dict(y=2018, term="第一屆", en="First Board", chair="沈馥馥",
         chair_en="Fu-Fu Shen",
         title="中華電信 公共事務處協理暨代理發言人",
         title_en="Chunghwa Telecom Co., Ltd. — Deputy Spokesperson & Assistant VP of Public Affairs Department",
         date="2018.05.30", n=23, n_en=23),
]


def build(lang):
    zh = lang == "zh"
    rows = []
    for t in TERMS:
        href = f'team{t["y"]}.html' if zh else f'team_en-{t["y"]}.html'
        term = t["term"] if zh else t["en"]
        chair = t["chair"] if zh else t["chair_en"]
        title = t["title"] if zh else t["title_en"]
        role = "理事長" if zh else "Chairman"
        meta = f'{t["date"]} 選任・{t["n"]} 位理監事' if zh else f'Elected {t["date"]} · {t["n_en"]} members'
        rows.append(f'''        <li class="reveal">
          <a href="{href}">
            <span class="term">{term}</span>
            <span class="who">{chair}<span>{role}・{title}</span></span>
            <span class="meta">{meta}</span>
          </a>
        </li>''')
    heading = "歷屆理監事" if zh else "Board Archive"
    lede = ("協會自 2018 年成立以來，每四年由會員大會選出理、監事。以下為歷屆名冊。"
            if zh else
            "TIRI’s members elect a board every four years. The full rosters are archived below.")
    body = "\n".join(rows)
    return f'''  <section class="page-hero has-photo" style="--hero-img: url('../images/hero-taipei-night.jpg')">
    <div class="container">
      <p class="eyebrow">About TIRI</p>
      <h1>{heading}</h1>
      <p class="lede">{lede}</p>
    </div>
  </section>

  <section class="page-section">
    <div class="container">
      <ul class="board-terms" data-reveal-group>
{body}
      </ul>
    </div>
  </section>''', heading


for lang, src, out in (("zh", "team2026.html", "board.html"),
                       ("en", "team_en-2026.html", "board_en.html")):
    main, heading = build(lang)
    s = (HTML / src).read_text(encoding="utf-8")
    s = MAIN_RE.sub(lambda m: m.group(1) + "\n" + main + "\n" + m.group(2), s, count=1)
    site = "台灣投資人關係協會 TIRI" if lang == "zh" else "Taiwan Investor Relations Institute"
    sep = "｜" if lang == "zh" else " | "
    s = re.sub(r'<title>.*?</title>', f'<title>{heading}{sep}{site}</title>', s, count=1, flags=re.S)
    desc = ("台灣投資人關係協會歷屆理監事名冊：第一屆至第三屆。" if lang == "zh"
            else "Archive of the boards of the Taiwan Investor Relations Institute.")
    s = re.sub(r'<meta name="description" content=".*?">',
               f'<meta name="description" content="{desc}">', s, count=1, flags=re.S)
    (HTML / out).write_text(s, encoding="utf-8")
    print("built", out)

# ---------------------------------------------------------------- 導覽列／頁尾
MEGA_OLD = ('<a class="mega-item" href="about.html#team"><span class="t">第三屆理監事成員</span>'
            '<span class="d">現任理監事名單</span></a>')
MEGA_NEW = ('<a class="mega-item" href="team2026.html"><span class="t">第三屆理監事成員</span>'
            '<span class="d">現任理監事名單</span></a>\n'
            '                <a class="mega-item" href="board.html"><span class="t">歷屆理監事</span>'
            '<span class="d">第一屆至第三屆名冊</span></a>')

FOOT_OLD = '<li><a href="about.html#team">第三屆理監事成員</a></li>'
FOOT_NEW = ('<li><a href="team2026.html">第三屆理監事成員</a></li>\n'
            '          <li><a href="board.html">歷屆理監事</a></li>')

SUBS_OLD = '<a href="about.html#team">第三屆理監事成員</a>'
SUBS_NEW = ('<a href="team2026.html">第三屆理監事成員</a>\n'
            '            <a href="board.html">歷屆理監事</a>')

changed = 0
for p in sorted(HTML.glob("*.html")):
    s = orig = p.read_text(encoding="utf-8")
    s = s.replace(MEGA_OLD, MEGA_NEW)
    s = s.replace(FOOT_OLD, FOOT_NEW)      # 先做較長的頁尾樣式
    s = s.replace(SUBS_OLD, SUBS_NEW)      # 再做行動版子選單
    if s != orig:
        p.write_text(s, encoding="utf-8")
        changed += 1
print("nav updated:", changed, "files")
print("remaining about.html#team refs:",
      sum(p.read_text(encoding="utf-8").count("about.html#team") for p in HTML.glob("*.html")))
