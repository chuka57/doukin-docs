#!/usr/bin/env python3
"""Trusted Pages publisher. PR artifacts are static input, never executed."""
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import zipfile

from check_html import check

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = '.github/workflows/docs-build.yml'
STATE_BRANCH = 'gh-pages'
MARKER = '<!-- doukin-docs-preview -->'
MAX_BYTES = 10 * 1024 * 1024
ALLOWED = {'.html', '.css', '.js', '.svg', '.png', '.jpg', '.jpeg', '.webp', '.ico', '.json', '.txt', '.woff', '.woff2'}


def command(*args, cwd=None):
    return subprocess.check_output(args, cwd=ROOT if cwd is None else cwd)


def api(repo, path, method='GET', body=None):
    args = ['gh', 'api', f'repos/{repo}/{path}', '--method', method]
    if body is not None:
        args.extend(['--input', '-'])
    data = subprocess.check_output(args, input=json.dumps(body).encode() if body is not None else None)
    return json.loads(data) if data else None


def items(repo, path, key=None):
    separator = '&' if '?' in path else '?'
    page = 1
    while True:
        result = api(repo, f'{path}{separator}per_page=100&page={page}')
        rows = result[key] if key else result
        yield from rows
        if len(rows) < 100:
            return
        page += 1


def extract_site(data, destination):
    """Do not let a PR ZIP write outside its preview or introduce symlinks."""
    if len(data) > MAX_BYTES:
        raise ValueError('Preview archive is too large')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        if len(entries) > 2000 or sum(entry.file_size for entry in entries) > MAX_BYTES:
            raise ValueError('Preview expands beyond the size/file limit')
        seen = set()
        for entry in entries:
            name = PurePosixPath(entry.filename)
            kind = stat.S_IFMT(entry.external_attr >> 16)
            if (name.is_absolute() or not name.parts or '..' in name.parts or
                    '\\' in entry.filename or str(name) in seen or
                    kind not in (0, stat.S_IFREG, stat.S_IFDIR)):
                raise ValueError(f'Unsafe archive member: {entry.filename}')
            seen.add(str(name))
            if any(part.startswith('.') for part in name.parts) and name != PurePosixPath('.nojekyll'):
                raise ValueError(f'Hidden archive member: {entry.filename}')
            if entry.is_dir():
                continue
            if name.suffix.lower() not in ALLOWED and str(name) != '.nojekyll':
                raise ValueError(f'Not a static site file: {entry.filename}')
        destination.mkdir(parents=True)
        for entry in entries:
            if entry.is_dir():
                continue
            target = destination / entry.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(entry))
    check(destination)


def eligible(pr, repo):
    return (pr['state'] == 'open' and pr['base']['ref'] == 'main' and
            pr['head']['repo'] is not None and pr['head']['repo']['full_name'] == repo)


def preview_pr(run, prs, repo):
    if (run['event'] != 'pull_request' or run['path'] != WORKFLOW or
            run['conclusion'] != 'success' or run['head_repository']['full_name'] != repo):
        return None
    for pr in prs:
        associated = any(p['number'] == pr['number'] and p['head']['sha'] == pr['head']['sha']
                         for p in run.get('pull_requests', []))
        if (eligible(pr, repo) and run['head_branch'] == pr['head']['ref'] and
                (run['head_sha'] == pr['head']['sha'] or associated)):
            return pr
    return None  # Closed PRs, fork PRs and obsolete builds cannot replace a preview.


def state_checkout(destination):
    probe = subprocess.run(['git', 'ls-remote', '--exit-code', '--heads', 'origin', STATE_BRANCH],
                           cwd=ROOT, stdout=subprocess.PIPE, check=False)
    if probe.returncode not in (0, 2):
        raise RuntimeError('Cannot inspect the preview state branch')
    ref = 'HEAD'
    if probe.returncode == 0:
        command('git', 'fetch', 'origin', f'{STATE_BRANCH}:refs/remotes/origin/{STATE_BRANCH}')
        ref = f'origin/{STATE_BRANCH}'
    command('git', 'worktree', 'add', '--detach', str(destination), ref)
    if probe.returncode == 2:
        # The first snapshot starts from main but contains only the built site.
        clear(destination)
    return destination


def clear(directory, keep=()):
    for path in directory.iterdir():
        if path.name in {'.git', *keep}:
            continue
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()


