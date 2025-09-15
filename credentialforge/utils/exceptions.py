"""Custom exceptions for CredentialForge."""


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


class DatabaseError(CredentialForgeError):
    """Database error."""
    pass


class ConfigurationError(CredentialForgeError):
    """Configuration error."""
    pass


class SecurityError(CredentialForgeError):
    """Security error."""
    pass
