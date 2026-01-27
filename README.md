# 多AI协作工具

一个强大的多AI角色协作系统，支持命令行和可视化两种操作模式。

## 🚀 功能特性

### 核心功能
- **多AI角色协作**: ProjectManager、Coder、Runner、Tech Lead、Auditor
- **自动任务规划**: 将复杂需求拆解为具体可执行任务
- **代码执行与审计**: 生成代码、执行并审计结果
- **自我进化能力**: 支持代码自动优化和改进
- **多AI提供商支持**: 兼容Gemini和OpenAI接口
- **智能错误处理**: 自动检测和修复常见错误

### 两种操作模式
1. **命令行模式**: 传统REPL交互，功能完整
2. **可视化模式**: 基于Streamlit的聊天界面，操作简便

## 📦 安装说明

### 1. 克隆仓库
```bash
git clone <repository-url>
cd ai-collaboration-tool
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
复制 `.env.example` 文件为 `.env` 并填写API密钥：
```bash
cp .env.example .env
# 编辑 .env 文件，添加您的API密钥
```

## 🎯 使用指南

### 命令行模式
```bash
python main.py
```

**使用示例**:
- 输入需求: `创建一个Python脚本，计算1到100的和`
- 进化模式: `evolve worker.py 增加重试机制`
- 退出工具: `exit`

### 可视化模式
```bash
streamlit run app.py
```

**使用步骤**:
1. 在浏览器中打开生成的URL
2. 在聊天框中输入您的需求
3. 查看任务规划结果
4. 切换到命令行模式执行任务

## 🔧 项目结构

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

## 🤖 AI角色说明

| 角色 | 职责 | 模块 |
|------|------|------|
| ProjectManager | 任务规划和管理 | manager.py |
| Coder | 生成代码或命令 | worker.py |
| Runner | 执行代码或命令 | worker.py |
| Tech Lead | 分析错误并提供修复建议 | worker.py |
| Auditor | 审计执行结果 | auditor.py |
| Evaluator | 评估代码改进 | evaluator.py |

## 🌟 进化模式

使用进化模式可以自动优化和改进代码：

```bash
# 命令格式
evolve <目标文件> <改进需求>

# 示例
evolve worker.py 增加重试机制
evolve manager.py 优化任务规划算法
```

**进化流程**:
1. 初始化沙箱环境
2. 读取原代码
3. 生成改进代码
4. 在沙箱中测试
5. 评估改进效果
6. 部署通过评估的代码

## 📝 版本历史

- **v1.0.0**: 初始版本，支持命令行模式和基本AI协作
- **v1.1.0**: 添加进化模式，支持代码自动优化
- **v1.2.0**: 添加可视化模式，基于Streamlit实现聊天界面

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
