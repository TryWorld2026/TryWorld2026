"""Guard the TryWorld brand hero and its README wiring."""

from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
MARK = (
    'M49 17C43 34 39 56 42 73C44 88 54 98 67 99'
    'M17 40C35 34 52 28 66 35C83 44 77 82 92 86'
    'C101 89 110 64 117 63C123 64 126 85 139 86C154 88 169 55 174 43'
)
LIGHT = ('#F2EEE6', '#24564E', '#F2693C', '#1B2523')
DARK = ('#1B2523', '#F2EEE6', '#9CC7BB', '#F2693C')
RAW = 'https://raw.githubusercontent.com/TryWorld2026/TryWorld2026/main/assets'


class BrandHeroTests(unittest.TestCase):
    def hero(self, name):
        path = ROOT / 'assets' / name
        self.assertTrue(path.is_file(), f'{name} is missing')
        return path.read_text(encoding='utf-8')

    def test_heroes_carry_the_official_tw_mark_and_viewport(self):
        for name in ('hero-light.svg', 'hero-dark.svg'):
            with self.subTest(name=name):
                svg = self.hero(name)
                ET.fromstring(svg)  # must stay well-formed XML for GitHub's SVG renderer
                self.assertIn('viewBox="0 0 1200 320"', svg)
                self.assertEqual(svg.count(MARK), 1, 'the hero must reuse the approved tw geometry verbatim')
                self.assertIn('aria-labelledby="title desc"', svg, 'accessible title/desc required')

    def test_heroes_use_the_approved_palette(self):
        light, dark = self.hero('hero-light.svg'), self.hero('hero-dark.svg')
        for color in LIGHT:
            self.assertIn(color, light, f'{color} missing from the light hero')
        for color in DARK:
            self.assertIn(color, dark, f'{color} missing from the dark hero')
        self.assertNotIn('#087f82', light + dark, 'the retired teal must not return')

    def test_readmes_pair_each_hero_with_a_mode_fragment(self):
        for readme in ('README.md', 'README.zh-CN.md'):
            with self.subTest(readme=readme):
                text = (ROOT / readme).read_text(encoding='utf-8')
                for name, fragment in (('hero-light.svg', '#gh-light-mode-only'), ('hero-dark.svg', '#gh-dark-mode-only')):
                    self.assertIn(f'{RAW}/{name}{fragment}', text)
                self.assertEqual(text.count('CONTRIBUTIONS:START'), 1)
                self.assertEqual(text.count('CONTRIBUTIONS:END'), 1)

    def test_readmes_link_the_live_site_once(self):
        for readme in ('README.md', 'README.zh-CN.md'):
            with self.subTest(readme=readme):
                text = (ROOT / readme).read_text(encoding='utf-8')
                self.assertEqual(text.count('https://tryworld.com.cn'), 2, 'hero link plus footer only')


if __name__ == '__main__':
    unittest.main()
