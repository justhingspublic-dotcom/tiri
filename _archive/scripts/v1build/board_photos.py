#!/usr/bin/env python3
"""
第三屆理監事肖像上稿器（2026-09-08）

客戶照片會分批丟進 `2理監事成員/第三屆理監事照片*/<中文姓名>.jpg`（取最新修改的那個資料夾）。
每收到新照片就重跑一次：

    python3 _archive/scripts/v1build/board_photos.py

做的事：
1. 讀資料夾裡每張 jpg/jpeg/png，依中文姓名對到 board.html 第三屆名冊（ALIAS 處理錯別字）；
   對不到的姓名會列出來、不處理。
2. 統一取景：用 macOS Vision 偵測人臉框，裁成 3:4 頭肩照（人臉高≈裁切高 30%、臉中心在 27% 處），
   縮成 600×800、JPEG 82，存到 v1/images/board-2026-<slug>.jpg（slug 取自英文名，固定不變）。
   偵測不到臉時退回「從上方取景」的舊裁法並提示。
3. 在 v1/html/board.html 與 board_en.html 的第三屆面板補上肖像：
   理事長那種 .board-lead 用大圖 <figure>；名冊列加 has-photo 縮圖。已有肖像的列跳過，重跑不重複。
4. original 版 team2026.html／team_en-2026.html 的肖像格依 v1 重建、圖檔同步複製到 original/images。
照片不影響搜尋索引，不必重跑 build_search_index.py。
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
DROP = ROOT / "2理監事成員"
IMG_DIR = ROOT / "v1" / "images"
PAGES = {"zh": ROOT / "v1/html/board.html", "en": ROOT / "v1/html/board_en.html"}
ORIG_PAGES = {"zh": ROOT / "original/html/team2026.html", "en": ROOT / "original/html/team_en-2026.html"}
ORIG_IMG_DIR = ROOT / "original/images"
TERM = "2026"
W, H = 600, 800                 # 3:4 頭肩照
FACE_FRAC, FACE_CY = 0.30, 0.27  # 人臉框高佔裁切高比例；臉中心落點（自頂端）
SWIFT_SRC = Path(__file__).with_name("facedetect.swift")

# 客戶檔名 → 名冊姓名
ALIAS = {"洪建凱": "洪健凱"}
# 已上線的檔名固定住，換照片時網址不變
FIXED_SLUG = {
    "郭宗霖": "jonny-kuo", "王恩國": "kevin-wang", "簡世雄": "andy-chien", "張明仁": "jack-chang",
    "黃奕誠": "nick-huang", "沈馥馥": "fufu-shen", "張妍婷": "tina-chang", "張真卿": "peter-chang",
}
# original 肖像格職稱：分組標題 → 單人職稱
ROLE_ALIAS = {"秘書處": "秘書長", "Secretariat": "Secretary General"}


def source_dir() -> Path:
    dirs = [d for d in DROP.glob("第三屆理監事照片*") if d.is_dir()]
    if not dirs:
        sys.exit(f"找不到照片資料夾：{DROP}/第三屆理監事照片*")
    return max(dirs, key=lambda d: d.stat().st_mtime)


def panel(html: str) -> str:
    start = html.index(f'data-term="{TERM}"')
    end = html.find('<div class="term-panel"', start + 1)
    return html[start:end if end > 0 else len(html)]


def names(html: str) -> list[str]:
    return re.findall(r'<p class="name">(.*?)</p>', panel(html))


def slugify(en: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", en.lower()).strip("-")


# ---------- 人臉偵測（Vision） ----------
def face_detector() -> Path | None:
    if sys.platform != "darwin" or not SWIFT_SRC.exists():
        return None
    digest = hashlib.sha1(SWIFT_SRC.read_bytes()).hexdigest()[:10]
    binary = Path.home() / "Library/Caches/tiri-facedetect" / f"facedetect-{digest}"
    if not binary.exists():
        binary.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["swiftc", "-O", str(SWIFT_SRC), "-o", str(binary)], capture_output=True, text=True)
        if r.returncode != 0:
            print("  ⚠ swiftc 編譯失敗，改用舊裁法：", r.stderr.strip()[:200])
            return None
    return binary


def detect_faces(binary: Path, images: dict[str, Image.Image]) -> dict[str, dict | None]:
    """images: {姓名: 已轉正的 PIL 影像}；回傳 {姓名: 最大人臉框(0–1) 或 None}。縮圖後再偵測，快很多。"""
    with tempfile.TemporaryDirectory() as tmp:
        paths = {}
        for key, im in images.items():
            small = im.copy(); small.thumbnail((1200, 1200))
            p = Path(tmp) / f"{key}.jpg"; small.save(p, quality=90); paths[str(p)] = key
        r = subprocess.run([str(binary), *paths], capture_output=True, text=True)
        if r.returncode != 0:
            print("  ⚠ 人臉偵測執行失敗，改用舊裁法：", r.stderr.strip()[:200])
            return {k: None for k in images}
        data = json.loads(r.stdout)
    out = {}
    for p, key in paths.items():
        faces = (data.get(p) or {}).get("faces") or []
        out[key] = max(faces, key=lambda f: f["w"] * f["h"]) if faces else None
    return out


def crop_portrait(im: Image.Image, face: dict | None, out: Path) -> str:
    iw, ih = im.size
    aspect = W / H
    if face:
        fx, fy, fw, fh = face["x"] * iw, face["y"] * ih, face["w"] * iw, face["h"] * ih
        ch = fh / FACE_FRAC
        cw = ch * aspect
        scale = min(1.0, ih / ch, iw / cw)   # 原圖不夠大就縮小裁切框
        ch *= scale; cw *= scale
        left = fx + fw / 2 - cw / 2
        top = fy + fh / 2 - ch * FACE_CY
        left = max(0.0, min(left, iw - cw)); top = max(0.0, min(top, ih - ch))
        box = (int(left), int(top), int(left + cw), int(top + ch))
        how = "臉部對齊" if scale == 1 else f"臉部對齊（原圖偏小，縮放 {scale:.2f}）"
    else:
        if iw / ih > aspect:
            nw = int(ih * aspect); box = ((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih)
        else:
            nh = int(iw / aspect); top = int((ih - nh) * 0.15); box = (0, top, iw, top + nh)
        how = "⚠ 未偵測到臉，從上方取景"
    im.crop(box).resize((W, H), Image.LANCZOS).save(out, quality=82, optimize=True)
    return how


# ---------- v1 頁面 ----------
def patch(html: str, name: str, src: str) -> tuple[str, int]:
    """只動第三屆面板；同名者在第一、二屆面板不加照片（那兩屆除 banner 外不放圖）。"""
    start = html.index(f'data-term="{TERM}"')
    end = html.find('<div class="term-panel"', start + 1)
    if end < 0:
        end = len(html)
    inner, n = _patch_panel(html[start:end], name, src)
    return html[:start] + inner + html[end:], n


def _patch_panel(html: str, name: str, src: str) -> tuple[str, int]:
    img = f'<img src="{src}" alt="{name}" width="{W}" height="{H}" loading="lazy">'
    n = 0
    html, c = re.subn(
        r'<div class="board-lead no-photo reveal">(\s*<div>\s*<p class="role">[^<]*</p>\s*<p class="name">' + re.escape(name) + r"</p>)",
        r'<div class="board-lead reveal">\n        <figure>' + img + r"</figure>\1", html)
    n += c
    html, c = re.subn(
        r'<li class="reveal">((?:<span class="also">[^<]*</span>)?<p class="name">' + re.escape(name) + r"</p>)",
        r'<li class="reveal has-photo">' + img + r"\1", html)
    n += c
    # 既有肖像的尺寸屬性統一成目前輸出尺寸
    html = re.sub(r'(<img src="\.\./images/board-2026-[^"]+" alt="[^"]*") width="\d+" height="\d+"', rf'\1 width="{W}" height="{H}"', html)
    return html, n


# ---------- original 版 ----------
def portrait_roster(v1_html: str) -> list[tuple[str, str, str]]:
    """從 v1 第三屆面板取出有肖像者：(姓名, 職稱, 圖檔名)，依名冊順序、同人只取第一次出現。"""
    p = panel(v1_html)
    found, seen = [], set()
    for m in re.finditer(r'<figure><img src="\.\./images/(board-2026-[^"]+)"[^>]*></figure>\s*<div>\s*<p class="role">([^<]*)</p>\s*<p class="name">([^<]*)</p>', p):
        fname, role, name = m.groups()
        if fname not in seen:
            seen.add(fname); found.append((name, role, fname))
    heading = ""
    for m in re.finditer(r'<h2 class="reveal">([^<]*)</h2>|<li class="reveal has-photo"><img src="\.\./images/(board-2026-[^"]+)"[^>]*>(?:<span class="also">[^<]*</span>)?<p class="name">([^<]*)</p>', p):
        if m.group(1) is not None:
            heading = m.group(1).strip()
            continue
        fname, name = m.group(2), m.group(3)
        if fname in seen:
            continue
        seen.add(fname)
        role = ROLE_ALIAS.get(heading) or (re.sub(r"s$", "", heading) if re.search(r"[A-Za-z]", heading) else heading)
        found.append((name, role, fname))
    return found


def sync_original(v1_pages: dict) -> None:
    for lang, path in ORIG_PAGES.items():
        if not path.exists():
            continue
        roster = portrait_roster(v1_pages[lang])
        for _, _, fname in roster:
            src, dst = IMG_DIR / fname, ORIG_IMG_DIR / fname
            if not dst.exists() or src.read_bytes() != dst.read_bytes():
                dst.write_bytes(src.read_bytes())
        items = "\n".join(
            f'<li><img src="../images/{fname}" alt="{name}" width="{W}" height="{H}" loading="lazy">'
            f'<span class="name">{name}</span><span class="role">{role}</span></li>'
            for name, role, fname in roster)
        html = path.read_text(encoding="utf-8")
        new, c = re.subn(r'<ul class="board-portraits">\n.*?\n</ul>', lambda _m: f'<ul class="board-portraits">\n{items}\n</ul>', html, count=1, flags=re.S)
        if c != 1:
            print(f"  ⚠ original {path.name} 找不到 .board-portraits，未同步")
            continue
        if new != html:
            path.write_text(new, encoding="utf-8")
        print(f"  original {path.name}: 肖像格 {len(roster)} 人{'（已更新）' if new != html else '（無變動）'}")


def main() -> int:
    pages = {lang: p.read_text(encoding="utf-8") for lang, p in PAGES.items()}
    zh_names, en_names = names(pages["zh"]), names(pages["en"])
    if len(zh_names) != len(en_names):
        sys.exit(f"中英名冊筆數不一致：zh {len(zh_names)} / en {len(en_names)}")
    zh_to_en = dict(zip(zh_names, en_names))

    src_dir = source_dir()
    photos = sorted(p for p in src_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if not photos:
        sys.exit(f"沒有照片：{src_dir}")
    print(f"照片來源：{src_dir.name}（{len(photos)} 張）")

    images, unknown = {}, []
    for photo in photos:
        zh = ALIAS.get(photo.stem.strip(), photo.stem.strip())
        if zh not in zh_to_en:
            unknown.append(photo.stem); continue
        images[zh] = ImageOps.exif_transpose(Image.open(photo)).convert("RGB")

    detector = face_detector()
    faces = detect_faces(detector, images) if detector else {k: None for k in images}

    done = []
    for zh, im in images.items():
        en = zh_to_en[zh]
        slug = FIXED_SLUG.get(zh) or slugify(en)
        out = IMG_DIR / f"board-2026-{slug}.jpg"
        how = crop_portrait(im, faces.get(zh), out)
        src = f"../images/{out.name}"
        counts = {}
        for lang, name in (("zh", zh), ("en", en)):
            pages[lang], counts[lang] = patch(pages[lang], name, src)
        done.append((zh, en, out.name, out.stat().st_size // 1024, counts, how))

    for lang, p in PAGES.items():
        p.write_text(pages[lang], encoding="utf-8")
    sync_original(pages)

    for zh, en, fname, kb, counts, how in done:
        state = "已在頁上" if counts["zh"] == 0 else f"新插入 zh {counts['zh']}／en {counts['en']}"
        print(f"  {zh:　<4}{en:<16} {fname:<30}{kb:>4} KB  {state:<14} {how}")
    if unknown:
        print("\n對不到第三屆名冊的檔名（請確認姓名或先補名冊）：", "、".join(unknown))
    return 0


if __name__ == "__main__":
    sys.exit(main())
