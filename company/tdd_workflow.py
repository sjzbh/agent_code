"""
TDD Workflow Manager - Ensures test-driven development process
"""
from typing import Dict, Any
from pathlib import Path
import os
import subprocess
import tempfile

from roles.qa_engineer import QAEngineer
from roles.coder import Coder
from rich.console import Console

console = Console()

class TDDWorkflow:
    """TDD Workflow Manager - ensures test-driven development process"""
    
    def __init__(self):
        self.qa_engineer = QAEngineer()
        self.coder = Coder()
    
    def execute_tdd_process(self, design_document: str, user_requirement: str) -> Dict[str, Any]:
        """
        Execute the TDD process: create tests first, then implement code
        Args:
            design_document: System design document
            user_requirement: User requirements
        Returns:
            TDD execution results
        """
        console.print("[bold blue]开始执行TDD流程...[/bold blue]")
        
        # Step 1: Create test cases first (before implementation)
        console.print("[bold yellow]步骤 1: 创建测试用例 (TDD原则)[/bold yellow]")
        test_result = self.qa_engineer.create_test_cases(
            design_document=design_document,
            task_description=user_requirement
        )
        
        if not test_result['success']:
            console.print("[bold red]测试用例创建失败[/bold red]")
            return {
                "success": False,
                "error": "测试用例创建失败",
                "test_result": test_result
            }
        
        # Step 2: Implement code based on tests and design
        console.print("[bold yellow]步骤 2: 基于测试和设计实现代码[/bold yellow]")
        implementation_result = self.coder.implement_code(
            design_document=design_document,
            task_description=f"{user_requirement}\n\n请确保代码能通过以下测试:\n{str(test_result.get('test_cases', []))}"
        )
        
        if not implementation_result['success']:
            console.print("[bold red]代码实现失败[/bold red]")
            return {
                "success": False,
                "error": "代码实现失败",
                "test_result": test_result,
                "implementation_result": implementation_result
            }
        
        # Step 3: Run tests against the implementation
        console.print("[bold yellow]步骤 3: 运行测试验证实现[/bold yellow]")
        test_execution_result = self.run_tests_against_implementation(
            test_files=test_result['test_files'],
            implementation_files=implementation_result['code_files']
        )
        
        # Step 4: Evaluate if all tests pass
        all_tests_pass = self.evaluate_test_results(test_execution_result)
        
        tdd_result = {
            "success": all_tests_pass,
            "test_creation": test_result,
            "implementation": implementation_result,
            "test_execution": test_execution_result,
            "all_tests_pass": all_tests_pass
        }
        
        if all_tests_pass:
            console.print("[bold green]TDD流程成功完成 - 所有测试通过！[/bold green]")
        else:
            console.print("[bold red]TDD流程完成 - 部分测试失败[/bold red]")
        
        return tdd_result
    
    def run_tests_against_implementation(self, test_files: list, implementation_files: list) -> Dict[str, Any]:
        """
        Run tests against the implementation
        Args:
            test_files: List of test files
            implementation_files: List of implementation files
        Returns:
            Test execution results
        """
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy implementation files to temp directory
            for impl_file in implementation_files:
                file_path = impl_file.get('path', '')
                content = impl_file.get('content', '')
                
                if file_path and content:
                    temp_file_path = Path(temp_dir) / file_path
                    temp_file_path.parent.mkdir(parents=True, exist_ok=True)
                    temp_file_path.write_text(content, encoding='utf-8')
            
            # Copy test files to temp directory
            for test_file in test_files:
                file_path = test_file.get('path', '')
                content = test_file.get('content', '')
                
                if file_path and content:
                    temp_file_path = Path(temp_dir) / file_path
                    temp_file_path.parent.mkdir(parents=True, exist_ok=True)
                    temp_file_path.write_text(content, encoding='utf-8')
            
            # Run tests in the temporary environment
            try:
                # Change to temp directory and run pytest
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                # Run pytest to execute tests
                result = subprocess.run(
                    ['python', '-m', 'pytest', '.'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                os.chdir(original_cwd)
                
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                    "command": "python -m pytest ."
                }
            except subprocess.TimeoutExpired:
                os.chdir(original_cwd)
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "Test execution timed out",
                    "return_code": -1,
                    "error": "timeout"
                }
            except FileNotFoundError:
                os.chdir(original_cwd)
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "pytest not found, please install pytest",
                    "return_code": -1,
                    "error": "pytest not found"
                }
            except Exception as e:
                os.chdir(original_cwd)
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": str(e),
                    "return_code": -1,
                    "error": str(e)
                }
    
    def evaluate_test_results(self, test_execution_result: Dict[str, Any]) -> bool:
        """
        Evaluate test results to determine if all tests pass
        Args:
            test_execution_result: Test execution results
        Returns:
            Boolean indicating if all tests pass
        """
        if not test_execution_result.get('success', False):
            return False
        
        # Check if there are any failures in the output
        stderr = test_execution_result.get('stderr', '')
        stdout = test_execution_result.get('stdout', '')
        
        # Look for failure indicators in output
        combined_output = (stdout + stderr).lower()
        
        failure_indicators = ['failed', 'error', 'traceback', 'exception']
        for indicator in failure_indicators:
            if indicator in combined_output:
                return False
        
        # If return code is 0 and no failure indicators, assume success
        return test_execution_result.get('return_code', 0) == 0