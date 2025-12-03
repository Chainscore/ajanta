// Runtime stubs for JAM PVM
#include <stdint.h>
#include <stddef.h>
#include "../../src/ajanta/include/polkavm_guest.h"

POLKAVM_IMPORT_WITH_INDEX(0, uint64_t, _gas);
uint64_t gas(void) { return _gas(); }

POLKAVM_IMPORT_WITH_INDEX(3, uint64_t, _get_storage, uint64_t, uint64_t, uint64_t, uint64_t, uint64_t, uint64_t);
uint64_t get_storage(uint64_t service_id, const void* key, uint64_t key_len, void* out, uint64_t out_offset, uint64_t out_len) {
    return _get_storage(service_id, (uint64_t)key, key_len, (uint64_t)out, out_offset, out_len);
}

POLKAVM_IMPORT_WITH_INDEX(4, uint64_t, _set_storage, uint64_t, uint64_t, uint64_t, uint64_t);
uint64_t set_storage(const void* key, uint64_t key_len, const void* value, uint64_t value_len) {
    return _set_storage((uint64_t)key, key_len, (uint64_t)value, value_len);
}

POLKAVM_IMPORT_WITH_INDEX(100, void, _log, uint64_t, uint64_t, uint64_t, uint64_t, uint64_t);
void log_raw(uint64_t level, const void* target, uint64_t target_len, const void* message, uint64_t message_len) {
    _log(level, (uint64_t)target, target_len, (uint64_t)message, message_len);
}

// Helper to get string length
static uint64_t _strlen(const char* s) {
    uint64_t len = 0;
    while (s[len]) len++;
    return len;
}

// Simple log - just message with info level
void log_msg(const char* message) {
    _log(2, 0, 0, (uint64_t)message, _strlen(message));
}

// Log with level
void log_msg_level(uint64_t level, const char* message) {
    _log(level, 0, 0, (uint64_t)message, _strlen(message));
}

// Entry point stub
void _start(void) {
    // This should never be called in PVM context
    while (1) {}
} 