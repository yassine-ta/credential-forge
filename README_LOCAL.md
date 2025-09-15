# CredentialForge - Local Setup

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
