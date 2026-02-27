"""
论文详情页面
显示论文的完整信息、思维导图和结构化笔记
"""
import copy
import json
from pathlib import Path

import streamlit as st
from database.db_manager import db_manager


def show_paper_detail():
    """显示论文详情"""
    paper_id = st.session_state.get('selected_paper_id')

    if not paper_id:
        st.error("未选择论文")
        return

    # 获取论文信息
    paper = db_manager.get_paper_by_id(paper_id)
    if not paper:
        st.error("论文不存在")
        return

    # 顶部按钮行
    col1, col2, col3 = st.columns([2, 6, 2])

    with col1:
        if st.button("← 返回主页"):
            st.session_state.current_page = 'dashboard'
            st.rerun()

    with col3:
        if st.button("🗑️ 删除论文", type="secondary"):
            st.session_state.show_delete_confirm = True

    # 删除确认对话框
    if st.session_state.get('show_delete_confirm', False):
        st.warning("⚠️ 确定要删除这篇论文吗？此操作无法撤销！")
        col_a, col_b, col_c = st.columns([1, 1, 2])
        with col_a:
            if st.button("✓ 确认删除", type="primary"):
                # 执行删除
                from services.rag_service import rag_service
                rag_service.delete_paper_vectors(paper_id)
                db_manager.delete_paper(paper_id)
                st.session_state.show_delete_confirm = False
                st.success("✓ 论文已删除")
                st.session_state.current_page = 'dashboard'
                st.rerun()
        with col_b:
            if st.button("✗ 取消"):
                st.session_state.show_delete_confirm = False
                st.rerun()

    # 论文标题
    st.title(paper.title)

    # 作者信息
    if paper.authors:
        st.markdown(f"**作者:** {', '.join(paper.authors)}")

    # 上传日期
    st.markdown(f"**上传时间:** {paper.upload_date.strftime('%Y-%m-%d %H:%M')}")

    # 标签
    paper_tags = db_manager.get_paper_tags(paper_id)
    if paper_tags:
        st.markdown("**标签:**")
        tags_html = " ".join([
            f'<span style="background-color: {tag.color}; color: white; padding: 4px 12px; border-radius: 4px; margin-right: 8px;">{tag.name}</span>'
            for tag in paper_tags
        ])
        st.markdown(tags_html, unsafe_allow_html=True)

    st.markdown("---")

    # 创建标签页
    tab1, tab2 = st.tabs(["📝 结构化笔记", "🗺️ 思维导图"])

    with tab1:
        show_structured_notes(paper)

    with tab2:
        show_mindmap(paper)


