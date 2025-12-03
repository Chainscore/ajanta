"""
Ajanta CLI - Unified command-line interface for building JAM services.

Usage:
    ajanta build <input.py> -o <output.pvm>   # Full pipeline: Python → C → PVM
    ajanta transpile <input.py> -o <output.c> # Just Python → C
"""

from __future__ import annotations

import argparse
import sys
import os
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List


# Default CFLAGS for PVM compilation
DEFAULT_CFLAGS = [
    "-ffixed-gp",
    "-ffixed-tp",
    "-ffixed-a6",
    "-ffixed-a7",
    "-ffixed-s2",
    "-ffixed-s3",
    "-ffixed-s4",
    "-ffixed-s5",
    "-ffixed-s6",
    "-ffixed-s7",
    "-ffixed-s8",
    "-ffixed-s9",
    "-ffixed-s10",
    "-ffixed-s11",
    "-ffixed-t3",
    "-ffixed-t4",
    "-ffixed-t5",
    "-ffixed-t6",
]


def find_build_tool() -> Optional[str]:
    """Find the ajanta-build-tool binary."""
    # Check if ajanta-build-tool is in PATH
    if shutil.which("ajanta-build-tool"):
        return "ajanta-build-tool"
    
    # Check in the workspace's target directory
    workspace_root = Path(__file__).parent.parent.parent.parent
    release_path = workspace_root / "ajanta-build-tool" / "target" / "release" / "ajanta-build-tool"
    debug_path = workspace_root / "ajanta-build-tool" / "target" / "debug" / "ajanta-build-tool"
    
    if release_path.exists():
        return str(release_path)
    if debug_path.exists():
        return str(debug_path)
    
    return None


