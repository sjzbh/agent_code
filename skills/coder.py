import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path


class CoderSkill:
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
    
    def read_file(self, file_path: str) -> str:
        path = self._resolve_path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    
    def write_file(self, file_path: str, content: str, create_dirs: bool = True) -> bool:
        path = self._resolve_path(file_path)
        
        if create_dirs and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    def append_file(self, file_path: str, content: str) -> bool:
        path = self._resolve_path(file_path)
        
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    def delete_file(self, file_path: str) -> bool:
        path = self._resolve_path(file_path)
        
        if path.exists():
            path.unlink()
            return True
        return False
    
    def modify_file(self, file_path: str, old_content: str, new_content: str) -> bool:
        content = self.read_file(file_path)
        
        if old_content not in content:
            return False
        
        modified = content.replace(old_content, new_content, 1)
        return self.write_file(file_path, modified)
    
    def insert_at_line(self, file_path: str, line_number: int, content: str) -> bool:
        file_content = self.read_file(file_path)
        lines = file_content.split('\n')
        
        if line_number < 0 or line_number > len(lines):
            return False
        
        lines.insert(line_number, content)
        return self.write_file(file_path, '\n'.join(lines))
    
    def find_and_replace(self, file_path: str, pattern: str, replacement: str, 
                         use_regex: bool = False) -> int:
        content = self.read_file(file_path)
        
        if use_regex:
            new_content, count = re.subn(pattern, replacement, content)
        else:
            count = content.count(pattern)
            new_content = content.replace(pattern, replacement)
        
        if count > 0:
            self.write_file(file_path, new_content)
        
        return count
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        path = self._resolve_path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = path.stat()
        
        return {
            "path": str(path),
            "name": path.name,
            "extension": path.suffix,
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "is_file": path.is_file(),
            "is_directory": path.is_dir()
        }
    
    def _resolve_path(self, file_path: str) -> Path:
        path = Path(file_path)
        if not path.is_absolute():
            path = self.project_root / path
        return path.resolve()
