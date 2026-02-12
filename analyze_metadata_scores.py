"""
分析当前论文的元数据分数分布
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_manager
from database.models import ArxivPaper
from services.metadata_scorer import metadata_scorer
from datetime import datetime

# 获取最近抓取的论文
session = db_manager.get_session()
try:
    # 获取今天抓取的论文
    papers = session.query(ArxivPaper).filter(
        ArxivPaper.fetch_date >= datetime.now().replace(hour=0, minute=0, second=0)
    ).all()

    print(f"找到 {len(papers)} 篇今天抓取的论文")
    print("=" * 60)

    # 计算元数据分数
    scores = []
    for paper in papers:
        paper_dict = {
            'title': paper.title,
            'abstract': paper.abstract,
            'authors': paper.authors,
            'published_date': paper.published_date
        }
        score = metadata_scorer.score_paper(paper_dict)
        scores.append((paper.title[:50], score))

    # 排序
    scores.sort(key=lambda x: x[1], reverse=True)

    # 统计分布
    score_ranges = {
        '8-10': 0,
        '6-8': 0,
        '5-6': 0,
        '4-5': 0,
        '3-4': 0,
        '0-3': 0
    }

    for _, score in scores:
        if score >= 8:
            score_ranges['8-10'] += 1
        elif score >= 6:
            score_ranges['6-8'] += 1
        elif score >= 5:
            score_ranges['5-6'] += 1
        elif score >= 4:
            score_ranges['4-5'] += 1
        elif score >= 3:
            score_ranges['3-4'] += 1
        else:
            score_ranges['0-3'] += 1

    print("\n分数分布:")
    print("-" * 60)
    for range_name, count in score_ranges.items():
        percentage = count / len(scores) * 100 if scores else 0
        bar = '█' * int(percentage / 2)
        print(f"{range_name} 分: {count:3d} 篇 ({percentage:5.1f}%) {bar}")

    print("\n" + "=" * 60)
    print("不同阈值的过滤效果:")
    print("-" * 60)
    for threshold in [4.0, 5.0, 6.0, 7.0]:
        passed = sum(1 for _, s in scores if s >= threshold)
        filtered = len(scores) - passed
        filter_rate = filtered / len(scores) * 100 if scores else 0
        print(f"阈值 {threshold}: 保留 {passed} 篇, 过滤 {filtered} 篇 ({filter_rate:.1f}%)")

    print("\n" + "=" * 60)
    print("Top 20 论文及其分数:")
    print("-" * 60)
    for i, (title, score) in enumerate(scores[:20], 1):
        print(f"{i:2d}. [{score:.1f}] {title}...")

    if len(scores) > 20:
        print(f"\n... 还有 {len(scores) - 20} 篇论文")

finally:
    session.close()
