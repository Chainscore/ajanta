
import ast
import inspect
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

from aj_lang.semantics import (
    SemanticAnalyzer, AnalysisResult, JamType, 
    resolve_type, SemanticError
)
from aj_lang.intrinsics import get_intrinsic, infer_intrinsic_return_type

class VariableCollector(ast.NodeVisitor):
    """Collects local variables and their types."""
    def __init__(self, transpiler):
        self.transpiler = transpiler
        self.vars = {} # name -> type

    def visit_Assign(self, node: ast.Assign):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            if var_name not in self.transpiler.state_vars and var_name != 'self':
                # Infer type
                var_type = self.transpiler.infer_type(node.value)
                if var_name not in self.vars or self.vars[var_name] == 'void*':
                    self.vars[var_name] = var_type
        self.generic_visit(node)
        
    def visit_AnnAssign(self, node: ast.AnnAssign):
        if isinstance(node.target, ast.Name):
            var_name = node.target.id
            if var_name not in self.transpiler.state_vars:
                var_type = 'void*'
                if isinstance(node.annotation, ast.Name):
                    var_type = self.transpiler.get_c_type(node.annotation.id)
                self.vars[var_name] = var_type
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Don't recurse into nested functions
        for stmt in node.body:
            self.visit(stmt)
