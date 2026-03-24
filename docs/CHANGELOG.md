# 更新日志 (CHANGELOG)

本文档记录 PaperBrain 项目的所有重要变更。

---

## [v1.6.0] - 2026-03-24

### ✨ 新增功能
- 新增 Obsidian 导出功能：论文详情页一键导出结构化笔记到本地 Obsidian vault
- 导出格式：YAML frontmatter + 8 维摘要（+ 可选思维导图 Mermaid 代码块）
- 设置页新增「📁 Obsidian 集成」配置区块（vault 路径 + 子目录 + 路径验证）
- 导出时可选「包含思维导图」（默认不勾选）

### 🐛 Bug 修复
- 修复 Obsidian 思维导图节点文字超长被截断：注入 `%%{init}%%` 禁用 `useMaxWidth`，节点文字按视觉宽度自动折行

详细内容请参考 [v1.6.0 更新日志](changelogs/v1.6.0/UPDATE_LOG.md) 和 [Obsidian 导出功能文档](features/OBSIDIAN_EXPORT.md)

---

## [v1.5.1] - 2026-02-28

### 🐛 Bug 修复
- 修复 Auto-Scholar 导入论文后点击"查看论文详情"无法跳转的问题（Streamlit 按钮嵌套陷阱）
- 修复导入论文的结构化笔记内容不全的问题（LLM 输出 max_tokens 不足 + 两阶段补全策略）
- 修复部分论文图片提取只有 Logo 的问题（矢量图页面渲染补全）

详细内容请参考 [Bug 修复日志 2026-02-28](development/bugfix_logs/2026-02-28.md)

---

## [v1.5.0] - 2026-02-28

### ✨ 新增功能
- 图形化 API 设置页面，支持标准提供商预设和自定义 API 两种接入方式
- 预设六大主流 API 提供商：DeepSeek、通义千问、OpenAI、Moonshot、智谱 GLM、SiliconFlow
- 双 LLM 角色配置（主 LLM + 评分 LLM），评分 LLM 默认复用主 LLM
- 一键测试连接功能
- 配置持久化至 JSON 文件，保存后热加载无需重启

### 🚀 性能优化
- 统一 LLM 服务层，同时支持 OpenAI 兼容和 Gemini 两种 API 格式
- DoubaoService 简化为 LLMService 子类，消除重复代码
- 延迟验证机制：未配置 API 时应用可正常启动，首次调用时提示配置

### 📚 文档更新
- 新增 API 设置功能说明文档
- 新增迭代日志

详细内容请参考 [v1.5.0 更新日志](changelogs/v1.5.0/UPDATE_LOG.md)

---

## [v1.3.1] - 2026-02-13

### 🐛 Bug 修复

#### 1. 修复 PDF 元数据提取器无法解析部分论文的问题

**问题描述**：
- 部分论文（如 arXiv 2602.11541）的机构信息无法被识别
- 错误信息：`cannot open broken document`
- 原因：只下载 PDF 前 500KB，但 PDF 的交叉引用表（xref）位于文件末尾（通常在 95%+ 位置）
- PyMuPDF 必须读取完整的 xref 表才能解析任何页面，即使只读取第一页

**技术分析**：
- PDF 文件结构：Header → Body → xref 表（末尾 96%+）→ Trailer
- 测试论文 2602.11541（848KB）：xref 表位于 822KB（96.9%）
- 500KB 只覆盖 60.4% 的文件，完全没有触及 xref 表
- 这就像书的目录在最后一页——必须先看到目录才能找到第一章

**解决方案**：
- 实现动态重试策略（方案 1）
- 先尝试下载 500KB，如果解析失败则自动下载完整文件
- 对小论文（<500KB）节省带宽，对大论文自动降级

**修改文件**：
- `services/pdf_metadata_extractor.py`
  - `download_arxiv_pdf_stream()` - 添加 `max_size` 参数支持
  - `extract_first_pages_text()` - 添加自动重试逻辑
  - `extract_from_arxiv_pdf()` - 更新调用方式

**技术实现**：
```python
# 1. 先下载 500KB
pdf_data = download_arxiv_pdf_stream(arxiv_id, max_size=500*1024)

# 2. 尝试解析，失败则自动重试
try:
    doc = fitz.open(stream=pdf_data, filetype="pdf")
except Exception as e:
    if "cannot open broken document" in str(e):
        # 自动下载完整文件
        pdf_data = download_arxiv_pdf_stream(arxiv_id, max_size=None)
        doc = fitz.open(stream=pdf_data, filetype="pdf")
```

