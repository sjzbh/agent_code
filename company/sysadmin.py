"""
SysAdmin Role - System Administrator for the Virtual Software Company
Responsible for managing and maintaining the development environment
"""
import subprocess
import sys
import os
from typing import Dict, Any
from config import settings, ai_client_manager
from utils import clean_json_text, call_llm, load_prompt
from rich.console import Console
from memory.evolutionary_memory import evolutionary_memory

console = Console()

class SysAdmin:
    """
    System Administrator Role - manages and maintains the development environment
    """
    
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        Initialize SysAdmin role
        Args:
            model_name: Model name, defaults to "gemini-1.5-pro"
        """
        self.model_name = model_name
        self.sysadmin_config = ai_client_manager.get_config("auto") or {
            "client": None,
            "type": "none",
            "model": "none"
        }
        self.prompts = load_prompt("company/prompts/sysadmin.yaml")
        self.memory = evolutionary_memory

    def diagnose_issue(self, issue_description: str) -> Dict[str, Any]:
        """
        Diagnose environment issues
        Args:
            issue_description: Description of the issue
        Returns:
            Diagnosis results with solutions
        """
        console.print("[bold blue]SysAdmin 正在诊断环境问题...[/bold blue]")
        
        # Retrieve relevant memories
        memory_context = self.memory.apply_solutions(issue_description)
        memory_str = "\n".join(memory_context) if memory_context else "无历史经验"
        
        # Format the prompt using the YAML template
        prompt_template = self.prompts['diagnose_issue_task']
        prompt = prompt_template.format(
            issue_description=issue_description,
            evolutionary_memory=memory_str
        )
        
        if self.sysadmin_config['client']:
            raw_response = call_llm(self.sysadmin_config, prompt)
            diagnosis_result = clean_json_text(raw_response)
            
            # Parse the diagnosis result
            try:
                diagnosis_data = eval(diagnosis_result)  # Note: In real implementation, use safer parsing
                console.print("[bold green]问题诊断完成！[/bold green]")
                
                return {
                    "success": True,
                    "diagnosis": diagnosis_data,
                    "raw_response": diagnosis_result
                }
            except Exception:
                # If parsing fails, return the raw response
                console.print("[bold yellow]问题诊断结果解析失败，返回原始内容[/bold yellow]")
                return {
                    "success": False,
                    "diagnosis": {},
                    "raw_response": diagnosis_result,
                    "error": "诊断结果解析失败"
                }
        else:
            console.print("[bold red]错误: SysAdmin AI 未初始化[/bold red]")
            return {
                "success": False,
                "diagnosis": {},
                "raw_response": "",
                "error": "SysAdmin AI 未初始化"
            }

    def fix_environment(self, fix_requirements: str) -> Dict[str, Any]:
        """
        Fix environment issues
        Args:
            fix_requirements: Requirements for fixing the environment
        Returns:
            Fix results
        """
        console.print("[bold blue]SysAdmin 正在修复环境...[/bold blue]")
        
        # Retrieve relevant memories
        memory_context = self.memory.apply_solutions(fix_requirements)
        memory_str = "\n".join(memory_context) if memory_context else "无历史经验"
        
        # Format the prompt using the YAML template
        prompt_template = self.prompts['fix_environment_task']
        prompt = prompt_template.format(
            fix_requirements=fix_requirements,
            evolutionary_memory=memory_str
        )
        
        if self.sysadmin_config['client']:
            raw_response = call_llm(self.sysadmin_config, prompt)
            fix_result = clean_json_text(raw_response)
            
            # Parse the fix result
            try:
                fix_data = eval(fix_result)  # Note: In real implementation, use safer parsing
                console.print("[bold green]环境修复完成！[/bold green]")
                
                # Actually execute the fix if possible
                # This is a simplified version - in reality, this would execute system commands safely
                execution_result = self._execute_fix_commands(fix_data.get('fix_steps', []))
                
                return {
                    "success": True,
                    "fix_data": fix_data,
                    "execution_result": execution_result,
                    "raw_response": fix_result
                }
            except Exception:
                # If parsing fails, return the raw response
                console.print("[bold yellow]修复结果解析失败，返回原始内容[/bold yellow]")
                return {
                    "success": False,
                    "fix_data": {},
                    "execution_result": {},
                    "raw_response": fix_result,
                    "error": "修复结果解析失败"
                }
        else:
            console.print("[bold red]错误: SysAdmin AI 未初始化[/bold red]")
            return {
                "success": False,
                "fix_data": {},
                "execution_result": {},
                "raw_response": "",
                "error": "SysAdmin AI 未初始化"
            }

    def configure_environment(self, configuration_requirements: str) -> Dict[str, Any]:
        """
        Configure the development environment
        Args:
            configuration_requirements: Requirements for environment configuration
        Returns:
            Configuration results
        """
        console.print("[bold blue]SysAdmin 正在配置环境...[/bold blue]")
        
        # Retrieve relevant memories
        memory_context = self.memory.apply_solutions(configuration_requirements)
        memory_str = "\n".join(memory_context) if memory_context else "无历史经验"
        
        # Format the prompt using the YAML template
        prompt_template = self.prompts['configure_environment_task']
        prompt = prompt_template.format(
            configuration_requirements=configuration_requirements,
            evolutionary_memory=memory_str
        )
        
        if self.sysadmin_config['client']:
            raw_response = call_llm(self.sysadmin_config, prompt)
            config_result = clean_json_text(raw_response)
            
            # Parse the configuration result
            try:
                config_data = eval(config_result)  # Note: In real implementation, use safer parsing
                console.print("[bold green]环境配置完成！[/bold green]")
                
                # Actually execute the configuration if possible
                execution_result = self._execute_configuration_commands(config_data.get('config_steps', []))
                
                return {
                    "success": True,
                    "config_data": config_data,
                    "execution_result": execution_result,
                    "raw_response": config_result
                }
            except Exception:
                # If parsing fails, return the raw response
                console.print("[bold yellow]配置结果解析失败，返回原始内容[/bold yellow]")
                return {
                    "success": False,
                    "config_data": {},
                    "execution_result": {},
                    "raw_response": config_result,
                    "error": "配置结果解析失败"
                }
        else:
            console.print("[bold red]错误: SysAdmin AI 未初始化[/bold red]")
            return {
                "success": False,
                "config_data": {},
                "execution_result": {},
                "raw_response": "",
                "error": "SysAdmin AI 未初始化"
            }

    def _execute_fix_commands(self, fix_steps: list) -> Dict[str, Any]:
        """
        Execute fix commands (simulated)
        Args:
            fix_steps: List of commands to execute for fixing
        Returns:
            Execution results
        """
        # This is a simulation - in a real implementation, this would execute system commands safely
        results = []
        for step in fix_steps:
            # Execute the command safely
            console.print(f"[yellow]执行修复步骤: {step}[/yellow]")
            # In real implementation, execute the command and collect results
            results.append({"step": step, "status": "executed", "result": "success"})
        
        return {"steps_executed": results, "overall_status": "success"}

    def _execute_configuration_commands(self, config_steps: list) -> Dict[str, Any]:
        """
        Execute configuration commands (simulated)
        Args:
            config_steps: List of commands to execute for configuration
        Returns:
            Execution results
        """
        # This is a simulation - in a real implementation, this would execute system commands safely
        results = []
        for step in config_steps:
            # Execute the command safely
            console.print(f"[yellow]执行配置步骤: {step}[/yellow]")
            # In real implementation, execute the command and collect results
            results.append({"step": step, "status": "executed", "result": "success"})
        
        return {"steps_executed": results, "overall_status": "success"}

    def check_system_health(self) -> Dict[str, Any]:
        """
        Check overall system health
        Returns:
            System health status
        """
        console.print("[bold blue]SysAdmin 正在检查系统健康状况...[/bold blue]")
        
        try:
            # Check disk space
            disk_usage = self._get_disk_usage()
            
            # Check memory usage
            memory_usage = self._get_memory_usage()
            
            # Check CPU usage
            cpu_usage = self._get_cpu_usage()
            
            # Check running processes
            processes = self._get_running_processes()
            
            health_status = {
                "disk_usage": disk_usage,
                "memory_usage": memory_usage,
                "cpu_usage": cpu_usage,
                "running_processes": processes,
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }
            
            console.print("[bold green]系统健康检查完成！[/bold green]")
            return {
                "success": True,
                "health_status": health_status
            }
        except Exception as e:
            console.print(f"[bold red]系统健康检查失败: {e}[/bold red]")
            return {
                "success": False,
                "health_status": {},
                "error": str(e)
            }

    def _get_disk_usage(self) -> str:
        """Get disk usage (simulated)"""
        # In a real implementation, this would use platform-specific commands
        return "Simulated disk usage: 45% used"
    
    def _get_memory_usage(self) -> str:
        """Get memory usage (simulated)"""
        # In a real implementation, this would use platform-specific commands
        return "Simulated memory usage: 60% used"
    
    def _get_cpu_usage(self) -> str:
        """Get CPU usage (simulated)"""
        # In a real implementation, this would use platform-specific commands
        return "Simulated CPU usage: 30% used"
    
    def _get_running_processes(self) -> list:
        """Get running processes (simulated)"""
        # In a real implementation, this would use platform-specific commands
        return ["process1", "process2", "process3"]