"""
SysAdmin Role - System Administrator for the Virtual Software Company
Optimized for Linux environment based on experience base
"""
import subprocess
import sys
import os
import tempfile
from typing import Dict, Any
from pathlib import Path

from rich.console import Console
from utils import load_prompt, safe_json_parse
from memory.evolutionary_memory import evolutionary_memory

console = Console()

class SysAdmin:
    """
    System Administrator Role - runs code, manages environments, and fixes environment issues
    Optimized for Linux environment
    """
    
    def __init__(self):
        self.temp_dirs = []
        self.prompts = load_prompt("roles/prompts/sysadmin.yaml")
        self.memory = evolutionary_memory

    def __del__(self):
        """Cleanup temporary directories on object deletion"""
        self.cleanup()

    def create_sandbox_env(self, name: str = None) -> str:
        """
        Create an isolated sandbox environment (Linux optimized)
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

        # Create a virtual environment in the sandbox using Linux-specific paths
        subprocess.run([sys.executable, "-m", "venv", sandbox_path], check=True)

        console.print(f"[green]沙箱环境创建成功: {sandbox_path}[/green]")
        return sandbox_path

    def run_code_with_monitoring(self, code_content: str, environment_requirements: str = "") -> Dict[str, Any]:
        """
        Run code with monitoring and detailed reporting (Linux optimized)
        Args:
            code_content: Code to run
            environment_requirements: Environment requirements
        Returns:
            Detailed execution results
        """
        console.print("[bold blue]SysAdmin 正在运行代码...[/bold blue]")

        # Create a temporary file to run the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code_content)
            temp_file = f.name

        try:
            # Run the code in a subprocess using Linux-specific paths
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )

            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr

            return {
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Execution timed out",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }
        finally:
            # Clean up the temporary file
            os.unlink(temp_file)

    def analyze_error_and_fix(self, error_message: str) -> Dict[str, Any]:
        """
        Analyze error message and attempt to fix the environment (Linux optimized)
        Args:
            error_message: Error message to analyze
        Returns:
            Fix attempt results
        """
        console.print("[bold blue]SysAdmin 正在分析错误并尝试修复...[/bold blue]")

        # Check for common error patterns in Linux environment
        if "ModuleNotFoundError" in error_message or "ImportError" in error_message:
            # Try to identify missing modules
            import re
            module_match = re.search(r"named ['\"]([^'\"]+)['\"]", error_message)
            if module_match:
                missing_module = module_match.group(1)
                console.print(f"[yellow]检测到缺失模块: {missing_module}[/yellow]")
                
                # Attempt to install the missing module using Linux-specific pip
                fix_result = self.attempt_install_package(missing_module)
                return {
                    "fixed": fix_result["success"],
                    "action_taken": f"Attempted to install {missing_module}",
                    "result": fix_result
                }
        
        # For other types of errors, return analysis
        return {
            "fixed": False,
            "action_taken": "Analyzed error but no automatic fix available",
            "error_analysis": error_message
        }

    def attempt_install_package(self, package_name: str) -> Dict[str, Any]:
        """
        Attempt to install a package (Linux optimized)
        Args:
            package_name: Name of the package to install
        Returns:
            Installation result
        """
        console.print(f"[yellow]尝试安装包: {package_name}[/yellow]")
        
        try:
            # Use Linux-specific pip command
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout for installation
            )
            
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            
            if success:
                console.print(f"[green]包 {package_name} 安装成功[/green]")
            else:
                console.print(f"[red]包 {package_name} 安装失败[/red]")
            
            return {
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Installation timed out",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }

    def install_dependencies_with_reporting(self, dependencies_list: str) -> Dict[str, Any]:
        """
        Install dependencies with detailed reporting (Linux optimized)
        Args:
            dependencies_list: List of dependencies to install
        Returns:
            Installation results
        """
        console.print("[bold blue]SysAdmin 正在安装依赖...[/bold blue]")

        # Create a temporary requirements file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(dependencies_list)
            req_file = f.name

        try:
            # Use Linux-specific pip command
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", req_file],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for installation
            )

            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr

            return {
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Installation timed out",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }
        finally:
            # Clean up the temporary file
            os.unlink(req_file)

    def check_environment(self, check_requirements: str = "") -> Dict[str, Any]:
        """
        Check the environment for requirements (Linux optimized)
        Args:
            check_requirements: What to check in the environment
        Returns:
            Environment check results
        """
        console.print("[bold blue]SysAdmin 正在检查环境...[/bold blue]")

        try:
            # Check if Python is available (Linux specific)
            result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
            python_version = result.stdout.strip() if result.returncode == 0 else "Not found"

            # Check if pip is available (Linux specific)
            result = subprocess.run(['python3', '-m', 'pip', '--version'], capture_output=True, text=True)
            pip_version = result.stdout.strip() if result.returncode == 0 else "Not found"

            return {
                "status": "OK",
                "python_version": python_version,
                "pip_version": pip_version
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }

    def cleanup(self):
        """Clean up all temporary directories"""
        for temp_dir in self.temp_dirs:
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass  # Ignore errors during cleanup
        self.temp_dirs = []