import flet as ft
import os
import time
import threading
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 引入你的核心逻辑
from manager import ProjectManager
from worker import WorkerAgent
from auditor import AuditorAgent
# 假设你已经有了 sandbox.py，如果没有，请确保创建了 _sandbox 目录
if not os.path.exists("_sandbox"):
    os.makedirs("_sandbox")

class SandboxEventHandler(FileSystemEventHandler):
    """文件系统监听器：当沙箱文件变化时通知 UI"""
    def __init__(self, app_instance):
        self.app = app_instance

    def on_any_event(self, event):
        if event.is_directory: return
        # 通知 UI 刷新文件树 (防抖动处理)
        self.app.trigger_refresh()

class AIStudioDesktop:
    def __init__(self):
        self.manager = ProjectManager()
        self.worker = WorkerAgent()
        self.auditor = AuditorAgent()
        self.sandbox_dir = os.path.abspath("_sandbox")
        self.selected_file = None

    def main(self, page: ft.Page):
        self.page = page
        page.title = "AI Agent Studio - Developer Console"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 10
        page.window_width = 1200
        page.window_height = 800

        # ==========================================
        # 左侧：指挥中心 (Chat & Tasks)
        # ==========================================
        self.chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.input_box = ft.TextField(
            hint_text="输入需求 (例如: 在沙箱里写一个贪吃蛇游戏)...",
            expand=True,
            border_radius=10,
            on_submit=self.send_message
        )

        left_panel = ft.Container(
            content=ft.Column([
                ft.Text("🎮 指挥中心", size=20, weight="bold"),
                ft.Divider(),
                ft.Container(content=self.chat_list, expand=True, bgcolor=ft.colors.BLACK12, border_radius=10, padding=10),
                ft.Row([
                    self.input_box,
                    ft.IconButton(icon=ft.icons.SEND, icon_color="blue", on_click=self.send_message)
                ])
            ]),
            expand=4, # 占 40% 宽度
            padding=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=10
        )

        # ==========================================
        # 右侧：沙箱实验室 (File Tree & Code & Run)
        # ==========================================
        self.file_tree = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.code_editor = ft.Markdown(
            "Select a file to preview...",
            selectable=True,
            extension_set="gitHubWeb",
            code_theme="atom-one-dark",
            expand=True
        )
        self.console_output = ft.Text("Ready...", font_family="Consolas", size=12, color="green")

        # 运行按钮
        self.run_btn = ft.ElevatedButton(
            "运行此文件",
            icon=ft.icons.PLAY_ARROW,
            bgcolor="green",
            color="white",
            disabled=True,
            on_click=self.run_selected_file
        )

        right_panel = ft.Container(
            content=ft.Row([
                # 文件树区域
                ft.Container(
                    content=ft.Column([
                        ft.Text("📂 沙箱文件", weight="bold"),
                        ft.Divider(),
                        self.file_tree
                    ]),
                    width=200,
                    bgcolor=ft.colors.BLACK26,
                    padding=10,
                    border_radius=10
                ),
                # 代码预览与终端区域
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("📝 代码预览", weight="bold"), self.run_btn], alignment="spaceBetween"),
                        ft.Container(content=self.code_editor, expand=True, bgcolor=ft.colors.BLACK87, border_radius=5, padding=10),
                        ft.Text("📺 终端输出", weight="bold"),
                        ft.Container(
                            content=ft.Column([self.console_output], scroll=ft.ScrollMode.AUTO),
                            height=150,
                            bgcolor="black",
                            padding=10,
                            border_radius=5
                        )
                    ]),
                    expand=True,
                    padding=10
                )
            ], expand=True),
            expand=6, # 占 60% 宽度
            padding=10,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10
        )

        # 布局组合
        page.add(ft.Row([left_panel, right_panel], expand=True))

        # 初始化
        self.add_bot_message("👋 全系统就绪。沙箱监控已启动。")
        self.refresh_file_tree()

        # 启动文件监控 (Watchdog)
        self.observer = Observer()
        self.observer.schedule(SandboxEventHandler(self), self.sandbox_dir, recursive=False)
        self.observer.start()

    # --- 逻辑功能区 ---

    def trigger_refresh(self):
        """线程安全的刷新触发器"""
        # Flet 的 UI 更新必须在主线程，这里用简单的重新加载策略
        # 实际生产中应使用 page.run_task 或 signal
        self.refresh_file_tree()
        self.page.update()

    def refresh_file_tree(self):
        """读取 _sandbox 目录并更新文件列表"""
        self.file_tree.controls.clear()
        try:
            files = [f for f in os.listdir(self.sandbox_dir) if os.path.isfile(os.path.join(self.sandbox_dir, f))]
            if not files:
                self.file_tree.controls.append(ft.Text("Empty sandbox", color="grey"))

            for f in files:
                # 为每个文件创建一个可点击的 Tile
                tile = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.PYTHON if f.endswith(".py") else ft.icons.INSERT_DRIVE_FILE, size=16),
                        ft.Text(f, size=14, overflow=ft.TextOverflow.ELLIPSIS)
                    ]),
                    padding=5,
                    ink=True,
                    on_click=lambda e, filename=f: self.load_file_content(filename)
                )
                self.file_tree.controls.append(tile)
        except Exception as e:
            print(f"Error reading sandbox: {e}")
        self.page.update()

    def load_file_content(self, filename):
        """加载文件内容到编辑器"""
        self.selected_file = filename
        path = os.path.join(self.sandbox_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            self.code_editor.value = f"```python\n{code}\n```"
            self.run_btn.disabled = not filename.endswith(".py")
            self.page.update()
        except Exception as e:
            self.code_editor.value = f"Error reading file: {e}"
            self.page.update()

    def run_selected_file(self, e):
        """在独立进程中运行沙箱代码"""
        if not self.selected_file: return

        path = os.path.join(self.sandbox_dir, self.selected_file)
        self.console_output.value = f"🚀 Running {self.selected_file}...\n"
        self.page.update()

        def run_thread():
            try:
                # 关键：cwd 设置为沙箱目录，保证相对路径正确
                proc = subprocess.run(
                    [sys.executable, path],
                    capture_output=True,
                    text=True,
                    cwd=self.sandbox_dir,
                    encoding='utf-8',
                    errors='replace'
                )
                output = proc.stdout + "\n" + proc.stderr
                self.console_output.value = output
            except Exception as ex:
                self.console_output.value = f"Execution Error: {ex}"
            self.page.update()

        threading.Thread(target=run_thread, daemon=True).start()

    def send_message(self, e):
        """发送消息给 Agent"""
        text = self.input_box.value
        if not text: return

        self.input_box.value = ""
        self.chat_list.controls.append(ft.Text(f"You: {text}", color="white"))
        self.page.update()

        # 异步调用 Agent，避免阻塞 UI
        threading.Thread(target=self.agent_task, args=(text,), daemon=True).start()

    def add_bot_message(self, text):
        self.chat_list.controls.append(ft.Markdown(text))
        self.page.update()

    def agent_task(self, prompt):
        """调用你的核心 Agent 逻辑"""
        try:
            self.add_bot_message("🤖 思考中...")
            # === 这里调用你的 manager/worker 逻辑 ===
            # 为了演示，我们直接让 Worker 写入一个文件到沙箱
            # 实际对接时，请调用 manager.plan_tasks(prompt) -> worker.run(...)

            # 模拟：Agent 决定在沙箱里写代码
            tasks = self.manager.plan_tasks(prompt)
            for task in tasks:
                self.add_bot_message(f"执行任务: {task['description']}")
                # 注意：你需要修改 worker.py 让它把文件写到 _sandbox 目录，或者在这里处理
                # 这里假设 worker.run 返回了代码，我们手动存入沙箱做演示
                res = self.worker.run(task['description'])

                # 如果生成了代码，尝试提取文件名并写入沙箱
                if res['code']:
                    # 简单的文件名猜测逻辑，实际应由 Agent 指定
                    filename = "generated_script.py"
                    if "filename" in task: filename = task['filename'] # 可以在 prompt 里要求 Agent 返回文件名

                    filepath = os.path.join(self.sandbox_dir, filename)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(res['code'])

                    self.add_bot_message(f"✅ 文件已写入沙箱: `{filename}`")

            self.add_bot_message("✨ 任务完成！请查看右侧沙箱面板。")
            # 文件监听器会自动刷新 UI

        except Exception as e:
            self.add_bot_message(f"❌ Error: {e}")

if __name__ == "__main__":
    app = AIStudioDesktop()
    ft.app(target=app.main)