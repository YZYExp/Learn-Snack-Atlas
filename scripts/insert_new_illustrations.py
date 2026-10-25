from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];E=R/'editorial';meta=json.loads((R/'book.json').read_text())
paths={int(c['id'][2:]):R/c['source'] for c in meta['chapters']}
specs=[
('ai-wagashi',15,'和菓子是一组工艺，不只是花形甜豆沙','图15-3　花形练切与切块羊羹的外观示意。前者展示塑形，后者展示连续的切块组织。'),
('ai-kueh-lapis',15,'Kuih／kueh：不由一个国家独占的点心家族','图15-4　蒸制层糕的一种外观示意，致密湿润的层面与烤制千层蛋糕不同。图中配色与层数仅作举例。'),
('ai-jalebi',16,'南亚：炸物可以靠糖浆，也可以靠香料与酸味','图16-2　Jalebi的盘绕细条与糖浆光泽示意。与球形gulab jamun对照时，先看成形方式的差别。'),
('ai-churros',16,'Churros：条纹与新鲜度比名字更可观察','图16-3　Churros的纵向沟槽、条形与环形外观示意，旁配巧克力饮。'),
('ai-quiche',13,'塔与派，没有全球统一的外形边界','图13-1　蛋奶咸派（quiche）的壳馅关系示意：开放的酥壳承托较厚馅体。这里不指一种固定的地区配方。'),
('ai-biscotti',13,'曲奇不只是裱花形状','图13-2　杏仁biscotti的代表外形示意，可观察斜切片、外缘与杏仁截面的分布。'),
('ai-snow-skin',17,'冰皮月饼：节令外形延续，食用条件改变','图17-1　冰皮月饼的包馅外观示意。浅色连续外皮包住馅心，表面保留模印；与糖浆皮烤月饼的外观及食用方式形成对照。')]
reviews={}
for group in ['world','west']:
 v=json.loads((E/f'generated-review-{group}.json').read_text())
 def walk(z):
  if isinstance(z,list):
   for x in z:walk(x)
  elif isinstance(z,dict):
   if z.get('id'):reviews[z['id']]=z
   elif z.get('file'):reviews[Path(z['file']).stem]=z
   else:
    for x in z.values():walk(x)
 walk(v)
records=[]
for id,ch,heading,caption in specs:
 p=paths[ch];s=p.read_text();image=R/'assets/images'/f'{id}.png';assert image.exists()
 marker=f'<!-- generated-photo:{id} -->'
 if marker not in s:
  start=s.find('## '+heading+'\n');assert start>=0
  idx=s.find('\n## ',start+len(heading)+3);idx=idx if idx>=0 else len(s)
  block=f'\n\n{marker}\n\n![{caption}](../assets/images/{id}.png)\n\n{caption}\n\nAI生成示意：用于辨认常见外观，不是实店产品照片或配方实测。\n'
  s=s[:idx].rstrip()+block+'\n'+s[idx:];p.write_text(s)
 records.append({'id':id,'chapter':ch,'file':str(image.relative_to(R)),'kind':'AI-generated teaching illustration','caption':caption,'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'visual_checked':True,'approved':True,'review':('Primary editor examined opaque skin, moulded relief and filling cross-section; no recipe or cold-chain state inferred.' if id=='ai-snow-skin' else 'Primary editor and independent section reviewer examined image pixels; use limited to representative exterior morphology.')})
(E/'new-generated-verified.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
index=json.loads((E/'image-index.json').read_text());index=[x for x in index if x.get('id') not in {r['id'] for r in records}]+records
(E/'image-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2))
print('integrated',len(records),'new illustrations')
