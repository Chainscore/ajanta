"""Test for token.c (ERC20-like with Mappings)"""
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

# Configure logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)
for h in root.handlers[:]:
    root.removeHandler(h)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

jam_logger = logging.getLogger("jam")
jam_logger.setLevel(logging.DEBUG)
pvm_logger = logging.getLogger("pvm")
pvm_logger.setLevel(logging.DEBUG)

# Setup
state.delta.clear()
code_path = os.path.join(os.path.dirname(__file__), '../../token.pvm')
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

def to_int(b):
    return int.from_bytes(b[:8], 'little') if len(b) >= 8 else b.hex()

def test_token():
    print('=== Token Test ===')
    
    # 1. Init
    print(f'Init: {run(bytes([0x06])).hex()}')
    
    # 2. Mint 1000 to User 1
    # MINT = 0x01, to=1, amount=1000
    payload = bytes([0x01]) + (1).to_bytes(8, 'little') + (1000).to_bytes(8, 'little')
    print(f'Mint 1000 to User 1: {run(payload).hex()}')
    
    # 3. Check Balance of User 1
    # BALANCE_OF = 0x03, who=1
    payload = bytes([0x03]) + (1).to_bytes(8, 'little')
    print(f'Balance of User 1: {to_int(run(payload))}')
    
    # 4. Transfer 200 from User 100 (hardcoded sender) to User 2
    # Wait, mint gave to User 1. Sender is hardcoded as 100 in C code.
    # So we need to mint to User 100 first.
    
    # Mint 500 to User 100
    payload = bytes([0x01]) + (100).to_bytes(8, 'little') + (500).to_bytes(8, 'little')
    print(f'Mint 500 to User 100: {run(payload).hex()}')
    
    # Transfer 200 from User 100 to User 2
    # TRANSFER = 0x02, to=2, amount=200
    payload = bytes([0x02]) + (2).to_bytes(8, 'little') + (200).to_bytes(8, 'little')
    print(f'Transfer 200 from 100 to 2: {run(payload).hex()}')
    
    # 5. Check Balances
    print(f'Balance of User 100: {to_int(run(bytes([0x03]) + (100).to_bytes(8, "little")))}')
    print(f'Balance of User 2: {to_int(run(bytes([0x03]) + (2).to_bytes(8, "little")))}')
    
    # 6. Check User Info for User 2
    # GET_USER = 0x04, who=2
    res = run(bytes([0x04]) + (2).to_bytes(8, 'little'))
    if len(res) >= 17:
        joined = int.from_bytes(res[:8], 'little')
        tx_count = int.from_bytes(res[8:16], 'little')
        blocked = res[16]
        print(f'User 2 Info: joined={joined}, tx_count={tx_count}, blocked={blocked}')
    else:
        print(f'User 2 Info Error: {res.hex()}')
        
    # 7. Block User 2
    # BLOCK_USER = 0x05, who=2
    print(f'Block User 2: {run(bytes([0x05]) + (2).to_bytes(8, "little")).hex()}')
    
    # 8. Verify Blocked
    res = run(bytes([0x04]) + (2).to_bytes(8, 'little'))
    print(f'User 2 Blocked Status: {res[16]}')
