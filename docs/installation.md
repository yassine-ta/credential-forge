# CredentialForge Installation Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Development Setup](#development-setup)
4. [Offline LLM Setup](#offline-llm-setup)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.10 or higher
- **Memory**: Minimum 4GB RAM (8GB+ recommended for LLM integration)
- **Storage**: 2GB free space (10GB+ for models)
- **CPU**: Multi-core processor (4+ cores recommended)

### Required Software

#### Windows
```powershell
# Install Python 3.10+
winget install Python.Python.3.11

# Install Git
winget install Git.Git

# Install CMake (for llama.cpp)
winget install Kitware.CMake

# Install Visual Studio Build Tools (for C++ compilation)
winget install Microsoft.VisualStudio.2022.BuildTools
```

#### macOS
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.10+
brew install python@3.11

# Install Git
brew install git

# Install CMake
brew install cmake

# Install Xcode Command Line Tools (for C++ compilation)
xcode-select --install
```

#### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install Python 3.10+
sudo apt install python3.11 python3.11-venv python3.11-dev

# Install Git
sudo apt install git

# Install CMake
sudo apt install cmake

# Install build tools
sudo apt install build-essential

# Install additional dependencies
sudo apt install libssl-dev libffi-dev
```

#### Linux (CentOS/RHEL/Fedora)
```bash
# Install Python 3.10+
sudo dnf install python3.11 python3.11-devel python3.11-venv

# Install Git
sudo dnf install git

# Install CMake
sudo dnf install cmake

# Install build tools
sudo dnf groupinstall "Development Tools"
```

## Installation Methods

### Method 1: PyPI Installation (Recommended)

```bash
# Create virtual environment
python -m venv credentialforge-env

# Activate virtual environment
# Windows:
credentialforge-env\Scripts\activate
# macOS/Linux:
source credentialforge-env/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install CredentialForge
pip install credentialforge

# Verify installation
credentialforge --help
```

### Method 2: Development Installation

```bash
# Clone repository
git clone https://github.com/your-org/credential-forge.git
cd credential-forge

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Verify installation
credentialforge --help
```

### Method 3: Docker Installation

```bash
# Clone repository
git clone https://github.com/your-org/credential-forge.git
cd credential-forge

# Build Docker image
docker build -t credentialforge .

# Run container
docker run -it --rm -v $(pwd)/output:/app/output credentialforge

# Or run with specific command
docker run -it --rm -v $(pwd)/output:/app/output credentialforge generate \
  --output-dir /app/output \
  --num-files 5 \
  --formats eml \
  --credential-types aws_access_key \
  --regex-db /app/regex_db.json \
  --topics "system architecture"
```

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/credential-forge.git
cd credential-forge
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install base dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### 4. Install Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

### 5. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=credentialforge --cov-report=html

# Run specific test file
pytest tests/test_generators.py

# Run with verbose output
pytest -v
```

## Offline LLM Setup

### 1. Install llama.cpp

```bash
# Clone llama.cpp repository
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Create build directory
mkdir build && cd build

# Configure CMake (CPU-only, no GPU dependencies)
cmake -DCMAKE_BUILD_TYPE=Release \
      -DLLAMA_CUBLAS=OFF \
      -DLLAMA_CLBLAST=OFF \
      -DLLAMA_HIPBLAS=OFF \
      -DLLAMA_METAL=OFF \
      -DLLAMA_VULKAN=OFF \
      ..

# Build
cmake --build . --config Release

# Verify build
./bin/llama-cli --help
```

### 2. Install llama-cpp-python

```bash
# Install with CPU-only support
CMAKE_ARGS="-DLLAMA_CUBLAS=OFF -DLLAMA_CLBLAST=OFF -DLLAMA_HIPBLAS=OFF -DLLAMA_METAL=OFF -DLLAMA_VULKAN=OFF" pip install llama-cpp-python

# Or install from source
pip install llama-cpp-python --no-cache-dir --force-reinstall --no-deps
```

### 3. Download Models

```bash
# Create models directory
mkdir -p models

# Download TinyLlama (Recommended for development)
cd models
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Download Phi-3-mini (Recommended for production)
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# Download Qwen2-0.5B (Ultra-lightweight)
wget https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF/resolve/main/qwen2-0.5b-instruct-q4_k_m.gguf

# Verify downloads
ls -lh *.gguf
```

### 4. Test LLM Integration

```bash
# Test with llama.cpp directly
./llama-cli --model ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --n-predict 50 -i

# Test with CredentialForge
credentialforge generate \
  --output-dir ./test \
  --num-files 1 \
  --formats eml \
  --credential-types aws_access_key \
  --regex-db ./regex_db.json \
  --topics "system architecture" \
  --llm-model ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

## Configuration

### 1. Create Configuration File

```bash
# Create config directory
mkdir -p ~/.config/credentialforge

# Create configuration file
cat > ~/.config/credentialforge/config.yaml << 'EOF'
# CredentialForge Configuration

# Default settings
defaults:
  output_dir: ./output
  batch_size: 10
  log_level: INFO
  embed_strategy: random

# LLM settings
llm:
  default_model: ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
  n_threads: 4
  n_ctx: 2048
  temperature: 0.7

# File format settings
formats:
  eml:
    max_size: 10MB
    embed_locations: [body, headers]
  excel:
    max_worksheets: 10
    embed_locations: [cells, formulas]
  pptx:
    max_slides: 50
    embed_locations: [content, notes]

# Security settings
security:
  isolation_mode: true
  allowed_directories: [./output, ./test]
  max_file_size: 50MB
EOF
```

### 2. Create Regex Database

```bash
# Create sample regex database
cat > regex_db.json << 'EOF'
{
  "credentials": [
    {
      "type": "aws_access_key",
      "regex": "^AKIA[0-9A-Z]{16}$",
      "description": "AWS Access Key ID",
      "generator": "random_string(20, 'A-Z0-9')"
    },
    {
      "type": "jwt_token",
      "regex": "^eyJ[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+$",
      "description": "JWT Token",
      "generator": "base64_encode(header.payload.signature)"
    },
    {
      "type": "db_connection",
      "regex": "^(mysql|postgres)://[a-zA-Z0-9]+:[a-zA-Z0-9]+@[a-zA-Z0-9.]+:[0-9]+/[a-zA-Z0-9]+$",
      "description": "Database Connection String",
      "generator": "construct_db_string()"
    },
    {
      "type": "api_key",
      "regex": "^[A-Za-z0-9]{32}$",
      "description": "Generic API Key",
      "generator": "random_string(32, 'A-Za-z0-9')"
    },
    {
      "type": "password",
      "regex": "^[A-Za-z0-9@#$%^&+=]{8,}$",
      "description": "Password",
      "generator": "random_password(12)"
    }
  ]
}
EOF
```

### 3. Environment Variables

```bash
# Set environment variables
export CREDENTIALFORGE_CONFIG_DIR=~/.config/credentialforge
export CREDENTIALFORGE_LOG_LEVEL=INFO
export CREDENTIALFORGE_DEFAULT_OUTPUT_DIR=./output
export CREDENTIALFORGE_DEFAULT_MODEL=./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Windows PowerShell:
$env:CREDENTIALFORGE_CONFIG_DIR = "$env:USERPROFILE\.config\credentialforge"
$env:CREDENTIALFORGE_LOG_LEVEL = "INFO"
$env:CREDENTIALFORGE_DEFAULT_OUTPUT_DIR = ".\output"
$env:CREDENTIALFORGE_DEFAULT_MODEL = ".\models\tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
```

## Verification

### 1. Basic Verification

```bash
# Check installation
credentialforge --version

# Check help
credentialforge --help

# List available commands
credentialforge --help-commands
```

### 2. Test Generation

```bash
# Create test output directory
mkdir -p test_output

# Test basic generation
credentialforge generate \
  --output-dir ./test_output \
  --num-files 1 \
  --formats eml \
  --credential-types aws_access_key \
  --regex-db ./regex_db.json \
  --topics "system architecture"

# Verify output
ls -la test_output/
cat test_output/*.eml
```

### 3. Test Interactive Mode

```bash
# Test interactive mode
credentialforge interactive
```

### 4. Test LLM Integration

```bash
# Test with LLM
credentialforge generate \
  --output-dir ./test_output \
  --num-files 1 \
  --formats eml \
  --credential-types aws_access_key \
  --regex-db ./regex_db.json \
  --topics "microservices architecture" \
  --llm-model ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Verify LLM-generated content
cat test_output/*.eml
```

### 5. Test Validation

```bash
# Test file validation
credentialforge validate --file ./test_output/*.eml --verbose
```

### 6. Performance Test

```bash
# Test batch generation
time credentialforge generate \
  --output-dir ./test_output \
  --num-files 10 \
  --formats eml,excel \
  --credential-types aws_access_key,jwt_token \
  --regex-db ./regex_db.json \
  --topics "system architecture,API documentation" \
  --batch-size 5
```

## Troubleshooting

### Common Issues

#### 1. Python Version Issues

```bash
# Check Python version
python --version

# If version is too old, install newer version
# Windows:
winget install Python.Python.3.11
# macOS:
brew install python@3.11
# Linux:
sudo apt install python3.11
```

#### 2. Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. CMake/Build Issues

```bash
# Install build tools
# Windows:
winget install Microsoft.VisualStudio.2022.BuildTools
# macOS:
xcode-select --install
# Linux:
sudo apt install build-essential cmake
```

#### 4. LLM Model Issues

```bash
# Verify model file
ls -lh models/*.gguf

# Test model with llama.cpp
./llama-cli --model ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --n-predict 10

# Reinstall llama-cpp-python
pip uninstall llama-cpp-python
CMAKE_ARGS="-DLLAMA_CUBLAS=OFF" pip install llama-cpp-python --no-cache-dir
```

#### 5. Memory Issues

```bash
# Check available memory
free -h  # Linux
vm_stat  # macOS
Get-ComputerInfo | Select-Object TotalPhysicalMemory  # Windows

# Use smaller model
credentialforge generate \
  --llm-model ./models/qwen2-0.5b-instruct-q4_k_m.gguf \
  # ... other options
```

#### 6. Permission Issues

```bash
# Fix permissions
chmod +x credentialforge
chmod -R 755 ~/.config/credentialforge

# Run with sudo if necessary (not recommended)
sudo credentialforge --help
```

### Debug Mode

```bash
# Enable debug logging
export CREDENTIALFORGE_LOG_LEVEL=DEBUG
credentialforge generate --log-level DEBUG # ... other options

# Or use Python debugger
python -m pdb -m credentialforge generate # ... other options
```

### Getting Help

```bash
# Check logs
tail -f ~/.config/credentialforge/logs/credentialforge.log

# Get detailed help
credentialforge --help
credentialforge generate --help
credentialforge interactive --help

# Check system information
credentialforge --version --verbose
```

### Support Channels

- **GitHub Issues**: [Report bugs and request features](https://github.com/your-org/credential-forge/issues)
- **GitHub Discussions**: [Community support](https://github.com/your-org/credential-forge/discussions)
- **Documentation**: [Full documentation](https://github.com/your-org/credential-forge/docs)

### Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Uninstall package
pip uninstall credentialforge

# Remove configuration
rm -rf ~/.config/credentialforge

# Remove models (optional)
rm -rf models/
```

This installation guide provides comprehensive instructions for setting up CredentialForge in various environments, ensuring a smooth installation and configuration process.
