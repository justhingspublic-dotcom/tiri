#!/usr/bin/env python3
"""Create a local, navigable mirror of the public pages on tiri.tw."""

from __future__ import annotations

import hashlib
import mimetypes
import os
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

from bs4 import BeautifulSoup


BASE_URL = "https://www.tiri.tw/"
SITEMAP_URL = urllib.parse.urljoin(BASE_URL, "sitemap.xml")
OUTPUT = Path(__file__).resolve().parents[1] / "original"
USER_AGENT = "Mozilla/5.0 (compatible; TIRI-Static-Archive/1.0)"
MAX_ASSET_BYTES = 30 * 1024 * 1024
REQUEST_DELAY = 0.04

CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I)
SOURCE_ATTRS = ("src", "href", "poster", "data-src", "data-background-image")
DOWNLOADABLE_SUFFIXES = {
    ".css",
    ".js",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".zip",
    ".mp4",
    ".webm",
}


def request(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=35) as response:
        length = response.headers.get("Content-Length")
        if length and int(length) > MAX_ASSET_BYTES:
            raise ValueError(f"asset too large ({length} bytes)")
        data = response.read(MAX_ASSET_BYTES + 1)
        if len(data) > MAX_ASSET_BYTES:
            raise ValueError("asset exceeded download limit")
        return data, response.headers.get_content_type()


def normalized_url(raw: str, page_url: str) -> str | None:
    raw = raw.strip()
    if not raw or raw.startswith(("#", "data:", "mailto:", "tel:", "javascript:")):
        return None
    if raw.startswith("//"):
        raw = "https:" + raw
    absolute = urllib.parse.urljoin(page_url, raw)
    parsed = urllib.parse.urlsplit(absolute)
    if parsed.scheme not in {"http", "https"}:
        return None
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))


def clean_segment(segment: str) -> str:
    return urllib.parse.unquote(segment).replace("\x00", "").replace(":", "_")


def local_page_path(url: str) -> Path:
    parsed = urllib.parse.urlsplit(url)
    path = parsed.path
    if path in {"", "/"}:
        return OUTPUT / "index.html"
    target = OUTPUT / clean_segment(path.lstrip("/"))
    if target.suffix.lower() not in {".html", ".htm"}:
        target = target / "index.html"
    return target


def local_asset_path(url: str) -> Path:
    parsed = urllib.parse.urlsplit(url)
    host = parsed.netloc.lower()
    path = parsed.path or "/index"
    suffix = PurePosixPath(path).suffix
    if path.endswith("/") or not suffix:
        guessed = mimetypes.guess_extension("application/octet-stream") or ".bin"
        path = path.rstrip("/") + "/index" + guessed
    path = "/".join(clean_segment(part) for part in path.lstrip("/").split("/"))
    if host in {"tiri.tw", "www.tiri.tw"}:
        target = OUTPUT / path
    else:
        target = OUTPUT / "assets" / "external" / clean_segment(host) / path
    if parsed.query:
        digest = hashlib.sha1(parsed.query.encode("utf-8")).hexdigest()[:8]
        target = target.with_name(f"{target.stem}-{digest}{target.suffix}")
    return target


def relative_link(from_file: Path, to_file: Path, fragment: str = "") -> str:
    rel = os.path.relpath(to_file, from_file.parent).replace(os.sep, "/")
    return rel + (f"#{fragment}" if fragment else "")


def is_internal_page(url: str, page_urls: set[str]) -> bool:
    parsed = urllib.parse.urlsplit(url)
    canonical = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
    return canonical in page_urls


def should_download_asset(url: str) -> bool:
    parsed = urllib.parse.urlsplit(url)
    suffix = PurePosixPath(parsed.path).suffix.lower()
    return suffix in DOWNLOADABLE_SUFFIXES or parsed.netloc.endswith("editmysite.com")


def rewrite_css(css: str, css_url: str, css_file: Path, asset_queue: list[str]) -> str:
    def replace(match: re.Match[str]) -> str:
        raw = match.group(2)
        absolute = normalized_url(raw, css_url)
        if not absolute or not should_download_asset(absolute):
            return match.group(0)
        target = local_asset_path(absolute)
        asset_queue.append(absolute)
        return f"url('{relative_link(css_file, target)}')"

    return CSS_URL_RE.sub(replace, css)


def rewrite_srcset(value: str, page_url: str, page_file: Path, asset_queue: list[str]) -> str:
    results = []
    for candidate in value.split(","):
        pieces = candidate.strip().split()
        if not pieces:
            continue
        absolute = normalized_url(pieces[0], page_url)
        if absolute and should_download_asset(absolute):
            target = local_asset_path(absolute)
            asset_queue.append(absolute)
            pieces[0] = relative_link(page_file, target)
        results.append(" ".join(pieces))
    return ", ".join(results)


