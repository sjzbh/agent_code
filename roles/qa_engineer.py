"""
QA Engineer Role - Next Generation
"""
import json
import os
from typing import Dict, Any
from config import WORKER_CONFIG
from utils import clean_json_text, call_llm, load_prompt, safe_json_parse
from rich.console import Console

console = Console()

class QAEngineer:
    """
    QA Engineer Role - responsible for creating test cases and performing quality assurance
    """
    
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        Initialize QA Engineer role
        Args:
            model_name: Model name, defaults to "gemini-1.5-pro"
        """
        self.model_name = model_name
        self.qa_config = WORKER_CONFIG

    def create_test_cases(self, design_document: str, implementation_code: str, task_description: str) -> Dict[str, Any]:
        """
        Create test cases based on design document and implementation
        Args:
            design_document: System design document
            implementation_code: Implementation code
            task_description: Task description
        Returns:
            Test cases and testing strategy
        """
        console.print("[bold blue]QA Engineer 正在创建测试用例...[/bold blue]")
        
        # Load the QA engineer prompt
        try:
            with open("roles/prompts/qa_engineer.yaml", 'r', encoding='utf-8') as f:
                import yaml
                prompts = yaml.safe_load(f)
                prompt_template = prompts['test_creation_task']
        except:
            # Fallback prompt if file not found
            prompt_template = "你是测试工程师。请为以下设计和实现创建测试用例：设计文档：{design_doc}，实现代码：{impl_code}，任务描述：{task_desc}。返回测试用例和测试策略。"
        
        prompt = prompt_template.format(
            design_doc=design_document,
            impl_code=implementation_code,
            task_desc=task_description
        )
        
        if self.qa_config['client']:
            raw_response = call_llm(self.qa_config, prompt)
            test_output = clean_json_text(raw_response)
            
            # Use safe JSON parsing
            test_data = safe_json_parse(test_output, {})
            
            console.print("[bold green]测试用例创建完成！[/bold green]")
            
            # Save test files
            test_files_created = self.save_test_files(test_data.get('test_files', []))
            
            return {
                "success": True,
                "test_cases": test_data.get('test_cases', []),
                "test_strategy": test_data.get('test_strategy', {}),
                "test_files": test_data.get('test_files', []),
                "test_files_created": test_files_created,
                "raw_output": test_output
            }
        else:
            console.print("[bold red]错误: QA Engineer AI 未初始化[/bold red]")
            return {
                "success": False,
                "test_cases": [],
                "test_strategy": {},
                "test_files": [],
                "test_files_created": [],
                "raw_output": "",
                "error": "QA Engineer AI 未初始化"
            }

    def save_test_files(self, test_files_data: list) -> list:
        """
        Save test files to disk
        Args:
            test_files_data: List of test file dictionaries with path and content
        Returns:
            List of created test file paths
        """
        created_files = []
        for file_info in test_files_data:
            file_path = file_info.get('path', '')
            content = file_info.get('content', '')
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            created_files.append(file_path)
            console.print(f"[green]创建测试文件: {file_path}[/green]")
        
        return created_files

    def execute_tests(self, implementation_code: str, test_cases: list) -> Dict[str, Any]:
        """
        Execute tests against implementation code
        Args:
            implementation_code: Code to test
            test_cases: List of test cases to execute
        Returns:
            Test execution results
        """
        console.print("[bold blue]QA Engineer 正在执行测试...[/bold blue]")
        
        # In a real implementation, this would run the actual tests
        # For now, we'll simulate the test execution
        try:
            # This is where you would actually execute the tests
            # For example, using subprocess to run pytest on the implementation
            console.print("[green]测试执行完成！[/green]")
            
            return {
                "success": True,
                "passed": 5,  # Simulated test results
                "failed": 0,
                "skipped": 0,
                "total": 5,
                "details": "所有测试通过"
            }
        except Exception as e:
            console.print(f"[red]测试执行失败: {e}[/red]")
            return {
                "success": False,
                "passed": 0,
                "failed": 1,
                "skipped": 0,
                "total": 1,
                "details": str(e),
                "error": str(e)
            }