# CredentialForge

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**CredentialForge** is a sophisticated Python CLI tool that leverages agentic AI and offline LLM integration to generate synthetic documents embedded with fabricated credentials. Designed for security auditing, vulnerability assessment, and educational simulations, it creates realistic test data without compromising genuine sensitive information.

## 🚀 Key Features

- **Agentic AI Integration**: Intelligent agents determine credential placement, document structure, and topic-specific content
- **Offline LLM Support**: CPU-only inference using llama.cpp with lightweight models
- **Multiple File Formats**: EML, MSG, Excel (XLSX), PowerPoint (PPTX), Visio (VSDX)
- **Topic-Specific Generation**: Contextual content creation (e.g., system architecture with DB/API integration)
- **Interactive Terminal Mode**: Real-time configuration and preview capabilities
- **Regex-Based Credentials**: Algorithmic generation of realistic but synthetic credentials
- **Batch Processing**: Efficient generation of large document sets

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Supported Models](#supported-models)
- [CLI Usage](#cli-usage)
- [Interactive Mode](#interactive-mode)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

## 🛠 Installation

### Prerequisites

- Python 3.10 or higher
- CMake (for llama.cpp compilation)
- C++ compiler (GCC, Clang, or MSVC)

### Install CredentialForge

```bash
# Clone the repository
git clone https://github.com/your-org/credential-forge.git
cd credential-forge

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Corporate Network Setup

If you're behind a corporate firewall or proxy, configure network settings:

**Windows (Automated):**
```cmd
setup_corporate_network.bat
```

**Cross-platform:**
```bash
python setup_corporate_network.py
```

**Manual Configuration:**
```cmd
set CREDENTIALFORGE_SSL_VERIFY=false
set CREDENTIALFORGE_TRUSTED_HOSTS=huggingface.co,pypi.org
set HTTP_PROXY=http://your-proxy:port
```

See [Corporate Network Setup Guide](CORPORATE_NETWORK_SETUP.md) for detailed instructions.

### Setup Offline LLM (Optional)

```bash
# Clone and build llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DLLAMA_CUBLAS=OFF -DLLAMA_CLBLAST=OFF -DLLAMA_HIPBLAS=OFF -DLLAMA_METAL=OFF -DLLAMA_VULKAN=OFF ..
cmake --build . --config Release

# Download a lightweight model (see Supported Models section)
# Example: Download TinyLlama-1.1B-Chat-v1.0.Q4_K_M.gguf
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

## 🚀 Quick Start

### Basic Usage

```bash
# Generate a single EML file with AWS credentials
credentialforge generate \
  --output-dir ./test_docs \
  --num-files 1 \
  --formats eml \
  --credential-types aws_key \
  --regex-db ./regex_db.json \
  --topics "system architecture with database integration"

# Generate multiple files with different formats
credentialforge generate \
  --output-dir ./bulk_docs \
  --num-files 50 \
  --formats eml,excel,pptx \
  --credential-types aws_key,jwt_token,db_connection \
  --regex-db ./regex_db.json \
  --topics "API documentation, database schemas, system integration" \
  --batch-size 10
```

### Interactive Mode

```bash
# Launch interactive terminal for guided generation
credentialforge interactive
```

## ⚙️ Configuration

### Regex Database Format

Create a `regex_db.json` file with credential patterns:

```json
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
    }
  ]
}
```

## 🤖 Supported Models

### Recommended Lightweight LLMs for CPU-Only Inference

| Model | Size | Memory | Speed | Quality | Download |
|-------|------|--------|-------|---------|----------|
| **TinyLlama-1.1B-Chat** | 1.1B | ~1.5GB | Fast | Good | [HuggingFace](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF) |
| **Phi-3-mini-4k** | 3.8B | ~3GB | Fast | Very Good | [HuggingFace](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf) |
| **Qwen2-0.5B-Instruct** | 0.5B | ~800MB | Very Fast | Good | [HuggingFace](https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF) |
| **Gemma-2B-IT** | 2B | ~2.5GB | Fast | Good | [HuggingFace](https://huggingface.co/google/gemma-2b-it-gguf) |

### Model Selection Guidelines

- **For Development/Testing**: TinyLlama-1.1B or Qwen2-0.5B
- **For Production**: Phi-3-mini-4k or Gemma-2B-IT
- **For Resource-Constrained**: Qwen2-0.5B (smallest footprint)

### Quantization Levels

- **Q4_K_M**: Best balance of size and quality (recommended)
- **Q4_0**: Smaller size, slightly lower quality
- **Q8_0**: Higher quality, larger size

## 📖 CLI Usage

### Command Structure

```bash
credentialforge [COMMAND] [OPTIONS]
```

### Commands

#### `generate` - Generate synthetic documents

```bash
credentialforge generate [OPTIONS]
```

**Options:**
- `--output-dir TEXT`: Output directory for generated files (required)
- `--num-files INTEGER`: Number of files to generate (default: 1)
- `--formats TEXT`: Comma-separated formats (eml,msg,xlsx,pptx,vsdx) (default: eml)
- `--credential-types TEXT`: Comma-separated credential types (required)
- `--regex-db TEXT`: Path to regex database file (required)
- `--topics TEXT`: Comma-separated topics for content generation (required)
- `--embed-strategy TEXT`: Embedding strategy (random,metadata,body) (default: random)
- `--batch-size INTEGER`: Batch size for parallel processing (default: 10)
- `--seed INTEGER`: Random seed for reproducible results
- `--llm-model TEXT`: Path to GGUF model file (optional)
- `--log-level TEXT`: Logging level (DEBUG,INFO,WARNING,ERROR) (default: INFO)

#### `interactive` - Launch interactive terminal mode

```bash
credentialforge interactive
```

#### `validate` - Validate generated files

```bash
credentialforge validate --file PATH
```

#### `db` - Manage regex database

```bash
# Add new credential type
credentialforge db add --type TEXT --regex TEXT --description TEXT

# List credential types
credentialforge db list
```

### Examples

```bash
# Generate architecture documentation with embedded credentials
credentialforge generate \
  --output-dir ./arch_docs \
  --num-files 25 \
  --formats eml,excel,pptx \
  --credential-types aws_key,db_connection,api_token \
  --regex-db ./patterns.json \
  --topics "microservices architecture, database design, API integration" \
  --embed-strategy body \
  --llm-model ./models/phi-3-mini-4k.Q4_K_M.gguf

# Validate generated files
credentialforge validate --file ./arch_docs/fake_architecture_001.eml
```

## 🎮 Interactive Mode

The interactive mode provides a guided experience for document generation:

```bash
credentialforge interactive
```

**Interactive Features:**
- Step-by-step parameter configuration
- Real-time previews of generated content
- Topic content preview with LLM
- Credential placement visualization
- Batch generation with progress tracking

## 🏗 Architecture

CredentialForge follows a modular, layered architecture:

```
┌─────────────────────────────────────┐
│           CLI Layer                 │
│  ┌─────────────────────────────────┐│
│  │ credentialforge.cli             ││
│  │ - Command parsing               ││
│  │ - Interactive terminal          ││
│  │ - Parameter validation          ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│        Agentic AI Layer             │
│  ┌─────────────────────────────────┐│
│  │ agents/orchestrator.py          ││
│  │ - Orchestrates generation       ││
│  │ - LLM integration               ││
│  │ - Topic content generation      ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│        Core Logic Layer             │
│  ┌─────────────────────────────────┐│
│  │ generators/                     ││
│  │ - credential_generator.py       ││
│  │ - topic_generator.py            ││
│  │ synthesizers/                   ││
│  │ - eml_synthesizer.py            ││
│  │ - excel_synthesizer.py          ││
│  │ - pptx_synthesizer.py           ││
│  │ db/                             ││
│  │ - regex_db.py                   ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│        Utilities Layer              │
│  ┌─────────────────────────────────┐│
│  │ utils/                          ││
│  │ - logger.py                     ││
│  │ - validators.py                 ││
│  │ - interactive.py                ││
│  │ - config.py                     ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│        Offline LLM Layer            │
│  ┌─────────────────────────────────┐│
│  │ llm/llama_interface.py          ││
│  │ - llama.cpp integration         ││
│  │ - CPU-only inference            ││
│  │ - Model management              ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

## 🔧 Development

### Project Structure

```
credentialforge/
├── cli.py                    # Main CLI entry point
├── agents/
│   ├── __init__.py
│   └── orchestrator.py       # Main AI orchestrator
├── generators/
│   ├── __init__.py
│   ├── credential_generator.py
│   └── topic_generator.py
├── synthesizers/
│   ├── __init__.py
│   ├── base.py
│   ├── eml_synthesizer.py
│   ├── excel_synthesizer.py
│   ├── pptx_synthesizer.py
│   └── vsdx_synthesizer.py
├── db/
│   └── regex_db.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── validators.py
│   ├── interactive.py
│   └── config.py
├── llm/
│   └── llama_interface.py
├── tests/
│   ├── test_generators.py
│   ├── test_synthesizers.py
│   └── test_agents.py
├── docs/
│   ├── architecture.md
│   ├── api_reference.md
│   └── examples.md
├── requirements.txt
├── setup.py
└── README.md
```

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=credentialforge --cov-report=html
```

### Code Style

```bash
# Format code
black credentialforge/

# Lint code
flake8 credentialforge/

# Type checking
mypy credentialforge/
```

## 🔧 Troubleshooting

### Network Issues

**SSL Certificate Errors:**
```bash
# Configure for corporate networks
python -m credentialforge network --no-ssl-verify --trusted-hosts huggingface.co,pypi.org

# Or set environment variables
set CREDENTIALFORGE_SSL_VERIFY=false
set CREDENTIALFORGE_TRUSTED_HOSTS=huggingface.co,pypi.org
```

**Proxy Configuration:**
```bash
# Configure proxy
python -m credentialforge network --proxy http://proxy.company.com:8080

# Test connectivity
python -m credentialforge network --test
```

**Model Download Failures:**
```bash
# Test network configuration
python test_ssl_config.py

# Manual model download
curl -k -L -o models/phi3-mini.gguf "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
```

### Build Issues

**llama-cpp-python Build Errors:**
```bash
# Install Visual Studio Build Tools (Windows)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Alternative: Use pre-compiled wheels
pip install llama-cpp-python --only-binary=all
```

**CMake Not Found:**
```bash
# Install CMake
pip install cmake
# Or download from: https://cmake.org/download/
```

For more detailed troubleshooting, see [Corporate Network Setup Guide](CORPORATE_NETWORK_SETUP.md).

## ⚠️ Security and Ethics

**Important Disclaimers:**

- **Synthetic Data Only**: All generated credentials are algorithmically created and have no real-world validity
- **Controlled Environment**: Use only in isolated, controlled testing environments
- **No Real Credentials**: Never use real credentials or sensitive data
- **Legal Compliance**: Ensure compliance with local laws and regulations
- **Data Disposal**: Properly dispose of generated test data after use

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/credential-forge.git
cd credential-forge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .

# Run pre-commit hooks
pre-commit install
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [llama.cpp](https://github.com/ggerganov/llama.cpp) for offline LLM inference
- [LangChain](https://github.com/langchain-ai/langchain) for agentic AI framework
- [Click](https://github.com/pallets/click) for CLI framework
- [Prompt Toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) for interactive terminal

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/credential-forge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/credential-forge/discussions)

---

**CredentialForge** - Empowering security testing with intelligent synthetic data generation.
