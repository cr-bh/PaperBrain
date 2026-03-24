# Obsidian 导出功能

> **版本**: 1.6.1
> **创建日期**: 2026-03-24
> **最后更新**: 2026-03-24
> **状态**: 已完成

---

## 功能概述

在论文详情页新增「📤 导出到 Obsidian」按钮，将结构化笔记（8 维摘要）、思维导图（Mermaid 代码）和论文元数据直接写入本地 Obsidian vault 目录，格式为 YAML frontmatter + Markdown 正文。

---

## 导出文件格式

```markdown
---
title: "Attention Is All You Need"
authors:
  - "Vaswani"
  - "Shazeer"
date: 2026-03-24
tags:
  - NLP
  - Transformer
source: paperbrain
---

# Attention Is All You Need

> 一句话摘要：提出 Transformer 架构，完全基于注意力机制，无需 RNN/CNN。

## 🎯 研究问题
...

## 📚 相关工作
...

## ⚠️ 现有方案的不足
...

## 💡 本文贡献
...

## 🔬 具体方法
...

## 📊 实验结果
...

## 🔮 未来工作（论文提出）
...

## 💭 未来工作（个人见解）
...

## 🗺️ 思维导图

​```mermaid
graph TD
...
​```
```

---

## 配置方法

1. 打开 PaperBrain → 点击左侧「⚙️ 设置」
2. 展开「📁 Obsidian 集成」区块
3. 填写 **Obsidian Vault 路径**（如 `/Users/yourname/Documents/MyVault`）
4. 填写**论文子目录名**（默认 `Papers`，不存在时自动创建）
5. 点击「🔍 验证路径」确认路径有效
6. 点击「💾 保存 Obsidian 配置」

---

## 使用方法

1. 打开任意一篇已有结构化笔记的论文详情页
2. 按需勾选「包含思维导图」（默认不勾选）
3. 点击右上角「📤 导出到 Obsidian」按钮
4. 导出成功后会显示文件的完整路径

---

## 边界情况处理

| 情况 | 处理方式 |
|------|---------|
| vault 路径未配置 | 提示用户前往设置页配置 |
| vault 路径不存在 | 显示错误信息，不崩溃 |
| 论文无结构化笔记 | 正文中显示"暂无结构化笔记"提示 |
| 论文无思维导图 | 跳过思维导图章节 |
| 未勾选「包含思维导图」 | 只导出结构化笔记，不含 Mermaid 代码块 |
| 文件名含特殊字符（`/ : * ? " < > \|`）| `sanitize_filename()` 替换为 `-` |
| 同名文件已存在 | 直接覆盖（幂等更新） |

---

## 文件改动

| 文件 | 操作 | 说明 |
|------|------|------|
| `services/obsidian_exporter.py` | 新建 | 核心导出逻辑 |
| `services/api_config.py` | 修改 | 新增 `get_obsidian_config()` / `save_obsidian_config()` |
| `ui/paper_detail.py` | 修改 | 新增导出按钮 |
| `ui/settings.py` | 修改 | 新增 Obsidian 配置 UI |

---

## 技术实现

### `services/obsidian_exporter.py`

- `sanitize_filename(title)` — 清理文件名非法字符，限制长度 200
- `generate_obsidian_md(paper, tags, include_mindmap)` — 生成完整 Markdown 字符串（可独立测试）
- `export_paper_to_obsidian(paper, tags, vault_path, sub_dir, include_mindmap)` — 写入文件，返回绝对路径
- `_process_mermaid_for_obsidian(code)` — 对 Mermaid 节点文字按视觉宽度自动折行（中文算2/ASCII算1），统一 `\n` → `<br/>`
- `_wrap_node_text(text)` — 单节点文字折行核心逻辑，优先在空格/中文标点处断开

### 配置持久化

Obsidian 配置存储在 `data/api_config.json` 的 `obsidian` 键下：

```json
{
  "obsidian": {
    "vault_path": "/Users/yourname/ObsidianVault",
    "sub_dir": "Papers",
    "enabled": true
  }
}
```

`data/api_config.json` 已在 `.gitignore` 中，不会提交到版本库。
