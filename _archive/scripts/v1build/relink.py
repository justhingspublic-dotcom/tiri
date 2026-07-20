#!/usr/bin/env python3
"""Point curated V1 pages at the real converted inner pages."""
import pathlib, re
from bs4 import BeautifulSoup

ROOT = pathlib.Path("/Users/jonathanyu/Desktop/Travail/投資人協會 TIRI/WEB DEMO")
SRC = ROOT / "original" / "html"
OUT = ROOT / "v1" / "html"

def norm(t):
    return re.sub(r"[\s　・‧．\.、，,：:；;！!？?（）()【】\[\]「」\-—–─/／]+", "", t)

# build text->href map from original list pages
anchor_map = []
for lp in ["news-387131.html", "irupdatestc.html", "news-971146.html", "news.html", "news-121049.html"]:
    soup = BeautifulSoup((SRC / lp).read_text(encoding="utf-8", errors="replace"), "html.parser")
    main = soup.select_one("#wsite-content")
    if not main:
        continue
    for a in main.find_all("a"):
        href = a.get("href", "")
        text = norm(a.get_text())
        if href.endswith(".html") and not href.startswith("http") and len(text) >= 4:
            anchor_map.append((text, href.split("/")[-1]))

def find(sub):
    key = norm(sub)
    for text, href in anchor_map:
        if key in text or text in key:
            return href
    return None

# --- direct known targets ---
T2025 = "seminar181023-720761-875714-576604-415060-555931-912810-913907.html"
recap_targets = {
    "2025": find("2025年度大會") or T2025,
    "2024": find("2024年度大會"),
    "2023": find("2023年度大會"),
    "2022": find("2022年度大會"),
    "2021": find("2021年度大會") or find("TheFutureofESG"),
    "2020": find("2020年度大會"),
    "2019大會": find("2019年度大會"),
    "2018": find("2018成立大會") or find("成立大會暨大師論壇"),
}
print("recap:", recap_targets)

article_targets = {
    "疫起面對": find("疫起面對"),
    "IR證照": find("IR證照台灣IRO"),
    "批判性思維": find("批判性思維"),
    "機構法人經營實例分析（下）": find("機構法人經營實例分析下"),
    "機構法人經營實例分析（上）": find("機構法人經營實例分析上"),
    "IRO必須知道": find("IRO必須知道"),
    "跨部門溝通與資訊整合（下）": find("跨部門溝通與資訊整合下"),
    "跨部門溝通與資訊整合（上）": find("跨部門溝通與資訊整合上"),
    "對誰說": find("對誰說"),
    "工作內容（下）": find("IRO的工作內容下"),
    "工作內容（上）": find("IRO的工作內容上"),
    "重要性": find("投資人關係對上市櫃企業的重要性"),
    "年財報英文化": find("年財報英文化"),
    "ESG與EPS": find("ESGEPS") or find("ESG與EPS"),
    "公共關係": find("等同沒做好公共關係"),
    "最佳溝通者": find("資本市場最佳溝通者"),
    "霹靂": find("霹靂"),
    "為何臺灣上市": find("為何臺灣上市"),
    "劉詩亮": find("籌資遇困境"),
    "COVID": find("COVID"),
    "ESG評比": find("備受矚目"),
    "企業文化之價值": find("企業文化之價值"),
    "參與董事會及報告": find("IRO如何參與董事會"),
    "成功IRO": find("成功IRO"),
    "高階主管異動": find("高階主管異動"),
    "佔有一席之地": find("佔有一席之地"),
}
print("articles missing:", [k for k, v in article_targets.items() if not v])

news_targets = {
    "9～12月": find("912月投資人關係實務課程") or find("投資人關係實務課程"),
    "竹科管理局": find("竹科管理局"),
    "智財管理新思惟": find("智財管理新思惟"),
    "藝術品": find("藝術品欣賞與投資"),
    "盡職治理": find("強化機構投資人盡職治理"),
    "韓國機票": find("韓國機票"),
    "併購實務大解析": find("國內外併購實務大解析") or find("731雙主題"),
    "公司治理主管系列課程": find("公司治理主管系列課程"),
    "越南": find("越南"),
    "新媒體時代": find("新媒體時代") or find("530雙主題"),
    "股權到經營權": find("股權到經營權"),
    "MZ Asia「IR說明會」": find("MZAsia"),
    "集保": find("投資人關係整合平台"),
    "國際接軌": find("台灣資本市場IR與國際接軌"),
    "紐約證交所": find("紐約證交所"),
    "獲證交所肯定": find("推專業IR獲證交所肯定"),
    "內政部核准立案": find("內政部核准立案"),
    "成立大會暨第一屆會員大會": find("成立大會暨第一屆會員大會"),
}
print("news missing:", [k for k, v in news_targets.items() if not v])

