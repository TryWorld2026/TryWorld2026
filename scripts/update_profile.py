"""Refresh public PR contributions through GitHub's paginated user connection."""

import argparse
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlencode


START = '<!-- CONTRIBUTIONS:START -->'
END = '<!-- CONTRIBUTIONS:END -->'
CHINA = timezone(timedelta(hours=8))
QUERY = '''query ProfileContributions($login: String!, $cursor: String) {
  user(login: $login) {
    pullRequests(first: 100, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        number title url state isDraft createdAt updatedAt mergedAt
        repository { nameWithOwner isPrivate owner { login } }
      }
    }
  }
}'''


def github_request(query, variables):
    result = subprocess.run(
        ['gh', 'api', 'graphql', '--input', '-'],
        input=json.dumps({'query': query, 'variables': variables}),
        capture_output=True, text=True, encoding='utf-8', timeout=45,
    )
    if result.returncode:
        raise RuntimeError('GitHub API request failed; previous records will be retained.')
    return json.loads(result.stdout)


def public_records(items):
    records = []
    for item in items:
        try:
            repo = item['repository']
            if type(repo['isPrivate']) is not bool:
                raise ValueError('Missing repository visibility')
            if repo['isPrivate']:
                continue
            name = repo['nameWithOwner']
            if not re.fullmatch(r'[A-Za-z0-9-]+/[A-Za-z0-9_.-]+', name):
                raise ValueError('Invalid repository name')
            if name.split('/')[0].casefold() != repo['owner']['login'].casefold():
                raise ValueError('Inconsistent repository owner')
            number = item['number']
            if type(number) is not int or number < 1 or item['url'] != f'https://github.com/{name}/pull/{number}':
                raise ValueError('Invalid PR link')
            if item['state'] not in ('OPEN', 'MERGED', 'CLOSED') or type(item['isDraft']) is not bool:
                raise ValueError('Invalid PR state')
            if not isinstance(item['title'], str) or not item['title'].strip():
                raise ValueError('Missing PR title')
            for key in ('createdAt', 'updatedAt'):
                if datetime.fromisoformat(item[key].replace('Z', '+00:00')).tzinfo is None:
                    raise ValueError('Missing timestamp timezone')
            if item['state'] == 'MERGED':
                if datetime.fromisoformat(item['mergedAt'].replace('Z', '+00:00')).tzinfo is None:
                    raise ValueError('Missing merge timestamp timezone')
        except (KeyError, TypeError, ValueError, AttributeError) as error:
            raise RuntimeError('GitHub returned an invalid PR record; refusing a partial refresh.') from error
        records.append(item)
    return sorted(records, key=lambda p: (p['updatedAt'], p['url']), reverse=True)


def fetch_contributions(login, request=None):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}', login):
        raise RuntimeError('Invalid GitHub login.')
    request = request or github_request
    cursor, expected = None, None
    seen_cursors, records = set(), {}
    while True:
        payload = request(QUERY, {'login': login, 'cursor': cursor})
        if payload.get('errors'):
            raise RuntimeError('GitHub returned API errors; refusing a partial refresh.')
        try:
            connection = payload['data']['user']['pullRequests']
            total, nodes, page = connection['totalCount'], connection['nodes'], connection['pageInfo']
            if type(total) is not int or total < 0 or not isinstance(nodes, list) or type(page['hasNextPage']) is not bool:
                raise ValueError('Invalid pagination data')
            if expected is not None and expected != total:
                raise ValueError('Contributions changed during pagination')
            expected = total
            for item in nodes:
                if not isinstance(item, dict) or item['url'] in records:
                    raise ValueError('Missing or repeated PR record')
                records[item['url']] = item
            if not page['hasNextPage']:
                if len(records) != expected:
                    raise ValueError('Incomplete PR list')
                return public_records(records.values())
            cursor = page['endCursor']
            if not isinstance(cursor, str) or not cursor or cursor in seen_cursors:
                raise ValueError('Pagination cursor did not advance')
            seen_cursors.add(cursor)
        except (KeyError, TypeError, ValueError) as error:
            raise RuntimeError('Incomplete GitHub response; previous records will be retained.') from error


def markdown(text):
    text = html.escape(' '.join(text.split()))
    return re.sub(r'([\\`*\[\]()|!_])', r'\\\1', text)


def split_records(login, items):
    external, own = [], []
    merged = [item for item in public_records(items) if item['state'] == 'MERGED']
    for item in sorted(merged, key=lambda p: (p['mergedAt'], p['url']), reverse=True):
        bucket = own if item['repository']['owner']['login'].casefold() == login.casefold() else external
        bucket.append(item)
    return external, own


def merged_search_link(login, language):
    label = 'GitHub 已合并 PR' if language == 'zh' else 'Merged PRs on GitHub'
    query = urlencode({'q': f'author:{login} is:pr is:public is:merged', 'type': 'pullrequests'})
    return f'[{label}](https://github.com/search?{query})'


