import subprocess
import sys
import os
import tempfile
import re
from config import WORKER_CONFIG
from utils import clean_json_text, call_llm
from rich.console import Console

console = Console()

class WorkerAgent:
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        初始化WorkerAgent
        Args:
            model_name: 模型名称，默认为"gemini-1.5-pro"
        """
        self.model_name = model_name
        self.max_retries = 3
    
    def coder(self, task_description):
        """
        Coder角色：根据任务描述生成Shell命令或Python代码
        """
        system_prompt = """
        你是一个专业的Coder，负责根据任务描述生成可执行的Shell命令或Python代码。
        请遵循以下规则：
        1. 分析任务描述，理解用户需求
        2. 生成简洁、高效、正确的代码或命令
        3. 如果是Python代码，必须是完整的、可独立运行的脚本，包含必要的导入语句
        4. 不要使用 input() 等待用户输入
        5. 只返回代码或命令本身，尽量不要包含 ``` 标记，如果包含我会自动清洗
        """
        
        prompt = f"{system_prompt}\n\n任务描述：{task_description}"
        
        if WORKER_CONFIG['client']:
            raw_response = call_llm(WORKER_CONFIG, prompt)
            return clean_json_text(raw_response)
        else:
            return "错误: Worker AI 未初始化"
    
    def runner(self, code_or_command):
        """
        Runner角色：执行代码或命令，并捕获输出
        更稳健的 Runner：将 Python 代码写入临时文件执行
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
                
                # 执行临时文件
                console.print(f"[dim]正在执行临时文件: {tmp_file_path}[/dim]")
                result = subprocess.run(
                    [sys.executable, tmp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    encoding='utf-8',
                    errors='replace' # 防止编码报错
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
        system_prompt = """
        你是一个专业的Tech Lead，负责分析代码和报错日志，指导Coder修复错误。
        请遵循以下规则：
        1. 分析任务描述、代码和错误信息
        2. 准确识别错误原因
        3. 提供清晰、具体的修复建议
        4. 确保修复后的代码能够正确执行
        5. 只返回修复建议，不要包含任何解释或额外内容
        6. 如果错误是缺少Python库，请生成相应的pip安装命令，格式为：pip install 库名
        7. 如果需要安装多个库，请在一行中用空格分隔，例如：pip install requests pandas numpy
        """
        
        prompt = f"{system_prompt}\n\n任务描述：{task_description}\n\n生成的代码：{code}\n\n错误信息：{error}"
        
        if WORKER_CONFIG['client']:
            return call_llm(WORKER_CONFIG, prompt)
        else:
            return "错误: Tech Lead AI 未初始化"
    
    def run(self, task_description):
        """
        运行整个工作流程：Coder生成代码 → Runner执行 → Tech Lead分析错误（如果有）
        """
        console.print(f"[bold blue]开始执行任务：[/bold blue]{task_description}")
        
        for retry in range(self.max_retries):
            console.print(f"[bold green]第 {retry + 1} 次尝试[/bold green]")
            
            # 1. Coder生成代码
            console.print("[cyan]Coder正在生成代码...[/cyan]")
            code = self.coder(task_description)
            console.print(f"[cyan]生成的代码：[/cyan]\n{code}")
            
            # 2. Runner执行代码
            console.print("[yellow]Runner正在执行代码...[/yellow]")
            success, output, error = self.runner(code)
            
            if success:
                console.print("[bold green]执行成功！[/bold green]")
                console.print(f"[green]输出：[/green]\n{output}")
                return {
                    "success": True,
                    "output": output,
                    "code": code
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
                
                # 更新任务描述，包含修复建议
                task_description = f"{task_description}\n\n修复建议：{fix_suggestion}"
                
                if retry == self.max_retries - 1:
                    console.print("[bold red]达到最大重试次数，执行失败[/bold red]")
                    return {
                        "success": False,
                        "error": error,
                        "code": code
                    }
                
                console.print("[yellow]准备重试...[/yellow]")
