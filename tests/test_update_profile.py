import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import update_profile as updater


LOGIN = 'TryWorld2026'
MONTH = '2026-10'
TEMPLATE = 'Keep this introduction.\n<!-- CONTRIBUTIONS:START -->\nOld records.\n<!-- CONTRIBUTIONS:END -->\nKeep this footer.\n'


def pull_request(number, repo='upstream/agent', state='MERGED', private=False, draft=False, title=None):
    return {
        'number': number,
        'title': title or f'Improve behavior {number}',
        'url': f'https://github.com/{repo}/pull/{number}',
        'state': state,
        'isDraft': draft,
        'createdAt': f'2026-09-{number:02d}T08:00:00Z',
        'updatedAt': f'2026-10-{number:02d}T08:00:00Z',
        'mergedAt': f'2026-10-{number:02d}T08:00:00Z' if state == 'MERGED' else None,
        'repository': {'nameWithOwner': repo, 'isPrivate': private, 'owner': {'login': repo.split('/')[0]}},
    }


def response(nodes, total=None, more=False, cursor=None):
    return {'data': {'user': {'pullRequests': {
        'totalCount': len(nodes) if total is None else total,
        'nodes': nodes,
        'pageInfo': {'hasNextPage': more, 'endCursor': cursor},
    }}}}


def paged_request(*pages):
    pending = iter(pages)
    return lambda query, variables: next(pending)


