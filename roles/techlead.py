"""
TechLead Role - Responsible for code review and quality assurance
"""
import json
from typing import Dict, Any
from config import settings, ai_client_manager
from utils import clean_json_text, call_llm, load_prompt, safe_json_parse
from rich.console import Console
from memory.evolutionary_memory import evolutionary_memory

console = Console()

class TechLead:
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        Initialize TechLead role
        Args:
            model_name: Model name, defaults to "gemini-1.5-pro"
        """
        self.model_name = model_name
        self.techlead_config = ai_client_manager.get_config("auto") or {
            "client": None,
            "type": "none",
            "model": "none"
        }
        self.prompts = load_prompt("roles/prompts/techlead.yaml")
        self.memory = evolutionary_memory

    def review_code(self, code: str, design_document: str, task_description: str) -> Dict[str, Any]:
        """
        Review code implementation against design document
        Args:
            code: Code to review
            design_document: Original design document
            task_description: Task description
        Returns:
            Review result with feedback and approval status
        """
        console.print("[bold blue]TechLead 正在审查代码...[/bold blue]")

        # Retrieve relevant memories
        memory_context = self.memory.apply_solutions(task_description)
        memory_str = "\n".join(memory_context) if memory_context else "无历史经验"

        # Format the prompt using the YAML template
        prompt_template = self.prompts['code_review_task']
        prompt = prompt_template.format(
            design_doc_content=design_document,
            code_content=code,
            user_requirement=task_description,
            evolutionary_memory=memory_str
        )

        if self.techlead_config['client']:
            raw_response = call_llm(self.techlead_config, prompt)

            # Extract review from response, removing any non-review content
            review_result = self._extract_review_from_response(raw_response)

            # Parse the review result using safe parser
            review_data = safe_json_parse(review_result, {})
            console.print("[bold green]代码审查完成！[/bold green]")

            # Determine if code is approved
            approved = review_data.get('approved', False)

            if approved:
                console.print("[bold green]代码审查通过！[/bold green]")
            else:
                console.print("[bold yellow]代码需要修改！[/bold yellow]")

            return {
                "approved": approved,
                "feedback": review_data.get('feedback', ''),
                "issues": review_data.get('issues', []),
                "suggestions": review_data.get('suggestions', []),
                "review_raw": review_result
            }
        else:
            console.print("[bold red]错误: TechLead AI 未初始化[/bold red]")
            return {
                "approved": False,
                "feedback": "TechLead AI 未初始化",
                "issues": [],
                "suggestions": [],
                "review_raw": "",
                "error": "TechLead AI 未初始化"
            }

    def re_review_code(self, modified_code: str, original_feedback: str) -> Dict[str, Any]:
        """
        Re-review code after modifications
        Args:
            modified_code: Code after modifications
            original_feedback: Original feedback that led to modifications
        Returns:
            Re-review result with feedback and approval status
        """
        console.print("[bold blue]TechLead 正在重新审查修改后的代码...[/bold blue]")

        # Retrieve relevant memories
        memory_context = self.memory.apply_solutions(original_feedback)
        memory_str = "\n".join(memory_context) if memory_context else "无历史经验"

        # Format the prompt using the YAML template
        prompt_template = self.prompts['re_review_task']
        prompt = prompt_template.format(
            original_feedback=original_feedback,
            modified_code=modified_code,
            evolutionary_memory=memory_str
        )

        if self.techlead_config['client']:
            raw_response = call_llm(self.techlead_config, prompt)
            review_result = clean_json_text(raw_response)

            # Parse the review result
            try:
                review_data = json.loads(review_result)
                console.print("[bold green]重新审查完成！[/bold green]")

                # Determine if code is approved
                approved = review_data.get('approved', False)

                if approved:
                    console.print("[bold green]修改后的代码审查通过！[/bold green]")
                else:
                    console.print("[bold yellow]修改后的代码仍需进一步修改！[/bold yellow]")

                return {
                    "approved": approved,
                    "feedback": review_data.get('feedback', ''),
                    "issues": review_data.get('issues', []),
                    "suggestions": review_data.get('suggestions', []),
                    "review_raw": review_result
                }
            except json.JSONDecodeError:
                console.print("[bold red]重新审查结果解析失败，返回原始内容[/bold red]")
                return {
                    "approved": False,
                    "feedback": "重新审查结果解析失败",
                    "issues": [],
                    "suggestions": [],
                    "review_raw": review_result,
                    "error": "重新审查结果解析失败"
                }
        else:
            console.print("[bold red]错误: TechLead AI 未初始化[/bold red]")
            return {
                "approved": False,
                "feedback": "TechLead AI 未初始化",
                "issues": [],
                "suggestions": [],
                "review_raw": "",
                "error": "TechLead AI 未初始化"
            }

    def _extract_review_from_response(self, raw_response: str) -> str:
        """
        Extract review content from AI response, removing any non-review text
        Args:
            raw_response: Raw response from AI
        Returns:
            Cleaned review content suitable for JSON parsing
        """
        import re

        # First, clean the JSON text
        cleaned = clean_json_text(raw_response)

        # If the response contains markdown code blocks, extract the content
        # Look for JSON blocks in the response
        json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', cleaned, re.DOTALL | re.IGNORECASE)
        if json_match:
            return json_match.group(1)

        # If there are Chinese characters that shouldn't be in code review, remove them
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

    def approve_code(self, code: str, design_document: str, task_description: str) -> bool:
        """
        Simple approval method that returns whether code is approved
        Args:
            code: Code to approve
            design_document: Design document
            task_description: Task description
        Returns:
            Boolean indicating approval status
        """
        review_result = self.review_code(code, design_document, task_description)
        return review_result.get('approved', False)