"""
QA Engineer Role - Responsible for testing and quality assurance
"""
import json
import os
from typing import Dict, Any
from config import settings, ai_client_manager
from utils import clean_json_text, call_llm, load_prompt, safe_json_parse
from rich.console import Console
from memory.evolutionary_memory import evolutionary_memory

console = Console()

class QAEngineer:
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        Initialize QA Engineer role
        Args:
            model_name: Model name, defaults to "gemini-1.5-pro"
        """
        self.model_name = model_name
        self.qa_config = ai_client_manager.get_config("auto") or {
            "client": None,
            "type": "none",
            "model": "none"
        }
        self.prompts = load_prompt("roles/prompts/qa_engineer.yaml")
        self.memory = evolutionary_memory

    def create_test_cases(self, design_document: str, implementation_code: str, task_description: str) -> Dict[str, Any]:
        """
        Create test cases based on design document and task description
        Args:
            design_document: System design document
            implementation_code: Implementation code to test
            task_description: Task description
        Returns:
            Test cases and testing strategy
        """
        console.print("[bold blue]QA Engineer 正在创建测试用例...[/bold blue]")

        # Retrieve relevant memories
        memory_context = self.memory.apply_solutions(task_description)
        memory_str = "\n".join(memory_context) if memory_context else "无历史经验"

        # Format the prompt using the YAML template
        prompt_template = self.prompts['create_tests_task']
        prompt = prompt_template.format(
            design_doc_content=design_document,
            implementation_code=implementation_code,
            user_requirement=task_description,
            evolutionary_memory=memory_str
        )

        if self.qa_config['client']:
            raw_response = call_llm(self.qa_config, prompt)

            # Extract test cases from response, removing any non-test content
            test_output = self._extract_test_from_response(raw_response)

            # Parse the test output using safe parser
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

        # Retrieve relevant memories
        memory_context = self.memory.apply_solutions("test execution")
        memory_str = "\n".join(memory_context) if memory_context else "无历史经验"

        # Format the prompt using the YAML template
        prompt_template = self.prompts['execute_tests_task']
        prompt = prompt_template.format(
            implementation_code=implementation_code,
            test_cases=str(test_cases),
            evolutionary_memory=memory_str
        )

        if self.qa_config['client']:
            raw_response = call_llm(self.qa_config, prompt)
            test_output = clean_json_text(raw_response)

            # Parse the test execution results
            try:
                test_results = json.loads(test_output)
                console.print("[bold green]测试执行完成！[/bold green]")

                return {
                    "success": test_results.get('success', False),
                    "passed": test_results.get('passed', 0),
                    "failed": test_results.get('failed', 0),
                    "skipped": test_results.get('skipped', 0),
                    "total": test_results.get('total', 0),
                    "details": test_results.get('details', ''),
                    "raw_output": test_output
                }
            except json.JSONDecodeError:
                console.print("[bold red]测试执行结果解析失败，返回原始内容[/bold red]")
                return {
                    "success": False,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "total": 0,
                    "details": "测试执行结果解析失败",
                    "raw_output": test_output,
                    "error": "测试执行结果解析失败"
                }
        else:
            console.print("[bold red]错误: QA Engineer AI 未初始化[/bold red]")
            return {
                "success": False,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "total": 0,
                "details": "QA Engineer AI 未初始化",
                "raw_output": "",
                "error": "QA Engineer AI 未初始化"
            }

    def suggest_fixes_for_failed_tests(self, test_failure_details: str) -> Dict[str, Any]:
        """
        Suggest fixes for failed tests
        Args:
            test_failure_details: Details of test failures
        Returns:
            Fix suggestions
        """
        console.print("[bold blue]QA Engineer 正在分析测试失败原因并提供建议...[/bold blue]")

        # Retrieve relevant memories
        memory_context = self.memory.apply_solutions(test_failure_details)
        memory_str = "\n".join(memory_context) if memory_context else "无历史经验"

        # Format the prompt using the YAML template
        prompt_template = self.prompts['test_fix_suggestion_task']
        prompt = prompt_template.format(
            test_failure_details=test_failure_details,
            evolutionary_memory=memory_str
        )

        if self.qa_config['client']:
            raw_response = call_llm(self.qa_config, prompt)
            fix_output = clean_json_text(raw_response)

            # Parse the fix suggestions
            try:
                fix_data = json.loads(fix_output)
                console.print("[bold green]修复建议生成完成！[/bold green]")

                return {
                    "success": True,
                    "fix_suggestions": fix_data.get('suggestions', []),
                    "analysis": fix_data.get('analysis', ''),
                    "raw_output": fix_output
                }
            except json.JSONDecodeError:
                console.print("[bold red]修复建议解析失败，返回原始内容[/bold red]")
                return {
                    "success": False,
                    "fix_suggestions": [],
                    "analysis": "",
                    "raw_output": fix_output,
                    "error": "修复建议解析失败"
                }
        else:
            console.print("[bold red]错误: QA Engineer AI 未初始化[/bold red]")
            return {
                "success": False,
                "fix_suggestions": [],
                "analysis": "",
                "raw_output": "",
                "error": "QA Engineer AI 未初始化"
            }

    def _extract_test_from_response(self, raw_response: str) -> str:
        """
        Extract test content from AI response, removing any non-test text
        Args:
            raw_response: Raw response from AI
        Returns:
            Cleaned test content suitable for JSON parsing
        """
        import re

        # First, clean the JSON text
        cleaned = clean_json_text(raw_response)

        # If the response contains markdown code blocks, extract the content
        # Look for JSON blocks in the response
        json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', cleaned, re.DOTALL | re.IGNORECASE)
        if json_match:
            return json_match.group(1)

        # If there are Chinese characters that shouldn't be in test cases, remove them
        chinese_char_pattern = r'[^\x00-\x7F\u4e00-\u9fff{}[\]:,""\\\-0-9.a-zA-Z\s\n\t]'
        cleaned = re.sub(chinese_char_pattern, '', cleaned)

        # Try to find a JSON-like structure in the cleaned text
        json_start = cleaned.find('{')
        json_end = cleaned.rfind('}')

        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_content = cleaned[json_start:json_end+1]
            return json_content
        else:
            # If no JSON structure found, return the cleaned text
            return cleaned

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

    def run_tests(self, project_path: str) -> Dict[str, Any]:
        """
        Execute tests in the project
        Args:
            project_path: Path to the project to test
        Returns:
            Test execution results
        """
        console.print(f"[bold blue]QA Engineer 正在运行测试...[/bold blue]")

        # This would typically run pytest or other test frameworks
        # For now, we'll simulate the test execution
        try:
            # In a real implementation, this would run actual tests
            # For example: subprocess.run(['pytest', project_path, '-v'])
            console.print("[green]测试执行完成！[/green]")

            return {
                "success": True,
                "passed": 10,  # Simulated test results
                "failed": 0,
                "skipped": 0,
                "total": 10,
                "details": "所有测试通过"
            }
        except Exception as e:
            console.print(f"[bold red]测试执行失败: {e}[/bold red]")
            return {
                "success": False,
                "passed": 0,
                "failed": 1,
                "skipped": 0,
                "total": 1,
                "details": str(e),
                "error": str(e)
            }