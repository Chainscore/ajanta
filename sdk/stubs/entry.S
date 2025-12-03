.section .text
.globl refine_ext
.globl accumulate_ext

// On-transfer handler [to be removed in 0.7]
.globl on_transfer_ext

// By convention, PC=0 is the refine entrypoint and PC=5 is accumulate.
// We place a jump to the user-defined functions and pad with NOPs so that
// accumulate_ext begins 4 instructions (16 bytes) later.

.type refine_ext, @function
refine_ext:
    j refine           // 0 - jump to user refine()
    nop                 // 1 - skip
    nop                 // 2 - skip
    nop                 // 3 - skip
    nop                // 4 instructions total → accumulate_ext starts at PC=5

.type accumulate_ext, @function
accumulate_ext:
    j accumulate       // 5 - jump to user accumulate() 
    nop                 // 6 - skip
    nop                 // 7 - skip
    nop                 // 8 - skip
    nop                 // 9 instructions total → on_transfer_ext starts at PC=10

// Default no-op on_transfer implementation.
.type on_transfer_ext, @function
on_transfer_ext:
    j on_transfer      // 10 - jump to user on_transfer()
    ret                // 11 - return to caller