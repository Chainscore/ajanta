"""
JAM SDK Type definitions.

These types map to JAM protocol types and are used for type checking
and code generation.
"""

from typing import NewType, TypeVar, Generic
from dataclasses import dataclass

# Basic integer types
U8 = NewType('U8', int)
U16 = NewType('U16', int)
U32 = NewType('U32', int)
class U64(int):
    """64-bit unsigned integer."""
    pass
I32 = NewType('I32', int)
I64 = NewType('I64', int)

# Protocol types
ServiceId = NewType('ServiceId', int)
Gas = NewType('Gas', int)
Balance = NewType('Balance', int)
TimeSlot = NewType('TimeSlot', int)

# Hash types
Hash = bytes  # 32 bytes
OpaqueHash = bytes  # 32 bytes
CodeHash = bytes  # 32 bytes

# Blob types  
Bytes = bytes
Blob = bytes


# Storage key/value types
StorageKey = bytes
StorageValue = bytes

# Mapping type for state variables
K = TypeVar('K')
V = TypeVar('V')
class Mapping(Generic[K, V]):
    """
    Represents a persistent mapping in JAM state.
    
    Usage:
        balances: Mapping[U64, U64]
    """
    def __getitem__(self, key: K) -> V:
        return None # type: ignore
        
    def __setitem__(self, key: K, value: V):
        pass


@dataclass
class RefineContext:
    """Context passed to refine function."""
    core_index: U32
    work_item_index: U32
    service_id: ServiceId
    payload: bytes
    payload_len: U64
    package_hash: Hash


@dataclass
class AccumulateItem:
    """Item passed to accumulate function."""
    package_hash: Hash
    output: bytes
    output_len: int
    ok: bool


@dataclass
class ServiceInfo:
    """Service account information."""
    code_hash: CodeHash
    balance: Balance
    gas_limit: Gas
    min_gas: Gas
    storage_items: U32
    storage_bytes: U64
    gratis_offset: Balance
    created_at: TimeSlot
    accumulated_at: TimeSlot
    parent_service: ServiceId


# Result type for refine
@dataclass
class RefineResult:
    """Result returned from refine function."""
    data: bytes
    
    def __bytes__(self) -> bytes:
        return self.data


# Segment for exports
Segment = bytes  # 4096 bytes


# Constants
MAX_SEGMENT_SIZE = 4096
MAX_STORAGE_KEY_SIZE = 256
MAX_STORAGE_VALUE_SIZE = 4096
HASH_SIZE = 32
