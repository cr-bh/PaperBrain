"""
测试筛选流程
"""
from services.arxiv_crawler import arxiv_crawler
from services.semantic_scholar_filter import semantic_scholar_filter
from database.db_manager import db_manager
from datetime import datetime, timedelta

print("=" * 60)
print("测试三阶段筛选流程")
print("=" * 60)

# 1. 抓取论文
print("\n📡 Step 1: 抓取 Arxiv 论文...")
papers = arxiv_crawler.fetch_daily_papers(
    date=datetime.now() - timedelta(days=1),
    max_results=20
)
print(f"✓ 抓取到 {len(papers)} 篇论文")

if not papers:
    print("没有论文，退出")
    exit()

# 2. 关键词筛选
print("\n🔍 Step 2: 关键词筛选...")
keywords = db_manager.get_all_keywords()
keyword_list = [kw.keyword for kw in keywords] if keywords else []
print(f"使用关键词: {keyword_list[:5]}...")

papers = arxiv_crawler.keyword_filter(papers, keyword_list, min_matches=2)
print(f"✓ 筛选后剩余 {len(papers)} 篇")

if not papers:
    print("关键词筛选后无论文，退出")
    exit()

# 3. S2 筛选
print("\n📊 Step 3: Semantic Scholar 筛选...")
papers = semantic_scholar_filter.batch_filter(papers, min_citations=3, min_influential=1)
print(f"✓ S2 筛选后剩余 {len(papers)} 篇")

# 4. 显示结果
print("\n" + "=" * 60)
print("筛选结果:")
for i, paper in enumerate(papers[:5], 1):
    print(f"\n{i}. {paper['title'][:60]}...")
    s2 = paper.get('s2_metadata')
    if s2:
        print(f"   引用数: {s2.get('citationCount', 0)}, 影响力: {s2.get('influentialCitationCount', 0)}")
print("=" * 60)
