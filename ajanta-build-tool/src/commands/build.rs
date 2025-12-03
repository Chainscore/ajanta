use std::path::{Path, PathBuf};
use std::process::Command;
use anyhow::{Context, Result};
use clap::Parser;
use jam_program_blob_common::{ProgramBlob};
use std::borrow::Cow;

/// Build a C source file into a PVM service
#[derive(Parser)]
pub struct Args {
    /// Input C source file
    #[arg(value_name = "SOURCE")]
    pub source: PathBuf,

    /// Output PVM file path
    #[arg(short, long, value_name = "OUTPUT", default_value = "build/service.pvm")]
    pub output: PathBuf,

    /// Path to the C compiler (clang or gcc)
    #[arg(long, default_value = "riscv64-elf-gcc")]
    pub compiler: String,

    /// Additional flags passed through to the C compiler
    #[arg(long, value_name = "FLAGS", value_delimiter = ' ')]
    pub cflags: Vec<String>,
}

pub fn run(args: Args) -> Result<()> {
    /* -------------------------------------------------------------------------- */
    /*                                Compile C Source                            */
    /* -------------------------------------------------------------------------- */
    let tempdir = tempfile::tempdir().context("create temp directory")?;

    let obj_path = tempdir.path().join("source.o");
    let mut cmd = Command::new(&args.compiler);
    cmd.arg("-march=rv64imac")
        .arg("-mabi=lp64")
        .arg("-mno-relax")
        .arg("-ffreestanding")
        .arg("-nostdlib")
        .arg("-fno-builtin")
        .arg("-c")
        .arg(&args.source)
        .arg("-o")
        .arg(&obj_path);

    for flag in &args.cflags {
        cmd.arg(flag);
    }

    // Add include path for our header
    let include_path = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../sdk/include");
    cmd.arg("-I").arg(&include_path);

    jamc::run_command(&mut cmd, "compile C source")?;

    /* -------------------------------------------------------------------------- */
    /*                                Compile Stubs                               */
    /* -------------------------------------------------------------------------- */
    let entry_stub = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("stubs/entry.S");
    let entry_obj = tempdir.path().join("entry.o");
    let runtime_stub = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("stubs/runtime.c");
    let runtime_obj = tempdir.path().join("runtime.o");
    let exports_stub = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("stubs/exports.S");
    let exports_obj = tempdir.path().join("exports.o");

    // 1. Compile entry stub
    let mut stub_cmd = Command::new(&args.compiler);
    stub_cmd
        .arg("-march=rv64imac")
        .arg("-mabi=lp64")
        .arg("-mno-relax")
        .arg("-c")
        .arg(&entry_stub)
        .arg("-o")
        .arg(&entry_obj);
    jamc::run_command(&mut stub_cmd, "compile entry stub")?;

    // 2. Compile runtime stub
    let mut runtime_cmd = Command::new(&args.compiler);
    runtime_cmd
        .arg("-march=rv64imac")
        .arg("-mabi=lp64")
        .arg("-mno-relax")
        .arg("-ffreestanding")
        .arg("-nostdlib")
        .arg("-fno-builtin")
        .arg("-c")
        .arg(&runtime_stub)
        .arg("-o")
        .arg(&runtime_obj);
    jamc::run_command(&mut runtime_cmd, "compile runtime stub")?;

    // 3. Compile exports stub
    let mut exports_cmd = Command::new(&args.compiler);
    exports_cmd
        .arg("-march=rv64imac")
        .arg("-mabi=lp64")
        .arg("-mno-relax")
        .arg("-c")
        .arg(&exports_stub)
        .arg("-o")
        .arg(&exports_obj);
    jamc::run_command(&mut exports_cmd, "compile exports stub")?;

    /* -------------------------------------------------------------------------- */
    /*                                 Link ELF                                   */
    /* -------------------------------------------------------------------------- */
    let mut link_cmd = Command::new("riscv64-elf-ld");
    link_cmd
        .arg("-r") // Produce a relocatable ELF to preserve section relocations
        .arg(&entry_obj)
        .arg(&obj_path)
        .arg(&runtime_obj)
        .arg(&exports_obj)
        .arg("-o")
        .arg(tempdir.path().join("linked.elf"));
    jamc::run_command(&mut link_cmd, "link ELF")?;

    let elf_path = tempdir.path().join("linked.elf");
    // let elf_data = std::fs::read("/home/kartik-chainscore/JAM/jamc/hello.elf").context("read linked ELF")?;
    let elf_data = std::fs::read(&elf_path).context("read linked ELF")?;

    /* -------------------------------------------------------------------------- */
    /*                            Linked ELF to PVM                               */
    /* -------------------------------------------------------------------------- */
    // Use polkavm-linker to generate PVM
    let mut cfg = polkavm_linker::Config::default();
    cfg.set_strip(true); // Disable debug info to avoid assertion failures
    // Configure a dispatch table so that the JAM runtime can call the
    // exported functions by index.  The accompanying exports.S stub provides
    // the necessary metadata so these symbols are discoverable.
    cfg.set_dispatch_table(vec![
        b"refine_ext".to_vec(),
        b"accumulate_ext".to_vec(),
        b"on_transfer_ext".to_vec(),
    ]);
    let pvm = polkavm_linker::program_from_elf(cfg, &elf_data).context("convert ELF to PVM")?;

    let parts = polkavm_linker::ProgramParts::from_bytes(pvm.clone().into())
        .expect("failed to deserialize linked program");

    let metadata: Cow<'_, [u8]> = Cow::Borrowed(&[]);

    let blob = ProgramBlob::from_pvm(&parts, metadata)
			.to_vec()
			.expect("error serializing the blob");

    // Write PVM file
    std::fs::write(&args.output, blob).context("write .pvm output")?;

    // write jam file for debugging
    let stem = Path::new(&args.output)
        .file_stem()
        .map(|s| s.to_string_lossy().into_owned())
        .unwrap_or_default();

    let debug_file_path = format!("{}.debug.pvm", stem);
    
    std::fs::write(&debug_file_path, pvm).context("write debug output")?;

    println!(
        "Successfully built {} -> {} & {}",
        args.source.display(),
        args.output.display(),
        debug_file_path
    );

    // Temp dir will be automatically cleaned up

    Ok(())
} 