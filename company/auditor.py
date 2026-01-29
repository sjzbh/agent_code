"""
Auditor Agent for the Virtual Software Company
"""
import json
from typing import Dict, Any
from config import settings, ai_client_manager
from utils import clean_json_text, call_llm
from prompts import AUDITOR_PROMPT
from rich.console import Console

console = Console()

class AuditorAgent:
    """
    Auditor Agent - responsible for final acceptance testing
    """
    
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        Initialize Auditor Agent
        Args:
            model_name: Model name, defaults to "gemini-1.5-pro"
        """
        self.model_name = model_name
        self.auditor_config = ai_client_manager.get_config("auto") or {
            "client": None,
            "type": "none",
            "model": "none"
        }

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
        prompt = f"{AUDITOR_PROMPT}\n\n任务描述：{task_description}\n\n执行日志：{logs_str}"
        
        if self.auditor_config['client']:
            raw_response = call_llm(self.auditor_config, prompt)
            audit_result = clean_json_text(raw_response)
            
            # Parse the audit result
            try:
                audit_data = json.loads(audit_result)
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
            except json.JSONDecodeError:
                console.print("[bold red]审计结果解析失败，返回原始内容[/bold red]")
                return {
                    "status": "FAIL",
                    "feedback": "审计结果解析失败",
                    "raw_response": audit_result,
                    "error": "JSON解析失败"
                }
        else:
            console.print("[bold red]错误: Auditor AI 未初始化[/bold red]")
            return {
                "status": "FAIL",
                "feedback": "Auditor AI 未初始化",
                "raw_response": "",
                "error": "Auditor AI 未初始化"
            }