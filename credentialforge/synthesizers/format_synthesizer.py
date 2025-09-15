"""Format-only synthesizer base class."""

import os
import random
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..utils.exceptions import SynthesizerError


class FormatSynthesizer(ABC):
    """Base class for format-only synthesizers."""
    
    def __init__(self, output_dir: str, ultra_fast_mode: bool = False):
        """Initialize format synthesizer.
        
        Args:
            output_dir: Output directory for generated files
            ultra_fast_mode: Enable ultra-fast mode with minimal validation
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ultra_fast_mode = ultra_fast_mode
        
        self.generation_stats = {
            'files_generated': 0,
            'total_credentials_embedded': 0,
            'errors': 0
        }
    
    @abstractmethod
    def synthesize(self, content_structure: Dict[str, Any]) -> str:
        """Structure content into the specific format.
        
        Args:
            content_structure: Generated content from agents
            {
                'title': 'Document Title',
                'sections': [
                    {'title': 'Section 1', 'content': '...'},
                    {'title': 'Section 2', 'content': '...'}
                ],
                'credentials': [
                    {'type': 'password', 'value': '...', 'label': 'Mot de passe'},
                    {'type': 'api_key', 'value': '...', 'label': 'Clé API'}
                ],
                'metadata': {...}
            }
            
        Returns:
            Path to generated file
            
        Raises:
            SynthesizerError: If synthesis fails
        """
        pass
    
    def _generate_filename(self, content_structure: Dict[str, Any]) -> str:
        """Generate filename based on content structure."""
        title = content_structure.get('title', 'document')
        format_type = content_structure.get('format_type', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_id = random.randint(1000, 9999)
        
        # Clean title for filename
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').lower()
        
        return f"{format_type}_{clean_title}_{timestamp}_{random_id}.{format_type}"
    
    def _get_file_path(self, filename: str) -> Path:
        """Get full file path."""
        return self.output_dir / filename
    
    def _embed_credentials_in_content(self, content_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Embed credentials into content sections."""
        credentials = content_structure.get('credentials', [])
        sections = content_structure.get('sections', [])
        
        if not credentials or not sections:
            return content_structure
        
        # Find the best section to embed credentials
        target_section = self._find_credential_section(sections)
        
        if target_section is not None:
            # Embed credentials in the target section
            credential_text = self._format_credentials_for_section(credentials, content_structure.get('language', 'en'))
            sections[target_section]['content'] += f"\n\n{credential_text}"
        
        # Update content structure
        updated_structure = content_structure.copy()
        updated_structure['sections'] = sections
        
        return updated_structure
    
    def _find_credential_section(self, sections: List[Dict[str, str]]) -> Optional[int]:
        """Find the best section to embed credentials."""
        # Look for configuration or technical details sections
        credential_keywords = ['configuration', 'config', 'technical', 'details', 'settings', 'parameters']
        
        for i, section in enumerate(sections):
            section_title = section.get('title', '').lower()
            section_content = section.get('content', '').lower()
            
            for keyword in credential_keywords:
                if keyword in section_title or keyword in section_content:
                    return i
        
        # If no specific section found, use the last section
        return len(sections) - 1 if sections else None
    
    def _format_credentials_for_section(self, credentials: List[Dict[str, str]], language: str) -> str:
        """Format credentials for embedding in a section."""
        if not credentials:
            return ""
        
        # Get appropriate header based on language
        headers = {
            'en': 'Configuration Details:',
            'fr': 'Détails de Configuration:',
            'es': 'Detalles de Configuración:',
            'de': 'Konfigurationsdetails:',
            'it': 'Dettagli di Configurazione:'
        }
        
        header = headers.get(language, headers['en'])
        
        credential_lines = [header]
        
        for cred in credentials:
            label = cred.get('label', cred.get('type', 'Credential'))
            value = cred.get('value', '')
            credential_lines.append(f"{label}: {value}")
        
        return "\n".join(credential_lines)
    
    def _validate_content_structure(self, content_structure: Dict[str, Any]) -> None:
        """Validate content structure."""
        if self.ultra_fast_mode:
            # Skip validation in ultra-fast mode
            return
            
        required_fields = ['title', 'sections', 'credentials', 'metadata']
        
        for field in required_fields:
            if field not in content_structure:
                raise SynthesizerError(f"Missing required field: {field}")
        
        if not content_structure['sections']:
            raise SynthesizerError("No sections provided")
        
        if not content_structure['credentials']:
            raise SynthesizerError("No credentials provided")
    
    def _log_generation_stats(self, content_structure: Dict[str, Any]) -> None:
        """Log generation statistics."""
        self.generation_stats['files_generated'] += 1
        self.generation_stats['total_credentials_embedded'] += len(content_structure.get('credentials', []))
