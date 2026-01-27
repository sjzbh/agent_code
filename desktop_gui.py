#!/usr/bin/env python3
"""
多AI协作工具 - 桌面GUI界面
基于Tkinter实现的可视化聊天界面
"""
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import threading
import time
import sys
import os

# 添加当前目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manager import ProjectManager
from worker import WorkerAgent
from auditor import AuditorAgent
from sandbox import SandboxManager
from evaluator import EvaluatorAgent

class DesktopGUI:
    """
    桌面GUI界面类
    """
    def __init__(self):
        """
        初始化GUI
        """
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("多AI协作工具")
        
        # 获取屏幕分辨率并适配
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 设置窗口大小为屏幕的80%
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # 计算窗口位置（居中）
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口大小和位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(True, True)
        
        # 设置窗口图标（如果有）
        # self.root.iconbitmap("icon.ico")
        
        # 初始化所有组件
        self.manager = ProjectManager()
        self.worker = WorkerAgent()
        self.auditor = AuditorAgent()
        self.sandbox = SandboxManager()
        self.evaluator = EvaluatorAgent()
        
        # 创建界面组件
        self.create_widgets()
        
        # 绑定事件
        self.bind_events()
        
        # 设置谷歌Gemini风格的主题
        self.set_tech_theme()
    
    def create_widgets(self):
        """
        创建界面组件
        """
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部标题
        title_label = ttk.Label(
            main_frame, 
            text="💬 多AI协作工具", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(fill=tk.X, pady=5)
        
        # 聊天区域
        chat_frame = ttk.LabelFrame(main_frame, text="聊天历史", padding="10")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 聊天文本框
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            font=("Arial", 11)
        )
        self.chat_text.pack(fill=tk.BOTH, expand=True)
        self.chat_text.config(state=tk.DISABLED)
        
        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="输入需求", padding="10")
        input_frame.pack(fill=tk.X, pady=5)
        
        # 输入文本框
        self.input_text = scrolledtext.ScrolledText(
            input_frame, 
            wrap=tk.WORD, 
            font=("Arial", 11),
            height=6
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # 保存按钮
        self.save_button = ttk.Button(
            button_frame, 
            text="💾 保存", 
            command=self.save_request,
            style="Tech.TButton"
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # 发送按钮
        self.send_button = ttk.Button(
            button_frame, 
            text="🚀 发送", 
            command=self.send_request,
            style="Tech.TButton"
        )
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        self.exit_button = ttk.Button(
            button_frame, 
            text="❌ 退出", 
            command=self.exit_app,
            style="Tech.TButton"
        )
        self.exit_button.pack(side=tk.RIGHT, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(
            main_frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            font=("Arial", 10)
        )
        status_bar.pack(fill=tk.X, pady=5)
        
        # 初始消息
        self.add_message("系统", "您好！我是多AI协作工具的项目经理。请输入您的需求，我会将其拆解为具体的任务。")
    
    def bind_events(self):
        """
        绑定事件
        """
        # 绑定回车键发送（需要FocusIn事件来捕获）
        self.input_text.bind("<Return>", self.on_enter_press)
        # 绑定Ctrl+回车键换行
        self.input_text.bind("<Control-Return>", self.on_ctrl_enter_press)
    
    def on_enter_press(self, event):
        """
        处理回车键事件
        """
        # 发送消息
        self.send_request()
        return "break"  # 阻止默认行为
    
    def on_ctrl_enter_press(self, event):
        """
        处理Ctrl+回车键事件
        """
        # 插入换行符
        self.input_text.insert(tk.INSERT, "\n")
        return "break"  # 阻止默认行为
    
    def add_message(self, sender, message):
        """
        添加消息到聊天区域
        """
        self.chat_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        if sender == "系统":
            self.chat_text.insert(tk.END, f"[{timestamp}] [系统]: {message}\n", "system")
        else:
            self.chat_text.insert(tk.END, f"[{timestamp}] [我]: {message}\n", "user")
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)
    
    def save_request(self):
        """
        保存需求
        """
        content = self.input_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "请输入需求内容！")
            return
        
        # 保存到文件
        import os
        from datetime import datetime
        filename = f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        # 添加消息
        self.add_message("我", content)
        self.add_message("系统", f"需求已保存为: {filename}")
        
        # 清空输入框
        self.input_text.delete(1.0, tk.END)
    
    def process_request(self, user_input):
        """
        处理用户需求的函数
        """
        try:
            # 调用ProjectManager进行任务规划
            tasks = self.manager.plan_tasks(user_input)
            
            if not tasks:
                return "任务规划失败，请重试。"
            
            # 执行任务队列
            task_index = 0
            result = []
            
            while task_index < len(self.manager.task_queue):
                # 提取当前最高优先级的任务
                sorted_tasks = sorted(self.manager.task_queue[task_index:], key=lambda x: {
                    "high": 0, "medium": 1, "low": 2
                }[x.get("priority", "medium")])
                
                if not sorted_tasks:
                    break
                
                current_task = sorted_tasks[0]
                task_index = self.manager.task_queue.index(current_task)
                
                # 交给Worker执行
                execution_result = self.worker.run(current_task["description"])
                
                # 生成执行日志
                if execution_result["success"]:
                    execution_logs = f"执行成功！\n输出：{execution_result['output']}\n代码：{execution_result['code']}"
                else:
                    execution_logs = f"执行失败！\n错误：{execution_result['error']}\n代码：{execution_result['code']}"
                
                # 交给Auditor审计
                audit_result = self.auditor.audit(current_task["description"], execution_logs)
                
                # 构建结果信息
                task_result = f"任务: {current_task['description']}\n"
                task_result += f"状态: {audit_result['status']}\n"
                task_result += f"反馈: {audit_result['feedback']}\n"
                result.append(task_result)
                
                # PM根据反馈决定是继续下一个任务，还是插入修复任务
                if audit_result["status"] == "FAIL":
                    # 更新任务计划
                    updated_tasks = self.manager.update_plan(audit_result["feedback"])
                    # 重置任务索引，重新开始执行
                    task_index = 0
                else:
                    # 继续下一个任务
                    task_index += 1
            
            # 任务执行完成，构建项目状态
            project_state = self.manager.get_project_state()
            final_result = "\n".join(result)
            final_result += f"\n项目状态: {project_state.get('status', 'unknown')}\n"
            final_result += f"完成任务数: {len(project_state.get('task_queue', []))}\n"
            
            return final_result
        except Exception as e:
            return f"处理需求时发生错误: {str(e)}"
    
    def send_request(self):
        """
        发送需求
        """
        content = self.input_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "请输入需求内容！")
            return
        
        # 保存需求
        self.save_request()
        
        # 更新状态
        self.status_var.set("正在处理需求...")
        self.root.update()
        
        # 在后台线程中处理需求
        def process_task():
            try:
                # 调用process_request处理需求
                result = self.process_request(content)
                self.add_message("系统", result)
            except Exception as e:
                self.add_message("系统", f"处理需求时发生错误: {str(e)}")
            finally:
                # 更新状态
                self.status_var.set("就绪")
                self.root.update()
        
        # 启动后台线程
        threading.Thread(target=process_task, daemon=True).start()
    
    def exit_app(self):
        """
        退出应用
        """
        if messagebox.askyesno("退出", "确定要退出吗？"):
            self.root.destroy()
    
    def set_tech_theme(self):
        """
        设置谷歌Gemini风格的主题
        """
        # 设置窗口背景色
        self.root.configure(bg="#ffffff")
        
        # 创建谷歌Gemini风格的颜色方案
        self.colors = {
            "bg": "#ffffff",
            "fg": "#333333",
            "accent": "#4285f4",  # 谷歌蓝
            "secondary": "#ea4335",  # 谷歌红
            "border": "#e0e0e0",
            "chat_bg": "#f8f9fa",
            "input_bg": "#ffffff",
            "button_bg": "#4285f4",
            "button_fg": "#ffffff",
            "user_bubble": "#e8f0fe",  # 用户消息气泡
            "system_bubble": "#f1f3f4"  # 系统消息气泡
        }
        
        # 更新所有组件的样式
        self.update_component_styles()
    
    def update_component_styles(self):
        """
        更新组件样式
        """
        # 更新主框架
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame) or isinstance(widget, ttk.LabelFrame):
                self._update_widget_style(widget)
    
    def _update_widget_style(self, widget):
        """
        递归更新组件样式
        """
        # 设置背景色
        if hasattr(widget, "configure"):
            try:
                widget.configure(bg=self.colors["bg"])
            except:
                pass
        
        # 处理子组件
        for child in widget.winfo_children():
            if isinstance(child, ttk.Label):
                child.configure(foreground=self.colors["fg"])
            elif isinstance(child, scrolledtext.ScrolledText):
                # 设置聊天文本框样式
                child.configure(
                    bg=self.colors["chat_bg"],
                    fg=self.colors["fg"],
                    insertbackground=self.colors["accent"]
                )
            elif isinstance(child, ttk.Button):
                # 创建谷歌Gemini风格的按钮样式
                style = ttk.Style()
                style.configure(
                    "Tech.TButton",
                    background=self.colors["button_bg"],
                    foreground=self.colors["button_fg"],
                    borderwidth=0,
                    relief="flat",
                    padding=(10, 5)
                )
                style.map(
                    "Tech.TButton",
                    background=[("active", "#3367d6")]  # 暗一点的蓝色
                )
                child.configure(style="Tech.TButton")
            elif isinstance(child, ttk.Frame) or isinstance(child, ttk.LabelFrame):
                self._update_widget_style(child)
    
    def run(self):
        """
        运行GUI
        """
        # 配置标签样式
        self.chat_text.tag_configure("system", foreground="#333333", font=("Arial", 11))
        self.chat_text.tag_configure("user", foreground="#4285f4", font=("Arial", 11, "bold"))
        
        # 启动主循环
        self.root.mainloop()

if __name__ == "__main__":
    gui = DesktopGUI()
    gui.run()