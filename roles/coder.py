"""
Coder Role - Responsible for implementing code based on design documents
"""
import json
import os
from typing import Dict, Any
from config import settings, ai_client_manager
from utils import clean_json_text, call_llm
from prompts import CODER_PROMPT
from rich.console import Console

console = Console()

class Coder:
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        Initialize Coder role
        Args:
            model_name: Model name, defaults to "gemini-1.5-pro"
        """
        self.model_name = model_name
        self.coder_config = ai_client_manager.get_config("auto") or {
            "client": None,
            "type": "none",
            "model": "none"
        }

    def implement_code(self, design_document: str, task_description: str) -> Dict[str, Any]:
        """
        Implement code based on design document
        Args:
            design_document: System design document
            task_description: Specific task description
        Returns:
            Implementation result with code files
        """
        console.print("[bold blue]Coder 正在实现代码...[/bold blue]")
        
        prompt = f"{CODER_PROMPT}\n\n系统设计文档：{design_document}\n\n任务描述：{task_description}"
        
        if self.coder_config['client']:
            raw_response = call_llm(self.coder_config, prompt)
            code_output = clean_json_text(raw_response)
            
            # Parse the code output
            try:
                code_data = json.loads(code_output)
                console.print("[bold green]代码实现完成！[/bold green]")
                
                # Save code files
                files_created = self.save_code_files(code_data.get('files', []))
                
                return {
                    "success": True,
                    "code_files": code_data.get('files', []),
                    "files_created": files_created,
                    "raw_output": code_output
                }
            except json.JSONDecodeError:
                console.print("[bold red]代码输出解析失败，返回原始内容[/bold red]")
                return {
                    "success": False,
                    "code_files": [],
                    "files_created": [],
                    "raw_output": code_output,
                    "error": "代码输出解析失败"
                }
        else:
            console.print("[bold red]错误: Coder AI 未初始化[/bold red]")
            return {
                "success": False,
                "code_files": [],
                "files_created": [],
                "raw_output": "",
                "error": "Coder AI 未初始化"
            }

    def save_code_files(self, files_data: list) -> list:
        """
        Save code files to disk
        Args:
            files_data: List of file dictionaries with path and content
        Returns:
            List of created file paths
        """
        created_files = []
        for file_info in files_data:
            file_path = file_info.get('path', '')
            content = file_info.get('content', '')
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            created_files.append(file_path)
            console.print(f"[green]创建文件: {file_path}[/green]")
        
        return created_files