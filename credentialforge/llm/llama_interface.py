"""LLM interface for offline inference using llama.cpp."""

import os
import time
import psutil
import requests
import threading
import gc
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from .exceptions import LLMError

# Try to import native components
try:
    from ..native import llama_cpp_interface
    NATIVE_AVAILABLE = True
except ImportError:
    NATIVE_AVAILABLE = False
    llama_cpp_interface = None


class LlamaInterface:
    """Interface for offline LLM inference using llama.cpp."""
    
    def __init__(self, model_path: str, n_threads: Optional[int] = None, 
                 n_ctx: int = 4096, n_batch: int = 512, 
                 temperature: float = 0.88, max_tokens: int = 512,
                 use_mmap: bool = True, use_mlock: bool = True,
                 enable_multiprocessing: bool = True):
        """Initialize Llama interface.
        
        Args:
            model_path: Path to GGUF model file (can be relative to project root)
            n_threads: Number of threads for inference
            n_ctx: Context window size
            n_batch: Batch size for processing
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            use_mmap: Use memory mapping for large models
            use_mlock: Lock memory to prevent swapping
            enable_multiprocessing: Enable multiprocessing optimizations
            
        Raises:
            LLMError: If model cannot be loaded
        """
        # Ensure model path is relative to project root
        if not Path(model_path).is_absolute():
            # Get project root (where this file is located, go up to credentialforge, then up to project root)
            project_root = Path(__file__).parent.parent.parent
            # If model_path already contains "models", don't add it again
            if "models" in model_path:
                model_path = project_root / model_path
            else:
                model_path = project_root / "models" / model_path
        
        self.model_path = str(Path(model_path).resolve())
        self.n_threads = n_threads or min(psutil.cpu_count(), 8)
        self.n_ctx = n_ctx
        self.n_batch = n_batch
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.use_mmap = use_mmap
        self.use_mlock = use_mlock
        self.enable_multiprocessing = enable_multiprocessing
        
        # Performance monitoring
        self.performance_stats = {
            'total_generations': 0,
            'total_tokens': 0,
            'total_time': 0.0,
            'avg_tokens_per_second': 0.0,
            'memory_usage_mb': 0.0
        }
        
        # Thread pool for parallel processing
        self.thread_pool = None
        if self.enable_multiprocessing:
            self.thread_pool = ThreadPoolExecutor(max_workers=min(4, self.n_threads))
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Native interface for CPU optimization
        self.native_interface = None
        if NATIVE_AVAILABLE and llama_cpp_interface:
            try:
                self.native_interface = llama_cpp_interface.init_llama_cpp()
                if self.native_interface:
                    llama_cpp_interface.set_threads_cpp(self.n_threads)
            except Exception as e:
                print(f"Warning: Failed to initialize native interface: {e}")
                self.native_interface = None
        
        self.llm = None
        self.model_info = {}
        
        self._load_model()
    
    def _load_model(self) -> None:
        """Load GGUF model using llama-cpp-python.
        
        Raises:
            LLMError: If model cannot be loaded
        """
        try:
            # Check if model file exists
            if not Path(self.model_path).exists():
                raise LLMError(f"Model file not found: {self.model_path}")
            
            # Import llama-cpp-python
            try:
                from llama_cpp import Llama
            except ImportError:
                raise LLMError(
                    "llama-cpp-python not installed. "
                    "Install with: pip install llama-cpp-python"
                )
            
            # Load model with optimized CPU configuration
            self.llm = Llama(
                model_path=self.model_path,
                n_gpu_layers=0,  # CPU-only
                n_threads=self.n_threads,
                n_ctx=self.n_ctx,
                n_batch=self.n_batch,
                verbose=False,
                use_mmap=self.use_mmap,
                use_mlock=self.use_mlock
            )
            
            # Get model information
            self.model_info = self._get_model_info()
            
        except Exception as e:
            error_msg = str(e)
            if "Failed to create llama_context" in error_msg:
                raise LLMError(f"Failed to create llama context - this may be due to insufficient memory or corrupted model file: {e}")
            elif "model file not found" in error_msg.lower():
                raise LLMError(f"Model file not found: {self.model_path}")
            else:
                raise LLMError(f"Failed to load model: {e}")
    
    def _get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        try:
            # Get model metadata
            model_file = Path(self.model_path)
            file_size = model_file.stat().st_size
            
            # Estimate parameters based on file size (rough approximation)
            estimated_params = self._estimate_parameters(file_size)
            
            return {
                'name': model_file.stem,
                'path': str(model_file),
                'size_bytes': file_size,
                'size_mb': file_size / (1024 * 1024),
                'estimated_parameters': estimated_params,
                'context_size': self.n_ctx,
                'threads': self.n_threads,
                'temperature': self.temperature
            }
        except Exception:
            return {'name': 'unknown', 'path': self.model_path}
    
    def _estimate_parameters(self, file_size: int) -> str:
        """Estimate model parameters based on file size.
        
        Args:
            file_size: Model file size in bytes
            
        Returns:
            Estimated parameter count as string
        """
        # Rough estimation for Q4_K_M quantized models
        # This is a very rough approximation
        size_mb = file_size / (1024 * 1024)
        
        if size_mb < 1000:
            return f"~{int(size_mb / 0.5)}M"
        elif size_mb < 5000:
            return f"~{int(size_mb / 0.8)}M"
        else:
            return f"~{int(size_mb / 1.2)}M"
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None, 
                 temperature: Optional[float] = None, 
                 stop: Optional[List[str]] = None) -> str:
        """Generate text using the loaded model.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop: Stop sequences
            
        Returns:
            Generated text
            
        Raises:
            LLMError: If generation fails
        """
        if not self.llm:
            raise LLMError("Model not loaded")
        
        start_time = time.time()
        
        try:
            with self._lock:
                # Use provided parameters or defaults
                max_tokens = max_tokens or self.max_tokens
                temperature = temperature or self.temperature
                stop = stop or ["</s>", "\n\n"]
                
                # Try native interface first if available
                if self.native_interface and NATIVE_AVAILABLE and llama_cpp_interface:
                    try:
                        result = llama_cpp_interface.generate_text_cpp(prompt, max_tokens, temperature)
                        if result and result != "Error: Model not loaded":
                            self._update_performance_stats(max_tokens, time.time() - start_time)
                            return result
                    except Exception as native_error:
                        print(f"Native generation failed, falling back to Python: {native_error}")
                
                # Fallback to Python implementation
                response = self.llm(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=stop,
                    echo=False
                )
                
                # Extract generated text
                if 'choices' in response and len(response['choices']) > 0:
                    generated_text = response['choices'][0]['text']
                    
                    # Check for language compliance if language is specified in prompt
                    if self._has_language_requirement(prompt):
                        language = self._extract_language_from_prompt(prompt)
                        if language and language != 'en':
                            generated_text = self._ensure_language_compliance(generated_text, language)
                    
                    # Update performance stats
                    self._update_performance_stats(max_tokens, time.time() - start_time)
                    return generated_text
                else:
                    raise LLMError("No text generated")
                    
        except Exception as e:
            # Handle specific llama-cpp-python errors
            error_msg = str(e)
            if "llama_decode returned -1" in error_msg:
                raise LLMError("Model decode error - try reducing context size or using a different model")
            elif "CUDA" in error_msg:
                raise LLMError("CUDA error - ensure CPU-only mode is enabled")
            else:
                raise LLMError(f"Text generation failed: {e}")
    
    def generate_batch(self, prompts: List[str], max_tokens: Optional[int] = None,
                      temperature: Optional[float] = None, 
                      stop: Optional[List[str]] = None) -> List[str]:
        """Generate text for multiple prompts in parallel.
        
        Args:
            prompts: List of input prompts
            max_tokens: Maximum tokens to generate per prompt
            temperature: Sampling temperature
            stop: Stop sequences
            
        Returns:
            List of generated texts
            
        Raises:
            LLMError: If generation fails
        """
        if not self.llm:
            raise LLMError("Model not loaded")
        
        if not self.enable_multiprocessing or len(prompts) <= 1:
            # Fallback to sequential processing
            return [self.generate(prompt, max_tokens, temperature, stop) for prompt in prompts]
        
        # Use thread pool for parallel processing
        if not self.thread_pool:
            self.thread_pool = ThreadPoolExecutor(max_workers=min(4, self.n_threads))
        
        try:
            # Submit all tasks
            futures = [
                self.thread_pool.submit(self.generate, prompt, max_tokens, temperature, stop)
                for prompt in prompts
            ]
            
            # Collect results as they complete
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=300)  # 5 minute timeout per generation
                    results.append(result)
                except Exception as e:
                    print(f"Batch generation failed for one prompt: {e}")
                    results.append("")  # Add empty result for failed generation
            
            return results
            
        except Exception as e:
            raise LLMError(f"Batch generation failed: {e}")
    
    def _update_performance_stats(self, tokens_generated: int, generation_time: float) -> None:
        """Update performance statistics."""
        self.performance_stats['total_generations'] += 1
        self.performance_stats['total_tokens'] += tokens_generated
        self.performance_stats['total_time'] += generation_time
        
        if generation_time > 0:
            tokens_per_second = tokens_generated / generation_time
            # Update running average
            current_avg = self.performance_stats['avg_tokens_per_second']
            total_gens = self.performance_stats['total_generations']
            self.performance_stats['avg_tokens_per_second'] = (
                (current_avg * (total_gens - 1) + tokens_per_second) / total_gens
            )
        
        # Update memory usage
        memory_info = self.get_memory_usage()
        self.performance_stats['memory_usage_mb'] = memory_info['rss_mb']
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        return self.performance_stats.copy()
    
    def reset_performance_stats(self) -> None:
        """Reset performance statistics."""
        self.performance_stats = {
            'total_generations': 0,
            'total_tokens': 0,
            'total_time': 0.0,
            'avg_tokens_per_second': 0.0,
            'memory_usage_mb': 0.0
        }
    
    def cleanup_memory(self) -> None:
        """Clean up memory and force garbage collection."""
        gc.collect()
        if hasattr(self, 'llm') and self.llm:
            # Force cleanup of llama-cpp-python internal state
            try:
                # This is a best-effort cleanup
                delattr(self.llm, '_ctx')
            except:
                pass
        gc.collect()
    
    def generate_with_context(self, prompt: str, context: str, 
                             max_tokens: Optional[int] = None) -> str:
        """Generate text with additional context.
        
        Args:
            prompt: Input prompt
            context: Additional context
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        # Combine prompt and context
        full_prompt = f"Context: {context}\n\nPrompt: {prompt}\n\nResponse:"
        return self.generate(full_prompt, max_tokens)
    
    def generate_topic_content(self, topic: str, file_format: str, 
                              context: Optional[Dict[str, Any]] = None) -> str:
        """Generate unique topic-specific content for file format.
        
        Args:
            topic: Topic for content generation
            file_format: Target file format
            context: Optional context information
            
        Returns:
            Generated content
        """
        # Add uniqueness factors to ensure content variation
        uniqueness_factors = self._get_uniqueness_factors(context)
        
        # Build specialized prompt based on format
        if file_format.lower() in ['eml', 'msg']:
            format_context = "email message"
            structure_hint = "Include proper email headers, subject line, and professional body structure."
        elif file_format.lower() in ['xlsx', 'xlsm', 'xltm', 'xls', 'xlsb', 'ods']:
            format_context = "spreadsheet data"
            structure_hint = "Include tabular data, formulas, cell references, and configuration tables."
        elif file_format.lower() in ['pptx', 'ppt', 'odp']:
            format_context = "presentation slides"
            structure_hint = "Include slide content, bullet points, speaker notes, and visual elements."
        elif file_format.lower() in ['vsdx', 'vsd', 'vsdm', 'vssx', 'vssm', 'vstx', 'vstm']:
            format_context = "diagram documentation"
            structure_hint = "Include shape descriptions, connections, data fields, and architectural elements."
        elif file_format.lower() in ['docx', 'doc', 'docm', 'rtf', 'odf']:
            format_context = "technical document"
            structure_hint = "Include structured content with clear sections, headers, and professional formatting."
        elif file_format.lower() == 'pdf':
            format_context = "comprehensive documentation"
            structure_hint = "Include detailed sections, technical specifications, and professional layout."
        elif file_format.lower() in ['png', 'jpg', 'jpeg', 'bmp']:
            format_context = "image metadata and description"
            structure_hint = "Include detailed image descriptions, technical specifications, and metadata."
        else:
            format_context = "documentation"
            structure_hint = "Include structured content with clear sections."
        
        # Get language from context
        language = context.get('language', 'en') if context else 'en'
        language_instruction = ""
        if language and language != 'en' and language != 'all':
            language_names = {
                'fr': 'French (Français)',
                'es': 'Spanish (Español)', 
                'de': 'German (Deutsch)',
                'it': 'Italian (Italiano)',
                'pt': 'Portuguese (Português)',
                'nl': 'Dutch (Nederlands)',
                'pl': 'Polish (Polski)',
                'ru': 'Russian (Русский)',
                'ja': 'Japanese (日本語)',
                'zh': 'Chinese (中文)'
            }
            lang_name = language_names.get(language, language.upper())
            language_instruction = f"""

