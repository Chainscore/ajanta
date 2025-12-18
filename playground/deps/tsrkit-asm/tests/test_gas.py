#!/usr/bin/env python3
"""
Simple Gas Metering Test

Tests the basic functionality of the "crazy option" gas metering implementation.
"""

import sys
import os
import signal

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

import pvm_asm
from pvm_asm import registers as reg
from pvm_opcodes import PVMOpcodes
from exec_demo import allocate_executable_memory, create_callable_function


class GasExhaustionError(Exception):
    """Raised when gas is exhausted during execution"""
    pass


def signal_handler(signum, frame):
    """Handle segfault caused by out-of-gas condition"""
    if signum == signal.SIGSEGV:
        raise GasExhaustionError("Out of gas - execution terminated")


def test_basic_gas_metering():
    """Test basic gas metering functionality"""
    print("Testing basic gas metering...")
    
    # Set up signal handler
    old_handler = signal.signal(signal.SIGSEGV, signal_handler)
    
    try:
        # Create assembler with gas metering enabled
        asm = pvm_asm.PyAssembler(is_64_bit=True)
        pvm = PVMOpcodes(asm, enable_gas=True)
        
        # Initialize with exactly 3 gas (for 3 instructions)
        pvm.init_gas_context(3)
        
        # Execute 3 instructions (should work)
        pvm.load_imm(reg.R0, 42)    # 1 gas
        pvm.load_imm(reg.R1, 17)    # 1 gas  
        pvm.add(reg.R8, reg.R0, reg.R1)  # 1 gas, result in RAX
        
        asm.ret()  # No gas check for return
        
        # Compile and execute
        code = asm.finalize()
        buf = allocate_executable_memory(code)
        func = create_callable_function(buf)
        
        try:
            result = func()
            print(f"✓ SUCCESS: Executed with exact gas limit, result = {result}")
        except GasExhaustionError:
            print("✗ FAILED: Ran out of gas unexpectedly")
        
        buf.close()
        
    finally:
        signal.signal(signal.SIGSEGV, old_handler)


def test_gas_exhaustion():
    """Test that gas exhaustion properly triggers segfault"""
    print("Testing gas exhaustion...")
    
    # Set up signal handler
    old_handler = signal.signal(signal.SIGSEGV, signal_handler)
    
    try:
        # Create assembler with gas metering enabled
        asm = pvm_asm.PyAssembler(is_64_bit=True)
        pvm = PVMOpcodes(asm, enable_gas=True)
        
        # Initialize with only 2 gas (but we need 3)
        pvm.init_gas_context(2)
        
        # Try to execute 3 instructions (should fail on the 3rd)
        pvm.load_imm(reg.R0, 42)    # 1 gas
        pvm.load_imm(reg.R1, 17)    # 1 gas
        pvm.add(reg.R8, reg.R0, reg.R1)  # Should trigger out-of-gas
        
        asm.ret()
        
        # Compile and execute
        code = asm.finalize()
        buf = allocate_executable_memory(code)
        func = create_callable_function(buf)
        
        try:
            result = func()
            print(f"✗ FAILED: Should have run out of gas, but got result = {result}")
        except GasExhaustionError:
            print("✓ SUCCESS: Out of gas condition properly detected")
        
        buf.close()
        
    finally:
        signal.signal(signal.SIGSEGV, old_handler)


def test_no_gas_metering():
    """Test that code works normally without gas metering"""
    print("Testing without gas metering...")
    
    # Create assembler without gas metering
    asm = pvm_asm.PyAssembler(is_64_bit=True)
    pvm = PVMOpcodes(asm, enable_gas=False)  # No gas metering
    
    # Execute instructions without gas checks
    pvm.load_imm(reg.R0, 42)
    pvm.load_imm(reg.R1, 17)
    pvm.add(reg.R8, reg.R0, reg.R1)
    
    asm.ret()
    
    # Compile and execute
    code = asm.finalize()
    buf = allocate_executable_memory(code)
    func = create_callable_function(buf)
    
    result = func()
    print(f"✓ SUCCESS: No gas metering works, result = {result}")
    
    buf.close()


if __name__ == "__main__":
    print("Gas Metering Test Suite")
    print("=" * 40)
    
    test_no_gas_metering()
    print()
    test_basic_gas_metering()
    print()
    test_gas_exhaustion()
    print()
    print("Test suite complete!") 