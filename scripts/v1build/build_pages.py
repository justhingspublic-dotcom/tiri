#!/usr/bin/env python3
"""Generate V1 inner pages with a shared shell."""
import pathlib

OUT = pathlib.Path("/Users/jonathanyu/Desktop/Travail/投資人協會 TIRI/WEB DEMO/v1/html")

NAV = [
    ("about.html", "關於 TIRI", "about", [
        ("about.html", "協會使命"),
        ("about.html#team", "第三屆理監事成員"),
        ("about.html#committee", "功能委員會"),
        ("services.html", "功能與服務"),
        ("certificate.html", "鄧白氏企業認證™"),
    ]),
    ("events.html", "活動課程", "events", [
        ("events.html", "焦點與近期課程"),
        ("news-971146.html", "精彩回顧"),
        ("tiric.html", "TIRIC IR 專業實戰班"),
        ("trainbod.html", "董監事進修課程"),
        ("certification.html", "IRC 國際證照"),
        ("scholarshipirc.html", "IRC 贊助獎學金"),
        ("mission-206783.html", "TIRI Awards"),
        ("mission-206783-766399.html", "TIRI 潛力進展獎"),
    ]),
    ("knowledge.html", "知識資源", "knowledge", [
        ("knowledge.html", "知識總覽"),
        ("news-387131-325944-831518.html", "專文分享"),
        ("news-387131-325944.html", "證券雙月刊專欄"),
        ("irupdatestc.html", "NIRI IR Update 精選"),
        ("2356035370-277843933339333297022010738263.html", "專訪 沈馥馥理事長"),
        ("5th_report-516844.html", "TIRI 年刊"),
    ]),
    ("membership.html", "會員服務", "membership", [
        ("membership.html", "會員類別與會費"),
        ("benefit.html", "會員專屬優惠"),
        ("bodperform.html", "董事會績效評估"),
        ("corpperform.html", "提升公司治理服務"),
        ("join.html", "加入會員"),
    ]),
    ("news.html", "最新消息", "news", [
        ("news.html", "協會消息"),
        ("news-971146.html", "精彩回顧"),
    ]),
    ("partners.html", "合作夥伴", "partners", [
        ("partners.html", "合作夥伴總覽"),
        ("partners.html#sponsor", "贊助方案"),
        ("contact.html", "聯絡我們"),
    ]),
]


def build_nav_items(active):
    items = []
    for href, label, key, subs in NAV:
        cur = ' aria-current="page"' if key == active else ""
        panel = "\n".join('            <a href="%s">%s</a>' % (h, t) for h, t in subs)
        items.append(
            '        <li><a href="%s"%s>%s</a>\n'
            '          <div class="menu-panel">\n%s\n          </div>\n'
            '        </li>' % (href, cur, label, panel)
        )
    return "\n".join(items)


def build_drawer_items():
    items = []
    for href, label, key, subs in NAV:
        sublinks = "\n".join('            <a href="%s">%s</a>' % (h, t) for h, t in subs)
        items.append(
            '        <li><a class="d-main" href="%s">%s <span class="arrow" aria-hidden="true">→</span></a>\n'
            '          <div class="subs">\n%s\n          </div>\n'
            '        </li>' % (href, label, sublinks)
        )
    return "\n".join(items)


def shell(title, desc, active, content):
    nav_items = build_nav_items(active)
    drawer_items = build_drawer_items()
    return f'''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}｜台灣投資人關係協會 TIRI</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="../fonts/fonts.css">
<link rel="stylesheet" href="../css/main.css">
</head>
<body>
<a class="skip-link" href="#main">跳至主要內容</a>

<div class="utility">
  <div class="container">
    <span class="utility-label">Taiwan Investor Relations Institute</span>
    <nav class="utility-nav" aria-label="工具列">
      <span class="lang">
        <span aria-current="true" style="color:#fff">中文</span>
        <span aria-hidden="true">&nbsp;/&nbsp;</span>
        <a href="en.html">EN</a>
      </span>
      <span class="divider" aria-hidden="true"></span>
      <a href="search.html">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.8-3.8"/></svg>
        搜尋
      </a>
      <span class="divider" aria-hidden="true"></span>
      <a href="login.html">會員登入</a>
    </nav>
  </div>
</div>

<header class="site-header" id="site-header">
  <div class="container">
    <a class="wordmark" href="index.html" aria-label="TIRI 台灣投資人關係協會 首頁">
      <span class="mark" aria-hidden="true">TI<span>RI</span></span>
      <span class="name">台灣投資人關係協會</span>
    </a>
    <nav class="main-nav" aria-label="主導覽">
      <ul>
{nav_items}
      </ul>
    </nav>
    <div class="header-actions">
      <a class="btn btn-primary btn-cta-desktop" href="join.html">加入會員</a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="drawer" aria-label="開啟選單">
        <span class="bar" aria-hidden="true"></span>
        <span class="bar" aria-hidden="true"></span>
        <span class="bar" aria-hidden="true"></span>
      </button>
    </div>
  </div>
</header>

<div class="drawer" id="drawer">
  <div class="drawer-backdrop" data-drawer-close></div>
  <div class="drawer-panel" role="dialog" aria-modal="true" aria-label="行動選單">
    <nav aria-label="行動導覽">
      <ul>
{drawer_items}
      </ul>
    </nav>
    <div class="drawer-cta">
      <a class="btn btn-primary" href="join.html">加入會員</a>
      <a class="btn btn-outline" href="login.html">會員登入</a>
    </div>
  </div>
</div>

<main id="main">
{content}
</main>

<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="../images/tiri-logo.png" alt="TIRI 台灣投資人關係協會" width="120" height="71">
        <p>社團法人台灣投資人關係協會<br>Taiwan Investor Relations Institute</p>
        <div class="social">
          <a class="u-link" href="https://www.facebook.com/tiri2018/" target="_blank" rel="noopener">FACEBOOK</a>
          <a class="u-link" href="https://www.linkedin.com/company/taiwan-investor-relations-institute-tiri-%E5%8F%B0%E7%81%A3%E6%8A%95%E8%B3%87%E4%BA%BA%E9%97%9C%E4%BF%82%E5%8D%94%E6%9C%83/" target="_blank" rel="noopener">LINKEDIN</a>
          <a class="u-link" href="https://lin.ee/AcTa5dh" target="_blank" rel="noopener">LINE</a>
          <a class="u-link" href="https://www.youtube.com/@officetiri6311" target="_blank" rel="noopener">YOUTUBE</a>
        </div>
      </div>
      <div class="footer-col">
        <h3>關於 TIRI</h3>
        <ul>
          <li><a href="about.html">協會使命</a></li>
          <li><a href="about.html#team">第三屆理監事成員</a></li>
          <li><a href="about.html#committee">功能委員會</a></li>
          <li><a href="about.html#duns">鄧白氏企業認證™雙標章</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h3>課程與證照</h3>
        <ul>
          <li><a href="events.html#training">董監事進修課程</a></li>
          <li><a href="events.html#tiric">TIRIC IR 專業實戰班</a></li>
          <li><a href="events.html#irc">IRC 國際證照</a></li>
          <li><a href="events.html#courses">2026 熱門課程</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h3>活動與知識</h3>
        <ul>
          <li><a href="events.html#recap">精彩回顧</a></li>
          <li><a href="knowledge.html">知識分享</a></li>
          <li><a href="knowledge.html#niri">NIRI IR Update 精選</a></li>
          <li><a href="news.html">最新消息</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h3>會員服務</h3>
        <ul>
          <li><a href="membership.html">會員類別與會費</a></li>
          <li><a href="membership.html#benefits">會員專屬優惠</a></li>
          <li><a href="membership.html#governance">董事會績效評估服務</a></li>
          <li><a href="join.html">加入會員</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 社團法人台灣投資人關係協會・統一編號 72976985</span>
      <span class="mono-meta">V1 DESIGN PROPOSAL — 版面為改版示意，內容取自 tiri.tw 公開資訊</span>
    </div>
  </div>
</footer>

<script src="../js/main.js" defer></script>
</body>
</html>
'''

