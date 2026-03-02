"""
Auto-Scholar 页面
论文智能监控和评分系统
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import List, Dict
from database.db_manager import db_manager
from services.scheduler import daily_scheduler
from services.progress_tracker import ProgressTracker, create_progress_callback, STAGE_NAMES, PipelineStage
from services.paper_importer import paper_importer


def show_auto_scholar():
    """显示 Auto-Scholar 页面"""
    st.title("🤖 Auto-Scholar 论文智能监控")

    # 创建 Tabs（新增发表趋势）
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 论文列表",
        "⭐ 收藏列表",
        "⚙️ 关键词设置",
        "📈 统计分析",
        "📊 发表趋势"
    ])

    with tab1:
        show_papers_list()

    with tab2:
        show_favorites_list()

    with tab3:
        show_keyword_config()

    with tab4:
        show_statistics()

    with tab5:
        show_trend_analysis()


def show_papers_list():
    """显示论文列表"""
    st.markdown("### 📚 已抓取论文")

    # 时间范围选择
    st.markdown("#### ⏰ 抓取时间设置")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        fetch_mode = st.selectbox(
            "抓取模式",
            ["昨天到目前", "自定义时间段"],
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
        fetch_clicked = st.button("🚀 立即抓取", use_container_width=True)

    with col2:
        if st.button("📄 导出报告", use_container_width=True):
            from services.report_generator import report_generator
            papers = db_manager.get_all_arxiv_papers(limit=500, min_score=5.0)
            if papers:
                report_path = report_generator.generate_daily_report(papers, datetime.now())
                st.success(f"✅ 报告已生成: {report_path}")
            else:
                st.warning("⚠️ 没有符合条件的论文")

    # 处理抓取逻辑（放在按钮区域外，避免嵌套问题）
    if fetch_clicked:
        # 创建进度显示容器
        progress_container = st.container()

        with progress_container:
            st.markdown("#### 🔄 抓取进度")

            # 总进度条
            overall_progress_bar = st.progress(0, text="准备开始...")

            # 阶段状态显示
            stage_status = st.empty()

            # 详细日志
            with st.expander("📋 详细日志", expanded=False):
                log_container = st.empty()

        # 进度追踪
        logs = []

        def update_ui(stage: str, current: int, total: int, message: str):
            """更新 UI 进度"""
            # 计算总进度
            stage_weights = {
                'arxiv': 0.10,
                'keyword': 0.05,
                'metadata': 0.10,
                's2': 0.25,
                'ai_scoring': 0.45,
                'saving': 0.05,
            }

            # 计算当前阶段进度
            stage_progress = current / total if total > 0 else 0

            # 计算总进度
            completed_weight = sum(
                w for s, w in stage_weights.items()
                if list(stage_weights.keys()).index(s) < list(stage_weights.keys()).index(stage)
            )
            current_weight = stage_weights.get(stage, 0) * stage_progress
            overall = completed_weight + current_weight

            # 更新进度条
            overall_progress_bar.progress(min(overall, 1.0), text=f"总进度: {overall*100:.1f}%")

            # 阶段名称映射
            stage_names = {
                'arxiv': '📡 Arxiv 抓取',
                'keyword': '🔍 关键词筛选',
                'metadata': '📊 元数据评分',
                's2': '🎓 S2 筛选',
                'ai_scoring': '🤖 AI 评分',
                'saving': '💾 保存数据',
            }

            # 更新阶段状态
            stage_status.markdown(f"""
**当前阶段**: {stage_names.get(stage, stage)}

**进度**: {current} / {total}

