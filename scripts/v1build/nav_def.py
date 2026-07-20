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
