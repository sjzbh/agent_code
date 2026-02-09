import os
import re
import fnmatch
from typing import List, Dict, Any, Optional, Generator
from pathlib import Path


class ExplorerSkill:
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
    
    def list_dir(self, path: str = ".", show_hidden: bool = False) -> List[str]:
        target = self._resolve_path(path)
        
        if not target.exists() or not target.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        
        items = []
        for item in target.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue
            
            if item.is_dir():
                items.append(f"[DIR]  {item.name}/")
            else:
                size = item.stat().st_size
                items.append(f"[FILE] {item.name} ({self._format_size(size)})")
        
        return sorted(items)
    
    def search(self, pattern: str, path: str = ".", 
               file_type: Optional[str] = None) -> List[str]:
        target = self._resolve_path(path)
        
        results = []
        
        for root, dirs, files in os.walk(target):
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    full_path = Path(root) / filename
                    
                    if file_type:
                        if not full_path.suffix.lower() == f".{file_type.lower()}":
                            continue
                    
                    results.append(str(full_path.relative_to(self.root_path)))
        
        return results
    
    def search_content(self, pattern: str, path: str = ".", 
                       file_pattern: str = "*", 
                       ignore_case: bool = True) -> List[Dict[str, Any]]:
        target = self._resolve_path(path)
        results = []
        
        flags = re.IGNORECASE if ignore_case else 0
        
        for root, dirs, files in os.walk(target):
            for filename in files:
                if not fnmatch.fnmatch(filename, file_pattern):
                    continue
                
                full_path = Path(root) / filename
                
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if re.search(pattern, line, flags):
                                results.append({
                                    "file": str(full_path.relative_to(self.root_path)),
                                    "line": line_num,
                                    "content": line.strip()
                                })
                except Exception:
                    continue
        
        return results
    
    def read_file(self, file_path: str, start_line: int = 0, 
                  end_line: Optional[int] = None) -> str:
        path = self._resolve_path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        if end_line is None:
            end_line = len(lines)
        
        return ''.join(lines[start_line:end_line])
    
    def get_file_tree(self, path: str = ".", max_depth: int = 3, 
                      show_hidden: bool = False) -> str:
        target = self._resolve_path(path)
        
        lines = []
        self._build_tree(target, lines, prefix="", max_depth=max_depth, 
                        current_depth=0, show_hidden=show_hidden)
        
        return '\n'.join(lines)
    
    def _build_tree(self, path: Path, lines: List[str], prefix: str, 
                    max_depth: int, current_depth: int, show_hidden: bool):
        if current_depth >= max_depth:
            return
        
        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return
        
        for i, item in enumerate(items):
            if not show_hidden and item.name.startswith('.'):
                continue
            
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            
            if item.is_dir():
                lines.append(f"{prefix}{current_prefix}{item.name}/")
                next_prefix = prefix + ("    " if is_last else "│   ")
                self._build_tree(item, lines, next_prefix, max_depth, 
                               current_depth + 1, show_hidden)
            else:
                lines.append(f"{prefix}{current_prefix}{item.name}")
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        path = self._resolve_path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = path.stat()
        
        return {
            "name": path.name,
            "path": str(path),
            "extension": path.suffix,
            "size": stat.st_size,
            "size_formatted": self._format_size(stat.st_size),
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "is_file": path.is_file(),
            "is_directory": path.is_dir(),
            "parent": str(path.parent)
        }
    
    def find_by_extension(self, extension: str, path: str = ".") -> List[str]:
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        target = self._resolve_path(path)
        results = []
        
        for root, dirs, files in os.walk(target):
            for filename in files:
                if filename.lower().endswith(extension.lower()):
                    full_path = Path(root) / filename
                    results.append(str(full_path.relative_to(self.root_path)))
        
        return results
    
    def count_files(self, path: str = ".", pattern: str = "*") -> Dict[str, int]:
        target = self._resolve_path(path)
        
        counts = {
            "files": 0,
            "directories": 0,
            "total_size": 0
        }
        
        for root, dirs, files in os.walk(target):
            counts["directories"] += len(dirs)
            
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    counts["files"] += 1
                    full_path = Path(root) / filename
                    try:
                        counts["total_size"] += full_path.stat().st_size
                    except Exception:
                        continue
        
        return counts
    
    def _resolve_path(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.root_path / p
        return p.resolve()
    
    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
