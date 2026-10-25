from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
art={
1:[('01-map','图1　同一件点心可以沿原料、工艺、结构、场景与变化分别观察。原创教学图。')],
2:[('02-roles','图2　原料按功能理解，比按风味名称替换更可靠。原创教学图。')],
3:[('03-routes','图3　四种常见膨胀路线可以叠加；不是所有点心都需要显著膨胀。原创教学图。')],
4:[('04-textures','图4　从初咬到放置后的变化，分阶段记录口感。原创教学图。')],
5:[('rice-comparison','图5　自上而下：致密米糕、多孔米发糕、煎萝卜糕。AI生成外观与切面示意，不能据图反推粉料比例或熟化参数。')],
6:[('06-layers','图6　分层与松碎是两种不同的结构安排。原创关系示意，层厚与颗粒作了夸张，不表示显微尺度。')],
7:[('07-skins','图7a　先辨外皮路线，再比较形状与馅心。原创教学图。'),('steamed-comparison','图7b　自上而下：虾饺、肉包、广式烧卖、锅贴。AI生成常见外观示意；透明度、孔洞和皮厚并非统一标准。')],
8:[('08-scenes','图8　茶桌、街头、家庭与礼品影响点心的分量和组合。原创教学图。')],
9:[('festival-comparison','图9　自上而下：粽子、广式莲蓉蛋黄月饼、黑芝麻汤圆。AI生成当代代表外观示意，不作为历史复原或起源证据。')],
10:[('10-bread','图10　分开观察面包主体、夹馅与外层装配。原创教学图。')],
11:[('cakes-comparison','图11　自上而下：磅蛋糕、戚风切件、烤芝士蛋糕。AI生成组织外观示意，不表示实测气孔或含水差异。')],
12:[('pastry-comparison','图12　自上而下：中式分层酥点、可颂、填馅泡芙。AI生成切面示意。上方酥点仅作分层参照；可颂含发酵组织，泡芙主要形成壳内空腔。')],
13:[('tarts-comparison','图13　自上而下：曲奇皮蛋挞、葡式酥皮蛋挞、双皮苹果派、黄油酥饼。AI生成外观示意，具体店家与地区做法有差异。')],
14:[('cold-comparison','图14　自上而下：焦糖布丁、奶冻、巧克力慕斯、乳类冰淇淋与果味sorbet。AI生成外观示意；表面光滑不能证明使用同一凝固方式。')],
15:[('15-families','图15　相近原料可形成不同组织；图中给出常见路线，不概括所有地方配方。原创教学图。')],
16:[('world-comparison','图16　自上而下：草莓大福、samosa、baklava、烤empanada。AI生成代表外观示意。大福参见第15章，其余见本章；并列用于结构比较，不推断同源。')],
17:[('17-change','图17　配方替换需要考虑原料的工作，而非只匹配味道。原创教学图。')],
18:[('18-notes','图18　把观察、解释、偏好与安全信息分开记录。原创教学图。')]
}
chapters=[];records=[]
for f in sorted((R/'chapters').glob('*.md')):
 n=int(f.name[:2]);s=f.read_text();first=s.splitlines()[0]
 title=re.sub(r'^#\s*(?:第[一二三四五六七八九十]+章\s*|\d+\s*)','',first).strip()
 s=s.replace(first,f'# {n:02d}　{title}',1)
 if '<!-- teaching-art -->' not in s:
  parts=s.split('\n\n');block=['<!-- teaching-art -->']
  for id,caption in art[n]:
   block += [f'![{caption}](../assets/images/{id}.png)',caption]
   records.append({'id':id,'chapter':n,'file':f'assets/images/{id}.png','kind':'AI-generated teaching illustration' if 'comparison' in id else 'original diagram','caption':caption})
  parts[2:2]=block
  s='\n\n'.join(parts)+'\n'
 f.write_text(s)
 chapters.append({'id':f'ch{n:02d}','title':title,'source':str(f.relative_to(R)),'slug':f.stem,'part':('基础观察' if n<=4 else '中国传统与地方小吃' if n<=9 else '西式工艺家族' if n<=14 else '世界传统与当代生活')})
(R/'book.json').write_text(json.dumps({'title':'点心之间','subtitle':'中西传统与新式糕点小吃图解','language':'zh-CN','edition':'首版 · 2026-10-25','description':'从原料、工艺和口感出发，认识甜咸点心的地方传统与现代变化。','chapters':chapters},ensure_ascii=False,indent=2))
(R/'editorial/image-index.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
