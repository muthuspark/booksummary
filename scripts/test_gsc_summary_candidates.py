#!/usr/bin/env python3
"""Offline GSC ranking and automation checks; no credentials or Codex required."""
from datetime import date
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import Mock

import gsc_summary_candidates as gsc

SCRIPTS = Path(__file__).resolve().parent


def row(slug, clicks, impressions, position=8):
    return dict(keys=[f'https://summaries.muthu.co/posts/science/{slug}/'],
                clicks=clicks, impressions=impressions, position=position)


class CandidatesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'scripts').mkdir()
        shutil.copy2(SCRIPTS.parent / 'IMAGE_STYLE.md', self.root / 'IMAGE_STYLE.md')
        for name in ('gsc_summary_candidates.py', 'improve_trending_summaries.sh', 'author_pages.py'):
            shutil.copy2(SCRIPTS / name, self.root / 'scripts' / name)
        for slug in ('growing', 'emerging', 'declining'):
            article = self.root / f'content/posts/science/{slug}/index.md'
            article.parent.mkdir(parents=True)
            article.write_text('---\ntitle: A Book by An Author\nauthor: An Author\n'
                               'authors: ["An Author"]\ncategories: ["Science"]\n'
                               'description: Useful explanation\nimage: image.png\n---\n'
                               '# Main idea\n\nA useful explanation.\n')
            article.with_name('image.png').write_bytes(b'existing image left unchanged')
        (self.root / 'progress.md').write_text('Leave progress unchanged.\n')
        self.report = dict(periods=gsc.reporting_periods(date(2026, 11, 10)), queries={},
                           current_pages=[row('growing', 20, 300), row('emerging', 0, 100),
                                          row('declining', 10, 1000)],
                           previous_pages=[row('growing', 10, 200), row('declining', 20, 500)])
        self.fixture = self.root / 'analytics.json'
        self.fixture.write_text(json.dumps(self.report))
        self.output = self.root / 'run'

    def helper(self, action='prepare', check=True):
        result = subprocess.run(['python3', str(self.root / 'scripts/gsc_summary_candidates.py'),
                                 action, '--output', str(self.output), '--analytics-json', str(self.fixture)],
                                cwd=self.root, capture_output=True, text=True)
        if check:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_periods_are_inclusive_adjacent_and_lagged(self):
        self.assertEqual(self.report['periods'], {
            'current': {'start': '2026-10-11', 'end': '2026-11-07'},
            'previous': {'start': '2026-09-13', 'end': '2026-10-10'}})

    def test_growth_ranking_and_count_exclude_declining_clicks(self):
        selected = gsc.select_candidates(self.report, self.root, 2)
        self.assertEqual([x['destination'].split('/')[-2] for x in selected], ['growing', 'emerging'])
        self.assertEqual(len(gsc.select_candidates(self.report, self.root, 1)), 1)
        self.assertEqual(selected[1]['reason'], 'impression growth')

    def test_tiny_spikes_and_non_articles_are_excluded(self):
        self.report['current_pages'] = [row('growing', 2, 49), row('missing', 99, 999)]
        self.assertEqual(gsc.select_candidates(self.report, self.root, 2), [])
        for url in ('https://other.co/posts/science/growing/',
                    'https://summaries.muthu.co/categories/science/',
                    'https://summaries.muthu.co/posts/%2e%2e/growing/'):
            self.assertIsNone(gsc.article_path(url, self.root))

    def test_variants_combine_without_duplicate_article_selection(self):
        variant = row('growing', 5, 100, 4)
        variant['keys'][0] += 'index.html'
        self.report['current_pages'].append(variant)
        selected = gsc.select_candidates(self.report, self.root, 2)
        self.assertEqual(selected[0]['current']['clicks'], 25)
        self.assertAlmostEqual(selected[0]['current']['position'], 7)

    def test_api_pagination_filters_and_errors(self):
        service = Mock()
        execute = service.searchanalytics.return_value.query.return_value.execute
        execute.side_effect = [{'rows': [{}] * 25000}, {'rows': [{}]}]
        filters = [{'dimension': 'page', 'operator': 'equals', 'expression': 'https://example.com/'}]
        rows = gsc.query_rows(service, gsc.PROPERTY, self.report['periods']['current'], ['page'], filters)
        self.assertEqual(len(rows), 25001)
        calls = service.searchanalytics.return_value.query.call_args_list
        self.assertEqual(calls[1].kwargs['body']['startRow'], 25000)
        self.assertEqual(calls[0].kwargs['body']['dataState'], 'final')
        self.assertNotIn('orderBy', calls[0].kwargs['body'])
        execute.side_effect = RuntimeError('API unavailable')
        with self.assertRaisesRegex(RuntimeError, 'API unavailable'):
            gsc.query_rows(service, gsc.PROPERTY, self.report['periods']['current'], ['page'])

    def test_evidence_prompt_and_no_change_validation(self):
        self.helper()
        prompt = (self.output / 'prompt.txt').read_text()
        self.assertIn('click_gain', prompt)
        self.assertIn('image-source.md', prompt)
        self.assertIn('ASD-STE100', prompt)
        self.assertIn('warm-gouache-v1', prompt)
        self.helper('validate')

    def test_metadata_progress_and_new_image_validation_failures(self):
        self.helper()
        article = self.root / 'content/posts/science/growing/index.md'
        original = article.read_text()
        article.write_text(original.replace('title: A Book', 'title: Another Book'))
        self.assertIn('metadata changed', self.helper('validate', check=False).stderr)
        article.write_text(original)
        article.with_name('image.png').write_bytes(b'not a real new PNG')
        self.assertIn('new hero must', self.helper('validate', check=False).stderr)
        (self.root / 'progress.md').write_text('Unexpected change')
        self.assertIn('progress.md changed', self.helper('validate', check=False).stderr)

    def test_missing_comparison_data_requests_no_edits(self):
        self.report['previous_pages'] = []
        self.fixture.write_text(json.dumps(self.report))
        self.assertIn('No eligible', self.helper().stdout)
        self.assertFalse((self.output / 'prompt.txt').exists())

    def test_shell_dry_run_and_failure_never_publish(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        for name, body in {
            'codex': '#!/bin/sh\ncat > child-prompt.txt\nexit 7\n',
            'hugo': '#!/bin/sh\nexit 0\n',
        }.items():
            tool = bin_dir / name
            tool.write_text(body)
            tool.chmod(0o755)
        script = self.root / 'scripts/improve_trending_summaries.sh'
        env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'])
        def run(*args):
            return subprocess.run(['bash', str(script), '--analytics-json', str(self.fixture), *args],
                                  cwd='/tmp', env=env, text=True, capture_output=True)
        dry = run('--dry-run', '--count', '1')
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertIn('Selected:', dry.stdout)
        self.assertFalse((self.root / 'child-prompt.txt').exists())
        self.assertEqual(run().returncode, 7)
        self.assertFalse((self.root / 'docs').exists())
        self.assertEqual(run('--count', '3').returncode, 2)
        self.assertEqual(run('--unknown').returncode, 2)
        # Publishing is refused before Codex because it would stage unrelated files.
        self.assertIn('clean checkout', run('--publish').stderr)

    def test_shell_success_and_build_failure_gate_publishing(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        (self.root / '.gitignore').write_text('__pycache__/\n')
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        files = {
            'bin/codex': '#!/bin/sh\ncat > /dev/null\nexit 0\n',
            'bin/hugo': '#!/bin/sh\nexit 0\n',
            'scripts/build_site.sh': '#!/bin/sh\ntouch build-ran\nexit "${BUILD_EXIT:-0}"\n',
            'render_publish.sh': '#!/bin/sh\ntouch publish-ran\n',
        }
        for name, body in files.items():
            tool = self.root / name
            tool.write_text(body)
            tool.chmod(0o755)
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Test',
                        '-c', 'user.email=test@example.com', 'commit', '-qm', 'Fixture'], check=True)
        env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'])
        command = ['bash', str(self.root / 'scripts/improve_trending_summaries.sh'),
                   '--analytics-json', str(self.fixture), '--publish']
        failed = subprocess.run(command, env=dict(env, BUILD_EXIT='6'), capture_output=True, text=True)
        self.assertEqual(failed.returncode, 6, failed.stderr)
        self.assertFalse((self.root / 'publish-ran').exists())
        (self.root / 'build-ran').unlink()
        success = subprocess.run(command, env=env, capture_output=True, text=True)
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertTrue((self.root / 'publish-ran').exists())


if __name__ == '__main__':
    unittest.main()
