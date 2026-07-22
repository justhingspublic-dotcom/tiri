#!/usr/bin/env python3
"""Normalize the mirrored site into a clean, file-type-based structure."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[2] / "original"
STAGING = ROOT / ".organize-staging"

FOLDER_BY_SUFFIX = {
    ".html": "html",
    ".htm": "html",
    ".css": "css/source",
    ".js": "js/source",
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
    ".mp4": "media",
    ".webm": "media",
}

CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I)
KEEP_ROOT = {"Files", "scripts", "README.md", "package.json"}
AUTHOR_FILES = {ROOT / "css" / "site.css", ROOT / "js" / "site.js"}


def safe_stem(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    stem = re.sub(r"[^0-9A-Za-z._-]+", "-", relative).strip("-")
    digest = hashlib.sha1(relative.encode("utf-8")).hexdigest()[:7]
    suffix = path.suffix.lower()
    without_suffix = stem[: -len(suffix)] if suffix and stem.lower().endswith(suffix) else stem
    return f"{without_suffix}-{digest}{suffix}"


def destination_for(path: Path) -> Path | None:
    suffix = path.suffix.lower()
    folder = FOLDER_BY_SUFFIX.get(suffix)
    if not folder:
        return None
    if folder == "html":
        name = "index.html" if path == ROOT / "index.html" else path.name
        return STAGING / folder / name
    return STAGING / folder / safe_stem(path)


def is_external(value: str) -> bool:
    parsed = urlsplit(value)
    return bool(parsed.scheme or parsed.netloc or value.startswith(("#", "mailto:", "tel:", "data:", "javascript:")))


def resolve_old_reference(source: Path, value: str) -> Path:
    parsed = urlsplit(value)
    raw_path = unquote(parsed.path)
    if raw_path.startswith("/"):
        return (ROOT / raw_path.lstrip("/")).resolve()
    return (source.parent / raw_path).resolve()


def relative_url(source: Path, target: Path, fragment: str = "") -> str:
    result = os.path.relpath(target, source.parent).replace(os.sep, "/")
    return result + (f"#{fragment}" if fragment else "")


def main() -> None:
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir()

    files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and STAGING not in path.parents
        and "node_modules" not in path.parts
        and path.name != ".DS_Store"
        and path not in AUTHOR_FILES
        and not any(part in KEEP_ROOT for part in path.relative_to(ROOT).parts[:1])
    ]

    mapping: dict[Path, Path] = {}
    for source in files:
        destination = destination_for(source)
        if destination:
            mapping[source.resolve()] = destination.resolve()

    for destination in mapping.values():
        destination.parent.mkdir(parents=True, exist_ok=True)

    # Move and rewrite HTML.
    for source, destination in mapping.items():
        if source.suffix.lower() not in {".html", ".htm"}:
            continue
        soup = BeautifulSoup(source.read_text(encoding="utf-8", errors="replace"), "html.parser")

        # Remove old CSS/JS includes; they are consolidated below.
        for link in soup.find_all("link", href=True):
            if "stylesheet" in [item.lower() for item in (link.get("rel") or [])]:
                link.decompose()
        for script in soup.find_all("script", src=True):
            old_target = resolve_old_reference(source, script["src"])
            if old_target in mapping:
                script.decompose()

        for tag in soup.find_all(True):
            for attr in ("href", "src", "poster", "data-src", "data-background-image"):
                value = tag.get(attr)
                if not isinstance(value, str) or is_external(value):
                    continue
                parsed = urlsplit(value)
                old_target = resolve_old_reference(source, value)
                new_target = mapping.get(old_target)
                if new_target:
                    tag[attr] = relative_url(destination, new_target, parsed.fragment)
                elif parsed.path:
                    raise FileNotFoundError(
                        f"Unresolved local reference in {source.relative_to(ROOT)}: {value}"
                    )

            if tag.has_attr("srcset"):
                rewritten = []
                for candidate in tag["srcset"].split(","):
                    pieces = candidate.strip().split()
                    if pieces and not is_external(pieces[0]):
                        old_target = resolve_old_reference(source, pieces[0])
                        new_target = mapping.get(old_target)
                        if new_target:
                            pieces[0] = relative_url(destination, new_target)
                    rewritten.append(" ".join(pieces))
                tag["srcset"] = ", ".join(rewritten)

        if soup.head:
            legacy = soup.new_tag("link", rel="stylesheet", href="../css/legacy.css")
            shared = soup.new_tag("link", rel="stylesheet", href="../css/site.css")
            soup.head.append(legacy)
            soup.head.append(shared)
        if soup.body:
            shared_js = soup.new_tag("script", src="../js/site.js", defer=True)
            soup.body.append(shared_js)

        destination.write_text(str(soup), encoding="utf-8")

    # Consolidate source styles into one reusable compatibility bundle.
    css_chunks: list[str] = []
    for source, destination in mapping.items():
        if source.suffix.lower() != ".css":
            continue
        css = source.read_text(encoding="utf-8", errors="replace")

        def replace_css_url(match: re.Match[str]) -> str:
            value = match.group(2)
            if is_external(value):
                return match.group(0)
            old_target = resolve_old_reference(source, value)
            new_target = mapping.get(old_target)
            if not new_target:
                raise FileNotFoundError(
                    f"Unresolved CSS reference in {source.relative_to(ROOT)}: {value}"
                )
            return f"url('{relative_url(STAGING / 'css' / 'legacy.css', new_target)}')"

        css = CSS_URL_RE.sub(replace_css_url, css)
        css_chunks.append(f"\n/* Source: {source.relative_to(ROOT)} */\n{css}\n")

    (STAGING / "css").mkdir(parents=True, exist_ok=True)
    (STAGING / "css" / "legacy.css").write_text("".join(css_chunks), encoding="utf-8")
    (STAGING / "js").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "css" / "site.css", STAGING / "css" / "site.css")
    shutil.copy2(ROOT / "js" / "site.js", STAGING / "js" / "site.js")

    # Copy all non-HTML/CSS categorized assets.
    for source, destination in mapping.items():
        if source.suffix.lower() in {".html", ".htm", ".css"}:
            continue
        shutil.copy2(source, destination)

    # Remove old generated content while preserving authored project files.
    for child in list(ROOT.iterdir()):
        if child.name in KEEP_ROOT or child == STAGING:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    for child in STAGING.iterdir():
        shutil.move(str(child), ROOT / child.name)
    STAGING.rmdir()

    print(f"Organized {len(mapping)} mirrored files.")


if __name__ == "__main__":
    main()