def sub_file(name, pairs, listname=""):
    p = OUT / name
    s = p.read_text(encoding="utf-8")
    n = 0
    for old, new in pairs:
        if old in s:
            s = s.replace(old, new)
            n += 1
    p.write_text(s, encoding="utf-8")
    print(f"{name}: {n}/{len(pairs)} replacements")

# ---------- index.html ----------
idx_pairs = []
# featured 焦點訊息 → 2025 大會頁
idx_pairs.append(('<a class="event-featured reveal" href="events.html">', f'<a class="event-featured reveal" href="{T2025}">'))
# recap strip
for label, key in [("2024 共創 IR 新紀元","2024"),("2023 國際論壇","2023"),("2022 第一屆台灣投資人關係大獎","2022"),("2021 The Future of ESG is NOW","2021"),("2020 IR 獎項啟動典禮","2020"),("2019 亞洲投資人關係連結","2019大會"),("2018 成立大會暨大師論壇","2018")]:
    if recap_targets.get(key):
        idx_pairs.append((f'<a href="events.html#recap">{label}</a>', f'<a href="{recap_targets[key]}">{label}</a>'))
# insight cards → real articles
card_map = [
    ("疫起面對，有效管理的媒體溝通策略", article_targets["疫起面對"]),
    ("IR 證照，台灣 IRO 邁向專業化之途？", article_targets["IR證照"]),
    ("投資人關係經理人如何在董事會佔有一席之地", article_targets["佔有一席之地"]),
    ("備受矚目的 ESG 評比", article_targets["ESG評比"]),
    ("ESG 與 EPS 同樣重要！非財務績效表現將影響投資人決策", article_targets["ESG與EPS"]),
    ("專訪創會理事長沈馥馥：中華電信代理發言人的 IR 之路", "exclusive-interview-ndash-founding-chairman-fu-fu-shen.html"),
]
s = (OUT/"index.html").read_text(encoding="utf-8")
for title, href in card_map:
    if href:
        s = s.replace(f'<a class="insight-card reveal" href="knowledge.html" data-category', f'<a class="insight-card reveal" href="__PENDING__" data-category', 1) if False else s
# simpler: replace per-card via title anchor
for title, href in card_map:
    if not href: continue
    pat = re.compile(r'(<a class="insight-card reveal" href=")knowledge\.html("[^>]*>\s*<span class="meta">.*?<h3>' + re.escape(title) + r'</h3>)', re.S)
    s = pat.sub(lambda m: m.group(1) + href + m.group(2), s)
# homepage news items → matched targets, unmatched → news.html list
home_news = [
    ("【TIRI 課程】9～12 月投資人關係實務課程", news_targets["9～12月"]),
    ("TIRI 與竹科管理局共同推動 IR 專業", news_targets["竹科管理局"]),
    ("紐約證交所、美國 IR 協會高層來台參加 TIRI 年度大會暨大師論壇", news_targets["紐約證交所"]),
    ("通過內政部核准立案", news_targets["內政部核准立案"]),
]
for title, href in home_news:
    if not href: continue
    pat = re.compile(r'(<a class="event-item reveal" href=")news\.html("><span class="date">[^<]*<span class="yr">[^<]*</span></span><span><h3>' + re.escape(title) + r'</h3>)')
    s = pat.sub(lambda m: m.group(1) + href + m.group(2), s)
(OUT/"index.html").write_text(s, encoding="utf-8")
print("index.html relinked")

