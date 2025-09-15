# 🚀 CredentialForge LLM CPU Optimization Guide

This guide explains how to build and use the optimized llama.cpp integration for maximum CPU performance in CredentialForge.

## 🎯 Overview

The optimized build provides:
- **Native C++ acceleration** with CPU-specific optimizations
- **SIMD instructions** (AVX2, FMA, SSE4.2, etc.)
- **Memory management** and pooling
- **Parallel processing** support
- **Performance monitoring** and benchmarking

## 🔧 Build Process

### 1. Prerequisites

Ensure you have:
- **Python 3.8+** with development headers
- **CMake 3.16+**
- **C++ compiler** (GCC 7+, Clang 6+, or MSVC 2019+)
- **Git** for fetching llama.cpp

### 2. Quick Build

```bash
# Use the optimized build script
python build_optimized.py
```

### 3. Manual Build

```bash
# Create build directory
mkdir build
cd build

# Configure with CPU optimizations
cmake .. -DCMAKE_BUILD_TYPE=Release \
         -DLLAMA_CUDA=OFF \
         -DLLAMA_AVX2=ON \
         -DLLAMA_FMA=ON \
         -DLLAMA_NATIVE=ON

# Build
cmake --build . --config Release --parallel
```

## 🏗️ Architecture

### Native Components

The optimized build includes these native C++ modules:

1. **`credential_utils.cpp`** - Fast credential generation
2. **`llama_cpp_interface.cpp`** - Direct llama.cpp integration
3. **`cpu_optimizer.cpp`** - CPU-specific optimizations
4. **`memory_manager.cpp`** - Memory pooling and management
5. **`parallel_executor.cpp`** - Multi-threaded execution

### CPU Optimizations

The build enables these CPU-specific optimizations:

- **AVX2** - Advanced Vector Extensions 2
- **FMA** - Fused Multiply-Add instructions
- **F16C** - Half-precision floating-point conversion
- **SSE3/SSSE3/SSE4.1/SSE4.2** - Streaming SIMD Extensions
- **POPCNT** - Population count instruction
- **Native CPU detection** - Automatic optimization selection

## 🚀 Usage

### Basic Usage

```python
from credentialforge.llm.llama_optimized import OptimizedLlamaInterface

# Create optimized interface
llm = OptimizedLlamaInterface(
    model_path="models/qwen2-0.5b.gguf",
    n_ctx=2048,
    n_threads=8,  # Auto-detected if None
    verbose=True
)

# Generate text
result = llm.generate("Explain AI", max_tokens=100)
print(result)
```

### Performance Monitoring

```python
# Get performance statistics
stats = llm.get_performance_stats()
print(f"Tokens/sec: {stats['avg_tokens_per_second']:.1f}")
print(f"Memory usage: {stats['memory_usage']:.1f} MB")

# Reset stats
llm.reset_performance_stats()
```

### Benchmarking

```python
# Run performance benchmark
test_prompts = [
    "Explain machine learning",
    "Write a short story",
    "Describe quantum computing"
]

results = llm.benchmark(test_prompts, max_tokens=50)
print(f"Average speed: {results['avg_tokens_per_second']:.1f} tokens/sec")
```

## 📊 Performance Testing

Run the comprehensive performance test:

```bash
python test_llama_performance.py
```

This will test:
- ✅ Basic functionality
- 🚀 Performance benchmarking
- 💾 Memory usage
- 🧵 Threading performance

## ⚡ Performance Tips

### 1. Model Selection
- Use **quantized models** (Q4_0, Q4_K) for better performance
- Smaller models (0.5B-2B parameters) for faster inference
- GGUF format for optimal compatibility

### 2. Thread Configuration
- Set threads to **75% of CPU cores** for optimal performance
- Monitor memory usage (1.5GB per thread recommended)
- Use `n_threads=None` for auto-detection

### 3. Context Management
- Use appropriate context size (`n_ctx`) for your use case
- Larger context = more memory usage
- Smaller context = faster inference

### 4. Memory Optimization
- Enable `use_mmap=True` for large models
- Use `use_mlock=True` to prevent swapping
- Monitor memory usage with performance stats

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Clean build directory
   rm -rf build
   python build_optimized.py
   ```

2. **Import Errors**
   ```bash
   # Check if native module was built
   ls credentialforge/native/
   ```

3. **Performance Issues**
   ```bash
   # Check CPU support
   python -c "import platform; print(platform.processor())"
   
   # Test with different thread counts
   python test_llama_performance.py
   ```

### Debug Mode

Enable verbose logging:

```python
llm = OptimizedLlamaInterface(
    model_path="models/model.gguf",
    verbose=True  # Enable debug output
)
```

## 📈 Expected Performance

### Benchmarks (on modern CPU)

| Model Size | Context | Threads | Tokens/sec | Memory |
|------------|---------|---------|------------|--------|
| 0.5B       | 2048    | 8       | 150-200    | 2-3GB  |
| 1.1B       | 2048    | 8       | 100-150    | 3-4GB  |
| 2B         | 2048    | 8       | 80-120     | 4-6GB  |

*Performance varies based on CPU, model quantization, and prompt complexity.*

## 🛠️ Advanced Configuration

### Custom CPU Flags

```cmake
# Enable specific CPU optimizations
cmake .. -DLLAMA_AVX2=ON \
         -DLLAMA_FMA=ON \
         -DLLAMA_F16C=ON \
         -DLLAMA_SSE4_2=ON
```

### Memory Pool Configuration

```python
# Configure memory management
llm = OptimizedLlamaInterface(
    model_path="models/model.gguf",
    n_ctx=4096,  # Larger context
    use_mmap=True,  # Memory mapping
    use_mlock=True  # Lock memory
)
```

### Threading Optimization

```python
import psutil

# Auto-detect optimal threads
cpu_count = psutil.cpu_count(logical=True)
optimal_threads = max(1, int(cpu_count * 0.75))

llm = OptimizedLlamaInterface(
    model_path="models/model.gguf",
    n_threads=optimal_threads
)
```

## 🔄 Integration with CredentialForge

The optimized LLM interface integrates seamlessly with CredentialForge:

```python
# In your CredentialForge application
from credentialforge.llm.llama_optimized import OptimizedLlamaInterface

# Replace the standard interface
llm = OptimizedLlamaInterface("models/qwen2-0.5b.gguf")

# Use in topic generation
from credentialforge.generators.topic_generator import TopicGenerator

topic_gen = TopicGenerator(llm_interface=llm)
content = topic_gen.generate_topic_content("security audit", "eml")
```

## 📚 Additional Resources

- [llama.cpp GitHub](https://github.com/ggerganov/llama.cpp)
- [GGUF Model Format](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)
- [CPU Optimization Guide](https://github.com/ggerganov/llama.cpp#optimizing)

## 🎉 Conclusion

The optimized llama.cpp integration provides significant performance improvements for CPU-based LLM inference in CredentialForge. With proper configuration and monitoring, you can achieve excellent performance for synthetic document generation tasks.

For questions or issues, refer to the troubleshooting section or check the performance test results.
