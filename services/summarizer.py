"""
论文总结服务
生成结构化的论文总结
"""
from services.llm_service import llm_service
from utils.prompts import SUMMARIZE_PAPER_PROMPT, format_prompt
from typing import Dict


class Summarizer:
    """论文总结器"""

    def __init__(self):
        self.llm = llm_service

    def summarize_paper(self, paper_text: str) -> Dict:
        """
        生成论文的结构化总结

        Args:
            paper_text: 论文全文文本

        Returns:
            结构化总结的 JSON 对象
        """
        # 如果文本过长，截取前 30000 字符
        if len(paper_text) > 30000:
            paper_text = paper_text[:30000] + "\n\n[文本已截断...]"

        # 格式化 Prompt
        prompt = format_prompt(SUMMARIZE_PAPER_PROMPT, paper_text=paper_text)

        # 调用 LLM 生成总结
        summary = self.llm.generate_json(prompt, temperature=0.3)

        return summary


# 创建全局总结器实例
summarizer = Summarizer()
