"""
知名机构配置
包含中国985大学、QS前50大学、US News前70大学、知名科技公司
"""

# 中国985大学（39所）
CHINA_985_UNIVERSITIES = {
    # 清华北大
    'Tsinghua University': {'abbr': 'THU', 'country': 'China', 'rank': 'Top'},
    'Peking University': {'abbr': 'PKU', 'country': 'China', 'rank': 'Top'},

    # C9联盟
    'Fudan University': {'abbr': 'FDU', 'country': 'China', 'rank': 'Top'},
    'Shanghai Jiao Tong University': {'abbr': 'SJTU', 'country': 'China', 'rank': 'Top'},
    'Zhejiang University': {'abbr': 'ZJU', 'country': 'China', 'rank': 'Top'},
    'Nanjing University': {'abbr': 'NJU', 'country': 'China', 'rank': 'Top'},
    'University of Science and Technology of China': {'abbr': 'USTC', 'country': 'China', 'rank': 'Top'},
    'Harbin Institute of Technology': {'abbr': 'HIT', 'country': 'China', 'rank': 'Top'},
    'Xi\'an Jiaotong University': {'abbr': 'XJTU', 'country': 'China', 'rank': 'Top'},

    # 其他985
    'Beihang University': {'abbr': 'BUAA', 'country': 'China', 'rank': 'A'},
    'Beijing Institute of Technology': {'abbr': 'BIT', 'country': 'China', 'rank': 'A'},
    'Beijing Normal University': {'abbr': 'BNU', 'country': 'China', 'rank': 'A'},
    'Nankai University': {'abbr': 'NKU', 'country': 'China', 'rank': 'A'},
    'Tianjin University': {'abbr': 'TJU', 'country': 'China', 'rank': 'A'},
    'Dalian University of Technology': {'abbr': 'DUT', 'country': 'China', 'rank': 'A'},
    'Jilin University': {'abbr': 'JLU', 'country': 'China', 'rank': 'A'},
    'Northeastern University': {'abbr': 'NEU', 'country': 'China', 'rank': 'A'},
    'Tongji University': {'abbr': 'TJU', 'country': 'China', 'rank': 'A'},
    'East China Normal University': {'abbr': 'ECNU', 'country': 'China', 'rank': 'A'},
    'Xiamen University': {'abbr': 'XMU', 'country': 'China', 'rank': 'A'},
    'Shandong University': {'abbr': 'SDU', 'country': 'China', 'rank': 'A'},
    'Wuhan University': {'abbr': 'WHU', 'country': 'China', 'rank': 'A'},
    'Huazhong University of Science and Technology': {'abbr': 'HUST', 'country': 'China', 'rank': 'A'},
    'Central South University': {'abbr': 'CSU', 'country': 'China', 'rank': 'A'},
    'Sun Yat-sen University': {'abbr': 'SYSU', 'country': 'China', 'rank': 'A'},
    'South China University of Technology': {'abbr': 'SCUT', 'country': 'China', 'rank': 'A'},
    'Sichuan University': {'abbr': 'SCU', 'country': 'China', 'rank': 'A'},
    'Chongqing University': {'abbr': 'CQU', 'country': 'China', 'rank': 'A'},
    'University of Electronic Science and Technology of China': {'abbr': 'UESTC', 'country': 'China', 'rank': 'A'},
    'Renmin University of China': {'abbr': 'RUC', 'country': 'China', 'rank': 'A'},
    'China Agricultural University': {'abbr': 'CAU', 'country': 'China', 'rank': 'A'},
    'Ocean University of China': {'abbr': 'OUC', 'country': 'China', 'rank': 'A'},
    'Northwestern Polytechnical University': {'abbr': 'NPU', 'country': 'China', 'rank': 'A'},
    'Lanzhou University': {'abbr': 'LZU', 'country': 'China', 'rank': 'A'},
    'Southeast University': {'abbr': 'SEU', 'country': 'China', 'rank': 'A'},
    'Hunan University': {'abbr': 'HNU', 'country': 'China', 'rank': 'A'},
    'National University of Defense Technology': {'abbr': 'NUDT', 'country': 'China', 'rank': 'A'},
    'Central University for Nationalities': {'abbr': 'MUC', 'country': 'China', 'rank': 'A'},

    # 香港
    'The University of Hong Kong': {'abbr': 'HKU', 'country': 'Hong Kong', 'rank': 'Top'},
    'The Chinese University of Hong Kong': {'abbr': 'CUHK', 'country': 'Hong Kong', 'rank': 'Top'},
    'Hong Kong University of Science and Technology': {'abbr': 'HKUST', 'country': 'Hong Kong', 'rank': 'Top'},
}

