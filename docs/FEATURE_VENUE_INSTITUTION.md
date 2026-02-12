# 顶刊顶会和知名机构展示功能说明

## 功能概述

本功能为 Auto-Scholar 论文卡片添加了顶级会议/期刊和知名机构的自动识别与徽章展示，帮助用户快速识别高质量论文和权威研究机构。

---

## 功能特性

### 1. 顶刊顶会识别

自动识别论文发表的顶级会议和期刊，包括：

#### AI 领域顶会
- **机器学习**：NeurIPS, ICML, ICLR
- **计算机视觉**：CVPR, ICCV, ECCV
- **自然语言处理**：ACL, EMNLP, NAACL
- **人工智能综合**：AAAI, IJCAI
- **数据挖掘**：KDD, SIGIR, WWW
- **强化学习**：AAMAS

#### AI 领域顶刊
- JMLR, TPAMI, IJCV, AIJ, JAIR

#### 运筹学和优化领域
- **顶会**：INFORMS, EURO, ISMP
- **顶刊**：Operations Research, Management Science, Mathematical Programming, EJOR, INFORMS JOC, COR

#### 交通运输领域
- **顶会**：TRB, ITSC, IV, WCTR
- **顶刊**：Transportation Research (Part A/B/C/D/E), Transportation Science

### 2. 知名机构识别

自动识别论文作者所属的知名高校和科技公司，包括：

#### 中国985大学（39所）
- **C9联盟**：清华、北大、复旦、上交、浙大、南大、中科大、哈工大、西交
- **其他985**：北航、北理、北师大、南开、天大、大连理工、吉大、东北大学、同济、华东师大、厦大、山大、武大、华科、中南、中山、华南理工、川大、重大、电子科大、人大、农大、海洋大学、西工大、兰大、东南、湖大、国防科大、中央民族
- **香港**：港大、中文大学、科技大学

#### QS前50大学
- **美国**：MIT, Stanford, Harvard, Caltech, UC Berkeley, UChicago, UPenn, Cornell, Princeton, Yale, Columbia, UCLA, CMU, UMich, NYU, Northwestern, Duke, JHU, UCSD, UW, Georgia Tech, UT Austin, UIUC
- **英国**：Oxford, Cambridge, Imperial, UCL, Edinburgh
- **欧洲**：ETH Zurich, EPFL
- **亚洲**：NUS, NTU, UTokyo, SNU, KAIST
- **澳洲**：ANU, Melbourne, Sydney

#### 知名科技公司
- **美国**：Google, Google Brain, Google DeepMind, DeepMind, OpenAI, Meta, Meta AI, Microsoft, Microsoft Research, Apple, Amazon, NVIDIA, Tesla, IBM
- **中国**：Alibaba, Alibaba DAMO Academy, Tencent, Tencent AI Lab, ByteDance, Baidu, Baidu Research, Huawei, Huawei Noah's Ark Lab, SenseTime, Megvii, DJI, Meituan
- **其他**：Samsung, Sony

---

## 实现原理

### 数据流程

```
论文标题 + 摘要 + 作者信息
    ↓
LLM 提取（豆包 API）
    ↓
提取 venue, venue_year, institutions
    ↓
标准化处理
    ├─ 会议/期刊名称标准化
    ├─ 机构名称标准化
    └─ 过滤非顶级会议/机构
    ↓
存储到数据库
    ↓
UI 徽章展示
```

### 技术实现

#### 1. LLM 提取

修改评分 Prompt，要求 LLM 在评分时同时提取：
- `venue`: 会议/期刊名称（如 "ICLR", "NeurIPS"）
- `venue_year`: 年份（如 2026）
- `institutions`: 知名机构列表（如 ["MIT", "Google"]）

**优势**：
- 复用现有 API 调用，无额外成本
- 准确率高，能理解上下文
- 支持多种表述方式

#### 2. 标准化处理

使用配置文件进行名称标准化：

**会议/期刊标准化** (`config/venues.py`)：
```python
VENUE_VARIANTS = {
    'neurips': 'NeurIPS',
    'nips': 'NeurIPS',
    'iclr': 'ICLR',
    'cvpr': 'CVPR',
    # ... 更多变体
}

def normalize_venue_name(venue_text: str) -> str:
    """标准化会议/期刊名称"""
    venue_lower = venue_text.lower().strip()
    if venue_lower in VENUE_VARIANTS:
        return VENUE_VARIANTS[venue_lower]
    return venue_text.title()
```

**机构标准化** (`config/institutions.py`)：
```python
INSTITUTION_VARIANTS = {
    'mit': 'Massachusetts Institute of Technology',
    'thu': 'Tsinghua University',
    'google': 'Google',
    # ... 更多变体
}

def normalize_institution_name(institution_text: str) -> str:
    """标准化机构名称"""
    inst_lower = institution_text.lower().strip()
    if inst_lower in INSTITUTION_VARIANTS:
        return INSTITUTION_VARIANTS[inst_lower]
    return institution_text
```

#### 3. 后备提取

如果 LLM 未提取到机构信息，从作者的 `affiliation` 字段中提取：

```python
def extract_institutions_from_authors(authors: list) -> list:
    """从作者列表中提取知名机构"""
    institutions = set()
    for author in authors:
        affiliation = author.get('affiliation', '')
        # 检查是否包含知名机构
        for variant, standard in INSTITUTION_VARIANTS.items():
            if variant in affiliation.lower():
                institutions.add(standard)
    return list(institutions)
```

#### 4. UI 展示

使用 HTML 徽章样式展示：

