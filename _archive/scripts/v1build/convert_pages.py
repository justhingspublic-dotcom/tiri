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

import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from nav_def import NAV, build_nav_items, build_drawer_items  # noqa: E402  單一來源

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

# 分類 → photo header 底圖（先查 (active, eyebrow) 細分，再查 active，最後 fallback）
HERO_IMAGES = {
    ("events", "Past Events"): "hero-recap.jpg",
    "about": "hero-taipei-night.jpg",
    "events": "hero-auditorium.jpg",
    "knowledge": "hero-chart.jpg",
    "membership": "hero-networking.jpg",
    "news": "hero-audience.jpg",
}

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

<svg class="icon-sprite" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">
  <!-- UI 圖示：Lucide v1.25 (ISC)．品牌 glyph：Simple Icons (CC0) -->
  <symbol id="i-search" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m21 21-4.34-4.34"/><circle cx="11" cy="11" r="8"/></symbol>
  <symbol id="i-x" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></symbol>
  <symbol id="i-globe" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></symbol>
  <symbol id="i-chevron-down" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></symbol>
  <symbol id="i-arrow-right" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></symbol>
  <symbol id="i-mail" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7"/><rect x="2" y="4" width="20" height="16" rx="2"/></symbol>
  <symbol id="i-facebook" viewBox="0 0 24 24" fill="currentColor"><path d="M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"/></symbol>
  <symbol id="i-linkedin" viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 3.5C4.98 4.88 3.87 6 2.5 6S0 4.88 0 3.5 1.12 1 2.5 1s2.48 1.12 2.48 2.5zM.32 24h4.37V8.5H.32V24zM8.34 8.5V24h4.36v-8.13c0-4.45 5.6-4.82 5.6 0V24h4.38V14.3c0-7.2-7.9-6.94-9.98-3.4V8.5H8.34z"/></symbol>
  <symbol id="i-line" viewBox="0 0 24 24" fill="currentColor"><path d="M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63h2.386c.346 0 .627.285.627.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .27-.174.51-.432.596-.064.021-.133.031-.199.031-.211 0-.391-.09-.51-.25l-2.443-3.317v2.94c0 .344-.279.629-.631.629-.346 0-.626-.285-.626-.629V8.108c0-.27.173-.51.43-.595.06-.023.136-.033.194-.033.195 0 .375.104.495.254l2.462 3.33V8.108c0-.345.282-.63.63-.63.345 0 .63.285.63.63v4.771zm-5.741 0c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63.346 0 .628.285.628.63v4.771zm-2.466.629H4.917c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.348 0 .63.285.63.63v4.141h1.756c.348 0 .629.283.629.63 0 .344-.282.629-.629.629M24 10.314C24 4.943 18.615.572 12 .572S0 4.943 0 10.314c0 4.811 4.27 8.842 10.035 9.608.391.082.923.258 1.058.59.12.301.079.766.038 1.08l-.164 1.02c-.045.301-.24 1.186 1.049.645 1.291-.539 6.916-4.078 9.436-6.975C23.176 14.393 24 12.458 24 10.314"/></symbol>
  <symbol id="i-youtube" viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></symbol>
</svg>

<header class="site-header" id="site-header">
  <div class="container">
    <a class="wordmark" href="index.html" aria-label="TIRI 台灣投資人關係協會 首頁">
      <span class="mark" aria-hidden="true">TI<span>RI</span></span>
      <span class="name">台灣投資人關係協會</span>
    </a>
    <div class="header-right">
    <nav class="header-top" aria-label="工具列">
      <button class="search-toggle" type="button" aria-expanded="false" aria-controls="search-panel">
        <svg class="icon" width="15" height="15" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-search"/></svg>
        搜尋
      </button>
      <span class="divider" aria-hidden="true"></span>
      <a href="login.html">會員登入</a>
      <span class="divider" aria-hidden="true"></span>
      <span class="social-icons">
        <a href="https://www.facebook.com/tiri2018/" target="_blank" rel="noopener" aria-label="Facebook"><span class="roll"><svg class="icon" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-facebook"/></svg><svg class="icon" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-facebook"/></svg></span></a>
        <a href="https://www.linkedin.com/company/taiwan-investor-relations-institute-tiri-%E5%8F%B0%E7%81%A3%E6%8A%95%E8%B3%87%E4%BA%BA%E9%97%9C%E4%BF%82%E5%8D%94%E6%9C%83/" target="_blank" rel="noopener" aria-label="LinkedIn"><span class="roll"><svg class="icon" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-linkedin"/></svg><svg class="icon" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-linkedin"/></svg></span></a>
        <a href="https://lin.ee/AcTa5dh" target="_blank" rel="noopener" aria-label="LINE"><span class="roll"><svg class="icon" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-line"/></svg><svg class="icon" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-line"/></svg></span></a>
        <a href="https://www.youtube.com/@officetiri6311" target="_blank" rel="noopener" aria-label="YouTube"><span class="roll"><svg class="icon" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-youtube"/></svg><svg class="icon" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-youtube"/></svg></span></a>
        <a href="mailto:office@tiri.tw" aria-label="Email"><span class="roll"><svg class="icon" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-mail"/></svg><svg class="icon" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-mail"/></svg></span></a>
      </span>
        </nav>
    <div class="header-main">
    <nav class="main-nav" aria-label="主導覽">
      <ul>
{nav_items}
      </ul>
    </nav>
    <div class="header-actions">
      <a class="btn btn-primary btn-cta-desktop" href="join.html"><span class="roll"><span>加入會員</span><span aria-hidden="true">加入會員</span></span></a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="drawer" aria-label="開啟選單">
        <span class="bar" aria-hidden="true"></span>
        <span class="bar" aria-hidden="true"></span>
        <span class="bar" aria-hidden="true"></span>
      </button>
    </div>
    </div>
    </div>
  </div>
  <div class="search-drop" id="search-panel">
    <div class="search-backdrop" data-search-close></div>
    <div class="search-sheet">
    <div class="container">
      <form data-demo-form role="search" aria-label="站內搜尋">
        <input type="search" name="q" placeholder="搜尋課程、活動、文章…" aria-label="關鍵字">
        <button class="search-close" type="button" data-search-close aria-label="關閉搜尋">
          <svg class="icon" width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-x"/></svg>
        </button>
        <button class="btn btn-primary" type="submit">搜尋</button>
      </form>
    </div>
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
      </div>
      <div class="footer-col">
        <h3>關於 TIRI</h3>
        <ul>
          <li><a href="about.html">協會使命</a></li>
          <li><a href="team2026.html">第三屆理監事成員</a></li>
          <li><a href="board.html">歷屆理監事</a></li>
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
      <div class="lang-switch">
        <button class="lang-toggle" type="button" aria-expanded="false" aria-controls="lang-menu">
          <svg class="icon" width="15" height="15" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-globe"/></svg>
          <span class="lang-current">中文</span>
          <svg class="icon chev" width="11" height="11" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-chevron-down"/></svg>
        </button>
        <div class="lang-menu" id="lang-menu">
          <a href="index.html" aria-current="true">中文</a>
          <a href="en.html">English</a>
        </div>
      </div>
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
    hero_img = HERO_IMAGES.get((active, eyebrow)) or HERO_IMAGES.get(active) or "hero-taipei-dark.jpg"
    lang = "en" if (name.startswith("en") or name.endswith("_en.html") or "_en-" in name or name in {"services_en.html", "mission_en.html"}) else "zh-Hant"

    body = main.decode_contents()
    content = f'''  <section class="page-hero has-photo" style="--hero-img: url('../images/{hero_img}')">
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
