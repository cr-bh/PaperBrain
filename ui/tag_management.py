"""
标签管理页面
支持查看、编辑、删除、合并标签
"""
import streamlit as st
from database.db_manager import db_manager
from collections import defaultdict


def show_tag_management():
    """显示标签管理页面"""
    st.title("🏷️ 标签管理")
    st.markdown("管理所有论文标签，支持编辑、删除和合并重复标签")
    st.markdown("---")

    # 获取所有标签
    all_tags = db_manager.get_all_tags()

    if not all_tags:
        st.info("还没有标签")
        return

    # 按类别分组
    tags_by_category = defaultdict(list)
    for tag in all_tags:
        category = tag.category or 'uncategorized'
        tags_by_category[category].append(tag)

    # 显示统计信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("标签总数", len(all_tags))
    with col2:
        st.metric("类别数", len(tags_by_category))
    with col3:
        # 检测可能的重复标签（名称相似）
        potential_duplicates = find_potential_duplicates(all_tags)
        st.metric("可能重复", len(potential_duplicates))

    st.markdown("---")

    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["📋 所有标签", "🔍 查找重复", "➕ 添加标签"])

    with tab1:
        show_all_tags(tags_by_category)

    with tab2:
        show_duplicate_detection(all_tags, potential_duplicates)

    with tab3:
        show_add_tag_form()


def show_all_tags(tags_by_category):
    """显示所有标签，按类别和层级分组"""
    st.markdown("### 标签层级结构")

    # 类别映射
    category_names = {
        'domain': '📚 领域 (Domain)',
        'methodology': '🔬 方法 (Methodology)',
        'task': '🎯 任务 (Task)',
        'uncategorized': '❓ 未分类'
    }

    # 添加初始化按钮
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🔄 初始化标签层级", help="创建预定义的MECE标签结构"):
            from database.init_tag_hierarchy import init_tag_hierarchy
            init_tag_hierarchy()
            st.success("✓ 标签层级已初始化")
            st.rerun()

    st.markdown("---")

    for category, tags in sorted(tags_by_category.items()):
        category_display = category_names.get(category, category)

        # 构建树形结构
        parent_tags = [t for t in tags if t.parent_id is None]
        child_tags_map = defaultdict(list)
        for t in tags:
            if t.parent_id:
                child_tags_map[t.parent_id].append(t)

        with st.expander(f"{category_display} ({len(tags)} 个标签)", expanded=True):
            # 显示父标签和子标签
            for parent_tag in sorted(parent_tags, key=lambda t: t.name.lower()):
                show_tag_with_children(parent_tag, child_tags_map)


