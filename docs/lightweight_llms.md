# Lightweight LLMs for CredentialForge

## Table of Contents

1. [Overview](#overview)
2. [Model Selection Criteria](#model-selection-criteria)
3. [Recommended Models](#recommended-models)
4. [Model Comparison](#model-comparison)
5. [Download and Setup](#download-and-setup)
6. [Performance Benchmarks](#performance-benchmarks)
7. [Integration Examples](#integration-examples)
8. [Optimization Tips](#optimization-tips)

## Overview

CredentialForge integrates with lightweight Large Language Models (LLMs) to generate realistic, topic-specific content for synthetic documents. This document provides comprehensive guidance on selecting, setting up, and optimizing lightweight LLMs for offline CPU-only inference.

## Model Selection Criteria

### Key Requirements

1. **Size**: Models under 4B parameters for reasonable memory usage
2. **Quantization**: Q4_K_M or Q4_0 quantization for optimal size/quality balance
3. **Performance**: CPU-optimized inference without GPU dependencies
4. **Quality**: Sufficient capability for content generation tasks
5. **Format**: GGUF format for llama.cpp compatibility
6. **License**: Open-source or permissive licensing

### Performance Factors

- **Memory Usage**: Should fit in available RAM (typically 2-8GB)
- **Inference Speed**: Fast enough for interactive use (1-10 tokens/second)
- **Context Window**: Adequate for content generation (2048+ tokens)
- **Quality**: Coherent, relevant content generation

## Recommended Models

### 1. TinyLlama-1.1B-Chat (Recommended for Development)

**Specifications:**
- **Parameters**: 1.1B
- **Size (Q4_K_M)**: ~1.5GB
- **Memory Usage**: ~2GB
- **Context Window**: 2048 tokens
- **Speed**: Very Fast (10-20 tokens/second)

**Download:**
```bash
# TinyLlama-1.1B-Chat Q4_K_M (Recommended)
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Alternative quantizations
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_0.gguf  # Smaller, slightly lower quality
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q8_0.gguf  # Larger, higher quality
```

**Best For:**
- Development and testing
- Resource-constrained environments
- Fast iteration and prototyping
- Educational purposes

### 2. Phi-3-mini-4k (Recommended for Production)

**Specifications:**
- **Parameters**: 3.8B
- **Size (Q4_K_M)**: ~3GB
- **Memory Usage**: ~4GB
- **Context Window**: 4096 tokens
- **Speed**: Fast (5-10 tokens/second)

**Download:**
```bash
# Phi-3-mini-4k Q4_K_M (Recommended)
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# Alternative quantizations
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4_K_M.gguf
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q8_0.gguf
```

**Best For:**
- Production environments
- High-quality content generation
- Complex topic generation
- Professional documentation

### 3. Qwen2-0.5B-Instruct (Ultra-Lightweight)

**Specifications:**
- **Parameters**: 0.5B
- **Size (Q4_K_M)**: ~800MB
- **Memory Usage**: ~1.2GB
- **Context Window**: 32768 tokens
- **Speed**: Very Fast (15-25 tokens/second)

**Download:**
```bash
# Qwen2-0.5B Q4_K_M
wget https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF/resolve/main/qwen2-0.5b-instruct-q4_k_m.gguf

# Alternative quantizations
wget https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF/resolve/main/qwen2-0.5b-instruct-q4_0.gguf
wget https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF/resolve/main/qwen2-0.5b-instruct-q8_0.gguf
```

**Best For:**
- Ultra-low resource environments
- Embedded systems
- Quick content generation
- Minimal memory footprint

### 4. Gemma-2B-IT (Google's Model)

**Specifications:**
- **Parameters**: 2B
- **Size (Q4_K_M)**: ~2.5GB
- **Memory Usage**: ~3GB
- **Context Window**: 8192 tokens
- **Speed**: Fast (8-12 tokens/second)

**Download:**
```bash
# Gemma-2B-IT Q4_K_M
wget https://huggingface.co/google/gemma-2b-it-gguf/resolve/main/gemma-2b-it-q4_k_m.gguf

# Alternative quantizations
wget https://huggingface.co/google/gemma-2b-it-gguf/resolve/main/gemma-2b-it-q4_0.gguf
wget https://huggingface.co/google/gemma-2b-it-gguf/resolve/main/gemma-2b-it-q8_0.gguf
```

**Best For:**
- Balanced performance and quality
- General-purpose content generation
- Multi-language support
- Google ecosystem integration

## Model Comparison

| Model | Parameters | Size | Memory | Speed | Quality | Context | Best Use Case |
|-------|------------|------|--------|-------|---------|---------|---------------|
| **TinyLlama-1.1B** | 1.1B | 1.5GB | 2GB | Very Fast | Good | 2K | Development, Testing |
| **Qwen2-0.5B** | 0.5B | 800MB | 1.2GB | Very Fast | Good | 32K | Ultra-lightweight |
| **Gemma-2B-IT** | 2B | 2.5GB | 3GB | Fast | Good | 8K | Balanced performance |
| **Phi-3-mini-4k** | 3.8B | 3GB | 4GB | Fast | Very Good | 4K | Production quality |

### Quality vs Performance Trade-offs

```
Quality:     Qwen2-0.5B < TinyLlama-1.1B < Gemma-2B-IT < Phi-3-mini-4k
Speed:       Phi-3-mini-4k < Gemma-2B-IT < TinyLlama-1.1B < Qwen2-0.5B
Memory:      Qwen2-0.5B < TinyLlama-1.1B < Gemma-2B-IT < Phi-3-mini-4k
Context:     TinyLlama-1.1B < Gemma-2B-IT < Phi-3-mini-4k < Qwen2-0.5B
```

## Download and Setup

### 1. Create Models Directory

```bash
mkdir -p ./models
cd ./models
```

### 2. Download Models

```bash
# Download TinyLlama (Recommended for development)
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Download Phi-3-mini (Recommended for production)
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# Download Qwen2-0.5B (Ultra-lightweight)
wget https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF/resolve/main/qwen2-0.5b-instruct-q4_k_m.gguf

# Download Gemma-2B-IT (Balanced)
wget https://huggingface.co/google/gemma-2b-it-gguf/resolve/main/gemma-2b-it-q4_k_m.gguf
```

### 3. Verify Downloads

```bash
# Check file sizes
ls -lh *.gguf

# Expected sizes:
# tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf    ~1.5GB
# Phi-3-mini-4k-instruct-q4.gguf          ~3GB
# qwen2-0.5b-instruct-q4_k_m.gguf         ~800MB
# gemma-2b-it-q4_k_m.gguf                 ~2.5GB
```

### 4. Test Model Loading

```bash
# Test with llama.cpp (if installed)
./llama-cli --model ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --n-predict 50 -i

# Test with CredentialForge
credentialforge generate \
  --output-dir ./test \
  --num-files 1 \
  --formats eml \
  --credential-types aws_access_key \
  --regex-db ./regex_db.json \
  --topics "system architecture" \
  --llm-model ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

## Performance Benchmarks

### Benchmark Setup

```bash
# Create benchmark script
cat > benchmark_models.py << 'EOF'
#!/usr/bin/env python3
import time
import psutil
from credentialforge.llm.llama_interface import LlamaInterface

def benchmark_model(model_path, prompt, iterations=5):
    """Benchmark a model's performance."""
    print(f"\nBenchmarking: {model_path}")
    
    # Load model
    start_time = time.time()
    llm = LlamaInterface(model_path)
    load_time = time.time() - start_time
    
    # Memory usage
    memory_before = psutil.virtual_memory().used
    memory_after = psutil.virtual_memory().used
    memory_usage = memory_after - memory_before
    
    # Generation speed
    total_tokens = 0
    total_time = 0
    
    for i in range(iterations):
        start_time = time.time()
        response = llm.generate(prompt, max_tokens=100)
        generation_time = time.time() - start_time
        
        # Estimate tokens (rough approximation)
        tokens = len(response.split())
        total_tokens += tokens
        total_time += generation_time
        
        print(f"  Iteration {i+1}: {tokens} tokens in {generation_time:.2f}s")
    
    avg_speed = total_tokens / total_time if total_time > 0 else 0
    
    print(f"  Load time: {load_time:.2f}s")
    print(f"  Memory usage: {memory_usage / 1024 / 1024:.1f}MB")
    print(f"  Average speed: {avg_speed:.1f} tokens/second")
    
    return {
        'load_time': load_time,
        'memory_usage': memory_usage,
        'avg_speed': avg_speed
    }

# Benchmark all models
models = [
    './models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
    './models/Phi-3-mini-4k-instruct-q4.gguf',
    './models/qwen2-0.5b-instruct-q4_k_m.gguf',
    './models/gemma-2b-it-q4_k_m.gguf'
]

prompt = "Generate technical documentation for a microservices architecture:"

results = {}
for model in models:
    try:
        results[model] = benchmark_model(model, prompt)
    except Exception as e:
        print(f"Error benchmarking {model}: {e}")

# Summary
print("\n" + "="*50)
print("BENCHMARK SUMMARY")
print("="*50)
for model, result in results.items():
    model_name = model.split('/')[-1].split('.')[0]
    print(f"{model_name}:")
    print(f"  Speed: {result['avg_speed']:.1f} tokens/s")
    print(f"  Memory: {result['memory_usage'] / 1024 / 1024:.1f}MB")
    print(f"  Load: {result['load_time']:.2f}s")
EOF

python benchmark_models.py
```

### Expected Results

| Model | Load Time | Memory Usage | Speed (tokens/s) | Quality Score |
|-------|-----------|--------------|------------------|---------------|
| TinyLlama-1.1B | 2-5s | 1.5-2GB | 10-20 | 7/10 |
| Qwen2-0.5B | 1-3s | 0.8-1.2GB | 15-25 | 6/10 |
| Gemma-2B-IT | 3-6s | 2.5-3GB | 8-12 | 8/10 |
| Phi-3-mini-4k | 5-10s | 3-4GB | 5-10 | 9/10 |

## Integration Examples

### 1. Basic Integration

```python
from credentialforge.llm.llama_interface import LlamaInterface

# Initialize with TinyLlama
llm = LlamaInterface('./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf')

# Generate content
prompt = "Generate technical documentation for a microservices architecture:"
content = llm.generate(prompt, max_tokens=256, temperature=0.7)
print(content)
```

### 2. Production Integration

```python
from credentialforge.llm.llama_interface import LlamaInterface

# Initialize with Phi-3-mini for production
llm = LlamaInterface(
    model_path='./models/Phi-3-mini-4k-instruct-q4.gguf',
    n_threads=8,  # Use more threads for better performance
    n_ctx=4096    # Use full context window
)

# Generate high-quality content
prompt = """
Generate detailed technical documentation for a microservices architecture.
Include sections on:
1. Service communication patterns
2. Database integration strategies
3. Security implementation
4. Deployment considerations

Focus on practical implementation details and best practices.
"""

content = llm.generate(prompt, max_tokens=512, temperature=0.5)
print(content)
```

### 3. Multi-Model Comparison

```python
from credentialforge.llm.llama_interface import LlamaInterface

def compare_models(prompt, models):
    """Compare output quality across different models."""
    results = {}
    
    for model_name, model_path in models.items():
        print(f"\nGenerating with {model_name}...")
        llm = LlamaInterface(model_path)
        content = llm.generate(prompt, max_tokens=200)
        results[model_name] = content
        print(f"Output: {content[:100]}...")
    
    return results

# Compare models
models = {
    'TinyLlama': './models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
    'Phi-3-mini': './models/Phi-3-mini-4k-instruct-q4.gguf',
    'Qwen2-0.5B': './models/qwen2-0.5b-instruct-q4_k_m.gguf',
    'Gemma-2B': './models/gemma-2b-it-q4_k_m.gguf'
}

prompt = "Explain the benefits of microservices architecture:"
results = compare_models(prompt, models)
```

### 4. Batch Processing with LLM

```python
from credentialforge.llm.llama_interface import LlamaInterface
from credentialforge.agents.orchestrator import OrchestratorAgent

# Initialize with optimized model
llm = LlamaInterface('./models/Phi-3-mini-4k-instruct-q4.gguf')
orchestrator = OrchestratorAgent(llm_interface=llm)

# Generate large batch with LLM
config = {
    'output_dir': './llm_generated_docs',
    'num_files': 50,
    'formats': ['eml', 'excel', 'pptx'],
    'credential_types': ['aws_access_key', 'jwt_token', 'db_connection'],
    'topics': [
        'microservices architecture',
        'API documentation',
        'database design',
        'security implementation',
        'deployment procedures'
    ],
    'regex_db_path': './regex_db.json',
    'batch_size': 10
}

results = orchestrator.orchestrate_generation(config)
print(f"Generated {len(results['files'])} files with LLM assistance")
```

## Optimization Tips

### 1. Memory Optimization

```python
# Optimize memory usage
llm = LlamaInterface(
    model_path='./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
    n_ctx=1024,  # Reduce context window to save memory
    n_batch=256  # Reduce batch size
)
```

### 2. Speed Optimization

```python
# Optimize for speed
llm = LlamaInterface(
    model_path='./models/qwen2-0.5b-instruct-q4_k_m.gguf',
    n_threads=8,  # Use more threads
    n_ctx=2048,   # Adequate context window
    n_batch=512   # Larger batch size
)
```

### 3. Quality Optimization

```python
# Optimize for quality
llm = LlamaInterface(
    model_path='./models/Phi-3-mini-4k-instruct-q4.gguf',
    n_ctx=4096,   # Full context window
    n_batch=256   # Smaller batch for better quality
)

# Use lower temperature for more focused output
content = llm.generate(prompt, temperature=0.3, max_tokens=512)
```

### 4. System Resource Monitoring

```python
import psutil
import time

def monitor_resources():
    """Monitor system resources during LLM usage."""
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    print(f"CPU Usage: {cpu_percent}%")
    print(f"Memory Usage: {memory.percent}% ({memory.used / 1024 / 1024:.1f}MB)")
    print(f"Available Memory: {memory.available / 1024 / 1024:.1f}MB")

# Monitor before and after model loading
monitor_resources()
llm = LlamaInterface('./models/Phi-3-mini-4k-instruct-q4.gguf')
monitor_resources()
```

### 5. Model Switching

```python
class ModelManager:
    def __init__(self):
        self.models = {
            'fast': './models/qwen2-0.5b-instruct-q4_k_m.gguf',
            'balanced': './models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
            'quality': './models/Phi-3-mini-4k-instruct-q4.gguf'
        }
        self.current_model = None
    
    def switch_model(self, model_type):
        """Switch to a different model based on requirements."""
        if model_type in self.models:
            self.current_model = LlamaInterface(self.models[model_type])
            return self.current_model
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def get_optimal_model(self, num_files, quality_requirement):
        """Select optimal model based on requirements."""
        if num_files > 100 and quality_requirement == 'low':
            return self.switch_model('fast')
        elif quality_requirement == 'high':
            return self.switch_model('quality')
        else:
            return self.switch_model('balanced')

# Usage
manager = ModelManager()
llm = manager.get_optimal_model(num_files=50, quality_requirement='medium')
```

## Troubleshooting

### Common Issues

1. **Out of Memory Error**
   - Use smaller model (Qwen2-0.5B)
   - Reduce context window (n_ctx)
   - Close other applications

2. **Slow Generation**
   - Use faster model (Qwen2-0.5B or TinyLlama)
   - Increase thread count (n_threads)
   - Reduce max_tokens

3. **Poor Quality Output**
   - Use higher quality model (Phi-3-mini-4k)
   - Adjust temperature (lower for focused output)
   - Improve prompt engineering

4. **Model Loading Errors**
   - Verify file integrity (checksum)
   - Check available disk space
   - Ensure llama-cpp-python is properly installed

### Performance Tuning

```python
# Fine-tune performance based on system
import multiprocessing

def get_optimal_config():
    """Get optimal configuration based on system resources."""
    cpu_count = multiprocessing.cpu_count()
    memory_gb = psutil.virtual_memory().total / (1024**3)
    
    if memory_gb < 4:
        return {
            'model': './models/qwen2-0.5b-instruct-q4_k_m.gguf',
            'n_threads': min(cpu_count, 4),
            'n_ctx': 1024,
            'n_batch': 256
        }
    elif memory_gb < 8:
        return {
            'model': './models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
            'n_threads': min(cpu_count, 6),
            'n_ctx': 2048,
            'n_batch': 512
        }
    else:
        return {
            'model': './models/Phi-3-mini-4k-instruct-q4.gguf',
            'n_threads': min(cpu_count, 8),
            'n_ctx': 4096,
            'n_batch': 512
        }

# Use optimal configuration
config = get_optimal_config()
llm = LlamaInterface(**config)
```

This comprehensive guide provides everything needed to select, set up, and optimize lightweight LLMs for CredentialForge, ensuring optimal performance for synthetic document generation tasks.