def show_structured_notes(paper):
    """显示结构化笔记"""
    if not paper.content_summary or 'summary_struct' not in paper.content_summary:
        st.warning("暂无结构化总结")
        return

    summary = paper.content_summary['summary_struct']
    summary_signature = json.dumps(summary, ensure_ascii=False, sort_keys=True)
    edited_summary_key = f"edited_summary_{paper.id}"
    edited_summary_signature_key = f"edited_summary_signature_{paper.id}"

    # 编辑模式切换
    col1, col2 = st.columns([6, 1])
    with col2:
        edit_mode = st.toggle("✏️ 编辑", key=f"edit_mode_{paper.id}")

    # 初始化编辑状态，或当数据库内容变化时刷新编辑缓存
    if (
        edited_summary_key not in st.session_state
        or st.session_state.get(edited_summary_signature_key) != summary_signature
    ):
        st.session_state[edited_summary_key] = copy.deepcopy(summary)
        st.session_state[edited_summary_signature_key] = summary_signature

    edited_summary = st.session_state[edited_summary_key]
    display_summary = edited_summary if edit_mode else summary

    # 定义各个部分的配置
    sections = [
        ('problem_definition', '🎯 研究问题', None),
        ('existing_solutions', '📚 相关工作', None),
        ('limitations', '⚠️ 现有方案的不足', None),
        ('contribution', '💡 本文贡献', None),
        ('methodology', '🔬 具体方法', 'architecture,algorithm'),
        ('results', '📊 实验结果', 'performance'),
        ('future_work_paper', '🔮 未来工作（论文提出）', None),
        ('future_work_insights', '💭 未来工作（个人见解）', None),
        # 向后兼容：如果是旧版本的 future_work 字段
        ('future_work', '🔮 未来工作', None)
    ]

    # 显示各个部分
    for section_key, section_title, image_type in sections:
        section_content = display_summary.get(section_key)
        if section_content:
            st.markdown(f"### {section_title}")

            if edit_mode:
                # 编辑模式：显示文本区域
                new_content = st.text_area(
                    f"编辑 {section_title}",
                    value=edited_summary.get(section_key, ""),
                    height=200,
                    key=f"edit_{section_key}_{paper.id}",
                    label_visibility="collapsed"
                )
                edited_summary[section_key] = new_content
            else:
                # 查看模式：显示 Markdown
                st.markdown(section_content)

            # 显示相关图片
            if image_type:
                # 在编辑模式下，显示图片上传功能
                if edit_mode:
                    st.markdown("**📎 上传图片:**")

                    # 使用唯一的 key 来标识上传状态
                    upload_key = f"upload_{section_key}_{paper.id}"
                    uploaded_file = st.file_uploader(
                        f"为 {section_title} 上传图片",
                        type=['png', 'jpg', 'jpeg'],
                        key=upload_key,
                        help="上传算法框架图、实验对比图等关键图片"
                    )

                    # 检查是否是新上传的文件（通过文件名和大小判断）
                    if uploaded_file:
                        # 生成文件的唯一标识
                        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
                        uploaded_files_key = f"uploaded_files_{paper.id}"

                        # 初始化已上传文件列表
                        if uploaded_files_key not in st.session_state:
                            st.session_state[uploaded_files_key] = set()

                        # 只有当文件未被处理过时才上传
                        if file_id not in st.session_state[uploaded_files_key]:
                            # 保存上传的图片
                            import config
                            import time

                            # 创建图片保存目录
                            images_dir = Path(config.IMAGES_DIR) / str(paper.id)
                            images_dir.mkdir(parents=True, exist_ok=True)

                            # 生成文件名（使用section_key和时间戳）
                            timestamp = int(time.time())
                            file_extension = uploaded_file.name.split('.')[-1]
                            image_filename = f"user_{section_key}_{timestamp}.{file_extension}"
                            image_path = images_dir / image_filename

                            # 保存文件
                            with open(image_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())

                            # 保存到数据库
                            image_types = [t.strip() for t in image_type.split(',')]
                            primary_type = image_types[0] if image_types else 'user_uploaded'
                            db_manager.add_image_to_paper(
                                paper.id,
                                str(image_path),
                                caption=f"用户上传 - {section_title}",
                                image_type=primary_type
                            )

                            # 标记文件已处理
                            st.session_state[uploaded_files_key].add(file_id)

                            st.success(f"✓ 图片已上传")
                            st.rerun()

                # 显示已有图片
                images = db_manager.get_paper_images(paper.id)
                # 支持多个图片类型（用逗号分隔）
                image_types = [t.strip() for t in image_type.split(',')]

                for img_type in image_types:
                    filtered_images = [img for img in images if img.image_type == img_type]
                    if filtered_images:
                        if img_type == 'architecture':
                            st.markdown("**系统架构图:**")
                        elif img_type == 'algorithm':
                            st.markdown("**算法流程图:**")
                        elif img_type == 'performance':
                            st.markdown("**性能对比图:**")

                        for idx, img in enumerate(filtered_images):
                            if Path(img.image_path).exists():
                                if edit_mode:
                                    # 编辑模式：显示图片和编辑控件
                                    st.image(img.image_path)
                                    col_caption, col_del = st.columns([5, 1])
                                    with col_caption:
                                        new_caption = st.text_input(
                                            "图片说明",
                                            value=img.caption or "",
                                            key=f"caption_{img.id}_{idx}",
                                            label_visibility="collapsed"
                                        )
                                        if new_caption != img.caption:
                                            if st.button("💾", key=f"save_caption_{img.id}_{idx}", help="保存图片说明"):
                                                db_manager.update_image_caption(img.id, new_caption)
                                                st.rerun()
                                    with col_del:
                                        if st.button("🗑️", key=f"del_img_{img.id}_{idx}", help="删除图片"):
                                            try:
                                                Path(img.image_path).unlink()
                                            except:
                                                pass
                                            db_manager.delete_image(img.id)
                                            st.rerun()
                                else:
                                    # 查看模式：只显示图片和标题
                                    st.image(img.image_path, caption=img.caption)

    # 保存按钮（仅在编辑模式下显示）
    if edit_mode:
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("💾 保存修改", type="primary", key=f"save_{paper.id}", use_container_width=True):
                # 更新数据库
                updated_summary = copy.deepcopy(edited_summary)
                paper.content_summary['summary_struct'] = updated_summary
                db_manager.update_paper_summary(paper.id, paper.content_summary)
                st.session_state[edited_summary_signature_key] = json.dumps(
                    updated_summary,
                    ensure_ascii=False,
                    sort_keys=True,
                )
                st.toast("✓ 修改已保存", icon="✅")
                st.rerun()
        with col2:
            if st.button("↩️ 重置", key=f"reset_{paper.id}", use_container_width=True):
                # 重置为原始内容
                st.session_state[edited_summary_key] = copy.deepcopy(summary)
                st.session_state[edited_summary_signature_key] = summary_signature
                st.rerun()