def hero(eyebrow, h1, *ledes):
    parts = "".join(f'\n      <p class="lede reveal">{x}</p>' for x in ledes)
    return f'''  <section class="page-hero">
    <div class="container">
      <p class="eyebrow reveal">{eyebrow}</p>
      <h1 class="reveal">{h1}</h1>{parts}
    </div>
  </section>'''

pages = {}

# ============================== about.html ==============================
pages["about.html"] = ("關於 TIRI", "TIRI 協會使命、創會緣起、理監事成員、功能委員會與鄧白氏企業認證。", "about", hero(
    "About TIRI", "關於 TIRI",
    "法定名稱：社團法人台灣投資人關係協會・統一編號 72976985") + '''

  <section class="page-section">
    <div class="container">

      <div class="page-split">
        <div class="side reveal">
          <p class="eyebrow">Our Story</p>
          <h2>創會緣起</h2>
        </div>
        <div class="prose reveal">
          <p>1962 年臺灣證券交易所正式開業，台灣資本市場 56 年過去，卻始終沒有一個正式的投資人關係協會，代表台灣與全球資本市場接軌，同時提升 IR 從業人員之專業與地位。</p>
          <p>台灣投資人關係協會由一群資本市場的有志之士共同成立，期望能改善現況。</p>
        </div>
      </div>

      <div class="page-split">
        <div class="side reveal">
          <p class="eyebrow">Mission</p>
          <h2>成立宗旨</h2>
        </div>
        <div class="prose reveal">
          <p><strong>TIRI 台灣投資人關係協會（Taiwan Investor Relations Institute）</strong>是專為台灣上市櫃、興櫃、公開發行、創櫃公司，負責經營團隊、股東、證券分析師、資本市場和主管機關之間溝通的企業經理人而設的專業協會，致力推進台灣投資人關係的實踐及其成員的專業能力和地位，並加強與國際資本市場接軌。</p>
        </div>
      </div>

      <div class="page-split">
        <div class="side reveal">
          <p class="eyebrow">Functions &amp; Services</p>
          <h2>功能與服務</h2>
        </div>
        <ul class="services-list" style="grid-template-columns: repeat(2, 1fr);" data-reveal-group>
          <li class="reveal"><span class="no">01</span>專業培訓課程</li>
          <li class="reveal"><span class="no">02</span>專業考試與證照</li>
          <li class="reveal"><span class="no">03</span>年度評鑑及頒獎典禮</li>
          <li class="reveal"><span class="no">04</span>年度大會及研討會</li>
          <li class="reveal"><span class="no">05</span>分區月會及座談會</li>
          <li class="reveal"><span class="no">06</span>會員交流活動</li>
          <li class="reveal"><span class="no">07</span>研究調查</li>
          <li class="reveal"><span class="no">08</span>年報、出版物及電子報</li>
          <li class="reveal"><span class="no">09</span>雲端知識庫</li>
          <li class="reveal"><span class="no">10</span>就業指導中心</li>
          <li class="reveal"><span class="no">11</span>產品與服務資源</li>
          <li class="reveal"><span class="no">12</span>國外交流</li>
        </ul>
      </div>

      <div class="page-split" id="team">
        <div class="side reveal">
          <p class="eyebrow">Board of Directors</p>
          <h2>第三屆理監事成員</h2>
          <p class="note">本會於 2026 年 3 月 20 日召開會員大會選出第三屆理、監事。</p>
        </div>
        <div>
          <div class="team-block reveal">
            <h3>榮譽理事長</h3>
            <ul><li><strong>孫又文</strong><span>前台灣積體電路製造股份有限公司 企業訊息處資深處長</span></li></ul>
          </div>
          <div class="team-block reveal">
            <h3>理事長</h3>
            <ul><li><strong>郭宗霖</strong><span>鴻勝會計師事務所執業會計師暨大井泵浦工業股份有限公司董事</span></li></ul>
          </div>
          <div class="team-block reveal">
            <h3>副理事長</h3>
            <ul>
              <li><strong>王恩國</strong><span>南昌菱光科技有限公司董事長、今皓實業股份有限公司獨立董事</span></li>
              <li><strong>簡世雄</strong><span>東元電機股份有限公司 公司治理中心處長暨發言人</span></li>
              <li><strong>張明仁</strong><span>新加坡商睿智先鋒有限公司 財務長</span></li>
            </ul>
          </div>
          <div class="team-block reveal">
            <h3>常務理事</h3>
            <ul>
              <li><strong>郭宗霖</strong><span>鴻勝會計師事務所執業會計師暨大井泵浦工業股份有限公司董事</span></li>
              <li><strong>王恩國</strong><span>南昌菱光科技有限公司董事長、今皓實業股份有限公司獨立董事</span></li>
              <li><strong>簡世雄</strong><span>東元電機股份有限公司 公司治理中心處長暨發言人</span></li>
              <li><strong>張明仁</strong><span>新加坡商睿智先鋒有限公司 財務長</span></li>
              <li><strong>黃奕誠</strong><span>鴻海精密股份有限公司 投資人關係暨永續委員會經理</span></li>
            </ul>
          </div>
          <div class="team-block reveal">
            <h3>理事</h3>
            <ul>
              <li><strong>沈馥馥</strong><span>中華電信股份有限公司 前財務處副總暨代理發言人</span></li>
              <li><strong>張妍婷</strong><span>仁寶電腦工業股份有限公司 投資人關係暨品牌辦公室資深處長、代理發言人</span></li>
              <li><strong>張真卿</strong><span>立隆電子工業股份有限公司 董事長特助暨發言人</span></li>
              <li><strong>姚文鈞</strong><span>全漢企業股份有限公司 董事長特別助理暨發言人</span></li>
              <li><strong>許碧雲</strong><span>桓達科技股份有限公司 總經理特助暨發言人</span></li>
              <li><strong>黃英記</strong><span>矽創電子股份有限公司 投資人關係暨永續辦公室處長</span></li>
              <li><strong>林男和</strong><span>旗山龍鳳食品股份有限公司 總經理</span></li>
              <li><strong>洪健凱</strong><span>經寶精密控股股份有限公司 投資人關係部經理</span></li>
              <li><strong>趙元祥</strong><span>群聯電子股份有限公司 董事長特助</span></li>
              <li><strong>張登溪</strong><span>大井泵浦工業股份有限公司 財務長</span></li>
            </ul>
          </div>
          <div class="team-block reveal">
            <h3>監事會</h3>
            <ul>
              <li><strong>涂蕙蘭</strong><span>常務監事</span></li>
              <li><strong>萬心寧</strong><span>圓裕企業股份有限公司 獨立董事</span></li>
              <li><strong>陳珮瑛</strong><span>永創數智股份有限公司 資深顧問</span></li>
              <li><strong>葉文燦</strong><span>宇峻奧汀科技股份有限公司 管理處協理暨發言人</span></li>
              <li><strong>鄭可人</strong><span>佳能企業 投資人關係經理暨永續發展暨風險管理執行委員會委員</span></li>
            </ul>
          </div>
          <div class="team-block reveal">
            <h3>顧問與秘書處</h3>
            <ul>
              <li><strong>楊朝榮</strong><span>榮譽顧問・中華民國證券期貨分析協會理事及聯茂、虎航、泰博等公司獨立董事</span></li>
              <li><strong>周德雲</strong><span>榮譽顧問・矽創電子股份有限公司 前策略投資顧問</span></li>
              <li><strong>劉詩亮</strong><span>榮譽顧問・TPK 宸鴻光電科技股份有限公司 資深副總經理策略長暨代理發言人</span></li>
              <li><strong>王沈銘</strong><span>榮譽顧問・1919 食物銀行 特約顧問</span></li>
              <li><strong>余凱文</strong><span>首席顧問・自 2004 年以來台灣投資人關係的推動者和革新者</span></li>
              <li><strong>許育綾</strong><span>秘書長</span></li>
            </ul>
          </div>
        </div>
      </div>

      <div class="page-split" id="committee">
        <div class="side reveal">
          <p class="eyebrow">Committees</p>
          <h2>功能委員會</h2>
          <p class="note">加入功能委員會可與 IR 領域先進交流、促進職涯發展。歡迎與各委員會或秘書處聯繫：(02) 2381-9248。</p>
        </div>
        <div class="committee-grid" data-reveal-group>
          <div class="committee-card reveal">
            <h3>證照委員會</h3>
            <p class="role">協助 IRC 證照推廣</p>
            <dl>
              <div><dt>召集人</dt><dd>張妍婷（仁寶電腦 投資人關係部處長）</dd></div>
              <div><dt>執行委員</dt><dd>張明仁、黃英記</dd></div>
            </dl>
          </div>
          <div class="committee-card reveal">
            <h3>獎項委員會</h3>
            <p class="role">協助投資人關係獎項推廣</p>
            <dl>
              <div><dt>召集人</dt><dd>劉詩亮（TPK 宸鴻 資深副總經理策略長）</dd></div>
              <div><dt>執行委員</dt><dd>周德雲、黃英記</dd></div>
            </dl>
          </div>
          <div class="committee-card reveal">
            <h3>專業委員會</h3>
            <p class="role">協助專業資訊內容產出</p>
            <dl>
              <div><dt>召集人</dt><dd>簡世雄（東元電機 公司治理中心處長暨發言人）</dd></div>
              <div><dt>執行委員</dt><dd>陳珮瑛、涂蕙蘭、許碧雲</dd></div>
            </dl>
          </div>
          <div class="committee-card reveal">
            <h3>媒體委員會</h3>
            <p class="role">協助媒體溝通合作</p>
            <dl>
              <div><dt>召集人</dt><dd>王恩國（東友科技 副董事長）</dd></div>
              <div><dt>執行委員</dt><dd>王沈銘、陳珮瑛</dd></div>
            </dl>
          </div>
          <div class="committee-card reveal">
            <h3>推廣委員會</h3>
            <p class="role">協助社群及活動行銷</p>
            <dl>
              <div><dt>召集人</dt><dd>林男和（旗山龍鳳食品 總經理）</dd></div>
              <div><dt>執行委員</dt><dd>洪健凱、姚文鈞</dd></div>
            </dl>
          </div>
        </div>
      </div>

      <div class="page-split" id="duns">
        <div class="side reveal">
          <p class="eyebrow">D-U-N-S Registered™</p>
          <h2>鄧白氏企業認證™雙標章</h2>
        </div>
        <div class="prose reveal">
          <p>台灣投資人關係協會通過「鄧白氏企業認證」，鄧白氏環球編碼®（D-U-N-S Number®）為 <strong>65-851-5060</strong>，並獲授權安裝經權威認證的 D-U-N-S® Registered™ 電子標章。</p>
          <p>鄧白氏（Dun &amp; Bradstreet）成立至今 180 年，是全球最大的商業數據公司，其企業認證廣為國際認可，是許多國際大型企業及政府機構評估商業合作夥伴的基礎。</p>
        </div>
      </div>

    </div>
  </section>''')

