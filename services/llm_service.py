"""
LLM 服务封装
封装 Gemini API 调用（支持自定义 API 端点）
"""
import requests
import config
from typing import Dict, Any
from utils.helpers import retry_on_error
import json


class LLMService:
    """LLM 服务类"""

    def __init__(self):
        """初始化 LLM 服务"""
        self.api_url = config.LLM_API_URL
        self.bearer_token = config.LLM_BEARER_TOKEN

        if not self.api_url or not self.bearer_token:
            raise ValueError("LLM API 配置未设置，请在 .env 文件中配置 LLM_API_URL 和 LLM_BEARER_TOKEN")

    def _extract_text(self, lst):
        """从流式响应中提取所有文本块并合并"""
        combined_text = ""
        if lst is None:
            return ""
        for item in lst:
            if 'candidates' in item and item['candidates']:
                candidate = item['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    for part in parts:
                        if 'text' in part:
                            combined_text += part['text']
        return combined_text

    def _call_api(self, prompt: str, temperature: float = None,
                  max_tokens: int = None) -> str:
        """
        调用 Gemini API

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

        # 使用 Gemini API 格式（contents 和 parts 是对象，不是数组）
        payload = {
            "contents": {
                "role": "user",
                "parts": {
                    "text": prompt
                }
            },
            "safetySettings": {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_LOW_AND_ABOVE"
            },
            "generationConfig": {
                "temperature": temperature or config.TEMPERATURE,
                "topP": 1.0,
                "maxOutputTokens": max_tokens or config.MAX_TOKENS
            }
        }

        # 使用 UTF-8 编码发送
        json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        response = requests.post(self.api_url, headers=headers, data=json_data, timeout=120)
        response.raise_for_status()

        result = response.json()

        # 解析 Gemini 响应格式
        if isinstance(result, list):
            return self._extract_text(result)
        elif isinstance(result, dict) and 'candidates' in result:
            return self._extract_text([result])
        else:
            raise ValueError(f"API 响应格式不正确: {json.dumps(result, ensure_ascii=False)[:500]}")

    @retry_on_error(max_retries=3, delay=2.0)
    def generate_text(self, prompt: str, temperature: float = None,
                     max_tokens: int = None) -> str:
        """
        生成文本

        Args:
            prompt: 提示词
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            生成的文本
        """
        return self._call_api(prompt, temperature, max_tokens)

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
        from utils.helpers import extract_json_from_text

        text = self._call_api(prompt, temperature)

        # 尝试从响应中提取 JSON
        return extract_json_from_text(text)

    def count_tokens(self, text: str) -> int:
        """
        计算文本的 token 数量（简单估算）

        Args:
            text: 输入文本

        Returns:
            token 数量
        """
        # 简单估算：中文约 1.5 字符/token，英文约 4 字符/token
        # 这是一个粗略估算，实际 token 数可能有差异
        return len(text) // 2


# 创建全局 LLM 服务实例
llm_service = LLMService()
