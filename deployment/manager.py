import os
import shutil
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from config import settings
from state import shared_state

console = Console()

class DeploymentManager:
    """
    部署管理器
    负责将测试通过的项目部署到目标环境
    """
    def __init__(self):
        self.deployment_dir = settings.DEPLOYMENT_DIR
        self._ensure_deployment_dir()
    
    def _ensure_deployment_dir(self):
        """
        确保部署目录存在
        """
        os.makedirs(self.deployment_dir, exist_ok=True)
    
    def deploy_project(self, project_path: str, project_name: str, deployment_env: str = "production") -> dict:
        """
        部署项目
        
        Args:
            project_path: 项目路径
            project_name: 项目名称
            deployment_env: 部署环境，可选值: "development", "staging", "production"
            
        Returns:
            部署结果字典
        """
        # 更新共享状态
        shared_state.set("current_task", "部署项目")
        shared_state.add_log(f"开始部署项目：{project_name} 到 {deployment_env} 环境")
        
        console.print(Panel(
            f"项目路径：{project_path}\n项目名称：{project_name}\n部署环境：{deployment_env}",
            title="[bold green]开始部署项目[/bold green]",
            border_style="green"
        ))
        
        # 创建部署目录
        deployment_path = os.path.join(self.deployment_dir, deployment_env, project_name)
        os.makedirs(deployment_path, exist_ok=True)
        shared_state.add_log(f"创建部署目录：{deployment_path}")
        
        # 创建备份
        backup_path = self._create_backup(deployment_path, project_name, deployment_env)
        shared_state.add_log(f"创建部署备份：{backup_path}")
        
        try:
            # 复制项目文件
            self._copy_project_files(project_path, deployment_path)
            shared_state.add_log(f"复制项目文件：{project_path} -> {deployment_path}")
            
            # 安装依赖
            self._install_dependencies(deployment_path, project_name)
            shared_state.add_log("安装项目依赖")
            
            # 部署后验证
            validation_result = self._validate_deployment(deployment_path, project_name)
            shared_state.add_log(f"部署后验证结果：{validation_result}")
            
            # 生成部署报告
            report = self._generate_deployment_report(
                project_name,
                deployment_env,
                deployment_path,
                validation_result,
                backup_path
            )
            shared_state.add_log(f"生成部署报告，最终状态：{report['status']}")
            
            # 更新共享状态
            shared_state.set("deployment_result", report)
            
            return report
        except Exception as e:
            console.print(f"[bold red]部署失败: {e}[/bold red]")
            shared_state.add_log(f"部署失败：{str(e)}")
            
            # 尝试回滚
            if backup_path and os.path.exists(backup_path):
                self._rollback_deployment(backup_path, deployment_path)
                shared_state.add_log(f"尝试回滚部署：{backup_path} -> {deployment_path}")
            
            error_report = {
                "status": "FAIL",
                "project_name": project_name,
                "deployment_env": deployment_env,
                "error": str(e)
            }
            
            # 更新共享状态
            shared_state.set("last_error", f"部署失败：{str(e)}")
            shared_state.set("deployment_result", error_report)
            
            return error_report
    
    def _create_backup(self, deployment_path: str, project_name: str, deployment_env: str) -> str:
        """
        创建部署备份
        
        Args:
            deployment_path: 部署路径
            project_name: 项目名称
            deployment_env: 部署环境
            
        Returns:
            备份路径
        """
        if os.path.exists(deployment_path) and os.listdir(deployment_path):
            backup_path = os.path.join(
                self.deployment_dir, 
                "backups", 
                deployment_env, 
                f"{project_name}_{int(time.time())}"
            )
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            console.print(f"[bold yellow]创建部署备份: {backup_path}[/bold yellow]")
            shutil.copytree(deployment_path, backup_path)
            
            return backup_path
        return None
    
    def _copy_project_files(self, project_path: str, deployment_path: str):
        """
        复制项目文件到部署目录
        
        Args:
            project_path: 项目路径
            deployment_path: 部署路径
        """
        console.print("[bold blue]复制项目文件...[/bold blue]")
        
        # 清理部署目录
        for item in os.listdir(deployment_path):
            item_path = os.path.join(deployment_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        
        # 复制项目文件
        for item in os.listdir(project_path):
            item_path = os.path.join(project_path, item)
            dest_path = os.path.join(deployment_path, item)
            
            if os.path.isfile(item_path):
                shutil.copy2(item_path, dest_path)
            elif os.path.isdir(item_path):
                shutil.copytree(item_path, dest_path)
        
        console.print("✅ 项目文件复制完成")
    
    def _install_dependencies(self, deployment_path: str, project_name: str):
        """
        安装项目依赖

        Args:
            deployment_path: 部署路径
            project_name: 项目名称
        """
        console.print("[bold yellow]安装项目依赖...[/bold yellow]")

        # 首先创建虚拟环境
        venv_path = os.path.join(deployment_path, "venv")
        import subprocess

        # 创建虚拟环境
        result = subprocess.run(
            f"python -m venv {venv_path}",
            shell=True,
            cwd=deployment_path,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            console.print(f"[red]创建虚拟环境失败: {result.stderr}[/red]")
            raise Exception(f"创建虚拟环境失败: {result.stderr}")

        # 激活虚拟环境并安装依赖
        if os.name == 'nt':  # Windows
            pip_cmd = f"{venv_path}\\Scripts\\pip"
        else:  # Unix/Linux/MacOS
            pip_cmd = f"{venv_path}/bin/pip"

        # 检查是否存在requirements.txt
        requirements_file = os.path.join(deployment_path, "requirements.txt")
        if os.path.exists(requirements_file):
            console.print("[blue]使用requirements.txt安装依赖...[/blue]")
            result = subprocess.run(
                f"{pip_cmd} install -r requirements.txt",
                shell=True,
                cwd=deployment_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                console.print("✅ 依赖安装成功")
            else:
                console.print(f"[red]依赖安装失败: {result.stderr}[/red]")
                raise Exception(f"依赖安装失败: {result.stderr}")
        else:
            console.print("[yellow]未找到requirements.txt，尝试使用pip install -e .安装...[/yellow]")
            result = subprocess.run(
                f"{pip_cmd} install -e .",
                shell=True,
                cwd=deployment_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                console.print(f"[yellow]pip install -e .失败，跳过依赖安装: {result.stderr}[/yellow]")
    
    def _validate_deployment(self, deployment_path: str, project_name: str) -> dict:
        """
        验证部署结果
        
        Args:
            deployment_path: 部署路径
            project_name: 项目名称
            
        Returns:
            验证结果字典
        """
        console.print("[bold yellow]验证部署结果...[/bold yellow]")
        
        validation_result = {
            "status": "UNKNOWN",
            "checks": [],
            "errors": []
        }
        
        # 检查项目文件是否存在
        required_files = ["main.py", "README.md"]
        for file_name in required_files:
            file_path = os.path.join(deployment_path, file_name)
            if os.path.exists(file_path):
                validation_result["checks"].append(f"✅ {file_name} 存在")
            else:
                validation_result["checks"].append(f"❌ {file_name} 不存在")
                validation_result["errors"].append(f"缺少必要文件: {file_name}")
        
        # 尝试运行项目
        console.print("[blue]尝试运行项目...[/blue]")
        import subprocess
        
        # 尝试运行 --help 命令
        result = subprocess.run(
            "python main.py --help",
            shell=True,
            cwd=deployment_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            # 尝试直接运行
            result = subprocess.run(
                "python main.py",
                shell=True,
                cwd=deployment_path,
                capture_output=True,
                text=True,
                timeout=30
            )
        
        if result.returncode == 0:
            validation_result["checks"].append("✅ 项目可以正常运行")
            validation_result["status"] = "PASS"
        else:
            validation_result["checks"].append("❌ 项目运行失败")
            validation_result["errors"].append(f"项目运行失败: {result.stderr}")
            validation_result["status"] = "FAIL"
        
        return validation_result
    
    def _rollback_deployment(self, backup_path: str, deployment_path: str):
        """
        回滚部署
        
        Args:
            backup_path: 备份路径
            deployment_path: 部署路径
        """
        console.print("[bold red]正在回滚部署...[/bold red]")
        
        try:
            # 清理部署目录
            for item in os.listdir(deployment_path):
                item_path = os.path.join(deployment_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            
            # 从备份恢复
            for item in os.listdir(backup_path):
                item_path = os.path.join(backup_path, item)
                dest_path = os.path.join(deployment_path, item)
                
                if os.path.isfile(item_path):
                    shutil.copy2(item_path, dest_path)
                elif os.path.isdir(item_path):
                    shutil.copytree(item_path, dest_path)
            
            console.print("✅ 部署回滚成功")
        except Exception as e:
            console.print(f"[bold red]回滚失败: {e}[/bold red]")
    
    def _generate_deployment_report(self, project_name: str, deployment_env: str, 
                                  deployment_path: str, validation_result: dict, 
                                  backup_path: str) -> dict:
        """
        生成部署报告
        
        Args:
            project_name: 项目名称
            deployment_env: 部署环境
            deployment_path: 部署路径
            validation_result: 验证结果
            backup_path: 备份路径
            
        Returns:
            部署报告字典
        """
        # 确定部署状态
        if validation_result["status"] == "PASS":
            deployment_status = "SUCCESS"
        else:
            deployment_status = "FAILED"
        
        report = {
            "status": deployment_status,
            "project_name": project_name,
            "deployment_env": deployment_env,
            "deployment_path": deployment_path,
            "backup_path": backup_path,
            "validation_result": validation_result,
            "timestamp": time.time(),
            "message": f"项目 {project_name} 在 {deployment_env} 环境的部署{('成功' if deployment_status == 'SUCCESS' else '失败')}"
        }
        
        console.print(Panel(
            f"部署状态：{deployment_status}\n部署路径：{deployment_path}\n验证结果：{validation_result['status']}",
            title="[bold green]部署完成[/bold green]",
            border_style="green"
        ))
        
        return report
    
    def list_deployments(self, deployment_env: str = None):
        """
        列出部署的项目
        
        Args:
            deployment_env: 部署环境
            
        Returns:
            部署项目列表
        """
        deployments = []
        
        if deployment_env:
            env_path = os.path.join(self.deployment_dir, deployment_env)
            if os.path.exists(env_path):
                for item in os.listdir(env_path):
                    item_path = os.path.join(env_path, item)
                    if os.path.isdir(item_path):
                        deployments.append({
                            "name": item,
                            "environment": deployment_env,
                            "path": item_path
                        })
        else:
            # 列出所有环境的部署
            for env in os.listdir(self.deployment_dir):
                env_path = os.path.join(self.deployment_dir, env)
                if os.path.isdir(env_path) and env != "backups":
                    for item in os.listdir(env_path):
                        item_path = os.path.join(env_path, item)
                        if os.path.isdir(item_path):
                            deployments.append({
                                "name": item,
                                "environment": env,
                                "path": item_path
                            })
        
        console.print("[bold cyan]当前部署列表:[/bold cyan]")
        for deployment in deployments:
            console.print(f"- {deployment['name']} (环境: {deployment['environment']})")
        
        return deployments
    
    def undeploy_project(self, project_name: str, deployment_env: str = "production"):
        """
        卸载项目
        
        Args:
            project_name: 项目名称
            deployment_env: 部署环境
        """
        deployment_path = os.path.join(self.deployment_dir, deployment_env, project_name)
        
        if os.path.exists(deployment_path):
            console.print(f"[bold yellow]正在卸载项目: {project_name}[/bold yellow]")
            shutil.rmtree(deployment_path)
            console.print(f"[bold green]项目 {project_name} 已成功卸载[/bold green]")
        else:
            console.print(f"[bold red]项目 {project_name} 在 {deployment_env} 环境中未部署[/bold red]")
