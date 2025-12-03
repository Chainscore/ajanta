use std::process::Command;
use anyhow::{anyhow, Context, Result};

/// Run a command and return an error if it fails
pub fn run_command(cmd: &mut Command, description: &str) -> Result<()> {
    let output = cmd.output().with_context(|| format!("execute command for {}", description))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        let stdout = String::from_utf8_lossy(&output.stdout);
        return Err(anyhow!(
            "Command failed for {}: {}\nstdout: {}\nstderr: {}",
            description,
            output.status,
            stdout,
            stderr
        ));
    }

    Ok(())
} 