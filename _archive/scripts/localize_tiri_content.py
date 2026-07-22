#!/usr/bin/env python3
"""Localize public TIRI page links and content assets across all site variants.

The static conversion previously fell back to ``https://www.tiri.tw`` whenever
an asset was missing.  That made apparently local pages leave the archive or
silently depend on the production site.  This script downloads public content
assets once into ``original/`` and rewrites Original, V1, and V2 to use them.

Third-party services (SurveyCake, Accupass, Weebly forms, Google Maps, etc.) are
deliberately left external.  Open Graph metadata is also left untouched because
social crawlers require deployment-specific absolute URLs.
"""

from __future__ import annotations

import hashlib
import html
import bisect
import os
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
SITE_ROOTS = tuple(ROOT / name for name in ("original", "v1", "v2"))
ARCHIVE_ROOT = ROOT / "original"
LEGACY_CSS = ARCHIVE_ROOT / "css" / "legacy.css"
THEME_CSS = ARCHIVE_ROOT / "css" / "theme.css"
TIRI_HOSTS = {"tiri.tw", "www.tiri.tw"}
USER_AGENT = "Mozilla/5.0 (compatible; TIRI-Static-Archive/2.0)"
MAX_ASSET_BYTES = 100 * 1024 * 1024

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico"}
DOCUMENT_SUFFIXES = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".zip",
}
FONT_SUFFIXES = {".woff", ".woff2", ".ttf", ".eot"}
MEDIA_SUFFIXES = {".mp4", ".webm", ".mp3", ".wav", ".m4a"}