# QS前50大学（部分重点）
QS_TOP_50_UNIVERSITIES = {
    # 美国
    'Massachusetts Institute of Technology': {'abbr': 'MIT', 'country': 'USA', 'rank': 'Top'},
    'Stanford University': {'abbr': 'Stanford', 'country': 'USA', 'rank': 'Top'},
    'Harvard University': {'abbr': 'Harvard', 'country': 'USA', 'rank': 'Top'},
    'California Institute of Technology': {'abbr': 'Caltech', 'country': 'USA', 'rank': 'Top'},
    'University of California, Berkeley': {'abbr': 'UC Berkeley', 'country': 'USA', 'rank': 'Top'},
    'University of Chicago': {'abbr': 'UChicago', 'country': 'USA', 'rank': 'Top'},
    'University of Pennsylvania': {'abbr': 'UPenn', 'country': 'USA', 'rank': 'Top'},
    'Cornell University': {'abbr': 'Cornell', 'country': 'USA', 'rank': 'Top'},
    'Princeton University': {'abbr': 'Princeton', 'country': 'USA', 'rank': 'Top'},
    'Yale University': {'abbr': 'Yale', 'country': 'USA', 'rank': 'Top'},
    'Columbia University': {'abbr': 'Columbia', 'country': 'USA', 'rank': 'Top'},
    'University of California, Los Angeles': {'abbr': 'UCLA', 'country': 'USA', 'rank': 'Top'},
    'Carnegie Mellon University': {'abbr': 'CMU', 'country': 'USA', 'rank': 'Top'},
    'University of Michigan': {'abbr': 'UMich', 'country': 'USA', 'rank': 'Top'},
    'New York University': {'abbr': 'NYU', 'country': 'USA', 'rank': 'Top'},
    'Northwestern University': {'abbr': 'Northwestern', 'country': 'USA', 'rank': 'Top'},
    'Duke University': {'abbr': 'Duke', 'country': 'USA', 'rank': 'Top'},
    'Johns Hopkins University': {'abbr': 'JHU', 'country': 'USA', 'rank': 'Top'},
    'University of California, San Diego': {'abbr': 'UCSD', 'country': 'USA', 'rank': 'Top'},
    'University of Washington': {'abbr': 'UW', 'country': 'USA', 'rank': 'Top'},
    'Georgia Institute of Technology': {'abbr': 'Georgia Tech', 'country': 'USA', 'rank': 'Top'},
    'University of Texas at Austin': {'abbr': 'UT Austin', 'country': 'USA', 'rank': 'Top'},
    'University of Illinois Urbana-Champaign': {'abbr': 'UIUC', 'country': 'USA', 'rank': 'Top'},

    # US News Top 70 补充（QS Top 50 未覆盖的优秀美国大学）
    'Vanderbilt University': {'abbr': 'Vanderbilt', 'country': 'USA', 'rank': 'Top'},
    'Rice University': {'abbr': 'Rice', 'country': 'USA', 'rank': 'Top'},
    'University of Notre Dame': {'abbr': 'Notre Dame', 'country': 'USA', 'rank': 'Top'},
    'Washington University in St. Louis': {'abbr': 'WashU', 'country': 'USA', 'rank': 'Top'},
    'Brown University': {'abbr': 'Brown', 'country': 'USA', 'rank': 'Top'},
    'Dartmouth College': {'abbr': 'Dartmouth', 'country': 'USA', 'rank': 'Top'},
    'Emory University': {'abbr': 'Emory', 'country': 'USA', 'rank': 'Top'},
    'University of Southern California': {'abbr': 'USC', 'country': 'USA', 'rank': 'Top'},
    'University of California, Davis': {'abbr': 'UC Davis', 'country': 'USA', 'rank': 'Top'},
    'University of California, Irvine': {'abbr': 'UC Irvine', 'country': 'USA', 'rank': 'Top'},
    'University of California, Santa Barbara': {'abbr': 'UCSB', 'country': 'USA', 'rank': 'Top'},
    'University of Wisconsin-Madison': {'abbr': 'UW-Madison', 'country': 'USA', 'rank': 'Top'},
    'University of North Carolina at Chapel Hill': {'abbr': 'UNC', 'country': 'USA', 'rank': 'Top'},
    'University of Florida': {'abbr': 'UF', 'country': 'USA', 'rank': 'Top'},
    'Boston University': {'abbr': 'BU', 'country': 'USA', 'rank': 'Top'},
    'University of Rochester': {'abbr': 'Rochester', 'country': 'USA', 'rank': 'Top'},
    'Ohio State University': {'abbr': 'OSU', 'country': 'USA', 'rank': 'Top'},
    'Pennsylvania State University': {'abbr': 'Penn State', 'country': 'USA', 'rank': 'Top'},
    'Purdue University': {'abbr': 'Purdue', 'country': 'USA', 'rank': 'Top'},
    'University of Maryland': {'abbr': 'UMD', 'country': 'USA', 'rank': 'Top'},
    'University of Minnesota': {'abbr': 'UMN', 'country': 'USA', 'rank': 'Top'},
    'University of Pittsburgh': {'abbr': 'Pitt', 'country': 'USA', 'rank': 'Top'},
    'Rutgers University': {'abbr': 'Rutgers', 'country': 'USA', 'rank': 'Top'},
    'University of Virginia': {'abbr': 'UVA', 'country': 'USA', 'rank': 'Top'},
    'University of Massachusetts Amherst': {'abbr': 'UMass', 'country': 'USA', 'rank': 'Top'},
    'Texas A&M University': {'abbr': 'TAMU', 'country': 'USA', 'rank': 'Top'},
    'University of Colorado Boulder': {'abbr': 'CU Boulder', 'country': 'USA', 'rank': 'Top'},
    'Arizona State University': {'abbr': 'ASU', 'country': 'USA', 'rank': 'Top'},
    'Michigan State University': {'abbr': 'MSU', 'country': 'USA', 'rank': 'Top'},
    'University of Arizona': {'abbr': 'UA', 'country': 'USA', 'rank': 'Top'},

    # 英国
    'University of Oxford': {'abbr': 'Oxford', 'country': 'UK', 'rank': 'Top'},
    'University of Cambridge': {'abbr': 'Cambridge', 'country': 'UK', 'rank': 'Top'},
    'Imperial College London': {'abbr': 'Imperial', 'country': 'UK', 'rank': 'Top'},
    'University College London': {'abbr': 'UCL', 'country': 'UK', 'rank': 'Top'},
    'University of Edinburgh': {'abbr': 'Edinburgh', 'country': 'UK', 'rank': 'Top'},

    # 欧洲
    'ETH Zurich': {'abbr': 'ETH', 'country': 'Switzerland', 'rank': 'Top'},
    'EPFL': {'abbr': 'EPFL', 'country': 'Switzerland', 'rank': 'Top'},

    # 亚洲
    'National University of Singapore': {'abbr': 'NUS', 'country': 'Singapore', 'rank': 'Top'},
    'Nanyang Technological University': {'abbr': 'NTU', 'country': 'Singapore', 'rank': 'Top'},
    'The University of Tokyo': {'abbr': 'UTokyo', 'country': 'Japan', 'rank': 'Top'},
    'Seoul National University': {'abbr': 'SNU', 'country': 'South Korea', 'rank': 'Top'},
    'KAIST': {'abbr': 'KAIST', 'country': 'South Korea', 'rank': 'Top'},

    # 澳洲
    'Australian National University': {'abbr': 'ANU', 'country': 'Australia', 'rank': 'Top'},
    'University of Melbourne': {'abbr': 'Melbourne', 'country': 'Australia', 'rank': 'Top'},
    'University of Sydney': {'abbr': 'Sydney', 'country': 'Australia', 'rank': 'Top'},
}

