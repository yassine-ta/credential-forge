#!/usr/bin/env python3
"""
Performance testing script for optimized llama.cpp integration.
"""

import time
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from credentialforge.llm.llama_optimized import OptimizedLlamaInterface, create_optimized_llama

def test_basic_functionality():
    """Test basic functionality of the optimized interface."""
    print("🧪 Testing Basic Functionality")
    print("=" * 40)
    
    # Check if we have a model available
    models_dir = Path("models")
    if not models_dir.exists():
        print("❌ No models directory found")
        return False
    
    # Find available models
    model_files = list(models_dir.glob("*.gguf"))
    if not model_files:
        print("❌ No GGUF models found in models directory")
        return False
    
    model_path = model_files[0]
    print(f"📁 Using model: {model_path}")
    
    try:
        # Create optimized interface
        llm = create_optimized_llama(
            str(model_path),
            n_ctx=2048,
            n_threads=4,
            verbose=True
        )
        
        # Test basic generation
        print("\n🔤 Testing basic generation...")
        prompt = "The quick brown fox"
        result = llm.generate(prompt, max_tokens=20, temperature=0.7)
        print(f"Prompt: {prompt}")
        print(f"Result: {result}")
        
        # Test performance stats
        stats = llm.get_performance_stats()
        print(f"\n📊 Performance Stats:")
        print(f"   Total tokens: {stats['total_tokens']}")
        print(f"   Total time: {stats['total_time']:.2f}s")
        print(f"   Avg tokens/sec: {stats['avg_tokens_per_second']:.1f}")
        print(f"   Memory usage: {stats['memory_usage']:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_performance_benchmark():
    """Test performance with multiple prompts."""
    print("\n🚀 Performance Benchmark")
    print("=" * 40)
    
    models_dir = Path("models")
    model_files = list(models_dir.glob("*.gguf"))
    if not model_files:
        print("❌ No GGUF models found")
        return False
    
    model_path = model_files[0]
    
    try:
        # Create optimized interface
        llm = create_optimized_llama(
            str(model_path),
            n_ctx=2048,
            n_threads=8,  # Use more threads for benchmark
            verbose=False
        )
        
        # Test prompts
        test_prompts = [
            "Explain the concept of artificial intelligence",
            "Write a short story about a robot",
            "Describe the benefits of renewable energy",
            "What are the key principles of cybersecurity?",
            "Explain quantum computing in simple terms"
        ]
        
        # Run benchmark
        benchmark_results = llm.benchmark(test_prompts, max_tokens=50)
        
        # Display results
        print(f"\n📈 Benchmark Results:")
        print(f"   Successful prompts: {benchmark_results['successful_prompts']}/{benchmark_results['total_prompts']}")
        print(f"   Total time: {benchmark_results['total_time']:.2f}s")
        print(f"   Total tokens: {benchmark_results['total_tokens']:.1f}")
        print(f"   Average speed: {benchmark_results['avg_tokens_per_second']:.1f} tokens/second")
        
        # Show individual results
        print(f"\n📋 Individual Results:")
        for result in benchmark_results['results']:
            if 'error' not in result:
                print(f"   Prompt {result['prompt_id']+1}: {result['time']:.2f}s, "
                      f"{result['tokens']:.1f} tokens, "
                      f"{result['tokens_per_second']:.1f} tok/s")
            else:
                print(f"   Prompt {result['prompt_id']+1}: ERROR - {result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return False

def test_memory_usage():
    """Test memory usage and management."""
    print("\n💾 Memory Usage Test")
    print("=" * 40)
    
    import psutil
    
    models_dir = Path("models")
    model_files = list(models_dir.glob("*.gguf"))
    if not model_files:
        print("❌ No GGUF models found")
        return False
    
    model_path = model_files[0]
    
    try:
        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
        print(f"Initial memory usage: {initial_memory:.1f} MB")
        
        # Create interface
        llm = create_optimized_llama(
            str(model_path),
            n_ctx=1024,  # Smaller context for memory test
            n_threads=4,
            verbose=False
        )
        
        # Get memory after loading
        after_load_memory = process.memory_info().rss / (1024 * 1024)  # MB
        print(f"Memory after loading: {after_load_memory:.1f} MB")
        print(f"Memory increase: {after_load_memory - initial_memory:.1f} MB")
        
        # Generate some text
        for i in range(5):
            result = llm.generate(f"Test prompt {i+1}", max_tokens=30)
            current_memory = process.memory_info().rss / (1024 * 1024)  # MB
            print(f"After generation {i+1}: {current_memory:.1f} MB")
        
        # Get final stats
        stats = llm.get_performance_stats()
        print(f"\n📊 Final Performance Stats:")
        print(f"   Total tokens: {stats['total_tokens']}")
        print(f"   Total time: {stats['total_time']:.2f}s")
        print(f"   Avg tokens/sec: {stats['avg_tokens_per_second']:.1f}")
        print(f"   Memory usage: {stats['memory_usage']:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False

def test_threading_performance():
    """Test performance with different thread counts."""
    print("\n🧵 Threading Performance Test")
    print("=" * 40)
    
    models_dir = Path("models")
    model_files = list(models_dir.glob("*.gguf"))
    if not model_files:
        print("❌ No GGUF models found")
        return False
    
    model_path = model_files[0]
    
    # Test different thread counts
    thread_counts = [1, 2, 4, 8]
    test_prompt = "Explain the benefits of using multiple threads in programming"
    
    results = []
    
    for threads in thread_counts:
        print(f"\n🔧 Testing with {threads} threads...")
        
        try:
            llm = create_optimized_llama(
                str(model_path),
                n_ctx=1024,
                n_threads=threads,
                verbose=False
            )
            
            # Reset stats
            llm.reset_performance_stats()
            
            # Generate text
            start_time = time.time()
            result = llm.generate(test_prompt, max_tokens=50)
            generation_time = time.time() - start_time
            
            # Get stats
            stats = llm.get_performance_stats()
            
            results.append({
                'threads': threads,
                'time': generation_time,
                'tokens_per_second': stats['avg_tokens_per_second'],
                'memory': stats['memory_usage']
            })
            
            print(f"   Time: {generation_time:.2f}s")
            print(f"   Tokens/sec: {stats['avg_tokens_per_second']:.1f}")
            print(f"   Memory: {stats['memory_usage']:.1f} MB")
            
        except Exception as e:
            print(f"   ❌ Failed with {threads} threads: {e}")
            results.append({
                'threads': threads,
                'error': str(e)
            })
    
    # Display comparison
    print(f"\n📊 Threading Performance Comparison:")
    print(f"{'Threads':<8} {'Time (s)':<10} {'Tokens/s':<12} {'Memory (MB)':<12}")
    print("-" * 45)
    
    for result in results:
        if 'error' not in result:
            print(f"{result['threads']:<8} {result['time']:<10.2f} "
                  f"{result['tokens_per_second']:<12.1f} {result['memory']:<12.1f}")
        else:
            print(f"{result['threads']:<8} ERROR: {result['error']}")
    
    return True

def main():
    """Run all performance tests."""
    print("🚀 CredentialForge LLM Performance Testing")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Performance Benchmark", test_performance_benchmark),
        ("Memory Usage", test_memory_usage),
        ("Threading Performance", test_threading_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n📋 Test Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! LLM optimization is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()