ATTRIBUTE_RE = re.compile(
    r"(?P<prefix>\b(?:href|src|poster|data-src|data-background-image)\s*=\s*)"
    r"(?P<quote>[\"'])(?P<value>[^\"']*)(?P=quote)",
    re.IGNORECASE,
)
ANCHOR_RE = re.compile(r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>", re.IGNORECASE | re.DOTALL)
HREF_RE = re.compile(
    r"(?P<prefix>\bhref\s*=\s*)(?P<quote>[\"'])(?P<value>[^\"']*)(?P=quote)",
    re.IGNORECASE,
)
CFEMAIL_RE = re.compile(r"\bdata-cfemail\s*=\s*[\"']([0-9a-f]+)[\"']", re.IGNORECASE)
EMAIL_PLACEHOLDER_RE = re.compile(
    r"\[email(?:\s|\xa0|&nbsp;|&#0*160;|&#x0*a0;)+protected\]", re.IGNORECASE
)
CSS_URL_RE = re.compile(
    r"url\(\s*(?P<quote>['\"]?)(?P<value>.*?)(?P=quote)\s*\)", re.IGNORECASE
)
CSS_SOURCE_RE = re.compile(
    r"/\* Source: assets/external/(?P<host>[^/]+)/(?P<path>.*?) \*/"
)

# Two obsolete production slugs still appear in an older news index.  Their
# content is already present locally under the aliases below.
PAGE_ALIASES = {
    "/201911-25237360392015438364204182831736890315743005365306235653550435498653113549820160406366531124590406363549865311.html": "191118.html",
    "/202007-356572013225152123003565721048263812120938617263762100212301235602739665293235603537020013337753865120449201952970230332353282015427784393333933321332.html": "2356035370-277843933339333297022010738263.html",
}

# These URLs were created by an old organizer fallback even though the files
# were originally hosted by NIRI.  They currently return 404 at tiri.tw; restore
# the real third-party host instead of sending visitors to the TIRI production
# site.  If a recoverable local copy is found later it can replace this mapping.
NIRI_PROXY_PREFIX = "/assets/external/www.niri.org/"
NIRI_ARCHIVE_URLS = {
    "/NIRI/media/NIRI-Resources/1017_NIRI_IRU_FullBook_ToPrint_LoRes.pdf": "https://web.archive.org/web/20190213084309id_/https://www.niri.org/NIRI/media/NIRI-Resources/1017_NIRI_IRU_FullBook_ToPrint_LoRes.pdf",
    "/NIRI/media/NIRI/Certification/Renewal_Program_Handbook_2020.pdf": "https://web.archive.org/web/20210915235718id_/https://www.niri.org/NIRI/media/NIRI/Certification/Renewal_Program_Handbook_2020.pdf",
    "/NIRI/media/NIRI/IRUpdates/2019 IR Update/001157_NIRI_Fall2019_FINAL.pdf": "https://web.archive.org/web/20191127200040id_/https://www.niri.org/NIRI/media/NIRI/IRUpdates/2019%20IR%20Update/001157_NIRI_Fall2019_FINAL.pdf",
    "/NIRI/media/NIRI/IRUpdates/2020 IR Update/001176_NIRI_Winter2020_FINAL_LR-(003).pdf": "https://web.archive.org/web/20240531213805id_/https://www.niri.org/NIRI/media/NIRI/IRUpdates/2020%20IR%20Update/001176_NIRI_Winter2020_FINAL_LR-(003).pdf",
    "/NIRI/media/NIRI/IRUpdates/2020 IR Update/Spring2020_NIRI_IRU_Feature1-Covid.pdf": "https://web.archive.org/web/20201203224541id_/https://www.niri.org/NIRI/media/NIRI/IRUpdates/2020%20IR%20Update/Spring2020_NIRI_IRU_Feature1-Covid.pdf",
}
THEME_ASSET_SOURCES = {
    "theme/images/quote-a67f89ed.png": "https://www.tiri.tw/files/theme/images/quote.png",
    "theme/images/arrow-a67f89ed.svg": "https://www.tiri.tw/files/theme/images/arrow.svg",
    "theme/images/default-bg-a67f89ed.jpg": "https://www.tiri.tw/files/theme/images/default-bg.jpg",
    "theme/images/arrow-light-a67f89ed.svg": "https://www.tiri.tw/files/theme/images/arrow-light.svg",
}


def same_tiri_host(value: str) -> bool:
    return (urllib.parse.urlsplit(value).hostname or "").lower() in TIRI_HOSTS


def parsed_tiri_url(value: str) -> urllib.parse.SplitResult | None:
    decoded = html.unescape(value.strip())
    if decoded.startswith("//"):
        decoded = "https:" + decoded
    parsed = urllib.parse.urlsplit(decoded)
    if (parsed.hostname or "").lower() not in TIRI_HOSTS:
        return None
    return parsed


def canonical_asset_url(parsed: urllib.parse.SplitResult) -> str:
    return urllib.parse.urlunsplit(("https", "www.tiri.tw", parsed.path, parsed.query, ""))


def safe_asset_name(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    relative = urllib.parse.unquote(parsed.path.lstrip("/")) or "index.bin"
    host = (parsed.hostname or "").lower()
    if host and host not in TIRI_HOSTS:
        relative = f"assets/external/{host}/{relative}"
    suffix = PurePosixPath(relative).suffix.lower()
    fingerprint_input = relative + (f"?{parsed.query}" if parsed.query else "")
    digest = hashlib.sha1(fingerprint_input.encode("utf-8")).hexdigest()[:7]
    flattened = re.sub(r"[^0-9A-Za-z._-]+", "-", relative).strip("-") or "asset"
    if suffix and flattened.lower().endswith(suffix):
        flattened = flattened[: -len(suffix)]
    # Keep enough context to make assets recognizable without approaching the
    # filesystem component length limit.
    flattened = flattened[:190].rstrip("-._") or "asset"
    return f"{flattened}-{digest}{suffix}"


def asset_destination(url: str) -> Path:
    suffix = PurePosixPath(urllib.parse.urlsplit(url).path).suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        folder = "images"
    elif suffix in DOCUMENT_SUFFIXES:
        folder = "documents"
    elif suffix in FONT_SUFFIXES:
        folder = "fonts"
    elif suffix in MEDIA_SUFFIXES:
        folder = "media"
    else:
        folder = "assets"
    return ARCHIVE_ROOT / folder / safe_asset_name(url)


def encoded_request_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    encoded_path = urllib.parse.quote(urllib.parse.unquote(parsed.path), safe="/:@")
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, encoded_path, parsed.query, "")
    )


