# CredentialForge Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Agentic AI Design](#agentic-ai-design)
5. [Offline LLM Integration](#offline-llm-integration)
6. [File Format Support](#file-format-support)
7. [Security Considerations](#security-considerations)
8. [Performance Optimization](#performance-optimization)

## System Overview

CredentialForge is built on a modular, layered architecture that separates concerns and enables extensibility. The system is designed to be:

- **Modular**: Each component has a single responsibility
- **Extensible**: New file formats and credential types can be easily added
- **Testable**: Components are loosely coupled and can be tested independently
- **Scalable**: Supports batch processing and parallel execution
- **Offline-Capable**: Works without external dependencies when using offline LLM

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                     │
├─────────────────────────────────────────────────────────────────┤
│  CLI Interface          │  Interactive Terminal                │
│  - Command parsing      │  - Real-time configuration           │
│  - Parameter validation │  - Preview capabilities              │
│  - Error handling       │  - Progress tracking                 │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Agentic AI Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  Orchestrator Agent     │  Specialized Agents                  │
│  - Coordinates workflow │  - Credential Agent                  │
│  - Manages state        │  - Topic Agent                       │
│  - Handles errors       │  - Embedding Agent                   │
│  - LLM integration      │  - Validation Agent                  │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Core Logic Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  Generators            │  Synthesizers        │  Database      │
│  - Credential Gen      │  - Format-specific   │  - Regex DB    │
│  - Topic Gen           │  - Base classes      │  - Pattern mgmt│
│  - Content Gen         │  - Embedding logic   │  - Querying    │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Infrastructure Layer                       │
├─────────────────────────────────────────────────────────────────┤
│  Utilities             │  LLM Interface       │  Configuration │
│  - Logging             │  - llama.cpp wrapper │  - Settings    │
│  - Validation          │  - Model management  │  - Environment │
│  - Interactive tools   │  - CPU-only inference│  - Defaults    │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. CLI Layer

The CLI layer provides the primary user interface through two modes:

#### Command-Line Interface (`cli.py`)

```python
@click.group()
def cli():
    """CredentialForge - Synthetic document generation with embedded credentials."""
    pass

@cli.command()
@click.option('--output-dir', required=True, help='Output directory for generated files')
@click.option('--num-files', default=1, help='Number of files to generate')
@click.option('--formats', default='eml', help='Comma-separated file formats')
@click.option('--credential-types', required=True, help='Comma-separated credential types')
@click.option('--regex-db', required=True, help='Path to regex database file')
@click.option('--topics', required=True, help='Comma-separated topics for content')
@click.option('--llm-model', help='Path to GGUF model file for offline LLM')
def generate(output_dir, num_files, formats, credential_types, regex_db, topics, llm_model):
    """Generate synthetic documents with embedded credentials."""
    # Implementation
```

#### Interactive Terminal (`utils/interactive.py`)

```python
class InteractiveTerminal:
    def __init__(self):
        self.session = prompt_toolkit.PromptSession()
        self.config = {}
    
    def collect_parameters(self):
        """Collect user parameters through interactive prompts."""
        # Step-by-step parameter collection
        # Real-time validation
        # Preview capabilities
    
    def preview_generation(self):
        """Show preview of generated content before full generation."""
        # Sample content generation
        # Credential placement preview
        # Topic content preview
```

### 2. Agentic AI Layer

The agentic AI layer orchestrates the generation process using intelligent agents:

#### Orchestrator Agent (`agents/orchestrator.py`)

```python
class OrchestratorAgent:
    def __init__(self, llm_interface=None):
        self.llm = llm_interface
        self.credential_agent = CredentialAgent()
        self.topic_agent = TopicAgent()
        self.embedding_agent = EmbeddingAgent()
        self.validation_agent = ValidationAgent()
    
    def orchestrate_generation(self, config):
        """Main orchestration method."""
        # 1. Parse configuration
        # 2. Load regex database
        # 3. Generate topic content
        # 4. Create credentials
        # 5. Determine embedding strategy
        # 6. Generate files
        # 7. Validate output
```

#### Specialized Agents

**Credential Agent** (`agents/credential_agent.py`):
- Generates synthetic credentials using regex patterns
- Ensures credential uniqueness within batches
- Validates generated credentials against patterns

**Topic Agent** (`agents/topic_agent.py`):
- Generates topic-specific content using LLM
- Ensures content relevance and coherence
- Adapts content style to file format

**Embedding Agent** (`agents/embedding_agent.py`):
- Determines optimal credential placement
- Considers file format constraints
- Ensures natural integration

**Validation Agent** (`agents/validation_agent.py`):
- Validates generated files
- Checks credential detectability
- Ensures topic relevance

### 3. Core Logic Layer

#### Generators (`generators/`)

**Credential Generator** (`generators/credential_generator.py`):

```python
class CredentialGenerator:
    def __init__(self, regex_db):
        self.regex_db = regex_db
        self.generated_credentials = set()
    
    def generate_credential(self, credential_type):
        """Generate a synthetic credential of specified type."""
        pattern = self.regex_db.get_pattern(credential_type)
        generator = self.regex_db.get_generator(credential_type)
        
        # Generate credential using pattern-specific logic
        credential = self._apply_generator(generator, pattern)
        
        # Ensure uniqueness
        while credential in self.generated_credentials:
            credential = self._apply_generator(generator, pattern)
        
        self.generated_credentials.add(credential)
        return credential
```

**Topic Generator** (`generators/topic_generator.py`):

```python
class TopicGenerator:
    def __init__(self, llm_interface):
        self.llm = llm_interface
    
    def generate_topic_content(self, topic, file_format, context=None):
        """Generate topic-specific content for given format."""
        prompt = self._build_prompt(topic, file_format, context)
        content = self.llm.generate(prompt)
        return self._format_content(content, file_format)
```

#### Synthesizers (`synthesizers/`)

**Base Synthesizer** (`synthesizers/base.py`):

```python
class BaseSynthesizer(ABC):
    def __init__(self, output_dir):
        self.output_dir = output_dir
    
    @abstractmethod
    def synthesize(self, topic_content, credentials, metadata):
        """Synthesize a file with embedded credentials."""
        pass
    
    def _embed_credentials(self, content, credentials, strategy):
        """Embed credentials into content using specified strategy."""
        # Implementation varies by format
        pass
```

**Format-Specific Synthesizers**:

- **EML Synthesizer** (`synthesizers/eml_synthesizer.py`): Email format with MIME structure
- **Excel Synthesizer** (`synthesizers/excel_synthesizer.py`): Spreadsheet with formulas and data
- **PowerPoint Synthesizer** (`synthesizers/pptx_synthesizer.py`): Presentation with slides and notes
- **Visio Synthesizer** (`synthesizers/vsdx_synthesizer.py`): Diagram format with shapes and data

#### Database (`db/regex_db.py`)

```python
class RegexDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.patterns = self._load_patterns()
    
    def get_pattern(self, credential_type):
        """Get regex pattern for credential type."""
        return self.patterns[credential_type]['regex']
    
    def get_generator(self, credential_type):
        """Get generator function for credential type."""
        return self.patterns[credential_type]['generator']
    
    def list_types(self):
        """List available credential types."""
        return list(self.patterns.keys())
```

### 4. Infrastructure Layer

#### LLM Interface (`llm/llama_interface.py`)

```python
class LlamaInterface:
    def __init__(self, model_path, n_threads=None):
        self.model_path = model_path
        self.n_threads = n_threads or multiprocessing.cpu_count()
        self.llm = None
        self._load_model()
    
    def _load_model(self):
        """Load GGUF model using llama-cpp-python."""
        from llama_cpp import Llama
        self.llm = Llama(
            model_path=self.model_path,
            n_gpu_layers=0,  # CPU-only
            n_threads=self.n_threads,
            verbose=False
        )
    
    def generate(self, prompt, max_tokens=512, temperature=0.7):
        """Generate text using the loaded model."""
        response = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["</s>", "\n\n"]
        )
        return response['choices'][0]['text']
```

#### Utilities

**Logger** (`utils/logger.py`):
- Structured logging with different levels
- File and console output
- Generation metadata tracking

**Validators** (`utils/validators.py`):
- Input parameter validation
- File format validation
- Credential pattern validation

**Configuration** (`utils/config.py`):
- Environment variable handling
- Default value management
- Configuration file support

## Data Flow

### 1. Initialization Phase

```
User Input → CLI Parser → Parameter Validation → Configuration Object
     ↓
Regex Database Loading → Pattern Validation → Database Object
     ↓
LLM Model Loading (if specified) → Model Validation → LLM Interface
```

### 2. Generation Phase

```
Configuration → Orchestrator Agent → Agent Initialization
     ↓
Topic Generation → LLM Interface → Topic Content
     ↓
Credential Generation → Regex Database → Synthetic Credentials
     ↓
Embedding Strategy → Embedding Agent → Placement Plan
     ↓
File Synthesis → Format-Specific Synthesizer → Generated Files
     ↓
Validation → Validation Agent → Quality Assurance
```

### 3. Output Phase

```
Generated Files → Output Directory → File Organization
     ↓
Generation Log → Logging System → Metadata Recording
     ↓
Summary Report → User Interface → Completion Status
```

## Agentic AI Design

### Agent Framework

CredentialForge uses a multi-agent system where each agent has specific responsibilities:

#### Agent Communication

```python
class AgentMessage:
    def __init__(self, sender, receiver, message_type, payload):
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.payload = payload
        self.timestamp = datetime.now()

class AgentBus:
    def __init__(self):
        self.agents = {}
        self.message_queue = []
    
    def register_agent(self, agent_id, agent):
        """Register an agent with the message bus."""
        self.agents[agent_id] = agent
    
    def send_message(self, message):
        """Send a message between agents."""
        self.message_queue.append(message)
        if message.receiver in self.agents:
            self.agents[message.receiver].receive_message(message)
```

#### Agent State Management

```python
class AgentState:
    def __init__(self):
        self.current_task = None
        self.completed_tasks = []
        self.error_count = 0
        self.performance_metrics = {}
    
    def update_task(self, task):
        """Update current task status."""
        self.current_task = task
    
    def complete_task(self, result):
        """Mark task as completed."""
        self.completed_tasks.append({
            'task': self.current_task,
            'result': result,
            'timestamp': datetime.now()
        })
        self.current_task = None
```

### Prompt Engineering

#### Topic Generation Prompts

```python
TOPIC_GENERATION_PROMPT = """
You are a technical documentation generator. Generate content for the following topic:

Topic: {topic}
File Format: {file_format}
Context: {context}

Requirements:
1. Content should be realistic and professional
2. Include technical details appropriate for the format
3. Use industry-standard terminology
4. Maintain consistency with the specified topic
5. Content length should be appropriate for the file format

Generate content that would naturally contain credentials in a real-world scenario.
"""
```

#### Credential Embedding Prompts

```python
EMBEDDING_PROMPT = """
You are a security testing specialist. Analyze the following content and suggest natural placement points for credentials:

Content: {content}
Credential Types: {credential_types}
File Format: {file_format}

Suggest 3-5 natural embedding locations where these credentials would realistically appear.
Consider:
1. Contextual relevance
2. Natural language flow
3. Format-specific constraints
4. Realistic usage patterns

Provide specific insertion points with brief explanations.
"""
```

## Offline LLM Integration

### Model Selection Criteria

1. **Size**: Models under 4B parameters for reasonable memory usage
2. **Quantization**: Q4_K_M or Q4_0 for optimal size/quality balance
3. **Performance**: CPU-optimized inference
4. **Quality**: Sufficient for content generation tasks

### Recommended Models

| Model | Parameters | Size (Q4_K_M) | Memory Usage | Quality | Speed |
|-------|------------|---------------|--------------|---------|-------|
| TinyLlama-1.1B | 1.1B | ~1.5GB | ~2GB | Good | Very Fast |
| Phi-3-mini-4k | 3.8B | ~3GB | ~4GB | Very Good | Fast |
| Qwen2-0.5B | 0.5B | ~800MB | ~1.2GB | Good | Very Fast |
| Gemma-2B-IT | 2B | ~2.5GB | ~3GB | Good | Fast |

### Model Management

```python
class ModelManager:
    def __init__(self, models_dir):
        self.models_dir = models_dir
        self.loaded_models = {}
    
    def load_model(self, model_name):
        """Load a model if not already loaded."""
        if model_name not in self.loaded_models:
            model_path = os.path.join(self.models_dir, f"{model_name}.gguf")
            self.loaded_models[model_name] = LlamaInterface(model_path)
        return self.loaded_models[model_name]
    
    def unload_model(self, model_name):
        """Unload a model to free memory."""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
```

### Performance Optimization

```python
class PerformanceOptimizer:
    def __init__(self):
        self.cpu_count = multiprocessing.cpu_count()
        self.available_memory = psutil.virtual_memory().available
    
    def optimize_llm_config(self, model_size):
        """Optimize LLM configuration based on system resources."""
        config = {
            'n_threads': min(self.cpu_count, 8),  # Cap at 8 threads
            'n_ctx': min(2048, self.available_memory // (model_size * 2)),
            'n_batch': 512,
            'n_gpu_layers': 0  # CPU-only
        }
        return config
```

## File Format Support

CredentialForge supports a comprehensive range of file formats organized into logical categories:

### Supported Format Categories

#### Email Formats
- **EML**: Standard email message format
- **MSG**: Microsoft Outlook message format

#### Microsoft Office Excel Formats
- **XLSM**: Excel macro-enabled workbook
- **XLSX**: Excel Open XML workbook
- **XLTM**: Excel macro-enabled template
- **XLS**: Excel 97-2003 workbook
- **XLSB**: Excel binary workbook

#### Microsoft Office Word Formats
- **DOCX**: Word Open XML document
- **DOC**: Word 97-2003 document
- **DOCM**: Word macro-enabled document
- **RTF**: Rich Text Format

#### Microsoft Office PowerPoint Formats
- **PPTX**: PowerPoint Open XML presentation
- **PPT**: PowerPoint 97-2003 presentation

#### OpenDocument Formats
- **ODF**: OpenDocument text document
- **ODS**: OpenDocument spreadsheet
- **ODP**: OpenDocument presentation

#### PDF Format
- **PDF**: Portable Document Format

#### Image Formats
- **PNG**: Portable Network Graphics
- **JPG/JPEG**: Joint Photographic Experts Group
- **BMP**: Bitmap image

#### Visio Formats
- **VSD**: Visio 2003-2010 drawing
- **VSDX**: Visio drawing
- **VSDM**: Visio macro-enabled drawing
- **VSSX**: Visio stencil
- **VSSM**: Visio macro-enabled stencil
- **VSTX**: Visio template
- **VSTM**: Visio macro-enabled template

### Format-Specific Considerations

#### Email Formats (EML, MSG)
- **Structure**: MIME headers, body, attachments
- **Embedding**: In email body, headers, or attachment content
- **Realism**: Proper email formatting, realistic sender/recipient

#### Microsoft Office Excel Formats (XLSM, XLSX, XLTM, XLS, XLSB)
- **Structure**: Worksheets, cells, formulas, charts, macros
- **Embedding**: In cell values, formulas, chart data, or macro code
- **Realism**: Business-appropriate data, realistic formulas, proper macro structure

#### Microsoft Office Word Formats (DOCX, DOC, DOCM, RTF)
- **Structure**: Paragraphs, tables, images, headers/footers, macros
- **Embedding**: In document content, metadata, or macro code
- **Realism**: Professional document structure, realistic formatting

#### Microsoft Office PowerPoint Formats (PPTX, PPT)
- **Structure**: Slides, text boxes, images, notes, animations
- **Embedding**: In slide content, speaker notes, or metadata
- **Realism**: Professional presentation structure, logical flow

#### OpenDocument Formats (ODF, ODS, ODP)
- **Structure**: Open standard document formats
- **Embedding**: In document content, metadata, or embedded objects
- **Realism**: Standard-compliant structure, realistic content

#### PDF Format
- **Structure**: Pages, text, images, forms, metadata
- **Embedding**: In document content, form fields, or metadata
- **Realism**: Proper PDF structure, realistic content layout

#### Image Formats (PNG, JPG, JPEG, BMP)
- **Structure**: Pixel data, metadata, color profiles
- **Embedding**: In image metadata, EXIF data, or steganography
- **Realism**: Proper image format, realistic metadata

#### Visio Formats (VSD, VSDX, VSDM, VSSX, VSSM, VSTX, VSTM)
- **Structure**: Shapes, connectors, data fields, templates, stencils
- **Embedding**: In shape labels, data fields, metadata, or macro code
- **Realism**: Logical diagram structure, proper shape relationships

### Extensibility

```python
class SynthesizerRegistry:
    def __init__(self):
        self.synthesizers = {}
    
    def register_synthesizer(self, format_name, synthesizer_class):
        """Register a new file format synthesizer."""
        self.synthesizers[format_name] = synthesizer_class
    
    def get_synthesizer(self, format_name):
        """Get synthesizer for specified format."""
        if format_name not in self.synthesizers:
            raise ValueError(f"Unsupported format: {format_name}")
        return self.synthesizers[format_name]
```

## Security Considerations

### Data Isolation

```python
class SecurityManager:
    def __init__(self):
        self.isolation_mode = True
        self.allowed_directories = []
    
    def validate_output_directory(self, path):
        """Validate that output directory is safe."""
        if self.isolation_mode:
            # Ensure directory is within allowed paths
            if not any(path.startswith(allowed) for allowed in self.allowed_directories):
                raise SecurityError("Output directory not in allowed paths")
    
    def sanitize_content(self, content):
        """Sanitize content to prevent injection attacks."""
        # Remove potentially dangerous patterns
        # Ensure content is safe for file generation
        pass
```

### Credential Safety

```python
class CredentialSafety:
    @staticmethod
    def validate_synthetic_only(credential):
        """Ensure credential is synthetic and not real."""
        # Check against known real credential patterns
        # Validate synthetic generation markers
        pass
    
    @staticmethod
    def add_synthetic_markers(credential):
        """Add markers to indicate synthetic nature."""
        # Add prefixes/suffixes to indicate synthetic nature
        # Include generation metadata
        pass
```

## Performance Optimization

### Parallel Processing

```python
class ParallelProcessor:
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
    
    def process_batch(self, tasks):
        """Process multiple tasks in parallel."""
        futures = []
        for task in tasks:
            future = self.executor.submit(self._process_task, task)
            futures.append(future)
        
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Task failed: {e}")
        
        return results
```

### Memory Management

```python
class MemoryManager:
    def __init__(self):
        self.memory_limit = psutil.virtual_memory().total * 0.8  # 80% of total memory
        self.current_usage = 0
    
    def check_memory_usage(self):
        """Check if memory usage is within limits."""
        current = psutil.virtual_memory().used
        if current > self.memory_limit:
            self._cleanup_resources()
    
    def _cleanup_resources(self):
        """Clean up resources to free memory."""
        # Unload unused models
        # Clear caches
        # Force garbage collection
        pass
```

This architecture provides a robust, extensible foundation for CredentialForge while maintaining security, performance, and usability requirements.
