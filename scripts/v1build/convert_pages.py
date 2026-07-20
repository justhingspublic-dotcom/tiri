#!/usr/bin/env python3
"""Convert every original tiri.tw page into the V1 shell (legacy content kept intact)."""
import pathlib
import re
import shutil
from bs4 import BeautifulSoup

ROOT = pathlib.Path("/Users/jonathanyu/Desktop/Travail/投資人協會 TIRI/WEB DEMO")
SRC = ROOT / "original" / "html"
OUT = ROOT / "v1" / "html"
IMG_SRC = ROOT / "original" / "images"
IMG_OUT = ROOT / "v1" / "images"
CSS_OUT = ROOT / "v1" / "css"

# curated pages own these filenames; original content is already fully represented there
SKIP = {"index.html", "membership.html", "join.html", "news.html"}

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


SECTION_RULES = [
    (r"^(mission|team|committee|certificate|services|contact|exclusive-interview)", ("about", "About TIRI")),
    (r"^(seminar|trainbod|tiric|certification|scholarshipirc|benefit|bodperform|corpperform)", None),  # refined below
]

def section_for(name: str):
    if re.match(r"^(team|committee|certificate|services|contact|mission_en)", name):
        return "about", "About TIRI"
    if name.startswith("mission"):
        return "about", "About TIRI"
    if name.startswith("exclusive-interview"):
        return "knowledge", "IR Knowledge"
    if re.match(r"^(seminar|trainbod|tiric|certification|scholarshipirc)", name):
        return "events", "Events & Programs"
    if re.match(r"^(benefit|bodperform|corpperform)", name):
        return "membership", "Membership"
    if re.match(r"^(news-971146)", name):
        return "events", "Past Events"
    if re.match(r"^(news-387131|irupdatestc|5th_report|6th_report|7th_report|191118|2019|2020|2356|3931|101712)", name):
        return "knowledge", "IR Knowledge"
    if name.startswith("news"):
        return "news", "Latest News"
    if name.startswith("en") or name.endswith("_en.html") or "_en-" in name:
        return None, "English"
    return None, "TIRI"

def shell(title, desc, active, content, lang="zh-Hant", extra_css=""):
    nav_items = build_nav_items(active)
    drawer_items = build_drawer_items()
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}｜台灣投資人關係協會 TIRI</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="../fonts/fonts.css">
<link rel="stylesheet" href="../css/main.css">{extra_css}
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

copied = set()

def copy_image(rel):
    """rel like ../images/xxx — copy from original to v1 keeping the filename."""
    name = rel.split("/")[-1].split("?")[0]
    src = IMG_SRC / name
    if name in copied:
        return
    if src.exists():
        dst = IMG_OUT / name
        if not dst.exists():
            shutil.copy2(src, dst)
        copied.add(name)

def process(fp: pathlib.Path):
    html = fp.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    raw_title = title_tag.get_text() if title_tag else fp.stem
    title = re.sub(r"\s*-\s*台灣投資人關係協會\s*$", "", raw_title).strip() or fp.stem

    main = soup.select_one("#wsite-content")
    if main is None:
        return None

    for bad in main.select("script, style, noscript"):
        bad.decompose()

    # rewrite/collect asset references
    for img in main.find_all("img"):
        src = img.get("src", "")
        if src.startswith("../images/"):
            copy_image(src)
        img["loading"] = "lazy"
        srcset = img.get("srcset")
        if srcset:
            for part in srcset.split(","):
                url = part.strip().split(" ")[0]
                if url.startswith("../images/"):
                    copy_image(url)
    for a in main.find_all("a"):
        href = a.get("href", "")
        if href.startswith("../images/"):
            copy_image(href)
        elif href.startswith("../documents/"):
            a["href"] = "../../original/documents/" + href[len("../documents/"):]
            a["target"] = "_blank"
            a["rel"] = "noopener"
        elif href.startswith("http"):
            a["target"] = "_blank"
            a["rel"] = "noopener"

    name = fp.name
    active, eyebrow = section_for(name)
    lang = "en" if (name.startswith("en") or name.endswith("_en.html") or "_en-" in name or name in {"services_en.html", "mission_en.html"}) else "zh-Hant"

    body = main.decode_contents()
    content = f'''  <section class="page-hero">
    <div class="container">
      <p class="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
    </div>
  </section>

  <section class="page-section" style="padding-top: clamp(32px, 5vw, 56px);">
    <div class="container">
      <div class="legacy-body">
{body}
      </div>
    </div>
  </section>'''

    extra = '\n<link rel="stylesheet" href="../css/legacy-inline.css">\n<link rel="stylesheet" href="../css/legacy-content.css">'
    out = shell(title, f"{title}──台灣投資人關係協會。", active, content, lang=lang, extra_css=extra)
    (OUT / name).write_text(out, encoding="utf-8")
    return name

# collect background images referenced by legacy-inline.css and copy the css
inline_css = (ROOT / "original" / "css" / "legacy-inline.css").read_text(encoding="utf-8")
for m in re.finditer(r"url\('\.\./images/([^']+)'\)", inline_css):
    copy_image("../images/" + m.group(1))
(CSS_OUT / "legacy-inline.css").write_text(inline_css, encoding="utf-8")

count = 0
skipped = 0
for fp in sorted(SRC.glob("*.html")):
    if fp.name in SKIP:
        skipped += 1
        continue
    if process(fp):
        count += 1

print(f"converted {count} pages, skipped {skipped} (curated), images copied {len(copied)}")
