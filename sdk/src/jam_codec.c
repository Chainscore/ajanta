/**
 * @file jam_codec.c
 * @brief JAM Codec implementation
 */

#include "jam_codec.h"

// --- Error Messages ---

const char* codec_result_name(codec_result_t result) {
    switch (result) {
        case CODEC_OK:          return "OK";
        case CODEC_ERR_BUFFER:  return "Buffer too small";
        case CODEC_ERR_OVERFLOW: return "Value overflow";
        case CODEC_ERR_INVALID: return "Invalid encoding";
        case CODEC_ERR_TRAILING: return "Trailing data";
        case CODEC_ERR_NULL:    return "Null pointer";
        default:                return "Unknown error";
    }
}

// --- General Integer Decoding ---

codec_result_t codec_decode_uint(codec_decoder_t* dec, uint64_t* out) {
    if (!dec || !out) return CODEC_ERR_NULL;
    if (!codec_decoder_has(dec, 1)) return CODEC_ERR_BUFFER;
    
    uint8_t tag = dec->buffer[dec->offset];
    
    // Single byte: 0-127
    if (tag < 128) {
        *out = tag;
        dec->offset += 1;
        return CODEC_OK;
    }
    
    // Full 64-bit encoding (tag == 0xFF)
    if (tag == 0xFF) {
        if (!codec_decoder_has(dec, 9)) return CODEC_ERR_BUFFER;
        
        *out = (uint64_t)dec->buffer[dec->offset + 1]
             | ((uint64_t)dec->buffer[dec->offset + 2] << 8)
             | ((uint64_t)dec->buffer[dec->offset + 3] << 16)
             | ((uint64_t)dec->buffer[dec->offset + 4] << 24)
             | ((uint64_t)dec->buffer[dec->offset + 5] << 32)
             | ((uint64_t)dec->buffer[dec->offset + 6] << 40)
             | ((uint64_t)dec->buffer[dec->offset + 7] << 48)
             | ((uint64_t)dec->buffer[dec->offset + 8] << 56);
        dec->offset += 9;
        return CODEC_OK;
    }
    
    // Variable length encoding
    // Calculate l from tag: l = floor(8 - log2(256 - tag))
    // For tag in [128, 191]: l = 1 (2 bytes total)
    // For tag in [192, 223]: l = 2 (3 bytes total)
    // For tag in [224, 239]: l = 3 (4 bytes total)
    // For tag in [240, 247]: l = 4 (5 bytes total)
    // For tag in [248, 251]: l = 5 (6 bytes total)
    // For tag in [252, 253]: l = 6 (7 bytes total)
    // For tag == 254:        l = 7 (8 bytes total)
    
    uint8_t l;
    if (tag < 192) {
        l = 1;
    } else if (tag < 224) {
        l = 2;
    } else if (tag < 240) {
        l = 3;
    } else if (tag < 248) {
        l = 4;
    } else if (tag < 252) {
        l = 5;
    } else if (tag < 254) {
        l = 6;
    } else {
        l = 7; // tag == 254
    }
    
    if (!codec_decoder_has(dec, 1 + l)) return CODEC_ERR_BUFFER;
    
    // alpha = tag + 2^(8-l) - 256
    uint8_t shift = 8 - l;
    uint64_t alpha = tag + (1 << shift) - 256;
    
    // beta = little-endian decode of next l bytes
    uint64_t beta = 0;
    for (uint8_t i = 0; i < l; i++) {
        beta |= ((uint64_t)dec->buffer[dec->offset + 1 + i]) << (8 * i);
    }
    
    // value = alpha * 2^(l*8) + beta
    *out = (alpha << (l * 8)) + beta;
    dec->offset += 1 + l;
    return CODEC_OK;
}

codec_result_t codec_decode_int(codec_decoder_t* dec, int64_t* out) {
    uint64_t uval;
    codec_result_t res = codec_decode_uint(dec, &uval);
    if (res != CODEC_OK) return res;
    
    // Convert from unsigned to signed (two's complement)
    *out = (int64_t)uval;
    return CODEC_OK;
}

// --- Fixed Integer Decoding ---

codec_result_t codec_decode_u8(codec_decoder_t* dec, uint8_t* out) {
    if (!dec || !out) return CODEC_ERR_NULL;
    if (!codec_decoder_has(dec, 1)) return CODEC_ERR_BUFFER;
    
    *out = dec->buffer[dec->offset];
    dec->offset += 1;
    return CODEC_OK;
}

