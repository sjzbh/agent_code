"""
人类介入兜底模块
实现HITL（Human in the Loop）模式
"""
from typing import Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from core.state import AgentState

console = Console()


def hitl_mode(state: AgentState) -> str:
    """
    HITL模式：当系统遇到无法自动解决的问题时，暂停自动执行并提供交互选项
    
    Args:
        state: Agent状态
        
    Returns:
        str: 用户选择的操作类型
    """
    console.print("[bold red]======= HITL 模式激活 =======[/bold red]")
    console.print("[bold yellow]系统遇到无法自动解决的问题，需要人工介入[/bold yellow]")
    console.print("")
    
    while True:
        console.print("请选择操作:")
        console.print("  [1] Force Pass - 强制标记当前任务成功，跳过审计，继续下一个")
        console.print("  [2] Retry - 清空重试计数，手动修复环境后让它再试一次")
        console.print("  [3] Exit - 保存状态并安全退出")
        
        choice = Prompt.ask("请输入选项编号", choices=["1", "2", "3"], default="1")
        
        if choice == "1":
            console.print("[bold green]选择：强制通过当前任务[/bold green]")
            # 重置重试计数并前进到下一个任务
            state.reset_retry_count()
            state.advance_task_index()
            return "FORCE_PASS"
        
        elif choice == "2":
            console.print("[bold yellow]选择：重试（清空重试计数）[/bold yellow]")
            # 清空重试计数，保持当前任务索引不变
            state.reset_retry_count()
            return "RETRY"
        
        elif choice == "3":
            console.print("[bold blue]选择：退出系统[/bold blue]")
            return "EXIT"
        
        else:
            console.print("[red]无效选项，请重新选择[/red]")


def save_state_before_exit(state: AgentState):
    """
    退出前保存状态
    
    Args:
        state: Agent状态
    """
    console.print("[yellow]正在保存当前状态...[/yellow]")
    try:
        import json
        with open("agent_state_backup.json", "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)
        console.print("[green]状态已保存到 agent_state_backup.json[/green]")
    except Exception as e:
        console.print(f"[red]保存状态失败：{e}[/red]")