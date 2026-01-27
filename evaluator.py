import os
from config import AUDITOR_CONFIG # 复用 Auditor 的配置（通常是高级模型）
from utils import call_llm, clean_json_text
from rich.console import Console
import json

console = Console()

class EvaluatorAgent:
    """
    评估官：负责对比新旧代码，决定是否采纳进化
    """
    def __init__(self):
        self.config = AUDITOR_CONFIG

    def evaluate_improvement(self, original_code, new_code, test_logs, task_desc):
        """
        评估代码改进是否有效
        """
        system_prompt = """
        你是一个拥有10年经验的首席架构师。你的任务是Code Review。
        你需要对比"原代码"和"新代码"，结合"沙箱测试日志"，判断新代码是否比原代码更好。
        
        **判断标准（优先级从高到低）：**
        1. **正确性**：沙箱测试必须通过（无报错，逻辑正确）。
        2. **健壮性**：新代码是否修复了潜在Bug，或增加了异常处理。
        3. **可读性/效率**：新代码是否更简洁、结构更清晰。
        
        请严格把关，如果新代码引入了新问题，或者没有实质提升，请拒绝。
        
        **输出要求：**
        只返回JSON格式：
        {
            "decision": "ACCEPT" 或 "REJECT",
            "reason": "详细的评估理由",
            "score": 0-100 (评分)
        }
        """
        
        user_prompt = f"""
        【任务目标】：{task_desc}
        
        【沙箱测试日志】：
        {test_logs}
        
        【原代码】：
        ```python
        {original_code}
        ```
        
        【新代码 (候选)】：
        ```python
        {new_code}
        ```
        """
        
        console.print("[bold magenta]Evaluator正在进行Code Review...[/bold magenta]")
        
        if self.config['client']:
            response = call_llm(self.config, system_prompt + "\n" + user_prompt)
            return clean_json_text(response)
        else:
            return '{"decision": "REJECT", "reason": "AI未初始化"}'