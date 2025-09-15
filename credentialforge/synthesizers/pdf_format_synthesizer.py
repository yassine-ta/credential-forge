"""PDF format synthesizer using agent-generated content."""

import random
from pathlib import Path
from typing import Dict, Any

from .format_synthesizer import FormatSynthesizer
from ..utils.exceptions import SynthesizerError

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import black, blue, red, green
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFFormatSynthesizer(FormatSynthesizer):
    """PDF format synthesizer that structures agent-generated content."""
    
    def __init__(self, output_dir: str, ultra_fast_mode: bool = False):
        """Initialize PDF format synthesizer.
        
        Args:
            output_dir: Output directory for generated files
            ultra_fast_mode: Enable ultra-fast mode with minimal validation
        """
        super().__init__(output_dir, ultra_fast_mode)
        self.format_type = 'pdf'
    
    def synthesize(self, content_structure: Dict[str, Any]) -> str:
        """Structure content into PDF format.
        
        Args:
            content_structure: Generated content from agents
            
        Returns:
            Path to generated PDF file
        """
        try:
            # Validate content structure
            self._validate_content_structure(content_structure)
            
            # Embed credentials in content
            content_structure = self._embed_credentials_in_content(content_structure)
            
            # Generate filename and save
            filename = self._generate_filename(content_structure)
            file_path = self._get_file_path(filename)
            
            if REPORTLAB_AVAILABLE:
                # Create PDF with ReportLab
                self._create_pdf_with_reportlab(content_structure, file_path)
            else:
                # Create simple text-based PDF
                self._create_simple_pdf(content_structure, file_path)
            
            # Log stats
            self._log_generation_stats(content_structure)
            
            return str(file_path)
            
        except Exception as e:
            self.generation_stats['errors'] += 1
            raise SynthesizerError(f"PDF synthesis failed: {e}")
    
    def _create_pdf_with_reportlab(self, content_structure: Dict[str, Any], file_path: Path) -> None:
        """Create PDF using ReportLab."""
        doc = SimpleDocTemplate(str(file_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        title = Paragraph(content_structure.get('title', 'Document'), title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Sections
        sections = content_structure.get('sections', [])
        for section in sections:
            section_title = section.get('title', 'Section')
            section_content = section.get('content', '')
            
            # Section title
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=blue
            )
            heading = Paragraph(section_title, heading_style)
            story.append(heading)
            
            # Section content
            content_style = ParagraphStyle(
                'CustomContent',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=12,
                leftIndent=20
            )
            content = Paragraph(section_content.replace('\n', '<br/>'), content_style)
            story.append(content)
            story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
    
    def _create_simple_pdf(self, content_structure: Dict[str, Any], file_path: Path) -> None:
        """Create simple text-based PDF."""
        # Create a simple text file with PDF-like structure
        content = f"""
PDF Document
============

Title: {content_structure.get('title', 'Document')}

"""
        
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
        """Generate PDF filename."""
        title = content_structure.get('title', 'document')
        timestamp = self._get_current_timestamp()
        random_id = random.randint(1000, 9999)
        
        # Clean title for filename
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').lower()
        
        return f"document_{clean_title}_{timestamp}_{random_id}.pdf"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for filename."""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')