def transpile_python_to_c(input_path: Path, verbose: bool = False) -> str:
    """Transpile a Python service file to C code."""
    import importlib.util
    
    # Ensure aj_lang is available
    try:
        from aj_lang.transpiler.transpile import transpile_service
        from aj_lang.decorators import get_all_services
    except ImportError:
        print("Error: aj-lang is not installed. Run 'make install' first.", file=sys.stderr)
        sys.exit(1)
    
    # Load the Python module
    abs_path = input_path.resolve()
    spec = importlib.util.spec_from_file_location("service_module", abs_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load module from {abs_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules["service_module"] = module
    sys.path.insert(0, str(abs_path.parent))
    spec.loader.exec_module(module)
    
    # Find the service class
    services = get_all_services()
    if not services:
        raise ValueError("No @service decorated class found in the module")
    
    meta = list(services.values())[0]
    
    # Transpile to C
    c_code = transpile_service(meta.cls)
    
    if verbose:
        print(f"Transpiled {input_path} to C ({len(c_code)} bytes)")
    
    return c_code


def compile_c_to_pvm(c_path: Path, output_path: Path, cflags: List[str], verbose: bool = False) -> bool:
    """Compile C code to PVM using ajanta-build-tool."""
    build_tool = find_build_tool()
    
    if not build_tool:
        print("Error: ajanta-build-tool not found.", file=sys.stderr)
        print("Please run 'make install' or build it manually:", file=sys.stderr)
        print("  cd ajanta-build-tool && cargo build --release", file=sys.stderr)
        return False
    
    cmd = [build_tool, "build", str(c_path), "-o", str(output_path)]
    
    if cflags:
        cmd.append(f"--cflags={' '.join(cflags)}")
    
    if verbose:
        print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=not verbose)
    
    if result.returncode != 0:
        if not verbose:
            print(result.stderr.decode(), file=sys.stderr)
        return False
    
    return True


def cmd_build(args):
    """Build a Python service to PVM (full pipeline)."""
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path("build") / input_path.with_suffix(".pvm").name
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Building {input_path} → {output_path}")
    
    # Step 1: Transpile Python to C
    if args.verbose:
        print("Step 1: Transpiling Python → C...")
    
    try:
        c_code = transpile_python_to_c(input_path, args.verbose)
    except Exception as e:
        print(f"Error during transpilation: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Write C file (either to temp or alongside output)
    if args.keep_c:
        c_path = output_path.with_suffix(".c")
        with open(c_path, "w") as f:
            f.write(c_code)
        if args.verbose:
            print(f"  Saved C code to {c_path}")
    else:
        # Use a temp file
        c_file = tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False)
        c_file.write(c_code)
        c_file.close()
        c_path = Path(c_file.name)
    
    # Step 2: Compile C to PVM
    if args.verbose:
        print("Step 2: Compiling C → PVM...")
    
    cflags = args.cflags if args.cflags else DEFAULT_CFLAGS
    
    try:
        success = compile_c_to_pvm(c_path, output_path, cflags, args.verbose)
    finally:
        # Clean up temp file if we created one
        if not args.keep_c and c_path.exists():
            c_path.unlink()
    
    if not success:
        sys.exit(1)
    
    print(f"✓ Built {output_path} ({output_path.stat().st_size} bytes)")


def cmd_transpile(args):
    """Transpile Python to C only (no PVM compilation)."""
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path("build") / input_path.with_suffix(".c").name
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Transpiling {input_path} → {output_path}")
    
    try:
        c_code = transpile_python_to_c(input_path, args.verbose)
    except Exception as e:
        print(f"Error during transpilation: {e}", file=sys.stderr)
        sys.exit(1)
    
    with open(output_path, "w") as f:
        f.write(c_code)
    
    print(f"✓ Generated {output_path}")


def cmd_compile(args):
    """Compile a C file to PVM (using ajanta-build-tool)."""
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path("build") / input_path.with_suffix(".pvm").name
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Compiling {input_path} → {output_path}")
    
    cflags = args.cflags if args.cflags else DEFAULT_CFLAGS
    success = compile_c_to_pvm(input_path, output_path, cflags, args.verbose)
    
    if not success:
        sys.exit(1)
    
    print(f"✓ Built {output_path} ({output_path.stat().st_size} bytes)")


def main():
    parser = argparse.ArgumentParser(
        prog="ajanta",
        description="Ajanta SDK - Build JAM services in Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ajanta build examples/python/hello.py                    # Build to build/hello.pvm
  ajanta build examples/python/hello.py -o service.pvm     # Build to service.pvm
  ajanta build examples/python/hello.py --keep-c           # Keep intermediate C file
  ajanta transpile examples/python/hello.py                # Just generate C code
  ajanta compile build/service.c -o build/service.pvm      # Compile C to PVM
""",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Build command (full pipeline: py → c → pvm)
    build_parser = subparsers.add_parser(
        "build",
        help="Build a Python service to PVM (full pipeline)",
        description="Transpiles Python to C, then compiles to PVM"
    )
    build_parser.add_argument("input", help="Input Python file (.py)")
    build_parser.add_argument("-o", "--output", help="Output PVM file (default: build/<name>.pvm)")
    build_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    build_parser.add_argument("--keep-c", action="store_true", help="Keep intermediate C file")
    build_parser.add_argument(
        "--cflags",
        nargs="*",
        help="Custom CFLAGS for compilation (overrides defaults)"
    )
    build_parser.set_defaults(func=cmd_build)
    
    # Transpile command (py → c only)
    transpile_parser = subparsers.add_parser(
        "transpile",
        help="Transpile Python to C (no compilation)",
        description="Generates C code from a Python service"
    )
    transpile_parser.add_argument("input", help="Input Python file (.py)")
    transpile_parser.add_argument("-o", "--output", help="Output C file (default: build/<name>.c)")
    transpile_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    transpile_parser.set_defaults(func=cmd_transpile)
    
    # Compile command (c → pvm only)
    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile C to PVM",
        description="Compiles a C file to PVM using ajanta-build-tool"
    )
    compile_parser.add_argument("input", help="Input C file (.c)")
    compile_parser.add_argument("-o", "--output", help="Output PVM file (default: build/<name>.pvm)")
    compile_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    compile_parser.add_argument(
        "--cflags",
        nargs="*",
        help="Custom CFLAGS for compilation (overrides defaults)"
    )
    compile_parser.set_defaults(func=cmd_compile)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
