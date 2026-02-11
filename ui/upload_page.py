"""
论文上传页面
处理 PDF 上传和自动分析
"""
import streamlit as st
from pathlib import Path
import shutil
import config
from database.db_manager import db_manager
from services.pdf_parser import pdf_parser
from services.summarizer import summarizer
from services.mindmap_generator import mindmap_generator
from services.tagger import tagger
from services.image_extractor import image_extractor
from services.rag_service import rag_service


def save_uploaded_file(uploaded_file) -> str:
    """
    保存上传的文件到本地

    Args:
        uploaded_file: Streamlit 上传的文件对象

    Returns:
        保存的文件路径
    """
    # 创建保存目录
    save_dir = Path(config.PAPERS_DIR)
    save_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件路径
    file_path = save_dir / uploaded_file.name

    # 保存文件
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(file_path)


def show_upload_page():
    """显示上传页面"""
    st.title("📤 上传论文")

    st.markdown("""
    上传 PDF 格式的学术论文，系统将自动：
    - 📄 提取论文内容
    - 🧠 生成结构化总结
    - 🗺️ 创建思维导图
    - 🏷️ 自动打标签
    - 🖼️ 提取关键图片
    - 💬 支持对话问答
    """)

    st.markdown("---")

    # 检查是否有上传完成的论文
    if st.session_state.get('upload_complete', False):
        st.success("🎉 论文处理成功！")
        st.balloons()

        # 显示查看详情按钮
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📖 查看论文详情", type="primary", use_container_width=True):
                paper_id = st.session_state.get('last_uploaded_paper_id')
                st.session_state.selected_paper_id = paper_id
                st.session_state.current_page = 'paper_detail'
                st.session_state.upload_complete = False  # 清除标志
                st.rerun()

        st.markdown("---")
        st.info("💡 您可以继续上传其他论文")

    # 文件上传
    uploaded_file = st.file_uploader(
        "选择 PDF 文件",
        type=['pdf'],
        help="支持 PDF 格式的学术论文"
    )

    if uploaded_file is not None:
        # 显示文件信息
        st.success(f"✅ 已选择文件: {uploaded_file.name}")

        # 处理按钮
        if st.button("🚀 开始处理", type="primary", use_container_width=True):
            process_paper(uploaded_file)


def process_paper(uploaded_file):
    """处理上传的论文"""
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # 步骤 1: 保存 PDF 文件
        status_text.text("📄 正在保存 PDF 文件...")
        progress_bar.progress(10)

        pdf_path = save_uploaded_file(uploaded_file)

        # 步骤 2: 解析 PDF
        status_text.text("🔍 正在解析 PDF 内容...")
        progress_bar.progress(20)

        parsed_data = pdf_parser.parse_pdf(pdf_path)
        paper_text = parsed_data['text']

        # 步骤 3: 生成总结
        status_text.text("🧠 正在生成结构化总结...")
        progress_bar.progress(40)

        summary = summarizer.summarize_paper(paper_text)

        # 检查是否存在同名论文
        title = summary.get('title', uploaded_file.name)
        existing_paper = db_manager.get_paper_by_title(title)

        if existing_paper:
            st.warning(f"⚠️ 检测到已存在同名论文: {title}")
            st.info("系统将更新现有论文的内容，而不是创建新记录。")
            paper_id = existing_paper.id
            is_update = True
        else:
            paper_id = None
            is_update = False

        # 步骤 4: 生成思维导图
        status_text.text("🗺️ 正在生成思维导图...")
        progress_bar.progress(55)

        mindmap_code = mindmap_generator.generate_mindmap(summary)

        # 步骤 5: 生成标签
        status_text.text("🏷️ 正在生成标签...")
        progress_bar.progress(70)

        tags = tagger.generate_tags(summary)

        # 步骤 6: 保存到数据库
        status_text.text("💾 正在保存到数据库...")
        progress_bar.progress(80)

        if is_update:
            # 更新现有论文
            paper = db_manager.update_paper(
                paper_id,
                title=title,
                authors=summary.get('authors', []),
                file_path=pdf_path,
                content_summary=summary,
                mindmap_code=mindmap_code
            )
            # 删除旧的向量数据
            rag_service.delete_paper_vectors(paper_id)
        else:
            # 创建新论文
            paper = db_manager.create_paper(
                title=title,
                authors=summary.get('authors', []),
                file_path=pdf_path,
                content_summary=summary,
                mindmap_code=mindmap_code
            )

        # 保存标签
        tagger.save_tags_to_db(paper.id, tags)

        # 步骤 7: 提取图片
        status_text.text("🖼️ 正在提取关键图片...")
        progress_bar.progress(85)

        image_extractor.extract_key_images(pdf_path, paper.id)

        # 步骤 8: 向量化（用于 RAG）
        status_text.text("💬 正在向量化文本（用于对话问答）...")
        progress_bar.progress(95)

        rag_service.add_paper_to_vector_db(paper.id, paper_text)

        # 更新向量化状态
        db_manager.update_paper(paper.id, embedding_status=True)

        # 完成
        progress_bar.progress(100)
        status_text.text("✅ 处理完成！")

        # 设置上传完成标志
        st.session_state.upload_complete = True
        st.session_state.last_uploaded_paper_id = paper.id

        # 触发页面重新渲染以显示按钮
        st.rerun()

    except Exception as e:
        st.error(f"❌ 处理失败: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