# ---------- events.html ----------
s = (OUT/"events.html").read_text(encoding="utf-8")
s = s.replace('<a class="event-featured reveal" href="#recap">', f'<a class="event-featured reveal" href="{T2025}">')
for label, key in [("2025 年度大會暨引領 IR 智慧新時代","2025"),("2024 年度大會暨共創 IR 新紀元","2024"),("2023 年度大會暨國際論壇","2023"),("2022 年度大會暨第一屆台灣投資人關係大獎","2022"),("2021 年度大會──The Future of ESG is NOW","2021"),("2020 年度大會暨台灣投資人關係獎項啟動典禮","2020"),("2019 年度大會暨亞洲投資人關係連結","2019大會"),("2018 成立大會暨大師論壇","2018")]:
    href = recap_targets.get(key)
    if href:
        pat = re.compile(r'(<a class="event-item reveal" href=")#("><span class="date">[^<]*<span class="yr">[^<]*</span></span><span><h3>' + re.escape(label) + r'</h3>)')
        s = pat.sub(lambda m: m.group(1) + href + m.group(2), s)
# TIRIC / 進修 / IRC 深入頁
s = s.replace('<p class="cta"><a class="btn btn-invert" href="join.html">報名與洽詢', '<p class="cta"><a class="btn btn-invert" href="tiric.html">課程詳情與報名')
s = s.replace('<h2>董監事與公司治理主管進修</h2>', '<h2>董監事與公司治理主管進修</h2><p class="note" style="margin-top:8px"><a class="u-link" href="trainbod.html">查看完整課程頁 →</a></p>')
s = s.replace('<h2>IRC 國際證照</h2>', '<h2>IRC 國際證照</h2><p class="note" style="margin-top:8px"><a class="u-link" href="certification.html">查看完整證照頁 →</a>　<a class="u-link" href="scholarshipirc.html">獎學金辦法 →</a></p>')
s = s.replace('<h2>獎項</h2>', '<h2>獎項</h2><p class="note" style="margin-top:8px"><a class="u-link" href="mission-206783.html">TIRI Awards →</a>　<a class="u-link" href="mission-206783-766399.html">潛力進展獎 →</a></p>')
(OUT/"events.html").write_text(s, encoding="utf-8")
print("events.html relinked")

# ---------- knowledge.html ----------
s = (OUT/"knowledge.html").read_text(encoding="utf-8")
kn_titles = {
    "疫起面對，有效管理的媒體溝通策略": article_targets["疫起面對"],
    "批判性思維在投資人溝通過程中的重要性": article_targets["批判性思維"],
    "機構法人經營實例分析（下）": article_targets["機構法人經營實例分析（下）"],
    "機構法人經營實例分析（上）": article_targets["機構法人經營實例分析（上）"],
    "IR 證照，台灣 IRO 邁向專業化之途？": article_targets["IR證照"],
    "IRO 必須知道的基本財務知識": article_targets["IRO必須知道"],
    "跨部門溝通與資訊整合（下）": article_targets["跨部門溝通與資訊整合（下）"],
    "跨部門溝通與資訊整合（上）": article_targets["跨部門溝通與資訊整合（上）"],
    "投資人關係溝通策略：對誰說？說什麼？怎麼說？": article_targets["對誰說"],
    "投資人關係長（IRO）的工作內容（下）": article_targets["工作內容（下）"],
    "投資人關係長（IRO）的工作內容（上）": article_targets["工作內容（上）"],
    "投資人關係對上市櫃企業的重要性": article_targets["重要性"],
    "上市櫃企業年財報英文化常見問題": article_targets["年財報英文化"],
    "ESG 與 EPS 同樣重要！非財務績效表現將影響投資人決策": article_targets["ESG與EPS"],
    "企業沒建立良好投資人關係，等同沒做好公共關係": article_targets["公共關係"],
    "IR 投資人關係：資本市場最佳溝通者": article_targets["最佳溝通者"],
    "肩負傳統走向創新──霹靂用投資人關係展現文創價值": article_targets["霹靂"],
    "為何臺灣上市（櫃）公司應重視投資人關係（IR）": article_targets["為何臺灣上市"],
    "投資人關係專家劉詩亮：籌資遇困境 企業先惦惦自己斤兩": article_targets["劉詩亮"],
    "如何在 COVID-19 期間，持續執行投資人關係計畫": article_targets["COVID"],
    "備受矚目的 ESG 評比": article_targets["ESG評比"],
    "企業文化之價值": article_targets["企業文化之價值"],
    "IRO 如何參與董事會及報告": article_targets["參與董事會及報告"],
    "投資人關係經理人如何在董事會佔有一席之地": article_targets["佔有一席之地"],
    "專訪創會理事長沈馥馥：中華電信代理發言人的 IR 之路": "exclusive-interview-ndash-founding-chairman-fu-fu-shen.html",
}
hit = 0
for title, href in kn_titles.items():
    if not href: continue
    pat = re.compile(r'(<a class="insight-card reveal" href=")#("[^>]*>\s*<span class="meta">.*?<h3>' + re.escape(title) + r'</h3>)', re.S)
    s2 = pat.sub(lambda m: m.group(1) + href + m.group(2), s)
    if s2 != s: hit += 1
    s = s2
