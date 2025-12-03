"""
Semantic analysis for JAM Python services.

This module provides type checking, validation, and namespace management
for the JAM Python DSL, following a similar architecture to Vyper.
"""

import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, List, Set, Any, Union
from contextlib import contextmanager


# =============================================================================
# Type System
# =============================================================================

class JamTypeKind(Enum):
    """Categories of JAM types."""
    INTEGER = auto()
    BYTES = auto()
    STRING = auto()
    BOOL = auto()
    VOID = auto()
    ARRAY = auto()
    STRUCT = auto()


@dataclass
class JamType(ABC):
    """Base class for all JAM types."""
    
    @property
    @abstractmethod
    def kind(self) -> JamTypeKind:
        """Return the type category."""
        ...
    
    @property
    @abstractmethod
    def c_type(self) -> str:
        """Return the C type representation."""
        ...
    
    @property
    def size(self) -> int:
        """Return the size in bytes."""
        return 0
    
    def is_numeric(self) -> bool:
        return self.kind == JamTypeKind.INTEGER
    
    def is_assignable_from(self, other: "JamType") -> bool:
        """Check if this type can be assigned from another type."""
        # Integer literals (I64) can be assigned to any integer type
        if isinstance(other, IntegerType) and isinstance(self, IntegerType):
            # I64 is the "generic" integer literal type - it's flexible
            if other.bits == 64 and other.signed:
                return True  # Allow integer literals to match any integer type
            # Otherwise check normal rules
            if self.signed == other.signed:
                return other.bits <= self.bits
            if self.signed and not other.signed:
                return other.bits < self.bits
        return type(self) == type(other)
    
    def __eq__(self, other):
        if not isinstance(other, JamType):
            return False
        return type(self) == type(other)
    
    def __hash__(self):
        return hash(type(self).__name__)


@dataclass
class IntegerType(JamType):
    """Integer types: u8, u16, u32, u64, i32, i64."""
    bits: int
    signed: bool = False
    
    @property
    def kind(self) -> JamTypeKind:
        return JamTypeKind.INTEGER
    
    @property
    def c_type(self) -> str:
        prefix = "int" if self.signed else "uint"
        return f"{prefix}{self.bits}_t"
    
    @property
    def size(self) -> int:
        return self.bits // 8
    
    def is_assignable_from(self, other: "JamType") -> bool:
        if isinstance(other, IntegerType):
            # Can assign smaller to larger, same signedness
            if self.signed == other.signed:
                return other.bits <= self.bits
            # Can assign unsigned to larger signed
            if self.signed and not other.signed:
                return other.bits < self.bits
        return False
    
    def __repr__(self):
        prefix = "i" if self.signed else "u"
        return f"{prefix}{self.bits}"


@dataclass
class BytesType(JamType):
    """Bytes type with optional fixed length."""
    length: Optional[int] = None  # None means dynamic
    
    @property
    def kind(self) -> JamTypeKind:
        return JamTypeKind.BYTES
    
    @property
    def c_type(self) -> str:
        return "uint8_t*"
    
    @property
    def size(self) -> int:
        return self.length if self.length else 0
    
    def is_assignable_from(self, other: "JamType") -> bool:
        if isinstance(other, BytesType):
            if self.length is None:
                return True  # Dynamic can accept any
            return other.length == self.length
        return False


@dataclass
class StringType(JamType):
    """String type (null-terminated)."""
    
    @property
    def kind(self) -> JamTypeKind:
        return JamTypeKind.STRING
    
    @property
    def c_type(self) -> str:
        return "char*"


@dataclass
class BoolType(JamType):
    """Boolean type."""
    
    @property
    def kind(self) -> JamTypeKind:
        return JamTypeKind.BOOL
    
    @property
    def c_type(self) -> str:
        return "uint8_t"
    
    @property
    def size(self) -> int:
        return 1


@dataclass
class VoidType(JamType):
    """Void type for functions with no return."""
    
    @property
    def kind(self) -> JamTypeKind:
        return JamTypeKind.VOID
    
    @property
    def c_type(self) -> str:
        return "void"


