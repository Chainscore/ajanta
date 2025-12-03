/**
 * @file jam_storage.c
 * @brief JAM Storage Module Implementation
 */

#include "jam_storage.h"
#include "jam_pvm.h"

// --- Internal Serialization ---

// Encode uint64 as little-endian bytes
static void _encode_u64(uint64_t val, uint8_t* buf) {
    buf[0] = (uint8_t)(val);
    buf[1] = (uint8_t)(val >> 8);
    buf[2] = (uint8_t)(val >> 16);
    buf[3] = (uint8_t)(val >> 24);
    buf[4] = (uint8_t)(val >> 32);
    buf[5] = (uint8_t)(val >> 40);
    buf[6] = (uint8_t)(val >> 48);
    buf[7] = (uint8_t)(val >> 56);
}

// Decode uint64 from little-endian bytes
static uint64_t _decode_u64(const uint8_t* buf) {
    return (uint64_t)buf[0]
         | ((uint64_t)buf[1] << 8)
         | ((uint64_t)buf[2] << 16)
         | ((uint64_t)buf[3] << 24)
         | ((uint64_t)buf[4] << 32)
         | ((uint64_t)buf[5] << 40)
         | ((uint64_t)buf[6] << 48)
         | ((uint64_t)buf[7] << 56);
}

// Encode uint32 as little-endian bytes
static void _encode_u32(uint32_t val, uint8_t* buf) {
    buf[0] = (uint8_t)(val);
    buf[1] = (uint8_t)(val >> 8);
    buf[2] = (uint8_t)(val >> 16);
    buf[3] = (uint8_t)(val >> 24);
}

// Decode uint32 from little-endian bytes
static uint32_t _decode_u32(const uint8_t* buf) {
    return (uint32_t)buf[0]
         | ((uint32_t)buf[1] << 8)
         | ((uint32_t)buf[2] << 16)
         | ((uint32_t)buf[3] << 24);
}

// --- Uint Storage ---

uint64_t storage_get_u64(const char* key, uint64_t default_val) {
    uint8_t buf[8];
    uint64_t key_len = str_len(key);
    
    // Read from storage (service_id=0 means current service)
    uint64_t result = get_storage(0, key, key_len, buf, 0, 8);
    
    // Check for errors or not found
    if (result == HOST_NONE || host_is_error(result)) {
        return default_val;
    }
    
    // Must have exactly 8 bytes for u64
    if (result != 8) {
        return default_val;
    }
    
    return _decode_u64(buf);
}

uint64_t storage_set_u64(const char* key, uint64_t value) {
    uint8_t buf[8];
    _encode_u64(value, buf);
    
    uint64_t key_len = str_len(key);
    uint64_t result = set_storage(key, key_len, buf, 8);
    
    if (host_is_error(result)) {
        return STORAGE_ERROR;
    }
    return STORAGE_OK;
}

uint32_t storage_get_u32(const char* key, uint32_t default_val) {
    uint8_t buf[4];
    uint64_t key_len = str_len(key);
    
    uint64_t result = get_storage(0, key, key_len, buf, 0, 4);
    
    if (result == HOST_NONE || host_is_error(result)) {
        return default_val;
    }
    
    if (result != 4) {
        return default_val;
    }
    
    return _decode_u32(buf);
}

uint64_t storage_set_u32(const char* key, uint32_t value) {
    uint8_t buf[4];
    _encode_u32(value, buf);
    
    uint64_t key_len = str_len(key);
    uint64_t result = set_storage(key, key_len, buf, 4);
    
    if (host_is_error(result)) {
        return STORAGE_ERROR;
    }
    return STORAGE_OK;
}

// --- Bytes Storage ---

uint64_t storage_get_bytes(const char* key, uint8_t* out, uint64_t out_len) {
    uint64_t key_len = str_len(key);
    uint64_t result = get_storage(0, key, key_len, out, 0, out_len);
    
    if (result == HOST_NONE || host_is_error(result)) {
        return 0;
    }
    
    return result;
}

uint64_t storage_set_bytes(const char* key, const uint8_t* data, uint64_t len) {
    uint64_t key_len = str_len(key);
    uint64_t result = set_storage(key, key_len, data, len);
    
    if (host_is_error(result)) {
        return STORAGE_ERROR;
    }
    return STORAGE_OK;
}

// --- Delete ---

uint64_t storage_delete(const char* key) {
    uint64_t key_len = str_len(key);
    // Setting empty value deletes the key
    uint64_t result = set_storage(key, key_len, (void*)0, 0);
    
    if (result == HOST_NONE) {
        return STORAGE_NOT_FOUND;
    }
    if (host_is_error(result)) {
        return STORAGE_ERROR;
    }
    return STORAGE_OK;
}
