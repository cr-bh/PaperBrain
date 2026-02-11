# PaperBrain 产品需求文档 (PRD)

**文档版本**: v1.1
**创建日期**: 2026-01-20
**最后更新**: 2026-02-05
**文档状态**: 正式版
**负责人**: 产品团队

---

## 文档修订历史

| 版本 | 日期 | 修订人 | 修订内容 |
|------|------|--------|----------|
| v1.0 | 2026-01-20 | 产品团队 | 初始版本，基于现有代码生成完整PRD |
| v1.1 | 2026-02-05 | 产品团队 | 新增Auto-Scholar论文智能监控功能模块 |

---

## 目录

1. [产品概述](#1-产品概述)
2. [产品定位与目标](#2-产品定位与目标)
3. [用户画像与使用场景](#3-用户画像与使用场景)
4. [核心功能需求](#4-核心功能需求)
5. [技术架构](#5-技术架构)
6. [数据架构](#6-数据架构)
7. [非功能性需求](#7-非功能性需求)
8. [产品路线图](#8-产品路线图)
9. [风险与挑战](#9-风险与挑战)
10. [附录](#10-附录)

---

## 1. 产品概述

### 1.1 产品简介

PaperBrain 是一款基于 AI 的智能学术论文管理与知识库系统，旨在帮助科研人员高效管理、理解和检索学术论文。通过自动化的论文解析、结构化总结、思维导图生成、智能标签归类和对话式检索，PaperBrain 显著提升科研人员的文献阅读效率和知识管理能力。

### 1.2 产品价值主张

- **自动化处理**: 一键上传 PDF，自动完成解析、总结、标签、向量化全流程
- **结构化理解**: 将论文转化为 8 个维度的结构化笔记，快速把握核心内容
- **可视化呈现**: 自动生成思维导图，直观展示论文逻辑结构
- **智能检索**: 基于 RAG 技术的对话式问答，支持跨论文检索和精准定位
- **知识组织**: 多维度标签体系（领域/方法/任务），支持层级化知识管理
- **智能监控**: Auto-Scholar 自动抓取 Arxiv 最新论文，AI 评分筛选，每日推送高质量论文

### 1.3 核心竞争力

1. **深度理解**: 不仅提取摘要，而是生成包含问题定义、相关工作、方法论、实验结果等完整结构的深度总结
2. **MECE 原则**: 相关工作总结严格遵循论文原有的组织逻辑（时间脉络/技术分类/问题导向/因果关系）
3. **对话式交互**: 支持 @mention 语法的多论文对话，自然语言查询替代传统关键词搜索
4. **可编辑性**: 所有 AI 生成内容均可人工编辑，支持用户上传自定义图片和修改标签
5. **智能监控**: Auto-Scholar 结合关键词筛选、引用数过滤和 AI 深度评分，自动发现高价值论文

---

## 2. 产品定位与目标

### 2.1 产品定位

**目标用户**: 科研人员、研究生、博士生、学术工作者
**产品类型**: 桌面端 Web 应用（基于 Streamlit）
**使用场景**: 本地部署或私有云部署，保护用户数据隐私

### 2.2 产品目标

**短期目标（3个月）**:
- 完善现有核心功能的稳定性和用户体验
- 优化 LLM 生成质量（总结、思维导图、标签）
- 支持批量上传和处理

**中期目标（6-12个月）**:
- 支持论文引用关系图谱
- 支持多语言论文（英文、中文）
- 支持导出功能（Markdown、PDF）
- 移动端适配

**长期目标（1-2年）**:
- 构建科研社区，支持论文分享和协作
- 集成文献管理工具（Zotero、Mendeley）
- 支持自动文献综述生成
- 提供 API 接口供第三方集成

### 2.3 成功指标

- **用户留存率**: 月活跃用户留存率 > 60%
- **论文处理量**: 单用户平均管理论文数 > 50 篇
- **使用频率**: 用户周均使用次数 > 3 次
- **功能使用率**: 对话问答功能使用率 > 40%
- **用户满意度**: NPS 评分 > 50

---

## 3. 用户画像与使用场景

### 3.1 核心用户画像

#### 用户画像 1: 博士研究生

**基本信息**:
- 年龄: 25-30 岁
- 学历: 博士在读
- 研究领域: 人工智能、计算机视觉、自然语言处理

**痛点**:
- 每周需要阅读 5-10 篇论文，时间紧张
- 难以快速把握论文核心贡献和技术细节
- 文献综述时难以系统梳理相关工作的演进脉络
- 论文管理混乱，难以快速检索历史阅读过的内容

**使用场景**:
- 开题阶段：批量上传领域内经典论文，快速了解研究现状
- 日常阅读：上传新论文，查看结构化总结和思维导图
- 撰写综述：通过标签筛选相关论文，使用对话功能提取关键信息
- 论文写作：查询特定方法的实现细节和实验结果

#### 用户画像 2: 科研工作者

**基本信息**:
- 年龄: 30-45 岁
- 职位: 高校教师、研究员
- 研究方向: 运筹学、优化算法、强化学习

**痛点**:
- 需要跟踪多个研究方向的最新进展
- 指导学生时需要快速回顾相关论文
- 撰写项目申请书时需要系统梳理研究背景
- 论文审稿时需要快速定位相关工作

**使用场景**:
- 文献跟踪：定期上传最新论文，通过标签体系组织知识
- 学生指导：使用对话功能快速回答学生关于论文的问题
- 项目申请：导出结构化笔记，整理研究背景和创新点
- 论文审稿：快速检索相似工作，判断论文创新性

### 3.2 典型使用流程

#### 流程 1: 新论文快速理解

1. 用户上传 PDF 论文
2. 系统自动处理（2-3 分钟）
3. 用户查看结构化笔记，快速了解：
   - 论文解决什么问题
   - 现有方案有什么局限
   - 本文的核心贡献是什么
   - 具体方法如何实现
   - 实验结果如何
4. 用户查看思维导图，理解论文整体结构
5. 用户通过对话功能深入询问技术细节

#### 流程 2: 文献综述撰写

1. 用户通过标签筛选特定领域的论文（如"强化学习" + "多智能体"）
2. 用户使用全局对话功能提问："这些论文的主要研究方向有哪些？"
3. 系统检索所有相关论文，生成综合性回答
4. 用户针对特定论文深入提问：`@AlphaGo 这篇论文的核心算法是什么？`
5. 用户编辑结构化笔记，添加自己的理解和批注
6. 用户导出笔记为 Markdown 格式，用于撰写综述

#### 流程 3: 知识库管理

1. 用户定期上传新论文
2. 系统自动生成标签并归类
3. 用户在标签管理页面：
   - 调整标签层级（如将"MARL"设为"强化学习"的子标签）
   - 合并重复标签
   - 自定义标签颜色
4. 用户通过主页的标签树快速定位相关论文
5. 用户删除不再需要的论文，系统自动清理相关数据

---

## 4. 核心功能需求

### 4.1 功能模块总览

| 功能模块 | 优先级 | 状态 | 说明 |
|---------|--------|------|------|
| 论文上传与解析 | P0 | ✅ 已实现 | PDF上传、文本提取、元数据提取 |
| 结构化总结生成 | P0 | ✅ 已实现 | 8维度深度总结 |
| 思维导图生成 | P0 | ✅ 已实现 | Mermaid.js可视化 |
| 智能标签系统 | P0 | ✅ 已实现 | 三维度自动标签+层级管理 |
| 图片提取与管理 | P1 | ✅ 已实现 | 关键图片识别、用户上传、标注编辑 |
| RAG对话问答 | P0 | ✅ 已实现 | 全局对话+@mention语法 |
| 论文检索与筛选 | P0 | ✅ 已实现 | 标签筛选、全文搜索 |
| 内容编辑 | P1 | ✅ 已实现 | 结构化笔记编辑、图片管理 |
| 标签管理 | P1 | ✅ 已实现 | 层级调整、重复检测、合并 |
| Auto-Scholar 论文监控 | P0 | ✅ 已实现 | Arxiv自动抓取+AI评分+日报生成 |
| 批量上传 | P2 | 🔄 规划中 | 多文件批量处理 |
| 导出功能 | P2 | 🔄 规划中 | Markdown/PDF导出 |
| 引用关系图谱 | P3 | 📋 待规划 | 论文引用网络可视化 |

### 4.2 功能详细说明

#### 4.2.1 论文上传与解析

**功能描述**:
用户上传PDF格式的学术论文，系统自动解析论文内容、提取元数据和图片信息。

**实现方式**:
- **技术选型**: PyMuPDF (fitz) - 高性能PDF解析库
- **核心流程**:
  1. 文件上传验证（格式、大小限制）
  2. PDF文本提取（保留页码标记）
  3. 元数据提取（标题、作者、创建日期）
  4. 图片信息提取（位置、Caption）
  5. 文件存储到 `data/papers/` 目录

**技术实现** (`services/pdf_parser.py`):
```python
def parse_pdf(pdf_path: str) -> dict:
    """
    解析PDF文件
    返回: {
        'text': 全文文本（带页码标记）,
        'metadata': {title, author, subject, creator},
        'images': [{page, caption, bbox}]
    }
    """
    doc = fitz.open(pdf_path)
    # 逐页提取文本和图片
    # 使用正则匹配Figure/Fig标题
```

**用户交互**:
- 拖拽或点击上传PDF文件
- 显示8步处理进度条（10% → 20% → 40% → 55% → 70% → 80% → 85% → 95%）
- 处理完成后显示成功动画和"查看详情"按钮

**异常处理**:
- PDF损坏：提示用户重新上传
- 文本提取失败：保存原始文件，标记为"待人工处理"
- 重复论文：检测标题，询问是否覆盖

**性能要求**:
- 单篇论文处理时间 < 3分钟
- 支持最大50MB的PDF文件
- 并发处理能力：单用户同时处理1篇

---

#### 4.2.2 结构化总结生成

**功能描述**:
使用LLM将论文全文转化为8个维度的结构化笔记，帮助用户快速理解论文核心内容。

**8个维度**:
1. **一句话总结** (one_sentence_summary): 100字内概括核心工作
2. **问题定义** (problem_definition): 研究问题、背景、动机
3. **相关工作** (existing_solutions): 现有方案综述（遵循MECE原则）
4. **现有局限** (limitations): 现有方案的不足
5. **本文贡献** (contribution): 2-4个核心创新点
6. **具体方法** (methodology): 详细技术路线（5个子部分）
7. **实验结果** (results): 数据集、指标、对比实验
8. **未来工作（论文）** (future_work_paper): 作者提出的方向
9. **未来工作（洞察）** (future_work_insights): 批判性分析

**实现方式**:
- **技术选型**: Google Gemini API（自定义端点）
- **Prompt工程**:
  - 使用详细的结构化Prompt（`utils/prompts.py::SUMMARIZE_PA`）
  - 强调MECE原则和论文原有组织逻辑
  - 要求使用Markdown格式（五级标题、列表、粗体、代码格式）
  - 输出JSON格式，便于结构化存储
- **文本处理**:
  - 输入截断：最大30,000字符（约15,000 tokens）
  - Temperature: 0.3（低温度保证一致性）
  - 重试机制：3次重试，间隔2秒

**技术实现** (`services/summarizer.py`):
```python
def summarize_paper(paper_text: str) -> dict:
    """
    生成结构化总结
    返回: {
        'title': str,
        'authors': [str],
        'summary_struct': {8个维度的内容}
    }
    """
    # 截断文本
    truncated_text = paper_text[:30000]
    # 调用LLM
    prompt = format_prompt(SUMMARIZE_PAPER_PROMPT, paper_text=truncated_text)
    result = llm_service.generate_json(prompt, temperature=0.3)
    return result
```

**质量保证**:
- **相关工作部分**:
  - 必须识别论文的组织方式（时间脉络/技术分类/问题导向/因果关系/MECE）
  - 列举5-8个代表性工作，包含作者、年份、方法名、核心思路
  - 使用五级标题分类，列表项展示具体工作
- **方法论部分**:
  - 5个必需子部分：整体框架、核心算法、技术细节、创新机制、实现要点
  - 详细到伪代码级别的描述
- **格式规范**:
  - 模块内子标题使用 `#####`（五级标题）
  - 避免与模块标题 `###`（三级标题）混淆

**用户交互**:
- 自动生成，无需用户干预
- 生成后在论文详情页展示
- 支持编辑模式，用户可修改任意部分

---

#### 4.2.3 思维导图生成

**功能描述**:
基于结构化总结，自动生成Mermaid.js格式的思维导图，可视化展示论文逻辑结构。

**实现方式**:
- **技术选型**: Mermaid.js（graph LR格式）
- **渲染方式**:
  1. **HTML渲染**（推荐）: 使用Mermaid CDN，直接在浏览器渲染
  2. **Streamlit组件**: streamlit-mermaid库
  3. **代码查看**: 提供mermaid.live链接，用户可在线编辑
- **结构设计**:
  - 根节点：论文标题
  - 第一层：研究问题 | 现有局限 | 本文贡献 | 方法框架 | 实验结果
  - 第二层：展开各部分的关键要点
  - 重要节点（贡献）：使用粗体和特殊样式

**配色要求**（关键）:
- **绝对禁止**: 浅色背景（浅黄、浅蓝、白色）+ 白色文字
- **推荐方案**:
  - 深色背景 + 白色文字: `fill:#2C3E50,color:#FFFFFF`
  - 中等背景 + 深色文字: `fill:#3498DB,color:#000000`
  - 鲜艳背景 + 深色文字: `fill:#E74C3C,color:#000000`
- **重要节点**: 使用醒目深色背景（红/绿/紫色系），`stroke-width:3px`

**技术实现** (`services/mindmap_generator.py`):
```python
def generate_mindmap(summary_json: str) -> str:
    """
    生成Mermaid代码
    返回: Mermaid.js代码字符串（graph LR格式）
    """
    prompt = format_prompt(GENERATE_MINDMAP_PROMPT, summary_json=summary_json)
    mermaid_code = llm_service.generate_text(prompt, temperature=0.5)
    
    # 验证Mermaid语法
    if not validate_mermaid(mermaid_code):
        return generate_fallback_mindmap(summary_json)
    
    return mermaid_code
```

**降级策略**:
- LLM生成失败：使用简化版思维导图模板
- 渲染失败：提供代码查看和mermaid.live链接

**用户交互**:
- 在论文详情页"思维导图"Tab查看
- 支持缩放、拖拽
- 提供"重新生成"按钮

---

#### 4.2.4 智能标签系统

**功能描述**:
自动为论文生成三维度标签（领域/方法/任务），支持层级化组织和人工管理。

**三维度标签**:
1. **Domain（领域）**: 研究领域，如 Reinforcement Learning, Computer Vision, NLP, Operations Research
2. **Methodology（方法）**: 技术方法，如 Transformer, PPO, Genetic Algorithm, Deep Learning
3. **Task（任务）**: 应用任务，如 Image Classification, Battery Dispatch, Text Generation

**实现方式**:
- **技术选型**: LLM自动生成 + 数据库存储
- **生成策略**:
  - 基于结构化总结内容分析
  - 每个维度生成1-3个标签
  - 推断层级关系（如 Multi-agent RL → Reinforcement Learning）
- **存储结构**:
  - Tag表：id, name, category, parent_id, color
  - PaperTag表：paper_id, tag_id（多对多关系）

**技术实现** (`services/tagger.py`):
```python
def generate_tags(summary_json: str) -> dict:
    """
    生成三维度标签
    返回: {
        'domain': ['tag1', 'tag2'],
        'methodology': ['tag1', 'tag2'],
        'task': ['tag1']
    }
    """
    prompt = format_prompt(GENERATE_TAGS_PROMPT, summary_json=summary_json)
    tags = llm_service.generate_json(prompt, temperature=0.3)
    return tags

def save_tags_to_db(paper_id: int, tags: dict):
    """保存标签到数据库，自动创建不存在的标签"""
    for category, tag_names in tags.items():
        for tag_name in tag_names:
            tag = db_manager.get_or_create_tag(tag_name, category)
            db_manager.add_tag_to_paper(paper_id, tag.id)
```

**标签管理功能**:
1. **层级调整**: 拖拽或选择父标签，构建标签树
2. **重复检测**: 
   - Levenshtein距离算法检测相似标签
   - 检测规则：编辑距离≤2、子串匹配、分隔符归一化
3. **标签合并**: 将重复标签合并，自动更新关联论文
4. **颜色自定义**: 为标签设置颜色，便于视觉区分
5. **批量初始化**: 一键创建MECE标准标签体系

**用户交互**:
- 自动生成后显示在论文卡片上
- 点击标签可筛选相关论文
- 在标签管理页面统一管理
- 支持手动添加/删除论文标签

---

#### 4.2.5 图片提取与管理

**功能描述**:
自动提取论文中的关键图片（架构图、性能图、算法图），支持用户上传自定义图片和编辑标注。

**实现方式**:
- **自动提取**:
  - 技术选型：PyMuPDF图片提取
  - 识别策略：正则匹配Figure/Fig/Architecture/Performance/Algorithm关键词
  - 分类：architecture（架构）、performance（性能）、algorithm（算法）、other（其他）
- **用户上传**:
  - 支持PNG/JPG/JPEG格式
  - 文件去重：使用 `{filename}_{size}` 作为唯一标识
  - Session state防止重复上传
- **图片管理**:
  - 存储路径：`data/images/{paper_id}/`
  - 命名规则：`page{N}_img{M}.{ext}` 或 `user_upload_{timestamp}.{ext}`
  - 数据库记录：image_path, caption, page_number, image_type

**技术实现** (`services/image_extractor.py`):
```python
def extract_key_images(pdf_path: str, paper_id: int) -> list:
    """
    提取关键图片
    返回: [{
        'image_path': str,
        'caption': str,
        'page_number': int,
        'image_type': str
    }]
    """
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num, page in enumerate(doc):
        # 提取图片
        image_list = page.get_images()
        # 查找Caption
        text = page.get_text()
        captions = extract_figure_captions(text)
        # 分类图片类型
        for img in image_list:
            img_type = classify_image_type(captions)
            images.append({...})
    
    return images
```

**用户交互**:
- 在论文详情页按类型筛选图片（架构/性能/算法/全部）
- 编辑模式：
  - 上传新图片（拖拽或点击）
  - 编辑图片标注（inline文本框）
  - 删除图片（垃圾桶图标）
- 查看模式：图片展示 + 标注显示

**性能优化**:
- 图片懒加载
- 缩略图生成（未来）
- 文件大小限制：单张<10MB

---

#### 4.2.6 RAG对话问答

**功能描述**:
基于RAG（Retrieval-Augmented Generation）技术，支持用户与论文进行自然语言对话，快速获取信息。

**核心能力**:
1. **全局对话**: 检索所有论文，回答跨论文问题
2. **@mention语法**: 指定特定论文，如 `@AlphaGo 这篇论文的核心算法是什么？`
3. **多论文查询**: 支持多个@mention，如 `@paper1 @paper2 有什么区别？`
4. **模糊匹配**: @mention支持部分标题匹配，自动查找最相关论文
5. **来源追溯**: 回答中标注来源论文，可点击跳转

**实现方式**:
- **技术选型**: ChromaDB（向量数据库） + Gemini Embedding
- **向量化流程**:
  1. 文本分块：按段落分割，每块约1000字符
  2. 生成Embedding：使用Gemini Embedding API
  3. 存储到ChromaDB：带paper_id和chunk_index元数据
- **检索流程**:
  1. 解析@mention，提取paper_id列表
  2. 向量检索：Top-K相似文本块（K=10）
  3. 构建Prompt：检索结果 + 用户问题
  4. LLM生成回答：Temperature=0.3
  5. 添加来源信息

**技术实现** (`services/rag_service.py`):
```python
class RAGService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection("papers")
    
    def add_paper_to_vector_db(self, paper_id: int, paper_text: str):
        """向量化并存储"""
        chunks = self._chunk_text(paper_text)
        ids = [f"paper_{paper_id}_chunk_{i}" for i in range(len(chunks))]
        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=[{"paper_id": paper_id, "chunk_index": i} for i in range(len(chunks))]
        )
    
    def query_all_papers(self, question: str) -> str:
        """全局检索"""
        results = self.collection.query(
            query_texts=[question],
            n_results=config.TOP_K_RESULTS
        )
        # 构建Prompt并生成回答
        answer = self._generate_answer(results, question)
        return answer
    
    def parse_mention(self, question: str):
        """解析@mention"""
        pattern = r'@"([^"]+)"|@(\S+)'
        matches = re.findall(pattern, question)
        paper_ids = []
        for match in matches:
            keyword = match[0] if match[0] else match[1]
            paper = db_manager.get_paper_by_title(keyword)
            if not paper:
                papers = db_manager.search_papers(keyword)
                paper = papers[0] if papers else None
            if paper:
                paper_ids.append(paper.id)
        cleaned_question = re.sub(pattern, '', question).strip()
        return paper_ids, cleaned_question
```

**用户交互**:
- 独立的"对话问答"页面
- 左侧：论文列表 + 搜索框 + 快速@mention按钮
- 右侧：聊天界面
  - 输入框支持@自动补全
  - 消息气泡显示问答历史
  - 回答下方显示来源论文（可点击）
- 清空历史按钮

**性能要求**:
- 单次检索时间 < 2秒
- 回答生成时间 < 5秒
- 支持对话历史：最多保留50轮

---

#### 4.2.7 论文检索与筛选

**功能描述**:
提供多维度的论文检索和筛选功能，帮助用户快速定位目标论文。

**检索方式**:
1. **全文搜索**: 按标题或作者搜索（模糊匹配）
2. **标签筛选**: 
   - 三维度独立筛选（领域/方法/任务）
   - 支持多选（OR逻辑）
   - 层级标签自动包含子标签
3. **组合筛选**: 搜索 + 标签筛选同时生效（AND逻辑）

**实现方式**:
- **技术选型**: SQLAlchemy ORM + SQLite LIKE查询
- **搜索实现**:
```python
def search_papers(keyword: str) -> list:
    """模糊搜索论文"""
    return session.query(Paper).filter(
        or_(
            Paper.title.ilike(f'%{keyword}%'),
            Paper.authors.ilike(f'%{keyword}%')
        )
    ).all()
```
- **标签筛选实现**:
```python
def filter_papers_by_tags(tag_ids: list) -> list:
    """按标签筛选论文"""
    return session.query(Paper).join(PaperTag).filter(
        PaperTag.tag_id.in_(tag_ids)
    ).distinct().all()
```

**用户交互**:
- 主页顶部：搜索框（实时搜索）
- 左侧边栏：标签树
  - 三个折叠面板（Domain/Methodology/Task）
  - 复选框多选
  - 显示每个标签的论文数量
- 右侧：论文卡片列表
  - 显示筛选结果数量
  - 支持排序（最新/最早/标题）

**性能优化**:
- 搜索防抖：300ms延迟
- 标签筛选：客户端缓存
- 分页加载：每页20篇（未来）

---

#### 4.2.8 内容编辑

**功能描述**:
支持用户编辑AI生成的结构化笔记和管理图片，实现人机协作。

**编辑功能**:
1. **结构化笔记编辑**:
   - 8个维度独立编辑
   - 使用Streamlit text_area组件
   - 支持Markdown格式
   - 保存/重置按钮
2. **图片管理**:
   - 上传新图片（按类型分类）
   - 编辑图片标注
   - 删除图片
3. **标签编辑**:
   - 添加/删除论文标签
   - 在论文详情页直接操作

**实现方式**:
- **技术选型**: Streamlit Session State + 数据库更新
- **编辑模式切换**:
```python
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

if st.button("✏️ 编辑" if not st.session_state.edit_mode else "👁️ 查看"):
    st.session_state.edit_mode = not st.session_state.edit_mode
    st.rerun()
```
- **内容保存**:
```python
def update_paper_summary(paper_id: int, summary: dict):
    """更新论文总结"""
    paper = session.query(Paper).filter(Paper.id == paper_id).first()
    paper.content_summary = summary
    session.commit()
```

**用户交互**:
- 论文详情页右上角：编辑/查看切换按钮
- 编辑模式：
  - 所有文本框可编辑
  - 显示保存/重置按钮
  - 图片管理区域激活
- 查看模式：
  - 只读展示
  - Markdown渲染

**数据安全**:
- 编辑前自动备份（未来）
- 重置功能恢复AI生成内容
- 版本历史（未来）

---

#### 4.2.9 标签管理

**功能描述**:
提供统一的标签管理界面，支持层级调整、重复检测、批量操作。

**核心功能**:
1. **标签列表**:
   - 按类别分组显示（Domain/Methodology/Task）
   - 显示层级关系（父标签 → 子标签）
   - 显示每个标签的论文数量
   - 编辑/删除/合并按钮
2. **重复检测**:
   - 自动检测相似标签
   - 显示相似度和匹配原因
   - 一键合并功能
3. **标签编辑**:
   - 修改标签名称
   - 调整父标签（构建层级）
   - 自定义颜色
4. **批量初始化**:
   - 一键创建MECE标准标签体系
   - 预定义常用领域/方法/任务标签

**实现方式**:
- **重复检测算法**:
```python
def detect_duplicate_tags() -> list:
    """检测重复标签"""
    tags = db_manager.get_all_tags()
    duplicates = []
    
    for i, tag1 in enumerate(tags):
        for tag2 in tags[i+1:]:
            # 1. 精确匹配（忽略大小写）
            if tag1.name.lower() == tag2.name.lower():
                duplicates.append((tag1, tag2, "exact"))
            # 2. 子串匹配
            elif tag1.name.lower() in tag2.name.lower():
                duplicates.append((tag1, tag2, "substring"))
            # 3. 编辑距离
            elif levenshtein_distance(tag1.name, tag2.name) <= 2:
                duplicates.append((tag1, tag2, "similar"))
    
    return duplicates
```
- **标签合并**:
```python
def merge_tags(source_tag_id: int, target_tag_id: int):
    """合并标签"""
    # 1. 将source_tag的所有论文关联转移到target_tag
    paper_tags = session.query(PaperTag).filter(
        PaperTag.tag_id == source_tag_id
    ).all()
    for pt in paper_tags:
        pt.tag_id = target_tag_id
    # 2. 删除source_tag
    session.query(Tag).filter(Tag.id == source_tag_id).delete()
    session.commit()
```

**用户交互**:
- 独立的"标签管理"页面
- 三个Tab：
  1. **所有标签**: 列表展示 + 编辑功能
  2. **重复检测**: 相似标签列表 + 合并按钮
  3. **添加标签**: 表单创建新标签
- 操作确认：删除/合并前弹出确认对话框

---

#### 4.2.10 Auto-Scholar 论文智能监控

**功能描述**:
自动监控 Arxiv 最新论文，通过多层筛选（关键词匹配、引用数过滤、AI深度评分）发现高价值论文，生成每日推荐报告。

**核心能力**:
1. **自动抓取**: 每日自动抓取 Arxiv 指定领域的最新论文
2. **三层筛选**:
   - 第一层：关键词匹配（用户自定义关键词库）
   - 第二层：Semantic Scholar 元数据筛选（引用数、影响力）
   - 第三层：AI 深度评分（1-10分，基于相关性和创新性）
3. **智能评分**: 使用 LLM 分析标题和摘要，生成评分和理由
4. **自动翻译**: 标题和摘要自动翻译为中文
5. **分级推荐**: S级（9-10分）、A级（7-8分）、B级（5-6分）
6. **日报生成**: 自动生成 HTML 格式的每日论文推荐报告

**实现方式**:

**技术架构**:
```
用户配置关键词
    ↓
Arxiv Crawler 抓取论文（arxiv库）
    ↓
关键词筛选（至少匹配2个关键词）
    ↓
Semantic Scholar 元数据筛选
    ├─ 引用数 ≥ 3 或影响力引用 ≥ 1
    ├─ 2024+ 年份论文直接通过
    └─ 降级规则：关键词匹配保留
    ↓
AI 评分引擎（豆包 LLM）
    ├─ 分析标题和摘要
    ├─ 生成 1-10 分评分
    ├─ 生成评分理由
    ├─ 翻译标题和摘要
    └─ 生成标签
    ↓
保存到数据库（ArxivPaper表）
    ↓
生成 HTML 日报
```

**技术实现**:

1. **Arxiv 爬虫** ([services/arxiv_crawler.py](services/arxiv_crawler.py)):
```python
class ArxivCrawler:
    def fetch_daily_papers(self, date: datetime, max_results: int = 200):
        """抓取指定日期的论文"""
        # 从数据库获取关键词
        keywords = self._get_keywords_from_db()

        # 构建查询（支持日期范围）
        query = self._build_query(keywords, start_date, end_date)

        # 使用 arxiv 库搜索
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        # 提取论文元数据（包含作者机构）
        papers = []
        for result in search.results():
            papers.append({
                'arxiv_id': result.entry_id.split('/')[-1],
                'title': result.title,
                'authors': [{'name': a.name, 'affiliation': a.affiliation}
                           for a in result.authors],
                'abstract': result.summary,
                'categories': result.categories,
                'published_date': result.published
            })

        return papers

    def keyword_filter(self, papers: List[Dict], keywords: List[str],
                      min_matches: int = 2) -> List[Dict]:
        """关键词筛选（至少匹配N个关键词）"""
        filtered = []
        for paper in papers:
            text = f"{paper['title']} {paper['abstract']}".lower()
            matches = sum(1 for kw in keywords if kw.lower() in text)
            if matches >= min_matches:
                filtered.append(paper)
        return filtered
```

2. **Semantic Scholar 筛选器** ([services/semantic_scholar_filter.py](services/semantic_scholar_filter.py)):
```python
class SemanticScholarFilter:
    def get_paper_metadata(self, arxiv_id: str) -> Optional[Dict]:
        """通过 Arxiv ID 获取 S2 元数据（带缓存和重试）"""
        # 检查缓存
        if arxiv_id in self.cache:
            return self.cache[arxiv_id]

        # 调用 S2 API（指数退避重试）
        url = f"{self.base_url}/paper/ARXIV:{arxiv_id}"
        params = {
            'fields': 'citationCount,influentialCitationCount,year,venue,authors'
        }
        response = requests.get(url, headers=self.headers, params=params)

        # 保存到缓存
        metadata = response.json()
        self.cache[arxiv_id] = metadata
        return metadata

    def should_keep_paper(self, metadata: Optional[Dict],
                         paper_info: Optional[Dict]) -> bool:
        """判断是否保留论文（带降级规则）"""
        # 标准规则：引用数或影响力引用达标
        if metadata:
            if metadata.get('citationCount', 0) >= 3:
                return True
            if metadata.get('influentialCitationCount', 0) >= 1:
                return True
            if metadata.get('year', 2024) >= 2024:
                return True  # 新论文放宽标准

        # 降级规则：关键词匹配
        if paper_info:
            text = f"{paper_info['title']} {paper_info['summary']}"
            if self._match_keywords(text, self.fallback_keywords):
                return True

        return False
```

3. **评分引擎** ([services/scoring_engine.py](services/scoring_engine.py)):
```python
class ScoringEngine:
    def score_paper(self, title: str, abstract: str) -> Dict:
        """对单篇论文打分"""
        prompt = format_prompt(
            SCORE_PAPER_PROMPT,
            title=title,
            abstract=abstract
        )

        # 调用豆包 LLM
        result = self.llm.generate_json(prompt, temperature=0.3)

        # 返回评分结果
        return {
            'score': float(result['score']),  # 1-10分
            'reason': result['reason'],       # 评分理由
            'title_zh': result['title_zh'],   # 中文标题
            'abstract_zh': result['abstract_zh'],  # 中文摘要
            'tags': result['tags']            # 自动标签
        }
```

4. **调度器** ([services/scheduler.py](services/scheduler.py)):
```python
class DailyScheduler:
    def run_daily_pipeline(self, date: datetime = None, max_results: int = 200):
        """执行完整的每日流水线"""
        # Step 1: 抓取论文
        papers = arxiv_crawler.fetch_daily_papers(date, max_results)

        # Step 1.5: 关键词筛选
        keywords = db_manager.get_all_keywords()
        papers = arxiv_crawler.keyword_filter(papers, keywords, min_matches=2)

        # Step 1.6: S2 筛选
        papers = semantic_scholar_filter.batch_filter(papers)

        # Step 2: 批量评分
        for paper in papers:
            score_result = scoring_engine.score_paper(
                paper['title'],
                paper['abstract']
            )

            # 保存到数据库
            db_manager.create_arxiv_paper(
                arxiv_id=paper['arxiv_id'],
                title=paper['title'],
                authors=paper['authors'],
                abstract=paper['abstract'],
                score=score_result['score'],
                score_reason=score_result['reason'],
                title_zh=score_result['title_zh'],
                abstract_zh=score_result['abstract_zh'],
                tags=score_result['tags']
            )

        # Step 3: 生成报告
        report_generator.generate_daily_report(papers, date)
```

5. **报告生成器** ([services/report_generator.py](services/report_generator.py)):
```python
class ReportGenerator:
    def generate_daily_report(self, papers: List[ArxivPaper], date: datetime):
        """生成 HTML 日报"""
        # 按分数分组
        s_papers = [p for p in papers if p.score >= 9]
        a_papers = [p for p in papers if 7 <= p.score < 9]
        b_papers = [p for p in papers if 5 <= p.score < 7]

        # 渲染 HTML 模板
        html = self._render_html(s_papers, a_papers, b_papers, date)

        # 保存文件
        report_path = f"data/reports/daily_{date.strftime('%Y%m%d')}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return report_path
```

**数据库设计**:

**ArxivPaper 表**:
| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键 |
| arxiv_id | String(50) | Arxiv ID（唯一） |
| title | String(500) | 英文标题 |
| authors | JSON | 作者列表（含机构） |
| abstract | Text | 英文摘要 |
| categories | JSON | Arxiv 分类 |
| published_date | DateTime | 发布日期 |
| score | Float | AI评分（1-10） |
| score_reason | Text | 评分理由 |
| title_zh | String(500) | 中文标题 |
| abstract_zh | Text | 中文摘要 |
| tags | JSON | 自动标签 |
| is_imported | Boolean | 是否已导入论文库 |
| fetch_date | DateTime | 抓取时间 |

**Keyword 表**:
| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键 |
| keyword | String(100) | 关键词 |
| category | String(50) | 类别（core/frontier） |
| is_active | Boolean | 是否启用 |

**用户交互**:

1. **论文列表页** ([ui/auto_scholar.py](ui/auto_scholar.py)):
   - 时间范围选择：昨天 / 自定义时间段
   - 操作按钮：
     - 🚀 立即抓取：触发流水线
     - 📄 导出报告：生成 HTML 日报
     - 📥 批量导入：导入到论文库（开发中）
     - 🗑️ 清空数据：清空所有抓取记录
   - 筛选选项：
     - 最低分数：0分以上 / 5分以上 / 7分以上 / 9分以上
     - 显示数量：20 / 50 / 100 / 200
   - 统计卡片：总计 / S级 / A级 / B级
   - 论文卡片：
     - 标题（中英文）
     - 作者（含机构）
     - 分数徽章（S/A/B级）
     - 评分理由
     - 标签
     - 操作：查看摘要、导入到论文库

2. **关键词配置页**:
   - 添加关键词表单（关键词 + 类别）
   - 关键词列表（按类别分组）
     - 核心关键词（Core）
     - 前沿关键词（Frontier）
   - 快速初始化：一键添加默认关键词

3. **统计分析页**:
   - 分数分布饼图
   - 论文数量柱状图
   - 分数详细分布直方图
   - 最高分论文 Top 5

**配置项** (config.py):
```python
# Semantic Scholar API
S2_API_KEY = os.getenv('S2_API_KEY', '')
S2_CACHE_PATH = 'data/s2_cache.json'
S2_MAX_RETRIES = 3
S2_RETRY_DELAY = 2.0
S2_REQUEST_INTERVAL = 1.0

# 降级关键词（S2 无数据时使用）
S2_FALLBACK_KEYWORDS = [
    'llm', 'large language model',
    'reinforcement learning', 'rl',
    'operations research', 'vrp', 'mip'
]
```

**性能优化**:
1. **缓存机制**: S2 API 响应缓存到本地 JSON 文件
2. **重试策略**: 指数退避重试（429 速率限制）
3. **批量处理**: 支持批量抓取和评分
4. **降级规则**: S2 无数据时使用关键词匹配

**异常处理**:
1. **Arxiv API 失败**: 重试3次，失败则跳过
2. **S2 API 404**: 论文未收录，使用降级规则
3. **S2 API 429**: 速率限制，指数退避重试
4. **评分失败**: 使用兜底评分（5.0分 + 默认理由）
5. **JSON 解析失败**: 保留原文，标记为"待分类"

**使用场景**:

**场景1：每日论文追踪**
1. 用户配置关键词（如 "Reinforcement Learning", "VRP", "LLM"）
2. 每天早上点击"立即抓取"
3. 系统自动抓取昨天的论文，筛选并评分
4. 用户查看 S级 和 A级 论文，快速了解最新进展
5. 点击"导出报告"生成 HTML 日报，分享给团队

**场景2：历史论文回溯**
1. 用户选择"自定义时间段"，设置过去30天
2. 点击"立即抓取"，系统批量处理
3. 系统抓取并评分200篇论文
4. 用户按分数筛选，查看高分论文
5. 将感兴趣的论文导入到论文库进行深度阅读

**场景3：关键词优化**
1. 用户发现抓取的论文不够精准
2. 进入"关键词设置"页面
3. 添加更具体的关键词（如 "Multi-agent RL", "Battery Dispatch"）
4. 删除不相关的关键词
5. 重新抓取，验证筛选效果

**未来优化方向**:
1. **定时任务**: 支持 Cron 定时自动抓取
2. **邮件推送**: 每日自动发送高分论文到邮箱
3. **一键导入**: 将 Auto-Scholar 论文直接导入到论文库
4. **作者追踪**: 关注特定作者的最新论文
5. **会议追踪**: 关注特定会议（ICML、NeurIPS）的论文
6. **引用追踪**: 追踪特定论文的引用情况

---

## 5. 技术架构

### 5.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层 (Streamlit)                  │
├─────────────────────────────────────────────────────────────┤
│  Dashboard  │  Upload  │  Paper Detail  │  Chat  │  Tag Mgmt │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        业务逻辑层 (Services)                   │
├─────────────────────────────────────────────────────────────┤
│  PDF Parser  │  Summarizer  │  Mindmap Gen  │  Tagger       │
│  Image Extractor  │  RAG Service  │  LLM Service             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        数据访问层 (Database)                   │
├─────────────────────────────────────────────────────────────┤
│  DB Manager (SQLAlchemy ORM)                                │
│  Models: Paper, Tag, PaperTag, PaperImage                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        数据存储层                              │
├─────────────────────────────────────────────────────────────┤
│  SQLite (关系型数据)  │  ChromaDB (向量数据)  │  文件系统      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        外部服务                                │
├─────────────────────────────────────────────────────────────┤
│  Gemini API (LLM)  │  Gemini Embedding API                   │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 技术栈

#### 5.2.1 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Streamlit | 1.31.0 | Web应用框架 |
| streamlit-mermaid | 0.3.0 | 思维导图渲染 |
| Mermaid.js | CDN | 图表可视化 |

**选型理由**:
- Streamlit：快速开发，Python原生，适合数据科学应用
- 无需前后端分离，降低开发复杂度
- 内置Session State管理，简化状态维护

#### 5.2.2 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 主要开发语言 |
| SQLAlchemy | 2.0.25 | ORM框架 |
| PyMuPDF (fitz) | 1.23.21 | PDF解析 |
| ChromaDB | 0.4.22 | 向量数据库 |
| LangChain | 0.1.6 | RAG框架 |
| Pillow | 10.2.0 | 图片处理 |

**选型理由**:
- SQLAlchemy：成熟的ORM，支持多种数据库
- PyMuPDF：高性能PDF解析，支持文本和图片提取
- ChromaDB：轻量级向量数据库，支持本地部署
- LangChain：简化RAG实现，提供文本分块等工具

#### 5.2.3 AI服务

| 服务 | 用途 | 配置 |
|------|------|------|
| Gemini API | 文本生成 | Temperature: 0.3-0.7, Max tokens: 8192 |
| Gemini Embedding | 向量化 | Model: models/embedding-001 |

**选型理由**:
- Gemini：Google最新LLM，性能优秀，支持长上下文
- 自定义API端点：支持私有部署或代理
- 成本可控：按Token计费

#### 5.2.4 数据库

| 数据库 | 用途 | 特点 |
|--------|------|------|
| SQLite | 关系型数据 | 轻量级，无需独立服务，适合单用户 |
| ChromaDB | 向量数据 | 本地持久化，支持元数据过滤 |

**选型理由**:
- SQLite：零配置，适合桌面应用和小规模部署
- ChromaDB：Python原生，易于集成，支持本地存储

### 5.3 核心数据流

#### 5.3.1 论文上传流程

```
用户上传PDF
    ↓
保存文件到 data/papers/
    ↓
PDF Parser 提取文本、元数据、图片信息
    ↓
Summarizer 生成结构化总结 (LLM)
    ↓
检查重复 (按标题)
    ├─ 存在 → 询问是否覆盖
    └─ 不存在 → 创建新记录
    ↓
Mindmap Generator 生成思维导图 (LLM)
    ↓
Tagger 生成标签 (LLM)
    ↓
保存到数据库 (Paper, Tag, PaperTag)
    ↓
Image Extractor 提取关键图片
    ↓
保存图片到 data/images/{paper_id}/
    ↓
RAG Service 向量化文本
    ├─ 文本分块 (1000 chars)
    ├─ 生成Embedding
    └─ 存储到ChromaDB
    ↓
更新 embedding_status = True
    ↓
完成，跳转到论文详情页
```

#### 5.3.2 对话问答流程

```
用户输入问题
    ↓
解析 @mention (正则匹配)
    ├─ 有@mention → 提取paper_id列表
    └─ 无@mention → paper_id = []
    ↓
向量检索 (ChromaDB)
    ├─ 有paper_id → 限定检索范围
    └─ 无paper_id → 全局检索
    ↓
获取 Top-K 文本块 (K=10)
    ↓
构建 RAG Prompt
    ├─ 检索到的文本块
    └─ 用户问题
    ↓
LLM 生成回答 (Temperature=0.3)
    ↓
添加来源论文信息
    ↓
返回回答 + 来源列表
```

### 5.4 关键技术决策

#### 5.4.1 为什么选择Streamlit而非Flask/Django?

**优势**:
- 快速开发：无需编写HTML/CSS/JavaScript
- Python原生：前后端统一语言
- 内置组件：文件上传、表单、图表等开箱即用
- Session State：简化状态管理

**劣势**:
- 性能限制：不适合高并发场景
- 定制性差：UI样式受限
- 单用户导向：多用户需要额外处理

**适用场景**: 本地部署、小团队使用、快速原型

#### 5.4.2 为什么使用SQLite而非PostgreSQL/MySQL?

**优势**:
- 零配置：无需安装数据库服务
- 轻量级：单文件存储
- 跨平台：支持Windows/Mac/Linux
- 足够性能：单用户场景下性能充足

**劣势**:
- 并发限制：不支持高并发写入
- 功能受限：缺少部分高级特性

**迁移路径**: 未来可通过SQLAlchemy无缝迁移到PostgreSQL

#### 5.4.3 为什么使用ChromaDB而非Pinecone/Weaviate?

**优势**:
- 本地部署：数据隐私保护
- Python原生：易于集成
- 零成本：无需付费
- 持久化存储：支持本地文件系统

**劣势**:
- 规模限制：不适合百万级向量
- 功能较少：缺少高级检索功能

**适用场景**: 个人使用、小规模数据（<10万篇论文）

---

## 6. 数据架构

### 6.1 数据库设计

#### 6.1.1 关系型数据库（SQLite）

**Paper 表（论文主表）**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, Auto | 论文ID |
| title | String(500) | NOT NULL | 论文标题 |
| authors | JSON | - | 作者列表 |
| file_path | String(500) | NOT NULL | PDF文件路径 |
| upload_date | DateTime | DEFAULT NOW | 上传时间 |
| content_summary | JSON | - | 结构化总结（8个维度） |
| mindmap_code | Text | - | Mermaid代码 |
| embedding_status | Boolean | DEFAULT FALSE | 是否已向量化 |

**Tag 表（标签表）**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, Auto | 标签ID |
| name | String(100) | UNIQUE, NOT NULL | 标签名称 |
| category | String(50) | - | 类别（domain/methodology/task） |
| parent_id | Integer | FK(Tag.id) | 父标签ID（支持层级） |
| color | String(20) | DEFAULT '#3B82F6' | 标签颜色（Hex） |

**PaperTag 表（论文-标签关联表）**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, Auto | 关联ID |
| paper_id | Integer | FK(Paper.id), NOT NULL | 论文ID |
| tag_id | Integer | FK(Tag.id), NOT NULL | 标签ID |

**PaperImage 表（论文图片表）**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, Auto | 图片ID |
| paper_id | Integer | FK(Paper.id), NOT NULL | 论文ID |
| image_path | String(500) | NOT NULL | 图片文件路径 |
| caption | Text | - | 图片标注 |
| page_number | Integer | - | 所在页码 |
| image_type | String(50) | - | 类型（architecture/performance/algorithm/other） |

**关系说明**:
- Paper ↔ Tag: 多对多关系，通过 PaperTag 关联
- Paper ↔ PaperImage: 一对多关系
- Tag ↔ Tag: 自关联，支持父子层级

#### 6.1.2 向量数据库（ChromaDB）

**Collection: papers**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String | 格式：`paper_{paper_id}_chunk_{chunk_index}` |
| document | String | 文本块内容（约1000字符） |
| embedding | Vector | 向量表示（自动生成） |
| metadata | JSON | `{paper_id: int, chunk_index: int}` |

**索引策略**:
- 按 paper_id 过滤：支持单篇论文检索
- 全局检索：不使用过滤条件

### 6.2 文件存储结构

```
data/
├── papers/                          # PDF文件存储
│   ├── paper_1.pdf
│   ├── paper_2.pdf
│   └── ...
├── images/                          # 图片存储
│   ├── 1/                          # paper_id = 1
│   │   ├── page1_img0.png
│   │   ├── page3_img1.jpg
│   │   └── user_upload_1234567890.png
│   ├── 2/
│   └── ...
├── paperbrain.db                    # SQLite数据库
└── chroma_db/                       # ChromaDB向量数据库
    ├── chroma.sqlite3
    └── ...
```

### 6.3 数据流转

#### 6.3.1 写入流程

```
用户操作 → 业务逻辑层 → 数据访问层 → 数据存储层

示例：上传论文
1. 用户上传PDF → upload_page.py
2. 保存文件 → 文件系统 (data/papers/)
3. 解析PDF → pdf_parser.py
4. 生成总结 → summarizer.py → LLM API
5. 保存论文 → db_manager.create_paper() → SQLite
6. 生成标签 → tagger.py → LLM API
7. 保存标签 → db_manager.save_tags() → SQLite
8. 向量化 → rag_service.add_paper_to_vector_db() → ChromaDB
```

#### 6.3.2 读取流程

```
用户请求 → 数据访问层 → 数据存储层 → 业务逻辑层 → 用户界面

示例：查看论文详情
1. 用户点击"查看详情" → dashboard.py
2. 获取论文 → db_manager.get_paper_by_id() → SQLite
3. 获取标签 → 通过关联表查询 → SQLite
4. 获取图片 → db_manager.get_paper_images() → SQLite
5. 渲染页面 → paper_detail.py
```

### 6.4 数据一致性保证

#### 6.4.1 级联删除

删除论文时，自动删除关联数据：
- PaperTag 记录（通过 SQLAlchemy cascade）
- PaperImage 记录（通过 SQLAlchemy cascade）
- PDF 文件（手动删除）
- 图片文件夹（手动删除）
- ChromaDB 向量（手动删除）

实现代码：
```python
def delete_paper(self, paper_id: int) -> bool:
    paper = session.query(Paper).filter(Paper.id == paper_id).first()
    if paper:
        # 1. 删除PDF文件
        if Path(paper.file_path).exists():
            Path(paper.file_path).unlink()
        # 2. 删除图片文件夹
        image_dir = Path(config.IMAGES_DIR) / str(paper_id)
        if image_dir.exists():
            shutil.rmtree(image_dir)
        # 3. 删除向量数据
        rag_service.delete_paper_vectors(paper_id)
        # 4. 删除数据库记录（级联删除关联表）
        session.delete(paper)
        session.commit()
        return True
    return False
```

#### 6.4.2 事务管理

使用 SQLAlchemy Session 管理事务：
- 所有数据库操作在 try-except-finally 块中
- 异常时自动回滚
- 成功时提交事务

---

## 7. 非功能性需求

### 7.1 性能要求

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 论文处理时间 | < 3分钟 | 从上传到完成向量化 |
| 页面加载时间 | < 2秒 | 主页和详情页首次加载 |
| 搜索响应时间 | < 500ms | 全文搜索和标签筛选 |
| 对话响应时间 | < 5秒 | RAG检索 + LLM生成 |
| 并发用户数 | 1-5 | 单实例支持的并发用户 |
| 数据库查询 | < 100ms | 单次查询响应时间 |
| 向量检索 | < 2秒 | ChromaDB Top-K检索 |

**性能优化策略**:
- 文本截断：LLM输入限制在30K字符
- 懒加载：图片按需加载
- 缓存：Session State缓存常用数据
- 索引：数据库关键字段建立索引
- 批处理：未来支持批量上传时使用异步处理

### 7.2 可用性要求

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 系统可用性 | 99% | 本地部署，依赖用户环境 |
| 错误恢复 | < 1分钟 | 重启应用恢复正常 |
| 数据备份 | 手动 | 用户自行备份 data/ 目录 |
| 故障容错 | 降级服务 | LLM失败时提供基础功能 |

**容错机制**:
- LLM调用失败：重试3次，间隔2秒
- PDF解析失败：保存原文件，标记待处理
- 思维导图生成失败：使用简化模板
- 向量化失败：标记 embedding_status=False，后续可重试

### 7.3 安全性要求

| 维度 | 要求 | 实现方式 |
|------|------|----------|
| 数据隐私 | 本地存储 | 所有数据存储在用户本地，不上传云端 |
| API密钥 | 环境变量 | 使用 .env 文件，不提交到代码库 |
| 文件上传 | 格式验证 | 仅允许PDF格式，大小限制50MB |
| SQL注入 | ORM防护 | 使用SQLAlchemy参数化查询 |
| XSS攻击 | 输入转义 | Streamlit自动转义用户输入 |

**安全最佳实践**:
- .env 文件加入 .gitignore
- 提供 .env.example 模板
- 文档中提醒用户保护API密钥
- 定期更新依赖库，修复安全漏洞

### 7.4 可维护性要求

| 维度 | 要求 | 实现方式 |
|------|------|----------|
| 代码规范 | PEP 8 | 使用 black/flake8 格式化 |
| 文档完整性 | 100% | README + CLAUDE.md + PRD |
| 模块化 | 高内聚低耦合 | 按功能划分模块 |
| 可测试性 | 单元测试覆盖 | 核心逻辑编写测试（未来） |
| 日志记录 | 关键操作 | 使用 logging 模块 |

**代码组织原则**:
- 单一职责：每个模块只负责一个功能
- 依赖注入：通过参数传递依赖
- 配置分离：所有配置集中在 config.py
- Prompt分离：所有Prompt集中在 utils/prompts.py

### 7.5 可扩展性要求

| 维度 | 要求 | 实现方式 |
|------|------|----------|
| 数据库迁移 | 支持 | SQLAlchemy支持多种数据库 |
| LLM切换 | 支持 | 抽象LLM接口，易于替换 |
| 新功能添加 | 模块化 | 新功能独立模块，不影响现有功能 |
| 多语言支持 | 预留 | 国际化框架（未来） |

**扩展点设计**:
- LLM Service：抽象接口，支持切换到OpenAI/Claude等
- 数据库：通过SQLAlchemy ORM，支持迁移到PostgreSQL
- 向量数据库：抽象RAG接口，支持切换到Pinecone等
- UI框架：未来可迁移到Flask + React

---

## 8. 产品路线图

### 8.1 已完成功能（v1.0）

**核心功能**:
- ✅ PDF上传与解析
- ✅ 结构化总结生成（8维度）
- ✅ 思维导图生成（Mermaid.js）
- ✅ 智能标签系统（三维度 + 层级）
- ✅ 图片提取与管理
- ✅ RAG对话问答（全局 + @mention）
- ✅ 论文检索与筛选
- ✅ 内容编辑功能
- ✅ 标签管理（层级、重复检测、合并）

**技术优化**:
- ✅ Session State防止重复上传
- ✅ SQLAlchemy Session分离问题修复
- ✅ 思维导图配色优化
- ✅ 相关工作MECE组织
- ✅ 标题层级规范（五级标题）

### 8.2 短期规划（v1.1 - v1.3，3个月）

**v1.1（1个月）**:
- 🔄 批量上传功能
  - 支持一次上传多个PDF
  - 后台队列处理
  - 进度追踪
- 🔄 导出功能
  - 导出结构化笔记为Markdown
  - 导出思维导图为PNG/SVG
  - 批量导出多篇论文
- 🔄 性能优化
  - 分页加载（每页20篇）
  - 图片缩略图生成
  - 数据库查询优化

**v1.2（2个月）**:
- 🔄 高级搜索
  - 按日期范围筛选
  - 按作者筛选
  - 组合条件搜索
- 🔄 笔记增强
  - 支持用户自定义章节
  - 支持添加个人批注
  - 版本历史记录
- 🔄 标签增强
  - 标签别名（同义词）
  - 标签推荐（基于已有论文）
  - 标签统计分析

**v1.3（3个月）**:
- 🔄 数据备份与恢复
  - 一键备份所有数据
  - 导入/导出数据库
  - 云端同步（可选）
- 🔄 用户设置
  - LLM参数自定义（Temperature, Max Tokens）
  - UI主题切换（亮色/暗色）
  - 快捷键配置

### 8.3 中期规划（v2.0 - v2.5，6-12个月）

**v2.0（6个月）**:
- 📋 引用关系图谱
  - 解析论文引用关系
  - 可视化引用网络（D3.js/Cytoscape）
  - 发现关键论文和研究脉络
- 📋 多语言支持
  - 英文论文优化
  - 中文论文支持
  - 自动语言检测

**v2.1（8个月）**:
- 📋 协作功能
  - 多用户支持
  - 论文分享
  - 评论和讨论
- 📋 移动端适配
  - 响应式设计
  - 移动端优化布局
  - PWA支持

**v2.2（10个月）**:
- 📋 集成文献管理工具
  - Zotero集成
  - Mendeley集成
  - BibTeX导入/导出
- 📋 自动文献综述生成
  - 基于多篇论文生成综述
  - 自动引用格式化
  - 研究趋势分析

**v2.3（12个月）**:
- 📋 API接口
  - RESTful API
  - 第三方集成
  - Webhook支持
- 📋 插件系统
  - 自定义Prompt模板
  - 自定义处理流程
  - 社区插件市场

### 8.4 长期规划（v3.0+，1-2年）

**v3.0（18个月）**:
- 📋 科研社区
  - 用户注册与登录
  - 论文公开分享
  - 关注和订阅
  - 热门论文推荐
- 📋 智能推荐
  - 基于阅读历史推荐论文
  - 相似论文发现
  - 研究方向建议

**v3.1（24个月）**:
- 📋 高级分析
  - 研究趋势分析
  - 作者影响力分析
  - 领域热点追踪
- 📋 自动化工作流
  - 定期抓取最新论文
  - 自动分类和标签
  - 邮件摘要推送

---

## 9. 风险与挑战

### 9.1 技术风险

| 风险 | 影响 | 概率 | 应对策略 |
|------|------|------|----------|
| LLM API不稳定 | 高 | 中 | 重试机制 + 降级服务 + 支持多个LLM提供商 |
| PDF解析失败 | 中 | 中 | 多种解析库备选 + 人工处理通道 |
| 向量数据库性能瓶颈 | 中 | 低 | 数据分片 + 迁移到专业向量数据库 |
| Streamlit性能限制 | 高 | 高 | 优化代码 + 未来迁移到Flask/FastAPI |
| 数据库文件损坏 | 高 | 低 | 定期备份 + 数据恢复工具 |

### 9.2 产品风险

| 风险 | 影响 | 概率 | 应对策略 |
|------|------|------|----------|
| 用户需求不明确 | 高 | 中 | 快速迭代 + 用户反馈 + MVP验证 |
| 竞品压力 | 中 | 高 | 差异化定位 + 深度功能 + 开源社区 |
| 用户留存率低 | 高 | 中 | 优化体验 + 增加粘性功能 + 数据导出 |
| 功能复杂度过高 | 中 | 中 | 简化UI + 新手引导 + 文档完善 |

### 9.3 运营风险

| 风险 | 影响 | 概率 | 应对策略 |
|------|------|------|----------|
| API成本过高 | 中 | 中 | 优化Prompt + 缓存结果 + 支持本地模型 |
| 用户数据隐私 | 高 | 低 | 本地部署 + 数据加密 + 隐私政策 |
| 开源协议冲突 | 中 | 低 | 审查依赖库协议 + 选择MIT/Apache协议 |
| 技术支持压力 | 中 | 中 | 完善文档 + FAQ + 社区论坛 |

### 9.4 应对措施

**技术层面**:
1. 建立完善的错误处理和日志系统
2. 定期备份数据，提供恢复工具
3. 性能监控和优化
4. 代码审查和测试

**产品层面**:
1. 快速迭代，及时响应用户反馈
2. 保持核心功能简单易用
3. 提供详细的使用文档和视频教程
4. 建立用户社区，收集需求

**运营层面**:
1. 控制API调用成本，优化Prompt
2. 提供本地模型支持（未来）
3. 开源项目，吸引社区贡献
4. 建立可持续的商业模式（企业版）

---

## 10. 附录

### 10.1 术语表

| 术语 | 英文 | 说明 |
|------|------|------|
| RAG | Retrieval-Augmented Generation | 检索增强生成，结合向量检索和LLM生成 |
| LLM | Large Language Model | 大语言模型，如GPT、Gemini、Claude |
| Embedding | - | 向量化表示，将文本转换为高维向量 |
| MECE | Mutually Exclusive, Collectively Exhaustive | 相互独立、完全穷尽，分类原则 |
| ORM | Object-Relational Mapping | 对象关系映射，如SQLAlchemy |
| Mermaid.js | - | JavaScript图表库，支持流程图、思维导图等 |
| ChromaDB | - | 开源向量数据库，支持本地部署 |
| Session State | - | Streamlit会话状态管理机制 |

### 10.2 参考资料

**技术文档**:
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [Mermaid.js Documentation](https://mermaid.js.org/)

**相关论文**:
- Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (Lewis et al., 2020)
- Dense Passage Retrieval for Open-Domain Question Answering (Karpukhin et al., 2020)

**竞品分析**:
- Zotero: 开源文献管理工具
- Mendeley: 学术社交网络 + 文献管理
- Notion AI: 通用知识管理 + AI助手
- Elicit: AI驱动的文献综述工具

### 10.3 开发规范

**代码规范**:
- 遵循 PEP 8 Python代码风格
- 使用 black 自动格式化
- 使用 flake8 进行代码检查
- 函数和类添加 docstring

**Git规范**:
- 分支命名：feature/功能名、bugfix/问题描述
- Commit信息：[类型] 简短描述（如 [feat] 添加批量上传功能）
- PR模板：包含功能描述、测试说明、截图

**文档规范**:
- README.md：项目介绍、安装步骤、使用指南
- CLAUDE.md：开发指南、架构说明、常见问题
- PRD.md：产品需求文档（本文档）
- API文档：未来提供API时编写

**测试规范**:
- 单元测试：核心业务逻辑
- 集成测试：数据库操作、API调用
- E2E测试：关键用户流程（未来）
- 测试覆盖率目标：>80%（未来）

### 10.4 联系方式

**项目地址**: [GitHub Repository URL]
**问题反馈**: [GitHub Issues URL]
**讨论社区**: [Discord/Slack URL]
**邮箱**: [Contact Email]

---

**文档结束**

本PRD文档将持续更新，记录产品演进过程。所有重大功能变更和技术决策都应在此文档中体现。

