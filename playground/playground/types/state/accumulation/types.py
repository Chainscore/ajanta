from typing import Any, Tuple, List, Set
from tsrkit_types import structure, TypedVector, Bytes, Uint
from ...protocol.merkle import OptionHash
from ...state.phi import Phi, AuthorizerHash
from ...work import WorkExecResult
from ...protocol.core import WorkPackageHash
from ...state.chi import Chi
from ...protocol.core import ServiceId, Gas, OpaqueHash, Balance, ExportsRoot
from ...state.delta import Delta
from ...state.iota import Iota


# Accumulation Types
GasConsumed = List[Tuple[ServiceId, Gas]]
BeefyMap = Set[Tuple[ServiceId, OpaqueHash]]

@structure
class OperandTuple:
    p: WorkPackageHash
    e: ExportsRoot
    a: AuthorizerHash
    y: OpaqueHash # payload_hash
    g: Uint # accumulate_gas of a work result / digest
    l: WorkExecResult
    t: Bytes # auth_output of work report


class OperandTuples(TypedVector[OperandTuple]):
    ...


@structure
class DeferredTransfer:
    sender: ServiceId # s
    receiver: ServiceId # d
    amount: Balance # a
    memo: Bytes # m
    gas: Gas # g


class DeferredTransfers(TypedVector[DeferredTransfer]):
    ...


PreimageDict = Set[Tuple[ServiceId, Bytes]]


@structure
class AccuContextX:
    # s
    s_index: ServiceId
    # e
    partial_state: Any
    # i
    i_index: ServiceId
    # t
    deferred_transfers: DeferredTransfers
    # y
    hash: OptionHash
    # p
    preimage: PreimageDict


@structure
class AccumulationContext:
    x: AccuContextX
    y: AccuContextX


# @structure
# class AccumulationOutput:
#     e: StateContext # posterior state context
#     t: DeferredTransfers # deferred transfers
#     y: OptionHash # output hash
#     u: Gas # gas used
#     p: PreimageDict # new preimages ?

AccumulationOutput = Tuple[Any, DeferredTransfers, OptionHash, Gas, PreimageDict]