codec_result_t codec_decode_u16(codec_decoder_t* dec, uint16_t* out) {
    if (!dec || !out) return CODEC_ERR_NULL;
    if (!codec_decoder_has(dec, 2)) return CODEC_ERR_BUFFER;
    
    *out = (uint16_t)dec->buffer[dec->offset]
         | ((uint16_t)dec->buffer[dec->offset + 1] << 8);
    dec->offset += 2;
    return CODEC_OK;
}

codec_result_t codec_decode_u32(codec_decoder_t* dec, uint32_t* out) {
    if (!dec || !out) return CODEC_ERR_NULL;
    if (!codec_decoder_has(dec, 4)) return CODEC_ERR_BUFFER;
    
    *out = (uint32_t)dec->buffer[dec->offset]
         | ((uint32_t)dec->buffer[dec->offset + 1] << 8)
         | ((uint32_t)dec->buffer[dec->offset + 2] << 16)
         | ((uint32_t)dec->buffer[dec->offset + 3] << 24);
    dec->offset += 4;
    return CODEC_OK;
}

codec_result_t codec_decode_u64(codec_decoder_t* dec, uint64_t* out) {
    if (!dec || !out) return CODEC_ERR_NULL;
    if (!codec_decoder_has(dec, 8)) return CODEC_ERR_BUFFER;
    
    *out = (uint64_t)dec->buffer[dec->offset]
         | ((uint64_t)dec->buffer[dec->offset + 1] << 8)
         | ((uint64_t)dec->buffer[dec->offset + 2] << 16)
         | ((uint64_t)dec->buffer[dec->offset + 3] << 24)
         | ((uint64_t)dec->buffer[dec->offset + 4] << 32)
         | ((uint64_t)dec->buffer[dec->offset + 5] << 40)
         | ((uint64_t)dec->buffer[dec->offset + 6] << 48)
         | ((uint64_t)dec->buffer[dec->offset + 7] << 56);
    dec->offset += 8;
    return CODEC_OK;
}

// --- Binary Decoding ---

codec_result_t codec_decode_binary(codec_decoder_t* dec, const uint8_t** out_data, uint64_t* out_len) {
    if (!dec || !out_data || !out_len) return CODEC_ERR_NULL;
    
    // Decode length prefix
    uint64_t length;
    codec_result_t res = codec_decode_uint(dec, &length);
    if (res != CODEC_OK) return res;
    
    // Check we have enough data
    if (!codec_decoder_has(dec, length)) return CODEC_ERR_BUFFER;
    
    // Return pointer into buffer (zero-copy)
    *out_data = dec->buffer + dec->offset;
    *out_len = length;
    dec->offset += length;
    
    return CODEC_OK;
}

codec_result_t codec_decode_fixed_binary(codec_decoder_t* dec, uint8_t* out_data, uint64_t expected_len) {
    if (!dec || !out_data) return CODEC_ERR_NULL;
    if (!codec_decoder_has(dec, expected_len)) return CODEC_ERR_BUFFER;
    
    // Copy data to output buffer
    for (uint64_t i = 0; i < expected_len; i++) {
        out_data[i] = dec->buffer[dec->offset + i];
    }
    dec->offset += expected_len;
    
    return CODEC_OK;
}

// --- Boolean Decoding ---

codec_result_t codec_decode_bool(codec_decoder_t* dec, uint8_t* out) {
    if (!dec || !out) return CODEC_ERR_NULL;
    if (!codec_decoder_has(dec, 1)) return CODEC_ERR_BUFFER;
    
    uint8_t val = dec->buffer[dec->offset];
    if (val > 1) return CODEC_ERR_INVALID;
    
    *out = val;
    dec->offset += 1;
    return CODEC_OK;
}

// --- General Integer Encoding ---

uint64_t codec_encode_uint_size(uint64_t value) {
    if (value < 128) return 1;
    if (value < 16384) return 2;
    if (value < 2097152) return 3;
    if (value < 268435456) return 4;
    if (value < 34359738368ULL) return 5;
    if (value < 4398046511104ULL) return 6;
    if (value < 562949953421312ULL) return 7;
    if (value < 72057594037927936ULL) return 8;
    return 9;
}

