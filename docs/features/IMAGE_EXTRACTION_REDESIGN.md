# 论文图片提取重设计方案

> **版本**: 1.4
> **创建日期**: 2026-03-21
> **最后更新**: 2026-03-22
> **状态**: 主体已完成，Algorithm 专用裁剪路径待实现（TODO）
> **优先级**: P1

---

## 一、问题描述

### 当前行为（有缺陷）

上传 PDF 或从 Auto-Scholar 导入论文后，结构化笔记中出现整页内容截图，而非单独的算法图、架构图、实验图等学术关键图片。

### 根因分析

**问题 1：整页渲染（最主要）**

`pdf_parser.py` 阶段 2 逻辑：对"有 Figure 文字引用但无嵌入光栅图"的页面（即矢量图页面），直接将**整页**渲染为一张 PNG 存入图库。这导致正文文字、页眉页脚、甚至两栏内容全部混入图片。

**问题 2：Caption 匹配无坐标感知**

`_find_image_caption` 用 `page.get_text()` 在整页文本中盲搜第一个 `Figure/Fig.` 行，不知道图片的空间位置，匹配结果不准确。

**问题 3：分类逻辑过于简单**

`_classify_image_type` 仅靠 caption 中是否含 `architecture/framework/performance/algorithm` 等关键词分类，大量图片因 caption 不含这些词而落入 `other`，无法有效区分。

**问题 4：`image_extractor.py` 放弃了语义过滤**

注释写明"不再依赖 caption 过滤，因为 caption 匹配不准确"——所有通过尺寸过滤的图片全部入库，等于没有内容过滤。

---

## 二、技术可行性

PyMuPDF（fitz）提供以下 API，当前**完全未被使用**：

| API | 能力 |
|-----|------|
| `page.search_for(text)` | 搜索文字在页面上的**精确坐标矩形**（Rect） |
| `page.get_image_rects(xref)` | 获取嵌入图片在页面上的**精确位置矩形** |
| `page.get_text("blocks")` | 返回文本块列表，含每块的坐标 `(x0, y0, x1, y1, text)` |
| `page.get_pixmap(matrix, clip=rect)` | **只渲染指定矩形区域**，而非整页 |

三个 API 组合，可实现：**无需 LLM、纯几何定位，精准裁剪 Figure/Table**。

---

## 三、核心设计思路

```
① 扫描页面，用 search_for() 定位所有 Caption 文字的坐标
         ↓
② 根据 Caption 类型确定图形区域方向
   Figure/Algorithm → Caption 在图下方 → 向上裁剪
   Table            → Caption 在图上方 → 向下裁剪
         ↓
③ 检测双栏布局，将裁剪范围限定在 Caption 所在的栏内
         ↓
④ get_pixmap(clip=裁剪矩形) 只渲染该区域，2× 分辨率
         ↓
⑤ 尺寸过滤 + 基于 Caption 文本精准分类 → 入库
```

---

## 四、Caption 识别规则

### 4.1 正则模式（扩展现有）

```python
CAPTION_PATTERN = re.compile(
    r'(Figure|Fig\.?|Table|Tab\.?|Algorithm|Alg\.?|Listing|Scheme)\s*\d+',
    re.IGNORECASE
)
```

覆盖范围：

| 模式 | 示例 |
|------|------|
| `Figure N` / `Fig. N` | Figure 1, Fig. 2 |
| `Table N` / `Tab. N` | Table 3, Tab. 4 |
| `Algorithm N` / `Alg. N` | Algorithm 1, Alg. 2 |
| `Listing N` | Listing 1（代码清单） |
| `Scheme N` | Scheme 1（化学/流程图） |

### 4.2 Caption 与图形的空间关系

| Caption 类型 | Caption 位置 | 搜索方向 |
|-------------|-------------|---------|
| Figure / Algorithm / Listing / Scheme | 图**下方** | 向 Caption **上方**搜索图形区域 |
| Table | 表**上方** | 向 Caption **下方**搜索表格区域 |

---

## 五、详细实现方案

### 5.1 改进阶段 1：嵌入式光栅图的 Caption 匹配