@dataclass 
class ArrayType(JamType):
    """Fixed-size array type."""
    element_type: JamType
    length: int
    
    @property
    def kind(self) -> JamTypeKind:
        return JamTypeKind.ARRAY
    
    @property
    def c_type(self) -> str:
        return f"{self.element_type.c_type}*"
    
    @property
    def size(self) -> int:
        return self.element_type.size * self.length


# Singleton type instances
U8 = IntegerType(8, signed=False)
U16 = IntegerType(16, signed=False)
U32 = IntegerType(32, signed=False)
U64 = IntegerType(64, signed=False)
I32 = IntegerType(32, signed=True)
I64 = IntegerType(64, signed=True)
BYTES = BytesType()
STRING = StringType()
BOOL = BoolType()
VOID = VoidType()

# Type aliases for JAM-specific types
SERVICE_ID = U32
GAS = U64
BALANCE = U64
HASH = BytesType(32)
TIMESLOT = U32


# Type name mapping
TYPE_REGISTRY: Dict[str, JamType] = {
    # Python built-in types
    "int": I64,
    "bytes": BYTES,
    "str": STRING,
    "bool": BOOL,
    "None": VOID,
    
    # Explicit integer types
    "U8": U8,
    "U16": U16,
    "U32": U32,
    "U64": U64,
    "I32": I32,
    "I64": I64,
    "u8": U8,
    "u16": U16,
    "u32": U32,
    "u64": U64,
    "i32": I32,
    "i64": I64,
    
    # JAM-specific types
    "ServiceId": SERVICE_ID,
    "Gas": GAS,
    "Balance": BALANCE,
    "Hash": HASH,
    "TimeSlot": TIMESLOT,
}


def resolve_type(type_name: str) -> Optional[JamType]:
    """Resolve a type name to a JamType."""
    return TYPE_REGISTRY.get(type_name)


# =============================================================================
# Symbols and Namespaces
# =============================================================================

class SymbolKind(Enum):
    """Kinds of symbols in the namespace."""
    VARIABLE = auto()
    FUNCTION = auto()
    CONSTANT = auto()
    PARAMETER = auto()


@dataclass
class Symbol:
    """A symbol in the namespace."""
    name: str
    kind: SymbolKind
    type: JamType
    is_mutable: bool = True
    node: Optional[ast.AST] = None  # Source location
    
    def __repr__(self):
        return f"Symbol({self.name}: {self.type}, {self.kind.name})"


@dataclass
class FunctionSignature:
    """Function type information."""
    name: str
    params: List[tuple[str, JamType]]  # (name, type) pairs
    return_type: JamType
    is_host_call: bool = False


# Built-in functions available in JAM services
BUILTIN_FUNCTIONS: Dict[str, FunctionSignature] = {
    "gas": FunctionSignature("gas", [], U64, is_host_call=True),
    "log": FunctionSignature("log", [("msg", STRING)], VOID, is_host_call=True),
    "log_info": FunctionSignature("log_info", [("msg", STRING)], VOID, is_host_call=True),
    "log_error": FunctionSignature("log_error", [("msg", STRING)], VOID, is_host_call=True),
    "log_warn": FunctionSignature("log_warn", [("msg", STRING)], VOID, is_host_call=True),
    "log_debug": FunctionSignature("log_debug", [("msg", STRING)], VOID, is_host_call=True),
    "get_storage": FunctionSignature(
        "get_storage",
        [("service_id", SERVICE_ID), ("key", BYTES), ("key_len", U64), 
         ("out", BYTES), ("offset", U64), ("length", U64)],
        U64,
        is_host_call=True
    ),
    "set_storage": FunctionSignature(
        "set_storage",
        [("key", BYTES), ("key_len", U64), ("value", BYTES), ("value_len", U64)],
        U64,
        is_host_call=True
    ),
    "len": FunctionSignature("len", [("s", STRING)], U64),
}