def legacy_source_url(url: str) -> str | None:
    """Undo the erroneous hash suffix added by the old organizer fallback.

    For example, the generated (and nonexistent) production URL
    ``published/jack0224-dd1f195e.jpg`` came from the valid public asset
    ``published/jack0224.jpg``.  The eight-character suffix is not part of the
    Weebly source filename; it was a local cache fingerprint.
    """

    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or "").lower()
    if not (
        parsed.path.startswith("/uploads/")
        or host.endswith("editmysite.com")
    ):
        return None
    repaired_path = re.sub(
        r"-[0-9a-f]{8}(?=\.[A-Za-z0-9]+$)", "", parsed.path, flags=re.IGNORECASE
    )
    if repaired_path == parsed.path:
        return None
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, repaired_path, parsed.query, "")
    )


def css_source_markers(markup: str) -> list[tuple[int, str]]:
    markers: list[tuple[int, str]] = []
    for match in CSS_SOURCE_RE.finditer(markup):
        source_url = f"https://{match.group('host')}/{match.group('path')}"
        markers.append((match.start(), source_url))
    return markers


def original_css_asset_url(bad_url: str, source_url: str) -> str:
    parsed = urllib.parse.urlsplit(bad_url)
    raw_path = urllib.parse.unquote(parsed.path).lstrip("/")
    meaningful_parts = [
        part for part in raw_path.split("/") if part not in {"", ".", ".."}
    ]
    if meaningful_parts and meaningful_parts[0].endswith("editmysite.com"):
        host = meaningful_parts[0]
        path = "/".join(meaningful_parts[1:])
        return urllib.parse.urlunsplit(("https", host, "/" + path, parsed.query, ""))
    resolved = urllib.parse.urljoin(source_url, raw_path)
    resolved_parts = urllib.parse.urlsplit(resolved)
    return urllib.parse.urlunsplit(
        (
            resolved_parts.scheme,
            resolved_parts.netloc,
            resolved_parts.path,
            parsed.query,
            "",
        )
    )


def css_asset_entries(markup: str) -> list[tuple[re.Match[str], str]]:
    markers = css_source_markers(markup)
    positions = [position for position, _ in markers]
    entries: list[tuple[re.Match[str], str]] = []
    for match in CSS_URL_RE.finditer(markup):
        value = match.group("value")
        if not same_tiri_host(value):
            continue
        marker_index = bisect.bisect_right(positions, match.start()) - 1
        if marker_index < 0:
            continue
        entries.append(
            (match, original_css_asset_url(value, markers[marker_index][1]))
        )
    return entries


def rewrite_legacy_css(markup: str, available_assets: dict[str, Path]) -> tuple[str, int]:
    entries = css_asset_entries(markup)
    if not entries:
        return markup, 0
    result: list[str] = []
    cursor = 0
    rewritten = 0
    for match, source_url in entries:
        destination = available_assets.get(source_url)
        if not destination:
            continue
        result.append(markup[cursor : match.start()])
        result.append(f"url('{relative_link(LEGACY_CSS, destination)}')")
        cursor = match.end()
        rewritten += 1
    result.append(markup[cursor:])
    return "".join(result), rewritten


def fetch_asset(url: str, destination: Path) -> tuple[str, Path, int]:
    if destination.is_file() and destination.stat().st_size:
        return url, destination, destination.stat().st_size

    request_urls = [url]
    repaired_url = legacy_source_url(url)
    if repaired_url:
        request_urls.append(repaired_url)

    last_http_error: urllib.error.HTTPError | None = None
    for request_url in request_urls:
        request = urllib.request.Request(
            encoded_request_url(request_url),
            headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                declared = response.headers.get("Content-Length")
                if declared and int(declared) > MAX_ASSET_BYTES:
                    raise ValueError(f"asset too large ({declared} bytes)")
                data = response.read(MAX_ASSET_BYTES + 1)
                if len(data) > MAX_ASSET_BYTES:
                    raise ValueError("asset exceeded download limit")
                content_type = response.headers.get_content_type()
            break
        except urllib.error.HTTPError as error:
            last_http_error = error
    else:
        assert last_http_error is not None
        raise last_http_error

    suffix = destination.suffix.lower()
    if content_type == "text/html" and suffix not in {".html", ".htm"}:
        raise ValueError("server returned HTML instead of the requested asset")
    if not data:
        raise ValueError("server returned an empty asset")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".part")
    temporary.write_bytes(data)
    temporary.replace(destination)
    return url, destination, len(data)


