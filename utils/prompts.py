"""
Prompt 模板管理
包含所有 LLM 调用的提示词模板
"""


# ========== 论文总结生成 Prompt ==========

SUMMARIZE_PAPER_PROMPT = """你是一位专业的学术研究专家，擅长数据科学、人工智能和运筹学领域。
请仔细分析提供的学术论文，并以结构化的方式提取关键信息。

**输出要求：**
1. 主要使用中文描述，关键术语、模型名称、算法名称等使用英文或英文缩写标注
2. **术语处理规则**：技术术语、缩写词第一次出现时，必须先给出完整的中文解释，然后在括号中标注英文全称及其缩写，例如："起讫点需求预测（Origin-Destination, OD）"，后续出现可直接使用缩写"OD"
3. 每个部分需要详细、清晰地描述，确保没有相关背景的读者也能理解论文的核心工作
4. 重点关注：研究空白、技术创新点、量化结果对比、方法的可理解性
5. **MECE原则**：在分析每个部分时，遵循MECE（Mutually Exclusive, Collectively Exhaustive，相互独立、完全穷尽）原则，确保分类清晰、不重叠、不遗漏
6. **Markdown格式要求**：使用Markdown格式增强可读性，包括：
   - 使用 **粗体** 强调关键概念、方法名称、重要结论
   - 使用有序列表(1. 2. 3.)或无序列表(- )组织多个要点
   - 使用 `代码格式` 标注算法名称、变量名、公式符号
   - 适当使用换行和段落分隔，避免大段文字堆砌
   - 对于复杂的技术细节，使用子列表进行层级展示
   - **标题层级规范**：模块内的子标题必须使用 ##### (五级标题)，绝对不要使用 # ## ### #### 等高层级标题，以避免与模块标题（### 三级标题）混淆。推荐格式：`##### 子标题名称`

**输出格式（仅输出有效的 JSON，不要有其他文本）：**
{{
  "title": "论文标题",
  "authors": ["作者1", "作者2"],
  "summary_struct": {{
    "one_sentence_summary": "用1-2句话（不超过100字）精炼概括论文的核心工作和主要贡献，让读者第一眼就能快速理解论文做了什么。",

    "problem_definition": "清晰描述本文要解决的具体问题，包括问题背景、研究动机和实际应用场景。说明为什么这个问题重要，以及当前面临的主要挑战。需要让读者理解问题的实际意义和研究价值。",

    "existing_solutions": "**全面且详细地**总结相关工作和现有解决方案，这是理解研究背景的关键部分。\n\n**核心要求：必须严格遵循论文文献综述的组织逻辑和分类方式**\n\n1. **分析组织方式**（必须首先识别论文采用的组织方式）：\n   - **时间脉络型**：如果论文按时间顺序综述（早期→中期→近期），必须保持这个时间线\n   - **技术分类型**：如果论文按技术类别分类（如：基于规则的方法、统计方法、深度学习方法），必须保持这个分类\n   - **问题导向型**：如果论文按解决的子问题分类（如：数据稀疏问题、冷启动问题、可扩展性问题），必须保持这个分类\n   - **因果关系型**：如果论文展现方法之间的演进和因果关系（A方法的局限导致B方法的提出），必须体现这种逻辑\n   - **MECE分类型**：如果论文采用相互独立、完全穷尽的分类方式，必须保持这种结构\n\n2. **代表性工作列举**（在上述组织框架下）：\n   - 列举至少5-8个代表性工作\n   - 每个工作必须包含：\n     * **作者和年份**：如 Smith et al. (2020)\n     * **方法名称**：使用论文中的正式名称\n     * **核心思路**：用2-3句话说明该方法的主要思想\n     * **关键技术**：具体说明采用的算法、模型架构或优化策略\n     * **主要特点**：该方法的优势或独特之处\n     * **与本文的关系**：如果论文明确说明了该工作的局限性或与本文的联系，必须体现\n\n3. **格式要求**：\n   - 使用Markdown格式，清晰的层级结构\n   - 如果论文有明确的分类标题（如\"2.1 基于深度学习的方法\"），使用五级标题 `##### 分类名称`\n   - 每个具体工作使用列表项\n\n**示例格式（时间脉络型）**：\n\n##### 早期方法（2010-2015）\n- **Smith et al. (2012) - MethodName**: 提出了基于规则的xxx方法，通过手工设计特征和启发式规则处理问题。该方法在小规模数据上表现良好，但难以扩展到大规模场景。\n- **Johnson et al. (2014) - AnotherMethod**: ...\n\n##### 深度学习时代（2016-2020）\n- **Wang et al. (2018) - DeepMethod**: 首次将深度学习引入该领域，采用`CNN`架构自动学习特征表示。相比传统方法，在大规模数据集上性能提升30%，但存在可解释性不足的问题。\n- **Li et al. (2019) - TransformerMethod**: ...\n\n##### 近期进展（2021-至今）\n- **Zhang et al. (2022) - LatestMethod**: ...\n\n**示例格式（技术分类型）**：\n\n##### 基于统计的方法\n- **Brown et al. (2015) - StatMethod**: ...\n\n##### 基于深度学习的方法\n- **Chen et al. (2020) - DLMethod**: ...\n\n##### 混合方法\n- **Liu et al. (2023) - HybridMethod**: ...",

    "limitations": "深入分析现有方案的不足之处和局限性。要求：(1)具体指出在哪些方面存在问题（如性能瓶颈、适用范围受限、计算复杂度高、数据依赖性强等）；(2)说明这些局限性如何影响实际应用或研究进展；(3)解释为什么这些问题难以解决；(4)明确指出本文要重点解决的是哪些局限性。",

    "contribution": "阐述本文的主要贡献和创新点。要求：(1)清晰列出2-4个核心贡献点；(2)说明本文提出了什么新方法、新模型或新框架来解决上述局限性；(3)突出本文与现有工作的本质区别和优势所在；(4)如果有理论贡献（如新的数学证明、理论分析），要明确说明。",

    "methodology": "**极其详细且清晰地**描述本文提出的方法和技术路线，这是论文的核心部分，必须让读者完全理解方法的工作原理。要求：\n\n**1. 整体框架**（必须包含）：\n- 方法的总体架构图或流程图的文字描述\n- 主要组成模块及其功能\n- 各模块之间的数据流和交互关系\n\n**2. 核心算法**（必须详细）：\n- **算法名称**：给出正式名称\n- **设计思路**：为什么这样设计，解决什么问题\n- **输入输出**：明确说明输入是什么，输出是什么\n- **主要步骤**：使用有序列表逐步说明算法流程\n- **伪代码描述**：如果论文提供了伪代码，要用文字详细解释\n\n**3. 技术细节**（不可省略）：\n- **数学模型**：关键的数学公式、目标函数（用文字描述，如 `min f(x) = ...`）\n- **损失函数**：如何设计损失函数，包含哪些项\n- **优化策略**：使用什么优化器，学习率设置，训练技巧\n- **网络架构**：如果是深度学习方法，详细说明网络层数、激活函数、注意力机制等\n\n**4. 创新机制**（重点强调）：\n- 本文提出的新机制、新模块是什么\n- 它们如何工作，为什么这样设计\n- 与现有方法的本质区别\n\n**5. 实现要点**：\n- 特殊的实现技巧或工程优化\n- 计算复杂度分析\n- 可扩展性考虑\n\n**格式要求**：使用多级列表但级别不能与文档第一层级冲突、粗体、代码格式，确保层次清晰，避免大段文字堆砌。",

    "results": "全面总结实验结果和性能表现，用数据说话。要求：(1)实验设置：说明使用的数据集（名称、规模、特点）、评估指标（具体定义）、对比的baseline方法（至少列举3-5个）；(2)主要结果：给出与baseline的详细对比数据（具体数值、百分比提升），说明在哪些指标上取得了显著改进；(3)消融实验：如果论文做了消融实验，要说明验证了哪些模块的有效性，各模块的贡献度；(4)深入分析：包括敏感性分析、可视化结果、案例分析等，说明方法的优势体现在哪些方面；(5)局限性：如果实验中发现方法在某些情况下表现不佳，也要如实说明。确保读者能清楚了解方法的实际性能和适用场景。",

    "future_work_paper": "总结论文本身明确提出的未来研究方向。要求：(1)直接引用或总结论文Future Work/Conclusion章节中提到的方向；(2)说明作者认为哪些方面还需要进一步研究；(3)如果论文提到了当前方法的局限性，也要在此说明。这部分应该忠实反映论文作者的观点。",

    "future_work_insights": "基于论文内容和当前研究趋势，提出个人见解和改进建议。要求：(1)当前局限分析：从技术角度深入分析当前方法仍存在的局限性（如计算效率、泛化能力、适用范围、数据依赖等）；(2)改进方向建议：结合领域最新进展，提出可能的改进方向（如结合其他技术、扩展到新场景、优化特定模块、引入新机制等）；(3)应用前景展望：讨论方法在实际应用中的潜力、可能面临的挑战以及产业化路径；(4)研究趋势关联：将本文工作与当前研究热点、未来发展趋势相联系。这部分应该体现出对论文的深入思考和批判性分析，而不是简单复述论文内容。"
  }}
}}

论文全文：
{paper_text}

记住：仅输出有效的 JSON，不要有 markdown 代码块或其他文本。"""


