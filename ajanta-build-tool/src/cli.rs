use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(author, version, about)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Build a C source file into a PVM service
    Build(crate::commands::build::Args),
    /// Disassemble a PVM program blob
    Disasm(crate::commands::disasm::Args),
    /// Build an pvm blob using polkavm-cc
    PolkavmCcBuild(crate::commands::polkavm_cc_build::Args),
}