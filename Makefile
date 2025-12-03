# Ajanta SDK Makefile
# ====================
# One-command installation and build for JAM services

SHELL := /bin/bash

# Directories
ROOT_DIR := $(shell pwd)
BUILD_TOOL_DIR := $(ROOT_DIR)/ajanta-build-tool
AJ_LANG_DIR := $(ROOT_DIR)/aj-lang

# Detect install location
PREFIX ?= /usr/local
CARGO_INSTALL_ROOT ?= $(HOME)/.cargo/bin

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

.PHONY: all install install-python install-rust clean help check-deps

# Default target
all: install

# Check dependencies
check-deps:
	@echo "Checking dependencies..."
	@command -v cargo >/dev/null 2>&1 || { echo "Error: cargo not found. Install Rust: https://rustup.rs"; exit 1; }
	@command -v uv >/dev/null 2>&1 || { echo "Error: uv not found. Install: pip install uv"; exit 1; }
	@command -v riscv64-elf-gcc >/dev/null 2>&1 || { echo "$(YELLOW)Warning: riscv64-elf-gcc not found. You'll need it for PVM compilation.$(NC)"; }
	@echo "$(GREEN)✓ Dependencies OK$(NC)"

# Install everything
install: check-deps install-rust install-python
	@echo ""
	@echo "$(GREEN)╔════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║         Ajanta SDK installed successfully!         ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "Usage:"
	@echo "  ajanta build examples/python/hello.py -o build/hello.pvm"
	@echo ""
	@echo "Or step by step:"
	@echo "  ajanta transpile examples/python/hello.py -o build/hello.c"
	@echo "  ajanta compile build/hello.c -o build/hello.pvm"
	@echo ""

# Install Python packages (aj-lang + ajanta CLI)
install-python:
	@echo "Installing Python packages..."
	cd $(ROOT_DIR) && uv pip install -e $(AJ_LANG_DIR)
	cd $(ROOT_DIR) && uv pip install -e .
	@echo "$(GREEN)✓ Python packages installed$(NC)"

# Install Rust build tool
install-rust:
	@echo "Building and installing ajanta-build-tool..."
	cd $(BUILD_TOOL_DIR) && cargo build --release
	@# Copy to cargo bin if writable, otherwise suggest manual install
	@if [ -w "$(CARGO_INSTALL_ROOT)" ]; then \
		cp $(BUILD_TOOL_DIR)/target/release/ajanta-build-tool $(CARGO_INSTALL_ROOT)/ajanta-build-tool; \
		echo "$(GREEN)✓ ajanta-build-tool installed to $(CARGO_INSTALL_ROOT)$(NC)"; \
	else \
		echo "$(YELLOW)Note: Add $(BUILD_TOOL_DIR)/target/release to your PATH, or run:$(NC)"; \
		echo "  sudo cp $(BUILD_TOOL_DIR)/target/release/ajanta-build-tool $(PREFIX)/bin/"; \
	fi

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(ROOT_DIR)/build
	cd $(BUILD_TOOL_DIR) && cargo clean
	rm -rf $(AJ_LANG_DIR)/build
	rm -rf $(ROOT_DIR)/*.egg-info
	rm -rf $(AJ_LANG_DIR)/*.egg-info
	@echo "$(GREEN)✓ Cleaned$(NC)"

# Development install (editable mode)
dev: check-deps install-rust
	@echo "Installing in development mode..."
	cd $(ROOT_DIR) && uv pip install -e $(AJ_LANG_DIR)
	cd $(ROOT_DIR) && uv pip install -e ".[dev]"
	@echo "$(GREEN)✓ Development install complete$(NC)"

# Run tests
test:
	@echo "Running tests..."
	cd $(ROOT_DIR) && uv run pytest tests/ -v

# Build an example
example:
	@echo "Building example: examples/python/hello.py"
	mkdir -p $(ROOT_DIR)/build
	uv run ajanta build $(ROOT_DIR)/examples/python/hello.py -o $(ROOT_DIR)/build/hello.pvm --verbose

# Help
help:
	@echo "Ajanta SDK Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  install        Install everything (default)"
	@echo "  install-python Install Python packages only"
	@echo "  install-rust   Build and install Rust build tool only"
	@echo "  dev            Development install with test dependencies"
	@echo "  clean          Remove build artifacts"
	@echo "  test           Run tests"
	@echo "  example        Build the hello.py example"
	@echo "  help           Show this help"
	@echo ""
	@echo "Requirements:"
	@echo "  - Rust (cargo): https://rustup.rs"
	@echo "  - uv: pip install uv"
	@echo "  - riscv64-elf-gcc: for PVM compilation"
