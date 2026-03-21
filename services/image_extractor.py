"""
图片提取服务
从 PDF 中提取关键图片
"""
from services.pdf_parser import pdf_parser
from database.db_manager import db_manager
import re
import os
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
        # 提取所有图片到磁盘（已经过滤了太小的图片和异常宽高比）
        all_images = pdf_parser.extract_images_to_disk(pdf_path, paper_id)

        # 所有通过尺寸过滤的图片都保存到数据库
        # 不再依赖 caption 过滤，因为 caption 匹配不准确
        key_images = []
        for img in all_images:
            # 保存到数据库
            db_manager.add_image_to_paper(
                paper_id=paper_id,
                image_path=img['path'],
                caption=img.get('caption', ''),
                page_number=img['page'],
                image_type=self._classify_image_type(img.get('caption', ''))
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
        """分类图片类型，基于 Caption 文本精准分类。与 pdf_parser._classify_caption 保持一致。"""
        c = caption.lower()
        if re.match(r'(algorithm|alg\.?)\s*\d+', c):
            return 'algorithm'
        elif re.match(r'(table|tab\.?)\s*\d+', c):
            return 'table'
        elif re.match(r'(listing|scheme)\s*\d+', c):
            return 'algorithm'
        elif re.search(r'convergence|result|performance|comparison|accuracy|loss|curve|ablation|f1|precision|recall', c):
            return 'performance'
        elif re.search(r'architecture|framework|overview|pipeline|structure|model|illustration|system', c):
            return 'architecture'
        else:
            return 'figure'


# 创建全局图片提取器实例
image_extractor = ImageExtractor()
