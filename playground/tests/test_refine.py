import os
from unittest.mock import MagicMock
from tsrkit_types import Bytes, Uint
from playground.execution.invocations.refine import PsiR
from playground.types.work.package import WorkPackage, WorkPackageSpec, Authorizer, WorkItems
from playground.types.work.item import WorkItem, ImportSpecs, ExtrinsicSpecs
from playground.types.protocol.core import ServiceId, Gas, Balance, TimeSlot
from playground.types.protocol.crypto import OpaqueHash
from playground.types.state.state import state
from playground.types.state.delta import AccountData, AccountMetadata
from playground.types.work.report import RefineContext
from playground.types.protocol.core import Balance

def test_refine(caplog):
    import logging
    caplog.set_level(logging.DEBUG)
    
    code = open(os.path.join(os.path.dirname(__file__), "../../service.pvm"), "rb").read()

    # Prepare arguments
    payload = b'Kartik'
    service_id = ServiceId(0)
    
    account_metadata = AccountMetadata(
        code_hash=Bytes[32](32),
        balance=Balance(10**12),  # Large balance
        gratis_offset=Balance(100),
        gas_limit=Gas(0),
        min_gas=Gas(0),
        created_at=TimeSlot(0),
        accumulated_at=TimeSlot(0),
        parent_service=ServiceId(1),
        num_i=Uint[32](0),
        num_o=Uint[64](0),
    )
    account_data = AccountData(service=account_metadata)
    
    account_data.historical_lookup = MagicMock(return_value=Bytes(code))
    state.delta[service_id] = account_data

    # Create WorkItem
    work_item = WorkItem(
        service=service_id,
        code_hash=OpaqueHash(bytes([0]*32)), # Dummy hash
        refine_gas_limit=Gas(10000000),
        accumulate_gas_limit=Gas(10000000),
        export_count=Uint(0),
        payload=Bytes(payload),
        import_segments=ImportSpecs([]),
        extrinsic=ExtrinsicSpecs([])
    )

    # Create WorkPackage
    work_package = WorkPackage(
        auth_code_host=ServiceId(0),
        authorization=Bytes(b""),
        authorizer=Authorizer(code_hash=OpaqueHash(bytes([0]*32)), params=Bytes(b"")),
        context=RefineContext.empty(),
        items=WorkItems([work_item])
    )
    psir = PsiR(
        item_index=0,
        p=work_package,
        auth_trace=b"",
        i_segments=[],
        e_offset=0
    )
    result, _, _ = psir.execute()
    
    print("Refine Result >> ", result)
    
    for record in caplog.records:
        print(f"Log >> {record.message}")
