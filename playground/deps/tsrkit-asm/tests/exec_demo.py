import ctypes
import time
from tsrkit_types import TypedArray, U64
import sys

from vm_ctx import VMContext

sys.path.insert(0, 'tests')

from py_asm import PyAssembler, RAX, RCX, RDI, R8, R9, R15
from py_asm import SIZE_64, LOAD_U64
from allocator import allocate_executable_memory


def assemble_add_program(count: int):
    print(f"=== Compiling ADD Program | Loops = {count} ===")
    
    asm = PyAssembler()
    
    # Load initial values into general-purpose registers (avoid touching RSP)
    asm.mov_imm64(R8, count)   # Limit
    asm.mov_imm64(R9, 0)       # Counter

    # Create a start label to return to after loop ends
    start_label = asm.forward_declare_label()
    
    asm.define_label(start_label)
    # Add 1
    asm.add_imm(R9, 1)
    
    # Jump to start if counter < count
    asm.cmp(SIZE_64, R9, R8)
    asm.jl_label32(start_label)

    # Move result into RAX for function return and return
    asm.mov_reg(SIZE_64, RAX, R9)

    asm.ret()

    code = asm.finalize()

    buf, addr = allocate_executable_memory(code)
    print(f"Add program of size {len(code)}; stored at {addr}")
    
    return buf, addr



def create_callable_function(code_pointer: int, vm_pointer: int):
    asm = PyAssembler()

    # RCX –> code pointer,  R15 –> pointer to VMContext struct
    asm.mov_imm64(RCX, code_pointer)
    asm.mov_imm64(R15, vm_pointer)

    # ----------------------------------------------------------
    # Guest-register mapping (examples, adapt as you need)
    # load  [R15 + 0]  into RDI   (regs[0])
    # load  [R15 + 8]  into RAX   (regs[1])
    # ----------------------------------------------------------
    asm.push(RAX)                                     # save caller RAX
    asm.load(LOAD_U64, RDI, 0, 64, R15, 0)            # RDI <- regs[0]
    asm.load(LOAD_U64, RAX, 0, 64, R15, 8)            # RAX <- regs[1]

    # call the generated program
    asm.call_reg(RCX)

    # ----------------------------------------------------------
    # store back the results
    # store RDI -> [R15 + 0]
    # store RAX -> [R15 + 8]
    # ----------------------------------------------------------
    asm.store(8, 0, 64, R15, 0, RDI)
    asm.store(8, 0, 64, R15, 8, RAX)
    asm.pop(RAX)                                      # restore caller RAX

    asm.ret()

    thunk = asm.finalize()
    buf, addr = allocate_executable_memory(thunk)
    FUNC = ctypes.CFUNCTYPE(ctypes.c_uint64)
    func = FUNC(addr)
    setattr(func, "_exec_buf", buf)                   # pin buffer
    return func



def run_program():
    """
    Execute compiled PVM program and return the result.
    """
    start_time_ns = time.time_ns()

    # Allocate executable memory
    code_buf, code_pointer = assemble_add_program(1_000_000_000)
    
    FUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_uint64)
    func = FUNC_TYPE(code_pointer)


    # Guest VM Context
    vm_ctx = VMContext(
        TypedArray[U64, 4]([U64(0), U64(0), U64(0), U64(0)]),
        U64(0)
    )
    vm_buf, vm_pointer = vm_ctx.store()
    

    print("INITIAL VM", VMContext.decode(vm_buf[:16]))
    
    # Create callable function
    func = create_callable_function(code_pointer, vm_pointer)
    
    # Execute the compiled code
    print("Executing compiled PVM code...")
    result = func()
    print(f"Execution taken {(time.time_ns() - start_time_ns) / (10**6)} ms")

    print("POST VM", VMContext.decode(vm_buf[:16]))
    
    # Create callable function
    # Clean up
    code_buf.close()
    # vm_buf.close()
    
    return result

if __name__ == "__main__":
    run_program()
