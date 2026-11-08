"""Local revisions must not invent a PR, or hide a missing historic reference."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from guide_history import load_history, pr_links


class PendingRevisionTests(unittest.TestCase):
    def test_only_newest_explicit_pending_revision_can_omit_pr(self):
        revision = dict(version='0.2', date='2026-11-08', title='Draft',
                        summary=['New proposal'], pull_requests=[], pending_pr=True)
        historic = dict(version='0.1', date='2026-11-01', title='Published',
                        summary=['Initial'], pull_requests=[1])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'revisions.json'
            valid = {'revisions': [revision, historic]}
            path.write_text(json.dumps(valid))
            self.assertEqual(load_history(path), valid)
            for mutation in ('missing_marker', 'historic_pending', 'invented_pr'):
                invalid = copy.deepcopy(valid)
                if mutation == 'missing_marker':
                    del invalid['revisions'][0]['pending_pr']
                elif mutation == 'historic_pending':
                    invalid['revisions'][1].update(pending_pr=True, pull_requests=[])
                else:
                    invalid['revisions'][0]['pull_requests'] = [2]
                path.write_text(json.dumps(invalid))
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    load_history(path)
        self.assertNotIn('href=', pr_links([]))
        self.assertIn('/pull/1', pr_links([1]))
