"""
API 配置管理器
管理 LLM API 的配置，支持标准提供商（OpenAI兼容）和自定义内部 API
配置持久化到 data/api_config.json，回退到 .env 环境变量
"""
import json
import copy
from pathlib import Path
from typing import Dict, Any, Optional, List

CONFIG_FILE = Path(__file__).parent.parent / 'data' / 'api_config.json'

# ========== 预设提供商列表（均为 OpenAI 兼容格式）==========

PROVIDERS: Dict[str, Dict[str, Any]] = {
    "deepseek": {
        "name": "DeepSeek",
        "api_base": "https://api.deepseek.com/v1/chat/completions",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "default_model": "deepseek-chat",
        "doc_url": "https://platform.deepseek.com/api_keys",
    },
    "qianwen": {
        "name": "通义千问 (Qwen)",
        "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "models": ["qwen-plus", "qwen-turbo", "qwen-max", "qwen-long"],
        "default_model": "qwen-plus",
        "doc_url": "https://dashscope.console.aliyun.com/apiKey",
    },
    "openai": {
        "name": "OpenAI",
        "api_base": "https://api.openai.com/v1/chat/completions",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "default_model": "gpt-4o-mini",
        "doc_url": "https://platform.openai.com/api-keys",
    },
    "moonshot": {
        "name": "Moonshot (月之暗面)",
        "api_base": "https://api.moonshot.cn/v1/chat/completions",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "default_model": "moonshot-v1-32k",
        "doc_url": "https://platform.moonshot.cn/console/api-keys",
    },
    "zhipu": {
        "name": "智谱 (GLM)",
        "api_base": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "models": ["glm-4-plus", "glm-4", "glm-4-flash"],
        "default_model": "glm-4-flash",
        "doc_url": "https://open.bigmodel.cn/usercenter/apikeys",
    },
    "siliconflow": {
        "name": "SiliconFlow (硅基流动)",
        "api_base": "https://api.siliconflow.cn/v1/chat/completions",
        "models": [
            "deepseek-ai/DeepSeek-V3",
            "Qwen/Qwen2.5-72B-Instruct",
            "Pro/deepseek-ai/DeepSeek-R1",
        ],
        "default_model": "deepseek-ai/DeepSeek-V3",
        "doc_url": "https://cloud.siliconflow.cn/account/ak",
    },
}

# ========== 默认配置模板 ==========

DEFAULT_LLM_CONFIG = {
    "mode": "standard",       # "standard" | "custom"
    "provider": "deepseek",
    "api_key": "",
    "model": "deepseek-chat",
    # custom mode fields
    "api_url": "",
    "api_token": "",
    "api_format": "openai",   # "openai" | "gemini"
    "custom_ssl": False,
    # generation params
    "temperature": 0.7,
    "max_tokens": 8192,
}

DEFAULT_CONFIG = {
    "main_llm": {
        **DEFAULT_LLM_CONFIG,
    },
    "scoring_llm": {
        "enabled": False,     # False = 复用主 LLM 配置
        **DEFAULT_LLM_CONFIG,
        "temperature": 0.3,
        "max_tokens": 4096,
    },
}


def _detect_env_api_format(api_url: str) -> str:
    """根据 .env 中的 URL 自动检测 API 格式"""
    url_lower = api_url.lower()
    if 'generatecontent' in url_lower or 'gemini' in url_lower:
        return 'gemini'
    return 'openai'


def _build_env_fallback() -> Optional[Dict[str, Any]]:
    """从 .env 环境变量构建回退配置（兼容现有用户）"""
    import config as env_config

    cfg = copy.deepcopy(DEFAULT_CONFIG)
    has_main = bool(env_config.LLM_API_URL and env_config.LLM_BEARER_TOKEN)
    has_scoring = bool(env_config.DOUBAO_API_URL and env_config.DOUBAO_BEARER_TOKEN)

    if not has_main and not has_scoring:
        return None

    if has_main:
        cfg['main_llm']['mode'] = 'custom'
        cfg['main_llm']['api_url'] = env_config.LLM_API_URL
        cfg['main_llm']['api_token'] = env_config.LLM_BEARER_TOKEN
        cfg['main_llm']['api_format'] = _detect_env_api_format(env_config.LLM_API_URL)
        cfg['main_llm']['custom_ssl'] = True
        cfg['main_llm']['temperature'] = env_config.TEMPERATURE
        cfg['main_llm']['max_tokens'] = env_config.MAX_TOKENS
        cfg['main_llm']['model'] = env_config.MODEL_NAME

    if has_scoring:
        cfg['scoring_llm']['enabled'] = True
        cfg['scoring_llm']['mode'] = 'custom'
        cfg['scoring_llm']['api_url'] = env_config.DOUBAO_API_URL
        cfg['scoring_llm']['api_token'] = env_config.DOUBAO_BEARER_TOKEN
        cfg['scoring_llm']['api_format'] = 'openai'
        cfg['scoring_llm']['custom_ssl'] = True
        cfg['scoring_llm']['model'] = 'Doubao-pro-128k'

    return cfg


