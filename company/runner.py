"""
Enhanced Runner with Sandbox Isolation
"""
import subprocess
import sys
import os
import tempfile
import shutil
from typing import Dict, Any, Tuple
from pathlib import Path
import venv

from rich.console import Console

console = Console()

class Runner:
    """
    Enhanced Runner with Sandbox Isolation
    Runs code in isolated virtual environments to prevent system contamination
    """
    
    def __init__(self):
        self.temp_dirs = []
    
    def __del__(self):
        """Cleanup temporary directories on object deletion"""
        self.cleanup()
    
    def create_sandbox_env(self, name: str = None) -> str:
        """
        Create an isolated sandbox environment
        Args:
            name: Name for the sandbox (optional)
        Returns:
            Path to the sandbox environment
        """
        if name:
            sandbox_path = tempfile.mkdtemp(prefix=f"sandbox_{name}_")
        else:
            sandbox_path = tempfile.mkdtemp(prefix="sandbox_")
        
        self.temp_dirs.append(sandbox_path)
        
        # Create a virtual environment in the sandbox
        venv.create(sandbox_path, with_pip=True)
        
        console.print(f"[green]沙箱环境创建成功: {sandbox_path}[/green]")
        return sandbox_path
    
    def run_in_sandbox(self, code_or_command: str, sandbox_path: str = None) -> Tuple[bool, str, str]:
        """
        Run code or command in a sandbox environment
        Args:
            code_or_command: Code or command to execute
            sandbox_path: Path to sandbox environment (if None, creates a new one)
        Returns:
            Tuple of (success, stdout, stderr)
        """
        # Create sandbox if not provided
        if sandbox_path is None:
            sandbox_path = self.create_sandbox_env()
        
        # Determine if input is Python code or shell command
        is_python_code = self._is_python_code(code_or_command)
        
        try:
            if is_python_code:
                # Write Python code to a temporary file in the sandbox
                code_file_path = os.path.join(sandbox_path, "temp_code.py")
                with open(code_file_path, "w", encoding="utf-8") as f:
                    f.write(code_or_command)
                
                # Run the Python code using the sandbox's Python interpreter
                python_exe = os.path.join(sandbox_path, "bin", "python") if os.name != "nt" else os.path.join(sandbox_path, "Scripts", "python.exe")
                
                result = subprocess.run(
                    [python_exe, code_file_path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    encoding='utf-8',
                    errors='replace',
                    cwd=sandbox_path
                )
            else:
                # Run as shell command in the sandbox environment
                result = subprocess.run(
                    code_or_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    encoding='utf-8',
                    errors='replace',
                    cwd=sandbox_path
                )
            
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Execution timed out"
        except Exception as e:
            return False, "", str(e)
    
    def install_dependencies_in_sandbox(self, requirements: str, sandbox_path: str) -> Tuple[bool, str, str]:
        """
        Install dependencies in the sandbox environment
        Args:
            requirements: Requirements content or path to requirements.txt
            sandbox_path: Path to sandbox environment
        Returns:
            Tuple of (success, stdout, stderr)
        """
        # Determine if requirements is a file path or content
        if requirements.strip().endswith('.txt') and os.path.exists(requirements):
            # It's a file path
            req_file_path = requirements
        else:
            # It's content, write to a temporary file
            req_file_path = os.path.join(sandbox_path, "requirements.txt")
            with open(req_file_path, "w", encoding="utf-8") as f:
                f.write(requirements)
        
        # Install using the sandbox's pip
        pip_exe = os.path.join(sandbox_path, "bin", "pip") if os.name != "nt" else os.path.join(sandbox_path, "Scripts", "pip.exe")
        
        try:
            result = subprocess.run(
                [pip_exe, "install", "-r", req_file_path],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout for installation
                encoding='utf-8',
                errors='replace',
                cwd=sandbox_path
            )
            
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            
            return success, stdout, stderr
        except subprocess.TimeoutExpired:
            return False, "", "Installation timed out"
        except Exception as e:
            return False, "", str(e)
    
    def _is_python_code(self, text: str) -> bool:
        """
        Determine if the input is Python code or a shell command
        Args:
            text: Input text to analyze
        Returns:
            Boolean indicating if it's Python code
        """
        # Simple heuristic to determine if it's Python code
        python_indicators = [
            'import ', 'def ', 'class ', 'print(', 'if __name__',
            'for ', 'while ', 'try:', 'except:', 'with ', 'from '
        ]
        
        text_lower = text.lower()
        for indicator in python_indicators:
            if indicator in text_lower:
                return True
        
        # If it looks like a command (contains common command patterns)
        command_indicators = [
            'pip ', 'npm ', 'git ', 'ls ', 'cd ', 'mkdir ', 'rm ', 'mv ',
            'cp ', 'touch ', 'chmod ', 'chown ', 'ps ', 'kill ', 'top '
        ]
        
        for indicator in command_indicators:
            if text_lower.startswith(indicator):
                return False
        
        # Default to Python if uncertain
        return True
    
    def cleanup(self):
        """Clean up all temporary directories"""
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass  # Ignore errors during cleanup
        self.temp_dirs = []
    
    def run_test_in_sandbox(self, test_code: str, implementation_code: str, sandbox_path: str = None) -> Dict[str, Any]:
        """
        Run tests against implementation code in sandbox
        Args:
            test_code: Test code to run
            implementation_code: Implementation code to test
            sandbox_path: Path to sandbox environment
        Returns:
            Test execution results
        """
        if sandbox_path is None:
            sandbox_path = self.create_sandbox_env()
        
        # Write implementation code to sandbox
        impl_file_path = os.path.join(sandbox_path, "implementation.py")
        with open(impl_file_path, "w", encoding="utf-8") as f:
            f.write(implementation_code)
        
        # Write test code to sandbox
        test_file_path = os.path.join(sandbox_path, "test_implementation.py")
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_code)
        
        # Run the test
        success, stdout, stderr = self.run_in_sandbox(f"python {test_file_path}", sandbox_path)
        
        return {
            "success": success,
            "stdout": stdout,
            "stderr": stderr,
            "sandbox_path": sandbox_path
        }