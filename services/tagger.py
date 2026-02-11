"""
自动标签生成服务
基于论文总结生成多维度标签
"""
from services.llm_service import llm_service
from utils.prompts import GENERATE_TAGS_PROMPT, format_prompt
from database.db_manager import db_manager
import json
from typing import List, Dict


class Tagger:
    """标签生成器"""

    def __init__(self):
        self.llm = llm_service

    def generate_tags(self, summary: dict) -> Dict[str, List[str]]:
        """
        基于论文总结生成标签

        Args:
            summary: 论文总结的 JSON 对象

        Returns:
            标签字典，包含 domain, methodology, task 三个维度
        """
        # 将总结转换为 JSON 字符串
        summary_json = json.dumps(summary, ensure_ascii=False, indent=2)

        # 格式化 Prompt
        prompt = format_prompt(GENERATE_TAGS_PROMPT, summary_json=summary_json)

        # 调用 LLM 生成标签
        tags = self.llm.generate_json(prompt, temperature=0.3)

        return tags

    def save_tags_to_db(self, paper_id: int, tags_dict: Dict[str, List[str]]):
        """
        将标签保存到数据库并关联到论文

        Args:
            paper_id: 论文 ID
            tags_dict: 标签字典
        """
        for category, tag_names in tags_dict.items():
            for tag_name in tag_names:
                # 创建或获取标签
                tag = db_manager.create_tag(name=tag_name, category=category)
                # 关联到论文
                db_manager.add_tag_to_paper(paper_id, tag.id)


# 创建全局标签生成器实例
tagger = Tagger()
