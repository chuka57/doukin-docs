"""Exercise preview isolation, stale events, lifecycle and the published tree."""
import io
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import publish_pages as publisher
from check_html import check

REPO = 'example/docs'
SHA = 'a' * 40


def pr(number=2, sha=SHA, repo=REPO, state='open'):
    return dict(number=number, state=state, base={'ref': 'main'},
                head={'ref': f'change-{number}', 'sha': sha,
                      'repo': {'full_name': repo} if repo else None})


def run(number=2, sha=SHA):
    return dict(id=42, event='pull_request', path=publisher.WORKFLOW,
                conclusion='success', head_repository={'full_name': REPO},
                head_branch=f'change-{number}', head_sha=sha, pull_requests=[])


def archive(files=None):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zipped:
        for name, content in (files or {'index.html': '<h1>Preview</h1>'}).items():
            zipped.writestr(name, content)
    return buffer.getvalue()


class PreviewTests(unittest.TestCase):
    def test_old_closed_fork_and_unrelated_workflow_runs_are_rejected(self):
        for change in [{'head_sha': 'b' * 40}, {'path': '.github/workflows/other.yml'},
                       {'conclusion': 'failure'}, {'head_repository': {'full_name': 'other/docs'}},
                       {'head_branch': 'unrelated'}, {'event': 'push'}]:
            with self.subTest(change=change):
                self.assertIsNone(publisher.preview_pr(run() | change, [pr()], REPO))
        for change in [{'state': 'closed'}, {'head': pr(repo='other/docs')['head']},
                       {'head': pr(repo=None)['head']}, {'base': {'ref': 'other'}}]:
            self.assertIsNone(publisher.preview_pr(run(), [pr() | change], REPO))
        self.assertEqual(publisher.preview_pr(run(), [pr()], REPO), pr())

    def test_associated_head_is_used_when_workflow_sha_is_a_merge_commit(self):
        merge = run(sha='b' * 40)
        merge['pull_requests'] = [{'number': 2, 'head': {'sha': SHA}}]
        self.assertEqual(publisher.preview_pr(merge, [pr()], REPO), pr())

    def test_archive_cannot_escape_preview_or_overwrite_publisher(self):
        bad = ['../index.html', '/index.html', 'assets/../../index.html',
               '.github/workflows/deploy.yml', '.git/config', 'x\\index.html', 'run.py']
        with tempfile.TemporaryDirectory() as tmp:
            for name in bad:
                with self.subTest(name=name), self.assertRaises(ValueError):
                    publisher.extract_site(archive({name: 'bad'}), Path(tmp) / 'preview')
                self.assertFalse((Path(tmp) / 'preview').exists())

    def test_symlinks_and_duplicate_archive_paths_are_rejected(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zipped:
            entry = zipfile.ZipInfo('index.html')
            entry.create_system = 3
            entry.external_attr = (stat.S_IFLNK | 0o777) << 16
            zipped.writestr(entry, '../outside')
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
            publisher.extract_site(buffer.getvalue(), Path(tmp) / 'preview')
        duplicate = io.BytesIO()
        with zipfile.ZipFile(duplicate, 'w') as zipped, warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            zipped.writestr('index.html', 'first')
            zipped.writestr('index.html', 'second')
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
            publisher.extract_site(duplicate.getvalue(), Path(tmp) / 'preview')

    def test_missing_index_oversize_and_bad_links_are_rejected(self):
        cases = [archive({'other.html': '<h1>No index</h1>'}),
                 archive({'index.html': '<a href="../../index.html">escape</a>'}),
                 archive({'index.html': '<script src="/assets/main.js"></script>'}),
                 b'0' * (publisher.MAX_BYTES + 1)]
        for data in cases:
            with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
                publisher.extract_site(data, Path(tmp) / 'preview')

    def test_valid_site_keeps_relative_assets_inside_preview(self):
        data = archive({'index.html': '<link href="assets/style.css"><a href="other.html#ok">go</a>',
                        'other.html': '<h2 id="ok">OK</h2>', 'assets/style.css': 'body{}', '.nojekyll': ''})
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / 'preview'
            publisher.extract_site(data, destination)
            self.assertEqual(check(destination), (2, 2))


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        (self.source / 'docs').mkdir()
        (self.source / 'docs' / 'index.html').write_text('<h1>Production main</h1>')
        self.state = self.root / 'state'
        self.state.mkdir()
        for number in (2, 3, 4):
            preview = self.state / 'pr-preview' / f'pr-{number}'
            preview.mkdir(parents=True)
            (preview / 'index.html').write_text(f'<h1>Old preview {number}</h1>')
        (self.state / '.preview-state.json').write_text(json.dumps({
            str(number): {'sha': 'b' * 40, 'run_id': number} for number in (2, 3, 4)}))
        self.work = self.root / 'work'
        self.work.mkdir()

    def assemble(self, event, artifact=True, candidate_run=None):
        def listing(repo, path, key=None):
            if path.startswith('pulls?'):
                return iter([pr(2), pr(3)])
            if path.startswith('actions/artifacts?'):
                return iter([{'id': 9, 'name': f'docs-preview-2-{SHA}', 'expired': False,
                              'workflow_run': {'id': 42}, 'size_in_bytes': 100}]
                            if artifact and f'docs-preview-2-{SHA}' in path else [])
            raise AssertionError(path)
        commands = []
        def command(*args, **kwargs):
            commands.append(args)
            if args[:2] == ('gh', 'api'):
                return archive()
            return b''
        with patch.object(publisher, 'ROOT', self.source), \
                patch.object(publisher, 'state_checkout', return_value=self.state), \
                patch.object(publisher, 'items', side_effect=listing), \
                patch.object(publisher, 'api', return_value=candidate_run or run()), \
                patch.object(publisher, 'command', side_effect=command), \
                patch.object(publisher.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1)):
            publisher.assemble(REPO, event, self.work)
        return commands

    def test_preview_update_preserves_production_and_other_pr_and_removes_closed(self):
        commands = self.assemble({'workflow_run': run()})
        site = self.work / 'docs-pages-site'
        self.assertIn('Production main', (site / 'index.html').read_text())
        self.assertIn('Preview', (site / 'pr-preview/pr-2/index.html').read_text())
        self.assertIn('Old preview 3', (site / 'pr-preview/pr-3/index.html').read_text())
        self.assertFalse((site / 'pr-preview/pr-4').exists())
        self.assertFalse((site / '.preview-state.json').exists())
        self.assertTrue(any(args[:2] == ('git', 'push') for args in commands))
        data = json.loads((self.work / 'docs-pages-comments.json').read_text())
        self.assertEqual(data['previews']['2']['sha'], SHA)
        self.assertEqual(data['removed'], ['4'])

    def test_stale_artifact_retains_last_successful_preview(self):
        commands = self.assemble({}, candidate_run=run(sha='c' * 40))
        self.assertFalse(any(args[:2] == ('gh', 'api') for args in commands))
        self.assertIn('Old preview 2', (self.work / 'docs-pages-site/pr-preview/pr-2/index.html').read_text())

    def test_missing_artifact_keeps_last_published_preview(self):
        self.assemble({}, artifact=False)
        self.assertIn('Old preview 2', (self.work / 'docs-pages-site/pr-preview/pr-2/index.html').read_text())

    def test_lost_or_old_trigger_still_reconciles_other_successful_builds(self):
        self.assemble({'workflow_run': run(number=99, sha='c' * 40)})
        self.assertIn('<h1>Preview</h1>', (self.work / 'docs-pages-site/pr-preview/pr-2/index.html').read_text())

    def test_close_event_also_retires_comment_after_retry(self):
        self.assemble({'action': 'closed', 'pull_request': {'number': 9}})
        data = json.loads((self.work / 'docs-pages-comments.json').read_text())
        self.assertEqual(data['removed'], ['4', '9'])

    def test_old_close_event_cannot_retire_a_reopened_pr(self):
        self.assemble({'action': 'closed', 'pull_request': {'number': 2}})
        data = json.loads((self.work / 'docs-pages-comments.json').read_text())
        self.assertNotIn('2', data['removed'])
        self.assertTrue((self.work / 'docs-pages-site/pr-preview/pr-2/index.html').exists())

    def test_comment_updates_one_bot_comment_and_marks_stale_sha(self):
        (self.work / 'docs-pages-comments.json').write_text(json.dumps({
            'previews': {'2': {'sha': 'b' * 40, 'run_id': 2}}, 'removed': ['4']}))
        calls = []
        def api(repo, path, method='GET', body=None):
            calls.append((path, method, body))
            if path.startswith('pulls/'):
                return pr(int(path.split('/')[-1]), state='closed' if path.endswith('/4') else 'open')
        comments = [{'id': 5, 'user': {'login': 'github-actions[bot]'},
                     'body': publisher.MARKER + '\nold'}]
        with patch.object(publisher, 'api', side_effect=api), \
                patch.object(publisher, 'items', return_value=comments):
            publisher.comment(REPO, self.work, 'https://example.github.io/docs/')
        writes = [body['body'] for _, method, body in calls if method == 'PATCH']
        self.assertEqual(len(writes), 2)
        self.assertIn('/pr-preview/pr-2/', writes[0])
        self.assertIn('最新の変更はまだ公開されていません', writes[0])
        self.assertIn('削除しました', writes[1])


