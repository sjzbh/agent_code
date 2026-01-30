"""
Architect Role - Next Generation
"""
import json
from typing import Dict, Any
from config import WORKER_CONFIG
from utils import clean_json_text, call_llm, load_prompt, safe_json_parse
from rich.console import Console

console = Console()

class Architect:
    def __init__(self, model_name="gemini-1.5-pro"):
        self.model_name = model_name
        self.architect_config = WORKER_CONFIG  # Using the PM_CONFIG as architect config

    def design_system(self, user_requirement: str) -> Dict[str, Any]:
        """Design system architecture based on user requirements"""
        console.print("[bold blue]Architect 正在设计系统架构...[/bold blue]")
        
        # Load the architect prompt
        try:
            with open("roles/prompts/architect.yaml", 'r', encoding='utf-8') as f:
                import yaml
                prompts = yaml.safe_load(f)
                prompt_template = prompts['design_task']
        except:
            # Fallback prompt if file not found
            prompt_template = "你是系统架构师。请为以下需求设计系统架构：{user_requirement}。返回包含文件结构和接口定义的JSON。"
        
        prompt = prompt_template.format(user_requirement=user_requirement)
        
        if self.architect_config['client']:
            raw_response = call_llm(self.architect_config, prompt)
            design_doc = clean_json_text(raw_response)
            
            # Use safe JSON parsing
            design_data = safe_json_parse(design_doc, {})
            
            console.print("[bold green]系统设计完成！[/bold green]")
            
            # Save design document
            self.save_design_document(design_data, "design.md")
            
            return {
                "success": True,
                "design_document": design_data,
                "design_md": design_doc
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
        """Save design document to file"""
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
                    
            console.print(f"[green]设计文档已保存至 {filename}[/green]")
        except Exception as e:
            console.print(f"[red]保存设计文档失败: {e}[/red]")