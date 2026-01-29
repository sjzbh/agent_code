# 基于状态机的工业级Agent架构设计文档

## 架构概述

本架构采用状态机模式，将原来线性的脚本式执行流程重构为基于状态驱动的工业级Agent系统。该架构具备以下特点：

- **状态全知**：所有组件共享统一的状态对象
- **智能路由**：根据状态和审计结果动态决定下一步行动
- **HITL机制**：当系统无法自动解决问题时，提供人工介入接口
- **死循环防护**：防止无限重试和递归
- **环境自适应**：自动检测和适配运行环境

## 核心组件

### 1. AgentState (状态管理)
```python
class AgentState:
    current_task_index: int      # 当前任务进度
    retry_count: int             # 当前重试次数
    max_retries: int = 3         # 最大重试阈值
    execution_history: List[Dict] # 执行历史
    # ... 其他状态属性
```

### 2. Router (智能路由)
```python
def router(state: AgentState, audit_result: Dict) -> Tuple[str, str]:
    # 根据状态和审计结果决定下一步行动
    # 返回 (action, reason)
```

路由逻辑：
- **PASS**: 任务通过 → 重置retry_count → 索引+1 → 下一任务
- **RETRY**: 逻辑错误 → retry_count < 3 → 保持索引 → 触发重试
- **HITL**: 熔断/系统错误 → 进入HITL模式

### 3. HITL (人工介入)
提供三种交互选项：
- Force Pass: 强制通过当前任务
- Retry: 清空重试计数后重试
- Exit: 保存状态并退出

### 4. EnhancedWorker (环境自适应)
- 自动检测Python可执行文件 (python/python3)
- 支持错误反馈机制
- 集成Tech Lead分析功能

## 状态流转图

```
[Planning] → [Execution] → [Testing] → [Deployment] → [Auditing]
                    ↓
               [Audit Result]
                    ↓
            ┌─────┴─────┐
            │           │
         [PASS]    [FAIL/ERROR]
            │           │
            │        [Router]
            │           │
            │    ┌─────┼─────┐
            │    │     │     │
            │ [NEXT] [RETRY] [HITL]
            │    │     │     │
            ↓    ↓     ↓     ↓
        [Success] [Continue] [Manual Intervention]
```

## 关键改进点

### 1. 状态管理
- 废弃局部变量，使用统一的AgentState对象
- 所有组件共享状态，提高一致性

### 2. 错误处理
- 实现分层错误处理机制
- 防止无限循环和递归
- 提供明确的错误上下文

### 3. 可扩展性
- 模块化设计，易于扩展新功能
- 标准化的接口设计
- 详细的执行历史记录

### 4. 可靠性
- 重试机制带有限制
- 环境自适应能力
- 人工介入兜底机制

## 使用场景

此架构特别适用于：
- 需要长期运行的自动化任务
- 对可靠性要求高的生产环境
- 需要人工监督的半自动化流程
- 复杂的多步骤工作流

## 总结

重构后的架构显著提升了系统的健壮性、可维护性和可扩展性，符合工业级标准。通过状态机模式，系统能够在复杂的执行环境中做出智能决策，并在出现问题时提供适当的处理机制。