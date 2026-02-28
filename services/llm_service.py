"""
LLM 服务封装
支持 OpenAI 兼容格式（DeepSeek/通义千问/OpenAI 等）和 Gemini 格式（自定义内部 API）
配置从 api_config 读取，支持运行时重载
"""
import requests
import json
import urllib3
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from utils.helpers import retry_on_error

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SSLAdapter(HTTPAdapter):
    """自定义 SSL 适配器，解决内部 API 的 SSL 证书验证问题"""

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)


class LLMService:
    """
    统一 LLM 服务类
    支持两种 API 格式：
    - openai: OpenAI Chat Completions 兼容格式（DeepSeek/通义千问/OpenAI 等）
    - gemini: Google Gemini generateContent 格式（自定义内部 API）
    """

    def __init__(self, role: str = 'main_llm'):
        self.role = role
        self._api_url: str = ''
        self._api_token: str = ''
        self._model: str = ''
        self._api_format: str = 'openai'
        self._custom_ssl: bool = False
        self._temperature: float = 0.7
        self._max_tokens: int = 8192
        self._configured: bool = False
        self._session: Optional[requests.Session] = None
        self._load_config()

    def _load_config(self) -> None:
        """从 api_config 加载配置"""
        from services.api_config import get_effective_api_params
        params = get_effective_api_params(self.role)

        if not params.get('configured', False):
            self._configured = False
            return

        self._api_url = params['api_url']
        self._api_token = params['api_token']
        self._model = params.get('model', '')
        self._api_format = params.get('api_format', 'openai')
        self._custom_ssl = params.get('custom_ssl', False)
        self._temperature = params.get('temperature', 0.7)
        self._max_tokens = params.get('max_tokens', 8192)
        self._configured = True
        self._init_session()

    def _init_session(self) -> None:
        """初始化 HTTP Session"""
        self._session = requests.Session()
        if self._custom_ssl:
            self._session.mount('https://', SSLAdapter())
            self._session.verify = False
        else:
            self._session.verify = True

    def reload(self) -> None:
        """重新加载配置（设置页面保存后调用）"""
        self._load_config()

    def is_configured(self) -> bool:
        return self._configured

    def _ensure_configured(self) -> None:
        if not self._configured:
            self._load_config()
        if not self._configured:
            raise ValueError(
                "LLM API 未配置。请前往「⚙️ 设置」页面配置 API，"
                "或在 .env 文件中设置 LLM_API_URL 和 LLM_BEARER_TOKEN。"
            )

    # ========== OpenAI 兼容格式 ==========

    def _call_openai_api(self, prompt: str, temperature: float,
                         max_tokens: int) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json; charset=utf-8",
        }
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        response = self._session.post(
            self._api_url, headers=headers, data=json_data, timeout=120
        )
        response.raise_for_status()
        result = response.json()

        try:
            return result['choices'][0]['message']['content']
        except (KeyError, IndexError) as e:
            raise ValueError(
                f"API 响应格式不正确: {e}。"
                f"响应: {json.dumps(result, ensure_ascii=False)[:500]}"
            )

    # ========== Gemini 格式 ==========

    def _extract_gemini_text(self, lst) -> str:
        combined_text = ""
        if lst is None:
            return ""
        for item in lst:
            if 'candidates' in item and item['candidates']:
                candidate = item['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    for part in candidate['content']['parts']:
                        if 'text' in part:
                            combined_text += part['text']
        return combined_text

    def _call_gemini_api(self, prompt: str, temperature: float,
                         max_tokens: int) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json; charset=utf-8",
        }
        payload = {
            "contents": {
                "role": "user",
                "parts": {"text": prompt},
            },
            "safetySettings": {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_LOW_AND_ABOVE",
            },
            "generationConfig": {
                "temperature": temperature,
                "topP": 1.0,
                "maxOutputTokens": max_tokens,
            },
        }
        json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        response = self._session.post(
            self._api_url, headers=headers, data=json_data, timeout=120
        )
        response.raise_for_status()
        result = response.json()

        if isinstance(result, list):
            return self._extract_gemini_text(result)
        elif isinstance(result, dict) and 'candidates' in result:
            return self._extract_gemini_text([result])
        else:
            raise ValueError(
                f"API 响应格式不正确: {json.dumps(result, ensure_ascii=False)[:500]}"
            )

    # ========== 统一调用入口 ==========

    def _call_api(self, prompt: str, temperature: float = None,
                  max_tokens: int = None) -> str:
        self._ensure_configured()
        temp = temperature if temperature is not None else self._temperature
        tokens = max_tokens if max_tokens is not None else self._max_tokens

        if self._api_format == 'gemini':
            return self._call_gemini_api(prompt, temp, tokens)
        else:
            return self._call_openai_api(prompt, temp, tokens)

    @retry_on_error(max_retries=3, delay=2.0)
    def generate_text(self, prompt: str, temperature: float = None,
                      max_tokens: int = None) -> str:
        return self._call_api(prompt, temperature, max_tokens)

    @retry_on_error(max_retries=3, delay=2.0)
    def generate_json(self, prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        from utils.helpers import extract_json_from_text
        text = self._call_api(prompt, temperature)
        return extract_json_from_text(text)

    def count_tokens(self, text: str) -> int:
        return len(text) // 2

    def test_connection(self) -> Dict[str, Any]:
        """测试 API 连接，返回 {success: bool, message: str, model: str}"""
        try:
            self._ensure_configured()
            response = self._call_api("请回复：连接测试成功", temperature=0.1, max_tokens=50)
            return {
                'success': True,
                'message': response.strip()[:100],
                'model': self._model,
                'format': self._api_format,
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)[:300],
                'model': self._model,
                'format': self._api_format,
            }


# 创建全局 LLM 服务实例（允许未配置时也能正常导入）
def _create_service(role: str) -> 'LLMService':
    try:
        return LLMService(role=role)
    except Exception:
        svc = object.__new__(LLMService)
        svc.role = role
        svc._api_url = ''
        svc._api_token = ''
        svc._model = ''
        svc._api_format = 'openai'
        svc._custom_ssl = False
        svc._temperature = 0.7
        svc._max_tokens = 8192
        svc._configured = False
        svc._session = None
        return svc


llm_service = _create_service('main_llm')