**现有问题**：`_find_image_caption` 不知道图片位置，在整页盲搜。

**改进**：用 `page.get_image_rects(xref)` 获取图片精确位置，在图片下方固定范围内搜索 Caption。

```python
def _find_caption_near_image(self, page: fitz.Page, xref: int,
                              margin: float = 80) -> str:
    """
    在图片下方 margin 点范围内搜索 Caption 文字。
    margin 默认 80 点（约 28mm），覆盖大多数单行/双行 caption。
    """
    rects = page.get_image_rects(xref)
    if not rects:
        # 降级：回退到原有整页盲搜
        return self._find_image_caption_legacy(page)

    img_rect = rects[0]
    # 搜索区域：图片下方 margin 范围
    search_rect = fitz.Rect(
        img_rect.x0, img_rect.y1,
        img_rect.x1, img_rect.y1 + margin
    )
    text_in_area = page.get_text(clip=search_rect)
    for line in text_in_area.split('\n'):
        if CAPTION_PATTERN.search(line):
            return line.strip()

    # 也尝试图片上方（部分论文 caption 在图上方）
    search_rect_above = fitz.Rect(
        img_rect.x0, img_rect.y0 - margin,
        img_rect.x1, img_rect.y0
    )
    text_above = page.get_text(clip=search_rect_above)
    for line in text_above.split('\n'):
        if CAPTION_PATTERN.search(line):
            return line.strip()

    return ""
```

### 5.2 重构阶段 2：精准裁剪替代整页渲染

**替换** `_render_figure_pages` 为 `_extract_figure_regions`，对每个页面：

#### Step 1：收集页面上所有 Caption 的坐标

```python
def _collect_caption_rects(self, page: fitz.Page) -> List[Dict]:
    """
    收集页面上所有匹配 CAPTION_PATTERN 的文字及其坐标。
    同一行文字可能被 search_for 返回多个矩形（跨行），取第一个即可。
    """
    caption_hits = []
    text = page.get_text()
    for line in text.split('\n'):
        line = line.strip()
        if not line or not CAPTION_PATTERN.search(line):
            continue
        rects = page.search_for(line)
        if not rects:
            continue
        is_table = bool(re.match(r'(Table|Tab\.?)\s*\d+', line, re.IGNORECASE))
        caption_hits.append({
            "text": line,
            "rect": rects[0],
            "is_table": is_table,
        })
    return caption_hits
```

#### Step 2：检测双栏布局

```python
def _detect_columns(self, page: fitz.Page) -> List[tuple]:
    """
    检测页面列布局，返回每列的 (x0, x1) 范围。
    单栏返回 [(页面左边距, 页面右边距)]
    双栏返回 [(左栏x0, 左栏x1), (右栏x0, 右栏x1)]
    """
    blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, block_type)
    if not blocks:
        return [(page.rect.x0 + 20, page.rect.x1 - 20)]

    page_mid = page.rect.width / 2
    left_count = sum(1 for b in blocks if b[6] == 0 and (b[0] + b[2]) / 2 < page_mid - 20)
    right_count = sum(1 for b in blocks if b[6] == 0 and (b[0] + b[2]) / 2 > page_mid + 20)

    if left_count > 3 and right_count > 3:
        # 双栏：找中间分隔线位置（取左侧文本块最大 x1 和右侧文本块最小 x0 的中点）
        left_x1s = [b[2] for b in blocks if b[6] == 0 and (b[0] + b[2]) / 2 < page_mid - 20]
        right_x0s = [b[0] for b in blocks if b[6] == 0 and (b[0] + b[2]) / 2 > page_mid + 20]
        if left_x1s and right_x0s:
            sep = (max(left_x1s) + min(right_x0s)) / 2
        else:
            sep = page_mid
        return [
            (page.rect.x0 + 20, sep - 5),
            (sep + 5, page.rect.x1 - 20),
        ]
    return [(page.rect.x0 + 20, page.rect.x1 - 20)]
```

#### Step 3：确定裁剪矩形

