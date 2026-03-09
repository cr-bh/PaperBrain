<div align="center">

# 🧠 PaperFlow

**智能论文笔记与知识库助手 | AI-Powered Academic Paper Management System**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.4.0-brightgreen.svg)](docs/CHANGELOG.md)

[English](#english) | [中文](#中文)

</div>

---

## 中文

### ✨ 核心功能

<table>
<tr>
<td width="50%">

#### 📄 智能论文管理
- PDF 上传与自动解析
- 元数据提取（标题、作者、日期）
- 关键图片提取与分类（架构图/性能图/算法图）
- 图片上传与标注管理
- 内容编辑与笔记管理

</td>
<td width="50%">

#### 🧠 AI 深度分析
- **8 维度结构化总结**：问题定义、相关工作、方法论、实验结果等
- **自动思维导图**：Mermaid.js 可视化，高对比度配色
- **三维度智能标签**：领域 / 方法 / 任务
- **层级标签体系**：支持父子标签关系

</td>
</tr>
<tr>
<td width="50%">

#### 💬 RAG 对话问答
- 基于 ChromaDB 的向量检索
- `@mention` 语法指定论文
- 多论文对比分析
- 来源追溯与引用

</td>
<td width="50%">

#### 🤖 Auto-Scholar 论文监控
- **智能抓取**：Arxiv 自动抓取 + 关键词配置
- **多层筛选**：关键词 → 元数据评分 → PDF 提取 → AI 深度评分
- **顶会识别**：自动识别 ICLR, NeurIPS, CVPR 等 40+ 顶会顶刊
- **机构识别**：自动识别 MIT, Stanford, 清华, 浙大等 100+ 知名机构
- **PDF 元数据提取**：直接从 PDF 提取会议和机构信息（零存储）
- **分级推荐**：S/A/B 级评分 + 中文翻译
- **徽章展示**：📍 会议徽章 + 🏛️ 机构徽章
- **数据分析**：论文质量统计、发表趋势、关键词热力图

</td>
</tr>
</table>

### 🎬 功能演示

#### 论文管理与分析

| 📚 论文库主页 | 📝 结构化笔记 |
|---|---|
| ![论文库主页](docs/images/main.png) | ![结构化笔记](docs/images/note.png) |
| 论文列表、搜索筛选、标签管理 | 8 维度深度总结、问题定义、方法论 |

| 🧠 思维导图 | 💬 智能问答 |
|---|---|
| ![思维导图](docs/images/mind.png) | ![智能问答](docs/images/chat.png) |
| 自动生成可视化思维导图 | RAG 检索、@mention 语法、多论文对比 |

### 🚀 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/paperflow.git
cd paperflow

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，配置 LLM_API_URL 和 LLM_BEARER_TOKEN

# 4. 初始化并启动
python database/init_db.py
streamlit run app.py
```

访问 http://localhost:8501 开始使用 🎉

### 📖 使用指南

#### 论文上传

![上传论文界面](docs/images/upload.png)

1. 点击侧边栏「📤 上传论文」
2. 拖拽或选择 PDF 文件
3. 点击「开始处理」，等待 AI 分析完成
4. 查看结构化笔记、思维导图和自动标签
5. 支持上传自定义图片并添加标注

#### 对话问答
- **全局问答**：直接输入问题，检索所有论文
- **指定论文**：使用 `@论文标题` 语法，如 `@AlphaGo 这篇论文的核心算法是什么？`
- **多论文对比**：`@paper1 @paper2 这两篇论文有什么区别？`

#### Auto-Scholar 配置
1. 点击侧边栏「🤖 Auto-Scholar」
2. 在「⚙️ 关键词设置」中配置研究兴趣关键词（核心/前沿）
3. 在「📊 论文列表」中选择抓取模式（昨天到目前/自定义时间段）
4. 点击「🚀 立即抓取」获取最新论文
5. 查看 S/A/B 分级推荐，支持收藏和导入
6. 在「📈 统计分析」中查看论文质量分析（分数/顶会/机构/交叉分析）
7. 在「📊 发表趋势」中查看实时趋势分析（时间趋势/关键词分析/热力图）

详细使用说明请参考 [Auto-Scholar 使用指南](docs/guides/AUTO_SCHOLAR_GUIDE.md)

#### 🤖 Auto-Scholar 功能展示

| 📊 论文抓取与评分 | ⚙️ 关键词配置 |
|---|---|
| ![论文抓取与评分](docs/images/catch.png) | ![关键词配置](docs/images/keywords.png) |
| S/A/B 分级推荐、会议徽章、机构徽章 | 核心关键词、前沿关键词配置 |

| 📥 自动导入论文库 | 📈 时间趋势分析 |
|---|---|
| ![自动导入论文库](docs/images/auto-import.png) | ![时间趋势分析](docs/images/catch-ana-time.png) |
| 收藏论文一键导入、自动分析 | 按日期统计论文发表数量 |

| 📊 关键词分析 | 🏛️ 机构与顶会分析 |
|---|---|
| ![关键词分析](docs/images/catch-ana-keyword.png) | ![机构与顶会分析](docs/images/catch-ana-org.png) |
| 关键词分布与热度分析 | 顶会顶刊与知名机构统计 |

#### 标签管理

![标签管理界面](docs/images/label.png)

- **层级标签**：支持父子标签关系，构建知识体系
- **重复检测**：自动检测相似标签，一键合并
- **颜色自定义**：为标签设置颜色，便于视觉区分
- **MECE 初始化**：一键创建标准标签体系

### 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    用户界面 (Streamlit)                          │
│   Dashboard │ Upload │ Detail │ Chat │ Tags │ Auto-Scholar     │
├─────────────────────────────────────────────────────────────────┤
│                      服务层                                      │
│  PDF解析 │ LLM总结 │ 思维导图 │ 标签 │ RAG │ 评分引擎           │
│  元数据提取 │ Arxiv爬虫 │ 质量分析 │ 趋势分析                   │
├─────────────────────────────────────────────────────────────────┤
│                      数据层                                      │
│         SQLite (关系数据)  │  ChromaDB (向量检索)                │
└─────────────────────────────────────────────────────────────────┘
```

### 🛠️ 技术栈

| 类别 | 技术 | 说明 |
|-----|-----|-----|
| 前端框架 | Streamlit | 快速构建数据应用 |
| LLM | Gemini / 豆包 | 论文分析、评分与翻译 |
| 关系数据库 | SQLite + SQLAlchemy | 论文元数据存储 |
| 向量数据库 | ChromaDB | RAG 语义检索 |
| PDF 解析 | PyMuPDF | 文本与图片提取 |
| 可视化 | Mermaid.js + Plotly | 思维导图与数据图表 |
| 学术 API | Arxiv API | 论文抓取与元数据 |

### 📋 功能路线图

#### ✅ 已完成功能

**论文管理与分析**
- [x] PDF 智能解析（文本、图片、元数据提取）
- [x] 8 维度结构化总结（问题、方法、结果、未来工作等）
- [x] 自动思维导图生成（Mermaid.js 可视化）
- [x] 三维度智能标签系统（领域/方法/任务）
- [x] 层级标签管理（父子关系、合并、去重）
- [x] 内容编辑（笔记编辑、图片上传与标注）

**智能问答与检索**
- [x] RAG 向量检索问答（基于 ChromaDB）
- [x] @mention 语法（指定论文提问）
- [x] 多论文对比分析
- [x] 来源追溯与引用

**Auto-Scholar 论文监控**
- [x] Arxiv 自动抓取与关键词筛选
- [x] 四层智能筛选（关键词 → 元数据评分 → PDF 提取 → AI 深度评分）
- [x] 顶会顶刊自动识别（40+ 顶会，包括 ICLR、NeurIPS、CVPR 等）
- [x] 知名机构自动识别（100+ 机构，包括 MIT、Stanford、清华、浙大等）
- [x] PDF 元数据提取（零存储，直接从 PDF 提取会议和机构信息）
- [x] S/A/B 分级推荐 + 中文翻译
- [x] 论文收藏与导入功能
- [x] 数据分析与可视化（质量统计、发表趋势、关键词热力图）
- [x] 导出功能（从抓取列表导出到笔记库）

#### 🚀 规划中功能

- [ ] 批量论文上传
- [ ] 论文引用关系图谱
- [ ] 跨论文知识图谱构建
- [ ] 自定义 Prompt 模板
- [ ] 团队协作与共享

### 📁 项目结构

```
paperflow/
├── app.py                          # 应用入口
├── config.py                       # 配置管理
├── config/                         # 配置模块
│   ├── venues.py                   # 顶会顶刊配置
│   └── institutions.py             # 知名机构配置
├── database/                       # 数据库层
│   ├── models.py                   # 数据模型
│   ├── db_manager.py               # CRUD 操作
│   └── init_db.py                  # 数据库初始化
├── services/                       # 服务层
│   ├── llm_service.py              # LLM API
│   ├── pdf_parser.py               # PDF 解析
│   ├── pdf_metadata_extractor.py   # PDF 元数据提取
│   ├── summarizer.py               # 总结生成
│   ├── mindmap_generator.py        # 思维导图生成
│   ├── tagger.py                   # 智能标签
│   ├── rag_service.py              # RAG 服务
│   ├── arxiv_crawler.py            # Arxiv 爬虫
│   ├── scoring_engine.py           # 评分引擎
│   ├── metadata_scorer.py          # 元数据评分
│   ├── quality_analyzer.py         # 质量分析
│   └── trend_analyzer.py           # 趋势分析
├── ui/                             # UI 组件
│   ├── dashboard.py                # 论文列表
│   ├── upload_page.py              # 上传页面
│   ├── paper_detail.py             # 论文详情
│   ├── chat_interface.py           # 对话界面
│   ├── tag_management.py           # 标签管理
│   └── auto_scholar.py             # Auto-Scholar
├── utils/                          # 工具函数
│   ├── prompts.py                  # Prompt 模板
│   └── helpers.py                  # 辅助函数
└── docs/                           # 文档
    ├── README.md                   # 文档索引
    ├── principle.md                # 文档管理规范
    ├── CHANGELOG.md                # 主更新日志
    ├── guides/                     # 用户指南
    ├── technical/                  # 技术文档
    ├── changelogs/                 # 版本更新日志
    ├── features/                   # 功能说明
    └── development/                # 开发文档
```

详细架构请参考 [技术文档](docs/technical/TECHNICAL_DOCUMENTATION.md)

### ❓ 常见问题

<details>
<summary>如何获取 LLM API？</summary>

配置 `.env` 文件中的 `LLM_API_URL` 和 `LLM_BEARER_TOKEN`。支持 Gemini API 或兼容接口。
</details>

<details>
<summary>思维导图无法显示？</summary>

确保已安装 `streamlit-mermaid`：
```bash
pip install streamlit-mermaid
```
</details>

<details>
<summary>Auto-Scholar 如何配置定时任务？</summary>

参考 [Auto-Scholar 使用指南](docs/guides/AUTO_SCHOLAR_GUIDE.md) 中的定时任务配置部分。
</details>

<details>
<summary>PDF 元数据提取失败？</summary>

系统会自动重试。如果论文较大（>500KB），会自动下载完整文件进行解析。
</details>

### 📚 文档

- [文档中心](docs/README.md) - 完整文档索引
- [更新日志](docs/CHANGELOG.md) - 版本历史与功能更新
- [技术文档](docs/technical/TECHNICAL_DOCUMENTATION.md) - 详细架构与 API
- [Auto-Scholar 使用指南](docs/guides/AUTO_SCHOLAR_GUIDE.md) - 论文监控功能说明
- [顶会机构功能说明](docs/features/VENUE_INSTITUTION.md) - 会议与机构识别
- [文档管理规范](docs/principle.md) - 文档组织和更新规范

---

## English

### ✨ Key Features

<table>
<tr>
<td width="50%">

#### 📄 Smart Paper Management
- PDF upload & auto-parsing
- Metadata extraction (title, authors, date)
- Key image extraction & classification
- Image upload & annotation
- Content editing & note management

</td>
<td width="50%">

#### 🧠 AI Deep Analysis
- **8-dimension structured summary**: problem, related work, methodology, results, etc.
- **Auto mind map**: Mermaid.js visualization with high contrast colors
- **3-dimension smart tags**: Domain / Method / Task
- **Hierarchical tag system**: Parent-child relationships

</td>
</tr>
<tr>
<td width="50%">

#### 💬 RAG Q&A
- ChromaDB-based vector search
- `@mention` syntax for specific papers
- Multi-paper comparison
- Source attribution & citation

</td>
<td width="50%">

#### 🤖 Auto-Scholar Monitoring
- **Smart crawling**: Arxiv auto-fetch + keyword configuration
- **Multi-layer filtering**: Keywords → Metadata scoring → PDF extraction → AI deep scoring
- **Conference recognition**: Auto-identify 40+ top conferences (ICLR, NeurIPS, CVPR, etc.)
- **Institution recognition**: Auto-identify 100+ prestigious institutions (MIT, Stanford, Tsinghua, etc.)
- **PDF metadata extraction**: Extract conference & institution info directly from PDF (zero storage)
- **Tier recommendations**: S/A/B scoring + Chinese translation
- **Badge display**: 📍 Conference badges + 🏛️ Institution badges
- **Data analytics**: Quality statistics, publication trends, keyword heatmaps

</td>
</tr>
</table>

### 🎬 Feature Showcase

#### Paper Management & Analysis

| 📚 Paper Library | 📝 Structured Notes |
|---|---|
| ![Paper Library](docs/images/main.png) | ![Structured Notes](docs/images/note.png) |
| Paper list, search & filter, tag management | 8-dimension deep summary, problem definition, methodology |

| 🧠 Mind Map | 💬 Smart Q&A |
|---|---|
| ![Mind Map](docs/images/mind.png) | ![Smart Q&A](docs/images/chat.png) |
| Auto-generated visual mind map | RAG retrieval, @mention syntax, multi-paper comparison |

### 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/your-repo/paperflow.git && cd paperflow

# 2. Install
pip install -r requirements.txt

# 3. Configure
cp .env.example .env  # Edit .env with your API credentials

# 4. Initialize & Run
python database/init_db.py && streamlit run app.py
```

Visit http://localhost:8501 🎉

### 📖 Usage

#### Upload Papers

![Upload Papers](docs/images/upload.png)

1. Click "📤 Upload Paper" in sidebar
2. Drag & drop or select PDF file
3. Click "Start Processing" and wait for AI analysis
4. View structured notes, mind map, and auto-generated tags
5. Upload custom images with annotations

#### Q&A Chat
- **Global search**: Ask questions across all papers
- **Specific paper**: Use `@paper_title` syntax, e.g., `@AlphaGo What is the core algorithm?`
- **Compare papers**: `@paper1 @paper2 What are the differences?`

#### Auto-Scholar
1. Click "🤖 Auto-Scholar" in sidebar
2. Configure keywords in "⚙️ Keyword Settings" (Core/Frontier)
3. Select fetch mode in "📊 Paper List" (Yesterday to Now / Custom Date Range)
4. Click "🚀 Fetch Now" to get latest papers
5. View S/A/B tier recommendations, support favorites and import
6. Check "📈 Statistics" for quality analysis (Score/Conference/Institution/Cross Analysis)
7. Check "📊 Trends" for real-time trend analysis (Time Trends/Keyword Analysis/Heatmap)

See [Auto-Scholar Guide](docs/guides/AUTO_SCHOLAR_GUIDE.md) for details.

#### 🤖 Auto-Scholar Feature Showcase

| 📊 Paper Crawling & Scoring | ⚙️ Keyword Configuration |
|---|---|
| ![Paper Crawling & Scoring](docs/images/catch.png) | ![Keyword Configuration](docs/images/keywords.png) |
| S/A/B tier recommendations, conference badges, institution badges | Core keywords and frontier keywords setup |

| 📥 Auto Import to Library | 📈 Time Trend Analysis |
|---|---|
| ![Auto Import to Library](docs/images/auto-import.png) | ![Time Trend Analysis](docs/images/catch-ana-time.png) |
| One-click import of favorited papers with auto-analysis | Daily publication statistics |

| 📊 Keyword Analysis | 🏛️ Institution & Conference Analysis |
|---|---|
| ![Keyword Analysis](docs/images/catch-ana-keyword.png) | ![Institution & Conference Analysis](docs/images/catch-ana-org.png) |
| Keyword distribution and popularity analysis | Top conferences and prestigious institutions statistics |

### 🛠️ Tech Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| Frontend | Streamlit | Rapid data app development |
| LLM | Gemini / Doubao | Paper analysis, scoring & translation |
| Database | SQLite + SQLAlchemy | Relational data storage |
| Vector DB | ChromaDB | RAG semantic search |
| PDF Parser | PyMuPDF | Text & image extraction |
| Visualization | Mermaid.js + Plotly | Mind maps & data charts |
| Academic API | Arxiv API | Paper crawling & metadata |

### 📋 Feature Roadmap

#### ✅ Completed Features

**Paper Management & Analysis**
- [x] Smart PDF parsing (text, images, metadata extraction)
- [x] 8-dimension structured summary (problem, methodology, results, future work, etc.)
- [x] Auto mind map generation (Mermaid.js visualization)
- [x] 3-dimension smart tag system (Domain/Method/Task)
- [x] Hierarchical tag management (parent-child, merge, deduplication)
- [x] Content editing (note editing, image upload & annotation)

**Smart Q&A & Retrieval**
- [x] RAG vector search Q&A (ChromaDB-based)
- [x] @mention syntax (query specific papers)
- [x] Multi-paper comparison
- [x] Source attribution & citation

**Auto-Scholar Paper Monitoring**
- [x] Arxiv auto-crawling & keyword filtering
- [x] 4-layer smart filtering (Keywords → Metadata scoring → PDF extraction → AI deep scoring)
- [x] Top conference recognition (40+ conferences: ICLR, NeurIPS, CVPR, etc.)
- [x] Prestigious institution recognition (100+ institutions: MIT, Stanford, Tsinghua, Zhejiang, etc.)
- [x] PDF metadata extraction (zero storage, extract conference & institution info directly from PDF)
- [x] S/A/B tier recommendations + Chinese translation
- [x] Paper favorites & import functionality
- [x] Data analytics & visualization (quality statistics, publication trends, keyword heatmaps)
- [x] Export functionality (export from crawl list to note library)

#### 🚀 Planned Features

- [ ] Batch paper upload
- [ ] Citation relationship graph
- [ ] Cross-paper knowledge graph
- [ ] Custom prompt templates
- [ ] Team collaboration & sharing

### 📖 Documentation

- [Documentation Center](docs/README.md) - Complete documentation index
- [CHANGELOG](docs/CHANGELOG.md) - Version history & feature updates
- [Technical Documentation](docs/technical/TECHNICAL_DOCUMENTATION.md) - Detailed architecture & API
- [Auto-Scholar Guide](docs/guides/AUTO_SCHOLAR_GUIDE.md) - Paper monitoring features
- [Conference & Institution Feature](docs/features/VENUE_INSTITUTION.md) - Recognition system
- [Documentation Guidelines](docs/principle.md) - Documentation organization & update rules

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

Made with ❤️ for researchers

</div>
