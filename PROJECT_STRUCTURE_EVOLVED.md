# Virtual Software Company - Next Generation (V2.1)
# Project Chrysalis - Self-Evolving Architecture

## Overview
This is the next-generation self-evolving agent system based on the experience gained from V2.0. The system has undergone environmental adaptation and error immunity enhancement to become more robust and efficient.

## Key Improvements

### 1. Role Atomization (角色原子化)
- **ProjectManager**: Converts user requirements to structured PRD
- **Architect**: System design and architecture
- **Coder**: Code implementation
- **TechLead**: Code review and quality assurance
- **SysAdmin**: Code execution and environment management
- **QAEngineer**: Testing and quality assurance
- **Auditor**: Final acceptance testing
- **EvolutionOfficer**: Post-project analysis and knowledge extraction

### 2. SOP State Graph (SOP状态图)
- Implemented graph-based scheduler
- Defined flow rules: `PM -> Architect -> Coder <-> TechLead -> SysAdmin -> QA -> Auditor -> Evolution`
- Each node produces standardized artifacts

### 3. Evolutionary Memory (进化记忆)
- Created `knowledge_base.json` to store historical errors and solutions
- EvolutionOfficer analyzes execution logs and extracts "Error->Solution" pairs

### 4. TDD Workflow (测试驱动开发)
- QA_Engineer creates test cases before or alongside code implementation
- Runner's success criterion is "passing all QA test cases"

### 5. Environment Sandboxing (环境沙箱化)
- Enhanced SysAdmin role with environment management
- Linux environment optimization with hardcoded paths

## Architecture Components

### Core Roles
1. **ProjectManager**: Converts user requirements to structured PRD
2. **Architect**: Designs system architecture and interfaces
3. **Coder**: Implements code based on design specifications
4. **TechLead**: Reviews code and enforces quality standards
5. **SysAdmin**: Manages environments and runs code (Linux-optimized)
6. **QAEngineer**: Creates and executes test cases
7. **Auditor**: Performs final acceptance testing
8. **EvolutionOfficer**: Analyzes execution logs and evolves the system

### Engine Components
- **SOP Engine**: Manages workflow between roles
- **Evolutionary Memory**: Stores error-solution pairs for continuous improvement
- **Utils**: Common utilities with robust JSON handling

## Self-Evolution Process

The system continuously learns from each project execution:
1. EvolutionOfficer analyzes execution logs
2. Extracts "Error -> Solution" pairs
3. Updates the knowledge base
4. Applies learned fixes in future iterations

## Directory Structure

```
agent_code/
├── main.py                    # Entry point for the next-generation company
├── requirements.txt           # Dependencies including pygame, requests for pre-installation
├── README.md                 # Project documentation
├── config/                   # Configuration module
│   └── __init__.py
│   └── config.py             # Linux-optimized configuration
├── roles/                    # Specialized role implementations
│   ├── __init__.py
│   ├── architect.py          # System designer (Linux-optimized)
│   ├── coder.py              # Code implementer (Linux-optimized)
│   ├── techlead.py           # Code reviewer (Linux-optimized)
│   ├── qa_engineer.py        # Quality assurance (Linux-optimized)
│   ├── project_manager.py    # Requirement analyzer (Linux-optimized)
│   ├── auditor.py            # Final acceptance (Linux-optimized)
│   ├── sysadmin.py           # Environment manager (Linux-optimized)
│   ├── evolution_officer.py  # Self-evolution manager
│   └── prompts/              # Role-specific prompts
│       ├── architect.yaml
│       ├── coder.yaml
│       ├── techlead.yaml
│       ├── qa_engineer.yaml
│       ├── project_manager.yaml
│       ├── auditor.yaml
│       ├── sysadmin.yaml
│       └── evolution_officer.yaml
├── sop_engine/               # SOP state graph engine
│   ├── __init__.py
│   └── scheduler.py          # Workflow orchestrator
├── memory/                   # Evolutionary memory module
│   ├── __init__.py
│   └── evolutionary_memory.py # Experience base with error-immunity
├── utils/                    # Utility functions
│   ├── __init__.py
│   └── utils.py              # Safe JSON parsing and helpers
├── company/                  # Company-level components
│   ├── __init__.py
│   └── runner.py             # Linux-optimized code runner
├── controller/               # Main controller
│   ├── __init__.py
│   └── main.py               # Company lifecycle controller
└── sandbox_env/              # Sandbox environment
    └── next_gen/             # Next generation codebase
        ├── __init__.py
        └── ...
```

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the system
python main.py
```

## Environmental Adaptations Applied

Based on the experience base, the following adaptations have been made:
- Removed cross-platform compatibility checks (hard-coded for Linux)
- Added common dependencies to requirements.txt (pygame, requests)
- Implemented safe JSON parsing to handle malformed responses
- Enhanced error recovery mechanisms
- Preserved evolution officer functionality for continuous improvement