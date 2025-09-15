"""Native components for CredentialForge."""

try:
    from . import credential_utils
    from . import llama_cpp_interface
    from . import cpu_optimizer
    from . import memory_manager
    from . import parallel_executor
    
    NATIVE_AVAILABLE = True
except ImportError:
    NATIVE_AVAILABLE = False
    # Don't print error message on every import - this is expected behavior

__all__ = ['NATIVE_AVAILABLE']
