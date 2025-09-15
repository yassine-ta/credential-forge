#!/usr/bin/env python3
"""Demonstration of CredentialForge Local Project Setup."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.llm.llama_interface import LlamaInterface


def demonstrate_local_project():
    """Demonstrate the local project setup."""
    print("🏠 CredentialForge Local Project Demonstration")
    print("=" * 60)
    print()
    
    # Show project structure
    print("📁 Local Project Structure:")
    print("E:\\credential_forge\\")
    print("├── models/          # LLM models (downloaded locally)")
    print("├── cache/           # Caching and temporary files")
    print("├── config/          # Configuration files")
    print("├── logs/            # Log files")
    print("├── output/          # Generated synthetic documents")
    print("├── data/            # Data files (regex database, etc.)")
    print("├── templates/       # Template files")
    print("└── credentialforge/ # Main application code")
    print()
    
    # Show local configuration
    print("⚙️  Local Configuration:")
    config_file = project_root / "config" / "local_config.json"
    if config_file.exists():
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        for key, value in config.items():
            if key != "description":
                print(f"  • {key}: {value}")
    print()
    
    # Show available local models
    print("🤖 Local LLM Models:")
    available_models = LlamaInterface.list_available_models()
    if available_models:
        for model in available_models:
            model_path = project_root / "models" / f"{model}.gguf"
            if model_path.exists():
                size_mb = model_path.stat().st_size / (1024 * 1024)
                print(f"  ✅ {model} ({size_mb:.1f} MB) - Local")
            else:
                print(f"  ⬇️  {model} - Available for download")
    else:
        print("  📥 No models downloaded yet")
        print("  Models will be downloaded to ./models/ when selected")
    print()
    
    # Show local directories
    print("📂 Local Directories Status:")
    directories = ["models", "cache", "config", "logs", "output", "data", "templates"]
    for directory in directories:
        dir_path = project_root / directory
        if dir_path.exists():
            file_count = len(list(dir_path.iterdir()))
            print(f"  ✅ {directory}/ ({file_count} items)")
        else:
            print(f"  ❌ {directory}/ (not found)")
    print()
    
    # Show local operation benefits
    print("🎯 Local Operation Benefits:")
    print("  ✅ All files stored in project directory")
    print("  ✅ No system-wide dependencies")
    print("  ✅ No global configuration files")
    print("  ✅ Completely portable")
    print("  ✅ LLM models downloaded locally")
    print("  ✅ All caches stored locally")
    print("  ✅ All logs written locally")
    print("  ✅ All generated files saved locally")
    print()
    
    # Show usage examples
    print("🚀 Local Usage Examples:")
    print("  # Interactive mode with local models")
    print("  python -m credentialforge interactive")
    print()
    print("  # Generate files with local storage")
    print("  python -m credentialforge generate --output-dir ./output --num-files 5")
    print()
    print("  # List available local models")
    print("  python -c \"from credentialforge.llm.llama_interface import LlamaInterface; print(LlamaInterface.list_available_models())\"")
    print()
    
    # Show model download capability
    print("📥 Model Download Capability:")
    print("  When you select a model in interactive mode:")
    print("  1. System checks ./models/ directory")
    print("  2. If model not found, downloads to ./models/")
    print("  3. Model is stored locally for future use")
    print("  4. No internet required after initial download")
    print()
    
    print("🎉 CredentialForge is now completely local!")
    print("All downloads, caches, and dependencies are stored in the current folder.")
    print("=" * 60)


def show_local_file_examples():
    """Show examples of local file operations."""
    print("\n📄 Local File Examples:")
    print("-" * 30)
    
    # Show local config
    config_file = project_root / "config" / "local_config.json"
    if config_file.exists():
        print(f"✅ Local config: {config_file}")
    
    # Show local data
    data_file = project_root / "data" / "regex_db.json"
    if data_file.exists():
        print(f"✅ Local regex database: {data_file}")
    
    # Show local output
    output_dir = project_root / "output"
    if output_dir.exists():
        output_files = list(output_dir.glob("*"))
        if output_files:
            print(f"✅ Local output files: {len(output_files)} files in {output_dir}")
        else:
            print(f"📁 Local output directory: {output_dir} (empty)")
    
    # Show local logs
    logs_dir = project_root / "logs"
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        if log_files:
            print(f"✅ Local log files: {len(log_files)} files in {logs_dir}")
        else:
            print(f"📁 Local logs directory: {logs_dir} (empty)")
    
    # Show local models
    models_dir = project_root / "models"
    if models_dir.exists():
        model_files = list(models_dir.glob("*.gguf"))
        if model_files:
            print(f"✅ Local model files: {len(model_files)} files in {models_dir}")
        else:
            print(f"📁 Local models directory: {models_dir} (empty)")


if __name__ == "__main__":
    try:
        demonstrate_local_project()
        show_local_file_examples()
        
        print("\n🚀 To start using CredentialForge locally:")
        print("   python -m credentialforge interactive")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
