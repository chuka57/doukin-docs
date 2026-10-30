#!/usr/bin/env python3
"""Check local HTML links, assets and IDs without external dependencies."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = []
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        self.links.extend(attrs[key] for key in ('href', 'src') if attrs.get(key))


def check(root):
    root = Path(root).resolve()
    pages = {path: Document(path.read_text(encoding='utf-8')) for path in root.rglob('*.html')}
    if root / 'index.html' not in pages:
        raise ValueError('index.html is missing')
    count = 0
    for path, document in pages.items():
        duplicates = [key for key, total in Counter(document.ids).items() if total > 1]
        if duplicates:
            raise ValueError(f'{path}: duplicate IDs: {duplicates}')
        for link in document.links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc:
                continue
            if parts.path.startswith('/'):
                raise ValueError(f'{path}: root-relative URL breaks PR previews: {link}')
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            if not target.is_relative_to(root) or not target.is_file():
                raise ValueError(f'{path}: missing or escaping link: {link}')
            if parts.fragment and target in pages and unquote(parts.fragment) not in pages[target].ids:
                raise ValueError(f'{path}: missing anchor: {link}')
            count += 1
    return len(pages), count


if __name__ == '__main__':
    pages, links = check(sys.argv[1] if len(sys.argv) > 1 else 'docs')
    print(f'Checked {pages} pages and {links} local links/assets.')
