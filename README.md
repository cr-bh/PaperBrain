# PaperBrain - 智能论文笔记与知识库助手

PaperBrain 是一个基于 AI 的智能论文管理系统，帮助科研人员高效管理和理解学术论文。

## 核心功能

- 📄 **PDF 解析**: 自动提取论文内容和元数据
- 🧠 **结构化总结**: 使用 LLM 生成论文的结构化总结
- 🗺️ **思维导图**: 自动生成论文的可视化思维导图
- 🏷️ **智能标签**: 自动生成多维度标签（领域、方法、任务）
- 🖼️ **图片提取**: 提取论文中的关键图片（架构图、性能图等）
- 💬 **对话问答**: 基于 RAG 技术与论文进行对话
- 🔍 **智能检索**: 按标签和关键词快速检索论文

## 技术栈

- **前端**: Streamlit
- **LLM**: Google Gemini API
- **数据库**: SQLite + ChromaDB
- **PDF 解析**: PyMuPDF (fitz)
- **向量检索**: ChromaDB

## 安装步骤

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd paperbrain
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 到 `.env` 并填入您的 Gemini API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
GEMINI_API_KEY=
```

### 5. 初始化数据库

```bash
python database/init_db.py
```

### 6. 启动应用

```bash
streamlit run app.py
```

应用将在浏览器中自动打开，默认地址为 `http://localhost:8501`

## 使用指南

### 上传论文

1. 点击侧边栏的「上传论文」按钮
2. 选择 PDF 格式的学术论文
3. 点击「开始处理」
4. 等待系统自动处理（解析、总结、标签、向量化）
5. 处理完成后查看论文详情

### 查看论文

1. 在主页的论文列表中点击「查看详情」
2. 查看结构化笔记、思维导图
3. 使用对话功能向论文提问

### 标签筛选

1. 在主页使用标签筛选器
2. 选择感兴趣的领域、方法或任务标签
3. 系统自动筛选相关论文

### 对话问答

1. 在论文详情页切换到「对话问答」标签
2. 输入您的问题
3. 系统基于论文内容生成回答

## 项目结构

```
paperbrain/
├── app.py                      # 主应用入口
├── requirements.txt            # 依赖列表
├── config.py                   # 配置文件
├── .env.example               # 环境变量示例
├── .gitignore                 # Git 忽略规则
├── README.md                  # 项目文档
│
├── database/                   # 数据库模块
│   ├── models.py              # 数据模型
│   ├── db_manager.py          # 数据库操作
│   └── init_db.py             # 初始化脚本
│
├── services/                   # 核心服务
│   ├── llm_service.py         # LLM 调用
│   ├── pdf_parser.py          # PDF 解析
│   ├── summarizer.py          # 总结生成
│   ├── mindmap_generator.py   # 思维导图生成
│   ├── tagger.py              # 标签生成
│   ├── image_extractor.py     # 图片提取
│   └── rag_service.py         # RAG 检索
│
├── ui/                         # UI 组件
│   ├── dashboard.py           # 主页面
│   ├── upload_page.py         # 上传页面
│   ├── paper_detail.py        # 详情页面
│   └── chat_interface.py      # 对话界面
│
├── utils/                      # 工具函数
│   ├── prompts.py             # Prompt 模板
│   └── helpers.py             # 辅助函数
│
└── data/                       # 数据存储
    ├── papers/                # PDF 文件
    ├── images/                # 提取的图片
    ├── paperbrain.db          # SQLite 数据库
    └── chroma_db/             # 向量数据库
```

## 常见问题

### 1. 如何获取 Gemini API 密钥？

访问 [Google AI Studio](https://makersuite.google.com/app/apikey) 创建 API 密钥。

### 2. 处理论文时出错怎么办？

- 检查 PDF 文件是否损坏
- 确认 Gemini API 密钥是否正确
- 查看终端输出的错误信息

### 3. 思维导图无法显示？

如果思维导图无法正常显示，可以安装 `streamlit-mermaid` 组件：

```bash
pip install streamlit-mermaid
```

### 4. 如何修改标签？

目前版本支持 LLM 自动生成标签。未来版本将支持手动编辑标签功能。

## 开发计划

- [ ] 支持批量上传论文
- [ ] 支持手动编辑标签
- [ ] 支持导出笔记为 Markdown
- [ ] 支持论文引用关系图
- [ ] 支持多语言论文
- [ ] 优化长论文处理性能

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。
