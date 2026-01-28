# 多AI协作工具项目概述

## 项目简介
这是一个强大的多AI角色协作系统，支持命令行和可视化两种操作模式。项目通过多个AI角色的协作来完成用户提出的需求，实现了自动化任务规划、代码生成、执行和审计等功能。

## 核心功能
- **多AI角色协作**: 包括ProjectManager、Coder、Runner、Tech Lead、Auditor等角色
- **自动任务规划**: 将复杂需求拆解为具体可执行任务
- **代码执行与审计**: 生成代码、执行并审计结果
- **自我进化能力**: 支持代码自动优化和改进
- **多AI提供商支持**: 兼容Gemini和OpenAI接口
- **智能错误处理**: 自动检测和修复常见错误

## 两种操作模式
1. **命令行模式**: 传统REPL交互，功能完整
2. **可视化模式**: 基于Streamlit的聊天界面，操作简便

## 项目结构

```
ai-collaboration-tool/
├── main.py           # 命令行模式入口
├── app.py            # 可视化模式入口
├── manager.py        # 项目经理模块
├── worker.py         # 工作者模块（Coder、Runner、Tech Lead）
├── auditor.py        # 审计员模块
├── evaluator.py      # 评估官模块（用于进化模式）
├── sandbox.py        # 沙箱管理模块
├── config.py         # 配置管理
├── utils.py          # 工具函数
├── prompts.py        # AI角色提示词
├── requirements.txt  # 依赖包列表
├── .env.example      # 环境变量模板
└── .gitignore        # Git忽略文件
```

## AI角色说明

| 角色 | 职责 | 模块 |
|------|------|------|
| ProjectManager | 任务规划和管理 | manager.py |
| Coder | 生成代码或命令 | worker.py |
| Runner | 执行代码或命令 | worker.py |
| Tech Lead | 分析错误并提供修复建议 | worker.py |
| Auditor | 审计执行结果 | auditor.py |
| Evaluator | 评估代码改进 | evaluator.py |

## 核心工作流程
1. 用户输入需求
2. ProjectManager将需求拆解为具体任务
3. Worker(Coder)生成代码或命令
4. Worker(Runner)执行代码或命令
5. 如果执行失败，Worker(Tech Lead)分析错误并提供修复建议
6. Auditor审计执行结果
7. 根据审计结果决定是否继续或调整计划

## 进化模式
使用进化模式可以自动优化和改进代码：
- 初始化沙箱环境
- 读取原代码
- 生成改进代码
- 在沙箱中测试
- 评估改进效果
- 部署通过评估的代码

## 技术栈
- Python 3.x
- Google Generative AI SDK
- OpenAI SDK
- Streamlit (可视化界面)
- Rich (命令行美化)
- Python-dotenv (环境变量管理)