def relative_link(source_html: Path, destination: Path, fragment: str = "") -> str:
    value = os.path.relpath(destination, source_html.parent).replace(os.sep, "/")
    return value + (f"#{fragment}" if fragment else "")


def page_destination(source_html: Path, parsed: urllib.parse.SplitResult) -> Path | None:
    filename = PAGE_ALIASES.get(parsed.path)
    if not filename:
        if parsed.path in {"", "/"}:
            filename = "index.html"
        elif PurePosixPath(parsed.path).suffix.lower() in {".html", ".htm"}:
            filename = PurePosixPath(urllib.parse.unquote(parsed.path)).name
        else:
            return None

    site_root = source_html.parent.parent
    local_candidate = site_root / "html" / filename
    if local_candidate.is_file():
        return local_candidate
    original_candidate = ARCHIVE_ROOT / "html" / filename
    return original_candidate if original_candidate.is_file() else None


def decode_cfemail(encoded: str) -> str:
    data = bytes.fromhex(encoded)
    if len(data) < 2:
        raise ValueError("invalid Cloudflare email payload")
    key = data[0]
    decoded = bytes(byte ^ key for byte in data[1:]).decode("utf-8")
    # One legacy social-link fragment on the live site contains a clear typo.
    return "office@tiri.tw" if decoded == "ofice@tiri.tw" else decoded


def rewrite_email_anchors(markup: str) -> tuple[str, int]:
    rewritten_count = 0

    def replace_anchor(match: re.Match[str]) -> str:
        nonlocal rewritten_count
        attrs = match.group("attrs")
        body = match.group("body")
        href_match = HREF_RE.search(attrs)
        if not href_match:
            return match.group(0)
        parsed = parsed_tiri_url(href_match.group("value"))
        if not parsed or parsed.path != "/cdn-cgi/l/email-protection":
            return match.group(0)

        encoded_match = CFEMAIL_RE.search(attrs + body)
        encoded = encoded_match.group(1) if encoded_match else parsed.fragment
        if not encoded or not re.fullmatch(r"[0-9a-fA-F]+", encoded):
            return match.group(0)
        try:
            address = decode_cfemail(encoded)
        except (ValueError, UnicodeDecodeError):
            return match.group(0)

        new_attrs = HREF_RE.sub(
            lambda item: (
                item.group("prefix")
                + item.group("quote")
                + f"mailto:{address}"
                + item.group("quote")
            ),
            attrs,
            count=1,
        )
        new_body = EMAIL_PLACEHOLDER_RE.sub(address, body)
        rewritten_count += 1
        return f"<a{new_attrs}>{new_body}</a>"

    return ANCHOR_RE.sub(replace_anchor, markup), rewritten_count


def niri_source_url(parsed: urllib.parse.SplitResult) -> str | None:
    if not parsed.path.startswith(NIRI_PROXY_PREFIX):
        return None
    path = parsed.path[len(NIRI_PROXY_PREFIX) :]
    return urllib.parse.urlunsplit(("https", "www.niri.org", "/" + path, parsed.query, parsed.fragment))


def recoverable_niri_path(value: str) -> str | None:
    decoded = html.unescape(value.strip())
    if decoded.startswith("//"):
        decoded = "https:" + decoded
    parsed = urllib.parse.urlsplit(decoded)
    if (parsed.hostname or "").lower() not in {"niri.org", "www.niri.org"}:
        return None
    path = urllib.parse.unquote(parsed.path)
    return path if path in NIRI_ARCHIVE_URLS else None


