"""
Optimized llama.cpp interface with CPU performance enhancements.
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
import psutil

# Try to import native components
try:
    from ..native import credentialforge_native
    NATIVE_AVAILABLE = True
except ImportError:
    NATIVE_AVAILABLE = False
    credentialforge_native = None

# Import llama-cpp-python as fallback
try:
    from llama_cpp import Llama, LlamaGrammar
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    Llama = None
    LlamaGrammar = None

class OptimizedLlamaInterface:
    """
    Optimized llama.cpp interface with CPU performance enhancements.
    
    Features:
    - Native C++ acceleration when available
    - CPU optimization flags (AVX2, FMA, etc.)
    - Memory management and pooling
    - Parallel processing support
    - Performance monitoring
    """
    
    def __init__(self, model_path: str, n_ctx: int = 2048, n_threads: Optional[int] = None, 
                 n_gpu_layers: int = 0, verbose: bool = False):
        """
        Initialize optimized llama interface.
        
        Args:
            model_path: Path to the GGUF model file
            n_ctx: Context window size
            n_threads: Number of threads (auto-detected if None)
            n_gpu_layers: Number of GPU layers (0 for CPU-only)
            verbose: Enable verbose logging
        """
        self.model_path = Path(model_path)
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.verbose = verbose
        
        # Auto-detect optimal thread count
        if n_threads is None:
            self.n_threads = self._get_optimal_threads()
        else:
            self.n_threads = n_threads
            
        # Performance monitoring
        self.performance_stats = {
            'total_tokens': 0,
            'total_time': 0.0,
            'avg_tokens_per_second': 0.0,
            'memory_usage': 0.0
        }
        
        # Initialize components
        self.llm = None
        self.native_interface = None
        self._lock = threading.Lock()
        
        # Load model
        self._load_model()
    
    def _get_optimal_threads(self) -> int:
        """Get optimal number of threads based on CPU cores and memory."""
        cpu_count = psutil.cpu_count(logical=True)
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Conservative approach: use 75% of logical cores
        # but limit based on memory (1GB per thread minimum)
        max_threads_by_cpu = max(1, int(cpu_count * 0.75))
        max_threads_by_memory = max(1, int(memory_gb / 1.5))
        
        optimal_threads = min(max_threads_by_cpu, max_threads_by_memory, 16)
        
        if self.verbose:
            print(f"CPU cores: {cpu_count}, Memory: {memory_gb:.1f}GB")
            print(f"Optimal threads: {optimal_threads}")
        
        return optimal_threads
    
    def _load_model(self):
        """Load the model with optimizations."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        if self.verbose:
            print(f"Loading model: {self.model_path}")
            print(f"Context size: {self.n_ctx}")
            print(f"Threads: {self.n_threads}")
            print(f"GPU layers: {self.n_gpu_layers}")
        
        # Try native interface first
        if NATIVE_AVAILABLE and credentialforge_native:
            try:
                self.native_interface = credentialforge_native.init_llama_cpp(
                    str(self.model_path),
                    self.n_ctx,
                    self.n_threads,
                    self.n_gpu_layers
                )
                if self.native_interface:
                    print("✅ Using native C++ acceleration")
                    return
            except Exception as e:
                if self.verbose:
                    print(f"Native interface failed: {e}")
        
        # Fallback to llama-cpp-python
        if LLAMA_CPP_AVAILABLE:
            try:
                self.llm = Llama(
                    model_path=str(self.model_path),
                    n_ctx=self.n_ctx,
                    n_threads=self.n_threads,
                    n_gpu_layers=self.n_gpu_layers,
                    verbose=self.verbose,
                    # CPU optimization flags
                    use_mmap=True,
                    use_mlock=True,
                    # Performance optimizations
                    logits_all=False,
                    embedding=False,
                    offload_kqv=True
                )
                print("✅ Using llama-cpp-python")
                return
            except Exception as e:
                raise RuntimeError(f"Failed to load model: {e}")
        else:
            raise RuntimeError("Neither native interface nor llama-cpp-python is available")
    
    def generate(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7,
                 top_p: float = 0.9, top_k: int = 40, repeat_penalty: float = 1.1,
                 stop: Optional[List[str]] = None, stream: bool = False) -> str:
        """
        Generate text with optimizations.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling
            top_k: Top-k sampling
            repeat_penalty: Repeat penalty
            stop: Stop sequences
            stream: Enable streaming
            
        Returns:
            Generated text
        """
        start_time = time.time()
        
        with self._lock:
            try:
                # Try native interface first
                if self.native_interface and NATIVE_AVAILABLE:
                    result = credentialforge_native.generate_text_cpp(
                        self.native_interface,
                        prompt,
                        max_tokens,
                        temperature,
                        top_p,
                        top_k,
                        repeat_penalty,
                        stop or []
                    )
                    
                    if result and result != "Error: Model not loaded":
                        self._update_performance_stats(max_tokens, time.time() - start_time)
                        return result
                
                # Fallback to llama-cpp-python
                if self.llm:
                    if stream:
                        return self._generate_stream(prompt, max_tokens, temperature, 
                                                   top_p, top_k, repeat_penalty, stop)
                    else:
                        result = self.llm(
                            prompt,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            top_p=top_p,
                            top_k=top_k,
                            repeat_penalty=repeat_penalty,
                            stop=stop,
                            echo=False
                        )
                        
                        generated_text = result['choices'][0]['text']
                        self._update_performance_stats(max_tokens, time.time() - start_time)
                        return generated_text
                
                raise RuntimeError("No working interface available")
                
            except Exception as e:
                if self.verbose:
                    print(f"Generation error: {e}")
                raise
    
    def _generate_stream(self, prompt: str, max_tokens: int, temperature: float,
                        top_p: float, top_k: int, repeat_penalty: float, 
                        stop: Optional[List[str]]) -> str:
        """Generate text with streaming."""
        full_text = ""
        
        for chunk in self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repeat_penalty=repeat_penalty,
            stop=stop,
            echo=False,
            stream=True
        ):
            if 'choices' in chunk and len(chunk['choices']) > 0:
                delta = chunk['choices'][0].get('text', '')
                full_text += delta
                yield delta
        
        return full_text
    
    def _update_performance_stats(self, tokens: int, time_taken: float):
        """Update performance statistics."""
        self.performance_stats['total_tokens'] += tokens
        self.performance_stats['total_time'] += time_taken
        
        if self.performance_stats['total_time'] > 0:
            self.performance_stats['avg_tokens_per_second'] = (
                self.performance_stats['total_tokens'] / self.performance_stats['total_time']
            )
        
        # Update memory usage
        process = psutil.Process()
        self.performance_stats['memory_usage'] = process.memory_info().rss / (1024 * 1024)  # MB
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        return self.performance_stats.copy()
    
    def reset_performance_stats(self):
        """Reset performance statistics."""
        self.performance_stats = {
            'total_tokens': 0,
            'total_time': 0.0,
            'avg_tokens_per_second': 0.0,
            'memory_usage': 0.0
        }
    
    def benchmark(self, prompts: List[str], max_tokens: int = 100) -> Dict[str, Any]:
        """
        Benchmark performance with multiple prompts.
        
        Args:
            prompts: List of test prompts
            max_tokens: Tokens to generate per prompt
            
        Returns:
            Benchmark results
        """
        print(f"🧪 Benchmarking with {len(prompts)} prompts...")
        
        start_time = time.time()
        total_tokens = 0
        results = []
        
        for i, prompt in enumerate(prompts):
            prompt_start = time.time()
            try:
                result = self.generate(prompt, max_tokens=max_tokens)
                prompt_time = time.time() - prompt_start
                
                # Estimate tokens (rough approximation)
                estimated_tokens = len(result.split()) * 1.3
                total_tokens += estimated_tokens
                
                results.append({
                    'prompt_id': i,
                    'time': prompt_time,
                    'tokens': estimated_tokens,
                    'tokens_per_second': estimated_tokens / prompt_time if prompt_time > 0 else 0
                })
                
                if self.verbose:
                    print(f"Prompt {i+1}/{len(prompts)}: {prompt_time:.2f}s, "
                          f"{estimated_tokens:.1f} tokens, "
                          f"{estimated_tokens/prompt_time:.1f} tok/s")
                
            except Exception as e:
                print(f"❌ Prompt {i+1} failed: {e}")
                results.append({
                    'prompt_id': i,
                    'error': str(e)
                })
        
        total_time = time.time() - start_time
        avg_tokens_per_second = total_tokens / total_time if total_time > 0 else 0
        
        benchmark_results = {
            'total_prompts': len(prompts),
            'successful_prompts': len([r for r in results if 'error' not in r]),
            'total_time': total_time,
            'total_tokens': total_tokens,
            'avg_tokens_per_second': avg_tokens_per_second,
            'results': results
        }
        
        print(f"✅ Benchmark complete:")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Total tokens: {total_tokens:.1f}")
        print(f"   Average speed: {avg_tokens_per_second:.1f} tokens/second")
        
        return benchmark_results
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'llm') and self.llm:
            del self.llm
        if hasattr(self, 'native_interface') and self.native_interface:
            if NATIVE_AVAILABLE and credentialforge_native:
                try:
                    credentialforge_native.cleanup_llama_cpp(self.native_interface)
                except:
                    pass

# Convenience function for easy usage
def create_optimized_llama(model_path: str, **kwargs) -> OptimizedLlamaInterface:
    """
    Create an optimized llama interface.
    
    Args:
        model_path: Path to the GGUF model file
        **kwargs: Additional arguments for OptimizedLlamaInterface
        
    Returns:
        OptimizedLlamaInterface instance
    """
    return OptimizedLlamaInterface(model_path, **kwargs)
