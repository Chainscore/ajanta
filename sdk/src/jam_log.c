/**
 * @file jam_log.c
 * @brief JAM Logging Module Implementation
 */

#include "jam_log.h"
#include "jam_pvm.h"

// --- Log Buffer ---

#define LOG_BUF_SIZE 256
static char _log_buf[LOG_BUF_SIZE];

// --- Core Logging ---

void jam_log_raw(uint64_t level, const char* target, const char* msg) {
    uint64_t target_len = target ? str_len(target) : 0;
    uint64_t msg_len = msg ? str_len(msg) : 0;
    log_raw(level, target, target_len, msg, msg_len);
}

void jam_log(uint64_t level, const char* msg) {
    jam_log_raw(level, "jam", msg);
}

// --- Formatted Logging ---

void jam_log_uint(uint64_t level, const char* label, uint64_t value) {
    fmt_uint(_log_buf, label, value);
    jam_log(level, _log_buf);
}

void jam_log_int(uint64_t level, const char* label, int64_t value) {
    fmt_int(_log_buf, label, value);
    jam_log(level, _log_buf);
}

void jam_log_str(uint64_t level, const char* label, const char* value) {
    fmt_str(_log_buf, label, value);
    jam_log(level, _log_buf);
}

void jam_log_hex(uint64_t level, const char* label, const uint8_t* data, uint64_t len, uint64_t max_bytes) {
    fmt_hex(_log_buf, label, data, len, max_bytes);
    jam_log(level, _log_buf);
}

void jam_log_bytes(uint64_t level, const char* label, const uint8_t* data, uint64_t len) {
    char* p = _log_buf;
    str_cpy(p, label);
    p += str_len(label);
    *p++ = ':';
    *p++ = ' ';
    
    uint64_t max_len = LOG_BUF_SIZE - (p - _log_buf) - 1;
    uint64_t copy_len = (len > max_len) ? max_len : len;
    mem_cpy(p, data, copy_len);
    p[copy_len] = '\0';
    
    jam_log(level, _log_buf);
}