# 成功IRO 的秘訣 / 高階主管異動 (NIRI without match fallback → irupdatestc.html)
for title in ["成功 IRO 的秘訣", "高階主管異動，IR 的應對工作"]:
    key = {"成功 IRO 的秘訣": "成功IRO", "高階主管異動，IR 的應對工作": "高階主管異動"}[title]
    href = article_targets.get(key) or "irupdatestc.html"
    pat = re.compile(r'(<a class="insight-card reveal" href=")#("[^>]*>\s*<span class="meta">.*?<h3>' + re.escape(title) + r'</h3>)', re.S)
    s = pat.sub(lambda m: m.group(1) + href + m.group(2), s)
# 年刊 rows → converted pages links added next to PDF buttons
s = s.replace('<span class="name">2025 TIRI 7 周年年刊', '<span class="name"><a class="u-link" href="7th_report-848158-214091.html">2025 TIRI 7 周年年刊</a>')
s = s.replace('<span class="name">2024 TIRI 6 周年年刊', '<span class="name"><a class="u-link" href="5th_report-848158.html">2024 TIRI 6 周年年刊</a>')
s = s.replace('<span class="name">TIRI 5 周年年刊', '<span class="name"><a class="u-link" href="5th_report.html">TIRI 5 周年年刊</a>')
# any remaining # cards → 知識分享 list page
s = s.replace('<a class="insight-card reveal" href="#"', '<a class="insight-card reveal" href="news-387131.html"')
(OUT/"knowledge.html").write_text(s, encoding="utf-8")
print(f"knowledge.html relinked ({hit} direct)")

# ---------- news.html ----------
s = (OUT/"news.html").read_text(encoding="utf-8")
news_titles = {
    "【TIRI 課程】9～12 月投資人關係實務課程": news_targets["9～12月"],
    "TIRI 與竹科管理局共同推動 IR 專業": news_targets["竹科管理局"],
    "【TIRI 課程】智財管理新思惟──運用 AI 智能平台協助智財管理": news_targets["智財管理新思惟"],
    "【TIRI 講座】藝術品欣賞與投資": news_targets["藝術品"],
    "簡世雄、黃英記理事代表參加證交所「強化機構投資人盡職治理與上市公司投資人關係」論壇": news_targets["盡職治理"],
    "【TIRI 會員福利】4 天 3 夜免費韓國機票、住宿、翻譯": news_targets["韓國機票"],
    "【7/31 雙主題講座】國內外併購實務大解析／ESG、年報雙語化趨勢與重要性": news_targets["併購實務大解析"],
    "公司治理主管系列課程：7/17（台北）、7/29（新竹）、7/31（台南）": news_targets["公司治理主管系列課程"],
    "新興市場崛起中的越南：台商面向資本市場更要強化投資人關係": news_targets["越南"],
    "【5/30 雙主題講座】新媒體時代的思維／成功發言系列": news_targets["新媒體時代"],
    "TIRI 受邀擔任證交所「股權到經營權，IR 核心策略座談會」分享嘉賓": news_targets["股權到經營權"],
    "TIRI 受邀擔任 MZ Asia「IR 說明會」開幕致詞嘉賓": news_targets["MZ Asia「IR說明會」"],
    "TIRI 受邀出席集保「投資人關係整合平台」成立大會": news_targets["集保"],
    "台灣資本市場 IR 與國際接軌": news_targets["國際接軌"],
    "紐約證交所、美國 IR 協會高層來台參加 TIRI 年度大會暨大師論壇": news_targets["紐約證交所"],
    "台灣投資人關係協會推專業 IR 獲證交所肯定": news_targets["獲證交所肯定"],
    "通過內政部核准立案": news_targets["內政部核准立案"],
    "成立大會暨第一屆會員大會、理監事選舉": news_targets["成立大會暨第一屆會員大會"],
}
linked = 0
for title, href in news_titles.items():
    pat = re.compile(r'<a class="event-item reveal" href="#"><span class="date">([^<]*)<span class="yr">([^<]*)</span></span><span><h3>' + re.escape(title) + r'</h3></span><span class="go" aria-hidden="true">→</span></a>')
    if href:
        s = pat.sub(lambda m: f'<a class="event-item reveal" href="{href}"><span class="date">{m.group(1)}<span class="yr">{m.group(2)}</span></span><span><h3>{title}</h3></span><span class="go" aria-hidden="true">→</span></a>', s)
        linked += 1
    else:
        s = pat.sub(lambda m: f'<div class="event-item reveal"><span class="date">{m.group(1)}<span class="yr">{m.group(2)}</span></span><span><h3>{title}</h3></span><span></span></div>', s)
