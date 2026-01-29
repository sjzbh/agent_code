"""
Agent状态管理模块
实现全局状态管理，用于基于状态机的Agent架构
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import json
from datetime import datetime


@dataclass
class AgentState:
    """
    Agent状态类，用于管理整个Agent系统的全局状态
    """
    # 任务管理
    current_task_index: int = 0  # 当前任务进度
    task_list: List[Dict[str, Any]] = field(default_factory=list)  # 任务列表
    current_task_description: str = ""  # 当前任务描述
    
    # 重试管理
    retry_count: int = 0  # 当前重试次数
    max_retries: int = 3  # 最大重试阈值
    
    # 执行历史
    execution_history: List[Dict[str, Any]] = field(default_factory=list)  # 执行历史
    
    # 审计结果
    last_audit_result: Optional[Dict[str, Any]] = None  # 上次审计结果
    
    # 系统状态
    current_phase: str = "initial"  # 当前阶段 (planning, execution, auditing, hitl)
    error_message: str = ""  # 错误消息
    success: bool = False  # 是否成功
    
    # 环境信息
    python_executable: str = "python"  # Python可执行文件路径
    
    def add_execution_record(self, record: Dict[str, Any]):
        """添加执行记录到历史"""
        record_with_timestamp = {
            "timestamp": datetime.now().isoformat(),
            **record
        }
        self.execution_history.append(record_with_timestamp)
    
    def reset_retry_count(self):
        """重置重试计数"""
        self.retry_count = 0
    
    def increment_retry_count(self):
        """增加重试计数"""
        self.retry_count += 1
    
    def get_current_task(self) -> Optional[Dict[str, Any]]:
        """获取当前任务"""
        if 0 <= self.current_task_index < len(self.task_list):
            return self.task_list[self.current_task_index]
        return None
    
    def has_next_task(self) -> bool:
        """检查是否有下一个任务"""
        return self.current_task_index + 1 < len(self.task_list)
    
    def advance_task_index(self):
        """前进到下一个任务"""
        if self.has_next_task():
            self.current_task_index += 1
    
    def get_last_execution_result(self) -> Optional[Dict[str, Any]]:
        """获取最后一次执行结果"""
        if self.execution_history:
            return self.execution_history[-1]
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，便于序列化"""
        return {
            "current_task_index": self.current_task_index,
            "task_list": self.task_list,
            "current_task_description": self.current_task_description,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "execution_history": self.execution_history,
            "last_audit_result": self.last_audit_result,
            "current_phase": self.current_phase,
            "error_message": self.error_message,
            "success": self.success,
            "python_executable": self.python_executable
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentState':
        """从字典创建状态对象"""
        state = cls()
        for key, value in data.items():
            if hasattr(state, key):
                setattr(state, key, value)
        return state