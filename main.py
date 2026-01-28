#!/usr/bin/env python3
"""
多AI协作CLI工具入口
"""
import sys
import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from manager import ProjectManager
from worker import WorkerAgent
from auditor import AuditorAgent
from sandbox import SandboxManager
from evaluator import EvaluatorAgent

# 尝试导入Flet GUI应用，添加跳过机制
try:
    from gui import AIStudioApp
    HAS_FLET_GUI = True
except ImportError:
    HAS_FLET_GUI = False
    print("[警告] 无法导入Flet GUI应用，将使用命令行模式。")

console = Console()

def process_request(user_input, manager, worker, auditor):
    """
    处理用户需求的函数
    """
    console.print(Panel(
        f"用户需求：{user_input}",
        title="[bold green]用户输入[/bold green]",
        border_style="green"
    ))
    
    tasks = manager.plan_tasks(user_input)
    
    if not tasks:
        console.print("[bold red]任务规划失败，请重试。[/bold red]")
        return
    
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

def main():
    """
    主函数，实现REPL循环
    """
    # 初始化各个组件
    manager = ProjectManager()
    worker = WorkerAgent()
    auditor = AuditorAgent()
    sandbox = SandboxManager()
    evaluator = EvaluatorAgent()
    
    # 显示模式选择界面
    console.print(Panel(
        "欢迎使用多AI协作CLI工具！\n\n" +
        "这个工具由以下AI角色组成：\n" +
        "- ProjectManager: 负责任务规划和管理\n" +
        "- Coder: 生成代码或命令\n" +
        "- Runner: 执行代码或命令\n" +
        "- Tech Lead: 分析错误并提供修复建议\n" +
        "- Auditor: 审计执行结果\n\n" +
        "请选择操作模式：\n" +
        "1. 命令行模式（传统REPL）\n" +
        f"2. Flet GUI模式{'（可用）' if HAS_FLET_GUI else '（不可用）'}\n" +
        "请输入数字选择模式，或输入 'exit' 退出工具。\n\n" +
        "提示：您也可以直接运行 gui.py 或 studio_app.py 启动独立的桌面GUI界面。",
        title="[bold cyan]多AI协作CLI工具[/bold cyan]",
        border_style="cyan"
    ))

    # 模式选择
    while True:
        try:
            mode_input = Prompt.ask("[bold green]请选择模式[/bold green]", default="1")

            if mode_input.lower() == "exit":
                console.print("[bold cyan]工具已退出，感谢使用！[/bold cyan]")
                return

            # 处理Flet GUI模式
            if mode_input == "2" and HAS_FLET_GUI:
                console.print("[bold yellow]正在启动Flet GUI应用...[/bold yellow]")
                try:
                    app = AIStudioApp()
                    import flet
                    flet.app(target=app.main)
                    return
                except Exception as e:
                    console.print(f"[bold red]Flet GUI应用启动失败：{e}[/bold red]")
                    console.print("[bold yellow]切换到命令行模式...[/bold yellow]")

            # 处理命令行模式
            elif mode_input == "1" or not HAS_FLET_GUI:
                console.print("[bold green]进入命令行模式...[/bold green]")
                break

            else:
                console.print("[bold red]无效的选择，请重新输入！[/bold red]")

        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold yellow]操作被用户中断。[/bold yellow]")
            return
    
    while True:
        try:
            # 接收用户输入
            # 【修复点1】增加 EOFError 的处理，防止 Ctrl+D/Z 导致死循环
            try:
                user_input = Prompt.ask("[bold green]您的需求[/bold green]", default="exit")
            except (EOFError, KeyboardInterrupt):
                console.print("\n[bold yellow]检测到退出信号，正在退出...[/bold yellow]")
                break

            if user_input.lower() == "exit":
                console.print("[bold cyan]工具已退出，感谢使用！[/bold cyan]")
                break
            
            if not user_input.strip():
                continue
            
            # === 新增：进化模式入口 ===
            if user_input.startswith("evolve "):
                target_file = user_input.split(" ")[1] # 例如: evolve worker.py 增加重试机制
                requirement = " ".join(user_input.split(" ")[2:])
                
                console.print(Panel(f"目标文件: {target_file}\n需求: {requirement}", title="[bold gold1]启动自我进化流程[/bold gold1]", border_style="gold1"))
                
                # 1. 初始化沙箱
                if not sandbox.init_sandbox():
                    continue
                    
                # 2. 读取原代码
                try:
                    with open(target_file, 'r', encoding='utf-8') as f:
                        original_code = f.read()
                except FileNotFoundError:
                    console.print(f"[red]文件 {target_file} 不存在！[/red]")
                    continue

                # 3. 让 Coder 生成新代码 (注意：这里我们复用 worker，但给它进化专用的 Prompt)
                # 这里为了简单，我们直接构造一个 Prompt 传给 coder
                evolution_task = f"请重构 {target_file}。\n原代码如下：\n{original_code}\n\n改进需求：{requirement}\n\n请遵循 EVOLUTION_PROMPT 的规则。"
                
                console.print("[cyan]正在生成进化版代码...[/cyan]")
                new_code = worker.coder(evolution_task) # 你可能需要稍微修改 worker.coder 让它接受自定义 System Prompt，或者直接这样传也行
                
                # 4. 写入沙箱
                sandbox_file_path = os.path.join(sandbox.sandbox_dir, target_file)
                with open(sandbox_file_path, 'w', encoding='utf-8') as f:
                    f.write(new_code)
                    
                # 5. 沙箱验证 (尝试运行代码)
                # 如果是库文件(如worker.py)，我们可能需要运行 main.py 来测试，或者运行一个专门生成的测试脚本
                # 这里做一个简单的"语法检查"和"导入测试"
                console.print("[yellow]正在沙箱中进行冒烟测试...[/yellow]")
                check_cmd = f"{sys.executable} -c 'import {target_file.replace('.py', '')}'" # 尝试导入
                success, stdout, stderr = sandbox.run_in_sandbox(check_cmd)
                
                test_logs = f"Exit Code: {0 if success else 1}\nStdout: {stdout}\nStderr: {stderr}"
                
                if not success:
                    console.print("[bold red]沙箱测试失败！新代码存在严重错误，进化终止。[/bold red]")
                    console.print(stderr)
                    continue
                    
                # 6. 评估官介入
                decision_json = evaluator.evaluate_improvement(original_code, new_code, test_logs, requirement)
                try:
                    decision = json.loads(decision_json)
                    console.print(Panel(f"决策: {decision['decision']}\n评分: {decision.get('score')}\n理由: {decision['reason']}", title="评估报告"))
                    
                    if decision['decision'] == "ACCEPT":
                        # 7. 部署
                        sandbox.deploy_file(target_file)
                        console.print("[bold green]进化成功！代码已更新。[/bold green]")
                    else:
                        console.print("[bold red]进化被拒绝。[/bold red]")
                        
                except Exception as e:
                    console.print(f"[red]评估结果解析失败: {e}[/red]")
                
                continue
            
            # 处理普通需求
            process_request(user_input, manager, worker, auditor)
            
        # 【修复点2】外层捕获防止意外退出，但要区分致命错误
        except KeyboardInterrupt:
            console.print("\n[bold yellow]操作被用户中断。[/bold yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]发生未知错误：{str(e)}[/bold red]")
            # 如果是输入流错误，必须退出，否则死循环
            if "EOF" in str(e) or "input" in str(e):
                break
            continue

if __name__ == "__main__":
    main()