"""
Hello World JAM Service

This is the Python equivalent of hello.c, demonstrating the JAM SDK.
"""

from aj_lang import service, refine, accumulate, on_transfer
from aj_lang.host import gas, LOG_DEBUG_INT, get_storage, set_storage


@service
class HelloService:
    """A simple JAM service to test basic functionality."""
    
    @refine
    def refine(self, payload: bytes) -> bytes:
        """Process a work item during refinement."""
        # Get remaining gas
        g = gas()
        LOG_DEBUG_INT("Gas", g)
        
        # Store a value
        key = b"mykey"
        value = b"myvalue"
        set_storage(key, 5, value, 7)
        
        buf = bytearray(7)
        read_len = get_storage(0, key, 5, buf, 0, 7)
        
        # Log the read value (the buffer now contains "myvalue")
        LOG_DEBUG_INT("read len", read_len)
        
        # Return result
        return b"Hello JAM!"
    
    @accumulate  
    def accumulate(self, slot: int, service_id: int, n_items: int) -> None:
        """Process refined items during accumulation."""
        pass
    
    @on_transfer
    def on_transfer(self, sender: int, amount: int, memo: int) -> None:
        """Handle incoming transfers."""
        pass
