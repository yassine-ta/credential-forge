#!/usr/bin/env python3
"""Test script to verify Qwen2-0.5B model download."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.llm.llama_interface import LlamaInterface


def test_qwen_download():
    """Test Qwen2-0.5B model download."""
    print("🧪 Testing Qwen2-0.5B Model Download")
    print("=" * 50)
    
    try:
        print("📥 Downloading Qwen2-0.5B model...")
        model_path = LlamaInterface.download_model('qwen2-0.5b')
        print(f"✅ Model downloaded successfully to: {model_path}")
        
        # Check if file exists and get size
        model_file = Path(model_path)
        if model_file.exists():
            size_mb = model_file.stat().st_size / (1024 * 1024)
            print(f"📊 Model size: {size_mb:.1f} MB")
            print("✅ Download test completed successfully!")
            return True
        else:
            print("❌ Model file not found after download")
            return False
            
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False


if __name__ == "__main__":
    success = test_qwen_download()
    if success:
        print("\n🎉 Qwen2-0.5B download test passed!")
    else:
        print("\n💥 Qwen2-0.5B download test failed!")
        sys.exit(1)
