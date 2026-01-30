# Virtual Software Company - Next Generation (V2.1)
## Project Chrysalis - Self-Evolving Architecture

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Project Chrysalis is an advanced AI-powered software development system that implements a SOP (Standard Operating Procedure) driven multi-agent architecture. The system features 8 specialized roles that work together to deliver high-quality software solutions with self-evolution capabilities.

## 🚀 Features

- **8 Specialized Roles**: ProjectManager, Architect, Coder, TechLead, SysAdmin, QAEngineer, Auditor, EvolutionOfficer
- **SOP-Driven Workflow**: Standardized procedures ensure consistent quality
- **Self-Evolution**: Continuous learning and improvement through experience base
- **Linux-Optimized**: Performance tuned for Linux environments
- **Robust Error Handling**: Multiple fallback strategies and error recovery
- **Environment Isolation**: Secure sandboxed execution

## 🏗️ Architecture

The system implements a role-atomized architecture with standardized workflows:

```
PM Requirements → Architect Design → Coder Implementation ↔ TechLead Review → 
SysAdmin Execution → QA Testing → Auditor Acceptance → Evolution Analysis → Completed
```

Each role specializes in a specific aspect of software development:
- **ProjectManager**: Requirement analysis and PRD generation
- **Architect**: System design and interface specification
- **Coder**: Code implementation following designs
- **TechLead**: Code review and quality assurance
- **SysAdmin**: Environment management and code execution
- **QAEngineer**: Test case creation and quality validation
- **Auditor**: Final acceptance testing
- **EvolutionOfficer**: Post-project analysis and knowledge extraction

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/sjzbh/agent_code.git
cd agent_code

# Install dependencies
pip install -r requirements.txt

# Set up your API keys in .env file
cp .env.example .env
# Edit .env with your Gemini and LLM API keys
```

## 🚀 Usage

```bash
python main.py
```

Follow the prompts to enter your project requirements and watch the virtual software company work!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 🧬 Self-Evolution

The system continuously learns from each project execution:
1. EvolutionOfficer analyzes execution logs
2. Extracts "Error -> Solution" pairs
3. Updates the knowledge base
4. Applies learned fixes in future iterations

This creates a self-improving system that gets better with each iteration.