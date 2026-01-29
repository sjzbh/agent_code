"""
智能路由机制模块
实现条件路由，决定Agent的下一步行动
"""
from typing import Dict, Any, Tuple
from core.state import AgentState
from rich.console import Console

console = Console()


def router(state: AgentState, audit_result: Dict[str, Any]) -> Tuple[str, str]:
    """
    智能路由函数，根据状态和审计结果决定下一步行动
    
    Args:
        state: Agent状态
        audit_result: 审计结果
        
    Returns:
        Tuple[str, str]: (action, reason) - 行动类型和原因
    """
    # 检查是否为熔断/系统错误
    if state.retry_count >= state.max_retries:
        console.print(f"[bold red]触发熔断机制：重试次数已达上限 ({state.retry_count}/{state.max_retries})[/bold red]")
        return "HITL", "重试次数已达上限，需要人工介入"
    
    # 检查审计结果
    if audit_result and audit_result.get("status") == "PASS":
        # 分支 A (PASS)：任务通过 -> 重置 retry_count -> 索引 +1 -> 进入下一任务
        console.print("[bold green]任务通过审核，进入下一任务[/bold green]")
        return "NEXT_TASK", "任务通过审核，前进到下一个任务"
    
    elif audit_result and audit_result.get("status") == "FAIL":
        # 检查是否是环境问题导致的失败
        feedback = audit_result.get("feedback", "")
        if "Auditor AI 未初始化" in feedback or "环境缺失" in feedback:
            console.print("[bold red]检测到环境问题，触发HITL模式[/bold red]")
            return "HITL", "检测到环境问题，需要人工介入"
        
        # 分支 B (逻辑错误)：代码不对 -> retry_count < 3 -> 保持索引不变 -> 触发 Worker 重试
        if state.retry_count < state.max_retries:
            console.print(f"[bold yellow]任务未通过审核，准备重试 ({state.retry_count + 1}/{state.max_retries})[/bold yellow]")
            return "RETRY_CURRENT", "任务未通过审核，重试当前任务"
        else:
            console.print("[bold red]重试次数已达上限，触发HITL模式[/bold red]")
            return "HITL", "重试次数已达上限，需要人工介入"
    
    else:
        # 未知状态，进入HITL模式
        console.print("[bold red]未知状态，进入HITL模式[/bold red]")
        return "HITL", "未知状态，需要人工介入"


def should_enter_hitl_mode(state: AgentState, audit_result: Dict[str, Any] = None) -> bool:
    """
    判断是否应该进入HITL模式
    
    Args:
        state: Agent状态
        audit_result: 审计结果
        
    Returns:
        bool: 是否应该进入HITL模式
    """
    # 重试次数达到上限
    if state.retry_count >= state.max_retries:
        return True
    
    # 审计结果表明是环境问题
    if audit_result:
        feedback = audit_result.get("feedback", "")
        if "Auditor AI 未初始化" in feedback or "环境缺失" in feedback:
            return True
    
    return False