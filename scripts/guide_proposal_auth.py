"""One personal proposal, kept separate from the research recommendations."""
from pathlib import Path


def add_auth_proposal_page(pages):
    body = (Path(__file__).resolve().parent.parent / 'content' / 'proposal-auth.html').read_text(encoding='utf-8')
    pages['proposal-auth'] = dict(
        nav='参加・認証の提案', title='参加から復旧まで、<br>情報を少なく、使いやすく。',
        intro='私からチームへ提案する参加・ログイン・招待・復旧の要件案です。チームの採用決定ではなく、認証方式は検証候補、技術スタック全体は未選定です。',
        body=body, icon='key', group='相談と資料のこと', issue='個人の提案 / 参加・認証',
        kicker='PERSONAL PROPOSAL / AUTH', related=('minimization', 'sessions', 'auth'))
