"""
JAM SDK for Python

A Pythonic SDK for building JAM blockchain services.
"""

from aj_lang.decorators import service, refine, accumulate, on_transfer
from aj_lang.runtime import JamService, ServiceRunner
from aj_lang import host
from aj_lang import types
from aj_lang.transpiler.transpile import transpile_service
from aj_lang.semantics import (
    SemanticAnalyzer, AnalysisResult, SemanticError,
    analyze_service
)

class TranspileError(Exception):
    """Transpilation error"""
    pass

__version__ = "0.1.0"
__all__ = [
    # Decorators
    "service",
    "refine", 
    "accumulate",
    "on_transfer",
    
    # Runtime
    "JamService",
    "ServiceRunner",
    "host",
    "types",
    
    # Transpiler
    "transpile_service",
    "TranspileError",
    
    # Semantics
    "SemanticAnalyzer",
    "AnalysisResult", 
    "SemanticError",
    "analyze_service",
]
