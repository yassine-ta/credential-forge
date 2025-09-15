"""Database-specific exceptions for CredentialForge."""

from ..utils.exceptions import CredentialForgeError


class DatabaseError(CredentialForgeError):
    """Database-related error."""
    pass
