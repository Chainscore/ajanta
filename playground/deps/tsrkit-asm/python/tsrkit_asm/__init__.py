"""
TSRKit ASM: PolkaVM Assembler Python Bindings

A Python wrapper for the PolkaVM runtime assembler, providing x86-64 assembly generation capabilities.
"""

from .tsrkit_asm import *

__version__ = "0.25.0"
__author__ = "Prasad Kumkar, Chainscore Labs, Jan Bujak, Parity Technologies"
__email__ = "hello@chainscore.finance"

__all__ = [
    # Main assembler class
    "PyAssembler",
] 
