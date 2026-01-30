#!/usr/bin/env python3
"""
Test script to trigger the self-evolution mechanism
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sop_engine.self_evolution import SelfEvolutionEngine

def test_evolution():
    print("🔬 开始测试自我进化机制...")
    
    # Create an instance of the evolution engine
    engine = SelfEvolutionEngine()
    
    # Mock source code and insights for testing
    mock_source_code = """
# Mock source code for testing
class MockAgent:
    def __init__(self):
        self.name = "Mock Agent"
    
    def work(self):
        return "Work completed"
"""
    
    mock_insights = {
        "patterns": ["linux environment", "error handling"],
        "error_solution_pairs": [
            {"error": "FileNotFoundError", "solution": "Add file existence check"},
            {"error": "PermissionError", "solution": "Check file permissions"}
        ],
        "recent_insights": ["Linux optimization", "Error immunity"]
    }
    
    print("🔄 触发下一代代理生成...")
    success = engine.generate_next_gen_agent(mock_source_code, mock_insights)
    
    if success:
        print("✅ 下一代代理生成成功！")
        
        # Verify that the directory was created
        next_gen_path = engine.next_gen_path
        if os.path.exists(next_gen_path):
            print(f"📁 目录已创建: {next_gen_path}")
            
            # List contents
            import subprocess
            result = subprocess.run(['find', str(next_gen_path), '-type', 'f'], 
                                  capture_output=True, text=True)
            files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            print(f"📄 生成的文件数量: {len(files)}")
            
            for file in files[:10]:  # Show first 10 files
                print(f"   - {file}")
            
            if len(files) > 10:
                print(f"   ... 还有 {len(files) - 10} 个文件")
        else:
            print(f"❌ 目录未创建: {next_gen_path}")
    else:
        print("❌ 下一代代理生成失败！")

if __name__ == "__main__":
    test_evolution()