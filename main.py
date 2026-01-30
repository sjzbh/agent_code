#!/usr/bin/env python3
"""
Virtual Software Company - Next Generation (V2.1)
Project Chrysalis - Self-Evolving Architecture with Linux Optimization
"""
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from sop_engine.scheduler import SOPScheduler, WorkflowState, CompanyStage
from roles.project_manager import ProjectManager
from roles.architect import Architect
from roles.coder import Coder
from roles.techlead import TechLead
from roles.qa_engineer import QAEngineer
from roles.auditor import Auditor
from roles.sysadmin import SysAdmin
from roles.evolution_officer import EvolutionOfficer

console = Console()

def start_company_cycle():
    """
    Start the Virtual Software Company cycle - Next Generation
    This is the main entry point for the SOP-driven pipeline
    """
    console.print(Panel(
        "🚀 欢迎来到虚拟软件公司 - 下一代 (Virtual Software Company NextGen)!\n\n"
        "我们采用 SOP (Standard Operating Procedure) 驱动的多智能体架构，\n"
        "确保高质量的软件交付。流程如下：\n\n"
        "PM需求 → 架构师设计 → 工程师开发 ↔ 技术主管审查 → 运行工程师执行 → 系统管理员环境管理 → 测试工程师测试 → 审计员验收 → 进化官分析\n",
        title="[bold cyan]虚拟软件公司 - 下一代 V2.1[/bold cyan]",
        border_style="cyan"
    ))
    
    try:
        # Get user requirement
        user_requirement = Prompt.ask("[bold green]请输入您的项目需求[/bold green]")
        
        if not user_requirement.strip():
            console.print("[yellow]未输入需求，退出程序[/yellow]")
            return
        
        # Initialize all roles
        project_manager = ProjectManager()
        architect = Architect()
        coder = Coder()
        techlead = TechLead()
        qa_engineer = QAEngineer()
        runner = SysAdmin()
        auditor = Auditor()
        sysadmin = SysAdmin()
        evolution_officer = EvolutionOfficer()
        
        # Execute the SOP workflow
        scheduler = SOPScheduler()
        final_state = scheduler.execute_workflow(user_requirement)
        
        # Display results
        if final_state.stage == CompanyStage.COMPLETED:
            console.print(Panel(
                "✅ 项目已成功完成！\n\n"
                "所有SOP流程已执行完毕，项目通过最终验收。\n"
                "交付物已生成。",
                title="[bold green]项目完成[/bold green]",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"❌ 项目执行失败！\n\n"
                f"失败阶段: {final_state.stage.value}\n"
                f"错误信息: {final_state.error_message}",
                title="[bold red]项目失败[/bold red]",
                border_style="red"
            ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]操作被用户中断[/yellow]")
    except Exception as e:
        console.print(f"[bold red]系统错误: {e}[/bold red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_company_cycle()