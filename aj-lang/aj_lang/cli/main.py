"""
Ajanta SDK Command Line Interface.

Provides commands for building, testing, and managing JAM services.
"""

import argparse
import sys
import os
import shutil
import subprocess
import importlib.util
from pathlib import Path

def load_service_module(path: str):
    """Load a Python file as a module."""
    path = os.path.abspath(path)
    spec = importlib.util.spec_from_file_location("service_module", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load module from {path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules["service_module"] = module
    sys.path.insert(0, os.path.dirname(path))
    spec.loader.exec_module(module)
    return module


def find_service_class(module):
    """Find the service class in a module."""
    from aj_lang.decorators import get_all_services
    
    services = get_all_services()
    if not services:
        raise ValueError("No @service decorated class found in the module")
    
    # Return the first (or only) service
    return list(services.values())[0]


def cmd_build(args):
    """Build a Python service to PVM."""
    from ..transpiler.transpile import transpile_service
    
    print(f"Building {args.input}...")
    
    # Load the Python service
    module = load_service_module(args.input)
    meta = find_service_class(module)
    
    # Transpile to C
    c_code = transpile_service(meta.cls)
    
    # Output paths
    # Determine project root (assuming we are running from project root or similar)
    # For now, let's create a 'build' directory in the current working directory
    build_dir = Path(__file__).parent.parent.parent.parent / 'build'
    build_dir.mkdir(exist_ok=True)
    
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = build_dir / output_path
        
    c_path = output_path.with_suffix('.c')
    
    # Write C file
    with open(c_path, 'w') as f:
        f.write(c_code)
    
    print(f"Generated C code: {c_path}")
    print(f"To compile to PVM, run:")
    print(f"  ajanta-build-tool build {c_path} -o {output_path.with_suffix('.pvm')}")


def main():
    parser = argparse.ArgumentParser(
        prog='aj-lang',
        description='Ajanta Language - Pythonic way to build JAM services'
    )
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build a service to PVM')
    build_parser.add_argument('input', help='Python service file')
    build_parser.add_argument('-o', '--output', default='service.pvm', help='Output PVM file')
    build_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    build_parser.set_defaults(func=cmd_build)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