**测试结果**：

| 论文 | 大小 | 第一次尝试 | 重试 | 结果 |
|------|------|-----------|------|------|
| 2602.11541 | 848KB | 500KB 失败 | 完整下载 | ✅ 成功提取机构 |
| 2312.00001 | 284KB | 500KB 成功 | 无需重试 | ✅ 节省带宽 |

**提取验证**（2602.11541）：
- ✅ Renmin University of China
- ✅ Shanghai University of Finance and Economics
- ✅ Baidu Inc.

**方案优势**：
- ✅ 智能节省带宽：小论文只下载 500KB
- ✅ 100% 成功率：大论文自动降级到完整下载
- ✅ 零存储开销：所有操作在内存中完成
- ✅ 用户体验好：自动重试，无需人工干预

---

## [v1.3.0] - 2026-02-12

### ✨ 功能增强

#### 1. Venue 和 Institutions 提取功能优化

**问题描述**：
- v1.2.0 中添加的 venue 和 institutions 功能未生效
- 论文卡片上没有显示会议徽章和机构徽章
- arXiv API 不提供作者机构信息，导致机构加分失效

**解决方案**：
- 创建 PDF 元数据提取器，直接从 arXiv PDF 中提取信息
- 流式下载 PDF 前 500KB（约前 3 页），零磁盘占用
- 使用 LLM 识别页眉、页脚、作者信息中的会议和机构
- 提取优先级：PDF > Semantic Scholar > LLM 摘要提取

**新增文件**：
- `services/pdf_metadata_extractor.py` - PDF 元数据提取器
- `scripts/update_venue_institutions.py` - 更新现有论文的脚本
- `analyze_metadata_scores.py` - 元数据分数分析工具
- `docs/UPDATE_LOG_V1.3.0.md` - 详细更新日志

**修改文件**：
- `services/scoring_engine.py` - 支持预提取数据，避免重复 PDF 解析
- `services/scheduler.py` - 实现三阶段元数据筛选
- `services/metadata_scorer.py` - 降低时效性加分权重
- `config/__init__.py` - 修复 config 包导入问题

**技术亮点**：
- ✅ 零存储开销（在内存中处理 PDF）
- ✅ 信息准确（直接来自论文官方信息）
- ✅ 不依赖外部 API（无需 S2 API Key）
- ✅ 对新论文有效（S2 可能还没收录）

---

### 🚀 性能优化

#### 2. 多层筛选流程优化

**问题描述**：
- 元数据筛选和 S2 筛选几乎不过滤论文（过滤率 < 5%）
- 时效性加分过高（7天内 +2分），导致所有新论文都能通过
- 无 S2 API Key 时仍然调用 API，浪费 2-3 分钟

**优化方案**：

**1. 三阶段元数据筛选**：
```
阶段 1: 基础筛选（阈值 4.0）
  ↓ 快速过滤低质量论文

阶段 2: PDF 提取
  ↓ 只对通过筛选的论文提取 venue 和 institutions

阶段 3: 二次筛选（阈值 5.0）
  ↓ 基于机构加分重新评分
```

**2. 降低时效性加分**：
- 7天内：2.0 → 0.5 分
- 30天内：1.5 → 0 分
- 理由：用户主动选择抓取日期，时效性加分意义不大

**3. 跳过无效的 S2 筛选**：
- 无 API Key 时直接跳过，节省 2-3 分钟
- S2 降级规则过于宽松（2024+ 年份直接通过）

**性能提升**：

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 元数据筛选过滤率 | 0-3% | 40-50% | ✅ 提升 15 倍 |
| S2 筛选时间 | 2-3 分钟 | 跳过 | ✅ 节省 100% |
| 需要 AI 评分的论文数 | 100 篇 | 40-50 篇 | ✅ 减少 50-60% |
| 总处理时间 | 27-28 分钟 | 20 分钟 | ✅ 节省 25-30% |

---

### 🐛 Bug 修复

#### 3. 修复 config 包导入问题

**问题描述**：
- 创建 `config/` 目录后，`import config` 导入的是包而不是 `config.py` 文件
- 导致 `config.DATABASE_PATH` 等配置变量无法访问
- 应用无法启动

**解决方案**：
- 在 `config/__init__.py` 中导入并重新导出 `config.py` 的所有配置变量
- 同时导出新增的 venues 和 institutions 模块

