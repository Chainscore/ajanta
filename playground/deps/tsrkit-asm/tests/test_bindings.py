#!/usr/bin/env python3

from py_asm import PyAssembler
from disassemble import disassemble_with_objdump

def test_assembler():
    print("Testing PyAssembler...")
    
    # Create assembler instance
    asm = PyAssembler()
    
    # Test label creation
    label1 = asm.forward_declare_label()
    label2 = asm.create_label()
    print(f"Label 1: {label1}")
    print(f"Label 2: {label2}")
    
    # 1. NOP
    asm.nop()
    print(f"After nop, length: {asm.len()}")
    
    # Test register constants
    rax = py_asm.RAX
    rcx = py_asm.RCX
    print(f"RAX: {rax}, RCX: {rcx}")
    
    # 2. push registers
    asm.push(rax)
    asm.push(rcx)
    print(f"After pushes, length: {asm.len()}")
    
    # 3. mov with immediate
    asm.mov_reg_imm64(rax, 0x1234567890abcdef)
    print(f"After mov, length: {asm.len()}")
    
    # 4. pop register values
    asm.pop(rcx)
    asm.pop(rax)
    asm.ret()
    
    print(f"Final length: {asm.len()}")
    
    # Generate machine code
    code = asm.finalize()
    print(f"Generated {len(code)} bytes of machine code")
    
    print(disassemble_with_objdump(code))

if __name__ == "__main__":
    test_assembler()
