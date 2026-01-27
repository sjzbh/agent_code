import subprocess
import sys
from config import client
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
        
        Args:
            task_description: 任务描述
        
        Returns:
            生成的代码或命令
        """
        system_prompt = """
        你是一个专业的Coder，负责根据任务描述生成可执行的Shell命令或Python代码。
        请遵循以下规则：
        1. 分析任务描述，理解用户需求
        2. 生成简洁、高效、正确的代码或命令
        3. 如果是Python代码，请确保代码完整可执行，包含必要的导入语句
        4. 如果是Shell命令，请确保命令在Windows环境下可执行
        5. 只返回代码或命令本身，不要包含任何解释或额外内容
        """
        
        prompt = f"{system_prompt}\n\n任务描述：{task_description}"
        
        if client:
            response = client.generate_content(prompt)
            return response.text.strip()
        else:
            return "错误: Gemini客户端未初始化"
    
    def runner(self, code_or_command):
        """
        Runner角色：执行代码或命令，并捕获输出
        
        Args:
            code_or_command: 要执行的代码或命令
        
        Returns:
            (success, output, error): 执行结果元组
        """
        try:
            # 判断是Python代码还是Shell命令
            if code_or_command.strip().startswith(('import ', 'def ', 'class ', 'print(', '#!/usr/bin/env python')):
                # 执行Python代码
                result = subprocess.run(
                    [sys.executable, '-c', code_or_command],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                # 执行Shell命令
                result = subprocess.run(
                    code_or_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            success = result.returncode == 0
            output = result.stdout
            error = result.stderr
            
            return success, output, error
        except Exception as e:
            return False, "", str(e)
    
    def tech_lead(self, task_description, code, error):
        """
        Tech Lead角色：分析代码和报错日志，指导Coder修复错误
        
        Args:
            task_description: 任务描述
            code: 生成的代码
            error: 执行错误信息
        
        Returns:
            修复建议
        """
        system_prompt = """
        你是一个专业的Tech Lead，负责分析代码和报错日志，指导Coder修复错误。
        请遵循以下规则：
        1. 分析任务描述、代码和错误信息
        2. 准确识别错误原因
        3. 提供清晰、具体的修复建议
        4. 确保修复后的代码能够正确执行
        5. 只返回修复建议，不要包含任何解释或额外内容
        """
        
        prompt = f"{system_prompt}\n\n任务描述：{task_description}\n\n生成的代码：{code}\n\n错误信息：{error}"
        
        if client:
            response = client.generate_content(prompt)
            return response.text.strip()
        else:
            return "错误: Gemini客户端未初始化"
    
    def run(self, task_description):
        """
        运行整个工作流程：Coder生成代码 → Runner执行 → Tech Lead分析错误（如果有）
        
        Args:
            task_description: 任务描述
        
        Returns:
            最终的执行结果
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
                
                # 3. Tech Lead分析错误
                console.print("[magenta]Tech Lead正在分析错误...[/magenta]")
                fix_suggestion = self.tech_lead(task_description, code, error)
                console.print(f"[magenta]修复建议：[/magenta]\n{fix_suggestion}")
                
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
