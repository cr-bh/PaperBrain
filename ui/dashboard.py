"""
仪表盘页面
显示论文列表和标签筛选
"""
import streamlit as st
from database.db_manager import db_manager
from utils.helpers import truncate_text


def show_dashboard():
    """显示仪表盘"""
    st.title("📚 论文库")

    # 搜索框
    search_query = st.text_input("🔍 搜索论文", placeholder="输入论文标题或作者...")

    # 获取所有论文
    if search_query:
        papers = db_manager.search_papers(search_query)
    else:
        papers = db_manager.get_all_papers()

    # 标签筛选
    st.markdown("### 🏷️ 按标签筛选")
    all_tags = db_manager.get_all_tags()

    if all_tags:
        # 按类别分组显示标签
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**领域 (Domain)**")
            domain_tags = [t for t in all_tags if t.category == 'domain']
            selected_domain = st.multiselect(
                "选择领域",
                options=[t.name for t in domain_tags],
                key="domain_filter",
                label_visibility="collapsed"
            )

        with col2:
            st.markdown("**方法 (Methodology)**")
            method_tags = [t for t in all_tags if t.category == 'methodology']
            selected_method = st.multiselect(
                "选择方法",
                options=[t.name for t in method_tags],
                key="method_filter",
                label_visibility="collapsed"
            )

        with col3:
            st.markdown("**任务 (Task)**")
            task_tags = [t for t in all_tags if t.category == 'task']
            selected_task = st.multiselect(
                "选择任务",
                options=[t.name for t in task_tags],
                key="task_filter",
                label_visibility="collapsed"
            )

        # 根据选中的标签筛选论文
        selected_tag_names = selected_domain + selected_method + selected_task
        if selected_tag_names:
            filtered_papers = []
            for paper in papers:
                paper_tags = db_manager.get_paper_tags(paper.id)
                paper_tag_names = [t.name for t in paper_tags]
                if any(tag in paper_tag_names for tag in selected_tag_names):
                    filtered_papers.append(paper)
            papers = filtered_papers

    st.markdown("---")

    # 显示论文列表
    if not papers:
        st.info("📭 还没有论文，点击侧边栏的「上传论文」开始吧！")
    else:
        st.markdown(f"### 📄 论文列表 ({len(papers)} 篇)")

        for paper in papers:
            with st.container():
                col1, col2, col3 = st.columns([4, 1, 1])

                with col1:
                    # 论文标题（英文）
                    st.markdown(f"### {paper.title}")
                    # 中文翻译（如果有，灰色小字）
                    if hasattr(paper, 'title_zh') and paper.title_zh:
                        st.markdown(f'<p style="color:#7f8c8d;font-size:14px;margin-top:-10px;">{paper.title_zh}</p>',
                                   unsafe_allow_html=True)

                    # 作者
                    if paper.authors:
                        authors_str = ", ".join(paper.authors[:3])
                        if len(paper.authors) > 3:
                            authors_str += f" 等 {len(paper.authors)} 人"
                        st.markdown(f"**作者:** {authors_str}")

                    # 核心贡献 - 优先显示一句话总结
                    if paper.content_summary and 'summary_struct' in paper.content_summary:
                        # 优先显示一句话总结，如果没有则显示完整贡献的截断版本
                        summary = paper.content_summary['summary_struct'].get('one_sentence_summary', '')
                        if not summary:
                            summary = paper.content_summary['summary_struct'].get('contribution', '')
                        if summary:
                            st.markdown(f"**核心贡献:** {truncate_text(summary, 150)}")

                    # 标签
                    paper_tags = db_manager.get_paper_tags(paper.id)
                    if paper_tags:
                        tags_html = " ".join([
                            f'<span style="background-color: {tag.color}; color: white; padding: 2px 8px; border-radius: 3px; margin-right: 5px; font-size: 12px;">{tag.name}</span>'
                            for tag in paper_tags[:5]
                        ])
                        st.markdown(tags_html, unsafe_allow_html=True)

                with col2:
                    # 查看详情按钮
                    if st.button("📖 查看", key=f"view_{paper.id}", use_container_width=True):
                        st.session_state.selected_paper_id = paper.id
                        st.session_state.current_page = 'paper_detail'
                        st.rerun()

                with col3:
                    # 删除按钮
                    if st.button("🗑️ 删除", key=f"delete_{paper.id}", use_container_width=True):
                        st.session_state.delete_paper_id = paper.id
                        st.rerun()

                # 删除确认对话框
                if st.session_state.get('delete_paper_id') == paper.id:
                    st.warning(f"⚠️ 确定要删除论文「{paper.title}」吗？")
                    col_a, col_b, col_c = st.columns([1, 1, 2])
                    with col_a:
                        if st.button("✓ 确认", key=f"confirm_delete_{paper.id}", type="primary"):
                            from services.rag_service import rag_service
                            rag_service.delete_paper_vectors(paper.id)
                            db_manager.delete_paper(paper.id)
                            st.session_state.delete_paper_id = None
                            st.success("✓ 已删除")
                            st.rerun()
                    with col_b:
                        if st.button("✗ 取消", key=f"cancel_delete_{paper.id}"):
                            st.session_state.delete_paper_id = None
                            st.rerun()

                st.markdown("---")
