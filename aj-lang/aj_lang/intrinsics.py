"""
Intrinsics registry for Python to C transpilation.

This module provides a flexible way to map Python functions/methods to C code
without hardcoding every translation in the transpiler.

Usage:
    # Register a simple function mapping
    @intrinsic('LOG_INFO')
    def log(msg): ...
    
    # Register a method with custom code generation
    @intrinsic_method('int', 'from_bytes', generator=decode_int_from_bytes)
    def from_bytes(data, byteorder): ...
"""

from typing import Callable, Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
import ast


@dataclass
class IntrinsicDef:
    """Definition of an intrinsic function/method."""
    c_name: Optional[str] = None  # Direct C function name mapping
    generator: Optional[Callable] = None  # Custom code generator
    return_type: str = 'void*'  # C return type
    arg_types: Optional[List[str]] = None  # C argument types
    
    def generate(self, args: List[str], node: ast.Call, ctx: Any) -> str:
        """Generate C code for this intrinsic."""
        if self.generator:
            return self.generator(args, node, ctx)
        elif self.c_name:
            return f"{self.c_name}({', '.join(args)})"
        else:
            raise ValueError("Intrinsic must have either c_name or generator")


# Global registry: (class_name, method_name) -> IntrinsicDef
# class_name can be None for standalone functions
_INTRINSICS: Dict[Tuple[Optional[str], str], IntrinsicDef] = {}


def register_intrinsic(
    class_name: Optional[str],
    method_name: str,
    c_name: Optional[str] = None,
    generator: Optional[Callable] = None,
    return_type: str = 'void*',
    arg_types: Optional[List[str]] = None
):
    """Register an intrinsic function or method."""
    _INTRINSICS[(class_name, method_name)] = IntrinsicDef(
        c_name=c_name,
        generator=generator,
        return_type=return_type,
        arg_types=arg_types
    )


def get_intrinsic(class_name: Optional[str], method_name: str) -> Optional[IntrinsicDef]:
    """Look up an intrinsic by class and method name."""
    # Try exact match first
    key = (class_name, method_name)
    if key in _INTRINSICS:
        return _INTRINSICS[key]
    
    # Try standalone function (class_name = None)
    if class_name is not None:
        key = (None, method_name)
        if key in _INTRINSICS:
            return _INTRINSICS[key]
    
    return None


def intrinsic(c_name: Optional[str] = None, return_type: str = 'void*'):
    """Decorator to register a standalone function as an intrinsic."""
    def decorator(fn):
        register_intrinsic(
            class_name=None,
            method_name=fn.__name__,
            c_name=c_name or fn.__name__,
            return_type=return_type
        )
        return fn
    return decorator


def intrinsic_method(class_name: str, method_name: str, c_name: Optional[str] = None,
                     generator: Optional[Callable] = None, return_type: str = 'void*'):
    """Decorator to register a method as an intrinsic."""
    def decorator(fn):
        register_intrinsic(
            class_name=class_name,
            method_name=method_name,
            c_name=c_name,
            generator=generator or fn,
            return_type=return_type
        )
        return fn
    return decorator


# =============================================================================
# Built-in Intrinsics - Custom Generators
# =============================================================================

def _gen_int_from_bytes(args: List[str], node: ast.Call, ctx) -> str:
    """Generate C code for int.from_bytes(data, byteorder)."""
    # We expect arg 0 to be a slice or bytes expression
    arg0 = node.args[0]
    
    if isinstance(arg0, ast.Subscript) and isinstance(arg0.slice, ast.Slice):
        # payload[start:end] -> _decode_u64_le(payload + start)
        base = ctx.visit_expr(arg0.value)
        start = ctx.visit_expr(arg0.slice.lower) if arg0.slice.lower else "0"
        return f"_decode_u64_le({base} + {start})"
    
    # Fall back to passing the expression directly
    return f"_decode_u64_le({args[0]})"


def _gen_len(args: List[str], node: ast.Call, ctx) -> str:
    """Generate C code for len()."""
    # Special case: len(payload) -> payload_len
    if len(node.args) == 1 and isinstance(node.args[0], ast.Name):
        if node.args[0].id == 'payload':
            return 'payload_len'
    
    # General case: str_len for strings/bytes
    return f"str_len({args[0]})"


def _gen_bytes_slice(args: List[str], node: ast.Call, ctx) -> str:
    """Generate C code for bytes slicing operations."""
    # This handles bytes[start:end] which returns a pointer
    return args[0]  # Already handled in visit_Subscript


# =============================================================================
# Register Built-in Intrinsics
# =============================================================================

# Integer conversion
register_intrinsic('int', 'from_bytes', generator=_gen_int_from_bytes, return_type='uint64_t')
register_intrinsic('U64', 'from_bytes', generator=_gen_int_from_bytes, return_type='uint64_t')
register_intrinsic('U32', 'from_bytes', generator=_gen_int_from_bytes, return_type='uint32_t')
register_intrinsic('U16', 'from_bytes', generator=_gen_int_from_bytes, return_type='uint16_t')
register_intrinsic('U8', 'from_bytes', generator=_gen_int_from_bytes, return_type='uint8_t')

# Built-in functions
register_intrinsic(None, 'len', generator=_gen_len, return_type='uint64_t')
register_intrinsic(None, 'print', c_name='LOG_INFO', return_type='void')
register_intrinsic(None, 'log', c_name='LOG_INFO', return_type='void')

# Logging functions from jam_sdk.host
register_intrinsic(None, 'LOG_INFO', c_name='LOG_INFO', return_type='void')
register_intrinsic(None, 'LOG_DEBUG', c_name='LOG_DEBUG', return_type='void')
register_intrinsic(None, 'LOG_ERROR', c_name='LOG_ERROR', return_type='void')
register_intrinsic(None, 'LOG_WARN', c_name='LOG_WARN', return_type='void')

# Host functions
register_intrinsic(None, 'gas', c_name='gas', return_type='uint64_t')
register_intrinsic(None, 'get_storage', c_name='get_storage', return_type='uint64_t')
register_intrinsic(None, 'set_storage', c_name='set_storage', return_type='uint64_t')


# =============================================================================
# Type Inference for Intrinsics
# =============================================================================

def infer_intrinsic_return_type(class_name: Optional[str], method_name: str) -> Optional[str]:
    """Get the return type of an intrinsic if known."""
    intrinsic = get_intrinsic(class_name, method_name)
    if intrinsic:
        return intrinsic.return_type
    return None
