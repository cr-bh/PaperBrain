"""
Semantic Scholar 元数据筛选器
基于引用数、影响力等指标进行程序式筛选
支持缓存、重试和降级规则
"""
import requests
import time
import json
import re
from typing import Dict, List, Optional
from pathlib import Path
import config


class SemanticScholarFilter:
    """Semantic Scholar 筛选器（带缓存和重试机制）"""

    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.api_key = api_key or config.S2_API_KEY
        self.headers = {}
        if self.api_key:
            self.headers['x-api-key'] = self.api_key

        # 缓存配置
        self.cache_path = Path(config.S2_CACHE_PATH)
        self.cache = self._load_cache()

        # 重试配置
        self.max_retries = config.S2_MAX_RETRIES
        self.retry_delay = config.S2_RETRY_DELAY
        self.request_interval = config.S2_REQUEST_INTERVAL

        # 降级关键词（标准化后）
        self.fallback_keywords = [self._normalize_keyword(kw) for kw in config.S2_FALLBACK_KEYWORDS]

    def _load_cache(self) -> Dict:
        """加载缓存文件"""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"  ⚠️ 缓存加载失败: {e}")
                return {}
        return {}

    def _save_cache(self):
        """保存缓存到文件"""
        try:
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  ⚠️ 缓存保存失败: {e}")

    def _normalize_keyword(self, keyword: str) -> str:
        """
        标准化关键词（处理缩写和全称）

        Args:
            keyword: 原始关键词

        Returns:
            标准化后的关键词（小写，去除多余空格）
        """
        return keyword.strip().lower()

    def _match_keywords(self, text: str, keywords: List[str]) -> bool:
        """
        检查文本是否匹配任一关键词

        Args:
            text: 待检查的文本（标题+摘要）
            keywords: 关键词列表

        Returns:
            是否匹配
        """
        if not text:
            return False

        text_normalized = self._normalize_keyword(text)

        # 关键词映射表（处理缩写）
        keyword_aliases = {
            'llm': ['llm', 'large language model', 'large language models'],
            'nlp': ['nlp', 'natural language processing'],
            'cv': ['cv', 'computer vision'],
            'rl': ['rl', 'reinforcement learning'],
            'ml': ['ml', 'machine learning'],
            'dl': ['dl', 'deep learning'],
        }

        for keyword in keywords:
            # 检查是否有别名
            aliases = keyword_aliases.get(keyword, [keyword])

            for alias in aliases:
                # 使用单词边界匹配，避免部分匹配
                pattern = r'\b' + re.escape(alias) + r'\b'
                if re.search(pattern, text_normalized):
                    return True

        return False

    def get_paper_metadata(self, arxiv_id: str) -> Optional[Dict]:
        """
        通过 arxiv_id 获取论文元数据（带缓存和重试）

        Args:
            arxiv_id: Arxiv ID (如 2401.12345)

        Returns:
            论文元数据字典，失败返回 None
        """
        # 检查缓存
        if arxiv_id in self.cache:
            return self.cache[arxiv_id]

        # 指数退避重试
        for attempt in range(self.max_retries):
            try:
                url = f"{self.base_url}/paper/ARXIV:{arxiv_id}"
                params = {
                    'fields': 'citationCount,influentialCitationCount,year,venue,authors.name,authors.affiliations,title,abstract'
                }

                response = requests.get(url, headers=self.headers, params=params, timeout=10)

                if response.status_code == 200:
                    metadata = response.json()
                    # 保存到缓存
                    self.cache[arxiv_id] = metadata
                    self._save_cache()
                    return metadata

                elif response.status_code == 404:
                    # 论文未被 S2 收录（可能是新论文）
                    self.cache[arxiv_id] = None
                    self._save_cache()
                    return None

                elif response.status_code == 429:
                    # 速率限制，使用指数退避
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay * (2 ** attempt)
                        print(f"  ⚠️ S2 API 速率限制 (429)，{delay}秒后重试... (尝试 {attempt + 1}/{self.max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        print(f"  ⚠️ S2 API 错误 429: {arxiv_id} (已达最大重试次数)")
                        return None

                else:
                    print(f"  ⚠️ S2 API 错误 {response.status_code}: {arxiv_id}")
                    return None

            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    print(f"  ⚠️ S2 查询异常: {str(e)}，{delay}秒后重试...")
                    time.sleep(delay)
                    continue
                else:
                    print(f"  ⚠️ S2 查询失败: {str(e)}")
                    return None

        return None

    def should_keep_paper(self,
                         metadata: Optional[Dict],
                         paper_info: Optional[Dict] = None,
                         min_citations: int = 3,
                         min_influential: int = 1,
                         min_year: int = 2022) -> bool:
        """
        判断是否保留论文（带降级规则）

        Args:
            metadata: S2 元数据
            paper_info: 论文基本信息（包含 title, summary 用于关键词匹配）
            min_citations: 最小引用数
            min_influential: 最小影响力引用数
            min_year: 最早年份

        Returns:
            是否保留
        """
        # 如果 S2 有数据，使用标准规则
        if metadata is not None:
            citation_count = metadata.get('citationCount', 0)
            influential_count = metadata.get('influentialCitationCount', 0)
            year = metadata.get('year', 2024)

            # 新论文（2024+）放宽标准
            if year >= 2024:
                return True

            # 旧论文需要有一定引用
            if citation_count >= min_citations or influential_count >= min_influential:
                return True

            return False

        # S2 没有数据，使用降级规则
        print(f"    🔄 使用降级规则判断...")

        # 规则1: 年份规则（从 paper_info 或 metadata 获取）
        year = None
        if metadata:
            year = metadata.get('year')
        if not year and paper_info:
            # 尝试从 arxiv_id 提取年份 (格式: YYMM.NNNNN)
            arxiv_id = paper_info.get('arxiv_id', '')
            if arxiv_id:
                try:
                    year_prefix = arxiv_id.split('.')[0][:2]
                    year = 2000 + int(year_prefix)
                except:
                    pass

        # 2024+ 年份的论文保留
        if year and year >= 2024:
            print(f"    ✅ 保留: 新论文 ({year}年)")
            return True

        # 规则2: 关键词匹配
        if paper_info:
            title = paper_info.get('title', '')
            summary = paper_info.get('summary', '')
            text = f"{title} {summary}"

            if self._match_keywords(text, self.fallback_keywords):
                print(f"    ✅ 保留: 匹配关键词")
                return True

        # 如果 metadata 中有 title 和 abstract，也检查
        if metadata:
            title = metadata.get('title', '')
            abstract = metadata.get('abstract', '')
            text = f"{title} {abstract}"

            if self._match_keywords(text, self.fallback_keywords):
                print(f"    ✅ 保留: 匹配关键词 (S2数据)")
                return True

        print(f"    ❌ 过滤: 不满足降级规则")
        return False

    def batch_filter(self, papers: List[Dict],
                    min_citations: int = 3,
                    min_influential: int = 1) -> List[Dict]:
        """
        批量筛选论文

        Args:
            papers: 论文列表（需包含 arxiv_id, title, summary）
            min_citations: 最小引用数
            min_influential: 最小影响力引用数

        Returns:
            筛选后的论文列表
        """
        filtered_papers = []

        for i, paper in enumerate(papers, 1):
            arxiv_id = paper['arxiv_id']
            print(f"  [{i}/{len(papers)}] S2 查询: {arxiv_id}")

            metadata = self.get_paper_metadata(arxiv_id)

            if self.should_keep_paper(metadata, paper, min_citations, min_influential):
                # 将 S2 元数据附加到论文
                paper['s2_metadata'] = metadata
                filtered_papers.append(paper)

            # 避免超过速率限制
            if i < len(papers):  # 最后一个不需要等待
                time.sleep(self.request_interval)

        return filtered_papers


# 创建全局筛选器实例
semantic_scholar_filter = SemanticScholarFilter()