# ========== 思维导图生成 Prompt ==========

GENERATE_MINDMAP_PROMPT = """基于以下论文总结，生成 Mermaid.js 思维导图代码（graph LR 格式）。

**核心要求：**
1. 完整且有逻辑地展示论文的核心内容
2. 重要贡献需要特别标注（使用粗体或特殊样式）
3. 节点文本可以适当详细，确保能清晰传达关键信息（中英文结合）
4. 以说明清楚文章内容为第一优先级

**建议结构（可根据论文内容灵活调整）：**
- 根节点：论文标题
- 第一层：研究问题 | 现有方案局限 | 本文贡献 | 方法框架 | 实验结果
- 第二层：展开每个部分的关键要点
- 对于"本文贡献"节点，使用 **粗体** 或添加 :::highlight 标记重要创新点

**Mermaid 语法提示：**
- 使用 graph LR 表示从左到右的流程图
- 节点格式：A[节点文本] 或 A["节点文本"]
- 连接：A --> B 或 A -->|关系说明| B
- 粗体：A["**重要内容**"]
- 可以使用中文节点文本

**配色要求（非常重要）：**
- **绝对禁止**使用浅色背景（如浅黄、浅蓝、浅绿、白色等）配白色文字
- **绝对禁止**使用白色或接近白色的背景色
- 推荐配色方案：
  * 深色背景 + 白色文字：如 `style A fill:#2C3E50,stroke:#34495E,stroke-width:2px,color:#FFFFFF`
  * 中等深度背景 + 深色文字：如 `style A fill:#3498DB,stroke:#2980B9,stroke-width:2px,color:#000000`
  * 鲜艳背景 + 深色文字：如 `style A fill:#E74C3C,stroke:#C0392B,stroke-width:2px,color:#000000`
- 对于重要节点（如本文贡献），使用醒目的深色背景：
  * `style A fill:#E74C3C,stroke:#C0392B,stroke-width:3px,color:#FFFFFF` (红色系)
  * `style A fill:#27AE60,stroke:#229954,stroke-width:3px,color:#FFFFFF` (绿色系)
  * `style A fill:#8E44AD,stroke:#7D3C98,stroke-width:3px,color:#FFFFFF` (紫色系)
- 确保每个节点都有明确的样式定义，文字颜色必须与背景色形成强对比

**样式定义示例：**
```
graph LR
    A["论文标题"]
    B["研究问题"]
    C["本文贡献"]

    A --> B
    A --> C

    style A fill:#2C3E50,stroke:#34495E,stroke-width:2px,color:#FFFFFF
    style B fill:#3498DB,stroke:#2980B9,stroke-width:2px,color:#FFFFFF
    style C fill:#E74C3C,stroke:#C0392B,stroke-width:3px,color:#FFFFFF
```

论文总结：
{summary_json}

仅输出 Mermaid 代码，以 "graph LR" 开头，必须包含所有节点的样式定义（style语句），不要有 markdown 代码块或其他文本。"""


