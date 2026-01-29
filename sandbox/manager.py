import os
import shutil
import subprocess
import tempfile
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from config import settings

console = Console()

class SandboxManager:
    """
    沙箱管理器
    负责创建和管理隔离的测试环境
    """
    def __init__(self):
        self.sandbox_dir = settings.SANDBOX_DIR
        self.timeout = settings.SANDBOX_TIMEOUT
        self._ensure_sandbox_dir()
    
    def _ensure_sandbox_dir(self):
        """
        确保沙箱目录存在
        """
        os.makedirs(self.sandbox_dir, exist_ok=True)
    
    def create_sandbox(self, sandbox_name: str = None) -> str:
        """
        创建新的沙箱环境
        
        Args:
            sandbox_name: 沙箱名称
            
        Returns:
            沙箱目录路径
        """
        if not sandbox_name:
            sandbox_name = f"sandbox_{int(time.time())}"
        
        sandbox_path = os.path.join(self.sandbox_dir, sandbox_name)
        
        # 清理已存在的同名沙箱
        if os.path.exists(sandbox_path):
            self.delete_sandbox(sandbox_name)
        
        # 创建沙箱目录结构
        os.makedirs(sandbox_path, exist_ok=True)
        os.makedirs(os.path.join(sandbox_path, "src"), exist_ok=True)
        os.makedirs(os.path.join(sandbox_path, "tests"), exist_ok=True)
        os.makedirs(os.path.join(sandbox_path, "logs"), exist_ok=True)
        
        console.print(f"✅ 沙箱创建成功: {sandbox_name}")
        return sandbox_path
    
    def delete_sandbox(self, sandbox_name: str):
        """
        删除沙箱环境
        
        Args:
            sandbox_name: 沙箱名称
        """
        sandbox_path = os.path.join(self.sandbox_dir, sandbox_name)
        
        if os.path.exists(sandbox_path):
            try:
                shutil.rmtree(sandbox_path)
                console.print(f"✅ 沙箱删除成功: {sandbox_name}")
            except Exception as e:
                console.print(f"❌ 沙箱删除失败: {e}")
        else:
            console.print(f"⚠️  沙箱不存在: {sandbox_name}")
    
    def reset_sandbox(self, sandbox_name: str):
        """
        重置沙箱环境
        
        Args:
            sandbox_name: 沙箱名称
            
        Returns:
            重置后的沙箱目录路径
        """
        self.delete_sandbox(sandbox_name)
        return self.create_sandbox(sandbox_name)
    
    def copy_to_sandbox(self, source_path: str, sandbox_name: str, target_path: str = "."):
        """
        复制文件或目录到沙箱
        
        Args:
            source_path: 源文件或目录路径
            sandbox_name: 沙箱名称
            target_path: 沙箱内的目标路径
        """
        sandbox_path = os.path.join(self.sandbox_dir, sandbox_name)
        dest_path = os.path.join(sandbox_path, target_path)
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        try:
            if os.path.isfile(source_path):
                shutil.copy2(source_path, dest_path)
                console.print(f"✅ 文件复制成功: {source_path} -> {dest_path}")
            elif os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                console.print(f"✅ 目录复制成功: {source_path} -> {dest_path}")
            else:
                console.print(f"❌ 源路径不存在: {source_path}")
        except Exception as e:
            console.print(f"❌ 复制失败: {e}")
    
    def copy_from_sandbox(self, sandbox_name: str, source_path: str, target_path: str):
        """
        从沙箱复制文件或目录到目标位置
        
        Args:
            sandbox_name: 沙箱名称
            source_path: 沙箱内的源路径
            target_path: 目标路径
        """
        sandbox_path = os.path.join(self.sandbox_dir, sandbox_name)
        src_path = os.path.join(sandbox_path, source_path)
        
        try:
            if os.path.isfile(src_path):
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.copy2(src_path, target_path)
                console.print(f"✅ 文件复制成功: {src_path} -> {target_path}")
            elif os.path.isdir(src_path):
                shutil.copytree(src_path, target_path, dirs_exist_ok=True)
                console.print(f"✅ 目录复制成功: {src_path} -> {target_path}")
            else:
                console.print(f"❌ 源路径不存在: {src_path}")
        except Exception as e:
            console.print(f"❌ 复制失败: {e}")
    
    def run_in_sandbox(self, sandbox_name: str, command: str, timeout: int = None) -> tuple:
        """
        在沙箱中执行命令
        
        Args:
            sandbox_name: 沙箱名称
            command: 要执行的命令
            timeout: 超时时间（秒）
            
        Returns:
            (success, stdout, stderr) 元组
        """
        sandbox_path = os.path.join(self.sandbox_dir, sandbox_name)
        
        if not os.path.exists(sandbox_path):
            console.print(f"❌ 沙箱不存在: {sandbox_name}")
            return False, "", "沙箱不存在"
        
        if timeout is None:
            timeout = self.timeout
        
        console.print(f"[bold blue]在沙箱中执行命令:[/bold blue] {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=sandbox_path,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            
            if success:
                console.print("✅ 命令执行成功")
                if stdout:
                    console.print(f"[green]输出:[/green]\n{stdout}")
            else:
                console.print("❌ 命令执行失败")
                if stderr:
                    console.print(f"[red]错误:[/red]\n{stderr}")
            
            return success, stdout, stderr
        except subprocess.TimeoutExpired as e:
            console.print(f"❌ 命令执行超时 ({timeout}秒)")
            # 处理超时情况下的输出
            stdout = ""
            stderr = f"命令执行超时 ({timeout}秒)"
            
            # 尝试获取已捕获的输出
            if e.stdout:
                try:
                    stdout = e.stdout.decode('utf-8') if isinstance(e.stdout, bytes) else e.stdout
                except:
                    stdout = str(e.stdout)
            
            if e.stderr:
                try:
                    stderr = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else e.stderr
                except:
                    stderr = str(e.stderr)
            
            # 输出捕获到的内容
            if stdout:
                console.print(f"[green]已捕获的输出:[/green]\n{stdout}")
            
            return False, stdout, stderr
        except Exception as e:
            console.print(f"❌ 命令执行异常: {e}")
            return False, "", str(e)
    
    def install_dependencies(self, sandbox_name: str, requirements_file: str = "requirements.txt"):
        """
        在沙箱中安装依赖

        Args:
            sandbox_name: 沙箱名称
            requirements_file: 依赖文件路径
        """
        sandbox_path = os.path.join(self.sandbox_dir, sandbox_name)
        req_path = os.path.join(sandbox_path, requirements_file)

        if not os.path.exists(req_path):
            console.print(f"⚠️  依赖文件不存在: {req_path}")
            return False

        console.print("[bold yellow]正在安装依赖...[/bold yellow]")

        # 首先创建虚拟环境
        venv_path = os.path.join(sandbox_path, "venv")
        success, stdout, stderr = self.run_in_sandbox(
            sandbox_name,
            f"python -m venv {venv_path}",
            timeout=120  # 创建虚拟环境的时间
        )

        if not success:
            console.print(f"[red]创建虚拟环境失败: {stderr}[/red]")
            return False

        # 激活虚拟环境并安装依赖
        if os.name == 'nt':  # Windows
            pip_cmd = f"{venv_path}\\Scripts\\pip"
        else:  # Unix/Linux/MacOS
            pip_cmd = f"{venv_path}/bin/pip"

        success, stdout, stderr = self.run_in_sandbox(
            sandbox_name,
            f"{pip_cmd} install -r {requirements_file}",
            timeout=300  # 依赖安装可能需要更长时间
        )

        return success
    
    def list_sandboxes(self):
        """
        列出所有沙箱
        
        Returns:
            沙箱名称列表
        """
        sandboxes = []
        if os.path.exists(self.sandbox_dir):
            for item in os.listdir(self.sandbox_dir):
                item_path = os.path.join(self.sandbox_dir, item)
                if os.path.isdir(item_path):
                    sandboxes.append(item)
        
        console.print("[bold cyan]当前沙箱列表:[/bold cyan]")
        for sandbox in sandboxes:
            console.print(f"- {sandbox}")
        
        return sandboxes
    
    def cleanup(self, older_than_hours: int = 24):
        """
        清理旧的沙箱环境
        
        Args:
            older_than_hours: 清理超过指定小时数的沙箱
        """
        cutoff_time = time.time() - (older_than_hours * 3600)
        
        console.print(f"[bold yellow]正在清理超过 {older_than_hours} 小时的沙箱...[/bold yellow]")
        
        for item in os.listdir(self.sandbox_dir):
            item_path = os.path.join(self.sandbox_dir, item)
            if os.path.isdir(item_path):
                mtime = os.path.getmtime(item_path)
                if mtime < cutoff_time:
                    console.print(f"清理旧沙箱: {item}")
                    self.delete_sandbox(item)
        
        console.print("✅ 清理完成")
