"""
工具函数
提供各种辅助功能
"""
import re
import json
from datetime import datetime
from typing import Any, Dict
from functools import wraps
import time


def clean_text(text: str) -> str:
    """
    清洗文本，移除多余空白字符

    Args:
        text: 原始文本

    Returns:
        清洗后的文本
    """
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 移除首尾空白
    text = text.strip()
    return text


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    从文本中提取 JSON 对象
    处理 LLM 可能返回的带有 markdown 代码块、不完整 JSON 的情况

    Args:
        text: 包含 JSON 的文本

    Returns:
        解析后的 JSON 对象
    """
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 尝试提取 markdown 代码块中的 JSON
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试提取第一个 JSON 对象（非贪婪匹配）
    json_match = re.search(r'\{.*?\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    # 尝试提取第一个 JSON 对象（贪婪匹配，用于处理嵌套）
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # 尝试修复不完整的 JSON（缺少结尾的 } 或 "）
            # 1. 如果末尾是 "..., 尝试补全
            if json_str.rstrip().endswith('...'):
                json_str = json_str.rstrip()[:-3] + '"'

            # 2. 处理被截断的字段值（如 LaTeX 公式、长文本）
            # 查找最后一个完整的字段（以 ", 或 } 结尾）
            # 如果最后一个字段值没有闭合引号，截断到上一个完整字段
            last_complete_field = max(
                json_str.rfind('",'),
                json_str.rfind('"]'),
                json_str.rfind('},')
            )

            # 如果找到了完整字段，且后面还有未闭合的内容
            if last_complete_field > 0:
                # 检查是否有未闭合的引号
                remaining = json_str[last_complete_field:]
                open_quotes = remaining.count('"')
                # 如果引号数量是奇数，说明有未闭合的字段
                if open_quotes % 2 == 1:
                    # 截断到最后一个完整字段
                    json_str = json_str[:last_complete_field + 1]

            # 3. 统计 { 和 } 的数量，补全缺失的 }
            open_braces = json_str.count('{')
            close_braces = json_str.count('}')
            if open_braces > close_braces:
                json_str += '}' * (open_braces - close_braces)

            # 4. 如果最后一个字段没有闭合引号，尝试补全
            # 查找最后一个 ": 后面是否有闭合的 "
            last_quote_pos = json_str.rfind('"')
            last_colon_pos = json_str.rfind('":')
            if last_colon_pos > last_quote_pos:
                # 在最后添加 "
                json_str = json_str.rstrip() + '"'
                # 再次补全 }
                open_braces = json_str.count('{')
                close_braces = json_str.count('}')
                if open_braces > close_braces:
                    json_str += '}' * (open_braces - close_braces)

            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                # 最后尝试：如果是因为某个字段值被截断，尝试移除该字段
                # 查找导致错误的位置
                error_pos = getattr(e, 'pos', None)
                if error_pos:
                    # 截断到错误位置之前的最后一个完整字段
                    truncated = json_str[:error_pos]
                    last_complete = max(
                        truncated.rfind('",'),
                        truncated.rfind('"]'),
                        truncated.rfind('},'),
                        0
                    )
                    if last_complete > 0:
                        json_str = truncated[:last_complete + 1]
                        # 补全括号
                        open_braces = json_str.count('{')
                        close_braces = json_str.count('}')
                        if open_braces > close_braces:
                            json_str += '}' * (open_braces - close_braces)
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            pass

    raise ValueError(f"无法从文本中提取有效的 JSON: {text[:500]}...")


def format_date(dt: datetime) -> str:
    """
    格式化日期时间

    Args:
        dt: datetime 对象

    Returns:
        格式化后的日期字符串
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    截断文本到指定长度

    Args:
        text: 原始文本
        max_length: 最大长度

    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """
    错误重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"尝试 {attempt + 1}/{max_retries} 失败: {str(e)}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator
