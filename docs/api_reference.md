# CredentialForge API Reference

## Table of Contents

1. [CLI Commands](#cli-commands)
2. [Core Modules](#core-modules)
3. [Agent API](#agent-api)
4. [Generator API](#generator-api)
5. [Synthesizer API](#synthesizer-api)
6. [LLM Interface API](#llm-interface-api)
7. [Utility API](#utility-api)
8. [Configuration API](#configuration-api)

## CLI Commands

### Main Commands

#### `credentialforge generate`

Generate synthetic documents with embedded credentials.

**Usage:**
```bash
credentialforge generate [OPTIONS]
```

**Options:**

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--output-dir` | TEXT | Yes | - | Output directory for generated files |
| `--num-files` | INTEGER | No | 1 | Number of files to generate |
| `--formats` | TEXT | No | eml | Comma-separated formats (eml,msg,xlsx,pptx,vsdx) |
| `--credential-types` | TEXT | Yes | - | Comma-separated credential types |
| `--regex-db` | TEXT | Yes | - | Path to regex database file |
| `--topics` | TEXT | Yes | - | Comma-separated topics for content generation |
| `--embed-strategy` | TEXT | No | random | Embedding strategy (random,metadata,body) |
| `--batch-size` | INTEGER | No | 10 | Batch size for parallel processing |
| `--seed` | INTEGER | No | - | Random seed for reproducible results |
| `--llm-model` | TEXT | No | - | Path to GGUF model file |
| `--log-level` | TEXT | No | INFO | Logging level (DEBUG,INFO,WARNING,ERROR) |

**Examples:**
```bash
# Basic generation
credentialforge generate \
  --output-dir ./docs \
  --num-files 5 \
  --formats eml,excel \
  --credential-types aws_key,db_connection \
  --regex-db ./patterns.json \
  --topics "system architecture"

# Advanced generation with LLM
credentialforge generate \
  --output-dir ./test_docs \
  --num-files 100 \
  --formats eml,excel,pptx \
  --credential-types aws_key,jwt_token,api_key \
  --regex-db ./regex_db.json \
  --topics "microservices,API documentation,database design" \
  --embed-strategy body \
  --batch-size 20 \
  --llm-model ./models/phi-3-mini-4k.Q4_K_M.gguf \
  --log-level DEBUG
```

#### `credentialforge interactive`

Launch interactive terminal mode for guided generation.

**Usage:**
```bash
credentialforge interactive
```

**Interactive Features:**
- Step-by-step parameter configuration
- Real-time validation
- Content preview
- Progress tracking
- Error handling with retry options

#### `credentialforge validate`

Validate generated files for credential detectability and content quality.

**Usage:**
```bash
credentialforge validate --file PATH [OPTIONS]
```

**Options:**

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--file` | TEXT | Yes | - | Path to file to validate |
| `--regex-db` | TEXT | No | - | Path to regex database for validation |
| `--verbose` | FLAG | No | False | Show detailed validation results |

**Examples:**
```bash
# Validate single file
credentialforge validate --file ./docs/fake_001.eml

# Validate with custom regex database
credentialforge validate \
  --file ./docs/fake_001.eml \
  --regex-db ./custom_patterns.json \
  --verbose
```

#### `credentialforge db`

Manage regex database.

**Subcommands:**

##### `credentialforge db add`

Add new credential type to database.

**Usage:**
```bash
credentialforge db add --type TYPE --regex PATTERN --description DESC [OPTIONS]
```

**Options:**

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--type` | TEXT | Yes | - | Credential type identifier |
| `--regex` | TEXT | Yes | - | Regex pattern for validation |
| `--description` | TEXT | Yes | - | Human-readable description |
| `--generator` | TEXT | No | - | Generator function specification |
| `--db-file` | TEXT | No | regex_db.json | Database file path |

**Examples:**
```bash
# Add new credential type
credentialforge db add \
  --type github_token \
  --regex "^ghp_[A-Za-z0-9]{36}$" \
  --description "GitHub Personal Access Token" \
  --generator "random_string(40, 'A-Za-z0-9')"

# Add to custom database
credentialforge db add \
  --type custom_api_key \
  --regex "^[A-Z]{3}_[0-9]{8}$" \
  --description "Custom API Key Format" \
  --db-file ./custom_db.json
```

##### `credentialforge db list`

List all credential types in database.

**Usage:**
```bash
credentialforge db list [OPTIONS]
```

**Options:**

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--db-file` | TEXT | No | regex_db.json | Database file path |
| `--format` | TEXT | No | table | Output format (table,json,yaml) |

**Examples:**
```bash
# List all types
credentialforge db list

# List with custom format
credentialforge db list --format json --db-file ./custom_db.json
```

## Core Modules

### Orchestrator Agent

The main orchestrator that coordinates the generation process.

#### `agents.orchestrator.OrchestratorAgent`

```python
class OrchestratorAgent:
    def __init__(self, llm_interface=None, config=None):
        """
        Initialize the orchestrator agent.
        
        Args:
            llm_interface: Optional LLM interface for content generation
            config: Configuration object with generation parameters
        """
    
    def orchestrate_generation(self, config):
        """
        Orchestrate the complete generation process.
        
        Args:
            config: Generation configuration
            
        Returns:
            dict: Generation results with metadata
        """
    
    def generate_batch(self, config, batch_size=10):
        """
        Generate a batch of files.
        
        Args:
            config: Generation configuration
            batch_size: Number of files per batch
            
        Returns:
            list: List of generated file paths
        """
```

**Example Usage:**
```python
from credentialforge.agents.orchestrator import OrchestratorAgent
from credentialforge.llm.llama_interface import LlamaInterface

# Initialize with LLM
llm = LlamaInterface("./models/tinyllama-1.1b.Q4_K_M.gguf")
orchestrator = OrchestratorAgent(llm_interface=llm)

# Configure generation
config = {
    'output_dir': './output',
    'num_files': 10,
    'formats': ['eml', 'excel'],
    'credential_types': ['aws_key', 'jwt_token'],
    'topics': ['system architecture', 'API documentation'],
    'regex_db_path': './regex_db.json'
}

# Generate files
results = orchestrator.orchestrate_generation(config)
print(f"Generated {len(results['files'])} files")
```

### Credential Generator

Generates synthetic credentials using regex patterns.

#### `generators.credential_generator.CredentialGenerator`

```python
class CredentialGenerator:
    def __init__(self, regex_db):
        """
        Initialize credential generator.
        
        Args:
            regex_db: RegexDatabase instance
        """
    
    def generate_credential(self, credential_type, context=None):
        """
        Generate a synthetic credential.
        
        Args:
            credential_type: Type of credential to generate
            context: Optional context for generation
            
        Returns:
            str: Generated credential
        """
    
    def generate_batch(self, credential_types, count=1):
        """
        Generate multiple credentials.
        
        Args:
            credential_types: List of credential types
            count: Number of credentials per type
            
        Returns:
            dict: Mapping of types to generated credentials
        """
    
    def validate_credential(self, credential, credential_type):
        """
        Validate a generated credential against its pattern.
        
        Args:
            credential: Credential to validate
            credential_type: Type of credential
            
        Returns:
            bool: True if valid
        """
```

**Example Usage:**
```python
from credentialforge.generators.credential_generator import CredentialGenerator
from credentialforge.db.regex_db import RegexDatabase

# Initialize
db = RegexDatabase('./regex_db.json')
generator = CredentialGenerator(db)

# Generate single credential
aws_key = generator.generate_credential('aws_access_key')
print(f"Generated AWS key: {aws_key}")

# Generate batch
credentials = generator.generate_batch(['aws_access_key', 'jwt_token'], count=5)
for cred_type, creds in credentials.items():
    print(f"{cred_type}: {creds}")
```

### Topic Generator

Generates topic-specific content using LLM.

#### `generators.topic_generator.TopicGenerator`

```python
class TopicGenerator:
    def __init__(self, llm_interface):
        """
        Initialize topic generator.
        
        Args:
            llm_interface: LLM interface for content generation
        """
    
    def generate_topic_content(self, topic, file_format, context=None):
        """
        Generate topic-specific content.
        
        Args:
            topic: Topic for content generation
            file_format: Target file format
            context: Optional context information
            
        Returns:
            str: Generated content
        """
    
    def generate_multiple_topics(self, topics, file_format):
        """
        Generate content for multiple topics.
        
        Args:
            topics: List of topics
            file_format: Target file format
            
        Returns:
            dict: Mapping of topics to generated content
        """
```

**Example Usage:**
```python
from credentialforge.generators.topic_generator import TopicGenerator
from credentialforge.llm.llama_interface import LlamaInterface

# Initialize with LLM
llm = LlamaInterface('./models/phi-3-mini-4k.Q4_K_M.gguf')
generator = TopicGenerator(llm)

# Generate content for specific topic
content = generator.generate_topic_content(
    topic="microservices architecture",
    file_format="eml",
    context="email documentation"
)
print(content)

# Generate for multiple topics
topics = ["API documentation", "database design", "security policies"]
contents = generator.generate_multiple_topics(topics, "excel")
for topic, content in contents.items():
    print(f"{topic}: {content[:100]}...")
```

## Synthesizer API

### Base Synthesizer

All file format synthesizers inherit from the base synthesizer.

#### `synthesizers.base.BaseSynthesizer`

```python
class BaseSynthesizer(ABC):
    def __init__(self, output_dir):
        """
        Initialize base synthesizer.
        
        Args:
            output_dir: Output directory for generated files
        """
    
    @abstractmethod
    def synthesize(self, topic_content, credentials, metadata):
        """
        Synthesize a file with embedded credentials.
        
        Args:
            topic_content: Generated topic content
            credentials: List of credentials to embed
            metadata: Additional metadata
            
        Returns:
            str: Path to generated file
        """
    
    def _embed_credentials(self, content, credentials, strategy):
        """
        Embed credentials into content.
        
        Args:
            content: Content to embed credentials into
            credentials: List of credentials
            strategy: Embedding strategy
            
        Returns:
            str: Content with embedded credentials
        """
```

### EML Synthesizer

Generates email files in EML format.

#### `synthesizers.eml_synthesizer.EMLSynthesizer`

```python
class EMLSynthesizer(BaseSynthesizer):
    def synthesize(self, topic_content, credentials, metadata):
        """
        Generate EML file with embedded credentials.
        
        Args:
            topic_content: Email content
            credentials: Credentials to embed
            metadata: Email metadata (sender, recipient, subject)
            
        Returns:
            str: Path to generated EML file
        """
    
    def _create_email_structure(self, content, metadata):
        """Create proper email MIME structure."""
    
    def _embed_in_body(self, content, credentials):
        """Embed credentials in email body."""
    
    def _embed_in_headers(self, headers, credentials):
        """Embed credentials in email headers."""
```

**Example Usage:**
```python
from credentialforge.synthesizers.eml_synthesizer import EMLSynthesizer

# Initialize
synthesizer = EMLSynthesizer('./output')

# Generate email
metadata = {
    'sender': 'admin@company.com',
    'recipient': 'dev@company.com',
    'subject': 'System Architecture Documentation'
}

credentials = ['AKIA1234567890ABCDEF', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...']

file_path = synthesizer.synthesize(
    topic_content="System architecture overview with API integration...",
    credentials=credentials,
    metadata=metadata
)
print(f"Generated EML: {file_path}")
```

### Excel Synthesizer

Generates Excel files with embedded credentials.

#### `synthesizers.excel_synthesizer.ExcelSynthesizer`

```python
class ExcelSynthesizer(BaseSynthesizer):
    def synthesize(self, topic_content, credentials, metadata):
        """
        Generate Excel file with embedded credentials.
        
        Args:
            topic_content: Spreadsheet content
            credentials: Credentials to embed
            metadata: Spreadsheet metadata
            
        Returns:
            str: Path to generated Excel file
        """
    
    def _create_worksheets(self, content, credentials):
        """Create multiple worksheets with content."""
    
    def _embed_in_cells(self, worksheet, credentials):
        """Embed credentials in cell values."""
    
    def _embed_in_formulas(self, worksheet, credentials):
        """Embed credentials in formulas."""
```

**Example Usage:**
```python
from credentialforge.synthesizers.excel_synthesizer import ExcelSynthesizer

# Initialize
synthesizer = ExcelSynthesizer('./output')

# Generate spreadsheet
metadata = {
    'title': 'API Configuration',
    'author': 'System Admin',
    'worksheets': ['Configuration', 'Credentials', 'Endpoints']
}

credentials = ['AKIA1234567890ABCDEF', 'mysql://user:pass@host:3306/db']

file_path = synthesizer.synthesize(
    topic_content="API configuration spreadsheet with connection details...",
    credentials=credentials,
    metadata=metadata
)
print(f"Generated Excel: {file_path}")
```

## LLM Interface API

### Llama Interface

Interface for offline LLM inference using llama.cpp.

#### `llm.llama_interface.LlamaInterface`

```python
class LlamaInterface:
    def __init__(self, model_path, n_threads=None, n_ctx=2048):
        """
        Initialize Llama interface.
        
        Args:
            model_path: Path to GGUF model file
            n_threads: Number of threads for inference
            n_ctx: Context window size
        """
    
    def generate(self, prompt, max_tokens=512, temperature=0.7, stop=None):
        """
        Generate text using the loaded model.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop: Stop sequences
            
        Returns:
            str: Generated text
        """
    
    def generate_with_context(self, prompt, context, max_tokens=512):
        """
        Generate text with additional context.
        
        Args:
            prompt: Input prompt
            context: Additional context
            max_tokens: Maximum tokens to generate
            
        Returns:
            str: Generated text
        """
    
    def get_model_info(self):
        """
        Get information about the loaded model.
        
        Returns:
            dict: Model information
        """
```

**Example Usage:**
```python
from credentialforge.llm.llama_interface import LlamaInterface

# Initialize
llm = LlamaInterface(
    model_path='./models/tinyllama-1.1b.Q4_K_M.gguf',
    n_threads=4,
    n_ctx=2048
)

# Generate content
prompt = "Generate technical documentation for a microservices architecture:"
response = llm.generate(
    prompt=prompt,
    max_tokens=256,
    temperature=0.7
)
print(response)

# Generate with context
context = "Focus on API integration and database connections."
response = llm.generate_with_context(
    prompt=prompt,
    context=context,
    max_tokens=256
)
print(response)

# Get model info
info = llm.get_model_info()
print(f"Model: {info['name']}, Parameters: {info['parameters']}")
```

## Utility API

### Logger

Structured logging for the application.

#### `utils.logger.Logger`

```python
class Logger:
    def __init__(self, name, level=logging.INFO, log_file=None):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            level: Logging level
            log_file: Optional log file path
        """
    
    def log_generation(self, file_path, metadata):
        """Log file generation event."""
    
    def log_error(self, error, context=None):
        """Log error with context."""
    
    def log_performance(self, operation, duration, metadata=None):
        """Log performance metrics."""
```

### Validators

Input validation utilities.

#### `utils.validators.Validators`

```python
class Validators:
    @staticmethod
    def validate_output_directory(path):
        """Validate output directory path."""
    
    @staticmethod
    def validate_file_format(format_name):
        """Validate file format."""
    
    @staticmethod
    def validate_credential_type(credential_type, regex_db):
        """Validate credential type against database."""
    
    @staticmethod
    def validate_topic(topic):
        """Validate topic string."""
```

### Interactive Terminal

Interactive terminal utilities.

#### `utils.interactive.InteractiveTerminal`

```python
class InteractiveTerminal:
    def __init__(self):
        """Initialize interactive terminal."""
    
    def collect_parameters(self):
        """Collect user parameters interactively."""
    
    def preview_generation(self, config):
        """Preview generation before execution."""
    
    def show_progress(self, current, total, operation):
        """Show progress during generation."""
```

## Configuration API

### Configuration Manager

Manages application configuration.

#### `utils.config.ConfigManager`

```python
class ConfigManager:
    def __init__(self, config_file=None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Optional configuration file path
        """
    
    def get(self, key, default=None):
        """Get configuration value."""
    
    def set(self, key, value):
        """Set configuration value."""
    
    def load_from_file(self, file_path):
        """Load configuration from file."""
    
    def save_to_file(self, file_path):
        """Save configuration to file."""
```

**Example Usage:**
```python
from credentialforge.utils.config import ConfigManager

# Initialize
config = ConfigManager('./config.json')

# Set values
config.set('default_output_dir', './output')
config.set('default_batch_size', 10)
config.set('llm_model_path', './models/tinyllama-1.1b.Q4_K_M.gguf')

# Get values
output_dir = config.get('default_output_dir', './default_output')
batch_size = config.get('default_batch_size', 5)

# Save configuration
config.save_to_file('./config.json')
```

## Error Handling

### Custom Exceptions

```python
class CredentialForgeError(Exception):
    """Base exception for CredentialForge."""
    pass

class ValidationError(CredentialForgeError):
    """Validation error."""
    pass

class GenerationError(CredentialForgeError):
    """Generation error."""
    pass

class LLMError(CredentialForgeError):
    """LLM-related error."""
    pass

class SynthesizerError(CredentialForgeError):
    """Synthesizer error."""
    pass
```

### Error Handling Examples

```python
from credentialforge.exceptions import ValidationError, GenerationError

try:
    # Validate input
    if not output_dir:
        raise ValidationError("Output directory is required")
    
    # Generate files
    results = orchestrator.orchestrate_generation(config)
    
except ValidationError as e:
    logger.error(f"Validation error: {e}")
    sys.exit(1)
    
except GenerationError as e:
    logger.error(f"Generation error: {e}")
    # Handle partial results
    
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    sys.exit(1)
```

This API reference provides comprehensive documentation for all CredentialForge components, enabling developers to integrate and extend the system effectively.
