#!/usr/bin/env python3
"""
Virtual Software Company - Main Entry Point
An SOP-driven multi-agent pipeline for software development
"""
import os
import sys
from typing import Dict, Any

# 确保在Windows下使用UTF-8
if os.name == 'nt':
    os.system('chcp 65001 > nul 2>&1')

from sop_engine.scheduler import SOPScheduler, WorkflowState, CompanyStage
from memory.evolutionary_memory import evolutionary_memory
from company.tdd_workflow import TDDWorkflow
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

class VirtualSoftwareCompany:
    """
    Virtual Software Company - Orchestration class for the multi-agent pipeline
    Implements SOP-driven workflow with role atomization
    """
    
    def __init__(self):
        self.scheduler = SOPScheduler()
        self.tdd_workflow = TDDWorkflow()
        self.memory = evolutionary_memory
    
    def start_project(self, user_requirement: str) -> WorkflowState:
        """
        Start a new project following the SOP workflow
        Args:
            user_requirement: User requirements for the project
        Returns:
            Final workflow state
        """
        console.print(Panel(
            "欢迎来到虚拟软件公司！\n\n"
            "我们是一个SOP驱动的多智能体流水线，包含以下角色：\n"
            "- 架构师 (Architect): 负责系统设计\n"
            "- 工程师 (Coder): 负责代码实现\n"
            "- 技术主管 (TechLead): 负责代码审查\n"
            "- 测试工程师 (QA): 负责测试用例和质量保证\n"
            "- 审计员 (Auditor): 负责最终验收\n\n"
            f"项目需求：{user_requirement}",
            title="[bold cyan]虚拟软件公司[/bold cyan]",
            border_style="cyan"
        ))
        
        # Apply evolutionary memory - check if we have solutions for similar problems
        memory_solutions = self.memory.apply_solutions(user_requirement)
        if memory_solutions:
            console.print(f"[yellow]应用历史解决方案: {len(memory_solutions)} 条记录[/yellow]")
            for i, solution in enumerate(memory_solutions[:3]):  # Show first 3 solutions
                console.print(f"  {i+1}. {solution[:100]}...")
        
        # Execute the TDD workflow first (tests before implementation)
        console.print("[bold yellow]执行TDD流程...[/bold yellow]")
        tdd_result = self.tdd_workflow.execute_tdd_process(
            design_document="",  # Will be filled in by the architect
            user_requirement=user_requirement
        )
        
        if not tdd_result['success']:
            console.print("[bold red]TDD流程失败，但继续执行SOP流程...[/bold red]")
        
        # Execute the main SOP workflow
        console.print("[bold yellow]执行SOP工作流...[/bold yellow]")
        final_state = self.scheduler.execute_workflow(user_requirement)
        
        return final_state
    
    def run_interactive(self):
        """Run the company in interactive mode"""
        console.print(Panel(
            "欢迎来到虚拟软件公司！\n\n"
            "这是一个SOP驱动的多智能体流水线，实现角色原子化。\n"
            "请输入您的项目需求，我们将按照标准作业程序为您开发。",
            title="[bold cyan]虚拟软件公司 - SOP驱动的多智能体流水线[/bold cyan]",
            border_style="cyan"
        ))
        
        while True:
            try:
                user_input = Prompt.ask("[bold green]请输入您的项目需求[/bold green]", default="exit")
                
                if user_input.lower() == "exit":
                    console.print("[bold cyan]虚拟软件公司已关闭，感谢使用！[/bold cyan]")
                    break
                
                if not user_input.strip():
                    continue
                
                # Process the project
                final_state = self.start_project(user_input)
                
                # Display final results
                self.display_final_results(final_state)
                
            except KeyboardInterrupt:
                console.print("\n[bold yellow]操作被用户中断。[/bold yellow]")
                break
            except Exception as e:
                console.print(f"[bold red]发生未知错误：{str(e)}[/bold red]")
                import traceback
                traceback.print_exc()
                continue
    
    def display_final_results(self, state: WorkflowState):
        """Display the final results of the workflow"""
        if state.stage == CompanyStage.COMPLETED:
            console.print(Panel(
                "项目已成功完成！\n\n"
                "所有SOP流程已执行完毕，项目通过最终验收。\n"
                "以下是项目的主要交付物：\n"
                f"- 设计文档: {'已生成' if state.design_document else '未生成'}\n"
                f"- 代码实现: {'已生成' if state.implementation else '未生成'}\n"
                f"- 代码审查: {'已通过' if state.artifacts and state.artifacts.get('review_approved', False) else '未通过或未执行'}\n"
                f"- 测试结果: {'已通过' if state.test_results and state.test_results.get('success', False) else '未通过或未执行'}\n"
                f"- 最终验收: {'已通过' if state.acceptance_result and state.acceptance_result.get('status') == 'PASS' else '未通过或未执行'}",
                title="[bold green]项目完成[/bold green]",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"项目执行失败！\n\n"
                f"失败阶段: {state.stage.value}\n"
                f"错误信息: {state.error_message}",
                title="[bold red]项目失败[/bold red]",
                border_style="red"
            ))
    
    def run_with_args(self, user_requirement: str):
        """Run the company with command-line arguments"""
        final_state = self.start_project(user_requirement)
        self.display_final_results(final_state)
        return final_state

def main():
    """Main entry point"""
    try:
        company = VirtualSoftwareCompany()
        
        # Check if command line arguments are provided
        if len(sys.argv) > 1:
            user_requirement = ' '.join(sys.argv[1:])
            company.run_with_args(user_requirement)
        else:
            # Run in interactive mode
            company.run_interactive()
            
    except KeyboardInterrupt:
        console.print("\n操作被用户中断。")
    except Exception as e:
        console.print(f"发生错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()