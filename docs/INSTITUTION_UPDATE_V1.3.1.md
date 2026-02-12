# 机构配置补充说明 - v1.3.1

**更新日期**: 2026-02-12
**类型**: 配置补充

---

## 📋 问题描述

用户反馈论文 "Grid-Aware Charging and Operational Optimization for Mixed-Fleet Public Transit" (arXiv: 2601.08753) 的机构信息未被识别。

该论文明确标注了：
- Institute for Software Integrated Systems, **Vanderbilt University**
- **Pennsylvania State University**

但这两所大学都没有显示机构徽章。

---

## 🔍 问题分析

### 根本原因

`config/institutions.py` 中只包含了 **QS Top 50 大学**，但很多美国优秀大学（US News Top 70）不在 QS Top 50 中，导致被遗漏。

**缺失的重要大学**：
- Vanderbilt University（范德堡大学，US News #18）
- Pennsylvania State University（宾州州立大学，US News #60）
- 以及其他 30+ 所美国 Top 70 大学

### 测试验证

```python
# 修复前
normalize_institution_name('Vanderbilt University')
# → 'Vanderbilt University'
is_top_institution('Vanderbilt University')
# → False ❌

# 修复后
normalize_institution_name('Vanderbilt University')
# → 'Vanderbilt University'
is_top_institution('Vanderbilt University')
# → True ✅
```

---

## ✅ 解决方案

### 新增 30 所 US News Top 70 美国大学

在 `config/institutions.py` 的 `QS_TOP_50_UNIVERSITIES` 字典中添加：

```python
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
```

### 新增名称变体映射

在 `INSTITUTION_VARIANTS` 字典中添加常用缩写和变体：

```python
# 新增美国大学变体
'vanderbilt': 'Vanderbilt University',
'penn state': 'Pennsylvania State University',
'psu': 'Pennsylvania State University',
'rice': 'Rice University',
'notre dame': 'University of Notre Dame',
'washu': 'Washington University in St. Louis',
'brown': 'Brown University',
'dartmouth': 'Dartmouth College',
'emory': 'Emory University',
'usc': 'University of Southern California',
'uc davis': 'University of California, Davis',
'uc irvine': 'University of California, Irvine',
'ucsb': 'University of California, Santa Barbara',
'uw madison': 'University of Wisconsin-Madison',
'unc': 'University of North Carolina at Chapel Hill',
'uf': 'University of Florida',
'bu': 'Boston University',
'osu': 'Ohio State University',
'purdue': 'Purdue University',
'umd': 'University of Maryland',
'umn': 'University of Minnesota',
'pitt': 'University of Pittsburgh',
'rutgers': 'Rutgers University',
'uva': 'University of Virginia',
'umass': 'University of Massachusetts Amherst',
'tamu': 'Texas A&M University',
'cu boulder': 'University of Colorado Boulder',
'asu': 'Arizona State University',
'msu': 'Michigan State University',
'ua': 'University of Arizona',
```

---

## 📊 更新后的覆盖范围

| 类别 | 数量 | 说明 |
|------|------|------|
| 中国 985 大学 | 39 所 | 包含清华、北大、C9 联盟等 |
| QS Top 50 大学 | ~30 所 | 全球顶尖大学 |
| US News Top 70 美国大学 | ~60 所 | **新增 30 所** |
| 知名科技公司 | 20+ 家 | Google, OpenAI, Meta, 阿里, 腾讯等 |
| **总计** | **~120 所** | 覆盖全球主要研究机构 |

---

## 🧪 测试结果

### 测试用例：arXiv 2601.08753

```bash
python -c "
from services.pdf_metadata_extractor import extract_from_arxiv_pdf
venue, venue_year, institutions = extract_from_arxiv_pdf('2601.08753')
print(f'Institutions: {institutions}')
"
```

**输出**：
```
Institutions: ['Vanderbilt University', 'Pennsylvania State University']
```

**验证**：
```
✅ Vanderbilt University → 识别成功
✅ Pennsylvania State University → 识别成功
✅ Penn State → 标准化为 Pennsylvania State University
```

---

## 📝 使用建议

### 1. 重新抓取论文

新抓取的论文会自动识别这些大学：

```bash
streamlit run app.py
# 进入 Auto-Scholar 页面，点击"立即抓取"
```

### 2. 更新现有论文

为已存在的论文补充机构信息：

```bash
# 更新所有论文
python scripts/update_venue_institutions.py

# 只更新最近的 20 篇
python scripts/update_venue_institutions.py --limit 20

# 指定日期范围
python scripts/update_venue_institutions.py --date-from 2026-01-01
```

### 3. 自定义添加机构

如果需要添加其他机构，在 `config/institutions.py` 中：

```python
# 1. 添加到对应的字典
QS_TOP_50_UNIVERSITIES = {
    # ...
    'Your University': {'abbr': 'YU', 'country': 'Country', 'rank': 'Top'},
}

# 2. 添加名称变体（可选）
INSTITUTION_VARIANTS = {
    # ...
    'your univ': 'Your University',
    'yu': 'Your University',
}
```

---

## 🔄 后续优化

### 建议补充的机构

1. **欧洲大学**：
   - Technical University of Munich (TUM)
   - KU Leuven
   - University of Amsterdam
   - 等

2. **亚洲大学**：
   - 香港科技大学（已有）
   - 复旦大学（已有）
   - 更多日韩大学

3. **研究机构**：
   - Max Planck Institute
   - INRIA
   - Allen Institute for AI
   - 等

### 自动化建议

考虑实现：
- 从 QS/US News 官方排名自动更新机构列表
- 支持用户自定义机构配置文件
- 机构识别的模糊匹配算法优化

---

## 📚 相关文档

- [配置说明](CONFIGURATION.md)
- [更新日志 v1.3.0](UPDATE_LOG_V1.3.0.md)
- [CHANGELOG](CHANGELOG.md)

---

**更新完成时间**: 2026-02-12 19:00
**测试状态**: ✅ 已测试通过
**影响范围**: 所有使用机构识别功能的模块
