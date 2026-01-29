"""
增强版WorkerAgent
支持环境自适应和错误反馈机制
"""
import subprocess
import sys
import os
import tempfile
import re
import shutil
from config import settings, ai_client_manager
from utils import clean_json_text, call_llm
from prompts import CODER_PROMPT, TECH_LEAD_PROMPT
from rich.console import Console
from core.state import AgentState

# 从旧的config.py导入WORKER_CONFIG
import importlib.util
import os

# 获取项目根目录下的config.py路径
config_py_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.py')
spec = importlib.util.spec_from_file_location("legacy_config", config_py_path)
legacy_config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy_config_module)

# 从旧配置中获取WORKER_CONFIG
WORKER_CONFIG = legacy_config_module.WORKER_CONFIG

console = Console()


class EnhancedWorkerAgent:
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        初始化EnhancedWorkerAgent
        Args:
            model_name: 模型名称，默认为"gemini-1.5-pro"
        """
        self.model_name = model_name
        self.max_retries = 3

    def detect_python_executable(self) -> str:
        """
        检测系统中可用的Python可执行文件
        
        Returns:
            str: Python可执行文件路径
        """
        # 检查python
        if shutil.which('python'):
            return 'python'
        # 检查python3
        elif shutil.which('python3'):
            return 'python3'
        # 默认返回python
        else:
            return 'python'

    def coder(self, task_description):
        """
        Coder角色：根据任务描述生成Shell命令或Python代码
        """
        prompt = f"{CODER_PROMPT}\n\n任务描述：{task_description}"

        if WORKER_CONFIG['client']:
            raw_response = call_llm(WORKER_CONFIG, prompt)
            return clean_json_text(raw_response)
        else:
            return "错误: Worker AI 未初始化"

    def runner(self, code_or_command, python_executable: str = "python"):
        """
        Runner角色：执行代码或命令，并捕获输出
        支持环境自适应
        """
        try:
            # 清理可能残留的 markdown 标记
            code_or_command = clean_json_text(code_or_command)

            # 简单判断是否为 Python 代码
            is_python = any(x in code_or_command for x in ['import ', 'def ', 'print(', 'class '])

            if is_python:
                # 【关键改进】写入临时文件
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp_file:
                    tmp_file.write(code_or_command)
                    tmp_file_path = tmp_file.name

                # 执行临时文件，使用检测到的Python可执行文件
                console.print(f"[dim]正在执行临时文件: {tmp_file_path} (使用 {python_executable})[/dim]")
                result = subprocess.run(
                    [python_executable, tmp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    encoding='utf-8',
                    errors='replace'  # 防止编码报错
                )
                # 执行完删除
                os.unlink(tmp_file_path)
            else:
                # 执行Shell命令
                result = subprocess.run(
                    code_or_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    encoding='utf-8',
                    errors='replace'
                )

            success = result.returncode == 0
            # 组合 stdout 和 stderr
            output = result.stdout + "\n" + result.stderr

            return success, output.strip(), result.stderr
        except Exception as e:
            return False, "", str(e)

    def tech_lead(self, task_description, code, error):
        """
        Tech Lead角色：分析代码和报错日志，指导Coder修复错误
        """
        prompt = f"{TECH_LEAD_PROMPT}\n\n任务描述：{task_description}\n\n生成的代码：{code}\n\n错误信息：{error}"

        if WORKER_CONFIG['client']:
            return call_llm(WORKER_CONFIG, prompt)
        else:
            return "错误: Tech Lead AI 未初始化"

    def run(self, task_description: str, state: AgentState):
        """
        运行整个工作流程：Coder生成代码 → Runner执行 → Tech Lead分析错误（如果有）
        """
        console.print(f"[bold blue]开始执行任务：[/bold blue]{task_description}")

        # 检测Python可执行文件
        python_executable = self.detect_python_executable()
        state.python_executable = python_executable
        console.print(f"[cyan]检测到Python可执行文件：{python_executable}[/cyan]")

        for retry in range(state.max_retries):
            console.print(f"[bold green]第 {retry + 1} 次尝试 (最大重试次数: {state.max_retries})[/bold green]")

            # 1. Coder生成代码
            console.print("[cyan]Coder正在生成代码...[/cyan]")
            code = self.coder(task_description)
            console.print(f"[cyan]生成的代码：[/cyan]\n{code}")

            # 2. Runner执行代码
            console.print("[yellow]Runner正在执行代码...[/yellow]")
            success, output, error = self.runner(code, python_executable)

            if success:
                console.print("[bold green]执行成功！[/bold green]")
                console.print(f"[green]输出：[/green]\n{output}")

                # 记录成功执行
                state.add_execution_record({
                    "task_index": state.current_task_index,
                    "task_description": task_description,
                    "success": True,
                    "output": output,
                    "code": code,
                    "retry_count": retry + 1,
                    "attempt_number": retry + 1
                })

                return {
                    "success": True,
                    "output": output,
                    "code": code,
                    "retry_count": retry + 1
                }
            else:
                console.print("[bold red]执行失败！[/bold red]")
                console.print(f"[red]错误信息：[/red]\n{error}")

                # 检查是否是缺少库的错误
                if "ModuleNotFoundError" in error or "ImportError" in error:
                    console.print("[yellow]检测到缺少库的错误，正在生成安装命令...[/yellow]")

                # 3. Tech Lead分析错误
                console.print("[magenta]Tech Lead正在分析错误...[/magenta]")
                fix_suggestion = self.tech_lead(task_description, code, error)
                console.print(f"[magenta]修复建议：[/magenta]\n{fix_suggestion}")

                # 检查修复建议是否包含pip安装命令
                if fix_suggestion.startswith("pip install"):
                    console.print("[yellow]正在执行pip安装命令...[/yellow]")
                    install_result = subprocess.run(
                        fix_suggestion,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    if install_result.returncode == 0:
                        console.print("[green]库安装成功！[/green]")
                    else:
                        console.print(f"[red]库安装失败：[/red]\n{install_result.stderr}")

                # 更新任务描述，包含修复建议和上次失败的反馈
                task_description = f"{task_description}\n\n上一轮失败反馈：{error}\n\n修复建议：{fix_suggestion}"

                # 增加重试计数（注意：这里是在失败后才增加）
                if retry < state.max_retries - 1:  # 只有在还有重试机会时才增加计数
                    state.increment_retry_count()

                if retry == state.max_retries - 1:
                    console.print("[bold red]达到最大重试次数，执行失败[/bold red]")

                    # 记录失败执行
                    state.add_execution_record({
                        "task_index": state.current_task_index,
                        "task_description": task_description,
                        "success": False,
                        "error": error,
                        "code": code,
                        "retry_count": retry + 1,
                        "attempt_number": retry + 1
                    })

                    return {
                        "success": False,
                        "error": error,
                        "code": code,
                        "retry_count": retry + 1
                    }

                console.print("[yellow]准备重试...[/yellow]")