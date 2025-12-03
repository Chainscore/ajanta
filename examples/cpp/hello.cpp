/**
 * @file hello.cpp
 * @brief Hello World in C++
 */

extern "C" {
#include "jam_sdk.c"
}
#include "jam_state_vars.h"

// C++ class to demonstrate C++ features
class Greeter {
public:
    Greeter(const char* name) : name_(name) {}
    
    void greet() {
        LOG_INFO("Hello from C++!");
        LOG_INFO(name_);
    }

private:
    const char* name_;
};

// Define empty state for C++ example
#define HELLO_STATE(X)

DEFINE_STATE(HELLO_STATE)

jam_refine_result_t refine(
    uint32_t item_index,
    uint32_t service_id,
    const uint8_t* payload,
    uint64_t payload_len,
    const uint8_t* work_package_hash
) {
    // Use C++ feature (class/object)
    Greeter g("Ajanta");
    g.greet();
    
    return ok_void();
}

void accumulate(uint32_t timeslot, uint32_t service_id, uint64_t num_inputs) {
    // No-op
}

void on_transfer(uint32_t sender, uint32_t receiver, uint64_t amount, const uint8_t* memo, uint64_t memo_len) {
    // No-op
}

EXPORT_REFINE(refine)
EXPORT_ACCUMULATE(accumulate)
EXPORT_ON_TRANSFER(on_transfer)