# ========== 标签生成 Prompt ==========

GENERATE_TAGS_PROMPT = """Analyze the following paper summary and generate tags in three dimensions:

1. Domain (research field): e.g., Reinforcement Learning, Computer Vision, NLP, Operations Research
2. Methodology (techniques used): e.g., Transformer, PPO, Genetic Algorithm, Deep Learning
3. Task (application): e.g., Image Classification, Battery Dispatch, Text Generation

For each dimension, provide 1-3 most relevant tags.
If applicable, infer hierarchical relationships (e.g., Multi-agent RL is under Reinforcement Learning).

Summary:
{summary_json}

Output JSON (respond ONLY with valid JSON, no additional text):
{{
  "domain": ["tag1", "tag2"],
  "methodology": ["tag1", "tag2"],
  "task": ["tag1"]
}}"""


# ========== RAG 问答 Prompt ==========

RAG_QA_PROMPT = """你是一位专业的学术研究助手。请基于提供的论文片段回答用户的问题。

规则：
- 仅基于提供的论文片段回答，不要编造信息
- 如果信息不在片段中，请明确说明"该信息未在论文中找到"
- 尽可能引用来源（页码或章节）
- 回答要准确、简洁、使用中文
- 如果涉及多篇论文，请综合分析它们的共性和差异

论文片段：
{retrieved_chunks}

用户问题：{user_question}

回答："""