class GitSnapshotTests(unittest.TestCase):
    def test_first_publish_update_and_cleanup_with_real_git(self):
        # A local bare origin exercises the actual worktree, commit and push
        # operations, without touching GitHub or the developer's repository.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            origin, source = root / 'origin.git', root / 'source'
            subprocess.run(['git', 'init', '--bare', '--quiet', '--initial-branch=main', str(origin)], check=True)
            subprocess.run(['git', 'init', '--quiet', '--initial-branch=main', str(source)], check=True)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=source, stderr=subprocess.PIPE)
            git('remote', 'add', 'origin', str(origin))
            (source / 'docs').mkdir()
            (source / 'docs/index.html').write_text('<h1>Production</h1>')
            git('add', '.')
            git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'main')
            git('push', 'origin', 'main')
            main_before = git('rev-parse', 'main')
            actual_command = publisher.command
            def command(*args, **kwargs):
                return archive() if args[:2] == ('gh', 'api') else actual_command(*args, **kwargs)
            def listing(repo, path, key=None):
                if path.startswith('pulls?'):
                    return iter([pr()])
                return iter([{'id': 9, 'name': f'docs-preview-2-{SHA}', 'expired': False,
                              'workflow_run': {'id': 42}, 'size_in_bytes': 100}])
            with patch.object(publisher, 'ROOT', source), \
                    patch.object(publisher, 'items', side_effect=listing), \
                    patch.object(publisher, 'api', return_value=run()), \
                    patch.object(publisher, 'command', side_effect=command):
                first = root / 'first'
                first.mkdir()
                publisher.assemble(REPO, {'workflow_run': run()}, first)
                self.assertTrue((first / 'docs-pages-site/pr-preview/pr-2/index.html').is_file())
                (source / 'docs/index.html').write_text('<h1>New production</h1>')
                second = root / 'second'
                second.mkdir()
                publisher.assemble(REPO, {}, second)
                self.assertIn('New production', (second / 'docs-pages-site/index.html').read_text())
                self.assertTrue((second / 'docs-pages-site/pr-preview/pr-2/index.html').is_file())
                third = root / 'third'
                third.mkdir()
                with patch.object(publisher, 'items', return_value=iter([])):
                    publisher.assemble(REPO, {'action': 'closed', 'pull_request': {'number': 2}}, third)
                self.assertFalse((third / 'docs-pages-site/pr-preview/pr-2').exists())
            self.assertEqual(git('rev-parse', 'main'), main_before)
            self.assertEqual(git('diff', '--cached', '--name-only'), b'')
            published = subprocess.check_output(['git', '--git-dir', str(origin), 'ls-tree', '-r', '--name-only', 'gh-pages'], text=True)
            self.assertEqual(set(published.splitlines()), {'index.html', '.preview-state.json'})

    def test_checker_rejects_missing_anchors_and_duplicate_ids(self):
        for text in ['<h2 id="same">1</h2><h2 id="same">2</h2>', '<a href="#missing">broken</a>']:
            with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
                root = Path(tmp)
                (root / 'index.html').write_text(text)
                check(root)


if __name__ == '__main__':
    unittest.main()
