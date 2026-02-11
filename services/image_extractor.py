"""
图片提取服务
从 PDF 中提取关键图片
"""
from services.pdf_parser import pdf_parser
from database.db_manager import db_manager
import re
from typing import List


class ImageExtractor:
    """图片提取器"""

    def __init__(self):
        self.key_patterns = [
            r'Figure\s*\d+',
            r'Fig\.\s*\d+',
            r'Architecture',
            r'Performance',
            r'Algorithm',
            r'Model'
        ]

    def extract_key_images(self, pdf_path: str, paper_id: int) -> List[dict]:
        """
        提取论文中的关键图片

        Args:
            pdf_path: PDF 文件路径
            paper_id: 论文 ID

        Returns:
            关键图片信息列表
        """
        # 提取所有图片到磁盘
        all_images = pdf_parser.extract_images_to_disk(pdf_path, paper_id)

        # 筛选关键图片
        key_images = []
        for img in all_images:
            if self._is_key_image(img['caption']):
                # 保存到数据库
                db_manager.add_image_to_paper(
                    paper_id=paper_id,
                    image_path=img['path'],
                    caption=img['caption'],
                    page_number=img['page'],
                    image_type=self._classify_image_type(img['caption'])
                )
                key_images.append(img)

        return key_images

    def _is_key_image(self, caption: str) -> bool:
        """判断是否为关键图片"""
        if not caption:
            return False

        for pattern in self.key_patterns:
            if re.search(pattern, caption, re.IGNORECASE):
                return True
        return False

    def _classify_image_type(self, caption: str) -> str:
        """分类图片类型"""
        caption_lower = caption.lower()
        if 'architecture' in caption_lower or 'framework' in caption_lower:
            return 'architecture'
        elif 'performance' in caption_lower or 'result' in caption_lower:
            return 'performance'
        elif 'algorithm' in caption_lower:
            return 'algorithm'
        else:
            return 'other'


# 创建全局图片提取器实例
image_extractor = ImageExtractor()