# ============================== events.html ==============================
pages["events.html"] = ("活動與課程", "TIRI 焦點訊息、TIRIC 實戰班、董監事進修課程、IRC 國際證照與歷屆年度大會回顧。", "events", hero(
    "Events & Programs", "活動與課程",
    "年度大會、專業課程與國際證照——TIRI 專業發展的完整路徑。") + '''

  <section class="page-section" style="padding-bottom: 0;">
    <div class="container">
      <div class="events-grid" style="padding-block: clamp(36px, 5vw, 56px);">
        <a class="event-featured reveal" href="#recap">
          <div class="frame">
            <img src="../images/event-2025-conference.jpg" alt="TIRI 2025 年度大會暨引領 IR 智慧新時代，五位貴賓於主視覺舞台合影">
            <span class="flag">焦點訊息</span>
          </div>
          <div class="body">
            <span class="mono-meta">2025.10.23・台北</span>
            <h3>TIRI 2025 年度大會暨引領 IR 智慧新時代</h3>
            <p class="desc">以「智慧驅動未來，IR 共創新時代」為年會主題，呼應數位轉型與人工智慧對資本市場的深遠影響，與國內外專業夥伴攜手，運用創新科技深化投資人互動、提升企業價值傳遞。</p>
            <div class="meta"><span class="tag">年度大會</span></div>
          </div>
        </a>
        <div class="event-list" data-reveal-group>
          <a class="event-item reveal" href="#tiric">
            <span class="date">08.21<span class="yr">2026・五</span></span>
            <span>
              <h3>TIRIC IR 專業實戰班開課（週五全日・共 5 堂）</h3>
              <span class="meta"><span class="tag is-members">會員優惠</span><span class="mono-meta">實體・台北</span></span>
            </span>
            <span class="go" aria-hidden="true">→</span>
          </a>
          <a class="event-item reveal" href="#training">
            <span class="date">全年<span class="yr">開課</span></span>
            <span>
              <h3>董監事與公司治理主管進修：公開班・企業專班・線上授課</h3>
              <span class="meta"><span class="tag">公開課程</span><span class="mono-meta">到府・線上</span></span>
            </span>
            <span class="go" aria-hidden="true">→</span>
          </a>
          <a class="event-item reveal" href="#irc">
            <span class="date">隨時<span class="yr">報名</span></span>
            <span>
              <h3>IRC 國際證照：TIRI 會員報名折 US$200</h3>
              <span class="meta"><span class="tag">國際證照</span><span class="mono-meta">線上測驗</span></span>
            </span>
            <span class="go" aria-hidden="true">→</span>
          </a>
        </div>
      </div>
    </div>
  </section>

  <section class="courses" id="tiric" style="scroll-margin-top: 96px;">
    <div class="container">
      <div class="section-head reveal">
        <div>
          <p class="eyebrow">Professional Development</p>
          <h2>課程與專業發展</h2>
        </div>
      </div>
      <div class="tiric-feature reveal">
        <div class="tf-main">
          <p class="eyebrow">TIRIC IR 專業實戰班</p>
          <h3>引領變革，成就頂尖 IR 領袖</h3>
          <p class="desc">採用經美國國家投資人關係協會（NIRI）正式授權的《Investor Relations Body of Knowledge》第二版繁體中文版教材——全球首本 NIRI 授權中文教材，結合業界實務師資，聚焦投資人關係、財務分析、法規遵循、公司治理、永續發展與對外溝通。</p>
          <div class="tf-meta">
            <span class="tag">2026.08.21 起・週五全日共 5 堂（08/21、08/28、09/04、09/11、09/18）</span>
            <span class="tag">09:00–16:00・台北市中正區忠孝東路二段 88 號 10 樓</span>
            <span class="tag">定價 NT$120,000・早鳥入會優惠 NT$76,000</span>
          </div>
          <p class="cta"><a class="btn btn-invert" href="join.html">報名與洽詢 <span class="arrow" aria-hidden="true">→</span></a></p>
        </div>
        <ul class="tf-points">
          <li><span class="no">01</span><span>NIRI 授權繁中教材<small>IRBOK 第二版，2025 波士頓 NIRI 年會正式授權</small></span></li>
          <li><span class="no">02</span><span>10 位資深業界師資<small>理事長、發言人、財務長與資深合夥律師共同授課</small></span></li>
          <li><span class="no">03</span><span>TIRIC 專屬結業證書<small>彰顯專業認可與學習成果</small></span></li>
        </ul>
      </div>
      <div class="course-rows" id="courses" data-reveal-group style="scroll-margin-top: 96px;">
        <a class="course-row reveal" href="#training">
          <span class="no">01</span>
          <h3>併購 M&amp;A</h3>
          <p>產業趨勢、國際管理與企業併購實務。</p>
          <span class="go" aria-hidden="true">→</span>
        </a>
        <a class="course-row reveal" href="#training">
          <span class="no">02</span>
          <h3>企業管理</h3>
          <p>企業財務與投資規劃、對外發言技巧與訓練。</p>
          <span class="go" aria-hidden="true">→</span>
        </a>
        <a class="course-row reveal" href="#training">
          <span class="no">03</span>
          <h3>公司治理</h3>
          <p>董事會成員與架構、提升董事會績效。</p>
          <span class="go" aria-hidden="true">→</span>
        </a>
        <a class="course-row reveal" href="#training">
          <span class="no">04</span>
          <h3>財稅法律</h3>
          <p>財務報表解析、國際財務報導準則與董事法律責任。</p>
          <span class="go" aria-hidden="true">→</span>
        </a>
        <a class="course-row reveal" href="#training">
          <span class="no">05</span>
          <h3>誠信經營</h3>
          <p>企業風險管理、內控監督與內部稽核品質。</p>
          <span class="go" aria-hidden="true">→</span>
        </a>
      </div>
      <p class="course-note reveal">2026 熱門課程主題｜可依需求設定不同講師及主題</p>
    </div>
  </section>

  <section class="page-section" id="training" style="scroll-margin-top: 96px; padding-top: clamp(40px, 6vw, 80px);">
    <div class="container">
      <div class="page-split" style="border-top: 0;">
        <div class="side reveal">
          <p class="eyebrow">Board Training</p>
          <h2>董監事與公司治理主管進修</h2>
          <p class="note">服務窗口：許小姐・(02) 2381-9248</p>
        </div>
        <div>
          <div class="prose reveal">
            <p>提供<strong>公開班</strong>與<strong>到府授課企業專班</strong>，並開辦<strong>線上授課</strong>——在家裡或辦公室透過電腦上線即可完成進修。內容除財務及法遵外，亦包含投資人關係、資本市場解析、策略發展、ESG 議題等多元選擇；可配合董監事時間與指定地點安排講師。</p>
          </div>
          <div class="topic-chips reveal" style="margin-top: 24px;">
            <span class="tag">建構投資人關係及對企業的正面影響</span>
            <span class="tag">台灣資本市場現況及對企業的衝擊</span>
            <span class="tag">董監事如何審查財報</span>
            <span class="tag">智財風險門道</span>
            <span class="tag">企業財務與投資規劃</span>
            <span class="tag">對外發言技巧與訓練</span>
            <span class="tag">董事的法律義務與責任</span>
            <span class="tag">ESG 企業社會責任</span>
            <span class="tag">董事會的成員與架構</span>
            <span class="tag">提升董事會績效</span>
            <span class="tag">董事與股東會事務</span>
            <span class="tag">企業併購</span>
            <span class="tag">財報與 IFRS 解析</span>
            <span class="tag">風險管理與內控稽核</span>
            <span class="tag">永續報告書架構</span>
          </div>
          <div class="benefit-rows reveal" style="margin-top: 28px;">
            <div><dt>費用</dt><dd>3 小時 NT$30,000・6 小時 NT$60,000（客製化請於一個月前提出申請）</dd></div>
            <div><dt>團體會員</dt><dd>到府授課 2 次或公開班 60 小時免費，額滿後享 5 折優惠</dd></div>
            <div><dt>個人會員</dt><dd>6 小時免費名額，滿額後享 9 折優惠</dd></div>
            <div><dt>退費</dt><dd>開課前三天取消可全額退費；前一天取消酌收 NT$500、當天取消酌收 NT$1,000</dd></div>
          </div>
        </div>
      </div>

      <div class="page-split" id="irc" style="scroll-margin-top: 96px;">
        <div class="side reveal">
          <p class="eyebrow">IRC Certification</p>
          <h2>IRC 國際證照</h2>
          <p class="note">諮詢窗口：楊小姐・(02) 2381-9248 #747</p>
        </div>
        <div>
          <div class="prose reveal">
            <p>IRC 證照是 2016 年由美國國家投資人關係協會（NIRI）推出的專業投資人關係證照。TIRI 與 NIRI 合作推廣 IR 最佳實務，<strong>TIRI 會員報名可省 US$200 報名費</strong>，並可於台灣考場直接應試。</p>
          </div>
          <div class="benefit-rows reveal" style="margin-top: 24px;">
            <div><dt>考試方式</dt><dd>170 題選擇題・測驗時間 3 小時・線上進行，題型含基礎財務數字與實務狀況模擬題</dd></div>
            <div><dt>報名費用</dt><dd>US$1,295，TIRI 會員享 US$200 折扣</dd></div>
            <div><dt>報考資格</dt><dd>學士學歷＋3 年以上 IR 全職經驗，或 6 年合格全職經驗；不具經驗者可以 IRC Candidate 身分應試</dd></div>
            <div><dt>證照維護</dt><dd>每三年累積至少 30 個 PDUs——參與 TIRI 活動即可累積</dd></div>
            <div><dt>適合對象</dt><dd>新任 IRO 快速學習職能；資深 IRO 檢視技能並與國際接軌</dd></div>
            <div><dt>贊助獎學金</dt><dd>TIRI 提供考取 IRC 者新台幣 3 萬元獎學金（名額 2 名，限台灣地區人士，先取得證書者優先）</dd></div>
            <div><dt>持證者分享</dt><dd>仁寶電腦 張妍婷副處長、新源生技 張明仁財務副總、時碩集團 高正興財務長</dd></div>
          </div>
        </div>
      </div>

      <div class="page-split" id="awards" style="scroll-margin-top: 96px;">
        <div class="side reveal">
          <p class="eyebrow">TIRI Awards</p>
          <h2>獎項</h2>
          <p class="note">2025 第四屆 TIRI Awards 投票至 2025 年 8 月 20 日止。</p>
        </div>
        <div>
          <div class="prose reveal">
            <p><strong>TIRI Awards</strong>──為提升台灣資本市場資訊揭露品質與 IR 專業水平而設，由投資台股之基金經理人、分析師與財經媒體記者投票選出，分上市巨型股、大型股、中小型股等組別，入圍企業包含台積電、鴻海、聯發科、台達電等指標公司。</p>
            <p><strong>TIRI 潛力進展獎</strong>──專為資本額較小、資源相對有限，卻積極投入 IR 實務的企業設計。不採投票制，以客觀數據評估上市市值 300 億元以下、上櫃市值 100 億元以下企業的市場表現與成長趨勢，經執行委員會審核後表揚。</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="page-section" id="recap" style="scroll-margin-top: 96px; background: var(--white); border-top: 1px solid var(--line); padding-top: clamp(40px, 6vw, 80px);">
    <div class="container">
      <div class="section-head reveal">
        <div>
          <p class="eyebrow">Past Events</p>
          <h2>精彩回顧</h2>
        </div>
      </div>
      <div class="event-list" data-reveal-group>
        <a class="event-item reveal" href="#"><span class="date">10.23<span class="yr">2025</span></span><span><h3>2025 年度大會暨引領 IR 智慧新時代</h3></span><span class="go" aria-hidden="true">→</span></a>
        <a class="event-item reveal" href="#"><span class="date">12.05<span class="yr">2024</span></span><span><h3>2024 年度大會暨共創 IR 新紀元</h3></span><span class="go" aria-hidden="true">→</span></a>
        <a class="event-item reveal" href="#"><span class="date">11.16<span class="yr">2023</span></span><span><h3>2023 年度大會暨國際論壇</h3></span><span class="go" aria-hidden="true">→</span></a>
        <a class="event-item reveal" href="#"><span class="date">12.14<span class="yr">2022</span></span><span><h3>2022 年度大會暨第一屆台灣投資人關係大獎</h3></span><span class="go" aria-hidden="true">→</span></a>
        <a class="event-item reveal" href="#"><span class="date">12.22<span class="yr">2021</span></span><span><h3>2021 年度大會──The Future of ESG is NOW</h3></span><span class="go" aria-hidden="true">→</span></a>
        <a class="event-item reveal" href="#"><span class="date">12.23<span class="yr">2020</span></span><span><h3>2020 年度大會暨台灣投資人關係獎項啟動典禮</h3></span><span class="go" aria-hidden="true">→</span></a>
        <a class="event-item reveal" href="#"><span class="date">12.16<span class="yr">2019</span></span><span><h3>2019 年度大會暨亞洲投資人關係連結</h3></span><span class="go" aria-hidden="true">→</span></a>
        <a class="event-item reveal" href="#"><span class="date">10.23<span class="yr">2018</span></span><span><h3>2018 成立大會暨大師論壇</h3></span><span class="go" aria-hidden="true">→</span></a>
      </div>
    </div>
  </section>''')

