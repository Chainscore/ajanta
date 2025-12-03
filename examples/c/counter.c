/**
 * @file counter.c
 * @brief Counter Service - Native C Syntax with Automated State
 * 
 * Features:
 * - No manual state_load() / state_save()
 * - Native C syntax (counter++, counter = 100)
 * - Clean entry points
 */

#include "../include/jam_sdk.c"
#include "../include/jam_state_vars.h"

// Undefine macros from jam_state.h if they conflict
#undef counter
#undef paused
#undef admin

// =============================================================================
// State Definition
// =============================================================================

typedef struct {
    uint64_t id;
    uint64_t balance;
} User;

#define MY_STATE(X) \
    X(U64, counter) \
    X(BOOL, paused) \
    X(STRUCT, admin, User)

DEFINE_STATE(MY_STATE)

// =============================================================================
// Commands
// =============================================================================

enum {
    INC     = 0x01,
    DEC     = 0x02,
    SET     = 0x03,
    GET     = 0x04,
    PAUSE   = 0x05,
    UNPAUSE = 0x06,
    SET_ADMIN = 0x07,
    GET_ADMIN = 0x08
};

// =============================================================================
// Refine Entry Point - Automated!
// =============================================================================

REFINE_FN {
    static uint8_t result[16]; // Increased for struct return

    LOG_INFO_UINT("Initial counter", counter);
    
    if (payload_len == 0) {
        result[0] = 0xFF;
        return (jam_refine_result_t){(uint64_t)result, 1};
    }
    
    uint8_t cmd = payload[0];
    
    // Check paused - native syntax!
    if (paused && cmd != UNPAUSE && cmd != GET && cmd != GET_ADMIN) {
        result[0] = 0xFE;
        return (jam_refine_result_t){(uint64_t)result, 1};
    }
    
    switch (cmd) {
        case INC:
            counter++;
            LOG_INFO("incremented");
            break;
            
        case DEC:
            counter--;
            LOG_INFO("decremented");
            break;
            
        case SET:
            if (payload_len >= 9) {
                counter = _decode_u64_le(payload + 1);
                LOG_UINT("set to", counter);
            }
            break;
            
        case GET:
            break;
            
        case PAUSE:
            paused = 1;
            LOG_INFO("paused");
            break;
            
        case UNPAUSE:
            paused = 0;
            LOG_INFO("unpaused");
            break;

        case SET_ADMIN:
            if (payload_len >= 17) {
                admin.id = _decode_u64_le(payload + 1);
                admin.balance = _decode_u64_le(payload + 9);
                LOG_UINT("admin id set", admin.id);
                LOG_UINT("admin balance set", admin.balance);
            }
            break;

        case GET_ADMIN:
            _encode_u64_le(admin.id, result);
            _encode_u64_le(admin.balance, result + 8);
            return (jam_refine_result_t){(uint64_t)result, 16};
    }
    
    _encode_u64_le(counter, result);
    return (jam_refine_result_t){(uint64_t)result, 8};
}

// =============================================================================
// Accumulate - Automated!
// =============================================================================

ACCUMULATE_FN {
    LOG_UINT("final_counter", counter);
}

// =============================================================================
// On Transfer - Automated!
// =============================================================================

ON_TRANSFER_FN {
    // counter++;
}
