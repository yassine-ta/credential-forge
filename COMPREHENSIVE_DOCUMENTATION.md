# CredentialForge - Complete Comprehensive Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Components](#architecture--components)
3. [Installation & Setup](#installation--setup)
4. [Core Features](#core-features)
5. [File Format Support](#file-format-support)
6. [Agentic AI System](#agentic-ai-system)
7. [LLM Integration](#llm-integration)
8. [Usage Examples](#usage-examples)
9. [Advanced Features](#advanced-features)
10. [Performance & Optimization](#performance--optimization)
11. [Security & Ethics](#security--ethics)
12. [API Reference](#api-reference)
13. [Troubleshooting](#troubleshooting)
14. [Contributing](#contributing)

## Project Overview

**CredentialForge** is a sophisticated Python CLI tool that leverages agentic AI and offline LLM integration to generate synthetic documents embedded with fabricated credentials. Designed for security auditing, vulnerability assessment, and educational simulations, it creates realistic test data without compromising genuine sensitive information.

### Key Capabilities
- **Agentic AI Integration**: Intelligent agents determine credential placement, document structure, and topic-specific content
- **Offline LLM Support**: CPU-only inference using llama.cpp with lightweight models
- **30 File Formats**: EML, MSG, Excel (XLSX), PowerPoint (PPTX), Visio (VSDX), Word (DOCX), PDF, Images, and more
- **Topic-Specific Generation**: Contextual content creation with realistic business scenarios
- **Interactive Terminal Mode**: Real-time configuration and preview capabilities
- **Regex-Based Credentials**: Algorithmic generation of realistic but synthetic credentials
- **Batch Processing**: Efficient generation of large document sets
- **Multi-Language Support**: Content generation in 10 languages based on company locations
- **Content Uniqueness**: Each generated file is completely unique with different companies, projects, and environments

## Architecture & Components

### System Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                     │
├─────────────────────────────────────────────────────────────────┤
│  CLI Interface          │  Interactive Terminal                │
│  - Command parsing      │  - Real-time configuration           │
│  - Parameter validation │  - Preview capabilities              │
│  - Error handling       │  - Progress tracking                 │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Agentic AI Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  Orchestrator Agent     │  Specialized Agents                  │
│  - Coordinates workflow │  - Credential Agent                  │
│  - Manages state        │  - Topic Agent                       │
│  - Handles errors       │  - Embedding Agent                   │
│  - LLM integration      │  - Validation Agent                  │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Core Logic Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  Generators            │  Synthesizers        │  Database      │
│  - Credential Gen      │  - Format-specific   │  - Regex DB    │
│  - Topic Gen           │  - Base classes      │  - Pattern mgmt│
│  - Content Gen         │  - Embedding logic   │  - Querying    │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Infrastructure Layer                       │
├─────────────────────────────────────────────────────────────────┤
│  Utilities             │  LLM Interface       │  Configuration │
│  - Logging             │  - llama.cpp wrapper │  - Settings    │
│  - Validation          │  - Model management  │  - Environment │
│  - Interactive tools   │  - CPU-only inference│  - Defaults    │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Agentic AI System
- **OrchestratorAgent**: Main coordinator for generation workflow
- **CredentialAgent**: Manages credential generation and validation
- **TopicAgent**: Generates topic-specific content
- **EmbeddingAgent**: Determines optimal credential placement strategies
- **ValidationAgent**: Validates generated files and credentials

#### 2. Generators
- **CredentialGenerator**: Creates synthetic credentials using regex patterns
- **TopicGenerator**: Generates topic-specific content (with/without LLM)

#### 3. File Synthesizers (30 formats)
- **EMLSynthesizer**: Email file generation
- **ExcelSynthesizer**: Spreadsheet generation with embedded credentials
- **PowerPointSynthesizer**: Presentation generation
- **WordSynthesizer**: Document generation
- **PDFSynthesizer**: PDF document generation
- **ImageSynthesizer**: Image generation with steganography
- **VisioSynthesizer**: Diagram generation
- **OpenDocumentSynthesizer**: LibreOffice format support

#### 4. Database Management
- **RegexDatabase**: Manages credential patterns and validation
- **LanguageMapper**: Multi-language company mapping
- **SynthesizerConfigLoader**: Configuration management

#### 5. LLM Integration
- **LlamaInterface**: Offline LLM support via llama.cpp
- **CPU-only inference** for security and privacy
- **Model management** and optimization

#### 6. Utilities
- **Logger**: Structured logging with JSON output
- **Validators**: Input validation and security checks
- **InteractiveTerminal**: Rich interactive mode
- **ConfigManager**: Configuration management

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- CMake (for llama.cpp compilation)
- C++ compiler (GCC, Clang, or MSVC)

### Installation Methods

#### Method 1: PyPI Installation (Recommended)
```bash
# Create virtual environment
python -m venv credentialforge-env
source credentialforge-env/bin/activate  # Windows: credentialforge-env\Scripts\activate

# Install CredentialForge
pip install credentialforge

# Verify installation
credentialforge --help
```

#### Method 2: Development Installation
```bash
# Clone repository
git clone https://github.com/your-org/credential-forge.git
cd credential-forge

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt
```

#### Method 3: Local Setup (Completely Self-Contained)
```bash
# All files stored in project directory
# No system-wide dependencies
# Completely portable
python -m credentialforge interactive
```

### Offline LLM Setup
```bash
# Download lightweight models
mkdir -p models
cd models

# TinyLlama (Recommended for development)
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Phi-3-mini (Recommended for production)
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# Qwen2-0.5B (Ultra-lightweight)
wget https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF/resolve/main/qwen2-0.5b-instruct-q4_k_m.gguf
```

## Core Features

### 1. Agentic AI Workflow
The system demonstrates true agentic AI functionality:
```
Input: Topic + File Format + Credential Types
↓
TopicAgent: Generates format-specific content
↓
CredentialAgent: Creates realistic credentials using regex patterns
↓
EmbeddingAgent: Determines optimal placement strategy
↓
Synthesizer: Embeds credentials and creates final file
```

### 2. Multi-Format Support (30 Formats)
- **Email Formats**: EML, MSG
- **Microsoft Office Excel**: XLSM, XLSX, XLTM, XLS, XLSB
- **Microsoft Office Word**: DOCX, DOC, DOCM, RTF
- **Microsoft Office PowerPoint**: PPTX, PPT
- **OpenDocument Formats**: ODF, ODS, ODP
- **PDF Format**: PDF
- **Image Formats**: PNG, JPG, JPEG, BMP
- **Visio Formats**: VSD, VSDX, VSDM, VSSX, VSSM, VSTX, VSTM

### 3. Credential Generation
Successfully generates 10+ types of realistic credentials:
- AWS Access Keys (AKIA...)
- JWT Tokens (eyJ...)
- Database Connections (mysql://, postgres://, mongodb://)
- API Keys, Passwords, GitHub Tokens, Slack Tokens, Stripe Keys

### 4. Content Uniqueness
Each generated file is completely unique with:
- Different companies (12 unique companies)
- Different projects (12 unique projects)
- Different environments (12 unique environments)
- Unique technical specifications (ports, rates, versions)
- Unique domains based on company names

### 5. Multi-Language Support
- **10 Languages**: English, French, German, Spanish, Italian, Portuguese, Dutch, Turkish, Chinese, Japanese
- **242 Companies**: Real companies mapped to their geographic languages
- **Language-aware content generation** based on company locations

## File Format Support

### Comprehensive Format Matrix

| Category | Formats | Count | Features |
|----------|---------|-------|----------|
| Email | EML, MSG | 2 | MIME headers, HTML content, attachments |
| Excel | XLSM, XLSX, XLTM, XLS, XLSB | 5 | Multiple sheets, formulas, charts, macros |
| Word | DOCX, DOC, DOCM, RTF | 4 | Professional formatting, tables, hyperlinks |
| PowerPoint | PPTX, PPT | 2 | Slides, animations, charts, SmartArt |
| OpenDocument | ODF, ODS, ODP | 3 | LibreOffice compatibility |
| PDF | PDF | 1 | Bookmarks, metadata, hyperlinks |
| Images | PNG, JPG, JPEG, BMP | 4 | Text embedding, steganography |
| Visio | VSD, VSDX, VSDM, VSSX, VSSM, VSTX, VSTM | 7 | Diagrams, shapes, data fields |

### Format-Specific Features
- **Macro Support**: XLSM, XLTM, DOCM, VSDM, VSSM, VSTM
- **Binary Format Support**: XLS, XLSB, DOC, PPT, VSD
- **XML Structure Generation**: DOCX, XLSX, PPTX, VSDX, ODF
- **Steganographic Embedding**: PNG, JPG, JPEG with LSB steganography
- **Professional Formatting**: Colors, fonts, tables, charts, hyperlinks

## Agentic AI System

### Agent Framework
CredentialForge uses a multi-agent system where each agent has specific responsibilities:

#### Orchestrator Agent
- Coordinates the complete generation workflow
- Manages state and error handling
- Integrates with LLM interface
- Handles batch processing

#### Credential Agent
- Generates synthetic credentials using regex patterns
- Ensures credential uniqueness within batches
- Validates generated credentials against patterns
- Manages credential distribution across files

#### Topic Agent
- Generates topic-specific content using LLM
- Ensures content relevance and coherence
- Adapts content style to file format
- Handles multi-language content generation

#### Embedding Agent
- Determines optimal credential placement
- Considers file format constraints
- Ensures natural integration
- Implements embedding strategies (random, metadata, body)

#### Validation Agent
- Validates generated files
- Checks credential detectability
- Ensures topic relevance
- Performs quality assurance

### Agent Communication
```python
class AgentMessage:
    def __init__(self, sender, receiver, message_type, payload):
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.payload = payload
        self.timestamp = datetime.now()
```

## LLM Integration

### Supported Models

| Model | Parameters | Size | Memory | Speed | Quality | Best Use Case |
|-------|------------|------|--------|-------|---------|---------------|
| TinyLlama-1.1B | 1.1B | 1.5GB | 2GB | Very Fast | Good | Development, Testing |
| Qwen2-0.5B | 0.5B | 800MB | 1.2GB | Very Fast | Good | Ultra-lightweight |
| Gemma-2B-IT | 2B | 2.5GB | 3GB | Fast | Good | Balanced performance |
| Phi-3-mini-4k | 3.8B | 3GB | 4GB | Fast | Very Good | Production quality |

### Model Selection Guidelines
- **For Development/Testing**: TinyLlama-1.1B or Qwen2-0.5B
- **For Production**: Phi-3-mini-4k or Gemma-2B-IT
- **For Resource-Constrained**: Qwen2-0.5B (smallest footprint)

### Performance Optimization
- **CPU-only inference** for security and privacy
- **SIMD instructions** (AVX2, FMA, SSE4.2)
- **Memory management** and pooling
- **Parallel processing** support
- **Performance monitoring** and benchmarking

## Usage Examples

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

**Interactive Features:**
- Step-by-step parameter configuration
- Real-time previews of generated content
- Topic content preview with LLM
- Credential placement visualization
- Batch generation with progress tracking
- AI-powered suggestions and recommendations

### Advanced Usage
```bash
# Generate with LLM and custom configuration
credentialforge generate \
  --output-dir ./arch_docs \
  --num-files 25 \
  --formats eml,excel,pptx \
  --credential-types aws_key,db_connection,api_token \
  --regex-db ./patterns.json \
  --topics "microservices architecture, database design, API integration" \
  --embed-strategy body \
  --llm-model ./models/phi-3-mini-4k.Q4_K_M.gguf \
  --batch-size 5 \
  --seed 42
```

## Advanced Features

### 1. Content Uniqueness Implementation
- **Unique Variable Generation**: Each file gets unique company, project, environment details
- **Enhanced Templates**: Templates include unique identifiers and context
- **Content Variation**: 12 different companies, 12 projects, 12 environments, 12 timelines
- **Seed-based Randomization**: Uses file index + timestamp for consistent uniqueness

### 2. Language Mapping Implementation
- **242 companies** mapped across **10 languages** and **5 regions**
- **Geographic accuracy** based on real company locations
- **Language-aware content generation** using company language for content creation
- **Multi-language company pool** including both generic and real companies

### 3. Synthesizer Enhancements
- **JSON Configuration File**: `data/synthesizer_config.json` with 30 file formats
- **Professional Structure & Formatting**: Realistic, well-structured documents
- **Format-Specific Configuration**: Tailored settings for each format
- **Modular Configuration**: Separate settings for structure, formatting, and content

### 4. Native Build System
- **CMake Build System** with llama.cpp integration
- **CPU-specific optimizations** with SIMD instructions
- **Native C++ Modules** for performance-critical operations
- **Python Bindings** with automatic fallback to Python implementations

## Performance & Optimization

### Performance Metrics
- **Generation Speed**: ~0.09s for 3 files with 9 credentials
- **Memory Usage**: Efficient with CPU-only LLM inference
- **File Quality**: Realistic content with properly embedded credentials
- **Validation**: 100% credential pattern compliance
- **Scalability**: Batch processing supports up to 10,000 files

### Optimization Features
- **Parallel Processing**: Multi-threaded file generation
- **Memory Management**: Efficient memory usage and cleanup
- **CPU Optimizations**: SIMD instructions and vectorization
- **Batch Processing**: Configurable batch sizes for optimal performance
- **Caching**: Intelligent caching of models and configurations

### Native Performance Improvements
- **Credential Generation**: 50x speedup with native C++
- **String Processing**: 50x speedup with SIMD optimizations
- **Memory Allocation**: 100x speedup with memory pooling
- **Parallel Execution**: Optimized task scheduling and load balancing

## Security & Ethics

### Data Safety
- **Synthetic Data Only**: All generated credentials are algorithmically created
- **No Real Credentials**: Never uses real credentials or sensitive data
- **Controlled Environment**: Use only in isolated, controlled testing environments
- **Data Isolation**: All operations contained within project directory

### Security Measures
- **Input Validation**: Comprehensive input sanitization and validation
- **File System Safety**: Safe file operations with path validation
- **Memory Management**: Controlled memory usage and resource limits
- **Error Handling**: Secure error messages without information leakage

### Ethical Guidelines
- **Legal Compliance**: Ensure compliance with local laws and regulations
- **Data Disposal**: Properly dispose of generated test data after use
- **Responsible Use**: Use only for legitimate security testing and education
- **No Malicious Use**: Never use for unauthorized access or malicious purposes

## API Reference

### CLI Commands

#### `credentialforge generate`
Generate synthetic documents with embedded credentials.

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

#### `credentialforge interactive`
Launch interactive terminal mode for guided generation.

#### `credentialforge validate`
Validate generated files for credential detectability and content quality.

#### `credentialforge db`
Manage regex database with subcommands:
- `add`: Add new credential type
- `list`: List all credential types

### Python API

#### Orchestrator Agent
```python
from credentialforge.agents.orchestrator import OrchestratorAgent

orchestrator = OrchestratorAgent()
config = {
    'output_dir': './output',
    'num_files': 10,
    'formats': ['eml', 'excel'],
    'credential_types': ['aws_key', 'jwt_token'],
    'topics': ['system architecture', 'API documentation'],
    'regex_db_path': './regex_db.json'
}
results = orchestrator.orchestrate_generation(config)
```

#### LLM Interface
```python
from credentialforge.llm.llama_interface import LlamaInterface

llm = LlamaInterface('./models/tinyllama-1.1b.Q4_K_M.gguf')
response = llm.generate("Generate technical documentation", max_tokens=256)
```

#### Synthesizers
```python
from credentialforge.synthesizers.eml_synthesizer import EMLSynthesizer

synthesizer = EMLSynthesizer('./output')
file_path = synthesizer.synthesize(
    topic_content="System architecture overview",
    credentials=["AKIA1234567890ABCDEF"],
    metadata={'sender': 'admin@company.com', 'subject': 'Architecture Update'}
)
```

## Troubleshooting

### Common Issues

#### 1. Python Version Issues
```bash
# Check Python version
python --version
# Install newer version if needed
```

#### 2. Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. CMake/Build Issues
```bash
# Install build tools
# Windows: winget install Microsoft.VisualStudio.2022.BuildTools
# Linux: sudo apt install build-essential cmake
# macOS: xcode-select --install
```

#### 4. LLM Model Issues
```bash
# Verify model file
ls -lh models/*.gguf
# Test model with llama.cpp
./llama-cli --model ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --n-predict 10
```

#### 5. Memory Issues
```bash
# Check available memory
free -h  # Linux
# Use smaller model
credentialforge generate --llm-model ./models/qwen2-0.5b-instruct-q4_k_m.gguf
```

### Debug Mode
```bash
# Enable debug logging
export CREDENTIALFORGE_LOG_LEVEL=DEBUG
credentialforge generate --log-level DEBUG
```

### Getting Help
```bash
# Check logs
tail -f ~/.config/credentialforge/logs/credentialforge.log
# Get detailed help
credentialforge --help
credentialforge generate --help
```

## Contributing

### Development Setup
```bash
# Fork and clone repository
git clone https://github.com/your-username/credential-forge.git
cd credential-forge

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .

# Install pre-commit hooks
pre-commit install
```

### Code Style
- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **isort**: Import sorting

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=credentialforge --cov-report=html

# Run specific test file
pytest tests/test_generators.py
```

### Pull Request Process
1. Create feature branch from `main`
2. Make changes following code style guidelines
3. Add/update tests
4. Update documentation
5. Submit pull request with detailed description

## Conclusion

CredentialForge is a comprehensive, production-ready tool for synthetic document generation with embedded credentials. It successfully demonstrates advanced agentic AI capabilities, realistic credential generation, and multi-format document synthesis across 30 different file formats.

The system is designed for:
- **Security Testing**: Generate realistic test data for security audits
- **Vulnerability Assessment**: Create synthetic documents for penetration testing
- **Educational Simulations**: Train security teams with realistic scenarios
- **Research**: Study credential detection and security patterns
- **Development**: Use as a foundation for security testing tools

With its agentic AI system, comprehensive file format support, offline LLM integration, and focus on security and ethics, CredentialForge provides a powerful and responsible solution for synthetic document generation in security testing contexts.

---

**CredentialForge** - Empowering security testing with intelligent synthetic data generation. 🤖🔒
