# Auto-Scholar 使用指南

## 功能概述

Auto-Scholar 是 PaperBrain 的智能论文监控系统，自动从 Arxiv 抓取、评分和推荐论文。

## 快速开始

### 1. 启动应用

```bash
streamlit run app.py
```

### 2. 配置关键词

1. 点击侧边栏 **🤖 Auto-Scholar** 按钮
2. 切换到 **⚙️ 关键词设置** 标签页
3. 点击 **🚀 初始化默认关键词** 或手动添加关键词
   - **核心关键词 (Core)**: 运筹学、强化学习等核心领域
   - **前沿关键词 (Frontier)**: Agent Memory、LLM Memory 等前沿方向

### 3. 抓取论文

1. 切换到 **📊 论文列表** 标签页
2. 点击 **🚀 立即抓取** 按钮
3. 等待抓取和评分完成（约 1-2 分钟）

### 4. 查看结果

论文按分数分级：
- **S级 (9-10分)**: Must Read - 核心相关，必读
- **A级 (7-8分)**: Highly Relevant - 高度相关
- **B级 (5-6分)**: Relevant - 相关
- **C级 (<5分)**: 不显示

## 定时自动抓取

### Linux/Mac (cron)

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天早上 8 点执行）
0 8 * * * cd /path/to/paperbrain && python scripts/daily_fetch.py >> logs/daily_fetch.log 2>&1
```

### Windows (任务计划程序)

1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器: 每天早上 8:00
4. 操作: 启动程序
   - 程序: `python`
   - 参数: `scripts/daily_fetch.py`
   - 起始于: `C:\path\to\paperbrain`

## 评分标准

### S级 (9-10分)
- OR 深度: 核心 OR 问题（VRP、TSP、Scheduling）
- 技术前沿: 神经组合优化、端到端优化
- 工业价值: 可直接应用于实际场景

### A级 (7-8分)
- OR 深度: 涉及 OR 方法但非核心
- 技术前沿: 使用 RL/LLM 但非突破性
- 工业价值: 有应用潜力

### B级 (5-6分)
- OR 深度: 轻度相关
- 技术前沿: 常规方法
- 工业价值: 理论研究为主

### 加分项
- End-to-end Optimization (+1-2分)
- Neural Combinatorial Optimization (+1-2分)
- Retrieval-Augmented RL (+0.5-1分)
- Agent Memory/LLM Memory (+0.5-1分)

## 生成报告

定时脚本会自动生成 HTML 报告：
- 路径: `data/reports/daily_YYYYMMDD.html`
- 格式: 瀑布流布局，S/A/B 级分类
- 内容: 论文标题、分数、评分理由、标签

## 常见问题

### Q: 抓取失败怎么办？
A: 检查网络连接和 Arxiv API 可用性，脚本会自动重试 3 次。

### Q: 评分不准确？
A: 可以在 `utils/prompts.py` 中调整 `SCORE_PAPER_PROMPT` 的评分标准。

### Q: 如何修改抓取数量？
A: 修改 `config.py` 中的 `ARXIV_MAX_RESULTS` 参数（默认 200）。

### Q: 如何添加新的 Arxiv 类别？
A: 修改 `config.py` 中的 `ARXIV_CATEGORIES`（默认: cs.AI, cs.LG, cs.CL, math.OC）。

## API 成本估算

- 每篇论文评分: ~1000 tokens
- 100 篇论文: ~100K tokens
- 建议每日抓取量: 50-200 篇

## 技术架构

```
┌─────────────┐
│ Arxiv API   │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│ Crawler     │────▶│ Scoring      │
│ (关键词搜索) │     │ (LLM 评分)   │
└─────────────┘     └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Database     │
                    │ (ArxivPaper) │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Report Gen   │
                    │ (HTML 报告)  │
                    └──────────────┘
```

## 下一步

- [ ] 测试完整流水线
- [ ] 配置定时任务
- [ ] 调整评分标准（如需要）
- [ ] 实现分享卡片生成（P1 功能）
