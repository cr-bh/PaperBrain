"""
PaperBrain 主应用入口
"""
import streamlit as st
from database.db_manager import db_manager
from database.init_db import init_database

# 页面配置
st.set_page_config(
    page_title="PaperBrain - 智能论文笔记助手",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库
@st.cache_resource
def initialize_app():
    """初始化应用"""
    try:
        init_database()
        return True
    except Exception as e:
        st.error(f"数据库初始化失败: {str(e)}")
        return False

# 初始化 session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'
if 'selected_paper_id' not in st.session_state:
    st.session_state.selected_paper_id = None

# 初始化应用
if not initialize_app():
    st.stop()

# 侧边栏导航
with st.sidebar:
    st.title("📚 PaperBrain")
    st.markdown("---")

    # 导航按钮
    if st.button("🏠 主页", use_container_width=True):
        st.session_state.current_page = 'dashboard'
        st.rerun()

    if st.button("📤 上传论文", use_container_width=True):
        st.session_state.current_page = 'upload'
        st.rerun()

    if st.button("💬 对话问答", use_container_width=True):
        st.session_state.current_page = 'chat'
        st.rerun()

    if st.button("🏷️ 标签管理", use_container_width=True):
        st.session_state.current_page = 'tag_management'
        st.rerun()

    if st.button("🤖 Auto-Scholar", use_container_width=True):
        st.session_state.current_page = 'auto_scholar'
        st.rerun()

    st.markdown("---")

    # 统计信息
    papers = db_manager.get_all_papers()
    tags = db_manager.get_all_tags()

    st.metric("论文总数", len(papers))
    st.metric("标签总数", len(tags))

# 主内容区域
if st.session_state.current_page == 'dashboard':
    from ui.dashboard import show_dashboard
    show_dashboard()
elif st.session_state.current_page == 'upload':
    from ui.upload_page import show_upload_page
    show_upload_page()
elif st.session_state.current_page == 'paper_detail':
    from ui.paper_detail import show_paper_detail
    show_paper_detail()
elif st.session_state.current_page == 'chat':
    from ui.chat_interface import show_global_chat_interface
    show_global_chat_interface()
elif st.session_state.current_page == 'tag_management':
    from ui.tag_management import show_tag_management
    show_tag_management()
elif st.session_state.current_page == 'auto_scholar':
    from ui.auto_scholar import show_auto_scholar
    show_auto_scholar()
