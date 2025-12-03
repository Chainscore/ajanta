/**
 * @file jam_str.h
 * @brief JAM String Utilities - Essential string functions for freestanding C
 * 
 * Provides basic string manipulation without libc dependency.
 */

#ifndef JAM_STR_H
#define JAM_STR_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// --- Length & Copy ---

/** @brief Get string length */
uint64_t str_len(const char* s);

/** @brief Copy string, returns dest */
char* str_cpy(char* dest, const char* src);

/** @brief Concatenate strings, returns dest */
char* str_cat(char* dest, const char* src);

/** @brief Copy n bytes */
void* mem_cpy(void* dest, const void* src, uint64_t n);

/** @brief Set n bytes to value */
void* mem_set(void* dest, int val, uint64_t n);

// --- Conversion ---

/** @brief Convert uint64 to decimal string, returns chars written */
uint64_t u64_to_str(uint64_t value, char* buf);

/** @brief Convert int64 to decimal string, returns chars written */
uint64_t i64_to_str(int64_t value, char* buf);

/** @brief Convert bytes to hex string, returns chars written */
uint64_t hex_encode(const uint8_t* data, uint64_t len, char* buf, uint64_t max_bytes);

/** @brief Decode hex string to bytes, returns bytes written */
uint64_t hex_decode(const char* hex, uint64_t hex_len, uint8_t* out, uint64_t out_len);

// --- Formatting (writes to buffer, returns chars written) ---

/** @brief Format: "label: value" */
uint64_t fmt_uint(char* buf, const char* label, uint64_t value);

/** @brief Format: "label: value" for signed int */
uint64_t fmt_int(char* buf, const char* label, int64_t value);

/** @brief Format: "label: hex..." */
uint64_t fmt_hex(char* buf, const char* label, const uint8_t* data, uint64_t len, uint64_t max_bytes);

/** @brief Format: "label: str" */
uint64_t fmt_str(char* buf, const char* label, const char* value);

#ifdef __cplusplus
}
#endif

#endif // JAM_STR_H
