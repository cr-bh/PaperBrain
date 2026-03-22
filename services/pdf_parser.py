"""
PDF 解析服务
使用 PyMuPDF 提取 PDF 内容
"""
import fitz  # PyMuPDF
import re
import logging
from typing import Dict, List, Set, Tuple
from pathlib import Path
import config

logger = logging.getLogger(__name__)

FIGURE_PATTERN = re.compile(r'(Figure|Fig\.?)\s*\d+', re.IGNORECASE)

# 匹配任意含 Caption 关键词的行（宽泛，用于正文扫描）
CAPTION_PATTERN = re.compile(
    r'(Figure|Fig\.?|Table|Tab\.?|Algorithm|Alg\.?|Listing|Scheme)\s*\d+',
    re.IGNORECASE
)

TABLE_PATTERN = re.compile(r'(Table|Tab\.?)\s*\d+', re.IGNORECASE)

# 严格 Caption 行：必须以 Caption 关键词开头，后跟编号，行长度有限（避免正文引用句）
# 例如：匹配 "Figure 1: Overview of..."，不匹配 "As shown in Figure 1, our..."
_CAPTION_LINE_RE = re.compile(
    r'^(Figure|Fig\.?|Table|Tab\.?|Algorithm|Alg\.?|Listing|Scheme)\s*\d+[\s:\.\-]',
    re.IGNORECASE
)
# 纯编号行（无后续文字），也视为 Caption 起始行
_CAPTION_LINE_BARE_RE = re.compile(
    r'^(Figure|Fig\.?|Table|Tab\.?|Algorithm|Alg\.?|Listing|Scheme)\s*\d+\s*$',
    re.IGNORECASE
)

MAX_CAPTION_LINE_LEN = 300  # Caption 行最长字符数，超过则认为是正文段落

# 正文引用句中常见动词/短语，用于排除 "Alg. 5 outlines..." 这类句子
_BODY_TEXT_VERBS_RE = re.compile(
    r'\b(outlines?|shows?|showcases?|presents?|describes?|illustrates?|depicts?|'
    r'demonstrates?|summarizes?|lists?|provides?|gives?|details?|'
    r'explains?|introduces?|proposes?|defines?|reports?|compares?|'
    r'displays?|reveals?|highlights?|includes?|contains?)\b',
    re.IGNORECASE
)