# ============================== knowledge.html ==============================
def icard(cat, tag, meta, title, src):
    return f'''        <a class="insight-card reveal" href="#" data-category="{cat}">
          <span class="meta"><span class="tag">{tag}</span><span class="mono-meta">{meta}</span></span>
          <h3>{title}</h3>
          <span class="foot"><span class="mono-meta">{src}</span><span class="go" aria-hidden="true">→</span></span>
        </a>'''

bimonthly = [
    ("2021.08.15", "疫起面對，有效管理的媒體溝通策略"),
    ("2021.06.15", "批判性思維在投資人溝通過程中的重要性"),
    ("2021.04.15", "機構法人經營實例分析（下）"),
    ("2021.02.20", "機構法人經營實例分析（上）"),
    ("2020.12.20", "IR 證照，台灣 IRO 邁向專業化之途？"),
    ("2020.08.20", "IRO 必須知道的基本財務知識"),
    ("2020.04.20", "跨部門溝通與資訊整合（下）"),
    ("2020.02.20", "跨部門溝通與資訊整合（上）"),
    ("2019.11.18", "投資人關係溝通策略：對誰說？說什麼？怎麼說？"),
    ("2019.08.20", "投資人關係長（IRO）的工作內容（下）"),
    ("2019.06.15", "投資人關係長（IRO）的工作內容（上）"),
    ("2019.04.15", "投資人關係對上市櫃企業的重要性"),
]
niri = [
    "如何在 COVID-19 期間，持續執行投資人關係計畫",
    "備受矚目的 ESG 評比",
    "企業文化之價值",
    "IRO 如何參與董事會及報告",
    "成功 IRO 的秘訣",
    "高階主管異動，IR 的應對工作",
    "投資人關係經理人如何在董事會佔有一席之地",
]
articles = [
    ("2019.11.26", "上市櫃企業年財報英文化常見問題", "協會專文"),
    ("2019.10.09", "ESG 與 EPS 同樣重要！非財務績效表現將影響投資人決策", "協會專文"),
    ("2019.08.27", "企業沒建立良好投資人關係，等同沒做好公共關係", "協會專文"),
    ("2019.03.01", "IR 投資人關係：資本市場最佳溝通者", "會計研究發展月刊 封面專題"),
    ("2019.03.01", "肩負傳統走向創新──霹靂用投資人關係展現文創價值", "會計研究發展月刊"),
    ("2019.03.01", "為何臺灣上市（櫃）公司應重視投資人關係（IR）", "會計研究發展月刊"),
    ("2018.12.21", "投資人關係專家劉詩亮：籌資遇困境 企業先惦惦自己斤兩", "協會專文"),
]

