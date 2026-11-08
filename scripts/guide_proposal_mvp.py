"""MVP proposal; no internal decision records or physical schema."""
from pathlib import Path


def add_proposal_mvp_page(pages):
    body = (Path(__file__).resolve().parent.parent / 'content' / 'proposal-mvp.html').read_text(encoding='utf-8')
    pages['proposal-mvp'] = dict(
        nav='MVP機能の提案', title='一緒に続けるための<br>MVP機能の提案',
        intro='「やった」だけでも残せる記録、履歴・テンプレートの再利用、同期への応援、体重の記録を提案します。',
        body=body, icon='steps', group='はじめに', issue='MVP機能・操作・入力項目 / 提案',
        kicker='PROPOSAL / MVP', related=('data', 'privacy', 'workflow'))
