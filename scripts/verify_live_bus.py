#!/usr/bin/env python3
from collections import deque
from html.parser import HTMLParser
import pathlib
from urllib.error import HTTPError, URLError
import urllib.parse
import urllib.request

START_URL = "https://constellation25.github.io/AiMetaverse/"
ALLOWED_HOST = "constellation25.github.io"
ALLOWED_PREFIX = "/AiMetaverse/"
MAX_PAGES = 200
TIMEOUT = 12
HEADERS = {
    "Cache-Control": "no-cache",
    "User-Agent": "c25-bus-live-verifier/1.0",
}

SKIP_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico",
    ".css", ".js", ".mjs", ".json", ".xml", ".txt", ".pdf",
    ".zip", ".tar", ".gz", ".mp4", ".webm", ".mp3", ".wav",
    ".woff", ".woff2", ".ttf", ".eot", ".map",
}


class PageTagParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        attr_map = {k.lower(): (v or "").strip() for k, v in attrs if k}
        if t == "a" and attr_map.get("href"):
            self.links.append(attr_map["href"])
        elif t == "script" and attr_map.get("src"):
            self.scripts.append(attr_map["src"])


def normalize_page_url(base_url: str, raw_href: str) -> str | None:
    href = raw_href.strip()
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    joined = urllib.parse.urljoin(base_url, href)
    parsed = urllib.parse.urlparse(joined)
    if parsed.scheme not in ("http", "https") or parsed.netloc.lower() != ALLOWED_HOST:
        return None
    path = parsed.path or "/"
    if path == "/AiMetaverse":
        path = ALLOWED_PREFIX
    if not path.startswith(ALLOWED_PREFIX):
        return None
    if pathlib.Path(path).suffix.lower() in SKIP_EXTS:
        return None
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc.lower(), path, "", "", ""))


def fetch(url: str, read_body: bool = False) -> tuple[int | None, str, str | None]:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            status = resp.getcode()
            body = ""
            if read_body and status == 200:
                body = resp.read(2_000_000).decode("utf-8", errors="replace")
            return status, body, None
    except HTTPError as exc:
        return exc.code, "", f"HTTP {exc.code}"
    except URLError as exc:
        return None, "", str(exc.reason)
    except OSError as exc:
        return None, "", str(exc)


def main() -> int:
    queue: deque[str] = deque([START_URL])
    seen: set[str] = {START_URL}
    checked_pages = 0
    pages_missing_bus_tag: list[str] = []
    non_200_pages: list[tuple[str, int | None, str | None]] = []
    bus_urls_seen: set[str] = set()

    while queue and checked_pages < MAX_PAGES:
        page_url = queue.popleft()
        checked_pages += 1
        status, html, err = fetch(page_url, read_body=True)
        if status != 200:
            non_200_pages.append((page_url, status, err))
            continue

        parser = PageTagParser()
        try:
            parser.feed(html)
        except Exception:
            pass

        matched_bus_srcs = [
            urllib.parse.urljoin(page_url, s)
            for s in parser.scripts
            if "c25-platform-bus.js" in s
        ]
        if not matched_bus_srcs:
            pages_missing_bus_tag.append(page_url)
        else:
            for b_url in matched_bus_srcs:
                bus_urls_seen.add(b_url)

        for raw_href in parser.links:
            nxt = normalize_page_url(page_url, raw_href)
            if nxt and nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)

    bus_status_failures: list[tuple[str, int | None, str | None]] = []
    for b_url in sorted(bus_urls_seen):
        b_status, _, b_err = fetch(b_url, read_body=False)
        if b_status != 200:
            bus_status_failures.append((b_url, b_status, b_err))

    print(f"Pages checked            : {checked_pages}")
    print(f"Non-200 pages            : {len(non_200_pages)}")
    print(f"Pages missing bus tag    : {len(pages_missing_bus_tag)}")
    print(f"Unique bus script URLs   : {len(bus_urls_seen)}")
    print(f"Non-200 bus script URLs  : {len(bus_status_failures)}")

    for u, st, er in non_200_pages:
        print(f"  [PAGE {st or 'ERR'}] {u} ({er})")
    for u in pages_missing_bus_tag:
        print(f"  [NO TAG] {u}")
    for u, st, er in bus_status_failures:
        print(f"  [BUS {st or 'ERR'}] {u} ({er})")

    has_failures = bool(non_200_pages or pages_missing_bus_tag or bus_status_failures)
    return 1 if has_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
