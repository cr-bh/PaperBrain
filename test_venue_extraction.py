"""
测试 venue 和 institutions 提取功能
"""
from services.scoring_engine import scoring_engine
from services.semantic_scholar_filter import semantic_scholar_filter

# 测试论文信息
test_paper = {
    'arxiv_id': '2602.11057',
    'title': 'Divide, Harmonize, Then Conquer It: Shooting Multi-Commodity Flow Problems with Multimodal Language Models',
    'abstract': 'The multi-commodity flow (MCF) problem is a fundamental topic in network flow and combinatorial optimization...',
    'authors': [
        {'name': 'Xinyu Yuan', 'affiliation': ''},
        {'name': 'Yan Qiao', 'affiliation': ''},
    ]
}

print("=" * 60)
print("测试 Venue 和 Institutions 提取功能")
print("=" * 60)

# 1. 获取 Semantic Scholar 元数据
print("\n1. 获取 Semantic Scholar 元数据...")
s2_metadata = semantic_scholar_filter.get_paper_metadata(test_paper['arxiv_id'])

if s2_metadata:
    print(f"✓ S2 元数据获取成功")
    print(f"  - Venue: {s2_metadata.get('venue', 'N/A')}")
    print(f"  - Year: {s2_metadata.get('year', 'N/A')}")
    print(f"  - Authors: {len(s2_metadata.get('authors', []))} 位")

    # 显示作者机构
    if s2_metadata.get('authors'):
        print(f"  - 作者机构:")
        for author in s2_metadata['authors'][:3]:  # 只显示前3位
            name = author.get('name', 'Unknown')
            affiliations = author.get('affiliations', [])
            if affiliations:
                for aff in affiliations:
                    if isinstance(aff, dict):
                        print(f"    * {name}: {aff.get('name', 'N/A')}")
                    else:
                        print(f"    * {name}: {aff}")
            else:
                print(f"    * {name}: 无机构信息")
else:
    print("✗ S2 元数据获取失败（论文可能未被收录）")

# 2. 测试评分引擎（不传递 S2 数据）
print("\n2. 测试评分引擎（不使用 S2 数据）...")
result_without_s2 = scoring_engine.score_paper(
    test_paper['title'],
    test_paper['abstract'],
    test_paper['authors']
)
print(f"  - Venue: {result_without_s2.get('venue', 'N/A')}")
print(f"  - Venue Year: {result_without_s2.get('venue_year', 'N/A')}")
print(f"  - Institutions: {result_without_s2.get('institutions', [])}")

# 3. 测试评分引擎（传递 S2 数据）
if s2_metadata:
    print("\n3. 测试评分引擎（使用 S2 数据）...")
    result_with_s2 = scoring_engine.score_paper(
        test_paper['title'],
        test_paper['abstract'],
        test_paper['authors'],
        s2_metadata
    )
    print(f"  - Venue: {result_with_s2.get('venue', 'N/A')}")
    print(f"  - Venue Year: {result_with_s2.get('venue_year', 'N/A')}")
    print(f"  - Institutions: {result_with_s2.get('institutions', [])}")

    print("\n" + "=" * 60)
    print("对比结果:")
    print("=" * 60)
    print(f"不使用 S2: venue={result_without_s2.get('venue')}, institutions={len(result_without_s2.get('institutions', []))}")
    print(f"使用 S2:   venue={result_with_s2.get('venue')}, institutions={len(result_with_s2.get('institutions', []))}")
else:
    print("\n⚠️  无法测试 S2 数据集成（S2 元数据不可用）")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
