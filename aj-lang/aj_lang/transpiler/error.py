
import ast
import inspect
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass



@dataclass
class TranspileError(Exception):
    """Error during transpilation."""
    message: str
    node: Optional[ast.AST] = None
    
    def __str__(self):
        if self.node and hasattr(self.node, 'lineno'):
            return f"Line {getattr(self.node, 'lineno')}: {self.message}"
        return self.message
