"""
Virtual Software Company - Entry Point
架构版本: V2.0 (SOP-Graph Architecture)
"""
import sys
import os
from rich.console import Console

# 初始化控制台
console = Console()

def main():
    try:
        # 动态添加路径，确保能引用到子模块
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        console.print("[bold green]🚀 正在启动虚拟软件公司 (V2.0)...[/bold green]")
        console.print("[dim]加载模块: controller, roles, sop_engine, memory[/dim]")

        # 导入新架构的核心控制器
        # 注意：这里假设您的 controller/main.py 里有一个 run() 或类似的启动函数
        from controller.main import start_company_cycle

        # 启动主循环
        start_company_cycle()

    except ImportError as e:
        console.print(f"[bold red]启动失败：环境依赖缺失或路径错误[/bold red]")
        console.print(f"详情: {e}")
        console.print("[yellow]提示：请确保已安装 requirements.txt 并在项目根目录下运行[/yellow]")
    except Exception as e:
        console.print(f"[bold red]系统崩溃[/bold red]: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()