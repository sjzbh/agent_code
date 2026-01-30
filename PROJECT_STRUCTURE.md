# Virtual Software Company - Next Generation (V2.1)
# Project Chrysalis - Self-Evolving Architecture

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