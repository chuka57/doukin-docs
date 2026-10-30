"""Small, static HTML components shared by every page of the guide."""
from html import escape


def icon(kind):
    paths = {
        'book': '<path d="M4 5h6c2 0 2 1 2 1s0-1 2-1h6v14h-6c-2 0-2 1-2 1s0-1-2-1H4zM12 6v14M7 9h2M15 9h2M7 12h2M15 12h2"/>',
        'key': '<circle cx="8" cy="9" r="4"/><path d="m11 12 8 8m-4-4 3-3m-1 5 3-3"/>',
        'shield': '<path d="m12 3 8 3v5c0 5-8 10-8 10S4 16 4 11V6zM8 12l3 3 5-6"/>',
        'cloud': '<path d="M7 18a5 5 0 1 1 0-10 6 6 0 0 1 11-1 5.5 5.5 0 0 1 0 11z"/>',
        'db': '<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 4 16 4 16 0V6M4 12c0 4 16 4 16 0"/>',
        'cost': '<rect x="5" y="3" width="14" height="18" rx="3"/><path d="M8 7h8M8 12h2m4 0h2M8 16h2m4 0h2"/>',
        'map': '<path d="m3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2zM9 3v16M15 5v16"/>',
        'steps': '<circle cx="6" cy="6" r="3"/><circle cx="18" cy="18" r="3"/><path d="M9 6h6a3 3 0 0 1 0 6H9a3 3 0 0 0 0 6h6"/>',
        'share': '<circle cx="6" cy="12" r="3"/><circle cx="18" cy="5" r="3"/><circle cx="18" cy="19" r="3"/><path d="m9 10 6-4M9 14l6 3"/>',
        'leaf': '<path d="M4 20C1 4 12 2 21 3c0 13-5 19-14 14M4 20 16 8"/>',
        'mail': '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 7 8 6 8-6"/>',
        'person': '<circle cx="12" cy="7" r="4"/><path d="M4 21v-3a8 8 0 0 1 16 0v3"/>',
        'check': '<path d="m4 12 5 5L20 6"/>',
    }
    return '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round">' + paths.get(kind, paths['book']) + '</svg>'


def ref(*keys):
    return '<span class="refs">' + ' '.join(f'<a href="#ref-{key}" data-ref="{key}" aria-label="出典 {key}">{key}</a>' for key in keys) + '</span>'


def section(key, title, content):
    return f'<section class="chapter"><h2 id="{key}">{title}</h2>{content}</section>'


def note(title, text, tone='green'):
    return f'<aside class="note {tone}"><div class="note-symbol" aria-hidden="true">{icon("leaf" if tone == "green" else "shield")}</div><div><strong>{title}</strong><p>{text}</p></div></aside>'


def card(title, text, kind='book', href=None, tag=None):
    heading = f'<a href="{href}">{title}<span aria-hidden="true"> ↗</span></a>' if href else title
    badge = f'<span class="tag">{tag}</span>' if tag else ''
    return f'<article class="card">{icon(kind)}{badge}<h3>{heading}</h3><p>{text}</p></article>'


def grid(*cards):
    return '<div class="cards">' + ''.join(cards) + '</div>'


def bullets(*items):
    return '<ul class="plain-list">' + ''.join(f'<li>{item}</li>' for item in items) + '</ul>'


def steps(items):
    return '<ol class="steps">' + ''.join(f'<li><div><h3>{title}</h3><p>{text}</p></div></li>' for title, text in items) + '</ol>'


def details(title, body):
    return f'<details><summary>{title}</summary><div class="details-body">{body}</div></details>'


def table(headers, rows, caption):
    body = []
    for row in rows:
        cells = ''.join((f'<th scope="row">{value}</th>' if i == 0 else f'<td>{value}</td>') for i, value in enumerate(row))
        body.append(f'<tr>{cells}</tr>')
    return f'<div class="table-wrap" tabindex="0" role="region" aria-label="{escape(caption, quote=True)}"><table><caption>{caption}</caption><thead><tr>' + ''.join(f'<th scope="col">{x}</th>' for x in headers) + '</tr></thead><tbody>' + ''.join(body) + '</tbody></table></div>'


def diagram(nodes, caption, links=None):
    parts = []
    for kind, title, text in nodes:
        heading = f'<a href="{links[kind]}">{title} ↗</a>' if links and kind in links else title
        parts.append(f'<li><div class="diagram-icon">{icon(kind)}</div><strong>{heading}</strong><span>{text}</span></li>')
    blocks = ''.join(parts)
    return f'<figure class="diagram"><ol>{blocks}</ol><figcaption>{caption}</figcaption></figure>'


def definition(items):
    return '<dl class="definitions">' + ''.join(f'<div><dt>{term}</dt><dd>{text}</dd></div>' for term, text in items) + '</dl>'