```python
def _determine_crop_rect(self, hit: Dict, caption_hits: List[Dict],
                          page_rect: fitz.Rect, col_x0: float,
                          col_x1: float) -> fitz.Rect:
    """
    根据 Caption 位置和类型，确定裁剪矩形。
    - Figure/Algorithm：Caption 在下方，向上找图形区域
    - Table：Caption 在上方，向下找表格区域
    边界由相邻 Caption 的位置决定，避免跨图裁剪。
    """
    cap_rect = hit["rect"]

    if hit["is_table"]:
        # Caption 在上，裁剪 Caption 及其下方区域
        # 下边界：下一个 Caption 的上沿，或页面底部
        next_ys = [
            h["rect"].y0 for h in caption_hits
            if h["rect"].y0 > cap_rect.y1 + 10
        ]
        bottom = min(next_ys) - 5 if next_ys else page_rect.y1 - 20
        return fitz.Rect(col_x0, cap_rect.y0 - 3, col_x1, bottom)
    else:
        # Caption 在下，裁剪 Caption 上方的图形区域
        # 上边界：上一个 Caption 的下沿，或页面顶部
        prev_ys = [
            h["rect"].y1 for h in caption_hits
            if h["rect"].y1 < cap_rect.y0 - 10
        ]
        top = max(prev_ys) + 5 if prev_ys else page_rect.y0 + 20
        return fitz.Rect(col_x0, top, col_x1, cap_rect.y1 + 3)
```

#### Step 4：裁剪渲染并保存

```python
def _extract_figure_regions(self, doc: fitz.Document,
                             page_numbers: Set[int],
                             image_dir: Path) -> List[Dict]:
    """
    对指定页面，精准裁剪每个 Figure/Table/Algorithm 区域。
    替代原有的整页渲染逻辑。
    """
    results = []
    zoom = 2.0
    mat = fitz.Matrix(zoom, zoom)
    MIN_WIDTH, MIN_HEIGHT = 200, 100

    for page_num in sorted(page_numbers):
        page = doc[page_num - 1]
        caption_hits = self._collect_caption_rects(page)
        if not caption_hits:
            continue

        columns = self._detect_columns(page)

        for idx, hit in enumerate(caption_hits):
            cap_rect = hit["rect"]
            # 确定 Caption 所在的栏
            cap_center_x = (cap_rect.x0 + cap_rect.x1) / 2
            col_x0, col_x1 = columns[0]  # 默认单栏
            for (cx0, cx1) in columns:
                if cx0 <= cap_center_x <= cx1:
                    col_x0, col_x1 = cx0, cx1
                    break

            crop_rect = self._determine_crop_rect(
                hit, caption_hits, page.rect, col_x0, col_x1
            )

            # 合法性检查
            if crop_rect.is_empty or crop_rect.width < 50 or crop_rect.height < 50:
                continue

            # 裁剪渲染
            pix = page.get_pixmap(matrix=mat, clip=crop_rect, alpha=False)

            if pix.width < MIN_WIDTH or pix.height < MIN_HEIGHT:
                continue

            image_filename = f"page{page_num}_fig{idx}.png"
            image_path = image_dir / image_filename
            pix.save(str(image_path))

            results.append({
                "page": page_num,
                "path": str(image_path),
                "caption": hit["text"],
                "width": pix.width,
                "height": pix.height,
                "size_kb": image_path.stat().st_size / 1024,
                "rendered": True,
                "cropped": True,
            })
            logger.info(f"  裁剪 page{page_num} idx{idx}: {hit['text'][:60]}")

    return results
```

### 5.3 改进 image_type 分类

基于 Caption 文本直接分类，精度远高于现有逻辑：

```python
def _classify_image_type(self, caption: str) -> str:
    c = caption.lower()
    if re.match(r'(algorithm|alg\.?)\s*\d+', c):
        return 'algorithm'
    elif re.match(r'(table|tab\.?)\s*\d+', c):
        return 'table'
    elif re.match(r'(listing|scheme)\s*\d+', c):
        return 'algorithm'   # 归入算法类
    elif re.search(r'architecture|framework|overview|pipeline|structure|model', c):
        return 'architecture'
    elif re.search(r'result|performance|comparison|accuracy|loss|curve|ablation|f1|precision|recall', c):
        return 'performance'
    else:
        return 'figure'      # 通用 figure，保留（原来的 other 改为 figure）
```

