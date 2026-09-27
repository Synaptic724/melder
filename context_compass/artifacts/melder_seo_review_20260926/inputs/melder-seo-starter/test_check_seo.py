"""Synthetic fixture tests; these do not build or test the Melder repository."""
import tempfile
import unittest
from pathlib import Path
from check_seo import audit

BASE = "https://melder.readthedocs.io/en/latest/"


def html(name="index.html", title="Melder documentation", description="Learn to use Melder.", extra=""):
    return (f'<html lang="en"><head><title>{title}</title>'
            f'<link rel="canonical" href="{BASE}{name}">'
            f'<meta name="description" content="{description}">{extra}'
            '</head><body><h1>Melder</h1></body></html>')


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def site(self, pages):
        for name, text in pages.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        entries = ''.join(f'<url><loc>{BASE}{name}</loc></url>' for name in pages)
        (self.root / 'sitemap.xml').write_text(
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + entries + '</urlset>')

    def test_valid_site(self):
        self.site({'index.html': html()})
        report = audit(self.root, BASE, ('index.html',))
        self.assertEqual((report['errors'], report['warnings']), (0, 0))

    def test_required_description(self):
        self.site({'index.html': html(description='')})
        self.assertEqual(audit(self.root, BASE, ('index.html',))['errors'], 1)
        self.assertEqual(audit(self.root, BASE)['warnings'], 1)

    def test_duplicate_titles(self):
        self.site({'index.html': html(), 'guide.html': html('guide.html', description='Guide details.')})
        self.assertTrue(any('Duplicate title' in x['message'] for x in audit(self.root, BASE)['issues']))

    def test_wrong_canonical(self):
        self.site({'index.html': html(name='wrong.html')})
        self.assertTrue(any('Expected canonical' in x['message'] for x in audit(self.root, BASE)['issues']))

    def test_noindex(self):
        self.site({'index.html': html(extra='<meta name="robots" content="noindex,follow">')})
        self.assertTrue(any('noindex on' in x['message'] for x in audit(self.root, BASE)['issues']))

    def test_duplicate_description_tags(self):
        self.site({'index.html': html(extra='<meta name="description" content="Other">')})
        self.assertTrue(any('More than one meta description' in x['message'] for x in audit(self.root, BASE)['issues']))

    def test_missed_required_glob(self):
        self.site({'index.html': html()})
        self.assertTrue(any('matched no page' in x['message'] for x in audit(self.root, BASE, ('missing/*',))['issues']))

    def test_missing_sitemap(self):
        (self.root / 'index.html').write_text(html())
        self.assertTrue(any('Missing sitemap' in x['message'] for x in audit(self.root, BASE)['issues']))

    def test_empty_directory(self):
        self.assertGreater(audit(self.root, BASE)['errors'], 0)


if __name__ == '__main__':
    unittest.main()
