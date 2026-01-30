"""
Next Generation Agent - Project Chrysalis V2.1+
Self-Evolving Architecture with Linux Optimization
"""
import os
import sys
from rich.console import Console
from controller.main import start_company_cycle

console = Console()

def main():
    """Main entry point for the Next Generation Agent"""
    console.print("[bold cyan]欢迎使用下一代智能代理系统 (NextGen Agent)![/bold cyan]")
    console.print("[green]系统已优化，专为当前环境定制[/green]")

    try:
        start_company_cycle()
    except KeyboardInterrupt:
        console.print("\n[yellow]操作被用户中断[/yellow]")
    except Exception as e:
        console.print(f"[red]系统错误: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
