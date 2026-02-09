import subprocess
import sys
import os
import tempfile
import time
from typing import Tuple, Optional, Dict, Any


class ShellSkill:
    
    def __init__(self, timeout: int = 60, cwd: Optional[str] = None):
        self.timeout = timeout
        self.cwd = cwd or os.getcwd()
    
    def run(self, command: str, timeout: Optional[int] = None) -> Tuple[bool, str, str]:
        timeout = timeout or self.timeout
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.cwd,
                encoding='utf-8',
                errors='replace'
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)
    
    def run_python(self, code: str, timeout: Optional[int] = None) -> Tuple[bool, str, str]:
        timeout = timeout or self.timeout
        
        code = self._clean_code(code)
        
        try:
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False, encoding='utf-8'
            ) as f:
                f.write(code)
                temp_path = f.name
            
            try:
                result = subprocess.run(
                    [sys.executable, temp_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.cwd,
                    encoding='utf-8',
                    errors='replace'
                )
                
                success = result.returncode == 0
                return success, result.stdout, result.stderr
                
            finally:
                os.unlink(temp_path)
                
        except subprocess.TimeoutExpired:
            return False, "", f"Execution timed out after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)
    
    def run_async(self, command: str) -> subprocess.Popen:
        return subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.cwd,
            encoding='utf-8'
        )
    
    def check_command(self, command: str) -> bool:
        try:
            result = subprocess.run(
                f"which {command}" if os.name != 'nt' else f"where {command}",
                shell=True,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_environment(self) -> Dict[str, str]:
        return dict(os.environ)
    
    def set_environment(self, key: str, value: str):
        os.environ[key] = value
    
    def get_current_directory(self) -> str:
        return os.getcwd()
    
    def change_directory(self, path: str) -> bool:
        try:
            os.chdir(path)
            self.cwd = os.getcwd()
            return True
        except Exception:
            return False
    
    def _clean_code(self, code: str) -> str:
        code = code.strip()
        
        if code.startswith("```"):
            lines = code.split("\n")
            if lines[-1] == "```":
                code = "\n".join(lines[1:-1])
            else:
                code = "\n".join(lines[1:])
        
        return code
    
    def install_package(self, package: str) -> Tuple[bool, str]:
        success, stdout, stderr = self.run(f"pip install {package}")
        
        if success:
            return True, f"Successfully installed {package}"
        else:
            return False, f"Failed to install {package}: {stderr}"
    
    def check_python_version(self) -> str:
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def check_disk_space(self, path: str = ".") -> Dict[str, float]:
        import shutil
        total, used, free = shutil.disk_usage(path)
        
        return {
            "total_gb": total / (1024 ** 3),
            "used_gb": used / (1024 ** 3),
            "free_gb": free / (1024 ** 3),
            "used_percent": (used / total) * 100
        }
