"""全站 NAV 定義（單一來源）。build_pages.py 與 convert_pages.py 都從這裡 import。

結構：(href, label, key, groups, feature)
  groups  = [(分組小標, [(href, 標題, 說明), ...]), ...]
  feature = (圖檔, 說明文, CTA 文字, CTA href)  ── 滿寬面板右欄的精選卡

說明文與精選卡文案一律取自各目標頁的真實內容，不得杜撰。
"""

NAV = [
    ("about.html", "關於 TIRI", "about", [
        ("協會", [
            ("about.html", "協會使命", "創會緣起、願景與協會定位"),
            ("team2026.html", "第三屆理監事成員", "現任理監事名單"),
            ("board.html", "歷屆理監事", "第一屆至第三屆名冊"),
            ("about.html#committee", "功能委員會", "各功能委員會的組成"),
        ]),
        ("服務與認證", [
            ("services.html", "功能與服務", "培訓、證照、評鑑、研究調查等 12 項服務"),
            ("certificate.html", "鄧白氏企業認證™", "D-U-N-S® 環球編碼 65-851-5060"),
        ]),
    ], (
        "hero-annual-forum.jpg",
        "專為上市櫃、興櫃、公開發行與創櫃公司經理人而設的專業協會，致力推進台灣投資人關係的實踐。",
        "認識協會", "about.html",
    )),
    ("events.html", "活動課程", "events", [
        ("活動與獎項", [
            ("events.html", "焦點與近期課程", "年度大會、專業課程與國際證照總覽"),
            ("news-971146.html", "精彩回顧", "歷屆年度大會與活動紀錄"),
            ("mission-206783.html", "TIRI Awards", "第四屆已啟動，邀請投資圈與媒體參與"),
            ("mission-206783-766399.html", "TIRI 潛力進展獎", "表揚中小型企業的 IR 進步標竿"),
        ]),
        ("專業課程與證照", [
            ("tiric.html", "TIRIC IR 專業實戰班", "採 NIRI 授權教材繁體中文版"),
            ("trainbod.html", "董監事進修課程", "可折抵董監事與公司治理主管進修時數"),
            ("certification.html", "IRC 國際證照", "NIRI 專業證照，會員報名省 200 美元"),
            ("scholarshipirc.html", "IRC 贊助獎學金", "填寫申請表取得贊助資格"),
        ]),
    ], (
        "event-2025-conference.jpg",
        "2025 年度大會以「智慧驅動未來，IR 共創新時代」為題，呼應數位轉型與 AI 對資本市場的影響。",
        "查看年度大會", "news-971146.html",
    )),
    ("knowledge.html", "知識資源", "knowledge", [
        ("刊物與專欄", [
            ("knowledge.html", "知識總覽", "專欄、精選文章與專訪的完整入口"),
            ("news-387131-325944.html", "證券雙月刊專欄", "證交所「證券服務雙月刊」歷期專欄"),
            ("5th_report-516844.html", "TIRI 年刊", "創始於 2024 年，每年出刊一次"),
        ]),
        ("文章與專訪", [
            ("news-387131-325944-831518.html", "專文分享", "會員與講者的主題分享文章"),
            ("irupdatestc.html", "NIRI IR Update 精選", "2019–2020 與 NIRI 合作中文化的精選文章"),
            ("2356035370-277843933339333297022010738263.html", "專訪 沈馥馥理事長", "專訪中華電信代理發言人沈馥馥協理"),
        ]),
    ], (
        "hero-talk.jpg",
        "證交所「證券服務雙月刊」專欄、NIRI IR Update 精選、專文與專訪──台灣 IR 的知識庫。",
        "前往知識資源", "knowledge.html",
    )),
    ("membership.html", "會員服務", "membership", [
        ("會員", [
            ("membership.html", "會員類別與會費", "個人與團體會員的類別與費用"),
            ("benefit.html", "會員專屬優惠", "課程、證照與治理服務的專屬折扣"),
            ("join.html", "加入會員", "申請流程、入會表單與匯款資訊"),
        ]),
        ("治理服務", [
            ("bodperform.html", "董事會績效評估", "團體會員享 85 折優惠"),
            ("corpperform.html", "提升公司治理服務", "團體會員享 8 折優惠"),
        ]),
    ], (
        "hero-handshake.jpg",
        "個人首次入會 NT$8,000（入會費 2,000＋常年會費 6,000），隔年起每年 NT$6,000。",
        "加入會員", "join.html",
    )),
    ("news.html", "最新消息", "news", [
        ("消息", [
            ("news.html", "協會消息", "協會公告、課程講座與產業參與紀錄"),
            ("news-971146.html", "精彩回顧", "歷屆年度大會與活動現場紀錄"),
        ]),
    ], (
        "hero-recap.jpg",
        "2025/10/23　2025 年度大會暨引領 IR 智慧新時代",
        "看活動回顧", "news-971146.html",
    )),
    ("partners.html", "合作夥伴", "partners", [
        ("夥伴與贊助", [
            ("partners.html", "合作夥伴總覽", "年度大會贊助單位與會員優惠夥伴"),
            ("partners.html#sponsor", "贊助方案", "企業贊助方案說明"),
            ("contact.html", "聯絡我們", "(02) 2381-9248・台北市中正區重慶南路一段 57 號"),
        ]),
    ], (
        "hero-networking.jpg",
        "年度大會贊助單位、會員專屬優惠合作夥伴，以及企業贊助方案。",
        "成為合作夥伴", "partners.html#sponsor",
    )),
]


def flat_subs(groups):
    """攤平分組，供抽屜選單與連結檢查使用。"""
    return [(h, t) for _, rows in groups for h, t, _ in rows]


def build_nav_items(active):
    items = []
    for href, label, key, groups, feature in NAV:
        cur = ' aria-current="page"' if key == active else ""
        cols = []
        for glabel, rows in groups:
            links = "\n".join(
                '                <a class="mega-item" href="%s">'
                '<span class="t">%s</span><span class="d">%s</span></a>' % (h, t, d)
                for h, t, d in rows
            )
            cols.append(
                '              <div class="mega-col">\n'
                '                <span class="mega-overline">%s</span>\n%s\n'
                '              </div>' % (glabel, links)
            )
        # 分組不足兩欄時補一個空欄，讓精選卡固定落在最右
        while len(cols) < 2:
            cols.append('              <div class="mega-col"></div>')
        img, cap, cta, cta_href = feature
        cols.append(
            '              <a class="mega-figure" href="%s">\n'
            '                <img src="../images/%s" alt="" loading="lazy" width="380" height="176">\n'
            '                <span class="cap">%s</span>\n'
            '                <span class="cta">%s <span aria-hidden="true">→</span></span>\n'
            '              </a>' % (cta_href, img, cap, cta)
        )
        items.append(
            '        <li><a href="%s"%s>%s</a>\n'
            '          <div class="menu-panel">\n'
            '            <div class="mega-inner">\n%s\n            </div>\n'
            '          </div>\n'
            '        </li>' % (href, cur, label, "\n".join(cols))
        )
    return "\n".join(items)


def build_drawer_items():
    items = []
    for href, label, key, groups, feature in NAV:
        sublinks = "\n".join(
            '            <a href="%s">%s</a>' % (h, t) for h, t in flat_subs(groups)
        )
        items.append(
            '        <li><a class="d-main" href="%s">%s <span class="arrow" aria-hidden="true">→</span></a>\n'
            '          <div class="subs">\n%s\n          </div>\n'
            '        </li>' % (href, label, sublinks)
        )
    return "\n".join(items)
