"""
Evolution Officer Role - Responsible for analyzing execution logs and extracting insights
"""
import json
from typing import Dict, Any
from config import settings, ai_client_manager
from utils import clean_json_text, call_llm, load_prompt, safe_json_parse
from rich.console import Console
from memory.evolutionary_memory import evolutionary_memory
from sop_engine.self_evolution import SelfEvolutionEngine

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
        self.evo_config = ai_client_manager.get_config("auto") or {
            "client": None,
            "type": "none",
            "model": "none"
        }
        self.prompts = load_prompt("roles/prompts/evolution_officer.yaml")
        self.memory = evolutionary_memory
        self.evolver = SelfEvolutionEngine()

    def analyze_execution_log(self, execution_log: str) -> Dict[str, Any]:
        """
        Analyze execution log and extract insights
        Args:
            execution_log: Full execution log to analyze
        Returns:
            Analysis results with extracted insights
        """
        console.print("[bold blue]Evolution Officer 正在分析执行日志...[/bold blue]")
        
        # Format the prompt using the YAML template
        prompt_template = self.prompts['log_analysis_task']
        prompt = prompt_template.format(
            execution_log=execution_log
        )
        
        if self.evo_config['client']:
            raw_response = call_llm(self.evo_config, prompt)
            analysis_result = clean_json_text(raw_response)
            
            # Parse the analysis result using safe parser
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
        
        # Format the prompt using the YAML template
        prompt_template = self.prompts['knowledge_extraction_task']
        prompt = prompt_template.format(
            analysis_result=str(analysis_result)
        )
        
        if self.evo_config['client']:
            raw_response = call_llm(self.evo_config, prompt)
            insight_result = clean_json_text(raw_response)
            
            # Parse the insight result
            try:
                insight_data = json.loads(insight_result)
                console.print("[bold green]洞察提取完成！[/bold green]")
                
                return {
                    "success": True,
                    "insights": insight_data,
                    "raw_response": insight_result
                }
            except json.JSONDecodeError:
                console.print("[bold yellow]洞察提取结果解析失败，返回原始内容[/bold yellow]")
                return {
                    "success": False,
                    "insights": {},
                    "raw_response": insight_result,
                    "error": "洞察提取结果解析失败"
                }
        else:
            console.print("[bold red]错误: Evolution Officer AI 未初始化[/bold red]")
            return {
                "success": False,
                "insights": {},
                "raw_response": "",
                "error": "Evolution Officer AI 未初始化"
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
        error_solution_pairs = insights.get('error_solution_pairs', [])
        
        for pair in error_solution_pairs:
            error = pair.get('error', '')
            solution = pair.get('solution', '')
            context = pair.get('context', '') or project_context
            
            # Add to evolutionary memory
            self.memory.add_error_solution_pair(error, solution, context)
        
        # Also store other types of insights
        other_insights = insights.get('other_insights', [])
        for insight in other_insights:
            description = insight.get('description', '')
            solution = insight.get('solution', '')
            self.memory.add_solution(solution, description)
        
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

        # Check if conditions for self-evolution are met
        if self.should_self_evolve():
            console.print("[bold magenta]触发自我进化条件，启动系统重写...[/bold magenta]")
            self.initiate_self_evolution(project_context)

        return True

    def should_self_evolve(self) -> bool:
        """
        Determine if self-evolution should be triggered
        Returns:
            Boolean indicating if self-evolution should occur
        """
        # Check for repeated patterns in the knowledge base that suggest optimization
        recent_insights = self.memory.get_recent_insights(10)  # Get last 10 insights

        # Count specific patterns that suggest evolution
        linux_specific_issues = 0
        error_patterns = 0
        unused_component_mentions = 0

        for insight in recent_insights:
            insight_str = str(insight).lower()
            if 'linux' in insight_str and ('permission' in insight_str or 'path' in insight_str or 'environment' in insight_str):
                linux_specific_issues += 1
            if 'error' in insight_str and 'solution' in insight_str:
                error_patterns += 1
            if 'unused' in insight_str or 'never called' in insight_str:
                unused_component_mentions += 1

        # If we have enough signals, trigger evolution
        return linux_specific_issues >= 2 or error_patterns >= 3 or unused_component_mentions >= 1

    def initiate_self_evolution(self, project_context: str = ""):
        """
        Initiate the self-evolution process
        Args:
            project_context: Context of the triggering project
        """
        console.print("[bold magenta]开始自我进化进程...[/bold magenta]")

        # Gather all necessary information for evolution
        knowledge_base = self.memory.get_full_knowledge_base()
        system_source_code = self._get_system_source_code()

        # Perform self-evolution
        evolution_result = self.perform_self_evolution(
            source_code=system_source_code,
            insights=knowledge_base,
            project_context=project_context
        )

        if evolution_result['success']:
            console.print("[bold green]自我进化成功完成！[/bold green]")
        else:
            console.print(f"[bold red]自我进化失败: {evolution_result.get('error', 'Unknown error')}[/bold red]")

    def _get_system_source_code(self) -> str:
        """
        Get the system's source code for evolution
        Returns:
            String containing system source code
        """
        import os
        source_code = ""

        # Collect source code from key directories
        for root, dirs, files in os.walk(".", topdown=True):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'sandbox', 'venv', 'node_modules']]

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            source_code += f"\n\n--- FILE: {file_path} ---\n{content}\n--- END OF {file_path} ---\n"
                    except Exception:
                        # Skip files that can't be read
                        continue

        return source_code

    def perform_self_evolution(self, source_code: str, insights: Dict[str, Any], project_context: str = "") -> Dict[str, Any]:
        """
        Perform the self-evolution process
        Args:
            source_code: Current system source code
            insights: Insights from knowledge base
            project_context: Context of the triggering project
        Returns:
            Evolution result
        """
        console.print("[bold magenta]Evolution Officer 正在执行自我重写...[/bold magenta]")

        # Use the SelfEvolutionEngine to generate the next generation agent
        success = self.evolver.generate_next_gen_agent(source_code, insights)

        if success:
            # Record the evolution in the knowledge base
            self.memory.add_solution(
                solution=f"Generated next-gen agent based on context: {project_context}",
                description="Self-evolution successfully generated next generation agent"
            )

            console.print("[bold green]自我重写成功完成！[/bold green]")
            return {
                "success": True,
                "evolution_result": "Next generation agent generated successfully",
                "raw_response": "Self-evolution completed"
            }
        else:
            console.print("[bold red]自我重写失败[/bold red]")
            return {
                "success": False,
                "evolution_result": {},
                "raw_response": "",
                "error": "Self-evolution failed"
            }