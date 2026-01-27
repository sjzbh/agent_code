import subprocess
import sys
import os
import tempfile
import re
from config import client
from utils import clean_json_text
from rich.console import Console

console = Console()

class WorkerAgent:
    def __init__(self, model_name="gemini-1.5-pro"):
        self.model_name = model_name
        self.max_retries = 3
    
    def coder(self, task_description):
        # ... (system_prompt 部分保持不变，或者你可以稍微精简) ...
        system_prompt = """
        你是一个专业的Coder。请根据任务生成可执行的Shell命令或Python代码。
        如果是Python代码，必须是完整的、可独立运行的脚本。
        不要使用 input() 等待用户输入。
        只返回代码本身，尽量不要包含 ``` 标记，如果包含我会自动清洗。
        """
        prompt = f"{system_prompt}\n\n任务描述：{task_description}"
        
        if client:
            response = client.generate_content(prompt)
            # 清洗一下，防止 AI 返回 ```python ... ```
            return clean_json_text(response.text.strip())
        else:
            return "错误: Gemini客户端未初始化"
    
    def runner(self, code_or_command):
        """
        更稳健的 Runner：将 Python 代码写入临时文件执行
        """
        try:
            # 清理可能残留的 markdown 标记
            code_or_command = clean_json_text(code_or_command)
            
            # 简单判断是否为 Python 代码 (包含 import, def, print 等)
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
                # Shell 命令
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
            # 这种写法能同时捕获 stdout 和 stderr
            output = result.stdout + "\n" + result.stderr 
            
            return success, output.strip(), result.stderr
            
        except Exception as e:
            return False, "", str(e)

    # ... (tech_lead 和 run 方法保持原样即可) ...
    # 注意：在 tech_lead 里也建议调用 coder 生成新代码
    def tech_lead(self, task_description, code, error):
        # ... (保持原样) ...
        prompt = f"你是一个Tech Lead。代码执行报错。\n任务：{task_description}\n代码：{code}\n报错：{error}\n请给出修复建议。"
        if client:
             response = client.generate_content(prompt)
             return response.text.strip()
        return "Gemini未初始化"

    def run(self, task_description):
        # ... (保持原样，逻辑没问题) ...
        # 只要把上面的 coder 和 runner 替换掉，这里就能正常工作
        # 为了节省篇幅，这里复用你原来的 run 逻辑，它是没问题的。
        return super().run(task_description) if hasattr(super(), 'run') else self._original_run_logic(task_description)

    # 补充：为了方便你直接复制，我把 run 方法的逻辑简写在这里，你可以保留原来文件的 run 方法
    def _original_run_logic(self, task_description):
        # 这里直接粘贴你原文件里 run 方法的代码即可
        console.print(f"[bold blue]开始执行任务：[/bold blue]{task_description}")
        for retry in range(self.max_retries):
             # ... (完全保留原逻辑) ...
             # 只需要注意：self.coder() 现在返回的是清洗过的代码
             # self.runner() 现在能跑通复杂代码了
             code = self.coder(task_description)
             # ...
             success, output, error = self.runner(code)
             if success:
                 return {"success": True, "output": output, "code": code}
             # ... 失败重试逻辑 ...
             fix_suggestion = self.tech_lead(task_description, code, error)
             task_description += f"\n修复建议：{fix_suggestion}"
        
        return {"success": False, "error": error, "code": code}

    # 真正的 run 方法入口
    def run(self, task_description):
        return self._original_run_logic(task_description)