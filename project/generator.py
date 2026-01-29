import os
import json
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from config import ai_client_manager
from prompts import PROJECT_GENERATOR_PROMPT
from state import shared_state

console = Console()

class ProjectGenerator:
    """
    项目生成器
    负责根据用户需求生成新的项目结构
    """
    def __init__(self):
        self.client_config = ai_client_manager.get_config()
        self.project_templates = {
            "python": self._create_python_project,
            "web": self._create_web_project,
            "cli": self._create_cli_project,
            "api": self._create_api_project
        }
    
    def generate_project(self, user_requirement: str, project_type: str = "auto", project_name: str = None):
        """
        生成项目
        
        Args:
            user_requirement: 用户需求
            project_type: 项目类型，可选值: "auto", "python", "web", "cli", "api"
            project_name: 项目名称
            
        Returns:
            项目信息字典，包含项目路径、文件列表等
        """
        # 生成项目名称（如果未提供）
        if not project_name:
            project_name = self._generate_project_name(user_requirement)
        
        # 确定项目类型
        if project_type == "auto":
            project_type = self._detect_project_type(user_requirement)
        
        # 创建项目目录
        project_dir = os.path.join("./generated_projects", project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        # 生成项目结构
        # 调用对应的项目生成方法
        if project_type in self.project_templates:
            project_info = self.project_templates[project_type](user_requirement, project_dir, project_name)
        else:
            # 默认生成Python项目
            project_info = self._create_python_project(user_requirement, project_dir, project_name)
        
        # 项目生成完成
        
        return project_info
    
    def _generate_project_name(self, user_requirement: str) -> str:
        """
        生成项目名称
        
        Args:
            user_requirement: 用户需求
            
        Returns:
            项目名称
        """
        prompt = f"请根据以下需求生成一个简短、有意义的项目名称，只返回名称，不要包含其他内容：\n{user_requirement}"
        
        if self.client_config:
            response = self._call_llm(prompt)
            project_name = response.strip().replace(" ", "_").lower()
            # 确保项目名称合法
            project_name = "".join(c for c in project_name if c.isalnum() or c == "_")
            return project_name[:50]  # 限制长度
        else:
            return f"project_{int(time.time())}"
    
    def _detect_project_type(self, user_requirement: str) -> str:
        """
        检测项目类型
        
        Args:
            user_requirement: 用户需求
            
        Returns:
            项目类型
        """
        prompt = f"请根据以下需求判断项目类型，返回以下类型之一：python, web, cli, api\n{user_requirement}"
        
        if self.client_config:
            response = self._call_llm(prompt)
            project_type = response.strip().lower()
            if project_type in self.project_templates:
                return project_type
        return "python"
    
    def _create_python_project(self, user_requirement: str, project_dir: str, project_name: str) -> dict:
        """
        创建Python项目
        """
        prompt = f"""{PROJECT_GENERATOR_PROMPT}

项目类型：Python
项目名称：{project_name}
用户需求：{user_requirement}

请生成完整的项目结构，包括：
1. 项目文件和目录
2. 每个文件的内容
3. requirements.txt
4. README.md

返回格式为JSON：
{{
  "files": [
    {{
      "path": "文件路径",
      "content": "文件内容"
    }}
  ]
}}
"""
        
        try:
            response = self._call_llm(prompt)
            project_structure = self._parse_project_structure(response)
            
            # 写入文件
            files = []
            for file_info in project_structure.get("files", []):
                file_path = os.path.join(project_dir, file_info["path"])
                file_dir = os.path.dirname(file_path)
                os.makedirs(file_dir, exist_ok=True)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(file_info["content"])
                
                files.append(file_path)
                # 添加到共享状态
                shared_state.add_file(file_path)
            
            project_info = {
                "project_name": project_name,
                "project_dir": project_dir,
                "project_type": "python",
                "files": files
            }
            
            return project_info
        except Exception as e:
            # 在没有AI客户端的情况下，提供默认的求和脚本
            import random
            import string
            
            # 生成随机乱码
            random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            script_name = f"abonde{random_suffix}.py"
            
            # 创建求和脚本内容
            script_content = '''#!/usr/bin/env python3
"""
1-100的求和脚本
运行后等待一分钟将删除
"""
import time
import os

# 计算1-100的和
sum_result = sum(range(1, 101))
print(f"1-100的和为: {sum_result}")

# 等待一分钟
print("等待一分钟后删除脚本...")
time.sleep(60)

# 删除自身
script_path = os.path.abspath(__file__)
try:
    os.remove(script_path)
    print(f"脚本已成功删除: {script_path}")
except Exception as e:
    print(f"删除脚本失败: {e}")
'''
            
            # 创建README.md
            readme_content = '''# 1-100求和脚本

这是一个简单的Python脚本，用于计算1-100的和，运行后等待一分钟将自动删除自身。

## 使用方法

```bash
python abonde*.py
```

## 功能说明

- 计算1-100的和并输出结果
- 运行后等待60秒
- 自动删除自身
'''
            
            # 写入文件
            files = []
            
            # 写入脚本文件
            script_path = os.path.join(project_dir, script_name)
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)
            files.append(script_path)
            shared_state.add_file(script_path)
            
            # 写入README.md
            readme_path = os.path.join(project_dir, "README.md")
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            files.append(readme_path)
            shared_state.add_file(readme_path)
            
            # 写入requirements.txt
            requirements_path = os.path.join(project_dir, "requirements.txt")
            with open(requirements_path, "w", encoding="utf-8") as f:
                f.write("# No dependencies required\n")
            files.append(requirements_path)
            shared_state.add_file(requirements_path)
            
            project_info = {
                "project_name": project_name,
                "project_dir": project_dir,
                "project_type": "python",
                "files": files
            }
            
            return project_info
    
    def _create_web_project(self, user_requirement: str, project_dir: str, project_name: str) -> dict:
        """
        创建Web项目
        """
        # 类似 _create_python_project 的实现
        # 这里简化处理，调用通用方法
        return self._create_python_project(user_requirement, project_dir, project_name)
    
    def _create_cli_project(self, user_requirement: str, project_dir: str, project_name: str) -> dict:
        """
        创建CLI项目
        """
        # 类似 _create_python_project 的实现
        return self._create_python_project(user_requirement, project_dir, project_name)
    
    def _create_api_project(self, user_requirement: str, project_dir: str, project_name: str) -> dict:
        """
        创建API项目
        """
        # 类似 _create_python_project 的实现
        return self._create_python_project(user_requirement, project_dir, project_name)
    
    def _call_llm(self, prompt: str) -> str:
        """
        调用LLM
        
        Args:
            prompt: 提示词
            
        Returns:
            LLM响应
        """
        if not self.client_config:
            raise Exception("AI客户端未初始化，无法生成项目")
        
        client = self.client_config["client"]
        client_type = self.client_config["type"]
        
        try:
            if client_type == "gemini":
                response = client.generate_content(prompt)
                return response.text
            elif client_type == "openai":
                response = client.chat.completions.create(
                    model=self.client_config["model"],
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
            else:
                raise Exception(f"不支持的客户端类型: {client_type}")
        except Exception as e:
            raise Exception(f"调用LLM失败: {e}")
    
    def _parse_project_structure(self, response: str) -> dict:
        """
        解析项目结构
        
        Args:
            response: LLM响应
            
        Returns:
            项目结构字典
        """
        # 清理响应
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
        
        # 解析JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            raise Exception("解析项目结构失败，LLM返回的不是有效的JSON")

# 导入必要的模块
from rich.panel import Panel
