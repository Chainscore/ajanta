#!/usr/bin/env python3
import sys
import os

# Add the current directory to Python path so we can import py_asm
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tsrkit_asm import PyAssembler, RAX, RCX, RDX, RBX, RSP, RBP, RSI, RDI
from tsrkit_asm import SIZE_32, SIZE_64, COND_EQUAL, COND_NOT_EQUAL

def test_basic_operations():
    """Test basic assembler operations"""
    print("=== Testing Basic Operations ===")
    
    asm = PyAssembler()
    
    # Test basic moves
    asm.mov_imm64(RAX, 42)
    asm.mov_imm32(RBX, 100)
    asm.mov_reg(SIZE_64, RCX, RAX)
    
    # Test arithmetic
    asm.add(SIZE_64, RAX, RBX)
    asm.sub_imm(RCX, 10)
    
    # Test logical operations
    asm.and_(SIZE_64, RAX, RBX)
    asm.or_(SIZE_64, RCX, RDX)
    asm.xor(SIZE_64, RSI, RDI)
    
    # Test comparison
    asm.cmp(SIZE_64, RAX, RBX)
    asm.test(SIZE_64, RCX, RDX)
    
    # Test control flow
    label1 = asm.forward_declare_label()
    asm.jcc_rel8(COND_EQUAL, 5)
    asm.define_label(label1)
    asm.jcc_label32(COND_NOT_EQUAL, label1)
    
    # Test stack operations
    asm.push(RAX)
    asm.pop(RBX)
    
    # Test return
    asm.ret()
    
    # Finalize
    code = asm.finalize()
    print(f"Generated {len(code)} bytes of machine code")
    print("Basic operations test passed!")
    return True

def test_memory_operations():
    """Test memory operations"""
    print("=== Testing Memory Operations ===")
    
    asm = PyAssembler()
    
    # Test load/store operations
    asm.mov_imm64(RAX, 0x1000)  # Base address
    asm.mov_imm64(RBX, 42)      # Value to store
    
    # Store value to memory
    asm.store(8, 0, 64, RAX, 0, RBX)  # store RBX to [RAX+0]
    
    # Load value from memory
    asm.load(3, RCX, 0, 64, RAX, 0)  # load [RAX+0] to RCX (LOAD_U64)
    
    # Test LEA
    asm.lea(SIZE_64, RDX, 0, 64, RAX, 16)  # LEA RDX, [RAX+16]
    
    asm.ret()
    
    code = asm.finalize()
    print(f"Generated {len(code)} bytes of machine code")
    print("Memory operations test passed!")
    return True

def test_advanced_operations():
    """Test advanced operations"""
    print("=== Testing Advanced Operations ===")
    
    asm = PyAssembler()
    
    # Test bit operations
    asm.mov_imm64(RAX, 0xFF00FF00)
    asm.bswap(SIZE_64, RAX)
    asm.popcnt(SIZE_64, RBX, RAX)
    
    # Test shift operations
    asm.shl_imm(SIZE_64, RAX, 2)
    asm.shr_imm(SIZE_64, RBX, 1)
    
    # Test multiplication
    asm.mov_imm64(RCX, 10)
    asm.imul(SIZE_64, RAX, RCX)
    
    # Test conditional operations
    asm.cmov(COND_EQUAL, SIZE_64, RDX, RAX)
    asm.setcc(COND_NOT_EQUAL, RSI)
    
    asm.ret()
    
    code = asm.finalize()
    print(f"Generated {len(code)} bytes of machine code")
    print("Advanced operations test passed!")
    return True

def test_assembler_utilities():
    """Test assembler utility functions"""
    print("=== Testing Assembler Utilities ===")
    
    asm = PyAssembler()
    
    # Test initial state
    print(f"Initial length: {asm.len()}")
    print(f"Is empty: {asm.is_empty()}")
    print(f"Origin: {asm.origin()}")
    
    # Add some instructions
    asm.nop()
    asm.nop2()
    asm.nop3()
    
    print(f"Length after NOPs: {asm.len()}")
    print(f"Is empty: {asm.is_empty()}")
    
    # Test labels
    label = asm.forward_declare_label()
    print(f"Created label: {label}")
    
    asm.define_label(label)
    offset = asm.get_label_origin_offset(label)
    print(f"Label offset: {offset}")
    
    asm.ret()
    
    code = asm.finalize()
    print(f"Final code length: {len(code)} bytes")
    print("Assembler utilities test passed!")
    return True
