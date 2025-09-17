"""Content Generation Agent for unified content creation."""

import random
import time
import threading
import multiprocessing as mp
from typing import Dict, List, Optional, Any
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from ..utils.exceptions import GenerationError
from ..utils.language_content_generator import LanguageContentGenerator
from ..utils.prompt_system import EnhancedPromptSystem
from ..generators.credential_generator import CredentialGenerator
from ..db.regex_db import RegexDatabase


# Helper functions for multiprocessing (must be at module level to be picklable)
def _generate_sections_worker(topic: str, language: str, format_type: str, section_names: List[str]) -> List[Dict[str, str]]:
    """Worker function for generating sections in parallel."""
    # Create a temporary agent instance for this worker with regex database
    from ..db.regex_db import RegexDatabase
    regex_db = RegexDatabase('./data/regex_db.json')
    temp_agent = ContentGenerationAgent(
        regex_db=regex_db,
        enable_parallel_generation=False,
        use_multiprocessing=False
    )
    return temp_agent._generate_sections(topic, language, format_type, section_names)


def _generate_credentials_worker(credential_types: List[str], language: str, min_creds: int, max_creds: int, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    """Worker function for generating credentials in parallel."""
    # Create a temporary agent instance for this worker with regex database
    from ..db.regex_db import RegexDatabase
    regex_db = RegexDatabase('./data/regex_db.json')
    temp_agent = ContentGenerationAgent(
        regex_db=regex_db,
        enable_parallel_generation=False,
        use_multiprocessing=False
    )
    return temp_agent._generate_credentials_with_labels(credential_types, language, min_creds, max_creds, context)


def _generate_metadata_worker(topic: str, language: str, format_type: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Worker function for generating metadata in parallel."""
    # Create a temporary agent instance for this worker with regex database
    from ..db.regex_db import RegexDatabase
    regex_db = RegexDatabase('./data/regex_db.json')
    temp_agent = ContentGenerationAgent(
        regex_db=regex_db,
        enable_parallel_generation=False,
        use_multiprocessing=False
    )
    return temp_agent._generate_metadata(topic, language, format_type, context)


class ContentGenerationAgent:
    """AI agent responsible for generating all content needed for documents."""
    
    def __init__(self, llm_interface=None, language_mapper=None, regex_db=None, 
                 enable_parallel_generation=True, max_parallel_workers=None,
                 use_llm_for_credentials=False, use_llm_for_content=False, 
                 multi_model_manager=None, use_multiprocessing=True):
        """Initialize content generation agent.
        
        Args:
            llm_interface: LLM interface for content generation (single model)
            language_mapper: Language mapper for company/language coordination
            regex_db: RegexDatabase instance for credential generation
            enable_parallel_generation: Enable parallel content generation
            max_parallel_workers: Maximum number of parallel workers (defaults to CPU count)
            use_llm_for_credentials: Use LLM for credential generation (slower but more realistic)
            use_llm_for_content: Use LLM for content generation (titles, sections, metadata) - slower but more realistic
            multi_model_manager: MultiModelManager for task-specific models
            use_multiprocessing: Use multiprocessing instead of threading for better CPU performance
        """
        self.llm = llm_interface
        self.multi_model_manager = multi_model_manager
        self.language_mapper = language_mapper
        self.language_content_generator = LanguageContentGenerator()
        self.prompt_system = EnhancedPromptSystem()
        self.enable_parallel_generation = enable_parallel_generation
        self.use_multiprocessing = use_multiprocessing
        self.use_llm_for_content = use_llm_for_content
        
        # Set default max workers to CPU count if not specified
        if max_parallel_workers is None:
            self.max_parallel_workers = mp.cpu_count()
        else:
            self.max_parallel_workers = max_parallel_workers
        
        # Ultra-fast mode optimizations
        self.ultra_fast_mode = not use_llm_for_content and not use_llm_for_credentials
        self._company_cache = {}  # Cache companies by language
        self._template_cache = {}  # Cache generated templates
        
        # Initialize credential generator from regex database (simplified)
        # Use fast fallback mode by default for better performance
        self.credential_generator = None
        if regex_db:
            try:
                self.credential_generator = CredentialGenerator(regex_db=regex_db)
                print(f"DEBUG: CredentialGenerator initialized successfully with fast fallback mode")
            except Exception as e:
                print(f"Warning: Failed to initialize CredentialGenerator: {e}")
                self.credential_generator = None
        
        # Process/Thread pool for parallel content generation
        self.executor_pool = None
        if self.enable_parallel_generation:
            if self.use_multiprocessing:
                # Use multiprocessing for CPU-intensive tasks
                self.executor_pool = ProcessPoolExecutor(max_workers=self.max_parallel_workers)
                print(f"DEBUG: Initialized ProcessPoolExecutor with {self.max_parallel_workers} workers")
            else:
                # Use threading for I/O-intensive tasks
                self.executor_pool = ThreadPoolExecutor(max_workers=self.max_parallel_workers)
                print(f"DEBUG: Initialized ThreadPoolExecutor with {self.max_parallel_workers} workers")
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Performance tracking
        self.generation_stats = {
            'total_generations': 0,
            'parallel_generations': 0,
            'sequential_generations': 0,
            'multiprocessing_generations': 0,
            'threading_generations': 0,
            'avg_generation_time': 0.0,
            'total_generation_time': 0.0,
            'max_workers': self.max_parallel_workers,
            'executor_type': 'multiprocessing' if self.use_multiprocessing else 'threading'
        }
        
        # Content templates for different formats
        self.format_templates = {
            # Email formats
            'eml': {
                'sections': ['subject', 'greeting', 'body', 'closing', 'signature'],
                'structure': 'email'
            },
            'msg': {
                'sections': ['subject', 'greeting', 'body', 'closing', 'signature'],
                'structure': 'email'
            },
            
            # Presentation formats
            'pptx': {
                'sections': ['title', 'overview', 'technical_details', 'configuration', 'implementation', 'security'],
                'structure': 'presentation'
            },
            'ppt': {
                'sections': ['title', 'overview', 'technical_details', 'configuration', 'implementation', 'security'],
                'structure': 'presentation'
            },
            'odp': {
                'sections': ['title', 'overview', 'technical_details', 'configuration', 'implementation', 'security'],
                'structure': 'presentation'
            },
            
            # Document formats
            'pdf': {
                'sections': ['title', 'executive_summary', 'technical_specifications', 'implementation_plan', 'security_considerations'],
                'structure': 'document'
            },
            'docx': {
                'sections': ['title', 'introduction', 'technical_details', 'configuration', 'implementation', 'conclusion'],
                'structure': 'document'
            },
            'doc': {
                'sections': ['title', 'introduction', 'technical_details', 'configuration', 'implementation', 'conclusion'],
                'structure': 'document'
            },
            'rtf': {
                'sections': ['title', 'introduction', 'technical_details', 'configuration', 'implementation', 'conclusion'],
                'structure': 'document'
            },
            'odt': {
                'sections': ['title', 'introduction', 'technical_details', 'configuration', 'implementation', 'conclusion'],
                'structure': 'document'
            },
            
            # Spreadsheet formats
            'xlsx': {
                'sections': ['data_sheet', 'configuration_sheet', 'credentials_sheet'],
                'structure': 'spreadsheet'
            },
            'xls': {
                'sections': ['data_sheet', 'configuration_sheet', 'credentials_sheet'],
                'structure': 'spreadsheet'
            },
            'xlsm': {
                'sections': ['data_sheet', 'configuration_sheet', 'credentials_sheet'],
                'structure': 'spreadsheet'
            },
            'xlsb': {
                'sections': ['data_sheet', 'configuration_sheet', 'credentials_sheet'],
                'structure': 'spreadsheet'
            },
            'ods': {
                'sections': ['data_sheet', 'configuration_sheet', 'credentials_sheet'],
                'structure': 'spreadsheet'
            },
            
            # Image formats
            'png': {
                'sections': ['title', 'description', 'technical_details'],
                'structure': 'image'
            },
            'jpg': {
                'sections': ['title', 'description', 'technical_details'],
                'structure': 'image'
            },
            'jpeg': {
                'sections': ['title', 'description', 'technical_details'],
                'structure': 'image'
            },
            'bmp': {
                'sections': ['title', 'description', 'technical_details'],
                'structure': 'image'
            },
            
            # Diagram formats
            'vsdx': {
                'sections': ['title', 'overview', 'technical_architecture', 'configuration', 'implementation'],
                'structure': 'diagram'
            },
            'vsd': {
                'sections': ['title', 'overview', 'technical_architecture', 'configuration', 'implementation'],
                'structure': 'diagram'
            }
        }
    
    def generate_content(self, 
                        topic: str,
                        credential_types: List[str],
                        language: str,
                        format_type: str,
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate all content needed for a document.
        
        Args:
            topic: Document topic
            credential_types: List of credential types to generate
            language: Target language
            format_type: File format (eml, pptx, pdf, xlsx)
            context: Additional context for generation
            
        Returns:
            Dictionary with all generated content
        """
        start_time = time.time()
        
        try:
            # Select a consistent company for the entire document
            company_info = self._get_cached_company(language)
            if context is None:
                context = {}
            context['company'] = company_info['name']
            context['company_info'] = company_info
            
            # Skip validation in ultra-fast mode
            if not self.ultra_fast_mode:
                self._validate_generation_requirements(topic, credential_types, language, format_type)
            
            # Get format template
            template = self.format_templates.get(format_type, self.format_templates['pdf'])
            
            # Use ultra-fast generation if in ultra-fast mode
            if self.ultra_fast_mode:
                content_data = self._generate_ultra_fast_content(topic, language, format_type, template, credential_types, context)
            # Use parallel generation if enabled and multiple sections
            elif self.enable_parallel_generation and len(template['sections']) > 2:
                content_data = self._generate_content_parallel(topic, language, format_type, template, credential_types, context)
            else:
                content_data = self._generate_content_sequential(topic, language, format_type, template, credential_types, context)
            
            # Update performance stats
            generation_time = time.time() - start_time
            self._update_generation_stats(generation_time, parallel=len(template['sections']) > 2)
            
            return content_data
            
        except Exception as e:
            raise GenerationError(f"Content generation failed: {e}")
    
    def _generate_content_parallel(self, topic: str, language: str, format_type: str, 
                                 template: Dict, credential_types: List[str], 
                                 context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate content using parallel processing (multiprocessing or threading)."""
        if not self.executor_pool:
            return self._generate_content_sequential(topic, language, format_type, template, credential_types, context)
        
        try:
            # Generate title first (quick operation)
            title = self._generate_title(topic, language, format_type, context)
            
            # Prepare parallel tasks
            tasks = []
            
            # Task 1: Generate sections
            if self.use_multiprocessing:
                sections_task = self.executor_pool.submit(
                    _generate_sections_worker, topic, language, format_type, template['sections']
                )
            else:
                sections_task = self.executor_pool.submit(
                    self._generate_sections, topic, language, format_type, template['sections'], context
                )
            tasks.append(('sections', sections_task))
            
            # Task 2: Generate credentials
            min_creds = context.get('min_credentials_per_file', 1) if context else 1
            max_creds = context.get('max_credentials_per_file', 3) if context else 3
            if self.use_multiprocessing:
                credentials_task = self.executor_pool.submit(
                    _generate_credentials_worker, credential_types, language, min_creds, max_creds, context
                )
            else:
                credentials_task = self.executor_pool.submit(
                    self._generate_credentials_with_labels, credential_types, language, min_creds, max_creds, context
                )
            tasks.append(('credentials', credentials_task))
            
            # Task 3: Generate metadata
            if self.use_multiprocessing:
                metadata_task = self.executor_pool.submit(
                    _generate_metadata_worker, topic, language, format_type, context
                )
            else:
                metadata_task = self.executor_pool.submit(
                    self._generate_metadata, topic, language, format_type, context
                )
            tasks.append(('metadata', metadata_task))
            
            # Collect results
            results = {}
            for task_name, future in tasks:
                try:
                    results[task_name] = future.result(timeout=120)  # 2 minute timeout per task
                except Exception as e:
                    print(f"Parallel task {task_name} failed: {e}")
                    # Fallback to sequential generation for failed task
                    if task_name == 'sections':
                        results[task_name] = self._generate_sections(topic, language, format_type, template['sections'], context)
                    elif task_name == 'credentials':
                        results[task_name] = self._generate_credentials_with_labels(credential_types, language, min_creds, max_creds, context)
                    elif task_name == 'metadata':
                        results[task_name] = self._generate_metadata(topic, language, format_type, context)
            
            return {
                'title': title,
                'sections': results['sections'],
                'credentials': results['credentials'],
                'metadata': results['metadata'],
                'format_type': format_type,
                'language': language,
                'context': context
            }
            
        except Exception as e:
            print(f"Parallel generation failed, falling back to sequential: {e}")
            return self._generate_content_sequential(topic, language, format_type, template, credential_types, context)
    
    def _generate_content_sequential(self, topic: str, language: str, format_type: str, 
                                   template: Dict, credential_types: List[str], 
                                   context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate content using sequential processing."""
        # Generate document title
        title = self._generate_title(topic, language, format_type, context)
        
        # Generate sections based on format
        sections = self._generate_sections(topic, language, format_type, template['sections'], context)
        
        # Generate credentials with proper labels and count limits
        min_creds = context.get('min_credentials_per_file', 1) if context else 1
        max_creds = context.get('max_credentials_per_file', 3) if context else 3
        credentials = self._generate_credentials_with_labels(credential_types, language, min_creds, max_creds, context)
        
        # Embed credentials into section content
        sections = self._embed_credentials_into_sections(sections, credentials, language)
        
        # Generate metadata
        metadata = self._generate_metadata(topic, language, format_type, context)
        
        return {
            'title': title,
            'sections': sections,
            'credentials': credentials,
            'metadata': metadata,
            'format_type': format_type,
            'language': language,
            'context': context
        }
    
    def _update_generation_stats(self, generation_time: float, parallel: bool = False) -> None:
        """Update generation statistics."""
        with self._lock:
            self.generation_stats['total_generations'] += 1
            self.generation_stats['total_generation_time'] += generation_time
            
            if parallel:
                self.generation_stats['parallel_generations'] += 1
                if self.use_multiprocessing:
                    self.generation_stats['multiprocessing_generations'] += 1
                else:
                    self.generation_stats['threading_generations'] += 1
            else:
                self.generation_stats['sequential_generations'] += 1
            
            # Update average generation time
            total_gens = self.generation_stats['total_generations']
            self.generation_stats['avg_generation_time'] = (
                self.generation_stats['total_generation_time'] / total_gens
            )
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics."""
        with self._lock:
            return self.generation_stats.copy()
    
    def reset_generation_stats(self) -> None:
        """Reset generation statistics."""
        with self._lock:
            self.generation_stats = {
                'total_generations': 0,
                'parallel_generations': 0,
                'sequential_generations': 0,
                'multiprocessing_generations': 0,
                'threading_generations': 0,
                'avg_generation_time': 0.0,
                'total_generation_time': 0.0,
                'max_workers': self.max_parallel_workers,
                'executor_type': 'multiprocessing' if self.use_multiprocessing else 'threading'
            }
    
    def _validate_generation_requirements(self, topic: str, credential_types: List[str], language: str, format_type: str) -> None:
        """Validate and log generation requirements with enhanced prompt system."""
        if self.llm and self.use_llm_for_content:
            # Get a random company that matches the language
            company_info = self.prompt_system.get_random_company(language)
            
            # Create enhanced validation prompt with company context
            validation_prompt = self.prompt_system.create_enhanced_validation_prompt(
                topic=topic,
                credential_types=credential_types,
                language=language,
                format_type=format_type,
                company=company_info['name']
            )
            
            try:
                # Send validation prompt to ensure LLM understands requirements
                self.llm.generate(validation_prompt, max_tokens=20, temperature=0.1)
            except Exception:
                pass  # Continue with generation even if validation fails
    
    def _generate_title(self, topic: str, language: str, format_type: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate document title based on topic and language."""
        if self.llm and self.use_llm_for_content:
            # Use company from context if available, otherwise get a random one
            if context and 'company_info' in context:
                company_info = context['company_info']
            else:
                company_info = self.prompt_system.get_random_company(language)
            
            # Use enhanced prompt system for title generation
            prompt = self.prompt_system.create_enhanced_title_prompt(
                topic=topic,
                language=language,
                format_type=format_type,
                company=company_info['name']
            )
            try:
                title = self.llm.generate(prompt, max_tokens=50, temperature=0.7)
                if title and title.strip():
                    # Clean the title to remove any template instructions
                    cleaned_title = self._clean_generated_content(title.strip())
                    if cleaned_title:
                        return cleaned_title
            except Exception as e:
                print(f"LLM title generation failed: {e}")
        
        # Template-based title generation
        title_templates = {
            'en': {
                'eml': f"System Update: {topic}",
                'msg': f"System Update: {topic}",
                'pptx': f"{topic} - Technical Overview",
                'ppt': f"{topic} - Technical Overview",
                'odp': f"{topic} - Technical Overview",
                'pdf': f"{topic} - Implementation Guide",
                'docx': f"{topic} - Technical Documentation",
                'doc': f"{topic} - Technical Documentation",
                'rtf': f"{topic} - Technical Documentation",
                'odt': f"{topic} - Technical Documentation",
                'xlsx': f"{topic} - Configuration Data",
                'xls': f"{topic} - Configuration Data",
                'xlsm': f"{topic} - Configuration Data",
                'xlsb': f"{topic} - Configuration Data",
                'ods': f"{topic} - Configuration Data",
                'png': f"{topic} - Technical Diagram",
                'jpg': f"{topic} - Technical Diagram",
                'jpeg': f"{topic} - Technical Diagram",
                'bmp': f"{topic} - Technical Diagram",
                'vsdx': f"{topic} - System Architecture",
                'vsd': f"{topic} - System Architecture"
            },
            'fr': {
                'eml': f"Mise à jour système : {topic}",
                'msg': f"Mise à jour système : {topic}",
                'pptx': f"{topic} - Aperçu technique",
                'ppt': f"{topic} - Aperçu technique",
                'odp': f"{topic} - Aperçu technique",
                'pdf': f"{topic} - Guide d'implémentation",
                'docx': f"{topic} - Documentation technique",
                'doc': f"{topic} - Documentation technique",
                'rtf': f"{topic} - Documentation technique",
                'odt': f"{topic} - Documentation technique",
                'xlsx': f"{topic} - Données de configuration",
                'xls': f"{topic} - Données de configuration",
                'xlsm': f"{topic} - Données de configuration",
                'xlsb': f"{topic} - Données de configuration",
                'ods': f"{topic} - Données de configuration",
                'png': f"{topic} - Schéma technique",
                'jpg': f"{topic} - Schéma technique",
                'jpeg': f"{topic} - Schéma technique",
                'bmp': f"{topic} - Schéma technique",
                'vsdx': f"{topic} - Architecture système",
                'vsd': f"{topic} - Architecture système"
            },
            'es': {
                'eml': f"Actualización del sistema: {topic}",
                'msg': f"Actualización del sistema: {topic}",
                'pptx': f"{topic} - Resumen técnico",
                'ppt': f"{topic} - Resumen técnico",
                'odp': f"{topic} - Resumen técnico",
                'pdf': f"{topic} - Guía de implementación",
                'docx': f"{topic} - Documentación técnica",
                'doc': f"{topic} - Documentación técnica",
                'rtf': f"{topic} - Documentación técnica",
                'odt': f"{topic} - Documentación técnica",
                'xlsx': f"{topic} - Datos de configuración",
                'xls': f"{topic} - Datos de configuración",
                'xlsm': f"{topic} - Datos de configuración",
                'xlsb': f"{topic} - Datos de configuración",
                'ods': f"{topic} - Datos de configuración",
                'png': f"{topic} - Diagrama técnico",
                'jpg': f"{topic} - Diagrama técnico",
                'jpeg': f"{topic} - Diagrama técnico",
                'bmp': f"{topic} - Diagrama técnico",
                'vsdx': f"{topic} - Arquitectura del sistema",
                'vsd': f"{topic} - Arquitectura del sistema"
            },
            'de': {
                'eml': f"System-Update: {topic}",
                'msg': f"System-Update: {topic}",
                'pptx': f"{topic} - Technische Übersicht",
                'ppt': f"{topic} - Technische Übersicht",
                'odp': f"{topic} - Technische Übersicht",
                'pdf': f"{topic} - Implementierungsanleitung",
                'docx': f"{topic} - Technische Dokumentation",
                'doc': f"{topic} - Technische Dokumentation",
                'rtf': f"{topic} - Technische Dokumentation",
                'odt': f"{topic} - Technische Dokumentation",
                'xlsx': f"{topic} - Konfigurationsdaten",
                'xls': f"{topic} - Konfigurationsdaten",
                'xlsm': f"{topic} - Konfigurationsdaten",
                'xlsb': f"{topic} - Konfigurationsdaten",
                'ods': f"{topic} - Konfigurationsdaten",
                'png': f"{topic} - Technisches Diagramm",
                'jpg': f"{topic} - Technisches Diagramm",
                'jpeg': f"{topic} - Technisches Diagramm",
                'bmp': f"{topic} - Technisches Diagramm",
                'vsdx': f"{topic} - Systemarchitektur",
                'vsd': f"{topic} - Systemarchitektur"
            },
            'it': {
                'eml': f"Aggiornamento sistema: {topic}",
                'msg': f"Aggiornamento sistema: {topic}",
                'pptx': f"{topic} - Panoramica tecnica",
                'ppt': f"{topic} - Panoramica tecnica",
                'odp': f"{topic} - Panoramica tecnica",
                'pdf': f"{topic} - Guida all'implementazione",
                'docx': f"{topic} - Documentazione tecnica",
                'doc': f"{topic} - Documentazione tecnica",
                'rtf': f"{topic} - Documentazione tecnica",
                'odt': f"{topic} - Documentazione tecnica",
                'xlsx': f"{topic} - Dati di configurazione",
                'xls': f"{topic} - Dati di configurazione",
                'xlsm': f"{topic} - Dati di configurazione",
                'xlsb': f"{topic} - Dati di configurazione",
                'ods': f"{topic} - Dati di configurazione",
                'png': f"{topic} - Diagramma tecnico",
                'jpg': f"{topic} - Diagramma tecnico",
                'jpeg': f"{topic} - Diagramma tecnico",
                'bmp': f"{topic} - Diagramma tecnico",
                'vsdx': f"{topic} - Architettura del sistema",
                'vsd': f"{topic} - Architettura del sistema"
            },
            'pt': {
                'eml': f"Atualização do sistema: {topic}",
                'msg': f"Atualização do sistema: {topic}",
                'pptx': f"{topic} - Visão geral técnica",
                'ppt': f"{topic} - Visão geral técnica",
                'odp': f"{topic} - Visão geral técnica",
                'pdf': f"{topic} - Guia de implementação",
                'docx': f"{topic} - Documentação técnica",
                'doc': f"{topic} - Documentação técnica",
                'rtf': f"{topic} - Documentação técnica",
                'odt': f"{topic} - Documentação técnica",
                'xlsx': f"{topic} - Dados de configuração",
                'xls': f"{topic} - Dados de configuração",
                'xlsm': f"{topic} - Dados de configuração",
                'xlsb': f"{topic} - Dados de configuração",
                'ods': f"{topic} - Dados de configuração",
                'png': f"{topic} - Diagrama técnico",
                'jpg': f"{topic} - Diagrama técnico",
                'jpeg': f"{topic} - Diagrama técnico",
                'bmp': f"{topic} - Diagrama técnico",
                'vsdx': f"{topic} - Arquitetura do sistema",
                'vsd': f"{topic} - Arquitetura do sistema"
            },
            'nl': {
                'eml': f"Systeemupdate: {topic}",
                'msg': f"Systeemupdate: {topic}",
                'pptx': f"{topic} - Technisch overzicht",
                'ppt': f"{topic} - Technisch overzicht",
                'odp': f"{topic} - Technisch overzicht",
                'pdf': f"{topic} - Implementatiegids",
                'docx': f"{topic} - Technische documentatie",
                'doc': f"{topic} - Technische documentatie",
                'rtf': f"{topic} - Technische documentatie",
                'odt': f"{topic} - Technische documentatie",
                'xlsx': f"{topic} - Configuratiegegevens",
                'xls': f"{topic} - Configuratiegegevens",
                'xlsm': f"{topic} - Configuratiegegevens",
                'xlsb': f"{topic} - Configuratiegegevens",
                'ods': f"{topic} - Configuratiegegevens",
                'png': f"{topic} - Technisch diagram",
                'jpg': f"{topic} - Technisch diagram",
                'jpeg': f"{topic} - Technisch diagram",
                'bmp': f"{topic} - Technisch diagram",
                'vsdx': f"{topic} - Systeemarchitectuur",
                'vsd': f"{topic} - Systeemarchitectuur"
            },
            'tr': {
                'eml': f"Sistem güncellemesi: {topic}",
                'msg': f"Sistem güncellemesi: {topic}",
                'pptx': f"{topic} - Teknik genel bakış",
                'ppt': f"{topic} - Teknik genel bakış",
                'odp': f"{topic} - Teknik genel bakış",
                'pdf': f"{topic} - Uygulama kılavuzu",
                'docx': f"{topic} - Teknik dokümantasyon",
                'doc': f"{topic} - Teknik dokümantasyon",
                'rtf': f"{topic} - Teknik dokümantasyon",
                'odt': f"{topic} - Teknik dokümantasyon",
                'xlsx': f"{topic} - Yapılandırma verileri",
                'xls': f"{topic} - Yapılandırma verileri",
                'xlsm': f"{topic} - Yapılandırma verileri",
                'xlsb': f"{topic} - Yapılandırma verileri",
                'ods': f"{topic} - Yapılandırma verileri",
                'png': f"{topic} - Teknik diyagram",
                'jpg': f"{topic} - Teknik diyagram",
                'jpeg': f"{topic} - Teknik diyagram",
                'bmp': f"{topic} - Teknik diyagram",
                'vsdx': f"{topic} - Sistem mimarisi",
                'vsd': f"{topic} - Sistem mimarisi"
            },
            'zh': {
                'eml': f"系统更新：{topic}",
                'msg': f"系统更新：{topic}",
                'pptx': f"{topic} - 技术概述",
                'ppt': f"{topic} - 技术概述",
                'odp': f"{topic} - 技术概述",
                'pdf': f"{topic} - 实施指南",
                'docx': f"{topic} - 技术文档",
                'doc': f"{topic} - 技术文档",
                'rtf': f"{topic} - 技术文档",
                'odt': f"{topic} - 技术文档",
                'xlsx': f"{topic} - 配置数据",
                'xls': f"{topic} - 配置数据",
                'xlsm': f"{topic} - 配置数据",
                'xlsb': f"{topic} - 配置数据",
                'ods': f"{topic} - 配置数据",
                'png': f"{topic} - 技术图表",
                'jpg': f"{topic} - 技术图表",
                'jpeg': f"{topic} - 技术图表",
                'bmp': f"{topic} - 技术图表",
                'vsdx': f"{topic} - 系统架构",
                'vsd': f"{topic} - 系统架构"
            },
            'ja': {
                'eml': f"システム更新：{topic}",
                'msg': f"システム更新：{topic}",
                'pptx': f"{topic} - 技術概要",
                'ppt': f"{topic} - 技術概要",
                'odp': f"{topic} - 技術概要",
                'pdf': f"{topic} - 実装ガイド",
                'docx': f"{topic} - 技術文書",
                'doc': f"{topic} - 技術文書",
                'rtf': f"{topic} - 技術文書",
                'odt': f"{topic} - 技術文書",
                'xlsx': f"{topic} - 設定データ",
                'xls': f"{topic} - 設定データ",
                'xlsm': f"{topic} - 設定データ",
                'xlsb': f"{topic} - 設定データ",
                'ods': f"{topic} - 設定データ",
                'png': f"{topic} - 技術図表",
                'jpg': f"{topic} - 技術図表",
                'jpeg': f"{topic} - 技術図表",
                'bmp': f"{topic} - 技術図表",
                'vsdx': f"{topic} - システムアーキテクチャ",
                'vsd': f"{topic} - システムアーキテクチャ"
            }
        }
        
        return title_templates.get(language, title_templates['en']).get(format_type, f"{topic} - Document")
    
    def _generate_sections(self, topic: str, language: str, format_type: str, section_names: List[str], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Generate content sections based on format and language."""
        sections = []
        
        for section_name in section_names:
            if self.llm and self.use_llm_for_content:
                # Use LLM for section generation
                section_content = self._generate_section_with_llm(topic, section_name, language, format_type, context)
            else:
                # Use template-based generation
                section_content = self._generate_section_template(topic, section_name, language, format_type, context)
            
            sections.append({
                'title': self._get_section_title(section_name, language),
                'content': section_content
            })
        
        return sections
    
    def _generate_section_with_llm(self, topic: str, section_name: str, language: str, format_type: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate section content using LLM with enhanced prompt system."""
        if not self.llm:
            return self._generate_section_template(topic, section_name, language, format_type, context)
            
        # Use company from context if available, otherwise get a random one
        if context and 'company_info' in context:
            company_info = context['company_info']
        else:
            company_info = self.prompt_system.get_random_company(language)
        
        # Use enhanced prompt system for section generation
        prompt = self.prompt_system.create_enhanced_section_prompt(
            topic=topic,
            language=language,
            format_type=format_type,
            section=section_name,
            company=company_info['name']
        )
        
        try:
            content = self.llm.generate(prompt, max_tokens=300, temperature=0.7)
            if content and content.strip():
                # Clean the content to remove any template instructions
                cleaned_content = self._clean_generated_content(content.strip())
                if cleaned_content:
                    return cleaned_content
                else:
                    # Content was all template instructions, fall back to template
                    return self._generate_section_template(topic, section_name, language, format_type, context)
            else:
                # LLM returned empty content, fall back to template
                return self._generate_section_template(topic, section_name, language, format_type, context)
        except Exception as e:
            print(f"LLM generation failed for {section_name}: {e}")
            return self._generate_section_template(topic, section_name, language, format_type, context)
    
    def _generate_section_template(self, topic: str, section_name: str, language: str, format_type: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate section content using templates."""
        # Use company from context if available, otherwise get a random one
        if context and 'company_info' in context:
            company_info = context['company_info']
        else:
            company_info = self.prompt_system.get_random_company(language)
        
        # Generate realistic content based on section type
        if section_name == 'subject':
            return self._generate_subject_content(topic, language, company_info['name'])
        elif section_name == 'greeting':
            return self._generate_greeting_content(language, company_info['name'])
        elif section_name == 'body':
            return self._generate_body_content(topic, language, company_info['name'])
        elif section_name == 'closing':
            return self._generate_closing_content(language, company_info['name'])
        elif section_name == 'signature':
            return self._generate_signature_content(language, company_info['name'])
        else:
            return self._generate_generic_section_content(topic, section_name, language, company_info['name'])
    
    def _generate_subject_content(self, topic: str, language: str, company: str) -> str:
        """Generate realistic email subject content."""
        subjects = {
            'en': f"System Update: {topic} Implementation",
            'fr': f"Mise à jour système : Implémentation {topic}",
            'es': f"Actualización del sistema: Implementación {topic}",
            'de': f"System-Update: {topic} Implementierung",
            'it': f"Aggiornamento sistema: Implementazione {topic}",
            'pt': f"Atualização do sistema: Implementação {topic}",
            'nl': f"Systeemupdate: {topic} Implementatie",
            'tr': f"Sistem güncellemesi: {topic} Uygulaması",
            'zh': f"系统更新：{topic} 实施",
            'ja': f"システム更新：{topic} 実装"
        }
        return subjects.get(language, subjects['en'])
    
    def _generate_greeting_content(self, language: str, company: str) -> str:
        """Generate realistic greeting content."""
        greetings = {
            'en': f"Dear {company} Team,\n\nI hope this message finds you well. I am writing to provide you with important updates regarding our system configuration and security protocols.",
            'fr': f"Chère équipe {company},\n\nJ'espère que ce message vous trouve en bonne santé. Je vous écris pour vous fournir des mises à jour importantes concernant notre configuration système et nos protocoles de sécurité.",
            'es': f"Estimado equipo de {company},\n\nEspero que este mensaje los encuentre bien. Les escribo para proporcionarles actualizaciones importantes sobre nuestra configuración del sistema y protocolos de seguridad.",
            'de': f"Liebes {company} Team,\n\nIch hoffe, diese Nachricht erreicht Sie gut. Ich schreibe Ihnen, um wichtige Updates bezüglich unserer Systemkonfiguration und Sicherheitsprotokolle zu geben.",
            'it': f"Caro team {company},\n\nSpero che questo messaggio vi trovi bene. Vi scrivo per fornirvi aggiornamenti importanti riguardo alla nostra configurazione del sistema e ai protocolli di sicurezza.",
            'pt': f"Caros membros da equipe {company},\n\nEspero que esta mensagem os encontre bem. Escrevo para fornecer atualizações importantes sobre nossa configuração do sistema e protocolos de segurança.",
            'nl': f"Beste {company} team,\n\nIk hoop dat dit bericht u goed bereikt. Ik schrijf om u belangrijke updates te geven over onze systeemconfiguratie en beveiligingsprotocollen.",
            'tr': f"Sevgili {company} Ekibi,\n\nBu mesajın sizi iyi bulduğunu umuyorum. Sistem yapılandırmamız ve güvenlik protokollerimiz hakkında önemli güncellemeler sağlamak için yazıyorum.",
            'zh': f"亲爱的{company}团队，\n\n希望这封邮件能够顺利送达。我写信是为了向您提供有关我们系统配置和安全协议的重要更新。",
            'ja': f"{company}チームの皆様へ\n\nこのメッセージが皆様に届いていることを願っています。システム設定とセキュリティプロトコルに関する重要な更新をお知らせするためにご連絡いたします。"
        }
        return greetings.get(language, greetings['en'])
    
    def _generate_body_content(self, topic: str, language: str, company: str) -> str:
        """Generate realistic body content."""
        bodies = {
            'en': f"As part of our ongoing commitment to maintaining the highest standards of security and operational excellence at {company}, we are implementing enhanced {topic} protocols. This update includes new authentication mechanisms, improved monitoring capabilities, and strengthened access controls to ensure the integrity of our systems.\n\nThe implementation will be rolled out in phases to minimize disruption to our daily operations. All team members will receive detailed instructions and training materials to ensure a smooth transition.",
            'fr': f"Dans le cadre de notre engagement continu à maintenir les plus hauts standards de sécurité et d'excellence opérationnelle chez {company}, nous mettons en œuvre des protocoles {topic} améliorés. Cette mise à jour comprend de nouveaux mécanismes d'authentification, des capacités de surveillance améliorées et des contrôles d'accès renforcés pour assurer l'intégrité de nos systèmes.\n\nL'implémentation sera déployée par phases pour minimiser les perturbations de nos opérations quotidiennes. Tous les membres de l'équipe recevront des instructions détaillées et du matériel de formation pour assurer une transition en douceur.",
            'es': f"Como parte de nuestro compromiso continuo de mantener los más altos estándares de seguridad y excelencia operacional en {company}, estamos implementando protocolos {topic} mejorados. Esta actualización incluye nuevos mecanismos de autenticación, capacidades de monitoreo mejoradas y controles de acceso fortalecidos para asegurar la integridad de nuestros sistemas.\n\nLa implementación se llevará a cabo en fases para minimizar la interrupción de nuestras operaciones diarias. Todos los miembros del equipo recibirán instrucciones detalladas y materiales de capacitación para asegurar una transición fluida.",
            'de': f"Als Teil unseres kontinuierlichen Engagements, die höchsten Standards für Sicherheit und operative Exzellenz bei {company} aufrechtzuerhalten, implementieren wir verbesserte {topic} Protokolle. Dieses Update umfasst neue Authentifizierungsmechanismen, verbesserte Überwachungsfunktionen und verstärkte Zugangskontrollen, um die Integrität unserer Systeme zu gewährleisten.\n\nDie Implementierung wird in Phasen durchgeführt, um Störungen unserer täglichen Operationen zu minimieren. Alle Teammitglieder erhalten detaillierte Anweisungen und Schulungsmaterialien für einen reibungslosen Übergang.",
            'it': f"Come parte del nostro impegno continuo nel mantenere i più alti standard di sicurezza ed eccellenza operativa presso {company}, stiamo implementando protocolli {topic} migliorati. Questo aggiornamento include nuovi meccanismi di autenticazione, capacità di monitoraggio migliorate e controlli di accesso rafforzati per garantire l'integrità dei nostri sistemi.\n\nL'implementazione verrà distribuita in fasi per minimizzare le interruzioni alle nostre operazioni quotidiane. Tutti i membri del team riceveranno istruzioni dettagliate e materiali di formazione per garantire una transizione fluida.",
            'pt': f"Como parte do nosso compromisso contínuo de manter os mais altos padrões de segurança e excelência operacional na {company}, estamos implementando protocolos {topic} aprimorados. Esta atualização inclui novos mecanismos de autenticação, capacidades de monitoramento melhoradas e controles de acesso fortalecidos para garantir a integridade de nossos sistemas.\n\nA implementação será lançada em fases para minimizar a interrupção de nossas operações diárias. Todos os membros da equipe receberão instruções detalhadas e materiais de treinamento para garantir uma transição suave.",
            'nl': f"Als onderdeel van onze voortdurende inzet om de hoogste normen voor veiligheid en operationele excellentie bij {company} te handhaven, implementeren we verbeterde {topic} protocollen. Deze update omvat nieuwe authenticatiemechanismen, verbeterde monitoringmogelijkheden en versterkte toegangscontroles om de integriteit van onze systemen te waarborgen.\n\nDe implementatie wordt gefaseerd uitgerold om verstoring van onze dagelijkse operaties te minimaliseren. Alle teamleden ontvangen gedetailleerde instructies en trainingsmateriaal voor een soepele overgang.",
            'tr': f"{company}'da güvenlik ve operasyonel mükemmellik için en yüksek standartları sürdürme konusundaki sürekli taahhüdümüzün bir parçası olarak, gelişmiş {topic} protokollerini uyguluyoruz. Bu güncelleme, sistemlerimizin bütünlüğünü sağlamak için yeni kimlik doğrulama mekanizmaları, geliştirilmiş izleme yetenekleri ve güçlendirilmiş erişim kontrollerini içerir.\n\nUygulama, günlük operasyonlarımızdaki kesintileri en aza indirmek için aşamalı olarak yayınlanacaktır. Sorunsuz bir geçiş sağlamak için tüm ekip üyeleri detaylı talimatlar ve eğitim materyalleri alacaktır.",
            'zh': f"作为我们在{company}持续致力于维护最高安全和运营卓越标准的一部分，我们正在实施增强的{topic}协议。此更新包括新的身份验证机制、改进的监控功能和强化的访问控制，以确保我们系统的完整性。\n\n实施将分阶段推出，以最大程度地减少对我们日常运营的干扰。所有团队成员将收到详细的说明和培训材料，以确保顺利过渡。",
            'ja': f"{company}で最高のセキュリティと運用の卓越性を維持するという継続的な取り組みの一環として、強化された{topic}プロトコルを実装しています。この更新には、新しい認証メカニズム、改善された監視機能、システムの整合性を確保するための強化されたアクセス制御が含まれます。\n\n実装は段階的に展開され、日常業務への影響を最小限に抑えます。すべてのチームメンバーは、スムーズな移行を確保するために詳細な指示とトレーニング資料を受け取ります。"
        }
        return bodies.get(language, bodies['en'])
    
    def _generate_closing_content(self, language: str, company: str) -> str:
        """Generate realistic closing content."""
        closings = {
            'en': f"Thank you for your attention to this important matter. If you have any questions or concerns, please do not hesitate to contact the IT Security team.\n\nWe appreciate your cooperation in maintaining the security and efficiency of {company}'s systems.",
            'fr': f"Merci de votre attention à cette question importante. Si vous avez des questions ou des préoccupations, n'hésitez pas à contacter l'équipe de sécurité informatique.\n\nNous apprécions votre coopération pour maintenir la sécurité et l'efficacité des systèmes de {company}.",
            'es': f"Gracias por su atención a este asunto importante. Si tiene alguna pregunta o inquietud, no dude en contactar al equipo de Seguridad de TI.\n\nApreciamos su cooperación para mantener la seguridad y eficiencia de los sistemas de {company}.",
            'de': f"Vielen Dank für Ihre Aufmerksamkeit zu dieser wichtigen Angelegenheit. Wenn Sie Fragen oder Bedenken haben, zögern Sie nicht, das IT-Sicherheitsteam zu kontaktieren.\n\nWir schätzen Ihre Zusammenarbeit bei der Aufrechterhaltung der Sicherheit und Effizienz der Systeme von {company}.",
            'it': f"Grazie per la vostra attenzione a questa questione importante. Se avete domande o preoccupazioni, non esitate a contattare il team di Sicurezza IT.\n\nApprezziamo la vostra cooperazione nel mantenere la sicurezza e l'efficienza dei sistemi di {company}.",
            'pt': f"Obrigado pela sua atenção a este assunto importante. Se tiver alguma dúvida ou preocupação, não hesite em entrar em contato com a equipe de Segurança de TI.\n\nAgradecemos sua cooperação para manter a segurança e eficiência dos sistemas da {company}.",
            'nl': f"Bedankt voor uw aandacht voor deze belangrijke kwestie. Als u vragen of zorgen heeft, aarzel dan niet om contact op te nemen met het IT-beveiligingsteam.\n\nWe waarderen uw samenwerking bij het handhaven van de veiligheid en efficiëntie van de systemen van {company}.",
            'tr': f"Bu önemli konuya gösterdiğiniz dikkat için teşekkür ederiz. Herhangi bir sorunuz veya endişeniz varsa, lütfen BT Güvenlik ekibiyle iletişime geçmekten çekinmeyin.\n\n{company}'nin sistemlerinin güvenliği ve verimliliğini sürdürmede işbirliğinizi takdir ediyoruz.",
            'zh': f"感谢您对此重要事项的关注。如果您有任何问题或疑虑，请随时联系IT安全团队。\n\n我们感谢您在维护{company}系统安全性和效率方面的合作。",
            'ja': f"この重要な問題にご注意いただき、ありがとうございます。ご質問やご懸念がございましたら、ITセキュリティチームまでお気軽にお問い合わせください。\n\n{company}のシステムのセキュリティと効率性を維持する上でのご協力に感謝いたします。"
        }
        return closings.get(language, closings['en'])
    
    def _generate_signature_content(self, language: str, company: str) -> str:
        """Generate realistic signature content."""
        signatures = {
            'en': f"Best regards,\nIT Security Team\n{company}",
            'fr': f"Cordialement,\nÉquipe de sécurité informatique\n{company}",
            'es': f"Saludos cordiales,\nEquipo de Seguridad de TI\n{company}",
            'de': f"Mit freundlichen Grüßen,\nIT-Sicherheitsteam\n{company}",
            'it': f"Cordiali saluti,\nTeam di Sicurezza IT\n{company}",
            'pt': f"Atenciosamente,\nEquipe de Segurança de TI\n{company}",
            'nl': f"Met vriendelijke groet,\nIT-beveiligingsteam\n{company}",
            'tr': f"Saygılarımla,\nBT Güvenlik Ekibi\n{company}",
            'zh': f"此致\nIT安全团队\n{company}",
            'ja': f"敬具\nITセキュリティチーム\n{company}"
        }
        return signatures.get(language, signatures['en'])
    
    def _generate_generic_section_content(self, topic: str, section_name: str, language: str, company: str) -> str:
        """Generate generic section content."""
        return f"Professional content for {section_name} section about {topic} for {company} in {language}."
    
    def _get_cached_company(self, language: str) -> Dict[str, str]:
        """Get cached company info for ultra-fast mode."""
        if self.ultra_fast_mode and language in self._company_cache:
            return self._company_cache[language]
        
        company_info = self.prompt_system.get_random_company(language)
        
        if self.ultra_fast_mode:
            self._company_cache[language] = company_info
        
        return company_info
    
    def _generate_ultra_fast_content(self, topic: str, language: str, format_type: str, 
                                   template: Dict, credential_types: List[str], 
                                   context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Ultra-fast content generation using pre-built templates."""
        company_name = context['company']
        
        # Generate title using simple template
        title = f"{topic} - {company_name} Update"
        
        # Generate sections using cached templates
        sections = []
        for section_name in template['sections']:
            section_content = self._get_cached_section_content(section_name, topic, language, company_name)
            sections.append({
                'title': self._get_section_title(section_name, language),
                'content': section_content
            })
        
        # Generate credentials using fast method
        min_creds = context.get('min_credentials_per_file', 1)
        max_creds = context.get('max_credentials_per_file', 3)
        credentials = self._generate_credentials_ultra_fast(credential_types, min_creds, max_creds)
        
        # Embed credentials into sections
        sections = self._embed_credentials_into_sections(sections, credentials, language)
        
        # Generate metadata
        metadata = {
            'topic': topic,
            'language': language,
            'format_type': format_type,
            'generated_at': time.time(),
            'generator': 'ContentGenerationAgent-UltraFast'
        }
        
        if context:
            metadata.update(context)
        
        return {
            'title': title,
            'sections': sections,
            'credentials': credentials,
            'metadata': metadata,
            'format_type': format_type,
            'language': language,
            'context': context
        }
    
    def _get_cached_section_content(self, section_name: str, topic: str, language: str, company: str) -> str:
        """Get cached section content for ultra-fast mode."""
        cache_key = f"{section_name}_{language}_{company}"
        
        if self.ultra_fast_mode and cache_key in self._template_cache:
            return self._template_cache[cache_key].replace('{topic}', topic)
        
        # Generate content using existing methods
        if section_name == 'subject':
            content = self._generate_subject_content(topic, language, company)
        elif section_name == 'greeting':
            content = self._generate_greeting_content(language, company)
        elif section_name == 'body':
            content = self._generate_body_content(topic, language, company)
        elif section_name == 'closing':
            content = self._generate_closing_content(language, company)
        elif section_name == 'signature':
            content = self._generate_signature_content(language, company)
        else:
            content = self._generate_generic_section_content(topic, section_name, language, company)
        
        # Cache the content (without topic substitution)
        if self.ultra_fast_mode:
            self._template_cache[cache_key] = content.replace(topic, '{topic}')
        
        return content
    
    def _generate_credentials_ultra_fast(self, credential_types: List[str], min_creds: int, max_creds: int) -> List[Dict[str, str]]:
        """Ultra-fast credential generation."""
        credentials = []
        num_creds = random.randint(min_creds, max_creds)
        
        for i in range(num_creds):
            cred_type = random.choice(credential_types)
            if self.credential_generator:
                try:
                    credential = self.credential_generator.generate_credential(cred_type)
                    print(f"DEBUG: Ultra-fast generated {cred_type}: {credential}")
                except Exception as e:
                    print(f"Warning: CredentialGenerator failed in ultra-fast mode for {cred_type}: {e}")
                    # Use more realistic fallback instead of simple pattern
                    credential = self._generate_realistic_fallback(cred_type)
            else:
                # Generate more realistic fallback
                credential = self._generate_realistic_fallback(cred_type)
            
            credentials.append({
                'type': cred_type,
                'value': credential,
                'label': cred_type.replace('_', ' ').title()
            })
        
        return credentials

    def _generate_realistic_fallback(self, credential_type: str) -> str:
        """Generate realistic fallback credentials when CredentialGenerator is not available."""
        import string
        import random
        
        # Provide realistic fallbacks for common credential types
        if credential_type == "slack_user_token":
            return 'xoxp-' + str(random.randint(10000000000, 99999999999)) + '-' + str(random.randint(10000000000, 99999999999)) + '-' + ''.join(random.choices(string.ascii_letters + string.digits, k=24))
        elif credential_type == "slack_bot_token":
            return 'xoxb-' + str(random.randint(10000000000, 99999999999)) + '-' + str(random.randint(10000000000, 99999999999)) + '-' + ''.join(random.choices(string.ascii_letters + string.digits, k=24))
        elif credential_type == "api_key":
            return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        elif credential_type == "aws_access_key":
            return 'AKIA' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        elif credential_type == "jwt_token":
            # Generate a realistic JWT-like token
            header = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9'
            payload = ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=40))
            signature = ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=43))
            return f"{header}.{payload}.{signature}"
        elif credential_type == "password":
            chars = string.ascii_letters + string.digits + '@#$%^&+='
            length = random.randint(8, 16)
            return ''.join(random.choices(chars, k=length))
        else:
            # Generic fallback for unknown types
            return f"{credential_type}_{random.randint(100000, 999999)}"

    def _clean_generated_content(self, content: str) -> str:
        """Clean generated content to remove template instructions and placeholders."""
        if not content:
            return ""
        
        # Remove common template instruction patterns
        template_patterns = [
            r'^- Use .*$',  # Bullet points starting with "- Use"
            r'^- Ensure .*$',  # Bullet points starting with "- Ensure"
            r'^- Include .*$',  # Bullet points starting with "- Include"
            r'^- Avoid .*$',  # Bullet points starting with "- Avoid"
            r'^- Make sure .*$',  # Bullet points starting with "- Make sure"
            r'^- Keep .*$',  # Bullet points starting with "- Keep"
            r'^- Structure .*$',  # Bullet points starting with "- Structure"
            r'^- Write .*$',  # Bullet points starting with "- Write"
            r'^- Provide .*$',  # Bullet points starting with "- Provide"
            r'^- Incorporate .*$',  # Bullet points starting with "- Incorporate"
            r'^- Proofread .*$',  # Bullet points starting with "- Proofread"
            r'^- Note .*$',  # Bullet points starting with "- Note"
            r'about the .*$',  # Generic "about the X" text
            r'for future reference$',  # Generic "for future reference"
            r'for the .*$',  # Generic "for the X" text
            r'^Requirements?:$',  # "Requirements:" headers
            r'^Content Requirements?:$',  # "Content Requirements:" headers
            r'^Structure Guidelines?:$',  # "Structure Guidelines:" headers
            r'^Language: .*$',  # Language specification lines
            r'^Length: .*$',  # Length specification lines
            r'^Style: .*$',  # Style specification lines
            r'^Context: .*$',  # Context specification lines
            r'^Topic: .*$',  # Topic specification lines
            r'^Company: .*$',  # Company specification lines
            r'^Format: .*$',  # Format specification lines
            r'^Generate only .*$',  # "Generate only" instructions
            r'^No explanations or instructions$',  # Instruction reminders
        ]
        
        import re
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line matches any template pattern
            is_template = False
            for pattern in template_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_template = True
                    break
            
            # Skip template instructions and empty lines
            if not is_template and line:
                cleaned_lines.append(line)
        
        # Join cleaned lines and remove excessive whitespace
        cleaned_content = '\n'.join(cleaned_lines).strip()
        
        # If content is too short or seems like template instructions, return empty
        if len(cleaned_content) < 10 or any(phrase in cleaned_content.lower() for phrase in [
            'generate', 'requirements', 'language:', 'length:', 'style:', 'context:'
        ]):
            return ""
        
        return cleaned_content
    
    def _generate_credentials_with_labels(self, credential_types: List[str], language: str, 
                                        min_creds: int = 1, max_creds: int = 3, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Generate credentials with proper localized labels and count limits."""
        credentials = []
        
        # Smart credential generation: avoid duplicating the same credential type
        # Generate one credential per unique type selected by the user
        selected_types = credential_types[:max_creds]  # Limit to max_creds to respect user's preference
        
        print(f"DEBUG: Generating {len(selected_types)} unique credentials from types: {selected_types}")
        
        for cred_type in selected_types:
            # Generate credential value (this would use the credential generator)
            credential_value = self._generate_credential_value(cred_type, language, context)
            
            # Get localized label
            label = self._get_credential_label(cred_type, language)
            
            credentials.append({
                'type': cred_type,
                'value': credential_value,
                'label': label
            })
        
        return credentials
    
    def _generate_credential_value(self, credential_type: str, language: str = 'en', context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a credential value based on type using regex patterns."""
        # First try to use the CredentialGenerator with regex patterns
        if self.credential_generator:
            try:
                # Use company from context if available, otherwise get a random one
                if context and 'company' in context:
                    company_name = context['company']
                else:
                    company_name = self.prompt_system.get_random_company(language)['name']
                
                # Generate credential using regex patterns from database
                cred_context = {
                    'language': language,
                    'company': company_name
                }
                credential = self.credential_generator.generate_credential(credential_type, cred_context)
                print(f"DEBUG: Generated {credential_type} credential: {credential}")
                return credential
            except Exception as e:
                print(f"Warning: CredentialGenerator failed for {credential_type}: {e}")
                # Fall back to LLM generation
        
        # Fallback to LLM generation if CredentialGenerator is not available
        if self.llm:
            # Use company from context if available, otherwise get a random one
            if context and 'company_info' in context:
                company_info = context['company_info']
            else:
                company_info = self.prompt_system.get_random_company(language)
            
            # Use enhanced prompt system for credential generation
            prompt = self.prompt_system.create_credential_prompt(
                credential_type=credential_type,
                language=language,
                company=company_info['name']
            )
            try:
                credential = self.llm.generate(prompt, max_tokens=50, temperature=0.3)
                print(f"DEBUG: Generated {credential_type} credential via LLM: {credential.strip()}")
                return credential.strip()
            except Exception as e:
                print(f"Warning: LLM generation failed for {credential_type}: {e}")
        
        # Ultimate fallback - generate a basic credential
        fallback_credential = f"generated_{credential_type}_{random.randint(1000, 9999)}"
        print(f"DEBUG: Using fallback credential for {credential_type}: {fallback_credential}")
        return fallback_credential
    
    # Removed hardcoded credential method - now using regex-based CredentialGenerator
    
    def _embed_credentials_into_sections(self, sections: List[Dict[str, str]], credentials: List[Dict[str, str]], language: str) -> List[Dict[str, str]]:
        """Embed credentials into section content naturally."""
        if not credentials:
            return sections
        
        # Skip embedding if credentials will be handled by format synthesizer
        # This prevents duplication when both ContentGenerationAgent and FormatSynthesizer embed credentials
        if hasattr(self, '_skip_credential_embedding') and self._skip_credential_embedding:
            print(f"DEBUG: Skipping credential embedding in sections - will be handled by format synthesizer")
            return sections
        
        # Find the best section to embed credentials (prefer technical/configuration sections)
        target_section = None
        for section in sections:
            section_title = section.get('title', '').lower()
            if any(keyword in section_title for keyword in ['configuration', 'technical', 'implementation', 'security', 'setup']):
                target_section = section
                break
        
        # If no technical section found, use the first section
        if not target_section and sections:
            target_section = sections[0]
        
        if target_section:
            # Add credentials to the section content
            credential_text = "\n\nConfiguration Details:\n"
            for cred in credentials:
                label = cred.get('label', cred.get('type', 'Credential'))
                value = cred.get('value', 'N/A')
                credential_text += f"{label}: {value}\n"
            
            # Append credentials to section content
            target_section['content'] = target_section.get('content', '') + credential_text
            print(f"DEBUG: Embedded {len(credentials)} credentials into section: {target_section.get('title', 'Unknown')}")
        
        return sections
    
    def _get_credential_label(self, credential_type: str, language: str) -> str:
        """Get localized label for credential type."""
        labels = {
            'en': {
                'password': 'Password',
                'api_key': 'API Key',
                'database_connection': 'Database Connection',
                'jwt_token': 'JWT Token',
                'aws_access_key': 'AWS Access Key',
                'ssh_key': 'SSH Key',
                'oauth_token': 'OAuth Token',
                'session_id': 'Session ID',
                'encryption_key': 'Encryption Key',
                'certificate': 'Certificate'
            },
            'fr': {
                'password': 'Mot de passe',
                'api_key': 'Clé API',
                'database_connection': 'Connexion Base de données',
                'jwt_token': 'Jeton JWT',
                'aws_access_key': 'Clé d\'accès AWS',
                'ssh_key': 'Clé SSH',
                'oauth_token': 'Jeton OAuth',
                'session_id': 'ID de session',
                'encryption_key': 'Clé de chiffrement',
                'certificate': 'Certificat'
            },
            'es': {
                'password': 'Contraseña',
                'api_key': 'Clave API',
                'database_connection': 'Conexión Base de datos',
                'jwt_token': 'Token JWT',
                'aws_access_key': 'Clave de acceso AWS',
                'ssh_key': 'Clave SSH',
                'oauth_token': 'Token OAuth',
                'session_id': 'ID de sesión',
                'encryption_key': 'Clave de cifrado',
                'certificate': 'Certificado'
            },
            'de': {
                'password': 'Passwort',
                'api_key': 'API-Schlüssel',
                'database_connection': 'Datenbankverbindung',
                'jwt_token': 'JWT-Token',
                'aws_access_key': 'AWS-Zugriffsschlüssel',
                'ssh_key': 'SSH-Schlüssel',
                'oauth_token': 'OAuth-Token',
                'session_id': 'Sitzungs-ID',
                'encryption_key': 'Verschlüsselungsschlüssel',
                'certificate': 'Zertifikat'
            },
            'it': {
                'password': 'Password',
                'api_key': 'Chiave API',
                'database_connection': 'Connessione Database',
                'jwt_token': 'Token JWT',
                'aws_access_key': 'Chiave di accesso AWS',
                'ssh_key': 'Chiave SSH',
                'oauth_token': 'Token OAuth',
                'session_id': 'ID sessione',
                'encryption_key': 'Chiave di crittografia',
                'certificate': 'Certificato'
            },
            'pt': {
                'password': 'Senha',
                'api_key': 'Chave API',
                'database_connection': 'Conexão Base de dados',
                'jwt_token': 'Token JWT',
                'aws_access_key': 'Chave de acesso AWS',
                'ssh_key': 'Chave SSH',
                'oauth_token': 'Token OAuth',
                'session_id': 'ID de sessão',
                'encryption_key': 'Chave de criptografia',
                'certificate': 'Certificado'
            },
            'nl': {
                'password': 'Wachtwoord',
                'api_key': 'API-sleutel',
                'database_connection': 'Databaseverbinding',
                'jwt_token': 'JWT-token',
                'aws_access_key': 'AWS-toegangssleutel',
                'ssh_key': 'SSH-sleutel',
                'oauth_token': 'OAuth-token',
                'session_id': 'Sessie-ID',
                'encryption_key': 'Versleutelingssleutel',
                'certificate': 'Certificaat'
            },
            'tr': {
                'password': 'Şifre',
                'api_key': 'API Anahtarı',
                'database_connection': 'Veritabanı Bağlantısı',
                'jwt_token': 'JWT Token',
                'aws_access_key': 'AWS Erişim Anahtarı',
                'ssh_key': 'SSH Anahtarı',
                'oauth_token': 'OAuth Token',
                'session_id': 'Oturum ID',
                'encryption_key': 'Şifreleme Anahtarı',
                'certificate': 'Sertifika'
            },
            'zh': {
                'password': '密码',
                'api_key': 'API密钥',
                'database_connection': '数据库连接',
                'jwt_token': 'JWT令牌',
                'aws_access_key': 'AWS访问密钥',
                'ssh_key': 'SSH密钥',
                'oauth_token': 'OAuth令牌',
                'session_id': '会话ID',
                'encryption_key': '加密密钥',
                'certificate': '证书'
            },
            'ja': {
                'password': 'パスワード',
                'api_key': 'APIキー',
                'database_connection': 'データベース接続',
                'jwt_token': 'JWTトークン',
                'aws_access_key': 'AWSアクセスキー',
                'ssh_key': 'SSHキー',
                'oauth_token': 'OAuthトークン',
                'session_id': 'セッションID',
                'encryption_key': '暗号化キー',
                'certificate': '証明書'
            }
        }
        
        return labels.get(language, labels['en']).get(credential_type, credential_type)
    
    def _get_section_title(self, section_name: str, language: str) -> str:
        """Get localized section title."""
        titles = {
            'en': {
                # Email sections
                'subject': 'Subject',
                'greeting': 'Greeting',
                'body': 'Message Body',
                'closing': 'Closing',
                'signature': 'Signature',
                
                # Document sections
                'title': 'Title',
                'overview': 'Overview',
                'introduction': 'Introduction',
                'executive_summary': 'Executive Summary',
                'technical_details': 'Technical Details',
                'technical_specifications': 'Technical Specifications',
                'technical_architecture': 'Technical Architecture',
                'configuration': 'Configuration',
                'implementation': 'Implementation',
                'implementation_plan': 'Implementation Plan',
                'security': 'Security',
                'security_considerations': 'Security Considerations',
                'conclusion': 'Conclusion',
                
                # Spreadsheet sections
                'data_sheet': 'Data Sheet',
                'configuration_sheet': 'Configuration Sheet',
                'credentials_sheet': 'Credentials Sheet',
                
                # Image sections
                'description': 'Description',
                
                # Diagram sections
                'system_architecture': 'System Architecture'
            },
            'fr': {
                # Email sections
                'subject': 'Objet',
                'greeting': 'Salutation',
                'body': 'Corps du message',
                'closing': 'Formule de politesse',
                'signature': 'Signature',
                
                # Document sections
                'title': 'Titre',
                'overview': 'Aperçu',
                'introduction': 'Introduction',
                'executive_summary': 'Résumé exécutif',
                'technical_details': 'Détails techniques',
                'technical_specifications': 'Spécifications techniques',
                'technical_architecture': 'Architecture technique',
                'configuration': 'Configuration',
                'implementation': 'Implémentation',
                'implementation_plan': 'Plan d\'implémentation',
                'security': 'Sécurité',
                'security_considerations': 'Considérations de sécurité',
                'conclusion': 'Conclusion',
                
                # Spreadsheet sections
                'data_sheet': 'Feuille de données',
                'configuration_sheet': 'Feuille de configuration',
                'credentials_sheet': 'Feuille d\'identifiants',
                
                # Image sections
                'description': 'Description',
                
                # Diagram sections
                'system_architecture': 'Architecture système'
            },
            'es': {
                # Email sections
                'subject': 'Asunto',
                'greeting': 'Saludo',
                'body': 'Cuerpo del mensaje',
                'closing': 'Despedida',
                'signature': 'Firma',
                
                # Document sections
                'title': 'Título',
                'overview': 'Resumen',
                'introduction': 'Introducción',
                'executive_summary': 'Resumen ejecutivo',
                'technical_details': 'Detalles técnicos',
                'technical_specifications': 'Especificaciones técnicas',
                'technical_architecture': 'Arquitectura técnica',
                'configuration': 'Configuración',
                'implementation': 'Implementación',
                'implementation_plan': 'Plan de implementación',
                'security': 'Seguridad',
                'security_considerations': 'Consideraciones de seguridad',
                'conclusion': 'Conclusión',
                
                # Spreadsheet sections
                'data_sheet': 'Hoja de datos',
                'configuration_sheet': 'Hoja de configuración',
                'credentials_sheet': 'Hoja de credenciales',
                
                # Image sections
                'description': 'Descripción',
                
                # Diagram sections
                'system_architecture': 'Arquitectura del sistema'
            },
            'de': {
                # Email sections
                'subject': 'Betreff',
                'greeting': 'Begrüßung',
                'body': 'Nachrichtentext',
                'closing': 'Grußformel',
                'signature': 'Signatur',
                
                # Document sections
                'title': 'Titel',
                'overview': 'Übersicht',
                'introduction': 'Einführung',
                'executive_summary': 'Zusammenfassung',
                'technical_details': 'Technische Details',
                'technical_specifications': 'Technische Spezifikationen',
                'technical_architecture': 'Technische Architektur',
                'configuration': 'Konfiguration',
                'implementation': 'Implementierung',
                'implementation_plan': 'Implementierungsplan',
                'security': 'Sicherheit',
                'security_considerations': 'Sicherheitsüberlegungen',
                'conclusion': 'Fazit',
                
                # Spreadsheet sections
                'data_sheet': 'Datenblatt',
                'configuration_sheet': 'Konfigurationsblatt',
                'credentials_sheet': 'Anmeldedatenblatt',
                
                # Image sections
                'description': 'Beschreibung',
                
                # Diagram sections
                'system_architecture': 'Systemarchitektur'
            },
            'it': {
                # Email sections
                'subject': 'Oggetto',
                'greeting': 'Saluto',
                'body': 'Corpo del messaggio',
                'closing': 'Chiusura',
                'signature': 'Firma',
                
                # Document sections
                'title': 'Titolo',
                'overview': 'Panoramica',
                'introduction': 'Introduzione',
                'executive_summary': 'Riassunto esecutivo',
                'technical_details': 'Dettagli tecnici',
                'technical_specifications': 'Specifiche tecniche',
                'technical_architecture': 'Architettura tecnica',
                'configuration': 'Configurazione',
                'implementation': 'Implementazione',
                'implementation_plan': 'Piano di implementazione',
                'security': 'Sicurezza',
                'security_considerations': 'Considerazioni di sicurezza',
                'conclusion': 'Conclusione',
                
                # Spreadsheet sections
                'data_sheet': 'Foglio dati',
                'configuration_sheet': 'Foglio configurazione',
                'credentials_sheet': 'Foglio credenziali',
                
                # Image sections
                'description': 'Descrizione',
                
                # Diagram sections
                'system_architecture': 'Architettura del sistema'
            },
            'pt': {
                # Email sections
                'subject': 'Assunto',
                'greeting': 'Saudação',
                'body': 'Corpo da mensagem',
                'closing': 'Fechamento',
                'signature': 'Assinatura',
                
                # Document sections
                'title': 'Título',
                'overview': 'Visão geral',
                'introduction': 'Introdução',
                'executive_summary': 'Resumo executivo',
                'technical_details': 'Detalhes técnicos',
                'technical_specifications': 'Especificações técnicas',
                'technical_architecture': 'Arquitetura técnica',
                'configuration': 'Configuração',
                'implementation': 'Implementação',
                'implementation_plan': 'Plano de implementação',
                'security': 'Segurança',
                'security_considerations': 'Considerações de segurança',
                'conclusion': 'Conclusão',
                
                # Spreadsheet sections
                'data_sheet': 'Planilha de dados',
                'configuration_sheet': 'Planilha de configuração',
                'credentials_sheet': 'Planilha de credenciais',
                
                # Image sections
                'description': 'Descrição',
                
                # Diagram sections
                'system_architecture': 'Arquitetura do sistema'
            },
            'nl': {
                # Email sections
                'subject': 'Onderwerp',
                'greeting': 'Begroeting',
                'body': 'Berichttekst',
                'closing': 'Afsluiting',
                'signature': 'Handtekening',
                
                # Document sections
                'title': 'Titel',
                'overview': 'Overzicht',
                'introduction': 'Inleiding',
                'executive_summary': 'Samenvatting',
                'technical_details': 'Technische details',
                'technical_specifications': 'Technische specificaties',
                'technical_architecture': 'Technische architectuur',
                'configuration': 'Configuratie',
                'implementation': 'Implementatie',
                'implementation_plan': 'Implementatieplan',
                'security': 'Beveiliging',
                'security_considerations': 'Beveiligingsoverwegingen',
                'conclusion': 'Conclusie',
                
                # Spreadsheet sections
                'data_sheet': 'Gegevensblad',
                'configuration_sheet': 'Configuratieblad',
                'credentials_sheet': 'Inloggegevensblad',
                
                # Image sections
                'description': 'Beschrijving',
                
                # Diagram sections
                'system_architecture': 'Systeemarchitectuur'
            },
            'tr': {
                # Email sections
                'subject': 'Konu',
                'greeting': 'Selamlama',
                'body': 'Mesaj gövdesi',
                'closing': 'Kapanış',
                'signature': 'İmza',
                
                # Document sections
                'title': 'Başlık',
                'overview': 'Genel bakış',
                'introduction': 'Giriş',
                'executive_summary': 'Yönetici özeti',
                'technical_details': 'Teknik detaylar',
                'technical_specifications': 'Teknik özellikler',
                'technical_architecture': 'Teknik mimari',
                'configuration': 'Yapılandırma',
                'implementation': 'Uygulama',
                'implementation_plan': 'Uygulama planı',
                'security': 'Güvenlik',
                'security_considerations': 'Güvenlik değerlendirmeleri',
                'conclusion': 'Sonuç',
                
                # Spreadsheet sections
                'data_sheet': 'Veri sayfası',
                'configuration_sheet': 'Yapılandırma sayfası',
                'credentials_sheet': 'Kimlik bilgileri sayfası',
                
                # Image sections
                'description': 'Açıklama',
                
                # Diagram sections
                'system_architecture': 'Sistem mimarisi'
            },
            'zh': {
                # Email sections
                'subject': '主题',
                'greeting': '问候',
                'body': '邮件正文',
                'closing': '结尾',
                'signature': '签名',
                
                # Document sections
                'title': '标题',
                'overview': '概述',
                'introduction': '介绍',
                'executive_summary': '执行摘要',
                'technical_details': '技术细节',
                'technical_specifications': '技术规格',
                'technical_architecture': '技术架构',
                'configuration': '配置',
                'implementation': '实施',
                'implementation_plan': '实施计划',
                'security': '安全',
                'security_considerations': '安全考虑',
                'conclusion': '结论',
                
                # Spreadsheet sections
                'data_sheet': '数据表',
                'configuration_sheet': '配置表',
                'credentials_sheet': '凭据表',
                
                # Image sections
                'description': '描述',
                
                # Diagram sections
                'system_architecture': '系统架构'
            },
            'ja': {
                # Email sections
                'subject': '件名',
                'greeting': '挨拶',
                'body': 'メッセージ本文',
                'closing': '結び',
                'signature': '署名',
                
                # Document sections
                'title': 'タイトル',
                'overview': '概要',
                'introduction': '導入',
                'executive_summary': 'エグゼクティブサマリー',
                'technical_details': '技術詳細',
                'technical_specifications': '技術仕様',
                'technical_architecture': '技術アーキテクチャ',
                'configuration': '設定',
                'implementation': '実装',
                'implementation_plan': '実装計画',
                'security': 'セキュリティ',
                'security_considerations': 'セキュリティ考慮事項',
                'conclusion': '結論',
                
                # Spreadsheet sections
                'data_sheet': 'データシート',
                'configuration_sheet': '設定シート',
                'credentials_sheet': '認証情報シート',
                
                # Image sections
                'description': '説明',
                
                # Diagram sections
                'system_architecture': 'システムアーキテクチャ'
            }
        }
        
        return titles.get(language, titles['en']).get(section_name, section_name)
    
    def _generate_metadata(self, topic: str, language: str, format_type: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate document metadata."""
        metadata = {
            'topic': topic,
            'language': language,
            'format_type': format_type,
            'generated_at': time.time(),
            'generator': 'ContentGenerationAgent'
        }
        
        if context:
            metadata.update(context)
        
        return metadata
    
    def cleanup(self) -> None:
        """Clean up resources and shutdown executor pool."""
        if self.executor_pool:
            self.executor_pool.shutdown(wait=True)
            self.executor_pool = None
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.cleanup()
    
    # Removed old prompt methods - now using EnhancedPromptSystem
