"""
Módulo Master - Nodo central del cluster SCSC
"""

from .app import MasterApp
from .orchestrator import Orchestrator

__all__ = ["MasterApp", "Orchestrator"]