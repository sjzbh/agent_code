from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, TextArea, Label, Static, Input
from textual.message import Message
from textual.events import Key
import json
import os
from datetime import datetime

class RequestDashboard(App):
    """
    一个基于终端的现代化聊天风格需求提交器
    """
    CSS = """
    Screen {
        layout: vertical;
        background: $surface;
    }
    
    # 聊天区域
    .chat-container {
        height: 80%;
        border: solid #333333;
        background: $surface;
        padding: 1;
        overflow: auto;
    }
    
    #chat_history {
        height: 100%;
        background: $surface;
    }
    
    #chat_input {
        height: 20%;
        border: solid #333333;
        border-top: none;
        background: $surface;
    }
    
    #input_area {
        height: 100%;
        background: $surface;
    }
    
    .input-container {
        height: 100%;
        layout: vertical;
    }
    
    .input-box {
        height: 80%;
        border: solid #555555;
        background: $primary-background;
    }
    
    .buttons {
        height: 20%;
        dock: bottom;
        padding: 1;
        background: $surface;
    }
    
    Button {
        margin: 1;
        width: 20;
    }
    
    Label {
        width: 100%;
        padding: 1;
        background: $surface;
    }
    
    #sidebar {
        width: 25%;
        dock: right;
        border-left: solid #333333;
        background: $surface;
    }
    
    .sidebar-section {
        padding: 1;
        border-bottom: solid #333333;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Horizontal():
            # 左侧聊天区域
            with Vertical():
                # 聊天历史
                with Vertical(classes="chat-container"):
                    yield Label("💬 聊天历史", classes="chat-header")
                    yield Static("[bold cyan]系统:[/bold cyan] 您好！我是多AI协作工具的项目经理。请输入您的需求，我会将其拆解为具体的任务。", id="chat_history")
                
                # 输入区域
                with Vertical(id="chat_input", classes="input-container"):
                    yield Label("请输入您的需求（按 Enter 发送，Ctrl+Enter 换行）", classes="input-label")
                    with Horizontal():
                        yield TextArea(id="input_area", show_line_numbers=False, classes="input-box")
                    with Horizontal(classes="buttons"):
                        yield Button("💾 保存", id="save", variant="primary")
                        yield Button("🚀 发送", id="send", variant="success")
            
            # 右侧侧边栏
            with Vertical(id="sidebar"):
                with Vertical(classes="sidebar-section"):
                    yield Label("📋 功能说明", classes="sidebar-header")
                    yield Static("- 按 Enter 发送需求\n- 按 Ctrl+Enter 换行\n- 点击保存按钮保存需求\n- 点击发送按钮提交给 Manager")
                with Vertical(classes="sidebar-section"):
                    yield Label("📂 历史记录", classes="sidebar-header")
                    yield Static("- 需求_20231027.json\n- 需求_修复Bug.json")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        editor = self.query_one("#input_area", TextArea)
        content = editor.text
        
        if event.button.id == "save":
            self.save_request(content)
        elif event.button.id == "send":
            self.send_request(content)

    def on_key(self, event: Key) -> None:
        """处理按键事件"""
        # 检查是否按下了Enter键
        if event.key == "enter":
            # 按Enter键发送
            editor = self.query_one("#input_area", TextArea)
            content = editor.text
            if content.strip():
                self.send_request(content)
                event.prevent_default()

    def save_request(self, content):
        """保存为文件"""
        if not content.strip():
            return
        
        filename = f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        # 更新聊天历史
        chat_history = self.query_one("#chat_history", Static)
        chat_history.update(
            chat_history.renderable + f"\n[bold green]我:[/bold green] {content}\n[bold cyan]系统:[/bold cyan] 需求已保存为: {filename}"
        )
        
        # 显示通知
        self.notify(f"需求已保存为: {filename}", title="保存成功")

    def send_request(self, content):
        """发送需求并退出"""
        if not content.strip():
            return
        
        # 保存需求
        self.save_request(content)
        
        # 更新聊天历史
        chat_history = self.query_one("#chat_history", Static)
        chat_history.update(
            chat_history.renderable + f"\n[bold cyan]系统:[/bold cyan] 需求已发送给 Manager，正在处理..."
        )
        
        # 退出并返回内容给主程序
        self.exit(result=content)

if __name__ == "__main__":
    app = RequestDashboard()
    result = app.run()
    
    # 这里演示了“可拆卸性”：
    # 如果作为模块被调用，它可以返回结果给 main.py
    if result:
        print(f"\n[系统] 接收到来自仪表盘的需求：\n{result}")
        # 这里可以衔接： manager.plan_tasks(result)