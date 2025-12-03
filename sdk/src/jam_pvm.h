#ifndef JAM_PVM_H
#define JAM_PVM_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// --- Host Result Constants ------------------------------------------------
// These are the standard return values from JAM host calls.
// Values are defined as per the JAM specification.

#define HOST_OK     ((uint64_t)0)       // Success
#define HOST_NONE   ((uint64_t)-1)      // Item does not exist / Not found
#define HOST_WHAT   ((uint64_t)-2)      // Invalid argument / Unknown item
#define HOST_OOB    ((uint64_t)-3)      // Out of bounds
#define HOST_WHO    ((uint64_t)-4)      // Unknown service / Invalid service ID
#define HOST_FULL   ((uint64_t)-5)      // Storage full / No space
#define HOST_CORE   ((uint64_t)-6)      // Core error
#define HOST_CASH   ((uint64_t)-7)      // Insufficient balance
#define HOST_LOW    ((uint64_t)-8)      // Insufficient gas
#define HOST_HUH    ((uint64_t)-9)      // General error / Invalid state

// Helper to check if a host result is an error
static inline int host_is_error(uint64_t result) {
    return result >= HOST_HUH;  // All error codes are negative (large positive when unsigned)
}

// Helper to check if result is OK (success or length value)
static inline int host_is_ok(uint64_t result) {
    return result < HOST_HUH;
}

// Get human-readable name for host result
static inline const char* host_result_name(uint64_t result) {
    switch (result) {
        case HOST_OK:   return "OK";
        case HOST_NONE: return "NONE (not found)";
        case HOST_WHAT: return "WHAT (invalid argument)";
        case HOST_OOB:  return "OOB (out of bounds)";
        case HOST_WHO:  return "WHO (unknown service)";
        case HOST_FULL: return "FULL (storage full)";
        case HOST_CORE: return "CORE (core error)";
        case HOST_CASH: return "CASH (insufficient balance)";
        case HOST_LOW:  return "LOW (insufficient gas)";
        case HOST_HUH:  return "HUH (general error)";
        default:        return NULL;  // Not an error code, probably a length
    }
}

// --- Types ----------------------------------------------------------------

// Item produced by workers that accumulate will process.
typedef struct {
    uint8_t package_hash[32];
    const uint8_t *output;
    size_t out_len;
    uint8_t ok; // 1 if refine succeeded, 0 otherwise
} AccumulateItem;

// --- Host-call stubs -------------------------------------------------------
// The JAM runtime implements these functions. The SDK only provides
// declarations so that user code can link.

// Index 0: Gas
uint64_t gas(void);

// Index 3: Read
uint64_t get_storage(uint64_t service_id, const void* key, uint64_t key_len, void* out, uint64_t out_offset, uint64_t out_len);

// Index 4: Write
uint64_t set_storage(const void* key, uint64_t key_len, const void* value, uint64_t value_len);

// Index 100: Log (raw)
void log_raw(uint64_t level, const void* target, uint64_t target_len, const void* message, uint64_t message_len);

// Simple log helper - logs message with default level (info)
void log_msg(const char* message);

// Log with level
void log_msg_level(uint64_t level, const char* message);

// Additional hostcalls can be declared here (e.g., logging, reading storage).

#ifdef __cplusplus
} // extern "C"
#endif

#endif // JAM_PVM_H 