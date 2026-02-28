"""
评分 LLM 服务封装
用于 Auto-Scholar 论文评分和 PDF 元数据提取
配置从 api_config 读取，当 scoring_llm 未独立配置时自动复用主 LLM
"""
from services.llm_service import LLMService


class DoubaoService(LLMService):
    """
    评分 LLM 服务（继承自 LLMService）
    角色为 scoring_llm，其余行为与 LLMService 完全一致
    保留类名 DoubaoService 以兼容现有引用
    """

    def __init__(self):
        super().__init__(role='scoring_llm')


# 创建全局评分服务实例（允许未配置时也能正常导入）
from services.llm_service import _create_service as _create_llm_service

try:
    doubao_service = DoubaoService()
except Exception:
    doubao_service = _create_llm_service('scoring_llm')
