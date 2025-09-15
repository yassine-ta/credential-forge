# Multi-Model Configuration Guide

## Overview

The multi-model system allows you to use different LLM models for different tasks, optimizing performance and quality based on your specific needs.

## Available Models

| Model | Size | Memory | Speed | Quality | Best Use Case |
|-------|------|--------|-------|---------|---------------|
| **TinyLlama-1.1B** | 1.5GB | 2GB | Very Fast | Good | Credential generation, simple tasks |
| **Qwen2-0.5B** | 800MB | 1.2GB | Very Fast | Good | Content generation, balanced tasks |
| **Phi-3-mini-4k** | 3GB | 4GB | Fast | Very Good | High-quality content, complex tasks |

## Configuration Examples

### 1. Basic Multi-Model Setup

```python
from credentialforge.llm.multi_model_manager import MultiModelManager

# Define model configuration
models_config = {
    'tinyllama': {
        'model_path': './models/tinyllama.gguf',
        'tasks': ['credential_generation', 'topic_generation'],
        'description': 'Fast, lightweight model for simple tasks',
        'n_ctx': 2048,
        'temperature': 0.1,
        'max_tokens': 50
    },
    'qwen2': {
        'model_path': './models/qwen2-0.5b.gguf',
        'tasks': ['content_generation', 'email_content'],
        'description': 'Balanced model for content generation',
        'n_ctx': 4096,
        'temperature': 0.3,
        'max_tokens': 200
    },
    'phi3': {
        'model_path': './models/phi3-mini.gguf',
        'tasks': ['high_quality_content', 'complex_topics'],
        'description': 'High-quality model for complex tasks',
        'n_ctx': 4096,
        'temperature': 0.2,
        'max_tokens': 300
    }
}

# Initialize multi-model manager
manager = MultiModelManager(models_config)
```

### 2. Using Multi-Model with Credential Generator

```python
from credentialforge.generators.credential_generator import CredentialGenerator
from credentialforge.db.regex_db import RegexDatabase

# Initialize credential generator with multi-model manager
regex_db = RegexDatabase('./data/regex_db.json')
generator = CredentialGenerator(
    regex_db=regex_db,
    multi_model_manager=manager,  # Use multi-model manager
    use_llm_by_default=True       # Enable LLM mode
)

# Generate credentials (will use TinyLlama for credential_generation task)
api_key = generator.generate_credential('api_key')
aws_key = generator.generate_credential('aws_access_key')
```

### 3. Using Multi-Model with Content Generation Agent

```python
from credentialforge.agents.content_generation_agent import ContentGenerationAgent

# Initialize content generation agent with multi-model manager
content_agent = ContentGenerationAgent(
    multi_model_manager=manager,
    regex_db=regex_db,
    use_llm_for_credentials=True
)

# Generate content (will use appropriate models for different tasks)
content_data = content_agent.generate_content(
    topic='API Security',
    language='en',
    format_type='eml',
    template={'sections': ['introduction', 'main_content']},
    credential_types=['api_key', 'jwt_token'],
    context={'company': 'TechCorp'}
)
```

### 4. Direct Task-Based Generation

```python
# Generate content using specific models for specific tasks
topic = manager.generate_for_task('topic_generation', 'Generate a technical topic about cloud security')
content = manager.generate_for_task('content_generation', 'Write about API security best practices')
high_quality = manager.generate_for_task('high_quality_content', 'Create detailed JWT token explanation')
```

## Task-to-Model Mapping

The system automatically routes tasks to appropriate models:

| Task | Model | Reason |
|------|-------|--------|
| `credential_generation` | TinyLlama | Fast, simple output |
| `topic_generation` | TinyLlama | Quick topic suggestions |
| `content_generation` | Qwen2 | Balanced quality/speed |
| `email_content` | Qwen2 | Good for structured content |
| `high_quality_content` | Phi-3 | Best quality output |
| `complex_topics` | Phi-3 | Handles complex reasoning |