codec_result_t codec_encode_uint(codec_encoder_t* enc, uint64_t value) {
    if (!enc) return CODEC_ERR_NULL;
    
    uint64_t size = codec_encode_uint_size(value);
    if (codec_encoder_remaining(enc) < size) return CODEC_ERR_BUFFER;
    
    if (value < 128) {
        enc->buffer[enc->offset++] = (uint8_t)value;
        return CODEC_OK;
    }
    
    if (size == 9) {
        // Full 64-bit encoding
        enc->buffer[enc->offset++] = 0xFF;
        for (int i = 0; i < 8; i++) {
            enc->buffer[enc->offset++] = (uint8_t)(value >> (i * 8));
        }
        return CODEC_OK;
    }
    
    // Variable length encoding
    uint8_t l = (uint8_t)(size - 1);
    uint8_t shift = 8 - l;
    
    // alpha = value >> (l * 8)
    uint64_t alpha = value >> (l * 8);
    
    // tag = 256 - 2^shift + alpha
    uint8_t tag = (uint8_t)(256 - (1 << shift) + alpha);
    enc->buffer[enc->offset++] = tag;
    
    // beta = value % 2^(l*8) - little endian
    for (uint8_t i = 0; i < l; i++) {
        enc->buffer[enc->offset++] = (uint8_t)(value >> (i * 8));
    }
    
    return CODEC_OK;
}

// --- Fixed Integer Encoding ---

codec_result_t codec_encode_u8(codec_encoder_t* enc, uint8_t value) {
    if (!enc) return CODEC_ERR_NULL;
    if (codec_encoder_remaining(enc) < 1) return CODEC_ERR_BUFFER;
    
    enc->buffer[enc->offset++] = value;
    return CODEC_OK;
}

codec_result_t codec_encode_u16(codec_encoder_t* enc, uint16_t value) {
    if (!enc) return CODEC_ERR_NULL;
    if (codec_encoder_remaining(enc) < 2) return CODEC_ERR_BUFFER;
    
    enc->buffer[enc->offset++] = (uint8_t)(value);
    enc->buffer[enc->offset++] = (uint8_t)(value >> 8);
    return CODEC_OK;
}

codec_result_t codec_encode_u32(codec_encoder_t* enc, uint32_t value) {
    if (!enc) return CODEC_ERR_NULL;
    if (codec_encoder_remaining(enc) < 4) return CODEC_ERR_BUFFER;
    
    enc->buffer[enc->offset++] = (uint8_t)(value);
    enc->buffer[enc->offset++] = (uint8_t)(value >> 8);
    enc->buffer[enc->offset++] = (uint8_t)(value >> 16);
    enc->buffer[enc->offset++] = (uint8_t)(value >> 24);
    return CODEC_OK;
}

codec_result_t codec_encode_u64(codec_encoder_t* enc, uint64_t value) {
    if (!enc) return CODEC_ERR_NULL;
    if (codec_encoder_remaining(enc) < 8) return CODEC_ERR_BUFFER;
    
    for (int i = 0; i < 8; i++) {
        enc->buffer[enc->offset++] = (uint8_t)(value >> (i * 8));
    }
    return CODEC_OK;
}

// --- Binary Encoding ---

codec_result_t codec_encode_binary(codec_encoder_t* enc, const uint8_t* data, uint64_t len) {
    if (!enc) return CODEC_ERR_NULL;
    
    // Encode length prefix
    codec_result_t res = codec_encode_uint(enc, len);
    if (res != CODEC_OK) return res;
    
    // Encode data
    if (codec_encoder_remaining(enc) < len) return CODEC_ERR_BUFFER;
    
    for (uint64_t i = 0; i < len; i++) {
        enc->buffer[enc->offset++] = data[i];
    }
    
    return CODEC_OK;
}

codec_result_t codec_encode_fixed_binary(codec_encoder_t* enc, const uint8_t* data, uint64_t len) {
    if (!enc) return CODEC_ERR_NULL;
    if (codec_encoder_remaining(enc) < len) return CODEC_ERR_BUFFER;
    
    for (uint64_t i = 0; i < len; i++) {
        enc->buffer[enc->offset++] = data[i];
    }
    
    return CODEC_OK;
}

// --- Boolean Encoding ---

codec_result_t codec_encode_bool(codec_encoder_t* enc, uint8_t value) {
    if (!enc) return CODEC_ERR_NULL;
    if (codec_encoder_remaining(enc) < 1) return CODEC_ERR_BUFFER;
    
    enc->buffer[enc->offset++] = value ? 1 : 0;
    return CODEC_OK;
}
