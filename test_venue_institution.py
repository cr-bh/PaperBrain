"""
测试顶会顶刊和知名机构提取功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.venues import normalize_venue_name, is_top_venue, get_venue_info
from config.institutions import normalize_institution_name, is_top_institution, get_institution_info, extract_institutions_from_authors


def test_venue_extraction():
    """测试会议/期刊提取"""
    print("\n" + "="*60)
    print("测试会议/期刊提取")
    print("="*60)

    test_cases = [
        "ICLR",
        "iclr",
        "NeurIPS",
        "neurips",
        "CVPR",
        "Operations Research",
        "Transportation Research Part C",
        "Unknown Conference",
    ]

    for venue in test_cases:
        normalized = normalize_venue_name(venue)
        is_top = is_top_venue(normalized)
        info = get_venue_info(normalized)

        print(f"\n原始: {venue}")
        print(f"  标准化: {normalized}")
        print(f"  是否顶会: {is_top}")
        if info:
            print(f"  详细信息: {info}")


def test_institution_extraction():
    """测试机构提取"""
    print("\n" + "="*60)
    print("测试机构提取")
    print("="*60)

    test_cases = [
        "MIT",
        "Stanford",
        "Tsinghua University",
        "THU",
        "Google",
        "ByteDance",
        "Unknown University",
    ]

    for inst in test_cases:
        normalized = normalize_institution_name(inst)
        is_top = is_top_institution(normalized)
        info = get_institution_info(normalized)

        print(f"\n原始: {inst}")
        print(f"  标准化: {normalized}")
        print(f"  是否知名机构: {is_top}")
        if info:
            print(f"  详细信息: {info}")


def test_authors_extraction():
    """测试从作者列表中提取机构"""
    print("\n" + "="*60)
    print("测试从作者列表中提取机构")
    print("="*60)

    test_authors = [
        {'name': 'John Doe', 'affiliation': 'Massachusetts Institute of Technology'},
        {'name': 'Jane Smith', 'affiliation': 'Google Brain'},
        {'name': 'Li Ming', 'affiliation': 'Tsinghua University'},
        {'name': 'Wang Wei', 'affiliation': 'ByteDance'},
        {'name': 'Unknown', 'affiliation': 'Some Unknown University'},
    ]

    institutions = extract_institutions_from_authors(test_authors)
    print(f"\n提取到的知名机构: {institutions}")


def test_scoring_engine():
    """测试评分引擎"""
    print("\n" + "="*60)
    print("测试评分引擎（模拟）")
    print("="*60)

    # 模拟测试数据
    test_paper = {
        'title': 'Accepted to ICLR 2026: Deep Reinforcement Learning for Vehicle Routing',
        'abstract': 'We propose a novel approach using deep reinforcement learning to solve vehicle routing problems. Authors from MIT and Google Brain collaborated on this work.',
        'authors': [
            {'name': 'John Doe', 'affiliation': 'MIT'},
            {'name': 'Jane Smith', 'affiliation': 'Google Brain'},
        ]
    }

    print(f"\n标题: {test_paper['title']}")
    print(f"摘要: {test_paper['abstract'][:100]}...")
    print(f"作者: {test_paper['authors']}")

    print("\n预期提取结果:")
    print("  venue: ICLR")
    print("  venue_year: 2026")
    print("  institutions: ['MIT', 'Google Brain']")

    # 测试机构提取
    institutions = extract_institutions_from_authors(test_paper['authors'])
    print(f"\n实际提取的机构: {institutions}")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("顶会顶刊和知名机构提取功能测试")
    print("="*60)

    test_venue_extraction()
    test_institution_extraction()
    test_authors_extraction()
    test_scoring_engine()

    print("\n" + "="*60)
    print("✅ 所有测试完成")
    print("="*60)


if __name__ == "__main__":
    main()
