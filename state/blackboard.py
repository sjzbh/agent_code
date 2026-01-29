from typing import Dict, Any, List
from dataclasses import dataclass, field
from rich.console import Console

console = Console()

@dataclass
class SharedState:
    """
    共享状态（Blackboard）类
    用于在不同Agent之间共享信息
    """
    # 用户需求
    user_requirements: str = ""

    # 创建的文件列表
    files_created: List[str] = field(default_factory=list)

    # 最后一次错误信息
    last_error: str = ""

    # 项目信息
    project_info: Dict[str, Any] = field(default_factory=dict)

    # 测试结果
    test_result: Dict[str, Any] = field(default_factory=dict)

    # 部署结果
    deployment_result: Dict[str, Any] = field(default_factory=dict)

    # 当前任务状态
    current_task: str = ""

    # 执行日志
    execution_logs: List[str] = field(default_factory=list)

    # 审计相关状态
    audit_fail_count: int = 0  # 连续审计失败次数
    max_audit_fails: int = 3   # 最大允许的连续审计失败次数
    
    def set(self, key: str, value: Any) -> None:
        """
        设置共享状态的值
        
        Args:
            key: 键名
            value: 值
        """
        if hasattr(self, key):
            setattr(self, key, value)
            console.print(f"[bold blue]共享状态更新：[/bold blue]{key} = {value}")
        else:
            console.print(f"[bold red]错误：共享状态中不存在键 {key}[/bold red]")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取共享状态的值
        
        Args:
            key: 键名
            default: 默认值
        
        Returns:
            共享状态的值
        """
        if hasattr(self, key):
            return getattr(self, key)
        else:
            console.print(f"[bold yellow]警告：共享状态中不存在键 {key}，返回默认值[/bold yellow]")
            return default
    
    def add_file(self, file_path: str) -> None:
        """
        添加创建的文件
        
        Args:
            file_path: 文件路径
        """
        if file_path not in self.files_created:
            self.files_created.append(file_path)
            console.print(f"[bold blue]文件添加到共享状态：[/bold blue]{file_path}")
    
    def add_log(self, log: str) -> None:
        """
        添加执行日志
        
        Args:
            log: 日志信息
        """
        self.execution_logs.append(log)
    
    def clear(self) -> None:
        """
        清空共享状态
        """
        self.user_requirements = ""
        self.files_created = []
        self.last_error = ""
        self.project_info = {}
        self.test_result = {}
        self.deployment_result = {}
        self.current_task = ""
        self.execution_logs = []
        console.print("[bold blue]共享状态已清空[/bold blue]")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            共享状态的字典表示
        """
        return {
            "user_requirements": self.user_requirements,
            "files_created": self.files_created,
            "last_error": self.last_error,
            "project_info": self.project_info,
            "test_result": self.test_result,
            "deployment_result": self.deployment_result,
            "current_task": self.current_task,
            "execution_logs": self.execution_logs
        }

# 创建全局共享状态实例
shared_state = SharedState()
