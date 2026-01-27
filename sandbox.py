import os
import shutil
import subprocess
import sys
import glob
from rich.console import Console

console = Console()

class SandboxManager:
    """
    沙箱管理器：负责创建隔离环境、文件同步和安全部署
    """
    
    def __init__(self, sandbox_dir="_sandbox"):
        self.root_dir = os.getcwd()
        self.sandbox_dir = os.path.join(self.root_dir, sandbox_dir)
        self.backup_dir = os.path.join(self.root_dir, "_backup")
        
    def init_sandbox(self):
        """初始化沙箱：清理旧数据，复制当前项目文件到沙箱"""
        try:
            # 1. 清理旧沙箱
            if os.path.exists(self.sandbox_dir):
                shutil.rmtree(self.sandbox_dir)
            os.makedirs(self.sandbox_dir)
            
            # 2. 复制核心代码和配置文件到沙箱
            # 定义需要复制的文件模式
            patterns = ['*.py', 'requirements.txt', '.env', 'README.md']
            for pattern in patterns:
                for file_path in glob.glob(pattern):
                    if os.path.isfile(file_path):
                        shutil.copy2(file_path, self.sandbox_dir)
            
            # 复制 config.py 等关键模块
            # 如果有 utils 等文件夹也需要递归复制，这里假设是扁平结构
            
            console.print(f"[bold green]沙箱环境初始化完成：{self.sandbox_dir}[/bold green]")
            return True
        except Exception as e:
            console.print(f"[bold red]沙箱初始化失败：{e}[/bold red]")
            return False

    def run_in_sandbox(self, command, timeout=60):
        """在沙箱环境中执行命令"""
        if not os.path.exists(self.sandbox_dir):
            return False, "沙箱不存在", "请先初始化沙箱"
            
        console.print(f"[yellow]在沙箱中执行：{command}[/yellow]")
        
        try:
            # 切换工作目录到沙箱
            result = subprocess.run(
                command,
                cwd=self.sandbox_dir, # 关键：指定工作目录为沙箱
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "执行超时"
        except Exception as e:
            return False, "", str(e)

    def deploy_file(self, filename):
        """将沙箱中的优秀代码部署到生产环境（此时才覆盖原文件）"""
        src = os.path.join(self.sandbox_dir, filename)
        dst = os.path.join(self.root_dir, filename)
        backup = os.path.join(self.backup_dir, filename + ".bak")
        
        if not os.path.exists(src):
            return False, f"源文件 {filename} 不在沙箱中"
            
        try:
            # 1. 备份原文件
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
            if os.path.exists(dst):
                shutil.copy2(dst, backup)
                
            # 2. 覆盖
            shutil.copy2(src, dst)
            console.print(f"[bold green]成功部署 {filename}！原文件已备份至 {backup}[/bold green]")
            return True, "部署成功"
        except Exception as e:
            return False, f"部署失败：{e}"