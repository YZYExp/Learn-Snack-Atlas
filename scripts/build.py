#!/usr/bin/env python3
"""Build an EPUB 3 reading edition; validate local references. Python standard library only."""
from pathlib import Path
from html import escape
import re,json,zipfile,uuid,datetime,xml.etree.ElementTree as ET
from urllib.parse import urlsplit,unquote
from notes import parse_notes,EpubNotes
R=Path(__file__).resolve().parents[1];B=R/'build';B.mkdir(exist_ok=True)
meta=json.loads((R/'book.json').read_text())
chapters=[R/c['source'] for c in meta['chapters']]
extras=[R/c['source'] for c in meta['appendices']]
# Collect all reader-facing source links into a derived bibliography.
refs={}
for p in chapters+extras:
 for name,url in re.findall(r'(?<!!)\[([^\]]+)\]\((https?://[^\s)]+)\)',p.read_text()):refs.setdefault(url,name)
bib='# 资料索引\n\n具体事实的来源已放在正文相应位置。以下按书内首次出现顺序汇集链接，便于复查。部分专业资料的全文可能需要订阅，机构网站也可能调整路径。图像分为公开许可实物照片、AI教学示意和原创关系图；实物照片在图旁与图片来源附录分别标注作者、来源和许可。\n\n'
for i,(url,name) in enumerate(refs.items(),1):bib+=f'{i}. [{name}]({url})\n\n'
(R/'references/reading-sources.md').write_text(bib)
files=chapters+extras+[R/'references/reading-sources.md']
names={p.resolve():f'text/{i:02d}-{p.stem}.xhtml' for i,p in enumerate(files,1)}
errors=[]
for p in files:
 for label,link in re.findall(r'!?\[([^\]]*)\]\(([^)]+)\)',p.read_text()):
  if link.startswith(('https://','http://','#')):continue
  if not (p.parent/link.split('#')[0]).exists():errors.append(f'{p.name}: {link}')
assert not errors,errors
# The source uses headings, paragraphs, simple lists, tables, images and links.
def inline(s,p,notes=None):
 tokens=[]
 def item(m):
  is_image,label,target=m.groups()
  if is_image:
   q=(p.parent/target).resolve()
   value=f'<img src="../assets/images/{escape(q.name,quote=True)}" alt="{escape(label,quote=True)}" />'
  else:
   if not target.startswith(('https://','http://','#')):
    path,sep,anchor=target.partition('#');q=(p.parent/path).resolve()
    if q in names:target=Path(names[q]).name+(sep+anchor if sep else '')
   value=f'<a href="{escape(target,quote=True)}">{escape(label)}</a>'
  tokens.append(value);return f'@@TOKEN{len(tokens)-1}@@'
 s=re.sub(r'(!?)\[([^\]]*)\]\(([^)]+)\)',item,s)
 if notes:
  def reference(m):
   tokens.append(notes.reference(m[1]));return f'@@TOKEN{len(tokens)-1}@@'
  s=re.sub(r'\[\^([^\]\n]+)\]',reference,s)
 s=escape(s)
 s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
 s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
 for i,t in enumerate(tokens):s=s.replace(f'@@TOKEN{i}@@',t)
 return s

def markdown(s,p):
 parsed_notes=parse_notes(s,str(p.relative_to(R)));notes=EpubNotes(parsed_notes)
 render=lambda value:inline(value,p,notes)
 lines=re.sub(r'<!--.*?-->','',parsed_notes.body,flags=re.S).splitlines();out=[];i=0
 while i<len(lines):
  line=lines[i].strip()
  if not line:i+=1;continue
  h=re.match(r'^(#{1,4})\s+(.*)',line)
  if h:
   n=len(h[1]);out.append(f'<h{n}>{render(h[2])}</h{n}>');i+=1;continue
  if line.startswith('|') and i+1<len(lines) and re.match(r'^\|[\s:|\-]+\|$',lines[i+1].strip()):
   rows=[line]+lines[i+2:];table=[line];i+=2
   while i<len(lines) and lines[i].strip().startswith('|'):table.append(lines[i].strip());i+=1
   out.append('<table>')
   for j,row in enumerate(table):
    tag='th' if j==0 else 'td';out.append('<tr>'+''.join(f'<{tag}>{render(v.strip())}</{tag}>' for v in row.strip('|').split('|'))+'</tr>')
   out.append('</table>');continue
  if re.match(r'^(?:[-*]|\d+\.)\s+',line):
   out.append('<p class="list-item">'+render(line)+'</p>');i+=1;continue
  para=[line];i+=1
  while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|')):para.append(lines[i].strip());i+=1
  value=render(' '.join(para))
  cl='figure' if '<img ' in value else 'caption' if (re.match(r'^图\d',para[0]) or para[0].startswith(('实物照片：','AI生成示意：'))) else ''
  out.append(f'<p class="{cl}">{value}</p>')
 out.append(notes.render(lambda value:inline(value,p)))
 return '\n'.join(out)
