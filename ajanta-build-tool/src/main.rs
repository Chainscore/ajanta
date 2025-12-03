mod cli;
mod commands;

use anyhow::Result;
use clap::Parser;

fn main() -> Result<()> {
    let cli = cli::Cli::parse();
    
    match cli.command {
        cli::Commands::Build(args) => commands::build::run(args),
        cli::Commands::Disasm(args) => commands::disasm::run(args),
        cli::Commands::PolkavmCcBuild(args) => commands::polkavm_cc_build::run(args),
    }
} 