class PDFParser:
    """PDF 解析器"""

    def __init__(self):
        pass

    def parse_pdf(self, pdf_path: str) -> Dict:
        """
        解析 PDF 文件

        Returns:
            包含文本、元数据和图片信息的字典
        """
        doc = fitz.open(pdf_path)

        full_text = self._extract_text(doc)
        metadata = self._extract_metadata(doc)
        images_info = self._extract_images_info(doc)
        page_count = len(doc)

        doc.close()

        return {
            "text": full_text,
            "metadata": metadata,
            "images": images_info,
            "page_count": page_count
        }

    def _extract_text(self, doc: fitz.Document) -> str:
        """提取 PDF 全文文本"""
        text_parts = []
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            text_parts.append(f"[Page {page_num}]\n{text}")

        return "\n\n".join(text_parts)

    def _extract_metadata(self, doc: fitz.Document) -> Dict:
        """提取 PDF 元数据"""
        metadata = doc.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", "")
        }

    def _extract_images_info(self, doc: fitz.Document) -> List[Dict]:
        """提取图片信息（不保存图片，只记录位置和 Caption）"""
        images_info = []

        for page_num, page in enumerate(doc, start=1):
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                caption = self._find_image_caption_legacy(page)

                images_info.append({
                    "page": page_num,
                    "index": img_index,
                    "caption": caption,
                    "xref": img[0]
                })

        return images_info

    def _find_image_caption_legacy(self, page: fitz.Page) -> str:
        """原有 Caption 查找逻辑（降级用），整页盲搜第一个 Figure/Fig. 行"""
        text = page.get_text()
        lines = text.split('\n')

        for line in lines:
            if FIGURE_PATTERN.search(line):
                return line.strip()

        return ""

    def _find_caption_near_image(self, page: fitz.Page, xref: int,
                                  margin: float = 80) -> str:
        """
        在图片附近搜索 Caption 文字。
        先尝试图片下方（Figure 常见），再尝试图片上方（Table 常见）。
        只返回严格的 Caption 行（以关键词开头），找不到时返回空字符串。
        不再降级为整页盲搜，避免将正文引用句误识别为 Caption。
        """
        try:
            rects = page.get_image_rects(xref)
        except Exception:
            rects = []

        if not rects:
            return ""

        img_rect = rects[0]

        # 先搜图片下方（扩大到 120pt，覆盖多行 Caption）
        search_below = fitz.Rect(
            img_rect.x0, img_rect.y1,
            img_rect.x1, img_rect.y1 + margin
        )
        text_below = page.get_text(clip=search_below)
        for line in text_below.split('\n'):
            line = line.strip()
            if self._is_caption_line(line):
                return line

        # 再搜图片上方（Table Caption 在上方）
        search_above = fitz.Rect(
            img_rect.x0, img_rect.y0 - margin,
            img_rect.x1, img_rect.y0
        )
        text_above = page.get_text(clip=search_above)
        for line in text_above.split('\n'):
            line = line.strip()
            if self._is_caption_line(line):
                return line

        # 找不到严格 Caption，返回空（不降级为整页盲搜）
        return ""

    def _find_figure_pages(self, doc: fitz.Document) -> Dict[int, List[str]]:
        """扫描所有页面，返回包含独立 Caption 行的页码及其 Caption 列表。
        使用严格 Caption 识别，避免正文引用句把无图页面误加入渲染列表。"""
        figure_pages = {}
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            captions = []
            for line in text.split('\n'):
                line = line.strip()
                if self._is_caption_line(line):
                    captions.append(line)
            if captions:
                figure_pages[page_num] = captions
        return figure_pages

    # ===== 精准裁剪相关方法 =====

    def _is_caption_line(self, line: str) -> bool:
        """
        判断一行文字是否是独立的 Caption 行（而非正文中引用 Figure/Table 的句子）。
        规则：
        1. 行必须以 Caption 关键词 + 编号开头（不是出现在句子中间）
        2. 行长度不超过 MAX_CAPTION_LINE_LEN（过长说明是正文段落）
        3. 行内不能含有正文引用动词（"outlines", "shows", "presents" 等）
           排除 "Alg. 5 outlines the full procedure..." 这类正文句子
        """
        if len(line) > MAX_CAPTION_LINE_LEN:
            return False
        if not (_CAPTION_LINE_RE.match(line) or _CAPTION_LINE_BARE_RE.match(line)):
            return False
        # 排除正文引用句：含有动词说明这是正文在引用图表，而非 Caption 本身
        if _BODY_TEXT_VERBS_RE.search(line):
            return False
        # 排除 "Algorithm N. 大写字母..." 格式的正文引用句
        # 真正的伪代码标题格式是 "Algorithm N Name" 或 "Algorithm N: Name"，无句点分隔
        # 例如：'Algorithm 3. We now proceed...' → 正文；'Algorithm 3 Iterative LQR' → Caption
        if re.match(r'^(Algorithm|Alg\.?)\s*\d+\.\s+[A-Z]', line):
            return False
        # 排除 "Algorithm N 小写动词..." 格式的正文引用句
        # 真正的 Caption 在编号后跟冒号或大写名词短语，正文引用句跟小写动词
        # 例如：'Algorithm 1 instantiates...' → 正文；'Algorithm 1 Backward Pass' → Caption
        m = re.match(r'^(Algorithm|Alg\.?)\s*\d+\s+([a-z]\w*)', line)
        if m:
            return False
        return True

    def _collect_caption_rects(self, page: fitz.Page) -> List[Dict]:
        """
        收集页面上所有独立 Caption 行及其精确坐标。
        关键改进：只识别以 Caption 关键词开头的行，过滤正文引用句。
        """
        caption_hits = []
        seen_texts = set()

        text = page.get_text()
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            # 严格判断：必须是独立 Caption 行
            if not self._is_caption_line(line):
                continue
            if line in seen_texts:
                continue
            seen_texts.add(line)

            # 优先用完整行搜索
            try:
                # 只取前 80 个字符搜索，避免因换行导致 search_for 失败
                search_text = line[:80]
                rects = page.search_for(search_text)
            except Exception:
                rects = []

            if not rects:
                # fallback：只用 "Figure N" / "Table N" 等短串搜索
                m = CAPTION_PATTERN.search(line)
                if m:
                    try:
                        short_key = m.group(0)
                        all_rects = page.search_for(short_key)
                        # 从所有匹配中，找最可能是 Caption 的位置：
                        # Caption 通常在页面下半部分，或 y 坐标最大的那个
                        # （正文引用一般散布在页面各处，Caption 往往在图的下方）
                        if all_rects:
                            # 优先选 y 坐标最靠下的（Caption 通常在图下方）
                            rects = [max(all_rects, key=lambda r: r.y0)]
                    except Exception:
                        rects = []

            if not rects:
                continue

            is_table = bool(TABLE_PATTERN.match(line))
            is_algorithm = bool(re.match(
                r'^(Algorithm|Alg\.?|Listing|Scheme)\s*\d+', line, re.IGNORECASE
            ))
            caption_hits.append({
                "text": line,
                "rect": rects[0],
                "is_table": is_table,
                "is_algorithm": is_algorithm,
            })

        # 按 y 坐标排序，从上到下
        caption_hits.sort(key=lambda h: h["rect"].y0)
        return caption_hits

    def _detect_columns(self, page: fitz.Page) -> List[Tuple[float, float]]:
        """
        检测页面列布局，返回每列的 (x0, x1) 范围。
        单栏：[(页左边距, 页右边距)]
        双栏：[(左栏x0, 左栏x1), (右栏x0, 右栏x1)]
        """
        try:
            blocks = page.get_text("blocks")
        except Exception:
            return [(page.rect.x0 + 20, page.rect.x1 - 20)]

        if not blocks:
            return [(page.rect.x0 + 20, page.rect.x1 - 20)]

        page_mid = page.rect.width / 2
        # block_type == 0 为文本块
        text_blocks = [b for b in blocks if len(b) > 6 and b[6] == 0 and b[4].strip()]

        left_count = sum(1 for b in text_blocks if (b[0] + b[2]) / 2 < page_mid - 20)
        right_count = sum(1 for b in text_blocks if (b[0] + b[2]) / 2 > page_mid + 20)

        if left_count > 3 and right_count > 3:
            left_x1s = [b[2] for b in text_blocks if (b[0] + b[2]) / 2 < page_mid - 20]
            right_x0s = [b[0] for b in text_blocks if (b[0] + b[2]) / 2 > page_mid + 20]
            if left_x1s and right_x0s:
                sep = (max(left_x1s) + min(right_x0s)) / 2
            else:
                sep = page_mid
            return [
                (page.rect.x0 + 20, sep - 5),
                (sep + 5, page.rect.x1 - 20),
            ]

        return [(page.rect.x0 + 20, page.rect.x1 - 20)]

    def _in_same_column(self, rect_a: "fitz.Rect", col_x0: float, col_x1: float) -> bool:
        """判断一个矩形的中心是否在指定列范围内"""
        center_x = (rect_a.x0 + rect_a.x1) / 2
        return col_x0 <= center_x <= col_x1

    def _find_content_bbox_via_drawings(self, page: "fitz.Page",
                                         cap_rect: "fitz.Rect",
                                         col_x0: float, col_x1: float,
                                         search_above: bool = True,
                                         search_top: float = 0.0,
                                         is_algorithm: bool = False) -> "fitz.Rect | None":
        """
        用 get_drawings() 找 Caption 附近的图形/算法框边界。
        两种策略：
        1. 水平线对（Algorithm 框）：仅在 is_algorithm=True 时启用。
           找 Caption 上方最近的横线（上边）+ 下方最近的横线（下边）。
           不对 Figure/Table 启用，避免将页眉装饰线误判为图片边框。
        2. 面积矩形（Figure/Algorithm 图形框）：找 Caption 附近所有符合条件的
           矩形的 union，rw 阈值 10% 栏宽（原 30%，放宽以捕获细长 drawing 组成的图）。
        """
        try:
            drawings = page.get_drawings()
        except Exception:
            return None

        col_width = col_x1 - col_x0

        # ── 策略1：水平线对（仅 Algorithm 框使用） ──
        # Figure 不使用此策略，避免页眉水平线被误判为图片边框
        if not is_algorithm:
            hlines = []
        else:
            hlines = []
            for d in drawings:
                r = d.get('rect')
                if r is None:
                    continue
                rw = r.x1 - r.x0
                rh = r.y1 - r.y0
                # 水平线：高度 < 2pt，宽度 > 30% 栏宽
                if rh >= 2 or rw < col_width * 0.3:
                    continue
                r_cx = (r.x0 + r.x1) / 2
                if not (col_x0 - 20 <= r_cx <= col_x1 + 20):
                    continue
                hlines.append(r.y0)

        if hlines:
            if search_above:
                # 找 Caption 上方的横线对：上边线（最小y）+ 下边线（最大y，但 ≤ Caption.y1 + 5）
                # search_top 限制搜索范围上界（前一个 Caption 的底部），避免跨图干扰
                above = sorted([y for y in hlines if search_top <= y < cap_rect.y1 + 5])
                below = [y for y in hlines if y > cap_rect.y1 + 5]
                if len(above) >= 2:
                    # 有上下边线对
                    top_y = above[0]   # 最上面的横线
                    bot_y = above[-1]  # 最下面的横线（框底或 Caption 附近）
                    # 如果框延伸到 Caption 下方，用 below 中最近的线
                    if below:
                        bot_y = max(bot_y, min(below))
                    return fitz.Rect(col_x0, top_y - 2, col_x1, bot_y + 5)
                elif len(above) == 1:
                    top_y = above[0]
                    bot_y = min(below) if below else cap_rect.y1
                    return fitz.Rect(col_x0, top_y - 2, col_x1, bot_y + 5)
            else:
                below = [y for y in hlines if y > cap_rect.y1 - 5]
                if below:
                    top_y = min(below)
                    bot_y = max([y for y in hlines if y > top_y], default=top_y + 50)
                    return fitz.Rect(col_x0, cap_rect.y0 - 3, col_x1, bot_y + 5)

        # ── 策略1b：Table 底部水平线定位 ──
        # Table 的框线是水平线（rh≈0），Strategy 1 仅对 Algorithm 启用，
        # 但 Table 同样需要水平线来确定底部边界。
        # 找 caption 下方所有宽度 ≥ 50% 栏宽的水平线，取 y 最大的作为表格底部。
        # 阈值用 50%（而非 30%）：Table 框线通常横跨大部分表格宽度，
        # 图表内部线条较窄，50% 阈值能有效区分表格线和图表线。
        if not search_above:
            table_hlines = []
            for d in drawings:
                r = d.get('rect')
                if r is None:
                    continue
                rw = r.x1 - r.x0
                rh = r.y1 - r.y0
                if rh >= 3 or rw < col_width * 0.5:
                    continue
                r_cx = (r.x0 + r.x1) / 2
                if not (col_x0 - 20 <= r_cx <= col_x1 + 20):
                    continue
                if r.y0 > cap_rect.y1:  # caption 下方
                    table_hlines.append(r.y0)
            if table_hlines:
                table_bottom = max(table_hlines)
                return fitz.Rect(col_x0, cap_rect.y0 - 3, col_x1, table_bottom + 5)

        # ── 策略2：面积矩形（适合 Figure 图形框） ──
        # 取所有候选矩形的 union（包围盒），而非单个"最优"矩形。
        # 原因：图形可能由多个 drawing 组成，单个 drawing 只覆盖局部（如橙色边框只覆盖下2/3），
        # 取 union 才能得到完整图形的上下边界。
        candidates = []
        for d in drawings:
            r = d.get('rect')
            if r is None:
                continue
            rw = r.x1 - r.x0
            rh = r.y1 - r.y0
            # rw 阈值：min(col_width*0.1, 20pt) 取较小值，确保最大不超过 20pt
            # - 单栏（col_width≈280）：0.1*280=28pt → 取 20pt，适度过滤噪声
            # - 跨栏（col_width≈572）：0.1*572=57pt 过严 → 取 20pt，保留顶部细小 drawing
            if rw < min(col_width * 0.1, 20) or rh < 20:
                continue
            r_cx = (r.x0 + r.x1) / 2
            if not (col_x0 - 20 <= r_cx <= col_x1 + 20):
                continue
            if search_above:
                # 上界用 search_top（前一个 Caption 底部），而非固定 200pt
                # 固定 200pt 会把高度 > 200pt 的大图顶部 drawing 错误排除
                if r.y0 < search_top or r.y0 >= cap_rect.y0:
                    continue
            else:
                if r.y0 > cap_rect.y1 + 200 or r.y1 <= cap_rect.y1:
                    continue
            candidates.append(r)

        if not candidates:
            return None

        # 取所有候选的包围盒（union）
        union_x0 = min(r.x0 for r in candidates)
        union_y0 = min(r.y0 for r in candidates)
        union_x1 = max(r.x1 for r in candidates)
        union_y1 = max(r.y1 for r in candidates)
        return fitz.Rect(union_x0, union_y0, union_x1, union_y1)

    def _determine_crop_rect(self, hit: Dict, caption_hits: List[Dict],
                              page_rect: "fitz.Rect",
                              col_x0: float, col_x1: float,
                              page: "fitz.Page" = None) -> "fitz.Rect":
        """
        根据 Caption 位置和类型确定裁剪矩形。
        优先策略：用 get_drawings() 找图形/算法框的实际边界矩形。
        降级策略：用同栏 Caption 位置估算边界。
        """
        cap_rect = hit["rect"]

        is_algorithm = hit.get("is_algorithm", False)

        if hit["is_table"]:
            # Table：Caption 在上方，内容在下方
            bbox = None
            if page is not None:
                bbox = self._find_content_bbox_via_drawings(
                    page, cap_rect, col_x0, col_x1,
                    search_above=False, is_algorithm=False
                )
            if bbox is not None:
                return fitz.Rect(
                    min(col_x0, bbox.x0 - 3),
                    cap_rect.y0 - 3,
                    max(col_x1, bbox.x1 + 3),
                    bbox.y1 + 5
                )
            # 降级：用下一个同栏 Caption
            same_col_hits = [
                h for h in caption_hits
                if h is not hit and self._in_same_column(h["rect"], col_x0, col_x1)
            ]
            next_ys = [h["rect"].y0 for h in same_col_hits if h["rect"].y0 > cap_rect.y1 + 10]
            bottom = (min(next_ys) - 5) if next_ys else (page_rect.y1 - 20)
            return fitz.Rect(col_x0, cap_rect.y0 - 3, col_x1, bottom)

        else:
            # Figure/Algorithm：Caption 在下方，内容在上方（或 Caption 是框的第一行）
            # 先计算 coarse_top（前一个同栏 Caption 底部），用于限制 drawing 搜索范围
            same_col_hits = [
                h for h in caption_hits
                if h is not hit and self._in_same_column(h["rect"], col_x0, col_x1)
            ]
            prev_ys = [h["rect"].y1 for h in same_col_hits if h["rect"].y1 < cap_rect.y0 - 10]
            coarse_top = (max(prev_ys) + 5) if prev_ys else (page_rect.y0 + 20)

            bbox = None
            if page is not None:
                bbox = self._find_content_bbox_via_drawings(
                    page, cap_rect, col_x0, col_x1,
                    search_above=True, search_top=coarse_top,
                    is_algorithm=is_algorithm
                )
            if bbox is not None:
                # bbox.y1 可能超过 Caption（Algorithm 框内容在 Caption 下方）
                # 取 bbox 整体范围，确保内容完整
                crop_top = bbox.y0 - 3

                # Figure 路径：向上扫描 bbox.y0 上方 30pt 内的短文本标签
                # 部分图片顶部由文本标签组成（如 "Output"、"VIRTUAL STAGE"），
                # Strategy 2 只扫描 drawing，会遗漏这些文本标签。
                # 条件：① 在 bbox.y0 上方 30pt 内；② x 范围与 bbox 有实质重叠；
                #       ③ avg_line_len < 30（排除正文段落，只纳入图片内短标签）
                if not is_algorithm and page is not None:
                    try:
                        blocks = page.get_text("blocks")
                        for b in blocks:
                            if len(b) < 5 or b[6] != 0:
                                continue
                            bx0, by0, bx1, by1 = b[0], b[1], b[2], b[3]
                            if by0 >= bbox.y0 or by0 < bbox.y0 - 30:
                                continue
                            # x 范围与 bbox 有实质重叠（各自内缩 10pt 避免边界误判）
                            if bx1 <= bbox.x0 + 10 or bx0 >= bbox.x1 - 10:
                                continue
                            text = b[4].strip() if len(b) > 4 else ""
                            lines = [l for l in text.split('\n') if l.strip()]
                            avg_len = len(text) / max(len(lines), 1)
                            if avg_len < 30:
                                crop_top = min(crop_top, by0 - 3)
                    except Exception:
                        pass

                return fitz.Rect(
                    min(col_x0, bbox.x0 - 3),
                    crop_top,
                    max(col_x1, bbox.x1 + 3),
                    max(cap_rect.y1 + 3, bbox.y1 + 5)
                )
            # 降级：用 coarse_top，x 范围保持栏宽（不收紧，避免裁掉跨栏图的边缘内容）
            return fitz.Rect(col_x0, coarse_top, col_x1, cap_rect.y1 + 3)

    # 图片类型优先级（数字越小越重要），用于数量限制时的筛选
    _TYPE_PRIORITY = {
        'algorithm': 0,
        'table': 1,
        'architecture': 2,
        'performance': 3,
        'figure': 4,
    }
    # 全局最大保留图片数（跨所有页面）
    MAX_TOTAL_IMAGES = 12
    # 每页最多保留图片数
    MAX_PER_PAGE = 4

    def _classify_caption(self, caption: str) -> str:
        """
        根据 Caption 文本分类图片类型，供优先级排序用。
        顺序：Algorithm/Table（前缀精确匹配）> 语义关键词（performance > architecture）> 通用 figure
        注意：performance 关键词检查在 architecture 之前，避免 'convergence curves' 被误判为 architecture。
        """
        c = caption.lower()
        # 1. 前缀精确匹配
        if re.match(r'(algorithm|alg\.?)\s*\d+', c):
            return 'algorithm'
        if re.match(r'(table|tab\.?)\s*\d+', c):
            return 'table'
        if re.match(r'(listing|scheme)\s*\d+', c):
            return 'algorithm'
        # 2. 语义关键词：performance 优先（曲线图、对比图常见于 Figure caption）
        if re.search(r'convergence|result|performance|comparison|accuracy|loss|curve|ablation|f1|precision|recall', c):
            return 'performance'
        # 3. 架构/框架图
        # 移除 'model'：该词在 performance/distribution 图 caption 中极常见，
        # 不足以判断是系统架构图，保留更具体的结构性词汇
        if re.search(r'architecture|framework|overview|pipeline|structure|illustration|system', c):
            return 'architecture'
        return 'figure'

    def _extend_crop_for_algorithm(self, crop_rect: "fitz.Rect",
                                    page: "fitz.Page",
                                    next_caption_y: float) -> "fitz.Rect":
        """
        对 Algorithm/伪代码，向下扩展裁剪区域到伪代码实际底部。
        关键：遇到正文段落（长文本块，非伪代码行）时立即停止，避免将正文包含进来。
        伪代码行特征：行短（< 120 字符/行），以行号/关键字开头。
        正文段落特征：文字块包含多行且总长 > 200 字符，或单行 > 120 字符。
        """
        try:
            blocks = page.get_text("blocks")
        except Exception:
            return crop_rect

        # 收集在裁剪栏内、Caption 下方到 next_caption_y 之间的文字块，按 y 排序
        col_x0, col_x1 = crop_rect.x0, crop_rect.x1
        candidate_blocks = []
        for b in blocks:
            if len(b) < 5:
                continue
            bx0, by0, bx1, by1 = b[0], b[1], b[2], b[3]
            block_text = b[4].strip() if len(b) > 4 else ""
            if not block_text:
                continue
            # 块在 Caption 下方（crop_rect.y1 是 Caption 底部 + 3）
            if by0 < crop_rect.y1 - 5:
                continue
            # 块在 next_caption_y 以上
            if by1 > next_caption_y - 5:
                continue
            # 块 x 范围严格在当前栏内（不允许跨栏文字）
            if bx0 < col_x0 - 5 or bx1 > col_x1 + 5:
                continue
            candidate_blocks.append((by0, by1, block_text))

        candidate_blocks.sort(key=lambda b: b[0])

        algo_bottom = crop_rect.y1
        prev_block_bottom = crop_rect.y1
        for (by0, by1, text) in candidate_blocks:
            lines = [l for l in text.split('\n') if l.strip()]
            avg_line_len = len(text) / max(len(lines), 1)
            gap = by0 - prev_block_bottom

            # 停止条件：
            # 1. 行平均长度 > 40 → 正文段落
            # 2. 与上一块间隙 > 25pt 且行平均长度 > 25 → 伪代码已结束，后面是正文
            # 3. 全大写单词行（节标题，如 APPENDIX、REFERENCES、ACKNOWLEDGMENT）
            # 4. 参考文献条目（以 [数字] 开头）
            if avg_line_len > 40:
                break
            if gap > 25 and avg_line_len > 25:
                break
            if re.match(r'^[A-Z][A-Z\s\-]{3,}$', text.strip()):
                break
            if re.match(r'^\[\d+\]', text.strip()):
                break

            # 伪代码行：继续扩展
            algo_bottom = max(algo_bottom, by1)
            prev_block_bottom = by1

        if algo_bottom > crop_rect.y1:
            return fitz.Rect(crop_rect.x0, crop_rect.y0, crop_rect.x1, algo_bottom + 10)
        return crop_rect

    def _extract_figure_regions(self, doc: fitz.Document,
                                 page_numbers: Set[int],
                                 image_dir: Path) -> List[Dict]:
        """
        对指定页面，精准裁剪每个 Figure/Table/Algorithm 区域。
        改进：
        - 严格 Caption 识别，避免正文引用被裁剪
        - 同栏边界计算，避免跨栏干扰
        - Algorithm 向下扩展，避免伪代码只截标题
        - 数量限制，只保留最重要的图片
        """
        all_candidates = []  # 收集所有候选，最后统一筛选
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)
        MIN_WIDTH, MIN_HEIGHT = 200, 100

        for page_num in sorted(page_numbers):
            page = doc[page_num - 1]
            caption_hits = self._collect_caption_rects(page)

            if not caption_hits:
                logger.info(f"  page{page_num}: 未找到 Caption，跳过（不再整页渲染）")
                continue

            columns = self._detect_columns(page)
            page_candidates = []

            for idx, hit in enumerate(caption_hits):
                cap_rect = hit["rect"]
                img_type = self._classify_caption(hit["text"])

                # 确定 Caption 所在的栏
                cap_center_x = (cap_rect.x0 + cap_rect.x1) / 2
                col_x0, col_x1 = columns[0]
                for (cx0, cx1) in columns:
                    if cx0 <= cap_center_x <= cx1:
                        col_x0, col_x1 = cx0, cx1
                        break

                # 跨栏检测：几何法——caption 同时跨越左栏右边界和右栏左边界
                # 比宽度阈值法更稳健，避免 caption 宽度恰好在阈值附近时误判
                # margin=5pt 防止浮点精度导致边界列的 caption 被误判为跨栏
                if len(columns) > 1:
                    left_col_x1 = columns[0][1]
                    right_col_x0 = columns[1][0]
                    if cap_rect.x0 < left_col_x1 - 5 and cap_rect.x1 > right_col_x0 + 5:
                        col_x0 = page.rect.x0 + 20
                        col_x1 = page.rect.x1 - 20

                crop_rect = self._determine_crop_rect(
                    hit, caption_hits, page.rect, col_x0, col_x1, page
                )

                # 合法性检查
                if (crop_rect.is_empty
                        or crop_rect.width < 50
                        or crop_rect.height < 50):
                    continue

                # Algorithm/伪代码：向下扩展到实际内容底部
                if img_type == 'algorithm':
                    # 下一个 Caption 的 y0 作为扩展上限
                    same_col_hits = [
                        h for h in caption_hits
                        if h is not hit and self._in_same_column(h["rect"], col_x0, col_x1)
                        and h["rect"].y0 > cap_rect.y1 + 10
                    ]
                    next_cap_y = (min(h["rect"].y0 for h in same_col_hits)
                                  if same_col_hits else page.rect.y1 - 20)
                    crop_rect = self._extend_crop_for_algorithm(crop_rect, page, next_cap_y)

                page_candidates.append({
                    "page": page_num,
                    "hit": hit,
                    "crop_rect": crop_rect,
                    "img_type": img_type,
                    "priority": self._TYPE_PRIORITY.get(img_type, 99),
                })

            # 每页最多保留 MAX_PER_PAGE 张，优先级高的优先
            page_candidates.sort(key=lambda c: c["priority"])
            all_candidates.extend(page_candidates[:self.MAX_PER_PAGE])

        # 全局最多保留 MAX_TOTAL_IMAGES 张，优先级高的优先
        all_candidates.sort(key=lambda c: c["priority"])
        selected = all_candidates[:self.MAX_TOTAL_IMAGES]

        # 按页码+idx 顺序渲染保存
        selected.sort(key=lambda c: (c["page"], c["hit"]["rect"].y0))

        results = []
        for entry in selected:
            page_num = entry["page"]
            page = doc[page_num - 1]
            crop_rect = entry["crop_rect"]
            hit = entry["hit"]

            try:
                pix = page.get_pixmap(matrix=mat, clip=crop_rect, alpha=False)
            except Exception as e:
                logger.warning(f"  page{page_num} 裁剪失败: {e}")
                continue

            if pix.width < MIN_WIDTH or pix.height < MIN_HEIGHT:
                continue

            image_filename = f"page{page_num}_fig{hit['text'][:20].replace(' ', '_')}.png"
            image_path = image_dir / image_filename
            pix.save(str(image_path))

            size_kb = image_path.stat().st_size / 1024
            results.append({
                "page": page_num,
                "path": str(image_path),
                "caption": hit["text"],
                "width": pix.width,
                "height": pix.height,
                "size_kb": size_kb,
                "rendered": True,
                "cropped": True,
            })
            logger.info(f"  裁剪 page{page_num} [{entry['img_type']}]: {hit['text'][:60]}")

        logger.info(f"精准裁剪完成：候选 {len(all_candidates)} 张，保留 {len(results)} 张")
        return results

    def _render_single_page(self, doc: fitz.Document, page_num: int,
                             image_dir: Path) -> Dict:
        """单页整体渲染（降级用）"""
        try:
            page = doc[page_num - 1]
            zoom = 2.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            image_filename = f"page{page_num}_rendered.png"
            image_path = image_dir / image_filename
            pix.save(str(image_path))

            return {
                "page": page_num,
                "path": str(image_path),
                "caption": "",
                "width": pix.width,
                "height": pix.height,
                "size_kb": image_path.stat().st_size / 1024,
                "rendered": True,
                "cropped": False,
            }
        except Exception as e:
            logger.warning(f"  page{page_num} 整页渲染失败: {e}")
            return None

    def extract_images_to_disk(self, pdf_path: str, paper_id: int) -> List[Dict]:
        """
        提取图片并保存到磁盘。
        阶段 1：收集嵌入式光栅图候选（不立即写盘）
        阶段 2：收集矢量图页面精准裁剪候选
        最终：两阶段候选合并，按优先级统一筛选后写盘，总数不超过 MAX_TOTAL_IMAGES
        """
        doc = fitz.open(pdf_path)

        image_dir = Path(config.IMAGES_DIR) / str(paper_id)
        image_dir.mkdir(parents=True, exist_ok=True)

        MIN_WIDTH = 200
        MIN_HEIGHT = 150
        MIN_SIZE_KB = 10
        MIN_ASPECT_RATIO = 0.3
        MAX_ASPECT_RATIO = 5.0

        pages_with_raster = set()
        # 候选列表：每项包含 img_type / priority / 及写盘所需信息
        all_candidates = []

        # ===== 阶段 1：收集嵌入式光栅图候选 =====
        for page_num, page in enumerate(doc, start=1):
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                xref = img[0]
                try:
                    base_image = doc.extract_image(xref)
                except Exception:
                    continue
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                width = base_image.get("width", 0)
                height = base_image.get("height", 0)
                size_kb = len(image_bytes) / 1024
                aspect_ratio = width / height if height > 0 else 0

                if (width < MIN_WIDTH or
                        height < MIN_HEIGHT or
                        size_kb < MIN_SIZE_KB or
                        aspect_ratio < MIN_ASPECT_RATIO or
                        aspect_ratio > MAX_ASPECT_RATIO):
                    continue

                caption = self._find_caption_near_image(page, xref)

                # 光栅图必须找到严格 Caption 才保留，避免把正文截图/装饰图误收录
                if not caption:
                    logger.debug(
                        f"  page{page_num} img{img_index} 无 Caption，跳过"
                    )
                    continue

                img_type = self._classify_caption(caption)
                priority = self._TYPE_PRIORITY.get(img_type, 99)

                all_candidates.append({
                    "source": "raster",
                    "page": page_num,
                    "img_type": img_type,
                    "priority": priority,
                    "xref": xref,  # 用于跨页去重
                    # 写盘用
                    "image_bytes": image_bytes,
                    "image_ext": image_ext,
                    "img_index": img_index,
                    "caption": caption,
                    "width": width,
                    "height": height,
                    "size_kb": size_kb,
                })
                pages_with_raster.add(page_num)

        # ===== 阶段 2：收集矢量图页面精准裁剪候选 =====
        figure_pages = self._find_figure_pages(doc)
        pages_needing_render = set(figure_pages.keys()) - pages_with_raster

        if pages_needing_render:
            logger.info(
                f"发现 {len(pages_needing_render)} 个页面有 Caption 但无光栅图，"
                f"启用精准裁剪: {sorted(pages_needing_render)}"
            )
            # _extract_figure_regions 内部已做每页限制，直接收集结果
            cropped = self._extract_figure_regions(
                doc, pages_needing_render, image_dir
            )
            # 裁剪结果已写盘，直接加入最终列表（不再走统一筛选）
            # 但也要受总数限制，先放入 cropped_candidates
            for item in cropped:
                img_type = self._classify_caption(item.get("caption", ""))
                all_candidates.append({
                    "source": "cropped",
                    "page": item["page"],
                    "img_type": img_type,
                    "priority": self._TYPE_PRIORITY.get(img_type, 99),
                    "already_saved": True,
                    "result": item,
                })

        doc.close()

        # ===== 统一筛选：去重 + 按优先级排序，总数不超过 MAX_TOTAL_IMAGES =====
        # 去重策略：
        # 1. 相同 xref（同一嵌入图对象跨页引用）只保留第一次
        # 2. 相同 caption（网页打印 PDF 中同一图被截成两个不同 xref）只保留第一次
        seen_xrefs: set = set()
        seen_captions: set = set()
        deduped = []
        for cand in all_candidates:
            xref_key = cand.get("xref")
            caption_key = cand.get("caption", "").strip().lower()[:60]

            if xref_key is not None and xref_key in seen_xrefs:
                logger.debug(f"  去重(xref): page{cand['page']} xref={xref_key}")
                continue
            if caption_key and caption_key in seen_captions:
                logger.debug(f"  去重(caption): page{cand['page']} {caption_key[:40]}")
                continue

            if xref_key is not None:
                seen_xrefs.add(xref_key)
            if caption_key:
                seen_captions.add(caption_key)
            deduped.append(cand)

        deduped.sort(key=lambda c: (c["priority"], c["page"]))
        selected = deduped[:self.MAX_TOTAL_IMAGES]

        # 按页码顺序写盘
        selected.sort(key=lambda c: c["page"])

        saved_images = []
        for cand in selected:
            if cand.get("already_saved"):
                saved_images.append(cand["result"])
                continue

            # 光栅图写盘
            image_filename = (
                f"page{cand['page']}_img{cand['img_index']}.{cand['image_ext']}"
            )
            image_path = image_dir / image_filename
            with open(image_path, "wb") as f:
                f.write(cand["image_bytes"])

            saved_images.append({
                "page": cand["page"],
                "path": str(image_path),
                "caption": cand["caption"],
                "width": cand["width"],
                "height": cand["height"],
                "size_kb": cand["size_kb"],
            })
            logger.info(
                f"  保留光栅图 page{cand['page']} [{cand['img_type']}]: "
                f"{cand['caption'][:60]}"
            )

        logger.info(
            f"图片提取完成：候选 {len(all_candidates)} 张，"
            f"保留 {len(saved_images)} 张"
        )
        return saved_images

    def _render_figure_pages(
        self,
        doc: fitz.Document,
        page_numbers: Set[int],
        figure_pages: Dict[int, List[str]],
        image_dir: Path,
    ) -> List[Dict]:
        """将指定页面渲染为高分辨率图片（保留作为降级备用）"""
        rendered_images = []
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)

        for page_num in sorted(page_numbers):
            page = doc[page_num - 1]
            pix = page.get_pixmap(matrix=mat, alpha=False)

            image_filename = f"page{page_num}_rendered.png"
            image_path = image_dir / image_filename
            pix.save(str(image_path))

            captions = figure_pages.get(page_num, [])
            caption = captions[0] if captions else ""

            rendered_images.append({
                "page": page_num,
                "path": str(image_path),
                "caption": caption,
                "width": pix.width,
                "height": pix.height,
                "size_kb": image_path.stat().st_size / 1024,
                "rendered": True,
            })
            logger.info(f"  渲染页面 {page_num}: {caption[:60]}")

        return rendered_images


pdf_parser = PDFParser()

