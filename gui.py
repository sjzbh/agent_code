# gui.py
import flet as ft
import threading
import time
from manager import ProjectManager
from worker import WorkerAgent
from auditor import AuditorAgent
# 引入 rich 的 console 以便我们拦截它
import rich.console

class AIStudioApp:
    def __init__(self):
        self.chat_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            auto_scroll=True
        )
        self.running = False
        self.dark_theme = True  # 默认深色主题
        self.manager = ProjectManager()
        self.worker = WorkerAgent()
        self.auditor = AuditorAgent()

    def main(self, page: ft.Page):
        self.page = page
        page.title = "AI Agent Studio (Desktop Mode)"
        page.theme_mode = ft.ThemeMode.DARK if self.dark_theme else ft.ThemeMode.LIGHT  # 根据主题设置
        page.padding = 0

        # 设置窗口大小为屏幕的80%
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True

        # --- 拦截 Rich Console 输出 ---
        # 这是一个黑科技：把所有 agent 的 console.print 劫持到我们的界面上
        def hook_print(*args, **kwargs):
            msg = " ".join(map(str, args))
            # 将日志输出到界面上的一个小日志窗口，或者作为系统消息插入聊天
            self.add_log_message(msg)

        # 核心原理：替换所有模块中的 gui_adapter.print
        # 这样所有组件的日志都会显示在 GUI 界面上
        from worker import gui_adapter
        gui_adapter.print = hook_print

        # 同时替换 manager.py 和 auditor.py 中的日志适配器
        from manager import gui_adapter as manager_adapter
        manager_adapter.print = hook_print

        from auditor import gui_adapter as auditor_adapter
        auditor_adapter.print = hook_print

        # --- 界面布局 ---

        # 创建背景渐变效果
        bg_gradient = ft.Container(
            width=800,
            height=800,
            border_radius=400,  # 形成圆形
            gradient=ft.RadialGradient(
                colors=[
                    "#4285F4" if not self.dark_theme else "#AA00FF",  # 蓝色或紫色
                    "#ffffff00" if not self.dark_theme else "#ffffff00"  # 透明色
                ],
                radius=1.0,
            ),
            opacity=0.15,  # 低透明度
            left=-200,  # 定位到顶部中央
            top=-200,
            blur=ft.Blur(20, 20, ft.BlurTileMode.MIRROR)  # 模糊效果
        )

        # 1. 侧边栏 (Sidebar)
        sidebar = ft.Container(
            width=280,
            bgcolor="#f0f0f0" if not self.dark_theme else "#1F2023",  # Gemini风格侧边栏
            padding=15,
            border_radius=24,  # 增大圆角
            border=ft.border.BorderSide(1, "#ffffff1a"),  # 极细半透明边框
            content=ft.Column([
                ft.Text("任务历史", size=18, weight=ft.FontWeight.W_500, color="#2c2c2c" if not self.dark_theme else "#e0e0e0"),  # 现代化文字
                ft.Divider(height=20, thickness=1),
                ft.ListTile(
                    title=ft.Text("任务 #001", color="#555555" if not self.dark_theme else "#bbbbbb"),
                    dense=True,
                    hover_color="#f5f5f5" if not self.dark_theme else "#3a3a3a"
                ),
                ft.ListTile(
                    title=ft.Text("任务 #002", color="#555555" if not self.dark_theme else "#bbbbbb"),
                    dense=True,
                    hover_color="#f5f5f5" if not self.dark_theme else "#3a3a3a"
                ),
            ], spacing=5)
        )

        # 2. 聊天区域 (Chat Area)
        self.input_field = ft.TextField(
            hint_text="输入您的需求 (例如: 写一个贪吃蛇游戏)...",
            border_radius=24,  # 增大圆角
            filled=True,
            bgcolor="#ffffff" if not self.dark_theme else "#3a3a3a",
            color="#333333" if not self.dark_theme else "#ffffff",
            border_color="#e0e0e0" if not self.dark_theme else "#555555",
            focused_border_color="#4285f4" if not self.dark_theme else "#669df6",  # Google蓝色主题
            multiline=True,
            shift_enter=True,
            on_submit=self.send_message,
            height=80  # 设置高度为两行
        )

        send_btn = ft.FilledButton(
            content=ft.Icon(
                icon="send_rounded",
                color="#4285f4" if not self.dark_theme else "#669df6",  # Google蓝色主题
                size=24
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=30),  # 圆形按钮
                padding=ft.padding.all(10),
            ),
            on_click=self.send_message
        )

        # 主题切换按钮
        theme_switch_btn = ft.TextButton(
            "🌙 深色" if not self.dark_theme else "☀️ 浅色",
            on_click=self.toggle_theme,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5),
                side=ft.BorderSide(1, "#333333" if not self.dark_theme else "#f0f0f0")  # 更柔和的边框颜色
            )
        )

        # 初始欢迎内容
        welcome_content = ft.Column(
            [
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            "你好",
                            ft.TextStyle(
                                size=40,
                                weight=ft.FontWeight.W_700,
                                foreground=ft.Paint(
                                    gradient=ft.LinearGradient(
                                        begin=ft.Alignment(0, -1),  # top center
                                        end=ft.Alignment(0, 1),    # bottom center
                                        colors=["#4285F4", "#EA4335"] if not self.dark_theme else ["#AA00FF", "#4285F4"]  # 蓝色到红色或紫色渐变
                                    )
                                )
                            )
                        )
                    ]
                ),
                ft.Text("需要我为你做些什么?", size=24, weight=ft.FontWeight.W_500, color="#C4C7C5"),  # 灰色次级文本
                ft.Container(height=50),  # 空白间隔
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=self.input_field,
                                width=500  # 设置宽度为500像素
                            ),
                            send_btn
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=ft.padding.all(10)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # 居中对齐
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER  # 垂直居中
        )

        # 聊天容器 - 采用Gemini风格布局
        chat_container = ft.Container(
            expand=True,
            bgcolor="#f8f8f8" if not self.dark_theme else "#131314",  # Gemini风格背景色
            content=ft.Stack([
                bg_gradient,  # 背景渐变
                ft.Column([
                    ft.Row([ft.Container(expand=True), theme_switch_btn], alignment=ft.MainAxisAlignment.END),  # 在右上角添加主题切换按钮
                    ft.Container(
                        content=welcome_content,  # 初始欢迎内容
                        alignment=ft.alignment.Alignment(0, 0)  # 居中对齐
                    )
                ], spacing=0, expand=True)
            ])
        )

        # 组装整体布局 (Row: 侧边栏 | 聊天区)
        layout = ft.Row([sidebar, chat_container], spacing=0, expand=True)
        page.add(layout)

    def add_user_message(self, text):
        """添加用户消息气泡 - 现代化风格"""
        # 用户名显示
        username = ft.Text("您", size=14, weight=ft.FontWeight.W_500, color="#4285f4" if not self.dark_theme else "#669df6")  # Google蓝色主题

        # 消息气泡
        bubble = ft.Container(
            content=ft.Markdown(text, selectable=True),
            bgcolor="#e8f0fe" if not self.dark_theme else "#303f9f",  # Google蓝色系
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            border_radius=24,  # 增大圆角
            margin=ft.margin.only(left=50, top=5, right=10),
            border=ft.border.all(1, "#ffffff1a"),  # 极细半透明边框
            alignment=ft.alignment.Alignment(-1, 0)  # 左对齐: (-1, 0)
        )

        # 将用户名和消息气泡垂直排列
        message_column = ft.Column([username, bubble], spacing=5)
        self.chat_list.controls.append(message_column)
        self.page.update()

    def add_bot_message(self, text):
        """添加 AI 消息气泡 (支持 Markdown) - 现代化风格"""
        # AI用户名显示
        username = ft.Text("AI Agent", size=14, weight=ft.FontWeight.W_500, color="#34a853" if not self.dark_theme else "#81c995")  # Google绿色主题

        # 消息气泡
        bubble = ft.Container(
            content=ft.Markdown(
                text,
                selectable=True,
                extension_set="gitHubWeb",
                code_theme="atom-one-dark"
            ),
            bgcolor="#f8f9fa" if not self.dark_theme else "#424242",  # 现代化灰白色
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            border_radius=24,  # 增大圆角
            margin=ft.margin.only(right=50, top=5, left=10),
            border=ft.border.all(1, "#ffffff1a")  # 极细半透明边框
        )

        # 将用户名和消息气泡垂直排列
        message_column = ft.Column([username, bubble], spacing=5)

        self.chat_list.controls.append(message_column)
        self.page.update()

    def toggle_theme(self, e):
        """切换主题"""
        self.dark_theme = not self.dark_theme

        # 更新页面主题
        self.page.theme_mode = ft.ThemeMode.DARK if self.dark_theme else ft.ThemeMode.LIGHT

        # 重新构建界面
        self.page.clean()  # 清空当前页面
        self.main(self.page)  # 重新构建界面
        self.page.update()

    def add_log_message(self, text):
        """添加系统处理日志 (灰色小字)"""
        log = ft.Text(f"[系统] {text}", size=12, color="#9e9e9e", font_family="Consolas")  # 使用十六进制颜色值替代ft.colors
        self.chat_list.controls.append(ft.Container(content=log, padding=ft.padding.only(left=50)))
        self.page.update()

    def send_message(self, e):
        text = self.input_field.value
        if not text.strip() or self.running: return

        # 清空当前页面并切换到正常聊天界面
        self.page.clean()
        self.main_chat_interface(self.page, initial_message=text)
        return

    def main_chat_interface(self, page: ft.Page, initial_message=None):
        """聊天界面主函数"""
        self.page = page
        page.title = "AI Agent Studio (Desktop Mode)"
        page.theme_mode = ft.ThemeMode.DARK if self.dark_theme else ft.ThemeMode.LIGHT  # 根据主题设置
        page.padding = 0

        # --- 拦截 Rich Console 输出 ---
        # 这是一个黑科技：把所有 agent 的 console.print 劫持到我们的界面上
        def hook_print(*args, **kwargs):
            msg = " ".join(map(str, args))
            # 将日志输出到界面上的一个小日志窗口，或者作为系统消息插入聊天
            self.add_log_message(msg)

        # 核心原理：替换所有模块中的 gui_adapter.print
        # 这样所有组件的日志都会显示在 GUI 界面上
        from worker import gui_adapter
        gui_adapter.print = hook_print

        # 同时替换 manager.py 和 auditor.py 中的日志适配器
        from manager import gui_adapter as manager_adapter
        manager_adapter.print = hook_print

        from auditor import gui_adapter as auditor_adapter
        auditor_adapter.print = hook_print

        # 创建背景渐变效果
        bg_gradient_chat = ft.Container(
            width=800,
            height=800,
            border_radius=400,  # 形成圆形
            gradient=ft.RadialGradient(
                colors=[
                    "#4285F4" if not self.dark_theme else "#AA00FF",  # 蓝色或紫色
                    "#ffffff00" if not self.dark_theme else "#ffffff00"  # 透明色
                ],
                radius=1.0,
            ),
            opacity=0.15,  # 低透明度
            left=-200,  # 定位到顶部中央
            top=-200,
            blur=ft.Blur(20, 20, ft.BlurTileMode.MIRROR)  # 模糊效果
        )

        # --- 界面布局 ---
        # 1. 侧边栏 (Sidebar)
        sidebar = ft.Container(
            width=280,
            bgcolor="#f0f0f0" if not self.dark_theme else "#1F2023",  # Gemini风格侧边栏
            padding=15,
            border_radius=24,  # 增大圆角
            border=ft.border.BorderSide(1, "#ffffff1a"),  # 极细半透明边框
            content=ft.Column([
                ft.Text("任务历史", size=18, weight=ft.FontWeight.W_500, color="#2c2c2c" if not self.dark_theme else "#e0e0e0"),  # 现代化文字
                ft.Divider(height=20, thickness=1),
                ft.ListTile(
                    title=ft.Text("任务 #001", color="#555555" if not self.dark_theme else "#bbbbbb"),
                    dense=True,
                    hover_color="#f5f5f5" if not self.dark_theme else "#3a3a3a"
                ),
                ft.ListTile(
                    title=ft.Text("任务 #002", color="#555555" if not self.dark_theme else "#bbbbbb"),
                    dense=True,
                    hover_color="#f5f5f5" if not self.dark_theme else "#3a3a3a"
                ),
            ], spacing=5)
        )

        # 2. 聊天区域 (Chat Area)
        self.chat_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            auto_scroll=True
        )
        self.input_field = ft.TextField(
            hint_text="输入您的需求 (例如: 写一个贪吃蛇游戏)...",
            border_radius=20,
            filled=True,
            multiline=True,
            shift_enter=True,
            on_submit=self.send_message,
            height=80  # 设置高度为两行
        )

        send_btn = ft.FilledButton(
            content=ft.Icon(
                icon="send_rounded",
                color="#4285f4" if not self.dark_theme else "#669df6",  # Google蓝色主题
                size=24
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=30),  # 圆形按钮
                padding=ft.padding.all(10),
            ),
            on_click=self.send_message
        )

        # 主题切换按钮
        theme_switch_btn = ft.TextButton(
            "🌙 深色" if not self.dark_theme else "☀️ 浅色",
            on_click=self.toggle_theme,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=15, vertical=5),
                bgcolor="#f0f0f0" if not self.dark_theme else "#3a3a3a"
            )
        )

        # 聊天容器 - 采用Gemini风格布局
        chat_container = ft.Container(
            expand=True,
            bgcolor="#f8f9fa" if not self.dark_theme else "#131314",  # Gemini风格背景色
            content=ft.Stack([
                bg_gradient_chat,  # 背景渐变
                ft.Column([
                    ft.Row([ft.Container(expand=True), theme_switch_btn], alignment=ft.MainAxisAlignment.END),  # 在右上角添加主题切换按钮
                    ft.Container(
                        content=self.chat_list,  # 消息列表
                        expand=True,
                        padding=ft.padding.only(left=20, right=20, top=10, bottom=10)
                    ),
                    ft.Container(    # 底部输入栏 - 采用Gemini风格居中
                        content=ft.Row([self.input_field, send_btn], alignment=ft.MainAxisAlignment.CENTER),
                        padding=ft.padding.symmetric(horizontal=20, vertical=20),
                        bgcolor="#f0f0f0" if not self.dark_theme else "#1e1e1e"
                    )
                ], spacing=0, expand=True)
            ])
        )

        # 组装整体布局 (Row: 侧边栏 | 聊天区)
        layout = ft.Row([sidebar, chat_container], spacing=0, expand=True)
        page.add(layout)

        # 如果有初始消息，发送它
        if initial_message:
            self.input_field.value = initial_message
            # 直接处理消息，而不是再次调用send_message以避免无限循环
            self.running = True
            threading.Thread(target=self.run_ai_workflow, args=(initial_message,), daemon=True).start()

        # 更新页面
        page.update()

    def run_ai_workflow(self, user_input):
        """这里复用你 main.py 里的核心逻辑"""
        try:
            # 1. 规划
            self.add_log_message("Project Manager 正在规划任务...")
            tasks = self.manager.plan_tasks(user_input)

            if not tasks:
                self.add_bot_message("❌ 任务规划失败，请重试。")
                self.running = False
                return

            # 显示规划结果
            plan_str = "**任务规划列表**:\n" + "\n".join([f"- [ ] {t['description']} ({t['priority']})" for t in tasks])
            self.add_bot_message(plan_str)

            # 2. 执行循环
            for i, task in enumerate(tasks):
                self.add_log_message(f"正在执行任务 {i+1}/{len(tasks)}: {task['description']}")

                # Worker 执行
                result = self.worker.run(task["description"])

                # 在界面显示代码块
                if result.get("code"):
                    self.add_bot_message(f"**生成的代码 ({task['id']})**:\n```python\n{result['code']}\n```")

                if result["success"]:
                    self.add_log_message(f"执行成功: {result['output'][:100]}...") # 只显示前100字日志
                else:
                    self.add_bot_message(f"**执行出错**: {result['error']}")

                # Auditor 审计
                self.add_log_message("Auditor 正在审计...")
                audit = self.auditor.audit(task["description"], str(result))

                if audit["status"] == "PASS":
                    self.add_log_message("审计通过")
                else:
                    self.add_bot_message(f"**审计驳回**: {audit['feedback']}")
                    # 这里你可以加逻辑调用 manager.update_plan

            self.add_bot_message("**所有任务执行完毕！**")

        except Exception as e:
            self.add_bot_message(f"系统错误: {str(e)}")
        finally:
            self.running = False

if __name__ == "__main__":
    app = AIStudioApp()
    ft.app(target=app.main)