/**
 * @file jam_log.h
 * @brief JAM Logging Module - Minimal logging for JAM services
 * 
 * Usage:
 *   LOG_INFO("Service started");
 *   LOG_UINT("gas", gas());
 *   
 *   // For hex, use jam_str's hex_encode:
 *   char hex[65];
 *   hex_encode(hash, 32, hex, 16);
 *   LOG_STR("hash", hex);
 */

#ifndef JAM_LOG_H
#define JAM_LOG_H

#include <stdint.h>
#include "jam_str.h"

#ifdef __cplusplus
extern "C" {
#endif

// --- Log Levels ---

#define LOG_LEVEL_ERROR   0
#define LOG_LEVEL_WARN    1
#define LOG_LEVEL_INFO    2
#define LOG_LEVEL_DEBUG   3
#define LOG_LEVEL_TRACE   4

// --- Core Functions ---

/** @brief Log raw message with level and target */
void jam_log_raw(uint64_t level, const char* target, const char* msg);

/** @brief Log message at level */
void jam_log(uint64_t level, const char* msg);

// --- Level-specific logging ---

static inline void jam_log_error(const char* msg) { jam_log(LOG_LEVEL_ERROR, msg); }
static inline void jam_log_warn(const char* msg)  { jam_log(LOG_LEVEL_WARN, msg); }
static inline void jam_log_info(const char* msg)  { jam_log(LOG_LEVEL_INFO, msg); }
static inline void jam_log_debug(const char* msg) { jam_log(LOG_LEVEL_DEBUG, msg); }

// --- Formatted logging (uses internal buffer) ---

/** @brief Log "label: value" for uint */
void jam_log_uint(uint64_t level, const char* label, uint64_t value);

/** @brief Log "label: value" for int */
void jam_log_int(uint64_t level, const char* label, int64_t value);

/** @brief Log "label: str" */
void jam_log_str(uint64_t level, const char* label, const char* value);

/** @brief Log "label: hex..." for binary data */
void jam_log_hex(uint64_t level, const char* label, const uint8_t* data, uint64_t len, uint64_t max_bytes);

/** @brief Log bytes as ASCII text */
void jam_log_bytes(uint64_t level, const char* label, const uint8_t* data, uint64_t len);

// --- Convenience Macros ---

#define LOG_ERROR(msg)      jam_log_error(msg)
#define LOG_WARN(msg)       jam_log_warn(msg)
#define LOG_INFO(msg)       jam_log_info(msg)
#define LOG_DEBUG(msg)      jam_log_debug(msg)

#define LOG_UINT(label, val)        jam_log_uint(LOG_LEVEL_INFO, label, val)
#define LOG_INT(label, val)         jam_log_int(LOG_LEVEL_INFO, label, val)
#define LOG_STR(label, val)         jam_log_str(LOG_LEVEL_INFO, label, val)
#define LOG_HEX(label, data, len)   jam_log_hex(LOG_LEVEL_INFO, label, data, len, 16)
#define LOG_BYTES(label, data, len) jam_log_bytes(LOG_LEVEL_INFO, label, data, len)

#define LOG_DEBUG_UINT(label, val)  jam_log_uint(LOG_LEVEL_DEBUG, label, val)
#define LOG_DEBUG_INT(label, val)   jam_log_int(LOG_LEVEL_DEBUG, label, val)
#define LOG_DEBUG_STR(label, val)   jam_log_str(LOG_LEVEL_DEBUG, label, val)
#define LOG_DEBUG_HEX(label, d, l)  jam_log_hex(LOG_LEVEL_DEBUG, label, d, l, 16)

#define LOG_ERROR_STR(label, val)   jam_log_str(LOG_LEVEL_ERROR, label, val)

// Aliases for compatibility
#define LOG_INFO_UINT(label, val)   LOG_UINT(label, val)
#define LOG_INFO_STR(label, val)    LOG_STR(label, val)

#ifdef __cplusplus
}
#endif

#endif // JAM_LOG_H
