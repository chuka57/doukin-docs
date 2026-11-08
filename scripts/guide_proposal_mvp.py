"""MVP proposal; no internal decision records or physical schema."""
from pathlib import Path
import re
from html import escape


def add_proposal_mvp_page(pages):
    body = (Path(__file__).resolve().parent.parent / 'content' / 'proposal-mvp.html').read_text(encoding='utf-8')
    lead = re.search(r'<aside class="mvp-summary".*?</aside>', body, re.S).group()
    body = body.replace(lead, '', 1)
    # Keep the same table content and headers when rows stack on small screens.
    def label_cells(match):
        table = match.group()
        headers = re.findall(r'<th scope="col">(.*?)</th>', table)
        def label_row(row):
            cells = iter(headers[1:])
            def label_cell(cell):
                label = escape(next(cells), quote=True)
                return f'<td data-label="{label}"><span class="mvp-cell-label" aria-hidden="true">{label}</span>{cell.group(1)}</td>'
            return re.sub(r'<td>(.*?)</td>', label_cell, row.group(), flags=re.S)
        table = re.sub(r'<tr><th scope="row">.*?</tr>', label_row, table, flags=re.S)
        # Explicit roles preserve table semantics when CSS changes its layout.
        for tag, role in [('table', 'table'), ('thead', 'rowgroup'), ('tbody', 'rowgroup'), ('tr', 'row')]:
            table = table.replace(f'<{tag}>', f'<{tag} role="{role}">')
        return table.replace('<th scope="col">', '<th scope="col" role="columnheader">').replace('<th scope="row">', '<th scope="row" role="rowheader">').replace('<td data-label=', '<td role="cell" data-label=')
    body = re.sub(r'<table>.*?</table>', label_cells, body, flags=re.S)
    pages['proposal-mvp'] = dict(
        nav='MVP機能の提案', title='一緒に続けるための<br>MVP機能の提案',
        intro='「やった」だけでも残せる記録から、同期と一緒に続ける体験を提案します。',
        lead=lead, body_class='mvp-page', compact_toc=True,
        body=body, icon='steps', group='はじめに', issue='MVP機能・操作・入力項目 / 提案',
        kicker='PROPOSAL / MVP', related=('data', 'privacy', 'workflow'))
