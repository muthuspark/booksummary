#!/usr/bin/env python3
"""Validate structured credits and generated author pages, using the standard library."""
from collections import defaultdict
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
import json
import re
import sys
import tomllib
import unicodedata


# Reviewed aliases from the initial credit inventory. Keep future additions on
# the same catalog instead of reintroducing these known name variants.
CANONICAL_ALIASES = {
    'Alan W. Watts': 'Alan Watts',
    'Max H. Bazerman': 'Max Bazerman',
    'Noah J. Goldstein': 'Noah Goldstein',
    'Richard J. Davidson': 'Richard Davidson',
    'Robert B. Cialdini': 'Robert Cialdini',
}


def author_names(text, source):
    """The supported author-list syntax is a JSON array on one YAML line."""
    match = re.match(r'\A---\s*\n(.*?)\n---(?:\s*\n|$)', text, re.S)
    if not match:
        raise ValueError(f'{source}: missing YAML front matter')
    lines = re.findall(r'^authors:[ \t]*(.*)$', match[1], re.M)
    if len(lines) != 1:
        raise ValueError(f'{source}: expected exactly one authors field')
    try:
        names = json.loads(lines[0])
    except json.JSONDecodeError as error:
        raise ValueError(f'{source}: authors must be a one-line JSON array of quoted names') from error
    if not isinstance(names, list) or not names:
        raise ValueError(f'{source}: authors must be a nonempty list')
    seen = set()
    for name in names:
        if not isinstance(name, str) or not name.strip() or name != name.strip():
            raise ValueError(f'{source}: authors entries must be nonblank, trimmed strings')
        if name in CANONICAL_ALIASES:
            raise ValueError(f'{source}: inconsistent author name {name!r}; use {CANONICAL_ALIASES[name]!r}')
        key = identity_key(name)
        if not key or key in seen:
            raise ValueError(f'{source}: duplicate or invalid authors entry: {name!r}')
        seen.add(key)
    return names


def identity_key(name):
    normalized = unicodedata.normalize('NFKD', name).casefold()
    return ''.join(c for c in normalized if c.isalnum())


def source_credits(root):
    credits = {}
    canonical = {}
    errors = []
    for source in sorted((root / 'content/posts').rglob('index.md')):
        text = source.read_text()
        front = text.split('---', 2)[1] if text.startswith('---') else ''
        if re.search(r'^draft:\s*true\s*$', front, re.M | re.I):
            continue
        try:
            names = author_names(text, source)
            for name in names:
                key = identity_key(name)
                if key in canonical and canonical[key][0] != name:
                    other, origin = canonical[key]
                    raise ValueError(f'{source}: inconsistent author name {name!r}; {other!r} already used in {origin}')
                canonical[key] = (name, source)
            credits['/' + source.parent.relative_to(root / 'content').as_posix() + '/'] = names
        except ValueError as error:
            errors.append(str(error))
    if errors:
        raise ValueError('\n'.join(errors))
    return credits


@dataclass
class Element:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    @property
    def text(self):
        return ''.join(c.text if isinstance(c, Element) else c for c in self.children)

    def find(self, tag=None, cls=None, **attrs):
        found = []
        for child in self.children:
            if isinstance(child, Element):
                if ((tag is None or child.tag == tag)
                        and (cls is None or cls in child.attrs.get('class', '').split())
                        and all(child.attrs.get(k) == v for k, v in attrs.items())):
                    found.append(child)
                found.extend(child.find(tag, cls, **attrs))
        return found


