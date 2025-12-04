from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ajanta Web IDE")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Ajanta Web IDE Backend Running"}

import os
from fastapi import HTTPException
from pydantic import BaseModel

# ... (existing imports)

# Path to examples directory
EXAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../examples"))

class Template(BaseModel):
    name: str
    language: str
    path: str

@app.get("/templates")
async def list_templates():
    templates = []
    for root, _, files in os.walk(EXAMPLES_DIR):
        for file in files:
            if file.endswith((".py", ".c", ".cpp", ".cc")):
                lang = "python" if file.endswith(".py") else "c" if file.endswith(".c") else "cpp"
                rel_path = os.path.relpath(os.path.join(root, file), EXAMPLES_DIR)
                templates.append(Template(name=file, language=lang, path=rel_path))
    return templates

@app.get("/templates/{path:path}")
async def get_template(path: str):
    full_path = os.path.join(EXAMPLES_DIR, path)
    if not os.path.exists(full_path) or not os.path.abspath(full_path).startswith(EXAMPLES_DIR):
        raise HTTPException(status_code=404, detail="Template not found")
    
    with open(full_path, "r") as f:
        content = f.read()
    
    return {"content": content}

import subprocess
import tempfile
import shutil

class CompileRequest(BaseModel):
    source: str
    language: str # python, c, cpp

@app.post("/compile")
async def compile_service(request: CompileRequest):
    # Create temp dir
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write source file
        ext = "py" if request.language == "python" else "cpp" if request.language == "cpp" else "c"
        source_path = os.path.join(temp_dir, f"service.{ext}")
        with open(source_path, "w") as f:
            f.write(request.source)
        
        output_path = os.path.join(temp_dir, "service.pvm")
        
        # Build command
        cmd = []
        env = os.environ.copy()
        
        # Add project root to PYTHONPATH for aj-lang
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}:{project_root}/aj-lang:{project_root}"
        
        # Ensure cargo bin is in PATH for ajanta-build-tool
        cargo_bin = os.path.expanduser("~/.cargo/bin")
        env["PATH"] = f"{cargo_bin}:{env.get('PATH', '')}"
        
        if request.language == "python":
            cmd = ["ajanta", "build", source_path, "-o", output_path]
        else:
            # C or C++
            # Ensure ajanta-build-tool is in path or use absolute path if we knew it
            # Assuming it's in PATH
            cmd = ["ajanta-build-tool", "build", source_path, "-o", output_path]
            
        # Run build
        try:
            result = subprocess.run(
                cmd, 
                cwd=project_root, # Run from project root
                env=env,
                capture_output=True, 
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                return {"success": False, "logs": result.stdout + "\n" + result.stderr}
            
            # Read PVM
            if os.path.exists(output_path):
                with open(output_path, "rb") as f:
                    pvm_bytes = f.read()
                
                return {
                    "success": True, 
                    "logs": result.stdout,
                    "pvm": pvm_bytes.hex()
                }
            else:
                return {"success": False, "logs": "Build succeeded but output file not found.\n" + result.stdout}
            
        except Exception as e:
            return {"success": False, "logs": str(e)}

# Setup paths for playground imports
import sys
import logging
import io

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "playground"))
sys.path.append(os.path.join(project_root, "playground/deps/tsrkit-types"))
sys.path.append(os.path.join(project_root, "playground/deps/tsrkit-asm/python"))
sys.path.append(os.path.join(project_root, "playground/deps/tsrkit-pvm"))

from playground.execution.invocations.refine import PsiR
from playground.types.work.package import WorkPackage, WorkPackageSpec, Authorizer, WorkItems
from playground.types.work.item import WorkItem, ImportSpecs, ExtrinsicSpecs
from playground.types.protocol.core import ServiceId, Gas, Balance, TimeSlot
from playground.types.protocol.crypto import OpaqueHash
from playground.types.state.state import state
from playground.types.state.delta import AccountData, AccountMetadata
from playground.types.work.report import RefineContext
from tsrkit_types import Bytes, Uint

class RunRequest(BaseModel):
    pvm_hex: str
    payload: str

@app.post("/run")
async def run_service(request: RunRequest):
    # Decode PVM
    try:
        pvm_bytes = bytes.fromhex(request.pvm_hex)
    except ValueError:
        return {"success": False, "logs": "Invalid hex string"}
    
    # Setup logging capture
    log_capture_string = io.StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.DEBUG)
    logger = logging.getLogger()
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)
    
    try:
        # Prepare arguments
        payload_bytes = bytes.fromhex(request.payload)
        service_id = ServiceId(0)
        
        # Create WorkItem
        work_item = WorkItem(
            service=service_id,
            code_hash=OpaqueHash(bytes([0]*32)), 
            refine_gas_limit=Gas(10000000),
            accumulate_gas_limit=Gas(10000000),
            export_count=Uint(0),
            payload=Bytes(payload_bytes),
            import_segments=ImportSpecs([]),
            extrinsic=ExtrinsicSpecs([])
        )

        # Create WorkPackage
        work_package = WorkPackage(
            auth_code_host=ServiceId(0),
            authorization=Bytes(b""),
            authorizer=Authorizer(code_hash=OpaqueHash(bytes([0]*32)), params=Bytes(b"")),
            context=RefineContext.empty(),
            items=WorkItems([work_item])
        )
        
        # Setup State
        account_metadata = AccountMetadata(
            code_hash=Bytes[32](32),
            balance=Balance(10**12),
            gratis_offset=Balance(100),
            gas_limit=Gas(0),
            min_gas=Gas(0),
            created_at=TimeSlot(0),
            accumulated_at=TimeSlot(0),
            parent_service=ServiceId(1),
            num_i=Uint[32](0),
            num_o=Uint[64](0),
        )
        account_data = AccountData(service=account_metadata)
        
        # Mock historical_lookup to return our PVM code
        account_data.historical_lookup = lambda x, y: Bytes(pvm_bytes)
        
        state.delta[service_id] = account_data
        
        # Execute
        psir = PsiR(
            item_index=0,
            p=work_package,
            auth_trace=b"",
            i_segments=[],
            e_offset=0
        )
        
        result, _, _ = psir.execute()
        
        logs = log_capture_string.getvalue()
        return {
            "success": True,
            "result": str(result),
            "logs": logs
        }
        
    except Exception as e:
        import traceback
        return {"success": False, "logs": log_capture_string.getvalue() + "\n" + traceback.format_exc()}
    finally:
        logger.removeHandler(ch)
