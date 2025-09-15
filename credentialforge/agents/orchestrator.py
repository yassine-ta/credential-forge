"""Main orchestrator agent for CredentialForge."""

import time
import random
import multiprocessing as mp
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from pathlib import Path
import psutil

# Removed redundant agents - functionality consolidated into ContentGenerationAgent
from .content_generation_agent import ContentGenerationAgent
from ..generators.credential_generator import CredentialGenerator
from ..generators.topic_generator import TopicGenerator
# Old synthesizers removed - using new format-only synthesizers
# New format-only synthesizers
from ..synthesizers.eml_format_synthesizer import EMLFormatSynthesizer
from ..synthesizers.msg_format_synthesizer import MSGFormatSynthesizer
from ..synthesizers.pptx_format_synthesizer import PPTXFormatSynthesizer
from ..synthesizers.pdf_format_synthesizer import PDFFormatSynthesizer
from ..synthesizers.excel_format_synthesizer import ExcelFormatSynthesizer
from ..synthesizers.word_format_synthesizer import WordFormatSynthesizer, RTFFormatSynthesizer
from ..synthesizers.opendocument_format_synthesizer import OpenDocumentFormatSynthesizer
from ..synthesizers.image_format_synthesizer import ImageFormatSynthesizer
from ..synthesizers.visio_format_synthesizer import VisioFormatSynthesizer
from ..db.regex_db import RegexDatabase
from ..llm.llama_interface import LlamaInterface
from ..utils.exceptions import GenerationError
from ..utils.logger import Logger
# Removed PromptSystem - using simplified prompts


