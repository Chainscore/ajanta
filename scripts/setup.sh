#!/bin/bash
# scripts/setup-uv.sh - New streamlined setup script using uv

set -e

# Navigate to the tests folder first
cd "$(dirname "$0")/../tests" || {
    echo "❌ ERROR: tests directory not found relative to script location"
    exit 1
}

echo "🚀 Setting up development environment with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed"
fi

# Verify Python version
echo "🐍 Checking Python version..."
if ! uv python find 3.12 &> /dev/null; then
    echo "📥 Installing Python 3.12..."
    uv python install 3.12
fi

# Initialize the workspace and install all dependencies
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
uv sync --all-extras