css='''body{font-family:serif;line-height:1.85;color:#303a39;margin:5%;}h1{font-size:1.6em;line-height:1.4;color:#85482e;page-break-before:always;}h2{font-size:1.18em;line-height:1.5;margin-top:1.7em;}p{text-align:justify;}a{color:#815134;overflow-wrap:anywhere;}img{max-width:100%;height:auto;}p.figure{text-align:center;break-inside:avoid;}p.caption{font-size:.8em;color:#666;line-height:1.6;margin-bottom:2em;}table{border-collapse:collapse;width:100%;font-size:.78em;table-layout:fixed;line-height:1.55;}th,td{border:1px solid #cfc9bc;padding:.5em;overflow-wrap:anywhere;vertical-align:top;}th{background:#eee9dd;}code{font-family:monospace;} .subtitle{color:#8b694d;}'''
css+=' .footnotes{border-top:1px solid #cfc9bc;margin-top:2em;font-size:.85em}.footnotes h2{font-size:1.1em}.footnotes p{text-align:left}sup{line-height:0}.note-number{font-weight:bold}'
ns='http://www.w3.org/1999/xhtml'
def page(title,body):return f'<?xml version="1.0" encoding="utf-8"?><html xmlns="{ns}" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN"><head><title>{escape(title)}</title><link rel="stylesheet" type="text/css" href="../style.css"/></head><body>{body}</body></html>'
image_index=json.loads((R/'editorial/image-index.json').read_text())
image_files=sorted({(R/x['file']).resolve() for x in image_index})
image_counts={kind:sum(x.get('kind')==kind for x in image_index) for kind in ['licensed photograph','AI-generated teaching illustration','original diagram']}
entries={'OEBPS/style.css':css}
titles=[]
for p in files:
 title=p.read_text().splitlines()[0].lstrip('# ');href=names[p.resolve()];titles.append((title,href))
 entries['OEBPS/'+href]=page(title,markdown(p.read_text(),p))
entries['OEBPS/text/title.xhtml']=page(meta['title'],f'<h1>{meta["title"]}</h1><h2>{meta["subtitle"]}</h2><p>{meta["edition"]}</p><p>{meta["description"]}</p><p>{len(chapters)}章正文、点心索引、工艺词汇与就近资料链接。配图包含公开许可实物照片、AI教学示意和原创关系图；不以生成图作历史或工艺事实的证据。</p>')
nav=''.join(f'<li><a href="{href}">{escape(t)}</a></li>' for t,href in titles)
entries['OEBPS/nav.xhtml']=f'<?xml version="1.0" encoding="utf-8"?><html xmlns="{ns}" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN"><head><title>目录</title></head><body><nav epub:type="toc" id="toc"><h1>目录</h1><ol>{nav}</ol></nav></body></html>'
manifest=['<item id="css" href="style.css" media-type="text/css"/>','<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>','<item id="title" href="text/title.xhtml" media-type="application/xhtml+xml"/>'];spine=['<itemref idref="title"/>','<itemref idref="nav"/>']
for i,(title,href) in enumerate(titles):manifest.append(f'<item id="c{i}" href="{href}" media-type="application/xhtml+xml"/>');spine.append(f'<itemref idref="c{i}"/>')
for i,p in enumerate(image_files):
 href='assets/images/'+p.name;entries['OEBPS/'+href]=p.read_bytes();mime='image/png' if p.suffix.lower()=='.png' else 'image/jpeg';manifest.append(f'<item id="im{i}" href="{href}" media-type="{mime}"/>')
uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'book:dimsum-atlas:2026-10-25'))
entries['OEBPS/content.opf']=f'''<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">urn:uuid:{uid}</dc:identifier><dc:title>{meta['title']}：{meta['subtitle']}</dc:title><dc:language>zh-CN</dc:language><dc:description>{meta['description']}</dc:description><meta property="dcterms:modified">{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}</meta></metadata><manifest>{''.join(manifest)}</manifest><spine>{''.join(spine)}</spine></package>'''
entries['META-INF/container.xml']='<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
out=B/'Dimsum-Atlas.epub'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
 for name,data in entries.items():
  if name.endswith(('.xml','.xhtml','.opf')):ET.fromstring(data)
  z.writestr(name,data)
with zipfile.ZipFile(out) as z:
 assert z.infolist()[0].filename=='mimetype' and z.infolist()[0].compress_type==0
 assert not z.testzip()
 from posixpath import normpath,dirname,join
 documents={name:ET.fromstring(z.read(name)) for name in z.namelist() if name.endswith('.xhtml')}
 identifiers={}
 for name,tree in documents.items():
  ids=[elem.get('id') for elem in tree.iter() if elem.get('id')]
  assert len(ids)==len(set(ids)),('Duplicate XHTML id',name)
  identifiers[name]=set(ids)
 for name,tree in documents.items():
  for elem in tree.iter():
   for attr in ('href','src'):
    value=elem.get(attr)
    if not value:continue
    url=urlsplit(value)
    if url.scheme or url.netloc:continue
    target=normpath(join(dirname(name),unquote(url.path))) if url.path else name
    assert target in z.namelist(),(name,value,target)
    if url.fragment and target in identifiers:
     assert unquote(url.fragment) in identifiers[target],('Broken EPUB fragment',name,value)
# README is generated from canonical chapter manifest.
readme=f'# {meta["title"]}\n\n## {meta["subtitle"]}\n\n{meta["description"]}\n\n{meta["edition"]}。{len(chapters)}章知识读本；甜咸兼收，以原料、工艺、口感和生活场景解释代表品种。不是覆盖世界全部点心的穷尽目录，也不是逐项实作配方集。\n\n'
part=None
for c in meta['chapters']:
 if c['part']!=part:part=c['part'];readme+=f'\n### {part}\n\n'
 readme+=f'- [{c["id"][2:]}　{c["title"]}]({c["source"]})\n'
readme+='\n### 附录\n\n'+''.join(f'- [{p.read_text().splitlines()[0].lstrip("# ")}]({p.relative_to(R)})\n' for p in extras)
readme+=f'\n- [汇总资料索引](references/reading-sources.md)\n\n## 构建与修订\n\nPython 3标准库即可构建EPUB并校验本地资源：\n\n```bash\npython3 scripts/build.py\n```\n\n输出：`build/Dimsum-Atlas.epub`。原始分章Markdown与图片为唯一内容来源。网站从`book.json`与分章内容构建，发布方式见下文。重新绘制关系图需要Pillow及中文字体；在`scripts/draw_diagrams.py`中调整字体路径后运行。电子书构建不依赖Pillow。\n\n图像：{image_counts["licensed photograph"]}张公开许可实物照片、{image_counts["AI-generated teaching illustration"]}幅AI生成外观教学图、{image_counts["original diagram"]}幅原创关系图，总计{len(image_files)}幅；图注逐图说明类型与用途。图像清单在`editorial/image-index.json`，编辑资料不编入电子书。\n'
# Preserve site documentation maintained with the homepage.
existing=(R/'README.md').read_text() if (R/'README.md').exists() else ''
if '\n## 网页阅读与发布' in existing:
 readme+=existing[existing.index('\n## 网页阅读与发布'):]
(R/'README.md').write_text(readme)
report={'chapters':len(chapters),'appendices':len(extras),'illustrations':len(image_files),'image_kind_counts':image_counts,'sources':len(refs),'footnotes':sum(len(parse_notes(p.read_text(),str(p)).order) for p in files),'body_han_characters':sum(len(re.findall(r'[\u4e00-\u9fff]',p.read_text())) for p in chapters),'epub_bytes':out.stat().st_size,'checks':['chapter manifest and local links','EPUB XML well-formedness','EPUB internal href/src and fragment resolution','ZIP integrity and first mimetype entry']}
(B/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
