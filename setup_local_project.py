#!/usr/bin/env python3
"""Setup script to make CredentialForge completely local."""

import os
import sys
from pathlib import Path

def setup_local_project():
    """Setup CredentialForge to be completely local."""
    print("🏠 Setting up CredentialForge for local operation...")
    
    # Get project root
    project_root = Path(__file__).parent
    print(f"📁 Project root: {project_root}")
    
    # Create local directories
    directories = [
        "models",      # LLM models
        "cache",       # Caching
        "config",      # Configuration files
        "logs",        # Log files
        "output",      # Generated files
        "data",        # Data files (regex database, etc.)
        "templates"    # Template files
    ]
    
    print("\n📂 Creating local directories...")
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)
        print(f"  ✅ {directory}/")
    
    # Create local configuration file
    config_file = project_root / "config" / "local_config.json"
    config_content = {
        "project_root": str(project_root),
        "models_dir": str(project_root / "models"),
        "cache_dir": str(project_root / "cache"),
        "config_dir": str(project_root / "config"),
        "logs_dir": str(project_root / "logs"),
        "output_dir": str(project_root / "output"),
        "data_dir": str(project_root / "data"),
        "templates_dir": str(project_root / "templates"),
        "local_operation": True,
        "description": "CredentialForge local configuration - all files stored in project directory"
    }
    
    import json
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_content, f, indent=2)
    
    print(f"  ✅ config/local_config.json")
    
    # Create .gitignore for local files
    gitignore_content = """# Local project files
models/
cache/
logs/
output/
config/local_config.json

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Temporary files
*.tmp
*.temp
"""
    
    gitignore_file = project_root / ".gitignore"
    with open(gitignore_file, 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print(f"  ✅ .gitignore")
    
    # Create local environment file
    env_content = """# CredentialForge Local Environment
# All paths are relative to project root

CREDENTIALFORGE_PROJECT_ROOT=.
CREDENTIALFORGE_MODELS_DIR=./models
CREDENTIALFORGE_CACHE_DIR=./cache
CREDENTIALFORGE_CONFIG_DIR=./config
CREDENTIALFORGE_LOGS_DIR=./logs
CREDENTIALFORGE_OUTPUT_DIR=./output
CREDENTIALFORGE_DATA_DIR=./data
CREDENTIALFORGE_TEMPLATES_DIR=./templates

# Local operation mode
CREDENTIALFORGE_LOCAL_MODE=true
"""
    
    env_file = project_root / ".env.local"
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"  ✅ .env.local")
    
    # Create README for local setup
    readme_content = """# CredentialForge - Local Setup

This CredentialForge installation is configured for completely local operation.

## Directory Structure

```
credential_forge/
├── models/          # LLM models (downloaded locally)
├── cache/           # Caching and temporary files
├── config/          # Configuration files
├── logs/            # Log files
├── output/          # Generated synthetic documents
├── data/            # Data files (regex database, etc.)
├── templates/       # Template files
└── credentialforge/ # Main application code
```

## Local Operation Features

- ✅ All LLM models downloaded to `./models/`
- ✅ All caches stored in `./cache/`
- ✅ All logs written to `./logs/`
- ✅ All generated files saved to `./output/`
- ✅ All configuration in `./config/`
- ✅ No system-wide dependencies
- ✅ No global configuration files
- ✅ Completely portable

## Usage

```bash
# Interactive mode with local models
python -m credentialforge interactive

# Generate files with local storage
python -m credentialforge generate --output-dir ./output --num-files 5

# List available local models
python -c "from credentialforge.llm.llama_interface import LlamaInterface; print(LlamaInterface.list_available_models())"
```

## Downloading Models

Models are automatically downloaded to the local `./models/` directory when selected in interactive mode.

Available models:
- `tinyllama` - TinyLlama 1.1B (Fast, ~1GB)
- `phi3-mini` - Phi-3 Mini 4K (Balanced, ~2GB)
- `qwen2-0.5b` - Qwen2 0.5B (Very Fast, ~500MB)
- `gemma-2b` - Gemma 2B (Good Quality, ~1.5GB)

## Local Configuration

All configuration is stored in `./config/local_config.json` and can be customized for your local setup.
"""
    
    readme_file = project_root / "README_LOCAL.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"  ✅ README_LOCAL.md")
    
    print("\n🎉 Local setup complete!")
    print("\n📋 Summary:")
    print("  • All files will be stored in the project directory")
    print("  • LLM models will be downloaded to ./models/")
    print("  • Generated files will be saved to ./output/")
    print("  • Logs will be written to ./logs/")
    print("  • Configuration is in ./config/")
    print("  • No system-wide dependencies or files")
    
    print("\n🚀 To start using CredentialForge locally:")
    print("  python -m credentialforge interactive")
    
    return True

if __name__ == "__main__":
    try:
        setup_local_project()
    except Exception as e:
        print(f"❌ Error setting up local project: {e}")
        sys.exit(1)