---

## 六、改动范围

### 6.1 需要修改的文件

| 文件 | 改动内容 | 影响范围 |
|------|---------|---------|
| `services/pdf_parser.py` | ① 新增 `_find_caption_near_image`（改进光栅图 caption 匹配）<br>② 新增 `_collect_caption_rects`、`_detect_columns`、`_determine_crop_rect`<br>③ 新增 `_extract_figure_regions`（精准裁剪）<br>④ `extract_images_to_disk` 阶段 2 改为调用 `_extract_figure_regions`<br>⑤ 保留 `_find_image_caption_legacy`（原有逻辑，作为降级） | 仅图片提取路径，文本提取/元数据提取不受影响 |
| `services/image_extractor.py` | ① 更新 `_classify_image_type` 使用新分类逻辑<br>② 新增 `table` 类型支持 | 接口签名 `extract_key_images(pdf_path, paper_id)` 完全不变 |

### 6.2 不需要修改的文件

| 文件 | 理由 |
|------|------|
| `services/summarizer.py` | 不涉及图片 |
| `services/mindmap_generator.py` | 不涉及图片 |
| `services/tagger.py` | 不涉及图片 |
| `services/rag_service.py` | 不涉及图片 |
| `services/llm_service.py` | 无需 LLM 参与 |
| `services/doubao_service.py` | 无需 LLM 参与 |
| `services/api_config.py` | 无需新 API 角色 |
| `services/paper_processor.py` | 调用 `image_extractor.extract_key_images()`，接口不变 |
| `ui/upload_page.py` | 调用 `image_extractor.extract_key_images()`，接口不变 |
| `ui/paper_detail.py` | 读取 `db_manager.get_paper_images()`，接口不变 |
| `ui/auto_scholar.py` | 通过 `paper_importer` 调用，接口不变 |
| `database/db_manager.py` | `add_image_to_paper` 接口不变，新增 `table` 类型无需 schema 变更（`image_type` 为 String 字段） |
| `database/models.py` | `PaperImage.image_type` 已为 String(50)，`table` 类型直接写入，无需迁移 |

---

## 七、对现有功能的影响分析

### 7.1 论文上传流程

**调用链**：`upload_page.py` → `image_extractor.extract_key_images()` → `pdf_parser.extract_images_to_disk()`

- 入口接口 `extract_key_images(pdf_path, paper_id)` **签名不变**
- 返回值结构 `List[dict]` **不变**（新增 `cropped: True` 字段，上层不使用该字段）
- 数据库写入逻辑不变，`image_type` 字段值增加 `table`、`figure` 两个新值
- **影响**：无破坏性影响，处理时间略有增加（`search_for` 调用开销极小）

### 7.2 Auto-Scholar 导入论文

**调用链**：`auto_scholar.py` → `paper_importer` → `paper_processor.py` → `image_extractor.extract_key_images()`

- 与上传流程调用同一接口，影响相同
- **影响**：无破坏性影响

### 7.3 论文详情页图片展示

`paper_detail.py` 按 `image_type` 过滤图片展示：

```python
# 现有代码
if img_type == 'architecture':
    st.markdown("**系统架构图:**")
elif img_type == 'algorithm':
    st.markdown("**算法图:**")
elif img_type == 'performance':
    st.markdown("**性能对比图:**")
```

新增的 `table` 和 `figure` 类型不在上述条件中，会被 `filtered_images` 过滤掉（因为 `sections` 配置中没有对应的 `image_type`）。

**需要同步更新** `paper_detail.py` 中的 `sections` 配置，为 `table` 和 `figure` 添加展示入口，否则这两类图片入库后不会显示。

建议在 `methodology` 和 `results` 章节中增加：

```python
sections = [
    ...
    ("methodology", "具体方法", "architecture,algorithm,figure"),
    ("results",     "实验结果", "performance,table"),
    ...
]
```

### 7.4 用户手动上传图片

用户在编辑模式下手动上传的图片，`image_type` 由上传时的 `section_key` 决定，与本方案无关，**不受影响**。

