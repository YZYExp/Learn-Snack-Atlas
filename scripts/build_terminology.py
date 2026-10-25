"""Rebuild the reviewed bilingual lookup region; not part of website CI."""
from pathlib import Path
import json,re
from notes import parse_notes
R=Path(__file__).resolve().parents[1]
book=json.loads((R/'book.json').read_text());chapters={int(c['id'][2:]):c for c in book['chapters']};rows=[];lookup={}
for path in sorted((R/'editorial/proofread').glob('review-*.json')):
 for term in json.loads(path.read_text()).get('terms',[]):
  chapter=term['chapter'];key={'澄粉／小麦淀粉':'澄面／小麦淀粉'}.get(term['zh'],term['zh'])
  if term.get('note_id'):
   assert term['note_id'] in parse_notes((R/chapters[chapter]['source']).read_text()).definitions,(key,term['note_id'])
  if key not in lookup:
   row={**term,'zh':key,'chapters':[chapter],'sources':[term['source_url']]};rows.append(row);lookup[key]=row
  else:
   row=lookup[key]
   if chapter not in row['chapters']:row['chapters'].append(chapter)
   if term['source_url'] not in row['sources']:row['sources'].append(term['source_url'])
def cell(value):return str(value).replace('|','／').replace('\n',' ')
lines=['## 原文检索：材料、工艺与品名','','下列原文与中文解释对应正文语境；重复出现的同名词合并回查章节。具体事实与出处见各章及其注释。','']
for low,high,title in [(1,6,'基础材料与中式工艺'),(7,12,'蒸煎、面包、蛋糕与起酥'),(13,18,'甜点与地区名称'),(19,24,'家常面食与世界咸点')]:
 lines+=['### '+title,'','| 中文词 | 原文／通行拼写 | 语言或使用语境 | 解释与回查 |','|---|---|---|---|']
 for row in rows:
  if not low<=row['chapter']<=high:continue
  links='、'.join(f'[第{n:02d}章](../{chapters[n]["source"]})' for n in sorted(row['chapters']))
  lines.append('| '+' | '.join([cell(row['zh']),cell(row['original']),cell(row['language']),cell(row['explanation']).rstrip('。；; ')+'；'+links])+' |')
 lines.append('')
p=R/'appendices/glossary.md';s=p.read_text();s=re.sub(r'<!-- terminology:start -->.*?<!-- terminology:end -->','<!-- terminology:start -->\n\n'+'\n'.join(lines)+'\n<!-- terminology:end -->',s,flags=re.S);p.write_text(s)
(R/'editorial/proofread/terminology.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('Reviewed terminology entries:',len(rows))
