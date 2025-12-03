"""
Decorators for JAM service definition.

These decorators are used to mark methods as service entry points
and capture metadata for code generation.
"""

from typing import Callable, TypeVar, Any, get_type_hints, Optional
from functools import wraps
import inspect
from dataclasses import dataclass

F = TypeVar('F', bound=Callable[..., Any])


class ServiceMeta:
    """Metadata about a service class."""
    
    def __init__(self, cls: type):
        self.cls = cls
        self.name = cls.__name__
        self.refine_method: Optional[str] = None
        self.accumulate_method: Optional[str] = None
        self.on_transfer_method: Optional[str] = None
        self.methods: dict[str, Callable] = {}
        
    def add_method(self, name: str, method: Callable, method_type: str):
        self.methods[name] = method
        if method_type == "refine":
            self.refine_method = name
        elif method_type == "accumulate":
            self.accumulate_method = name
        elif method_type == "on_transfer":
            self.on_transfer_method = name


# Global registry of services
_services: dict[str, ServiceMeta] = {}


def get_service(name: str) -> Optional[ServiceMeta]:
    """Get a registered service by name."""
    return _services.get(name)


def get_all_services() -> dict[str, ServiceMeta]:
    """Get all registered services."""
    return _services.copy()


def service(cls: type) -> type:
    """
    Decorator to mark a class as a JAM service.
    
    Example:
        @service
        class MyService:
            @refine
            def refine(self, item_index: int, service_id: int, 
                       payload: bytes, payload_len: int,
                       work_package_hash: bytes) -> bytes:
                return b"result"
    """
    meta = ServiceMeta(cls)
    
    # Find decorated methods
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if hasattr(method, '_jam_method_type'):
            meta.add_method(name, method, method._jam_method_type)
    
    # Store metadata on the class
    cls._jam_meta = meta
    
    # Register globally
    _services[cls.__name__] = meta
    
    return cls


def refine(method: F) -> F:
    """
    Decorator to mark a method as the refine entry point.
    
    The refine method processes work items during the refinement phase.
    It receives individual decoded arguments and returns the refined output.
    
    Signature: 
        (self, item_index: int, service_id: int, 
         payload: bytes, payload_len: int,
         work_package_hash: bytes) -> bytes
    
    Or simplified (legacy):
        (self, payload: bytes) -> bytes
    """
    method._jam_method_type = "refine"
    
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> bytes:
        return method(self, *args, **kwargs)
    
    wrapper._jam_method_type = "refine"
    return wrapper  # type: ignore


def accumulate(method: F) -> F:
    """
    Decorator to mark a method as the accumulate entry point.
    
    The accumulate method processes refined work items and updates state.
    It receives individual decoded arguments.
    
    Signature: 
        (self, timeslot: int, service_id: int, num_inputs: int) -> None
    """
    method._jam_method_type = "accumulate"
    
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> None:
        return method(self, *args, **kwargs)
    
    wrapper._jam_method_type = "accumulate"
    return wrapper  # type: ignore


def on_transfer(method: F) -> F:
    """
    Decorator to mark a method as the on_transfer entry point.
    
    The on_transfer method is called when the service receives a transfer
    with a memo.
    
    Signature: (self, sender: int, receiver: int, amount: int, 
                memo: bytes, memo_len: int) -> None
    """
    method._jam_method_type = "on_transfer"
    
    @wraps(method)
    def wrapper(self, sender: int, receiver: int, amount: int, 
                memo: bytes, memo_len: int) -> None:
        return method(self, sender, receiver, amount, memo, memo_len)
    
    wrapper._jam_method_type = "on_transfer"
    return wrapper  # type: ignore


def structure(cls: type) -> type:
    """
    Decorator to mark a class as a JAM structure (C struct).
    
    Example:
        @structure
        class UserInfo:
            joined_at: U64
            tx_count: U64
            is_blocked: bool
    """
    cls._jam_struct = True
    return dataclass(cls)
