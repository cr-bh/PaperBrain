"""
论文评分引擎
基于豆包 LLM 对论文进行深度评分
"""
from services.doubao_service import doubao_service
from utils.prompts import SCORE_PAPER_PROMPT, format_prompt
from typing import Dict
import sys
import os

# 添加项目路径以导入 config 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.venues import normalize_venue_name, is_top_venue
from config.institutions import normalize_institution_name, is_top_institution


class ScoringEngine:
    """论文评分引擎"""

    def __init__(self):
        self.llm = doubao_service

    def score_paper(self, title: str, abstract: str, authors: list = None, s2_metadata: dict = None,
                    arxiv_id: str = None, pre_extracted_venue: str = None, pre_extracted_venue_year: int = None,
                    pre_extracted_institutions: list = None) -> Dict:
        """
        对单篇论文打分

        Args:
            title: 论文标题
            abstract: 论文摘要
            authors: 作者列表（可选），格式为 [{'name': str, 'affiliation': str}, ...]
            s2_metadata: Semantic Scholar 元数据（可选），包含 venue, authors.affiliations 等
            arxiv_id: ArXiv ID（可选），用于从 PDF 提取 venue 和 institutions
            pre_extracted_venue: 已提取的 venue（可选），如果提供则跳过 PDF 提取
            pre_extracted_venue_year: 已提取的 venue_year（可选）
            pre_extracted_institutions: 已提取的 institutions（可选）

        Returns:
            评分结果字典 {
                'score': float,
                'reason': str,
                'title_zh': str,
                'abstract_zh': str,
                'tags': [str],
                'venue': str,
                'venue_year': int,
                'institutions': [str]
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

            # 处理 venue 字段（优先级：预提取 > PDF > S2 > LLM）
            venue = ''
            venue_year = None
            pdf_institutions_normalized = []

            # 1. 最优先：使用预提取的 venue（避免重复 PDF 解析）
            if pre_extracted_venue:
                normalized_venue = normalize_venue_name(pre_extracted_venue)
                if is_top_venue(normalized_venue):
                    venue = normalized_venue
                    venue_year = pre_extracted_venue_year
                    print(f"  ✓ 使用预提取的 venue: {venue} {venue_year}")

            # 2. 如果没有预提取，且有 arxiv_id，尝试从 PDF 提取
            if not venue and arxiv_id:
                try:
                    from services.pdf_metadata_extractor import extract_from_arxiv_pdf
                    print(f"  📄 尝试从 PDF 提取 venue 和 institutions...")
                    pdf_venue, pdf_year, pdf_institutions = extract_from_arxiv_pdf(arxiv_id)

                    if pdf_venue:
                        normalized_venue = normalize_venue_name(pdf_venue)
                        if is_top_venue(normalized_venue):
                            venue = normalized_venue
                            venue_year = pdf_year
                            print(f"  ✓ PDF 提取成功: {venue} {venue_year}")

                    # 保存 PDF 提取的机构信息，稍后使用
                    for inst in pdf_institutions:
                        normalized = normalize_institution_name(inst)
                        if is_top_institution(normalized) and normalized not in pdf_institutions_normalized:
                            pdf_institutions_normalized.append(normalized)

                except Exception as e:
                    print(f"  ⚠️ PDF 提取失败: {str(e)}")

            # 3. 如果 PDF 也没有，尝试使用 Semantic Scholar 的 venue 数据
            if not venue and s2_metadata and s2_metadata.get('venue'):
                s2_venue = s2_metadata.get('venue', '')
                if s2_venue:
                    normalized_venue = normalize_venue_name(s2_venue)
                    if is_top_venue(normalized_venue):
                        venue = normalized_venue
                        # 尝试从 S2 获取年份
                        if s2_metadata.get('year'):
                            venue_year = int(s2_metadata['year'])

            # 4. 如果 S2 也没有，尝试从 LLM 结果中提取
            if not venue:
                llm_venue = result.get('venue', '')
                if llm_venue:
                    normalized_venue = normalize_venue_name(llm_venue)
                    if is_top_venue(normalized_venue):
                        venue = normalized_venue
                        # 使用 LLM 提取的年份
                        llm_year = result.get('venue_year')
                        if llm_year and isinstance(llm_year, (int, float)):
                            venue_year = int(llm_year)

            result['venue'] = venue
            result['venue_year'] = venue_year

            # 处理 institutions 字段（优先级：预提取 > PDF > S2 > LLM > arXiv authors）
            normalized_institutions = []

            # 1. 最优先：使用预提取的 institutions
            if pre_extracted_institutions:
                for inst in pre_extracted_institutions:
                    normalized = normalize_institution_name(inst)
                    if is_top_institution(normalized) and normalized not in normalized_institutions:
                        normalized_institutions.append(normalized)
                if normalized_institutions:
                    print(f"  ✓ 使用预提取的机构: {normalized_institutions}")

            # 2. 如果没有预提取，使用 PDF 提取的机构
            if not normalized_institutions and pdf_institutions_normalized:
                normalized_institutions = pdf_institutions_normalized
                print(f"  ✓ 使用 PDF 提取的机构: {normalized_institutions}")

            # 3. 如果 PDF 也没有，尝试从 Semantic Scholar 的 authors.affiliations 提取
            if not normalized_institutions and s2_metadata and s2_metadata.get('authors'):
                for author in s2_metadata['authors']:
                    affiliations = author.get('affiliations', [])
                    for affiliation in affiliations:
                        if isinstance(affiliation, dict):
                            inst_name = affiliation.get('name', '')
                        else:
                            inst_name = str(affiliation)

                        if inst_name:
                            normalized = normalize_institution_name(inst_name)
                            if is_top_institution(normalized) and normalized not in normalized_institutions:
                                normalized_institutions.append(normalized)

            # 4. 如果 S2 也没有，尝试从 LLM 结果中提取
            if not normalized_institutions:
                llm_institutions = result.get('institutions', [])
                if isinstance(llm_institutions, list):
                    for inst in llm_institutions:
                        if inst:
                            normalized = normalize_institution_name(str(inst))
                            if is_top_institution(normalized) and normalized not in normalized_institutions:
                                normalized_institutions.append(normalized)

            # 5. 如果还是没有，尝试从 authors 参数中提取（arXiv 数据）
            if not normalized_institutions and authors:
                from config.institutions import extract_institutions_from_authors
                normalized_institutions = extract_institutions_from_authors(authors)

            result['institutions'] = normalized_institutions[:5]  # 最多保留5个

            return result

        except Exception as e:
            error_msg = str(e)
            print(f"❌ 评分失败: {error_msg}")

            # 记录完整的错误堆栈信息
            import traceback
            full_traceback = traceback.format_exc()
            print(f"完整错误堆栈:\n{full_traceback}")

            # 增强的兜底策略
            # 1. 如果是 JSON 提取失败，尝试使用更宽松的默认值
            if "无法从文本中提取有效的 JSON" in error_msg:
                print(f"    🔄 使用兜底评分（JSON 解析失败）")
                return {
                    'score': 5.0,
                    'reason': '评分系统暂时无法解析 LLM 响应，建议人工复核该论文',
                    'title_zh': title,  # 保留原标题
                    'abstract_zh': abstract[:200] + '...' if len(abstract) > 200 else abstract,  # 截断摘要
                    'tags': ['待分类'],
                    'venue': '',
                    'venue_year': None,
                    'institutions': []
                }

            # 2. 如果是其他错误（如 API 调用失败）
            # 显示完整错误信息，不截断
            return {
                'score': 5.0,
                'reason': f'评分失败（{error_msg}），建议人工复核',
                'title_zh': title,
                'abstract_zh': abstract[:200] + '...' if len(abstract) > 200 else abstract,
                'tags': ['待分类'],
                'venue': '',
                'venue_year': None,
                'institutions': []
            }


# 创建全局评分引擎实例
scoring_engine = ScoringEngine()
