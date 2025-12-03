"""
Tests for the JAM SDK transpiler and semantic analyzer.
"""

import pytest
import ast
from jam_sdk.semantics import (
    SemanticAnalyzer, AnalysisResult,
    U8, U16, U32, U64, I32, I64, BYTES, STRING, BOOL, VOID,
    BytesType, IntegerType
)
from jam_sdk.transpiler import transpile_service, CCodeGenerator


class TestSemanticAnalyzer:
    """Tests for the semantic analyzer."""
    
    def test_simple_function(self):
        """Test analyzing a simple function."""
        code = '''
def add(x: int, y: int) -> int:
    return x + y
'''
        tree = ast.parse(code)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(tree)
        
        assert not result.has_errors
        assert len(result.type_annotations) > 0
    
    def test_type_mismatch_error(self):
        """Test that type mismatches are caught."""
        code = '''
def test(x: int) -> str:
    return x
'''
        tree = ast.parse(code)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(tree)
        
        assert result.has_errors
        assert any("Return type mismatch" in str(e) for e in result.errors)
    
    def test_undefined_variable_error(self):
        """Test that undefined variables are caught."""
        code = '''
def test() -> int:
    return undefined_var
'''
        tree = ast.parse(code)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(tree)
        
        assert result.has_errors
        assert any("Undefined variable" in str(e) for e in result.errors)
    
    def test_function_call_type_inference(self):
        """Test that function call return types are inferred."""
        # gas() returns U64, which we return as U64
        code = '''
def test() -> U64:
    g = gas()
    return g
'''
        tree = ast.parse(code)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(tree)
        
        # Should have no errors when types match
        assert not result.has_errors
    
    def test_binary_operations(self):
        """Test binary operation type inference."""
        code = '''
def test(x: int, y: int) -> int:
    z = x + y
    w = z * 2
    return w
'''
        tree = ast.parse(code)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(tree)
        
        assert not result.has_errors
    
    def test_comparison_returns_bool(self):
        """Test that comparisons return bool type."""
        code = '''
def test(x: int) -> bool:
    return x > 10
'''
        tree = ast.parse(code)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(tree)
        
        assert not result.has_errors
    
    def test_for_loop_with_range(self):
        """Test for loop with range() is allowed."""
        code = '''
def test() -> int:
    total = 0
    for i in range(10):
        total = total + i
    return total
'''
        tree = ast.parse(code)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(tree)
        
        assert not result.has_errors
    
    def test_for_loop_without_range_error(self):
        """Test that for loops without range() are rejected."""
        code = '''
def test(items: bytes) -> int:
    total = 0
    for item in items:
        total = total + 1
    return total
'''
        tree = ast.parse(code)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(tree)
        
        assert result.has_errors
        assert any("range()" in str(e) for e in result.errors)


class TestCCodeGenerator:
    """Tests for C code generation."""
    
    def test_simple_assignment(self):
        """Test simple variable assignment."""
        generator = CCodeGenerator("Test")
        tree = ast.parse("x = 42")
        
        for stmt in tree.body:
            generator.visit(stmt)
        
        assert "int64_t x = 42;" in generator.output[0]
    
    def test_if_statement(self):
        """Test if statement generation."""
        code = '''
if x > 10:
    y = 1
else:
    y = 0
'''
        generator = CCodeGenerator("Test")
        generator.local_vars['x'] = 'int64_t'
        tree = ast.parse(code)
        
        for stmt in tree.body:
            generator.visit(stmt)
        
        output = '\n'.join(generator.output)
        assert 'if' in output
        assert 'else' in output
    
    def test_for_loop_with_range(self):
        """Test for loop generation."""
        code = '''
for i in range(10):
    x = i
'''
        generator = CCodeGenerator("Test")
        tree = ast.parse(code)
        
        for stmt in tree.body:
            generator.visit(stmt)
        
        output = '\n'.join(generator.output)
        assert 'for' in output
        assert 'i < 10' in output
    
    def test_function_call(self):
        """Test function call generation."""
        generator = CCodeGenerator("Test")
        tree = ast.parse("g = gas()")
        
        for stmt in tree.body:
            generator.visit(stmt)
        
        assert "gas()" in generator.output[0]
    
    def test_binary_ops(self):
        """Test binary operation generation."""
        generator = CCodeGenerator("Test")
        generator.local_vars['x'] = 'int64_t'
        generator.local_vars['y'] = 'int64_t'
        tree = ast.parse("z = x + y * 2")
        
        for stmt in tree.body:
            generator.visit(stmt)
        
        output = generator.output[0]
        assert '+' in output
        assert '*' in output


class TestTranspileService:
    """Integration tests for the full transpilation pipeline."""
    
    def test_transpile_hello_service(self):
        """Test transpiling the hello service example."""
        import sys
        sys.path.insert(0, 'examples')
        from hello import HelloService
        
        c_code = transpile_service(HelloService)
        
        # Check for expected content
        assert '#include' in c_code
        assert 'RefineResult refine' in c_code
        assert 'gas()' in c_code
        assert 'log_msg' in c_code
        assert 'set_storage' in c_code
        assert 'get_storage' in c_code
        assert 'return _result;' in c_code
    
    def test_transpile_validation_errors(self):
        """Test that validation errors are raised."""
        from jam_sdk.decorators import service as service_dec, refine as refine_dec
        from jam_sdk.semantics import SemanticError
        
        @service_dec
        class BadService:
            @refine_dec
            def refine(self, payload: bytes) -> bytes:
                return undefined_variable  # Should error
        
        with pytest.raises(SemanticError):
            transpile_service(BadService)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
