#!/usr/bin/env python3
"""
多AI协作CLI工具入口
"""
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from manager import ProjectManager
from worker import WorkerAgent
from auditor import AuditorAgent

console = Console()

def main():
    """
    主函数，实现REPL循环
    """
    # 初始化各个组件
    manager = ProjectManager()
    worker = WorkerAgent()
    auditor = AuditorAgent()
    
    console.print(Panel(
        "欢迎使用多AI协作CLI工具！\n\n" +
        "这个工具由以下AI角色组成：\n" +
        "- ProjectManager: 负责任务规划和管理\n" +
        "- Coder: 生成代码或命令\n" +
        "- Runner: 执行代码或命令\n" +
        "- Tech Lead: 分析错误并提供修复建议\n" +
        "- Auditor: 审计执行结果\n\n" +
        "请输入您的需求，或输入 'exit' 退出工具。",
        title="[bold cyan]多AI协作CLI工具[/bold cyan]",
        border_style="cyan"
    ))
    
    while True:
        try:
            # 接收用户输入
            user_input = Prompt.ask("[bold green]您的需求[/bold green]", default="exit")
            
            if user_input.lower() == "exit":
                console.print("[bold cyan]工具已退出，感谢使用！[/bold cyan]")
                break
            
            if not user_input.strip():
                continue
            
            # PM生成或更新任务队列
            console.print(Panel(
                f"用户需求：{user_input}",
                title="[bold green]用户输入[/bold green]",
                border_style="green"
            ))
            
            tasks = manager.plan_tasks(user_input)
            
            if not tasks:
                console.print("[bold red]任务规划失败，请重试。[/bold red]")
                continue
            
            # 执行任务队列
            task_index = 0
            while task_index < len(manager.task_queue):
                # 提取当前最高优先级的任务
                # 按优先级排序，获取当前任务
                sorted_tasks = sorted(manager.task_queue[task_index:], key=lambda x: {
                    "high": 0, "medium": 1, "low": 2
                }[x.get("priority", "medium")])
                
                if not sorted_tasks:
                    break
                
                current_task = sorted_tasks[0]
                task_index = manager.task_queue.index(current_task)
                
                console.print(Panel(
                    f"任务ID: {current_task.get('id', 'N/A')}\n" +
                    f"任务描述: {current_task['description']}\n" +
                    f"优先级: {current_task.get('priority', 'medium')}",
                    title="[bold blue]当前任务[/bold blue]",
                    border_style="blue"
                ))
                
                # 交给Worker执行
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True
                ) as progress:
                    progress.add_task("Worker执行任务中...", total=None)
                    execution_result = worker.run(current_task["description"])
                
                # 生成执行日志
                if execution_result["success"]:
                    execution_logs = f"执行成功！\n输出：{execution_result['output']}\n代码：{execution_result['code']}"
                else:
                    execution_logs = f"执行失败！\n错误：{execution_result['error']}\n代码：{execution_result['code']}"
                
                # 交给Auditor审计
                audit_result = auditor.audit(current_task["description"], execution_logs)
                
                # 显示审计结果
                console.print(Panel(
                    f"状态: {audit_result['status']}\n" +
                    f"反馈: {audit_result['feedback']}",
                    title="[bold purple]审计结果[/bold purple]",
                    border_style="purple"
                ))
                
                # PM根据反馈决定是继续下一个任务，还是插入修复任务
                if audit_result["status"] == "FAIL":
                    # 更新任务计划
                    updated_tasks = manager.update_plan(audit_result["feedback"])
                    # 重置任务索引，重新开始执行
                    task_index = 0
                else:
                    # 继续下一个任务
                    task_index += 1
            
            # 任务执行完成，显示项目状态
            project_state = manager.get_project_state()
            console.print(Panel(
                f"状态: {project_state.get('status', 'unknown')}\n" +
                f"完成任务数: {len(project_state.get('task_queue', []))}",
                title="[bold green]项目状态[/bold green]",
                border_style="green"
            ))
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]操作被用户中断。[/bold yellow]")
            continue
        except Exception as e:
            console.print(f"[bold red]发生错误：{str(e)}[/bold red]")
            continue

if __name__ == "__main__":
    main()
