"""Validate the generated Pages site using only Python's standard library."""
import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ORIGIN = "https://n-e-e-t.github.io"
PREFIX = "/pages/"
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.canonicals = []
        self.descriptions = []
        self.robots = ""
        self.refs = []
        self.ids = set()
        self.schemas = []
        self.schema = None
        self.titles = 0
        self.h1s = 0
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "title":
            self.titles += 1
        if tag == "h1":
            self.h1s += 1
        if tag == "meta":
            if attrs.get("name") == "description":
                self.descriptions.append(attrs.get("content", ""))
            if attrs.get("name") == "robots":
                self.robots = attrs.get("content", "")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href", ""))
        if tag in ("a", "link", "img", "script"):
            ref = attrs.get("href") or attrs.get("src")
            if ref:
                self.refs.append(ref)
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.schema = ""

    def handle_data(self, data):
        if self.schema is not None:
            self.schema += data

    def handle_endtag(self, tag):
        if tag == "script" and self.schema is not None:
            try:
                self.schemas.append(json.loads(self.schema))
            except ValueError as exc:
                errors.append(f"{self.path}: invalid JSON-LD: {exc}")
            self.schema = None


def file_for(url):
    parsed = urlsplit(url)
    if parsed.netloc != urlsplit(ORIGIN).netloc:
        return None
    path = unquote(parsed.path)
    if not path.startswith(PREFIX):
        return None
    target = ROOT / path[len(PREFIX):]
    return target / "index.html" if path.endswith("/") else target


def page_url(path):
    relative = path.relative_to(ROOT).as_posix()
    if relative.endswith("index.html"):
        relative = relative[:-len("index.html")]
    return ORIGIN + PREFIX + relative


check(ROOT.is_dir(), f"Build directory does not exist: {ROOT}")
pages = {p: Page(p) for p in ROOT.rglob("*.html")}
check(bool(pages), "No HTML pages found")
canonical_urls = set()
for path, page in pages.items():
    label = path.relative_to(ROOT)
    base = page_url(path)
    check(page.titles == 1, f"{label}: expected exactly one title")
    check(page.h1s == 1, f"{label}: expected exactly one h1")
    check(len(page.descriptions) == 1 and bool(page.descriptions[0].strip()),
          f"{label}: missing or duplicated description")
    check(len(page.canonicals) == 1, f"{label}: missing or duplicated canonical")
    if len(page.canonicals) == 1:
        canonical = page.canonicals[0]
        check(canonical.startswith(ORIGIN + PREFIX), f"{label}: non-production canonical")
        check(file_for(canonical) == path, f"{label}: canonical does not resolve to this page")
        if "noindex" not in page.robots:
            check(canonical not in canonical_urls, f"{label}: duplicate canonical")
            canonical_urls.add(canonical)
    for ref in page.refs:
        url = urljoin(base, ref)
        target = file_for(url)
        if target is None:
            continue
        check(target.is_file(), f"{label}: broken local link: {ref}")
        fragment = unquote(urlsplit(url).fragment)
        if fragment and target in pages:
            check(fragment in pages[target].ids, f"{label}: missing anchor: {ref}")
    if path.name == "404.html":
        check("noindex" in page.robots, f"{label}: 404 page should be noindex")
    if "gakumas-unity-fast-sync" in path.name:
        articles = [s for s in page.schemas if s.get("@type") == "BlogPosting"]
        check(len(articles) == 1, f"{label}: missing BlogPosting structured data")
        if articles:
            check(articles[0].get("datePublished") == "2026-09-25T00:00:00+09:00",
                  f"{label}: publication date changed")
        check("/2026/09/24/" in base, f"{label}: existing public URL changed")
        check("noindex" not in page.robots, f"{label}: article must remain indexable")

namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
listed = set()
for name in ("sitemap.xml", "site-pages.xml", "blog/sitemap.xml"):
    path = ROOT / name
    check(path.is_file(), f"Missing sitemap: {name}")
    if not path.is_file():
        continue
    try:
        tree = ET.parse(path)
        for element in tree.findall(".//s:loc", namespace):
            url = element.text or ""
            target = file_for(url)
            check(target is not None and target.is_file(), f"{name}: invalid sitemap URL: {url}")
            if target in pages:
                check("noindex" not in pages[target].robots, f"{name}: noindex page listed")
                listed.add(unquote(url))
    except ET.ParseError as exc:
        errors.append(f"{name}: invalid XML: {exc}")
for canonical in canonical_urls:
    check(unquote(canonical) in listed, f"Indexable page missing from sitemap: {canonical}")

if errors:
    print("\n".join(f"ERROR: {error}" for error in errors))
    sys.exit(1)
print(f"PASS: {len(pages)} HTML pages; metadata, JSON-LD, local links, anchors, and 3 sitemaps.")
