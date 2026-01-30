"""
Auditor Role - Responsible for final acceptance testing
"""
import json
from typing import Dict, Any
from config import settings, ai_client_manager
from utils import clean_json_text, call_llm, load_prompt, safe_json_parse
from rich.console import Console
from memory.evolutionary_memory import evolutionary_memory

console = Console()

class Auditor:
    """
    Auditor Role - responsible for final acceptance testing
    """
    
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        Initialize Auditor role
        Args:
            model_name: Model name, defaults to "gemini-1.5-pro"
        """
        self.model_name = model_name
        self.auditor_config = ai_client_manager.get_config("auto") or {
            "client": None,
            "type": "none",
            "model": "none"
        }
        self.prompts = load_prompt("roles/prompts/auditor.yaml")
        self.memory = evolutionary_memory

    def audit(self, task_description: str = None, execution_logs: list = None, project_artifacts: str = "") -> Dict[str, Any]:
        """
        Audit the project implementation
        Args:
            task_description: Description of the task
            execution_logs: List of execution logs
            project_artifacts: Project artifacts for review
        Returns:
            Audit result
        """
        console.print("[bold blue]Auditor 正在进行最终验收...[/bold blue]")
        
        # Retrieve relevant memories
        memory_context = self.memory.apply_solutions(task_description or "")
        memory_str = "\n".join(memory_context) if memory_context else "无历史经验"
        
        # Build the audit prompt
        logs_str = "\n".join(execution_logs) if execution_logs else "No execution logs provided"
        
        # Format the prompt using the YAML template
        prompt_template = self.prompts['acceptance_task']
        prompt = prompt_template.format(
            task_description=task_description or "No task description provided",
            execution_logs=logs_str,
            project_artifacts=project_artifacts,
            evolutionary_memory=memory_str
        )
        
        if self.auditor_config['client']:
            raw_response = call_llm(self.auditor_config, prompt)
            audit_result = clean_json_text(raw_response)
            
            # Parse the audit result using safe parser
            audit_data = safe_json_parse(audit_result, {})
            console.print("[bold green]审计完成！[/bold green]")

            status = audit_data.get('status', 'FAIL')
            feedback = audit_data.get('feedback', 'No feedback provided')

            if status == 'PASS':
                console.print("[bold green]项目验收通过！[/bold green]")
            else:
                console.print(f"[bold red]项目验收未通过: {feedback}[/bold red]")

            return {
                "status": status,
                "feedback": feedback,
                "details": audit_data,
                "raw_response": audit_result
            }
        else:
            console.print("[bold red]错误: Auditor AI 未初始化[/bold red]")
            return {
                "status": "FAIL",
                "feedback": "Auditor AI 未初始化",
                "raw_response": "",
                "error": "Auditor AI 未初始化"
            }