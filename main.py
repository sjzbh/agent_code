#!/usr/bin/env python3
"""
zwgent - AI Agent 协作框架
"""
import sys
import os

if os.name == 'nt':
    os.system('chcp 65001 > nul 2>&1')

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.table import Table

from core.engine import Engine, EngineState
from core.blackboard import blackboard, BlackboardEventType
from config.settings import settings

console = Console()


def print_welcome():
    console.print(Panel(
        "[bold cyan]zwgent - AI Agent 协作框架[/bold cyan]\n\n"
        "这是一个强大的多AI角色协作系统，支持：\n"
        "- [green]智能意图识别[/green]：自动识别用户需求类型\n"
        "- [green]任务自动规划[/green]：将复杂需求拆解为可执行任务\n"
        "- [green]代码生成执行[/green]：生成并执行代码\n"
        "- [green]错误自动修复[/green]：分析错误并提供修复建议\n"
        "- [green]向量化记忆[/green]：RAG经验库支持\n\n"
        "输入 [bold]help[/bold] 查看帮助，输入 [bold]exit[/bold] 退出",
        title="[bold green]欢迎使用[/bold green]",
        border_style="green"
    ))


def print_help():
    help_table = Table(title="命令帮助")
    help_table.add_column("命令", style="cyan")
    help_table.add_column("说明", style="green")
    
    help_table.add_row("exit", "退出程序")
    help_table.add_row("help", "显示帮助信息")
    help_table.add_row("status", "显示当前状态")
    help_table.add_row("reset", "重置引擎状态")
    help_table.add_row("memory", "显示记忆库统计")
    help_table.add_row("clear", "清屏")
    
    console.print(help_table)
    
    console.print("\n[bold yellow]使用示例：[/bold yellow]")
    console.print("  • 写一个Python函数计算斐波那契数列")
    console.print("  • 读取 main.py 文件的内容")
    console.print("  • 在当前目录搜索所有 .py 文件")
    console.print("  • 运行 pip list 查看已安装的包")


def print_status(engine: Engine):
    status = engine.get_status()
    
    status_table = Table(title="引擎状态")
    status_table.add_column("属性", style="cyan")
    status_table.add_column("值", style="green")
    
    status_table.add_row("状态", status["state"])
    status_table.add_row("待处理任务", str(status["blackboard_summary"]["pending_tasks"]))
    status_table.add_row("已完成任务", str(status["blackboard_summary"]["completed_tasks"]))
    status_table.add_row("失败任务", str(status["blackboard_summary"]["failed_tasks"]))
    
    console.print(status_table)


def process_request(user_input: str, engine: Engine):
    console.print(Panel(
        f"[bold]{user_input}[/bold]",
        title="[bold green]用户需求[/bold green]",
        border_style="green"
    ))
    
    def on_stream_chunk(chunk: str):
        print(chunk, end="", flush=True)
    
    engine.on_stream_chunk(on_stream_chunk)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        progress.add_task("处理中...", total=None)
        result = engine.process(user_input)
    
    print()
    
    if result.get("status") == "success":
        if result.get("intent") == "question":
            console.print(Panel(
                Markdown(result.get("answer", "")),
                title="[bold green]回答[/bold green]",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[bold green]任务完成！[/bold green]\n"
                f"完成任务数: {result.get('completed_tasks', 0)}",
                title="[bold green]执行结果[/bold green]",
                border_style="green"
            ))
    elif result.get("status") == "failed":
        console.print(Panel(
            f"[bold red]任务失败[/bold red]\n"
            f"任务: {result.get('task', 'N/A')}\n"
            f"错误: {result.get('error', 'Unknown error')}",
            title="[bold red]失败[/bold red]",
            border_style="red"
        ))
    else:
        console.print(Panel(
            f"[bold yellow]部分完成[/bold yellow]\n"
            f"{result}",
            title="[bold yellow]结果[/bold yellow]",
            border_style="yellow"
        ))


def main():
    print_welcome()
    
    engine = Engine()
    
    while True:
        try:
            user_input = Prompt.ask(
                "\n[bold cyan]zwgent[/bold cyan]",
                default=""
            ).strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "exit":
                console.print("[bold cyan]感谢使用 zwgent，再见！[/bold cyan]")
                break
            
            if user_input.lower() == "help":
                print_help()
                continue
            
            if user_input.lower() == "status":
                print_status(engine)
                continue
            
            if user_input.lower() == "reset":
                engine.stop()
                console.print("[bold green]引擎已重置[/bold green]")
                continue
            
            if user_input.lower() == "memory":
                from brain.memory import memory
                stats = memory.get_stats()
                console.print(Panel(
                    f"总条目数: {stats['total_items']}\n"
                    f"向量维度: {stats['dimension']}\n"
                    f"存储路径: {stats['storage_path']}",
                    title="[bold cyan]记忆库统计[/bold cyan]",
                    border_style="cyan"
                ))
                continue
            
            if user_input.lower() == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            
            process_request(user_input, engine)
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]操作被中断[/bold yellow]")
            engine.stop()
        except EOFError:
            console.print("\n[bold cyan]退出程序[/bold cyan]")
            break
        except Exception as e:
            console.print(f"[bold red]错误: {str(e)}[/bold red]")
            if settings.debug:
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()
