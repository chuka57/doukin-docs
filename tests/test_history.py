"""Local document drafts may precede a PR without inventing a PR number."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from guide_history import load_history, pr_links


class HistoryTests(unittest.TestCase):
    def test_unposted_revision_and_invalid_pr_references(self):
        revision = dict(version='0.5', date='2026-11-08', title='Draft',
                        summary=['New proposal'], pull_requests=[])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'revisions.json'
            path.write_text(json.dumps({'revisions': [revision]}), encoding='utf-8')
            self.assertEqual(load_history(path)['revisions'][0]['pull_requests'], [])
            self.assertIn('未作成', pr_links([]))
            self.assertIn('/pull/5', pr_links([5]))
            for invalid in ([0], [True], ['5'], None):
                with self.subTest(invalid=invalid):
                    revision['pull_requests'] = invalid
                    path.write_text(json.dumps({'revisions': [revision]}), encoding='utf-8')
                    with self.assertRaises(ValueError):
                        load_history(path)
