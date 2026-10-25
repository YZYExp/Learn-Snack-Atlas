"""Integrate the reviewed expansion into the canonical chapter sources and public atlas."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[1];E=R/'editorial'
plans=[x for group in ['china','west','world'] for x in json.loads((E/f'pr-{group}-image-plan.json').read_text())]
meta=json.loads((R/'book.json').read_text());titles={
'atlas-cn-songgao':'松糕','atlas-cn-peanut-nuomici':'花生糯米糍','atlas-cn-taro-cake':'芋头糕','atlas-cn-taosu-shaobing':'桃酥与芝麻烧饼','atlas-cn-shaomai-fillings':'两种烧卖','atlas-cn-qianceng-yougao':'千层油糕','atlas-cn-yeerba':'叶儿粑','atlas-cn-fengli-honggui':'凤梨酥与红龟粿',
'atlas-we-cinnamon-roll':'肉桂卷','atlas-we-doughnut-types':'两种甜甜圈','atlas-we-danish':'丹麦点心','atlas-we-palmier-millefeuille':'蝴蝶酥与拿破仑','atlas-we-sponge-roll':'海绵蛋糕卷','atlas-we-lemon-fruit-tarts':'柠檬塔与水果塔','atlas-we-chewy-cookie':'巧克力豆曲奇','atlas-we-custard-cream':'两种蛋奶体系',
'atlas-wo-dango':'米粉团子','atlas-wo-monaka-dorayaki':'最中与铜锣烧','atlas-wo-kueh-dadar':'椰糖椰丝卷','atlas-wo-love-letters':'薄脆蛋卷','atlas-wo-halva-comparison':'两种Halva','atlas-wo-mochi-bread-comparison':'两种“麻薯”面包'}
reviews={}
for g in ['china','west','world']:
 p=E/f'pr-{g}-image-review.json'
 if p.exists():
  data=json.loads(p.read_text())
  if isinstance(data,dict):data=data.get('images',data.get('reviews',data.get('results',[])))
  for x in data:reviews[x['id']]=x
records=[];cards=[]
index=json.loads((E/'image-index.json').read_text());ids={x['id'] for x in plans};index=[x for x in index if x['id'] not in ids]
for plan in plans:
 id=plan['id'];chapter=plan['chapter'];source=R/next(c['source'] for c in meta['chapters'] if int(c['id'][2:])==chapter);s=source.read_text();image=R/'assets/images'/f'{id}.png';assert image.exists(),image
 caption=reviews.get(id,{}).get('caption') or plan['caption'];caption=re.sub(r'^(?:AI)?(?:生成图|教学示意|生成示意)[：:]?','',caption).strip()
 marker=f'<!-- atlas-expansion:{id} -->'
 if marker not in s:
  current=[int(x) for x in re.findall(r'图'+str(chapter)+r'-([0-9]+)',s)];num=max(current,default=0)+1
  figure=f'图{chapter}-{num}　{caption}'
  block=f'\n\n{marker}\n\n![{figure}](../assets/images/{id}.png)\n\n{figure}\n\nAI生成示意：用于观察代表外形与组织关系。[工艺参照资料]({plan["source_url"]})。\n'
  h='## '+plan['heading'];start=s.find(h+'\n');assert start>=0,(id,h);end=s.find('\n## ',start+len(h));end=len(s) if end<0 else end
  s=s[:end].rstrip()+block+'\n'+s[end:];source.write_text(s)
 else:
  oldfigure=re.search(r'!\[([^\]]+)\]\(../assets/images/'+re.escape(id)+r'\.png\)',s)[1]
  prefix=oldfigure.split('　',1)[0];figure=prefix+'　'+caption
  s=s.replace(oldfigure,figure);source.write_text(s)
 rec={**plan,'file':str(image.relative_to(R)),'kind':'AI-generated teaching illustration','caption':figure,'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'visual_review_file':f'editorial/pr-{"china" if chapter<10 else "west" if chapter<15 else "world"}-image-review.json','visual_checked':bool(reviews.get(id,{}).get('approved'))}
 records.append(rec);index.append(rec)
 desc=caption.replace('教学示意：','：').replace('生成图用于外观对照。','').replace('教学对照：','：')
 cards.append({'id':id,'title':titles[id],'description':desc,'group':'中式' if chapter<10 else '西式' if chapter<15 else '世界','chapter':chapter,'heading':plan['heading'],'objects':plan['objects'],'image':str(image.relative_to(R))})
(E/'pr-expanded-illustrations.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));(E/'image-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2))
(R/'site/atlas.json').write_text(json.dumps({'hero_id':'atlas-we-cinnamon-roll','home_ids':['atlas-cn-songgao','atlas-cn-taosu-shaobing','atlas-we-lemon-fruit-tarts','atlas-we-danish','atlas-wo-monaka-dorayaki','atlas-wo-kueh-dadar'],'cards':cards},ensure_ascii=False,indent=2))
print('Integrated',len(records),'illustrations; book total',len(index))
