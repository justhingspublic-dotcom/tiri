#!/usr/bin/env python3
"""Check local HTML references and production-site leaks in the static site."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
ATTRS = ("href", "src", "poster", "data-src", "data-background-image")
TIRI_HOSTS = {"tiri.tw", "www.tiri.tw"}
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._collect(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._collect(tag, attrs)

    def _collect(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in ATTRS and isinstance(value, str):
                self.references.append((tag, name, value))


def main() -> None:
    missing: list[str] = []
    production_references: list[str] = []
    html_files = sorted(ROOT.rglob("*.html"))
    for html_file in html_files:
        parser = ReferenceParser()
        parser.feed(html_file.read_text(encoding="utf-8", errors="replace"))
        for tag, name, value in parser.references:
            parsed = urlsplit(value)
            if (parsed.hostname or "").lower() in TIRI_HOSTS:
                production_references.append(
                    f"{html_file.relative_to(ROOT)} [{tag} {name}] -> {value}"
                )
                continue
            if parsed.scheme or parsed.netloc or value.startswith(("#", "mailto:", "tel:", "data:")):
                continue
            target = (html_file.parent / unquote(parsed.path)).resolve()
            if parsed.path and not target.exists():
                missing.append(f"{html_file.relative_to(ROOT)} -> {value}")

    css_files = sorted(ROOT.rglob("*.css"))
    for css_file in css_files:
        stylesheet = css_file.read_text(encoding="utf-8", errors="replace")
        for _, value in CSS_URL_RE.findall(stylesheet):
            parsed = urlsplit(value)
            if (parsed.hostname or "").lower() in TIRI_HOSTS:
                production_references.append(
                    f"{css_file.relative_to(ROOT)} [css url] -> {value}"
                )
                continue
            if parsed.scheme or parsed.netloc or value.startswith(("#", "data:")):
                continue
            target = (css_file.parent / unquote(parsed.path)).resolve()
            if parsed.path and not target.exists():
                missing.append(f"{css_file.relative_to(ROOT)} -> {value}")

    print(f"HTML files checked: {len(html_files)}")
    print(f"CSS files checked: {len(css_files)}")
    print(f"Missing local references: {len(missing)}")
    for item in missing[:100]:
        print(item)
    print(f"TIRI production runtime references: {len(production_references)}")
    for item in production_references[:100]:
        print(item)
    if missing or production_references:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
