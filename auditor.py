import json
from config import AUDITOR_CONFIG
from utils import call_llm, clean_json_text
from prompts import AUDITOR_PROMPT, FAILURE_REPORT_PROMPT

class AuditorAgent:
    """
    审计员代理，根据执行日志判断任务是否成功
    """
    
    def __init__(self):
        """
        初始化AuditorAgent
        """
        pass
    
    def generate_failure_report(self, root_task_id, failure_history):
        """
        生成失败分析报告
        
        Args:
            root_task_id: 根任务ID
            failure_history: 失败历史记录
        
        Returns:
            str: 失败分析报告
        """
        from prompts import FAILURE_REPORT_PROMPT
        
        # 构建失败历史日志
        failure_history_str = "\n".join(failure_history)
        
        # 构建提示词
        prompt = FAILURE_REPORT_PROMPT.format(
            failure_history=failure_history_str,
            root_task_id=root_task_id
        )
        
        # 调用LLM生成报告
        if AUDITOR_CONFIG['client']:
            response = call_llm(AUDITOR_CONFIG, prompt)
            return response
        else:
            # 如果AI未初始化，返回简单报告
            return f"# 任务 {root_task_id} 失败分析报告\n\n累计失败 {len(failure_history)} 次，达到最大容忍阈值。\n\n建议：检查环境配置、API密钥设置等基础问题。"
    
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
        
        if AUDITOR_CONFIG['client']:
            response_text = call_llm(AUDITOR_CONFIG, prompt)
            response_text = clean_json_text(response_text)
            
            try:
                # 解析JSON响应
                result = json.loads(response_text)
                # 验证JSON格式是否正确
                if "status" in result and "feedback" in result:
                    # 返回JSON格式结果
                    audit_result = {
                        "status": "success",
                        "audit_status": result["status"],
                        "feedback": result["feedback"],
                        "task_description": task_description
                    }
                    print(json.dumps(audit_result, ensure_ascii=True))
                    return result
                else:
                    # 如果JSON格式不正确，返回默认失败结果
                    error_result = {
                        "status": "error",
                        "message": "Invalid JSON format from Auditor",
                        "audit_status": "FAIL",
                        "feedback": "Audit error: Invalid JSON format"
                    }
                    print(json.dumps(error_result, ensure_ascii=True))
                    return {"status": "FAIL", "feedback": "Audit error: Invalid JSON format"}
            except json.JSONDecodeError:
                # 如果无法解析JSON，返回默认失败结果
                error_result = {
                    "status": "error",
                    "message": "Failed to parse JSON response",
                    "audit_status": "FAIL",
                    "feedback": "Audit error: Failed to parse JSON"
                }
                print(json.dumps(error_result, ensure_ascii=True))
                return {"status": "FAIL", "feedback": "Audit error: Failed to parse JSON"}
        else:
            error_result = {
                "status": "error",
                "message": "Auditor AI not initialized",
                "audit_status": "FAIL",
                "feedback": "Auditor AI not initialized"
            }
            print(json.dumps(error_result, ensure_ascii=True))
            return {"status": "FAIL", "feedback": "Auditor AI not initialized"}
