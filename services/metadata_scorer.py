"""
元数据评分器
基于论文元数据进行快速评分，无需调用 AI
用于多级筛选的 Layer 2
"""
from datetime import datetime
from typing import List, Dict


class MetadataScorer:
    """基于元数据的快速评分器（无AI调用）"""

    def __init__(self):
        # 高权重机构列表
        self.top_institutions = [
            'google', 'deepmind', 'openai', 'meta', 'microsoft', 'nvidia',
            'stanford', 'mit', 'berkeley', 'cmu', 'carnegie mellon',
            'tsinghua', 'peking', 'alibaba', 'tencent', 'baidu', 'meituan',
            'amazon', 'apple', 'ibm', 'huawei', 'bytedance',
            'eth zurich', 'oxford', 'cambridge', 'princeton', 'harvard'
        ]

        # 核心关键词权重（与用户研究兴趣相关）
        self.keyword_weights = {
            # 高权重 (OR + LLM 交叉)
            'neural combinatorial optimization': 3.0,
            'llm for optimization': 3.0,
            'large language model': 2.5,
            'vehicle routing': 2.5,
            'traveling salesman': 2.5,
            'mixed integer programming': 2.5,
            'combinatorial optimization': 2.5,
            'agent memory': 2.5,
            'agentic': 2.0,
            'reinforcement learning': 2.0,
            'operations research': 2.0,
            # 中权重
            'transformer': 1.5,
            'attention mechanism': 1.5,
            'graph neural network': 1.5,
            'meta-learning': 1.5,
            'multi-agent': 1.5,
            'deep learning': 1.0,
            'optimization': 1.0,
            'scheduling': 1.0,
            'routing': 1.0,
            # 低权重
            'machine learning': 0.5,
            'neural network': 0.5,
        }

    def score_paper(self, paper: Dict) -> float:
        """
        计算元数据分数 (0-10)

        评分维度:
        1. 关键词匹配度 (0-4分)
        2. 作者机构权重 (0-2分)
        3. 摘要质量指标 (0-2分)
        4. 时效性加分 (0-2分)

        Args:
            paper: 论文字典，包含 title, abstract, authors, published_date

        Returns:
            float: 0-10 的分数
        """
        score = 0.0
        text = (paper.get('title', '') + ' ' + paper.get('abstract', '')).lower()

        # 1. 关键词匹配度 (0-4分)
        keyword_score = 0.0
        matched_keywords = []
        for kw, weight in self.keyword_weights.items():
            if kw in text:
                keyword_score += weight
                matched_keywords.append(kw)
        score += min(4.0, keyword_score)

        # 2. 作者机构权重 (0-2分)
        institution_score = 0.0
        for author in paper.get('authors', []):
            if isinstance(author, dict):
                affiliation = author.get('affiliation', '').lower()
            else:
                affiliation = ''
            for inst in self.top_institutions:
                if inst in affiliation:
                    institution_score += 0.5
                    break  # 每个作者最多加一次
        score += min(2.0, institution_score)

        # 3. 摘要质量指标 (0-2分)
        abstract = paper.get('abstract', '')
        abstract_len = len(abstract)

        # 适中长度的摘要通常质量更好
        if 800 <= abstract_len <= 2000:
            score += 1.0
        elif abstract_len > 500:
            score += 0.5

        # 检查是否有量化结果（表明有实验验证）
        quantitative_indicators = [
            '%', 'improvement', 'outperform', 'sota', 'state-of-the-art',
            'baseline', 'benchmark', 'accuracy', 'f1', 'precision', 'recall'
        ]
        if any(ind in text for ind in quantitative_indicators):
            score += 0.5

        # 检查是否有方法论关键词
        methodology_indicators = [
            'propose', 'novel', 'framework', 'architecture', 'algorithm',
            'method', 'approach', 'model'
        ]
        if sum(1 for ind in methodology_indicators if ind in text) >= 2:
            score += 0.5

        # 4. 时效性加分 (0-0.5分) - 大幅降低权重
        # 注：由于用户主动选择抓取日期，时效性加分意义不大
        pub_date = paper.get('published_date')
        if pub_date:
            if isinstance(pub_date, str):
                try:
                    pub_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                except ValueError:
                    pub_date = None

            if pub_date:
                # 移除时区信息进行比较
                if hasattr(pub_date, 'replace'):
                    pub_date = pub_date.replace(tzinfo=None)
                days_ago = (datetime.now() - pub_date).days

                # 只给极新的论文少量加分（避免过度影响筛选）
                if days_ago <= 3:
                    score += 0.5
                elif days_ago <= 7:
                    score += 0.3

        return min(10.0, score)

    def batch_filter(self, papers: List[Dict], min_score: float = 4.0) -> List[Dict]:
        """
        批量筛选，返回分数 >= min_score 的论文

        Args:
            papers: 论文列表
            min_score: 最低分数阈值

        Returns:
            筛选后的论文列表（按分数降序）
        """
        scored_papers = []
        for paper in papers:
            meta_score = self.score_paper(paper)
            paper['meta_score'] = meta_score
            if meta_score >= min_score:
                scored_papers.append(paper)

        # 按分数降序排序
        return sorted(scored_papers, key=lambda x: x.get('meta_score', 0), reverse=True)

    def get_score_breakdown(self, paper: Dict) -> Dict:
        """
        获取评分详情（用于调试）

        Returns:
            包含各维度分数的字典
        """
        text = (paper.get('title', '') + ' ' + paper.get('abstract', '')).lower()

        # 关键词匹配
        matched_keywords = [kw for kw in self.keyword_weights if kw in text]
        keyword_score = sum(self.keyword_weights[kw] for kw in matched_keywords)

        # 机构匹配
        matched_institutions = []
        for author in paper.get('authors', []):
            if isinstance(author, dict):
                affiliation = author.get('affiliation', '').lower()
                for inst in self.top_institutions:
                    if inst in affiliation:
                        matched_institutions.append(inst)
                        break

        return {
            'total_score': self.score_paper(paper),
            'keyword_score': min(4.0, keyword_score),
            'matched_keywords': matched_keywords,
            'institution_score': min(2.0, len(matched_institutions) * 0.5),
            'matched_institutions': matched_institutions,
            'abstract_length': len(paper.get('abstract', '')),
        }


# 创建全局实例
metadata_scorer = MetadataScorer()
