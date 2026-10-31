#!/usr/bin/env python3
"""Focused attribution validation and real Hugo catalog regression fixtures."""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
import unittest

from author_pages import author_names, source_credits, verify_author_pages

ROOT = Path(__file__).resolve().parents[1]


class AuthorDataTest(unittest.TestCase):
    def test_valid_names_and_supported_format(self):
        names = ['Anne Brontë', 'J. R. O’Neil', 'Comma, Name', 'Amp & Name']
        self.assertEqual(author_names('---\nauthors: ' + json.dumps(names) + '\n---\nBody', 'sample.md'), names)

    def test_invalid_author_fields_are_actionable(self):
        for field in ['', 'authors: []', 'authors: "Person"', 'authors: null', 'authors: ["Max H. Bazerman"]', 'authors: [1]',
                      'authors: [" "]', 'authors: [" Person"]', 'authors: ["Person", "Person"]',
                      'authors: ["Anne Brontë", "Anne Bronte"]', "authors: ['Person']",
                      'authors:\n  - Person', 'authors: ["Person"]\nauthors: ["Other"]']:
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'sample.md:'):
                author_names('---\n' + field + '\n---\n', 'sample.md')

    def test_inconsistent_names_rejected_and_drafts_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for i, name in enumerate(['J. Smith', 'J Smith']):
                p = root / f'content/posts/topic/book-{i}/index.md'
                p.parent.mkdir(parents=True)
                p.write_text('---\nauthors: ' + json.dumps([name]) + '\n---\n')
            with self.assertRaisesRegex(ValueError, 'inconsistent author name'):
                source_credits(root)
            p.write_text('---\ndraft: true\n---\n')
            self.assertEqual(len(source_credits(root)), 1)


class HugoAuthorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='author-pages-test-')
        cls.root = root = Path(cls.temp.name)
        shutil.copy2(ROOT / 'hugo.toml', root / 'hugo.toml')
        shutil.copytree(ROOT / 'layouts', root / 'layouts')
        (root / 'themes').symlink_to(ROOT / 'themes', target_is_directory=True)
        (root / 'assets').symlink_to(ROOT / 'assets', target_is_directory=True)
        cls.output = root / 'public'
        for i in range(39):
            names = ['Main Author']
            if i == 0:
                names += ['Anne Brontë', 'Art Bennett', 'Laraine Bennett']
            if i == 1:
                names += ['J. R. O’Neil', 'A & B <C>']
            cls.add_book(i, names)
        cls.build()

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @classmethod
    def add_book(cls, i, names):
        p = cls.root / f'content/posts/topic-{i % 2}/book-{i:02d}/index.md'
        p.parent.mkdir(parents=True, exist_ok=True)
        display = 'Art and Laraine Bennett' if i == 0 else ' and '.join(names)
        p.write_text('---\ntitle: ' + json.dumps(f'Book {i:02d}')
                     + '\nauthor: ' + json.dumps(display) + '\nauthors: ' + json.dumps(names)
                     + '\ncategories: ["Topic"]\ndescription: A test book.\n---\nSummary body.\n')

    @classmethod
    def build(cls):
        result = subprocess.run(['hugo', '--source', str(cls.root), '--destination', str(cls.output), '--cleanDestinationDir', '--panicOnWarning', '--quiet'], capture_output=True, text=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    def test_complete_catalog_pagination_cross_category_and_escaped_links(self):
        self.assertEqual(verify_author_pages(self.root, self.output), [])
        self.assertTrue((self.output / 'authors/main-author/page/2/index.html').is_file())
        first = (self.output / 'posts/topic-0/book-00/index.html').read_text()
        self.assertIn('>Art Bennett</a> and ', first)
        special = (self.output / 'posts/topic-1/book-01/index.html').read_text()
        self.assertIn('A &amp; B &lt;C&gt;', special)

    def test_wrong_membership_count_and_links_are_detected(self):
        path = self.output / 'authors/main-author/index.html'
        original = path.read_text()
        try:
            path.write_text(original.replace('/posts/topic-0/book-00/', '/posts/topic-0/missing/').replace('39 summaries', '99 summaries'))
            errors = verify_author_pages(self.root, self.output)
            self.assertTrue(any('membership' in e for e in errors), errors)
            self.assertTrue(any('count' in e for e in errors), errors)
            self.assertTrue(any('targets' in e or 'source' in e for e in errors), errors)
        finally:
            path.write_text(original)

    def test_slug_collision_fails_instead_of_merging_people(self):
        path = self.output / 'authors/index.html'
        original = path.read_text()
        try:
            path.write_text(original.replace('/authors/anne-bront%C3%AB/', '/authors/main-author/'))
            errors = verify_author_pages(self.root, self.output)
            self.assertTrue(any('collision' in e for e in errors), errors)
        finally:
            path.write_text(original)


if __name__ == '__main__':
    unittest.main()
