#!/usr/bin/env python3
"""Build the reading site from book.json without ebook toolchains."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, os, re, shutil
import markdown

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
book = json.loads((ROOT / 'book.json').read_text())
repo = os.environ.get('GITHUB_REPOSITORY', 'YZYExp/' + ('Learn-Body' if '人体' in book['title'] else 'Learn-Snack-Atlas'))
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(ROOT / 'assets', OUT / 'assets')
entries = []
for key in ('frontmatter', 'chapters', 'appendices', 'backmatter'):
    for item in book.get(key, []):
        if isinstance(item, str):
            title = (ROOT / item).read_text().splitlines()[0].lstrip('# ').strip()
            item = {'source': item, 'title': title}
        entries.append(item)
public = {Path(e['source']) for e in entries}
public.update((p.relative_to(ROOT) for p in (ROOT / 'references').glob('*.md')))
public.update((p.relative_to(ROOT) for p in ROOT.glob('LICENSE*') if p.suffix == '.md'))
for path in sorted(public):
    if not any(e['source'] == str(path) for e in entries):
        entries.append({'source': str(path), 'title': (ROOT / path).read_text().splitlines()[0].lstrip('# ').strip()})
css = '''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#faf8f3;color:#253336;font:18px/1.85 system-ui,-apple-system,"Noto Sans CJK SC",sans-serif}a{color:#236765;text-underline-offset:4px}header{background:#173f40;color:white;padding:24px max(5vw,20px)}header a{color:white;text-decoration:none}main{max-width:900px;margin:auto;padding:36px 24px 80px}h1{font-size:clamp(1.9rem,5vw,3rem);line-height:1.4}h2,h3{line-height:1.5;margin-top:2em}img{display:block;max-width:100%;height:auto;margin:30px auto;background:white;border-radius:8px}table{display:block;overflow-x:auto;border-collapse:collapse;font-size:.9em}td,th{padding:10px;border:1px solid #cbd3cd}blockquote{margin-left:0;padding:12px 24px;border-left:4px solid #507f71;background:#eff1e9}nav{display:flex;gap:18px;flex-wrap:wrap;padding:20px 0;border-top:1px solid #ccd4cb;margin-top:40px}footer{font-size:.85em;color:#61706b}li{margin:8px 0}.toc{padding:18px 26px;background:#edf1e9;border-radius:12px}.toc li{margin:12px 0}pre{overflow:auto;padding:16px;background:#eceee8}code{overflow-wrap:anywhere}a:focus-visible{outline:3px solid #d48b31} .skip{position:absolute;left:-9999px}.skip:focus{left:10px;top:10px;background:white;color:black} @media(max-width:600px){body{font-size:17px}main{padding:24px 18px}header{padding:18px}h1{font-size:1.9rem}}'''
(OUT / 'style.css').write_text(css)
(OUT / '.nojekyll').touch()
def page(path, title, body, navigation=''):
    prefix = '../' * (len(path.parts) - 1)
    doc = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · {escape(book['title'])}</title><link rel="stylesheet" href="{prefix}style.css"></head><body><a class="skip" href="#reading">跳至正文</a><header><a href="{prefix}index.html">{escape(book['title'])}</a></header><main id="reading">{body}{navigation}<footer><p>分章 Markdown 与随书配图构建。来源、署名和许可保留于正文及附录。</p><a href="https://github.com/{repo}">查看源工程</a> · <a href="{prefix}index.html">返回全书目录</a></footer></main></body></html>'''
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc)

def link(item):
    return str(Path(item['source']).with_suffix('.html'))
for i, item in enumerate(entries):
    source = Path(item['source'])
    body = markdown.markdown((ROOT / source).read_text(), extensions=['extra', 'toc', 'sane_lists'])
    body = re.sub(r'href="([^"?#]+)\.md([?#][^"]*)?"', lambda m: 'href="' + m[1] + '.html' + (m[2] or '') + '"', body)
    body = body.replace('<img ', '<img loading="lazy" decoding="async" ')
    navigation = '<nav aria-label="章节导航">'
    for index, label in ((i - 1, '上一章'), (i + 1, '下一章')):
        if 0 <= index < len(entries):
            destination = os.path.relpath(link(entries[index]), str(source.parent))
            navigation += f'<a href="{destination}">{label}：{escape(entries[index]["title"])}</a>'
    page(source.with_suffix('.html'), item['title'], body, navigation + '</nav>')
body = f'<h1>{escape(book["title"])}</h1><p>{escape(book.get("subtitle", ""))}</p><p>{escape(book.get("description", ""))}</p><p>{escape(book.get("edition", ""))} · {len(book["chapters"])} 章</p><h2>逐章阅读</h2><ol class="toc">'
for item in entries:
    body += f'<li><a href="{link(item)}">{escape(item["title"])}</a></li>'
body += f'</ol><h2>下载与复用</h2><p><a href="https://github.com/{repo}/archive/refs/heads/main.zip">下载完整源工程（ZIP）</a>。电子书构建方法见仓库 README；网站部署不运行电子书工具链。</p>'
for file in (ROOT / 'build').glob('*.epub'):
    (OUT / 'downloads').mkdir(exist_ok=True)
    shutil.copy2(file, OUT / 'downloads' / file.name)
    body += f'<p><a download href="downloads/{file.name}">下载 EPUB</a></p>'
page(Path('index.html'), '全书目录', body)

class Check(HTMLParser):
    def __init__(self, source):
        super().__init__(); self.source = source
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key not in ('src', 'href') or not value: continue
            url = urlsplit(value)
            if url.scheme or url.netloc or not url.path: continue
            target = (self.source.parent / unquote(url.path)).resolve()
            if not target.is_file():
                raise ValueError(f'Broken local link: {self.source}: {value}')
for file in OUT.rglob('*.html'):
    Check(file).feed(file.read_text())
print(f'Built and checked {len(entries) + 1} pages; all local links and images exist.')
