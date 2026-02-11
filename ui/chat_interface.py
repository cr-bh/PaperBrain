"""
对话界面组件
支持全局对话和 @mention 特定论文
"""
import streamlit as st
from services.rag_service import rag_service
from database.db_manager import db_manager


def show_global_chat_interface():
    """
    显示全局对话界面
    支持 @paper_title 语法指定论文
    """
    st.title("💬 智能对话")

    # 使用说明
    with st.expander("💡 使用说明"):
        st.markdown("""
        - **全局提问**: 直接输入问题，系统会检索所有论文库回答
        - **指定论文**: 使用 `@论文标题` 来针对特定论文提问
        - **示例**:
          - "强化学习的主要挑战是什么？" (检索所有论文)
          - "@AlphaOpt 这篇论文的核心贡献是什么？" (只检索 AlphaOpt)
        """)

    st.markdown("---")

    # 侧边栏显示可用论文列表
    with st.sidebar:
        st.markdown("### 📚 可用论文")

        # 添加搜索框
        search_keyword = st.text_input("🔍 搜索论文", placeholder="输入关键词...", key="paper_search")

        # 获取论文列表
        if search_keyword:
            papers = db_manager.search_papers(search_keyword)
        else:
            papers = db_manager.get_all_papers(limit=50)

        if papers:
            st.caption(f"找到 {len(papers)} 篇论文，点击可快速 @mention")

            # 使用折叠器来节省空间
            with st.expander(f"📋 论文列表 ({len(papers)} 篇)", expanded=False):
                for paper in papers:
                    # 显示简短标题
                    short_title = paper.title[:40] + "..." if len(paper.title) > 40 else paper.title
                    if st.button(f"📄 {short_title}", key=f"mention_{paper.id}", use_container_width=True):
                        # 将论文标题添加到输入框（通过 session state）
                        st.session_state.mention_paper = paper.title
                        st.rerun()
        else:
            st.info("还没有论文")

    # 初始化全局聊天历史
    if 'global_chat_history' not in st.session_state:
        st.session_state.global_chat_history = []

    # 显示聊天历史
    chat_history = st.session_state.global_chat_history

    for message in chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # 显示上下文信息
            if message.get("context"):
                st.caption(message["context"])

    # 初始化 pending_mentions 列表（用于累积多个@mention）
    if 'pending_mentions' not in st.session_state:
        st.session_state.pending_mentions = []

    # 处理 @mention 点击
    if st.session_state.get('mention_paper'):
        # 将新的 @mention 添加到列表中
        new_mention = st.session_state.mention_paper
        st.session_state.mention_paper = None

        # 避免重复添加同一篇论文
        if new_mention not in st.session_state.pending_mentions:
            st.session_state.pending_mentions.append(new_mention)
            st.success(f"✅ 已添加 @{new_mention}")
        else:
            st.warning(f"⚠️ @{new_mention} 已经在列表中")

    # 显示当前已选择的论文
    if st.session_state.pending_mentions:
        st.info(f"📌 已选择 {len(st.session_state.pending_mentions)} 篇论文: " +
                ", ".join([f"@{p}" for p in st.session_state.pending_mentions]))

        # 添加清空按钮
        if st.button("🗑️ 清空选择", key="clear_mentions"):
            st.session_state.pending_mentions = []
            st.rerun()

    # 用户输入 - 使用 chat_input 支持回车发送
    placeholder_text = "输入您的问题... (可使用 @论文标题 指定论文)"
    if st.session_state.pending_mentions:
        placeholder_text = f"继续输入问题... (已选择 {len(st.session_state.pending_mentions)} 篇论文)"

    user_input = st.chat_input(placeholder_text)

    # 处理用户输入
    if user_input:
        # 如果有待处理的mentions，添加到输入前面
        if st.session_state.pending_mentions:
            mentions_text = " ".join([f"@{p}" for p in st.session_state.pending_mentions])
            user_question = f"{mentions_text} {user_input}"
            st.session_state.pending_mentions = []
        else:
            user_question = user_input

        # 解析 @mention（支持多个论文）
        paper_ids, cleaned_question = rag_service.parse_mention(user_question)

        # 添加用户消息到历史
        chat_history.append({"role": "user", "content": user_question})

        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(user_question)

        # 调用 RAG 服务获取回答
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                if paper_ids:
                    # 针对特定论文提问
                    if len(paper_ids) == 1:
                        paper = db_manager.get_paper_by_id(paper_ids[0])
                        context = f"🎯 正在检索论文: {paper.title}"
                        answer = rag_service.query_paper(paper_ids[0], cleaned_question)
                    else:
                        # 多篇论文
                        paper_titles = []
                        for pid in paper_ids:
                            paper = db_manager.get_paper_by_id(pid)
                            if paper:
                                paper_titles.append(paper.title)
                        context = f"🎯 正在检索 {len(paper_ids)} 篇论文: {', '.join(paper_titles[:3])}" + ("..." if len(paper_titles) > 3 else "")
                        answer = rag_service.query_multiple_papers(paper_ids, cleaned_question)
                else:
                    # 全局提问
                    context = "🌐 正在检索所有论文库"
                    answer = rag_service.query_all_papers(user_question)

                st.markdown(answer)
                st.caption(context)

        # 添加助手回答到历史
        chat_history.append({
            "role": "assistant",
            "content": answer,
            "context": context
        })

        # 更新 session state
        st.session_state.global_chat_history = chat_history
        st.rerun()

    # 清空对话历史按钮
    if chat_history:
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🗑️ 清空历史", use_container_width=True):
                st.session_state.global_chat_history = []
                st.rerun()


def show_chat_interface(paper_id: int):
    """
    显示单篇论文对话界面（保留用于向后兼容）

    Args:
        paper_id: 论文 ID
    """
    st.markdown("### 💬 与论文对话")
    st.markdown("基于论文内容回答您的问题")

    # 初始化聊天历史
    if f'chat_history_{paper_id}' not in st.session_state:
        st.session_state[f'chat_history_{paper_id}'] = []

    # 显示聊天历史
    chat_history = st.session_state[f'chat_history_{paper_id}']

    for message in chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 用户输入
    user_question = st.chat_input("输入您的问题...")

    if user_question:
        # 添加用户消息到历史
        chat_history.append({"role": "user", "content": user_question})

        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(user_question)

        # 调用 RAG 服务获取回答
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                answer = rag_service.query_paper(paper_id, user_question)
                st.markdown(answer)

        # 添加助手回答到历史
        chat_history.append({"role": "assistant", "content": answer})

        # 更新 session state
        st.session_state[f'chat_history_{paper_id}'] = chat_history

    # 清空对话历史按钮
    if chat_history and st.button("🗑️ 清空对话历史"):
        st.session_state[f'chat_history_{paper_id}'] = []
        st.rerun()
