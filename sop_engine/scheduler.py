"""
SOP State Graph Scheduler - Manages the workflow between different roles
"""
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
import json
import os
from pathlib import Path

from roles import Architect, Coder, TechLead, QAEngineer
from company.runner import Runner
from company.auditor import AuditorAgent

class CompanyStage(Enum):
    """Company workflow stages"""
    PM_REQUIREMENTS = "pm_requirements"
    ARCHITECT_DESIGN = "architect_design"
    CODER_IMPLEMENTATION = "coder_implementation"
    TECHLEAD_REVIEW = "techlead_review"
    QA_TESTING = "qa_testing"
    AUDITOR_ACCEPTANCE = "auditor_acceptance"
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
        self.architect = Architect()
        self.coder = Coder()
        self.techlead = TechLead()
        self.qa_engineer = QAEngineer()
        self.runner = Runner()
        self.auditor = AuditorAgent()
        
        # Initialize workflow state
        self.state = WorkflowState(stage=CompanyStage.PM_REQUIREMENTS)
        
        # Define the workflow graph
        self.workflow_graph = {
            CompanyStage.PM_REQUIREMENTS: self._process_pm_requirements,
            CompanyStage.ARCHITECT_DESIGN: self._process_architect_design,
            CompanyStage.CODER_IMPLEMENTATION: self._process_coder_implementation,
            CompanyStage.TECHLEAD_REVIEW: self._process_techlead_review,
            CompanyStage.QA_TESTING: self._process_qa_testing,
            CompanyStage.AUDITOR_ACCEPTANCE: self._process_auditor_acceptance
        }
    
    def execute_workflow(self, user_requirement: str) -> WorkflowState:
        """Execute the complete workflow from PM requirements to completion"""
        self.state.user_requirement = user_requirement
        
        # Execute each stage in sequence
        stages_order = [
            CompanyStage.ARCHITECT_DESIGN,
            CompanyStage.CODER_IMPLEMENTATION,
            CompanyStage.TECHLEAD_REVIEW,
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
                        return self.state
        
        self.state.stage = CompanyStage.COMPLETED
        return self.state
    
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
    
    def _process_qa_testing(self) -> bool:
        """Process QA testing stage"""
        # Create test cases based on design and requirements
        test_result = self.qa_engineer.create_test_cases(
            design_document=self.state.design_document,
            task_description=self.state.user_requirement
        )
        
        if test_result['success']:
            # Run the tests in a sandbox environment
            project_path = "."  # In real scenario, this would be the project directory
            test_execution = self.qa_engineer.run_tests(project_path)
            
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

# Import console here to avoid circular import
from rich.console import Console
console = Console()