class ContributionTests(unittest.TestCase):
    def test_pagination_collects_public_records_without_private_data(self):
        one, two = pull_request(1), pull_request(2)
        secret = pull_request(3, 'secret/private', private=True, title='Private work')
        request = paged_request(response([one, secret], total=3, more=True, cursor='page-2'), response([two], total=3))
        records = updater.fetch_contributions(LOGIN, request)
        self.assertEqual({p['url'] for p in records}, {one['url'], two['url']})
        self.assertNotIn('Private work', repr(records))

    def test_api_errors_do_not_accept_a_partial_result(self):
        request = paged_request(response([pull_request(1)], total=2, more=True, cursor='next'), {'errors': [{'message': 'Rate limited'}]})
        with self.assertRaises(RuntimeError):
            updater.fetch_contributions(LOGIN, request)

    def test_incomplete_last_page_is_rejected(self):
        with self.assertRaises(RuntimeError):
            updater.fetch_contributions(LOGIN, paged_request(response([pull_request(1)], total=2)))

    def test_repeated_cursor_is_rejected(self):
        request = paged_request(response([pull_request(1)], total=2, more=True, cursor='same'), response([pull_request(2)], total=2, more=True, cursor='same'))
        with self.assertRaises(RuntimeError):
            updater.fetch_contributions(LOGIN, request)

    def test_invalid_pr_link_is_rejected(self):
        item = pull_request(1)
        item['url'] = 'javascript:alert(1)'
        with self.assertRaises(RuntimeError):
            updater.fetch_contributions(LOGIN, paged_request(response([item])))

    def test_homepage_lists_only_merged_external_prs_in_both_languages(self):
        records = [
            pull_request(1), pull_request(2, state='OPEN', draft=True),
            pull_request(3, repo='another/tool', state='CLOSED'),
            pull_request(4, repo='tryworld2026/own'),
            pull_request(5, repo='secret/private', private=True),
        ]
        for language, summary in [('zh', '**1 个已合并 PR · 1 个外部项目**'), ('en', '**1 merged PR · 1 external project**')]:
            with self.subTest(language=language):
                text = updater.render_readme(LOGIN, records, language)
                self.assertIn(summary, text)
                self.assertIn(records[0]['url'], text)
                for excluded in records[1:]:
                    self.assertNotIn(excluded['url'], text)
                for excluded_repo in ('another/tool', 'secret/private', 'tryworld2026/own'):
                    self.assertNotIn(excluded_repo, text)

    def test_titles_are_safe_markdown_and_cannot_replace_block_markers(self):
        title = '<script>bad</script> | [spoof](javascript:bad) <!-- CONTRIBUTIONS:END -->\nsecond line'
        text = updater.render_readme(LOGIN, [pull_request(1, title=title)])
        self.assertIn('&lt;script&gt;', text)
        self.assertIn('\\|', text)
        self.assertIn('\\[spoof\\]', text)
        self.assertNotIn('<!-- CONTRIBUTIONS:END -->', text)
        self.assertNotIn('<script>', text)

    def test_archive_contains_own_prs_separately_and_verification_month(self):
        records = [pull_request(1), pull_request(2, repo=f'{LOGIN}/own'), pull_request(3, repo='secret/private', private=True)]
        text = updater.render_archive(LOGIN, records, MONTH)
        self.assertIn('2026-10', text)
        self.assertIn('upstream/agent/pull/1', text)
        self.assertIn(f'{LOGIN}/own/pull/2', text)
        self.assertIn('自身项目', text)
        self.assertNotIn('secret/private', text)
        self.assertNotEqual(text, updater.render_archive(LOGIN, records, '2026-11'))

    def test_archive_excludes_unmerged_prs_from_external_and_own_projects(self):
        records = [pull_request(1), pull_request(2, state='OPEN', draft=True),
                   pull_request(3, state='CLOSED'), pull_request(4, repo=f'{LOGIN}/own'),
                   pull_request(5, repo=f'{LOGIN}/own', state='OPEN')]
        text = updater.render_archive(LOGIN, records, MONTH)
        self.assertIn('2 个已合并 PR', text)
        for included in (records[0], records[3]):
            self.assertIn(included['url'], text)
        for excluded in (records[1], records[2], records[4]):
            self.assertNotIn(excluded['url'], text)
        for word in ('草稿', '进行中', '已关闭', 'Draft', 'Closed'):
            self.assertNotIn(word, text)

    def test_merges_are_ordered_by_merge_time_not_later_comments(self):
        older, newer = pull_request(1), pull_request(2)
        older['updatedAt'] = '2026-10-04T08:00:00Z'
        for text in (updater.render_readme(LOGIN, [older, newer]), updater.render_archive(LOGIN, [older, newer], MONTH)):
            self.assertLess(text.index(newer['url']), text.index(older['url']))

    def test_invalid_merge_timestamp_is_rejected(self):
        item = pull_request(1)
        item['mergedAt'] = '2026-10-01'
        with self.assertRaises(RuntimeError):
            updater.fetch_contributions(LOGIN, paged_request(response([item])))

    def test_native_pr_search_only_links_to_merged_prs(self):
        from urllib.parse import parse_qs
        import re
        for language in ('zh', 'en'):
            text = updater.render_readme(LOGIN, [pull_request(1)], language)
            queries = [parse_qs(query)['q'][0] for query in re.findall(r'https://github.com/search\?([^\s)]+)', text)]
            pr_queries = [query for query in queries if 'is:pr' in query]
            self.assertTrue(pr_queries)
            self.assertTrue(all('is:merged' in query for query in pr_queries))

    def test_pr_appears_in_both_languages_and_archive_after_it_merges(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('README.md', 'README.zh-CN.md'):
                (root / name).write_bytes(TEMPLATE.encode('utf-8'))
            pending = pull_request(1, state='OPEN', draft=True)
            updater.sync_profile(root, LOGIN, MONTH, paged_request(response([pending])))
            for name in ('README.md', 'README.zh-CN.md', 'CONTRIBUTIONS.md'):
                self.assertNotIn(pending['url'], (root / name).read_text(encoding='utf-8'))
            merged = pull_request(1)
            changed = updater.sync_profile(root, LOGIN, MONTH, paged_request(response([merged])))
            self.assertEqual(len(changed), 3)
            for name in ('README.md', 'README.zh-CN.md', 'CONTRIBUTIONS.md'):
                self.assertIn(merged['url'], (root / name).read_text(encoding='utf-8'))

    def test_bilingual_generation_preserves_surrounding_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('README.md', 'README.zh-CN.md'):
                (root / name).write_bytes(TEMPLATE.encode('utf-8'))
            files = updater.build_files(root, LOGIN, [pull_request(1)], MONTH)
            self.assertIn(root / 'README.md', files)
            self.assertIn(root / 'README.zh-CN.md', files)
            self.assertIn(root / 'CONTRIBUTIONS.md', files)
            for name in ('README.md', 'README.zh-CN.md'):
                self.assertTrue(files[root / name].startswith('Keep this introduction.\n<!-- CONTRIBUTIONS:START -->'))
                self.assertTrue(files[root / name].endswith('<!-- CONTRIBUTIONS:END -->\nKeep this footer.\n'))
            self.assertIn('Merged', files[root / 'README.md'])
            self.assertIn('已合并', files[root / 'README.zh-CN.md'])

    def test_missing_primary_marker_does_not_write_either_language_or_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            originals = {'README.md': TEMPLATE, 'README.zh-CN.md': 'No managed block.\n', 'CONTRIBUTIONS.md': 'Keep archive.\n'}
            for name, text in originals.items():
                (root / name).write_bytes(text.encode('utf-8'))
            with self.assertRaises(RuntimeError):
                updater.sync_profile(root, LOGIN, MONTH, paged_request(response([pull_request(1)])))
            self.assertEqual({name: (root / name).read_text(encoding='utf-8') for name in originals}, originals)

    def test_repeated_sync_is_idempotent_and_monthly_checkpoint_only_changes_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('README.md', 'README.zh-CN.md'):
                (root / name).write_bytes(TEMPLATE.encode('utf-8'))
            first = updater.sync_profile(root, LOGIN, MONTH, paged_request(response([pull_request(1)])))
            self.assertEqual(set(first), {root / 'README.md', root / 'README.zh-CN.md', root / 'CONTRIBUTIONS.md'})
            repeated = updater.sync_profile(root, LOGIN, MONTH, paged_request(response([pull_request(1)])))
            self.assertEqual(repeated, [])
            monthly = updater.sync_profile(root, LOGIN, '2026-11', paged_request(response([pull_request(1)])))
            self.assertEqual(monthly, [root / 'CONTRIBUTIONS.md'])

    def test_failed_file_replacement_restores_previous_documents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            originals = {root / 'README.md': b'old English\n', root / 'README.zh-CN.md': b'old Chinese\n', root / 'CONTRIBUTIONS.md': b'old archive\n'}
            for path, content in originals.items():
                path.write_bytes(content)
            files = {path: 'new content\n' for path in originals}
            real_replace = os.replace
            failed = False

            def replace(source, target):
                nonlocal failed
                if Path(target) == root / 'README.zh-CN.md' and not failed:
                    failed = True
                    raise OSError('Disk write failed')
                return real_replace(source, target)

            with patch.object(updater.os, 'replace', side_effect=replace):
                with self.assertRaises(OSError):
                    updater.apply_files(files)
            self.assertEqual({path: path.read_bytes() for path in originals}, originals)
            self.assertEqual(set(root.iterdir()), set(originals))


if __name__ == '__main__':
    unittest.main()
