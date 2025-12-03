/**
 * @file jam_state.h
 * @brief JAM State Module - Solidity-like typed storage variables
 * 
 * Provides near-native variable syntax for persistent storage.
 * 
 * Usage:
 *   // Declare state variables
 *   STATE_U64(counter);
 *   STATE_BOOL(paused);
 *   
 *   // Read - just use the name!
 *   uint64_t x = counter;      // reads from storage
 *   if (paused) { ... }        // reads bool
 *   
 *   // Write
 *   SET(counter, 42);          // writes to storage
 *   SET(counter, counter + 1); // increment
 *   
 *   // Convenience
 *   INC(counter);              // counter++
 *   DEC(counter);              // counter--
 */

#ifndef JAM_STATE_H
#define JAM_STATE_H

#include <stdint.h>
#include "jam_str.h"
#include "jam_pvm.h"

#ifdef __cplusplus
extern "C" {
#endif

// =============================================================================
// Internal: Storage encoding/decoding
// =============================================================================

static inline void _encode_u64_le(uint64_t val, uint8_t* buf) {
    for (int i = 0; i < 8; i++) buf[i] = (uint8_t)(val >> (i * 8));
}

static inline uint64_t _decode_u64_le(const uint8_t* buf) {
    uint64_t val = 0;
    for (int i = 0; i < 8; i++) val |= ((uint64_t)buf[i]) << (i * 8);
    return val;
}

static inline void _encode_u32_le(uint32_t val, uint8_t* buf) {
    for (int i = 0; i < 4; i++) buf[i] = (uint8_t)(val >> (i * 8));
}

static inline uint32_t _decode_u32_le(const uint8_t* buf) {
    uint32_t val = 0;
    for (int i = 0; i < 4; i++) val |= ((uint32_t)buf[i]) << (i * 8);
    return val;
}

// =============================================================================
// State Variable Declaration Macros
// =============================================================================

#define STATE_U64(name) \
    static const char _k_##name[] = #name; \
    static inline uint64_t _get_##name(void) { \
        uint8_t _b[8]; \
        uint64_t _r = get_storage(0, _k_##name, sizeof(_k_##name)-1, _b, 0, 8); \
        return (_r == HOST_NONE || host_is_error(_r) || _r != 8) ? 0 : _decode_u64_le(_b); \
    } \
    static inline void _set_##name(uint64_t _v) { \
        uint8_t _b[8]; \
        _encode_u64_le(_v, _b); \
        set_storage(_k_##name, sizeof(_k_##name)-1, _b, 8); \
    } \
    typedef int _dummy_##name

#define STATE_U32(name) \
    static const char _k_##name[] = #name; \
    static inline uint32_t _get_##name(void) { \
        uint8_t _b[4]; \
        uint64_t _r = get_storage(0, _k_##name, sizeof(_k_##name)-1, _b, 0, 4); \
        return (_r == HOST_NONE || host_is_error(_r) || _r != 4) ? 0 : _decode_u32_le(_b); \
    } \
    static inline void _set_##name(uint32_t _v) { \
        uint8_t _b[4]; \
        _encode_u32_le(_v, _b); \
        set_storage(_k_##name, sizeof(_k_##name)-1, _b, 4); \
    } \
    typedef int _dummy_##name

#define STATE_BOOL(name) \
    static const char _k_##name[] = #name; \
    static inline int _get_##name(void) { \
        uint8_t _b[1]; \
        uint64_t _r = get_storage(0, _k_##name, sizeof(_k_##name)-1, _b, 0, 1); \
        return (_r == HOST_NONE || host_is_error(_r) || _r != 1) ? 0 : (_b[0] != 0); \
    } \
    static inline void _set_##name(int _v) { \
        uint8_t _b[1] = { _v ? 1 : 0 }; \
        set_storage(_k_##name, sizeof(_k_##name)-1, _b, 1); \
    } \
    typedef int _dummy_##name

// =============================================================================
// Access Macros
// =============================================================================

// Generic getter: $(my_var) reads any state variable
#define $(name) _get_##name()

// WRITE: SET(counter, 42) or SET(counter, counter + 1)
#define SET(name, val) _set_##name(val)

// MODIFY: Shortcuts for common operations
#define INC(name)       do { _set_##name(_get_##name() + 1); } while(0)
#define DEC(name)       do { uint64_t _v = _get_##name(); if (_v > 0) _set_##name(_v - 1); } while(0)
#define ADD(name, n)    do { _set_##name(_get_##name() + (n)); } while(0)
#define SUB(name, n)    do { _set_##name(_get_##name() - (n)); } while(0)
#define TOGGLE(name)    do { _set_##name(!_get_##name()); } while(0)

// =============================================================================
// Mapping support: mapping(bytes => uint64)
// =============================================================================

#define MAP_U64(name) \
    static const char _mp_##name[] = #name ":"; \
    static inline uint64_t _mget_##name(const void* _key, uint64_t _klen) { \
        char _fk[64]; \
        uint64_t _plen = sizeof(_mp_##name) - 1; \
        mem_cpy(_fk, _mp_##name, _plen); \
        uint64_t _clen = _klen > (64 - _plen) ? (64 - _plen) : _klen; \
        mem_cpy(_fk + _plen, _key, _clen); \
        uint8_t _b[8]; \
        uint64_t _r = get_storage(0, _fk, _plen + _clen, _b, 0, 8); \
        return (_r == HOST_NONE || host_is_error(_r) || _r != 8) ? 0 : _decode_u64_le(_b); \
    } \
    static inline void _mset_##name(const void* _key, uint64_t _klen, uint64_t _v) { \
        char _fk[64]; \
        uint64_t _plen = sizeof(_mp_##name) - 1; \
        mem_cpy(_fk, _mp_##name, _plen); \
        uint64_t _clen = _klen > (64 - _plen) ? (64 - _plen) : _klen; \
        mem_cpy(_fk + _plen, _key, _clen); \
        uint8_t _b[8]; \
        _encode_u64_le(_v, _b); \
        set_storage(_fk, _plen + _clen, _b, 8); \
    } \
    typedef int _dummy_##name

#define MAP_GET(name, key, klen)        _mget_##name(key, klen)
#define MAP_SET(name, key, klen, val)   _mset_##name(key, klen, val)
#define MAP_ADD(name, key, klen, n)     do { _mset_##name(key, klen, _mget_##name(key, klen) + (n)); } while(0)

#ifdef __cplusplus
}
#endif

#endif // JAM_STATE_H
