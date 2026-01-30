# Contributing to Virtual Software Company (Project Chrysalis)

We welcome contributions to the Virtual Software Company project! This document provides guidelines for contributing.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Code Standards](#code-standards)
4. [Architecture Overview](#architecture-overview)
5. [Submitting Changes](#submitting-changes)

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/agent_code.git
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Development Workflow

The Virtual Software Company follows a SOP (Standard Operating Procedure) driven multi-agent architecture:

### 1. Role Development
- Each role should be developed in the `roles/` directory
- Follow the existing pattern for role implementation
- Roles should have clear, single responsibilities

### 2. Prompt Engineering
- Prompts are stored in YAML format in `roles/prompts/`
- Use the standardized prompt structure
- Include evolutionary memory references where appropriate

### 3. Testing
- Add unit tests for new functionality
- Test the complete workflow with end-to-end scenarios
- Verify that the evolution officer properly captures insights

## Code Standards

### Python
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all classes and functions
- Keep functions focused and concise

### Architecture
- Maintain role atomization - each role should have a single, clear purpose
- Use standardized artifact formats between roles
- Preserve the evolution officer's ability to learn from execution logs
- Ensure all JSON parsing uses safe methods with fallbacks

## Architecture Overview

The system consists of 8 specialized roles:

```
PM Requirements → Architect Design → Coder Implementation ↔ TechLead Review → 
SysAdmin Execution → QA Testing → Auditor Acceptance → Evolution Analysis
```

### Key Components:
- `roles/` - Individual agent implementations
- `sop_engine/` - Workflow orchestration
- `memory/` - Evolutionary memory system
- `utils/` - Shared utilities
- `config/` - Configuration management

## Submitting Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code standards

3. Test your changes thoroughly

4. Commit your changes with a clear, descriptive message:
   ```
   feat: Add new capability to role
   
   - Describe what was added
   - Mention why it was needed
   - Reference any related issues
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a pull request with a clear description of your changes

## Pull Request Guidelines

- Keep pull requests focused on a single feature or fix
- Include tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting
- Describe the problem and solution in the PR description

## Questions?

If you have questions, feel free to open an issue or contact the maintainers.

Thank you for contributing to Project Chrysalis!