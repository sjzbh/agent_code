"""
TechLead Role - Next Generation
"""
import json
from typing import Dict, Any
from config import WORKER_CONFIG
from utils import clean_json_text, call_llm, load_prompt, safe_json_parse
from rich.console import Console

console = Console()

class TechLead:
    """
    TechLead Role - responsible for code review and quality assurance
    """
    
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        Initialize TechLead role
        Args:
            model_name: Model name, defaults to "gemini-1.5-pro"
        """
        self.model_name = model_name
        self.techlead_config = WORKER_CONFIG

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
        
        # Load the techlead prompt
        try:
            with open("roles/prompts/techlead.yaml", 'r', encoding='utf-8') as f:
                import yaml
                prompts = yaml.safe_load(f)
                prompt_template = prompts['review_task']
        except:
            # Fallback prompt if file not found
            prompt_template = "你是技术主管。请审查以下代码：{code}，基于设计文档：{design_doc} 和任务描述：{task_desc}。返回是否批准及反馈。"
        
        prompt = prompt_template.format(
            code=code,
            design_doc=design_document,
            task_desc=task_description
        )
        
        if self.techlead_config['client']:
            raw_response = call_llm(self.techlead_config, prompt)
            review_result = clean_json_text(raw_response)
            
            # Use safe JSON parsing
            review_data = safe_json_parse(review_result, {})
            
            console.print("[bold green]代码审查完成！[/bold green]")
            
            # Determine if code is approved
            approved = review_data.get('approved', False)
            
            if approved:
                console.print("[bold green]代码审查通过！[/bold green]")
            else:
                console.print(f"[bold yellow]代码需要修改: {review_data.get('feedback', 'No feedback provided')}[/bold yellow]")
            
            return {
                "approved": approved,
                "feedback": review_data.get('feedback', ''),
                "issues": review_data.get('issues', []),
                "suggestions": review_data.get('suggestions', []),
                "raw_response": review_result
            }
        else:
            console.print("[bold red]错误: TechLead AI 未初始化[/bold red]")
            return {
                "approved": False,
                "feedback": "TechLead AI 未初始化",
                "issues": [],
                "suggestions": [],
                "raw_response": "",
                "error": "TechLead AI 未初始化"
            }