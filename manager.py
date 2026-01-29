import json
from config import PM_CONFIG
from rich.console import Console
from utils import clean_json_text, call_llm
from prompts import PM_PROMPT

console = Console()

# 日志适配器，可被外部替换
gui_adapter = type('GUIAdapter', (), {'print': lambda *args, **kwargs: console.print(*args, **kwargs)})()

class ProjectManager:
    """
    项目管理器，负责任务规划和状态管理
    """
    
    def __init__(self):
        """
        初始化ProjectManager
        """
        self.task_queue = []  # 任务队列
        self.project_state = {}  # 项目状态
        self.current_task_index = -1  # 当前执行的任务索引
    
    def plan_tasks(self, user_request):
        """
        将用户需求拆解为JSON任务列表
        
        Args:
            user_request: 用户需求
        
        Returns:
            list: 任务列表
        """
        prompt = f"{PM_PROMPT}\n\n用户需求：{user_request}"
        
        if PM_CONFIG['client']:
            response_text = call_llm(PM_CONFIG, prompt)
            response_text = clean_json_text(response_text)
            
            try:
                # 解析JSON响应
                tasks = json.loads(response_text)
                # 验证任务列表格式是否正确
                if isinstance(tasks, list):
                    # 更新任务队列
                    self.task_queue = tasks
                    # 更新项目状态
                    self.project_state['task_queue'] = tasks
                    self.project_state['status'] = 'planned'
                    self.current_task_index = -1
                    
                    # 返回JSON格式结果
                    result = {
                        "status": "success",
                        "user_request": user_request,
                        "tasks": tasks,
                        "task_count": len(tasks)
                    }
                    print(json.dumps(result, ensure_ascii=True))
                    return tasks
                else:
                    # 如果任务列表格式不正确，返回空列表
                    result = {
                        "status": "error",
                        "message": "Invalid task list format",
                        "tasks": []
                    }
                    print(json.dumps(result, ensure_ascii=True))
                    return []
            except json.JSONDecodeError:
                # 如果无法解析JSON，返回空列表
                result = {
                    "status": "error",
                    "message": "Failed to parse JSON response",
                    "tasks": []
                }
                print(json.dumps(result, ensure_ascii=True))
                return []
        else:
            result = {
                "status": "error",
                "message": "PM AI not initialized",
                "tasks": []
            }
            print(json.dumps(result, ensure_ascii=True))
            return []
    
    def update_plan(self, feedback, failed_task_id=None):
        """
        接收反馈，动态修改计划。
        Args:
            feedback: 反馈信息
            failed_task_id: 导致这次更新的失败任务 ID (例如 "001")
        """
        # 在 Prompt 中注入上下文，引导 PM 生成 "001-1" 这种 ID
        context_info = f"当前任务队列：{json.dumps(self.task_queue)}\n反馈信息：{feedback}"
        if failed_task_id:
            context_info += f"\n\n【重要指令】任务 '{failed_task_id}' 执行失败。请将该任务分解或生成修复任务。新任务的 ID 必须以 '{failed_task_id}-' 开头（例如 {failed_task_id}-1），以保持追踪。"

        update_prompt = f"{PM_PROMPT}\n\n{context_info}"
        
        console.print(f"[bold green]ProjectManager正在针对任务 {failed_task_id} 更新计划...[/bold green]")
        
        if PM_CONFIG['client']:
            response_text = call_llm(PM_CONFIG, update_prompt)
            response_text = clean_json_text(response_text)
            
            try:
                # 解析JSON响应
                updated_tasks = json.loads(response_text)
                # 验证任务列表格式是否正确
                if isinstance(updated_tasks, list):
                    # 更新任务队列
                    self.task_queue = updated_tasks
                    # 更新项目状态
                    self.project_state['task_queue'] = updated_tasks
                    self.project_state['status'] = 'updated'
                    
                    # 返回JSON格式结果
                    result = {
                        "status": "success",
                        "feedback": feedback,
                        "updated_tasks": updated_tasks,
                        "task_count": len(updated_tasks)
                    }
                    print(json.dumps(result, ensure_ascii=True))
                    return updated_tasks
                else:
                    # 如果任务列表格式不正确，返回当前任务队列
                    result = {
                        "status": "error",
                        "message": "Invalid task list format",
                        "updated_tasks": self.task_queue
                    }
                    print(json.dumps(result, ensure_ascii=True))
                    return self.task_queue
            except json.JSONDecodeError:
                # 如果无法解析JSON，返回当前任务队列
                result = {
                    "status": "error",
                    "message": "Failed to parse JSON response",
                    "updated_tasks": self.task_queue
                }
                print(json.dumps(result, ensure_ascii=True))
                return self.task_queue
        else:
            result = {
                "status": "error",
                "message": "PM AI not initialized",
                "updated_tasks": self.task_queue
            }
            print(json.dumps(result, ensure_ascii=True))
            return self.task_queue
    
    def get_next_task(self):
        """
        获取下一个待执行的任务
        
        Returns:
            dict: 下一个任务
        """
        self.current_task_index += 1
        if self.current_task_index < len(self.task_queue):
            task = self.task_queue[self.current_task_index]
            gui_adapter.print(f"[bold blue]开始执行任务：[/bold blue]{task['description']}")
            # 更新项目状态
            self.project_state['current_task'] = task
            self.project_state['status'] = 'executing'
            return task
        else:
            gui_adapter.print("[bold green]所有任务已执行完成[/bold green]")
            # 更新项目状态
            self.project_state['status'] = 'completed'
            return None
    
    def get_project_state(self):
        """
        获取当前项目状态
        
        Returns:
            dict: 项目状态
        """
        return self.project_state
    
    def reset(self):
        """
        重置项目管理器
        """
        self.task_queue = []
        self.project_state = {}
        self.current_task_index = -1
        gui_adapter.print("[bold yellow]ProjectManager已重置[/bold yellow]")