def gather_assets(html_files: list[Path]) -> set[str]:
    assets: set[str] = set()
    for html_file in html_files:
        markup = html_file.read_text(encoding="utf-8", errors="replace")
        for match in ATTRIBUTE_RE.finditer(markup):
            parsed = parsed_tiri_url(match.group("value"))
            if not parsed or parsed.path == "/cdn-cgi/l/email-protection":
                continue
            if niri_source_url(parsed):
                continue
            if match.group("prefix").strip().lower().startswith("href"):
                if page_destination(html_file, parsed):
                    continue
            assets.add(canonical_asset_url(parsed))
    return assets


def gather_niri_archives(html_files: list[Path]) -> set[str]:
    paths: set[str] = set()
    for html_file in html_files:
        markup = html_file.read_text(encoding="utf-8", errors="replace")
        for match in ATTRIBUTE_RE.finditer(markup):
            path = recoverable_niri_path(match.group("value"))
            if path:
                paths.add(path)
    return paths


def rewrite_html_file(
    html_file: Path,
    available_assets: dict[str, Path],
    available_niri_archives: dict[str, Path],
) -> tuple[int, int, int]:
    markup = html_file.read_text(encoding="utf-8", errors="replace")
    markup, email_count = rewrite_email_anchors(markup)
    page_count = 0
    asset_count = 0

    def replace_attribute(match: re.Match[str]) -> str:
        nonlocal page_count, asset_count
        raw_value = match.group("value")
        niri_path = recoverable_niri_path(raw_value)
        if niri_path and niri_path in available_niri_archives:
            replacement = relative_link(html_file, available_niri_archives[niri_path])
            asset_count += 1
            return (
                match.group("prefix")
                + match.group("quote")
                + replacement
                + match.group("quote")
            )

        parsed = parsed_tiri_url(raw_value)
        if not parsed or parsed.path == "/cdn-cgi/l/email-protection":
            return match.group(0)

        replacement: str | None = None
        is_href = match.group("prefix").strip().lower().startswith("href")
        if is_href:
            destination = page_destination(html_file, parsed)
            if destination:
                replacement = relative_link(html_file, destination, parsed.fragment)
                page_count += 1

        if replacement is None:
            niri_url = niri_source_url(parsed)
            if niri_url:
                replacement = niri_url
                asset_count += 1
            else:
                asset_url = canonical_asset_url(parsed)
                destination = available_assets.get(asset_url)
                if destination:
                    replacement = relative_link(html_file, destination, parsed.fragment)
                    asset_count += 1

        if replacement is None:
            return match.group(0)
        return (
            match.group("prefix")
            + match.group("quote")
            + replacement
            + match.group("quote")
        )

    rewritten = ATTRIBUTE_RE.sub(replace_attribute, markup)
    if rewritten != html_file.read_text(encoding="utf-8", errors="replace"):
        html_file.write_text(rewritten, encoding="utf-8")
    return page_count, asset_count, email_count


def remaining_tiri_runtime_references(html_files: list[Path]) -> list[str]:
    remaining: list[str] = []
    for html_file in html_files:
        markup = html_file.read_text(encoding="utf-8", errors="replace")
        for match in ATTRIBUTE_RE.finditer(markup):
            if parsed_tiri_url(match.group("value")):
                remaining.append(f"{html_file.relative_to(ROOT)} -> {match.group('value')}")
    return remaining


