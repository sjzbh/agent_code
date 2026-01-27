import json
from config import AUDITOR_CONFIG
from utils import call_llm, clean_json_text
from prompts import AUDITOR_PROMPT
from rich.console import Console

console = Console()

class AuditorAgent:
    """
    审计员代理，根据执行日志判断任务是否成功
    """
    
    def __init__(self):
        """
        初始化AuditorAgent
        """
        pass
    
    def audit(self, task_description, execution_logs):
        """
        审计任务执行结果
        
        Args:
            task_description: 任务描述
            execution_logs: 执行日志
        
        Returns:
            dict: 审计结果，格式为 {"status": "PASS/FAIL", "feedback": "..."}
        """
        prompt = f"{AUDITOR_PROMPT}\n\n任务描述：{task_description}\n\n执行日志：{execution_logs}"
        
        console.print("[bold purple]Auditor正在分析执行结果...[/bold purple]")
        
        if AUDITOR_CONFIG['client']:
            response_text = call_llm(AUDITOR_CONFIG, prompt)
            response_text = clean_json_text(response_text)
            
            try:
                # 解析JSON响应
                result = json.loads(response_text)
                # 验证JSON格式是否正确
                if "status" in result and "feedback" in result:
                    console.print(f"[bold purple]审计结果：[/bold purple]{result['status']}")
                    console.print(f"[purple]反馈：[/purple]{result['feedback']}")
                    return result
                else:
                    # 如果JSON格式不正确，返回默认失败结果
                    console.print("[bold red]警告：Auditor返回的JSON格式不正确[/bold red]")
                    return {"status": "FAIL", "feedback": "审计过程中出现错误，无法正确解析审计结果"}
            except json.JSONDecodeError:
                # 如果无法解析JSON，返回默认失败结果
                console.print("[bold red]警告：Auditor返回的内容不是有效的JSON[/bold red]")
                return {"status": "FAIL", "feedback": "审计过程中出现错误，返回内容不是有效的JSON"}
        else:
            console.print("[bold red]错误：Auditor AI 未初始化[/bold red]")
            return {"status": "FAIL", "feedback": "Auditor AI 未初始化，无法进行审计"}