# 知名科技公司和研究机构
TECH_COMPANIES = {
    # 美国科技巨头
    'Google': {'type': 'Company', 'country': 'USA'},
    'Google Brain': {'type': 'Research Lab', 'country': 'USA'},
    'Google DeepMind': {'type': 'Research Lab', 'country': 'USA'},
    'DeepMind': {'type': 'Research Lab', 'country': 'UK'},
    'OpenAI': {'type': 'Research Lab', 'country': 'USA'},
    'Meta': {'type': 'Company', 'country': 'USA'},
    'Meta AI': {'type': 'Research Lab', 'country': 'USA'},
    'Facebook': {'type': 'Company', 'country': 'USA'},
    'Microsoft': {'type': 'Company', 'country': 'USA'},
    'Microsoft Research': {'type': 'Research Lab', 'country': 'USA'},
    'Apple': {'type': 'Company', 'country': 'USA'},
    'Amazon': {'type': 'Company', 'country': 'USA'},
    'NVIDIA': {'type': 'Company', 'country': 'USA'},
    'Tesla': {'type': 'Company', 'country': 'USA'},
    'IBM': {'type': 'Company', 'country': 'USA'},
    'IBM Research': {'type': 'Research Lab', 'country': 'USA'},

    # 中国科技公司
    'Alibaba': {'type': 'Company', 'country': 'China'},
    'Alibaba DAMO Academy': {'type': 'Research Lab', 'country': 'China'},
    'Tencent': {'type': 'Company', 'country': 'China'},
    'Tencent AI Lab': {'type': 'Research Lab', 'country': 'China'},
    'ByteDance': {'type': 'Company', 'country': 'China'},
    'Bytedance': {'type': 'Company', 'country': 'China'},
    'Baidu': {'type': 'Company', 'country': 'China'},
    'Baidu Research': {'type': 'Research Lab', 'country': 'China'},
    'Huawei': {'type': 'Company', 'country': 'China'},
    'Huawei Noah\'s Ark Lab': {'type': 'Research Lab', 'country': 'China'},
    'SenseTime': {'type': 'Company', 'country': 'China'},
    'Megvii': {'type': 'Company', 'country': 'China'},
    'DJI': {'type': 'Company', 'country': 'China'},
    'Meituan': {'type': 'Company', 'country': 'China'},

    # 其他
    'Samsung': {'type': 'Company', 'country': 'South Korea'},
    'Sony': {'type': 'Company', 'country': 'Japan'},
}

