import ast
import inspect
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

from aj_lang.semantics import (
    SemanticAnalyzer, AnalysisResult, JamType, 
    resolve_type, SemanticError
)
from aj_lang.intrinsics import get_intrinsic, infer_intrinsic_return_type
from .var_collector import VariableCollector
from .error import TranspileError


class CCodeGenerator(ast.NodeVisitor):
    """
    AST visitor that generates C code from Python.
    """
    
    def __init__(self, service_name: str, type_annotations: Optional[Dict[int, JamType]] = None, 
                 state_vars: Dict[str, Any] = None, structs: Dict[str, Any] = None):
        self.service_name = service_name
        self.indent_level = 0
        self.output: list[str] = []
        self.local_vars: dict[str, str] = {}  # name -> C type
        self.temp_counter = 0
        self.type_annotations = type_annotations or {}
        self.state_vars = state_vars or {}
        self.structs = structs or {}
        
    def indent(self) -> str:
        return "    " * self.indent_level
    
    def emit(self, code: str):
        self.output.append(self.indent() + code)
    
    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"_tmp{self.temp_counter}"
    
    def get_c_type(self, py_type: str) -> str:
        """Convert Python type name to C type."""
        type_map = {
            'U64': 'uint64_t',
            'U32': 'uint32_t',
            'U16': 'uint16_t',
            'U8': 'uint8_t',
            'I64': 'int64_t',
            'I32': 'int32_t',
            'bool': 'int',
            'int': 'int64_t',
            'bytes': 'uint8_t*',
            'str': 'char*',
        }
        return type_map.get(py_type, py_type) # Default to passing through (e.g. struct names)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # Collect and declare local variables
        collector = VariableCollector(self)
        collector.visit(node)
        
        for name, c_type in collector.vars.items():
            if name == 'payload': continue # Already declared in wrapper
            if c_type == 'void*': c_type = 'uint64_t' # Default
            
            # Special case for arrays (strings/bytes)
            if c_type == 'char*' or c_type == 'uint8_t*':
                 self.emit(f"{c_type} {name} = NULL;")
            elif c_type.startswith('uint8_t[') and c_type.endswith(']'):
                 # Stack allocated array: uint8_t name[N] = {0};
                 # c_type is "uint8_t[N]"
                 base_type, size_part = c_type.split('[', 1)
                 size = size_part[:-1] # Remove trailing ']'
                 self.emit(f"{base_type} {name}[{size}] = {{0}};")
            elif c_type in self.structs:
                 self.emit(f"{c_type} {name} = {{0}};")
            else:
                 self.emit(f"{c_type} {name} = 0;")
            self.local_vars[name] = c_type

        for stmt in node.body:
            self.visit(stmt)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        if len(node.targets) != 1:
            raise TranspileError("Multiple assignment not supported", node)
        
        target = node.targets[0]
        
        # Special case: bytearray allocation
        # buf = bytearray(N) -> already handled in declaration (zero init)
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'bytearray':
            # Skip assignment, as it's handled in declaration
            return

        value_code = self.visit_expr(node.value)
        
        if isinstance(target, ast.Name):
            var_name = target.id
            if var_name in self.state_vars:
                # Global state assignment
                self.emit(f"{var_name} = {value_code};")
            else:
                # Local variable (already declared)
                # Check if it's an array type (stack allocated)
                if var_name in self.local_vars and '[' in self.local_vars[var_name]:
                     # Array assignment not supported directly, usually handled by special cases (like bytearray above)
                     # or memcpy if we supported it.
                     # For now, if we get here, it's likely an error or unsupported.
                     pass 
                else:
                    self.emit(f"{var_name} = {value_code};")
                
        elif isinstance(target, ast.Subscript):
            # Mapping assignment: balances[to] = val -> balances_set(to, val)
            # Or self.balances[to] = val
            
            map_name = None
            if isinstance(target.value, ast.Name) and target.value.id in self.state_vars:
                map_name = target.value.id
            elif isinstance(target.value, ast.Attribute) and isinstance(target.value.value, ast.Name) and target.value.value.id == 'self':
                if target.value.attr in self.state_vars:
                    map_name = target.value.attr
            
            if map_name:
                key_code = self.visit_expr(target.slice)
                self.emit(f"{map_name}_set({key_code}, {value_code});")
            else:
                raise TranspileError("Only mapping assignment supported for subscripts", node)
                
        elif isinstance(target, ast.Attribute):
            # Struct field assignment: user.joined_at = val
            # Or self.state_var = val
            
            if isinstance(target.value, ast.Name) and target.value.id == 'self':
                if target.attr in self.state_vars:
                    self.emit(f"{target.attr} = {value_code};")
                    return

            obj_code = self.visit_expr(target.value)
            self.emit(f"{obj_code}.{target.attr} = {value_code};")
            
        else:
            raise TranspileError("Unsupported assignment target", node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        target = node.target
        value_code = self.visit_expr(node.value)
        
        op_map = {
            ast.Add: '+',
            ast.Sub: '-',
            ast.Mult: '*',
            ast.Div: '/',
            ast.Mod: '%',
            ast.BitOr: '|',
            ast.BitAnd: '&',
            ast.BitXor: '^',
            ast.LShift: '<<',
            ast.RShift: '>>',
        }
        op = op_map.get(type(node.op))
        
        if isinstance(target, ast.Name):
            var_name = target.id
            self.emit(f"{var_name} {op}= {value_code};")
            
        elif isinstance(target, ast.Attribute):
            # self.total_supply += amount
            if isinstance(target.value, ast.Name) and target.value.id == 'self':
                if target.attr in self.state_vars:
                    self.emit(f"{target.attr} {op}= {value_code};")
                    return
            
            # user.count += 1
            obj_code = self.visit_expr(target.value)
            self.emit(f"{obj_code}.{target.attr} {op}= {value_code};")

        elif isinstance(target, ast.Subscript):
            # Mapping aug assign: balances[to] += val
            # -> balances_set(to, balances_get(to) + val)
            
            map_name = None
            if isinstance(target.value, ast.Name) and target.value.id in self.state_vars:
                map_name = target.value.id
            elif isinstance(target.value, ast.Attribute) and isinstance(target.value.value, ast.Name) and target.value.value.id == 'self':
                if target.value.attr in self.state_vars:
                    map_name = target.value.attr

            if map_name:
                key_code = self.visit_expr(target.slice)
                # We need a temp for key to avoid double evaluation if it's complex
                # But for now assume simple keys
                self.emit(f"{map_name}_set({key_code}, {map_name}_get({key_code}) {op} {value_code});")
            else:
                raise TranspileError("Only mapping aug assignment supported for subscripts", node)
        else:
             raise TranspileError("Unsupported augmented assignment target", node)

    def visit_Return(self, node: ast.Return) -> None:
        if node.value:
            value_code = self.visit_expr(node.value)
            value_type = self.infer_type(node.value)
            
            # Handle bytes/string return for REFINE_FN
            # In C SDK REFINE_FN expects jam_refine_result_t
            # We can use helper functions like ok_void() or error() or manual construction
            
            if value_type == 'uint8_t*' or value_type == 'char*':
                # Assuming returning bytes means success with data
                # We need to construct jam_refine_result_t
                # But wait, the C SDK examples use static buffers or helpers.
                # Let's try to be smart.
                
                # If returning b'', return ok_void()
                if isinstance(node.value, ast.Constant) and node.value.value == b'':
                     self.emit("return ok_void();")
                     return

                # If returning b'\xFE', return error(0xFE)
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, bytes) and len(node.value.value) == 1:
                     self.emit(f"return error(0x{node.value.value[0]:02X});")
                     return

                # General case: return (jam_refine_result_t){(uint64_t)ptr, len}
                # We need length.
                len_code = "0"
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, (bytes, str)):
                    len_code = str(len(node.value.value))
                else:
                    len_code = f"str_len((char*){value_code})" # Assuming null-terminated if unknown
                
                self.emit(f"return (jam_refine_result_t){{(uint64_t){value_code}, {len_code}}};")
            elif value_type == 'uint64_t' or value_type == 'int64_t':
                self.emit(f"return ok_u64({value_code});")
            elif value_type in self.structs:
                self.emit(f"return ok_struct(&{value_code}, sizeof({value_type}));")
            else:
                # Maybe returning jam_refine_result_t directly?
                self.emit(f"return {value_code};")
        else:
            self.emit("return ok_void();")

    def visit_If(self, node: ast.If) -> None:
        cond = self.visit_expr(node.test)
        self.emit(f"if ({cond}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        
        if node.orelse:
            self.emit("} else {")
            self.indent_level += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indent_level -= 1
        self.emit("}")

    def visit_Expr(self, node: ast.Expr) -> None:
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return # Skip docstrings
        self.emit(f"{self.visit_expr(node.value)};")

    def visit_expr(self, node: ast.expr) -> str:
        if isinstance(node, ast.Constant):
            return self.visit_Constant(node)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.BinOp):
            return self.visit_BinOp(node)
        elif isinstance(node, ast.Compare):
            return self.visit_Compare(node)
        elif isinstance(node, ast.BoolOp):
            return self.visit_BoolOp(node)
        elif isinstance(node, ast.UnaryOp):
            return self.visit_UnaryOp(node)
        elif isinstance(node, ast.Call):
            return self.visit_Call(node)
        elif isinstance(node, ast.Subscript):
            return self.visit_Subscript(node)
        elif isinstance(node, ast.Attribute):
            return self.visit_Attribute(node)
        elif isinstance(node, ast.Slice):
            # Handle slice for bytes: payload[1:9]
            # This is tricky in C. We usually want a pointer arithmetic.
            # But visit_Subscript handles the usage.
            # If we are here, it might be part of something else.
            pass
        
        raise TranspileError(f"Unsupported expression: {type(node).__name__}", node)

    def visit_Constant(self, node: ast.Constant) -> str:
        if isinstance(node.value, str):
            return f'"{node.value}"'
        elif isinstance(node.value, bytes):
            # C string literal for bytes
            res = '"'
            for b in node.value:
                res += f'\\x{b:02x}'
            res += '"'
            return res
        elif isinstance(node.value, bool):
            return '1' if node.value else '0'
        elif isinstance(node.value, int):
            return str(node.value)
        elif node.value is None:
            return 'NULL'
        return str(node.value)

    def visit_BinOp(self, node: ast.BinOp) -> str:
        left = self.visit_expr(node.left)
        right = self.visit_expr(node.right)
        op_map = {
            ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/',
            ast.Mod: '%', ast.BitAnd: '&', ast.BitOr: '|', ast.BitXor: '^',
            ast.LShift: '<<', ast.RShift: '>>'
        }
        return f"({left} {op_map[type(node.op)]} {right})"

    def visit_Compare(self, node: ast.Compare) -> str:
        left = self.visit_expr(node.left)
        right = self.visit_expr(node.comparators[0])
        op_map = {
            ast.Eq: '==', ast.NotEq: '!=', ast.Lt: '<',
            ast.LtE: '<=', ast.Gt: '>', ast.GtE: '>='
        }
        return f"({left} {op_map[type(node.ops[0])]} {right})"

    def visit_BoolOp(self, node: ast.BoolOp) -> str:
        op = '&&' if isinstance(node.op, ast.And) else '||'
        return f"({' ' + op + ' '.join(self.visit_expr(v) for v in node.values)})"

    def visit_Call(self, node: ast.Call) -> str:
        func_name = ""
        class_name = None
        
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            # Get the class/object name for method calls
            if isinstance(node.func.value, ast.Name):
                class_name = node.func.value.id
        
        # Look up in intrinsics registry
        intrinsic = get_intrinsic(class_name, func_name)
        if intrinsic:
            # Generate args first (some intrinsics need the raw node)
            args = [self.visit_expr(a) for a in node.args]
            return intrinsic.generate(args, node, self)
        
        # Fallback: direct function call
        args = [self.visit_expr(a) for a in node.args]
        return f"{func_name}({', '.join(args)})"

    def visit_Subscript(self, node: ast.Subscript) -> str:
        # Mapping access: balances[to] -> balances_get(to)
        map_name = None
        if isinstance(node.value, ast.Name) and node.value.id in self.state_vars:
            map_name = node.value.id
        elif isinstance(node.value, ast.Attribute) and isinstance(node.value.value, ast.Name) and node.value.value.id == 'self':
            if node.value.attr in self.state_vars:
                map_name = node.value.attr
        
        if map_name:
            key_code = self.visit_expr(node.slice)
            return f"{map_name}_get({key_code})"
        
        # Array access / Slice
        value = self.visit_expr(node.value)
        if isinstance(node.slice, ast.Slice):
            # Slicing not directly supported in C expression unless used in specific context
            # But if we just want pointer arithmetic?
            # payload[1:9] -> (payload + 1)
            start = self.visit_expr(node.slice.lower) if node.slice.lower else "0"
            return f"({value} + {start})"
            
        index = self.visit_expr(node.slice)
        return f"{value}[{index}]"

    def visit_Attribute(self, node: ast.Attribute) -> str:
        if isinstance(node.value, ast.Name) and node.value.id == 'self':
            if node.attr in self.state_vars:
                return node.attr
        return f"{self.visit_expr(node.value)}.{node.attr}"

    def infer_type(self, node: ast.expr) -> str:
        # Basic inference
        if isinstance(node, ast.Constant):
            if isinstance(node.value, int): return 'int64_t'
            if isinstance(node.value, str): return 'char*'
            if isinstance(node.value, bytes): return 'uint8_t*'
        
        if isinstance(node, ast.Name):
            if node.id in self.local_vars:
                return self.local_vars[node.id]
            if node.id in self.state_vars:
                # Global state var type
                info = self.state_vars[node.id]
                return self.get_c_type(info['type'])

        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == 'self':
                if node.attr in self.state_vars:
                    info = self.state_vars[node.attr]
                    return self.get_c_type(info['type'])
        
        if isinstance(node, ast.Subscript):
            # payload[0] -> uint8_t
            if isinstance(node.value, ast.Name) and node.value.id == 'payload':
                return 'uint8_t'
            
            # balances[to] -> uint64_t
            # users[to] -> UserInfo
            map_name = None
            if isinstance(node.value, ast.Name) and node.value.id in self.state_vars:
                map_name = node.value.id
            elif isinstance(node.value, ast.Attribute) and isinstance(node.value.value, ast.Name) and node.value.value.id == 'self':
                if node.value.attr in self.state_vars:
                    map_name = node.value.attr
            
            if map_name:
                info = self.state_vars[map_name]
                return self.get_c_type(info['val_type'])

        if isinstance(node, ast.Call):
            # Special case: bytearray(N)
            if isinstance(node.func, ast.Name) and node.func.id == 'bytearray':
                if len(node.args) == 1 and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, int):
                    return f"uint8_t[{node.args[0].value}]"

            # Look up intrinsic return type
            func_name = ""
            class_name = None
            
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
                if isinstance(node.func.value, ast.Name):
                    class_name = node.func.value.id
            
            ret_type = infer_intrinsic_return_type(class_name, func_name)
            if ret_type:
                return ret_type
            
        return 'void*' # Fallback