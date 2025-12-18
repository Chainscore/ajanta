import subprocess
import tempfile
import os

def disassemble_with_objdump(machine_code):
    """Disassemble machine code using objdump"""
    try:
        # Create a temporary file with the machine code
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            f.write(machine_code)
            temp_file = f.name
        
        # Use objdump to disassemble
        result = subprocess.run([
            'objdump', '-D', '-b', 'binary', '-m', 'i386:x86-64', temp_file
        ], capture_output=True, text=True)
        
        # Clean up
        os.unlink(temp_file)
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {e}"