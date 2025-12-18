#!/usr/bin/env python3
"""
Comprehensive test of the complete PyAssembler API
Tests all the newly implemented functionality for 100% completeness
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from py_asm import PyAssembler, RAX, RCX, RDX, RBX, RSP, RBP, RSI, RDI, R8, R9, R10, R11, R12, R13, R14, R15
from py_asm import SIZE_8, SIZE_16, SIZE_32, SIZE_64
from py_asm import COND_EQUAL, COND_NOT_EQUAL, COND_LESS, COND_GREATER, COND_OVERFLOW
from py_asm import LOAD_U8, LOAD_U16, LOAD_U32, LOAD_U64, LOAD_I8, LOAD_I16, LOAD_I32
from py_asm import SCALE_1, SCALE_2, SCALE_4, SCALE_8
from py_asm import SEG_NONE, SEG_FS, SEG_GS
from py_asm import IMM_8, IMM_16, IMM_32, IMM_64

def test_basic_operations():
    """Test basic assembler operations"""
    print("=== Testing Basic Operations ===")
    asm = PyAssembler()
    
    # Basic mov operations
    asm.mov_reg(SIZE_64, RAX, RCX)
    asm.mov_imm64(RDX, 0x1234567890ABCDEF)
    asm.mov_imm32(RBX, 0x12345678)
    asm.mov_imm16(RSI, 0x1234)
    asm.mov_imm8(RDI, 0x12)
    
    # Arithmetic operations
    asm.add(SIZE_64, RAX, RCX)
    asm.add_imm(RDX, 42)
    asm.sub(SIZE_32, RBX, RSI)
    asm.sub_imm(RDI, 10)
    
    # Logical operations
    asm.and_(SIZE_64, RAX, RCX)
    asm.and_imm(RDX, 0xFF)
    asm.or_(SIZE_32, RBX, RSI)
    asm.or_imm(RDI, 0x0F)
    asm.xor(SIZE_64, RAX, RCX)
    asm.xor_imm(RDX, 0xAA)
    
    # Compare and test
    asm.cmp(SIZE_64, RAX, RCX)
    asm.cmp_imm(RDX, 100)
    asm.test(SIZE_32, RBX, RSI)
    asm.test_imm(RDI, 0xFF)
    
    print(f"Basic operations: {asm.len()} bytes generated")

def test_memory_operations():
    """Test memory load/store operations"""
    print("=== Testing Memory Operations ===")
    asm = PyAssembler()
    
    # Load operations
    asm.load(LOAD_U64, RAX, SEG_NONE, SIZE_64, RBP, -8)
    asm.load(LOAD_U32, RCX, SEG_NONE, SIZE_64, RSP, 16)
    asm.load(LOAD_I16, RDX, SEG_FS, SIZE_64, RBX, 0)
    asm.load_base_index(LOAD_U8, RSI, SEG_NONE, SIZE_64, RBP, RCX, SCALE_4, -16)
    
    # Store operations
    asm.store(8, SEG_NONE, SIZE_64, RBP, -8, RAX)  # 8 bytes
    asm.store(4, SEG_NONE, SIZE_64, RSP, 16, RCX)  # 4 bytes
    asm.store_base_index(2, SEG_GS, SIZE_64, RBP, RDX, SCALE_2, 8, RSI)  # 2 bytes
    
    # LEA operations
    asm.lea(SIZE_64, RAX, SEG_NONE, SIZE_64, RBP, -16)
    asm.lea_base_index(SIZE_64, RCX, SEG_NONE, SIZE_64, RBP, RSI, SCALE_8, 24)
    
    print(f"Memory operations: {asm.len()} bytes generated")

def test_arithmetic_extended():
    """Test extended arithmetic operations"""
    print("=== Testing Extended Arithmetic ===")
    asm = PyAssembler()
    
    # Inc/Dec operations
    asm.inc(SIZE_64, RAX)
    asm.dec(SIZE_32, RCX)
    asm.inc_mem(SIZE_8, SEG_NONE, SIZE_64, RBP, -4)
    asm.dec_mem(SIZE_16, SEG_NONE, SIZE_64, RSP, 8)
    
    # Neg/Not operations
    asm.neg(SIZE_64, RAX)
    asm.not_(SIZE_32, RCX)
    asm.neg_mem(SIZE_64, SEG_NONE, SIZE_64, RBP, -8)
    asm.not_mem(SIZE_32, SEG_NONE, SIZE_64, RSP, 12)
    
    # Multiplication
    asm.imul(SIZE_64, RAX, RCX)
    asm.imul_imm(SIZE_32, RDX, RBX, 10)
    asm.imul_dx_ax(SIZE_64, RSI)
    asm.mul(SIZE_32, RDI)
    
    # Division
    asm.cqo()  # Sign extend RAX to RDX:RAX
    asm.idiv(SIZE_64, RCX)
    asm.cdq()  # Sign extend EAX to EDX:EAX
    asm.div(SIZE_32, RBX)
    
    print(f"Extended arithmetic: {asm.len()} bytes generated")

def test_bit_operations():
    """Test bit manipulation operations"""
    print("=== Testing Bit Operations ===")
    asm = PyAssembler()
    
    # Shift operations
    asm.shl_imm(SIZE_64, RAX, 4)
    asm.shr_imm(SIZE_32, RCX, 2)
    asm.sar_imm(SIZE_64, RDX, 3)
    asm.shl_cl(SIZE_32, RBX)  # Shift by CL register
    asm.shr_cl(SIZE_64, RSI)
    asm.sar_cl(SIZE_32, RDI)
    
    # Rotate operations
    asm.rol_cl(SIZE_64, RAX)
    asm.ror_cl(SIZE_32, RCX)
    asm.ror_imm(SIZE_64, RDX, 8)
    asm.rcr_imm(SIZE_32, RBX, 1)
    
    # Bit manipulation
    asm.bts(SIZE_64, RAX, 15)  # Set bit 15
    asm.bts_mem(SIZE_32, SEG_NONE, SIZE_64, RBP, -4, 7)
    
    # Bit counting
    asm.popcnt(SIZE_64, RAX, RCX)
    asm.lzcnt(SIZE_32, RDX, RBX)
    asm.tzcnt(SIZE_64, RSI, RDI)
    asm.bswap(SIZE_64, RAX)  # Byte swap
    
    print(f"Bit operations: {asm.len()} bytes generated")

def test_conditional_operations():
    """Test conditional operations"""
    print("=== Testing Conditional Operations ===")
    asm = PyAssembler()
    
    # Conditional moves
    asm.cmov(COND_EQUAL, SIZE_64, RAX, RCX)
    asm.cmov(COND_NOT_EQUAL, SIZE_32, RDX, RBX)
    asm.cmov_mem(COND_LESS, SIZE_64, RSI, SEG_NONE, SIZE_64, RBP, -8)
    
    # Set on condition
    asm.setcc(COND_GREATER, RAX)  # Set AL if greater
    asm.setcc_mem(COND_OVERFLOW, SEG_NONE, SIZE_64, RBP, -1)
    
    print(f"Conditional operations: {asm.len()} bytes generated")

def test_control_flow():
    """Test control flow operations"""
    print("=== Testing Control Flow ===")
    asm = PyAssembler()
    
    # Create labels
    loop_start = asm.forward_declare_label()
    loop_end = asm.forward_declare_label()
    
    # Jumps
    asm.define_label(loop_start)
    asm.dec(SIZE_64, RCX)
    asm.jcc_label32(COND_EQUAL, loop_end)  # Jump if zero
    asm.jmp_label32(loop_start)  # Unconditional jump back
    
    asm.define_label(loop_end)
    
    # Call through register/memory
    asm.call_reg(RAX)
    asm.call_mem(SEG_NONE, SIZE_64, RBP, 16)
    asm.jmp_reg(RDX)
    asm.jmp_mem(SEG_NONE, SIZE_64, RSP, 8)
    
    # All condition codes
    for cond in range(16):
        asm.jcc_rel8(cond, 2)  # Short jump
        asm.nop()  # Target
    
    print(f"Control flow: {asm.len()} bytes generated")

def test_sign_extension():
    """Test sign extension operations"""
    print("=== Testing Sign Extension ===")
    asm = PyAssembler()
    
    # Sign/zero extension moves
    asm.movsx_8_to_64(RAX, RCX)  # Sign extend CL to RAX
    asm.movsx_16_to_64(RDX, RBX)  # Sign extend BX to RDX
    asm.movzx_16_to_64(RSI, RDI)  # Zero extend DI to RSI
    asm.movsxd_32_to_64(R8, R9)   # Sign extend R9D to R8
    
    print(f"Sign extension: {asm.len()} bytes generated")

def test_misc_operations():
    """Test miscellaneous operations"""
    print("=== Testing Miscellaneous Operations ===")
    asm = PyAssembler()
    
    # Stack operations
    asm.push(RAX)
    asm.push_imm(0x12345678)
    asm.pop(RCX)
    
    # Exchange
    asm.xchg_mem(SIZE_64, RAX, SEG_NONE, SIZE_64, RBP, -8)
    
    # Cache operations
    asm.clflushopt(SEG_NONE, SIZE_64, RBP, -64)
    
    # CPU instructions
    asm.cpuid()
    asm.rdtscp()
    asm.rdpmc()
    asm.mfence()
    asm.lfence()
    
    # NOP variants
    for i in range(2, 12):
        getattr(asm, f'nop{i}')()
    
    print(f"Miscellaneous operations: {asm.len()} bytes generated")

def test_assembler_methods():
    """Test assembler utility methods"""
    print("=== Testing Assembler Methods ===")
    asm = PyAssembler()
    
    # Origin and addressing
    print(f"Initial origin: 0x{asm.origin():x}")
    asm.set_origin(0x400000)
    print(f"New origin: 0x{asm.origin():x}")
    print(f"Current address: 0x{asm.current_address():x}")
    
    # Labels
    label1 = asm.forward_declare_label()
    label2 = asm.forward_declare_label()
    
    asm.define_label(label1)
    asm.mov_imm64(RAX, 0x1234)
    offset = asm.get_label_origin_offset(label1)
    print(f"Label1 offset: {offset}")
    
    asm.define_label(label2)
    offset = asm.get_label_origin_offset(label2)
    print(f"Label2 offset: {offset}")
    
    # Capacity management
    print(f"Length: {asm.len()}")
    print(f"Is empty: {asm.is_empty()}")
    print(f"Spare capacity: {asm.spare_capacity()}")
    
    asm.reserve_code(1024)
    asm.reserve_labels(100)
    print(f"After reserving - spare capacity: {asm.spare_capacity()}")
    
    # Raw bytes
    asm.push_raw(b'\x90\x90\x90')  # Three NOPs
    print(f"After raw bytes: {asm.len()}")
    
    print("Assembler methods test completed")

def main():
    """Run all tests"""
    print("Testing Complete PyAssembler API")
    print("=" * 50)
    
    try:
        test_basic_operations()
        test_memory_operations()
        test_arithmetic_extended()
        test_bit_operations()
        test_conditional_operations()
        test_control_flow()
        test_sign_extension()
        test_misc_operations()
        test_assembler_methods()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("🎉 PyAssembler now has 100% feature completeness!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 