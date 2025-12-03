/**
 * @file jam_codec.h
 * @brief JAM Codec - Encoding/Decoding utilities for JAM protocol types
 * 
 * This module implements the JAM serialization format as specified in the 
 * Gray Paper. It provides functions for encoding and decoding:
 * - General integers (variable-length encoding)
 * - Fixed-size integers (u8, u16, u32, u64)
 * - Binary data (length-prefixed and fixed-length)
 * - Booleans
 * 
 * The encoding format follows these rules:
 * - Values 0-127: Single byte
 * - Values 128-16383: 2 bytes (prefix 0x80-0xBF)
 * - Values 16384-536870911: 4 bytes (prefix 0xC0-0xDF)
 * - Values 536870912-2^64-1: 8 bytes (prefix 0xE0-0xEF or 0xFF for full 64-bit)
 * 
 * All multi-byte values use little-endian byte order for the data portion.
 */

#ifndef JAM_CODEC_H
#define JAM_CODEC_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// --- Result Codes ---

#define CODEC_OK            0   // Success
#define CODEC_ERR_BUFFER    1   // Buffer too small
#define CODEC_ERR_OVERFLOW  2   // Value overflow
#define CODEC_ERR_INVALID   3   // Invalid encoding
#define CODEC_ERR_TRAILING  4   // Unexpected trailing data
#define CODEC_ERR_NULL      5   // Null pointer

typedef uint8_t codec_result_t;

// --- Decoder Context ---

/**
 * @brief Decoder context for tracking position in buffer
 */
typedef struct {
    const uint8_t* buffer;  // Pointer to buffer
    uint64_t length;        // Total buffer length
    uint64_t offset;        // Current read position
} codec_decoder_t;

/**
 * @brief Initialize a decoder context
 */
static inline void codec_decoder_init(codec_decoder_t* dec, const uint8_t* buffer, uint64_t length) {
    dec->buffer = buffer;
    dec->length = length;
    dec->offset = 0;
}

/**
 * @brief Get remaining bytes in decoder
 */
static inline uint64_t codec_decoder_remaining(const codec_decoder_t* dec) {
    return dec->length - dec->offset;
}

/**
 * @brief Check if decoder has at least n bytes remaining
 */
static inline int codec_decoder_has(const codec_decoder_t* dec, uint64_t n) {
    return codec_decoder_remaining(dec) >= n;
}

// --- Encoder Context ---

/**
 * @brief Encoder context for tracking position in buffer
 */
typedef struct {
    uint8_t* buffer;        // Pointer to buffer
    uint64_t capacity;      // Buffer capacity
    uint64_t offset;        // Current write position
} codec_encoder_t;

/**
 * @brief Initialize an encoder context
 */
static inline void codec_encoder_init(codec_encoder_t* enc, uint8_t* buffer, uint64_t capacity) {
    enc->buffer = buffer;
    enc->capacity = capacity;
    enc->offset = 0;
}

/**
 * @brief Get remaining capacity in encoder
 */
static inline uint64_t codec_encoder_remaining(const codec_encoder_t* enc) {
    return enc->capacity - enc->offset;
}

// --- General Integer Decoding ---

/**
 * @brief Decode a JAM general integer (variable-length encoding)
 * 
 * @param dec Decoder context
 * @param out Output value
 * @return CODEC_OK on success, error code otherwise
 */
codec_result_t codec_decode_uint(codec_decoder_t* dec, uint64_t* out);

/**
 * @brief Decode a JAM general integer as signed
 * 
 * @param dec Decoder context  
 * @param out Output value
 * @return CODEC_OK on success, error code otherwise
 */
codec_result_t codec_decode_int(codec_decoder_t* dec, int64_t* out);

// --- Fixed Integer Decoding ---

codec_result_t codec_decode_u8(codec_decoder_t* dec, uint8_t* out);
codec_result_t codec_decode_u16(codec_decoder_t* dec, uint16_t* out);
codec_result_t codec_decode_u32(codec_decoder_t* dec, uint32_t* out);
codec_result_t codec_decode_u64(codec_decoder_t* dec, uint64_t* out);

// --- Binary Decoding ---

/**
 * @brief Decode length-prefixed binary data
 * 
 * Note: out_data points into the original buffer (zero-copy)
 * 
 * @param dec Decoder context
 * @param out_data Output pointer to data
 * @param out_len Output data length
 * @return CODEC_OK on success, error code otherwise
 */
codec_result_t codec_decode_binary(codec_decoder_t* dec, const uint8_t** out_data, uint64_t* out_len);

/**
 * @brief Decode fixed-length binary data into provided buffer
 * 
 * @param dec Decoder context
 * @param out_data Output buffer (must be at least expected_len bytes)
 * @param expected_len Expected data length
 * @return CODEC_OK on success, error code otherwise
 */
codec_result_t codec_decode_fixed_binary(codec_decoder_t* dec, uint8_t* out_data, uint64_t expected_len);

// --- Boolean Decoding ---

codec_result_t codec_decode_bool(codec_decoder_t* dec, uint8_t* out);

// --- General Integer Encoding ---

/**
 * @brief Get encoded size for a uint64 value
 */
uint64_t codec_encode_uint_size(uint64_t value);

/**
 * @brief Encode a uint64 as JAM general integer
 */
codec_result_t codec_encode_uint(codec_encoder_t* enc, uint64_t value);

// --- Fixed Integer Encoding ---

codec_result_t codec_encode_u8(codec_encoder_t* enc, uint8_t value);
codec_result_t codec_encode_u16(codec_encoder_t* enc, uint16_t value);
codec_result_t codec_encode_u32(codec_encoder_t* enc, uint32_t value);
codec_result_t codec_encode_u64(codec_encoder_t* enc, uint64_t value);

// --- Binary Encoding ---

/**
 * @brief Encode length-prefixed binary data
 */
codec_result_t codec_encode_binary(codec_encoder_t* enc, const uint8_t* data, uint64_t len);

/**
 * @brief Encode fixed-length binary data (no length prefix)
 */
codec_result_t codec_encode_fixed_binary(codec_encoder_t* enc, const uint8_t* data, uint64_t len);

// --- Boolean Encoding ---

codec_result_t codec_encode_bool(codec_encoder_t* enc, uint8_t value);

// --- Utility Functions ---

/**
 * @brief Get human-readable error message
 */
const char* codec_result_name(codec_result_t result);

#ifdef __cplusplus
}
#endif

#endif // JAM_CODEC_H