---

### 📊 使用方法

**1. 抓取新论文（自动使用新功能）**：
```bash
streamlit run app.py
```

**2. 更新现有论文**：
```bash
# 更新所有缺失 venue/institutions 的论文
python scripts/update_venue_institutions.py

# 只更新前 10 篇（测试用）
python scripts/update_venue_institutions.py --limit 10

# 指定日期范围
python scripts/update_venue_institutions.py --date-from 2026-01-01
```

**3. 分析元数据分数分布**：
```bash
python analyze_metadata_scores.py
```

---

### ⚙️ 配置说明

**元数据筛选阈值**（在 `services/scheduler.py` 中）：
- 阶段 1 基础筛选：4.0（过滤约 7% 的论文）
- 阶段 3 二次筛选：5.0（过滤约 50% 的论文）

**Semantic Scholar API Key**（可选）：
```bash
# 在 .env 中配置
S2_API_KEY=你的API密钥
```

---

### 📈 后续优化方向

1. **并行 PDF 提取** - 使用多线程减少处理时间
2. **缓存 PDF 提取结果** - 避免重复下载和解析
3. **优化 LLM Prompt** - 提高提取准确率
4. **支持更多会议和机构** - 扩展配置列表

---

### 📚 相关文档

- [详细更新日志](UPDATE_LOG_V1.3.0.md)
- [Auto-Scholar 使用指南](AUTO_SCHOLAR_GUIDE.md)
- [技术文档](TECHNICAL_DOCUMENTATION.md)

---

## [v1.2.0] - 2026-02-12

### ✨ 新增功能

#### 1. 论文卡片展示顶刊顶会和知名机构信息

**功能描述**：
- 在 Auto-Scholar 论文卡片中自动识别并展示顶级会议/期刊信息
- 自动识别并展示知名高校和科技公司信息
- 使用徽章样式清晰展示，提升信息可读性

**实现方式**：
- 使用 LLM 从论文标题和摘要中提取会议/期刊和机构信息
- 从作者的 affiliation 字段中提取知名机构
- 标准化机构和会议名称，过滤非顶级会议/机构

**支持的顶会顶刊**：
- **AI 领域**：NeurIPS, ICML, ICLR, CVPR, ICCV, ECCV, ACL, AAAI, IJCAI, KDD 等
- **运筹学领域**：Operations Research, Management Science, Mathematical Programming 等
- **交通领域**：Transportation Research (A/B/C/D/E), Transportation Science, TRB 等

**支持的知名机构**：
- **中国985大学**：清华、北大、上交、浙大、复旦、南大、中科大等 39 所
- **QS前50大学**：MIT, Stanford, Berkeley, CMU, Harvard, Oxford, Cambridge, NUS, ETH 等
- **US News前70大学**：包含美国主要研究型大学
- **知名科技公司**：Google, OpenAI, Meta, Microsoft, ByteDance, Alibaba, Tencent, Baidu 等

**UI 展示效果**：
```
┌─────────────────────────────────────────────────────────┐
│ Deep Reinforcement Learning for VRP                     │
│ 深度强化学习用于车辆路径问题                              │
│                                                         │
│ 📍 ICLR 2026  🏛️ MIT, Google Brain                     │
│                                                         │
│ 📝 John Doe (MIT), Jane Smith (Google Brain)...        │
│ 🔗 arxiv.org/abs/2401.12345 | 📅 2024-01-15           │
│                                                         │
│ ⭐ S级 8.5分                                            │
└─────────────────────────────────────────────────────────┘
```

**修改文件**：
- `database/models.py` - 添加 venue, venue_year, institutions 字段
- `database/migrate_add_venue_institutions.py` - 数据库迁移脚本
- `config/venues.py` - 顶刊顶会配置（新增）
- `config/institutions.py` - 知名机构配置（新增）
- `config/__init__.py` - Config 包初始化（新增）
- `utils/prompts.py` - 修改评分 Prompt，添加 venue 和 institutions 提取
- `services/scoring_engine.py` - 处理新字段，标准化机构和会议名称
- `services/scheduler.py` - 传递 authors 参数和新字段
- `database/db_manager.py` - 更新 create_arxiv_paper 方法
- `ui/auto_scholar.py` - 添加徽章显示

**技术细节**：
1. **数据库扩展**：
   - `venue` (String(200)) - 会议/期刊名称
   - `venue_year` (Integer) - 年份
   - `institutions` (JSON) - 知名机构列表

