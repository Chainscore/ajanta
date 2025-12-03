use std::path::PathBuf;
use std::fs;
use anyhow::{Context, Result};
use clap::Parser;
use polkavm_common::program::ProgramBlob;

/// Disassemble a PVM program blob
#[derive(Parser)]
pub struct Args {
    /// Input .pvm file
    pub input: PathBuf,

    /// Disassembly format (guest|guest-native|native|diff)
    #[arg(long, default_value = "guest")]
    pub format: String,
}

pub fn run(args: Args) -> Result<()> {
    let blob_data = fs::read(&args.input).with_context(|| "read pvm file")?;
    let blob = ProgramBlob::parse(blob_data.into())?;

    use polkavm_disassembler::DisassemblyFormat as F;
    let format = match args.format.as_str() {
        "guest" => F::Guest,
        "guestnative" | "guest-native" => F::GuestAndNative,
        "native" => F::Native,
        "diff" | "difffriendly" => F::DiffFriendly,
        other => anyhow::bail!("unknown format: {}", other),
    };

    let mut dis = polkavm_disassembler::Disassembler::new(&blob, format)?;
    dis.show_raw_bytes(true);
    dis.display_gas()?;
    dis.disassemble_into(std::io::stdout())?;

    Ok(())
} 