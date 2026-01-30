"""
SOP State Graph Scheduler - Next Generation
Manages the workflow between different roles
"""
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
import json
import os
from pathlib import Path

from roles.architect import Architect
from roles.coder import Coder
from roles.techlead import TechLead
from roles.qa_engineer import QAEngineer
from roles.project_manager import ProjectManager
from roles.auditor import Auditor
from roles.sysadmin import SysAdmin
from roles.evolution_officer import EvolutionOfficer

class CompanyStage(Enum):
    """Company workflow stages"""
    PM_REQUIREMENTS = "pm_requirements"
    PM_ANALYSIS = "pm_analysis"
    ARCHITECT_DESIGN = "architect_design"
    CODER_IMPLEMENTATION = "coder_implementation"
    TECHLEAD_REVIEW = "techlead_review"
    RUNNER_EXECUTION = "runner_execution"
    SYSADMIN_ENVIRONMENT = "sysadmin_environment"
    QA_TESTING = "qa_testing"
    AUDITOR_ACCEPTANCE = "auditor_acceptance"
    EVOLUTION_ANALYSIS = "evolution_analysis"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class WorkflowState:
    """Represents the state of the company workflow"""
    stage: CompanyStage
    user_requirement: str = ""
    design_document: str = ""
    implementation: str = ""
    review_feedback: str = ""
    test_results: Dict[str, Any] = None
    acceptance_result: Dict[str, Any] = None
    error_message: str = ""
    artifacts: Dict[str, Any] = None

