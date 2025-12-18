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
            # Python workflow: transpile to C first, then compile to PVM
            c_output_path = source_path.replace(".py", ".c")
            cmd = ["ajanta", "build", source_path, "-o", c_output_path]
            
            # Step 1: Transpile Python to C
            try:
                result = subprocess.run(
                    cmd, 
                    cwd=project_root,
                    env=env,
                    capture_output=True, 
                    text=True,
                    check=False
                )
                
                if result.returncode != 0:
                    return {"success": False, "logs": result.stdout + "\n" + result.stderr}
                
                # Find the generated C file - ajanta puts it in build/ or same dir
                if not os.path.exists(c_output_path):
                    # Check for C file with same name
                    possible_c_file = os.path.join(os.path.dirname(source_path), "service.c")
                    if os.path.exists(possible_c_file):
                        c_output_path = possible_c_file
                    else:
                        # Parse output for actual C file path
                        for line in (result.stdout + result.stderr).split('\n'):
                            if 'Generated C code:' in line:
                                c_output_path = line.split('Generated C code:')[1].strip()
                                break
                
                if not os.path.exists(c_output_path):
                    return {"success": False, "logs": f"Transpilation succeeded but C file not found.\n{result.stdout}"}
                
                transpile_logs = result.stdout
                
            except Exception as e:
                return {"success": False, "logs": f"Transpilation error: {str(e)}"}
            
            # Step 2: Compile C to PVM using ajanta-build-tool
            cmd = ["ajanta-build-tool", "build", c_output_path, "-o", output_path]
            
        else:
            # C or C++
            cmd = ["ajanta-build-tool", "build", source_path, "-o", output_path]
            transpile_logs = ""
            
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
            
            all_logs = (transpile_logs + "\n" if request.language == "python" else "") + result.stdout + "\n" + result.stderr
            
            if result.returncode != 0:
                return {"success": False, "logs": all_logs}
            
            # Read PVM
            if os.path.exists(output_path):
                with open(output_path, "rb") as f:
                    pvm_bytes = f.read()
                
                return {
                    "success": True, 
                    "logs": all_logs,
                    "pvm": pvm_bytes.hex()
                }
            else:
                return {"success": False, "logs": "Build succeeded but output file not found.\n" + all_logs}
            
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
from playground.execution.invocations.accumulate import PsiA
from playground.types.state.accumulation.types import OperandTuples, OperandTuple
from playground.types.state.partial import GhostPartial
from playground.types.protocol.core import WorkPackageHash, ExportsRoot
from playground.types.protocol.crypto import Hash
from playground.types.state.phi import AuthorizerHash
from playground.types.work import WorkExecResult
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


class AccumulateRequest(BaseModel):
    pvm_hex: str

@app.post("/accumulate")
async def accumulate_service(request: AccumulateRequest):
    # Decode PVM
    try:
        pvm_bytes = bytes.fromhex(request.pvm_hex)
    except ValueError:
        return {"success": False, "logs": "Invalid hex string"}
    
    # Setup logging
    log_capture_string = io.StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.DEBUG)
    logger = logging.getLogger()
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)
    
    try:
        # PVM Code
        code = pvm_bytes
        service_id = ServiceId(0)
        
        # Setup Account Data (Reset state for simulation)
        account_metadata = AccountMetadata(
            code_hash=Bytes[32](bytes([0]*32)), # Dummy hash
            balance=Balance(10**12),
            gratis_offset=Balance(100),
            gas_limit=Gas(10000000),
            min_gas=Gas(0),
            created_at=TimeSlot(0),
            accumulated_at=TimeSlot(0),
            parent_service=ServiceId(1),
            num_i=Uint[32](0),
            num_o=Uint[64](0),
        )
        account_data = AccountData(service=account_metadata)
        state.delta[service_id] = account_data
        
        # Calculate code hash and store preimage
        code_hash = Hash.blake2b(code)
        state.delta[service_id].service.code_hash = code_hash
        state.delta[service_id].preimages[code_hash] = Bytes(code)
        
        # Prepare OperandTuples (Dummy data for simulation)
        operand_tuple = OperandTuple(
            p=WorkPackageHash(bytes([0]*32)),
            e=ExportsRoot(bytes([0]*32)),
            a=AuthorizerHash(bytes([0]*32)),
            y=OpaqueHash(bytes([0]*32)),
            g=Uint(1000),
            l=WorkExecResult(bytes([0]*32)),
            t=Bytes(b"")
        )
        
        operand_tuples = OperandTuples([operand_tuple])
        
        # GhostPartial wrapper
        partial_state = GhostPartial(
            service_accounts=state.delta,
            validator_keys=state.iota,
            authorizer_keys=state.phi,
            privileges=state.chi
        )
        
        timeslot = TimeSlot(1)
        gas_limit = Gas(10000000)
        entropy = OpaqueHash(bytes([0]*32))
        
        psia = PsiA(
            u=partial_state,
            t=timeslot,
            s=service_id,
            g=gas_limit,
            o=operand_tuples,
            entropy=entropy
        )
        
        # Execute
        result, deferred_transfers, commitment, gas_used, preimages = psia.execute()
        
        # Format logs
        print(f"Deferred Transfers: {deferred_transfers}")
        print(f"Commitment: {commitment}")
        print(f"Preimages added: {preimages}")
        print(f"Gas Used: {gas_used}")
        
        logs = log_capture_string.getvalue()
        
        return {
            "success": True,
            "logs": logs,
            "result": f"Gas Used: {gas_used}\nCommitment: {commitment}"
        }
        
    except Exception as e:
        import traceback
        return {"success": False, "logs": log_capture_string.getvalue() + "\n" + traceback.format_exc()}
    finally:
        logger.removeHandler(ch)


