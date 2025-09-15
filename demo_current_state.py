#!/usr/bin/env python3
"""Demonstration of current CredentialForge state with multiprocessing and CMake integration."""

import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demo_multiprocessing():
    """Demonstrate multiprocessing capabilities."""
    print("🔄 Multiprocessing Demo")
    print("=" * 40)
    
    from credentialforge.agents.orchestrator import OrchestratorAgent
    
    # Test with multiprocessing enabled
    config = {
        'use_multiprocessing': True,
        'memory_limit_gb': 4,
        'batch_size': 20,
        'num_files': 5  # Small test
    }
    
    orchestrator = OrchestratorAgent(config=config)
    print(f"✅ Orchestrator initialized with {orchestrator.max_workers} workers")
    print(f"✅ Memory limit: {orchestrator.memory_limit_gb}GB")
    print(f"✅ Multiprocessing enabled: {orchestrator.use_multiprocessing}")
    
    return True

def demo_llm_interface():
    """Demonstrate LLM interface with native component support."""
    print("\n🤖 LLM Interface Demo")
    print("=" * 40)
    
    from credentialforge.llm.llama_interface import LlamaInterface
    
    # Test LLM interface
    try:
        llm = LlamaInterface("qwen2-0.5b.gguf", n_threads=4)
        print(f"✅ LLM interface initialized")
        print(f"✅ Model path: {llm.model_path}")
        print(f"✅ Threads: {llm.n_threads}")
        print(f"✅ Native interface available: {llm.native_interface is not None}")
        
        return True
    except Exception as e:
        print(f"⚠️ LLM interface test: {e}")
        return False

def demo_credential_generation():
    """Demonstrate credential generation."""
    print("\n🔑 Credential Generation Demo")
    print("=" * 40)
    
    from credentialforge.generators.credential_generator import CredentialGenerator
    from credentialforge.db.regex_db import RegexDatabase
    
    try:
        regex_db = RegexDatabase("./data/regex_db.json")
        generator = CredentialGenerator(regex_db)
        
        # Test credential generation using regex database
        aws_key = generator.generate_credential("aws_access_key")
        print(f"✅ Generated AWS key: {aws_key}")
        
        jwt_token = generator.generate_credential("jwt_token")
        print(f"✅ Generated JWT token: {jwt_token[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Credential generation failed: {e}")
        return False

def demo_system_info():
    """Show system information."""
    print("\n💻 System Information")
    print("=" * 40)
    
    import psutil
    import multiprocessing as mp
    
    print(f"✅ CPU cores: {mp.cpu_count()}")
    print(f"✅ Total RAM: {psutil.virtual_memory().total / (1024**3):.1f}GB")
    print(f"✅ Available RAM: {psutil.virtual_memory().available / (1024**3):.1f}GB")
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Platform: {sys.platform}")
    
    return True

def demo_native_components_status():
    """Show native components status."""
    print("\n🏗️ Native Components Status")
    print("=" * 40)
    
    try:
        from credentialforge.native import NATIVE_AVAILABLE
        print(f"✅ Native components available: {NATIVE_AVAILABLE}")
        
        if not NATIVE_AVAILABLE:
            print("ℹ️ Native components not built yet - using Python fallbacks")
            print("ℹ️ To build native components, run: python build_native.py")
        
        return True
    except ImportError:
        print("ℹ️ Native components module not found - expected if not built")
        return True

def demo_cmake_integration():
    """Show CMake integration status."""
    print("\n🔨 CMake Integration Status")
    print("=" * 40)
    
    cmake_files = [
        "CMakeLists.txt",
        "src/credential_utils.cpp",
        "src/llama_cpp_interface.cpp",
        "src/cpu_optimizer.cpp",
        "src/memory_manager.cpp",
        "src/parallel_executor.cpp",
        "build_native.py",
        "test_native_build.py"
    ]
    
    all_exist = True
    for file_path in cmake_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_exist = False
    
    if all_exist:
        print("✅ All CMake integration files present")
        print("ℹ️ Ready for native build with: python build_native.py")
    
    return all_exist

def main():
    """Run all demonstrations."""
    print("🚀 CredentialForge Current State Demo")
    print("=" * 50)
    
    demos = [
        ("System Information", demo_system_info),
        ("Multiprocessing", demo_multiprocessing),
        ("LLM Interface", demo_llm_interface),
        ("Credential Generation", demo_credential_generation),
        ("Native Components Status", demo_native_components_status),
        ("CMake Integration", demo_cmake_integration)
    ]
    
    passed = 0
    total = len(demos)
    
    for demo_name, demo_func in demos:
        try:
            if demo_func():
                passed += 1
                print(f"✅ {demo_name} - PASSED")
            else:
                print(f"❌ {demo_name} - FAILED")
        except Exception as e:
            print(f"❌ {demo_name} - FAILED: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Demo Results: {passed}/{total} demos passed")
    
    if passed == total:
        print("🎉 All core functionality is working!")
        print("💡 To enable native performance optimizations:")
        print("   1. Install build dependencies (CMake, C++ compiler)")
        print("   2. Run: python build_native.py")
        print("   3. Run: python test_native_build.py")
    else:
        print("⚠️ Some demos failed. Check the output above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