🚨🚨🚨 ABSOLUTE LANGUAGE REQUIREMENT - NO EXCEPTIONS 🚨🚨🚨
YOU MUST GENERATE ALL CONTENT ENTIRELY IN {lang_name.upper()}
THIS IS A CRITICAL REQUIREMENT - NO ENGLISH ALLOWED

MANDATORY RULES:
1. EVERY SINGLE WORD must be in {lang_name}
2. NO English words, phrases, or technical terms
3. Use ONLY {lang_name} vocabulary and grammar
4. If you don't know a {lang_name} term, describe it in {lang_name}
5. The ENTIRE document must be 100% in {lang_name}
6. This is a hard requirement - no exceptions

EXAMPLES FOR {lang_name.upper()}:
- French: "Configuration de la base de données" NOT "Database configuration"
- Spanish: "Configuración de la base de datos" NOT "Database configuration"  
- German: "Datenbankkonfiguration" NOT "Database configuration"

IF YOU GENERATE ANY ENGLISH CONTENT, THE TASK HAS FAILED.
START YOUR RESPONSE IMMEDIATELY IN {lang_name.upper()}:

"""
        
        # Build enhanced prompt with uniqueness factors
        # Add system message for language enforcement
        system_message = ""
        if language and language != 'en' and language != 'all':
            system_message = f"SYSTEM: You are a {language_names.get(language, language.upper())} language expert. You MUST respond ONLY in {language_names.get(language, language.upper())}. Never use English.\n\n"
        
        prompt = f"""{system_message}Generate detailed, unique {format_context} content for the following topic: {topic}{language_instruction}