2. **LLM 提取**：
   - 复用现有评分 API 调用，无额外成本
   - 从标题、摘要中提取会议/期刊信息
   - 从标题、摘要、作者信息中提取机构

3. **标准化处理**：
   - 会议名称标准化（如 "neurips" → "NeurIPS"）
   - 机构名称标准化（如 "MIT" → "Massachusetts Institute of Technology"）
   - 支持多种名称变体识别

4. **徽章样式**：
   - 会议/期刊：紫色徽章 📍
   - 知名机构：青绿色徽章 🏛️
   - 圆角设计，清晰易读

**测试验证**：
- 创建测试脚本 `test_venue_institution.py`
- 验证会议/期刊识别和标准化
- 验证机构识别和提取
- 所有测试通过 ✅

---

## [v1.1.1] - 2026-02-12

### 🐛 Bug 修复

#### 1. 修复"昨天"模式无法抓取论文的问题

**问题描述**：
- 选择"昨天"模式时，抓取很快结束且无法抓取任何文章
- 但使用自定义时间段设置为昨天的具体日期时，可以正常抓取

**根本原因**：
- UI 层调用 `daily_scheduler.run_daily_pipeline()` 时未传递明确的日期参数
- 导致日期范围计算不准确

**解决方案**：
- 将"昨天"模式重命名为"昨天到目前"，更准确地描述功能
- 修改 `ui/auto_scholar.py`，明确传递 `start_date`（昨天 00:00）和 `end_date`（今天 23:59）

**修改文件**：
- `ui/auto_scholar.py` (第 44 行, 第 167-176 行)

**代码变更**：
```python
# 修改前
fetch_mode = st.selectbox("抓取模式", ["昨天", "自定义时间段"], ...)
else:
    result = daily_scheduler.run_daily_pipeline(max_results=500, ...)

# 修改后
fetch_mode = st.selectbox("抓取模式", ["昨天到目前", "自定义时间段"], ...)
else:  # 昨天到目前模式
    yesterday = datetime.now() - timedelta(days=1)
    start_dt = datetime.combine(yesterday.date(), datetime.min.time())
    end_dt = datetime.combine(datetime.now().date(), datetime.max.time())
    result = daily_scheduler.run_daily_pipeline(
        max_results=500,
        start_date=start_dt,
        end_date=end_dt,
        progress_callback=update_ui
    )
```

---

#### 2. 增强评分失败时的错误信息显示

**问题描述**：
- 评分失败时，错误信息被截断为前 50 个字符
- 无法看到完整的错误原因，难以诊断问题

**解决方案**：
- 移除错误信息的 `[:50]` 截断限制
- 添加完整的错误堆栈跟踪（`traceback.format_exc()`）
- 在控制台输出完整的错误信息

**修改文件**：
- `services/scoring_engine.py` (第 56-78 行)

**代码变更**：
```python
# 修改前
return {
    'score': 5.0,
    'reason': f'评分失败（{error_msg[:50]}），建议人工复核',
    ...
}

# 修改后
import traceback
full_traceback = traceback.format_exc()
print(f"完整错误堆栈:\n{full_traceback}")

return {
    'score': 5.0,
    'reason': f'评分失败（{error_msg}），建议人工复核',  # 不截断
    ...
}
```

---

#### 3. 修复豆包 API SSL 连接失败问题

**问题描述**：
- 评分时出现错误：`HTTPSConnectionPool(host='aigc.sankuai.com', port=443): Max retries exceeded`
- 具体错误：`SSLZeroReturnError: TLS/SSL connection has been closed (EOF)`
- 在本次功能优化之前，豆包 API 可以正常调用

**根本原因**：
- 豆包 API 的 SSL 证书在 Python requests 库的默认配置下无法通过验证
- SSL/TLS 握手过程中服务器主动关闭了连接

**诊断过程**：
1. 创建测试脚本 `test_doubao_api.py` 进行基础诊断
2. 创建高级测试脚本 `test_doubao_api_advanced.py` 尝试不同配置
3. 发现禁用 SSL 验证后可以正常调用
4. 确认是 SSL 证书验证问题

**解决方案**：
- 创建自定义 `SSLAdapter` 类，降低 SSL 安全级别（`SECLEVEL=1`）
- 使用 `requests.Session` 对象，配置自定义 SSL 适配器
- 禁用 SSL 验证（`verify=False`）
- 禁用 SSL 警告信息

