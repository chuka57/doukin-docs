"""Document revisions; unrelated to application releases or adoption decisions."""
from datetime import date
from html import escape
import json
from pathlib import Path
import re

from guide_ui import bullets, definition, details, note, section

REVISIONS = Path(__file__).resolve().parent.parent / 'content' / 'revisions.json'
PR_BASE = 'https://github.com/chuka57/doukin-docs/pull/'


def load_history(path=REVISIONS):
    history = json.loads(path.read_text(encoding='utf-8'))
    revisions = history['revisions']
    if not revisions:
        raise ValueError('At least one document revision is required')
    versions = set()
    previous_date = date.max
    for revision in revisions:
        version = revision['version']
        if not re.fullmatch(r'\d+\.\d+', version) or version in versions:
            raise ValueError('Document versions must be unique numbers such as 0.2')
        versions.add(version)
        revised = date.fromisoformat(revision['date'])
        if revised > previous_date:
            raise ValueError('Document revisions must be newest first')
        previous_date = revised
        if not revision['title'] or not revision['summary'] or not revision['pull_requests']:
            raise ValueError('Each revision needs a title, summary and PR link')
    for entry in [*revisions, *history.get('publishing_changes', [])]:
        date.fromisoformat(entry['date'])
        if any(type(number) is not int or number < 1 for number in entry['pull_requests']):
            raise ValueError('PR numbers must be positive integers')
    return history


def version_anchor(revision):
    return 'version-' + revision['version'].replace('.', '-')


def pr_links(numbers):
    return ' ／ '.join(f'<a href="{PR_BASE}{number}">PR #{number} ↗</a>' for number in numbers)


def add_history_page(pages, history):
    current = history['revisions'][0]
    body = note('変更の要約から、詳細のPRへ。',
                '新しい版から順に、資料の変更点を短くまとめています。詳しい差分・議論・レビューは、各版のPRから確認できます。')
    for revision in history['revisions']:
        body += section(version_anchor(revision),
                        f'v{escape(revision["version"])} · {escape(revision["title"])}',
                        f'<p class="subtle">改訂 {escape(revision["date"])}（日本時間）</p>'
                        + bullets(*(escape(item) for item in revision['summary']))
                        + '<p>' + pr_links(revision['pull_requests']) + '</p>')
    if history.get('publishing_changes'):
        body += section('publishing', '掲載方法の変更', ''.join(
            f'<p><strong>{escape(entry["date"])}</strong> · {escape(entry["summary"])} '
            + pr_links(entry['pull_requests']) + '</p>' for entry in history['publishing_changes']))
    body += details('版・改訂日・出典確認日の違い', definition([
        ('現在の表示版', f'資料 v{escape(current["version"])} · 改訂 {escape(current["date"])}（日本時間）'),
        ('版番号', '資料全体の改訂番号です。アプリのリリース番号や、提案の採用状況を表しません。'),
        ('改訂日と出典確認日', '改訂日は資料の編集日。出典確認日はサービスの仕様等を確認した日で、別々に表示します。')]))
    pages['history'] = dict(nav='改訂履歴', title='調査資料の変更を、<br>短くたどろう。',
                            intro='資料の版・改訂日・変更点の要約と、詳細を確認できるPRへのリンクです。',
                            body=body, icon='book', group='相談と資料のこと', issue='資料の編集履歴',
                            kicker='DOCUMENT / HISTORY', related=('index', 'sources', 'sharing'))