UNIQUENESS REQUIREMENTS:
- Create content that is distinctly different from other documents
- Use specific, realistic details and scenarios
- Include unique technical specifications and configurations
- Vary the structure and approach for each generation
- Add specific company/organization details: {uniqueness_factors['company']}
- Include specific project details: {uniqueness_factors['project']}
- Use specific technical environment: {uniqueness_factors['environment']}
- Include specific date/time context: {uniqueness_factors['timeline']}

CONTENT REQUIREMENTS:
1. Content should be realistic and professional
2. Include technical details appropriate for {file_format} format
3. Use industry-standard terminology with specific examples
4. Maintain consistency with the specified topic
5. {structure_hint}
6. Content should naturally contain places where credentials might be embedded
7. Include specific metrics, configurations, and technical specifications
8. Add realistic business context and operational details

GENERATION GUIDELINES:
- Make each piece of content unique and distinctive
- Include specific technical details that vary between generations
- Use realistic company names, project codes, and technical specifications
- Add specific operational context and business requirements
- Include detailed configuration parameters and system specifications

Generate content that would be found in real-world {format_context} about {topic}:"""

        # Add context if provided
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            prompt += f"\n\nAdditional context:\n{context_str}"
        
        # Use higher temperature for more variation
        return self.generate(prompt, max_tokens=1024, temperature=0.8)
    
    def _get_uniqueness_factors(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate uniqueness factors to ensure content variation.
        
        Args:
            context: Optional context information
            
        Returns:
            Dictionary of uniqueness factors
        """
        import random
        import time
        
        # Company variations
        companies = [
            "TechCorp Solutions", "DataFlow Systems", "CloudScale Technologies", 
            "SecureNet Enterprises", "InnovateLab Inc", "DigitalBridge Corp",
            "NextGen Systems", "CyberShield Technologies", "QuantumSoft Solutions",
            "EliteTech Industries", "ProActive Systems", "FutureTech Dynamics"
        ]
        
        # Project variations
        projects = [
            "Project Phoenix", "Operation Thunder", "System Alpha", "Initiative Beta",
            "Mission Control", "Project Genesis", "Operation Storm", "System Nova",
            "Initiative Titan", "Mission Vector", "Project Quantum", "Operation Matrix"
        ]
        
        # Environment variations
        environments = [
            "Production AWS Cloud", "Development Azure Environment", "Staging GCP Platform",
            "Hybrid Cloud Infrastructure", "On-Premises Data Center", "Multi-Cloud Setup",
            "Containerized Kubernetes", "Serverless Architecture", "Microservices Platform",
            "Edge Computing Network", "Distributed Systems", "High-Availability Cluster"
        ]
        
        # Timeline variations
        timelines = [
            "Q1 2024 Implementation", "Q2 2024 Deployment", "Q3 2024 Migration",
            "Q4 2024 Rollout", "January 2024 Launch", "February 2024 Go-Live",
            "March 2024 Release", "April 2024 Update", "May 2024 Enhancement",
            "June 2024 Upgrade", "July 2024 Modernization", "August 2024 Optimization"
        ]
        
        # Use context file_index for additional variation if available
        seed = context.get('file_index', 0) if context else 0
        random.seed(seed + int(time.time() * 1000) % 10000)
        
        return {
            'company': random.choice(companies),
            'project': random.choice(projects),
            'environment': random.choice(environments),
            'timeline': random.choice(timelines)
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        return self.model_info.copy()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage.
        
        Returns:
            Dictionary with memory usage information
        """
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / (1024 * 1024),  # Resident Set Size
            'vms_mb': memory_info.vms / (1024 * 1024),  # Virtual Memory Size
            'percent': process.memory_percent()
        }
    
    def benchmark(self, prompt: str, iterations: int = 5) -> Dict[str, float]:
        """Benchmark model performance.
        
        Args:
            prompt: Test prompt
            iterations: Number of iterations
            
        Returns:
            Dictionary with performance metrics
        """
        if not self.llm:
            raise LLMError("Model not loaded")
        
        times = []
        tokens_generated = []
        
        for i in range(iterations):
            start_time = time.time()
            response = self.generate(prompt, max_tokens=100)
            end_time = time.time()
            
            times.append(end_time - start_time)
            # Rough token count estimation
            tokens_generated.append(len(response.split()))
        
        avg_time = sum(times) / len(times)
        avg_tokens = sum(tokens_generated) / len(tokens_generated)
        tokens_per_second = avg_tokens / avg_time if avg_time > 0 else 0
        
        return {
            'avg_generation_time': avg_time,
            'avg_tokens_generated': avg_tokens,
            'tokens_per_second': tokens_per_second,
            'iterations': iterations
        }
    
    def unload(self) -> None:
        """Unload the model to free memory."""
        # Cleanup thread pool
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
            self.thread_pool = None
        
        # Cleanup model
        if self.llm:
            del self.llm
            self.llm = None
        
        # Force garbage collection
        self.cleanup_memory()
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.unload()
    
    @staticmethod
    def get_available_models(models_dir: str = "./models") -> List[Dict[str, Any]]:
        """Get list of available GGUF models in directory.
        
        Args:
            models_dir: Directory to search for models
            
        Returns:
            List of model information dictionaries
        """
        models = []
        models_path = Path(models_dir)
        
        if not models_path.exists():
            return models
        
        for model_file in models_path.glob("*.gguf"):
            try:
                file_size = model_file.stat().st_size
                models.append({
                    'name': model_file.stem,
                    'path': str(model_file),
                    'size_mb': file_size / (1024 * 1024),
                    'size_bytes': file_size
                })
            except Exception:
                continue
        
        return sorted(models, key=lambda x: x['size_mb'])
    
    @staticmethod
    def get_optimal_config(system_memory_gb: Optional[float] = None) -> Dict[str, Any]:
        """Get optimal configuration based on system resources.
        
        Args:
            system_memory_gb: Available system memory in GB
            
        Returns:
            Optimal configuration dictionary
        """
        if system_memory_gb is None:
            system_memory_gb = psutil.virtual_memory().total / (1024**3)
        
        cpu_count = psutil.cpu_count()
        
        # Determine optimal settings based on available resources
        if system_memory_gb < 4:
            return {
                'n_threads': min(cpu_count, 4),
                'n_ctx': 4096,
                'n_batch': 512,
                'recommended_models': ['qwen2-0.5b', 'tinyllama-1.1b']
            }
        elif system_memory_gb < 8:
            return {
                'n_threads': min(cpu_count, 6),
                'n_ctx': 4096,
                'n_batch': 512,
                'recommended_models': ['tinyllama-1.1b', 'gemma-2b']
            }
        else:
            return {
                'n_threads': min(cpu_count, 8),
                'n_ctx': 4096,
                'n_batch': 512,
                'recommended_models': ['phi-3-mini-4k', 'gemma-2b', 'tinyllama-1.1b']
            }
    
    @classmethod
    def download_model(cls, model_name: str, models_dir: Optional[str] = None) -> str:
        """Download a lightweight LLM model to local models directory.
        
        Args:
            model_name: Name of the model to download
            models_dir: Directory to store models (defaults to project models/)
            
        Returns:
            Path to the downloaded model file
            
        Raises:
            LLMError: If download fails
        """
        # Get project root and models directory
        project_root = Path(__file__).parent.parent.parent
        if models_dir is None:
            models_dir = project_root / "models"
        else:
            models_dir = Path(models_dir)
        
        models_dir.mkdir(exist_ok=True)
        
        # Model URLs for lightweight models
        model_urls = {
            'tinyllama': 'https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
            'phi3-mini': 'https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf',
            'qwen2-0.5b': 'https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF/resolve/main/qwen2-0_5b-instruct-q4_k_m.gguf',
            'gemma-2b': 'https://huggingface.co/google/gemma-2b-it-GGUF/resolve/main/gemma-2b-it-q4_k_m.gguf'
        }
        
        if model_name not in model_urls:
            raise LLMError(f"Unknown model: {model_name}. Available: {list(model_urls.keys())}")
        
        model_file = models_dir / f"{model_name}.gguf"
        
        # Check if model already exists
        if model_file.exists():
            return str(model_file)
        
        # Download model
        url = model_urls[model_name]
        print(f"Downloading {model_name} from {url}...")
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(model_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rDownloaded: {percent:.1f}%", end='', flush=True)
            
            print(f"\nModel downloaded to: {model_file}")
            return str(model_file)
            
        except Exception as e:
            if model_file.exists():
                model_file.unlink()  # Remove partial download
            raise LLMError(f"Failed to download model {model_name}: {e}")
    
    @classmethod
    def list_available_models(cls, models_dir: Optional[str] = None) -> List[str]:
        """List available models in the local models directory.
        
        Args:
            models_dir: Directory to check for models (defaults to project models/)
            
        Returns:
            List of available model names
        """
        project_root = Path(__file__).parent.parent.parent
        if models_dir is None:
            models_dir = project_root / "models"
        else:
            models_dir = Path(models_dir)
        
        if not models_dir.exists():
            return []
        
        models = []
        for file in models_dir.glob("*.gguf"):
            models.append(file.stem)
        
        return models
    
    def _has_language_requirement(self, prompt: str) -> bool:
        """Check if prompt contains language requirement."""
        return "ABSOLUTE LANGUAGE REQUIREMENT" in prompt or "CRITICAL LANGUAGE REQUIREMENT" in prompt
    
    def _extract_language_from_prompt(self, prompt: str) -> str:
        """Extract target language from prompt."""
        import re
        
        # Look for language patterns in the prompt
        patterns = [
            r"GENERATE ALL CONTENT ENTIRELY IN (\w+)",
            r"in (\w+\.upper\(\))",
            r"language.*?(\w{2,3})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                lang = match.group(1).lower()
                # Map common language names to codes
                lang_map = {
                    'french': 'fr', 'français': 'fr',
                    'spanish': 'es', 'español': 'es',
                    'german': 'de', 'deutsch': 'de',
                    'italian': 'it', 'italiano': 'it',
                    'portuguese': 'pt', 'português': 'pt',
                    'dutch': 'nl', 'nederlands': 'nl',
                    'polish': 'pl', 'polski': 'pl',
                    'russian': 'ru', 'русский': 'ru',
                    'japanese': 'ja', '日本語': 'ja',
                    'chinese': 'zh', '中文': 'zh'
                }
                return lang_map.get(lang, lang)
        
        return None
    
    def _ensure_language_compliance(self, content: str, target_language: str) -> str:
        """Ensure content is in the target language, translate if necessary."""
        # Simple English detection (basic heuristic)
        english_indicators = [
            'the ', 'and ', 'or ', 'but ', 'in ', 'on ', 'at ', 'to ', 'for ',
            'of ', 'with ', 'by ', 'from ', 'is ', 'are ', 'was ', 'were ',
            'have ', 'has ', 'had ', 'will ', 'would ', 'could ', 'should ',
            'configuration', 'database', 'system', 'server', 'client',
            'application', 'service', 'network', 'security', 'authentication'
        ]
        
        # Check if content contains English indicators
        content_lower = content.lower()
        english_count = sum(1 for indicator in english_indicators if indicator in content_lower)
        
        # If significant English content detected, add translation instruction
        if english_count > 3:
            self.logger.warning(f"Detected English content in {target_language} generation, adding translation instruction")
            
            # Add translation instruction to the content
            language_names = {
                'fr': 'French (Français)',
                'es': 'Spanish (Español)', 
                'de': 'German (Deutsch)',
                'it': 'Italian (Italiano)',
                'pt': 'Portuguese (Português)',
                'nl': 'Dutch (Nederlands)',
                'pl': 'Polish (Polski)',
                'ru': 'Russian (Русский)',
                'ja': 'Japanese (日本語)',
                'zh': 'Chinese (中文)'
            }
            
            lang_name = language_names.get(target_language, target_language.upper())
            
            # Create a translation prompt
            translation_prompt = f"""
TRANSLATE THE FOLLOWING CONTENT TO {lang_name.upper()}:

{content}

IMPORTANT: 
- Translate ALL English words and phrases to {lang_name}
- Maintain the same technical meaning and structure
- Use proper {lang_name} grammar and vocabulary
- Do not leave any English words untranslated

TRANSLATED CONTENT IN {lang_name.upper()}:"""
            
            try:
                # Attempt to translate using the LLM
                translated = self.generate(translation_prompt, max_tokens=1500, temperature=0.3)
                if translated and len(translated.strip()) > 50:  # Ensure we got a reasonable translation
                    self.logger.info(f"Successfully translated content to {target_language}")
                    return translated.strip()
            except Exception as e:
                self.logger.warning(f"Translation failed: {e}")
        
        return content
