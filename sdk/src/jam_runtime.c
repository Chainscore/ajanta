/**
 * @file jam_runtime.c
 * @brief JAM Runtime - Entry point preprocessor implementation
 * 
 * This file implements the runtime entry points that decode arguments
 * and call the user's service hooks.
 */

#include "jam_runtime.h"
#include "jam_service.h"
#include "jam_codec.h"
#include "jam_pvm.h"

// --- Refine Entry Point ---

jam_refine_result_t _jam_entry_refine(uint8_t* arg_ptr, uint64_t arg_len) {
    jam_refine_args_t args;
    jam_refine_result_t error_result = {0, 0};
    
    // Decode arguments
    codec_result_t res = jam_decode_refine_args(arg_ptr, arg_len, &args);
    if (res != CODEC_OK) {
        // Log the error
        log_msg("ERROR: Failed to decode refine arguments");
        
        // Log error details
        char buf[64];
        char* p = buf;
        const char* prefix = "Codec error: ";
        while (*prefix) *p++ = *prefix++;
        const char* err_name = codec_result_name(res);
        while (*err_name) *p++ = *err_name++;
        *p = '\0';
        log_msg(buf);
        
        return error_result;
    }
    
    // Optional: Log decoded arguments for debugging
    #ifdef JAM_DEBUG
    char fmt_buf[256];
    jam_refine_args_fmt(&args, fmt_buf, sizeof(fmt_buf));
    log_msg(fmt_buf);
    #endif
    
    // Call user's refine hook with individual arguments
    return jam_hook_refine(
        args.item_index,
        args.service_id,
        args.payload,
        args.payload_len,
        args.work_package_hash
    );
}

// --- Accumulate Entry Point ---

void _jam_entry_accumulate(uint8_t* arg_ptr, uint64_t arg_len) {
    jam_accumulate_args_t args;
    
    // Decode arguments
    codec_result_t res = jam_decode_accumulate_args(arg_ptr, arg_len, &args);
    if (res != CODEC_OK) {
        log_msg("ERROR: Failed to decode accumulate arguments");
        return;
    }
    
    // Optional: Log decoded arguments for debugging
    #ifdef JAM_DEBUG
    char fmt_buf[256];
    jam_accumulate_args_fmt(&args, fmt_buf, sizeof(fmt_buf));
    log_msg(fmt_buf);
    #endif
    
    // Call user's accumulate hook with individual arguments
    jam_hook_accumulate(
        args.timeslot,
        args.service_id,
        args.num_inputs
    );
}

// --- On-Transfer Entry Point ---

void _jam_entry_on_transfer(uint8_t* arg_ptr, uint64_t arg_len) {
    // TODO: Implement on_transfer argument decoding
    // For now, call with empty args
    jam_hook_on_transfer(0, 0, 0, (uint8_t*)0, 0);
}

// --- Entry Point Wrappers ---
// These bridge from the legacy entry.S names to the SDK runtime

jam_refine_result_t refine(uint8_t* arg_ptr, uint64_t arg_len) {
    return _jam_entry_refine(arg_ptr, arg_len);
}

void accumulate(uint8_t* arg_ptr, uint64_t arg_len) {
    _jam_entry_accumulate(arg_ptr, arg_len);
}

void on_transfer(uint8_t* arg_ptr, uint64_t arg_len) {
    _jam_entry_on_transfer(arg_ptr, arg_len);
}