kcards = []
kcards.append(icard("interview", "專訪", "2020.06.20", "專訪創會理事長沈馥馥：中華電信代理發言人的 IR 之路", "證交所「證券服務雙月刊」"))
for d, t in bimonthly[:6]:
    kcards.append(icard("bimonthly", "雙月刊專欄", d, t, "證交所「證券服務雙月刊」"))
for t in niri[:4]:
    kcards.append(icard("niri", "NIRI 精選", "NIRI × TIRI", t, "NIRI IR Update 中文化"))
for d, t, s in articles[:4]:
    kcards.append(icard("article", "專文分享", d, t, s))
for d, t in bimonthly[6:]:
    kcards.append(icard("bimonthly", "雙月刊專欄", d, t, "證交所「證券服務雙月刊」"))
for t in niri[4:]:
    kcards.append(icard("niri", "NIRI 精選", "NIRI × TIRI", t, "NIRI IR Update 中文化"))
for d, t, s in articles[4:]:
    kcards.append(icard("article", "專文分享", d, t, s))
kcards_html = "\n".join(kcards)

pages["knowledge.html"] = ("知識資源", "TIRI 知識分享：證交所證券雙月刊專欄、NIRI IR Update 精選文章、專文與專訪。", "knowledge", hero(
    "IR Knowledge", "知識資源",
    "證交所「證券服務雙月刊」專欄、NIRI IR Update 精選、專文與專訪──台灣 IR 的知識庫。",
    "「IR Update 精選文章」由 NIRI 與 TIRI 於 2019–2020 合作，精選文章並中文化，透過 HKIRA 等合作夥伴同步揭露。") + f'''

  <section class="insights" id="niri" style="border-top: 0;">
    <div class="container">
      <div class="filter-bar reveal" role="group" aria-label="文章分類篩選">
        <button class="filter-btn" type="button" data-filter="all" aria-pressed="true">全部</button>
        <button class="filter-btn" type="button" data-filter="bimonthly" aria-pressed="false">證券雙月刊專欄</button>
        <button class="filter-btn" type="button" data-filter="niri" aria-pressed="false">NIRI 精選</button>
        <button class="filter-btn" type="button" data-filter="article" aria-pressed="false">專文分享</button>
        <button class="filter-btn" type="button" data-filter="interview" aria-pressed="false">專訪</button>
      </div>
      <div class="insights-grid" data-reveal-group>
{kcards_html}
      </div>
    </div>
  </section>

  <section class="page-section" id="yearbook" style="scroll-margin-top: 96px; padding-top: clamp(40px, 6vw, 80px);">
    <div class="container">
      <div class="page-split" style="border-top: 0;">
        <div class="side reveal">
          <p class="eyebrow">Annual Report</p>
          <h2>TIRI 年刊</h2>
          <p class="note">本刊創始於 2024 年，每年出刊一次。</p>
        </div>
        <div>
          <div class="prose reveal">
            <p>TIRI 自 2018 年成立以來持續提升服務品質、擴大業務範圍。年刊呈現協會的專業、團隊與核心價值觀，紀錄每一年與會員共同累積的成果。</p>
          </div>
          <div class="reveal" style="margin-top: 20px;">
            <div class="download-row">
              <span class="name">2025 TIRI 7 周年年刊<small>7th Anniversary Commemorative Booklet・PDF</small></span>
              <a class="btn btn-outline" style="height: 42px; padding: 0 18px; font-size: 14px;" href="https://www.tiri.tw/uploads/1/1/9/9/119925991/2025_tiri_7th_anniversary_commemorative_booklet.pdf" target="_blank" rel="noopener">閱讀年刊</a>
            </div>
            <div class="download-row">
              <span class="name">2024 TIRI 6 周年年刊<small>6th Anniversary Commemorative Booklet・PDF</small></span>
              <a class="btn btn-outline" style="height: 42px; padding: 0 18px; font-size: 14px;" href="https://www.tiri.tw/uploads/1/1/9/9/119925991/2024_tiri_6th_anniversary_commemorative_booklet.pdf" target="_blank" rel="noopener">閱讀年刊</a>
            </div>
            <div class="download-row">
              <span class="name">TIRI 5 周年年刊<small>5th Anniversary Commemorative Booklet・PDF</small></span>
              <a class="btn btn-outline" style="height: 42px; padding: 0 18px; font-size: 14px;" href="https://www.tiri.tw/uploads/1/1/9/9/119925991/tiri_5th_anniversary_commemorative_booklet.pdf" target="_blank" rel="noopener">閱讀年刊</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>''')

