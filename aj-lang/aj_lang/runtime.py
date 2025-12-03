"""
Base service class and runtime for JAM services.
"""

from typing import Optional, get_type_hints, get_origin, get_args, Any
from aj_lang.types import RefineContext, AccumulateItem, ServiceId, Mapping
from aj_lang.decorators import ServiceMeta
from aj_lang import host
from aj_lang.encoding import encode, decode, get_size


class StorageMapping:
    """Runtime implementation of Mapping backed by host storage."""
    
    def __init__(self, prefix: str, key_type: type, value_type: type):
        self.prefix = prefix.encode('utf-8')
        self.key_type = key_type
        self.value_type = value_type
        
    def _get_key(self, key: Any) -> bytes:
        # Key format: prefix + encoded_key
        return self.prefix + encode(key, self.key_type)
        
    def __getitem__(self, key: Any) -> Any:
        storage_key = self._get_key(key)
        # We need to know the size of the value to read it
        # For dynamic types, we might need a different strategy, but for now assume fixed size
        # or read a large chunk. The C SDK reads fixed size.
        try:
            size = get_size(self.value_type)
        except TypeError:
            size = 4096 # Max size fallback
            
        data = bytearray(size)
        # get_storage returns bytes read
        read_len = host.get_storage(0, storage_key, len(storage_key), data, 0, size)
        
        if host.host_is_error(read_len) or read_len == host.HOST_NONE:
            # Return default value (zero-initialized)
            # For simple types, 0/False. For structs, empty struct.
            # decode handles zero bytes correctly for most types if we pass zeroed buffer
            return decode(bytes(size), self.value_type)
            
        return decode(bytes(data[:read_len]), self.value_type)
        
    def __setitem__(self, key: Any, value: Any) -> None:
        storage_key = self._get_key(key)
        data = encode(value, self.value_type)
        host.set_storage(storage_key, len(storage_key), data, len(data))


class JamService:
    """
    Base class for JAM services.
    
    Provides runtime support for service execution.
    """
    
    _jam_meta: ServiceMeta
    
    def __init__(self):
        self._context: Optional[RefineContext] = None
    
    def _set_context(self, ctx: RefineContext):
        """Set the execution context."""
        self._context = ctx
    
    @property
    def context(self) -> RefineContext:
        """Get the current execution context."""
        if self._context is None:
            raise RuntimeError("No execution context set")
        return self._context
    
    @property 
    def service_id(self) -> ServiceId:
        """Get the current service ID."""
        return self.context.service_id
    
    @property
    def payload(self) -> bytes:
        """Get the work item payload."""
        return self.context.payload
    
    @property
    def package_hash(self) -> bytes:
        """Get the work package hash."""
        return self.context.package_hash


class ServiceRunner:
    """
    Runner for executing services locally.
    
    Used for testing services without compilation.
    """
    
    def __init__(self, service_class: type):
        if not hasattr(service_class, '_jam_meta'):
            raise ValueError(f"{service_class.__name__} is not a JAM service. "
                           "Did you forget the @service decorator?")
        
        self.service_class = service_class
        self.meta = service_class._jam_meta
        self.instance = service_class()
        self.initial_state = {} # To track changes
        
    def _load_state(self):
        """Load state variables from storage."""
        hints = get_type_hints(self.service_class)
        self.initial_state = {}
        
        for name, type_hint in hints.items():
            # Check if it's a Mapping
            origin = get_origin(type_hint)
            if origin is Mapping:
                args = get_args(type_hint)
                if len(args) != 2:
                    raise TypeError(f"Mapping {name} must have 2 type arguments")
                key_type, value_type = args
                # Initialize mapping
                setattr(self.instance, name, StorageMapping(name, key_type, value_type))
            else:
                # Scalar / Struct
                key = name.encode('utf-8')
                try:
                    size = get_size(type_hint)
                except TypeError:
                    size = 4096
                
                data = bytearray(size)
                read_len = host.get_storage(0, key, len(key), data, 0, size)
                
                if host.host_is_error(read_len) or read_len == host.HOST_NONE:
                    val = decode(bytes(size), type_hint) # Default
                else:
                    val = decode(bytes(data[:read_len]), type_hint)
                
                setattr(self.instance, name, val)
                self.initial_state[name] = val

    def _save_state(self):
        """Save changed state variables to storage."""
        hints = get_type_hints(self.service_class)
        
        for name, type_hint in hints.items():
            origin = get_origin(type_hint)
            if origin is Mapping:
                continue # Mappings save directly
            
            val = getattr(self.instance, name)
            # Check if changed
            # Simple comparison. For structs, this works if they are dataclasses (value equality)
            if name not in self.initial_state or val != self.initial_state[name]:
                key = name.encode('utf-8')
                data = encode(val, type_hint)
                host.set_storage(key, len(key), data, len(data))

    def run_refine(self, payload: bytes, 
                   service_id: int = 0,
                   core_index: int = 0,
                   work_item_index: int = 0) -> bytes:
        """
        Execute the refine method.
        
        Args:
            payload: Work item payload
            service_id: Service ID (default 0)
            core_index: Core index (default 0)
            work_item_index: Work item index (default 0)
        
        Returns:
            Refined output bytes
        """
        if self.meta.refine_method is None:
            raise ValueError(f"Service {self.meta.name} has no @refine method")
        
        # Set up context
        ctx = RefineContext(
            core_index=core_index,
            work_item_index=work_item_index,
            service_id=service_id,
            payload=payload,
            payload_len=len(payload),
            package_hash=bytes(32),
        )
        
        if isinstance(self.instance, JamService):
            self.instance._set_context(ctx)
        
        self._load_state()
        try:
            # Call the refine method
            method = getattr(self.instance, self.meta.refine_method)
            result = method(payload)
        finally:
            self._save_state()
        
        if isinstance(result, bytes):
            return result
        elif hasattr(result, '__bytes__'):
            return bytes(result)
        else:
            raise TypeError(f"Refine method must return bytes, got {type(result)}")
    
    def run_accumulate(self, items: list[AccumulateItem]) -> None:
        """
        Execute the accumulate method.
        
        Args:
            items: List of accumulate items
        """
        if self.meta.accumulate_method is None:
            raise ValueError(f"Service {self.meta.name} has no @accumulate method")
        
        self._load_state()
        try:
            method = getattr(self.instance, self.meta.accumulate_method)
            method(items)
        finally:
            self._save_state()
    
    def run_on_transfer(self, sender: int, amount: int, memo: bytes) -> None:
        """
        Execute the on_transfer method.
        
        Args:
            sender: Sender service ID
            amount: Transfer amount
            memo: Transfer memo
        """
        if self.meta.on_transfer_method is None:
            raise ValueError(f"Service {self.meta.name} has no @on_transfer method")
        
        self._load_state()
        try:
            method = getattr(self.instance, self.meta.on_transfer_method)
            method(sender, amount, memo)
        finally:
            self._save_state()
