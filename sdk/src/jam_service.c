/**
 * @file jam_service.c
 * @brief JAM Service argument decoding implementation
 */

#include "jam_service.h"
#include "jam_codec.h"

// --- String Helpers (for freestanding environment) ---

static uint64_t _strlen(const char* str) {
    uint64_t len = 0;
    while (str[len]) len++;
    return len;
}

static void _strcpy(char* dest, const char* src) {
    while (*src) *dest++ = *src++;
    *dest = '\0';
}

static void _strcat(char* dest, const char* src) {
    while (*dest) dest++;
    while (*src) *dest++ = *src++;
    *dest = '\0';
}

static void _uint_to_str(uint64_t value, char* buffer) {
    char temp[21];
    char* p = temp;
    do {
        *p++ = (char)(value % 10) + '0';
        value /= 10;
    } while (value > 0);
    while (p > temp) {
        *buffer++ = *--p;
    }
    *buffer = '\0';
}

static void _hex_to_str(const uint8_t* data, uint64_t len, char* buffer, uint64_t max_bytes) {
    const char hex[] = "0123456789abcdef";
    uint64_t show = len < max_bytes ? len : max_bytes;
    
    for (uint64_t i = 0; i < show; i++) {
        *buffer++ = hex[data[i] >> 4];
        *buffer++ = hex[data[i] & 0x0F];
    }
    if (len > max_bytes) {
        *buffer++ = '.';
        *buffer++ = '.';
        *buffer++ = '.';
    }
    *buffer = '\0';
}

// --- Refine Arguments ---

codec_result_t jam_decode_refine_args(const uint8_t* buffer, uint64_t length, jam_refine_args_t* args) {
    if (!buffer || !args) return CODEC_ERR_NULL;
    
    codec_decoder_t dec;
    codec_decoder_init(&dec, buffer, length);
    
    codec_result_t res;
    uint64_t value;
    
    // 1. Decode item_index (general int -> uint32)
    res = codec_decode_uint(&dec, &value);
    if (res != CODEC_OK) return res;
    if (value > 0xFFFFFFFF) return CODEC_ERR_OVERFLOW;
    args->item_index = (uint32_t)value;
    
    // 2. Decode service_id (general int -> uint32)
    res = codec_decode_uint(&dec, &value);
    if (res != CODEC_OK) return res;
    if (value > 0xFFFFFFFF) return CODEC_ERR_OVERFLOW;
    args->service_id = (uint32_t)value;
    
    // 3. Decode payload (binary: length-prefixed)
    res = codec_decode_binary(&dec, &args->payload, &args->payload_len);
    if (res != CODEC_OK) return res;
    
    // 4. Decode work_package_hash (fixed 32 bytes)
    res = codec_decode_fixed_binary(&dec, args->work_package_hash, JAM_HASH_SIZE);
    if (res != CODEC_OK) return res;
    
    return CODEC_OK;
}

uint64_t jam_refine_args_fmt(const jam_refine_args_t* args, char* buffer, uint64_t buffer_len) {
    if (!args || !buffer || buffer_len == 0) return 0;
    
    char num_buf[21];
    char* p = buffer;
    uint64_t remaining = buffer_len;
    
    // item_index
    _strcpy(p, "item_index=");
    p += _strlen(p);
    _uint_to_str(args->item_index, num_buf);
    _strcat(p, num_buf);
    p += _strlen(num_buf);
    
    // service_id
    _strcpy(p, ", service_id=");
    p += _strlen(", service_id=");
    _uint_to_str(args->service_id, num_buf);
    _strcpy(p, num_buf);
    p += _strlen(num_buf);
    
    // payload_len
    _strcpy(p, ", payload_len=");
    p += _strlen(", payload_len=");
    _uint_to_str(args->payload_len, num_buf);
    _strcpy(p, num_buf);
    p += _strlen(num_buf);
    
    // work_package_hash (first 8 bytes)
    _strcpy(p, ", wp_hash=");
    p += _strlen(", wp_hash=");
    _hex_to_str(args->work_package_hash, JAM_HASH_SIZE, p, 8);
    
    return _strlen(buffer);
}

// --- Accumulate Arguments ---

codec_result_t jam_decode_accumulate_args(const uint8_t* buffer, uint64_t length, jam_accumulate_args_t* args) {
    if (!buffer || !args) return CODEC_ERR_NULL;
    
    codec_decoder_t dec;
    codec_decoder_init(&dec, buffer, length);
    
    codec_result_t res;
    uint64_t value;
    
    // 1. Decode timeslot (general int -> uint32)
    res = codec_decode_uint(&dec, &value);
    if (res != CODEC_OK) return res;
    if (value > 0xFFFFFFFF) return CODEC_ERR_OVERFLOW;
    args->timeslot = (uint32_t)value;
    
    // 2. Decode service_id (general int -> uint32)
    res = codec_decode_uint(&dec, &value);
    if (res != CODEC_OK) return res;
    if (value > 0xFFFFFFFF) return CODEC_ERR_OVERFLOW;
    args->service_id = (uint32_t)value;
    
    // 3. Decode num_inputs (general int)
    res = codec_decode_uint(&dec, &args->num_inputs);
    if (res != CODEC_OK) return res;
    
    return CODEC_OK;
}

uint64_t jam_accumulate_args_fmt(const jam_accumulate_args_t* args, char* buffer, uint64_t buffer_len) {
    if (!args || !buffer || buffer_len == 0) return 0;
    
    char num_buf[21];
    char* p = buffer;
    
    // timeslot
    _strcpy(p, "timeslot=");
    p += _strlen("timeslot=");
    _uint_to_str(args->timeslot, num_buf);
    _strcpy(p, num_buf);
    p += _strlen(num_buf);
    
    // service_id
    _strcpy(p, ", service_id=");
    p += _strlen(", service_id=");
    _uint_to_str(args->service_id, num_buf);
    _strcpy(p, num_buf);
    p += _strlen(num_buf);
    
    // num_inputs
    _strcpy(p, ", num_inputs=");
    p += _strlen(", num_inputs=");
    _uint_to_str(args->num_inputs, num_buf);
    _strcpy(p, num_buf);
    
    return _strlen(buffer);
}
