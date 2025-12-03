.section .polkavm_metadata
.align 3
refine_symbol:
    .string "refine_ext"

.align 3
accumulate_symbol:
    .string "accumulate_ext"

.align 3
on_transfer_symbol:
    .string "on_transfer_ext"

// -----------------------------------------------------------------------------
// Export metadata structures (ExternMetadataV1) -- version = 1, no flags.
// struct ExternMetadataV1 {
//     uint32_t version;
//     uint32_t flags;
//     uint32_t symbol_length;
//     const char *symbol;
//     uint8_t input_regs;
//     uint8_t output_regs;
// };
// For simplicity all funcs take/return via memory → input_regs = 0, output_regs = 0.
// -----------------------------------------------------------------------------

.align 3
refine_metadata:
    .byte 1               /* version */
    /* flags (u32 little-endian) */
    .byte 0, 0, 0, 0
    /* symbol length = 10 */
    .byte 10, 0, 0, 0
    .quad refine_symbol   /* symbol pointer */
    .byte 0               /* input_regs */
    .byte 0               /* output_regs */

.align 3
accumulate_metadata:
    .byte 1
    .byte 0, 0, 0, 0       /* flags */
    /* symbol length = 14 */
    .byte 14, 0, 0, 0
    .quad accumulate_symbol
    .byte 0
    .byte 0

.align 3
on_transfer_metadata:
    .byte 1
    .byte 0, 0, 0, 0       /* flags */
    /* symbol length = 15 */
    .byte 15, 0, 0, 0
    .quad on_transfer_symbol
    .byte 0
    .byte 0

// -----------------------------------------------------------------------------
// Export table (.polkavm_exports) entries: (metadata ptr, function ptr)
// -----------------------------------------------------------------------------

.section .polkavm_exports,"Ra",@note
    // Entry 0: refine
    .byte 1
    .quad refine_metadata
    .quad refine_ext

    // Entry 1: accumulate
    .byte 1
    .quad accumulate_metadata
    .quad accumulate_ext

    // Entry 2: on_transfer
    .byte 1
    .quad on_transfer_metadata
    .quad on_transfer_ext
    // .align 3 
    /* omit final .align to avoid extraneous zero padding */ 