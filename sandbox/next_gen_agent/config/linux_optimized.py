
# Linux-optimized configuration
import os
import subprocess

# Hardcoded Linux-specific paths and commands
DEFAULT_PYTHON_PATH = "/usr/bin/python3"
DEFAULT_VENV_CMD = ["python3", "-m", "venv"]
DEFAULT_PIP_CMD = ["python3", "-m", "pip"]

def create_venv(path):
    """Linux-optimized virtual environment creation"""
    result = subprocess.run(DEFAULT_VENV_CMD + [path], capture_output=True, text=True)
    return result.returncode == 0

def install_deps(requirements_file, venv_path):
    """Linux-optimized dependency installation"""
    pip_path = os.path.join(venv_path, "bin", "pip")  # Linux-specific path
    result = subprocess.run([pip_path, "install", "-r", requirements_file], capture_output=True, text=True)
    return result.returncode == 0