### 7.5 RAG 对话问答

RAG 服务仅使用文本向量，不涉及图片，**完全不受影响**。

### 7.6 标签系统

标签系统与图片无关，**完全不受影响**。

---

## 八、降级策略

每一步都有明确的降级路径，保证任何异常不会导致整个图片提取流程失败：

```
search_for(caption_text) 返回空列表
    → 跳过该 Caption，继续处理下一个
    → 该页面其他 Caption 正常处理

_collect_caption_rects 整页无匹配
    → 该页面不进入阶段 2（与现有逻辑一致）

crop_rect 计算结果过小（< 50×50）
    → 跳过，不保存

page.get_image_rects(xref) 返回空
    → _find_caption_near_image 降级为原有 _find_image_caption_legacy

裁剪后图片尺寸不足（< 200×100）
    → 跳过，不入库

page.get_text("blocks") 返回空（极少数加密 PDF）
    → _detect_columns 降级为单栏模式
```

---

## 九、已知局限

| 场景 | 表现 | 说明 |
|------|------|------|
| 跨页图片（图跨两页） | 只裁剪 Caption 所在页的区域 | 跨页图在学术论文中极少见，可接受 |
| Caption 文字被 PDF 编码为不可搜索（扫描版 PDF） | `search_for` 返回空，降级跳过 | 扫描版 PDF 本身文本提取也不可靠 |
| 同一页多个图共享同一 Caption 区域 | 可能裁剪范围过大 | 较少见，裁剪结果仍优于整页渲染 |
| 极窄双栏（如 3 栏布局） | 列检测可能失效，回退单栏模式 | 3 栏论文极少见 |
| ~~跨双栏大图（如 Fig. 1）上边界截取~~ | ~~`_find_content_bbox_via_drawings` 返回的 bbox 仅覆盖图形的局部子区域~~  | **已修复**（v1.2）：Strategy 2 改为取所有候选 drawing 的 union，并将距离过滤从固定 200pt 改为 `search_top` |

---

## 十、实现顺序

1. ✅ **`services/pdf_parser.py`**：实现所有新方法，重构阶段 2
2. ✅ **`services/image_extractor.py`**：更新分类逻辑
3. ✅ **`ui/paper_detail.py`**：同步更新 `sections` 配置，支持 `table` 和 `figure` 类型展示
4. ✅ **修复 Fig. 1 跨栏大图上边界截取问题**（见十二节）
5. ✅ **修复 Algorithm 正文引用句误判 + 伪代码扩展越界**（见十三节）
6. ✅ **针对 ATTENTION RESIDUALS.pdf 的全面修复**（见十五节）
7. 🔲 **TODO：Algorithm 专用裁剪路径**（见十四节）
8. 🔲 使用至少 3 篇不同类型论文（纯光栅图、纯矢量图、混合）验证提取结果

---

## 十一、验收标准

- [x] 矢量图论文（LaTeX tikz）不再出现整页截图
- [x] 每个 Figure/Table/Algorithm 对应独立裁剪图片
- [x] Caption 与裁剪图片正确对应
- [x] 双栏论文左右栏图片不互相干扰
- [x] 现有光栅图提取结果不变
- [x] 用户手动上传图片功能正常
- [x] Auto-Scholar 导入论文后图片正常提取
- [x] RAG 对话、标签、思维导图等功能不受影响
- [x] Fig. 1 跨栏大图完整提取（上边界不截取）
- [x] Algorithm 正文引用句不再被误判为 Caption
- [x] Algorithm 伪代码截取不越界到 APPENDIX/REFERENCES
- [x] Figure 页眉水平线不再被误判为图片边框
- [x] Figure 顶部文本标签（Output、VIRTUAL STAGE 等）完整截取
- [x] Table 底部包含完整脚注（† ‡ 注释行）
- [x] 跨栏图（Figure 4 等）不再被截成左半边
- [x] PyMuPDF 版本兼容：search_for 多段返回时 caption 宽度正确
- [ ] **TODO：Algorithm 裁剪策略与实际结构对齐**（见十四节）