class OrchestratorAgent:
    """Main orchestrator that coordinates the generation process."""
    
    def __init__(self, llm_interface: Optional[LlamaInterface] = None, 
                 config: Optional[Dict[str, Any]] = None):
        """Initialize orchestrator agent.
        
        Args:
            llm_interface: Optional LLM interface for content generation
            config: Configuration object with generation parameters
        """
        self.llm = llm_interface
        self.config = config or {}
        self.logger = Logger('orchestrator')
        
        # Simplified prompt system removed
        
        # Enhanced multiprocessing configuration
        self.max_workers = self._get_optimal_workers()
        self.use_multiprocessing = self.config.get('use_multiprocessing', True)  # Enabled by default
        self.memory_limit_gb = self.config.get('memory_limit_gb', 4)
        self.batch_size = self.config.get('batch_size', 10)
        self.enable_parallel_llm = self.config.get('enable_parallel_llm', True)
        self.memory_cleanup_interval = self.config.get('memory_cleanup_interval', 5)  # Cleanup every 5 batches
        
        # Initialize content generation agent
        self.content_generation_agent = None  # Will be initialized with LLM
        
        # Initialize generators
        self.credential_generator = None
        self.topic_generator = None
        
        # Initialize regex database (will be set after config parsing)
        self.regex_db = None
        
        # Initialize components if config is provided
        if self.config:
            self._initialize_components()
        
        # Initialize format synthesizers
        self.format_synthesizers = {}
        
        # Enhanced generation statistics
        self.generation_stats = {
            'total_files': 0,
            'total_credentials': 0,
            'total_errors': 0,
            'generation_time': 0,
            'files_by_format': {},
            'credentials_by_type': {},
            'parallel_batches': 0,
            'sequential_batches': 0,
            'memory_cleanups': 0,
            'avg_batch_time': 0.0,
            'total_batches': 0
        }
        
        # Performance monitoring
        self.batch_times = []
        self.memory_usage_history = []
        
        # LLM loading state
        self.llm_loading = False
    
    def orchestrate_generation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate the complete generation process.
        
        Args:
            config: Generation configuration
            
        Returns:
            Dictionary with generation results and metadata
        """
        start_time = time.time()
        
        try:
            # Parse and validate configuration
            self._parse_configuration(config)
            
            # Initialize components
            self._initialize_components()
            
            # Wait for LLM to be ready if it's loading
            if hasattr(self, 'llm_loading') and self.llm_loading:
                self.logger.info("Waiting for LLM to finish loading before generation...")
                if self._wait_for_llm_loading(timeout=60):  # Wait up to 60 seconds
                    self.logger.info("LLM is ready for realistic generation")
                else:
                    self.logger.warning("LLM loading timed out - proceeding with fallback generation")
            
            # Generate files
            results = self._generate_files()
            
            # Calculate generation time
            generation_time = time.time() - start_time
            self.generation_stats['generation_time'] = generation_time
            
            # Prepare results
            return {
                'files': results['files'],
                'errors': results['errors'],
                'metadata': {
                    'total_files': len(results['files']),
                    'total_credentials': self.generation_stats['total_credentials'],
                    'generation_time': generation_time,
                    'files_by_format': self.generation_stats['files_by_format'],
                    'credentials_by_type': self.generation_stats['credentials_by_type']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}")
            raise GenerationError(f"Generation orchestration failed: {e}")
    
    def _parse_configuration(self, config: Dict[str, Any]) -> None:
        """Parse and validate configuration.
        
        Args:
            config: Generation configuration
        """
        # Required parameters
        required_params = ['output_dir', 'num_files', 'formats', 'credential_types', 'topics']
        for param in required_params:
            if param not in config:
                raise GenerationError(f"Missing required parameter: {param}")
        
        # Set configuration
        self.config = config
        
        # Initialize regex database after config is set
        self.regex_db = None
        print(f"DEBUG: Config keys in _parse_configuration: {list(config.keys())}")
        if 'regex_db_path' in config:
            try:
                from ..db.regex_db import RegexDatabase
                print(f"DEBUG: Initializing regex database with path: {config['regex_db_path']}")
                self.regex_db = RegexDatabase(config['regex_db_path'])
                print("DEBUG: Regex database initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize regex database: {e}")
                self.regex_db = None
        else:
            print("DEBUG: No regex_db_path key found in config")
        
        # Set random seed if provided
        if 'seed' in config:
            random.seed(config['seed'])
        
        self.logger.info(f"Configuration parsed: {len(config)} parameters")
        
        # Apply enhanced reasoning for configuration analysis
        self._apply_enhanced_reasoning('configuration_analysis', config)
    
    def _initialize_credential_generator(self) -> None:
        """Initialize credential generator with regex database."""
        try:
            # Load regex database
            regex_db_path = self.config.get('regex_db_path', './data/regex_db.json')
            regex_db = RegexDatabase(regex_db_path)
            
            # Wait for LLM loading if it's in progress
            if hasattr(self, 'llm_loading') and self.llm_loading:
                self.logger.info("Waiting for LLM to finish loading...")
                if not self._wait_for_llm_loading():
                    self.logger.warning("LLM loading failed or timed out, proceeding without LLM")
            
            # Initialize credential generator (simplified)
            self.credential_generator = CredentialGenerator(regex_db=regex_db)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize credential generator: {e}")
            self.credential_generator = None
    
    def _initialize_topic_generator(self) -> None:
        """Initialize topic generator with language mapper."""
        try:
            from ..utils.language_mapper import LanguageMapper
            language_mapper = LanguageMapper()
            
            # If no LLM interface provided, try to initialize one
            if self.llm is None:
                self._initialize_llm_interface()
            
            self.topic_generator = TopicGenerator(self.llm, language_mapper=language_mapper)
            
            # Initialize content generation agent with regex database
            # Use fast credential generation by default for better performance
            use_llm_for_credentials = self.config.get('use_llm_for_credentials', False)
            use_llm_for_content = self.config.get('use_llm_for_content', False)
            self.content_generation_agent = ContentGenerationAgent(
                llm_interface=self.llm,
                language_mapper=language_mapper,
                regex_db=self.regex_db,
                use_llm_for_credentials=use_llm_for_credentials,
                use_llm_for_content=use_llm_for_content
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize topic generator: {e}")
            self.topic_generator = None
    
    def _initialize_content_generation_agent(self) -> None:
        """Initialize content generation agent."""
        try:
            # Wait for LLM loading if it's in progress
            if hasattr(self, 'llm_loading') and self.llm_loading:
                self.logger.info("Waiting for LLM to finish loading for content generation agent...")
                if not self._wait_for_llm_loading():
                    self.logger.warning("LLM loading failed or timed out, proceeding without LLM")
            
            # Get language mapper
            language_mapper = None
            if hasattr(self, 'language_mapper') and self.language_mapper:
                language_mapper = self.language_mapper
            
            # Initialize content generation agent with regex database
            # Use fast credential generation by default for better performance
            use_llm_for_credentials = self.config.get('use_llm_for_credentials', False)
            use_llm_for_content = self.config.get('use_llm_for_content', False)
            self.content_generation_agent = ContentGenerationAgent(
                llm_interface=self.llm,
                language_mapper=language_mapper,
                regex_db=self.regex_db,
                use_llm_for_credentials=use_llm_for_credentials,
                use_llm_for_content=use_llm_for_content
            )
            
            self.logger.info("Content generation agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize content generation agent: {e}")
            self.content_generation_agent = None
    
    def _initialize_llm_interface(self) -> None:
        """Initialize LLM interface if not provided."""
        try:
            # Always initialize LLM for realistic credential generation
            # Use async loading to avoid blocking the main process
            self.logger.info("LLM is required for realistic credential generation")
            
            # Use lazy initialization - start LLM loading in background thread
            self.logger.info("Starting LLM initialization in background thread...")
            self._start_llm_initialization_async()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM interface: {e}")
            self.llm = None
    
    def _start_llm_initialization_async(self) -> None:
        """Start LLM initialization in a background thread."""
        import threading
        
        def load_llm_async():
            try:
                from ..llm.llama_interface import LlamaInterface
                import time
                
                # Look for available models
                models_dir = Path("./models")
                if not models_dir.exists():
                    self.logger.warning("No models directory found")
                    self.llm_loading = False
                    return
                    
                model_files = list(models_dir.glob("*.gguf"))
                if not model_files:
                    self.logger.warning("No GGUF model files found")
                    self.llm_loading = False
                    return
                
                model_path = str(model_files[0].absolute())
                self.logger.info(f"Loading LLM model: {model_files[0].name}")
                
                start_time = time.time()
                # Use optimized settings for faster loading
                self.llm = LlamaInterface(
                    model_path, 
                    n_threads=6,  # Balanced threads for main process
                    n_ctx=2048,   # Reduced context for faster loading
                    n_batch=256   # Reduced batch size for faster loading
                )
                load_time = time.time() - start_time
                
                self.logger.info(f"LLM loaded successfully in {load_time:.2f} seconds")
                self.llm_loading = False  # Mark loading as complete
                
            except Exception as e:
                self.logger.error(f"Background LLM loading failed: {e}")
                self.llm = None
                self.llm_loading = False  # Mark loading as complete even on failure
        
        # Start LLM loading in background thread
        llm_thread = threading.Thread(target=load_llm_async, daemon=True)
        llm_thread.start()
        
        # Set a flag to indicate LLM is being loaded
        self.llm_loading = True
    
    def _wait_for_llm_loading(self, timeout: int = 15) -> bool:
        """Wait for LLM loading to complete.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if LLM is ready, False if timeout or failed
        """
        if not hasattr(self, 'llm_loading') or not self.llm_loading:
            return self.llm is not None
        
        import time
        start_time = time.time()
        
        while hasattr(self, 'llm_loading') and self.llm_loading and (time.time() - start_time) < timeout:
            time.sleep(0.1)  # Check every 100ms
        
        if hasattr(self, 'llm_loading') and self.llm_loading:
            self.logger.warning(f"LLM loading timed out after {timeout} seconds")
            self.llm_loading = False
            return False
        
        return self.llm is not None
    
    def is_llm_ready(self) -> bool:
        """Check if LLM is ready for use.
        
        Returns:
            True if LLM is loaded and ready, False otherwise
        """
        return self.llm is not None and (not hasattr(self, 'llm_loading') or not self.llm_loading)
    
    def _initialize_components(self) -> None:
        """Initialize all components for generation."""
        try:
            self.logger.info("Initializing components...")
            
            # Initialize LLM interface first if needed
            if self.llm is None:
                self._initialize_llm_interface()
            
            # Initialize generators if not already done
            if not self.credential_generator:
                self._initialize_credential_generator()
            if not self.topic_generator:
                self._initialize_topic_generator()
            
            # Initialize content generation agent if not already done
            if not self.content_generation_agent:
                self.logger.info("Initializing content generation agent...")
                self._initialize_content_generation_agent()
                self.logger.info(f"Content generation agent initialized: {self.content_generation_agent is not None}")
                
                # Check if LLM is ready for realistic generation
                if not self.is_llm_ready():
                    self.logger.warning("LLM is not ready - content generation will use fallback methods")
            
            # Initialize synthesizers
            output_dir = str(self.config['output_dir'])
            ultra_fast_mode = not self.config.get('use_llm_for_credentials', False) and not self.config.get('use_llm_for_content', False)
            
            # Initialize new format-only synthesizers (for testing new architecture)
            self.format_synthesizers = {
                # Email formats
                'eml_format': EMLFormatSynthesizer(output_dir, ultra_fast_mode),
                'msg_format': MSGFormatSynthesizer(output_dir, ultra_fast_mode),
                
                # Excel formats
                'xlsx_format': ExcelFormatSynthesizer(output_dir, 'xlsx', ultra_fast_mode),
                'xls_format': ExcelFormatSynthesizer(output_dir, 'xls', ultra_fast_mode),
                'xlsm_format': ExcelFormatSynthesizer(output_dir, 'xlsm', ultra_fast_mode),
                'xlsb_format': ExcelFormatSynthesizer(output_dir, 'xlsb', ultra_fast_mode),
                'xltm_format': ExcelFormatSynthesizer(output_dir, 'xltm', ultra_fast_mode),
                
                # Word formats
                'docx_format': WordFormatSynthesizer(output_dir, 'docx', ultra_fast_mode),
                'doc_format': WordFormatSynthesizer(output_dir, 'doc', ultra_fast_mode),
                'docm_format': WordFormatSynthesizer(output_dir, 'docm', ultra_fast_mode),
                'rtf_format': RTFFormatSynthesizer(output_dir, ultra_fast_mode),
                
                # PowerPoint formats
                'pptx_format': PPTXFormatSynthesizer(output_dir, ultra_fast_mode),
                'ppt_format': PPTXFormatSynthesizer(output_dir, ultra_fast_mode),
                
                # OpenDocument formats
                'odt_format': OpenDocumentFormatSynthesizer(output_dir, 'odt', ultra_fast_mode),
                'ods_format': OpenDocumentFormatSynthesizer(output_dir, 'ods', ultra_fast_mode),
                'odp_format': OpenDocumentFormatSynthesizer(output_dir, 'odp', ultra_fast_mode),
                'odf_format': OpenDocumentFormatSynthesizer(output_dir, 'odf', ultra_fast_mode),
                
                # PDF format
                'pdf_format': PDFFormatSynthesizer(output_dir, ultra_fast_mode),
                
                # Image formats
                'png_format': ImageFormatSynthesizer(output_dir, 'png', ultra_fast_mode),
                'jpg_format': ImageFormatSynthesizer(output_dir, 'jpg', ultra_fast_mode),
                'jpeg_format': ImageFormatSynthesizer(output_dir, 'jpeg', ultra_fast_mode),
                'bmp_format': ImageFormatSynthesizer(output_dir, 'bmp', ultra_fast_mode),
                
                # Visio formats
                'vsdx_format': VisioFormatSynthesizer(output_dir, 'vsdx', ultra_fast_mode),
                'vsd_format': VisioFormatSynthesizer(output_dir, 'vsd', ultra_fast_mode),
                'vsdm_format': VisioFormatSynthesizer(output_dir, 'vsdm', ultra_fast_mode),
                'vssx_format': VisioFormatSynthesizer(output_dir, 'vssx', ultra_fast_mode),
                'vssm_format': VisioFormatSynthesizer(output_dir, 'vssm', ultra_fast_mode),
                'vstx_format': VisioFormatSynthesizer(output_dir, 'vstx', ultra_fast_mode),
                'vstm_format': VisioFormatSynthesizer(output_dir, 'vstm', ultra_fast_mode)
            }
            
            self.logger.info("Components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")
            # Don't raise exception during initialization, just log it
            # The system can still work with some components missing
    
    def _generate_files(self) -> Dict[str, Any]:
        """Generate all files according to configuration.
        
        Returns:
            Dictionary with generated files and errors
        """
        files = []
        errors = []
        
        num_files = self.config['num_files']
        formats = self.config['formats']
        topics = self.config['topics']
        credential_types = self.config['credential_types']
        output_dir = Path(self.config['output_dir'])
        batch_size = self.config.get('batch_size', 10)
        
        # Load regex database
        regex_db_path = self.config.get('regex_db_path', './data/regex_db.json')
        regex_db = RegexDatabase(regex_db_path)
        
        # Auto-adjust batch size for very large operations
        if num_files > 1000 and batch_size > 50:
            batch_size = min(50, num_files // 20)  # Reduce batch size for large operations
            self.logger.info(f"Auto-adjusted batch size to {batch_size} for better performance with {num_files} files")
        
        # Generate files in batches
        batch_num = 1
        for batch_start in range(0, num_files, batch_size):
            batch_end = min(batch_start + batch_size, num_files)
            batch_files = batch_end - batch_start
            
            self.logger.info(f"Generating batch {batch_num}: files {batch_start+1}-{batch_end}")
            
            # Check memory before processing batch
            if not self._check_memory_usage():
                self.logger.warning("Memory usage high, performing cleanup")
                self._cleanup_memory()
                
                # If still high, reduce batch size (but be less aggressive)
                if not self._check_memory_usage():
                    self.logger.warning("Memory usage still high, reducing batch size")
                    batch_size = max(2, batch_size // 2)  # Don't go below 2
                    # Continue with reduced batch size instead of restarting
                    self.logger.info(f"Continuing with reduced batch size: {batch_size}")
            
            # Generate batch using multiprocessing or sequential
            if self.use_multiprocessing and batch_files >= 5:  # Lowered threshold for better performance
                batch_results = self._generate_batch_parallel(
                    batch_files, formats, topics, credential_types, 
                    regex_db, output_dir, batch_start
                )
            else:
                batch_results = self._generate_batch_sequential(
                    batch_files, formats, topics, credential_types, 
                    regex_db, output_dir, batch_start
                )
            
            files.extend(batch_results['files'])
            errors.extend(batch_results['errors'])
            batch_num += 1
            
            # Periodic memory cleanup
            if batch_num % self.memory_cleanup_interval == 0:
                self.logger.info(f"Performing periodic memory cleanup after batch {batch_num}")
                self._cleanup_memory()
        
        return {'files': files, 'errors': errors}
    
    def _get_optimal_workers(self) -> int:
        """Calculate optimal number of workers based on system resources."""
        cpu_count = mp.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Enhanced approach: use 60-80% of available cores
        # but limit based on memory (1GB per worker minimum)
        max_workers_by_cpu = max(1, int(cpu_count * 0.8))
        max_workers_by_memory = max(1, int(memory_gb / 1.2))  # 1.2GB per worker for better performance
        
        optimal_workers = min(max_workers_by_cpu, max_workers_by_memory, 12)  # Cap at 12 for better performance
        self.logger.info(f"System: {cpu_count} CPUs, {memory_gb:.1f}GB RAM -> {optimal_workers} workers")
        return optimal_workers
    
    def _apply_enhanced_reasoning(self, task_type: str, context: Dict[str, Any]) -> None:
        """Apply enhanced reasoning using the prompt system.
        
        Args:
            task_type: Type of task for reasoning
            context: Context information for reasoning
        """
        try:
            # Get language from config - handle both string and list
            language_config = self.config.get('language', 'en')
            if isinstance(language_config, list):
                # Multiple languages selected - use first one for reasoning
                language = language_config[0] if language_config else 'en'
            else:
                # Single language or None (for random selection)
                language = language_config or 'en'
            
            # Simplified prompt for orchestrator
            enhanced_prompt = f"Analyze and coordinate {task_type} in {language}"
            
            # Log the enhanced reasoning approach
            self.logger.info(f"Applied enhanced reasoning for {task_type} in {language}")
            
            # Store reasoning context for future reference
            if not hasattr(self, 'reasoning_context'):
                self.reasoning_context = {}
            
            self.reasoning_context[task_type] = {
                'prompt': enhanced_prompt,
                'context': context,
                'language': language,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.warning(f"Enhanced reasoning failed for {task_type}: {e}")
            # Continue without enhanced reasoning if it fails
    
    def _check_memory_usage(self) -> bool:
        """Check if memory usage is within limits."""
        memory = psutil.virtual_memory()
        used_gb = memory.used / (1024**3)
        total_gb = memory.total / (1024**3)
        # Use percentage-based check instead of absolute limit
        usage_percentage = (used_gb / total_gb) * 100
        
        # Store memory usage history
        self.memory_usage_history.append({
            'timestamp': time.time(),
            'used_gb': used_gb,
            'percentage': usage_percentage
        })
        
        # Keep only last 100 entries
        if len(self.memory_usage_history) > 100:
            self.memory_usage_history = self.memory_usage_history[-100:]
        
        return usage_percentage < 95  # Allow up to 95% memory usage (more reasonable for 31GB system)
    
    def _cleanup_memory(self) -> None:
        """Clean up memory and force garbage collection."""
        import gc
        gc.collect()
        
        # Cleanup LLM memory if available
        if self.llm and hasattr(self.llm, 'cleanup_memory'):
            self.llm.cleanup_memory()
        
        # Update stats
        self.generation_stats['memory_cleanups'] += 1
        self.logger.info("Memory cleanup performed")
    
    def _generate_batch_parallel(self, batch_files: int, formats: List[str], 
                                topics: List[str], credential_types: List[str],
                                regex_db: RegexDatabase, output_dir: Path, 
                                batch_start: int) -> Dict[str, Any]:
        """Generate batch files using enhanced multiprocessing."""
        batch_start_time = time.time()
        
        # Use parallel processing for batches with 5+ files, but limit concurrent workers
        if not self.use_multiprocessing or batch_files < 5:
            self.generation_stats['sequential_batches'] += 1
            return self._generate_batch_sequential(batch_files, formats, topics, 
                                                 credential_types, regex_db, output_dir, batch_start)
        
        # Limit concurrent workers to avoid memory issues
        max_concurrent_workers = min(self.max_workers, 4)  # Cap at 4 concurrent workers
        
        self.generation_stats['parallel_batches'] += 1
        files = []
        errors = []
        
        # Create tasks for parallel processing
        tasks = []
        for i in range(batch_files):
            file_format = random.choice(formats)
            topic = random.choice(topics)
            credential_type = random.choice(credential_types)
            
            tasks.append({
                'file_format': file_format,
                'topic': topic,
                'credential_type': credential_type,
                'file_index': batch_start + i,
                'output_dir': str(output_dir),
                'regex_db_path': self.config.get('regex_db_path', './data/regex_db.json'),
                'language': self.config.get('language', 'en'),
                'enable_parallel_llm': self.enable_parallel_llm,
                'llm_model_path': self.llm.model_path if self.llm else None
            })
        
        # Process tasks in parallel with enhanced error handling
        try:
            with ProcessPoolExecutor(max_workers=max_concurrent_workers) as executor:
                future_to_task = {
                    executor.submit(self._generate_single_file_worker, task): task 
                    for task in tasks
                }
                
                completed_count = 0
                for future in as_completed(future_to_task, timeout=600):  # 10 minute timeout for entire batch
                    task = future_to_task[future]
                    try:
                        result = future.result(timeout=300)  # 5 minute timeout per file
                        if result['success']:
                            files.append(result['file'])
                            # Update credential stats
                            if 'credentials_count' in result:
                                self.generation_stats['total_credentials'] += result['credentials_count']
                                cred_type = result.get('credential_type', 'unknown')
                                self.generation_stats['credentials_by_type'][cred_type] = \
                                    self.generation_stats['credentials_by_type'].get(cred_type, 0) + result['credentials_count']
                        else:
                            errors.append(f"File {task['file_index']}: {result['error']}")
                        
                        completed_count += 1
                        
                        # Progress logging
                        if completed_count % 5 == 0:
                            self.logger.info(f"Completed {completed_count}/{batch_files} files in parallel batch")
                            
                    except Exception as e:
                        errors.append(f"File {task['file_index']}: {e}")
                        completed_count += 1
                        
        except Exception as e:
            self.logger.error(f"Multiprocessing failed, falling back to sequential: {e}")
            return self._generate_batch_sequential(batch_files, formats, topics, 
                                                 credential_types, regex_db, output_dir, batch_start)
        
        # Update batch timing stats
        batch_time = time.time() - batch_start_time
        self.batch_times.append(batch_time)
        self.generation_stats['total_batches'] += 1
        
        # Calculate average batch time
        if self.batch_times:
            self.generation_stats['avg_batch_time'] = sum(self.batch_times) / len(self.batch_times)
        
        # Keep only last 50 batch times
        if len(self.batch_times) > 50:
            self.batch_times = self.batch_times[-50:]
        
        self.logger.info(f"Parallel batch completed: {len(files)} files in {batch_time:.2f}s")
        
        return {'files': files, 'errors': errors}
    
    @staticmethod
    def _generate_single_file_worker(task: Dict[str, Any]) -> Dict[str, Any]:
        """Worker function for multiprocessing file generation."""
        try:
            # Import here to avoid issues with multiprocessing
            from ..generators.credential_generator import CredentialGenerator
            from ..generators.topic_generator import TopicGenerator
            from ..synthesizers.format_synthesizer import FormatSynthesizer
            from ..synthesizers.eml_format_synthesizer import EMLFormatSynthesizer
            from ..synthesizers.msg_format_synthesizer import MSGFormatSynthesizer
            from ..synthesizers.excel_format_synthesizer import ExcelFormatSynthesizer
            from ..synthesizers.word_format_synthesizer import WordFormatSynthesizer, RTFFormatSynthesizer
            from ..synthesizers.pptx_format_synthesizer import PPTXFormatSynthesizer
            from ..synthesizers.opendocument_format_synthesizer import OpenDocumentFormatSynthesizer
            from ..synthesizers.pdf_format_synthesizer import PDFFormatSynthesizer
            from ..synthesizers.image_format_synthesizer import ImageFormatSynthesizer
            from ..synthesizers.visio_format_synthesizer import VisioFormatSynthesizer
            from ..db.regex_db import RegexDatabase
            from pathlib import Path
            import time
            
            # Initialize components in worker process
            regex_db = RegexDatabase(task.get('regex_db_path', './data/regex_db.json'))
            from ..utils.prompt_system import EnhancedPromptSystem
            prompt_system = EnhancedPromptSystem()
            
            # Initialize LLM interface in worker process if model path is available
            llm_interface = None
            if 'llm_model_path' in task and task['llm_model_path']:
                try:
                    # Add a small delay to avoid concurrent model loading
                    import random
                    time.sleep(random.uniform(0.1, 0.5))
                    
                    from ..llm.llama_interface import LlamaInterface
                    # Use minimal settings for worker processes to avoid memory issues
                    llm_interface = LlamaInterface(
                        task['llm_model_path'],
                        n_threads=2,  # Reduced threads for worker processes
                        n_ctx=1024,   # Reduced context for worker processes
                        n_batch=128   # Reduced batch size for worker processes
                    )
                except Exception as e:
                    print(f"Warning: Failed to initialize LLM in worker process: {e}")
                    llm_interface = None
            
            credential_generator = CredentialGenerator(regex_db=regex_db)
            topic_generator = TopicGenerator()
            
            # Log successful initialization
            print(f"DEBUG: CredentialGenerator agent initialized successfully with LLM interface and prompt system")
            
            synthesizers = {
                # Email formats
                'eml': EMLFormatSynthesizer(str(task['output_dir'])),
                'msg': MSGFormatSynthesizer(str(task['output_dir'])),
                
                # Excel formats
                'xlsm': ExcelFormatSynthesizer(str(task['output_dir']), 'xlsm'),
                'xlsx': ExcelFormatSynthesizer(str(task['output_dir']), 'xlsx'),
                'xltm': ExcelFormatSynthesizer(str(task['output_dir']), 'xltm'),
                'xls': ExcelFormatSynthesizer(str(task['output_dir']), 'xls'),
                'xlsb': ExcelFormatSynthesizer(str(task['output_dir']), 'xlsb'),
                
                # Word formats
                'docx': WordFormatSynthesizer(str(task['output_dir']), 'docx'),
                'doc': WordFormatSynthesizer(str(task['output_dir']), 'doc'),
                'docm': WordFormatSynthesizer(str(task['output_dir']), 'docm'),
                'rtf': RTFFormatSynthesizer(str(task['output_dir'])),
                
                # PowerPoint formats
                'pptx': PPTXFormatSynthesizer(str(task['output_dir'])),
                'ppt': PPTXFormatSynthesizer(str(task['output_dir'])),
                
                # OpenDocument formats
                'odf': OpenDocumentFormatSynthesizer(str(task['output_dir']), 'odf'),
                'ods': OpenDocumentFormatSynthesizer(str(task['output_dir']), 'ods'),
                'odp': OpenDocumentFormatSynthesizer(str(task['output_dir']), 'odp'),
                
                # PDF format
                'pdf': PDFFormatSynthesizer(str(task['output_dir'])),
                
                # Image formats
                'png': ImageFormatSynthesizer(str(task['output_dir']), 'png'),
                'jpg': ImageFormatSynthesizer(str(task['output_dir']), 'jpg'),
                'jpeg': ImageFormatSynthesizer(str(task['output_dir']), 'jpeg'),
                'bmp': ImageFormatSynthesizer(str(task['output_dir']), 'bmp'),
                
                # Visio formats
                'vsd': VisioFormatSynthesizer(str(task['output_dir']), 'vsd'),
                'vsdx': VisioFormatSynthesizer(str(task['output_dir']), 'vsdx'),
                'vsdm': VisioFormatSynthesizer(str(task['output_dir']), 'vsdm'),
                'vssx': VisioFormatSynthesizer(str(task['output_dir']), 'vssx'),
                'vssm': VisioFormatSynthesizer(str(task['output_dir']), 'vssm'),
                'vstx': VisioFormatSynthesizer(str(task['output_dir']), 'vstx'),
                'vstm': VisioFormatSynthesizer(str(task['output_dir']), 'vstm')
            }
            
            # Initialize content generation agent
            from ..agents.content_generation_agent import ContentGenerationAgent
            content_agent = ContentGenerationAgent(
                llm_interface=llm_interface,  # Use the LLM interface we initialized (may be None)
                language_mapper=None,
                regex_db=regex_db
            )
            
            # Generate all content using the content generation agent
            content_data = content_agent.generate_content(
                topic=task['topic'],
                credential_types=[task['credential_type']],
                language=task.get('language', 'en'),
                format_type=task['file_format'],
                context={
                    'file_index': task['file_index'],
                    'generation_timestamp': time.time(),
                    'min_credentials_per_file': 1,
                    'max_credentials_per_file': 1
                }
            )
            
            # Debug: Log credential generation
            if 'credentials' in content_data and content_data['credentials']:
                for cred in content_data['credentials']:
                    print(f"DEBUG: Generated {cred.get('type', 'unknown')} credential: {cred.get('value', 'N/A')}")
            
            # Generate file
            synthesizer = synthesizers.get(task['file_format'])
            if not synthesizer:
                return {'success': False, 'error': f'Unsupported format: {task["file_format"]}'}
            
            file_path = synthesizer.synthesize(content_data)
            
            return {
                'success': True, 
                'file': {
                    'path': str(file_path),
                    'format': task['file_format'],
                    'topic': task['topic'],
                    'credential_type': task['credential_type']
                },
                'credentials_count': 1,
                'credential_type': task['credential_type']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_batch_sequential(self, batch_files: int, formats: List[str], 
                                  topics: List[str], credential_types: List[str],
                                  regex_db: RegexDatabase, output_dir: Path, 
                                  batch_start: int) -> Dict[str, Any]:
        """Generate batch files sequentially (fallback method)."""
        files = []
        errors = []
        
        for i in range(batch_files):
            try:
                self.logger.info(f"Processing file {i+1}/{batch_files}")
                file_format = random.choice(formats)
                topic = random.choice(topics)
                credential_type = random.choice(credential_types)
                self.logger.info(f"Selected: format={file_format}, topic={topic}, credential_type={credential_type}")
                
                # Generate credential with proper context
                context = {
                    'company': 'TechCorp',
                    'topic': topic,
                    'language': self.config.get('language', 'en')
                }
                
                try:
                    credential = self.credential_generator.generate_credential(
                        credential_type, 
                        context
                    )
                except Exception as cred_error:
                    self.logger.warning(f"Credential generation failed for {credential_type}: {cred_error}")
                    # Use a fallback credential for this file
                    credential = f"fallback_{credential_type}_{i}"
                
                # Update generation stats
                self.generation_stats['total_credentials'] += 1
                self.generation_stats['credentials_by_type'][credential_type] = \
                    self.generation_stats['credentials_by_type'].get(credential_type, 0) + 1
                
                # Ensure content generation agent is initialized
                if not self.content_generation_agent:
                    self._initialize_content_generation_agent()
                
                if not self.content_generation_agent:
                    errors.append(f"Content generation agent could not be initialized")
                    continue
                
                # Generate content using new architecture
                self.logger.info(f"Generating content for {file_format} file...")
                # Handle both single language (string) and multiple languages (list)
                language_config = self.config.get('language', 'en')
                if isinstance(language_config, list):
                    # Multiple languages selected - pick one randomly for this file
                    language = random.choice(language_config)
                else:
                    # Single language or None (for random selection)
                    language = language_config or 'en'
                
                content_data = self.content_generation_agent.generate_content(
                    topic=topic,
                    credential_types=[credential_type],
                    language=language,
                    format_type=file_format,
                    context={
                        'file_index': batch_start + i,
                        'generation_timestamp': time.time(),
                        'min_credentials_per_file': self.config.get('min_credentials_per_file', 1),
                        'max_credentials_per_file': self.config.get('max_credentials_per_file', 3)
                    }
                )
                self.logger.info(f"Content generated successfully")
                
                # Generate file using format synthesizer
                format_key = f"{file_format}_format"
                synthesizer = self.format_synthesizers.get(format_key)
                if not synthesizer:
                    errors.append(f"Unsupported format: {file_format}")
                    continue
                
                output_path = output_dir / f"{file_format}_{topic.replace(' ', '_')}_{batch_start + i}.{file_format}"
                
                file_path = synthesizer.synthesize(content_data)
                
                files.append({
                    'path': str(file_path),
                    'format': file_format,
                    'topic': topic,
                    'credential_type': credential_type
                })
                
            except Exception as e:
                errors.append(f"File {batch_start + i}: {e}")
        
        return {'files': files, 'errors': errors}
    
    def _generate_batch(self, num_files: int, formats: List[str]) -> Dict[str, Any]:
        """Generate a batch of files.
        
        Args:
            num_files: Number of files in batch
            formats: List of file formats
            
        Returns:
            Dictionary with generated files and errors
        """
        files = []
        errors = []
        
        # Use parallel processing for batch generation
        with ThreadPoolExecutor(max_workers=min(num_files, 4)) as executor:
            futures = []
            
            for i in range(num_files):
                # Select random format
                format_name = random.choice(formats)
                
                # Submit generation task
                future = executor.submit(self._generate_single_file, format_name, i)
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result['success']:
                        files.append(result['file_path'])
                        self.generation_stats['total_files'] += 1
                        self.generation_stats['files_by_format'][result['format']] = \
                            self.generation_stats['files_by_format'].get(result['format'], 0) + 1
                    else:
                        errors.append(result['error'])
                        self.generation_stats['total_errors'] += 1
                except Exception as e:
                    errors.append(str(e))
                    self.generation_stats['total_errors'] += 1
        
        return {'files': files, 'errors': errors}
    
    def _generate_single_file(self, format_name: str, file_index: int) -> Dict[str, Any]:
        """Generate a single file.
        
        Args:
            format_name: File format
            file_index: File index for uniqueness
            
        Returns:
            Dictionary with generation result
        """
        try:
            # Get format synthesizer
            format_key = f"{format_name}_format"
            if format_key not in self.format_synthesizers:
                raise GenerationError(f"Unsupported format: {format_name}")
            
            synthesizer = self.format_synthesizers[format_key]
            
            # Generate topic content (support multiple topics)
            topics = self.config.get('topics', [])
            
            # Safety check for empty topics
            if not topics or (isinstance(topics, list) and len(topics) == 0):
                # Fallback topics
                topics = [
                    "system documentation",
                    "security configuration", 
                    "API integration guide",
                    "database setup",
                    "network configuration"
                ]
                self.logger.warning("No topics provided, using fallback topics")
            
            if isinstance(topics, list) and len(topics) > 1:
                # Select 1-3 topics randomly for this file
                num_topics = random.randint(1, min(3, len(topics)))
                selected_topics = random.sample(topics, num_topics)
                topic = ', '.join(selected_topics)
            else:
                topic = random.choice(topics) if isinstance(topics, list) else topics
            
            # Ensure content generation agent is initialized
            if not self.content_generation_agent:
                self._initialize_content_generation_agent()
            
            if not self.content_generation_agent:
                raise GenerationError("Content generation agent could not be initialized")
            
            # Generate content using the new ContentGenerationAgent
            credential_types = self.config['credential_types']
            language_config = self.config.get('language', 'en')
            
            # Handle both single language (string) and multiple languages (list)
            if isinstance(language_config, list):
                # Multiple languages selected - pick one randomly for this file
                language = random.choice(language_config)
            else:
                # Single language or None (for random selection)
                language = language_config or 'en'
            
            # Generate all content (topic-based content + credentials) using the new agent
            content_data = self.content_generation_agent.generate_content(
                topic=topic,
                credential_types=credential_types,
                language=language,
                format_type=format_name,
                context={
                    'file_index': file_index,
                    'generation_timestamp': time.time(),
                    'unique_seed': file_index + int(time.time() * 1000) % 10000,
                    'min_credentials_per_file': self.config.get('min_credentials_per_file', 1),
                    'max_credentials_per_file': self.config.get('max_credentials_per_file', 3)
                }
            )
            
            # Extract generated content
            topic_content = content_data['sections']
            credentials = content_data['credentials']
            actual_credential_types = [cred['type'] for cred in credentials]
            
            # Update generation stats
            for cred in credentials:
                cred_type = cred['type']
                self.generation_stats['total_credentials'] += 1
                self.generation_stats['credentials_by_type'][cred_type] = \
                    self.generation_stats['credentials_by_type'].get(cred_type, 0) + 1
            
            # Determine embedding strategy (simplified)
            embed_strategy = self.config.get('embed_strategy', 'random')
            
            # Create metadata
            metadata = {
                'topic': topic,
                'format': format_name,
                'file_index': file_index,
                'credential_types': actual_credential_types,  # Use actual types used
                'embed_strategy': embed_strategy,
                'language': self.config.get('language', 'en')
            }
            
            # Generate file using the new format synthesizer
            file_path = synthesizer.synthesize(content_data)
            
            return {
                'success': True,
                'file_path': file_path,
                'format': format_name,
                'topic': topic,
                'credentials_count': len(credentials)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'format': format_name,
                'file_index': file_index
            }
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics.
        
        Returns:
            Dictionary with generation statistics
        """
        return self.generation_stats.copy()
    
    def clear_stats(self) -> None:
        """Clear generation statistics."""
        self.generation_stats = {
            'total_files': 0,
            'total_credentials': 0,
            'total_errors': 0,
            'generation_time': 0,
            'files_by_format': {},
            'credentials_by_type': {},
            'parallel_batches': 0,
            'sequential_batches': 0,
            'memory_cleanups': 0,
            'avg_batch_time': 0.0,
            'total_batches': 0
        }
        self.batch_times = []
        self.memory_usage_history = []
