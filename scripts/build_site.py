#!/usr/bin/env python3
"""Independent homepage, searchable paginated atlas and chapter reader."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import argparse,json,os,re,shutil
from io import BytesIO
import markdown
from PIL import Image,ImageOps
from notes import parse_notes
from atlas_catalog import collect_cards, image_anchor
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',default='_site');p.add_argument('--epub',type=Path);args=p.parse_args()
OUT=(ROOT/args.output).resolve();assert OUT.parent==ROOT and OUT!=ROOT
if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir();book=json.loads((ROOT/'book.json').read_text());repo=os.environ.get('GITHUB_REPOSITORY','YZYExp/Learn-Snack-Atlas')
entries=[dict(e) for key in ('frontmatter','chapters','appendices','backmatter') for e in book.get(key,[])]
entries.append({'source':'references/reading-sources.md','title':'资料索引','slug':'reading-sources'})
by_source={e['source']:e for e in entries}
for e in entries:
 e['url']=str(Path(e['source']).with_suffix('.html'));e['text']=(ROOT/e['source']).read_text();e['headings']=re.findall(r'^## (.+)$',e['text'],re.M);e['notes']=parse_notes(e['text'],e['source']);e['text']=e['notes'].markdown()
images={}
for e in entries:
 for url in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',e['text']):
  src=(ROOT/Path(e['source']).parent/url).resolve();assert src.is_relative_to(ROOT/'assets/images') and src.is_file(),src;images[src.name]=src
image_dir=OUT/'assets/images';image_dir.mkdir(parents=True);sizes={}
for name,src in images.items():
 with Image.open(src) as opened:
  im=ImageOps.exif_transpose(opened).convert('RGB');sizes[name]=im.size
  for width in (480,1200):
   small=im.copy();small.thumbnail((width,10000),Image.Resampling.LANCZOS)
   buffer=BytesIO();small.save(buffer,format='WEBP',quality=88,method=4)
   payload=buffer.getvalue();assert payload,src
   (image_dir/f'{src.stem}-{width}.webp').write_bytes(payload)
for generated in image_dir.glob('*.webp'):
 with Image.open(generated) as checked:checked.verify()
for name in ('style.css','atlas.js'):shutil.copy2(ROOT/'site'/name,OUT/name)
(OUT/'.nojekyll').touch()
def image_url(name,prefix='',width=1200):return prefix+'assets/images/'+Path(name).stem+f'-{width}.webp'
def img_tag(name,alt,prefix='',eager=False):
 w,h=sizes[name];srcset=f'{image_url(name,prefix,480)} {min(480,w)}w, {image_url(name,prefix)} {min(1200,w)}w'
 return f'<img src="{image_url(name,prefix)}" srcset="{srcset}" sizes="(max-width:720px) calc(100vw - 36px),780px" width="{w}" height="{h}" alt="{escape(alt,quote=True)}" loading="{"eager" if eager else "lazy"}" decoding="async"'+(' fetchpriority="high"' if eager else '')+'>'
def header(active,prefix=''):
 links=''.join(f'<a href="{prefix}{url}"'+(' aria-current="page"' if active==key else '')+f'>{label}</a>' for key,url,label in [('home','index.html','首页'),('atlas','atlas.html','图鉴'),('contents','contents.html','目录')])
 return f'<a class="skip" href="#reading">跳至正文</a><header class="masthead"><div class="wrap"><a class="brand" href="{prefix}index.html"><span class="brand-mark" aria-hidden="true">点</span>点心之间</a><nav class="global-nav" aria-label="主要导航">{links}</nav></div></header>'
def footer(prefix=''):
 return f'<footer class="footer"><div class="wrap"><span>《点心之间》 · 中西传统与新式糕点小吃</span><div class="footer-links"><a href="{prefix}appendices/photo-credits.html">图片来源</a><a href="{prefix}references/reading-sources.html">资料索引</a><a href="https://github.com/{repo}">书稿与资料</a></div></div></footer>'
def page(path,title,body,active='',extra=''):
 path=Path(path);prefix='../'*(len(path.parts)-1)
 html=f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{escape(book["description"],quote=True)}"><title>{escape(title)} · 点心之间</title><link rel="stylesheet" href="{prefix}style.css"></head><body>{header(active,prefix)}{body}{footer(prefix)}{extra}</body></html>'
 target=OUT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(html)
config=json.loads((ROOT/'site/atlas.json').read_text())
metadata=json.loads((ROOT/'editorial/image-index.json').read_text())
cards=collect_cards(entries,metadata,config)
assert {c['image_name'] for c in cards} == set(images), 'Atlas must cover every book image'
for c in cards:
 name=c['image_name']
 c.update({'image':image_url(name),'srcset':f'{image_url(name,width=480)} {min(480,sizes[name][0])}w, {image_url(name)} {min(1200,sizes[name][0])}w','width':sizes[name][0],'height':sizes[name][1]})
def food_card(c):
 credit=(f'<p class="atlas-credit">{escape(c["credit"])} · <a href="{escape(c["source_url"],quote=True)}">原图与许可</a></p>' if c['credit'] else '')
 image=img_tag(c['image_name'],c['title']+'，'+c['kind'])
 return f'<article class="food-card"><a href="{c["href"]}"><div class="picture">{image}<span class="kind">{escape(c["kind"])}</span></div><div class="copy"><span class="category-name">{c["group"]} · 第{c["chapter"]:02d}章</span><h3>{escape(c["title"])}</h3><p>{escape(c["description"])}</p></div></a>{credit}</article>'
def count_index_rows(text):
 count=0
 for line in text.splitlines():
  if not line.startswith('|'):continue
  first=line.split('|')[1].strip()
  if first and not first.startswith('品名') and not set(first)<=set('- :'):count+=1
 return count
index_count=sum(count_index_rows((ROOT/'appendices'/name).read_text()) for name in ('chinese-index.md','world-index.md'))
hero=next((c for c in cards if c['id']==config['hero_id']),cards[0])
home=f'<main id="reading" class="wrap"><section class="hero"><div class="hero-copy"><span class="eyebrow">中西传统与新式点心图鉴</span><h1>从一口点心，<br>读懂<em>风味与工艺。</em></h1><p>米的糯、面的松、酥皮的层次，每一种口感都有来处。从熟悉的小吃出发，认识不同地方的点心与日常生活。</p><div class="actions"><a class="button primary" href="{book["chapters"][0]["source"].replace(".md",".html")}">开始阅读 <span aria-hidden="true">→</span></a><a class="button" href="atlas.html">先看点心图鉴</a></div></div><figure class="hero-visual">{img_tag(hero["image_name"],hero["title"]+"，AI教学示意",eager=True)}<span class="visual-tag">风味观察 · {escape(hero["title"])}</span><figcaption>AI教学示意 · {escape(hero["description"])}</figcaption></figure></section><div class="stats"><div class="stat"><strong>{len(book["chapters"])}</strong><span>章知识读本</span></div><div class="stat"><strong>{len(images)}</strong><span>幅随书图解</span></div><div class="stat"><strong>{index_count}</strong><span>条代表点心索引</span></div></div>'
category_data=[('01','饺子与馄饨','家常、汤食与锅贴的皮馅变化。',19),('02','汤圆与米食','甜馅、无馅圆子与咸汤的不同。',21),('03','早餐与街食','一笼包点、一张薄饼与一份小食。',22),('04','面包与烘焙','发酵、打发、起酥，让组织走向不同。',10),('05','世界的点心传统','从米豆椰甜点，到烤炸包馅。',24),('06','原料与口感','先理解材料，再辨认糯、酥、松与滑。',2)]
home+='<section class="section"><div class="section-head"><div><span class="eyebrow">从熟悉的一类进入</span><h2>选择一条阅读路线</h2></div><a class="text-link" href="contents.html">查看完整目录 →</a></div><div class="categories">'
for num,title,desc,ch in category_data:
 url=next(e['url'] for e in entries if e.get('id')==f'ch{ch:02d}')
 home+=f'<a class="category" href="{url}"><span class="number">{num}</span><h3>{title}</h3><p>{desc}</p><span class="arrow" aria-hidden="true">↗</span></a>'
home+='</div></section><section class="section"><div class="section-head"><div><span class="eyebrow">先看外形，再认识里面</span><h2>典型点心，先看一眼</h2><p>成形、切面与皮馅关系，让不同品种的特点更清楚。</p></div><a class="text-link" href="atlas.html">浏览全部 '+str(len(cards))+' 幅图片 →</a></div><div class="food-grid">'
home+=''.join(food_card(next(c for c in cards if c['id']==key)) for key in config['home_ids'])+'</div><p class="note">本区插图均为AI教学示意。各章同时保留有出处的实物照片与知识来源。</p></section>'
home+='<section class="section"><div class="section-head"><div><span class="eyebrow">全书图片，一处浏览</span><h2>看实物，也看懂工艺</h2><p>精选之外，完整图鉴收录每一幅随书图片，并保留图片性质与来源。</p></div><a class="text-link" href="atlas.html">查看全部 '+str(len(cards))+' 幅 →</a></div><div class="image-library">'
for kind,description in [('实物照片','观察真实外形、切面与制作现场，查看作者和使用许可。'),('AI教学示意','用统一画风比较外观与皮馅关系，结合原文理解示意边界。'),('原创工艺图','沿着原料、工艺与口感的关系，理解结构与观察方法。')]:
 count=sum(c['kind']==kind for c in cards)
 home+=f'<a class="library-entry" href="atlas.html?kind={kind}"><strong>{count}<small> 幅{kind}</small></strong><p>{description}</p><span class="text-link">按此类型浏览 →</span></a>'
home+='</div><div class="food-grid">'
for key in ('real-cn-tangyuan','rice-comparison','07-skins'):
 home+=food_card(next(c for c in cards if c['id']==key))
home+='</div></section>'
home+='<section class="scene-entry"><h2>今天，想从哪一餐开始？</h2><p>早餐、家常、茶点、节令与夜宵，沿着熟悉的场景找品种。</p><a class="button" href="appendices/scene-guide.html">按用餐场景阅读 →</a></section>'
home+='<section class="section"><div class="routes"><div><span class="eyebrow">按你的兴趣阅读</span><h2>认一个品种，<br>也看懂一种做法。</h2><p>可以从头逐章读，也可以沿着品种、工艺或地方传统进入。每一章都保留图注与资料，方便继续比较。</p></div><div class="route-list">'
for num,title,desc,url in [('01','想认品种','用图鉴寻找外形与名称，再进入对应图片与讲解。','atlas.html'),('02','想理解口感','从粉、水、油、糖、蛋与馅的作用开始。','chapters/02-materials.html'),('03','想系统读完','沿完整目录，走过基础、地区、工艺与日常应用。','contents.html')]:home+=f'<a href="{url}"><span class="route-num">{num}</span><span><strong>{title}</strong><small>{desc}</small></span><span aria-hidden="true">→</span></a>'
home+='</div></div></section></main>';page('index.html','首页',home,'home')
contents='<main id="reading" class="wrap"><div class="page-intro"><span class="eyebrow">由浅入深 · 逐章阅读</span><h1>完整目录</h1><p>先建立观察方法，再认识地区传统与工艺家族。也可从感兴趣的一章开始。</p></div><div class="contents-groups">';groups={}
for c in book['chapters']:groups.setdefault(c['part'],[]).append(c)
for title,chapters in groups.items():
 contents+=f'<section class="contents-group"><h2>{escape(title)}</h2><ol>'
 for c in chapters:contents+=f'<li><a href="{by_source[c["source"]]["url"]}"><span class="num">{c["id"][2:]}</span><span>{escape(c["title"])}</span></a></li>'
 contents+='</ol></section>'
contents+='<section class="contents-group"><h2>索引、词汇与来源</h2><ol>'
for c in entries[len(book['chapters']):]:contents+=f'<li><a href="{c["url"]}">{escape(c["title"])}</a></li>'
contents+='</ol></section></div><section class="index-only-note"><h2 class="section-title">下载书稿</h2><p><a href="https://github.com/'+repo+'/archive/refs/heads/main.zip">下载完整书稿与图片（ZIP）</a></p>'
if args.epub:
 import zipfile
 assert args.epub.is_file()
 with zipfile.ZipFile(args.epub) as z:assert z.read('mimetype')==b'application/epub+zip' and not z.testzip()
 (OUT/'downloads').mkdir();shutil.copy2(args.epub,OUT/'downloads/book.epub');contents+='<p><a download href="downloads/book.epub">下载EPUB电子书</a></p>'
contents+='</section></main>';page('contents.html','完整目录',contents,'contents')
atlas='<main id="reading" class="wrap"><div class="page-intro"><span class="eyebrow">一眼认识 · 就近学习</span><h1>点心图鉴</h1><p>收录全书实物照片、AI教学示意与原创工艺图。点击图卡可定位到原文图片和图注；实物照片保留作者及许可，AI示意不作为真实配方或历史证据。</p></div><div class="tools"><div class="filters" aria-label="点心类别">'
for group in ('全部','中式','西式','世界','基础与应用'):atlas+=f'<button type="button" data-filter="{group}" aria-pressed="{str(group=="全部").lower()}">{group}</button>'
atlas+='</div><label class="image-kind-filter">图片类型 <select id="atlas-kind"><option value="全部">全部类型</option><option>实物照片</option><option>AI教学示意</option><option>原创工艺图</option></select></label><label class="search"><span>查找点心</span><input id="atlas-search" type="search" placeholder="搜索品名、原料或工艺" autocomplete="off"></label></div><p id="result-count" class="result-count" aria-live="polite">共 '+str(len(cards))+' 幅随书图片</p><div class="food-grid" id="atlas-grid">'+''.join(food_card(c) for c in cards[:12])+'</div><nav class="pagination" aria-label="图鉴分页"><button id="previous-page" type="button" disabled>上一页</button><span id="page-info">1 / '+str((len(cards)+11)//12)+'</span><button id="next-page" type="button">下一页</button></nav><noscript><p>以下为全部图片，支持直接进入原文：</p><ul>'+''.join(f'<li><a href="{c["href"]}">{escape(c["title"])}（{c["kind"]}）</a></li>' for c in cards)+'</ul></noscript></main>'
data=json.dumps(cards,ensure_ascii=False).replace('</','<\\/');page('atlas.html','点心图鉴',atlas,'atlas',f'<script id="atlas-data" type="application/json">{data}</script><script src="atlas.js" defer></script>')
def book_nav(current,prefix):return ''.join(f'<a href="{prefix}{e["url"]}"'+(' aria-current="page"' if e['source']==current else '')+f'>{(e.get("id","")[2:]+"　") if e.get("id","").startswith("ch") else ""}{escape(e["title"])}</a>' for e in entries)
for index,e in enumerate(entries):
 source=Path(e['source']);prefix='../'*(len(source.parts)-1);body=markdown.markdown(e['text'],extensions=['extra','toc','sane_lists'],extension_configs={'extra':{'footnotes':{'BACKLINK_TEXT':'返回正文','BACKLINK_TITLE':'返回注释%d的引用处'}}});body=re.sub(r'<!--.*?-->','',body,flags=re.S)
 body=re.sub(r'href="([^"?#]+)\.md([?#][^"]*)?"',lambda m:'href="'+m[1]+'.html'+(m[2] or '')+'"',body);section=[0]
 def heading(m):section[0]+=1;return f'<h2 id="section-{section[0]}">{m[1]}</h2>'
 body=re.sub(r'<h2(?: [^>]*)?>(.*?)</h2>',heading,body,flags=re.S)
 def image(m):
  a=dict(re.findall(r'([\w-]+)="([^"]*)"',m[0]));name=Path(unquote(urlsplit(a['src']).path)).name;return img_tag(name,a.get('alt','点心教学配图'),prefix).replace('<img ',f'<img id="{image_anchor(name)}" ',1)
 body=re.sub(r'<img\b[^>]*>',image,body)
 body=re.sub(r'<p>(<img\b[^>]*>)</p>\s*<p>(图.*?)</p>',lambda m:f'<figure>{m[1]}<figcaption>{m[2]}</figcaption></figure>',body,flags=re.S)
 body=re.sub(r'<p>((?:实物照片：|AI生成示意：).*?)</p>',r'<p class="image-credit">\1</p>',body,flags=re.S);body=body.replace('<table>','<div class="table-wrap"><table>').replace('</table>','</table></div>')
 if e['notes'].order:
  body=re.sub(r'<div class="footnote">(.*?)</div>',lambda m:'<section class="footnotes" id="chapter-notes" aria-labelledby="chapter-notes-title"><h2 id="chapter-notes-title">本章注释</h2>'+m[1].replace('<hr />','')+'</section>',body,flags=re.S)
  body=re.sub(r'<a class="footnote-ref"', '<a role="doc-noteref" class="footnote-ref"',body)
  body=re.sub(r'<a class="footnote-backref"', '<a role="doc-backlink" class="footnote-backref"',body)
 toc='<details class="local-toc"><summary>本章内容</summary><ul>'+''.join(f'<li><a href="#section-{i+1}">{escape(title)}</a></li>' for i,title in enumerate(e['headings']))+('<li><a href="#chapter-notes">本章注释（'+str(len(e['notes'].order))+'）</a></li>' if e['notes'].order else '')+'</ul></details>';nav='<nav class="chapter-nav" aria-label="章节导航">'
 for dest,label in ((index-1,'上一章'),(index+1,'下一章')):
  if 0<=dest<len(entries):target=entries[dest];nav+=f'<a href="{prefix}{target["url"]}"><small>{label}</small>{escape(target["title"])}</a>'
  else:nav+='<span></span>'
 nav+='</nav>';sidebar=book_nav(e['source'],prefix)
 main=f'<main id="reading" class="reader-layout"><aside class="book-sidebar" aria-label="全书目录"><h2>全书目录</h2>{sidebar}</aside><article class="reader"><details class="mobile-book-nav"><summary>打开全书目录</summary>{sidebar}</details><div class="chapter-label">{escape(e.get("part","索引与资料"))}</div>{toc}{body}{nav}</article></main>';page(e['url'],e['title'],main,'contents')
class Check(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set();self.h1=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get('id'):
   assert a['id'] not in self.ids,('Duplicate HTML id',a['id'])
   self.ids.add(a['id'])
  if tag=='h1':self.h1+=1
  for key in ('href','src'):
   if a.get(key):self.links.append(a[key])
  if a.get('srcset'):self.links.extend(x.strip().split()[0] for x in a['srcset'].split(','))
parsed={}
for f in OUT.rglob('*.html'):
 c=Check();c.feed(f.read_text());assert c.h1==1,(f,'Expected one page title');parsed[f.resolve()]=c
for f,c in parsed.items():
 for value in c.links:
  u=urlsplit(value)
  if u.scheme or u.netloc:continue
  target=(f.parent/unquote(u.path)).resolve() if u.path else f;assert target.is_relative_to(OUT) and target.is_file(),('Broken resource',f,value)
  if u.fragment and target in parsed:assert unquote(u.fragment) in parsed[target].ids,('Broken section',f,value)
assert not any('editorial/' in f.read_text() for f in OUT.rglob('*.html'))
summary={'pages':len(parsed),'chapters':len(book['chapters']),'book_images':len(images),'atlas_cards':len(cards),'atlas_image_coverage':len(cards)/len(images),'atlas_kind_counts':{kind:sum(c['kind']==kind for c in cards) for kind in sorted({c['kind'] for c in cards})},'broken_resources':0,'footnotes':sum(len(e['notes'].order) for e in entries),'independent_home':True,'paginated_atlas':True,'ebook_export_ran':False,'optimized_image_bytes':sum(p.stat().st_size for p in image_dir.iterdir())};(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False))