```python
# 会议/期刊徽章（紫色）
if paper.venue:
    venue_display = f"{paper.venue} {paper.venue_year}" if paper.venue_year else paper.venue
    badge = f'<span style="background:#9b59b6;color:white;padding:4px 10px;'
            f'border-radius:12px;font-size:13px;">📍 {venue_display}</span>'

# 知名机构徽章（青绿色）
if paper.institutions:
    institutions_display = ', '.join(paper.institutions[:3])
    badge = f'<span style="background:#16a085;color:white;padding:4px 10px;'
            f'border-radius:12px;font-size:13px;">🏛️ {institutions_display}</span>'
```

---

## 数据库设计

### ArxivPaper 表新增字段

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `venue` | String(200) | 会议/期刊名称 | "ICLR", "NeurIPS" |
| `venue_year` | Integer | 年份 | 2026 |
| `institutions` | JSON | 知名机构列表 | ["MIT", "Google Brain"] |

### 数据库迁移

运行迁移脚本添加新字段：

```bash
python database/migrate_add_venue_institutions.py
```

---

## 使用示例

### 示例1：顶会论文

**输入**：
- 标题：`Accepted to ICLR 2026: Deep Reinforcement Learning for Vehicle Routing`
- 摘要：`We propose a novel approach...`
- 作者：`[{'name': 'John Doe', 'affiliation': 'MIT'}, ...]`

**输出**：
- `venue`: "ICLR"
- `venue_year`: 2026
- `institutions`: ["MIT"]

**UI 展示**：
```
📍 ICLR 2026  🏛️ MIT
```

### 示例2：多机构合作

**输入**：
- 标题：`Neural Combinatorial Optimization`
- 摘要：`Authors from Google Brain and Stanford University...`
- 作者：`[{'name': 'Jane Smith', 'affiliation': 'Google Brain'}, ...]`

**输出**：
- `venue`: ""
- `venue_year`: null
- `institutions`: ["Google Brain", "Stanford University"]

**UI 展示**：
```
🏛️ Google Brain, Stanford University
```

### 示例3：中国高校

**输入**：
- 标题：`Deep Learning for Traffic Prediction`
- 摘要：`...`
- 作者：`[{'name': 'Li Ming', 'affiliation': 'Tsinghua University'}, ...]`

**输出**：
- `venue`: ""
- `venue_year`: null
- `institutions`: ["Tsinghua University"]

**UI 展示**：
```
🏛️ Tsinghua University
```

---

## 配置管理

### 添加新的顶会顶刊

编辑 `config/venues.py`：

```python
AI_TOP_CONFERENCES = {
    'NewConf': {'full_name': 'New Conference Name', 'rank': 'A*'},
    # ... 其他会议
}

VENUE_VARIANTS = {
    'newconf': 'NewConf',
    'new conference': 'NewConf',
    # ... 其他变体
}
```

### 添加新的知名机构

编辑 `config/institutions.py`：

```python
QS_TOP_50_UNIVERSITIES = {
    'New University': {'abbr': 'NU', 'country': 'USA', 'rank': 'Top'},
    # ... 其他大学
}

INSTITUTION_VARIANTS = {
    'nu': 'New University',
    'new univ': 'New University',
    # ... 其他变体
}
```

---

## 测试验证

### 运行测试脚本

```bash
python test_venue_institution.py
```

### 测试内容

1. **会议/期刊识别测试**
   - 测试标准化功能
   - 测试变体识别
   - 测试顶会判断

2. **机构识别测试**
   - 测试标准化功能
   - 测试变体识别
   - 测试知名机构判断

3. **作者信息提取测试**
   - 测试从 affiliation 提取机构
   - 测试去重和过滤

### 测试结果

```
✅ 会议/期刊识别：通过
✅ 机构识别：通过
✅ 作者信息提取：通过
✅ 所有测试完成
```

---

## 注意事项

### 1. LLM 提取准确性

- LLM 提取依赖于标题和摘要中的信息
- 如果论文未明确提到会议/期刊，可能无法识别
- 建议：在论文标题中包含会议信息（如 "Accepted to ICLR 2026"）

### 2. 机构名称标准化

- 机构名称有多种表述方式（如 MIT, Massachusetts Institute of Technology）
- 系统会自动标准化为统一格式
- 如果遇到未识别的机构，可以添加到配置文件中

### 3. 性能影响

- 复用现有 API 调用，无额外成本
- 标准化处理在本地完成，速度快
- 对整体性能影响可忽略不计

### 4. 数据迁移

- 已有数据的 venue 和 institutions 字段为空
- 重新抓取论文时会自动填充新字段
- 可以手动运行评分更新脚本（如需要）

---

## 未来优化方向

### 1. 增强识别能力

- 集成 Semantic Scholar API 获取更准确的 venue 信息
- 使用 OpenAlex 等学术数据库补充机构信息
- 支持更多会议和期刊

### 2. 机构排名展示

- 添加机构排名信息（如 QS 排名）
- 根据排名调整徽章颜色
- 支持按机构排名筛选论文

### 3. 会议影响力评分

- 添加会议影响因子（如 CCF 分类）
- 根据会议等级调整徽章样式
- 支持按会议等级筛选论文

### 4. 统计分析

- 统计各机构发表论文数量
- 统计各会议收录论文数量
- 生成机构和会议的趋势分析

---

## 相关文档

- [更新日志](CHANGELOG.md)
- [技术文档](TECHNICAL_DOCUMENTATION.md)
- [Auto-Scholar 使用指南](AUTO_SCHOLAR_GUIDE.md)
- [产品需求文档](PRD.md)

---

## 联系方式

如有问题或建议，请联系：
- 开发人员：Claude Code
- 开发日期：2026-02-12
- 版本：v1.2.0
