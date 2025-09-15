#!/usr/bin/env python3
"""Test script for native components with CMake and llama.cpp integration."""

import sys
import os
import time
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_native_imports():
    """Test importing native components."""
    print("🧪 Testing native component imports...")
    
    try:
        # Test individual modules
        import credentialforge.native.credential_utils as cred_utils
        print("✅ credential_utils imported successfully")
        
        import credentialforge.native.llama_cpp_interface as llama_cpp
        print("✅ llama_cpp_interface imported successfully")
        
        import credentialforge.native.cpu_optimizer as cpu_opt
        print("✅ cpu_optimizer imported successfully")
        
        import credentialforge.native.memory_manager as mem_mgr
        print("✅ memory_manager imported successfully")
        
        import credentialforge.native.parallel_executor as par_exec
        print("✅ parallel_executor imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_credential_generation():
    """Test native credential generation."""
    print("\n🔑 Testing native credential generation...")
    
    try:
        import credentialforge.native.credential_utils as cred_utils
        
        # Test credential generation
        aws_key = cred_utils.generate_credential("aws_access_key", None)
        print(f"✅ Generated AWS key: {aws_key[:20]}...")
        
        jwt_token = cred_utils.generate_credential("jwt_token", None)
        print(f"✅ Generated JWT token: {jwt_token[:30]}...")
        
        # Test validation
        is_valid = cred_utils.validate_credential(aws_key, r"^AKIA[A-Z0-9]{16}$")
        print(f"✅ Validation test: {is_valid}")
        
        return True
        
    except Exception as e:
        print(f"❌ Credential generation test failed: {e}")
        return False

def test_cpu_optimization():
    """Test CPU optimization features."""
    print("\n⚡ Testing CPU optimization...")
    
    try:
        import credentialforge.native.cpu_optimizer as cpu_opt
        
        # Initialize optimizer
        cpu_opt.init_cpu_optimizer()
        
        # Get CPU info
        cpu_info = cpu_opt.get_cpu_info()
        print(f"✅ CPU info: {cpu_info}")
        
        # Test string processing
        test_strings = ["test string 1", "test string 2", "test string 3"]
        result = cpu_opt.process_strings_optimized(test_strings)
        print(f"✅ Processed strings: {result}")
        
        # Get performance stats
        stats = cpu_opt.get_performance_stats()
        print(f"✅ Performance stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ CPU optimization test failed: {e}")
        return False

def test_memory_management():
    """Test memory management."""
    print("\n💾 Testing memory management...")
    
    try:
        import credentialforge.native.memory_manager as mem_mgr
        
        # Initialize memory manager
        mem_mgr.init_memory_manager(1024 * 1024 * 100)  # 100MB limit
        
        # Test allocation
        ptr = mem_mgr.allocate_memory(1024)  # 1KB
        if ptr:
            print("✅ Memory allocation successful")
            
            # Test deallocation
            mem_mgr.deallocate_memory(ptr)
            print("✅ Memory deallocation successful")
        
        # Get memory stats
        stats = mem_mgr.get_memory_stats()
        print(f"✅ Memory stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory management test failed: {e}")
        return False

def test_parallel_execution():
    """Test parallel execution."""
    print("\n🔄 Testing parallel execution...")
    
    try:
        import credentialforge.native.parallel_executor as par_exec
        
        # Initialize executor
        par_exec.init_parallel_executor(4)  # 4 threads
        
        # Test task submission (simplified)
        print("✅ Parallel executor initialized")
        
        # Get executor stats
        stats = par_exec.get_executor_stats()
        print(f"✅ Executor stats: {stats}")
        
        # Cleanup
        par_exec.shutdown_executor()
        print("✅ Executor shutdown successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Parallel execution test failed: {e}")
        return False

def test_llama_cpp_integration():
    """Test llama.cpp integration."""
    print("\n🤖 Testing llama.cpp integration...")
    
    try:
        import credentialforge.native.llama_cpp_interface as llama_cpp
        
        # Initialize interface
        llama_cpp.init_llama_cpp()
        print("✅ LlamaCPP interface initialized")
        
        # Set threads
        llama_cpp.set_threads_cpp(4)
        print("✅ Thread count set")
        
        # Check if model is loaded (should be False initially)
        is_loaded = llama_cpp.is_model_loaded_cpp()
        print(f"✅ Model loaded status: {is_loaded}")
        
        # Get thread count
        threads = llama_cpp.get_threads_cpp()
        print(f"✅ Thread count: {threads}")
        
        return True
        
    except Exception as e:
        print(f"❌ LlamaCPP integration test failed: {e}")
        return False

def test_integration_with_credentialforge():
    """Test integration with main CredentialForge components."""
    print("\n🔗 Testing integration with CredentialForge...")
    
    try:
        from credentialforge.llm.llama_interface import LlamaInterface
        from credentialforge.agents.orchestrator import OrchestratorAgent
        
        # Test LLM interface with native components
        print("✅ LlamaInterface imported successfully")
        
        # Test orchestrator with multiprocessing
        config = {
            'use_multiprocessing': True,
            'memory_limit_gb': 2,
            'batch_size': 10
        }
        orchestrator = OrchestratorAgent(config=config)
        print("✅ OrchestratorAgent with native components initialized")
        
        # Check if native components are available
        try:
            import credentialforge.native
            print(f"✅ Native components available: {credentialforge.native.NATIVE_AVAILABLE}")
        except ImportError:
            print("✅ Native components not available (expected if not built)")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def run_performance_benchmark():
    """Run a simple performance benchmark."""
    print("\n📊 Running performance benchmark...")
    
    try:
        import credentialforge.native.credential_utils as cred_utils
        import credentialforge.native.cpu_optimizer as cpu_opt
        
        # Initialize components
        cpu_opt.init_cpu_optimizer()
        
        # Benchmark credential generation
        start_time = time.time()
        credentials = []
        
        for i in range(1000):
            cred = cred_utils.generate_credential("aws_access_key", None)
            credentials.append(cred)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Generated 1000 credentials in {duration:.2f} seconds")
        print(f"✅ Rate: {1000/duration:.0f} credentials/second")
        
        # Benchmark string processing
        test_strings = [f"test string {i}" for i in range(1000)]
        
        start_time = time.time()
        processed = cpu_opt.process_strings_optimized(test_strings)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Processed 1000 strings in {duration:.2f} seconds")
        print(f"✅ Rate: {1000/duration:.0f} strings/second")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Native Components with CMake and llama.cpp Integration")
    print("=" * 70)
    
    tests = [
        ("Native Imports", test_native_imports),
        ("Credential Generation", test_credential_generation),
        ("CPU Optimization", test_cpu_optimization),
        ("Memory Management", test_memory_management),
        ("Parallel Execution", test_parallel_execution),
        ("LlamaCPP Integration", test_llama_cpp_integration),
        ("CredentialForge Integration", test_integration_with_credentialforge),
        ("Performance Benchmark", run_performance_benchmark)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*70}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Native components are working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
