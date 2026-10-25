"""Shared validation and EPUB rendering for the book's Markdown footnotes.

Notes are chapter-local explanatory prose. Definitions may continue in indented
paragraphs; nested notes and unused definitions are rejected rather than hidden.
"""
from collections import Counter
from dataclasses import dataclass
from html import escape
import re

REFERENCE = re.compile(r'\[\^([^\]\n]+)\]')
DEFINITION = re.compile(r'^\[\^([^\]]+)\]:[ \t]*(.*)$')
IDENTIFIER = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


@dataclass
class Notes:
    body: str
    definitions: dict
    order: tuple

    def markdown(self):
        """Normalize definition order so both readers number by first reference."""
        definitions = []
        for key in self.order:
            first, *rest = self.definitions[key].splitlines()
            definitions.append(f'[^{key}]: {first}' + ''.join('\n    ' + line if line else '\n' for line in rest))
        return self.body.rstrip() + ('\n\n' + '\n\n'.join(definitions) if definitions else '') + '\n'


def parse_notes(source, label='document'):
    lines = source.splitlines()
    body, definitions = [], {}
    i = 0
    while i < len(lines):
        match = DEFINITION.match(lines[i])
        if not match:
            body.append(lines[i]); i += 1; continue
        key, first = match.groups()
        if not IDENTIFIER.fullmatch(key):
            raise ValueError(f'{label}: invalid footnote identifier {key!r}')
        if key in definitions:
            raise ValueError(f'{label}: duplicate footnote definition {key}')
        parts = [first]; i += 1
        while i < len(lines):
            if lines[i].startswith(('    ', '\t')):
                parts.append(lines[i][4:] if lines[i].startswith('    ') else lines[i][1:]); i += 1
            elif not lines[i].strip() and i + 1 < len(lines) and lines[i+1].startswith(('    ', '\t')):
                parts.append(''); i += 1
            else:
                break
        definition = '\n'.join(parts).strip()
        if not definition or REFERENCE.search(definition):
            raise ValueError(f'{label}: empty or nested footnote {key}')
        definitions[key] = definition
    body = '\n'.join(body)
    order = tuple(dict.fromkeys(REFERENCE.findall(body)))
    missing = set(order) - definitions.keys()
    unused = definitions.keys() - set(order)
    if missing or unused:
        raise ValueError(f'{label}: undefined notes {sorted(missing)}, unused notes {sorted(unused)}')
    return Notes(body, definitions, order)


class EpubNotes:
    def __init__(self, notes):
        self.notes = notes
        self.counts = Counter()
        self.numbers = {key: i for i, key in enumerate(notes.order, 1)}

    def reference(self, key):
        self.counts[key] += 1
        number = self.numbers[key]
        return (f'<sup id="fnref-{key}-{self.counts[key]}"><a href="#fn-{key}" '
                f'epub:type="noteref" role="doc-noteref" aria-label="注释{number}">{number}</a></sup>')

    def render(self, inline):
        if not self.notes.order:
            return ''
        output = ['<section class="footnotes" aria-labelledby="chapter-notes-title"><h2 id="chapter-notes-title">本章注释</h2>']
        for key in self.notes.order:
            paragraphs = [inline(' '.join(p.splitlines())) for p in self.notes.definitions[key].split('\n\n')]
            back = ' '.join(f'<a href="#fnref-{key}-{i}" role="doc-backlink">返回正文' + (str(i) if self.counts[key] > 1 else '') + '</a>' for i in range(1, self.counts[key]+1))
            paragraphs[0] = f'<span class="note-number">[{self.numbers[key]}]</span> ' + paragraphs[0]
            paragraphs[-1] += ' ' + back
            output.append(f'<div id="fn-{escape(key, quote=True)}" epub:type="footnote">' + ''.join('<p>'+p+'</p>' for p in paragraphs) + '</div>')
        return '\n'.join(output) + '</section>'
