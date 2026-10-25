"""Integrate only individually approved scene-expansion illustrations into the book."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1];E=R/'editorial';book=json.loads((R/'book.json').read_text());plans=json.loads((E/'expansion/image-plan.json').read_text());placements={};reviews={}
for group,review_name in [('dumplings','dumpling'),('rounds-breakfast','rounds-breakfast'),('street-world','street-world')]:
 d=json.loads((E/f'expansion-{group}.json').read_text())
 for row in d.get('images',d.get('illustrations',[])):placements[row['id']]=row
 for row in json.loads((E/f'expansion/{review_name}-image-review.json').read_text()):reviews[row['id']]=row
ids={r['id'] for r in plans};index=[r for r in json.loads((E/'image-index.json').read_text()) if r['id'] not in ids];atlas=json.loads((R/'site/atlas.json').read_text());atlas['cards']=[r for r in atlas['cards'] if r['id'] not in ids];records=[]
for plan in plans:
 id=plan['id'];review=reviews[id];assert review['approved'],id
 p=placements[id];ch=plan['chapter'];entry=next(c for c in book['chapters'] if int(c['id'][2:])==ch);path=R/entry['source'];s=path.read_text();heading=p['heading'];start=s.index('## '+heading+'\n');end=s.find('\n## ',start+4);end=len(s) if end<0 else end
 section=s[start:end];links=re.findall(r'\]\((https?://[^)]+)\)',section);source=p.get('source_url') or (links[0] if links else None);assert source,id
 caption=review['caption'].strip();marker='<!-- scene-expansion:'+id+' -->';image=R/f'assets/images/{id}.png';assert image.is_file()
 if marker not in s:
  number=max([int(n) for n in re.findall(r'图'+str(ch)+r'-([0-9]+)',s)]+[0])+1
  figure=f'图{ch}-{number}　'+caption
  block=f'\n\n{marker}\n\n![{figure}](../assets/images/{id}.png)\n\n{figure}\n\nAI生成示意：呈现一种代表外观，具体用料与地区变体见正文。[品种与工艺参照]({source})。\n'
  s=s[:end].rstrip()+block+'\n'+s[end:];path.write_text(s)
 else:
  figure=re.search(r'!\[([^\]]+)\]\(../assets/images/'+id+r'\.png\)',s)[1]
 digest=hashlib.sha256(image.read_bytes()).hexdigest()
 record={'id':id,'file':str(image.relative_to(R)),'chapter':ch,'heading':heading,'caption':figure,'kind':'AI-generated teaching illustration','source_url':source,'sha256':digest,'visual_checked':True,'review_notes':review['notes']};records.append(record);index.append(record)
 atlas['cards'].append({'id':id,'title':plan['title'],'description':caption,'group':'世界' if ch==24 else '中式','chapter':ch,'heading':heading,'objects':[plan['title']],'image':str(image.relative_to(R))})
atlas['home_ids']=['exp-jiaozi','exp-small-wonton','exp-sesame-tangyuan','exp-mantou-huajuan','exp-springroll','exp-samosa']
(E/'image-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n');(E/'expansion/final-images.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');(R/'site/atlas.json').write_text(json.dumps(atlas,ensure_ascii=False,indent=2)+'\n')
print('Integrated',len(records),'new images; total',len(index),'atlas cards',len(atlas['cards']))
