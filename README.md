# 点心之间

## 中西传统与新式糕点小吃图解

从原料、工艺和口感出发，认识甜咸点心的地方传统与现代变化。

首版：2026-10-25。18章知识读本；甜咸兼收，以原料、工艺、口感和生活场景解释代表品种。不是覆盖世界全部点心的穷尽目录，也不是逐项实作配方集。


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

### 附录

- [中式点心代表索引](appendices/chinese-index.md)
- [附录　工艺词汇与阅读路线](appendices/glossary.md)
- [附录　西式及其他地区点心检索](appendices/world-index.md)

- [汇总资料索引](references/reading-sources.md)

## 构建与修订

Python 3标准库即可构建EPUB并校验本地资源：

```bash
python3 scripts/build.py
```

输出：`build/Dimsum-Atlas.epub`。原始分章Markdown与图片为唯一内容来源。未来网站可读取`book.json`，本版未创建或部署网站。重新绘制关系图需要Pillow及中文字体；在`scripts/draw_diagrams.py`中调整字体路径后运行。电子书构建不依赖Pillow。

图像：8幅AI生成外观教学图、11幅原创关系图；图注逐图说明用途。图像清单在`editorial/image-index.json`，编辑资料不编入电子书。
