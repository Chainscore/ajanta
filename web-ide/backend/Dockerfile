FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including build tools for Cython, Rust, and C/C++ (clang)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gcc \
    g++ \
    clang \
    llvm \
    lld \
    xz-utils \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install RISC-V cross-compiler toolchain (required by ajanta-build-tool)
# Using riscv-collab/riscv-gnu-toolchain nightly releases
RUN curl -L https://github.com/riscv-collab/riscv-gnu-toolchain/releases/download/2025.11.27/riscv64-elf-ubuntu-22.04-gcc.tar.xz -o /tmp/riscv.tar.xz \
    && mkdir -p /opt/riscv \
    && tar -xJf /tmp/riscv.tar.xz -C /opt/riscv --strip-components=1 \
    && rm /tmp/riscv.tar.xz \
    && ln -s /opt/riscv/bin/riscv64-unknown-elf-gcc /opt/riscv/bin/riscv64-elf-gcc \
    && ln -s /opt/riscv/bin/riscv64-unknown-elf-g++ /opt/riscv/bin/riscv64-elf-g++ \
    && ln -s /opt/riscv/bin/riscv64-unknown-elf-ld /opt/riscv/bin/riscv64-elf-ld \
    && ln -s /opt/riscv/bin/riscv64-unknown-elf-as /opt/riscv/bin/riscv64-elf-as

ENV PATH="/opt/riscv/bin:${PATH}"

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install cython and build dependencies
RUN pip install cython setuptools wheel mypy

# Copy and build ajanta-build-tool
COPY ajanta-build-tool /app/ajanta-build-tool
WORKDIR /app/ajanta-build-tool
RUN cargo build --release
RUN cp target/release/ajanta-build-tool /usr/local/bin/

# Copy the entire project structure needed by backend
WORKDIR /app
# Copy SDK for C/C++ headers (ajanta-build-tool expects sdk/src at CARGO_MANIFEST_DIR/../sdk)
COPY sdk /app/sdk
COPY playground/deps/tsrkit-types /app/playground/deps/tsrkit-types
COPY playground/deps/tsrkit-pvm /app/playground/deps/tsrkit-pvm
COPY playground/deps/tsrkit-asm /app/playground/deps/tsrkit-asm
COPY playground/playground /app/playground/playground
COPY aj-lang /app/aj-lang
COPY examples /app/examples

# Copy backend code
COPY web-ide/backend /app/web-ide/backend

# Install tsrkit-types first (it's a dependency)
WORKDIR /app/playground/deps/tsrkit-types
RUN pip install .

# Build tsrkit-pvm with Cython extensions explicitly
WORKDIR /app/playground/deps/tsrkit-pvm
ENV PVM_BUILD_MODE=cython
RUN python setup.py build_ext --inplace && pip install .

# Install tsrkit-asm
WORKDIR /app/playground/deps/tsrkit-asm
RUN pip install .

# Install aj-lang (Python JAM compiler) and create 'ajanta' symlink
WORKDIR /app/aj-lang
RUN pip install . && ln -s $(which aj) /usr/local/bin/ajanta

# Set working directory to backend
WORKDIR /app/web-ide/backend

# Install backend dependencies directly (no venv)
RUN pip install fastapi uvicorn python-multipart websockets bitarray safe-pysha3

# Set PYTHONPATH
ENV PYTHONPATH="/app:/app/aj-lang:/app/playground/deps/tsrkit-pvm"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
