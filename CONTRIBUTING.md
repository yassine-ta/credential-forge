# Contributing to CredentialForge

Thank you for your interest in contributing to CredentialForge! This document provides guidelines and information for contributors.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contributing Guidelines](#contributing-guidelines)
5. [Pull Request Process](#pull-request-process)
6. [Code Style](#code-style)
7. [Testing](#testing)
8. [Documentation](#documentation)
9. [Security](#security)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Basic understanding of Python development
- Familiarity with security testing concepts

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/credential-forge.git
   cd credential-forge
   ```

3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/your-org/credential-forge.git
   ```

## Development Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install base dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### 3. Install Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

### 4. Verify Setup

```bash
# Run tests
pytest

# Check code style
black --check credentialforge/
flake8 credentialforge/

# Type checking
mypy credentialforge/
```

## Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

1. **Bug Reports**: Report bugs and issues
2. **Feature Requests**: Suggest new features
3. **Code Contributions**: Fix bugs or implement features
4. **Documentation**: Improve documentation
5. **Testing**: Add or improve tests
6. **Security**: Report security vulnerabilities

### Before Contributing

1. **Check Existing Issues**: Look for existing issues or pull requests
2. **Create an Issue**: For significant changes, create an issue first
3. **Discuss**: Engage in discussions before implementing major changes
4. **Follow Guidelines**: Adhere to coding standards and project conventions

### Development Workflow

1. **Create Branch**: Create a feature branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**: Implement your changes following the code style
3. **Test**: Ensure all tests pass
4. **Commit**: Write clear, descriptive commit messages
5. **Push**: Push your branch to your fork
6. **Pull Request**: Create a pull request

## Pull Request Process

### Before Submitting

- [ ] Code follows the project's style guidelines
- [ ] Self-review of your code has been performed
- [ ] Comments have been added to hard-to-understand areas
- [ ] Documentation has been updated accordingly
- [ ] Tests have been added/updated
- [ ] All tests pass locally
- [ ] Pre-commit hooks pass

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Test improvement

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)

## Related Issues
Closes #issue_number
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and checks
2. **Code Review**: Maintainers review the code
3. **Feedback**: Address any feedback or requested changes
4. **Approval**: Once approved, the PR will be merged

## Code Style

### Python Style

We use the following tools for code formatting and linting:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **isort**: Import sorting

### Configuration Files

#### `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

#### `pyproject.toml`
```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Code Examples

#### Good Code Style
```python
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CredentialGenerator:
    """Generate synthetic credentials using regex patterns."""
    
    def __init__(self, regex_db: 'RegexDatabase') -> None:
        """Initialize credential generator.
        
        Args:
            regex_db: Database containing regex patterns for credentials
        """
        self.regex_db = regex_db
        self.generated_credentials: set = set()
    
    def generate_credential(
        self, 
        credential_type: str, 
        context: Optional[Dict[str, str]] = None
    ) -> str:
        """Generate a synthetic credential of specified type.
        
        Args:
            credential_type: Type of credential to generate
            context: Optional context for generation
            
        Returns:
            Generated credential string
            
        Raises:
            ValueError: If credential type is not found
        """
        if credential_type not in self.regex_db.patterns:
            raise ValueError(f"Unknown credential type: {credential_type}")
        
        pattern = self.regex_db.get_pattern(credential_type)
        generator = self.regex_db.get_generator(credential_type)
        
        # Generate credential using pattern-specific logic
        credential = self._apply_generator(generator, pattern)
        
        # Ensure uniqueness
        while credential in self.generated_credentials:
            credential = self._apply_generator(generator, pattern)
        
        self.generated_credentials.add(credential)
        logger.info(f"Generated {credential_type} credential")
        
        return credential
```

#### Bad Code Style
```python
import logging

class CredentialGenerator:
    def __init__(self, regex_db):
        self.regex_db = regex_db
        self.generated_credentials = set()
    
    def generate_credential(self, credential_type, context=None):
        pattern = self.regex_db.get_pattern(credential_type)
        generator = self.regex_db.get_generator(credential_type)
        credential = self._apply_generator(generator, pattern)
        while credential in self.generated_credentials:
            credential = self._apply_generator(generator, pattern)
        self.generated_credentials.add(credential)
        return credential
```

## Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py
├── test_generators.py
├── test_synthesizers.py
├── test_agents.py
├── test_llm_interface.py
├── test_cli.py
├── test_utils.py
└── integration/
    ├── __init__.py
    ├── test_full_generation.py
    └── test_batch_processing.py
```

### Writing Tests

#### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch
from credentialforge.generators.credential_generator import CredentialGenerator
from credentialforge.db.regex_db import RegexDatabase


class TestCredentialGenerator:
    """Test cases for CredentialGenerator."""
    
    @pytest.fixture
    def mock_regex_db(self):
        """Create mock regex database."""
        db = Mock(spec=RegexDatabase)
        db.patterns = {
            'aws_access_key': {
                'regex': '^AKIA[0-9A-Z]{16}$',
                'generator': 'random_string(20, "A-Z0-9")'
            }
        }
        db.get_pattern.return_value = '^AKIA[0-9A-Z]{16}$'
        db.get_generator.return_value = 'random_string(20, "A-Z0-9")'
        return db
    
    @pytest.fixture
    def generator(self, mock_regex_db):
        """Create CredentialGenerator instance."""
        return CredentialGenerator(mock_regex_db)
    
    def test_generate_credential_success(self, generator, mock_regex_db):
        """Test successful credential generation."""
        with patch.object(generator, '_apply_generator', return_value='AKIA1234567890ABCDEF'):
            result = generator.generate_credential('aws_access_key')
            
            assert result == 'AKIA1234567890ABCDEF'
            assert result in generator.generated_credentials
            mock_regex_db.get_pattern.assert_called_once_with('aws_access_key')
            mock_regex_db.get_generator.assert_called_once_with('aws_access_key')
    
    def test_generate_credential_unknown_type(self, generator):
        """Test error handling for unknown credential type."""
        with pytest.raises(ValueError, match="Unknown credential type"):
            generator.generate_credential('unknown_type')
    
    def test_generate_credential_uniqueness(self, generator, mock_regex_db):
        """Test that generated credentials are unique."""
        with patch.object(generator, '_apply_generator') as mock_generator:
            mock_generator.side_effect = ['AKIA1234567890ABCDEF', 'AKIA0987654321FEDCBA']
            
            result1 = generator.generate_credential('aws_access_key')
            result2 = generator.generate_credential('aws_access_key')
            
            assert result1 != result2
            assert len(generator.generated_credentials) == 2
```

#### Integration Tests
```python
import pytest
import tempfile
import os
from credentialforge.agents.orchestrator import OrchestratorAgent
from credentialforge.db.regex_db import RegexDatabase


class TestFullGeneration:
    """Integration tests for full generation workflow."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_regex_db(self):
        """Create sample regex database."""
        return {
            "credentials": [
                {
                    "type": "aws_access_key",
                    "regex": "^AKIA[0-9A-Z]{16}$",
                    "description": "AWS Access Key ID",
                    "generator": "random_string(20, 'A-Z0-9')"
                }
            ]
        }
    
    def test_full_generation_workflow(self, temp_output_dir, sample_regex_db):
        """Test complete generation workflow."""
        # Create temporary regex database file
        import json
        regex_db_path = os.path.join(temp_output_dir, 'regex_db.json')
        with open(regex_db_path, 'w') as f:
            json.dump(sample_regex_db, f)
        
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Configure generation
        config = {
            'output_dir': temp_output_dir,
            'num_files': 2,
            'formats': ['eml'],
            'credential_types': ['aws_access_key'],
            'topics': ['system architecture'],
            'regex_db_path': regex_db_path
        }
        
        # Generate files
        results = orchestrator.orchestrate_generation(config)
        
        # Verify results
        assert len(results['files']) == 2
        assert all(os.path.exists(f) for f in results['files'])
        assert results['metadata']['total_credentials'] == 2
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_generators.py

# Run with coverage
pytest --cov=credentialforge --cov-report=html

# Run with verbose output
pytest -v

# Run only fast tests
pytest -m "not slow"

# Run integration tests
pytest tests/integration/
```

### Test Markers

```python
# Mark slow tests
@pytest.mark.slow
def test_large_batch_generation():
    """Test generation of large batches."""
    pass

# Mark integration tests
@pytest.mark.integration
def test_full_workflow():
    """Test complete workflow."""
    pass

# Mark LLM tests
@pytest.mark.llm
def test_llm_integration():
    """Test LLM integration."""
    pass
```

## Documentation

### Documentation Standards

1. **Docstrings**: Use Google-style docstrings
2. **Type Hints**: Include type hints for all functions
3. **Examples**: Provide usage examples
4. **API Documentation**: Keep API docs up to date

### Docstring Format

```python
def generate_credential(
    self, 
    credential_type: str, 
    context: Optional[Dict[str, str]] = None
) -> str:
    """Generate a synthetic credential of specified type.
    
    This method generates a synthetic credential that matches the specified
    type's regex pattern. The credential is guaranteed to be unique within
    the current generation session.
    
    Args:
        credential_type: Type of credential to generate (e.g., 'aws_access_key')
        context: Optional context dictionary for generation parameters
        
    Returns:
        Generated credential string that matches the type's regex pattern
        
    Raises:
        ValueError: If credential_type is not found in the regex database
        GenerationError: If credential generation fails after multiple attempts
        
    Example:
        >>> generator = CredentialGenerator(regex_db)
        >>> credential = generator.generate_credential('aws_access_key')
        >>> print(credential)
        AKIA1234567890ABCDEF
    """
```

### Documentation Updates

When making changes that affect the API or functionality:

1. Update docstrings
2. Update README.md if needed
3. Update API documentation in `docs/`
4. Add examples if introducing new features

## Security

### Security Considerations

1. **No Real Credentials**: Never use real credentials in tests or examples
2. **Synthetic Data Only**: All generated data must be synthetic
3. **Input Validation**: Validate all user inputs
4. **File System Safety**: Ensure safe file operations
5. **Memory Management**: Handle large files safely

### Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** create a public issue
2. Email security@your-org.com with details
3. Include steps to reproduce
4. Wait for response before public disclosure

### Security Checklist

- [ ] No hardcoded credentials or secrets
- [ ] Input validation implemented
- [ ] File operations are safe
- [ ] Memory usage is controlled
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies are up to date

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version bumped
- [ ] CHANGELOG.md updated
- [ ] Release notes prepared
- [ ] Security review completed

## Getting Help

### Community Support

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check existing documentation first

### Maintainer Contact

- **Email**: maintainers@your-org.com
- **GitHub**: @maintainer-username

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to CredentialForge! Your contributions help make security testing more accessible and effective.