class Namespace:
    """
    Scoped symbol table for tracking variables and functions.
    
    Supports nested scopes (function → block → loop, etc.)
    """
    
    def __init__(self, parent: Optional["Namespace"] = None, name: str = "global"):
        self.parent = parent
        self.name = name
        self._symbols: Dict[str, Symbol] = {}
        self._functions: Dict[str, FunctionSignature] = {}
        
        # Load builtins at global scope
        if parent is None:
            self._functions.update(BUILTIN_FUNCTIONS)
    
    def define(self, symbol: Symbol) -> None:
        """Define a new symbol in this scope."""
        if symbol.name in self._symbols:
            raise SemanticError(
                f"Variable '{symbol.name}' already defined in this scope",
                symbol.node
            )
        self._symbols[symbol.name] = symbol
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol, searching parent scopes."""
        if name in self._symbols:
            return self._symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope only."""
        return self._symbols.get(name)
    
    def define_function(self, func: FunctionSignature) -> None:
        """Define a function in this scope."""
        self._functions[func.name] = func
    
    def lookup_function(self, name: str) -> Optional[FunctionSignature]:
        """Look up a function, searching parent scopes."""
        if name in self._functions:
            return self._functions[name]
        if self.parent:
            return self.parent.lookup_function(name)
        return None
    
    @contextmanager
    def enter_scope(self, name: str = "block"):
        """Create a child scope and enter it."""
        child = Namespace(parent=self, name=name)
        yield child
    
    def all_symbols(self) -> Dict[str, Symbol]:
        """Get all symbols in this scope (not parents)."""
        return self._symbols.copy()
    
    def __repr__(self):
        return f"Namespace({self.name}, symbols={list(self._symbols.keys())})"


# =============================================================================
# Semantic Errors
# =============================================================================

@dataclass
class SemanticError(Exception):
    """Error during semantic analysis."""
    message: str
    node: Optional[ast.AST] = None
    
    def __str__(self):
        if self.node and hasattr(self.node, 'lineno'):
            return f"Line {self.node.lineno}: {self.message}"
        return self.message


@dataclass
class TypeError(SemanticError):
    """Type mismatch error."""
    expected: Optional[JamType] = None
    actual: Optional[JamType] = None
    
    def __str__(self):
        base = super().__str__()
        if self.expected and self.actual:
            return f"{base} (expected {self.expected}, got {self.actual})"
        return base


# =============================================================================
# Semantic Analyzer
# =============================================================================

@dataclass
class AnalysisResult:
    """Result of semantic analysis."""
    namespace: Namespace
    type_annotations: Dict[int, JamType]  # node id -> type
    errors: List[SemanticError]
    warnings: List[str]
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


