"""Derive the complete image atlas from images actually embedded in the book."""
import re
from pathlib import Path

KINDS = {'licensed photograph': '实物照片',
         'AI-generated teaching illustration': 'AI教学示意',
         'original diagram': '原创工艺图'}

def image_anchor(name):
    return 'image-' + Path(name).stem

def collect_cards(entries, metadata, config):
    """Use the manuscript as membership source; curated cards are optional overrides."""
    records = {Path(m['file']).name: m for m in metadata}
    curated = {Path(c['image']).name: c for c in config['cards']}
    assert len(curated) == len(config['cards']), 'Duplicate curated image'
    cards = []
    seen = set()
    for entry in entries:
        for match in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', entry['text']):
            name = Path(match[2]).name
            if name in seen:
                continue
            seen.add(name)
            assert name in records, f'Missing image metadata: {name}'
            meta = records[name]
            kind = KINDS[meta['kind']]
            card = dict(curated.get(name, {}))
            chapter = int(entry['id'][2:]) if entry.get('id', '').startswith('ch') else 0
            title = config.get('titles', {}).get(meta['id']) or re.sub(r'^图\S+\s*', '', match[1]).split('。')[0]
            if meta['kind'] == 'original diagram':
                group = '基础与应用'
            elif chapter in (5, 6, 7, 8, 9, 19, 20, 21, 22, 23):
                group = '中式'
            elif chapter in (10, 11, 12, 13, 14):
                group = '西式'
            elif chapter in (15, 16, 24):
                group = '世界'
            else:
                group = '基础与应用'
            card.update({'id': meta['id'], 'title': card.get('title', title),
                         'description': card.get('description', meta['caption']),
                         'group': card.get('group', group), 'chapter': chapter,
                         'href': entry['url'] + '#' + image_anchor(name),
                         'image_name': name, 'kind': kind,
                         'keywords': ' '.join(card.get('objects', [])) + ' ' + match[1],
                         'credit': '', 'source_url': meta.get('source_page', '')})
            if kind == '实物照片':
                assert meta.get('author') and meta.get('license') and meta.get('source_page'), name
                card['credit'] = meta['author'] + ' · ' + meta['license']
            cards.append(card)
    assert set(curated) <= seen, 'Curated card image is not embedded in the book'
    assert len({c['id'] for c in cards}) == len(cards), 'Duplicate image ID'
    return cards