---

## 十二、待修复：Fig. 1 跨栏大图上边界截取

### 问题描述

`Fig. 1: Illustration of the proposed multi-objective algorithm evolution via LLM` 的上 1/3 内容（"Operator Initialization"、"Parallel Operator Evaluation"、"Dynamic Operator Selection via Scores" 三行标签及对应图形）被截取掉。

### 根因分析

`_find_content_bbox_via_drawings` 对该图返回 `bbox = Rect(112.58, 178.17, 315.23, 349.49)`，该 bbox 仅覆盖图中央的流程框，而非整个图形。

当前代码使用 `bbox.y0 - 3 = 175.17` 作为裁剪上边界，而图形实际顶部内容从 `y ≈ 58` 开始，导致 y=58~175 的内容全部丢失。

### 根因

Strategy 2 存在两个缺陷：

1. **距离过滤太激进**：`r.y1 < cap_rect.y0 - 200` 用固定 200pt 作为距离上限，Fig. 1 高度约 300pt，导致 `y0=58~y1=100` 的顶部 drawing 被排除（`100 < 361 - 200 = 161`）

2. **取单个"最优"矩形**：Strategy 2 只取评分最高的一个矩形（橙色大边框 `Rect(178, 349)`），而非所有 drawing 的包围盒，顶部内容丢失

### 修复方案（已实现，v1.2）

修改 `_find_content_bbox_via_drawings` Strategy 2：

- 将距离过滤从 `r.y1 < cap_rect.y0 - 200` 改为 `r.y0 < search_top`：上界由 `coarse_top`（前一个 Caption 底部）决定，天然防止跨图干扰，无需固定 200pt
- 将"取最高分单个矩形"改为"取所有候选的 union（包围盒）"：确保完整覆盖所有图形元素

修复后 Fig. 1 的 `bbox.y0` 从 178.2 → 59.6，`crop = Rect(20, 56.6, 592, 374)`，完整包含图形顶部三行内容。

---

## 十三、已修复：Algorithm 正文引用句误判 + 伪代码扩展越界

**测试 PDF**：`AL_iLQR_Tutorial.pdf`

### 问题 1：Algorithm 正文引用句被误判为 Caption

**现象**：page 4 正文句 `Algorithm 3. We now proceed with the formal derivation.` 被识别为 Caption，生成一张截取 page 4 左栏正文内容（III. AL-DDP → A. Backward Pass）的图片。

**根因**：`_is_caption_line` 的动词过滤列表不含 `proceed`，该句通过所有过滤规则。正文引用句有明确句法特征：`Algorithm N.` + 空格 + 大写字母开头的完整句子（数字后紧跟句点）。

**修复**（`_is_caption_line`）：新增规则，匹配 `^(Algorithm|Alg\.?)\s*\d+\.\s+[A-Z]` 的行直接返回 `False`。

### 问题 2：Algorithm 6 伪代码扩展越界，包含 APPENDIX/REFERENCES

**现象**：Algorithm 6 截图（574×375px 应有内容）被扩展为 574×785px，包含 APPENDIX、REFERENCES 及 3 篇引用文献。

**根因**：`_extend_crop_for_algorithm` 在 crop 底部（y=513）到 `next_cap_y`（y=772，页面底部）之间扫描文本块时：
- `APPENDIX`（avg_len=8）、`REFERENCES`（avg_len=10）、参考文献条目（avg_len=35.9）均低于停止阈值 `avg_len > 40`，全部被纳入扩展

**修复**（`_extend_crop_for_algorithm`）：新增两条早停条件：
```python
# 全大写节标题（APPENDIX、REFERENCES、ACKNOWLEDGMENT 等）
if re.match(r'^[A-Z][A-Z\s\-]{3,}$', text.strip()):
    break
# 参考文献条目（以 [数字] 开头）
if re.match(r'^\[\d+\]', text.strip()):
    break
```

**验证结果**：Algorithm 6 图片高度 785px → 375px，不含 APPENDIX/REFERENCES；误判图片消失，总提取数 7 → 6。

---

## 十四、TODO：Algorithm 专用裁剪路径

### 背景

