"""
Virtual Software Company Roles Package
"""
from .architect import Architect
from .coder import Coder
from .techlead import TechLead
from .qa_engineer import QAEngineer
from .project_manager import ProjectManager
from .evolution_officer import EvolutionOfficer
from .auditor import Auditor
from .sysadmin import SysAdmin

__all__ = [
    'Architect',
    'Coder',
    'TechLead',
    'QAEngineer',
    'ProjectManager',
    'EvolutionOfficer',
    'Auditor',
    'SysAdmin'
]