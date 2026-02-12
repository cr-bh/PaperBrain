"""
顶刊顶会配置
包含 AI 领域和交通运输领域的顶级会议和期刊
"""

# AI 领域顶级会议
AI_TOP_CONFERENCES = {
    # 机器学习
    'NeurIPS': {'full_name': 'Neural Information Processing Systems', 'rank': 'A*'},
    'ICML': {'full_name': 'International Conference on Machine Learning', 'rank': 'A*'},
    'ICLR': {'full_name': 'International Conference on Learning Representations', 'rank': 'A*'},

    # 计算机视觉
    'CVPR': {'full_name': 'Conference on Computer Vision and Pattern Recognition', 'rank': 'A*'},
    'ICCV': {'full_name': 'International Conference on Computer Vision', 'rank': 'A*'},
    'ECCV': {'full_name': 'European Conference on Computer Vision', 'rank': 'A*'},

    # 自然语言处理
    'ACL': {'full_name': 'Association for Computational Linguistics', 'rank': 'A*'},
    'EMNLP': {'full_name': 'Empirical Methods in Natural Language Processing', 'rank': 'A'},
    'NAACL': {'full_name': 'North American Chapter of the ACL', 'rank': 'A'},

    # 人工智能综合
    'AAAI': {'full_name': 'AAAI Conference on Artificial Intelligence', 'rank': 'A*'},
    'IJCAI': {'full_name': 'International Joint Conference on Artificial Intelligence', 'rank': 'A*'},

    # 数据挖掘
    'KDD': {'full_name': 'Knowledge Discovery and Data Mining', 'rank': 'A*'},
    'SIGIR': {'full_name': 'Special Interest Group on Information Retrieval', 'rank': 'A*'},
    'WWW': {'full_name': 'The Web Conference', 'rank': 'A*'},

    # 强化学习
    'AAMAS': {'full_name': 'Autonomous Agents and Multiagent Systems', 'rank': 'A'},
}

# AI 领域顶级期刊
AI_TOP_JOURNALS = {
    'JMLR': {'full_name': 'Journal of Machine Learning Research', 'rank': 'A*'},
    'TPAMI': {'full_name': 'IEEE Transactions on Pattern Analysis and Machine Intelligence', 'rank': 'A*'},
    'IJCV': {'full_name': 'International Journal of Computer Vision', 'rank': 'A*'},
    'AIJ': {'full_name': 'Artificial Intelligence', 'rank': 'A*'},
    'JAIR': {'full_name': 'Journal of Artificial Intelligence Research', 'rank': 'A'},
}

# 运筹学和优化领域顶级会议
OR_TOP_CONFERENCES = {
    'INFORMS': {'full_name': 'Institute for Operations Research and the Management Sciences', 'rank': 'A*'},
    'EURO': {'full_name': 'European Conference on Operational Research', 'rank': 'A'},
    'ISMP': {'full_name': 'International Symposium on Mathematical Programming', 'rank': 'A'},
}

# 运筹学和优化领域顶级期刊
OR_TOP_JOURNALS = {
    'OR': {'full_name': 'Operations Research', 'rank': 'A*'},
    'MS': {'full_name': 'Management Science', 'rank': 'A*'},
    'MP': {'full_name': 'Mathematical Programming', 'rank': 'A*'},
    'EJOR': {'full_name': 'European Journal of Operational Research', 'rank': 'A'},
    'INFORMS JOC': {'full_name': 'INFORMS Journal on Computing', 'rank': 'A'},
    'COR': {'full_name': 'Computers & Operations Research', 'rank': 'A'},
    'TRSC': {'full_name': 'Transportation Research Part C', 'rank': 'A'},
    'TRB': {'full_name': 'Transportation Research Part B', 'rank': 'A'},
}

# 交通运输领域顶级会议
TRANSPORTATION_TOP_CONFERENCES = {
    'TRB': {'full_name': 'Transportation Research Board Annual Meeting', 'rank': 'A'},
    'ITSC': {'full_name': 'IEEE Intelligent Transportation Systems Conference', 'rank': 'A'},
    'IV': {'full_name': 'IEEE Intelligent Vehicles Symposium', 'rank': 'A'},
    'WCTR': {'full_name': 'World Conference on Transport Research', 'rank': 'A'},
}

