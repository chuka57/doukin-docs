#!/usr/bin/env python3
"""Build the offline, multi-page doukin guide. Python standard library only."""
from pathlib import Path
from html import escape
import re

from guide_content import make_pages, EXTRA_SOURCES
from guide_ui import icon
from guide_history import add_history_page, load_history, version_anchor
from guide_minimal_auth import SOURCE_DATES

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'docs'
DATE = '2026-10-30'


def sources():
    text = (ROOT / 'content' / 'comparison.md').read_text(encoding='utf-8')
    urls = dict(re.findall(r'^\[(s\d+)\]: (https?://\S+)', text, re.M))
    rows = re.findall(r'^\| (S\d+) \| \[([^\]]+)\]\[s\d+\] \| ([^|]+) \|', text, re.M)
    result = {key: (title, urls[key.lower()], claim.strip()) for key, title, claim in rows}
    result.update(EXTRA_SOURCES)
    return result


def navigation(pages, current):
    result = []
    for group in ['はじめに', 'テーマから調べる', '追加調査', '構成案をくわしく', '相談と資料のこと']:
        links = []
        for slug, page in pages.items():
            if page['group'] != group:
                continue
            active = ' aria-current="page"' if current == slug else ''
            links.append(f'<a href="{slug}.html"{active}>{icon(page["icon"])}<span>{page["nav"]}</span></a>')
        result.append(f'<div class="nav-group"><p>{group}</p>{"".join(links)}</div>')
    return ''.join(result)


def render(slug, page, pages, bibliography, revision):
    body = page['body']
    refs = sorted(set(re.findall(r'data-ref="(S\d+)"', body)))
    dated_keys = bibliography if slug == 'sources' else refs
    source_dates = ' / '.join(sorted({SOURCE_DATES.get(key, DATE) for key in dated_keys}))
    if refs:
        items = ''.join(f'<li id="ref-{key}"><a href="{escape(bibliography[key][1], quote=True)}">{key} · {escape(bibliography[key][0])} ↗</a><span>{escape(bibliography[key][2])} · 確認 {SOURCE_DATES.get(key, DATE)}（日本時間）</span></li>' for key in refs)
        body += f'<details class="sources"><summary>このページの一次情報・出典（{len(refs)}件）</summary><p>出典確認日：{source_dates}（日本時間）。各項目にも確認日を記載。公式の仕様と、今回の設計提案を分けて読もう。</p><ul>{items}</ul></details>'
    toc = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    toc_html = '<nav class="on-page" aria-label="このページの目次">' + ''.join(f'<a href="#{key}">{re.sub("<[^>]+>", "", title)}</a>' for key, title in toc) + '</nav>' if toc else ''
    related = ''.join(f'<a class="next-link" href="{key}.html">{icon(pages[key]["icon"])}<span>{pages[key]["nav"]}</span><span aria-hidden="true">↗</span></a>' for key in page.get('related', []))
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{escape(page['intro'], quote=True)}">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; script-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'; connect-src 'none'">
<title>{escape(re.sub('<[^>]+>', '', page['title']))} | doukin の検討ノート</title><link rel="icon" type="image/svg+xml" href="assets/guide.svg"><link rel="stylesheet" href="assets/guide.css"><script src="assets/guide.js" defer></script></head>
<body><a class="skip" href="#main">本文へすすむ</a>
<header class="mobile-head"><a href="index.html">doukin <span>の検討ノート</span></a><button id="menu-button" type="button" aria-controls="sidebar" aria-expanded="false">目次をひらく</button></header>
<aside class="sidebar" id="sidebar"><a class="brand" href="index.html">{icon('book')}<span>doukin<small>みんなで選ぶ、技術の手引き</small></span></a>
<p class="edition"><a href="history.html#{version_anchor(revision)}">資料 v{escape(revision['version'])}</a> / 調査・検討用</p><nav aria-label="資料全体の目次">{navigation(pages, slug)}</nav>
<div class="side-note">一度にぜんぶ読まなくて大丈夫。<br>気になるところからどうぞ。</div></aside>
<main id="main"><div class="topline"><a href="index.html">検討ノート</a><span>／ {escape(page['nav'])}</span><span class="status">調査・検討用</span></div>
<header class="hero"><div><p class="eyebrow">{page['kicker']}</p><h1>{page['title']}</h1><p class="intro">{page['intro']}</p><div class="meta"><span>{page['issue']}</span><a class="revision-link" href="history.html#{version_anchor(revision)}">資料 v{escape(revision['version'])} · 改訂 {escape(revision['date'])}</a>{f'<span>出典確認 {source_dates} · JST</span>' if refs else ''}</div></div>
<img class="mascot" src="assets/guide.svg" width="220" height="190" alt="" aria-hidden="true"></header>
<aside class="scope-note" aria-label="資料の位置づけ">公開用の調査・検討資料です。推奨や数値は比較のための提案で、アプリの確定事項・採用結果・実運用の記録は掲載しません。</aside>
{toc_html}{body}
<nav class="related" aria-label="関連するページ"><p class="eyebrow">つづきは、こちらから</p><div>{related}</div></nav>
<footer>doukin の検討ノート · 公開用の調査・検討資料<br><a href="history.html#{version_anchor(revision)}">資料 v{escape(revision['version'])} · 改訂履歴</a> <span>／</span> <a href="sources.html">出典・用語・レビュー記録</a> <span>／</span> <a href="index.html">表紙にもどる</a></footer></main></body></html>'''


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    bibliography = sources()
    pages = make_pages(bibliography)
    history = load_history()
    add_history_page(pages, history)
    for slug, page in pages.items():
        (OUTPUT / f'{slug}.html').write_text(render(slug, page, pages, bibliography, history['revisions'][0]), encoding='utf-8')
    print(f'Built {len(pages)} HTML pages.')


if __name__ == '__main__':
    main()
