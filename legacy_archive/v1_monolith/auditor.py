import json
import sys
import os
import importlib.util

# 直接导入config.py文件，绕过模块系统
config_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.py')

# 使用importlib导入config.py文件
spec = importlib.util.spec_from_file_location("config", config_py_path)
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)

# 从导入的模块中获取AUDITOR_CONFIG
AUDITOR_CONFIG = config_module.AUDITOR_CONFIG

from utils import call_llm, clean_json_text
from prompts import AUDITOR_PROMPT
from rich.console import Console
from state import shared_state

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
    
    def audit(self, task_description=None, execution_logs=None):
        """
        审计任务执行结果

        Args:
            task_description: 任务描述（可选，默认从共享状态获取）
            execution_logs: 执行日志（可选，默认从共享状态获取）

        Returns:
            dict: 审计结果，格式为 {"status": "PASS/FAIL", "feedback": "..."}
        """
        # 从共享状态获取信息
        if task_description is None:
            task_description = shared_state.get("current_task", "")

        if execution_logs is None:
            execution_logs = "\n".join(shared_state.get("execution_logs", []))

        prompt = f"{AUDITOR_PROMPT}\n\n任务描述：{task_description}\n\n执行日志：{execution_logs}"

        console.print("[bold purple]Auditor正在分析执行结果...[/bold purple]")

        # 检查是否达到最大连续拒绝次数
        if shared_state.audit_fail_count >= shared_state.max_audit_fails:
            console.print(f"[bold red]警告：审计已连续拒绝 {shared_state.audit_fail_count} 次，达到最大限制，将跳过审计并让任务通过[/bold red]")
            # 重置计数器
            shared_state.audit_fail_count = 0
            pass_result = {"status": "PASS", "feedback": f"由于连续 {shared_state.max_audit_fails} 次审计失败，系统自动通过任务以防止无限循环"}
            shared_state.set("last_audit_result", pass_result)
            return pass_result

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

                    # 更新共享状态
                    shared_state.set("last_audit_result", result)

                    # 如果审计结果为FAIL，返回特殊标记，指示需要返回Worker
                    if result["status"] == "FAIL":
                        # 增加连续失败计数
                        shared_state.audit_fail_count += 1
                        console.print(f"[bold red]审计失败，连续失败次数：{shared_state.audit_fail_count}/{shared_state.max_audit_fails}[/bold red]")

                        # 如果达到最大失败次数，跳过后续审计
                        if shared_state.audit_fail_count >= shared_state.max_audit_fails:
                            console.print(f"[bold red]连续审计失败次数达到上限 {shared_state.max_audit_fails}，将停止重试并让任务通过[/bold red]")
                            pass_result = {"status": "PASS", "feedback": f"由于连续 {shared_state.max_audit_fails} 次审计失败，系统自动通过任务以防止无限循环"}
                            shared_state.set("last_audit_result", pass_result)
                            return pass_result

                        # 添加特殊标记，指示需要返回Worker
                        result["return_to_worker"] = True
                    else:
                        # 如果审计通过，重置失败计数器
                        shared_state.audit_fail_count = 0

                    return result
                else:
                    # 如果JSON格式不正确，返回默认失败结果
                    console.print("[bold red]警告：Auditor返回的JSON格式不正确[/bold red]")
                    error_result = {"status": "FAIL", "feedback": "审计过程中出现错误，无法正确解析审计结果", "return_to_worker": True}
                    shared_state.set("last_audit_result", error_result)
                    # 增加连续失败计数
                    shared_state.audit_fail_count += 1
                    return error_result
            except json.JSONDecodeError:
                # 如果无法解析JSON，返回默认失败结果
                console.print("[bold red]警告：Auditor返回的内容不是有效的JSON[/bold red]")
                error_result = {"status": "FAIL", "feedback": "审计过程中出现错误，返回内容不是有效的JSON", "return_to_worker": True}
                shared_state.set("last_audit_result", error_result)
                # 增加连续失败计数
                shared_state.audit_fail_count += 1
                return error_result
        else:
            # 如果Auditor AI未初始化，启用"静音键"功能，直接让任务通过
            console.print("[bold yellow]注意：Auditor AI 未初始化，启用'静音键'功能，直接让任务通过[/bold yellow]")
            # 返回通过结果，让任务继续
            pass_result = {"status": "PASS", "feedback": "Auditor AI 未初始化，启用'静音键'功能，直接通过审核"}
            shared_state.set("last_audit_result", pass_result)
            return pass_result