# 合并所有机构
ALL_INSTITUTIONS = {
    **CHINA_985_UNIVERSITIES,
    **QS_TOP_50_UNIVERSITIES,
    **TECH_COMPANIES,
}

# 机构名称变体映射
INSTITUTION_VARIANTS = {
    # 清华大学
    'tsinghua': 'Tsinghua University',
    'thu': 'Tsinghua University',
    'tsinghua univ': 'Tsinghua University',
    'tsinghua u': 'Tsinghua University',

    # 北京大学
    'peking': 'Peking University',
    'pku': 'Peking University',
    'peking univ': 'Peking University',
    'beijing university': 'Peking University',

    # MIT
    'mit': 'Massachusetts Institute of Technology',
    'massachusetts institute of technology': 'Massachusetts Institute of Technology',

    # Stanford
    'stanford': 'Stanford University',
    'stanford univ': 'Stanford University',
    'stanford u': 'Stanford University',

    # Berkeley
    'berkeley': 'University of California, Berkeley',
    'uc berkeley': 'University of California, Berkeley',
    'ucb': 'University of California, Berkeley',

    # CMU
    'cmu': 'Carnegie Mellon University',
    'carnegie mellon': 'Carnegie Mellon University',

    # NUS
    'nus': 'National University of Singapore',
    'national university of singapore': 'National University of Singapore',

    # Google
    'google': 'Google',
    'google brain': 'Google Brain',
    'google deepmind': 'Google DeepMind',
    'deepmind': 'DeepMind',

    # OpenAI
    'openai': 'OpenAI',
    'open ai': 'OpenAI',

    # Meta
    'meta': 'Meta',
    'facebook': 'Meta',
    'meta ai': 'Meta AI',

    # Microsoft
    'microsoft': 'Microsoft',
    'msft': 'Microsoft',
    'microsoft research': 'Microsoft Research',
    'msr': 'Microsoft Research',

    # ByteDance
    'bytedance': 'ByteDance',
    'byte dance': 'ByteDance',
    'tiktok': 'ByteDance',

    # 新增美国大学变体
    'vanderbilt': 'Vanderbilt University',
    'vanderbilt univ': 'Vanderbilt University',
    'penn state': 'Pennsylvania State University',
    'pennsylvania state': 'Pennsylvania State University',
    'psu': 'Pennsylvania State University',
    'rice': 'Rice University',
    'rice univ': 'Rice University',
    'notre dame': 'University of Notre Dame',
    'washu': 'Washington University in St. Louis',
    'washington university': 'Washington University in St. Louis',
    'brown': 'Brown University',
    'dartmouth': 'Dartmouth College',
    'emory': 'Emory University',
    'usc': 'University of Southern California',
    'uc davis': 'University of California, Davis',
    'uc irvine': 'University of California, Irvine',
    'ucsb': 'University of California, Santa Barbara',
    'uw madison': 'University of Wisconsin-Madison',
    'wisconsin': 'University of Wisconsin-Madison',
    'unc': 'University of North Carolina at Chapel Hill',
    'uf': 'University of Florida',
    'bu': 'Boston University',
    'boston univ': 'Boston University',
    'osu': 'Ohio State University',
    'ohio state': 'Ohio State University',
    'purdue': 'Purdue University',
    'umd': 'University of Maryland',
    'maryland': 'University of Maryland',
    'umn': 'University of Minnesota',
    'minnesota': 'University of Minnesota',
    'pitt': 'University of Pittsburgh',
    'pittsburgh': 'University of Pittsburgh',
    'rutgers': 'Rutgers University',
    'uva': 'University of Virginia',
    'virginia': 'University of Virginia',
    'umass': 'University of Massachusetts Amherst',
    'tamu': 'Texas A&M University',
    'texas a&m': 'Texas A&M University',
    'cu boulder': 'University of Colorado Boulder',
    'colorado': 'University of Colorado Boulder',
    'asu': 'Arizona State University',
    'arizona state': 'Arizona State University',
    'msu': 'Michigan State University',
    'michigan state': 'Michigan State University',
    'ua': 'University of Arizona',
    'arizona': 'University of Arizona',

    # Alibaba
    'alibaba': 'Alibaba',
    'ali': 'Alibaba',
    'damo academy': 'Alibaba DAMO Academy',
    'damo': 'Alibaba DAMO Academy',

    # Tencent
    'tencent': 'Tencent',
    'tencent ai lab': 'Tencent AI Lab',

    # 其他中国大学简称
    'sjtu': 'Shanghai Jiao Tong University',
    'zju': 'Zhejiang University',
    'nju': 'Nanjing University',
    'ustc': 'University of Science and Technology of China',
    'fdu': 'Fudan University',
    'hku': 'The University of Hong Kong',
    'cuhk': 'The Chinese University of Hong Kong',
    'hkust': 'Hong Kong University of Science and Technology',
}


