/**
 * @file jam_sdk.h
 * @brief JAM SDK - Complete service development kit
 * 
 * Include this single header to get all SDK functionality:
 * - Host call bindings (jam_pvm.h)
 * - String utilities (jam_str.h) 
 * - Logging utilities (jam_log.h)
 * - Codec for encoding/decoding (jam_codec.h)
 * - Service types and argument structures (jam_service.h)
 * - Runtime entry points (jam_runtime.h)
 * 
 * Usage:
 *   #include "jam_sdk.h"
 *   
 *   jam_refine_result_t jam_hook_refine(
 *       uint32_t item_index, uint32_t service_id,
 *       const uint8_t* payload, uint64_t payload_len,
 *       const uint8_t* work_package_hash
 *   ) {
 *       LOG_INFO("Refine called");
 *       LOG_UINT("item_index", item_index);
 *       LOG_HEX("wp_hash", work_package_hash, 32);
 *       // Your refine implementation
 *   }
 *   
 *   void jam_hook_accumulate(uint32_t timeslot, uint32_t service_id, uint64_t num_inputs) {
 *       LOG_INFO("Accumulate called");
 *   }
 *   
 *   void jam_hook_on_transfer(uint32_t sender, uint32_t receiver,
 *                             uint64_t amount, const uint8_t* memo, uint64_t memo_len) {
 *       LOG_UINT("transfer_amount", amount);
 *   }
 */

#ifndef JAM_SDK_H
#define JAM_SDK_H

#include "jam_pvm.h"
#include "jam_str.h"
#include "jam_log.h"
#include "jam_codec.h"
#include "jam_storage.h"
#include "jam_state.h"
#include "jam_service.h"
#include "jam_runtime.h"

#endif // JAM_SDK_H
