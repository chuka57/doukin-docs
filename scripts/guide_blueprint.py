"""Integrated recommendation, kept separate from adopted application requirements."""
from pathlib import Path


def add_blueprint_page(pages):
    body = (Path(__file__).resolve().parent.parent / 'content' / 'overall-spec.html').read_text(encoding='utf-8')
    pages['overall-spec'] = dict(
        nav='推奨を統合した全体設計案', title='推奨をすべて選ぶと、<br>どんなアプリになる？',
        intro='N1の構成・画面・認証・権限・データ・復旧を、具体的なサービス名と図表でつなぐ設計案。Workersの制約も追加調査します。',
        body=body, icon='map', group='はじめに', issue='全体設計案 / 追加調査',
        kicker='DOUKIN / RECOMMENDED BLUEPRINT', related=('plan-n1', 'sessions', 'platform', 'workflow'))
