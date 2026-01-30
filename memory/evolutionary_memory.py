"""
Evolutionary Memory Module - Next Generation
Records historical errors and solutions with improved error handling
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from rich.console import Console

console = Console()

class EvolutionaryMemory:
    """Evolutionary Memory Module - records historical errors and solutions"""
    
    def __init__(self, knowledge_base_file: str = "knowledge_base.json"):
        self.knowledge_base_file = knowledge_base_file
        self.knowledge_base = self.load_knowledge_base()
    
    def load_knowledge_base(self) -> Dict[str, Any]:
        """Load knowledge base from file with error handling"""
        if os.path.exists(self.knowledge_base_file):
            try:
                with open(self.knowledge_base_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                console.print(f"[yellow]加载知识库失败: {e}, 创建新的知识库[/yellow]")
                return {"errors": [], "solutions": [], "patterns": [], "error_solution_pairs": []}
        else:
            # Create a new knowledge base
            return {"errors": [], "solutions": [], "patterns": [], "error_solution_pairs": []}
    
    def save_knowledge_base(self):
        """Save knowledge base to file with error handling"""
        try:
            with open(self.knowledge_base_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            console.print(f"[green]知识库已保存到 {self.knowledge_base_file}[/green]")
        except Exception as e:
            console.print(f"[red]保存知识库失败: {e}[/red]")
    
    def add_error_solution_pair(self, error: str, solution: str, context: str = ""):
        """Add an error-solution pair to the knowledge base"""
        entry = {
            "error": error,
            "solution": solution,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "id": len(self.knowledge_base["error_solution_pairs"])
        }
        
        self.knowledge_base["error_solution_pairs"].append(entry)
        console.print(f"[green]错误解决方案已记录: {error[:50]}...[/green]")
        self.save_knowledge_base()
    
    def add_solution(self, solution: str, description: str = ""):
        """Add a general solution to the knowledge base"""
        entry = {
            "solution": solution,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "id": len(self.knowledge_base["solutions"])
        }
        
        self.knowledge_base["solutions"].append(entry)
        console.print(f"[green]解决方案已记录: {description[:50]}...[/green]")
        self.save_knowledge_base()
    
    def add_pattern(self, pattern: str, description: str = "", solution: str = ""):
        """Add a pattern to the knowledge base"""
        entry = {
            "pattern": pattern,
            "description": description,
            "solution": solution,
            "timestamp": datetime.now().isoformat(),
            "id": len(self.knowledge_base["patterns"])
        }
        
        self.knowledge_base["patterns"].append(entry)
        console.print(f"[green]模式已记录: {description[:50]}...[/green]")
        self.save_knowledge_base()
    
    def search_by_error(self, error_query: str) -> List[Dict[str, Any]]:
        """Search for similar errors in the knowledge base"""
        results = []
        for entry in self.knowledge_base["error_solution_pairs"]:
            if error_query.lower() in entry["error"].lower():
                results.append(entry)
        return results
    
    def search_by_context(self, context_query: str) -> List[Dict[str, Any]]:
        """Search for entries by context"""
        results = []
        for entry in self.knowledge_base["error_solution_pairs"]:
            if context_query.lower() in entry.get("context", "").lower():
                results.append(entry)
        return results
    
    def get_common_solutions(self) -> List[Dict[str, Any]]:
        """Get commonly used solutions"""
        return self.knowledge_base["solutions"]
    
    def get_patterns(self) -> List[Dict[str, Any]]:
        """Get known patterns"""
        return self.knowledge_base["patterns"]
    
    def apply_solutions(self, error_context: str) -> List[str]:
        """Apply relevant solutions based on error context"""
        solutions = []
        
        # Search for similar errors
        error_matches = self.search_by_error(error_context)
        for match in error_matches:
            solutions.append(match["solution"])
        
        # Search by context
        context_matches = self.search_by_context(error_context)
        for match in context_matches:
            if match["solution"] not in solutions:
                solutions.append(match["solution"])
        
        # Add common solutions that might be relevant
        for solution_entry in self.get_common_solutions():
            if "linux" in error_context.lower() and "linux" in solution_entry.get("description", "").lower():
                solutions.append(solution_entry["solution"])
            elif "python" in error_context.lower() and "python" in solution_entry.get("description", "").lower():
                solutions.append(solution_entry["solution"])
        
        return solutions

# Global instance
evolutionary_memory = EvolutionaryMemory()