class SOPScheduler:
    """SOP State Graph Scheduler - manages the workflow between different roles"""
    
    def __init__(self):
        self.project_manager = ProjectManager()
        self.architect = Architect()
        self.coder = Coder()
        self.techlead = TechLead()
        self.qa_engineer = QAEngineer()
        self.runner = SysAdmin()  # Using SysAdmin for both running and environment management
        self.auditor = Auditor()
        self.sysadmin = SysAdmin()
        self.evolution_officer = EvolutionOfficer()
        
        # Initialize workflow state
        self.state = WorkflowState(stage=CompanyStage.PM_REQUIREMENTS)
        
        # Define the workflow graph
        self.workflow_graph = {
            CompanyStage.PM_REQUIREMENTS: self._process_pm_requirements,
            CompanyStage.PM_ANALYSIS: self._process_pm_analysis,
            CompanyStage.ARCHITECT_DESIGN: self._process_architect_design,
            CompanyStage.CODER_IMPLEMENTATION: self._process_coder_implementation,
            CompanyStage.TECHLEAD_REVIEW: self._process_techlead_review,
            CompanyStage.RUNNER_EXECUTION: self._process_runner_execution,
            CompanyStage.SYSADMIN_ENVIRONMENT: self._process_sysadmin_environment,
            CompanyStage.QA_TESTING: self._process_qa_testing,
            CompanyStage.AUDITOR_ACCEPTANCE: self._process_auditor_acceptance,
            CompanyStage.EVOLUTION_ANALYSIS: self._process_evolution_analysis
        }
    
    def execute_workflow(self, user_requirement: str) -> WorkflowState:
        """Execute the complete workflow from PM requirements to completion"""
        self.state.user_requirement = user_requirement
        
        # Execute each stage in sequence
        stages_order = [
            CompanyStage.PM_ANALYSIS,
            CompanyStage.ARCHITECT_DESIGN,
            CompanyStage.CODER_IMPLEMENTATION,
            CompanyStage.TECHLEAD_REVIEW,
            CompanyStage.RUNNER_EXECUTION,
            CompanyStage.SYSADMIN_ENVIRONMENT,
            CompanyStage.QA_TESTING,
            CompanyStage.AUDITOR_ACCEPTANCE
        ]
        
        for stage in stages_order:
            self.state.stage = stage
            console.print(f"[bold yellow]执行阶段: {stage.value}[/bold yellow]")
            
            # Process the current stage
            success = self._execute_stage(stage)
            
            if not success:
                self.state.stage = CompanyStage.FAILED
                # Trigger evolution officer to analyze failure
                self._trigger_evolution_analysis()
                return self.state
            
            # Check if we need to loop back due to review rejection
            if stage == CompanyStage.TECHLEAD_REVIEW:
                review_approved = self.state.artifacts.get('review_approved', True)
                if not review_approved:
                    console.print("[bold yellow]代码审查未通过，返回编码阶段...[/bold yellow]")
                    # Re-execute the implementation stage with feedback
                    self.state.stage = CompanyStage.CODER_IMPLEMENTATION
                    success = self._execute_stage(CompanyStage.CODER_IMPLEMENTATION)
                    if not success:
                        self.state.stage = CompanyStage.FAILED
                        # Trigger evolution officer to analyze failure
                        self._trigger_evolution_analysis()
                        return self.state
        
        self.state.stage = CompanyStage.EVOLUTION_ANALYSIS
        # Trigger evolution officer to analyze successful completion
        self._trigger_evolution_analysis()
        
        self.state.stage = CompanyStage.COMPLETED
        return self.state
    
    def _trigger_evolution_analysis(self):
        """Trigger evolution officer to analyze the execution log"""
        # Create a summary of the execution log
        execution_log = f"""
        项目执行日志:
        - 需求: {self.state.user_requirement}
        - 设计文档: {self.state.design_document[:100] if self.state.design_document else 'N/A'}
        - 实现代码: {self.state.implementation[:100] if self.state.implementation else 'N/A'}
        - 审查反馈: {self.state.review_feedback}
        - 测试结果: {self.state.test_results}
        - 验收结果: {self.state.acceptance_result}
        - 错误信息: {self.state.error_message}
        - 最终状态: {self.state.stage.value}
        """
        
        # Trigger the evolution officer to analyze and store insights
        self.evolution_officer.trigger_post_project_analysis(
            execution_log=execution_log,
            project_context=self.state.user_requirement
        )
    
    def _execute_stage(self, stage: CompanyStage) -> bool:
        """Execute a single stage"""
        try:
            handler = self.workflow_graph.get(stage)
            if handler:
                return handler()
            else:
                console.print(f"[bold red]未知阶段: {stage}[/bold red]")
                return False
        except Exception as e:
            console.print(f"[bold red]执行阶段 {stage} 时出错: {e}[/bold red]")
            self.state.error_message = str(e)
            return False
    
    def _process_pm_requirements(self) -> bool:
        """Process PM requirements stage"""
        # This stage just sets up the initial requirement
        console.print(f"[green]已接收需求: {self.state.user_requirement}[/green]")
        return True
    
    def _process_pm_analysis(self) -> bool:
        """Process PM analysis stage - convert user requirements to structured PRD"""
        console.print("[bold yellow]执行阶段: PM需求分析[/bold yellow]")
        
        # Use the project manager to clarify requirements and generate PRD
        clarification_result = self.project_manager.clarify_requirements(self.state.user_requirement)
        
        if clarification_result.get('needs_clarification', False):
            # If requirements need clarification, we'll assume they were clarified for this demo
            # In a real implementation, this would involve user interaction
            console.print("[yellow]需求需要澄清，使用原始需求继续...[/yellow]")
            prd_result = self.project_manager.generate_prd(self.state.user_requirement)
        else:
            # Generate PRD from clear requirements
            prd_result = self.project_manager.generate_prd(clarification_result.get('clear_requirement', self.state.user_requirement))
        
        if prd_result['success']:
            self.state.user_requirement = prd_result['prd_document'].get('product_overview', self.state.user_requirement)
            if not self.state.artifacts:
                self.state.artifacts = {}
            self.state.artifacts.update({
                'prd_document': prd_result['prd_document']
            })
            console.print("[green]PM需求分析完成，PRD生成成功[/green]")
            return True
        else:
            console.print(f"[red]PRD生成失败: {prd_result.get('error', 'Unknown error')}[/red]")
            return False
    
    def _process_architect_design(self) -> bool:
        """Process architect design stage"""
        result = self.architect.design_system(self.state.user_requirement)
        if result['success']:
            self.state.design_document = result['design_md']
            self.state.artifacts = {'design_document': result['design_document']}
            console.print("[green]架构设计完成[/green]")
            return True
        else:
            console.print(f"[red]架构设计失败: {result.get('error', 'Unknown error')}[/red]")
            return False
    
    def _process_coder_implementation(self) -> bool:
        """Process coder implementation stage"""
        # Get any review feedback to incorporate into the implementation
        review_feedback = self.state.review_feedback
        
        # Combine original requirement with design document
        task_description = self.state.user_requirement
        if review_feedback:
            task_description += f"\n\n代码审查反馈: {review_feedback}"
        
        result = self.coder.implement_code(
            design_document=self.state.design_document,
            task_description=task_description
        )
        
        if result['success']:
            self.state.implementation = result['raw_output']
            if not self.state.artifacts:
                self.state.artifacts = {}
            self.state.artifacts.update({
                'implementation': result['code_files'],
                'files_created': result['files_created']
            })
            console.print("[green]代码实现完成[/green]")
            return True
        else:
            console.print(f"[red]代码实现失败: {result.get('error', 'Unknown error')}[/red]")
            return False
    
    def _process_techlead_review(self) -> bool:
        """Process techlead review stage"""
        # Get implementation details
        implementation = self.state.implementation
        design_document = self.state.design_document
        
        # Perform code review
        review_result = self.techlead.review_code(
            code=implementation,
            design_document=design_document,
            task_description=self.state.user_requirement
        )
        
        if 'error' not in review_result:
            self.state.review_feedback = review_result['feedback']
            
            if not self.state.artifacts:
                self.state.artifacts = {}
            self.state.artifacts.update({
                'review_approved': review_result['approved'],
                'review_feedback': review_result['feedback'],
                'review_issues': review_result['issues']
            })
            
            if review_result['approved']:
                console.print("[green]代码审查通过[/green]")
                return True
            else:
                console.print(f"[yellow]代码审查未通过: {review_result['feedback']}[/yellow]")
                # Don't return False here, as we allow looping back to implementation
                return True
        else:
            console.print(f"[red]代码审查失败: {review_result.get('error', 'Unknown error')}[/red]")
            return False
    
    def _process_runner_execution(self) -> bool:
        """Process runner execution stage"""
        console.print("[bold yellow]执行阶段: 代码运行[/bold yellow]")
        
        # Run the implementation code in a sandbox environment
        run_result = self.runner.run_code_with_monitoring(
            code_content=self.state.implementation,
            environment_requirements="Standard Python environment"
        )
        
        if not self.state.artifacts:
            self.state.artifacts = {}
        self.state.artifacts.update({
            'run_result': run_result
        })
        
        if run_result['success']:
            console.print("[green]代码运行成功[/green]")
            return True
        else:
            console.print(f"[red]代码运行失败: {run_result.get('stderr', 'Unknown error')}[/red]")
            return False
    
    def _process_sysadmin_environment(self) -> bool:
        """Process sysadmin environment stage"""
        console.print("[bold yellow]执行阶段: 环境管理[/bold yellow]")
        
        # Check environment health and ensure everything is properly configured
        health_result = self.sysadmin.check_environment()
        
        if not self.state.artifacts:
            self.state.artifacts = {}
        self.state.artifacts.update({
            'health_check': health_result
        })
        
        if health_result['success']:
            console.print("[green]环境检查通过[/green]")
            return True
        else:
            console.print(f"[red]环境检查失败: {health_result.get('error', 'Unknown error')}[/red]")
            return False
    
    def _process_qa_testing(self) -> bool:
        """Process QA testing stage"""
        # Create test cases based on design and requirements
        test_result = self.qa_engineer.create_test_cases(
            design_document=self.state.design_document,
            implementation_code=self.state.implementation,
            task_description=self.state.user_requirement
        )
        
        if test_result['success']:
            # Execute tests against the implementation
            test_execution = self.qa_engineer.execute_tests(
                implementation_code=self.state.implementation,
                test_cases=test_result['test_cases']
            )
            
            self.state.test_results = test_execution
            
            if not self.state.artifacts:
                self.state.artifacts = {}
            self.state.artifacts.update({
                'test_cases': test_result['test_cases'],
                'test_strategy': test_result['test_strategy'],
                'test_execution': test_execution
            })
            
            if test_execution['success'] and test_execution.get('failed', 0) == 0:
                console.print("[green]测试通过[/green]")
                return True
            else:
                console.print(f"[red]测试失败: {test_execution.get('details', 'Unknown error')}[/red]")
                return False
        else:
            console.print(f"[red]测试创建失败: {test_result.get('error', 'Unknown error')}[/red]")
            return False
    
    def _process_auditor_acceptance(self) -> bool:
        """Process auditor acceptance stage"""
        # Perform final audit
        audit_result = self.auditor.audit(
            task_description=self.state.user_requirement,
            execution_logs=[f"Design: {self.state.design_document}", 
                           f"Implementation: {self.state.implementation}"]
        )
        
        self.state.acceptance_result = audit_result
        
        if not self.state.artifacts:
            self.state.artifacts = {}
        self.state.artifacts.update({
            'acceptance_result': audit_result
        })
        
        if audit_result.get('status') == 'PASS':
            console.print("[green]项目验收通过[/green]")
            return True
        else:
            console.print(f"[red]项目验收失败: {audit_result.get('feedback', 'Unknown error')}[/red]")
            return False
    
    def _process_evolution_analysis(self) -> bool:
        """Process evolution analysis stage - analyze execution log and store insights"""
        console.print("[bold yellow]执行阶段: 进化分析[/bold yellow]")
        
        # This stage is handled by the _trigger_evolution_analysis method
        # which is called after successful completion or failure
        return True

# Import console here to avoid circular import
from rich.console import Console
console = Console()