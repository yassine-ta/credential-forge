"""Validation utilities for CredentialForge."""

import re
import os
from pathlib import Path
from typing import List, Optional, Union
from .exceptions import ValidationError


class Validators:
    """Input validation utilities."""
    
    # Supported file formats - categorized by type
    SUPPORTED_FORMATS = {
        # Email formats
        'eml', 'msg',
        
        # Microsoft Office formats
        'xlsm', 'xlsx', 'xltm', 'xls', 'xlsb',  # Excel
        'docx', 'doc', 'docm', 'rtf',            # Word
        'pptx', 'ppt',                           # PowerPoint
        
        # OpenDocument formats
        'odf', 'ods', 'odp',
        
        # PDF format
        'pdf',
        
        # Image formats
        'png', 'jpg', 'jpeg', 'bmp',
        
        # Visio formats
        'vsd', 'vsdx', 'vsdm', 'vssx', 'vssm', 'vstx', 'vstm'
    }
    
    # Format categories for better organization
    FORMAT_CATEGORIES = {
        'email': {'eml', 'msg'},
        'excel': {'xlsm', 'xlsx', 'xltm', 'xls', 'xlsb', 'ods'},
        'word': {'docx', 'doc', 'docm', 'rtf', 'odf'},
        'powerpoint': {'pptx', 'ppt', 'odp'},
        'pdf': {'pdf'},
        'images': {'png', 'jpg', 'jpeg', 'bmp'},
        'visio': {'vsd', 'vsdx', 'vsdm', 'vssx', 'vssm', 'vstx', 'vstm'}
    }
    
    # Embedding strategies
    EMBED_STRATEGIES = {'random', 'metadata', 'body'}
    
    @staticmethod
    def validate_output_directory(path: Union[str, Path]) -> None:
        """Validate output directory path.
        
        Args:
            path: Directory path to validate
            
        Raises:
            ValidationError: If path is invalid
        """
        path = Path(path)
        
        # Check if path is absolute and safe
        if not path.is_absolute():
            path = path.resolve()
        
        # Check for dangerous paths (but allow temp directories)
        dangerous_patterns = [
            r'\.\.',  # Parent directory traversal
        ]
        
        path_str = str(path)
        # Allow temp directories and common safe paths
        if not any(safe in path_str.lower() for safe in ['temp', 'tmp', 'output', 'test', 'credentialforge']):
            for pattern in dangerous_patterns:
                if re.search(pattern, path_str):
                    raise ValidationError(f"Potentially dangerous path: {path}")
        
        # Create directory if it doesn't exist
        try:
            path.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise ValidationError(f"Cannot create output directory {path}: {e}")
    
    @staticmethod
    def get_format_category(format_name: str) -> Optional[str]:
        """Get the category for a file format.
        
        Args:
            format_name: Format name to categorize
            
        Returns:
            Category name or None if not found
        """
        format_name = format_name.lower()
        for category, formats in Validators.FORMAT_CATEGORIES.items():
            if format_name in formats:
                return category
        return None
    
    @staticmethod
    def get_formats_by_category(category: str) -> set:
        """Get all formats in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            Set of format names in the category
        """
        return Validators.FORMAT_CATEGORIES.get(category.lower(), set())
    
    @staticmethod
    def validate_file_format(format_name: str) -> None:
        """Validate file format.
        
        Args:
            format_name: Format name to validate
            
        Raises:
            ValidationError: If format is not supported
        """
        if format_name.lower() not in Validators.SUPPORTED_FORMATS:
            raise ValidationError(
                f"Unsupported format: {format_name}. "
                f"Supported formats: {', '.join(Validators.SUPPORTED_FORMATS)}"
            )
    
    @staticmethod
    def validate_file_formats(formats: List[str]) -> None:
        """Validate list of file formats.
        
        Args:
            formats: List of format names to validate
            
        Raises:
            ValidationError: If any format is not supported
        """
        for format_name in formats:
            Validators.validate_file_format(format_name)
    
    @staticmethod
    def validate_credential_type(credential_type: str, regex_db) -> None:
        """Validate credential type against database.
        
        Args:
            credential_type: Credential type to validate
            regex_db: RegexDatabase instance
            
        Raises:
            ValidationError: If credential type is not found
        """
        if not regex_db.has_credential_type(credential_type):
            available_types = regex_db.list_credential_types()
            raise ValidationError(
                f"Unknown credential type: {credential_type}. "
                f"Available types: {', '.join(available_types.keys())}"
            )
    
    @staticmethod
    def validate_topic(topic: str) -> None:
        """Validate topic string.
        
        Args:
            topic: Topic string to validate
            
        Raises:
            ValidationError: If topic is invalid
        """
        if not topic or not topic.strip():
            raise ValidationError("Topic cannot be empty")
        
        if len(topic.strip()) < 3:
            raise ValidationError("Topic must be at least 3 characters long")
        
        if len(topic) > 500:
            raise ValidationError("Topic must be less than 500 characters")
        
        # Check for potentially dangerous content
        dangerous_patterns = [
            r'<script',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'data:',  # Data URLs
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, topic, re.IGNORECASE):
                raise ValidationError(f"Topic contains potentially dangerous content: {pattern}")
    
    @staticmethod
    def validate_embed_strategy(strategy: str) -> None:
        """Validate embedding strategy.
        
        Args:
            strategy: Embedding strategy to validate
            
        Raises:
            ValidationError: If strategy is not supported
        """
        if strategy not in Validators.EMBED_STRATEGIES:
            raise ValidationError(
                f"Unsupported embed strategy: {strategy}. "
                f"Supported strategies: {', '.join(Validators.EMBED_STRATEGIES)}"
            )
    
    @staticmethod
    def validate_num_files(num_files: int) -> None:
        """Validate number of files.
        
        Args:
            num_files: Number of files to validate
            
        Raises:
            ValidationError: If number is invalid
        """
        if not isinstance(num_files, int):
            raise ValidationError("Number of files must be an integer")
        
        if num_files < 1:
            raise ValidationError("Number of files must be at least 1")
        
        if num_files > 10000:
            raise ValidationError("Number of files cannot exceed 10,000")
    
    @staticmethod
    def validate_batch_size(batch_size: int) -> None:
        """Validate batch size.
        
        Args:
            batch_size: Batch size to validate
            
        Raises:
            ValidationError: If batch size is invalid
        """
        if not isinstance(batch_size, int):
            raise ValidationError("Batch size must be an integer")
        
        if batch_size < 1:
            raise ValidationError("Batch size must be at least 1")
        
        if batch_size > 100:
            raise ValidationError("Batch size cannot exceed 100")
    
    @staticmethod
    def validate_file_path(file_path: Union[str, Path]) -> None:
        """Validate file path.
        
        Args:
            file_path: File path to validate
            
        Raises:
            ValidationError: If path is invalid
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ValidationError(f"File does not exist: {path}")
        
        if not path.is_file():
            raise ValidationError(f"Path is not a file: {path}")
        
        # Check file size (max 100MB)
        file_size = path.stat().st_size
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            raise ValidationError(f"File too large: {file_size} bytes (max: {max_size})")
    
    @staticmethod
    def validate_regex_pattern(pattern: str) -> None:
        """Validate regex pattern.
        
        Args:
            pattern: Regex pattern to validate
            
        Raises:
            ValidationError: If pattern is invalid
        """
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValidationError(f"Invalid regex pattern: {e}")
    
    @staticmethod
    def validate_model_path(model_path: Union[str, Path]) -> None:
        """Validate LLM model path.
        
        Args:
            model_path: Model file path to validate
            
        Raises:
            ValidationError: If path is invalid
        """
        path = Path(model_path)
        
        if not path.exists():
            raise ValidationError(f"Model file does not exist: {path}")
        
        if not path.is_file():
            raise ValidationError(f"Model path is not a file: {path}")
        
        # Check file extension
        if path.suffix.lower() not in {'.gguf', '.bin', '.safetensors'}:
            raise ValidationError(
                f"Unsupported model format: {path.suffix}. "
                "Supported formats: .gguf, .bin, .safetensors"
            )
        
        # Check file size (min 100MB, max 20GB)
        file_size = path.stat().st_size
        min_size = 100 * 1024 * 1024  # 100MB
        max_size = 20 * 1024 * 1024 * 1024  # 20GB
        
        if file_size < min_size:
            raise ValidationError(f"Model file too small: {file_size} bytes (min: {min_size})")
        
        if file_size > max_size:
            raise ValidationError(f"Model file too large: {file_size} bytes (max: {max_size})")
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe filesystem usage.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        # Remove or replace dangerous characters
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
        sanitized = re.sub(dangerous_chars, '_', filename)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Ensure filename is not empty
        if not sanitized:
            sanitized = 'unnamed_file'
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255-len(ext)] + ext
        
        return sanitized
