# 引入新模块
from sandbox import SandboxManager
from evaluator import EvaluatorAgent
# ... 其他引入保持不变

def main():
    # ... 初始化保持不变
    sandbox = SandboxManager()
    evaluator = EvaluatorAgent()
    
    while True:
        # ... 获取输入部分保持不变 ...
        
        # === 新增：进化模式入口 ===
        if user_input.startswith("evolve "):
            target_file = user_input.split(" ")[1] # 例如: evolve worker.py 增加重试机制
            requirement = " ".join(user_input.split(" ")[2:])
            
            console.print(Panel(f"目标文件: {target_file}\n需求: {requirement}", title="[bold gold1]启动自我进化流程[/bold gold1]", border_style="gold1"))
            
            # 1. 初始化沙箱
            if not sandbox.init_sandbox():
                continue
                
            # 2. 读取原代码
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    original_code = f.read()
            except FileNotFoundError:
                console.print(f"[red]文件 {target_file} 不存在！[/red]")
                continue

            # 3. 让 Coder 生成新代码 (注意：这里我们复用 worker，但给它进化专用的 Prompt)
            # 这里为了简单，我们直接构造一个 Prompt 传给 coder
            evolution_task = f"请重构 {target_file}。\n原代码如下：\n{original_code}\n\n改进需求：{requirement}\n\n请遵循 EVOLUTION_PROMPT 的规则。"
            
            console.print("[cyan]正在生成进化版代码...[/cyan]")
            new_code = worker.coder(evolution_task) # 你可能需要稍微修改 worker.coder 让它接受自定义 System Prompt，或者直接这样传也行
            
            # 4. 写入沙箱
            sandbox_file_path = os.path.join(sandbox.sandbox_dir, target_file)
            with open(sandbox_file_path, 'w', encoding='utf-8') as f:
                f.write(new_code)
                
            # 5. 沙箱验证 (尝试运行代码)
            # 如果是库文件(如worker.py)，我们可能需要运行 main.py 来测试，或者运行一个专门生成的测试脚本
            # 这里做一个简单的“语法检查”和“导入测试”
            console.print("[yellow]正在沙箱中进行冒烟测试...[/yellow]")
            check_cmd = f"{sys.executable} -c 'import {target_file.replace('.py', '')}'" # 尝试导入
            success, stdout, stderr = sandbox.run_in_sandbox(check_cmd)
            
            test_logs = f"Exit Code: {0 if success else 1}\nStdout: {stdout}\nStderr: {stderr}"
            
            if not success:
                console.print("[bold red]沙箱测试失败！新代码存在严重错误，进化终止。[/bold red]")
                console.print(stderr)
                continue
                
            # 6. 评估官介入
            decision_json = evaluator.evaluate_improvement(original_code, new_code, test_logs, requirement)
            try:
                decision = json.loads(decision_json)
                console.print(Panel(f"决策: {decision['decision']}\n评分: {decision.get('score')}\n理由: {decision['reason']}", title="评估报告"))
                
                if decision['decision'] == "ACCEPT":
                    # 7. 部署
                    sandbox.deploy_file(target_file)
                    console.print("[bold green]进化成功！代码已更新。[/bold green]")
                else:
                    console.print("[bold red]进化被拒绝。[/bold red]")
                    
            except Exception as e:
                console.print(f"[red]评估结果解析失败: {e}[/red]")
            
            continue
            
        # ... 原有的普通任务流程保持不变 ...