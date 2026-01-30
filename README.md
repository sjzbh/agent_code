# Project Chrysalis (破茧计划) - Virtual Software Company V2.1

## Overview
This is the next-generation self-evolving agent system based on the experience gained from V2.0. The system has undergone environmental adaptation and error immunity enhancement to become more robust and efficient.

## Key Features

### 1. Environment Optimization (Linux-Optimized)
- Removed all Windows/macOS conditional logic
- Hard-coded for Linux environment with optimized commands
- Pre-installed common libraries (pygame, requests) based on usage patterns

### 2. Error Immunity
- Applied solutions from "Error -> Solution" pairs found in knowledge base
- Enhanced JSON parsing with fallback mechanisms
- Auto-recovery for common environment issues

### 3. Evolution Gene Preservation
- Retained EvolutionOfficer with enhanced analysis capabilities
- Improved experience base with better categorization
- Automated insight extraction and storage

### 4. Architecture Enhancement
- Modular design with cleaner separation of concerns
- Enhanced SOP engine with better error handling
- More robust error handling throughout the pipeline

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