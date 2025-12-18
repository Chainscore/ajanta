#!/usr/bin/env python3
from re import RegexFlag
import sys
import os

# Add the current directory to Python path so we can import py_asm
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tsrkit_asm import PyAssembler, ImmKind, Reg, RegMem

def test_basic_operations():
    """Test basic assembler operations"""
    print("=== Testing Basic Operations ===")
    
    asm = PyAssembler()

    asm.push_reg(Reg.0)
    asm.mov_imm(RegMem.Reg(Reg.rax), ImmKind.I8(value = 100))
    
    # Test basic moves
    # asm.mov_imm64(RAX, 42)
    # asm.mov_imm32(RBX, 100)
    # asm.mov_reg(SIZE_64, RCX, RAX)
    # 
    # # Test arithmetic
    # asm.add(SIZE_64, RAX, RBX)
    # asm.sub_imm(RCX, 10)
    # 
    # # Test logical operations
    # asm.and_(SIZE_64, RAX, RBX)
    # asm.or_(SIZE_64, RCX, RDX)
    # asm.xor(SIZE_64, RSI, RDI)
    # 
    # # Test comparison
    # asm.cmp(SIZE_64, RAX, RBX)
    # asm.test(SIZE_64, RCX, RDX)
    # 
    # # Test control flow
    # label1 = asm.forward_declare_label()
    # asm.jcc_rel8(COND_EQUAL, 5)
    # asm.define_label(label1)
    # asm.jcc_label32(COND_NOT_EQUAL, label1)
    # 
    # # Test stack operations
    # asm.push(RAX)
    # asm.pop(RBX)

    # Test return
    # asm.ret()
    
    # Finalize
    code = asm.finalize()
    print(f"Generated Machine Code: {code} of {len(code)} bytes of machine code")
    print("Basic operations test passed!")
    return True
