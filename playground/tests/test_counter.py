"""Test for counter.c (Native Syntax)"""
import os
import logging
import sys
from unittest.mock import MagicMock
from tsrkit_types import Bytes, Uint
from playground.execution.invocations.refine import PsiR
from playground.types.work.package import WorkPackage, Authorizer, WorkItems
from playground.types.work.item import WorkItem, ImportSpecs, ExtrinsicSpecs
from playground.types.protocol.core import ServiceId, Gas, Balance, TimeSlot
from playground.types.protocol.crypto import OpaqueHash
from playground.types.state.state import state
from playground.types.state.delta import AccountData, AccountMetadata
from playground.types.work.report import RefineContext

# Configure logging to show output in pytest -s
# Force root logger configuration
root = logging.getLogger()
root.setLevel(logging.DEBUG)
# Remove existing handlers to avoid duplicates/interference
for h in root.handlers[:]:
    root.removeHandler(h)
    
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

# Also configure the specific loggers used in general_fns.py
jam_logger = logging.getLogger("jam")
jam_logger.setLevel(logging.DEBUG)
pvm_logger = logging.getLogger("pvm")
pvm_logger.setLevel(logging.DEBUG)

# Setup
state.delta.clear()
code_path = os.path.join(os.path.dirname(__file__), '../../counter.pvm')
code = open(code_path, 'rb').read()
sid = ServiceId(0)
meta = AccountMetadata(
    code_hash=Bytes[32](32), balance=Balance(10**12), gratis_offset=Balance(100),
    gas_limit=Gas(0), min_gas=Gas(0), created_at=TimeSlot(0), accumulated_at=TimeSlot(0),
    parent_service=ServiceId(1), num_i=Uint[32](0), num_o=Uint[64](0)
)
acc = AccountData(service=meta)
acc.historical_lookup = MagicMock(return_value=Bytes(code))
state.delta[sid] = acc

def run(payload):
    wi = WorkItem(service=sid, code_hash=OpaqueHash(bytes(32)), refine_gas_limit=Gas(10000000),
                  accumulate_gas_limit=Gas(10000000), export_count=Uint(0), payload=Bytes(payload),
                  import_segments=ImportSpecs([]), extrinsic=ExtrinsicSpecs([]))
    wp = WorkPackage(auth_code_host=ServiceId(0), authorization=Bytes(b''),
                     authorizer=Authorizer(code_hash=OpaqueHash(bytes(32)), params=Bytes(b'')),
                     context=RefineContext.empty(), items=WorkItems([wi]))
    psir = PsiR(item_index=0, p=wp, auth_trace=b'', i_segments=[], e_offset=0)
    res, _, _ = psir.execute()
    return bytes(res._value)

def test_counter():
    print('=== Counter Test (Native Syntax) ===')
    
    def to_int(b):
        return int.from_bytes(b[:8], 'little') if len(b) >= 8 else b.hex()

    print(f'Initial: {to_int(run(bytes([0x04])))}')
    print(f'After INC: {to_int(run(bytes([0x01])))}')
    print(f'After INC: {to_int(run(bytes([0x01])))}')
    print(f'After DEC: {to_int(run(bytes([0x02])))}')
    print(f'After SET(50): {to_int(run(bytes([0x03]) + (50).to_bytes(8, "little")))}')
    print(f'Current: {to_int(run(bytes([0x04])))}')
    
    # Test pause
    print(f'Pause: {to_int(run(bytes([0x05])))}')
    result = run(bytes([0x01]))  # Try INC while paused
    print(f'INC while paused: {result.hex()}')  # Should be 0xFE error
    print(f'Unpause: {to_int(run(bytes([0x06])))}')
    print(f'After unpause INC: {to_int(run(bytes([0x01])))}')

    # Test struct
    print('=== Struct Test ===')
    # Set admin: id=123, balance=456
    payload = bytes([0x07]) + (123).to_bytes(8, "little") + (456).to_bytes(8, "little")
    print(f'Set Admin: {to_int(run(payload))}')
    
    # Get admin
    res = run(bytes([0x08]))
    if len(res) >= 16:
        id_val = int.from_bytes(res[:8], 'little')
        bal_val = int.from_bytes(res[8:16], 'little')
        print(f'Get Admin: id={id_val}, balance={bal_val}')
    else:
        print(f'Get Admin (unexpected): {res.hex()}')
