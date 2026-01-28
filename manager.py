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
        
        gui_adapter.print("[bold green]ProjectManager正在规划任务...[/bold green]")
        
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
                    gui_adapter.print(f"[bold green]任务规划完成，共生成 {len(tasks)} 个任务[/bold green]")
                    for i, task in enumerate(tasks):
                        gui_adapter.print(f"[green]任务 {i+1}:[/green] {task['description']} (优先级: {task['priority']})")
                    # 更新项目状态
                    self.project_state['task_queue'] = tasks
                    self.project_state['status'] = 'planned'
                    self.current_task_index = -1
                    return tasks
                else:
                    # 如果任务列表格式不正确，返回空列表
                    gui_adapter.print("[bold red]警告：ProjectManager返回的任务列表格式不正确[/bold red]")
                    return []
            except json.JSONDecodeError:
                # 如果无法解析JSON，返回空列表
                gui_adapter.print("[bold red]警告：ProjectManager返回的内容不是有效的JSON[/bold red]")
                return []
        else:
            gui_adapter.print("[bold red]错误：PM AI 未初始化[/bold red]")
            return []
    
    def update_plan(self, feedback):
        """
        接收Auditor的反馈或用户的插队需求，动态修改队列中尚未开始的任务
        
        Args:
            feedback: 反馈信息
        
        Returns:
            list: 更新后的任务列表
        """
        update_prompt = f"{PM_PROMPT}\n\n当前任务队列：{json.dumps(self.task_queue)}\n\n反馈信息：{feedback}"
        
        gui_adapter.print("[bold green]ProjectManager正在更新任务计划...[/bold green]")
        
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
                    gui_adapter.print(f"[bold green]任务计划更新完成，共 {len(updated_tasks)} 个任务[/bold green]")
                    for i, task in enumerate(updated_tasks):
                        gui_adapter.print(f"[green]任务 {i+1}:[/green] {task['description']} (优先级: {task['priority']})")
                    # 更新项目状态
                    self.project_state['task_queue'] = updated_tasks
                    self.project_state['status'] = 'updated'
                    return updated_tasks
                else:
                    # 如果任务列表格式不正确，返回当前任务队列
                    gui_adapter.print("[bold red]警告：ProjectManager返回的任务列表格式不正确[/bold red]")
                    return self.task_queue
            except json.JSONDecodeError:
                # 如果无法解析JSON，返回当前任务队列
                gui_adapter.print("[bold red]警告：ProjectManager返回的内容不是有效的JSON[/bold red]")
                return self.task_queue
        else:
            gui_adapter.print("[bold red]错误：PM AI 未初始化[/bold red]")
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
