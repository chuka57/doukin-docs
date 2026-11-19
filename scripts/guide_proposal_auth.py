"""Register the participation and authentication specification example."""
from pathlib import Path


def add_auth_proposal_page(pages):
    body = (Path(__file__).resolve().parent.parent / 'content' / 'proposal-auth.html').read_text(encoding='utf-8')
    pages['proposal-auth'] = dict(
        nav='参加・認証の仕様例', title='参加・認証の仕様例',
        intro='招待制アプリでの参加承認、日常のログイン、復旧と利用停止を、画面例とともに示します。',
        body=body, icon='key', group='相談と資料のこと', issue='参加・認証',
        kicker='仕様例', related=('minimization', 'sessions', 'auth'))
