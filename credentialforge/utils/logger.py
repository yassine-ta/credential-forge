"""Logging utilities for CredentialForge."""

import logging
import logging.handlers
import structlog
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class Logger:
    """Structured logger for CredentialForge."""
    
    def __init__(self, name: str, level: int = logging.INFO, 
                 log_file: Optional[str] = None):
        """Initialize logger.
        
        Args:
            name: Logger name
            level: Logging level
            log_file: Optional log file path
        """
        self.name = name
        self.level = level
        self.log_file = log_file
        
        # Setup structured logging
        self._setup_structured_logging()
        
        # Get logger instance
        self.logger = structlog.get_logger(name)
    
    def _setup_structured_logging(self):
        """Setup structured logging configuration."""
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Setup standard library logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=self.level,
        )
        
        # Add file handler if specified
        if self.log_file:
            # Ensure log file is in project directory
            if not Path(self.log_file).is_absolute():
                project_root = Path(__file__).parent.parent.parent
                self.log_file = str(project_root / "logs" / self.log_file)
            
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setLevel(self.level)
            
            # Add handler to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, **kwargs)
    
    def log_generation(self, file_path: str, metadata: Dict[str, Any]):
        """Log file generation event."""
        self.info(
            "File generated",
            file_path=file_path,
            metadata=metadata,
            timestamp=datetime.now().isoformat()
        )
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with context."""
        self.error(
            "Error occurred",
            error=str(error),
            error_type=type(error).__name__,
            context=context or {},
            timestamp=datetime.now().isoformat()
        )
    
    def log_performance(self, operation: str, duration: float, 
                       metadata: Optional[Dict[str, Any]] = None):
        """Log performance metrics."""
        self.info(
            "Performance metric",
            operation=operation,
            duration_seconds=duration,
            metadata=metadata or {},
            timestamp=datetime.now().isoformat()
        )


# Import sys for logging setup
import sys
