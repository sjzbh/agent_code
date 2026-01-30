# Virtual Software Company - 项目架构文档

## 概述
这是一个基于 SOP (Standard Operating Procedure) 驱动的多智能体流水线架构，实现了角色原子化，将传统的单体 Worker 模式拆分为多个专业化角色。

## 目录结构

```
agent_code/                           # 项目根目录
├── main.py                          # 主入口点 - 虚拟软件公司
├── requirements.txt                 # 项目依赖
├── .env                            # 环境变量配置文件
├── VIRTUAL_COMPANY_ARCHITECTURE.md # 架构文档
├── knowledge_base.json             # 知识库文件
├── legacy_archive/                 # 旧文件归档目录
│   └── v1_monolith/               # V1单体架构归档
│       ├── main_old.py            # 旧版主入口
│       ├── worker.py              # 旧版Worker
│       ├── manager.py             # 旧版Manager
│       └── auditor.py             # 旧版Auditor
├── config/                         # 配置模块
│   ├── __init__.py
│   ├── settings.py                # 项目设置
│   └── ai_client.py               # AI客户端管理
├── roles/                          # 角色原子化模块
│   ├── __init__.py
│   ├── architect.py               # 架构师角色逻辑
│   ├── coder.py                   # 工程师角色逻辑
│   ├── techlead.py                # 技术主管角色逻辑
│   ├── qa_engineer.py             # 测试工程师角色逻辑
│   ├── project_manager.py         # 项目经理角色逻辑
│   ├── evolution_officer.py       # 进化官角色逻辑
│   ├── auditor.py                 # 审计员角色逻辑
│   ├── sysadmin.py                # 系统管理员角色逻辑
│   └── prompts/                   # 角色专用提示词
│       ├── architect.yaml         # 架构师提示词模板
│       ├── coder.yaml             # 工程师提示词模板
│       ├── techlead.yaml          # 技术主管提示词模板
│       ├── qa_engineer.yaml       # 测试工程师提示词模板
│       ├── project_manager.yaml   # 项目经理提示词模板
│       ├── evolution_officer.yaml # 进化官提示词模板
│       ├── auditor.yaml           # 审计员提示词模板
│       └── sysadmin.yaml          # 系统管理员提示词模板
├── sop_engine/                     # SOP引擎
│   ├── __init__.py
│   └── scheduler.py               # SOP状态图调度器
├── memory/                         # 进化记忆模块
│   ├── __init__.py
│   └── evolutionary_memory.py     # 进化记忆实现
├── company/                        # 公司级组件
│   ├── __init__.py
│   └── tdd_workflow.py            # TDD工作流
├── controller/                     # 控制器模块
│   ├── __init__.py
│   └── main.py                   # 公司控制器主入口
├── utils/                          # 工具函数
│   └── __init__.py
└── state/                          # 状态管理
    └── __init__.py
```

## 核心特性

### 1. 角色原子化 (Role Atomization)
- **ProjectManager (项目经理)**: 负责将用户需求转化为结构化PRD
- **Architect (架构师)**: 负责系统设计和架构，输出 `design.md`
- **Coder (工程师)**: 负责代码实现，严格遵循 `design.md`
- **TechLead (技术主管)**: 负责代码审查，有权驳回 Coder 的代码
- **Runner (运行工程师)**: 负责在隔离环境中安全运行代码
- **SysAdmin (系统管理员)**: 负责环境管理和问题解决
- **QA_Engineer (测试工程师)**: 负责编写测试用例和质量保证
- **EvolutionOfficer (进化官)**: 负责分析执行日志并提取知识
- **Auditor (审计员)**: 负责最终验收

### 2. SOP 状态图 (SOP State Graph)
- 实现基于图的调度器
- 定义流转规则：`ProjectManager -> Architect -> Coder <-> TechLead -> Runner -> SysAdmin -> QA -> EvolutionOfficer -> Auditor`
- 每个节点产出标准化的 Artifact

### 3. 进化记忆 (Evolutionary Memory)
- 创建 `knowledge_base.json` 存储历史错误和解决方案
- 所有 Agent 在任务开始前读取知识库
- 避免重复犯错

### 4. 测试驱动开发 (TDD Workflow)
- 强制执行 TDD 流程：测试用例在代码实现前生成
- Runner 判定标准为"通过 QA 的所有测试用例"

### 5. 环境沙箱化 (Sandbox Isolation)
- 强化沙箱机制，在临时 venv 中运行代码
- 禁止使用 `--break-system-packages`
- 确保环境隔离

## 使用方法

```bash
# 安装依赖
pip install -r requirements.txt

# 配置API密钥
# 编辑 .env 文件，填入您的API密钥

# 交互模式运行
python main.py

# 命令行模式运行
python main.py "创建一个简单的计算器程序"
```

## API 配置

API 配置入口点：
- 主配置：`config.py`
- 新配置系统：`config/`
- 环境变量：`.env`

需要配置以下密钥：
- `GEMINI_API_KEY`: Google Gemini API密钥
- `LLM_API_KEY`: LLM服务API密钥
- `LLM_BASE_URL`: LLM服务API端点URL