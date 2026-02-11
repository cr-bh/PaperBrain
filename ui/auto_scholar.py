"""
Auto-Scholar 页面
论文智能监控和评分系统
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from database.db_manager import db_manager
from services.scheduler import daily_scheduler


def show_auto_scholar():
    """显示 Auto-Scholar 页面"""
    st.title("🤖 Auto-Scholar 论文智能监控")

    # 创建 Tabs
    tab1, tab2, tab3 = st.tabs(["📊 论文列表", "⚙️ 关键词设置", "📈 统计分析"])

    with tab1:
        show_papers_list()

    with tab2:
        show_keyword_config()

    with tab3:
        show_statistics()


def show_papers_list():
    """显示论文列表"""
    st.markdown("### 📚 已抓取论文")

    # 时间范围选择
    st.markdown("#### ⏰ 抓取时间设置")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        fetch_mode = st.selectbox(
            "抓取模式",
            ["昨天", "自定义时间段"],
            key="fetch_mode"
        )

    start_date = None
    end_date = None

    if fetch_mode == "自定义时间段":
        with col2:
            start_date = st.date_input(
                "开始日期",
                value=datetime.now() - timedelta(days=30),
                key="start_date"
            )
        with col3:
            end_date = st.date_input(
                "结束日期",
                value=datetime.now(),
                key="end_date"
            )

        if start_date > end_date:
            st.error("⚠️ 开始日期不能晚于结束日期")
            return

    st.markdown("---")

    # 操作按钮
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("🚀 立即抓取", use_container_width=True):
            with st.spinner("正在抓取和评分论文..."):
                try:
                    if fetch_mode == "自定义时间段":
                        # 转换为 datetime
                        start_dt = datetime.combine(start_date, datetime.min.time())
                        end_dt = datetime.combine(end_date, datetime.max.time())
                        daily_scheduler.run_daily_pipeline(
                            max_results=200,
                            start_date=start_dt,
                            end_date=end_dt
                        )
                    else:
                        daily_scheduler.run_daily_pipeline(max_results=50)
                    st.success("✅ 抓取完成！")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 抓取失败: {str(e)}")

    with col2:
        if st.button("📄 导出报告", use_container_width=True):
            from services.report_generator import report_generator
            papers = db_manager.get_all_arxiv_papers(limit=500, min_score=5.0)
            if papers:
                report_path = report_generator.generate_daily_report(papers, datetime.now())
                st.success(f"✅ 报告已生成: {report_path}")
            else:
                st.warning("⚠️ 没有符合条件的论文")

    with col3:
        if st.button("📥 批量导入", use_container_width=True):
            st.info("批量导入功能开发中...")

    with col4:
        if st.button("🗑️ 清空数据", use_container_width=True, type="secondary"):
            st.session_state.show_clear_confirm = True

    # 清空数据确认对话框
    if st.session_state.get('show_clear_confirm', False):
        st.warning("⚠️ 确认要清空所有抓取的论文数据吗？此操作不可恢复！")
        col_confirm1, col_confirm2, col_confirm3 = st.columns([1, 1, 3])
        with col_confirm1:
            if st.button("✅ 确认清空", type="primary"):
                try:
                    db_manager.delete_all_arxiv_papers()
                    st.session_state.show_clear_confirm = False
                    st.success("✅ 已清空所有论文数据")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 清空失败: {str(e)}")
        with col_confirm2:
            if st.button("❌ 取消"):
                st.session_state.show_clear_confirm = False
                st.rerun()

    # 筛选选项
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        score_filter = st.selectbox(
            "最低分数",
            options=[0.0, 5.0, 7.0, 9.0],
            index=0,
            format_func=lambda x: f"{x}分以上" if x > 0 else "全部"
        )
    with col2:
        limit = st.selectbox(
            "显示数量",
            options=[20, 50, 100, 200],
            index=1
        )

    # 获取论文列表
    papers = db_manager.get_all_arxiv_papers(limit=limit, min_score=score_filter)

    if not papers:
        st.info("📭 还没有抓取论文，点击「立即抓取」开始吧！")
        return

    # 统计信息
    s_count = len([p for p in papers if p.score >= 9])
    a_count = len([p for p in papers if 7 <= p.score < 9])
    b_count = len([p for p in papers if 5 <= p.score < 7])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总计", len(papers))
    col2.metric("S级 (9-10分)", s_count)
    col3.metric("A级 (7-8分)", a_count)
    col4.metric("B级 (5-6分)", b_count)

    st.markdown("---")

    # 显示论文卡片
    for paper in papers:
        render_paper_card(paper)


def render_paper_card(paper):
    """渲染单个论文卡片"""
    # 确定分数等级
    if paper.score >= 9:
        badge_color = "#e74c3c"
        level = "S级"
    elif paper.score >= 7:
        badge_color = "#3498db"
        level = "A级"
    else:
        badge_color = "#95a5a6"
        level = "B级"

    with st.container():
        # 标题和分数
        col1, col2 = st.columns([4, 1])
        with col1:
            # 显示英文原标题
            st.markdown(f"### {paper.title}")
            # 显示中文翻译（如果有，灰色小字）
            if paper.title_zh:
                st.markdown(f'<p style="color:#7f8c8d;font-size:14px;margin-top:-10px;">{paper.title_zh}</p>',
                           unsafe_allow_html=True)
        with col2:
            st.markdown(
                f'<div style="background:{badge_color};color:white;padding:8px;'
                f'border-radius:20px;text-align:center;font-weight:bold;">'
                f'{level} {paper.score:.1f}分</div>',
                unsafe_allow_html=True
            )

        # 作者信息（带机构）
        authors_display = []
        for author in paper.authors[:3]:
            if isinstance(author, dict):
                name = author.get('name', '')
                affiliation = author.get('affiliation', '')
                if affiliation:
                    authors_display.append(f"{name} ({affiliation})")
                else:
                    authors_display.append(name)
            else:
                # 兼容旧数据格式（纯字符串）
                authors_display.append(str(author))

        authors_text = ', '.join(authors_display)
        if len(paper.authors) > 3:
            authors_text += '...'

        # 元数据
        st.caption(f"📝 {authors_text} | "
                  f"🔗 [arxiv.org/abs/{paper.arxiv_id}](https://arxiv.org/abs/{paper.arxiv_id}) | "
                  f"📅 {paper.published_date.strftime('%Y-%m-%d')}")

        # 评分理由
        st.markdown(f"**评分理由**: {paper.score_reason}")

        # 标签
        if paper.tags:
            tags_html = " ".join([
                f'<span style="background:#ecf0f1;padding:4px 10px;border-radius:4px;'
                f'font-size:12px;margin-right:5px;">{tag}</span>'
                for tag in paper.tags
            ])
            st.markdown(tags_html, unsafe_allow_html=True)

        # 操作按钮
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("📄 查看摘要", key=f"abstract_{paper.id}"):
                st.session_state[f'show_abstract_{paper.id}'] = True

        with col2:
            if not paper.is_imported:
                if st.button("📥 导入到论文库", key=f"import_{paper.id}"):
                    st.info("导入功能开发中...")

        # 显示摘要（如果点击了查看）
        if st.session_state.get(f'show_abstract_{paper.id}', False):
            with st.expander("📖 中文摘要", expanded=True):
                st.write(paper.abstract_zh or paper.abstract)
            if st.button("收起", key=f"hide_{paper.id}"):
                st.session_state[f'show_abstract_{paper.id}'] = False
                st.rerun()

        st.markdown("---")


def show_keyword_config():
    """显示关键词配置"""
    st.markdown("### ⚙️ 关键词配置")
    st.caption("配置用于 Arxiv 搜索的关键词，系统会抓取包含这些关键词的论文")

    # 添加关键词
    st.markdown("#### 添加新关键词")
    with st.form("add_keyword_form"):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            new_keyword = st.text_input("关键词", placeholder="例如: Reinforcement Learning")
        with col2:
            category = st.selectbox("类别", ["core", "frontier"])
        with col3:
            st.write("")  # 占位
            st.write("")  # 占位
            submitted = st.form_submit_button("➕ 添加", use_container_width=True)

        if submitted and new_keyword:
            db_manager.add_keyword(new_keyword, category)
            st.success(f"✅ 已添加关键词: {new_keyword}")
            st.rerun()

    st.markdown("---")

    # 显示现有关键词
    st.markdown("#### 已配置关键词")

    keywords = db_manager.get_all_keywords()

    if not keywords:
        st.info("还没有配置关键词，请添加一些关键词")
        # 提供快速初始化按钮
        if st.button("🚀 初始化默认关键词"):
            default_keywords = [
                ('Operations Research', 'core'),
                ('VRP', 'core'),
                ('MIP', 'core'),
                ('MILP', 'core'),
                ('Combinatorial Optimization', 'core'),
                ('Agent Memory', 'frontier'),
                ('LLM Memory', 'frontier'),
                ('Agentic RL', 'frontier'),
                ('RLHF', 'frontier'),
                ('Reinforcement Learning', 'core')
            ]
            for kw, cat in default_keywords:
                db_manager.add_keyword(kw, cat)
            st.success("✅ 已初始化默认关键词")
            st.rerun()
    else:
        # 按类别分组显示
        core_kws = [k for k in keywords if k.category == 'core']
        frontier_kws = [k for k in keywords if k.category == 'frontier']

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**核心关键词 (Core)**")
            for kw in core_kws:
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"• {kw.keyword}")
                with col_b:
                    if st.button("🗑️", key=f"del_core_{kw.id}"):
                        db_manager.delete_keyword(kw.id)
                        st.rerun()

        with col2:
            st.markdown("**前沿关键词 (Frontier)**")
            for kw in frontier_kws:
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"• {kw.keyword}")
                with col_b:
                    if st.button("🗑️", key=f"del_frontier_{kw.id}"):
                        db_manager.delete_keyword(kw.id)
                        st.rerun()


def show_statistics():
    """显示统计分析"""
    st.markdown("### 📈 统计分析")

    # 获取最近7天的数据
    papers = db_manager.get_all_arxiv_papers(limit=500)

    if not papers:
        st.info("还没有数据")
        return

    # 分数分布
    st.markdown("#### 📊 分数分布")
    score_ranges = {
        "S级 (9-10分)": len([p for p in papers if p.score >= 9]),
        "A级 (7-8分)": len([p for p in papers if 7 <= p.score < 9]),
        "B级 (5-6分)": len([p for p in papers if 5 <= p.score < 7]),
        "C级 (<5分)": len([p for p in papers if p.score < 5])
    }

    col1, col2 = st.columns([1, 1])

    with col1:
        # 饼图
        fig_pie = go.Figure(data=[go.Pie(
            labels=list(score_ranges.keys()),
            values=list(score_ranges.values()),
            hole=0.3,
            marker=dict(colors=['#e74c3c', '#3498db', '#95a5a6', '#bdc3c7'])
        )])
        fig_pie.update_layout(title="论文等级分布", height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # 柱状图
        fig_bar = go.Figure(data=[go.Bar(
            x=list(score_ranges.keys()),
            y=list(score_ranges.values()),
            marker=dict(color=['#e74c3c', '#3498db', '#95a5a6', '#bdc3c7'])
        )])
        fig_bar.update_layout(title="论文数量统计", height=400, yaxis_title="数量")
        st.plotly_chart(fig_bar, use_container_width=True)

    # 平均分
    avg_score = sum(p.score for p in papers) / len(papers) if papers else 0
    st.metric("平均分", f"{avg_score:.2f}")

    # 分数分布直方图
    st.markdown("#### 📈 分数详细分布")
    scores = [p.score for p in papers]
    fig_hist = go.Figure(data=[go.Histogram(
        x=scores,
        nbinsx=20,
        marker=dict(color='#3498db')
    )])
    fig_hist.update_layout(
        title="论文分数分布直方图",
        xaxis_title="分数",
        yaxis_title="论文数量",
        height=400
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # 最高分论文
    st.markdown("#### 🏆 最高分论文 Top 5")
    top_papers = sorted(papers, key=lambda p: p.score, reverse=True)[:5]
    for i, paper in enumerate(top_papers, 1):
        st.write(f"{i}. **[{paper.score:.1f}分]** {paper.title_zh or paper.title}")