# 交通运输领域顶级期刊
TRANSPORTATION_TOP_JOURNALS = {
    'TR-A': {'full_name': 'Transportation Research Part A: Policy and Practice', 'rank': 'A'},
    'TR-B': {'full_name': 'Transportation Research Part B: Methodological', 'rank': 'A*'},
    'TR-C': {'full_name': 'Transportation Research Part C: Emerging Technologies', 'rank': 'A*'},
    'TR-D': {'full_name': 'Transportation Research Part D: Transport and Environment', 'rank': 'A'},
    'TR-E': {'full_name': 'Transportation Research Part E: Logistics and Transportation Review', 'rank': 'A'},
    'Transportation': {'full_name': 'Transportation', 'rank': 'A'},
    'Transportation Science': {'full_name': 'Transportation Science', 'rank': 'A*'},
}

# 合并所有顶会顶刊
ALL_TOP_VENUES = {
    **AI_TOP_CONFERENCES,
    **AI_TOP_JOURNALS,
    **OR_TOP_CONFERENCES,
    **OR_TOP_JOURNALS,
    **TRANSPORTATION_TOP_CONFERENCES,
    **TRANSPORTATION_TOP_JOURNALS,
}

# 会议/期刊名称变体映射（用于识别）
VENUE_VARIANTS = {
    # NeurIPS 变体
    'neurips': 'NeurIPS',
    'nips': 'NeurIPS',
    'neural information processing systems': 'NeurIPS',

    # ICML 变体
    'icml': 'ICML',
    'international conference on machine learning': 'ICML',

    # ICLR 变体
    'iclr': 'ICLR',
    'international conference on learning representations': 'ICLR',

    # CVPR 变体
    'cvpr': 'CVPR',
    'conference on computer vision and pattern recognition': 'CVPR',

    # ICCV 变体
    'iccv': 'ICCV',
    'international conference on computer vision': 'ICCV',

    # ECCV 变体
    'eccv': 'ECCV',
    'european conference on computer vision': 'ECCV',

    # ACL 变体
    'acl': 'ACL',
    'association for computational linguistics': 'ACL',

    # AAAI 变体
    'aaai': 'AAAI',
    'aaai conference on artificial intelligence': 'AAAI',

    # IJCAI 变体
    'ijcai': 'IJCAI',
    'international joint conference on artificial intelligence': 'IJCAI',

    # KDD 变体
    'kdd': 'KDD',
    'knowledge discovery and data mining': 'KDD',

    # Operations Research 变体
    'operations research': 'OR',
    'oper. res.': 'OR',
    'oper res': 'OR',

    # Management Science 变体
    'management science': 'MS',
    'manag. sci.': 'MS',

    # Transportation Research 变体
    'transportation research part a': 'TR-A',
    'transportation research part b': 'TR-B',
    'transportation research part c': 'TR-C',
    'transportation research part d': 'TR-D',
    'transportation research part e': 'TR-E',
    'transp. res. part a': 'TR-A',
    'transp. res. part b': 'TR-B',
    'transp. res. part c': 'TR-C',
    'transp. res. part d': 'TR-D',
    'transp. res. part e': 'TR-E',
    'trb': 'TR-B',
    'trc': 'TR-C',

    # Transportation Science 变体
    'transportation science': 'Transportation Science',
    'transp. sci.': 'Transportation Science',
}


def normalize_venue_name(venue_text: str) -> str:
    """
    标准化会议/期刊名称

    Args:
        venue_text: 原始会议/期刊名称

    Returns:
        标准化后的名称，如果无法识别则返回原始名称
    """
    if not venue_text:
        return ''

    # 转小写并去除多余空格
    venue_lower = venue_text.lower().strip()

    # 查找变体映射
    if venue_lower in VENUE_VARIANTS:
        return VENUE_VARIANTS[venue_lower]

    # 尝试部分匹配
    for variant, standard in VENUE_VARIANTS.items():
        if variant in venue_lower or venue_lower in variant:
            return standard

    # 如果无法识别，返回原始名称（首字母大写）
    return venue_text.title()


def is_top_venue(venue_name: str) -> bool:
    """
    判断是否为顶级会议/期刊

    Args:
        venue_name: 会议/期刊名称

    Returns:
        是否为顶级会议/期刊
    """
    normalized = normalize_venue_name(venue_name)
    return normalized in ALL_TOP_VENUES


def get_venue_info(venue_name: str) -> dict:
    """
    获取会议/期刊详细信息

    Args:
        venue_name: 会议/期刊名称

    Returns:
        包含 full_name 和 rank 的字典，如果不是顶会则返回 None
    """
    normalized = normalize_venue_name(venue_name)
    return ALL_TOP_VENUES.get(normalized)
