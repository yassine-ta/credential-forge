"""OpenDocument format synthesizer using agent-generated content."""

import random
from pathlib import Path
from typing import Dict, Any

from .format_synthesizer import FormatSynthesizer
from ..utils.exceptions import SynthesizerError

try:
    from odf.opendocument import OpenDocumentText, OpenDocumentSpreadsheet, OpenDocumentPresentation
    from odf.text import P, H
    from odf.style import Style, TextProperties, ParagraphProperties
    ODF_AVAILABLE = True
except ImportError:
    ODF_AVAILABLE = False


class OpenDocumentFormatSynthesizer(FormatSynthesizer):
    """OpenDocument format synthesizer that structures agent-generated content."""
    
    def __init__(self, output_dir: str, format_type: str = 'odt', ultra_fast_mode: bool = False):
        """Initialize OpenDocument format synthesizer.
        
        Args:
            output_dir: Output directory for generated files
            format_type: OpenDocument format type (odt, ods, odp)
            ultra_fast_mode: Enable ultra-fast mode with minimal validation
        """
        super().__init__(output_dir, ultra_fast_mode)
        self.format_type = format_type
    
    def synthesize(self, content_structure: Dict[str, Any]) -> str:
        """Structure content into OpenDocument format.
        
        Args:
            content_structure: Generated content from agents
            
        Returns:
            Path to generated OpenDocument file
        """
        try:
            # Validate content structure
            self._validate_content_structure(content_structure)
            
            # Embed credentials in content
            content_structure = self._embed_credentials_in_content(content_structure)
            
            # Generate filename and save
            filename = self._generate_filename(content_structure)
            file_path = self._get_file_path(filename)
            
            if ODF_AVAILABLE:
                # Create OpenDocument with python-odf
                self._create_opendocument_with_odf(content_structure, file_path)
            else:
                # Create simple text-based document
                self._create_simple_document(content_structure, file_path)
            
            # Log stats
            self._log_generation_stats(content_structure)
            
            return str(file_path)
            
        except Exception as e:
            self.generation_stats['errors'] += 1
            raise SynthesizerError(f"OpenDocument synthesis failed: {e}")
    
    def _create_opendocument_with_odf(self, content_structure: Dict[str, Any], file_path: Path) -> None:
        """Create OpenDocument using python-odf."""
        if self.format_type == 'odt':
            doc = OpenDocumentText()
        elif self.format_type == 'ods':
            doc = OpenDocumentSpreadsheet()
        elif self.format_type == 'odp':
            doc = OpenDocumentPresentation()
        else:
            doc = OpenDocumentText()
        
        # Title
        title = content_structure.get('title', 'Document')
        h = H(outlinelevel=1, text=title)
        doc.text.addElement(h)
        
        # Metadata
        metadata = content_structure.get('metadata', {})
        if metadata:
            p = P(text=f"Topic: {metadata.get('topic', 'N/A')}")
            doc.text.addElement(p)
            p = P(text=f"Language: {content_structure.get('language', 'en')}")
            doc.text.addElement(p)
            p = P(text=f"Format: {content_structure.get('format_type', 'unknown')}")
            doc.text.addElement(p)
            p = P(text="")  # Empty line
            doc.text.addElement(p)
        
        # Sections
        sections = content_structure.get('sections', [])
        for section in sections:
            section_title = section.get('title', 'Section')
            section_content = section.get('content', '')
            
            # Section heading
            h = H(outlinelevel=2, text=section_title)
            doc.text.addElement(h)
            
            # Section content
            p = P(text=section_content)
            doc.text.addElement(p)
            
            # Add some spacing
            p = P(text="")
            doc.text.addElement(p)
        
        # Save document
        doc.save(str(file_path))
    
    def _create_simple_document(self, content_structure: Dict[str, Any], file_path: Path) -> None:
        """Create simple text-based document."""
        content = f"""
{content_structure.get('title', 'Document')}
{'=' * len(content_structure.get('title', 'Document'))}

"""
        
        # Metadata
        metadata = content_structure.get('metadata', {})
        if metadata:
            content += f"Topic: {metadata.get('topic', 'N/A')}\n"
            content += f"Language: {content_structure.get('language', 'en')}\n"
            content += f"Format: {content_structure.get('format_type', 'unknown')}\n\n"
        
        # Sections
        sections = content_structure.get('sections', [])
        for section in sections:
            section_title = section.get('title', 'Section')
            section_content = section.get('content', '')
            
            content += f"""
{section_title}
{'=' * len(section_title)}

{section_content}

"""
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_filename(self, content_structure: Dict[str, Any]) -> str:
        """Generate OpenDocument filename."""
        title = content_structure.get('title', 'document')
        timestamp = self._get_current_timestamp()
        random_id = random.randint(1000, 9999)
        
        # Clean title for filename
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').lower()
        
        return f"opendocument_{clean_title}_{timestamp}_{random_id}.{self.format_type}"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for filename."""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')
