# v1.6.0 更新日志

> **发布日期**: 2026-03-24
> **分支**: main-private → main

---

## ✨ 新增功能

### Obsidian 导出

在论文详情页新增「📤 导出到 Obsidian」按钮，支持将论文结构化笔记一键导出为 Obsidian Markdown 文件。

**导出内容：**
- YAML frontmatter（标题、作者、日期、标签、来源）
- 一句话摘要
- 8 维结构化笔记（研究问题 / 相关工作 / 不足 / 贡献 / 方法 / 结果 / 未来工作 × 2）
- 思维导图 Mermaid 代码块（Obsidian 原生支持渲染）

**配置入口：** 设置页 → 「📁 Obsidian 集成」展开区块

详细说明请参考 [Obsidian 导出功能文档](../../features/OBSIDIAN_EXPORT.md)

---

## 📁 文件改动

| 文件 | 操作 |
|------|------|
| `services/obsidian_exporter.py` | 新建 |
| `services/api_config.py` | 新增 Obsidian 配置读写函数 |
| `ui/paper_detail.py` | 新增导出按钮 |
| `ui/settings.py` | 新增 Obsidian 配置 UI |
| `docs/features/OBSIDIAN_EXPORT.md` | 新建功能文档 |
| `docs/changelogs/v1.6.0/UPDATE_LOG.md` | 本文件 |
