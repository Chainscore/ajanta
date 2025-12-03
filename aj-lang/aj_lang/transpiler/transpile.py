import ast
import inspect
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

from aj_lang.semantics import (
    SemanticAnalyzer, AnalysisResult, JamType, 
    resolve_type, SemanticError
)
from aj_lang.intrinsics import get_intrinsic, infer_intrinsic_return_type
from .code_gen import CCodeGenerator


def transpile_service(service_class: type) -> str:
    """Transpile a Python service class to C code."""
    
    if not hasattr(service_class, '_jam_meta'):
        raise ValueError(f"{service_class.__name__} is not a JAM service")
    
    meta = service_class._jam_meta
    
    # 1. Collect Structs
    structs = {}
    # We need to find all structs defined in the module or imported
    # For now, let's assume they are available in the module of the service class
    module = inspect.getmodule(service_class)
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and hasattr(obj, '_jam_struct'):
            structs[name] = obj

    # 2. Collect State Variables
    state_vars = {}
    # Parse class body for type annotations
    source = inspect.getsource(service_class)
    tree = ast.parse(inspect.cleandoc(source))
    class_def = tree.body[0]
    
    for stmt in class_def.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            var_name = stmt.target.id
            # Parse annotation to get type
            # e.g. U64, Mapping[U64, U64]
            type_node = stmt.annotation
            
            var_type = 'U64' # Default
            key_type = None
            val_type = None
            is_map = False
            is_struct = False
            
            if isinstance(type_node, ast.Name):
                var_type = type_node.id
                if var_type in structs:
                    is_struct = True
            elif isinstance(type_node, ast.Subscript):
                # Mapping[K, V]
                if isinstance(type_node.value, ast.Name) and type_node.value.id == 'Mapping':
                    is_map = True
                    # Get K, V
                    if isinstance(type_node.slice, ast.Tuple):
                        k_node, v_node = type_node.slice.elts
                        key_type = k_node.id if isinstance(k_node, ast.Name) else 'U64'
                        val_type = v_node.id if isinstance(v_node, ast.Name) else 'U64'
                    else:
                        # Python < 3.9 or single arg? Mapping usually takes 2
                        pass

            state_vars[var_name] = {
                'type': var_type,
                'is_map': is_map,
                'is_struct': is_struct,
                'key_type': key_type,
                'val_type': val_type
            }

    # 3. Generate C Code
    c_code = []
    c_code.append('// Generated from Python')
    c_code.append('#include <jam_sdk.c>')
    c_code.append('#include <jam_state_vars.h>')
    c_code.append('')
    c_code.append('static uint8_t _ret_buf[256];')
    c_code.append('jam_refine_result_t ok_u64(uint64_t val) {')
    c_code.append('    *(uint64_t*)_ret_buf = val;')
    c_code.append('    return (jam_refine_result_t){(uint64_t)_ret_buf, 8};')
    c_code.append('}')
    c_code.append('jam_refine_result_t ok_struct(void* ptr, uint64_t size) {')
    c_code.append('    if (size > sizeof(_ret_buf)) return error(0xFF);')
    c_code.append('    mem_cpy(_ret_buf, ptr, size);')
    c_code.append('    return (jam_refine_result_t){(uint64_t)_ret_buf, size};')
    c_code.append('}')
    c_code.append('')
    
    # Struct Definitions
    for name, cls in structs.items():
        c_code.append(f'typedef struct {{')
        # Get fields from dataclass/annotations
        # We need to parse the struct class source too to get order and types
        struct_source = inspect.getsource(cls)
        struct_tree = ast.parse(inspect.cleandoc(struct_source))
        struct_def = struct_tree.body[0]
        
        gen = CCodeGenerator("", structs=structs)
        for stmt in struct_def.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                field_name = stmt.target.id
                field_type = 'uint64_t'
                if isinstance(stmt.annotation, ast.Name):
                    field_type = gen.get_c_type(stmt.annotation.id)
                c_code.append(f'    {field_type} {field_name};')
        
        c_code.append(f'}} {name};')
        c_code.append('')

    # State Definition Macro
    c_code.append(f'#define {meta.name.upper()}_STATE(X) \\')
    for name, info in state_vars.items():
        if info['is_map']:
            # X(MAP, name, key_type, val_type)
            # Map types need to be C types
            gen = CCodeGenerator("")
            kt = gen.get_c_type(info['key_type'])
            vt = gen.get_c_type(info['val_type'])
            c_code.append(f'    X(MAP, {name}, {kt}, {vt}) \\')
        elif info['is_struct']:
            c_code.append(f'    X(STRUCT, {name}, {info["type"]}) \\')
        elif info['type'] == 'U64':
            c_code.append(f'    X(U64, {name}) \\')
        elif info['type'] == 'bool':
            c_code.append(f'    X(BOOL, {name}) \\')
        else:
            # Default to U64 for now
            c_code.append(f'    X(U64, {name}) \\')
    
    c_code.append('')
    c_code.append(f'DEFINE_STATE({meta.name.upper()}_STATE)')
    c_code.append('')

    # Methods
    gen = CCodeGenerator(meta.name, state_vars=state_vars, structs=structs)
    
    if meta.refine_method:
        c_code.append('REFINE_FN {')
        method = meta.methods[meta.refine_method]
        source = inspect.getsource(method)
        tree = ast.parse(inspect.cleandoc(source))
        gen.visit(tree.body[0]) # Visit FunctionDef
        c_code.extend(gen.output)
        c_code.append('}')
        c_code.append('')

    if meta.accumulate_method:
        c_code.append('ACCUMULATE_FN {')
        # ...
        c_code.append('}')
        c_code.append('')

    if meta.on_transfer_method:
        c_code.append('ON_TRANSFER_FN {')
        # ...
        c_code.append('}')
        c_code.append('')

    return '\n'.join(c_code)