def rewrite_html(
    html: bytes,
    page_url: str,
    page_file: Path,
    page_urls: set[str],
    asset_queue: list[str],
) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for base in soup.find_all("base"):
        base.decompose()

    for tag in soup.find_all(True):
        if tag.has_attr("srcset"):
            tag["srcset"] = rewrite_srcset(tag["srcset"], page_url, page_file, asset_queue)

        for attr in SOURCE_ATTRS:
            if not tag.has_attr(attr):
                continue
            raw = tag.get(attr)
            if not isinstance(raw, str):
                continue
            absolute = normalized_url(raw, page_url)
            if not absolute:
                continue
            parsed = urllib.parse.urlsplit(absolute)
            canonical = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))

            if attr == "href" and is_internal_page(canonical, page_urls):
                tag[attr] = relative_link(page_file, local_page_path(canonical), parsed.fragment)
            elif should_download_asset(absolute):
                target = local_asset_path(absolute)
                asset_queue.append(absolute)
                tag[attr] = relative_link(page_file, target, parsed.fragment)

        if tag.has_attr("style"):
            tag["style"] = rewrite_css(tag["style"], page_url, page_file, asset_queue)

    offline_note = soup.new_tag("div", id="tiri-offline-note")
    offline_note.string = "TIRI 官網靜態封存版本｜部分第三方功能需網路連線"
    body = soup.body
    if body:
        body.insert(0, offline_note)
        style = soup.new_tag("style")
        style.string = """
#tiri-offline-note {
  box-sizing: border-box;
  width: 100%;
  padding: 7px 16px;
  background: #342044;
  color: #fff;
  font: 12px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  text-align: center;
  letter-spacing: .02em;
  position: relative;
  z-index: 999999;
}
"""
        (soup.head or soup).append(style)

    return str(soup)


def sitemap_urls() -> list[str]:
    data, _ = request(SITEMAP_URL)
    root = ET.fromstring(data)
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text for node in root.findall("sm:url/sm:loc", namespace) if node.text]
    urls.extend([BASE_URL, urllib.parse.urljoin(BASE_URL, "en.html")])
    canonical = {
        urllib.parse.urlunsplit(
            (
                urllib.parse.urlsplit(url).scheme,
                urllib.parse.urlsplit(url).netloc,
                urllib.parse.urlsplit(url).path,
                "",
                "",
            )
        )
        for url in urls
    }
    return sorted(canonical)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    pages = sitemap_urls()
    page_set = set(pages)
    assets: list[str] = []
    failures: list[str] = []

    print(f"Downloading {len(pages)} public pages...")
    for index, url in enumerate(pages, 1):
        destination = local_page_path(url)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            data, _ = request(url)
            rewritten = rewrite_html(data, url, destination, page_set, assets)
            destination.write_text(rewritten, encoding="utf-8")
            print(f"[page {index:03d}/{len(pages)}] {url}")
        except (urllib.error.URLError, TimeoutError, socket.timeout, ValueError, OSError) as error:
            failures.append(f"PAGE {url}: {error}")
            print(f"[page failed] {url}: {error}")
        time.sleep(REQUEST_DELAY)

    seen: set[str] = set()
    cursor = 0
    print("Downloading page assets...")
    while cursor < len(assets):
        url = assets[cursor]
        cursor += 1
        if url in seen:
            continue
        seen.add(url)
        destination = local_asset_path(url)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            if destination.exists() and destination.suffix.lower() != ".css":
                continue
            data, content_type = request(url)
            if content_type == "text/css" or destination.suffix.lower() == ".css":
                text = data.decode("utf-8", errors="replace")
                text = rewrite_css(text, url, destination, assets)
                destination.write_text(text, encoding="utf-8")
            else:
                destination.write_bytes(data)
            if len(seen) % 50 == 0:
                print(f"[assets] {len(seen)} downloaded")
        except (urllib.error.URLError, TimeoutError, socket.timeout, ValueError, OSError) as error:
            failures.append(f"ASSET {url}: {error}")
        time.sleep(REQUEST_DELAY)

    (OUTPUT / "mirror-report.txt").write_text(
        "\n".join(
            [
                f"Source: {BASE_URL}",
                f"Pages requested: {len(pages)}",
                f"Assets requested: {len(seen)}",
                f"Failures: {len(failures)}",
                "",
                *failures,
            ]
        ),
        encoding="utf-8",
    )
    print(f"Finished. Output: {OUTPUT}")
    print(f"Failures: {len(failures)}")


if __name__ == "__main__":
    main()
