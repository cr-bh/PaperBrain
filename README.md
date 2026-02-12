<div align="center">

# 🧠 PaperBrain

**智能论文笔记与知识库助手 | AI-Powered Academic Paper Management System**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

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

</td>
<td width="50%">

#### 🧠 AI 深度分析
- **8 维度结构化总结**：问题定义、相关工作、方法论、实验结果等
- **自动思维导图**：Mermaid.js 可视化
- **三维度智能标签**：领域 / 方法 / 任务

</td>
</tr>
<tr>
<td width="50%">

#### 💬 RAG 对话问答
- 基于向量检索的智能问答
- `@mention` 语法指定论文
- 多论文对比分析
- 来源追溯

</td>
<td width="50%">

#### 🤖 Auto-Scholar 论文监控
- Arxiv 每日自动抓取
- **三层智能筛选**：关键词 + 元数据评分 + AI 深度评分
- **自动识别顶刊顶会**：ICLR, NeurIPS, CVPR 等 40+ 顶会
- **自动识别知名机构**：MIT, Stanford, 清华, 浙大等 100+ 机构
- S/A/B 分级推荐 + 中文翻译
- 📍 会议徽章 + 🏛️ 机构徽章展示

</td>
</tr>
</table>

### 🎬 功能演示

<!-- 截图占位符 - 请添加实际截图到 docs/images/ 目录 -->
| 论文列表 | 结构化笔记 | 思维导图 | Auto-Scholar |
|:-------:|:---------:|:-------:|:------------:|
| ![Dashboard](docs/images/dashboard.png) | ![Notes](docs/images/paper-detail.png) | ![Mindmap](docs/images/mindmap.png) | ![Scholar](docs/images/auto-scholar.png) |

### 🚀 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/paperbrain.git
cd paperbrain

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
1. 点击侧边栏「📤 上传论文」
2. 拖拽或选择 PDF 文件
3. 点击「开始处理」，等待 AI 分析完成（约 2-3 分钟）
4. 查看结构化笔记、思维导图和自动标签

#### 对话问答
- **全局问答**：直接输入问题，检索所有论文
- **指定论文**：使用 `@论文标题` 语法，如 `@AlphaGo 这篇论文的核心算法是什么？`
- **多论文对比**：`@paper1 @paper2 这两篇论文有什么区别？`

#### Auto-Scholar 配置
1. 点击侧边栏「🤖 Auto-Scholar」
2. 在「关键词设置」中配置研究兴趣关键词
3. 点击「立即抓取」获取最新论文
4. 查看 S/A/B 分级推荐，导出 HTML 日报

详细使用说明请参考 [Auto-Scholar 使用指南](docs/AUTO_SCHOLAR_GUIDE.md)

#### 标签管理
- **层级标签**：支持父子标签关系，构建知识体系
- **重复检测**：自动检测相似标签，一键合并
- **颜色自定义**：为标签设置颜色，便于视觉区分
- **MECE 初始化**：一键创建标准标签体系