def show_tag_with_children(tag, child_tags_map):
    """显示标签及其子标签"""
    papers = db_manager.get_papers_by_tag(tag.id)
    paper_count = len(papers)
    children = child_tags_map.get(tag.id, [])

    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    with col1:
        # 父标签显示
        st.markdown(
            f'<span style="background-color: {tag.color}; color: white; '
            f'padding: 4px 12px; border-radius: 4px; margin-right: 8px; font-weight: bold;">'
            f'{tag.name}</span> <span style="color: gray;">({paper_count} 篇)</span>',
            unsafe_allow_html=True
        )

    with col2:
        if st.button("✏️", key=f"edit_{tag.id}", help="编辑标签"):
            st.session_state[f'editing_tag_{tag.id}'] = True
            st.rerun()

    with col3:
        if st.button("🗑️", key=f"delete_{tag.id}", help="删除标签", disabled=paper_count > 0 or len(children) > 0):
            if db_manager.delete_tag(tag.id):
                st.success(f"✓ 已删除标签: {tag.name}")
                st.rerun()

    with col4:
        # 合并按钮
        if st.button("🔗", key=f"merge_{tag.id}", help="合并到其他标签"):
            st.session_state[f'merging_tag_{tag.id}'] = True
            st.rerun()

    # 编辑表单
    if st.session_state.get(f'editing_tag_{tag.id}', False):
        with st.form(key=f"edit_form_{tag.id}"):
            st.markdown("**编辑标签**")
            new_name = st.text_input("标签名称", value=tag.name)
            new_category = st.selectbox(
                "类别",
                options=['domain', 'methodology', 'task'],
                index=['domain', 'methodology', 'task'].index(tag.category) if tag.category in ['domain', 'methodology', 'task'] else 0
            )
            new_color = st.color_picker("颜色", value=tag.color)

            # 获取所有可能的父标签（同类别的顶级标签，排除自己和自己的子标签）
            all_tags = db_manager.get_all_tags()
            # 排除自己和自己的子标签（防止循环引用）
            child_ids = [c.id for c in children]
            potential_parents = [t for t in all_tags if t.parent_id is None and t.category == new_category and t.id != tag.id and t.id not in child_ids]
            parent_options = ["无（保持为顶级标签）"] + [t.name for t in potential_parents]

            # 找到当前父标签的索引
            current_parent_index = 0
            if tag.parent_id:
                current_parent = db_manager.get_tag_by_id(tag.parent_id)
                if current_parent and current_parent.name in parent_options:
                    current_parent_index = parent_options.index(current_parent.name)

            new_parent_name = st.selectbox(
                "父标签",
                options=parent_options,
                index=current_parent_index,
                help="选择父标签以设置层级关系，或选择'无'保持为顶级标签"
            )

            col_a, col_b = st.columns(2)
            with col_a:
                if st.form_submit_button("💾 保存", use_container_width=True):
                    # 确定新的 parent_id
                    new_parent_id = None
                    if new_parent_name != "无（保持为顶级标签）":
                        new_parent = db_manager.get_tag_by_name(new_parent_name)
                        if new_parent:
                            new_parent_id = new_parent.id

                    db_manager.update_tag(tag.id, name=new_name, category=new_category, color=new_color, parent_id=new_parent_id)
                    st.session_state[f'editing_tag_{tag.id}'] = False
                    st.success("✓ 标签已更新")
                    st.rerun()
            with col_b:
                if st.form_submit_button("✗ 取消", use_container_width=True):
                    st.session_state[f'editing_tag_{tag.id}'] = False
                    st.rerun()

    # 显示子标签（缩进显示）
    if children:
        for child in sorted(children, key=lambda t: t.name.lower()):
            child_papers = db_manager.get_papers_by_tag(child.id)
            child_paper_count = len(child_papers)

            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                # 子标签显示（带缩进）
                st.markdown(
                    f'&nbsp;&nbsp;&nbsp;&nbsp;↳ <span style="background-color: {child.color}; color: white; '
                    f'padding: 2px 8px; border-radius: 3px; margin-right: 8px; font-size: 12px;">'
                    f'{child.name}</span> <span style="color: gray; font-size: 12px;">({child_paper_count} 篇)</span>',
                    unsafe_allow_html=True
                )

            with col2:
                if st.button("✏️", key=f"edit_{child.id}", help="编辑子标签"):
                    st.session_state[f'editing_tag_{child.id}'] = True
                    st.rerun()

            with col3:
                if st.button("🗑️", key=f"delete_{child.id}", help="删除子标签", disabled=child_paper_count > 0):
                    if db_manager.delete_tag(child.id):
                        st.success(f"✓ 已删除标签: {child.name}")
                        st.rerun()

            # 编辑表单（子标签）
            if st.session_state.get(f'editing_tag_{child.id}', False):
                with st.form(key=f"edit_form_{child.id}"):
                    st.markdown("**编辑子标签**")
                    new_name = st.text_input("标签名称", value=child.name)
                    new_category = st.selectbox(
                        "类别",
                        options=['domain', 'methodology', 'task'],
                        index=['domain', 'methodology', 'task'].index(child.category) if child.category in ['domain', 'methodology', 'task'] else 0
                    )
                    new_color = st.color_picker("颜色", value=child.color)

                    # 获取所有可能的父标签（同类别的顶级标签）
                    all_tags = db_manager.get_all_tags()
                    potential_parents = [t for t in all_tags if t.parent_id is None and t.category == new_category and t.id != child.id]
                    parent_options = ["无（设为顶级标签）"] + [t.name for t in potential_parents]

                    # 找到当前父标签的索引
                    current_parent_index = 0
                    if child.parent_id:
                        current_parent = db_manager.get_tag_by_id(child.parent_id)
                        if current_parent and current_parent.name in parent_options:
                            current_parent_index = parent_options.index(current_parent.name)

                    new_parent_name = st.selectbox(
                        "父标签",
                        options=parent_options,
                        index=current_parent_index,
                        help="选择父标签以设置层级关系，或选择'无'设为顶级标签"
                    )

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.form_submit_button("💾 保存", use_container_width=True):
                            # 确定新的 parent_id
                            new_parent_id = None
                            if new_parent_name != "无（设为顶级标签）":
                                new_parent = db_manager.get_tag_by_name(new_parent_name)
                                if new_parent:
                                    new_parent_id = new_parent.id

                            db_manager.update_tag(child.id, name=new_name, category=new_category, color=new_color, parent_id=new_parent_id)
                            st.session_state[f'editing_tag_{child.id}'] = False
                            st.success("✓ 标签已更新")
                            st.rerun()
                    with col_b:
                        if st.form_submit_button("✗ 取消", use_container_width=True):
                            st.session_state[f'editing_tag_{child.id}'] = False
                            st.rerun()

    st.markdown("---")


