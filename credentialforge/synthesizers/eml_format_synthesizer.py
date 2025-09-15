"""EML format synthesizer using agent-generated content."""

import base64
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Dict, Any

from .format_synthesizer import FormatSynthesizer
from ..utils.exceptions import SynthesizerError


class EMLFormatSynthesizer(FormatSynthesizer):
    """EML format synthesizer that structures agent-generated content."""
    
    def __init__(self, output_dir: str, ultra_fast_mode: bool = False):
        """Initialize EML format synthesizer.
        
        Args:
            output_dir: Output directory for generated files
            ultra_fast_mode: Enable ultra-fast mode with minimal validation
        """
        super().__init__(output_dir, ultra_fast_mode)
        self.format_type = 'eml'
    
    def synthesize(self, content_structure: Dict[str, Any]) -> str:
        """Structure content into EML format.
        
        Args:
            content_structure: Generated content from agents
            
        Returns:
            Path to generated EML file
        """
        try:
            # Validate content structure
            self._validate_content_structure(content_structure)
            
            # Embed credentials in content
            content_structure = self._embed_credentials_in_content(content_structure)
            
            # Create EML message
            msg = self._create_eml_message(content_structure)
            
            # Generate filename and save
            filename = self._generate_filename(content_structure)
            file_path = self._get_file_path(filename)
            
            # Save EML file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(msg.as_string())
            
            # Log stats
            self._log_generation_stats(content_structure)
            
            return str(file_path)
            
        except Exception as e:
            self.generation_stats['errors'] += 1
            raise SynthesizerError(f"EML synthesis failed: {e}")
    
    def _create_eml_message(self, content_structure: Dict[str, Any]) -> MIMEMultipart:
        """Create EML message from content structure."""
        # Create message
        msg = MIMEMultipart('alternative')
        
        # Set headers
        self._set_message_headers(msg, content_structure)
        
        # Create content from sections
        text_content, html_content = self._create_message_content(content_structure)
        
        # Add text part
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # Add HTML part
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        return msg
    
    def _set_message_headers(self, msg: MIMEMultipart, content_structure: Dict[str, Any]) -> None:
        """Set EML message headers."""
        metadata = content_structure.get('metadata', {})
        language = content_structure.get('language', 'en')
        
        # Basic headers
        msg['From'] = metadata.get('sender', 'admin@company.com')
        msg['To'] = metadata.get('recipient', 'team@company.com')
        msg['Date'] = metadata.get('date', self._get_current_date())
        msg['Message-ID'] = metadata.get('message_id', self._generate_message_id())
        msg['X-Mailer'] = 'CredentialForge/1.0'
        
        # Subject from title or metadata
        subject = content_structure.get('title', metadata.get('subject', 'System Update'))
        msg['Subject'] = subject
        
        # Language-specific headers
        if language != 'en':
            msg['Content-Language'] = language
            msg['X-Language'] = language
    
    def _create_message_content(self, content_structure: Dict[str, Any]) -> tuple[str, str]:
        """Create text and HTML content from sections."""
        sections = content_structure.get('sections', [])
        language = content_structure.get('language', 'en')
        
        # Create text content without visible section headers
        text_lines = []
        for section in sections:
            content = section.get('content', '')
            
            # Add content directly without section title headers
            if content.strip():
                text_lines.append(content)
                text_lines.append("")  # Empty line between sections
        
        text_content = "\n".join(text_lines)
        
        # Create HTML content
        html_lines = [
            "<html>",
            "<head>",
            "<meta charset='utf-8'>",
            "</head>",
            "<body>"
        ]
        
        for section in sections:
            title = section.get('title', '')
            content = section.get('content', '')
            
            if title:
                html_lines.append(f"<h2>{title}</h2>")
            
            # Convert line breaks to HTML
            html_content = content.replace('\n', '<br>')
            html_lines.append(f"<p>{html_content}</p>")
        
        html_lines.extend([
            "</body>",
            "</html>"
        ])
        
        html_content = "\n".join(html_lines)
        
        return text_content, html_content
    
    def _get_current_date(self) -> str:
        """Get current date in email format."""
        from datetime import datetime
        return datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID."""
        import random
        import time
        timestamp = int(time.time())
        random_id = random.randint(100000, 999999)
        return f"<{timestamp}.{random_id}@company.com>"
    
    def _generate_filename(self, content_structure: Dict[str, Any]) -> str:
        """Generate EML filename."""
        title = content_structure.get('title', 'email')
        timestamp = self._get_current_date().replace(':', '').replace(' ', '_')
        random_id = random.randint(1000, 9999)
        
        # Clean title for filename
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').lower()
        
        return f"email_{clean_title}_{timestamp}_{random_id}.eml"
