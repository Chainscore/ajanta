"""
Encoding utilities for JAM SDK.
Matches the C SDK's little-endian encoding.
"""

import struct
from typing import Any, Type, get_type_hints
from dataclasses import is_dataclass, fields
from aj_lang.types import U8, U16, U32, U64, I32, I64, Mapping

def encode(value: Any, type_hint: Type) -> bytes:
    """Encode a value to bytes based on its type."""
    if type_hint in (int, U64, I64):
        return value.to_bytes(8, 'little', signed=(type_hint == I64))
    elif type_hint in (U32, I32):
        return value.to_bytes(4, 'little', signed=(type_hint == I32))
    elif type_hint in (U16,):
        return value.to_bytes(2, 'little')
    elif type_hint in (U8,):
        return value.to_bytes(1, 'little')
    elif type_hint == bool:
        return b'\x01' if value else b'\x00'
    elif type_hint == bytes:
        return value
    elif is_dataclass(type_hint):
        # Encode fields in order
        result = bytearray()
        for f in fields(type_hint):
            val = getattr(value, f.name)
            result.extend(encode(val, f.type))
        return bytes(result)
    else:
        raise TypeError(f"Unsupported type for encoding: {type_hint}")

def decode(data: bytes, type_hint: Type) -> Any:
    """Decode bytes to a value based on its type."""
    if type_hint in (int, U64, I64):
        return int.from_bytes(data[:8], 'little', signed=(type_hint == I64))
    elif type_hint in (U32, I32):
        return int.from_bytes(data[:4], 'little', signed=(type_hint == I32))
    elif type_hint in (U16,):
        return int.from_bytes(data[:2], 'little')
    elif type_hint in (U8,):
        return int.from_bytes(data[:1], 'little')
    elif type_hint == bool:
        return bool(data[0]) if data else False
    elif type_hint == bytes:
        return data
    elif is_dataclass(type_hint):
        # Decode fields in order
        offset = 0
        kwargs = {}
        for f in fields(type_hint):
            # We need to know the size of the field
            # This is a simplification; for dynamic types we'd need more logic
            size = get_size(f.type)
            field_data = data[offset:offset+size]
            kwargs[f.name] = decode(field_data, f.type)
            offset += size
        return type_hint(**kwargs)
    else:
        raise TypeError(f"Unsupported type for decoding: {type_hint}")

def get_size(type_hint: Type) -> int:
    """Get the fixed size of a type in bytes."""
    if type_hint in (int, U64, I64):
        return 8
    elif type_hint in (U32, I32):
        return 4
    elif type_hint in (U16,):
        return 2
    elif type_hint in (U8, bool):
        return 1
    elif is_dataclass(type_hint):
        return sum(get_size(f.type) for f in fields(type_hint))
    else:
        raise TypeError(f"Cannot determine fixed size for: {type_hint}")
