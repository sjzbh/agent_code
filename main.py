#!/usr/bin/env python3
"""
AI项目创建与部署工具入口
"""
import os
import sys

# 确保在Windows下使用UTF-8
if os.name == 'nt':
    os.system('chcp 65001 > nul 2>&1')

from controller import ProjectController

if __name__ == "__main__":
    try:
        # 创建控制器实例
        controller = ProjectController()
        
        # 检查是否有命令行参数
        if len(sys.argv) > 1:
            # 使用命令行参数作为用户需求
            user_requirement = ' '.join(sys.argv[1:])
            controller._execute_workflow(user_requirement)
        else:
            # 运行交互式控制器
            controller.run()
    except KeyboardInterrupt:
        print("\n操作被用户中断。")
    except Exception as e:
        print(f"发生错误：{e}")
        import traceback
        traceback.print_exc()
