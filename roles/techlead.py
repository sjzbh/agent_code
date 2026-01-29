"""
TechLead Role - Responsible for code review and quality assurance
"""
import json
from typing import Dict, Any
from config import settings, ai_client_manager
from utils import clean_json_text, call_llm
from prompts import TECH_LEAD_PROMPT
from rich.console import Console

console = Console()

class TechLead:
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        Initialize TechLead role
        Args:
            model_name: Model name, defaults to "gemini-1.5-pro"
        """
        self.model_name = model_name
        self.techlead_config = ai_client_manager.get_config("auto") or {
            "client": None,
            "type": "none",
            "model": "none"
        }

    def review_code(self, code: str, design_document: str, task_description: str) -> Dict[str, Any]:
        """
        Review code implementation against design document
        Args:
            code: Code to review
            design_document: Original design document
            task_description: Task description
        Returns:
            Review result with feedback and approval status
        """
        console.print("[bold blue]TechLead 正在审查代码...[/bold blue]")
        
        prompt = f"{TECH_LEAD_PROMPT}\n\n系统设计文档：{design_document}\n\n任务描述：{task_description}\n\n待审查代码：{code}"
        
        if self.techlead_config['client']:
            raw_response = call_llm(self.techlead_config, prompt)
            review_result = clean_json_text(raw_response)
            
            # Parse the review result
            try:
                review_data = json.loads(review_result)
                console.print("[bold green]代码审查完成！[/bold green]")
                
                # Determine if code is approved
                approved = review_data.get('approved', False)
                
                if approved:
                    console.print("[bold green]代码审查通过！[/bold green]")
                else:
                    console.print("[bold yellow]代码需要修改！[/bold yellow]")
                
                return {
                    "approved": approved,
                    "feedback": review_data.get('feedback', ''),
                    "issues": review_data.get('issues', []),
                    "suggestions": review_data.get('suggestions', []),
                    "review_raw": review_result
                }
            except json.JSONDecodeError:
                console.print("[bold red]审查结果解析失败，返回原始内容[/bold red]")
                return {
                    "approved": False,
                    "feedback": "审查结果解析失败",
                    "issues": [],
                    "suggestions": [],
                    "review_raw": review_result,
                    "error": "审查结果解析失败"
                }
        else:
            console.print("[bold red]错误: TechLead AI 未初始化[/bold red]")
            return {
                "approved": False,
                "feedback": "TechLead AI 未初始化",
                "issues": [],
                "suggestions": [],
                "review_raw": "",
                "error": "TechLead AI 未初始化"
            }

    def approve_code(self, code: str, design_document: str, task_description: str) -> bool:
        """
        Simple approval method that returns whether code is approved
        Args:
            code: Code to approve
            design_document: Design document
            task_description: Task description
        Returns:
            Boolean indicating approval status
        """
        review_result = self.review_code(code, design_document, task_description)
        return review_result.get('approved', False)