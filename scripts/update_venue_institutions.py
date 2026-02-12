"""
更新现有论文的 venue 和 institutions 信息
从 arXiv PDF 中提取（不依赖 Semantic Scholar API）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_manager
from database.models import ArxivPaper
from services.pdf_metadata_extractor import extract_from_arxiv_pdf
from config.venues import normalize_venue_name, is_top_venue
from config.institutions import normalize_institution_name, is_top_institution
import time

def update_paper_metadata(paper_id: int, arxiv_id: str, dry_run: bool = False):
    """
    更新单篇论文的 venue 和 institutions

    Args:
        paper_id: 论文 ID
        arxiv_id: ArXiv ID
        dry_run: 是否为试运行（不实际更新数据库）

    Returns:
        (success, venue, institutions)
    """
    try:
        # 从 PDF 提取 venue 和 institutions
        venue, venue_year, institutions = extract_from_arxiv_pdf(arxiv_id)

        # 标准化和验证
        if venue:
            venue = normalize_venue_name(venue)
            if not is_top_venue(venue):
                venue = ''
                venue_year = None

        # 标准化机构名称
        normalized_institutions = []
        for inst in institutions:
            normalized = normalize_institution_name(inst)
            if is_top_institution(normalized) and normalized not in normalized_institutions:
                normalized_institutions.append(normalized)

        normalized_institutions = normalized_institutions[:5]

        # 更新数据库
        if not dry_run:
            session = db_manager.get_session()
            try:
                paper = session.query(ArxivPaper).filter(ArxivPaper.id == paper_id).first()
                if paper:
                    paper.venue = venue
                    paper.venue_year = venue_year
                    paper.institutions = normalized_institutions
                    session.commit()
            finally:
                session.close()

        return True, venue, normalized_institutions

    except Exception as e:
        print(f"  ❌ 提取失败: {str(e)}")
        return False, None, None


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='更新论文的 venue 和 institutions 信息')
    parser.add_argument('--dry-run', action='store_true', help='试运行，不实际更新数据库')
    parser.add_argument('--limit', type=int, default=None, help='限制更新的论文数量')
    parser.add_argument('--date-from', type=str, help='起始日期 (YYYY-MM-DD)')
    parser.add_argument('--date-to', type=str, help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--delay', type=float, default=2.0, help='请求间隔（秒），默认 2.0（避免 arXiv 速率限制）')

    args = parser.parse_args()

    print("=" * 60)
    print("更新论文 Venue 和 Institutions 信息")
    print("数据来源：arXiv PDF（不依赖 Semantic Scholar API）")
    print("=" * 60)

    if args.dry_run:
        print("⚠️  试运行模式：不会实际更新数据库")

    # 获取需要更新的论文
    session = db_manager.get_session()
    try:
        query = session.query(ArxivPaper)

        # 只更新没有 venue 和 institutions 的论文
        query = query.filter(
            (ArxivPaper.venue == None) | (ArxivPaper.venue == '') |
            (ArxivPaper.institutions == None) | (ArxivPaper.institutions == [])
        )

        # 日期过滤
        if args.date_from:
            query = query.filter(ArxivPaper.published_date >= args.date_from)
        if args.date_to:
            query = query.filter(ArxivPaper.published_date <= args.date_to)

        # 限制数量
        if args.limit:
            query = query.limit(args.limit)

        papers = query.all()
        total = len(papers)

        print(f"\n找到 {total} 篇需要更新的论文")

        if total == 0:
            print("✓ 所有论文都已有 venue 和 institutions 信息")
            return

        print(f"请求间隔: {args.delay} 秒")
        print()

        # 统计
        success_count = 0
        failed_count = 0
        venue_count = 0
        institution_count = 0

        for i, paper in enumerate(papers, 1):
            print(f"[{i}/{total}] 处理: {paper.title[:50]}...")
            print(f"  ArXiv ID: {paper.arxiv_id}")

            try:
                success, venue, institutions = update_paper_metadata(
                    paper.id,
                    paper.arxiv_id,
                    dry_run=args.dry_run
                )

                if success:
                    success_count += 1
                    if venue:
                        venue_count += 1
                        print(f"  ✓ Venue: {venue}")
                    else:
                        print(f"  - Venue: 无")

                    if institutions:
                        institution_count += 1
                        print(f"  ✓ Institutions: {', '.join(institutions)}")
                    else:
                        print(f"  - Institutions: 无")
                else:
                    failed_count += 1
                    print(f"  ✗ PDF 提取失败或无相关信息")

            except Exception as e:
                failed_count += 1
                print(f"  ✗ 错误: {str(e)}")

            print()

            # 避免速率限制
            if i < total:
                time.sleep(args.delay)

        print("=" * 60)
        print("更新完成")
        print("=" * 60)
        print(f"总计: {total} 篇")
        print(f"成功: {success_count} 篇")
        print(f"失败: {failed_count} 篇")
        print(f"找到 venue: {venue_count} 篇")
        print(f"找到 institutions: {institution_count} 篇")
        print("=" * 60)

    finally:
        session.close()


if __name__ == '__main__':
    main()
