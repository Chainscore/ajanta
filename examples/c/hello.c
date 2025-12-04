#include "jam_sdk.c"

jam_refine_result_t jam_hook_refine(
    uint32_t item_index,
    uint32_t service_id,
    const uint8_t* payload,
    uint64_t payload_len,
    const uint8_t* work_package_hash
) {
    // Log gas
    LOG_UINT("Gas", gas());
    
    // Log decoded arguments
    LOG_UINT("item_index", item_index);
    LOG_UINT("service_id", service_id);
    LOG_UINT("payload_len", payload_len);
    
    // Log payload as string if printable
    if (payload_len > 0 && payload_len < 100) {
        LOG_BYTES("payload", payload, payload_len);
    }
    
    // Log work package hash as hex
    LOG_HEX("wp_hash", work_package_hash, JAM_HASH_SIZE);
    
    // --- Storage test ---
    char key[] = "mykey";
    char value[] = "myvalue";
    
    uint64_t write_result = set_storage(key, 5, value, 7);
    
    if (write_result == HOST_NONE) {
        LOG_INFO("set_storage: new key created");
    } else if (host_is_error(write_result)) {
        LOG_ERROR_STR("set_storage error", host_result_name(write_result));
    } else {
        LOG_UINT("set_storage: updated, prev_len", write_result);
    }
    
    // Read back
    char buf[32];
    uint64_t read_len = get_storage(0, key, 5, buf, 0, 32);
    
    if (read_len == HOST_NONE) {
        LOG_WARN("get_storage: key not found");
    } else if (host_is_error(read_len)) {
        LOG_ERROR_STR("get_storage error", host_result_name(read_len));
    } else {
        LOG_UINT("read_len", read_len);
        LOG_STR("value", buf);
    }
    
    // Return result
    static char ret_str[] = "Hello JAM!";
    jam_refine_result_t res;
    res.ptr = (uint64_t)ret_str;
    res.len = 10;
    return res;
}

void jam_hook_accumulate(
    uint32_t timeslot,
    uint32_t service_id,
    uint64_t num_inputs
) {
    LOG_INFO("Accumulate called");
    LOG_UINT("timeslot", timeslot);
    LOG_UINT("service_id", service_id);
    LOG_UINT("num_inputs", num_inputs);
}

void jam_hook_on_transfer(uint32_t sender, uint32_t receiver, 
                          uint64_t amount, const uint8_t* memo, uint64_t memo_len) {
    LOG_INFO("On transfer called");
    LOG_UINT("sender", sender);
    LOG_UINT("receiver", receiver);
    LOG_UINT("amount", amount);
    LOG_UINT("memo_len", memo_len);
}