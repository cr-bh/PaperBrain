"""
Obsidian 导出服务
将论文结构化笔记、思维导图和元数据导出为 Obsidian Markdown 格式
"""
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# 节点文字视觉宽度上限（中文字符算2，ASCII算1）
_NODE_VISUAL_WIDTH_MAX = 28


def _visual_width(text: str) -> int:
    """计算字符串的视觉宽度（中文/全角算2，其余算1）"""
    return sum(2 if ord(c) > 127 else 1 for c in text)


def _wrap_node_text(text: str, max_visual: int = _NODE_VISUAL_WIDTH_MAX) -> str:
    """
    将节点文字按视觉宽度折行，插入 <br/>。
    - 先把已有的 \n 替换为 <br/>
    - 再对每段按视觉宽度折行，优先在空格/中文标点处断开
    """
    # 统一换行符
    text = text.replace('\\n', '\n').replace('\r\n', '\n')
    segments = text.split('\n')
    result_lines = []

    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if _visual_width(seg) <= max_visual:
            result_lines.append(seg)
            continue

        # 按视觉宽度逐字切分
        current = ""
        current_w = 0
        for ch in seg:
            ch_w = 2 if ord(ch) > 127 else 1
            if current_w + ch_w > max_visual:
                # 尝试在最近的断点回退
                break_chars = ' ，、；：（('
                bp = -1
                for bc in break_chars:
                    pos = current.rfind(bc)
                    if pos > len(current) // 3:  # 断点不能太靠前
                        bp = pos
                        break
                if bp > 0:
                    result_lines.append(current[:bp + 1].rstrip())
                    current = current[bp + 1:].lstrip() + ch
                    current_w = _visual_width(current)
                else:
                    result_lines.append(current)
                    current = ch
                    current_w = ch_w
            else:
                current += ch
                current_w += ch_w
        if current.strip():
            result_lines.append(current.strip())

    return "<br/>".join(result_lines)


def _process_mermaid_for_obsidian(mermaid_code: str) -> str:
    """
    对 Mermaid 代码做 Obsidian 适配：节点文字超长时自动折行（插入 <br/>）。
    支持 ["文字"] 格式的节点。
    """
    def replace_node_text(m: re.Match) -> str:
        original_text = m.group(1)
        wrapped = _wrap_node_text(original_text)
        if wrapped == original_text:
            return m.group(0)
        return f'["{wrapped}"]'

    # 匹配 ["任意文字（含换行）"] 节点
    processed = re.sub(
        r'\["([^"]+)"\]',
        replace_node_text,
        mermaid_code,
        flags=re.DOTALL,
    )
    return processed


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
        processed_mindmap = _process_mermaid_for_obsidian(paper.mindmap_code.strip())
        lines += [
            "## 🗺️ 思维导图",
            "",
            "```mermaid",
            "%%{init: {'theme': 'default', 'flowchart': {'useMaxWidth': false, 'rankSpacing': 80, 'nodeSpacing': 40}}}%%",
            processed_mindmap,
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