class Document(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, text):
        super().__init__()
        self.root = Element('document')
        self.stack = [self.root]
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        node = Element(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def read_page(path):
    return Document(path.read_text()).root


def verify_author_pages(root, output):
    credits = source_credits(root)
    expected = defaultdict(set)
    for route, names in credits.items():
        for name in names:
            expected[name].add(route)
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    directory_file = output / 'authors/index.html'
    if not directory_file.is_file():
        return ['Missing Authors directory: ' + str(directory_file)]
    directory = read_page(directory_file)
    lists = directory.find('div', 'author-directory')
    if len(lists) != 1:
        return ['Expected one author-directory container in ' + str(directory_file)]
    groups = lists[0].find('section', 'author-group')
    jumps = directory.find('nav', 'author-alphabet')
    heading_ids = [h.attrs.get('id') for group in groups for h in group.find('h2')]
    require(bool(groups) and len(heading_ids) == len(groups), 'Missing author letter headings')
    require(len(heading_ids) == len(set(heading_ids)), 'Duplicate author letter heading IDs')
    require(len(jumps) == 1 and [a.attrs.get('href') for a in jumps[0].find('a')] == ['#' + value for value in heading_ids], 'Author letter navigation does not match sections')
    for group in groups:
        headings = group.find('h2')
        names = group.find('span', 'term-name')
        require(bool(headings) and all(name.text[0].upper() == headings[0].text for name in names), 'Author in the wrong letter section')
    searches = directory.find('input', id='author-query')
    require(len(searches) == 1 and searches[0].attrs.get('type') == 'search', 'Missing author search input')
    require(bool(directory.find('label', **{'for': 'author-query'})), 'Missing author search label')
    author_routes = {}
    route_names = {}
    order = []
    for li in lists[0].find('li'):
        links = li.find('a')
        labels = li.find('span', 'term-name')
        counts = li.find('span', 'muted')
        if len(links) != 1 or len(labels) != 1 or len(counts) != 1:
            errors.append('Malformed author directory entry: ' + li.text)
            continue
        name, route = labels[0].text, links[0].attrs.get('href', '')
        order.append(name)
        require(name not in author_routes, f'Duplicate directory author: {name}')
        require(route.startswith('/authors/'), f'Invalid author route: {name}: {route}')
        require(route not in route_names, f'Author route collision: {name} and {route_names.get(route)}: {route}')
        author_routes[name] = route
        route_names[route] = name
        count = len(expected.get(name, set()))
        require(counts[0].text.strip() == f'{count} {"summary" if count == 1 else "summaries"}', f'Wrong directory count for {name}')
    require(set(author_routes) == set(expected), f'Directory author mismatch: missing {set(expected) - set(author_routes)}, unexpected {set(author_routes) - set(expected)}')
    require(order == sorted(order, key=lambda n: ''.join(c for c in unicodedata.normalize('NFKD', n).casefold() if not unicodedata.combining(c))), 'Author directory is not alphabetical')

    # Hugo's ByTitle export supplies the exact site collation order, not a second sort implementation.
    search = json.loads((output / 'search.json').read_text())
    rank = {entry['url']: i for i, entry in enumerate(search)}
    pager_size = tomllib.loads((root / 'hugo.toml').read_text()).get('pagination', {}).get('pagerSize', 36)
    for name, route in author_routes.items():
        folder = output / unquote(route).lstrip('/')
        first = folder / 'index.html'
        if not first.is_file():
            errors.append(f'Missing author page: {name}: {route}')
            continue
        extra = sorted((folder / 'page').glob('*/index.html'), key=lambda p: int(p.parent.name))
        files = [first] + [p for p in extra if p.parent.name != '1']
        gathered = []
        expected_order = sorted(expected[name], key=lambda r: rank.get(r, -1))
        total = len(expected[name])
        require(len(files) == max(1, (total + pager_size - 1) // pager_size), f'Wrong page count: {name}')
        for number, file in enumerate(files, 1):
            doc = read_page(file)
            h1 = doc.find('h1')
            require(bool(h1) and h1[0].text == name, f'Wrong author heading: {file}')
            grids = doc.find('div', id='book-grid')
            page_books = []
            if len(grids) == 1:
                for title in grids[0].find(cls='book-title'):
                    page_books.extend(a.attrs.get('href') for a in title.find('a'))
            else:
                errors.append(f'Missing book-grid: {file}')
            gathered.extend(page_books)
            require(page_books == expected_order[(number - 1) * pager_size:number * pager_size], f'Wrong catalog order or membership: {file}')
            counts = doc.find('p', id='result-count')
            require(bool(counts) and counts[0].text.startswith(f'{total} {"summary" if total == 1 else "summaries"}'), f'Wrong catalog count: {file}')
            if len(files) > 1:
                pagination = doc.find('nav', id='pagination')
                require(bool(pagination) and f'Page {number} of {len(files)}' in pagination[0].text, f'Wrong pagination: {file}')
                for dest_number, label in [(number - 1, 'Previous'), (number + 1, 'Next')]:
                    if 1 <= dest_number <= len(files):
                        links = pagination[0].find('a') if pagination else []
                        wanted = route if dest_number == 1 else route + f'page/{dest_number}/'
                        require(any(label in a.text and a.attrs.get('href') == wanted for a in links), f'Missing {label} link: {file}')
        require(len(gathered) == len(set(gathered)) and set(gathered) == expected[name], f'Author catalog membership mismatch: {name}')

    headers_seen = set()
    for file in output.rglob('*.html'):
        doc = read_page(file)
        for span in doc.find('span', 'author-links'):
            source = span.attrs.get('data-summary')
            names = credits.get(source)
            links = span.find('a')
            require(names is not None, f'Unknown author credit source: {file}: {source}')
            require([a.text for a in links] == names, f'Wrong author link labels: {file}: {source}')
            require([a.attrs.get('href') for a in links] == [author_routes.get(n) for n in names or []], f'Wrong author link targets: {file}: {source}')
        for card in doc.find('article', 'book-card'):
            require(len(card.find('span', 'author-links')) == 1, f'Book card missing author links: {file}')
        for header in doc.find('header', 'post-header'):
            spans = header.find('span', 'author-links')
            require(len(spans) == 1, f'Summary header missing author links: {file}')
            if spans:
                headers_seen.add(spans[0].attrs.get('data-summary'))
        menus = doc.find('nav', 'site-menu')
        if menus:
            require(any(a.text == 'Authors' and a.attrs.get('href') == '/authors/' for a in menus[0].find('a')), f'Missing Authors navigation: {file}')
    require(headers_seen == set(credits), 'Not every summary header has author links')
    return errors


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    try:
        if len(sys.argv) > 1:
            errors = verify_author_pages(root, Path(sys.argv[1]).resolve())
            if errors:
                raise ValueError('\n'.join(errors))
            print('Verified author directory, credits, links, catalogs, counts, and pagination.')
        else:
            credits = source_credits(root)
            print(f'Validated author credits for {len(credits)} published summaries.')
    except (ValueError, OSError) as error:
        sys.exit(str(error))