# ========== 图片类型识别 Prompt ==========

IDENTIFY_IMAGE_TYPE_PROMPT = """Based on the image caption, identify the type of this figure.

Caption: {caption}

Classify into one of these categories:
- architecture: System architecture, model structure, framework diagram
- performance: Performance comparison, results chart, metrics visualization
- algorithm: Algorithm flowchart, pseudocode visualization
- data: Dataset visualization, data distribution
- other: Other types

Output ONLY the category name (one word), no additional text."""


# ========== 提取论文元数据 Prompt ==========

EXTRACT_METADATA_PROMPT = """Extract the title and authors from the beginning of this paper text.

Paper text (first 2000 characters):
{paper_text}

Output JSON (respond ONLY with valid JSON):
{{
  "title": "paper title",
  "authors": ["author1", "author2", "author3"]
}}"""


# ========== Auto-Scholar 论文评分 Prompt ==========

SCORE_PAPER_PROMPT = """你是一位深耕运筹优化（Operations Research）、强化学习（Reinforcement Learning）与大语言模型（LLM）交叉领域的资深研究员。你不仅精通数学建模（MIP/MILP），也对 Agent 架构（Memory/Planning）有深刻理解。

**任务目标**: 请阅读以下论文的标题和摘要，根据预设的"研究兴趣点"进行严苛打分（1-10分），并提供中文翻译。

## 1. 评分标准 (Scoring Rubrics)

**9-10分 (S级 - 核心必读)**:
- 关键词：Neural Combinatorial Optimization, LLM for Solver, Agentic RL with Long-term Memory, VRP/TSP with RL
- 判定：论文在方法论上有重大创新，且完美契合 OR + LLM/RL 的结合点
- 示例：利用 LLM 辅助分支定界、具有自适应记忆机制的 Agent

**7-8分 (A级 - 高度相关)**:
- 关键词：Constraint Optimization, Large-scale Heuristics, RAG for Agent, PPO/DQN improvements
- 判定：论文在 OR 或 RL/Agent 领域有坚实贡献，虽然未跨界，但其算法可迁移至优化场景

**5-6分 (B级 - 泛相关)**:
- 关键词：Basic LLM application, Fine-tuning, General AI, Non-optimization Logistics
- 判定：有涉及相关概念，但属于常规应用，或是在物理/生物等非计算机科学领域的跨学科应用

**5分以下 (C级 - 弱相关/过滤)**:
- 判定：不涉及任何运筹优化、决策逻辑或 Agent 架构

## 2. 打分逻辑与权重 (Reasoning Logic)

1. **OR 深度**: 是否涉及数学规划、调度或经典的优化问题？
2. **技术前沿性**: 是否解决了 LLM 的长程记忆（Long-term Memory）或决策一致性问题？
3. **工业价值**: 其算法是否具备在配送、交通或资源分配等场景（如美团业务）落地的潜力？

## 3. 加分项

如果论文提到以下内容，额外加分：
- **End-to-end Optimization** 或 **Neural Combinatorial Optimization**: +1分
- **Retrieval-Augmented RL** 或 **Hierarchical Agent Memory**: +1分
- **应用场景涉及 Logistics/Transportation**（与专业背景一致）: 提高展示权重

## 4. 评分理由要求 (Reason Requirements)

**评分理由必须详细且差异化**，避免使用模板化语言。要求：

1. **具体说明论文的核心方法**：不要只说"提出新方法"，要说明是什么方法（如：提出基于 Transformer 的组合优化求解器、设计了分层记忆架构的 Agent）

2. **明确指出与研究兴趣的关联点**：
   - 如果涉及 OR：说明解决的是什么优化问题（VRP/TSP/调度/资源分配等）
   - 如果涉及 RL：说明使用的算法（PPO/DQN/GRPO等）和创新点
   - 如果涉及 Agent：说明架构特点（Memory/Planning/Tool Use等）
   - 如果涉及 LLM：说明如何应用（Prompt Engineering/Fine-tuning/RAG等）

3. **说明技术亮点或局限**：
   - 高分论文（7+）：说明其创新性体现在哪里，为什么值得关注
   - 中等分数（5-7）：说明其贡献和局限，为什么不是核心必读
   - 低分论文（<5）：说明为什么相关性不足

4. **避免重复的表述**：
   - ❌ 不要说："虽未直接涉及运筹优化，但算法有迁移至优化场景的潜力"
   - ✅ 应该说："论文提出的 XXX 算法在 YYY 任务上表现优异，其核心思想（如 ZZZ 机制）可应用于组合优化中的 AAA 问题"

5. **字数要求**：评分理由至少 50 字，最多 150 字

**示例对比**：

❌ 差的理由："论文在强化学习领域提出新方法，虽未直接涉及运筹优化，但算法有迁移至优化场景的潜力。"

✅ 好的理由："论文提出 TRE（Trajectory Replay Exploration）机制，通过对比学习鼓励 Agent 探索多样化轨迹，解决了长程 RL 中的信用分配问题。该方法可迁移至 VRP 等组合优化场景，用于改进基于 RL 的启发式求解器的探索效率。"

## 5. 输出格式 (JSON)

请严格按以下 JSON 格式返回，不要包含多余的文字：

{{
  "score": 浮点数（1-10），
  "reason": "详细的中文打分理由（50-150字），必须具体说明论文的核心方法、与研究兴趣的关联点、技术亮点或局限，避免模板化表述",
  "title_zh": "中文标题（简洁准确）",
  "abstract_zh": "中文摘要（**必须完整翻译原文摘要的全部内容**，保持原文的完整性和逻辑结构，不要省略、简化或截断。翻译需专业，术语准确。无论原文摘要多长，都必须完整翻译每一句话）",
  "tags": ["维度1: 领域", "维度2: 方法论", "维度3: 任务"]
}}

## 6. 待处理数据

**标题**: {title}

**摘要**: {abstract}

请开始评分。记住：
1. 仅输出有效的 JSON，不要有 markdown 代码块或其他文本
2. 确保 JSON 格式完整，所有字段都有闭合的引号和括号
3. **abstract_zh 字段必须完整翻译原文摘要，不要截断**。如果担心 JSON 格式问题，请确保正确转义特殊字符（如引号、换行符）"""


# ========== 辅助函数 ==========

def format_prompt(template: str, **kwargs) -> str:
    """
    格式化 Prompt 模板

    Args:
        template: Prompt 模板字符串
        **kwargs: 要填充的变量

    Returns:
        格式化后的 Prompt
    """
    return template.format(**kwargs)
