#!/usr/bin/env python3
"""
Virtual Software Company - Next Generation (V2.1)
Project Chrysalis - Self-Evolving Agent System
"""
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controller.main import start_company_cycle

console = Console()

def main():
    """
    Main entry point for the Next Generation Virtual Software Company
    """
    console.print(Panel(
        "🌟 欢迎来到虚拟软件公司 - 下一代 (Virtual Software Company NextGen)!\n\n"
        "基于 Project Chrysalis (破茧计划) 的自进化智能体系统\n"
        "采用 SOP (Standard Operating Procedure) 驱动的多智能体架构\n\n"
        "核心流程：\n"
        "PM需求 → 架构师设计 → 工程师开发 ↔ 技术主管审查 → 运维工程师执行 → 测试工程师测试 → 审计员验收 → 进化官分析\n\n"
        "本系统基于经验库持续进化，每次运行都会提升自身能力。",
        title="[bold cyan]虚拟软件公司 - 下一代 V2.1[/bold cyan]",
        border_style="cyan"
    ))
    
    try:
        start_company_cycle()
    except KeyboardInterrupt:
        console.print("\n[yellow]操作被用户中断[/yellow]")
    except Exception as e:
        console.print(f"[bold red]系统错误: {e}[/bold red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()