# ============================== news.html ==============================
newsitems = [
    ("12.31", "2019", "【TIRI 課程】9～12 月投資人關係實務課程"),
    ("11.20", "2019", "TIRI 與竹科管理局共同推動 IR 專業"),
    ("10.25", "2019", "【TIRI 課程】智財管理新思惟──運用 AI 智能平台協助智財管理"),
    ("10.17", "2019", "【TIRI 講座】藝術品欣賞與投資"),
    ("09.19", "2019", "簡世雄、黃英記理事代表參加證交所「強化機構投資人盡職治理與上市公司投資人關係」論壇"),
    ("09.01", "2019", "【TIRI 會員福利】4 天 3 夜免費韓國機票、住宿、翻譯"),
    ("07.31", "2019", "【7/31 雙主題講座】國內外併購實務大解析／ESG、年報雙語化趨勢與重要性"),
    ("07.17", "2019", "公司治理主管系列課程：7/17（台北）、7/29（新竹）、7/31（台南）"),
    ("06.26", "2019", "新興市場崛起中的越南：台商面向資本市場更要強化投資人關係"),
    ("05.30", "2019", "【5/30 雙主題講座】新媒體時代的思維／成功發言系列"),
    ("04.15", "2019", "TIRI 受邀擔任證交所「股權到經營權，IR 核心策略座談會」分享嘉賓"),
    ("03.29", "2019", "TIRI 受邀擔任 MZ Asia「IR 說明會」開幕致詞嘉賓"),
    ("03.15", "2019", "TIRI 受邀出席集保「投資人關係整合平台」成立大會"),
    ("12.31", "2018", "台灣資本市場 IR 與國際接軌"),
    ("10.23", "2018", "紐約證交所、美國 IR 協會高層來台參加 TIRI 年度大會暨大師論壇"),
    ("09.11", "2018", "台灣投資人關係協會推專業 IR 獲證交所肯定"),
    ("06.22", "2018", "通過內政部核准立案"),
    ("05.30", "2018", "成立大會暨第一屆會員大會、理監事選舉"),
]
news_html = "\n".join(
    f'''        <a class="event-item reveal" href="#"><span class="date">{d}<span class="yr">{y}</span></span><span><h3>{t}</h3></span><span class="go" aria-hidden="true">→</span></a>'''
    for d, y, t in newsitems
)
pages["news.html"] = ("最新消息", "TIRI 台灣投資人關係協會最新消息與公告。", "news", hero(
    "Latest News", "最新消息",
    "協會公告、課程講座與產業參與紀錄。") + f'''

  <section class="page-section" style="padding-top: clamp(36px, 5vw, 56px);">
    <div class="container">
      <div class="event-list" data-reveal-group>
{news_html}
      </div>
    </div>
  </section>''')

# ============================== membership.html ==============================
pages["membership.html"] = ("會員服務", "TIRI 會員類別、會費、專屬優惠與公司治理服務。", "membership", hero(
    "Membership", "會員服務",
    "個人與團體會員的類別、會費、專屬優惠與治理服務總覽。") + '''

  <section class="page-section">
    <div class="container">

      <div class="page-split">
        <div class="side reveal">
          <p class="eyebrow">Categories</p>
          <h2>會員類別</h2>
          <p class="note">入會申請經理事會通過後生效；詳細資格以協會章程為準。</p>
        </div>
        <div class="benefit-rows reveal">
          <div><dt>個人會員</dt><dd>凡贊同本會宗旨、年滿二十歲，於公司擔任發言人或代理發言人、投資人關係相關工作之從業人員，及長期經營資本市場投資人關係者。</dd></div>
          <div><dt>團體會員</dt><dd>凡贊同本會宗旨之公私立機關、企業或團體；需指派一位代表行使會員權利，並得另行指派兩人參與本會活動。</dd></div>
          <div><dt>預備會員</dt><dd>凡贊同本會宗旨、年滿二十歲，經會員（會員代表）一人推薦，並按時繳納會費者。</dd></div>
          <div><dt>永久會員</dt><dd>個人或團體會員一次繳納十年會費後即成為永久會員，不必再繳納常年會費。</dd></div>
          <div><dt>榮譽會員</dt><dd>對本會有特殊貢獻者，經理事會通過邀請加入，免繳納會費。</dd></div>
          <div><dt>贊助會員</dt><dd>凡贊同本會宗旨之公私立機構、團體或個人，對本會會務活動經費有所贊助者。</dd></div>
        </div>
      </div>

      <div class="page-split">
        <div class="side reveal">
          <p class="eyebrow">Fees</p>
          <h2>會費標準</h2>
        </div>
        <div class="fee-cards" style="margin-top: 0; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));" data-reveal-group>
          <div class="fee-card reveal">
            <p class="type">Individual</p>
            <h3>個人會員</h3>
            <p class="price">NT$6,000<span>／年</span></p>
            <p class="init">入會費 NT$2,000（入會時繳納一次）</p>
            <ul>
              <li>公開班課程 6 小時免費，滿額後享 9 折</li>
              <li>會員專屬合作夥伴優惠</li>
            </ul>
          </div>
          <div class="fee-card reveal">
            <p class="type">Corporate</p>
            <h3>團體會員</h3>
            <p class="price">NT$60,000<span>／年</span></p>
            <p class="init">入會費 NT$6,000（入會時繳納一次）</p>
            <ul>
              <li>到府專班授課 2 次，或公開班 60 小時免費（額滿後 5 折）</li>
              <li>指派 1 位代表＋2 位活動參與</li>
              <li>治理服務 85 折</li>
            </ul>
          </div>
          <div class="fee-card reveal">
            <p class="type">Lifetime</p>
            <h3>永久會員</h3>
            <p class="price">十年會費<span>一次繳納</span></p>
            <p class="init">個人 NT$60,000／團體另洽</p>
            <ul>
              <li>免再繳納常年會費</li>
              <li>個人與團體會員皆適用</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="page-split" id="benefits">
        <div class="side reveal">
          <p class="eyebrow">Member Benefits</p>
          <h2>會員專屬優惠</h2>
          <p class="note">以下優惠限本會會員專屬，須由秘書處引薦會員給合作夥伴始享優惠；合作夥伴保留各方案最終決定權。</p>
        </div>
        <div class="benefit-rows reveal">
          <div><dt>TIRI 主辦課程</dt><dd>團體會員：到府專班 2 次或公開班 60 小時免費（額滿後 5 折）；個人會員：6 小時免費（滿額後 9 折）</dd></div>
          <div><dt>治理服務</dt><dd>提升公司治理服務、董事會績效評估服務──團體會員 85 折</dd></div>
          <div><dt>NIRI IRC 證照</dt><dd>報名費 US$1,295，會員享 US$200 折扣</dd></div>
          <div><dt>MZ Asia</dt><dd>IR 管理和資本市場情報系統、線上法說會、網站建置──定價 9 折</dd></div>
          <div><dt>雲翻譯</dt><dd>法說會資料、股東會年報、議事手冊等多國語言翻譯──定價 88 折</dd></div>
          <div><dt>精彩創意整合行銷</dt><dd>線上法說會服務 9 折；媒體、行銷免費專業顧問諮詢一次</dd></div>
          <div><dt>Notified</dt><dd>財報新聞稿發布、線上法說會及電話會議、IR 網站、吹哨者平台──定價 75 折</dd></div>
          <div><dt>倍力資訊</dt><dd>碳盤查工具 Carbonkeeper 9 折＋免費 3 小時教學影片，經 TIRI 推薦可免費試用二週</dd></div>
          <div><dt>商業周刊</dt><dd>企業故事與加值宣傳──優惠價再 9 折</dd></div>
          <div><dt>旅居文旅集團</dt><dd>旅居文旅平日 9 折、假日 95 折等住宿優惠，享延後退房禮遇</dd></div>
          <div><dt>Hi 家教</dt><dd>線上課程購課滿額贈購課金（最高加贈 NT$8,000）</dd></div>
          <div><dt>找到了旅行社</dt><dd>訂購國外團體旅遊行程即獲「旅行六大好禮」</dd></div>
          <div><dt>英特內軟體</dt><dd>S-HR 人資系統、永續報告書平台全系列 88 折，經 TIRI 推薦可免費試用二週</dd></div>
        </div>
      </div>

      <div class="page-split" id="governance">
        <div class="side reveal">
          <p class="eyebrow">Governance Services</p>
          <h2>董事會績效評估<br>外部評估服務</h2>
          <p class="note">服務窗口：許小姐・(02) 2381-9248</p>
        </div>
        <div>
          <div class="prose reveal">
            <p>依《上市上櫃公司治理實務守則》第三十七條與《董事會績效評估辦法》，以務實且高效的方式協助企業落實公司治理、促進董事會管理效能。</p>
          </div>
          <div class="benefit-rows reveal" style="margin-top: 24px;">
            <div><dt>實務</dt><dd>專業團隊依最新公司治理 3.0──永續發展藍圖提供實務建議</dd></div>
            <div><dt>高效</dt><dd>符合規範並配合董監事時程，高效進行評估程序</dd></div>
            <div><dt>實惠</dt><dd>以最實惠的價格、最便利的流程獲得最佳實務結果；團體會員另享 85 折</dd></div>
            <div><dt>提升公司治理服務</dt><dd>透過治理評鑑執行公司治理總體檢，取得明確改善方向；團體會員另享 8 折</dd></div>
          </div>
        </div>
      </div>

      <div class="page-split">
        <div class="side reveal">
          <p class="eyebrow">Join</p>
          <h2>準備好加入了嗎？</h2>
        </div>
        <div class="reveal">
          <p class="prose" style="max-width: 36em; color: var(--ink-64);">現在加入即享本會主辦課程優惠。申請經審核後，將收到入會確認單與匯款資訊。</p>
          <p style="margin-top: 24px; display: flex; gap: 20px; flex-wrap: wrap; align-items: center;">
            <a class="btn btn-primary" href="join.html">前往加入會員 <span class="arrow" aria-hidden="true">→</span></a>
            <a class="arrow-link u-link" href="partners.html">了解贊助方案</a>
          </p>
        </div>
      </div>

    </div>
  </section>''')

