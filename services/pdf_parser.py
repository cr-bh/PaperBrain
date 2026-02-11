"""
PDF 解析服务
使用 PyMuPDF 提取 PDF 内容
"""
import fitz  # PyMuPDF
from typing import Dict, List, Tuple
from pathlib import Path
import config


class PDFParser:
    """PDF 解析器"""

    def __init__(self):
        pass

    def parse_pdf(self, pdf_path: str) -> Dict:
        """
        解析 PDF 文件

        Args:
            pdf_path: PDF 文件路径

        Returns:
            包含文本、元数据和图片信息的字典
        """
        doc = fitz.open(pdf_path)

        # 提取全文文本
        full_text = self._extract_text(doc)

        # 提取元数据
        metadata = self._extract_metadata(doc)

        # 提取图片信息
        images_info = self._extract_images_info(doc)

        # 获取页面数量（在关闭文档之前）
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
        """
        提取图片信息（不保存图片，只记录位置和 Caption）

        Returns:
            图片信息列表
        """
        images_info = []

        for page_num, page in enumerate(doc, start=1):
            # 获取页面上的图片
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                # 尝试查找图片附近的文本作为 Caption
                caption = self._find_image_caption(page, img_index)

                images_info.append({
                    "page": page_num,
                    "index": img_index,
                    "caption": caption,
                    "xref": img[0]  # 图片引用
                })

        return images_info

    def _find_image_caption(self, page: fitz.Page, img_index: int) -> str:
        """
        尝试查找图片的 Caption
        通过查找页面文本中的 "Figure X", "Fig. X" 等模式
        """
        text = page.get_text()
        lines = text.split('\n')

        # 查找包含 Figure 或 Fig 的行
        import re
        for line in lines:
            if re.search(r'(Figure|Fig\.?)\s*\d+', line, re.IGNORECASE):
                return line.strip()

        return ""

    def extract_images_to_disk(self, pdf_path: str, paper_id: int) -> List[Dict]:
        """
        提取图片并保存到磁盘

        Args:
            pdf_path: PDF 文件路径
            paper_id: 论文 ID

        Returns:
            保存的图片信息列表
        """
        doc = fitz.open(pdf_path)
        saved_images = []

        # 创建图片保存目录
        image_dir = Path(config.IMAGES_DIR) / str(paper_id)
        image_dir.mkdir(parents=True, exist_ok=True)

        for page_num, page in enumerate(doc, start=1):
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # 保存图片
                image_filename = f"page{page_num}_img{img_index}.{image_ext}"
                image_path = image_dir / image_filename

                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                # 查找 Caption
                caption = self._find_image_caption(page, img_index)

                saved_images.append({
                    "page": page_num,
                    "path": str(image_path),
                    "caption": caption
                })

        doc.close()
        return saved_images


# 创建全局 PDF 解析器实例
pdf_parser = PDFParser()