## Performance Optimization

### 1. Model Selection Strategy

```python
# For bulk generation (fastest)
config = {
    'use_llm_for_credentials': False  # Use fast fallback
}

# For quality-critical generation
config = {
    'use_llm_for_credentials': True,  # Use LLM mode
    'models_config': {
        'tinyllama': {'tasks': ['credential_generation']},
        'phi3': {'tasks': ['high_quality_content']}
    }
}
```

### 2. Memory Management

```python
# Check memory usage
memory_info = manager.get_memory_usage()
print(f"Memory: {memory_info['total_memory_mb']:.1f} MB")

# Unload unused models to free memory
manager.unload_model('phi3')  # Free 4GB memory
```

### 3. Dynamic Model Loading

```python
# Add models at runtime
manager.add_model(
    name='custom_model',
    model_path='./models/custom.gguf',
    tasks=['custom_task'],
    description='Custom model for specific needs'
)
```

## Configuration Examples by Use Case

### Development/Testing (Fast)
```python
models_config = {
    'tinyllama': {
        'model_path': './models/tinyllama.gguf',
        'tasks': ['credential_generation', 'topic_generation', 'content_generation'],
        'temperature': 0.1,
        'max_tokens': 100
    }
}
```

### Production (Balanced)
```python
models_config = {
    'tinyllama': {
        'model_path': './models/tinyllama.gguf',
        'tasks': ['credential_generation', 'topic_generation']
    },
    'qwen2': {
        'model_path': './models/qwen2-0.5b.gguf',
        'tasks': ['content_generation', 'email_content']
    }
}
```

### High-Quality (Best Quality)
```python
models_config = {
    'tinyllama': {
        'model_path': './models/tinyllama.gguf',
        'tasks': ['credential_generation']
    },
    'phi3': {
        'model_path': './models/phi3-mini.gguf',
        'tasks': ['content_generation', 'high_quality_content', 'complex_topics']
    }
}
```

## Integration with Orchestrator

```python
from credentialforge.agents.orchestrator import OrchestratorAgent

# Configure orchestrator with multi-model support
config = {
    'output_dir': './output',
    'num_files': 10,
    'formats': ['eml', 'xlsx'],
    'credential_types': ['api_key', 'aws_access_key'],
    'topics': ['API Security', 'Cloud Integration'],
    'use_llm_for_credentials': True,
    'multi_model_config': {
        'tinyllama': {'tasks': ['credential_generation']},
        'qwen2': {'tasks': ['content_generation']}
    }
}

# Initialize orchestrator with multi-model manager
manager = MultiModelManager(config['multi_model_config'])
orchestrator = OrchestratorAgent()
orchestrator.initialize_with_multi_model(manager)

# Generate files using different models for different tasks
results = orchestrator.generate_files(config)
```

## Best Practices

1. **Start Simple**: Begin with TinyLlama for all tasks, then add specialized models
2. **Monitor Memory**: Use `get_memory_usage()` to track memory consumption
3. **Task-Specific Models**: Use appropriate models for specific tasks
4. **Fallback Strategy**: Always have fast fallback mode as backup
5. **Model Caching**: Keep frequently used models loaded
6. **Quality vs Speed**: Balance model selection based on your needs

## Troubleshooting

### Model Not Loading
```python
# Check if model file exists
from pathlib import Path
model_path = Path('./models/tinyllama.gguf')
if not model_path.exists():
    print("Model file not found!")
```

### Memory Issues
```python
# Unload unused models
manager.unload_model('phi3')

# Use fast fallback for bulk operations
config['use_llm_for_credentials'] = False
```

### Task Routing Issues
```python
# Check task mapping
task_mapping = manager.get_task_mapping()
print(f"Task mapping: {task_mapping}")

# Manually specify model for task
response = manager.generate_for_task('content_generation', prompt)
```

This multi-model system gives you the flexibility to use the right model for the right task, optimizing both performance and quality based on your specific needs.
