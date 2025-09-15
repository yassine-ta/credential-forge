"""CredentialForge - Synthetic document generation with embedded credentials."""

__version__ = "0.1.0"
__author__ = "CredentialForge Contributors"
__email__ = "maintainers@credentialforge.org"
__description__ = "Synthetic document generation with embedded credentials for security testing"

from .cli import main

__all__ = ["main", "__version__"]