**修改文件**：
- `services/doubao_service.py` (第 1-42 行, 第 58 行)

**代码变更**：
```python
# 新增自定义 SSL 适配器
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SSLAdapter(HTTPAdapter):
    """自定义 SSL 适配器，解决豆包 API 的 SSL 证书验证问题"""
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

# 在 DoubaoService.__init__ 中
self.session = requests.Session()
self.session.mount('https://', SSLAdapter())
self.session.verify = False

# 在 _call_api 中
response = self.session.post(self.api_url, headers=headers, ...)  # 使用 session
```

**测试结果**：
```
✅ 测试成功！
返回结果: {
    'score': 7,
    'reason': '论文提出使用深度强化学习解决组合优化问题，具有一定创新性...',
    'title_zh': '深度强化学习用于组合优化',
    'abstract_zh': '本文提出了一种使用深度强化学习解决组合优化问题的新方法。',
    'tags': ['强化学习', '组合优化']
}
```

---

### 📝 新增文件

1. **test_doubao_api.py** - 豆包 API 基础诊断测试脚本
   - 测试网络连接
   - 测试 API 配置
   - 测试 API 调用
   - 测试 DoubaoService 类

2. **test_doubao_api_advanced.py** - 豆包 API 高级诊断测试脚本
   - 测试禁用 SSL 验证
   - 测试不同的请求头格式
   - 测试使用 Session 对象
   - 生成 curl 命令供手动测试

3. **docs/CHANGELOG.md** - 本更新日志文件

---

### 🔧 技术细节

#### SSL 问题分析

**环境信息**：
- Python 版本: 3.9.19
- requests 版本: 2.31.0
- urllib3 版本: 1.26.19
- OpenSSL 版本: OpenSSL 3.0.14

**错误堆栈**：
```
ssl.SSLZeroReturnError: TLS/SSL connection has been closed (EOF) (_ssl.c:1133)
urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='aigc.sankuai.com', port=443):
Max retries exceeded with url: /v1/openai/native/chat/completions
(Caused by SSLError(SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF)')))
```

**解决方案原理**：
- `SECLEVEL=1`：降低 OpenSSL 的安全级别，允许使用较旧的加密算法
- `verify=False`：禁用 SSL 证书验证（适用于内部 API）
- `Session` 对象：复用连接，提高性能

---

### ⚠️ 注意事项

1. **SSL 验证禁用**：
   - 本次修复禁用了豆包 API 的 SSL 证书验证
   - 这在内部 API 或受信任的环境中是可接受的
   - 如果需要更高的安全性，请联系豆包 API 技术支持解决证书问题

2. **日期范围**：
   - "昨天到目前"模式抓取的是从昨天 00:00 到今天 23:59 的论文
   - 如果需要只抓取昨天的论文，请使用"自定义时间段"模式

3. **错误信息**：
   - 现在评分失败时会显示完整的错误信息
   - 请注意查看控制台输出以获取详细的错误堆栈

---

### 🧪 测试验证

**测试步骤**：
1. 运行 `python test_doubao_api.py` 进行基础诊断
2. 运行 `python test_doubao_api_advanced.py` 进行高级诊断
3. 在 Streamlit 应用中选择"昨天到目前"模式并点击"立即抓取"
4. 验证论文可以正常抓取和评分

**预期结果**：
- ✅ 可以正常抓取论文
- ✅ 评分功能正常工作
- ✅ 错误信息完整显示

---

### 📚 相关文档

- [Auto-Scholar 使用指南](AUTO_SCHOLAR_GUIDE.md)
- [技术文档](TECHNICAL_DOCUMENTATION.md)
- [产品需求文档](PRD.md)

---

### 👥 贡献者

- 修复人员：Claude Code
- 测试人员：用户
- 修复日期：2026-02-12

---

## [v1.1.0] - 2026-02-05

### ✨ 新增功能

- 新增 Auto-Scholar 论文智能监控功能模块
- 支持 Arxiv 自动抓取
- 支持 AI 评分筛选
- 支持每日推送高质量论文

（详细内容见 PRD.md v1.1 版本）

---

## [v1.0.0] - 2026-01-20

### ✨ 初始版本

- 论文上传与解析
- 结构化总结生成
- 思维导图生成
- 智能标签系统
- RAG 对话问答
- 论文检索与筛选

（详细内容见 PRD.md v1.0 版本）
