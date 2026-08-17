#!/usr/bin/env python3
"""
V1 站內搜尋索引產生器（2026-08-17）

掃 v1/html/*.html → 產出 v1/search-index.json，供 v1/js/main.js 的搜尋面板
在瀏覽器端做子字串比對。獨立於 build_pages.py（不重跑頁面產生器，不會回退頁面）。

每筆：{ "u": 檔名, "t": 標題, "s": 區塊（八區之一）, "l": zh|en, "b": 內文純文字（截斷） }

區塊判定順序：navbar.js 導覽資料（page → 第一層 label）→ 頁首 eyebrow 對照表 → 預設。

用法：.venv/bin/python _archive/scripts/v1build/build_search_index.py
"""
import json
import re
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[3]
V1 = ROOT / "v1"
HTML_DIR = V1 / "html"
NAVBAR_JS = V1 / "js" / "navbar.js"
OUT = V1 / "search-index.json"

BODY_LIMIT = 3000          # 每頁內文上限（字元）；夠找到文章內文，又控住檔案大小
SKIP = {"search.html", "login.html"}

# 未列在導覽中的頁面 → 依頁首 eyebrow 歸區
EYEBROW_ZH = {
    "IR Knowledge": "專業分享",
    "TIRI": "專業分享",             # 雙月刊／專文文章頁
    "Events & Programs": "活動訊息",
    "Past Events": "活動訊息",
    "Latest News": "活動訊息",
    "News & Events": "活動訊息",
    "About TIRI": "關於 TIRI",
    "Partners & Sponsors": "關於 TIRI",
    "Membership": "會員中心",
    "Member Area": "會員中心",
    "Join TIRI": "會員中心",
}
EYEBROW_EN = {
    "IR Knowledge": "IR Library",
    "TIRI": "IR Library",
    "Events & Programs": "Recap",
    "Past Events": "Recap",
    "Latest News": "Recap",
    "News & Events": "Recap",
    "About TIRI": "About TIRI",
    "Partners & Sponsors": "About TIRI",
    "Membership": "Membership",
    "Member Area": "Membership",
    "Join TIRI": "Membership",
}


def nav_section_map():
    """用 node 把 navbar.js 裡的 navigation / navigationEn 兩個陣列 dump 成 JSON，
    回傳 {檔名: 第一層 label}（中英各自）。"""
    src = NAVBAR_JS.read_text(encoding="utf-8")

    def block(name):
        m = re.search(r"var %s = (\[.*?\n  \]);" % name, src, re.S)
        if not m:
            raise SystemExit("navbar.js 找不到 %s" % name)
        return m.group(1)

    js = "const zh = %s; const en = %s; console.log(JSON.stringify({zh, en}));" % (
        block("navigation"), block("navigationEn"))
    data = json.loads(subprocess.check_output(["node", "-e", js], text=True))
    result = {}
    for lang, items in data.items():
        m = {}
        for item in items:
            label = item["label"]
            pages = [item["href"]]
            if item.get("figure"):
                pages.append(item["figure"][0])
            for col in item.get("columns", []):
                pages += [ln[0] for ln in col.get("links", [])]
            for href in pages:
                f = href.split("#")[0]
                if f and f not in m:
                    m[f] = label
        result[lang] = m
    return result


def clean_text(node):
    for t in node.find_all(["script", "style", "noscript", "svg", "template"]):
        t.decompose()
    text = node.get_text(" ")
    text = text.replace("​", "").replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def build():
    nav = nav_section_map()
    entries = []
    for path in sorted(HTML_DIR.glob("*.html")):
        if path.name in SKIP:
            continue
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        lang = "en" if (soup.html and soup.html.get("lang", "").startswith("en")) else "zh"
        main = soup.find("main") or soup.body

        h1 = main.find("h1") if main else None
        title = clean_text(h1) if h1 else ""
        # 首頁 h1 是標語（含換行），改用固定名稱；其他頁 h1 找不到時退回 <title>
        if path.name == "index.html":
            title = "TIRI 台灣投資人關係協會"
        elif path.name == "en.html":
            title = "Taiwan Investor Relations Institute (TIRI)"
        elif not title and soup.title:
            title = soup.title.get_text().split("｜")[0].split("|")[0].strip()
        # 收掉 h1 換行造成的中文標點前後空白
        title = re.sub(r"\s+([，。、！？：；）」』])", r"\1", title)
        title = re.sub(r"([（「『])\s+", r"\1", title)

        eyebrow_el = main.find(class_="eyebrow") if main else None
        eyebrow = clean_text(eyebrow_el).replace("&amp;", "&") if eyebrow_el else ""

        table = EYEBROW_EN if lang == "en" else EYEBROW_ZH
        section = nav[lang].get(path.name) or table.get(eyebrow) or ("Home" if lang == "en" else "首頁")

        # 內文：去掉 h1／eyebrow／hero 區塊避免標題重複出現在摘要開頭
        if main:
            hero = main.find(class_=re.compile(r"\b(page-hero|hero)\b"))
            if hero:
                hero.decompose()
            body = clean_text(main)
        else:
            body = ""
        # 內文常以同一標題開頭（文章版型會再印一次 h1），去掉避免摘要重複標題
        if title and body.startswith(title):
            body = body[len(title):].lstrip(" ,.:：，。")
        if len(body) > BODY_LIMIT:
            body = body[:BODY_LIMIT]

        entries.append({"u": path.name, "t": title, "s": section, "l": lang, "b": body})

    OUT.write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    size = OUT.stat().st_size
    print("寫出 %s：%d 頁，%.0f KB" % (OUT.relative_to(ROOT), len(entries), size / 1024))
    from collections import Counter
    for (lang, sec), n in sorted(Counter((e["l"], e["s"]) for e in entries).items()):
        print("  %s  %-14s %d" % (lang, sec, n))


if __name__ == "__main__":
    build()
