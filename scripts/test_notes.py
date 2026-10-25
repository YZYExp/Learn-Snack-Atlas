import unittest
import xml.etree.ElementTree as ET
from notes import parse_notes, EpubNotes


class NotesTests(unittest.TestCase):
    def test_definition_order_normalizes_to_reading_order(self):
        notes = parse_notes('B[^ch01-b] then A[^ch01-a].\n\n[^ch01-a]: A\n[^ch01-b]: B')
        self.assertEqual(notes.order, ('ch01-b', 'ch01-a'))
        self.assertNotIn(']:', notes.body)
        self.assertLess(notes.markdown().index('[^ch01-b]:'), notes.markdown().index('[^ch01-a]:'))

    def test_multiple_references_each_get_a_return_link(self):
        notes = parse_notes('A[^ch01-a] again[^ch01-a].\n\n[^ch01-a]: Explains & compares.')
        renderer = EpubNotes(notes)
        from html import escape
        body = renderer.reference('ch01-a') + renderer.reference('ch01-a') + renderer.render(escape)
        tree = ET.fromstring('<html xmlns:epub="http://www.idpf.org/2007/ops">'+body+'</html>')
        ids = {node.get('id') for node in tree.iter() if node.get('id')}
        links = [node.get('href')[1:] for node in tree.iter('a')]
        self.assertTrue(set(links) <= ids)
        self.assertIn('fnref-ch01-a-2', ids)
        self.assertIn('返回正文2', ''.join(tree.itertext()))

    def test_indented_paragraphs_and_external_citation(self):
        notes = parse_notes('Term[^ch02-a].\n\n[^ch02-a]: First.\n\n    Second [source](https://example.org/).\n\nNext body.')
        self.assertIn('\n\nSecond', notes.definitions['ch02-a'])
        self.assertIn('Next body.', notes.body)
        self.assertEqual(parse_notes(notes.markdown()).definitions, notes.definitions)

    def test_no_notes(self):
        notes = parse_notes('# Chapter\nPlain text.')
        self.assertFalse(notes.order)
        self.assertEqual(EpubNotes(notes).render(str), '')

    def test_rejects_broken_source(self):
        for source in ('A[^ch01-a].', '[^ch01-a]: unused', 'A[^ch01-a].\n[^ch01-a]: x\n[^ch01-a]: y', 'A[^ch01-a].\n[^ch01-a]: nested[^ch01-b]', 'A[^Bad Id].\n[^Bad Id]: x'):
            with self.subTest(source=source), self.assertRaises(ValueError):
                parse_notes(source)


if __name__ == '__main__':
    unittest.main()