def main() -> None:
    html_files = sorted(
        html_file
        for site_root in SITE_ROOTS
        for html_file in (site_root / "html").glob("*.html")
    )
    assets = gather_assets(html_files)
    niri_archives = gather_niri_archives(html_files)
    legacy_css_markup = LEGACY_CSS.read_text(encoding="utf-8", errors="replace")
    theme_css_markup = THEME_CSS.read_text(encoding="utf-8", errors="replace")
    css_assets = {source_url for _, source_url in css_asset_entries(legacy_css_markup)}
    theme_assets = {
        relative_path: source_url
        for relative_path, source_url in THEME_ASSET_SOURCES.items()
        if relative_path in theme_css_markup
    }
    available_assets: dict[str, Path] = {}
    available_niri_archives: dict[str, Path] = {}
    available_css_assets: dict[str, Path] = {}
    failures: list[str] = []
    downloaded_bytes = 0

    print(f"HTML files: {len(html_files)}")
    print(f"TIRI content assets to localize: {len(assets)}")
    print(f"Recoverable NIRI archive documents: {len(niri_archives)}")
    print(f"Legacy CSS assets to localize: {len(css_assets)}")
    print(f"Theme assets to localize: {len(theme_assets)}")
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(fetch_asset, url, asset_destination(url)): url
            for url in sorted(assets)
        }
        for future in as_completed(futures):
            url = futures[future]
            try:
                _, destination, size = future.result()
                available_assets[url] = destination
                downloaded_bytes += size
            except (
                urllib.error.URLError,
                urllib.error.HTTPError,
                TimeoutError,
                socket.timeout,
                ValueError,
                OSError,
            ) as error:
                failures.append(f"{url}: {error}")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(
                fetch_asset,
                source_url,
                THEME_CSS.parent / relative_path,
            ): (relative_path, source_url)
            for relative_path, source_url in sorted(theme_assets.items())
        }
        for future in as_completed(futures):
            relative_path, source_url = futures[future]
            try:
                _, _, size = future.result()
                downloaded_bytes += size
            except (
                urllib.error.URLError,
                urllib.error.HTTPError,
                TimeoutError,
                socket.timeout,
                ValueError,
                OSError,
            ) as error:
                failures.append(f"{source_url} ({relative_path}): {error}")

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for path in sorted(niri_archives):
            original_url = urllib.parse.urlunsplit(
                ("https", "www.niri.org", path, "", "")
            )
            destination = asset_destination(original_url)
            futures[
                executor.submit(fetch_asset, NIRI_ARCHIVE_URLS[path], destination)
            ] = path
        for future in as_completed(futures):
            path = futures[future]
            try:
                _, destination, size = future.result()
                available_niri_archives[path] = destination
                downloaded_bytes += size
            except (
                urllib.error.URLError,
                urllib.error.HTTPError,
                TimeoutError,
                socket.timeout,
                ValueError,
                OSError,
            ) as error:
                failures.append(f"{NIRI_ARCHIVE_URLS[path]}: {error}")

    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {
            executor.submit(fetch_asset, url, asset_destination(url)): url
            for url in sorted(css_assets)
        }
        for future in as_completed(futures):
            url = futures[future]
            try:
                _, destination, size = future.result()
                available_css_assets[url] = destination
                downloaded_bytes += size
            except (
                urllib.error.URLError,
                urllib.error.HTTPError,
                TimeoutError,
                socket.timeout,
                ValueError,
                OSError,
            ) as error:
                failures.append(f"{url}: {error}")

    page_total = 0
    asset_total = 0
    email_total = 0
    for html_file in html_files:
        pages, localized_assets, emails = rewrite_html_file(
            html_file, available_assets, available_niri_archives
        )
        page_total += pages
        asset_total += localized_assets
        email_total += emails

    rewritten_css, css_reference_total = rewrite_legacy_css(
        legacy_css_markup, available_css_assets
    )
    if rewritten_css != legacy_css_markup:
        LEGACY_CSS.write_text(rewritten_css, encoding="utf-8")

    remaining = remaining_tiri_runtime_references(html_files)
    remaining_css = [
        match.group("value")
        for match in CSS_URL_RE.finditer(rewritten_css)
        if same_tiri_host(match.group("value"))
    ]
    print(f"Page links localized: {page_total}")
    print(f"Asset references localized: {asset_total}")
    print(f"Email links restored: {email_total}")
    print(f"Legacy CSS references localized: {css_reference_total}")
    print(f"Local asset bytes available: {downloaded_bytes}")
    print(f"Download failures: {len(failures)}")
    for item in failures:
        print(f"DOWNLOAD FAILED: {item}")
    print(f"Remaining tiri.tw runtime references: {len(remaining)}")
    for item in remaining[:100]:
        print(f"REMAINING: {item}")
    print(f"Remaining tiri.tw CSS references: {len(remaining_css)}")
    for item in remaining_css[:100]:
        print(f"REMAINING CSS: {item}")

    if failures or remaining or remaining_css:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
