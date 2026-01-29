"""
Architect Role - Responsible for system design and architecture
"""
import json
from typing import Dict, Any
from config import settings, ai_client_manager
from utils import clean_json_text, call_llm
from prompts import ARCHITECT_PROMPT
from rich.console import Console

console = Console()

class Architect:
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        Initialize Architect role
        Args:
            model_name: Model name, defaults to "gemini-1.5-pro"
        """
        self.model_name = model_name
        self.architect_config = ai_client_manager.get_config("auto") or {
            "client": None,
            "type": "none",
            "model": "none"
        }

    def design_system(self, user_requirement: str) -> Dict[str, Any]:
        """
        Design system architecture based on user requirements
        Args:
            user_requirement: User requirements
        Returns:
            Design document with file structure and interfaces
        """
        console.print("[bold blue]Architect 正在设计系统架构...[/bold blue]")
        
        prompt = f"{ARCHITECT_PROMPT}\n\n用户需求：{user_requirement}"
        
        if self.architect_config['client']:
            raw_response = call_llm(self.architect_config, prompt)
            design_doc = clean_json_text(raw_response)
            
            # Parse the design document
            try:
                design_data = json.loads(design_doc)
                console.print("[bold green]系统设计完成！[/bold green]")
                
                # Save design document
                self.save_design_document(design_data, "design.md")
                
                return {
                    "success": True,
                    "design_document": design_data,
                    "design_md": design_doc
                }
            except json.JSONDecodeError:
                console.print("[bold red]设计文档解析失败，返回原始内容[/bold red]")
                return {
                    "success": False,
                    "design_document": {},
                    "design_md": design_doc,
                    "error": "设计文档解析失败"
                }
        else:
            console.print("[bold red]错误: Architect AI 未初始化[/bold red]")
            return {
                "success": False,
                "design_document": {},
                "design_md": "",
                "error": "Architect AI 未初始化"
            }

    def save_design_document(self, design_data: Dict[str, Any], filename: str = "design.md"):
        """
        Save design document to file
        Args:
            design_data: Design data dictionary
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# 系统设计文档\n\n")
                f.write("## 项目概述\n")
                f.write(f"{design_data.get('overview', 'N/A')}\n\n")
                
                f.write("## 文件结构\n")
                for file_path in design_data.get('file_structure', []):
                    f.write(f"- {file_path}\n")
                
                f.write("\n## 接口定义\n")
                for interface in design_data.get('interfaces', []):
                    f.write(f"- {interface}\n")
                
                f.write("\n## 技术栈\n")
                for tech in design_data.get('technologies', []):
                    f.write(f"- {tech}\n")
                    
            console.print(f"[green]设计文档已保存至 {filename}[/green]")
        except Exception as e:
            console.print(f"[red]保存设计文档失败: {e}[/red]")