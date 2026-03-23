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
        # 部分模型（如 qwen3 系列）在 non-streaming 模式下存在输出为空的问题，
        # 对这类模型统一使用 streaming 模式采集完整内容
        use_stream = self._should_use_stream()
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": use_stream,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')

        if use_stream:
            return self._call_openai_api_stream(headers, json_data)

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

    def _should_use_stream(self) -> bool:
        """判断是否需要使用 streaming 模式。
        qwen3 系列模型在部分接口的 non-streaming 模式下存在输出为空的问题。
        """
        model_lower = self._model.lower()
        return 'qwen3' in model_lower

    def _preprocess_prompt_for_model(self, prompt: str) -> str:
        """针对特定模型对 prompt 进行预处理。

        qwen3 系列问题根因（两层）：
        1. JSON 模板出现在论文内容之前时，qwen3 将其视为「最终输出」直接复制，不读论文
        2. summary_struct 嵌套结构导致 qwen3 只填 title/authors，嵌套字段留空

        修复：
        1. 将 JSON 格式要求移到论文内容之后
        2. 将 summary_struct 的嵌套字段展开为顶层字段，调用后在 _postprocess_qwen3 中重新包装
        """
        if 'qwen3' not in self._model.lower():
            return prompt

        json_start = prompt.find('{')
        paper_text_marker = '论文全文：'
        paper_text_pos = prompt.rfind(paper_text_marker)

        if json_start == -1 or paper_text_pos == -1 or json_start >= paper_text_pos:
            return prompt

        # qwen3 对包含复杂 Markdown 格式指令（**粗体**、有序列表、`代码`、**输出格式** 等）
        # 的 prompt 会直接输出空 JSON，不阅读论文内容。
        # 对 qwen3 使用极简指令，完全绕过原有复杂指令。
        instructions = (
            '你是学术研究专家。请仔细阅读以下论文，用中文详细分析。'
            'title 填论文的实际标题（原文，不要解释），'
            'authors 填作者列表，'
            '其余字段每个至少100字的详细分析。'
        )

        # paper_part 从「论文全文：」开始，去掉末尾的「记住：」指令行（如果有）
        paper_part_raw = prompt[paper_text_pos:]
        remember_marker = '记住：仅输出有效的 JSON'
        remember_pos = paper_part_raw.find(remember_marker)
        paper_part = paper_part_raw[:remember_pos].rstrip() if remember_pos != -1 else paper_part_raw

        # qwen3 在 Friday 接口上对超过约 3500 tokens 的 prompt 直接输出空 JSON
        # 安全阈值：论文文本截断到 8000 字符（约 2700 tokens），加上指令约 3000 tokens 以内
        QWEN3_MAX_PAPER_CHARS = 8000
        paper_header = '论文全文：'
        paper_content_start = paper_part.find(paper_header)
        if paper_content_start != -1:
            paper_content = paper_part[paper_content_start + len(paper_header):]
            if len(paper_content) > QWEN3_MAX_PAPER_CHARS:
                paper_content = paper_content[:QWEN3_MAX_PAPER_CHARS] + '\n\n[文本已截断，请基于以上内容分析]'
                paper_part = paper_header + paper_content

        # 扁平化 JSON 模板：将 summary_struct 嵌套字段展开到顶层
        # qwen3 对嵌套 JSON 字段不填充，但对顶层字段能正常工作
        flat_schema = (
            '{\n'
            '  "title": "",\n'
            '  "authors": [],\n'
            '  "one_sentence_summary": "",\n'
            '  "problem_definition": "",\n'
            '  "existing_solutions": "",\n'
            '  "limitations": "",\n'
            '  "contribution": "",\n'
            '  "methodology": "",\n'
            '  "results": "",\n'
            '  "future_work_paper": "",\n'
            '  "future_work_insights": ""\n'
            '}'
        )

        # 重排：指令 → 论文内容 → 扁平 JSON 格式要求
        return (
            instructions + '\n\n'
            + paper_part + '\n\n'
            + '请根据上面的论文内容，详细填写以下 JSON 的每个字段（每字段至少 100 字），'
            '仅输出 JSON，不要有其他文字：\n'
            + flat_schema
        )

    def _postprocess_qwen3_response(self, text: str) -> str:
        """将 qwen3 返回的扁平 JSON 重新包装为标准的嵌套格式（含 summary_struct）。"""
        import json as _json
        try:
            flat = _json.loads(text)
        except Exception:
            return text  # 解析失败，原样返回

        # 如果已经是标准格式（含 summary_struct），不需要转换
        if 'summary_struct' in flat:
            return text

        summary_fields = [
            'one_sentence_summary', 'problem_definition', 'existing_solutions',
            'limitations', 'contribution', 'methodology', 'results',
            'future_work_paper', 'future_work_insights'
        ]
        summary_struct = {k: flat.pop(k, '') for k in summary_fields}
        flat['summary_struct'] = summary_struct

        return _json.dumps(flat, ensure_ascii=False, indent=2)

    def _call_openai_api_stream(self, headers: dict, json_data: bytes) -> str:
        """使用 streaming 模式调用 OpenAI 兼容接口，采集完整输出内容。"""
        response = self._session.post(
            self._api_url, headers=headers, data=json_data,
            timeout=180, stream=True
        )
        response.raise_for_status()

        full_content = []
        for line in response.iter_lines():
            if not line:
                continue
            line_str = line.decode('utf-8') if isinstance(line, bytes) else line
            if not line_str.startswith('data: '):
                continue
            data_str = line_str[6:]
            if data_str == '[DONE]':
                break
            try:
                chunk = json.loads(data_str)
                delta = chunk['choices'][0].get('delta', {})
                content = delta.get('content', '')
                if content:
                    full_content.append(content)
            except (json.JSONDecodeError, KeyError, IndexError):
                continue

        result = ''.join(full_content)
        if not result:
            raise ValueError("Streaming 模式未返回任何内容，请检查模型配置。")
        return result

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

        # 针对特定模型预处理 prompt（如 qwen3 的 schema 占位符问题）
        prompt = self._preprocess_prompt_for_model(prompt)

        if self._api_format == 'gemini':
            return self._call_gemini_api(prompt, temp, tokens)
        else:
            return self._call_openai_api(prompt, temp, tokens)

    @retry_on_error(max_retries=3, delay=2.0)
    def generate_text(self, prompt: str, temperature: float = None,
                      max_tokens: int = None) -> str:
        return self._call_api(prompt, temperature, max_tokens)

    @retry_on_error(max_retries=3, delay=2.0)
    def generate_json(self, prompt: str, temperature: float = 0.3,
                      max_tokens: int = None) -> Dict[str, Any]:
        from utils.helpers import extract_json_from_text
        text = self._call_api(prompt, temperature, max_tokens)
        # qwen3 返回扁平 JSON，需要重新包装为嵌套格式
        if 'qwen3' in self._model.lower():
            text = self._postprocess_qwen3_response(text)
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