# =============================================
# Live Network Support (via jamt CLI)
# =============================================

# Path to jamt binary
JAMT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "bin/jamt"))


class DeployRequest(BaseModel):
    pvm_hex: str
    rpc_url: str = "ws://localhost:19800"
    initial_amount: int = 10000


class InvokeRequest(BaseModel):
    service_id: str
    payload: str = ""
    rpc_url: str = "ws://localhost:19800"


class NetworkStatusRequest(BaseModel):
    rpc_url: str = "ws://localhost:19800"


@app.post("/network-status")
async def network_status(request: NetworkStatusRequest):
    """Check if the network is reachable via jamt."""
    try:
        result = subprocess.run(
            [JAMT_PATH, "--rpc", request.rpc_url, "queue"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return {"success": True, "status": "connected", "logs": result.stdout}
        else:
            return {"success": False, "status": "error", "logs": result.stderr or result.stdout}
    except subprocess.TimeoutExpired:
        return {"success": False, "status": "timeout", "logs": "Connection timed out"}
    except Exception as e:
        return {"success": False, "status": "error", "logs": str(e)}


@app.post("/deploy")
async def deploy_service(request: DeployRequest):
    """Deploy a service to the live network using jamt create-service."""
    # Decode PVM hex
    try:
        pvm_bytes = bytes.fromhex(request.pvm_hex)
    except ValueError:
        return {"success": False, "logs": "Invalid hex string", "serviceId": None}
    
    # Write PVM to temp file
    with tempfile.TemporaryDirectory() as temp_dir:
        pvm_path = os.path.join(temp_dir, "service.pvm")
        with open(pvm_path, "wb") as f:
            f.write(pvm_bytes)
        
        # Run jamt create-service
        cmd = [
            JAMT_PATH,
            "--rpc", request.rpc_url,
            "create-service",
            pvm_path,
            str(request.initial_amount)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # Deployment can take a while
            )
            
            output = result.stdout + "\n" + result.stderr
            
            # Parse service ID from output
            # Expected: "Service 0a27f8ea created at slot 4912067"
            service_id = None
            for line in output.split("\n"):
                if "Service" in line and "created" in line:
                    # Extract service ID (hex string after "Service ")
                    import re
                    match = re.search(r'Service\s+([0-9a-fA-F]+)\s+created', line)
                    if match:
                        service_id = match.group(1)
                        break
            
            if result.returncode == 0 and service_id:
                return {
                    "success": True,
                    "serviceId": service_id,
                    "logs": output
                }
            else:
                return {
                    "success": False,
                    "serviceId": None,
                    "logs": output or "Deployment failed with no output"
                }
                
        except subprocess.TimeoutExpired:
            return {"success": False, "serviceId": None, "logs": "Deployment timed out after 120 seconds"}
        except Exception as e:
            return {"success": False, "serviceId": None, "logs": str(e)}


@app.post("/invoke")
async def invoke_service(request: InvokeRequest):
    """Invoke a deployed service using jamt item."""
    # Run jamt item
    cmd = [
        JAMT_PATH,
        "--rpc", request.rpc_url,
        "item",
        request.service_id,
        request.payload
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = result.stdout + "\n" + result.stderr
        
        if result.returncode == 0:
            return {
                "success": True,
                "result": output,
                "logs": output
            }
        else:
            return {
                "success": False,
                "result": None,
                "logs": output or "Invocation failed with no output"
            }
            
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "logs": "Invocation timed out after 120 seconds"}
    except Exception as e:
        return {"success": False, "result": None, "logs": str(e)}