def assemble(repo, event, work):
    state = state_checkout(work / 'docs-pages-state')
    manifest_path = state / '.preview-state.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    previous = set(manifest)
    prs = [pr for pr in items(repo, 'pulls?state=open&base=main') if eligible(pr, repo)]
    open_numbers = {str(pr['number']) for pr in prs}
    previews = state / 'pr-preview'
    previews.mkdir(exist_ok=True)
    for directory in previews.iterdir():
        if directory.name not in {f'pr-{number}' for number in open_numbers}:
            if directory.is_symlink() or not directory.is_dir():
                directory.unlink()
            else:
                shutil.rmtree(directory)
    manifest = {number: data for number, data in manifest.items() if number in open_numbers}
    # GitHub concurrency keeps only one pending run. Reconcile ALL open PRs
    # rather than only the event that survived the queue, so no PR is lost.
    for pr in prs:
        number, sha = pr['number'], pr['head']['sha']
        expected = f'docs-preview-{number}-{sha}'
        artifacts = items(repo, f'actions/artifacts?name={expected}', 'artifacts')
        artifact = None
        for candidate in sorted(artifacts, key=lambda entry: entry['id'], reverse=True):
            if candidate['name'] != expected or candidate['expired']:
                continue
            if manifest.get(str(number), {}).get('artifact_id') == candidate['id']:
                break  # The latest usable artifact has already been validated.
            run = api(repo, f'actions/runs/{candidate["workflow_run"]["id"]}')
            if preview_pr(run, [pr], repo):
                artifact = candidate
                break
        if artifact is None:
            continue  # Keep the last good preview while a new build is pending.
        if artifact['size_in_bytes'] > MAX_BYTES:
            raise ValueError('PR preview artifact is too large')
        data = command('gh', 'api', f'repos/{repo}/actions/artifacts/{artifact["id"]}/zip')
        temporary = work / f'incoming-preview-{number}'
        extract_site(data, temporary)
        destination = previews / f'pr-{number}'
        if destination.exists():
            shutil.rmtree(destination)
        shutil.move(temporary, destination)
        manifest[str(number)] = {'sha': sha, 'run_id': run['id'], 'artifact_id': artifact['id']}

    # Always rebuild production from trusted main, preserving every open PR.
    clear(state, keep=('pr-preview', '.preview-state.json'))
    if (ROOT / 'docs' / 'pr-preview').exists():
        raise ValueError('docs/pr-preview is reserved for the publisher')
    shutil.copytree(ROOT / 'docs', state, dirs_exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    site = work / 'docs-pages-site'
    shutil.copytree(state, site, ignore=shutil.ignore_patterns('.git', '.preview-state.json'))
    check(site)

    command('git', 'add', '--all', cwd=state)
    if subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=state).returncode:
        command('git', '-c', 'user.name=github-actions[bot]',
                '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
                'commit', '-m', 'Update production and PR preview snapshots', cwd=state)
        command('git', 'push', 'origin', f'HEAD:refs/heads/{STATE_BRANCH}', cwd=state)
    removed = previous - open_numbers
    if (event.get('action') == 'closed' and 'pull_request' in event and
            str(event['pull_request']['number']) not in open_numbers):
        removed.add(str(event['pull_request']['number']))
    (work / 'docs-pages-comments.json').write_text(json.dumps({'previews': manifest, 'removed': sorted(removed)}))


def comment(repo, work, pages_url):
    data = json.loads((work / 'docs-pages-comments.json').read_text())
    for number in sorted(set(data['previews']) | set(data['removed']), key=int):
        pr = api(repo, f'pulls/{int(number)}')
        # A PR can close/reopen while Pages deploys. The next queued publisher
        # will reconcile it; do not post a now-incorrect lifecycle comment.
        if number in data['removed']:
            if pr['state'] == 'open':
                continue
            body = f'{MARKER}\nこのPRのプレビューは削除しました。'
        else:
            if not eligible(pr, repo):
                continue
            sha = data['previews'][number]['sha']
            if not re.fullmatch(r'[0-9a-f]{40}', sha):
                raise ValueError('Invalid preview SHA')
            url = f'{pages_url.rstrip("/")}/pr-preview/pr-{int(number)}/'
            body = f'{MARKER}\n📖 [このPRのプレビューを開く]({url})\n\n対象PRコミット：`{sha}`（ビルド時のmainとのマージ結果）。'
            if sha != pr['head']['sha']:
                body += '\n\n最新の変更はまだ公開されていません。上記コミットのプレビューです。'
        comments = items(repo, f'issues/{int(number)}/comments')
        existing = next((c for c in comments if c['user']['login'] == 'github-actions[bot]' and MARKER in (c['body'] or '')), None)
        if existing:
            if existing['body'] != body:
                api(repo, f'issues/comments/{existing["id"]}', 'PATCH', {'body': body})
        elif pr['state'] == 'open':
            api(repo, f'issues/{int(number)}/comments', 'POST', {'body': body})


if __name__ == '__main__':
    repo = os.environ['GITHUB_REPOSITORY']
    work = Path(os.environ['RUNNER_TEMP'])
    if sys.argv[1] == 'assemble':
        assemble(repo, json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text()), work)
    elif sys.argv[1] == 'comment':
        comment(repo, work, os.environ['PAGES_URL'])
    else:
        raise SystemExit('Usage: publish_pages.py assemble|comment')
