"""
Project Manager Role - Responsible for converting user requirements into structured PRD
"""
import json
from typing import Dict, Any
from config import settings, ai_client_manager
from utils import clean_json_text, call_llm, load_prompt, safe_json_parse
from rich.console import Console
from memory.evolutionary_memory import evolutionary_memory

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
        self.pm_config = ai_client_manager.get_config("auto") or {
            "client": None,
            "type": "none",
            "model": "none"
        }
        self.prompts = load_prompt("roles/prompts/project_manager.yaml")
        self.memory = evolutionary_memory

    def clarify_requirements(self, user_input: str) -> Dict[str, Any]:
        """
        Clarify requirements if they are unclear
        Args:
            user_input: Raw user input
        Returns:
            Clarification result with questions or clear requirements
        """
        console.print("[bold blue]Project Manager 正在分析需求...[/bold blue]")
        
        # Retrieve relevant memories
        memory_context = self.memory.apply_solutions(user_input)
        memory_str = "\n".join(memory_context) if memory_context else "无历史经验"
        
        # Format the prompt using the YAML template
        prompt_template = self.prompts['clarification_task']
        prompt = prompt_template.format(
            user_input=user_input,
            evolutionary_memory=memory_str
        )
        
        if self.pm_config['client']:
            raw_response = call_llm(self.pm_config, prompt)
            clarification_result = clean_json_text(raw_response)
            
            # Parse the clarification result using safe parser
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
        
        # Retrieve relevant memories
        memory_context = self.memory.apply_solutions(clear_requirement)
        memory_str = "\n".join(memory_context) if memory_context else "无历史经验"
        
        # Format the prompt using the YAML template
        prompt_template = self.prompts['prd_generation_task']
        prompt = prompt_template.format(
            clear_requirement=clear_requirement,
            evolutionary_memory=memory_str
        )
        
        if self.pm_config['client']:
            raw_response = call_llm(self.pm_config, prompt)
            prd_result = clean_json_text(raw_response)
            
            # Parse the PRD result using safe parser
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