# ============================== partners.html ==============================
pages["partners.html"] = ("合作夥伴", "TIRI 年度大會贊助單位、會員優惠合作夥伴與贊助方案。", "partners", hero(
    "Partners & Sponsors", "合作夥伴",
    "年度大會贊助單位、會員專屬優惠合作夥伴，以及企業贊助方案。") + '''

  <section class="page-section">
    <div class="container">
      <div class="partners-wall reveal" style="padding-block: clamp(28px, 4vw, 44px);">
        <span aria-label="KPMG 安侯建業"><img src="../images/partner-kpmg.jpg" alt="KPMG 安侯建業"></span>
        <span aria-label="PwC 資誠"><img src="../images/partner-pwc.png" alt="PwC 資誠"></span>
        <span aria-label="CMoney 全曜財經資訊"><img src="../images/partner-cmoney.png" alt="CMoney 全曜財經資訊"></span>
        <span aria-label="MZ Asia"><img src="../images/partner-mz.png" alt="MZ Asia"></span>
        <span aria-label="精彩創意 TheICONS"><img src="../images/partner-theicons.jpg" alt="精彩創意 TheICONS"></span>
      </div>

      <div class="page-split">
        <div class="side reveal">
          <p class="eyebrow">Benefit Partners</p>
          <h2>會員優惠合作夥伴</h2>
          <p class="note">優惠內容詳見<a class="u-link" href="membership.html#benefits">會員專屬優惠</a>。</p>
        </div>
        <div class="benefit-rows reveal">
          <div><dt>MZ Asia</dt><dd>投資人關係管理和資本市場情報系統、線上法說會、網站建置</dd></div>
          <div><dt>雲翻譯</dt><dd>法說會資料、股東會年報、議事手冊、重大訊息等多國語言翻譯</dd></div>
          <div><dt>精彩創意整合行銷</dt><dd>線上法說會服務與媒體、行銷專業顧問</dd></div>
          <div><dt>Notified</dt><dd>財報新聞稿發布、線上法說會、投資人關係網站、吹哨者平台</dd></div>
          <div><dt>倍力資訊</dt><dd>碳盤查工具 Carbonkeeper（碳管家）</dd></div>
          <div><dt>商業周刊</dt><dd>企業故事採訪、平面雜誌與數位專題加值宣傳</dd></div>
          <div><dt>旅居文旅集團</dt><dd>旅居文旅、旅居驛站、台灣青旅膠囊旅店住宿優惠</dd></div>
          <div><dt>Hi 家教</dt><dd>線上語言課程</dd></div>
          <div><dt>找到了旅行社</dt><dd>國外團體旅遊行程</dd></div>
          <div><dt>英特內軟體</dt><dd>S-HR 策略性人力資源系統、永續報告書平台</dd></div>
        </div>
      </div>

      <div class="page-split" id="sponsor">
        <div class="side reveal">
          <p class="eyebrow">Sponsorship</p>
          <h2>贊助方案</h2>
          <p class="note">贊助單位之商標與名稱，將揭露於本會網站、實體活動看板與各式廣宣稿。</p>
        </div>
        <div class="fee-cards" style="margin-top: 0; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));" data-reveal-group>
          <div class="fee-card reveal">
            <p class="type">Gold Sponsor</p>
            <h3>年度贊助</h3>
            <p class="price">NT$300<span>萬</span></p>
            <ul>
              <li>成為「唯一」Gold Sponsor，具產業排他性</li>
              <li>於國際組織、主管機關交流等重要活動中致詞發聲</li>
              <li>指派窗口對接，積極參與本會相關活動</li>
            </ul>
          </div>
          <div class="fee-card reveal">
            <p class="type">Silver Sponsor</p>
            <h3>年度贊助</h3>
            <p class="price">NT$100<span>萬</span></p>
            <ul>
              <li>指派窗口對接，積極參與本會相關活動</li>
              <li>商標與名稱揭露於網站、活動看板與廣宣稿</li>
            </ul>
          </div>
          <div class="fee-card reveal">
            <p class="type">Other Sponsor</p>
            <h3>年度贊助</h3>
            <p class="price">NT$20<span>萬</span></p>
            <ul>
              <li>商標與名稱揭露於網站、活動大型看板與廣宣稿</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="page-split">
        <div class="side reveal">
          <p class="eyebrow">Contact</p>
          <h2>成為合作夥伴</h2>
        </div>
        <div class="reveal">
          <p class="prose" style="max-width: 36em; color: var(--ink-64);">歡迎與秘書處聯繫，討論贊助與合作方案。</p>
          <p style="margin-top: 24px; display: flex; gap: 20px; flex-wrap: wrap; align-items: center;">
            <a class="btn btn-primary" href="mailto:office@tiri.tw">聯絡秘書處 <span class="arrow" aria-hidden="true">→</span></a>
            <span class="mono-meta">(02) 2381-9248・office@tiri.tw</span>
          </p>
        </div>
      </div>

    </div>
  </section>''')

