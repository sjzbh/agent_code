# Virtual Software Company 架构文档

## 概述

Virtual Software Company 是一个基于 SOP (标准作业程序) 的多智能体流水线架构，实现了角色原子化，将传统的单体 Worker 模式拆分为多个专业化角色。

## 架构组件

### 1. 角色原子化 (Role Atomization)

#### Architect (架构师)
- 职责：负责系统设计和架构，不写代码
- 输出：`design.md` 文件，包含文件结构和接口定义
- 位于：`roles/architect.py`

#### Coder (工程师)
- 职责：负责代码实现，严格遵循设计文档
- 位于：`roles/coder.py`

#### TechLead (技术主管)
- 职责：负责代码审查，有权驳回 Coder 的代码
- 实现：`Review Loop` 机制
- 位于：`roles/techlead.py`

#### QA_Engineer (测试工程师)
- 职责：编写测试用例，进行破坏性测试
- 位于：`roles/qa_engineer.py`

### 2. SOP 状态图 (SOP State Graph)

工作流程：
```
PM (需求) -> Architect (设计) -> Coder (开发) <-> TechLead (审查) -> QA (测试) -> Auditor (验收)
```

调度器：`sop_engine/scheduler.py`
- 基于图的调度器
- 每个节点产出标准化的 Artifact (交付物)

### 3. 进化记忆 (Evolutionary Memory)

- 位于：`memory/evolutionary_memory.py`
- 维护 `knowledge_base.json`
- 记录历史报错和修复方案
- 所有 Agent 在任务开始前读取知识库

### 4. 测试驱动开发 (TDD Workflow)

- 位于：`company/tdd_workflow.py`
- 强制 TDD 流程：QA 工程师在 Coder 写代码前生成测试用例
- Runner 判定标准：通过所有 QA 测试用例

### 5. 环境沙箱化 (Sandbox Isolation)

- 位于：`company/runner.py`
- 强化沙箱机制，在临时 venv 中运行代码
- 禁止使用 `--break-system-packages`
- 确保环境隔离

## 文件目录结构

```
agent_code/
├── main.py                     # 主入口点 - 虚拟软件公司
├── roles/                      # 角色原子化模块
│   ├── __init__.py
│   ├── architect.py           # 架构师角色
│   ├── coder.py              # 工程师角色
│   ├── techlead.py           # 技术主管角色
│   └── qa_engineer.py        # 测试工程师角色
├── sop_engine/                # SOP引擎
│   ├── __init__.py
│   └── scheduler.py          # SOP状态图调度器
├── memory/                    # 进化记忆模块
│   ├── __init__.py
│   └── evolutionary_memory.py # 进化记忆实现
├── company/                   # 公司级组件
│   ├── __init__.py
│   ├── tdd_workflow.py       # TDD工作流
│   ├── runner.py             # 沙箱化运行器
│   └── auditor.py            # 审计员
├── config/                    # 配置模块
├── utils/                     # 工具函数
├── prompts/                   # 提示词模板
└── knowledge_base.json        # 知识库文件
```

## 核心特性

1. **角色专业化**：每个角色职责单一，专业性强
2. **流程标准化**：SOP驱动，确保质量一致性
3. **记忆学习**：进化记忆避免重复犯错
4. **测试先行**：TDD确保代码质量
5. **环境隔离**：沙箱化运行保障系统安全
6. **审查循环**：TechLead审查机制保证代码规范

## 使用方法

```bash
# 交互模式
python main.py

# 命令行模式
python main.py "创建一个简单的计算器程序"
```