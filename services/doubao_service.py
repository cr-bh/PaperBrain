"""
豆包 LLM 服务封装
专门用于 Auto-Scholar 论文评分
"""
import requests
import config
from typing import Dict, Any
from utils.helpers import retry_on_error, extract_json_from_text
import json
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

# 禁用 SSL 警告（因为我们使用自定义 SSL 配置）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SSLAdapter(HTTPAdapter):
    """自定义 SSL 适配器，解决豆包 API 的 SSL 证书验证问题"""

    def init_poolmanager(self, *args, **kwargs):
        """初始化连接池管理器，使用宽松的 SSL 配置"""
        context = create_urllib3_context()
        # 降低 SSL 安全级别以兼容豆包 API
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)


class DoubaoService:
    """豆包 LLM 服务类（专用于论文评分）"""

    def __init__(self):
        """初始化豆包服务"""
        self.api_url = config.DOUBAO_API_URL
        self.bearer_token = config.DOUBAO_BEARER_TOKEN

        if not self.api_url or not self.bearer_token:
            raise ValueError("豆包 API 配置未设置，请在 .env 文件中配置 DOUBAO_API_URL 和 DOUBAO_BEARER_TOKEN")

        # 创建一个持久的 Session，使用自定义 SSL 配置
        self.session = requests.Session()
        self.session.mount('https://', SSLAdapter())
        # 禁用 SSL 验证（因为豆包 API 的证书有问题）
        self.session.verify = False

    def _call_api(self, prompt: str, temperature: float = 0.3,
                  max_tokens: int = 4096) -> str:
        """
        调用豆包 API (OpenAI 格式)

        Args:
            prompt: 提示词
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            生成的文本
        """
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        # 使用 OpenAI 格式的 payload
        payload = {
            "model": "Doubao-pro-128k",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # 确保使用 UTF-8 编码
        json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')

        # 使用 Session 对象发送请求（已配置自定义 SSL）
        response = self.session.post(self.api_url, headers=headers, data=json_data, timeout=120)
        response.raise_for_status()

        result = response.json()

        # 解析 OpenAI 格式的响应
        try:
            content = result['choices'][0]['message']['content']
            return content
        except (KeyError, IndexError) as e:
            raise ValueError(f"API 响应格式不正确: {e}。实际响应: {json.dumps(result, ensure_ascii=False)[:500]}")

    @retry_on_error(max_retries=3, delay=2.0)
    def generate_json(self, prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        """
        生成 JSON 格式的响应

        Args:
            prompt: 提示词
            temperature: 温度参数（较低以获得更稳定的 JSON）

        Returns:
            解析后的 JSON 对象
        """
        text = self._call_api(prompt, temperature)

        # 尝试从响应中提取 JSON
        return extract_json_from_text(text)


# 创建全局豆包服务实例
doubao_service = DoubaoService()
