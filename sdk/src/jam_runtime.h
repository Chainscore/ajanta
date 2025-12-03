/**
 * @file jam_runtime.h
 * @brief JAM Runtime entry points and preprocessor
 * 
 * This module provides the entry point functions that are called by the PVM runtime.
 * It handles:
 * - Decoding arguments from registers
 * - Calling user's service hooks
 * - Returning results to the host
 */

#ifndef JAM_RUNTIME_H
#define JAM_RUNTIME_H

#include <stdint.h>
#include "jam_service.h"
#include "jam_pvm.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Entry point for refine invocation
 * 
 * Called by the PVM with encoded arguments:
 * - arg_ptr: Pointer to encoded argument buffer
 * - arg_len: Length of encoded arguments
 * 
 * This function:
 * 1. Decodes the arguments using jam_decode_refine_args()
 * 2. Calls the user's jam_hook_refine() implementation
 * 3. Returns the result via registers
 */
jam_refine_result_t _jam_entry_refine(uint8_t* arg_ptr, uint64_t arg_len);

/**
 * @brief Entry point for accumulate invocation
 */
void _jam_entry_accumulate(uint8_t* arg_ptr, uint64_t arg_len);

/**
 * @brief Entry point for on_transfer invocation
 */
void _jam_entry_on_transfer(uint8_t* arg_ptr, uint64_t arg_len);

#ifdef __cplusplus
}
#endif

#endif // JAM_RUNTIME_H