(OUT/"news.html").write_text(s, encoding="utf-8")
print(f"news.html relinked ({linked} linked)")

# ---------- about.html ----------
s = (OUT/"about.html").read_text(encoding="utf-8")
s = s.replace('<p class="note">本會於 2026 年 3 月 20 日召開會員大會選出第三屆理、監事。</p>',
              '<p class="note">本會於 2026 年 3 月 20 日召開會員大會選出第三屆理、監事。<br>歷屆名單：<a class="u-link" href="team2018.html">第一屆</a>・<a class="u-link" href="team2022.html">第二屆</a></p>')
s = s.replace('<h2>鄧白氏企業認證™雙標章</h2>', '<h2>鄧白氏企業認證™雙標章</h2><p class="note" style="margin-top:8px"><a class="u-link" href="certificate.html">查看認證頁與證書 →</a></p>')
s = s.replace('<h2>功能與服務</h2>', '<h2>功能與服務</h2><p class="note" style="margin-top:8px"><a class="u-link" href="services.html">原站服務頁 →</a></p>')
(OUT/"about.html").write_text(s, encoding="utf-8")
print("about.html relinked")

# ---------- membership.html ----------
s = (OUT/"membership.html").read_text(encoding="utf-8")
s = s.replace('<h2>會員專屬優惠</h2>', '<h2>會員專屬優惠</h2><p class="note" style="margin-top:8px"><a class="u-link" href="benefit.html">完整優惠條款 →</a></p>')
s = s.replace('<h2>董事會績效評估<br>外部評估服務</h2>', '<h2>董事會績效評估<br>外部評估服務</h2><p class="note" style="margin-top:8px"><a class="u-link" href="bodperform.html">董事會績效評估 →</a>　<a class="u-link" href="corpperform.html">提升公司治理服務 →</a></p>')
(OUT/"membership.html").write_text(s, encoding="utf-8")
print("membership.html relinked")

# ---------- 手動補丁（relink 規則涵蓋不到，之前每次重跑都得手動回補，改在此自動化） ----------
# 1. knowledge.html：第一張雙月刊卡指向真實文章頁
s = (OUT/"knowledge.html").read_text(encoding="utf-8")
old = '<a class="insight-card reveal" href="news-387131.html" data-category="bimonthly">'
new = '<a class="insight-card reveal" href="191118.html" data-category="bimonthly">'
if old in s:
    s = s.replace(old, new, 1)
    (OUT/"knowledge.html").write_text(s, encoding="utf-8")
    print("knowledge.html patched (bimonthly → 191118.html)")

# 2. news.html：5/30 雙主題講座改為可點連結
s = (OUT/"news.html").read_text(encoding="utf-8")
title = "【5/30 雙主題講座】新媒體時代的思維／成功發言系列"
old = ('<div class="event-item reveal"><span class="date">05.30<span class="yr">2019</span></span>'
       f'<span><h3>{title}</h3></span><span></span></div>')
new = ('<a class="event-item reveal" href="news-121049.html"><span class="date">05.30<span class="yr">2019</span></span>'
       f'<span><h3>{title}</h3></span><span class="go" aria-hidden="true">→</span></a>')
if old in s:
    s = s.replace(old, new, 1)
    (OUT/"news.html").write_text(s, encoding="utf-8")
    print("news.html patched (5/30 講座 → news-121049.html)")
