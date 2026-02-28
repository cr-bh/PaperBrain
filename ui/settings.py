"""
API 设置页面
提供图形化界面配置 LLM API，支持标准提供商和自定义内部 API
"""
import streamlit as st
from services.api_config import (
    PROVIDERS, load_config, save_config, get_effective_api_params,
)


def _render_llm_config(role: str, role_label: str, cfg: dict) -> dict:
    """
    渲染单个 LLM 角色的配置表单
    Returns: 更新后的配置 dict
    """
    mode = cfg.get('mode', 'standard')

    mode_options = ["标准模式（推荐）", "自定义模式"]
    mode_map = {"标准模式（推荐）": "standard", "自定义模式": "custom"}
    reverse_map = {"standard": "标准模式（推荐）", "custom": "自定义模式"}
    selected_mode = st.radio(
        "API 接入方式",
        mode_options,
        index=mode_options.index(reverse_map.get(mode, "标准模式（推荐）")),
        key=f"{role}_mode",
        horizontal=True,
        help="标准模式：选择主流 API 提供商，填入 API Key 即可使用\n\n"
             "自定义模式：手动配置 API 地址和认证信息（适用于内部部署或私有 API）",
    )
    cfg['mode'] = mode_map[selected_mode]

    st.markdown("---")

    if cfg['mode'] == 'standard':
        _render_standard_mode(role, cfg)
    else:
        _render_custom_mode(role, cfg)

    st.markdown("---")

    # 通用参数
    col1, col2 = st.columns(2)
    with col1:
        cfg['temperature'] = st.slider(
            "Temperature",
            0.0, 2.0, float(cfg.get('temperature', 0.7)), 0.1,
            key=f"{role}_temp",
            help="值越低输出越确定，值越高输出越多样化。论文总结建议 0.3-0.7",
        )
    with col2:
        cfg['max_tokens'] = st.number_input(
            "Max Tokens",
            256, 131072, int(cfg.get('max_tokens', 8192)), 1024,
            key=f"{role}_max_tokens",
            help="单次生成的最大 token 数。结构化摘要建议 8192+",
        )

    return cfg


def _render_standard_mode(role: str, cfg: dict) -> None:
    """渲染标准模式（选择提供商 + 填 API Key）"""
    provider_keys = list(PROVIDERS.keys())
    provider_names = [PROVIDERS[k]['name'] for k in provider_keys]

    current_provider = cfg.get('provider', 'deepseek')
    if current_provider not in provider_keys:
        current_provider = 'deepseek'
    provider_idx = provider_keys.index(current_provider)

    selected_name = st.selectbox(
        "API 提供商",
        provider_names,
        index=provider_idx,
        key=f"{role}_provider",
    )
    selected_key = provider_keys[provider_names.index(selected_name)]
    cfg['provider'] = selected_key
    provider = PROVIDERS[selected_key]

    doc_url = provider.get('doc_url', '')
    if doc_url:
        st.caption(f"获取 API Key：[{provider['name']} 控制台]({doc_url})")

    cfg['api_key'] = st.text_input(
        "API Key",
        value=cfg.get('api_key', ''),
        type="password",
        key=f"{role}_api_key",
        placeholder="sk-... 或你的 API Key",
    )

    models = provider.get('models', [])
    current_model = cfg.get('model', provider.get('default_model', ''))
    if current_model in models:
        model_idx = models.index(current_model)
    else:
        model_idx = 0

    col1, col2 = st.columns([3, 2])
    with col1:
        selected_model = st.selectbox(
            "模型",
            models,
            index=model_idx,
            key=f"{role}_model_select",
        )
    with col2:
        custom_model = st.text_input(
            "或自定义模型名",
            value="" if selected_model else current_model,
            key=f"{role}_model_custom",
            placeholder="留空则使用左侧选项",
        )
    cfg['model'] = custom_model.strip() if custom_model.strip() else selected_model


def _render_custom_mode(role: str, cfg: dict) -> None:
    """渲染自定义模式（手动填 URL + Token）"""
    st.info(
        "自定义模式适用于公司内部 API、私有部署、或其他非标准接口。"
        "支持 OpenAI 兼容格式和 Gemini generateContent 格式。"
    )

    cfg['api_url'] = st.text_input(
        "API URL",
        value=cfg.get('api_url', ''),
        key=f"{role}_api_url",
        placeholder="https://your-api.com/v1/chat/completions",
    )

    cfg['api_token'] = st.text_input(
        "API Token / Bearer Token",
        value=cfg.get('api_token', ''),
        type="password",
        key=f"{role}_api_token",
        placeholder="your_bearer_token_here",
    )

    col1, col2 = st.columns(2)
    with col1:
        format_options = ["OpenAI 兼容格式", "Gemini 格式"]
        format_map = {"OpenAI 兼容格式": "openai", "Gemini 格式": "gemini"}
        reverse_fmt = {"openai": "OpenAI 兼容格式", "gemini": "Gemini 格式"}
        current_fmt = cfg.get('api_format', 'openai')
        selected_fmt = st.selectbox(
            "API 格式",
            format_options,
            index=format_options.index(reverse_fmt.get(current_fmt, "OpenAI 兼容格式")),
            key=f"{role}_api_format",
            help="OpenAI 兼容：使用 messages 数组格式（大部分 API 都兼容）\n\n"
                 "Gemini 格式：使用 contents/parts 格式（Google Gemini 原生接口）",
        )
        cfg['api_format'] = format_map[selected_fmt]
    with col2:
        cfg['model'] = st.text_input(
            "模型名称",
            value=cfg.get('model', ''),
            key=f"{role}_custom_model",
            placeholder="gemini-pro / gpt-4o / ...",
        )

    cfg['custom_ssl'] = st.checkbox(
        "使用自定义 SSL 配置（解决内部 API 证书问题）",
        value=cfg.get('custom_ssl', False),
        key=f"{role}_custom_ssl",
        help="启用后会降低 SSL 安全级别并跳过证书验证，仅建议在内部网络使用",
    )


