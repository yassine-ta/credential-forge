"""Configuration loader for synthesizer enhancements."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from ..utils.exceptions import ValidationError


class SynthesizerConfigLoader:
    """Loads and manages synthesizer configuration from JSON file."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration loader.
        
        Args:
            config_file: Path to synthesizer configuration JSON file
        """
        if config_file is None:
            # Default to the config file in data directory
            project_root = Path(__file__).parent.parent.parent
            config_file = project_root / "data" / "synthesizer_config.json"
        
        self.config_file = Path(config_file)
        self.config_data = self._load_config_data()
    
    def _load_config_data(self) -> Dict[str, Any]:
        """Load synthesizer configuration data from JSON file.
        
        Returns:
            Dictionary containing configuration data
            
        Raises:
            ValidationError: If configuration file cannot be loaded
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValidationError(f"Synthesizer configuration file not found: {self.config_file}")
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ValidationError(f"Error loading configuration file: {e}")
    
    def get_format_config(self, file_format: str) -> Dict[str, Any]:
        """Get configuration for a specific file format.
        
        Args:
            file_format: File format (e.g., 'docx', 'xlsx', 'pptx')
            
        Returns:
            Configuration dictionary for the format
        """
        configs = self.config_data.get('synthesizer_configurations', {})
        
        # Search through all categories
        for category, formats in configs.items():
            if file_format in formats:
                return formats[file_format]
        
        # Return default configuration if not found
        return self._get_default_config(file_format)
    
    def _get_default_config(self, file_format: str) -> Dict[str, Any]:
        """Get default configuration for a format.
        
        Args:
            file_format: File format
            
        Returns:
            Default configuration dictionary
        """
        return {
            "structure": {
                "min_pages": 2,
                "max_pages": 10,
                "sections": ["title", "content", "conclusion"],
                "headers": False,
                "footers": False,
                "page_numbers": False
            },
            "formatting": {
                "colors": {
                    "primary": ["#000000", "#333333"],
                    "secondary": ["#cccccc", "#e6e6e6"],
                    "accent": ["#0000ff", "#0066cc"]
                },
                "fonts": {
                    "heading": "Arial",
                    "body": "Arial",
                    "code": "Courier New"
                },
                "font_sizes": {
                    "title": 16,
                    "heading": 14,
                    "body": 12,
                    "caption": 10
                }
            },
            "content": {
                "include_tables": True,
                "include_charts": False,
                "include_images": False,
                "include_hyperlinks": False,
                "min_paragraphs_per_page": 2,
                "max_paragraphs_per_page": 5
            }
        }
    
    def get_structure_config(self, file_format: str) -> Dict[str, Any]:
        """Get structure configuration for a format.
        
        Args:
            file_format: File format
            
        Returns:
            Structure configuration dictionary
        """
        format_config = self.get_format_config(file_format)
        return format_config.get('structure', {})
    
    def get_formatting_config(self, file_format: str) -> Dict[str, Any]:
        """Get formatting configuration for a format.
        
        Args:
            file_format: File format
            
        Returns:
            Formatting configuration dictionary
        """
        format_config = self.get_format_config(file_format)
        return format_config.get('formatting', {})
    
    def get_content_config(self, file_format: str) -> Dict[str, Any]:
        """Get content configuration for a format.
        
        Args:
            file_format: File format
            
        Returns:
            Content configuration dictionary
        """
        format_config = self.get_format_config(file_format)
        return format_config.get('content', {})
    
    def get_colors(self, file_format: str, color_type: str = 'primary') -> list:
        """Get color palette for a format.
        
        Args:
            file_format: File format
            color_type: Type of colors ('primary', 'secondary', 'accent', 'background')
            
        Returns:
            List of color codes
        """
        formatting_config = self.get_formatting_config(file_format)
        colors = formatting_config.get('colors', {})
        return colors.get(color_type, ['#000000', '#333333'])
    
    def get_fonts(self, file_format: str) -> Dict[str, str]:
        """Get font configuration for a format.
        
        Args:
            file_format: File format
            
        Returns:
            Font configuration dictionary
        """
        formatting_config = self.get_formatting_config(file_format)
        return formatting_config.get('fonts', {
            'heading': 'Arial',
            'body': 'Arial',
            'code': 'Courier New'
        })
    
    def get_font_sizes(self, file_format: str) -> Dict[str, int]:
        """Get font size configuration for a format.
        
        Args:
            file_format: File format
            
        Returns:
            Font size configuration dictionary
        """
        formatting_config = self.get_formatting_config(file_format)
        return formatting_config.get('font_sizes', {
            'title': 16,
            'heading': 14,
            'body': 12,
            'caption': 10
        })
    
    def get_page_count(self, file_format: str) -> tuple:
        """Get page count range for a format.
        
        Args:
            file_format: File format
            
        Returns:
            Tuple of (min_pages, max_pages)
        """
        structure_config = self.get_structure_config(file_format)
        min_pages = structure_config.get('min_pages', 2)
        max_pages = structure_config.get('max_pages', 10)
        return (min_pages, max_pages)
    
    def get_sheet_count(self, file_format: str) -> tuple:
        """Get sheet count range for Excel formats.
        
        Args:
            file_format: Excel file format
            
        Returns:
            Tuple of (min_sheets, max_sheets)
        """
        structure_config = self.get_structure_config(file_format)
        min_sheets = structure_config.get('min_sheets', 2)
        max_sheets = structure_config.get('max_sheets', 5)
        return (min_sheets, max_sheets)
    
    def get_row_count(self, file_format: str) -> tuple:
        """Get row count range for Excel formats.
        
        Args:
            file_format: Excel file format
            
        Returns:
            Tuple of (min_rows, max_rows)
        """
        structure_config = self.get_structure_config(file_format)
        min_rows = structure_config.get('min_rows', 20)
        max_rows = structure_config.get('max_rows', 100)
        return (min_rows, max_rows)
    
    def get_slide_count(self, file_format: str) -> tuple:
        """Get slide count range for PowerPoint formats.
        
        Args:
            file_format: PowerPoint file format
            
        Returns:
            Tuple of (min_slides, max_slides)
        """
        structure_config = self.get_structure_config(file_format)
        min_slides = structure_config.get('min_slides', 5)
        max_slides = structure_config.get('max_slides', 15)
        return (min_slides, max_slides)
    
    def should_include_feature(self, file_format: str, feature: str) -> bool:
        """Check if a feature should be included for a format.
        
        Args:
            file_format: File format
            feature: Feature name (e.g., 'include_tables', 'include_charts')
            
        Returns:
            True if feature should be included
        """
        content_config = self.get_content_config(file_format)
        return content_config.get(feature, False)
    
    def get_supported_formats(self) -> list:
        """Get list of all supported formats in configuration.
        
        Returns:
            List of supported file formats
        """
        formats = []
        configs = self.config_data.get('synthesizer_configurations', {})
        
        for category, format_configs in configs.items():
            formats.extend(format_configs.keys())
        
        return formats
    
    def get_categories(self) -> list:
        """Get list of all configuration categories.
        
        Returns:
            List of categories
        """
        configs = self.config_data.get('synthesizer_configurations', {})
        return list(configs.keys())
    
    def validate_config(self) -> bool:
        """Validate the configuration data.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            configs = self.config_data.get('synthesizer_configurations', {})
            if not configs:
                return False
            
            # Check each category
            for category, formats in configs.items():
                if not isinstance(formats, dict):
                    return False
                
                # Check each format
                for format_name, config in formats.items():
                    if not isinstance(config, dict):
                        return False
                    
                    # Check required sections
                    required_sections = ['structure', 'formatting', 'content']
                    for section in required_sections:
                        if section not in config:
                            return False
                        if not isinstance(config[section], dict):
                            return False
            
            return True
            
        except Exception:
            return False