# ============================== join.html ==============================
pages["join.html"] = ("加入會員", "加入 TIRI 台灣投資人關係協會：申請流程、入會表單與匯款資訊。", "membership", hero(
    "Join TIRI", "加入會員",
    "本會收到申請後將盡速審核，並傳送入會確認單至您的信箱；請於收到確認單後匯款，並將匯款證明 email 至 office@tiri.tw。",
    "現在加入享主辦課程優惠：團體會員到府授課 2 次或公開班 60 小時免費；個人會員 6 小時免費。") + '''

  <section class="page-section">
    <div class="container">

      <div class="page-split">
        <div class="side reveal">
          <p class="eyebrow">Application</p>
          <h2>申請個人預備會員</h2>
          <p class="note">＊個人首次入會會費為 NT$8,000（入會費 2,000＋常年會費 6,000），隔年起每年 NT$6,000；一次繳足十年常年會費 NT$60,000 即為個人永久會員。</p>
        </div>
        <form class="reveal" aria-label="申請個人預備會員" data-demo-form>
          <div class="form-grid">
            <div class="field"><label>姓名<span class="req">*</span></label><input type="text" name="name" required></div>
            <div class="field"><label>公司名稱<span class="req">*</span></label><input type="text" name="company" required></div>
            <div class="field"><label>部門<span class="req">*</span></label><input type="text" name="dept" required></div>
            <div class="field"><label>職稱<span class="req">*</span></label><input type="text" name="title" required></div>
            <div class="field"><label>聯絡電話<span class="req">*</span></label><input type="tel" name="phone" required></div>
            <div class="field"><label>電子郵件<span class="req">*</span></label><input type="email" name="email" required></div>
            <div class="field"><label>Line／WeChat ID</label><input type="text" name="lineid"></div>
            <div class="field"><label>推薦人<span class="req">*</span></label><input type="text" name="referrer" required></div>
            <div class="field"><label>收據抬頭<span class="req">*</span></label><input type="text" name="receipt" required></div>
            <div class="field"><label>統一編號／身分證字號<span class="req">*</span></label><input type="text" name="taxid" required></div>
            <div class="field full"><label>聯絡地址<span class="req">*</span></label><input type="text" name="address" required></div>
            <div class="field"><label>申請會期<span class="req">*</span></label>
              <select name="period"><option>一年</option><option>永久（十年會費一次繳納）</option></select>
            </div>
            <div class="field"><label>繳交方式<span class="req">*</span></label>
              <select name="payment"><option>匯款</option></select>
            </div>
          </div>
          <p style="margin-top: 24px;"><button class="btn btn-primary" type="submit">提交申請 <span class="arrow" aria-hidden="true">→</span></button></p>
          <p class="form-note" style="margin-top: 12px;">本頁為改版設計示意，表單不會實際送出。</p>
        </form>
      </div>

      <div class="page-split" id="group">
        <div class="side reveal">
          <p class="eyebrow">Forms</p>
          <h2>正式會員與團體會員</h2>
          <p class="note">正式會員與預備會員權益完全相等，惟正式會員須出席會員大會並參與理監事改選投票；若公務繁忙，建議申請預備會員。</p>
        </div>
        <div>
          <div class="prose reveal">
            <p>申請個人正式會員或團體會員者，請下載入會申請表，填妥後郵寄至：<strong>台灣投資人關係協會－秘書處收</strong>（台北市中正區重慶南路一段 57 號 13 樓之 13）。</p>
          </div>
          <div class="reveal" style="margin-top: 20px;">
            <div class="download-row">
              <span class="name">個人正式會員_入會申請表.docx<small>File Size: 207 KB</small></span>
              <a class="btn btn-outline" style="height: 42px; padding: 0 18px; font-size: 14px;" href="https://www.tiri.tw/uploads/1/1/9/9/119925991/%E5%80%8B%E4%BA%BA%E6%AD%A3%E5%BC%8F%E6%9C%83%E5%93%A1_%E5%85%A5%E6%9C%83%E7%94%B3%E8%AB%8B%E8%A1%A8.docx" target="_blank" rel="noopener">下載檔案</a>
            </div>
            <div class="download-row">
              <span class="name">團體會員_入會申請表.docx<small>File Size: 208 KB</small></span>
              <a class="btn btn-outline" style="height: 42px; padding: 0 18px; font-size: 14px;" href="https://www.tiri.tw/uploads/1/1/9/9/119925991/%E5%9C%98%E9%AB%94%E6%9C%83%E5%93%A1_%E5%85%A5%E6%9C%83%E7%94%B3%E8%AB%8B%E8%A1%A8.docx" target="_blank" rel="noopener">下載檔案</a>
            </div>
          </div>
        </div>
      </div>

      <div class="page-split">
        <div class="side reveal">
          <p class="eyebrow">Payment</p>
          <h2>匯款資訊</h2>
        </div>
        <div class="info-block reveal" style="max-width: 520px;">
          <dl>
            <div><dt>銀行</dt><dd>國泰世華商業銀行 中山分行（銀行代號 013）</dd></div>
            <div><dt>戶名</dt><dd>社團法人台灣投資人關係協會</dd></div>
            <div><dt>帳號</dt><dd>042-03-500850-5</dd></div>
            <div><dt>銀行地址</dt><dd>台北市中山北路三段 47 號</dd></div>
          </dl>
        </div>
      </div>

    </div>
  </section>''')

# ============================== login.html ==============================
pages["login.html"] = ("會員登入", "TIRI 會員專區登入。", "membership", '''
  <div class="auth-wrap container">
    <div class="auth-card reveal">
      <p class="eyebrow">Member Area</p>
      <h1>會員登入</h1>
      <p class="lede">登入會員專區，查看課程時數、優惠與活動報名。</p>
      <form data-demo-form>
        <div class="field"><label>電子郵件</label><input type="email" name="email" autocomplete="username" required></div>
        <div class="field"><label>密碼</label><input type="password" name="password" autocomplete="current-password" required></div>
        <button class="btn btn-primary" type="submit" style="width: 100%;">登入</button>
      </form>
      <div class="aux">
        <span style="opacity:.6">忘記密碼（示意）</span>
        <span>尚未入會？<a class="u-link" href="join.html" style="color: var(--purple);">加入會員</a></span>
      </div>
      <p class="form-note" style="margin-top: 20px;">會員系統為改版設計示意，尚未串接。</p>
    </div>
  </div>''')

# ============================== search.html ==============================
pages["search.html"] = ("站內搜尋", "搜尋 TIRI 網站內容。", "knowledge", '''
  <div class="auth-wrap container">
    <div class="auth-card reveal" style="width: min(560px, 100%);">
      <p class="eyebrow">Search</p>
      <h1>站內搜尋</h1>
      <p class="lede">搜尋課程、活動、文章與會員資訊。</p>
      <form data-demo-form>
        <div class="field"><label>關鍵字</label><input type="search" name="q" placeholder="例如：IRC、董監事進修、年度大會"></div>
        <button class="btn btn-primary" type="submit" style="width: 100%;">搜尋</button>
      </form>
      <div class="aux" style="flex-wrap: wrap; gap: 8px;">
        <span style="color: var(--ink-45);">常用捷徑：</span>
        <a class="u-link" href="events.html#tiric">TIRIC 實戰班</a>
        <a class="u-link" href="events.html#irc">IRC 證照</a>
        <a class="u-link" href="join.html">加入會員</a>
      </div>
      <p class="form-note" style="margin-top: 20px;">站內搜尋為改版設計示意，尚未串接。</p>
    </div>
  </div>''')

for fname, (title, desc, active, content) in pages.items():
    (OUT / fname).write_text(shell(title, desc, active, content), encoding="utf-8")
    print("wrote", fname)