### 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户界面 (Streamlit)                   │
│   Dashboard │ Upload │ Detail │ Chat │ Tags │ Scholar   │
├─────────────────────────────────────────────────────────┤
│                      服务层                               │
│  PDF解析 │ LLM总结 │ 思维导图 │ 标签 │ RAG │ 评分引擎    │
├─────────────────────────────────────────────────────────┤
│                      数据层                               │
│         SQLite (关系数据)  │  ChromaDB (向量检索)         │
└─────────────────────────────────────────────────────────┘
```

### 🛠️ 技术栈

| 类别 | 技术 | 说明 |
|-----|-----|-----|
| 前端框架 | Streamlit | 快速构建数据应用 |
| LLM | Gemini / 豆包 | 论文分析与评分 |
| 关系数据库 | SQLite + SQLAlchemy | 论文元数据存储 |
| 向量数据库 | ChromaDB | RAG 语义检索 |
| PDF 解析 | PyMuPDF | 文本与图片提取 |
| 可视化 | Mermaid.js | 思维导图渲染 |

### 📋 路线图

- [x] 核心功能：PDF 解析、结构化总结、思维导图、智能标签
- [x] RAG 对话问答（@mention 语法）
- [x] Auto-Scholar 论文监控
- [x] 标签管理增强（层级、合并、重复检测）
- [x] 内容编辑（笔记编辑、图片管理）
- [ ] 批量上传
- [ ] 导出功能（Markdown/PDF）
- [ ] 引用关系图谱
- [ ] 多语言论文支持

### 📁 项目结构

```
paperbrain/
├── app.py                 # 应用入口
├── config.py              # 配置管理
├── database/              # 数据库层
│   ├── models.py          # 数据模型
│   └── db_manager.py      # CRUD 操作
├── services/              # 服务层
│   ├── llm_service.py     # LLM API
│   ├── pdf_parser.py      # PDF 解析
│   ├── summarizer.py      # 总结生成
│   ├── rag_service.py     # RAG 服务
│   ├── arxiv_crawler.py   # Arxiv 爬虫
│   └── scoring_engine.py  # 评分引擎
├── ui/                    # UI 组件
└── utils/                 # 工具函数
```

详细架构请参考 [技术文档](docs/TECHNICAL_DOCUMENTATION.md)

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

参考 [Auto-Scholar 使用指南](docs/AUTO_SCHOLAR_GUIDE.md) 中的定时任务配置部分。
</details>

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

</td>
<td width="50%">

#### 🧠 AI Deep Analysis
- **8-dimension structured summary**: problem, related work, methodology, results, etc.
- **Auto mind map**: Mermaid.js visualization
- **3-dimension smart tags**: Domain / Method / Task

</td>
</tr>
<tr>
<td width="50%">

#### 💬 RAG Q&A
- Vector-based semantic search
- `@mention` syntax for specific papers
- Multi-paper comparison
- Source attribution

</td>
<td width="50%">

#### 🤖 Auto-Scholar Monitoring
- Daily Arxiv auto-fetch
- 3-layer filtering (keywords + citations + AI scoring)
- S/A/B tier recommendations + Chinese translation
- Auto HTML report generation

</td>
</tr>
</table>

### 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/your-repo/paperbrain.git && cd paperbrain

# 2. Install
pip install -r requirements.txt

# 3. Configure
cp .env.example .env  # Edit .env with your API credentials

# 4. Run
python database/init_db.py && streamlit run app.py
```

Visit http://localhost:8501 🎉

### 📖 Usage

#### Upload Papers
1. Click "📤 Upload Paper" in sidebar
2. Drag & drop or select PDF file
3. Click "Start Processing" and wait for AI analysis (~2-3 min)
4. View structured notes, mind map, and auto-generated tags

#### Q&A Chat
- **Global search**: Ask questions across all papers
- **Specific paper**: Use `@paper_title` syntax, e.g., `@AlphaGo What is the core algorithm?`
- **Compare papers**: `@paper1 @paper2 What are the differences?`

#### Auto-Scholar
1. Click "🤖 Auto-Scholar" in sidebar
2. Configure keywords in "Keyword Settings"
3. Click "Fetch Now" to get latest papers
4. View S/A/B tier recommendations, export HTML report

### 🛠️ Tech Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| Frontend | Streamlit | Rapid data app development |
| LLM | Gemini / Doubao | Paper analysis & scoring |
| Database | SQLite + SQLAlchemy | Relational data storage |
| Vector DB | ChromaDB | RAG semantic search |
| PDF Parser | PyMuPDF | Text & image extraction |
| Visualization | Mermaid.js | Mind map rendering |

### 📋 Roadmap

- [x] Core features: PDF parsing, structured summary, mind map, smart tags
- [x] RAG Q&A with @mention syntax
- [x] Auto-Scholar paper monitoring
- [x] Enhanced tag management (hierarchy, merge, duplicate detection)
- [x] Content editing (notes, images)
- [ ] Batch upload
- [ ] Export (Markdown/PDF)
- [ ] Citation graph
- [ ] Multi-language support

### 📖 Documentation

See [Technical Documentation](docs/TECHNICAL_DOCUMENTATION.md) for detailed architecture and API reference.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

Made with ❤️ for researchers

</div>
