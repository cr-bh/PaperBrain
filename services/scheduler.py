"""
调度器服务
编排 Auto-Scholar 完整流水线
"""
from datetime import datetime, timedelta
from typing import Callable, Optional
from services.arxiv_crawler import arxiv_crawler
from services.scoring_engine import scoring_engine
from services.semantic_scholar_filter import semantic_scholar_filter
from services.metadata_scorer import metadata_scorer
from database.db_manager import db_manager


class DailyScheduler:
    """每日论文抓取和评分调度器"""

    def run_daily_pipeline(self, date: datetime = None, max_results: int = 200,
                          start_date: datetime = None, end_date: datetime = None,
                          progress_callback: Optional[Callable] = None):
        """
        执行完整的每日流水线

        Args:
            date: 目标日期，默认为昨天（与start_date/end_date互斥）
            max_results: 最大抓取数量
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            progress_callback: 进度回调函数 (stage, current, total, message)
        """
        def update_progress(stage: str, current: int, total: int, message: str):
            """更新进度"""
            if progress_callback:
                progress_callback(stage, current, total, message)
            print(message)

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
        update_progress('arxiv', 0, 1, "📡 Step 1/5: 抓取 Arxiv 论文...")
        papers = arxiv_crawler.fetch_daily_papers(
            date=date,
            max_results=max_results,
            start_date=start_date,
            end_date=end_date
        )
        update_progress('arxiv', 1, 1, f"✓ 抓取到 {len(papers)} 篇原始论文")

        if not papers:
            update_progress('arxiv', 1, 1, "⚠️  没有抓取到新论文")
            return

        # Step 2: 关键词筛选
        update_progress('keyword', 0, len(papers), "🔍 Step 2/5: 关键词筛选...")
        keywords = db_manager.get_all_keywords()
        keyword_list = [kw.keyword for kw in keywords] if keywords else []

        if keyword_list:
            # 降低关键词匹配要求，从2改为1，避免过度过滤
            papers = arxiv_crawler.keyword_filter(papers, keyword_list, min_matches=1)
        update_progress('keyword', len(papers), len(papers), f"✓ 关键词筛选后剩余 {len(papers)} 篇")

        if not papers:
            update_progress('keyword', 0, 0, "⚠️  关键词筛选后无论文")
            return

        # Step 3: 元数据评分筛选（两阶段筛选）
        update_progress('metadata', 0, len(papers), "📊 Step 3/5: 元数据评分筛选...")

        # 阶段 1：基础元数据筛选（不需要机构信息，快速过滤低质量论文）
        update_progress('metadata', 0, len(papers), "  🔍 阶段 1: 基础元数据筛选（基于关键词、摘要质量）...")
        papers = metadata_scorer.batch_filter(papers, min_score=4.0)
        update_progress('metadata', len(papers), len(papers), f"  ✓ 基础筛选后剩余 {len(papers)} 篇")

        if not papers:
            update_progress('metadata', 0, 0, "⚠️  基础筛选后无论文")
            return

        # 阶段 2：提取 venue 和 institutions（只处理通过基础筛选的论文）
        update_progress('metadata', 0, len(papers), f"  📄 阶段 2: 提取 venue 和 institutions（处理 {len(papers)} 篇）...")
        from services.pdf_metadata_extractor import extract_from_arxiv_pdf

        for i, paper in enumerate(papers, 1):
            try:
                # 从 PDF 提取 venue 和 institutions
                venue, venue_year, institutions = extract_from_arxiv_pdf(paper['arxiv_id'])

                # 将提取的信息附加到 paper 对象
                paper['extracted_venue'] = venue
                paper['extracted_venue_year'] = venue_year
                paper['extracted_institutions'] = institutions

                # 更新 authors 的 affiliation（用于二次筛选的机构加分）
                if institutions and paper.get('authors'):
                    for j, author in enumerate(paper['authors']):
                        if j < len(institutions):
                            author['affiliation'] = institutions[j]

                # 更新进度（每 5 篇或最后一篇）
                if i % 5 == 0 or i == len(papers):
                    update_progress('metadata', i, len(papers), f"    已处理 {i}/{len(papers)} 篇...")

            except Exception as e:
                # 提取失败不影响后续流程
                paper['extracted_venue'] = ''
                paper['extracted_venue_year'] = None
                paper['extracted_institutions'] = []

        update_progress('metadata', len(papers), len(papers), f"  ✓ 完成 venue 和 institutions 提取")

        # 阶段 3：二次筛选（基于机构加分）
        update_progress('metadata', 0, len(papers), f"  🎯 阶段 3: 二次筛选（基于机构加分，阈值 5.0）...")
        papers_with_institutions = []
        for paper in papers:
            # 重新计算分数（现在机构信息已填充）
            new_score = metadata_scorer.score_paper(paper)
            paper['meta_score'] = new_score

            # 使用更高的阈值进行二次筛选
            if new_score >= 5.0:
                papers_with_institutions.append(paper)

        papers = papers_with_institutions
        update_progress('metadata', len(papers), len(papers), f"  ✓ 二次筛选后剩余 {len(papers)} 篇")
        update_progress('metadata', len(papers), len(papers), f"✓ 元数据筛选后剩余 {len(papers)} 篇")

        if not papers:
            update_progress('metadata', 0, 0, "⚠️  元数据筛选后无论文")
            return

        # Step 4: Semantic Scholar 筛选（如果没有 API Key 则跳过）
        import config
        if config.S2_API_KEY:
            update_progress('s2', 0, len(papers), "🎓 Step 4/5: Semantic Scholar 筛选...")
            papers = semantic_scholar_filter.batch_filter(papers, min_citations=3, min_influential=1)
            update_progress('s2', len(papers), len(papers), f"✓ S2 筛选后剩余 {len(papers)} 篇")
        else:
            print("  ⏭️  跳过 S2 筛选（未配置 S2_API_KEY）")
            update_progress('s2', len(papers), len(papers), f"⏭️  跳过 S2 筛选，保留 {len(papers)} 篇")

        if not papers:
            update_progress('s2', 0, 0, "⚠️  S2 筛选后无论文")
            return

        # Step 5: AI 深度评分（仅对最终候选论文）
        total_papers = len(papers)
        update_progress('ai_scoring', 0, total_papers, f"🤖 Step 5/5: AI 评分 {total_papers} 篇论文...")
        scored_count = 0

        for i, paper in enumerate(papers, 1):
            try:
                # 再次检查是否已存在（防止重复运行）
                if db_manager.get_arxiv_paper_by_arxiv_id(paper['arxiv_id']):
                    update_progress('ai_scoring', i, total_papers,
                                  f"  [{i}/{total_papers}] ⏭️  跳过已存在: {paper['title'][:40]}...")
                    continue

                update_progress('ai_scoring', i, total_papers,
                              f"  [{i}/{total_papers}] 评分中: {paper['title'][:40]}...")

                # 调用评分引擎（传递已提取的 venue 和 institutions）
                score_result = scoring_engine.score_paper(
                    paper['title'],
                    paper['abstract'],
                    paper['authors'],  # 传递作者信息
                    paper.get('s2_metadata'),  # 传递 S2 元数据
                    paper['arxiv_id'],  # 传递 arxiv_id
                    paper.get('extracted_venue'),  # 传递已提取的 venue
                    paper.get('extracted_venue_year'),  # 传递已提取的 venue_year
                    paper.get('extracted_institutions', [])  # 传递已提取的 institutions
                )

                # 保存到数据库（包含新字段）
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
                    tags=score_result['tags'],
                    venue=score_result.get('venue', ''),
                    venue_year=score_result.get('venue_year'),
                    institutions=score_result.get('institutions', [])
                )

                scored_count += 1

            except Exception as e:
                print(f"  ❌ 评分失败: {str(e)}")
                continue

        update_progress('ai_scoring', total_papers, total_papers,
                       f"✓ 成功评分并保存 {scored_count} 篇论文")

        # 统计结果
        update_progress('saving', 0, 1, "📈 统计结果...")
        if start_date and end_date:
            all_papers = db_manager.get_arxiv_papers_by_date_range(start_date, end_date)
        elif date:
            all_papers = db_manager.get_arxiv_papers_by_date(date)
        else:
            all_papers = db_manager.get_arxiv_papers_by_date(datetime.now() - timedelta(days=1))

        s_papers = [p for p in all_papers if p.score >= 9]
        a_papers = [p for p in all_papers if 7 <= p.score < 9]
        b_papers = [p for p in all_papers if 5 <= p.score < 7]

        update_progress('saving', 1, 1, "✅ 流水线执行完成！")

        print(f"\n{'='*60}")
        print(f"📈 统计结果:")
        print(f"  - S级 (9-10分): {len(s_papers)} 篇")
        print(f"  - A级 (7-8分): {len(a_papers)} 篇")
        print(f"  - B级 (5-6分): {len(b_papers)} 篇")
        print(f"  - 总计: {len(all_papers)} 篇")
        print(f"{'='*60}\n")

        return {
            'total': len(all_papers),
            's_count': len(s_papers),
            'a_count': len(a_papers),
            'b_count': len(b_papers),
            'scored': scored_count
        }


# 创建全局调度器实例
daily_scheduler = DailyScheduler()
