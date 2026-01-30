"""
Evolution Officer Role - Responsible for analyzing execution logs and extracting insights
"""
import json
from typing import Dict, Any
from config import WORKER_CONFIG
from utils import safe_json_parse, call_llm, load_prompt
from rich.console import Console
from memory.evolutionary_memory import evolutionary_memory

console = Console()

class EvolutionOfficer:
    """
    Evolution Officer Role - analyzes execution logs and extracts insights for knowledge base
    """
    
    def __init__(self, model_name="gemini-1.5-pro"):
        """
        Initialize Evolution Officer role
        Args:
            model_name: Model name, defaults to "gemini-1.5-pro"
        """
        self.model_name = model_name
        self.evo_config = WORKER_CONFIG

    def analyze_execution_log(self, execution_log: str) -> Dict[str, Any]:
        """
        Analyze execution log and extract insights
        Args:
            execution_log: Full execution log to analyze
        Returns:
            Analysis results with extracted insights
        """
        console.print("[bold blue]Evolution Officer 正在分析执行日志...[/bold blue]")
        
        # Build the analysis prompt
        prompt = f"""
        你是 [Virtual Software Company] 的进化官 (Evolution Officer)。
        你的职责是：在项目结束后分析执行日志，提取有价值的经验教训并存入知识库。
        
        当前阶段：[执行日志分析]
        执行日志：
        {execution_log}
        
        请分析执行日志，提取以下信息：
        1. 遾现的问题和错误
        2. 采取的解决方案
        3. 成功的经验和最佳实践
        4. 可避类似问题的建议
        
        以标准格式返回Error->Solution对，用于知识库存储。
        """
        
        if self.evo_config['client']:
            raw_response = call_llm(self.evo_config, prompt)
            analysis_result = raw_response  # Using safe_json_parse to handle any format issues
            
            # Parse the analysis result
            analysis_data = safe_json_parse(analysis_result, {})
            console.print("[bold green]执行日志分析完成！[/bold green]")
            
            return {
                "success": True,
                "analysis": analysis_data,
                "raw_response": analysis_result
            }
        else:
            console.print("[bold red]错误: Evolution Officer AI 未初始化[/bold red]")
            return {
                "success": False,
                "analysis": {},
                "raw_response": "",
                "error": "Evolution Officer AI 未初始化"
            }

    def extract_insights(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract insights from analysis result
        Args:
            analysis_result: Result from log analysis
        Returns:
            Extracted insights in standard format
        """
        console.print("[bold blue]Evolution Officer 正在提取洞察...[/bold blue]")
        
        # For now, return the analysis result as insights
        # In a real implementation, this would further process the analysis
        return {
            "success": True,
            "insights": analysis_result,
            "raw_response": str(analysis_result)
        }

    def store_insights(self, insights: Dict[str, Any], project_context: str = ""):
        """
        Store insights in the knowledge base
        Args:
            insights: Insights to store
            project_context: Context of the project for reference
        """
        console.print("[bold blue]Evolution Officer 正在存储洞察到知识库...[/bold blue]")
        
        # Extract error-solution pairs from insights
        error_solution_pairs = insights.get('analysis', {}).get('error_solution_pairs', [])
        
        for pair in error_solution_pairs:
            error = pair.get('error', '')
            solution = pair.get('solution', '')
            context = pair.get('context', '') or project_context
            
            # Add to evolutionary memory
            evolutionary_memory.add_error_solution_pair(error, solution, context)
        
        # Also store other types of insights
        other_insights = insights.get('analysis', {}).get('other_insights', [])
        for insight in other_insights:
            description = insight.get('description', '')
            solution = insight.get('solution', '')
            evolutionary_memory.add_solution(solution, description)
        
        console.print("[bold green]洞察已成功存储到知识库！[/bold green]")
    
    def trigger_post_project_analysis(self, execution_log: str, project_context: str = "") -> bool:
        """
        Trigger full post-project analysis (main method called after project ends)
        Args:
            execution_log: Full execution log
            project_context: Context of the project
        Returns:
            Success status
        """
        console.print("[bold blue]Evolution Officer 启动项目后分析...[/bold blue]")
        
        # Step 1: Analyze execution log
        analysis_result = self.analyze_execution_log(execution_log)
        
        if not analysis_result['success']:
            console.print("[bold red]执行日志分析失败[/bold red]")
            return False
        
        # Step 2: Extract insights
        insight_result = self.extract_insights(analysis_result['analysis'])
        
        if not insight_result['success']:
            console.print("[bold red]洞察提取失败[/bold red]")
            return False
        
        # Step 3: Store insights in knowledge base
        self.store_insights(insight_result['insights'], project_context)
        
        console.print("[bold green]项目后分析完成，洞察已存储！[/bold green]")
        return True