用户给出的 3 条规律：
- **Figure**：标题在图片**下方**
- **Table**：标题在表格**上方**
- **Algorithm**：标题是伪代码框的**第一行**，内容在标题下方

当前实现将 Algorithm 与 Figure 同路径处理（向上找内容），实际上 Algorithm 的 Caption 就是框的第一行，内容在 Caption 下方。当前能工作是因为 Strategy 1（水平线对）碰巧找到了框顶线和框底线，但 `_extend_crop_for_algorithm` 的文本扩展逻辑是补丁，存在隐患。

### 目标

Algorithm 专用路径，完全对齐实际结构，废弃对 Algorithm 的 `_extend_crop_for_algorithm` 调用。

### 实现方案

**Step 1**：`_collect_caption_rects` 新增 `is_algorithm` 字段

```python
is_algorithm = bool(re.match(r'(Algorithm|Alg\.?|Listing|Scheme)\s*\d+', line, re.IGNORECASE))
caption_hits.append({
    "text": line,
    "rect": rects[0],
    "is_table": is_table,
    "is_algorithm": is_algorithm,  # 新增，向后兼容（下游用 hit.get("is_algorithm", False)）
})
```

**Step 2**：`_determine_crop_rect` 新增 Algorithm 分支

```python
elif hit.get("is_algorithm"):
    # Algorithm：Caption 是框第一行，crop 从框顶线到框底线
    # coarse_top = 前一个同栏 Caption 底部（或页面顶部）
    same_col_hits = [h for h in caption_hits if h is not hit and ...]
    prev_ys = [h["rect"].y1 for h in same_col_hits if h["rect"].y1 < cap_rect.y0 - 10]
    coarse_top = (max(prev_ys) + 5) if prev_ys else (page_rect.y0 + 20)
    next_ys = [h["rect"].y0 for h in same_col_hits if h["rect"].y0 > cap_rect.y1 + 10]
    bottom_fallback = (min(next_ys) - 5) if next_ys else (page_rect.y1 - 20)

    # Strategy 1：水平线对精确定位框顶（Caption 上方）和框底
    # 提取为独立方法 _find_algorithm_bbox_via_hlines(page, cap_rect, col_x0, col_x1, coarse_top, bottom_fallback)
    bbox = self._find_algorithm_bbox_via_hlines(...)
    if bbox:
        return bbox
    # 降级：coarse_top 到 bottom_fallback
    return fitz.Rect(col_x0, coarse_top, col_x1, bottom_fallback)
```

**Step 3**：`_extract_figure_regions` 中 `img_type == 'algorithm'` 时**不再调用** `_extend_crop_for_algorithm`

### 影响评估

- Algorithm 路径完全独立，Figure 和 Table 路径代码不变
- `_extend_crop_for_algorithm` 保留但不再被调用（可在验证后删除）
- `_find_algorithm_bbox_via_hlines` 是从现有 Strategy 1 逻辑中提取，无新逻辑

### 优先级

P2，当前补丁（改动 1+2）已能正常工作，此改动是结构性优化，待有空推进。

---

## 十五、已修复：ATTENTION RESIDUALS.pdf 全面修复（v1.4）

**测试 PDF**：`ATTENTION RESIDUALS.pdf`（Kimi Team 技术报告，双栏，含复杂矢量图、宽表格、页眉装饰线）

### 修复 1：Figure 页眉水平线误判（`_find_content_bbox_via_drawings`）

**现象**：Figure 1/3/5/6/8 的 crop 从页眉线（y≈47~80）开始，包含大量正文。

**根因**：Strategy 1（水平线对）原本为 Algorithm 框设计，但对所有类型都执行。该 PDF 每页有全页宽页眉装饰线（w=468pt），满足「宽度 > 30% 栏宽」条件，被误判为图片边框。

**修复**：新增 `is_algorithm` 参数，Strategy 1 仅在 `is_algorithm=True` 时执行；Strategy 2 的 rw 阈值从 `col_width*0.3` 改为 `min(col_width*0.1, 20)`，确保细长 drawing 组成的图（神经网络示意图）也能正确定位。

