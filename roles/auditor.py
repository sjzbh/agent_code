"""
Auditor Role - Next Generation
"""
import json
from typing import Dict, Any
from config import PM_CONFIG  # Using PM_CONFIG as it typically has more capabilities
from utils import clean_json_text, call_llm, load_prompt, safe_json_parse
from rich.console import Console

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
        self.auditor_config = PM_CONFIG  # Using PM_CONFIG as auditors typically need high-level reasoning

    def audit(self, task_description: str = None, execution_logs: list = None) -> Dict[str, Any]:
        """
        Audit the project implementation
        Args:
            task_description: Description of the task
            execution_logs: List of execution logs
        Returns:
            Audit result
        """
        console.print("[bold blue]Auditor 正在进行最终验收...[/bold blue]")
        
        # Build the audit prompt
        logs_str = "\n".join(execution_logs) if execution_logs else "No execution logs provided"
        
        # Load the auditor prompt
        try:
            with open("roles/prompts/auditor.yaml", 'r', encoding='utf-8') as f:
                import yaml
                prompts = yaml.safe_load(f)
                prompt_template = prompts['acceptance_task']
        except:
            # Fallback prompt if file not found
            prompt_template = "你是审计员。请根据以下任务描述和执行日志进行最终验收：任务描述：{task_desc}，执行日志：{exec_logs}。返回验收结果（PASS/FAIL）和反馈。"
        
        prompt = prompt_template.format(
            task_desc=task_description or "No task description provided",
            exec_logs=logs_str
        )
        
        if self.auditor_config['client']:
            raw_response = call_llm(self.auditor_config, prompt)
            audit_result = clean_json_text(raw_response)
            
            # Use safe JSON parsing
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