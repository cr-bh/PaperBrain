"""
论文评分引擎
基于豆包 LLM 对论文进行深度评分
"""
from services.doubao_service import doubao_service
from utils.prompts import SCORE_PAPER_PROMPT, format_prompt
from typing import Dict


class ScoringEngine:
    """论文评分引擎"""

    def __init__(self):
        self.llm = doubao_service

    def score_paper(self, title: str, abstract: str) -> Dict:
        """
        对单篇论文打分

        Args:
            title: 论文标题
            abstract: 论文摘要

        Returns:
            评分结果字典 {
                'score': float,
                'reason': str,
                'title_zh': str,
                'abstract_zh': str,
                'tags': [str]
            }
        """
        try:
            # 格式化 Prompt
            prompt = format_prompt(
                SCORE_PAPER_PROMPT,
                title=title,
                abstract=abstract
            )

            # 调用豆包 LLM 生成评分
            result = self.llm.generate_json(prompt, temperature=0.3)

            # 验证必需字段
            required_fields = ['score', 'reason', 'title_zh', 'abstract_zh', 'tags']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"缺少必需字段: {field}")

            # 确保 score 在 1-10 范围内
            result['score'] = max(1.0, min(10.0, float(result['score'])))

            return result

        except Exception as e:
            error_msg = str(e)
            print(f"❌ 评分失败: {error_msg}")

            # 增强的兜底策略
            # 1. 如果是 JSON 提取失败，尝试使用更宽松的默认值
            if "无法从文本中提取有效的 JSON" in error_msg:
                print(f"    🔄 使用兜底评分（JSON 解析失败）")
                return {
                    'score': 5.0,
                    'reason': '评分系统暂时无法解析 LLM 响应，建议人工复核该论文',
                    'title_zh': title,  # 保留原标题
                    'abstract_zh': abstract[:200] + '...' if len(abstract) > 200 else abstract,  # 截断摘要
                    'tags': ['待分类']
                }

            # 2. 如果是其他错误（如 API 调用失败）
            return {
                'score': 5.0,
                'reason': f'评分失败（{error_msg[:50]}），建议人工复核',
                'title_zh': title,
                'abstract_zh': abstract[:200] + '...' if len(abstract) > 200 else abstract,
                'tags': ['待分类']
            }


# 创建全局评分引擎实例
scoring_engine = ScoringEngine()
