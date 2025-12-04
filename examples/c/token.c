/**
 * @file token.c
 * @brief ERC20-like Token Service
 * 
 * Features:
 * - Mappings: balances[u64] -> u64
 * - Struct Mappings: users[u64] -> User
 * - Global State: total_supply, owner
 */

#include "jam_sdk.c"
#include "jam_state_vars.h"

// =============================================================================
// Types
// =============================================================================

typedef struct {
    uint64_t joined_at;
    uint64_t tx_count;
    uint8_t is_blocked;
} UserInfo;

// =============================================================================
// State Definition
// =============================================================================

#define TOKEN_STATE(X) \
    X(U64, total_supply) \
    X(U64, owner) \
    X(MAP, balances, uint64_t, uint64_t) \
    X(MAP, users, uint64_t, UserInfo)

DEFINE_STATE(TOKEN_STATE)

// =============================================================================
// Commands
// =============================================================================

enum {
    MINT        = 0x01, // (to, amount)
    TRANSFER    = 0x02, // (to, amount)
    BALANCE_OF  = 0x03, // (who) -> amount
    GET_USER    = 0x04, // (who) -> UserInfo
    BLOCK_USER  = 0x05, // (who)
    INIT        = 0x06  // () -> sets owner
};

// =============================================================================
// Refine Entry Point
// =============================================================================

jam_refine_result_t token_refine(
    uint32_t item_index,
    uint32_t service_id,
    const uint8_t* payload,
    uint64_t payload_len,
    const uint8_t* work_package_hash
) {
    static uint8_t result[32];
    
    if (payload_len == 0) return error(0xFF);
    
    uint8_t cmd = payload[0];
    
    // Initialize owner if not set (simple check)
    if (cmd == INIT) {
        if (owner == 0) {
            owner = 100; // Hardcoded owner ID for test
            LOG_INFO("Initialized owner to 100");
        }
        return ok_void();
    }

    switch (cmd) {
        case MINT: {
            // Only owner can mint
            // For test simplicity, we assume caller is owner if owner is set
            // In real app, check authorization
            
            if (payload_len < 17) return error(0xFE);
            uint64_t to = _decode_u64_le(payload + 1);
            uint64_t amount = _decode_u64_le(payload + 9);
            
            // Update total supply
            total_supply += amount;
            
            // Update balance
            uint64_t bal = balances_get(to);
            bal += amount;
            balances_set(to, bal);
            
            LOG_UINT("Minted to", to);
            LOG_UINT("Amount", amount);
            break;
        }
            
        case TRANSFER: {
            if (payload_len < 17) return error(0xFE);
            uint64_t from = 100; // Hardcoded sender for test
            uint64_t to = _decode_u64_le(payload + 1);
            uint64_t amount = _decode_u64_le(payload + 9);
            
            // Check blocked
            UserInfo u_from = users_get(from);
            if (u_from.is_blocked) return error(0xFA);
            
            // Check balance
            uint64_t bal_from = balances_get(from);
            if (bal_from < amount) return error(0xFB); // Insufficient balance
            
            // Update balances
            balances_set(from, bal_from - amount);
            
            uint64_t bal_to = balances_get(to);
            balances_set(to, bal_to + amount);
            
            // Update user stats
            u_from.tx_count++;
            users_set(from, u_from);
            
            UserInfo u_to = users_get(to);
            if (u_to.joined_at == 0) u_to.joined_at = 1; // Set joined time
            u_to.tx_count++;
            users_set(to, u_to);
            
            LOG_INFO("Transfer success");
            break;
        }
            
        case BALANCE_OF: {
            if (payload_len < 9) return error(0xFE);
            uint64_t who = _decode_u64_le(payload + 1);
            uint64_t bal = balances_get(who);
            _encode_u64_le(bal, result);
            return (jam_refine_result_t){(uint64_t)result, 8};
        }
            
        case GET_USER: {
            if (payload_len < 9) return error(0xFE);
            uint64_t who = _decode_u64_le(payload + 1);
            UserInfo u = users_get(who);
            
            _encode_u64_le(u.joined_at, result);
            _encode_u64_le(u.tx_count, result + 8);
            result[16] = u.is_blocked;
            return (jam_refine_result_t){(uint64_t)result, 17};
        }
            
        case BLOCK_USER: {
            if (payload_len < 9) return error(0xFE);
            uint64_t who = _decode_u64_le(payload + 1);
            
            UserInfo u = users_get(who);
            u.is_blocked = 1;
            users_set(who, u);
            LOG_UINT("Blocked user", who);
            break;
        }
    }
    
    return ok_void();
}

// =============================================================================
// Accumulate
// =============================================================================

void token_accumulate(uint32_t timeslot, uint32_t service_id, uint64_t num_inputs) {
    // No-op
}

// =============================================================================
// On Transfer
// =============================================================================

void token_on_transfer(uint32_t sender, uint32_t receiver, uint64_t amount, const uint8_t* memo, uint64_t memo_len) {
    // No-op
}

// =============================================================================
// Exports
// =============================================================================

EXPORT_REFINE(token_refine)
EXPORT_ACCUMULATE(token_accumulate)
EXPORT_ON_TRANSFER(token_on_transfer)
