/**
 * @file jam_state_vars.h
 * @brief JAM State Variables - Native C syntax for storage
 * 
 * Enables:
 *   counter = 42;
 *   counter++;
 * 
 * Usage:
 *   #define MY_STATE(X) \
 *       X(U64, counter) \
 *       X(BOOL, paused)
 *   
 *   DEFINE_STATE(MY_STATE)
 * 
 *   void hook() {
 *       state_load();
 *       counter = 42;
 *       state_save();
 *   }
 */

#ifndef JAM_STATE_VARS_H
#define JAM_STATE_VARS_H

#include "jam_state.h"

#ifdef __cplusplus
extern "C" {
#endif

// =============================================================================
// Type Definitions
// =============================================================================

#define _TYPE_U64   uint64_t
#define _TYPE_U32   uint32_t
#define _TYPE_BOOL  int

// =============================================================================
// Helpers
// =============================================================================

static inline jam_refine_result_t error(uint8_t code) {
    static uint8_t res[1];
    res[0] = code;
    return (jam_refine_result_t){(uint64_t)res, 1};
}

static inline jam_refine_result_t ok_void(void) {
    static uint8_t res[1];
    res[0] = 0; // OK
    return (jam_refine_result_t){(uint64_t)res, 0}; // Empty result
}

static inline int _mem_cmp(const void* a, const void* b, uint64_t n) {
    const uint8_t* p1 = (const uint8_t*)a;
    const uint8_t* p2 = (const uint8_t*)b;
    for (uint64_t i = 0; i < n; i++) {
        if (p1[i] != p2[i]) return p1[i] - p2[i];
    }
    return 0;
}

// =============================================================================
// Accessor Generators (Internal)
// =============================================================================

#define _GEN_ACCESSOR_U64(name) \
    static const char _k_##name[] = #name; \
    static inline uint64_t _read_##name(void) { \
        uint8_t _b[8]; \
        uint64_t _r = get_storage(0, _k_##name, sizeof(_k_##name)-1, _b, 0, 8); \
        return (_r == HOST_NONE || host_is_error(_r) || _r != 8) ? 0 : _decode_u64_le(_b); \
    } \
    static inline void _write_##name(uint64_t _v) { \
        uint8_t _b[8]; \
        _encode_u64_le(_v, _b); \
        set_storage(_k_##name, sizeof(_k_##name)-1, _b, 8); \
    }

#define _GEN_ACCESSOR_U32(name) \
    static const char _k_##name[] = #name; \
    static inline uint32_t _read_##name(void) { \
        uint8_t _b[4]; \
        uint64_t _r = get_storage(0, _k_##name, sizeof(_k_##name)-1, _b, 0, 4); \
        return (_r == HOST_NONE || host_is_error(_r) || _r != 4) ? 0 : _decode_u32_le(_b); \
    } \
    static inline void _write_##name(uint32_t _v) { \
        uint8_t _b[4]; \
        _encode_u32_le(_v, _b); \
        set_storage(_k_##name, sizeof(_k_##name)-1, _b, 4); \
    }

#define _GEN_ACCESSOR_BOOL(name) \
    static const char _k_##name[] = #name; \
    static inline int _read_##name(void) { \
        uint8_t _b[1]; \
        uint64_t _r = get_storage(0, _k_##name, sizeof(_k_##name)-1, _b, 0, 1); \
        return (_r == HOST_NONE || host_is_error(_r) || _r != 1) ? 0 : (_b[0] != 0); \
    } \
    static inline void _write_##name(int _v) { \
        uint8_t _b[1] = { _v ? 1 : 0 }; \
        set_storage(_k_##name, sizeof(_k_##name)-1, _b, 1); \
    }

#define _GEN_ACCESSOR_STRUCT(name, type) \
    static const char _k_##name[] = #name; \
    static inline type _read_##name(void) { \
        type _v; \
        uint8_t _b[sizeof(type)]; \
        uint64_t _r = get_storage(0, _k_##name, sizeof(_k_##name)-1, _b, 0, sizeof(type)); \
        if (_r == HOST_NONE || host_is_error(_r) || _r != sizeof(type)) { \
            mem_set(&_v, 0, sizeof(type)); \
        } else { \
            mem_cpy(&_v, _b, sizeof(type)); \
        } \
        return _v; \
    } \
    static inline void _write_##name(type _v) { \
        set_storage(_k_##name, sizeof(_k_##name)-1, &_v, sizeof(type)); \
    }

#define _GEN_ACCESSOR_MAP(name, key_type, val_type) \
    static const char _k_##name[] = #name; \
    static inline val_type name##_get(key_type key) { \
        val_type _v; \
        uint8_t _k[sizeof(_k_##name) - 1 + 8]; \
        mem_cpy(_k, _k_##name, sizeof(_k_##name) - 1); \
        _encode_u64_le((uint64_t)key, _k + sizeof(_k_##name) - 1); \
        uint8_t _b[sizeof(val_type)]; \
        uint64_t _r = get_storage(0, _k, sizeof(_k), _b, 0, sizeof(val_type)); \
        if (_r == HOST_NONE || host_is_error(_r) || _r != sizeof(val_type)) { \
            mem_set(&_v, 0, sizeof(val_type)); \
        } else { \
            mem_cpy(&_v, _b, sizeof(val_type)); \
        } \
        return _v; \
    } \
    static inline void name##_set(key_type key, val_type _v) { \
        uint8_t _k[sizeof(_k_##name) - 1 + 8]; \
        mem_cpy(_k, _k_##name, sizeof(_k_##name) - 1); \
        _encode_u64_le((uint64_t)key, _k + sizeof(_k_##name) - 1); \
        set_storage(_k, sizeof(_k), &_v, sizeof(val_type)); \
    }

// Dispatcher
#define _GEN_ACCESSOR(type, name, ...) _GEN_ACCESSOR_##type(name, ##__VA_ARGS__)

// =============================================================================
// Global Variable Generators
// =============================================================================

#define _GEN_GLOBAL_U64(name) uint64_t name; uint64_t _orig_##name;
#define _GEN_GLOBAL_U32(name) uint32_t name; uint32_t _orig_##name;
#define _GEN_GLOBAL_BOOL(name) int name; int _orig_##name;
#define _GEN_GLOBAL_STRUCT(name, type) type name; type _orig_##name;
#define _GEN_GLOBAL_MAP(name, key_type, val_type)

#define _GEN_GLOBAL(type, name, ...) _GEN_GLOBAL_##type(name, ##__VA_ARGS__)

// =============================================================================
// Load/Save Logic
// =============================================================================

#define _GEN_LOAD_U64(name) name = _read_##name(); _orig_##name = name;
#define _GEN_LOAD_U32(name) name = _read_##name(); _orig_##name = name;
#define _GEN_LOAD_BOOL(name) name = _read_##name(); _orig_##name = name;
#define _GEN_LOAD_STRUCT(name, type) name = _read_##name(); _orig_##name = name;
#define _GEN_LOAD_MAP(name, key_type, val_type)

#define _GEN_LOAD(type, name, ...) _GEN_LOAD_##type(name, ##__VA_ARGS__)

#define _GEN_SAVE_U64(name) if (name != _orig_##name) _write_##name(name);
#define _GEN_SAVE_U32(name) if (name != _orig_##name) _write_##name(name);
#define _GEN_SAVE_BOOL(name) if (name != _orig_##name) _write_##name(name);
#define _GEN_SAVE_STRUCT(name, type) if (_mem_cmp(&name, &_orig_##name, sizeof(type)) != 0) _write_##name(name);
#define _GEN_SAVE_MAP(name, key_type, val_type)

#define _GEN_SAVE(type, name, ...) _GEN_SAVE_##type(name, ##__VA_ARGS__)

// =============================================================================
// Main Macro
// =============================================================================

#define DEFINE_STATE(SCHEMA) \
    /* 1. Generate Accessors */ \
    SCHEMA(_GEN_ACCESSOR) \
    \
    /* 2. Generate Globals */ \
    SCHEMA(_GEN_GLOBAL) \
    \
    /* 3. Load Function */ \
    static inline void state_load(void) { \
        SCHEMA(_GEN_LOAD) \
    } \
    \
    /* 4. Save Function */ \
    static inline void state_save(void) { \
        SCHEMA(_GEN_SAVE) \
    }

// =============================================================================
// Entry Point Wrappers - Automate state_load() and state_save()
// =============================================================================

/**
 * EXPORT_REFINE - Export the refine entry point with automatic state management
 * 
 * Usage:
 *   jam_refine_result_t my_refine(uint32_t item_index, uint32_t service_id, ...) {
 *       // ...
 *   }
 *   EXPORT_REFINE(my_refine)
 */
#define EXPORT_REFINE(user_fn) \
    jam_refine_result_t jam_hook_refine( \
        uint32_t item_index, \
        uint32_t service_id, \
        const uint8_t* payload, \
        uint64_t payload_len, \
        const uint8_t* work_package_hash \
    ) { \
        state_load(); \
        jam_refine_result_t res = user_fn(item_index, service_id, payload, payload_len, work_package_hash); \
        state_save(); \
        return res; \
    }

/**
 * EXPORT_ACCUMULATE - Export the accumulate entry point with automatic state management
 */
#define EXPORT_ACCUMULATE(user_fn) \
    void jam_hook_accumulate( \
        uint32_t timeslot, \
        uint32_t service_id, \
        uint64_t num_inputs \
    ) { \
        state_load(); \
        user_fn(timeslot, service_id, num_inputs); \
        state_save(); \
    }

/**
 * EXPORT_ON_TRANSFER - Export the on_transfer entry point with automatic state management
 */
#define EXPORT_ON_TRANSFER(user_fn) \
    void jam_hook_on_transfer( \
        uint32_t sender, \
        uint32_t receiver, \
        uint64_t amount, \
        const uint8_t* memo, \
        uint64_t memo_len \
    ) { \
        state_load(); \
        user_fn(sender, receiver, amount, memo, memo_len); \
        state_save(); \
    }

#ifdef __cplusplus
}
#endif

#endif // JAM_STATE_VARS_H
