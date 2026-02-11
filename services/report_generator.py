"""
HTML 报告生成器
生成每日论文评分报告
"""
from datetime import datetime
from typing import List
from database.models import ArxivPaper
from pathlib import Path
import config


class ReportGenerator:
    """报告生成器"""

    def generate_daily_report(self, papers: List[ArxivPaper], date: datetime) -> str:
        """
        生成 HTML 日报

        Args:
            papers: 论文列表
            date: 日期

        Returns:
            报告文件路径
        """
        # 按分数分组
        s_papers = [p for p in papers if p.score >= 9]
        a_papers = [p for p in papers if 7 <= p.score < 9]
        b_papers = [p for p in papers if 5 <= p.score < 7]

        # 生成 HTML
        html = self._render_html(s_papers, a_papers, b_papers, date)

        # 保存文件
        report_dir = Path("data/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"daily_{date.strftime('%Y%m%d')}.html"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return str(report_path)

    def _render_html(self, s_papers, a_papers, b_papers, date):
        """渲染 HTML 模板"""
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto-Scholar 日报 - {date.strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               background: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .stats {{ display: flex; gap: 20px; margin-top: 20px; }}
        .stat-card {{ background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; flex: 1; }}
        .section {{ margin-bottom: 30px; }}
        .section-title {{ font-size: 24px; font-weight: bold; margin-bottom: 15px;
                          padding-left: 10px; border-left: 4px solid; }}
        .s-title {{ border-color: #e74c3c; color: #e74c3c; }}
        .a-title {{ border-color: #3498db; color: #3498db; }}
        .b-title {{ border-color: #95a5a6; color: #95a5a6; }}
        .paper-card {{ background: white; padding: 20px; border-radius: 8px;
                       margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .paper-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
        .paper-meta {{ color: #666; font-size: 14px; margin-bottom: 10px; }}
        .score-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px;
                        font-weight: bold; color: white; }}
        .score-s {{ background: #e74c3c; }}
        .score-a {{ background: #3498db; }}
        .score-b {{ background: #95a5a6; }}
        .tags {{ margin-top: 10px; }}
        .tag {{ display: inline-block; background: #ecf0f1; padding: 4px 10px;
                border-radius: 4px; font-size: 12px; margin-right: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Auto-Scholar 日报</h1>
            <p>📅 {date.strftime('%Y年%m月%d日')}</p>
            <div class="stats">
                <div class="stat-card">
                    <div style="font-size: 32px; font-weight: bold;">{len(s_papers)}</div>
                    <div>S级论文 (Must Read)</div>
                </div>
                <div class="stat-card">
                    <div style="font-size: 32px; font-weight: bold;">{len(a_papers)}</div>
                    <div>A级论文 (Highly Relevant)</div>
                </div>
                <div class="stat-card">
                    <div style="font-size: 32px; font-weight: bold;">{len(b_papers)}</div>
                    <div>B级论文 (Relevant)</div>
                </div>
            </div>
        </div>

        {self._render_section("🏆 S级论文 (Must Read)", s_papers, "s")}
        {self._render_section("📈 A级论文 (Highly Relevant)", a_papers, "a")}
        {self._render_section("📊 B级论文 (Relevant)", b_papers, "b")}
    </div>
</body>
</html>
"""
        return html

    def _render_section(self, title, papers, level):
        """渲染单个分数段"""
        if not papers:
            return ""

        cards = ""
        for paper in papers:
            tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in (paper.tags or [])])
            cards += f"""
            <div class="paper-card">
                <div class="paper-title">
                    <span class="score-badge score-{level}">{paper.score:.1f}分</span>
                    {paper.title_zh or paper.title}
                </div>
                <div class="paper-meta">
                    📝 {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}
                    | 🔗 arxiv.org/abs/{paper.arxiv_id}
                </div>
                <div style="color: #555; margin: 10px 0;">{paper.score_reason}</div>
                <div class="tags">{tags_html}</div>
            </div>
            """

        return f"""
        <div class="section">
            <div class="section-title {level}-title">{title}</div>
            {cards}
        </div>
        """


# 创建全局报告生成器实例
report_generator = ReportGenerator()
