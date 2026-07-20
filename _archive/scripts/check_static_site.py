#!/usr/bin/env python3
"""Check local HTML references in the mirrored static site."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ATTRS = ("href", "src", "poster")


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._collect(attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._collect(attrs)

    def _collect(self, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in ATTRS and isinstance(value, str):
                self.references.append(value)


def main() -> None:
    missing: list[str] = []
    html_files = sorted(ROOT.rglob("*.html"))
    for html_file in html_files:
        parser = ReferenceParser()
        parser.feed(html_file.read_text(encoding="utf-8", errors="replace"))
        for value in parser.references:
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or value.startswith(("#", "mailto:", "tel:", "data:")):
                continue
            target = (html_file.parent / unquote(parsed.path)).resolve()
            if parsed.path and not target.exists():
                missing.append(f"{html_file.relative_to(ROOT)} -> {value}")

    print(f"HTML files checked: {len(html_files)}")
    print(f"Missing local references: {len(missing)}")
    for item in missing[:100]:
        print(item)
    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
