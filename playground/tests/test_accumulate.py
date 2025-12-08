import os
from playground.types.state.partial import GhostPartial
from tsrkit_types import Bytes, Uint
from playground.execution.invocations.accumulate import PsiA
from playground.types.state.accumulation.types import OperandTuples, OperandTuple, PreimageDict
from playground.types.protocol.core import ServiceId, Gas, Balance, TimeSlot, WorkPackageHash, ExportsRoot
from playground.types.protocol.crypto import Hash, OpaqueHash
from playground.types.state.phi import AuthorizerHash
from playground.types.state.state import state
from playground.types.state.delta import AccountData, AccountMetadata, AccountStorage, AccountPreimages, AccountLookup
from playground.types.work import WorkExecResult

def test_accumulate(caplog):
    import logging
    caplog.set_level(logging.DEBUG)
    
    code = open(os.path.join(os.path.dirname(__file__), "../../build/hello_cpp.pvm"), "rb").read()

    # Prepare arguments
    payload = b'Kartik' # Payload used in expected execution
    service_id = ServiceId(0)
    
    # Setup Account Data (reusing similar setup to test_refine for consistency)
    account_metadata = AccountMetadata(
        code_hash=Bytes[32](bytes([0]*32)), # Dummy hash
        balance=Balance(10**12),
        gratis_offset=Balance(100),
        gas_limit=Gas(10000000),
        min_gas=Gas(0),
        created_at=TimeSlot(0),
        accumulated_at=TimeSlot(0),
        parent_service=ServiceId(1),
        num_i=Uint[32](0),
        num_o=Uint[64](0),
    )
    account_data = AccountData(service=account_metadata)
    state.delta[service_id] = account_data
    state.delta[service_id].service.code_hash = Hash.blake2b(code)
    state.delta[service_id].preimages[Hash.blake2b(code)] = Bytes(code)
    
    # Prepare OperandTuples
    operand_tuple = OperandTuple(
        p=WorkPackageHash(bytes([0]*32)),
        e=ExportsRoot(bytes([0]*32)),
        a=AuthorizerHash(bytes([0]*32)),
        y=OpaqueHash(bytes([0]*32)),
        g=Uint(1000),
        l=WorkExecResult(bytes([0]*32)),
        t=Bytes(b"")
    )
    
    operand_tuples = OperandTuples([operand_tuple])
    
    # GhostPartial wrapper
    partial_state = GhostPartial(
        service_accounts=state.delta,
        validator_keys=state.iota,
        authorizer_keys=state.phi,
        privileges=state.chi
    )
    
    timeslot = TimeSlot(1)
    gas_limit = Gas(10000000)
    entropy = OpaqueHash(bytes([0]*32))
    
    psia = PsiA(
        u=partial_state,
        t=timeslot,
        s=service_id,
        g=gas_limit,
        o=operand_tuples,
        entropy=entropy
    )
    
    # Execute
    result, deferred_transfers, commitment, gas_used, preimages = psia.execute()
    
    # print("Resultant state >> ", result.to_json())
    print("\n"+"-"*50)
    print("Deferred Transfers >> ", deferred_transfers)
    print("Commitment >> ", commitment)
    print("Preimages added >>", preimages)
    print("Gas Used >> ", gas_used)
    print("-"*50+"\n")
    
    assert gas_used <= gas_limit
    
    for record in caplog.records:
        print(f"Log >> {record.message}")
