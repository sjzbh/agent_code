# gui_adapter.py
from rich.console import Console

class GuiLogger:
    """
    用于拦截 console.print 并转发给 GUI 的适配器
    """
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.console = Console() # 保留一个原始 console 用于调试

    def print(self, message, style=None, **kwargs):
        """替代 rich.console.print"""
        # 1. 在终端也打印一份（方便调试）
        self.console.print(message, style=style, **kwargs)
        
        # 2. 如果连接了 GUI，发送给 GUI
        if self.log_callback:
            # 简单处理：如果是 Panel 或复杂对象，转为字符串
            if not isinstance(message, str):
                message = str(message)
            self.log_callback(message)

# 全局单例，供所有 Agent 使用
gui_logger = GuiLogger()