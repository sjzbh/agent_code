import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from config import settings, ai_client_manager
from project import ProjectGenerator
from testing import TestEvaluator
from deployment import DeploymentManager
from auditor import AuditorAgent
from state import shared_state

console = Console()

class ProjectController:
    """
    项目控制器
    负责协调各个模块的工作，实现完整的项目创建、测试和部署流程
    """
    def __init__(self):
        self.project_generator = ProjectGenerator()
        self.test_evaluator = TestEvaluator()
        self.deployment_manager = DeploymentManager()
        self.auditor = AuditorAgent()
        self._ensure_directories()
        # 清空共享状态
        shared_state.clear()
    
    def _ensure_directories(self):
        """
        确保必要的目录存在
        """
        directories = [
            "./generated_projects",
            settings.SANDBOX_DIR,
            settings.DEPLOYMENT_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def run(self):
        """
        运行主控制器
        """
        console.print(Panel(
            "欢迎使用AI项目创建与部署工具！\n\n" +
            "这个工具可以：\n" +
            "- 根据您的需求生成完整的项目结构\n" +
            "- 在隔离的沙箱环境中测试项目\n" +
            "- 将测试通过的项目部署到目标环境\n\n" +
            "请输入您的项目需求，或输入 'exit' 退出工具。",
            title="[bold cyan]AI项目创建与部署工具[/bold cyan]",
            border_style="cyan"
        ))
        
        while True:
            try:
                # 接收用户输入
                user_input = Prompt.ask("[bold green]请输入您的项目需求[/bold green]", default="exit")
                
                if user_input.lower() == "exit":
                    console.print("[bold cyan]工具已退出，感谢使用！[/bold cyan]")
                    break
                
                if not user_input.strip():
                    continue
                
                # 执行完整的工作流程
                self._execute_workflow(user_input)
                
            except KeyboardInterrupt:
                console.print("\n[bold yellow]操作被用户中断。[/bold yellow]")
                break
            except Exception as e:
                console.print(f"[bold red]发生未知错误：{str(e)}[/bold red]")
                continue
    
    def _execute_workflow(self, user_requirement: str):
        """
        执行完整的工作流程
        
        Args:
            user_requirement: 用户需求
        """
        # 更新共享状态中的用户需求
        shared_state.set("user_requirements", user_requirement)
        shared_state.set("current_task", "执行完整工作流程")
        
        console.print(Panel(
            user_requirement,
            title="[bold green]用户需求[/bold green]",
            border_style="green"
        ))
        
        # 1. 生成项目
        shared_state.set("current_task", "生成项目")
        project_info = self._generate_project(user_requirement)
        
        if not project_info:
            console.print("[bold red]项目生成失败，流程终止[/bold red]")
            shared_state.set("last_error", "项目生成失败")
            return
        
        # 更新共享状态中的项目信息
        shared_state.set("project_info", project_info)
        
        project_path = project_info["project_dir"]
        project_name = project_info["project_name"]
        
        # 2. 测试项目
        shared_state.set("current_task", "测试项目")
        evaluation_result = self._test_project(project_path, project_name)
        
        # 更新共享状态中的测试结果
        shared_state.set("test_result", evaluation_result)
        
        if evaluation_result["status"] != "PASS":
            console.print("[bold red]项目测试失败，流程终止[/bold red]")
            console.print(f"[red]失败原因：{evaluation_result['feedback']}[/red]")
            shared_state.set("last_error", f"项目测试失败：{evaluation_result['feedback']}")
            return
        
        # 3. 部署项目
        shared_state.set("current_task", "部署项目")
        deployment_result = self._deploy_project(project_path, project_name)
        
        # 更新共享状态中的部署结果
        if deployment_result:
            shared_state.set("deployment_result", deployment_result)
        
        # 4. 审计项目
        shared_state.set("current_task", "审计项目")
        audit_result = self.auditor.audit()

        # 更新共享状态中的审计结果
        shared_state.set("last_audit_result", audit_result)

        # 检查审计结果
        if audit_result["status"] == "FAIL":
            console.print("[bold red]审计失败，需要重新执行任务[/bold red]")

            # 检查是否需要返回Worker
            if audit_result.get("return_to_worker", False):
                console.print("[bold yellow]返回Worker重新执行任务...[/bold yellow]")
                # 重新执行工作流程
                console.print("[bold green]重新执行工作流程...[/bold green]")
                self._execute_workflow(user_requirement)
            else:
                console.print("[bold red]审计失败，流程终止[/bold red]")
                console.print(f"[red]失败原因：{audit_result['feedback']}[/red]")
                return
        elif audit_result["status"] == "PASS" and "由于连续" in audit_result.get("feedback", "") and "次审计失败" in audit_result.get("feedback", ""):
            # 特殊情况：由于连续审计失败而自动通过
            console.print(f"[bold yellow]审计因连续失败达到上限而自动通过：{audit_result['feedback']}[/bold yellow]")
            console.print("[bold green]项目流程完成（因连续审计失败而自动通过）[/bold green]")
        else:
            console.print("[bold green]审计成功，项目流程完成[/bold green]")
    
    def _generate_project(self, user_requirement: str) -> dict:
        """
        生成项目
        
        Args:
            user_requirement: 用户需求
            
        Returns:
            项目信息字典
        """
        console.print("[bold yellow]步骤 1: 生成项目结构[/bold yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("生成项目...", total=None)
            project_info = self.project_generator.generate_project(user_requirement)
            progress.stop()
        
        return project_info
    
    def _test_project(self, project_path: str, project_name: str) -> dict:
        """
        测试项目
        
        Args:
            project_path: 项目路径
            project_name: 项目名称
            
        Returns:
            测试评估结果
        """
        console.print("[bold yellow]步骤 2: 测试项目[/bold yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("测试项目...", total=None)
            evaluation_result = self.test_evaluator.evaluate_project(project_path, project_name)
            progress.stop()
        
        return evaluation_result
    
    def _deploy_project(self, project_path: str, project_name: str) -> dict:
        """
        部署项目
        
        Args:
            project_path: 项目路径
            project_name: 项目名称
            
        Returns:
            部署结果
        """
        console.print("[bold yellow]步骤 3: 部署项目[/bold yellow]")
        
        # 询问部署环境
        deployment_env = Prompt.ask(
            "[bold green]请选择部署环境[/bold green]",
            choices=["development", "staging", "production"],
            default="development"
        )
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("部署项目...", total=None)
            deployment_result = self.deployment_manager.deploy_project(
                project_path,
                project_name,
                deployment_env
            )
            progress.stop()
        
        if deployment_result["status"] == "SUCCESS":
            console.print(Panel(
                f"项目 {project_name} 已成功部署到 {deployment_env} 环境！\n\n" +
                f"部署路径：{deployment_result['deployment_path']}\n" +
                f"您可以在该目录中运行项目。",
                title="[bold green]部署成功[/bold green]",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"项目 {project_name} 部署失败！\n\n" +
                f"错误信息：{deployment_result.get('error', '未知错误')}",
                title="[bold red]部署失败[/bold red]",
                border_style="red"
            ))
        
        return deployment_result
    
    def list_projects(self):
        """
        列出已生成的项目
        """
        console.print("[bold yellow]已生成的项目：[/bold yellow]")
        
        projects_dir = "./generated_projects"
        if os.path.exists(projects_dir):
            projects = os.listdir(projects_dir)
            for project in projects:
                project_path = os.path.join(projects_dir, project)
                if os.path.isdir(project_path):
                    console.print(f"- {project}")
        else:
            console.print("[yellow]暂无生成的项目[/yellow]")
    
    def list_deployments(self):
        """
        列出已部署的项目
        """
        console.print("[bold yellow]已部署的项目：[/bold yellow]")
        self.deployment_manager.list_deployments()
