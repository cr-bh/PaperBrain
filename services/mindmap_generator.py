"""
思维导图生成服务
基于论文总结生成 Mermaid.js 代码
"""
from services.llm_service import llm_service
from utils.prompts import GENERATE_MINDMAP_PROMPT, format_prompt
import json


class MindmapGenerator:
    """思维导图生成器"""

    def __init__(self):
        self.llm = llm_service

    def generate_mindmap(self, summary: dict) -> str:
        """
        基于论文总结生成思维导图

        Args:
            summary: 论文总结的 JSON 对象

        Returns:
            Mermaid.js 代码字符串
        """
        # 将总结转换为 JSON 字符串
        summary_json = json.dumps(summary, ensure_ascii=False, indent=2)

        # 格式化 Prompt
        prompt = format_prompt(GENERATE_MINDMAP_PROMPT, summary_json=summary_json)

        # 调用 LLM 生成思维导图
        mindmap_code = self.llm.generate_text(prompt, temperature=0.5)

        # 清理可能的 markdown 代码块标记
        mindmap_code = mindmap_code.strip()
        if mindmap_code.startswith("```"):
            lines = mindmap_code.split('\n')
            mindmap_code = '\n'.join(lines[1:-1]) if len(lines) > 2 else mindmap_code

        # 验证生成的代码
        if not mindmap_code or len(mindmap_code) < 10:
            print(f"警告: 生成的思维导图代码过短或为空，长度: {len(mindmap_code)}")
            return self._generate_fallback_mindmap(summary)

        # 检查是否是有效的 Mermaid 代码
        if not (mindmap_code.startswith("graph") or mindmap_code.startswith("mindmap") or mindmap_code.startswith("flowchart")):
            print(f"警告: 生成的代码不是有效的 Mermaid 格式，前50字符: {mindmap_code[:50]}")
            return self._generate_fallback_mindmap(summary)

        print(f"✓ 成功生成思维导图，代码长度: {len(mindmap_code)}")
        return mindmap_code

    def _generate_fallback_mindmap(self, summary: dict) -> str:
        """
        生成备用的简单思维导图

        Args:
            summary: 论文总结

        Returns:
            简单的 Mermaid 代码
        """
        title = summary.get('title', '论文')
        summary_struct = summary.get('summary_struct', {})

        # 生成简单的思维导图
        mindmap = f"""graph LR
    A[{title}]
    A --> B[研究问题]
    A --> C[方法]
    A --> D[贡献]
    A --> E[结果]
"""

        if summary_struct.get('problem_definition'):
            mindmap += f"    B --> B1[{summary_struct['problem_definition'][:30]}...]\n"
        if summary_struct.get('methodology'):
            mindmap += f"    C --> C1[{summary_struct['methodology'][:30]}...]\n"
        if summary_struct.get('contribution'):
            mindmap += f"    D --> D1[{summary_struct['contribution'][:30]}...]\n"
        if summary_struct.get('results'):
            mindmap += f"    E --> E1[{summary_struct['results'][:30]}...]\n"

        return mindmap


# 创建全局思维导图生成器实例
mindmap_generator = MindmapGenerator()
