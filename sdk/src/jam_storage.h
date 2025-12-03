/**
 * @file jam_storage.h
 * @brief JAM Storage Module - Typed storage access for JAM services
 * 
 * Provides Solidity-like storage slots with serialization.
 * 
 * Usage:
 *   // Define storage keys
 *   #define KEY_COUNTER "counter"
 *   
 *   // Read/write uint64
 *   uint64_t count = storage_get_u64(KEY_COUNTER, 0);  // 0 is default
 *   storage_set_u64(KEY_COUNTER, count + 1);
 */

#ifndef JAM_STORAGE_H
#define JAM_STORAGE_H

#include <stdint.h>
#include "jam_str.h"

#ifdef __cplusplus
extern "C" {
#endif

// --- Storage Result Codes ---

#define STORAGE_OK        0
#define STORAGE_NOT_FOUND 1
#define STORAGE_ERROR     2

// --- Uint Storage ---

/**
 * @brief Get uint64 from storage
 * @param key Storage key (null-terminated string)
 * @param default_val Value to return if key not found
 * @return Stored value or default_val
 */
uint64_t storage_get_u64(const char* key, uint64_t default_val);

/**
 * @brief Set uint64 in storage
 * @param key Storage key
 * @param value Value to store
 * @return STORAGE_OK on success
 */
uint64_t storage_set_u64(const char* key, uint64_t value);

/**
 * @brief Get uint32 from storage
 */
uint32_t storage_get_u32(const char* key, uint32_t default_val);

/**
 * @brief Set uint32 in storage
 */
uint64_t storage_set_u32(const char* key, uint32_t value);

// --- Bytes Storage ---

/**
 * @brief Get bytes from storage
 * @param key Storage key
 * @param out Output buffer
 * @param out_len Output buffer size
 * @return Number of bytes read, or 0 if not found
 */
uint64_t storage_get_bytes(const char* key, uint8_t* out, uint64_t out_len);

/**
 * @brief Set bytes in storage
 * @param key Storage key
 * @param data Data to store
 * @param len Data length
 * @return STORAGE_OK on success
 */
uint64_t storage_set_bytes(const char* key, const uint8_t* data, uint64_t len);

// --- Delete ---

/**
 * @brief Delete a storage key
 * @param key Storage key
 * @return STORAGE_OK on success, STORAGE_NOT_FOUND if key didn't exist
 */
uint64_t storage_delete(const char* key);

// --- Convenience Macros ---

// Define a storage slot with a name
#define STORAGE_SLOT(name) static const char* SLOT_##name = #name

// Increment a counter and return new value
#define storage_inc_u64(key) ({ \
    uint64_t _v = storage_get_u64(key, 0); \
    storage_set_u64(key, _v + 1); \
    _v + 1; \
})

// Decrement a counter and return new value  
#define storage_dec_u64(key) ({ \
    uint64_t _v = storage_get_u64(key, 0); \
    if (_v > 0) storage_set_u64(key, _v - 1); \
    _v > 0 ? _v - 1 : 0; \
})

#ifdef __cplusplus
}
#endif

#endif // JAM_STORAGE_H
