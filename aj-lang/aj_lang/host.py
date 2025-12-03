"""
Host call functions for JAM services.

These functions are the interface to the JAM runtime. During local testing,
they use mock implementations. When compiled, they become actual PVM host calls.
"""

from typing import Optional, Union
from aj_lang.types import ServiceId, Gas, ServiceInfo, Hash, StorageKey, StorageValue

# Global context for local testing
_context = None
_storage: dict[tuple[ServiceId, StorageKey], StorageValue] = {}
_gas_remaining: Gas = Gas(10_000_000)


def set_context(ctx):
    """Set the execution context (used by test harness)."""
    global _context
    _context = ctx


def reset():
    """Reset the mock state (used by test harness)."""
    global _storage, _gas_remaining
    _storage = {}
    _gas_remaining = Gas(10_000_000)


# === Logs ===
LOG_LEVEL_ERROR = 0
LOG_LEVEL_WARN = 1
LOG_LEVEL_INFO = 2
LOG_LEVEL_DEBUG = 3
LOG_LEVEL_TRACE = 4

# === General Host Calls ===

def gas() -> Gas: ...

def LOG_DEBUG(message: Union[str, bytes], level: int = LOG_LEVEL_INFO) -> None: ...
def LOG_INFO(message: Union[str, bytes], level: int = LOG_LEVEL_INFO) -> None: ...
def LOG_WARN(message: Union[str, bytes], level: int = LOG_LEVEL_INFO) -> None: ...
def LOG_ERROR(message: Union[str, bytes], level: int = LOG_LEVEL_INFO) -> None: ...

def LOG_DEBUG_UINT(label: str, value: int) -> None: ...
def LOG_INFO_UINT(label: str, value: int) -> None: ...
def LOG_WARN_UINT(label: str, value: int) -> None: ...
def LOG_ERROR_UINT(label: str, value: int) -> None: ...
def LOG_DEBUG_INT(label: str, value: int) -> None: ...
def LOG_INFO_INT(label: str, value: int) -> None: ...
def LOG_DEBUG_BOOL(label: str, value: int) -> None: ...
def LOG_INFO_BOOL(label: str, value: bool) -> None: ...
def LOG_DEBUG_STR(label: str, value: str) -> None: ...
def LOG_INFO_STR(label: str, value: str) -> None: ...
def LOG_WARN_STR(label: str, value: str) -> None: ...
def LOG_ERROR_STR(label: str, value: str) -> None: ...

# === Storage Host Calls ===

def get_storage(
    service_id: int,
    key: bytes,
    key_len: int,
    out: bytes,
    offset: int,
    length: int
) -> int: ...


def set_storage(key: bytes, key_len: int, value: bytes, value_len: int) -> int: ...


def delete_storage(key: StorageKey) -> Optional[int]: ...


# === Info Host Calls ===

def get_service_info(service_id: Optional[ServiceId] = None) -> Optional[ServiceInfo]: ...


# === Refine-specific Host Calls ===

def historical_lookup(hash: Hash, service_id: Optional[ServiceId] = None) -> Optional[bytes]: ...


def export_segment(data: bytes) -> int: ...


# === Accumulate-specific Host Calls ===

def transfer(receiver: ServiceId, amount: int, gas_limit: Gas, memo: bytes = b"") -> bool: ...


def create_service(
    code_hash: Hash,
    min_gas_accumulate: Gas,
    min_gas_memo: Gas,
    initial_balance: int = 0,
) -> Optional[ServiceId]: ...


def upgrade_service(code_hash: Hash, min_gas_accumulate: Gas, min_gas_memo: Gas) -> bool: ...


# === Host Result Constants (matching C SDK) ===
HOST_NONE = 0xFFFFFFFFFFFFFFFF
HOST_WHAT = 0xFFFFFFFFFFFFFFFE
HOST_OOB = 0xFFFFFFFFFFFFFFFD
HOST_WHO = 0xFFFFFFFFFFFFFFFC
HOST_FULL = 0xFFFFFFFFFFFFFFFB
HOST_CORE = 0xFFFFFFFFFFFFFFFA
HOST_CASH = 0xFFFFFFFFFFFFFFF9
HOST_LOW = 0xFFFFFFFFFFFFFFF8
HOST_HIGH = 0xFFFFFFFFFFFFFFF7
HOST_HUH = 0xFFFFFFFFFFFFFFF6


def host_is_error(result: int) -> bool:
    """Check if a host call result is an error."""
    return result >= HOST_HUH


def host_result_name(result: int) -> str:
    """Get the name of a host result code."""
    names = {
        HOST_NONE: "NONE",
        HOST_WHAT: "WHAT",
        HOST_OOB: "OOB",
        HOST_WHO: "WHO",
        HOST_FULL: "FULL",
        HOST_CORE: "CORE",
        HOST_CASH: "CASH",
        HOST_LOW: "LOW",
        HOST_HIGH: "HIGH",
        HOST_HUH: "HUH",
    }
    return names.get(result, f"UNKNOWN({result})")