def normalize_institution_name(institution_text: str) -> str:
    """
    标准化机构名称

    Args:
        institution_text: 原始机构名称

    Returns:
        标准化后的名称，如果无法识别则返回原始名称
    """
    if not institution_text:
        return ''

    # 转小写并去除多余空格
    inst_lower = institution_text.lower().strip()

    # 查找变体映射
    if inst_lower in INSTITUTION_VARIANTS:
        return INSTITUTION_VARIANTS[inst_lower]

    # 尝试部分匹配
    for variant, standard in INSTITUTION_VARIANTS.items():
        if variant in inst_lower:
            return standard

    # 如果无法识别，返回原始名称
    return institution_text


def is_top_institution(institution_name: str) -> bool:
    """
    判断是否为知名机构

    Args:
        institution_name: 机构名称

    Returns:
        是否为知名机构
    """
    normalized = normalize_institution_name(institution_name)
    return normalized in ALL_INSTITUTIONS


def get_institution_info(institution_name: str) -> dict:
    """
    获取机构详细信息

    Args:
        institution_name: 机构名称

    Returns:
        包含机构信息的字典，如果不是知名机构则返回 None
    """
    normalized = normalize_institution_name(institution_name)
    return ALL_INSTITUTIONS.get(normalized)


def extract_institutions_from_authors(authors: list) -> list:
    """
    从作者列表中提取知名机构

    Args:
        authors: 作者列表，格式为 [{'name': str, 'affiliation': str}, ...]

    Returns:
        知名机构列表（去重）
    """
    institutions = set()

    for author in authors:
        if isinstance(author, dict):
            affiliation = author.get('affiliation', '')
        else:
            affiliation = str(author)

        if not affiliation:
            continue

        # 检查是否包含知名机构
        affiliation_lower = affiliation.lower()
        for variant, standard in INSTITUTION_VARIANTS.items():
            if variant in affiliation_lower:
                institutions.add(standard)
                break

    return list(institutions)
