# TSRKit ASM: PolkaVM Assembler Python Bindings

Python bindings for the PolkaVM runtime assembler, providing high-performance x86-64 assembly generation capabilities.

## Features

- **Runtime Assembly Generation**: Generate x86-64 machine code at runtime
- **Label Support**: Forward declaration and resolution of jump/call targets
- **Full Instruction Set**: Support for common x86-64 instructions including:
  - Basic operations (NOP, RET, SYSCALL)
  - Register operations (PUSH, POP, MOV)
  - Arithmetic (ADD, SUB, AND, OR, XOR, CMP)
  - Control flow (JMP, CALL, conditional jumps)
- **Type Safety**: Complete type stubs for excellent IDE support
- **High Performance**: Built on Rust for maximum speed

## Installation

```bash
pip install tsrkit-asm
```

## Quick Start

```python
from tsrkit_asm import PyAssembler

# Create an assembler instance
asm = PyAssembler()

# Generate a simple function that adds two numbers
asm.mov_reg_imm64(py_asm.RAX, 42)
asm.mov_reg_imm64(py_asm.RBX, 13)
asm.add_reg_reg(64, py_asm.RAX, py_asm.RBX)
asm.ret()

# Get the machine code
machine_code = asm.finalize()
print(f"Generated {len(machine_code)} bytes of machine code")
```

## Advanced Usage

### Using Labels for Control Flow

```python
from tsrkit_asm import PyAssembler

asm = PyAssembler()

# Create labels for a loop
loop_start = asm.forward_declare_label()
loop_end = asm.forward_declare_label()

# Initialize counter in RAX
asm.mov_reg_imm64(py_asm.RAX, 10)

# Loop start
asm.define_label(loop_start)
asm.sub_reg_imm(py_asm.RAX, 1)
asm.cmp_reg_imm(py_asm.RAX, 0)
asm.jne_label32(loop_start)

# Loop end
asm.define_label(loop_end)
asm.ret()

machine_code = asm.finalize()
```

## License

This project is licensed under Apache-2.0.

## Contributing

Contributions are welcome! Please see the main PolkaVM repository for contribution guidelines.
