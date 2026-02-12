"""
从 PDF 中提取 venue 和 institutions 信息
通过解析论文前几页的页眉、作者信息等
"""
import fitz  # PyMuPDF
import requests
import sys
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.doubao_service import doubao_service


def download_arxiv_pdf_stream(arxiv_id: str) -> Optional[bytes]:
    """
    从 arXiv 流式下载 PDF（不保存到磁盘）

    Args:
        arxiv_id: ArXiv ID (如 2602.11057 或 2602.11057v1)

    Returns:
        PDF 二进制数据，失败返回 None
    """
    # 清理 arxiv_id（移除版本号）
    clean_id = arxiv_id.replace('v1', '').replace('v2', '').replace('v3', '')

    # arXiv PDF URL
    pdf_url = f"https://arxiv.org/pdf/{clean_id}.pdf"

    try:
        print(f"  📥 下载 PDF 前几页: {pdf_url}")
        # 使用流式下载，只下载前 500KB（通常足够前 3 页）
        response = requests.get(pdf_url, timeout=30, stream=True)

        if response.status_code == 200:
            # 只读取前 500KB
            max_size = 500 * 1024  # 500KB
            pdf_data = b''

            for chunk in response.iter_content(chunk_size=8192):
                pdf_data += chunk
                if len(pdf_data) >= max_size:
                    break

            response.close()
            return pdf_data
        else:
            print(f"  ❌ 下载失败: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"  ❌ 下载异常: {str(e)}")
        return None


def extract_first_pages_text(pdf_data: bytes, num_pages: int = 3) -> str:
    """
    从 PDF 二进制数据中提取前几页的文本（包含页眉、页脚、作者信息）

    Args:
        pdf_data: PDF 二进制数据
        num_pages: 提取的页数

    Returns:
        前几页的文本内容
    """
    try:
        # 直接从内存中打开 PDF
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        text_parts = []

        for page_num in range(min(num_pages, len(doc))):
            page = doc[page_num]

            # 提取页面文本
            page_text = page.get_text()
            text_parts.append(f"=== 第 {page_num + 1} 页 ===\n{page_text}\n")

        doc.close()
        return "\n".join(text_parts)

    except Exception as e:
        print(f"  ❌ PDF 解析失败: {str(e)}")
        return ""


def extract_venue_institutions_from_pdf(pdf_text: str) -> Dict:
    """
    使用 LLM 从 PDF 文本中提取 venue 和 institutions

    Args:
        pdf_text: PDF 前几页的文本

    Returns:
        {'venue': str, 'venue_year': int, 'institutions': [str]}
    """
    prompt = f"""请从以下论文的前几页文本中提取会议/期刊信息和作者机构信息。

**提取规则**：

1. **会议/期刊 (venue)**：
   - 查找页眉、页脚中的发表信息，常见格式：
     * "Published as a conference paper at ICLR 2026"
     * "Proceedings of NeurIPS 2025"
     * "CVPR 2024"
     * "Accepted to ICML 2026"
   - 只提取顶级会议/期刊的标准缩写：NeurIPS, ICML, ICLR, CVPR, AAAI, IJCAI, ACL, EMNLP, KDD, WWW, SIGIR, RecSys, INFORMS Journal on Computing, Operations Research, Transportation Research Part C 等
   - 如果没有找到，返回空字符串

2. **年份 (venue_year)**：
   - 从会议/期刊信息中提取年份（如 2026, 2025）
   - 如果没有找到，返回 null

3. **作者机构 (institutions)**：
   - 从标题下方的作者列表中提取机构信息
   - 常见格式：
     * "Author Name¹, Author Name²"
     * "¹MIT, ²Stanford University"
     * "Author Name (MIT)"
   - 只提取知名机构：
     * 顶级大学：MIT, Stanford, Berkeley, CMU, Harvard, Oxford, Cambridge, Tsinghua, Peking, NUS, ETH, EPFL 等
     * 知名公司：Google, OpenAI, Meta, Microsoft, ByteDance, Alibaba, Tencent, Baidu, DeepMind 等
   - 使用标准全称或常用缩写
   - 如果没有找到，返回空列表

**输出格式（仅输出有效的 JSON）**：
{{
  "venue": "会议/期刊缩写（如 ICLR）或空字符串",
  "venue_year": 年份（整数）或 null,
  "institutions": ["机构1", "机构2", ...]
}}

**论文文本**：
{pdf_text[:4000]}

请仅输出 JSON，不要有其他文本。"""

    try:
        result = doubao_service.generate_json(prompt, temperature=0.1)

        # 验证结果
        if not isinstance(result, dict):
            return {'venue': '', 'venue_year': None, 'institutions': []}

        return {
            'venue': result.get('venue', ''),
            'venue_year': result.get('venue_year'),
            'institutions': result.get('institutions', [])
        }

    except Exception as e:
        print(f"  ❌ LLM 提取失败: {str(e)}")
        return {'venue': '', 'venue_year': None, 'institutions': []}


def extract_from_arxiv_pdf(arxiv_id: str) -> Tuple[str, Optional[int], list]:
    """
    从 arXiv PDF 中提取 venue 和 institutions

    注意：此函数不会保存 PDF 到磁盘，所有操作在内存中完成

    Args:
        arxiv_id: ArXiv ID

    Returns:
        (venue, venue_year, institutions)
    """
    # 流式下载 PDF 前几页（不保存到磁盘）
    pdf_data = download_arxiv_pdf_stream(arxiv_id)

    if not pdf_data:
        return '', None, []

    # 从内存中提取前几页文本
    print(f"  📄 解析 PDF 前 3 页...")
    pdf_text = extract_first_pages_text(pdf_data, num_pages=3)

    if not pdf_text:
        return '', None, []

    # 使用 LLM 提取信息
    print(f"  🤖 使用 LLM 提取 venue 和 institutions...")
    result = extract_venue_institutions_from_pdf(pdf_text)

    return result['venue'], result['venue_year'], result['institutions']


if __name__ == '__main__':
    # 测试
    test_arxiv_id = '2602.11057'
    print(f"测试提取: {test_arxiv_id}")
    print("=" * 60)

    venue, year, institutions = extract_from_arxiv_pdf(test_arxiv_id)

    print("\n" + "=" * 60)
    print("提取结果:")
    print("=" * 60)
    print(f"Venue: {venue or '未找到'}")
    print(f"Year: {year or '未找到'}")
    print(f"Institutions: {institutions or '未找到'}")