**状态**: {message}
            """)

            # 添加日志
            timestamp = datetime.now().strftime('%H:%M:%S')
            logs.append(f"[{timestamp}] {message}")
            log_container.code('\n'.join(logs[-30:]))  # 显示最近30条

        try:
            if fetch_mode == "自定义时间段":
                start_dt = datetime.combine(start_date, datetime.min.time())
                end_dt = datetime.combine(end_date, datetime.max.time())
                result = daily_scheduler.run_daily_pipeline(
                    max_results=500,
                    start_date=start_dt,
                    end_date=end_dt,
                    progress_callback=update_ui
                )
            else:  # 昨天到目前模式
                # 最近2天：前天 00:00 到今天 23:59
                # 这样可以确保抓到论文（考虑到 Arxiv 更新时间和时区差异）
                two_days_ago = datetime.now() - timedelta(days=2)
                start_dt = datetime.combine(two_days_ago.date(), datetime.min.time())
                end_dt = datetime.combine(datetime.now().date(), datetime.max.time())
                result = daily_scheduler.run_daily_pipeline(
                    max_results=500,
                    start_date=start_dt,
                    end_date=end_dt,
                    progress_callback=update_ui
                )

            # 完成
            overall_progress_bar.progress(1.0, text="✅ 抓取完成！")
            if result:
                st.success(f"✅ 抓取完成！共处理 {result.get('scored', 0)} 篇论文")
            else:
                st.success("✅ 抓取完成！")

            # 延迟刷新
            import time
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"❌ 抓取失败: {str(e)}")

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
        # 扩展显示数量选项，支持自定义输入
        limit_options = [20, 50, 100, 200, 500, 1000]
        limit_choice = st.selectbox(
            "显示数量",
            options=limit_options + ["自定义"],
            index=2,  # 默认100
            format_func=lambda x: f"{x}篇" if isinstance(x, int) else x
        )

        if limit_choice == "自定义":
            limit = st.number_input(
                "输入数量",
                min_value=10,
                max_value=5000,
                value=200,
                step=50
            )
        else:
            limit = limit_choice

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

        # 顶会顶刊和知名机构徽章（新增）
        badges_html = []

        # 会议/期刊徽章
        if hasattr(paper, 'venue') and paper.venue:
            venue_display = paper.venue
            if hasattr(paper, 'venue_year') and paper.venue_year:
                venue_display = f"{paper.venue} {paper.venue_year}"
            badges_html.append(
                f'<span style="background:#9b59b6;color:white;padding:4px 10px;border-radius:12px;'
                f'font-size:13px;margin-right:8px;font-weight:500;">📍 {venue_display}</span>'
            )

        # 知名机构徽章
        if hasattr(paper, 'institutions') and paper.institutions:
            institutions_display = ', '.join(paper.institutions[:3])  # 最多显示3个
            if len(paper.institutions) > 3:
                institutions_display += f' +{len(paper.institutions) - 3}'
            badges_html.append(
                f'<span style="background:#16a085;color:white;padding:4px 10px;border-radius:12px;'
                f'font-size:13px;margin-right:8px;font-weight:500;">🏛️ {institutions_display}</span>'
            )

        # 显示徽章
        if badges_html:
            st.markdown(
                '<div style="margin-top:8px;margin-bottom:8px;">' + ''.join(badges_html) + '</div>',
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
            # 收藏按钮
            is_favorited = getattr(paper, 'is_favorited', False)
            if is_favorited:
                st.button("⭐ 已收藏", key=f"fav_{paper.id}", disabled=True)
            else:
                if st.button("☆ 收藏", key=f"fav_{paper.id}"):
                    result = db_manager.favorite_arxiv_paper(paper.id)
                    if result:
                        st.success("✅ 已收藏")
                        st.rerun()
                    else:
                        st.error("收藏失败")

        with col3:
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


def show_favorites_list():
    """显示收藏列表"""
    st.markdown("### ⭐ 我的收藏")

    # 获取存储统计
    stats = db_manager.get_storage_stats()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("收藏数量", stats['favorites'])
    col2.metric("已导入", stats['imported'])
    col3.metric("临时论文", stats['arxiv_papers'])
    col4.metric("可清理", stats['can_cleanup'])

    # 清理按钮
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("🗑️ 清理过期数据", use_container_width=True):
            deleted = db_manager.cleanup_expired_arxiv_papers(days_to_keep=7)
            if deleted > 0:
                st.success(f"✅ 已清理 {deleted} 篇过期论文")
                st.rerun()
            else:
                st.info("没有需要清理的数据")

    st.markdown("---")

    # 获取收藏列表
    favorites = db_manager.get_all_favorites()

    if not favorites:
        st.info("📭 还没有收藏论文，去论文列表中收藏感兴趣的论文吧！")
        return

    # 显示收藏的论文
    for fav in favorites:
        render_favorite_card(fav)


def render_favorite_card(fav):
    """渲染收藏的论文卡片"""
    # 确定分数等级
    score = fav.score or 0
    if score >= 9:
        badge_color = "#e74c3c"
        level = "S级"
    elif score >= 7:
        badge_color = "#3498db"
        level = "A级"
    else:
        badge_color = "#95a5a6"
        level = "B级"

    with st.container():
        # 标题和分数
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### {fav.title}")
            if fav.title_zh:
                st.markdown(f'<p style="color:#7f8c8d;font-size:14px;margin-top:-10px;">{fav.title_zh}</p>',
                           unsafe_allow_html=True)
        with col2:
            st.markdown(
                f'<div style="background:{badge_color};color:white;padding:8px;'
                f'border-radius:20px;text-align:center;font-weight:bold;">'
                f'{level} {score:.1f}分</div>',
                unsafe_allow_html=True
            )

        # 作者信息
        authors = fav.authors or []
        authors_text = ', '.join(authors[:3])
        if len(authors) > 3:
            authors_text += '...'

        # 元数据
        pub_date = fav.published_date.strftime('%Y-%m-%d') if fav.published_date else 'N/A'
        fav_date = fav.favorited_date.strftime('%Y-%m-%d') if fav.favorited_date else 'N/A'
        st.caption(f"📝 {authors_text} | "
                  f"🔗 [arxiv.org/abs/{fav.arxiv_id}]({fav.arxiv_url}) | "
                  f"📅 发布: {pub_date} | ⭐ 收藏: {fav_date}")

        # 评分理由
        if fav.score_reason:
            st.markdown(f"**评分理由**: {fav.score_reason}")

        # 标签
        if fav.tags:
            tags_html = " ".join([
                f'<span style="background:#ecf0f1;padding:4px 10px;border-radius:4px;'
                f'font-size:12px;margin-right:5px;">{tag}</span>'
                for tag in fav.tags
            ])
            st.markdown(tags_html, unsafe_allow_html=True)

        # 操作按钮
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        with col1:
            if st.button("📄 查看摘要", key=f"fav_abstract_{fav.id}"):
                st.session_state[f'show_fav_abstract_{fav.id}'] = True

        with col2:
            imported_paper_key = f"imported_paper_{fav.id}"
            if st.button("📥 导入论文库", key=f"fav_import_{fav.id}"):
                arxiv_paper = db_manager.get_arxiv_paper_by_arxiv_id(fav.arxiv_id)

                if not arxiv_paper:
                    st.error(f"未找到对应的 Arxiv 论文记录 (arxiv_id: {fav.arxiv_id})")
                elif arxiv_paper.is_imported:
                    st.info("该论文已导入到论文库")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    def update_progress(progress: int, message: str):
                        progress_bar.progress(progress / 100)
                        status_text.text(message)

                    result = paper_importer.import_arxiv_paper(
                        arxiv_paper_id=arxiv_paper.id,
                        progress_callback=update_progress
                    )

                    if result['success']:
                        if result.get('is_duplicate'):
                            st.info(result['message'])
                        else:
                            st.success(f"✅ {result['message']}")
                            st.balloons()
                        st.session_state[imported_paper_key] = result['paper'].id
                    else:
                        st.error(f"❌ {result.get('error', '导入失败')}")

            if imported_paper_key in st.session_state:
                if st.button("📖 查看论文详情", key=f"view_imported_{fav.id}"):
                    paper_id = st.session_state.pop(imported_paper_key)
                    st.session_state.current_page = 'paper_detail'
                    st.session_state.selected_paper_id = paper_id
                    st.rerun()

        with col3:
            if st.button("❌ 取消收藏", key=f"unfav_{fav.id}"):
                if db_manager.remove_favorite(fav.id):
                    st.success("已取消收藏")
                    st.rerun()

        # 显示摘要
        if st.session_state.get(f'show_fav_abstract_{fav.id}', False):
            with st.expander("📖 摘要", expanded=True):
                if fav.abstract_zh:
                    st.markdown("**中文摘要**")
                    st.write(fav.abstract_zh)
                    st.markdown("**英文摘要**")
                st.write(fav.abstract)

                # PDF 链接
                st.markdown(f"📎 [下载 PDF]({fav.pdf_url})")

            if st.button("收起", key=f"hide_fav_{fav.id}"):
                st.session_state[f'show_fav_abstract_{fav.id}'] = False
                st.rerun()

        # 用户笔记
        with st.expander("📝 我的笔记", expanded=False):
            notes = fav.user_notes or ""
            new_notes = st.text_area("笔记内容", value=notes, key=f"notes_{fav.id}",
                                     placeholder="记录你对这篇论文的想法...")
            if st.button("💾 保存笔记", key=f"save_notes_{fav.id}"):
                if db_manager.update_favorite_notes(fav.id, new_notes):
                    st.success("笔记已保存")
                else:
                    st.error("保存失败")

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
    """显示统计分析（基于已评分论文）"""
    st.markdown("### 📈 统计分析（基于已评分论文）")

    # 获取所有已评分论文
    papers = db_manager.get_all_arxiv_papers(limit=500)

    if not papers:
        st.info("暂无已评分论文数据")
        return

    # 创建子Tab
    subtab1, subtab2, subtab3, subtab4 = st.tabs([
        "📊 分数分析",
        "🏆 顶会顶刊",
        "🏛️ 知名机构",
        "🔬 交叉分析"
    ])

    with subtab1:
        show_score_analysis(papers)

    with subtab2:
        show_venue_analysis(papers)

    with subtab3:
        show_institution_analysis(papers)

    with subtab4:
        show_cross_analysis(papers)


def show_score_analysis(papers: List):
    """显示分数分析"""
    from services.quality_analyzer import quality_analyzer

    st.markdown("#### 📊 分数分析")

    # 分数分布
    score_ranges = quality_analyzer.get_score_distribution(papers)

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

    # 统计指标
    stats = quality_analyzer.get_score_statistics(papers)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("平均分", f"{stats['avg']:.2f}")
    col2.metric("中位数", f"{stats['median']:.2f}")
    col3.metric("最高分", f"{stats['max']:.2f}")
    col4.metric("最低分", f"{stats['min']:.2f}")

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


def show_venue_analysis(papers: List):
    """显示顶会顶刊分析"""
    from services.quality_analyzer import quality_analyzer

    st.markdown("#### 🏆 顶会顶刊分析")

    # 获取顶会顶刊分布
    venue_dist = quality_analyzer.get_venue_distribution(papers, min_score=0.0, top_n=20)

    if not venue_dist:
        st.info("暂无会议/期刊数据")
        return

    # 横向柱状图
    fig = go.Figure(data=[go.Bar(
        y=[v['venue'] for v in venue_dist],
        x=[v['count'] for v in venue_dist],
        orientation='h',
        marker=dict(color='#9b59b6'),
        text=[f"{v['count']}篇 (均分:{v['avg_score']:.1f})" for v in venue_dist],
        textposition='auto'
    )])
    fig.update_layout(
        title="顶会顶刊论文数量排行",
        xaxis_title="论文数量",
        yaxis_title="会议/期刊",
        height=max(400, len(venue_dist) * 25),
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig, use_container_width=True)

    # 显示详细数据
    with st.expander("📋 详细数据", expanded=False):
        for i, v in enumerate(venue_dist, 1):
            st.write(f"{i}. **{v['venue']}**: {v['count']}篇论文，平均分 {v['avg_score']:.2f}")


def show_institution_analysis(papers: List):
    """显示知名机构分析"""
    from services.quality_analyzer import quality_analyzer

    st.markdown("#### 🏛️ 知名机构分析")

    # 获取知名机构分布
    inst_dist = quality_analyzer.get_institution_distribution(papers, min_score=0.0, top_n=20)

    if not inst_dist:
        st.info("暂无机构数据")
        return

    # 横向柱状图
    fig = go.Figure(data=[go.Bar(
        y=[i['institution'] for i in inst_dist],
        x=[i['count'] for i in inst_dist],
        orientation='h',
        marker=dict(color='#16a085'),
        text=[f"{i['count']}篇 (均分:{i['avg_score']:.1f})" for i in inst_dist],
        textposition='auto'
    )])
    fig.update_layout(
        title="知名机构论文数量排行",
        xaxis_title="论文数量",
        yaxis_title="机构",
        height=max(400, len(inst_dist) * 25),
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig, use_container_width=True)

    # 显示详细数据
    with st.expander("📋 详细数据", expanded=False):
        for i, inst in enumerate(inst_dist, 1):
            st.write(f"{i}. **{inst['institution']}**: {inst['count']}篇论文，平均分 {inst['avg_score']:.2f}")


def show_trend_analysis():
    """显示发表趋势分析（轻量级，从Arxiv API抓取）"""
    st.markdown("### 📊 发表趋势分析（轻量级）")

    st.info("💡 此功能从Arxiv API实时抓取数据，不依赖评分系统，可查看完整的论文发表趋势")

    # 时间范围选择器
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "开始日期",
            value=datetime.now() - timedelta(days=7),
            max_value=datetime.now()
        )
    with col2:
        end_date = st.date_input(
            "结束日期",
            value=datetime.now(),
            max_value=datetime.now()
        )

    # 限制查询范围（避免API超时）
    max_days = 90  # 放宽到90天
    if (end_date - start_date).days > max_days:
        st.warning(f"⚠️ 查询范围不能超过{max_days}天，已自动调整")
        start_date = end_date - timedelta(days=max_days)

    # 获取关键词配置
    keywords_config = db_manager.get_all_keywords()
    if not keywords_config:
        st.warning("⚠️ 请先在「关键词设置」中配置关键词")
        return

    # 抓取按钮
    if st.button("🔍 开始分析", type="primary"):
        with st.spinner("正在从Arxiv API抓取数据..."):
            # 创建趋势分析器
            from services.trend_analyzer import trend_analyzer

            # 抓取数据
            keywords = [kw.keyword for kw in keywords_config]
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date, datetime.max.time())

            papers = trend_analyzer.fetch_papers_by_date_range(
                start_dt, end_dt, keywords
            )

            if not papers:
                st.info("未找到相关论文")
                return

            # 缓存数据到session state
            st.session_state.trend_papers = papers
            st.session_state.trend_keywords = keywords
            st.session_state.trend_keywords_config = keywords_config

            # 立即初始化关键词选择状态（避免第一次选择时跳转）
            if "trend_keyword_comparison" not in st.session_state:
                st.session_state.trend_keyword_comparison = keywords[:min(3, len(keywords))]

    # 显示分析结果
    if 'trend_papers' in st.session_state:
        papers = st.session_state.trend_papers
        keywords = st.session_state.trend_keywords
        keywords_config = st.session_state.trend_keywords_config

        # 确保关键词选择状态已初始化（防御性编程）
        if "trend_keyword_comparison" not in st.session_state:
            st.session_state.trend_keyword_comparison = keywords[:min(3, len(keywords))]

        st.success(f"✅ 共抓取 {len(papers)} 篇论文")

        # 子Tab
        subtab1, subtab2, subtab3 = st.tabs([
            "📅 时间趋势",
            "🔍 关键词分析",
            "🔥 热力图"
        ])

        with subtab1:
            show_time_trend(papers)

        with subtab2:
            show_keyword_distribution(papers, keywords, keywords_config)

        with subtab3:
            show_keyword_heatmap(papers, keywords)


def show_time_trend(papers: List[Dict]):
    """显示时间趋势分析"""
    from services.trend_analyzer import trend_analyzer

    st.markdown("#### 📅 时间趋势分析")

    # 每日论文数量趋势
    daily_data = trend_analyzer.get_daily_paper_count(papers)

    if not daily_data:
        st.info("暂无数据")
        return

    # 折线图
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[d['date'] for d in daily_data],
        y=[d['count'] for d in daily_data],
        mode='lines+markers',
        name='论文数量',
        line=dict(color='#3498db', width=2),
        marker=dict(size=8)
    ))
    fig.update_layout(
        title="每日新增论文数量趋势",
        xaxis_title="日期",
        yaxis_title="论文数量",
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # 统计信息
    col1, col2, col3 = st.columns(3)
    total_papers = len(papers)
    avg_daily = total_papers / len(daily_data) if daily_data else 0
    max_daily = max([d['count'] for d in daily_data]) if daily_data else 0

    col1.metric("总论文数", total_papers)
    col2.metric("日均论文数", f"{avg_daily:.1f}")
    col3.metric("单日最高", max_daily)


def show_keyword_distribution(papers: List[Dict], keywords: List[str], keywords_config: List):
    """显示关键词分析"""
    from services.trend_analyzer import trend_analyzer

    st.markdown("#### 🔍 关键词分析")

    # 关键词论文数量分布
    keyword_dist = trend_analyzer.get_keyword_distribution(papers, keywords)

    if not keyword_dist:
        st.info("暂无数据")
        return

    # 柱状图
    fig_bar = go.Figure(data=[go.Bar(
        x=[d['keyword'] for d in keyword_dist],
        y=[d['count'] for d in keyword_dist],
        marker=dict(color='#3498db')
    )])
    fig_bar.update_layout(
        title="关键词论文数量分布",
        xaxis_title="关键词",
        yaxis_title="论文数量",
        height=400,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # 关键词类别占比
    category_ratio = trend_analyzer.get_keyword_category_ratio(papers, keywords_config)

    col1, col2 = st.columns(2)

    with col1:
        # 饼图
        fig_pie = go.Figure(data=[go.Pie(
            labels=['核心关键词 (Core)', '前沿关键词 (Frontier)'],
            values=[category_ratio['core'], category_ratio['frontier']],
            hole=0.3,
            marker=dict(colors=['#3498db', '#e74c3c'])
        )])
        fig_pie.update_layout(title="关键词类别占比", height=350)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # 显示统计数据
        st.markdown("**统计数据**")
        st.metric("核心关键词论文", category_ratio['core'])
        st.metric("前沿关键词论文", category_ratio['frontier'])

    # 多关键词趋势对比（P2阶段新增）
    st.markdown("---")
    st.markdown("#### 📈 关键词时间趋势对比")

    # 注意：初始化已在数据抓取完成时完成，这里不需要再初始化
    # 选择要对比的关键词（最多5个）
    selected_keywords = st.multiselect(
        "选择要对比的关键词（最多5个）",
        options=keywords,
        max_selections=5,
        key="trend_keyword_comparison"
    )

    if selected_keywords:
        # 创建多条折线图
        fig_trends = go.Figure()

        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']

        for i, keyword in enumerate(selected_keywords):
            trend_data = trend_analyzer.get_keyword_trend(papers, keyword)
            if trend_data:
                fig_trends.add_trace(go.Scatter(
                    x=[d['date'] for d in trend_data],
                    y=[d['count'] for d in trend_data],
                    mode='lines+markers',
                    name=keyword,
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=6)
                ))

        fig_trends.update_layout(
            title="关键词时间趋势对比",
            xaxis_title="日期",
            yaxis_title="论文数量",
            height=400,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trends, use_container_width=True)
    else:
        st.info("请选择至少一个关键词进行趋势分析")


def show_keyword_heatmap(papers: List[Dict], keywords: List[str]):
    """显示关键词×时间热力图"""
    from services.trend_analyzer import trend_analyzer

    st.markdown("#### 🔥 关键词×时间热力图")

    # 限制关键词数量（避免热力图过大）
    max_keywords = 20
    if len(keywords) > max_keywords:
        st.info(f"关键词数量过多，仅显示前 {max_keywords} 个")
        keywords = keywords[:max_keywords]

    # 获取热力图数据
    heatmap_data = trend_analyzer.get_keyword_time_heatmap(papers, keywords)

    if not heatmap_data['dates']:
        st.info("暂无数据")
        return

    # 创建热力图
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data['matrix'],
        x=[d.strftime('%Y-%m-%d') for d in heatmap_data['dates']],
        y=heatmap_data['keywords'],
        colorscale='Blues',
        hoverongaps=False
    ))
    fig.update_layout(
        title="关键词×时间热力图",
        xaxis_title="日期",
        yaxis_title="关键词",
        height=max(400, len(keywords) * 25),
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)


def show_cross_analysis(papers: List):
    """显示交叉分析（P2阶段）"""
    from services.quality_analyzer import quality_analyzer

    st.markdown("#### 🔬 交叉分析")

    # 选择分析类型
    analysis_type = st.selectbox(
        "选择分析类型",
        ["会议×分数", "机构×分数"]
    )

    if analysis_type == "会议×分数":
        show_venue_score_matrix(papers)
    else:
        show_institution_score_matrix(papers)


def show_venue_score_matrix(papers: List):
    """显示会议×分数交叉分析"""
    from services.quality_analyzer import quality_analyzer

    st.markdown("##### 🏆 会议×分数交叉分析")

    # 获取交叉分析数据
    matrix_data = quality_analyzer.get_venue_score_matrix(papers, top_venues=10)

    if not matrix_data['venues']:
        st.info("暂无会议数据")
        return

    # 创建分组柱状图
    fig = go.Figure()

    colors = ['#e74c3c', '#3498db', '#95a5a6', '#bdc3c7']

    for i, level in enumerate(matrix_data['score_levels']):
        fig.add_trace(go.Bar(
            name=level,
            y=matrix_data['venues'],
            x=[matrix_data['matrix'][j][i] for j in range(len(matrix_data['venues']))],
            orientation='h',
            marker=dict(color=colors[i])
        ))

    fig.update_layout(
        title="会议×分数交叉分析",
        xaxis_title="论文数量",
        yaxis_title="会议/期刊",
        barmode='stack',
        height=max(400, len(matrix_data['venues']) * 30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 显示详细数据
    with st.expander("📋 详细数据", expanded=False):
        for i, venue in enumerate(matrix_data['venues']):
            st.write(f"**{venue}**:")
            for j, level in enumerate(matrix_data['score_levels']):
                count = matrix_data['matrix'][i][j]
                if count > 0:
                    st.write(f"  - {level}: {count}篇")


def show_institution_score_matrix(papers: List):
    """显示机构×分数交叉分析"""
    from services.quality_analyzer import quality_analyzer

    st.markdown("##### 🏛️ 机构×分数交叉分析")

    # 获取交叉分析数据
    matrix_data = quality_analyzer.get_institution_score_matrix(papers, top_institutions=10)

    if not matrix_data['institutions']:
        st.info("暂无机构数据")
        return

    # 创建分组柱状图
    fig = go.Figure()

    colors = ['#e74c3c', '#3498db', '#95a5a6', '#bdc3c7']

    for i, level in enumerate(matrix_data['score_levels']):
        fig.add_trace(go.Bar(
            name=level,
            y=matrix_data['institutions'],
            x=[matrix_data['matrix'][j][i] for j in range(len(matrix_data['institutions']))],
            orientation='h',
            marker=dict(color=colors[i])
        ))

    fig.update_layout(
        title="机构×分数交叉分析",
        xaxis_title="论文数量",
        yaxis_title="机构",
        barmode='stack',
        height=max(400, len(matrix_data['institutions']) * 30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 显示详细数据
    with st.expander("📋 详细数据", expanded=False):
        for i, inst in enumerate(matrix_data['institutions']):
            st.write(f"**{inst}**:")
            for j, level in enumerate(matrix_data['score_levels']):
                count = matrix_data['matrix'][i][j]
                if count > 0:
                    st.write(f"  - {level}: {count}篇")
