# PaperBrain 配置说明

本文档说明 PaperBrain 的各项配置选项和优化建议。

---

## 📋 目录

- [环境变量配置](#环境变量配置)
- [筛选阈值配置](#筛选阈值配置)
- [Semantic Scholar API 配置](#semantic-scholar-api-配置)
- [性能优化建议](#性能优化建议)

---

## 环境变量配置

### 必需配置

在 `.env` 文件中配置以下变量：

```bash
# LLM API 配置（必需）
LLM_API_URL=https://your-api-endpoint.com/v1/chat/completions
LLM_BEARER_TOKEN=your_bearer_token_here

# Doubao API 配置（Auto-Scholar 功能必需）
DOUBAO_API_URL=https://aigc.sankuai.com/v1/openai/native/chat/completions
DOUBAO_BEARER_TOKEN=your_doubao_token_here
```

### 可选配置

```bash
# 数据库路径（默认：data/paperbrain.db）
DATABASE_PATH=data/paperbrain.db

# 向量数据库路径（默认：data/chroma_db）
CHROMA_DB_PATH=data/chroma_db

# 文件存储路径
PAPERS_DIR=data/papers
IMAGES_DIR=data/images

# LLM 模型配置
MODEL_NAME=gemini-pro
TEMPERATURE=0.7
MAX_TOKENS=8192

# RAG 配置
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5

# Auto-Scholar 配置
ARXIV_CATEGORIES=cs.AI,cs.LG,cs.CL,math.OC
ARXIV_MAX_RESULTS=200
SCORE_THRESHOLD=5.0

# Semantic Scholar API（可选，提高筛选质量）
S2_API_KEY=your_s2_api_key_here
S2_MIN_CITATIONS=3
S2_MIN_INFLUENTIAL=1
```

---

## 筛选阈值配置

### 元数据筛选阈值

在 `services/scheduler.py` 中配置：

```python
# 阶段 1：基础筛选阈值
papers = metadata_scorer.batch_filter(papers, min_score=4.0)

# 阶段 3：二次筛选阈值
if new_score >= 5.0:
    papers_with_institutions.append(paper)
```

**阈值效果参考**（基于 200 篇论文的统计）：

| 阈值 | 保留论文数 | 过滤率 | 适用场景 |
|------|-----------|--------|---------|
| 3.0 | 200 篇 | 0% | 不推荐（无筛选效果） |
| 4.0 | 188 篇 | 7% | 基础筛选（过滤明显低质量） |
| 5.0 | 98 篇 | 51% | **推荐**（平衡质量和数量） |
| 6.0 | 46 篇 | 77% | 严格筛选（只保留高质量） |
| 7.0 | 0 篇 | 100% | 过于严格（不推荐） |

**调整建议**：

1. **宽松筛选**（保留更多论文）：
   ```python
   # 阶段 1: 3.5, 阶段 3: 4.5
   papers = metadata_scorer.batch_filter(papers, min_score=3.5)
   if new_score >= 4.5:
   ```

2. **标准筛选**（推荐）：
   ```python
   # 阶段 1: 4.0, 阶段 3: 5.0（默认配置）
   papers = metadata_scorer.batch_filter(papers, min_score=4.0)
   if new_score >= 5.0:
   ```

3. **严格筛选**（只保留高质量）：
   ```python
   # 阶段 1: 4.5, 阶段 3: 6.0
   papers = metadata_scorer.batch_filter(papers, min_score=4.5)
   if new_score >= 6.0:
   ```

### 元数据评分规则

元数据评分由以下维度组成（总分 10 分）：

1. **关键词匹配度**（0-4 分）
   - 高权重关键词（如 "neural combinatorial optimization"）：3.0 分
   - 中权重关键词（如 "transformer"）：1.5 分
   - 低权重关键词（如 "machine learning"）：0.5 分

2. **机构权重**（0-2 分）
   - 每个知名机构作者：+0.5 分
   - 最多 2 分

3. **摘要质量**（0-2 分）
   - 适中长度（800-2000 字符）：+1.0 分
   - 包含量化结果：+0.5 分
   - 包含方法论关键词：+0.5 分

4. **时效性**（0-0.5 分）
   - 3 天内：+0.5 分
   - 7 天内：+0.3 分

**自定义关键词权重**：

在 `services/metadata_scorer.py` 中修改：

```python
self.keyword_weights = {
    # 添加你的高权重关键词
    'your_keyword': 3.0,

    # 调整现有关键词权重
    'reinforcement learning': 2.5,  # 默认 2.0
}
```

---

## Semantic Scholar API 配置

### 申请 API Key

1. 访问：https://www.semanticscholar.org/product/api
2. 注册账号并申请 API Key（免费）
3. 在 `.env` 中配置：
   ```bash
   S2_API_KEY=your_api_key_here
   ```

### API Key 的作用

**有 API Key**：
- 速率限制：10 请求/秒
- 可以获取论文的引用数、影响力引用数、venue 等信息
- 提供额外的筛选维度

**无 API Key**：
- 速率限制：1 请求/秒（且经常失败）
- S2 筛选会被自动跳过
- 不影响核心功能（PDF 提取仍然有效）

### S2 筛选配置

在 `services/scheduler.py` 中：

```python
# 配置引用数和影响力引用数阈值
papers = semantic_scholar_filter.batch_filter(
    papers,
    min_citations=3,        # 最小引用数
    min_influential=1       # 最小影响力引用数
)
```

**注意**：
- 2024+ 年份的论文会自动通过（新论文还没有引用）
- 如果没有 API Key，S2 筛选会被跳过

---

## 性能优化建议

### 1. 减少 PDF 提取时间

**当前瓶颈**：元数据筛选阶段需要提取 PDF（每篇约 3-5 秒）

**优化方案**：

1. **提高基础筛选阈值**（减少需要提取 PDF 的论文数）：
   ```python
   # 从 4.0 提高到 4.5
   papers = metadata_scorer.batch_filter(papers, min_score=4.5)
   ```

2. **并行 PDF 提取**（未实现，需要开发）：
   ```python
   # 使用多线程并行下载和解析
   from concurrent.futures import ThreadPoolExecutor
   with ThreadPoolExecutor(max_workers=5) as executor:
       results = executor.map(extract_from_arxiv_pdf, arxiv_ids)
   ```

### 2. 减少 AI 评分时间

**当前瓶颈**：AI 评分每篇约 15 秒

**优化方案**：

1. **提高元数据筛选阈值**（减少需要 AI 评分的论文数）
2. **使用更快的 LLM 模型**（如果可用）
3. **批量评分**（未实现，需要 API 支持）

### 3. 缓存优化

**建议实现**：

1. **缓存 PDF 提取结果**：
   ```python
   # 在 pdf_metadata_extractor.py 中添加缓存
   import json
   from pathlib import Path

   cache_file = Path('data/pdf_cache.json')
   if arxiv_id in cache:
       return cache[arxiv_id]
   ```

2. **缓存 LLM 评分结果**：
   - 对于已评分的论文，不重复评分
   - 数据库中已有 `score` 字段，可以直接使用

### 4. 网络优化

1. **使用代理**（如果 arXiv 访问慢）：
   ```python
   # 在 pdf_metadata_extractor.py 中
   proxies = {
       'http': 'http://your-proxy:port',
       'https': 'http://your-proxy:port',
   }
   response = requests.get(url, proxies=proxies)
   ```

2. **增加超时时间**（如果网络不稳定）：
   ```python
   response = requests.get(url, timeout=60)  # 默认 30 秒
   ```

---

## 常见问题

### Q1: 元数据筛选过滤太多/太少论文？

**A**: 调整筛选阈值：
- 过滤太多：降低阈值（4.0 → 3.5）
- 过滤太少：提高阈值（4.0 → 4.5 或 5.0）

### Q2: PDF 提取失败率高？

**A**: 可能的原因：
1. 网络问题：检查 arXiv 访问是否正常
2. PDF 格式问题：部分论文 PDF 可能损坏
3. LLM 提取失败：检查 Doubao API 是否正常

**解决方案**：
- 增加重试次数
- 使用代理
- 检查日志中的具体错误信息

### Q3: S2 筛选不生效？

**A**: 检查：
1. 是否配置了 `S2_API_KEY`
2. API Key 是否有效
3. 查看日志中是否有 "⏭️ 跳过 S2 筛选" 的提示

### Q4: 如何查看详细的筛选日志？

**A**:
1. 在终端运行 Streamlit（而不是后台运行）
2. 查看终端输出的详细日志
3. 使用分析工具：`python analyze_metadata_scores.py`

---

## 版本历史

- **v1.3.0** (2026-02-12): 优化筛选流程，添加 PDF 提取功能
- **v1.2.0** (2026-02-12): 添加 venue 和 institutions 识别
- **v1.1.0** (2026-02-05): 添加 Auto-Scholar 功能

---

## 相关文档

- [更新日志](CHANGELOG.md)
- [详细更新日志 v1.3.0](UPDATE_LOG_V1.3.0.md)
- [技术文档](TECHNICAL_DOCUMENTATION.md)
- [使用指南](AUTO_SCHOLAR_GUIDE.md)
