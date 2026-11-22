"""Register the personal proposal for record and profile visibility."""
from pathlib import Path


def add_privacy_proposal_page(pages):
    source = (Path(__file__).resolve().parent.parent / 'content' / 'proposal-privacy.html').read_text(encoding='utf-8')
    overview, figure_end, body = source.partition('</figure>')
    pages['proposal-privacy'] = dict(
        nav='記録・プロフィールの公開範囲の提案',
        title='記録とプロフィールの公開範囲の提案',
        intro='記録は登録のたびに共有範囲を選び、体重は別に設定する案です。',
        lead=overview + figure_end, body_class='privacy-proposal', compact_toc=True,
        body=body, icon='shield', group='はじめに', issue='チームへの提案',
        kicker='個人提案', related=('privacy', 'proposal-mvp', 'proposal-auth', 'data'))
