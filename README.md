# 点心之间

## 中西传统与新式糕点小吃图解

从原料、工艺和口感出发，认识甜咸点心的地方传统与现代变化。

品类与场景扩充版 · 2026-10-25。24章知识读本；甜咸兼收，以原料、工艺、口感和生活场景解释代表品种。不是覆盖世界全部点心的穷尽目录，也不是逐项实作配方集。


### 基础观察

- [01　点心的边界：从一口食物读懂一套饮食文化](chapters/01-reading.md)
- [02　原料的工作：粉、水、油、糖、蛋与馅](chapters/02-materials.md)
- [03　从生坯到成品：加热、膨胀与定形](chapters/03-process.md)
- [04　口感的地图：糯、韧、酥、脆、松、滑](chapters/04-texture.md)

### 中国传统与地方小吃

- [05　米与杂粮：糕、团、粿的不同骨架](chapters/05-rice.md)
- [06　中式酥点与烤点：从油脂分层到蛋挞](chapters/06-chinese-pastry.md)
- [07　包、饺与蒸煎咸点：外皮怎样照顾馅心](chapters/07-steamed-savory.md)
- [08　地区茶点与街头小吃：从一张餐桌读到一座城市](chapters/08-regional-snacks.md)
- [09　节令、礼俗与传播：点心怎样成为共同记忆](chapters/09-festivals.md)

### 西式工艺家族

- [10　从小餐包到布里欧修：发酵面团的点心生活](chapters/10-bread.md)
- [11　蛋糕里的空气：从海绵到芝士](chapters/11-cakes.md)
- [12　层层展开与一腔空心：起酥和泡芙](chapters/12-laminated.md)
- [13　酥底与小饼：塔、派、曲奇和饼干](chapters/13-tarts-cookies.md)
- [14　凝固、充气与冻结：冷甜点的几条路线](chapters/14-cold-sweets.md)

### 世界传统与当代生活

- [15　东亚与东南亚：米、豆、椰与季节](chapters/15-east-asia.md)
- [16　更广阔的点心地图：薄片、糖浆与包馅](chapters/16-world-snacks.md)
- [17　新式点心：改变口味，也改变结构](chapters/17-fusion.md)
- [18　把知识带到餐桌：品尝、选购与保存](chapters/18-tasting.md)

### 日常场景与品种专题

- [19　饺子家族：从一盘家常水饺到一口茶楼粉粿](chapters/19-dumplings.md)
- [20　馄饨、云吞与抄手：一张薄皮怎样进入一碗汤](chapters/20-wontons.md)
- [21　汤圆、元宵与圆子：一碗米食的甜咸世界](chapters/21-rice-balls.md)
- [22　早餐面点：从一笼馒头到一张现摊的饼](chapters/22-breakfast.md)
- [23　街头与夜市：卷、炸、夹与一份现吃的小食](chapters/23-street-snacks.md)
- [24　世界咸点：从一盘水煮饺到手拿烤馅饼](chapters/24-world-savory.md)

### 附录

- [中式点心代表索引](appendices/chinese-index.md)
- [附录　工艺词汇与阅读路线](appendices/glossary.md)
- [附录　西式及其他地区点心检索](appendices/world-index.md)
- [图片来源与使用许可](appendices/photo-credits.md)
- [按场景找点心：从一顿早餐到一份夜点](appendices/scene-guide.md)

- [汇总资料索引](references/reading-sources.md)

## 构建与修订

Python 3标准库即可构建EPUB并校验本地资源：

```bash
python3 scripts/build.py
```

输出：`build/Dimsum-Atlas.epub`。原始分章Markdown与图片为唯一内容来源。网站从`book.json`与分章内容构建，发布方式见下文。重新绘制关系图需要Pillow及中文字体；在`scripts/draw_diagrams.py`中调整字体路径后运行。电子书构建不依赖Pillow。

图像：27张公开许可实物照片、55幅AI生成外观教学图、11幅原创关系图，总计93幅；图注逐图说明类型与用途。图像清单在`editorial/image-index.json`，编辑资料不编入电子书。

## 网页阅读与发布

GitHub Pages 的 Source 设为 GitHub Actions 后，推送 main 自动构建并发布。PR 仅构建与检查，不部署。

```bash
python -m pip install -r requirements-site.txt
python scripts/build_site.py
python -m http.server 8000 --directory _site
```

构建检查所有站内链接和配图路径。输出在 `_site/`，不执行 EPUB、PDF、图像生成或外部素材下载。目录、逐章导航、附录和原有来源署名从现有稿件生成。



### 独立首页与点心图鉴

首页 `index.html` 展示视觉导览、六类入口与阅读路线；完整目录移至 `contents.html`；`atlas.html` 提供按中式、西式、世界分类的图鉴、品名搜索及每页12项分页。所有图卡链接至同一份分章书稿的对应小节。

网页版按比例生成480/1200像素WebP与懒加载，保留原始图源。PR只构建校验，并提供保留14天的 `snack-atlas-site-preview` 预览包（下载需GitHub登录）；合并main后才部署正式站点。网页构建独立于EPUB导出，只有显式传入 `--epub` 才附带已经验证的电子书文件。

### 品类与场景扩充

新增第19—24章，系统讲解饺子、馄饨云吞抄手、汤圆圆子、早餐面点、街头夜市及世界咸点。新增18幅已复审示意，图鉴共40卡；[场景导览](appendices/scene-guide.md)帮助从早餐、家常、茶点、节令和夜宵进入正文。

更广范围的20个家族、230条候选检索记录与A/B/C批次见[扩充规划](editorial/expansion/scope-and-roadmap.md)。候选包含别名、地方分支和边界项目，不代表230种独立食品或全部完成；本PR交付A批，后续缺图与待扩写仍如实记录。