def show_duplicate_detection(all_tags, potential_duplicates):
    """显示重复标签检测"""
    st.markdown("### 🔍 重复标签检测")
    st.caption("基于名称相似度检测可能重复的标签")

    if not potential_duplicates:
        st.success("✓ 未发现明显重复的标签")
        return

    st.warning(f"发现 {len(potential_duplicates)} 组可能重复的标签")

    for group in potential_duplicates:
        with st.expander(f"相似标签组: {', '.join([t.name for t in group])}", expanded=True):
            st.markdown("**��些标签可能是重复的，建议合并：**")

            for tag in group:
                papers = db_manager.get_papers_by_tag(tag.id)
                st.markdown(
                    f'- <span style="background-color: {tag.color}; color: white; '
                    f'padding: 2px 8px; border-radius: 3px;">{tag.name}</span> '
                    f'({len(papers)} 篇论文)',
                    unsafe_allow_html=True
                )

            st.markdown("**合并操作：**")
            # 选择保留的标签
            keep_tag_name = st.selectbox(
                "保留哪个标签？",
                options=[t.name for t in group],
                key=f"keep_tag_{'_'.join([str(t.id) for t in group])}"
            )

            if st.button("🔗 合并到选中标签", key=f"merge_group_{'_'.join([str(t.id) for t in group])}", type="primary"):
                keep_tag = db_manager.get_tag_by_name(keep_tag_name)
                if keep_tag:
                    for tag in group:
                        if tag.id != keep_tag.id:
                            merge_tags(tag.id, keep_tag.id)
                    st.success(f"✓ 已合并到 '{keep_tag_name}'")
                    st.rerun()


def show_add_tag_form():
    """显示添加标签表单"""
    st.markdown("### ➕ 添加新标签")

    with st.form("add_tag_form"):
        tag_name = st.text_input("标签名称", placeholder="例如: Deep Learning")
        tag_category = st.selectbox(
            "类别",
            options=['domain', 'methodology', 'task'],
            format_func=lambda x: {'domain': '领域', 'methodology': '方法', 'task': '任务'}[x]
        )
        tag_color = st.color_picker("颜色", value="#3B82F6")

        if st.form_submit_button("➕ 添加标签", type="primary", use_container_width=True):
            if tag_name:
                # 检查是否已存在
                existing = db_manager.get_tag_by_name(tag_name)
                if existing:
                    st.error(f"标签 '{tag_name}' 已存在")
                else:
                    db_manager.create_tag(tag_name, category=tag_category, color=tag_color)
                    st.success(f"✓ 已添加标签: {tag_name}")
                    st.rerun()
            else:
                st.error("请输入标签名称")


def find_potential_duplicates(tags):
    """查找可能重复的标签"""
    duplicates = []
    checked = set()

    for i, tag1 in enumerate(tags):
        if tag1.id in checked:
            continue

        similar_group = [tag1]
        for tag2 in tags[i+1:]:
            if tag2.id in checked:
                continue

            # 检查名称相似度
            if are_similar(tag1.name, tag2.name):
                similar_group.append(tag2)
                checked.add(tag2.id)

        if len(similar_group) > 1:
            duplicates.append(similar_group)
            checked.add(tag1.id)

    return duplicates


def are_similar(name1, name2):
    """判断两个标签名称是否相似"""
    name1_lower = name1.lower().strip()
    name2_lower = name2.lower().strip()

    # 完全相同（忽略大小写）
    if name1_lower == name2_lower:
        return True

    # 一个是另一个的子串
    if name1_lower in name2_lower or name2_lower in name1_lower:
        return True

    # 移除常见分隔符后比较
    clean1 = name1_lower.replace('-', '').replace('_', '').replace(' ', '')
    clean2 = name2_lower.replace('-', '').replace('_', '').replace(' ', '')
    if clean1 == clean2:
        return True

    # 简单的编辑距离检查（针对拼写错误）
    if len(name1_lower) > 3 and len(name2_lower) > 3:
        if levenshtein_distance(name1_lower, name2_lower) <= 2:
            return True

    return False


def levenshtein_distance(s1, s2):
    """计算编辑距离"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def merge_tags(source_tag_id, target_tag_id):
    """合并标签：将source_tag的所有论文关联转移到target_tag，然后删除source_tag"""
    # 获取使用source_tag的所有论文
    papers = db_manager.get_papers_by_tag(source_tag_id)

    # 将这些论文关联到target_tag
    for paper in papers:
        # 先移除旧标签
        db_manager.remove_tag_from_paper(paper.id, source_tag_id)
        # 添加新标签（如果还没有）
        db_manager.add_tag_to_paper(paper.id, target_tag_id)

    # 删除source_tag
    db_manager.delete_tag(source_tag_id)
