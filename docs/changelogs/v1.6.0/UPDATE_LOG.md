# v1.6.0 更新日志

> **发布日期**: 2026-03-24
> **最后更新**: 2026-03-24
> **分支**: main-private → main

---

## ✨ 新增功能

### Obsidian 导出（v1.6.0 初版）

在论文详情页新增「📤 导出到 Obsidian」按钮，支持将论文结构化笔记一键导出为 Obsidian Markdown 文件。

**导出内容：**
- YAML frontmatter（标题、作者、日期、标签、来源）
- 一句话摘要
- 8 维结构化笔记（研究问题 / 相关工作 / 不足 / 贡献 / 方法 / 结果 / 未来工作 × 2）
- 思维导图 Mermaid 代码块（可选，见下）

**配置入口：** 设置页 → 「📁 Obsidian 集成」展开区块

详细说明请参考 [Obsidian 导出功能文档](../../features/OBSIDIAN_EXPORT.md)

---

## 🐛 Bug 修复 & 迭代优化

### 思维导图节点截断修复

**问题：** Obsidian Mermaid 渲染器对节点宽度有限制，节点文字过长时右侧内容被 clip 截断。

**修复：**
- 注入 `%%{init}%%` 指令：`useMaxWidth: false`、`rankSpacing: 80`、`nodeSpacing: 40`
- 新增 `_process_mermaid_for_obsidian()`：按视觉宽度（中文算2/ASCII算1）自动折行，插入 `<br/>`
- 统一处理 LLM 生成的 `\n` 换行符 → `<br/>`
- 优先在空格/中文标点处断行，不硬截单词

### 新增「包含思维导图」选项

**背景：** 思维导图折行后视觉效果大致可用但不完美，用户可自行决定是否导入。

**实现：**
- 导出按钮上方新增 checkbox「包含思维导图」，**默认不勾选**
- `generate_obsidian_md()` / `export_paper_to_obsidian()` 新增 `include_mindmap` 参数

---

## 📁 文件改动汇总

| 文件 | 操作 | 说明 |
|------|------|------|
| `services/obsidian_exporter.py` | 新建 | 核心导出逻辑，含折行处理 |
| `services/api_config.py` | 修改 | 新增 Obsidian 配置读写函数 |
| `ui/paper_detail.py` | 修改 | 新增导出按钮 + 思维导图 checkbox |
| `ui/settings.py` | 修改 | 新增 Obsidian 配置 UI |
| `docs/features/OBSIDIAN_EXPORT.md` | 新建/更新 | 功能文档 |
| `docs/changelogs/v1.6.0/UPDATE_LOG.md` | 本文件 | — |
