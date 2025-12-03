import time
from typing import Any, Tuple
from playground.execution.host_call import HostCallReturn, PsiH
from playground.execution.invocations.protocol import Context, DispatchFunction
from tsrkit_pvm import PANIC, ExecutionStatus, y_function
from tsrkit_types.bytes import Bytes
from playground.types.protocol.core import Gas
from playground.log_setup import pvm_logger as logger

ArgInvokeReturn = Tuple[Gas, ExecutionStatus | bytes, Context]


class PsiM:
    @staticmethod
    def execute(
        blob: Bytes | bytes,
        pc: int,
        gas: Gas,
        arguments: bytes,
        dispatch_fn: DispatchFunction,
        context: Any,
    ) -> ArgInvokeReturn:
        try:
            program, registers, memory = y_function(blob, arguments)

        except Exception as e:
            logger.error(
                "Failed to initialize the program",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )
            return Gas(0), PANIC, context
        
        # Direct execution without intermediate R call
        host_result = PsiH.execute(program, int(pc), int(gas), registers, memory, dispatch_fn, context)
        return PsiM.R(gas, host_result)


    @staticmethod
    def R(g: Gas, grouped: HostCallReturn) -> ArgInvokeReturn:
        status, pc, remaining_gas, registers, memory, context = grouped
        
        # Fast path calculations
        consumed_gas = Gas(g - max(remaining_gas, 0))

        # Optimized status handling
        if status == ExecutionStatus.OUT_OF_GAS:
            result = status
            logger.warning("Invocation ran out of gas", extra={"initial_gas": int(g), "consumed_gas": int(consumed_gas)})
        elif status == ExecutionStatus.HALT:
            # Fast path for memory access check
            reg7, reg8 = int(registers[7]), int(registers[8])
            try:
                if memory.is_accessible(reg7, reg8):
                    result = memory.read(reg7, reg8)
                else:
                    result = bytes(0)
            except OverflowError:
                result = bytes(0)
        else:
            result = ExecutionStatus.PANIC

        logger.info(
            "Invocation completed",
            extra={
                "status": str(status._value_),
                "initial_gas": int(g),
                "consumed_gas": int(consumed_gas),
                "result": result,
            }
        )

        return consumed_gas, result, context
