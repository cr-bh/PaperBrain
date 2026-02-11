"""
Arxiv 爬虫服务
从 Arxiv 抓取论文元数据
"""
import arxiv
from datetime import datetime, timedelta
from typing import List, Dict
from database.db_manager import db_manager


class ArxivCrawler:
    """Arxiv 爬虫"""

    def __init__(self):
        self.base_categories = ['cs.AI', 'cs.LG', 'cs.CL', 'math.OC']
        self.excluded_categories = ['physics.', 'biology.', 'chem.', 'q-bio.']

    def fetch_daily_papers(self, date: datetime = None, max_results: int = 200,
                          start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """
        抓取指定日期或日期范围的论文

        Args:
            date: 目标日期，默认为昨天（与start_date/end_date互斥）
            max_results: 最大结果数
            start_date: 开始日期（可选，与date互斥）
            end_date: 结束日期（可选，与date互斥）

        Returns:
            论文元数据列表
        """
        # 确定日期范围
        if start_date and end_date:
            date_str = f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
        elif date:
            date_str = date.strftime('%Y-%m-%d')
            start_date = date
            end_date = date + timedelta(days=1)
        else:
            date = datetime.now() - timedelta(days=1)
            date_str = date.strftime('%Y-%m-%d')
            start_date = date
            end_date = date + timedelta(days=1)

        # 构建查询
        keywords = self._get_keywords_from_db()
        query = self._build_query(keywords, start_date, end_date)

        print(f"📡 开始抓取 {date_str} 的论文...")
        print(f"🔍 查询关键词: {', '.join(keywords[:5])}...")

        papers = []
        try:
            # 使用 arxiv 库搜索
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            for result in search.results():
                # 过滤非相关领域
                if self._should_exclude(result.categories):
                    continue

                # 检查是否已存在
                if db_manager.get_arxiv_paper_by_arxiv_id(result.entry_id.split('/')[-1]):
                    continue

                # 提取作者及其机构信息
                authors_with_affiliation = []
                for author in result.authors:
                    author_info = {'name': author.name}
                    # arxiv库可能不提供affiliation，使用空字符串作为默认值
                    if hasattr(author, 'affiliation') and author.affiliation:
                        author_info['affiliation'] = author.affiliation
                    else:
                        author_info['affiliation'] = ''
                    authors_with_affiliation.append(author_info)

                paper_data = {
                    'arxiv_id': result.entry_id.split('/')[-1],
                    'title': result.title,
                    'authors': authors_with_affiliation,
                    'abstract': result.summary,
                    'categories': result.categories,
                    'published_date': result.published
                }
                papers.append(paper_data)

            print(f"✓ 成功抓取 {len(papers)} 篇新论文")
            return papers

        except Exception as e:
            print(f"❌ 抓取失败: {str(e)}")
            return []

    def _get_keywords_from_db(self) -> List[str]:
        """从数据库获取关键词"""
        keywords_config = db_manager.get_all_keywords()
        if keywords_config:
            return [kw.keyword for kw in keywords_config]

        # 默认关键词（如果数据库为空）
        return [
            'Operations Research', 'VRP', 'MIP', 'MILP', 'Combinatorial Optimization',
            'Agent Memory', 'LLM Memory', 'Agentic RL', 'RLHF', 'Reinforcement Learning'
        ]

    def _build_query(self, keywords: List[str], start_date: datetime = None,
                    end_date: datetime = None) -> str:
        """构建 Arxiv 查询字符串"""
        # 类别查询
        cat_query = ' OR '.join([f'cat:{cat}' for cat in self.base_categories])

        # 关键词查询（标题或摘要）
        kw_queries = [f'(ti:"{kw}" OR abs:"{kw}")' for kw in keywords]
        kw_query = ' OR '.join(kw_queries)

        # 组合查询
        query = f'({cat_query}) AND ({kw_query})'

        # 添加日期范围（如果提供）
        if start_date and end_date:
            # Arxiv 使用 submittedDate 格式: YYYYMMDD
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')
            query += f' AND submittedDate:[{start_str}0000 TO {end_str}2359]'

        return query

    def _should_exclude(self, categories: List[str]) -> bool:
        """判断是否应该排除该论文"""
        for cat in categories:
            for excluded in self.excluded_categories:
                if cat.startswith(excluded):
                    # 检查是否有计算机科学类别
                    has_cs = any(c.startswith('cs.') or c.startswith('math.OC') for c in categories)
                    if not has_cs:
                        return True
        return False

    def keyword_filter(self, papers: List[Dict], keywords: List[str], min_matches: int = 2) -> List[Dict]:
        """
        关键词匹配筛选

        Args:
            papers: 论文列表
            keywords: 关键词列表
            min_matches: 最小匹配数

        Returns:
            筛选后的论文列表
        """
        filtered = []
        exclude_keywords = ['survey', 'review', 'tutorial', 'overview']

        for paper in papers:
            text = (paper['title'] + ' ' + paper['abstract']).lower()

            # 排除综述类
            if any(kw in text for kw in exclude_keywords):
                continue

            # 计算关键词命中数
            matches = sum(1 for kw in keywords if kw.lower() in text)

            if matches >= min_matches:
                filtered.append(paper)

        return filtered


# 创建全局爬虫实例
arxiv_crawler = ArxivCrawler()
