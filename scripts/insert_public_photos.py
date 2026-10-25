from pathlib import Path
import json,re,urllib.parse,hashlib
R=Path(__file__).resolve().parents[1];E=R/'editorial'
rows=[]
for g in ['china','west','world']:
 rows += [x for x in json.loads((E/f'photo-verified-{g}.json').read_text()) if x.get('approved') and x.get('visual_checked')]
# Keep captions factual and readable; detailed uncertainty checks remain in the audit record.
short={
'real-cn-qingtuan':'塘栖拍摄的蒸熟青团。绿色外皮中可见植物碎片。',
'real-cn-turnip-cake':'香港家庭制作的整盘萝卜糕，尚未切片煎制；与本章前面的煎糕切面示意形成对照。',
'real-cn-suzhou-mooncake':'加拿大家庭制作的苏式咸馅月饼，品名依作者说明。切面可观察外皮与馅心的比例。',
'real-cn-mahua':'麻花实物。条状面坯扭结成小环，炸后呈金黄色。',
'real-cn-shumai':'香港家庭风格猪肉烧卖，名称依原图说明。开放顶部露出馅心，薄皮在外围形成褶皱。',
'real-cn-cheung-fun':'潮汕式肠粉在澳大利亚阿德莱德的一种店售实例，店家为Stonemill Rice Roll。图中可见薄片的折叠、卷裹与酱汁。',
'real-cn-tangyuan':'南瓜汤圆实例；红豆与黑芝麻馅的信息来自原图说明。前方匙上的切面呈现了皮与馅的关系。',
'real-cn-yuanxiao':'未煮元宵与滚制用馅块并置。左侧已经裹粉，右侧保留馅块形态。',
'real-cn-yuanxiao-basket':'滚制元宵用的笸箩与糯米粉，器具和材料身份依原图说明。可与前图的馅块、成品联系理解。',
'real-cn-two-zongzi':'粽子的叶包、系绳与解开状态。打开后仍可辨认米粒及包入其中的馅料块。',
'real-cn-dim-sum-table':'香港荃湾川龙端记的点心蒸笼。原图列明叉烧包、马拉糕和腊肠卷；黑白影像突出几种形态的并置。',
'real-cn-hk-egg-tarts':'两枚香港蛋挞实物。浅黄色蛋面与褐色挞壳形成对照；本图不区分挞皮配方。',
'real-cn-liangnong-cake':'余姚梁弄大糕的陈列实例，摄于余姚阳明古镇历史文化街区。方形糕体表面的字纹清楚可见。',
'real-cn-guangdong-niangao':'整块广东年糕，名称依原图说明。圆盘形糕体与完整表面展示了切片前的状态。',
'real-cn-baotou-ricecake':'包头餐厅拍摄的“米糕”，名称依原图说明。可见浅黄与白色两层，以及表面的酱汁和颗粒配料。',
'real-we-brioche':'巧克力豆布里欧修。金黄色长条面包上可见分散的深色配料。',
'real-we-pretzel':'家庭制作的普雷结面包。扭结形态、深褐色表皮与表面浅色颗粒共同构成辨认线索。',
'real-we-concha':'墨西哥concha贝壳面包。浅色甜酥皮覆盖面包主体，弯曲刻纹与烤后裂缝清楚可见。',
'real-we-puff-prep-03':'千层酥制作中的折叠面团块，近侧可见叠起的边缘。这是一张过程快照，未标示折叠次数。',
'real-we-choux-inside':'香草卡仕达馅泡芙切面。褐色薄壳围住浅黄色馅料，壳内空间已被填馅占据。',
'real-we-bavarois':'配草莓的巴伐利亚奶油（bavarois）。被挖去一口后，浅色内部与勺取痕迹清楚可见。',
'real-we-creme-caramel':'焦糖布丁实物。主体的缺口显露内部，表面及碗底的褐色焦糖液与浅色布丁形成对照。',
'real-we-croissant-section':'可颂真实横切面。弯曲的薄壁围出大小不一的孔洞，可与本章的分层原理联系观察。',
'real-we-chiffon-process':'戚风蛋糕制作记录中的一次混合：浅色液体表面有气泡，深色配料尚未拌散。',
'real-wo-songpyeon':'韩国年糕松饼（songpyeon）实物。白、粉、绿的外皮呈半月形；这里的“松饼”不指西式pancake。',
'real-wo-che':'越南Bình Long的chè trôi nước，名称依摄影者说明。一碗中组合了大圆团、条状配料与液体。',
'real-wo-gulab-jamun':'Gulab jamun实物外形。球形甜点呈较深的炸制色泽；具体乳原料配方见正文的实例说明。'
}
meta=json.loads((R/'book.json').read_text());chapter_paths={int(x['id'][2:]):R/x['source'] for x in meta['chapters']}
counts={};verified=[];credits=['# 图片来源与使用许可','本书区分实物照片、AI教学示意和原创关系图。实物照片按各自许可单独使用，作者与许可见图旁及下表；不将照片许可扩大为整本书的许可。照片的品名依据原作者说明与可见形态核对，配方、工艺参数及历史结论另由正文资料支持。','## 公开许可实物照片','这些照片仅进行等比例缩小和必要的显示方向处理，未裁切、修图或调色。个别照片采用Wikimedia提供的缩略版本；具体处理与原始文件身份保存在工程的审校记录中。']
for x in sorted(rows,key=lambda a:(a['chapter'],rows.index(a))):
 p=chapter_paths[x['chapter']];s=p.read_text();key=x['id'];marker=f'<!-- public-photo:{key} -->'
 already_present=marker in s
 assert (R/x['file']).exists(),x['file']
 assert hashlib.sha256((R/x['file']).read_bytes()).hexdigest()==x['sha256'],key
 assert x['author'] or not x.get('attribution_required')=='true',(key,'missing author')
 counts[x['chapter']]=counts.get(x['chapter'],0)+1;num=f'{x["chapter"]}-{counts[x["chapter"]]}'
 caption=f'图{num}　{short.get(key,x["caption"])}'
 url=x['source_page'].replace('(','%28').replace(')','%29')
 lic=x['license'];license_url=x.get('license_url')
 license_link=f'[{lic}]({license_url})' if license_url else lic+'（见原许可页）'
 credit=f'实物照片：{x["author"] or "原图列示作者"}；{license_link}。[原图与许可页]({url})。'
 block=f'\n\n{marker}\n\n![{caption}](../{x["file"]})\n\n{caption}\n\n{credit}\n'
 heading='## '+x['heading'];start=s.find(heading+'\n');assert start>=0,(key,heading)
 nexthead=s.find('\n## ',start+len(heading));idx=nexthead if nexthead>=0 else len(s)
 if not already_present:
  s=s[:idx].rstrip()+block+'\n'+s[idx:];p.write_text(s)
 x['caption']=caption;x['credit']=credit;x['figure_number']=num;x['primary_review']='Accepted after main-editor comparison of pixels with caption and source metadata.';verified.append(x)
 credits += [f'### 图{num}　{key}',short.get(key,x['caption']),f'作者：{x["author"] or "见原许可页"}。许可：{license_link}。',f'原始文件：[ {x["title"]} ]({url})。',f'书内位置：第{x["chapter"]:02d}章；仅等比缩小，未裁切或调色。']
credits += ['## 生成示意与原创关系图','AI生成图逐图标有“AI生成示意”，用于说明常见外观或对比，不充当实际店家产品、历史实物或精确工艺参数的证据。原创关系图表达本书的观察框架和常见工艺路线，非实测显微图。']
(R/'appendices/photo-credits.md').write_text('\n\n'.join(credits)+'\n')
(E/'public-photo-verified.json').write_text(json.dumps(verified,ensure_ascii=False,indent=2))
index=json.loads((E/'image-index.json').read_text());index=[x for x in index if x.get('kind')!='licensed photograph']
for x in verified:index.append({**x,'kind':'licensed photograph'})
(E/'image-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2))
meta['edition']='补图修订版 · 2026-10-25'
if not any(x['source']=='appendices/photo-credits.md' for x in meta['appendices']):meta['appendices'].append({'id':'a4','title':'图片来源与使用许可','source':'appendices/photo-credits.md','slug':'photo-credits'})
(R/'book.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print('inserted',len(verified),'licensed photographs')
