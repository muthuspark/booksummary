#!/usr/bin/env python3
"""Verify the built Hugo site with only the Python standard library."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib
import json
import re
import sys
import tomllib
import xml.etree.ElementTree as ET

from author_pages import verify_author_pages

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'docs').resolve()
CONFIG = tomllib.loads((ROOT / 'hugo.toml').read_text())
BASE = CONFIG['baseURL'].rstrip('/')
errors = []


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.images = []
        self.canonical = None
        self.schemas = []
        self.in_schema = False
        self.schema = ''
        self.mermaid_count = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'pre' and 'mermaid' in attrs.get('class', '').split():
            self.mermaid_count += 1
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])
        if tag in ('img', 'script') and attrs.get('src'):
            self.links.append(attrs['src'])
        if tag == 'img':
            self.images.append(attrs)
            for candidate in attrs.get('srcset', '').split(','):
                if candidate.strip():
                    self.links.append(candidate.strip().split()[0])
        if tag == 'link' and attrs.get('href'):
            self.links.append(attrs['href'])
            if attrs.get('rel') == 'canonical':
                self.canonical = attrs['href']
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.in_schema = True
            self.schema = ''

    def handle_data(self, data):
        if self.in_schema:
            self.schema += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.in_schema:
            self.in_schema = False
            try:
                self.schemas.append(json.loads(self.schema))
            except json.JSONDecodeError as error:
                errors.append(f'Invalid structured data: {error}')


def require(condition, message):
    if not condition:
        errors.append(message)


def local_target(href, page_path):
    parts = urlsplit(href)
    if parts.scheme or parts.netloc or not parts.path:
        return None
    path = unquote(parts.path)
    dest = OUTPUT / path.lstrip('/') if path.startswith('/') else page_path.parent / path
    if path.endswith('/') or dest.is_dir():
        dest /= 'index.html'
    return dest


sources = sorted((ROOT / 'content/posts').rglob('index.md'))
require(bool(sources), 'No source summaries found')
index = json.loads((OUTPUT / 'search.json').read_text())
require(len(index) == len(sources), f'Search has {len(index)} records for {len(sources)} summaries')
indexed_urls = {entry['url'] for entry in index}
require(len(indexed_urls) == len(index), 'Duplicate search URLs')
require((OUTPUT / 'search.json').stat().st_size < 700_000, 'Metadata search index exceeds 700 KB')
full_text = {}
for chunk_url in {entry['contentURL'] for entry in index}:
    chunk_path = OUTPUT / chunk_url.lstrip('/')
    require(chunk_path.is_file(), f'Missing full-text chunk: {chunk_url}')
    if chunk_path.is_file():
        for row in json.loads(chunk_path.read_text()):
            full_text[row['url']] = row['content']
require(set(full_text) == indexed_urls, 'Full-text search does not cover all summaries')
for entry in index:
    require('content' not in entry, 'Article text is embedded in the metadata index')
    require(bool(full_text.get(entry['url'])), f"Empty full-text search record: {entry['url']}")
    require(entry['image'].endswith('.webp'), f"Non-WebP thumbnail: {entry['url']}")
    for image in [entry['image']] + [item.strip().split()[0] for item in entry['imageSrcset'].split(',')]:
        target = OUTPUT / image.lstrip('/')
        require(target.is_file(), f'Missing responsive thumbnail: {image}')
        if target.is_file():
            require(target.stat().st_size < 30_000, f'Oversized thumbnail: {image}')
home_html = (OUTPUT / 'index.html').read_text()
require('1000+' not in home_html, 'Homepage count is outdated')
require(home_html.lower().count('browse by category') == 1, 'Duplicate category section on homepage')
require(f'{len(sources)} book summaries' in home_html, 'Homepage count is not current')

for source in sources:
    relative = source.relative_to(ROOT / 'content').with_suffix('.html')
    page_path = OUTPUT / relative
    route = '/' + relative.parent.as_posix() + '/'
    require(page_path.is_file(), f'Missing legacy route: {route}')
    require(route in indexed_urls, f'Missing search record: {route}')
    if not page_path.is_file():
        continue
    text = page_path.read_text()
    page = Page(text)
    require(page.canonical == BASE + route, f'Wrong canonical for {route}: {page.canonical}')
    types = {schema.get('@type') for schema in page.schemas}
    require({'Article', 'Book'} <= types, f'Missing Article/Book metadata for {route}')
    require('0001-01-01' not in text, f'Invented date in {route}')
    source_text = source.read_text()
    require(not re.search(r'^```\{(?:mermaid|dot|=html)\}', source_text, re.M), f'Unconverted Quarto fence: {source}')
    require(not re.search(r'^```mermaid\b', source_text, re.M), f'Unconverted Mermaid diagram: {source}')
    require(page.mermaid_count == 0, f'Mermaid runtime diagram remains: {route}')
    source_image = source.parent / 'image.png'
    output_image = page_path.parent / 'image.png'
    require(output_image.is_file(), f'Missing image: {output_image}')
    if output_image.is_file():
        require(hashlib.sha256(source_image.read_bytes()).digest() == hashlib.sha256(output_image.read_bytes()).digest(), f'Image changed: {route}')

# Check every converted diagram's image reference, accessible SVG, graph, and published copy.
diagrams = json.loads((ROOT / 'scripts/diagrams.json').read_text())
diagram_files = [entry['file'] for entry in diagrams]
require(len(diagram_files) == len(set(diagram_files)), 'Duplicate diagram asset paths')
for entry in diagrams:
    source = ROOT / entry['file']
    published = OUTPUT / source.relative_to(ROOT / 'content')
    article = source.with_name('index.md').read_text()
    require(article.count('](' + source.name + ')') == 1, f'Missing or duplicate diagram reference: {source}')
    require(source.is_file() and published.is_file(), f'Missing diagram asset: {source}')
    if not source.is_file() or not published.is_file():
        continue
    require(source.read_bytes() == published.read_bytes(), f'Diagram copy differs: {source}')
    try:
        svg = ET.parse(source).getroot()
    except ET.ParseError as error:
        errors.append(f'Invalid SVG {source}: {error}')
        continue
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    require(svg.tag == '{http://www.w3.org/2000/svg}svg', f'Not an SVG image: {source}')
    require(svg.get('role') == 'img' and svg.get('aria-labelledby') == 'title description', f'Inaccessible diagram: {source}')
    require(bool(svg.findtext('svg:title', namespaces=ns)) and bool(svg.findtext('svg:desc', namespaces=ns)), f'Missing diagram description: {source}')
    require(not svg.findall('.//svg:script', ns) and not svg.findall('.//svg:foreignObject', ns), f'Non-standalone SVG: {source}')
    nodes = svg.findall('.//svg:g[@class="node"]', ns)
    edges = svg.findall('.//svg:g[@class="edge"]', ns)
    require(len(nodes) == len(entry['nodes']), f'Diagram lost nodes: {source}')
    require(len(edges) == len(entry['edges']), f'Diagram lost connections: {source}')
    expected_labels = sorted(' '.join(node['label'].split()) for node in entry['nodes'])
    actual_labels = sorted(' '.join(' '.join(node.itertext()).split()) for node in nodes)
    require(actual_labels == expected_labels, f'Diagram labels differ: {source}')
require(not (OUTPUT / 'vendor/mermaid.min.js').exists(), 'Mermaid runtime still published')
require(not (OUTPUT / 'js/diagrams.js').exists(), 'Diagram runtime still published')

html_files = list(OUTPUT.rglob('*.html'))
for path in html_files:
    text = path.read_text()
    require(not re.search(r'adsbygoogle|googlesyndication|quarto-html|quarto-search', text), f'Legacy runtime or ad script in {path}')
    page = Page(text)
    for href in page.links:
        dest = local_target(href, path)
        if dest is not None:
            require(dest.is_file(), f'Broken local link in {path.relative_to(OUTPUT)}: {href}')
    for image in page.images:
        require('alt' in image, f'Missing image alt attribute in {path}')

for name in ('sitemap.xml', 'index.xml', 'posts/index.xml'):
    try:
        ET.parse(OUTPUT / name)
    except (OSError, ET.ParseError) as error:
        errors.append(f'Invalid or missing {name}: {error}')
require((OUTPUT / '404.html').is_file(), 'Missing 404 page')
require((OUTPUT / 'CNAME').read_text().strip() == 'summaries.muthu.co', 'Custom domain missing')
require(not (OUTPUT / 'ads.txt').exists(), 'Obsolete ads.txt still published')
require('Sitemap: ' + BASE + '/sitemap.xml' in (OUTPUT / 'robots.txt').read_text(), 'Robots sitemap is incorrect')
try:
    errors.extend(verify_author_pages(ROOT, OUTPUT))
except (ValueError, OSError) as error:
    errors.append(str(error))

if errors:
    print('\n'.join(errors[:40]), file=sys.stderr)
    sys.exit(f'{len(errors)} verification errors')
print(f'Verified {len(sources)} summaries, {len(index)} search records, images, diagrams, metadata, feeds, and links across {len(html_files)} HTML pages.')
