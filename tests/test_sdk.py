"""
Tests for JAM SDK.
"""

import pytest
from jam_sdk import service, refine, accumulate, on_transfer
from jam_sdk.runtime import ServiceRunner
from jam_sdk import host


# Reset host state before each test
@pytest.fixture(autouse=True)
def reset_host():
    host.reset()
    yield


def test_basic_service():
    """Test a basic service definition and execution."""
    
    @service
    class TestService:
        @refine
        def refine(self, payload: bytes) -> bytes:
            return b"test result"
    
    runner = ServiceRunner(TestService)
    result = runner.run_refine(b"input")
    
    assert result == b"test result"


def test_storage():
    """Test storage operations."""
    
    @service
    class StorageService:
        @refine
        def refine(self, payload: bytes) -> bytes:
            host.set_storage(b"key1", b"value1")
            value = host.get_storage(b"key1")
            return value if value else b"not found"
    
    runner = ServiceRunner(StorageService)
    result = runner.run_refine(b"")
    
    assert result == b"value1"


def test_gas():
    """Test gas tracking."""
    
    @service
    class GasService:
        @refine
        def refine(self, payload: bytes) -> bytes:
            g1 = host.gas()
            g2 = host.gas()
            # Gas should decrease
            assert g2 < g1
            return b"ok"
    
    runner = ServiceRunner(GasService)
    result = runner.run_refine(b"")
    
    assert result == b"ok"


def test_log(capsys):
    """Test logging."""
    
    @service
    class LogService:
        @refine
        def refine(self, payload: bytes) -> bytes:
            host.log("Hello from Python!")
            host.log_error("An error occurred")
            return b"logged"
    
    runner = ServiceRunner(LogService)
    result = runner.run_refine(b"")
    
    captured = capsys.readouterr()
    assert "Hello from Python!" in captured.out
    assert "An error occurred" in captured.out
    assert result == b"logged"


def test_decorator_metadata():
    """Test that decorators capture metadata correctly."""
    
    @service
    class MetaService:
        @refine
        def my_refine(self, payload: bytes) -> bytes:
            return b""
        
        @accumulate
        def my_accumulate(self, items: list) -> None:
            pass
        
        @on_transfer
        def my_on_transfer(self, sender: int, amount: int, memo: bytes) -> None:
            pass
    
    meta = MetaService._jam_meta
    
    assert meta.name == "MetaService"
    assert meta.refine_method == "my_refine"
    assert meta.accumulate_method == "my_accumulate"
    assert meta.on_transfer_method == "my_on_transfer"


def test_transpiler():
    """Test the Python to C transpiler."""
    from jam_sdk.transpiler import transpile_service
    
    @service
    class SimpleService:
        @refine
        def refine(self, payload: bytes) -> bytes:
            x = 42
            return b"done"
    
    c_code = transpile_service(SimpleService)
    
    assert "#include" in c_code
    assert "refine" in c_code
    assert "42" in c_code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