def load_config() -> Dict[str, Any]:
    """
    加载 API 配置
    优先级: api_config.json > .env 环境变量 > 默认空配置
    """
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            merged = copy.deepcopy(DEFAULT_CONFIG)
            for role in ('main_llm', 'scoring_llm'):
                if role in saved:
                    merged[role].update(saved[role])
            return merged
        except (json.JSONDecodeError, IOError):
            pass

    env_cfg = _build_env_fallback()
    if env_cfg:
        return env_cfg

    return copy.deepcopy(DEFAULT_CONFIG)


def save_config(cfg: Dict[str, Any]) -> None:
    """保存 API 配置到 JSON 文件"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_role_config(role: str) -> Dict[str, Any]:
    """
    获取指定角色的有效配置
    如果 scoring_llm 未独立启用，则回退到 main_llm 配置
    """
    cfg = load_config()
    if role == 'scoring_llm' and not cfg['scoring_llm'].get('enabled', False):
        role_cfg = copy.deepcopy(cfg['main_llm'])
        role_cfg['temperature'] = cfg['scoring_llm'].get('temperature', 0.3)
        role_cfg['max_tokens'] = cfg['scoring_llm'].get('max_tokens', 4096)
        return role_cfg
    return cfg.get(role, copy.deepcopy(DEFAULT_LLM_CONFIG))


def get_effective_api_params(role: str) -> Dict[str, Any]:
    """
    解析角色配置，返回实际调用 API 所需的参数
    Returns: {api_url, api_token, model, api_format, custom_ssl, temperature, max_tokens}
    """
    role_cfg = get_role_config(role)
    mode = role_cfg.get('mode', 'standard')

    if mode == 'standard':
        provider_key = role_cfg.get('provider', 'deepseek')
        provider = PROVIDERS.get(provider_key)
        if not provider:
            return {'configured': False, 'error': f'未知的提供商: {provider_key}'}
        api_key = role_cfg.get('api_key', '')
        if not api_key:
            return {'configured': False, 'error': '未设置 API Key'}
        return {
            'configured': True,
            'api_url': provider['api_base'],
            'api_token': api_key,
            'model': role_cfg.get('model', provider['default_model']),
            'api_format': 'openai',
            'custom_ssl': False,
            'temperature': role_cfg.get('temperature', 0.7),
            'max_tokens': role_cfg.get('max_tokens', 8192),
        }
    else:
        api_url = role_cfg.get('api_url', '')
        api_token = role_cfg.get('api_token', '')
        if not api_url or not api_token:
            return {'configured': False, 'error': '未设置自定义 API URL 或 Token'}
        return {
            'configured': True,
            'api_url': api_url,
            'api_token': api_token,
            'model': role_cfg.get('model', ''),
            'api_format': role_cfg.get('api_format', 'openai'),
            'custom_ssl': role_cfg.get('custom_ssl', False),
            'temperature': role_cfg.get('temperature', 0.7),
            'max_tokens': role_cfg.get('max_tokens', 8192),
        }


def is_configured(role: str = 'main_llm') -> bool:
    """检查指定角色是否已配置"""
    params = get_effective_api_params(role)
    return params.get('configured', False)


def get_provider_list() -> List[Dict[str, str]]:
    """获取提供商列表，用于 UI 展示"""
    return [
        {"key": k, "name": v["name"], "doc_url": v.get("doc_url", "")}
        for k, v in PROVIDERS.items()
    ]
