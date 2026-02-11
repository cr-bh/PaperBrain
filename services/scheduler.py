"""
调度器服务
编排 Auto-Scholar 完整流水线
"""
from datetime import datetime, timedelta
from services.arxiv_crawler import arxiv_crawler
from services.scoring_engine import scoring_engine
from services.semantic_scholar_filter import semantic_scholar_filter
from database.db_manager import db_manager


class DailyScheduler:
    """每日论文抓取和评分调度器"""

    def run_daily_pipeline(self, date: datetime = None, max_results: int = 200,
                          start_date: datetime = None, end_date: datetime = None):
        """
        执行完整的每日流水线

        Args:
            date: 目标日期，默认为昨天（与start_date/end_date互斥）
            max_results: 最大抓取数量
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
        """
        if start_date and end_date:
            date_str = f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
        elif date:
            date_str = date.strftime('%Y-%m-%d')
        else:
            date = datetime.now() - timedelta(days=1)
            date_str = date.strftime('%Y-%m-%d')

        print(f"\n{'='*60}")
        print(f"🚀 开始执行 Auto-Scholar 流水线")
        print(f"📅 目标日期: {date_str}")
        print(f"{'='*60}\n")

        # Step 1: 抓取论文
        print("📡 Step 1/3: 抓取 Arxiv 论文...")
        papers = arxiv_crawler.fetch_daily_papers(
            date=date,
            max_results=max_results,
            start_date=start_date,
            end_date=end_date
        )

        if not papers:
            print("⚠️  没有抓取到新论文")
            return

        # Step 1.5: 关键词筛选
        print(f"\n🔍 Step 1.5/4: 关键词筛选...")
        keywords = db_manager.get_all_keywords()
        keyword_list = [kw.keyword for kw in keywords] if keywords else []

        if keyword_list:
            papers = arxiv_crawler.keyword_filter(papers, keyword_list, min_matches=2)
            print(f"✓ 关键词筛选后剩余 {len(papers)} 篇")

        if not papers:
            print("⚠️  关键词筛选后无论文")
            return

        # Step 1.6: Semantic Scholar 筛选
        print(f"\n📊 Step 1.6/4: Semantic Scholar 元数据筛选...")
        papers = semantic_scholar_filter.batch_filter(papers, min_citations=3, min_influential=1)
        print(f"✓ S2 筛选后剩余 {len(papers)} 篇")

        if not papers:
            print("⚠️  S2 筛选后无论文")
            return

        # Step 2: 批量评分
        print(f"\n🎯 Step 2/4: 评分 {len(papers)} 篇论文...")
        scored_count = 0
        for i, paper in enumerate(papers, 1):
            try:
                # 再次检查是否已存在（防止重复运行）
                if db_manager.get_arxiv_paper_by_arxiv_id(paper['arxiv_id']):
                    print(f"  [{i}/{len(papers)}] ⏭️  跳过已存在: {paper['title'][:50]}...")
                    continue

                print(f"  [{i}/{len(papers)}] 评分中: {paper['title'][:50]}...")

                # 调用评分引擎
                score_result = scoring_engine.score_paper(
                    paper['title'],
                    paper['abstract']
                )

                # 保存到数据库
                db_manager.create_arxiv_paper(
                    arxiv_id=paper['arxiv_id'],
                    title=paper['title'],
                    authors=paper['authors'],
                    abstract=paper['abstract'],
                    categories=paper['categories'],
                    published_date=paper['published_date'],
                    score=score_result['score'],
                    score_reason=score_result['reason'],
                    title_zh=score_result['title_zh'],
                    abstract_zh=score_result['abstract_zh'],
                    tags=score_result['tags']
                )

                scored_count += 1

            except Exception as e:
                print(f"  ❌ 评分失败: {str(e)}")
                continue

        print(f"\n✓ 成功评分并保存 {scored_count} 篇论文")

        # Step 3: 统计结果
        print(f"\n📊 Step 3/4: 统计结果...")
        # 根据日期范围获取论文
        if start_date and end_date:
            all_papers = db_manager.get_arxiv_papers_by_date_range(start_date, end_date)
        elif date:
            all_papers = db_manager.get_arxiv_papers_by_date(date)
        else:
            all_papers = db_manager.get_arxiv_papers_by_date(datetime.now() - timedelta(days=1))

        s_papers = [p for p in all_papers if p.score >= 9]
        a_papers = [p for p in all_papers if 7 <= p.score < 9]
        b_papers = [p for p in all_papers if 5 <= p.score < 7]

        print(f"\n{'='*60}")
        print(f"✅ 流水线执行完成！")
        print(f"📈 统计结果:")
        print(f"  - S级 (9-10分): {len(s_papers)} 篇")
        print(f"  - A级 (7-8分): {len(a_papers)} 篇")
        print(f"  - B级 (5-6分): {len(b_papers)} 篇")
        print(f"  - 总计: {len(all_papers)} 篇")
        print(f"{'='*60}\n")


# 创建全局调度器实例
daily_scheduler = DailyScheduler()
