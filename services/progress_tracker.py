"""
进度追踪器
用于跟踪 Auto-Scholar 流水线的执行进度
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Callable, Optional
from enum import Enum


class PipelineStage(Enum):
    """流水线阶段"""
    ARXIV_FETCH = "arxiv"
    KEYWORD_FILTER = "keyword"
    METADATA_SCORE = "metadata"
    S2_FILTER = "s2"
    AI_SCORING = "ai_scoring"
    SAVING = "saving"
    COMPLETED = "completed"


# 各阶段的显示名称
STAGE_NAMES = {
    PipelineStage.ARXIV_FETCH: "📡 Arxiv 抓取",
    PipelineStage.KEYWORD_FILTER: "🔍 关键词筛选",
    PipelineStage.METADATA_SCORE: "📊 元数据评分",
    PipelineStage.S2_FILTER: "🎓 S2 筛选",
    PipelineStage.AI_SCORING: "🤖 AI 评分",
    PipelineStage.SAVING: "💾 保存数据",
    PipelineStage.COMPLETED: "✅ 完成",
}

# 各阶段权重（用于计算总进度）
STAGE_WEIGHTS = {
    PipelineStage.ARXIV_FETCH: 0.10,
    PipelineStage.KEYWORD_FILTER: 0.05,
    PipelineStage.METADATA_SCORE: 0.10,
    PipelineStage.S2_FILTER: 0.25,
    PipelineStage.AI_SCORING: 0.45,
    PipelineStage.SAVING: 0.05,
}


@dataclass
class StageProgress:
    """单个阶段的进度"""
    stage: PipelineStage
    current: int = 0
    total: int = 0
    message: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    @property
    def progress(self) -> float:
        """阶段进度 0.0 - 1.0"""
        if self.total == 0:
            return 0.0
        return min(1.0, self.current / self.total)

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None


@dataclass
class PipelineProgress:
    """流水线整体进度"""
    stages: Dict[PipelineStage, StageProgress] = field(default_factory=dict)
    current_stage: PipelineStage = PipelineStage.ARXIV_FETCH
    logs: List[str] = field(default_factory=list)

    @property
    def overall_progress(self) -> float:
        """计算总体进度 0.0 - 1.0"""
        total_progress = 0.0
        for stage, weight in STAGE_WEIGHTS.items():
            if stage in self.stages:
                sp = self.stages[stage]
                total_progress += weight * sp.progress
        return total_progress

    def to_dict(self) -> dict:
        """转换为字典（用于序列化）"""
        return {
            'current_stage': self.current_stage.value,
            'current_stage_name': STAGE_NAMES.get(self.current_stage, ""),
            'overall_progress': self.overall_progress,
            'stages': {
                stage.value: {
                    'name': STAGE_NAMES.get(stage, ""),
                    'current': sp.current,
                    'total': sp.total,
                    'progress': sp.progress,
                    'message': sp.message,
                    'completed': sp.is_completed
                }
                for stage, sp in self.stages.items()
            },
            'logs': self.logs[-50:]  # 最近50条日志
        }


class ProgressTracker:
    """流水线进度追踪器"""

    def __init__(self):
        self.progress = PipelineProgress()
        self._callbacks: List[Callable] = []

    def register_callback(self, callback: Callable[[PipelineProgress], None]):
        """注册进度更新回调"""
        self._callbacks.append(callback)

    def update(self, stage: str, current: int, total: int, message: str):
        """
        更新进度

        Args:
            stage: 阶段名称（字符串，如 'arxiv', 'keyword' 等）
            current: 当前进度
            total: 总数
            message: 状态消息
        """
        # 转换字符串为枚举
        try:
            stage_enum = PipelineStage(stage)
        except ValueError:
            stage_enum = PipelineStage.ARXIV_FETCH

        # 创建或更新阶段进度
        if stage_enum not in self.progress.stages:
            self.progress.stages[stage_enum] = StageProgress(
                stage=stage_enum,
                current=current,
                total=total,
                message=message,
                started_at=datetime.now()
            )
        else:
            sp = self.progress.stages[stage_enum]
            sp.current = current
            sp.total = total
            sp.message = message

            # 标记完成
            if current >= total and total > 0:
                sp.completed_at = datetime.now()

        self.progress.current_stage = stage_enum

        # 添加日志
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.progress.logs.append(f"[{timestamp}] {message}")

        # 通知回调
        self._notify_callbacks()

    def get_progress(self) -> PipelineProgress:
        """获取当前进度"""
        return self.progress

    def get_progress_dict(self) -> dict:
        """获取进度字典"""
        return self.progress.to_dict()

    def reset(self):
        """重置进度"""
        self.progress = PipelineProgress()

    def _notify_callbacks(self):
        """通知所有回调"""
        for callback in self._callbacks:
            try:
                callback(self.progress)
            except Exception as e:
                print(f"Progress callback error: {e}")


def create_progress_callback(tracker: ProgressTracker) -> Callable:
    """
    创建用于 scheduler 的进度回调函数

    Args:
        tracker: ProgressTracker 实例

    Returns:
        回调函数
    """
    def callback(stage: str, current: int, total: int, message: str):
        tracker.update(stage, current, total, message)

    return callback
