"""
Obsidian 导出服务
将论文结构化笔记、思维导图和元数据导出为 Obsidian Markdown 格式
"""
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def sanitize_filename(title: str) -> str:
    """清理文件名中的非法字符"""
    # 替换 Windows/macOS/Linux 文件名非法字符
    sanitized = re.sub(r'[/\\:*?"<>|]', '-', title)
    # 压缩连续空格和破折号
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    sanitized = re.sub(r'-{2,}', '-', sanitized)
    # 限制长度（避免路径过长）
    return sanitized[:200] if len(sanitized) > 200 else sanitized


def generate_obsidian_md(paper, tags: list) -> str:
    """
    生成 Obsidian Markdown 字符串
    格式：YAML frontmatter + Markdown 正文
    """
    # ---- YAML frontmatter ----
    title_escaped = paper.title.replace('"', '\\"')
    authors_yaml = (
        "\n".join(f'  - "{a}"' for a in paper.authors)
        if paper.authors else "  []"
    )
    date_str = (
        paper.upload_date.strftime('%Y-%m-%d')
        if hasattr(paper, 'upload_date') and paper.upload_date
        else datetime.now().strftime('%Y-%m-%d')
    )
    tag_names = [t.name for t in tags] if tags else []
    tags_yaml = (
        "\n".join(f'  - {t}' for t in tag_names)
        if tag_names else "  []"
    )

    frontmatter = f"""---
title: "{title_escaped}"
authors:
{authors_yaml}
date: {date_str}
tags:
{tags_yaml}
source: paperbrain
---"""

    # ---- 正文 ----
    lines = [frontmatter, "", f"# {paper.title}", ""]

    # 一句话摘要
    summary_struct = None
    if paper.content_summary and 'summary_struct' in paper.content_summary:
        summary_struct = paper.content_summary['summary_struct']

    one_sentence = (
        paper.content_summary.get('one_sentence_summary', '')
        if paper.content_summary else ''
    )
    if one_sentence:
        lines += [f"> {one_sentence}", ""]

    # 8 维结构化摘要
    if summary_struct:
        section_map = [
            ('problem_definition',    '## 🎯 研究问题'),
            ('existing_solutions',    '## 📚 相关工作'),
            ('limitations',           '## ⚠️ 现有方案的不足'),
            ('contribution',          '## 💡 本文贡献'),
            ('methodology',           '## 🔬 具体方法'),
            ('results',               '## 📊 实验结果'),
            ('future_work_paper',     '## 🔮 未来工作（论文提出）'),
            ('future_work_insights',  '## 💭 未来工作（个人见解）'),
            # 兼容旧版字段
            ('future_work',           '## 🔮 未来工作'),
        ]
        for key, heading in section_map:
            content = summary_struct.get(key, '').strip()
            if content:
                lines += [heading, "", content, ""]
    else:
        lines += ["*暂无结构化笔记*", ""]

    # 思维导图
    if paper.mindmap_code:
        lines += [
            "## 🗺️ 思维导图",
            "",
            "```mermaid",
            paper.mindmap_code.strip(),
            "```",
            "",
        ]

    return "\n".join(lines)


def export_paper_to_obsidian(
    paper,
    tags: list,
    vault_path: str,
    sub_dir: str = "Papers",
) -> str:
    """
    将论文导出为 Obsidian Markdown 文件

    Args:
        paper: Paper 数据库对象
        tags: 标签列表
        vault_path: Obsidian vault 根目录路径
        sub_dir: vault 内的子目录名（默认 "Papers"）

    Returns:
        写入的文件绝对路径字符串

    Raises:
        ValueError: vault 路径不存在时
        IOError: 写入失败时
    """
    vault = Path(vault_path).expanduser()
    if not vault.exists():
        raise ValueError(f"Obsidian vault 路径不存在: {vault_path}")

    target_dir = vault / sub_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = sanitize_filename(paper.title) + ".md"
    file_path = target_dir / filename

    md_content = generate_obsidian_md(paper, tags)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    return str(file_path)
