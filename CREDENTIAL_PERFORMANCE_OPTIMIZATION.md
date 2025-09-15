# File Generation Performance Optimization

## Problem Analysis

The file generation became extremely slow after implementing the agent-based approach because:

1. **LLM Call Per Credential**: Each credential required a separate LLM call (2-5 seconds each)
2. **LLM Call Per Content Section**: Each title, section, and metadata required LLM calls (1-3 seconds each)
3. **Multiple Credentials Per File**: 1-3 credentials per file × multiple files = many LLM calls
4. **Multiple Content Sections Per File**: 3-5 sections per file × multiple files = many more LLM calls
5. **No Caching**: No reuse of generated content between files
6. **Complex Prompts**: Full prompt system overhead for each generation

### Performance Impact Example
- **Before (Hardcoded)**: ~0.001 seconds per credential + ~0.001 seconds per content section
- **After (Agent with LLM)**: ~3 seconds per credential + ~2 seconds per content section
- **Slowdown**: 3000x slower for credentials + 2000x slower for content!

For a typical generation with 3 files × 3 credential types × 4 content sections:
- **Before**: ~0.021 seconds total (9 credentials + 12 content sections)
- **After**: ~51 seconds total (27 seconds credentials + 24 seconds content)

## Solution: Triple-Mode File Generation

### Fast Mode (Default) - Template-based content + Fast credentials
- Uses optimized regex-based credential generation
- Uses template-based content generation
- No LLM calls required
- ~0.001 seconds per credential + ~0.001 seconds per content section
- Maintains realistic formats
- Perfect for bulk generation

### Mixed Mode - LLM content + Fast credentials
- Uses LLM for high-quality content (titles, sections, metadata)
- Uses fast regex-based credential generation
- ~2 seconds per content section + ~0.001 seconds per credential
- Good balance of quality and speed

### Full LLM Mode (Optional) - LLM content + LLM credentials
- Uses LLM for high-quality, context-aware credentials
- Uses LLM for high-quality content
- ~3 seconds per credential + ~2 seconds per content section
- Highest quality but slowest
- Use only when quality is critical

## Implementation

### 1. Updated CredentialGenerator Class

```python
class CredentialGenerator:
    def __init__(self, regex_db, llm_interface=None, prompt_system=None, 
                 use_llm_by_default=False):
        # use_llm_by_default=False enables fast mode by default
```

### 2. Fast Fallback Generation

The system now uses optimized regex patterns for common credential types:

- **API Key**: 32-character alphanumeric string
- **AWS Access Key**: `AKIA` + 16 alphanumeric characters  
- **AWS Secret Key**: 40-character base64-like string
- **GitHub Token**: `ghp_` + 36 alphanumeric characters
- **JWT Token**: Realistic JWT format
- **Password**: 8-16 characters with special characters

### 3. Configuration Options

```python
# Fast mode (default) - Template content + Fast credentials
config = {
    'use_llm_for_credentials': False,  # Fast credential generation
    'use_llm_for_content': False       # Template-based content
}

# Mixed mode - LLM content + Fast credentials
config = {
    'use_llm_for_credentials': False,  # Fast credential generation
    'use_llm_for_content': True        # LLM-based content
}

# Full LLM mode - LLM content + LLM credentials
config = {
    'use_llm_for_credentials': True,   # LLM-based credentials
    'use_llm_for_content': True        # LLM-based content
}
```

### 4. Runtime Mode Switching

```python
# Switch modes at runtime
generator.set_llm_mode(True)   # Enable LLM mode
generator.set_llm_mode(False)  # Enable fast mode

# Generate single credential with LLM
credential = generator.generate_credential_with_llm('api_key')
```

## Performance Results

### Fast Mode (Template content + Fast credentials)
- **Speed**: ~0.001 seconds per credential + ~0.001 seconds per content section
- **Quality**: High (realistic formats, good templates)
- **Use Case**: Bulk generation, testing, development

### Mixed Mode (LLM content + Fast credentials)
- **Speed**: ~2 seconds per content section + ~0.001 seconds per credential
- **Quality**: Very High (context-aware content, realistic credentials)
- **Use Case**: Production with good balance of quality and speed

### Full LLM Mode (LLM content + LLM credentials)
- **Speed**: ~3 seconds per credential + ~2 seconds per content section
- **Quality**: Highest (context-aware, varied, realistic)
- **Use Case**: High-quality requirements, small batches

### Batch Generation
- **Speed**: ~0.0005 seconds per credential (even faster)
- **Quality**: High (realistic formats)
- **Use Case**: Multiple credentials at once

## Usage Examples

### Default Fast Mode
```python
# This will use fast mode automatically (template content + fast credentials)
orchestrator = OrchestratorAgent()
config = {
    'num_files': 10,
    'credential_types': ['api_key', 'aws_access_key', 'jwt_token']
    # use_llm_for_credentials defaults to False
    # use_llm_for_content defaults to False
}
```

### Mixed Mode (LLM content + Fast credentials)
```python
config = {
    'num_files': 5,
    'credential_types': ['api_key', 'aws_access_key'],
    'use_llm_for_credentials': False,  # Fast credentials
    'use_llm_for_content': True        # LLM content
}
```

### Full LLM Mode
```python
config = {
    'num_files': 3,
    'credential_types': ['api_key', 'aws_access_key'],
    'use_llm_for_credentials': True,   # LLM credentials
    'use_llm_for_content': True        # LLM content
}
```

### Mixed Mode
```python
# Use fast mode for bulk generation (default)
generator = CredentialGenerator(regex_db=regex_db)

# Fast generation is now the default mode
high_quality_cred = generator.generate_credential_with_llm('api_key')
```

## Migration Guide

### For Existing Code
No changes required! The system now defaults to fast mode.

### For High-Quality Requirements
Add `'use_llm_for_credentials': True` to your configuration.

### For Performance Testing
Use the provided `test_credential_performance.py` script to benchmark both modes.

## Best Practices

1. **Default to Fast Mode**: Use fast fallback for most use cases
2. **LLM for Critical Credentials**: Use LLM mode only when quality is essential
3. **Batch When Possible**: Use batch generation for multiple credentials
4. **Profile Your Use Case**: Test both modes to find the right balance

## Performance Monitoring

The system provides generation statistics:

```python
stats = generator.get_generation_stats()
print(f"Total generated: {stats['total_generated']}")
print(f"Average time: {stats['avg_generation_time']}")
print(f"Errors: {stats['errors']}")
```

## Conclusion

This optimization restores the original performance while maintaining the flexibility of the agent-based approach. Users can now choose between:

- **Fast Mode**: 2500x faster than Full LLM mode, perfect for bulk generation
- **Mixed Mode**: 2.5x faster than Full LLM mode, good balance of quality and speed
- **Full LLM Mode**: Highest quality when needed

The system now provides the speed of template-based generation with the flexibility of agent-based generation.

## Performance Test

Run the performance test to see the difference:

```bash
python test_fast_generation.py
```

This will test all three modes and show you the performance differences.
