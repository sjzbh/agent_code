"""
Project Manager Role - Next Generation
"""
import json
from typing import Dict, Any
from config import PM_CONFIG
from utils import clean_json_text, call_llm, load_prompt, safe_json_parse
from rich.console import Console

console = Console()

class ProjectManager:
    """
    Project Manager Role - converts user requirements into structured PRD
    """
    
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        Initialize Project Manager role
        Args:
            model_name: Model name, defaults to "gemini-1.5-pro"
        """
        self.model_name = model_name
        self.pm_config = PM_CONFIG

    def clarify_requirements(self, user_input: str) -> Dict[str, Any]:
        """
        Clarify requirements if they are unclear
        Args:
            user_input: Raw user input
        Returns:
            Clarification result with questions or clear requirements
        """
        console.print("[bold blue]Project Manager 正在分析需求...[/bold blue]")
        
        # Load the project manager prompt
        try:
            with open("roles/prompts/project_manager.yaml", 'r', encoding='utf-8') as f:
                import yaml
                prompts = yaml.safe_load(f)
                prompt_template = prompts['clarification_task']
        except:
            # Fallback prompt if file not found
            prompt_template = "你是产品经理。请分析以下用户需求：{user_input}。如果需求不明确，请提出澄清问题；如果需求明确，请返回结构化的PRD。"
        
        prompt = prompt_template.format(user_input=user_input)
        
        if self.pm_config['client']:
            raw_response = call_llm(self.pm_config, prompt)
            clarification_result = clean_json_text(raw_response)
            
            # Use safe JSON parsing
            clarification_data = safe_json_parse(clarification_result, {})
            
            console.print("[bold green]需求分析完成！[/bold green]")
            
            return {
                "needs_clarification": clarification_data.get('needs_clarification', False),
                "questions": clarification_data.get('questions', []),
                "clear_requirement": clarification_data.get('clear_requirement', user_input),
                "raw_response": clarification_result
            }
        else:
            console.print("[bold red]错误: Project Manager AI 未初始化[/bold red]")
            return {
                "needs_clarification": True,
                "questions": ["AI未初始化，请提供更详细的需求信息"],
                "clear_requirement": user_input,
                "raw_response": "",
                "error": "Project Manager AI 未初始化"
            }

    def generate_prd(self, clear_requirement: str) -> Dict[str, Any]:
        """
        Generate structured PRD from clear requirements
        Args:
            clear_requirement: Clear and detailed requirement
        Returns:
            Structured PRD document
        """
        console.print("[bold blue]Project Manager 正在生成PRD...[/bold blue]")
        
        # Load the PRD generation prompt
        try:
            with open("roles/prompts/project_manager.yaml", 'r', encoding='utf-8') as f:
                import yaml
                prompts = yaml.safe_load(f)
                prompt_template = prompts['prd_generation_task']
        except:
            # Fallback prompt if file not found
            prompt_template = "你是产品经理。请为以下明确的需求生成PRD：{requirement}。返回包含功能列表、技术要求、验收标准的结构化PRD。"
        
        prompt = prompt_template.format(requirement=clear_requirement)
        
        if self.pm_config['client']:
            raw_response = call_llm(self.pm_config, prompt)
            prd_result = clean_json_text(raw_response)
            
            # Use safe JSON parsing
            prd_data = safe_json_parse(prd_result, {})
            
            console.print("[bold green]PRD生成完成！[/bold green]")
            
            # Save PRD document
            self.save_prd_document(prd_data, "prd_document.json")
            
            return {
                "success": True,
                "prd_document": prd_data,
                "raw_response": prd_result
            }
        else:
            console.print("[bold red]错误: Project Manager AI 未初始化[/bold red]")
            return {
                "success": False,
                "prd_document": {},
                "raw_response": "",
                "error": "Project Manager AI 未初始化"
            }

    def save_prd_document(self, prd_data: Dict[str, Any], filename: str = "prd_document.json"):
        """
        Save PRD document to file
        Args:
            prd_data: PRD data dictionary
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(prd_data, f, ensure_ascii=False, indent=2)
            console.print(f"[green]PRD文档已保存至 {filename}[/green]")
        except Exception as e:
            console.print(f"[red]保存PRD文档失败: {e}[/red]")