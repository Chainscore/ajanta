/**
 * @file jam_service.h
 * @brief JAM Service types and argument structures
 * 
 * This module defines the data structures used for JAM service entry points:
 * - Refine arguments
 * - Accumulate arguments
 * - On-transfer arguments
 */

#ifndef JAM_SERVICE_H
#define JAM_SERVICE_H

#include <stdint.h>
#include <stddef.h>
#include "jam_codec.h"

#ifdef __cplusplus
extern "C" {
#endif

// --- Constants ---

#define JAM_HASH_SIZE 32

// --- Refine Arguments ---

/**
 * @brief Arguments passed to the refine function
 * 
 * Decoded from the encoded buffer passed via registers.
 * Format: item_index (uint) || service_id (uint) || payload (binary) || work_package_hash (32 bytes)
 */
typedef struct {
    uint32_t item_index;            // Index of this work item in the package
    uint32_t service_id;            // Service ID processing this item
    const uint8_t* payload;         // Pointer to payload data (zero-copy into args buffer)
    uint64_t payload_len;           // Length of payload
    uint8_t work_package_hash[JAM_HASH_SIZE];  // Blake2b hash of the work package
} jam_refine_args_t;

/**
 * @brief Decode refine arguments from encoded buffer
 * 
 * @param buffer Input buffer
 * @param length Buffer length
 * @param args Output arguments structure
 * @return CODEC_OK on success, error code otherwise
 */
codec_result_t jam_decode_refine_args(const uint8_t* buffer, uint64_t length, jam_refine_args_t* args);

/**
 * @brief Format refine arguments as string for logging
 * 
 * @param args Arguments to format
 * @param buffer Output buffer
 * @param buffer_len Output buffer length
 * @return Number of characters written
 */
uint64_t jam_refine_args_fmt(const jam_refine_args_t* args, char* buffer, uint64_t buffer_len);

// --- Accumulate Arguments ---

/**
 * @brief Arguments passed to the accumulate function
 */
typedef struct {
    uint32_t timeslot;      // Current timeslot
    uint32_t service_id;    // Service being accumulated
    uint64_t num_inputs;    // Number of inputs to process
} jam_accumulate_args_t;

/**
 * @brief Decode accumulate arguments from encoded buffer
 */
codec_result_t jam_decode_accumulate_args(const uint8_t* buffer, uint64_t length, jam_accumulate_args_t* args);

/**
 * @brief Format accumulate arguments as string for logging
 */
uint64_t jam_accumulate_args_fmt(const jam_accumulate_args_t* args, char* buffer, uint64_t buffer_len);

// --- Refine Result ---

/**
 * @brief Result returned from refine function
 */
typedef struct {
    uint64_t ptr;   // Pointer to result data
    uint64_t len;   // Length of result data
} jam_refine_result_t;

// --- Service Hooks (to be implemented by user) ---

/**
 * @brief User's refine implementation
 * 
 * This function must be implemented by the service developer.
 * 
 * @param item_index Index of this work item in the package
 * @param service_id Service ID processing this item
 * @param payload Pointer to payload data
 * @param payload_len Length of payload
 * @param work_package_hash Blake2b hash of the work package (32 bytes)
 * @return Refine result with pointer to output data and length
 */
jam_refine_result_t jam_hook_refine(
    uint32_t item_index,
    uint32_t service_id,
    const uint8_t* payload,
    uint64_t payload_len,
    const uint8_t* work_package_hash
);

/**
 * @brief User's accumulate implementation
 * 
 * This function must be implemented by the service developer.
 * 
 * @param timeslot Current timeslot
 * @param service_id Service being accumulated
 * @param num_inputs Number of inputs to process
 */
void jam_hook_accumulate(
    uint32_t timeslot,
    uint32_t service_id,
    uint64_t num_inputs
);

/**
 * @brief User's on_transfer implementation
 * 
 * This function must be implemented by the service developer.
 */
void jam_hook_on_transfer(uint32_t sender, uint32_t receiver, 
                          uint64_t amount, const uint8_t* memo, uint64_t memo_len);

#ifdef __cplusplus
}
#endif

#endif // JAM_SERVICE_H
