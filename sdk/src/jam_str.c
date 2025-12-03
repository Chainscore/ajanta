/**
 * @file jam_str.c
 * @brief JAM String Utilities Implementation
 */

#include "jam_str.h"

// --- Length & Copy ---

uint64_t str_len(const char* s) {
    if (!s) return 0;
    uint64_t len = 0;
    while (s[len]) len++;
    return len;
}

char* str_cpy(char* dest, const char* src) {
    char* d = dest;
    if (src) {
        while (*src) *d++ = *src++;
    }
    *d = '\0';
    return dest;
}

char* str_cat(char* dest, const char* src) {
    char* d = dest;
    while (*d) d++;
    if (src) {
        while (*src) *d++ = *src++;
    }
    *d = '\0';
    return dest;
}

void* mem_cpy(void* dest, const void* src, uint64_t n) {
    uint8_t* d = (uint8_t*)dest;
    const uint8_t* s = (const uint8_t*)src;
    for (uint64_t i = 0; i < n; i++) d[i] = s[i];
    return dest;
}

void* mem_set(void* dest, int val, uint64_t n) {
    uint8_t* d = (uint8_t*)dest;
    for (uint64_t i = 0; i < n; i++) d[i] = (uint8_t)val;
    return dest;
}

// --- Conversion ---

uint64_t u64_to_str(uint64_t value, char* buf) {
    char temp[21];
    char* p = temp;
    do {
        *p++ = (char)(value % 10) + '0';
        value /= 10;
    } while (value > 0);
    
    uint64_t len = p - temp;
    char* out = buf;
    while (p > temp) *out++ = *--p;
    *out = '\0';
    return len;
}

uint64_t i64_to_str(int64_t value, char* buf) {
    if (value < 0) {
        *buf++ = '-';
        return 1 + u64_to_str((uint64_t)(-value), buf);
    }
    return u64_to_str((uint64_t)value, buf);
}

static const char _hex[] = "0123456789abcdef";

uint64_t hex_encode(const uint8_t* data, uint64_t len, char* buf, uint64_t max_bytes) {
    uint64_t show = (max_bytes > 0 && len > max_bytes) ? max_bytes : len;
    char* p = buf;
    
    for (uint64_t i = 0; i < show; i++) {
        *p++ = _hex[data[i] >> 4];
        *p++ = _hex[data[i] & 0x0F];
    }
    
    if (max_bytes > 0 && len > max_bytes) {
        *p++ = '.';
        *p++ = '.';
        *p++ = '.';
    }
    *p = '\0';
    return p - buf;
}

static uint8_t _hex_val(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return 10 + c - 'a';
    if (c >= 'A' && c <= 'F') return 10 + c - 'A';
    return 0;
}

uint64_t hex_decode(const char* hex, uint64_t hex_len, uint8_t* out, uint64_t out_len) {
    uint64_t bytes = hex_len / 2;
    if (bytes > out_len) bytes = out_len;
    
    for (uint64_t i = 0; i < bytes; i++) {
        out[i] = (_hex_val(hex[i*2]) << 4) | _hex_val(hex[i*2 + 1]);
    }
    return bytes;
}

// --- Formatting ---

uint64_t fmt_uint(char* buf, const char* label, uint64_t value) {
    char* p = buf;
    p = str_cpy(p, label);
    p += str_len(label);
    *p++ = ':';
    *p++ = ' ';
    p += u64_to_str(value, p);
    return p - buf;
}

uint64_t fmt_int(char* buf, const char* label, int64_t value) {
    char* p = buf;
    p = str_cpy(p, label);
    p += str_len(label);
    *p++ = ':';
    *p++ = ' ';
    p += i64_to_str(value, p);
    return p - buf;
}

uint64_t fmt_hex(char* buf, const char* label, const uint8_t* data, uint64_t len, uint64_t max_bytes) {
    char* p = buf;
    str_cpy(p, label);
    p += str_len(label);
    *p++ = ':';
    *p++ = ' ';
    p += hex_encode(data, len, p, max_bytes);
    return p - buf;
}

uint64_t fmt_str(char* buf, const char* label, const char* value) {
    char* p = buf;
    str_cpy(p, label);
    p += str_len(label);
    *p++ = ':';
    *p++ = ' ';
    str_cpy(p, value ? value : "(null)");
    p += str_len(value ? value : "(null)");
    return p - buf;
}