### 修复 2：Figure 顶部文本标签遗漏（`_determine_crop_rect`）

**现象**：Figure 1 缺失顶部 "Output" 标签（22pt），Figure 3 缺失 "VIRTUAL STAGE 0/1" 标签（14pt）。

**根因**：Strategy 2 只扫描 drawing，不扫描文本。图片顶部由文本标签组成时，`bbox.y0` 来自最小 drawing 的 y，比文本标签低 14~22pt。

**修复**：Figure 路径中，bbox 不为 None 后向上额外扫描 bbox.y0 上方 30pt 内与 bbox x 范围有实质重叠的短文本块（avg_line_len < 30），将 crop_top 扩展到这些文本块的 y0-3。

### 修复 3：Table 底部截断脚注（Strategy 1b）

**现象**：Table 2 crop bottom=191，脚注（† ‡ ⋆ 三行注释，y=182.8~214.6）被截断。

**根因**：Strategy 1b 只找水平线最大 y（y=181.1），脚注在水平线之后，未被纳入。

**修复**：找到 `table_bottom` 后，向下扫描 `table_bottom+60pt` 内的连续短文本块（间隔≤15pt，avg_len<80），扩展到脚注底部。连续性检测确保不会跨越 Figure 4 图表内容（间距 21.8pt > 15pt 触发停止）。

同时将 Strategy 1b 水平线宽度阈值从 `col_width*0.3` 提高到 `col_width*0.5`，防止图表内部线条（w=181.9pt < 50%=286pt）被误判为表格底线。

### 修复 4：Figure 4 跨栏检测失败（`_extract_figure_regions`）

**现象**：Figure 4 被截成左半边（792px），实际应为全页宽（1144px）。

**根因**：Figure 4 caption 右边界 367.7pt，右栏左边界 369pt，差 1.3pt，几何法跨栏检测（margin=5pt）失败，图表被限制在左栏（x=20~359），而 drawings x 范围达 228~413。

**修复**：`_determine_crop_rect` 返回后，检查 `crop.x1 > col_x1 + 20`——若超出当前栏边界，说明图表实际跨栏，自动扩展为全页宽并重新计算。

### 修复 5：Figure 8 误分类为 architecture（`_classify_caption`）

**现象**：Figure 8（分布图）被分类为 `architecture`，显示在"系统架构图"区域。

**根因**：architecture 关键词包含 `model`，而 Figure 8 caption 含 `model`（指模型规格，非架构图）。

**修复**：从 architecture 关键词中移除 `model`，同步修改 `image_extractor._classify_image_type`。

### 修复 6：PyMuPDF 版本兼容（`_collect_caption_rects`）

**现象**：Paper Brain 重启后 Table 2 仍只截左半边（690×743px）。

**根因**：Paper Brain 使用 anaconda 的 PyMuPDF 1.23.x，`search_for` 将同一行长文字分成多个矩形（Table 2 caption 被分为 3 段），原代码只取 `rects[0]`（第一段，x=71~209，宽度 137pt），导致跨栏检测失败。用 homebrew Python 测试时 `search_for` 返回单个矩形，掩盖了此问题。

**修复**：取所有 `rects` 的 union x/y 范围构造 caption rect，确保跨 PyMuPDF 版本一致性。修复后 caption 宽度 137pt → 312pt，跨栏检测正确，图片 690×743px → 1156×301px。

### 验证结果（三个 PDF 全部通过）

| 图片 | 修复前 | 修复后 |
|------|--------|--------|
| Figure 1 | 1144×494px（缺 Output 标签） | **1144×538px** |
| Figure 3 | 1144×269px（缺 VIRTUAL STAGE） | **1144×302px** |
| Figure 4 | 792×464px（左半边） | **1144×464px** |
| Figure 8 | 分类为 architecture | **分类为 figure** |
| Table 2 | 690×743px（左半边+含 Figure 4） | **1156×301px** |
| Table 1/3/4/5 | crop 到页面底部 | **精确到表格底线+脚注** |
| auto-multi-obj 所有图 | 正常 | **不变** |
| AL_iLQR_Tutorial 所有图 | 正常 | **不变** |