def show_mindmap(paper):
    """显示思维导图"""
    if not paper.mindmap_code:
        st.warning("暂无思维导图")
        return

    st.markdown("### 论文思维导图")

    # 提供渲染方式选择
    render_method = st.radio(
        "选择渲染方式",
        options=["HTML (推荐)", "Streamlit-Mermaid", "查看代码"],
        horizontal=True,
        key=f"mindmap_render_{paper.id}"
    )

    if render_method == "查看代码":
        st.code(paper.mindmap_code, language="mermaid")
        st.caption("💡 提示: 您可以复制代码到 https://mermaid.live 在线查看")
        return

    # 方法1: 使用 HTML iframe (最可靠)
    if render_method == "HTML (推荐)":
        try:
            mermaid_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            flowchart: {{ useMaxWidth: true }}
        }});
    </script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            background: white;
        }}
        .mermaid {{
            width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <div class="mermaid">
{paper.mindmap_code}
    </div>
</body>
</html>
"""
            st.components.v1.html(mermaid_html, height=800, scrolling=True)
            st.caption("✓ 使用 HTML 渲染")
        except Exception as e:
            st.error(f"HTML 渲染失败: {str(e)}")
            with st.expander("查看错误详情和代码"):
                st.text(f"错误: {str(e)}")
                st.code(paper.mindmap_code, language="mermaid")

    # 方法2: 使用 streamlit-mermaid
    elif render_method == "Streamlit-Mermaid":
        try:
            from streamlit_mermaid import st_mermaid
            st_mermaid(paper.mindmap_code, height=800)
            st.caption("✓ 使用 Streamlit-Mermaid 渲染")
        except ImportError:
            st.error("streamlit-mermaid 未安装，请运行: pip install streamlit-mermaid")
        except Exception as e:
            st.error(f"Streamlit-Mermaid 渲染失败: {str(e)}")
            with st.expander("查看错误详情和代码"):
                st.text(f"错误: {str(e)}")
                st.code(paper.mindmap_code, language="mermaid")

    # 添加重新生成按钮
    st.markdown("---")
    if st.button("🔄 重新生成思维导图", key=f"regenerate_mindmap_{paper.id}"):
        with st.spinner("正在重新生成思维导图..."):
            try:
                from services.mindmap_generator import mindmap_generator
                new_mindmap = mindmap_generator.generate_mindmap(paper.content_summary)
                if new_mindmap:
                    db_manager.update_paper(paper.id, mindmap_code=new_mindmap)
                    st.success("✓ 思维导图已重新生成")
                    st.rerun()
                else:
                    st.error("生成失败")
            except Exception as e:
                st.error(f"生成失败: {str(e)}")