def _test_connection(role: str) -> None:
    """测试 API 连接"""
    from services.llm_service import LLMService
    with st.spinner("正在测试连接..."):
        test_service = LLMService(role=role)
        result = test_service.test_connection()

    if result['success']:
        st.success(
            f"连接成功！ 模型: `{result['model']}` | "
            f"格式: `{result['format']}`\n\n"
            f"回复: {result['message']}"
        )
    else:
        st.error(f"连接失败：{result['message']}")


def show_settings():
    """显示设置页面"""
    st.title("⚙️ 设置")

    cfg = load_config()

    # ==================== 主 LLM 配置 ====================
    st.header("🧠 主 LLM 配置")
    st.caption("用于论文总结、思维导图生成、标签生成、RAG 对话问答")

    cfg['main_llm'] = _render_llm_config('main_llm', '主 LLM', cfg['main_llm'])

    col_test, col_save = st.columns([1, 1])
    with col_test:
        if st.button("🔗 测试主 LLM 连接", key="test_main", use_container_width=True):
            save_config(cfg)
            _test_connection('main_llm')
    with col_save:
        if st.button("💾 保存主 LLM 配置", key="save_main", type="primary",
                      use_container_width=True):
            save_config(cfg)
            _reload_services()
            st.success("主 LLM 配置已保存并生效！")

    st.markdown("---")

    # ==================== 评分 LLM 配置 ====================
    st.header("⭐ 评分 LLM 配置")
    st.caption("用于 Auto-Scholar 论文评分和 PDF 元数据提取")

    scoring_enabled = st.checkbox(
        "独立配置评分 LLM（不勾选则复用主 LLM）",
        value=cfg['scoring_llm'].get('enabled', False),
        key="scoring_enabled",
        help="如果你的评分服务使用不同的 API（如豆包），请勾选并单独配置",
    )
    cfg['scoring_llm']['enabled'] = scoring_enabled

    if scoring_enabled:
        cfg['scoring_llm'] = _render_llm_config(
            'scoring_llm', '评分 LLM', cfg['scoring_llm']
        )
        cfg['scoring_llm']['enabled'] = True

        col_test2, col_save2 = st.columns([1, 1])
        with col_test2:
            if st.button("🔗 测试评分 LLM 连接", key="test_scoring",
                          use_container_width=True):
                save_config(cfg)
                _test_connection('scoring_llm')
        with col_save2:
            if st.button("💾 保存评分 LLM 配置", key="save_scoring", type="primary",
                          use_container_width=True):
                save_config(cfg)
                _reload_services()
                st.success("评分 LLM 配置已保存并生效！")
    else:
        st.info("评分 LLM 将复用主 LLM 配置（推荐：只需配置一个 API 即可）")
        if st.button("💾 保存配置", key="save_scoring_reuse", type="primary"):
            save_config(cfg)
            _reload_services()
            st.success("配置已保存！评分 LLM 将使用主 LLM 的 API。")

    st.markdown("---")

    # ==================== 当前配置状态 ====================
    st.header("📊 当前配置状态")
    _render_config_status()


def _reload_services() -> None:
    """重新加载全局服务实例"""
    try:
        from services.llm_service import llm_service
        llm_service.reload()
    except Exception:
        pass
    try:
        from services.doubao_service import doubao_service
        doubao_service.reload()
    except Exception:
        pass


def _render_config_status() -> None:
    """渲染配置状态总览"""
    main_params = get_effective_api_params('main_llm')
    scoring_params = get_effective_api_params('scoring_llm')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧠 主 LLM")
        if main_params.get('configured'):
            st.success("已配置")
            st.markdown(f"- **API 地址**: `{_mask_url(main_params['api_url'])}`")
            st.markdown(f"- **模型**: `{main_params.get('model', '-')}`")
            st.markdown(f"- **格式**: `{main_params.get('api_format', '-')}`")
            st.markdown(f"- **Temperature**: `{main_params.get('temperature', '-')}`")
        else:
            st.error(f"未配置: {main_params.get('error', '未知错误')}")

    with col2:
        st.subheader("⭐ 评分 LLM")
        if scoring_params.get('configured'):
            st.success("已配置")
            same_as_main = (
                scoring_params.get('api_url') == main_params.get('api_url')
                and scoring_params.get('api_token') == main_params.get('api_token')
            )
            if same_as_main:
                st.caption("（复用主 LLM）")
            st.markdown(f"- **API 地址**: `{_mask_url(scoring_params['api_url'])}`")
            st.markdown(f"- **模型**: `{scoring_params.get('model', '-')}`")
            st.markdown(f"- **格式**: `{scoring_params.get('api_format', '-')}`")
            st.markdown(f"- **Temperature**: `{scoring_params.get('temperature', '-')}`")
        else:
            st.error(f"未配置: {scoring_params.get('error', '未知错误')}")


def _mask_url(url: str) -> str:
    """遮蔽 URL 中的敏感信息，只显示域名部分"""
    if not url:
        return "-"
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.hostname}/..."
    except Exception:
        return url[:30] + "..."
