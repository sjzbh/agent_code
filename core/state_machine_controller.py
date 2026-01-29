"""
基于状态机的工业级Agent主控制器
"""
import os
import sys
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from config import settings, ai_client_manager
from project import ProjectGenerator
from testing import TestEvaluator
from deployment import DeploymentManager
from auditor import AuditorAgent
from core.state import AgentState
from core.router import router, should_enter_hitl_mode
from core.hitl import hitl_mode, save_state_before_exit
from core.enhanced_worker import EnhancedWorkerAgent

console = Console()


class StateMachineController:
    """
    基于状态机的工业级Agent控制器
    实现全局状态管理、智能路由和HITL机制
    """
    
    def __init__(self):
        self.project_generator = ProjectGenerator()
        self.test_evaluator = TestEvaluator()
        self.deployment_manager = DeploymentManager()
        self.auditor = AuditorAgent()
        self.worker = EnhancedWorkerAgent()
        self.state = AgentState()
        self._ensure_directories()
    
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
            "欢迎使用基于状态机的AI项目创建与部署工具！\n\n" +
            "这个工具可以：\n" +
            "- 根据您的需求生成完整的项目结构\n" +
            "- 在隔离的沙箱环境中测试项目\n" +
            "- 将测试通过的项目部署到目标环境\n" +
            "- 支持智能路由和人工介入机制\n\n" +
            "请输入您的项目需求，或输入 'exit' 退出工具。",
            title="[bold cyan]基于状态机的AI项目创建与部署工具[/bold cyan]",
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
                import traceback
                traceback.print_exc()
                continue

    def _execute_workflow(self, user_requirement: str):
        """
        执行完整的工作流程，基于状态机架构
        
        Args:
            user_requirement: 用户需求
        """
        # 初始化状态
        self.state = AgentState()
        self.state.current_phase = "planning"
        self.state.current_task_description = user_requirement
        
        console.print(Panel(
            user_requirement,
            title="[bold green]用户需求[/bold green]",
            border_style="green"
        ))

        # 1. 生成项目任务列表
        console.print("[bold yellow]步骤 1: 生成项目结构[/bold yellow]")
        self.state.current_phase = "planning"
        project_info = self._generate_project(user_requirement)

        if not project_info:
            console.print("[bold red]项目生成失败，流程终止[/bold red]")
            self.state.error_message = "项目生成失败"
            return

        # 更新状态中的项目信息
        self.state.add_execution_record({
            "phase": "planning",
            "project_info": project_info,
            "success": True
        })

        project_path = project_info["project_dir"]
        project_name = project_info["project_name"]

        # 2. 测试项目
        console.print("[bold yellow]步骤 2: 测试项目[/bold yellow]")
        self.state.current_phase = "testing"
        evaluation_result = self._test_project(project_path, project_name)

        self.state.add_execution_record({
            "phase": "testing",
            "evaluation_result": evaluation_result,
            "success": evaluation_result.get("status") == "PASS"
        })

        if evaluation_result["status"] != "PASS":
            console.print("[bold red]项目测试失败，流程终止[/bold red]")
            console.print(f"[red]失败原因：{evaluation_result['feedback']}[/red]")
            self.state.error_message = f"项目测试失败：{evaluation_result['feedback']}"
            return

        # 3. 部署项目
        console.print("[bold yellow]步骤 3: 部署项目[/bold yellow]")
        self.state.current_phase = "deployment"
        deployment_result = self._deploy_project(project_path, project_name)

        self.state.add_execution_record({
            "phase": "deployment",
            "deployment_result": deployment_result,
            "success": deployment_result.get("status") == "SUCCESS"
        })

        if deployment_result:
            self.state.add_execution_record({
                "phase": "deployment",
                "deployment_result": deployment_result,
                "success": deployment_result.get("status") == "SUCCESS"
            })

        # 4. 审计项目
        console.print("[bold yellow]步骤 4: 审计项目[/bold yellow]")
        self.state.current_phase = "auditing"
        
        # 执行审计
        audit_result = self.auditor.audit()
        self.state.last_audit_result = audit_result
        
        # 使用智能路由决定下一步行动
        action, reason = router(self.state, audit_result)
        
        console.print(f"[bold magenta]路由决策：{action} - {reason}[/bold magenta]")
        
        # 根据路由结果执行相应操作
        if action == "NEXT_TASK":
            # 任务通过，重置重试计数
            self.state.reset_retry_count()
            console.print("[bold green]审计成功，项目流程完成[/bold green]")
            self.state.success = True
            
        elif action == "RETRY_CURRENT":
            # 任务未通过，但仍在重试范围内
            console.print("[bold yellow]审计未通过，准备重试...[/bold yellow]")
            # 这里可以触发Worker重新执行特定任务
            self._handle_retry_logic(audit_result)
            
        elif action == "HITL":
            # 进入HITL模式
            console.print("[bold red]进入HITL模式[/bold red]")
            self._handle_hitl_mode(audit_result)
        
        # 检查是否需要进入HITL模式
        if should_enter_hitl_mode(self.state, audit_result):
            console.print("[bold red]触发HITL模式[/bold red]")
            self._handle_hitl_mode(audit_result)

    def _handle_retry_logic(self, audit_result: Dict[str, Any]):
        """
        处理重试逻辑

        Args:
            audit_result: 审计结果
        """
        # 使用Worker根据审计反馈重新执行任务
        feedback = audit_result.get("feedback", "")
        current_task_desc = self.state.current_task_description

        # 将审计反馈加入任务描述，让Worker知道需要修复什么
        enhanced_task_desc = f"{current_task_desc}\n\n审计反馈：{feedback}"

        console.print(f"[yellow]使用审计反馈重新执行任务...[/yellow]")
        console.print(f"[yellow]反馈：{feedback}[/yellow]")

        # 使用增强版Worker执行任务
        result = self.worker.run(enhanced_task_desc, self.state)

        # 重新审计
        new_audit_result = self.auditor.audit()
        self.state.last_audit_result = new_audit_result

        # 再次路由
        action, reason = router(self.state, new_audit_result)
        console.print(f"[bold magenta]重试后路由决策：{action} - {reason}[/bold magenta]")

        if action == "NEXT_TASK":
            self.state.reset_retry_count()
            console.print("[bold green]重试成功，项目流程完成[/bold green]")
            self.state.success = True
        elif action == "RETRY_CURRENT":
            console.print("[bold yellow]重试仍未通过，继续重试...[/bold yellow]")
            # 递归处理，但要防止无限递归
            if self.state.retry_count < self.state.max_retries:
                self._handle_retry_logic(new_audit_result)
            else:
                # 如果重试次数已达到上限，进入HITL模式
                console.print("[bold red]重试达到上限，进入HITL模式[/bold red]")
                self._handle_hitl_mode(new_audit_result)
        elif action == "HITL":
            console.print("[bold red]重试达到上限，进入HITL模式[/bold red]")
            self._handle_hitl_mode(new_audit_result)

    def _handle_hitl_mode(self, audit_result: Dict[str, Any]):
        """
        处理HITL模式
        
        Args:
            audit_result: 审计结果
        """
        # 进入HITL模式
        hitl_action = hitl_mode(self.state)
        
        if hitl_action == "FORCE_PASS":
            console.print("[bold green]用户选择强制通过，继续执行[/bold green]")
            # 强制通过当前任务，继续执行
            self.state.success = True
        elif hitl_action == "RETRY":
            console.print("[bold yellow]用户选择重试[/bold yellow]")
            # 重置重试计数，重新执行
            self.state.reset_retry_count()
            # 重新执行当前任务
            self._execute_workflow(self.state.current_task_description)
        elif hitl_action == "EXIT":
            console.print("[bold blue]用户选择退出[/bold blue]")
            save_state_before_exit(self.state)
            sys.exit(0)

    def _generate_project(self, user_requirement: str) -> dict:
        """
        生成项目

        Args:
            user_requirement: 用户需求

        Returns:
            项目信息字典
        """
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
        console.print("[bold yellow]部署项目到开发环境[/bold yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("部署项目...", total=None)
            deployment_result = self.deployment_manager.deploy_project(
                project_path,
                project_name,
                "development"  # 默认部署到开发环境
            )
            progress.stop()

        if deployment_result["status"] == "SUCCESS":
            console.print(Panel(
                f"项目 {project_name} 已成功部署到 development 环境！\n\n" +
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