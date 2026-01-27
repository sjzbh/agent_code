import json
from config import client
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
        system_prompt = """
        你是一个审计员，你看不见源代码。只根据日志判断任务是否成功。如果失败或有隐患，给出简短的修复建议。
        请遵循以下规则：
        1. 仔细分析执行日志，判断任务是否成功完成
        2. 如果任务成功完成，返回 PASS 状态
        3. 如果任务失败或存在隐患，返回 FAIL 状态，并给出简短的修复建议
        4. 只返回 JSON 格式的结果，不要包含任何其他内容
        5. JSON 格式必须严格为：{"status": "PASS/FAIL", "feedback": "..."}
        """
        
        prompt = f"{system_prompt}\n\n任务描述：{task_description}\n\n执行日志：{execution_logs}"
        
        console.print("[bold purple]Auditor正在分析执行结果...[/bold purple]")
        
        if client:
            response = client.generate_content(prompt)
            response_text = response.text.strip()
            
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
            console.print("[bold red]错误：Gemini客户端未初始化[/bold red]")
            return {"status": "FAIL", "feedback": "Gemini客户端未初始化，无法进行审计"}
