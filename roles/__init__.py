"""
Roles Package for Virtual Software Company - Next Generation
"""
from .architect import Architect
from .coder import Coder
from .techlead import TechLead
from .qa_engineer import QAEngineer
from .project_manager import ProjectManager
from .auditor import Auditor
from .sysadmin import SysAdmin
from .evolution_officer import EvolutionOfficer

__all__ = [
    'Architect', 
    'Coder', 
    'TechLead', 
    'QAEngineer',
    'ProjectManager',
    'Auditor',
    'SysAdmin',
    'EvolutionOfficer'
]