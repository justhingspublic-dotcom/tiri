#!/usr/bin/env python3
"""Extract inline presentation/behavior and repair legacy asset references."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[2] / "original"
HTML_DIR = ROOT / "html"
INLINE_CSS = ROOT / "css" / "legacy-inline.css"
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I)

FOLDER_BY_SUFFIX = {
    ".png": "images",
    ".jpg": "images",
    ".jpeg": "images",
    ".gif": "images",
    ".webp": "images",
    ".svg": "images",
    ".ico": "images",
    ".woff": "fonts",
    ".woff2": "fonts",
    ".ttf": "fonts",
    ".eot": "fonts",
    ".pdf": "documents",
    ".doc": "documents",
    ".docx": "documents",
    ".xls": "documents",
    ".xlsx": "documents",
    ".ppt": "documents",
    ".pptx": "documents",
    ".zip": "documents",
}


def is_external(value: str) -> bool:
    parsed = urlsplit(value)
    return bool(parsed.scheme or parsed.netloc or value.startswith(("#", "mailto:", "tel:", "data:", "javascript:", "../")))


def organized_target(old_path: str) -> Path | None:
    parsed = urlsplit(old_path)
    relative = parsed.path.lstrip("/")
    suffix = Path(relative).suffix.lower()
    folder = FOLDER_BY_SUFFIX.get(suffix)
    if not folder:
        return None
    source_label = relative
    stem = re.sub(r"[^0-9A-Za-z._-]+", "-", source_label).strip("-")
    digest = hashlib.sha1(source_label.encode("utf-8")).hexdigest()[:7]
    without_suffix = stem[: -len(suffix)] if suffix and stem.lower().endswith(suffix) else stem
    candidate = ROOT / folder / f"{without_suffix}-{digest}{suffix}"
    return candidate if candidate.exists() else None


def relative_url(source: Path, target: Path) -> str:
    return os.path.relpath(target, source.parent).replace(os.sep, "/")


def rewrite_css_urls(css: str, output_css: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        value = match.group(2)
        if is_external(value):
            return match.group(0)
        target = organized_target(value)
        if target:
            return f"url('{relative_url(output_css, target)}')"
        raise FileNotFoundError(f"Unresolved CSS reference: {value}")

    return CSS_URL_RE.sub(replace, css)


def main() -> None:
    style_blocks: list[str] = []
    style_block_seen: set[str] = set()
    style_classes: dict[str, str] = {}

    for html_file in sorted(HTML_DIR.glob("*.html")):
        soup = BeautifulSoup(html_file.read_text(encoding="utf-8", errors="replace"), "html.parser")

        for tag in soup.find_all(True):
            for attr in ("href", "src", "poster", "data-src", "data-background-image"):
                value = tag.get(attr)
                if not isinstance(value, str) or is_external(value):
                    continue
                target = organized_target(value)
                if target:
                    tag[attr] = relative_url(html_file, target)

            inline_style = tag.get("style")
            if isinstance(inline_style, str) and inline_style.strip():
                normalized = rewrite_css_urls(inline_style.strip(), INLINE_CSS)
                class_name = style_classes.get(normalized)
                if not class_name:
                    class_name = f"tiri-inline-{len(style_classes) + 1}"
                    style_classes[normalized] = class_name
                existing = list(tag.get("class") or [])
                if class_name not in existing:
                    existing.append(class_name)
                tag["class"] = existing
                del tag["style"]

        for style in list(soup.find_all("style")):
            content = rewrite_css_urls(style.get_text("\n"), INLINE_CSS).strip()
            if content and content not in style_block_seen:
                style_block_seen.add(content)
                style_blocks.append(content)
            style.decompose()

        # The original Weebly runtime is not required for this static archive.
        # Shared interactions are provided by js/site.js.
        for script in list(soup.find_all("script")):
            source = script.get("src")
            if isinstance(source, str) and urlsplit(source).path == "../js/site.js":
                continue
            script.decompose()

        has_inline_stylesheet = soup.find(
            "link",
            href=lambda value: isinstance(value, str)
            and urlsplit(value).path == "../css/legacy-inline.css",
        )
        if soup.head and not has_inline_stylesheet:
            link = soup.new_tag("link", rel="stylesheet", href="../css/legacy-inline.css")
            existing_site = soup.find(
                "link",
                href=lambda value: isinstance(value, str)
                and urlsplit(value).path == "../css/site.css",
            )
            if existing_site:
                existing_site.insert_before(link)
            else:
                soup.head.append(link)

        html_file.write_text(str(soup), encoding="utf-8")

    rules = [
        "/* Extracted from the original site's repeated inline styles. */",
        *style_blocks,
        "/* Extracted style attributes, deduplicated across all pages. */",
    ]
    for declaration, class_name in style_classes.items():
        rules.append(f".{class_name} {{{declaration}}}")
    INLINE_CSS.write_text("\n\n".join(rules) + "\n", encoding="utf-8")

    for unused in (ROOT / "css" / "source", ROOT / "js" / "source"):
        if unused.exists():
            shutil.rmtree(unused)

    print(f"Cleaned {len(list(HTML_DIR.glob('*.html')))} HTML pages.")
    print(f"Extracted {len(style_blocks)} unique style blocks.")
    print(f"Extracted {len(style_classes)} reusable inline-style classes.")


if __name__ == "__main__":
    main()
