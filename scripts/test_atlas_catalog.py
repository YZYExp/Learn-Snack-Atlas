"""Regression checks for complete manuscript-derived atlas membership."""
import json
from pathlib import Path
import unittest
from atlas_catalog import collect_cards

ROOT = Path(__file__).resolve().parents[1]
class AtlasCoverageTests(unittest.TestCase):
    def test_all_embedded_images_and_provenance(self):
        book = json.loads((ROOT/'book.json').read_text())
        entries = []
        for key in ('frontmatter', 'chapters', 'appendices', 'backmatter'):
            for entry in book.get(key, []):
                entries.append(dict(entry, text=(ROOT/entry['source']).read_text(),
                                    url=str(Path(entry['source']).with_suffix('.html'))))
        metadata = json.loads((ROOT/'editorial/image-index.json').read_text())
        config = json.loads((ROOT/'site/atlas.json').read_text())
        cards = collect_cards(entries, metadata, config)
        # Membership is derived independently of the optional hand-selected cards.
        automatic = collect_cards(entries, metadata, dict(config, cards=[]))
        self.assertEqual({c['id'] for c in cards}, {c['id'] for c in automatic})
        self.assertEqual({c['image_name'] for c in cards}, {Path(m['file']).name for m in metadata})
        for card in cards:
            with self.subTest(card=card['id']):
                self.assertIn('#image-', card['href'])
                if card['kind'] == '实物照片':
                    self.assertTrue(card['credit'])
                    self.assertTrue(card['source_url'].startswith('https://'))
                self.assertTrue(card['title'])
                self.assertTrue(card['description'])

    def test_new_embedded_image_is_automatically_included(self):
        entry = {'id':'ch01', 'url':'chapters/01.html', 'text':'![新工艺](../assets/images/new.png)'}
        meta = {'file':'assets/images/new.png','id':'new','kind':'original diagram','caption':'新图'}
        cards = collect_cards([entry], [meta], {'cards':[]})
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]['href'], 'chapters/01.html#image-new')
        self.assertEqual(cards[0]['kind'], '原创工艺图')
        with self.assertRaises(AssertionError):
            collect_cards([entry], [], {'cards':[]})

if __name__ == '__main__':
    unittest.main()