class SemanticAnalyzer(ast.NodeVisitor):
    """
    Performs semantic analysis on Python AST.
    
    - Type checking
    - Variable scope validation
    - JAM-specific constraint validation
    """
    
    def __init__(self):
        self.namespace = Namespace()
        self.type_annotations: Dict[int, JamType] = {}
        self.errors: List[SemanticError] = []
        self.warnings: List[str] = []
        self.current_function: Optional[FunctionSignature] = None
        
    def analyze(self, tree: ast.AST) -> AnalysisResult:
        """Analyze an AST and return the result."""
        self.visit(tree)
        return AnalysisResult(
            namespace=self.namespace,
            type_annotations=self.type_annotations,
            errors=self.errors,
            warnings=self.warnings
        )
    
    def error(self, message: str, node: Optional[ast.AST] = None):
        """Record an error."""
        self.errors.append(SemanticError(message, node))
    
    def warn(self, message: str, node: Optional[ast.AST] = None):
        """Record a warning."""
        loc = f"Line {node.lineno}: " if node and hasattr(node, 'lineno') else ""
        self.warnings.append(f"{loc}{message}")
    
    def annotate(self, node: ast.AST, typ: JamType):
        """Annotate a node with its type."""
        self.type_annotations[id(node)] = typ
    
    def get_type(self, node: ast.AST) -> Optional[JamType]:
        """Get the annotated type of a node."""
        return self.type_annotations.get(id(node))
    
    # -------------------------------------------------------------------------
    # Visitors
    # -------------------------------------------------------------------------
    
    def visit_Module(self, node: ast.Module):
        for stmt in node.body:
            self.visit(stmt)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Parse return type
        return_type = VOID
        if node.returns:
            return_type = self._resolve_type_annotation(node.returns) or VOID
        
        # Parse parameters
        params: List[tuple[str, JamType]] = []
        for arg in node.args.args:
            if arg.arg == 'self':
                continue
            
            param_type = VOID
            if arg.annotation:
                param_type = self._resolve_type_annotation(arg.annotation) or VOID
            
            if param_type == VOID:
                self.error(f"Parameter '{arg.arg}' must have a type annotation", arg)
                param_type = I64  # Default to i64 for error recovery
            
            params.append((arg.arg, param_type))
        
        # Create function signature
        func_sig = FunctionSignature(node.name, params, return_type)
        self.namespace.define_function(func_sig)
        
        # Enter function scope
        with self.namespace.enter_scope(f"func:{node.name}") as func_scope:
            # Add parameters to scope
            for param_name, param_type in params:
                func_scope.define(Symbol(
                    name=param_name,
                    kind=SymbolKind.PARAMETER,
                    type=param_type,
                    is_mutable=False
                ))
            
            # Save current namespace and function
            old_namespace = self.namespace
            old_function = self.current_function
            self.namespace = func_scope
            self.current_function = func_sig
            
            # Visit body
            for stmt in node.body:
                self.visit(stmt)
            
            # Restore
            self.namespace = old_namespace
            self.current_function = old_function
    
    def visit_Assign(self, node: ast.Assign):
        if len(node.targets) != 1:
            self.error("Multiple assignment not supported", node)
            return
        
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            self.error("Only simple variable assignment supported", node)
            return
        
        # Infer type from value
        value_type = self._infer_type(node.value)
        if value_type is None:
            self.error(f"Cannot infer type for assignment to '{target.id}'", node)
            return
        
        # Check if already defined
        existing = self.namespace.lookup_local(target.id)
        if existing:
            # Check type compatibility
            if not existing.type.is_assignable_from(value_type):
                self.error(
                    f"Cannot assign {value_type} to variable '{target.id}' of type {existing.type}",
                    node
                )
        else:
            # Define new variable
            self.namespace.define(Symbol(
                name=target.id,
                kind=SymbolKind.VARIABLE,
                type=value_type,
                node=node
            ))
        
        self.annotate(node, value_type)
    
    def visit_AnnAssign(self, node: ast.AnnAssign):
        if not isinstance(node.target, ast.Name):
            self.error("Only simple variable assignment supported", node)
            return
        
        var_name = node.target.id
        
        # Get declared type
        declared_type = self._resolve_type_annotation(node.annotation)
        if declared_type is None:
            self.error(f"Unknown type annotation for '{var_name}'", node)
            return
        
        if node.value:
            # Check value type matches
            value_type = self._infer_type(node.value)
            if value_type and not declared_type.is_assignable_from(value_type):
                self.error(
                    f"Cannot assign {value_type} to variable '{var_name}' of type {declared_type}",
                    node
                )
        
        # Define variable
        self.namespace.define(Symbol(
            name=var_name,
            kind=SymbolKind.VARIABLE,
            type=declared_type,
            node=node
        ))
        
        self.annotate(node, declared_type)
    
    def visit_Return(self, node: ast.Return):
        if self.current_function is None:
            self.error("Return statement outside function", node)
            return
        
        if node.value:
            value_type = self._infer_type(node.value)
            if value_type:
                if not self.current_function.return_type.is_assignable_from(value_type):
                    self.error(
                        f"Return type mismatch: expected {self.current_function.return_type}, got {value_type}",
                        node
                    )
        elif self.current_function.return_type != VOID:
            self.error(
                f"Function must return {self.current_function.return_type}",
                node
            )
    
    def visit_If(self, node: ast.If):
        # Check condition is boolean-like
        cond_type = self._infer_type(node.test)
        if cond_type and cond_type not in (BOOL, U8, U16, U32, U64, I32, I64):
            self.warn(f"Condition should be boolean or integer, got {cond_type}", node.test)
        
        # Visit branches in their own scopes
        with self.namespace.enter_scope("if") as if_scope:
            old_ns = self.namespace
            self.namespace = if_scope
            for stmt in node.body:
                self.visit(stmt)
            self.namespace = old_ns
        
        if node.orelse:
            with self.namespace.enter_scope("else") as else_scope:
                old_ns = self.namespace
                self.namespace = else_scope
                for stmt in node.orelse:
                    self.visit(stmt)
                self.namespace = old_ns
    
    def visit_For(self, node: ast.For):
        if not isinstance(node.target, ast.Name):
            self.error("Only simple loop variable supported", node)
            return
        
        # Only support range() for now
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
            if node.iter.func.id == 'range':
                # Validate range arguments
                for arg in node.iter.args:
                    arg_type = self._infer_type(arg)
                    if arg_type and not arg_type.is_numeric():
                        self.error(f"range() argument must be integer, got {arg_type}", arg)
                
                # Define loop variable
                with self.namespace.enter_scope("for") as for_scope:
                    for_scope.define(Symbol(
                        name=node.target.id,
                        kind=SymbolKind.VARIABLE,
                        type=I64,
                        is_mutable=False
                    ))
                    
                    old_ns = self.namespace
                    self.namespace = for_scope
                    for stmt in node.body:
                        self.visit(stmt)
                    self.namespace = old_ns
                return
        
        self.error("Only for loops with range() are supported", node)
    
    def visit_While(self, node: ast.While):
        cond_type = self._infer_type(node.test)
        if cond_type and cond_type not in (BOOL, U8, U16, U32, U64, I32, I64):
            self.warn(f"Condition should be boolean or integer, got {cond_type}", node.test)
        
        with self.namespace.enter_scope("while") as while_scope:
            old_ns = self.namespace
            self.namespace = while_scope
            for stmt in node.body:
                self.visit(stmt)
            self.namespace = old_ns
    
    def visit_Expr(self, node: ast.Expr):
        # Expression statement - just infer the type
        self._infer_type(node.value)
    
    def visit_Pass(self, node: ast.Pass):
        pass
    
    def visit_Break(self, node: ast.Break):
        pass
    
    def visit_Continue(self, node: ast.Continue):
        pass
    
    # -------------------------------------------------------------------------
    # Type inference
    # -------------------------------------------------------------------------
    
    def _resolve_type_annotation(self, node: ast.expr) -> Optional[JamType]:
        """Resolve a type annotation node to a JamType."""
        if isinstance(node, ast.Name):
            return resolve_type(node.id)
        elif isinstance(node, ast.Constant) and node.value is None:
            return VOID
        elif isinstance(node, ast.Subscript):
            # Handle things like bytes[32], List[int], etc.
            if isinstance(node.value, ast.Name):
                base_type = node.value.id
                if base_type == "bytes" and isinstance(node.slice, ast.Constant):
                    return BytesType(node.slice.value)
        return None
    
    def _infer_type(self, node: ast.expr) -> Optional[JamType]:
        """Infer the type of an expression."""
        
        if isinstance(node, ast.Constant):
            return self._infer_constant_type(node)
        
        elif isinstance(node, ast.Name):
            symbol = self.namespace.lookup(node.id)
            if symbol:
                typ = symbol.type
                self.annotate(node, typ)
                return typ
            else:
                self.error(f"Undefined variable: '{node.id}'", node)
                return None
        
        elif isinstance(node, ast.BinOp):
            left_type = self._infer_type(node.left)
            right_type = self._infer_type(node.right)
            
            if left_type and right_type:
                result_type = self._binary_result_type(left_type, right_type, node.op)
                if result_type:
                    self.annotate(node, result_type)
                    return result_type
                else:
                    self.error(
                        f"Incompatible types for binary operation: {left_type} and {right_type}",
                        node
                    )
            return None
        
        elif isinstance(node, ast.Compare):
            # Comparisons always return bool
            left_type = self._infer_type(node.left)
            for comp in node.comparators:
                self._infer_type(comp)
            self.annotate(node, BOOL)
            return BOOL
        
        elif isinstance(node, ast.BoolOp):
            for value in node.values:
                self._infer_type(value)
            self.annotate(node, BOOL)
            return BOOL
        
        elif isinstance(node, ast.UnaryOp):
            operand_type = self._infer_type(node.operand)
            if operand_type:
                if isinstance(node.op, ast.Not):
                    self.annotate(node, BOOL)
                    return BOOL
                elif isinstance(node.op, (ast.USub, ast.UAdd)):
                    self.annotate(node, operand_type)
                    return operand_type
                elif isinstance(node.op, ast.Invert):
                    if operand_type.is_numeric():
                        self.annotate(node, operand_type)
                        return operand_type
            return None
        
        elif isinstance(node, ast.Call):
            return self._infer_call_type(node)
        
        elif isinstance(node, ast.Subscript):
            value_type = self._infer_type(node.value)
            if value_type:
                if isinstance(value_type, ArrayType):
                    self.annotate(node, value_type.element_type)
                    return value_type.element_type
                elif isinstance(value_type, (BytesType, StringType)):
                    self.annotate(node, U8)
                    return U8
            return None
        
        elif isinstance(node, ast.IfExp):
            # Ternary expression
            self._infer_type(node.test)
            body_type = self._infer_type(node.body)
            else_type = self._infer_type(node.orelse)
            
            if body_type and else_type:
                if body_type == else_type:
                    self.annotate(node, body_type)
                    return body_type
                else:
                    self.error(
                        f"Ternary branches have different types: {body_type} and {else_type}",
                        node
                    )
            return body_type or else_type
        
        elif isinstance(node, ast.JoinedStr):
            # f-string always returns string
            for value in node.values:
                if isinstance(value, ast.FormattedValue):
                    self._infer_type(value.value)
            self.annotate(node, STRING)
            return STRING
        
        elif isinstance(node, ast.Attribute):
            # For now, just return void - would need struct support
            self.warn(f"Attribute access not fully supported", node)
            return None
        
        return None
    
    def _infer_constant_type(self, node: ast.Constant) -> JamType:
        """Infer type of a constant."""
        if isinstance(node.value, bool):
            typ = BOOL
        elif isinstance(node.value, int):
            # Integer literals are flexible - use I64 as default
            # They can be assigned to any integer type
            typ = I64
        elif isinstance(node.value, str):
            typ = STRING
        elif isinstance(node.value, bytes):
            typ = BytesType(len(node.value))
        elif node.value is None:
            typ = VOID
        else:
            typ = VOID
        
        self.annotate(node, typ)
        return typ
    
    def _infer_call_type(self, node: ast.Call) -> Optional[JamType]:
        """Infer the return type of a function call."""
        func_name = None
        
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if func_name:
            func_sig = self.namespace.lookup_function(func_name)
            if func_sig:
                # Validate argument count
                expected_count = len(func_sig.params)
                actual_count = len(node.args)
                
                if actual_count != expected_count:
                    self.error(
                        f"Function '{func_name}' expects {expected_count} arguments, got {actual_count}",
                        node
                    )
                
                # Type check arguments
                for i, (arg, (param_name, param_type)) in enumerate(zip(node.args, func_sig.params)):
                    arg_type = self._infer_type(arg)
                    if arg_type and not param_type.is_assignable_from(arg_type):
                        self.warn(
                            f"Argument {i+1} ({param_name}): expected {param_type}, got {arg_type}",
                            arg
                        )
                
                self.annotate(node, func_sig.return_type)
                return func_sig.return_type
            else:
                self.error(f"Unknown function: '{func_name}'", node)
        
        return None
    
    def _binary_result_type(
        self, left: JamType, right: JamType, op: ast.operator
    ) -> Optional[JamType]:
        """Determine the result type of a binary operation."""
        
        # Numeric operations
        if left.is_numeric() and right.is_numeric():
            left_int = left if isinstance(left, IntegerType) else None
            right_int = right if isinstance(right, IntegerType) else None
            
            if left_int and right_int:
                # Result is the wider type
                result_bits = max(left_int.bits, right_int.bits)
                result_signed = left_int.signed or right_int.signed
                return IntegerType(result_bits, result_signed)
        
        # String concatenation
        if isinstance(op, ast.Add):
            if isinstance(left, StringType) and isinstance(right, StringType):
                return STRING
        
        return None


def analyze_service(service_class: type) -> AnalysisResult:
    """
    Perform semantic analysis on a JAM service class.
    
    Args:
        service_class: A class decorated with @service
    
    Returns:
        AnalysisResult with type annotations and any errors
    """
    import inspect
    
    if not hasattr(service_class, '_jam_meta'):
        raise ValueError(f"{service_class.__name__} is not a JAM service")
    
    meta = service_class._jam_meta
    analyzer = SemanticAnalyzer()
    
    # Analyze each method
    for method_name, method in meta.methods.items():
        source = inspect.getsource(method)
        source = inspect.cleandoc(source)
        tree = ast.parse(source)
        analyzer.visit(tree)
    
    return AnalysisResult(
        namespace=analyzer.namespace,
        type_annotations=analyzer.type_annotations,
        errors=analyzer.errors,
        warnings=analyzer.warnings
    )