def render_readme(login, pull_requests, language='zh'):
    external, _ = split_records(login, pull_requests)
    by_repo = defaultdict(list)
    for item in external:
        by_repo[item['repository']['nameWithOwner']].append(item)
    archive = f'https://github.com/{login}/{login}/blob/main/CONTRIBUTIONS.md'
    if language == 'zh':
        lines = [f'**{len(external)} 个已合并 PR · {len(by_repo)} 个外部项目**', '',
                 '我向外部开源项目贡献的成果，已被上游合并。', '',
                 '| 项目 | 已合并 PR |', '| --- | --- |']
    else:
        pr_word = 'PR' if len(external) == 1 else 'PRs'
        project_word = 'project' if len(by_repo) == 1 else 'projects'
        lines = [f'**{len(external)} merged {pr_word} · {len(by_repo)} external {project_word}**', '',
                 'My contributions accepted and merged into external open-source projects.', '',
                 '| Project | Merged PRs |', '| --- | --- |']
    for repo, items in sorted(by_repo.items(), key=lambda pair: (pair[1][0]['mergedAt'], pair[0]), reverse=True):
        lines.append(f'| [{markdown(repo)}](https://github.com/{repo}) | {len(items)} |')
    lines += ['', '**最近合并**' if language == 'zh' else '**Recently merged**', '']
    for item in external[:8]:
        repo = item['repository']['nameWithOwner']
        lines.append(f'- [{markdown(repo)} #{item["number"]}]({item["url"]}) — {markdown(item["title"])}')
    if not external:
        lines.append('已合并的公开 PR 会自动加入这里。' if language == 'zh' else 'Public PRs will appear here after they are merged.')
    lines += ['', f'[完整合并记录]({archive}) · {merged_search_link(login, language)}' if language == 'zh'
              else f'[Complete merged PR archive]({archive}) · {merged_search_link(login, language)}', '',
              '<sub>每天自动同步新合并的公开 PR。</sub>' if language == 'zh'
              else '<sub>Synced daily as public PRs are merged.</sub>']
    return '\n'.join(lines) + '\n'


def render_archive(login, pull_requests, verified_month):
    datetime.strptime(verified_month, '%Y-%m')
    external, own = split_records(login, pull_requests)
    lines = ['# 已合并 PR 贡献记录 · Merged pull requests', '',
             f'作者：[{login}](https://github.com/{login}) · {len(external) + len(own)} 个已合并 PR · {len(external)} 个外部项目 PR · {len(own)} 个自身项目 PR', '',
             f'自动核对月份：**{verified_month}**（北京时间）。有变动时更新记录，至少每月刷新一次核对月份。', '',
             '本列表收录已被合并的公开 PR。', '', merged_search_link(login, 'zh'), '',
             f'[主页](https://github.com/{login}) · [English](https://github.com/{login}/{login}/blob/main/README.md)', '']
    for title, items in [('外部项目 · External projects', external), ('自身项目 · Own projects', own)]:
        lines += [f'## {title}', '', '| 合并日期（北京时间） | 项目 / PR | 标题 / Title |', '| --- | --- | --- |']
        for item in items:
            date = datetime.fromisoformat(item['mergedAt'].replace('Z', '+00:00')).astimezone(CHINA).date().isoformat()
            repo = item['repository']['nameWithOwner']
            lines.append(f'| {date} | [{markdown(repo)} #{item["number"]}]({item["url"]}) | {markdown(item["title"])} |')
        if not items:
            lines.append('| — | — | — |')
        lines.append('')
    return '\n'.join(lines)


def build_files(root, login, pull_requests, verified_month):
    files = {}
    for name, language in [('README.md', 'en'), ('README.zh-CN.md', 'zh')]:
        path = root / name
        text = path.read_bytes().decode('utf-8')
        if text.count(START) != 1 or text.count(END) != 1 or text.index(START) >= text.index(END):
            raise RuntimeError(f'{name} needs exactly one contribution block; refusing to overwrite it.')
        newline = '\r\n' if '\r\n' in text else '\n'
        block = render_readme(login, pull_requests, language).replace('\n', newline)
        files[path] = text[:text.index(START) + len(START)] + newline + block + text[text.index(END):]
    files[root / 'CONTRIBUTIONS.md'] = render_archive(login, pull_requests, verified_month)
    return files


def stage_file(path, content):
    descriptor, name = tempfile.mkstemp(prefix='.profile-sync-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        Path(name).unlink(missing_ok=True)
        raise
    return Path(name)


def apply_files(files):
    originals = {path: path.read_bytes() if path.exists() else None for path in files}
    changed = {path: text.encode('utf-8') for path, text in files.items() if originals[path] != text.encode('utf-8')}
    staged, replaced, temporary = {}, [], []
    try:
        for path, content in changed.items():
            staged[path] = stage_file(path, content)
            temporary.append(staged[path])
        for path, source in staged.items():
            os.replace(source, path)
            replaced.append(path)
    except BaseException:
        for path in reversed(replaced):
            if originals[path] is None:
                path.unlink(missing_ok=True)
            else:
                restored = stage_file(path, originals[path])
                temporary.append(restored)
                os.replace(restored, path)
        raise
    finally:
        for path in temporary:
            path.unlink(missing_ok=True)
    return list(changed)


def sync_profile(root, login, verified_month, request=None):
    records = fetch_contributions(login, request)
    return apply_files(build_files(root, login, records, verified_month))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user', required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    arguments = parser.parse_args()
    month = datetime.now(CHINA).strftime('%Y-%m')
    try:
        changed = sync_profile(arguments.root.resolve(), arguments.user, month)
    except (RuntimeError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f'Refresh failed: {error}', file=sys.stderr)
        return 1
    print(f'Contribution refresh complete: {len(changed)} file(s) changed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
