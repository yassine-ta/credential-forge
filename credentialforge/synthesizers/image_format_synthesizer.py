"""Image format synthesizer using agent-generated content."""

import random
from pathlib import Path
from typing import Dict, Any

from .format_synthesizer import FormatSynthesizer
from ..utils.exceptions import SynthesizerError

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ImageFormatSynthesizer(FormatSynthesizer):
    """Image format synthesizer that structures agent-generated content."""
    
    def __init__(self, output_dir: str, format_type: str = 'png', ultra_fast_mode: bool = False):
        """Initialize Image format synthesizer.
        
        Args:
            output_dir: Output directory for generated files
            format_type: Image format type (png, jpg, jpeg, bmp)
            ultra_fast_mode: Enable ultra-fast mode with minimal validation
        """
        super().__init__(output_dir, ultra_fast_mode)
        self.format_type = format_type
    
    def synthesize(self, content_structure: Dict[str, Any]) -> str:
        """Structure content into Image format.
        
        Args:
            content_structure: Generated content from agents
            
        Returns:
            Path to generated Image file
        """
        try:
            # Validate content structure
            self._validate_content_structure(content_structure)
            
            # Generate filename and save
            filename = self._generate_filename(content_structure)
            file_path = self._get_file_path(filename)
            
            if PIL_AVAILABLE:
                # Create image with PIL
                self._create_image_with_pil(content_structure, file_path)
            else:
                # Create simple text file
                self._create_simple_text_file(content_structure, file_path)
            
            # Log stats
            self._log_generation_stats(content_structure)
            
            return str(file_path)
            
        except Exception as e:
            self.generation_stats['errors'] += 1
            raise SynthesizerError(f"Image synthesis failed: {e}")
    
    def _create_image_with_pil(self, content_structure: Dict[str, Any], file_path: Path) -> None:
        """Create image using PIL."""
        # Create image
        width, height = 1000, 800
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Try to load a font, fall back to default if not available
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_medium = ImageFont.truetype("arial.ttf", 16)
            font_small = ImageFont.truetype("arial.ttf", 12)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Title
        title = content_structure.get('title', 'Document')
        title_bbox = draw.textbbox((0, 0), title, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 20), title, fill='black', font=font_large)
        
        # Metadata
        y_position = 80
        metadata = content_structure.get('metadata', {})
        if metadata:
            draw.text((20, y_position), f"Topic: {metadata.get('topic', 'N/A')}", fill='blue', font=font_medium)
            y_position += 30
            draw.text((20, y_position), f"Language: {content_structure.get('language', 'en')}", fill='blue', font=font_medium)
            y_position += 30
            draw.text((20, y_position), f"Format: {content_structure.get('format_type', 'unknown')}", fill='blue', font=font_medium)
            y_position += 40
        
        # Sections
        sections = content_structure.get('sections', [])
        for section in sections:
            section_title = section.get('title', 'Section')
            section_content = section.get('content', '')
            
            # Section title
            draw.text((20, y_position), section_title, fill='red', font=font_medium)
            y_position += 25
            
            # Section content (truncated for image)
            content_lines = section_content.split('\n')
            for line in content_lines[:3]:  # Limit to 3 lines
                if y_position > height - 50:
                    break
                if line.strip():
                    draw.text((40, y_position), line.strip()[:60], fill='black', font=font_small)
                    y_position += 20
            
            y_position += 20
        
        # Credentials (if any)
        credentials = content_structure.get('credentials', [])
        if credentials and y_position < height - 100:
            draw.text((20, y_position), "Credentials:", fill='green', font=font_medium)
            y_position += 25
            
            for cred in credentials:  # Show all credentials
                if y_position > height - 50:
                    break
                label = cred.get('label', cred.get('type', 'Credential'))
                credential_value = cred.get('value', 'N/A')
                draw.text((40, y_position), f"{label}: {credential_value}", fill='black', font=font_small)
                y_position += 20
        
        # Save image
        image.save(str(file_path))
    
    def _create_simple_text_file(self, content_structure: Dict[str, Any], file_path: Path) -> None:
        """Create simple text file."""
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
        
        # Credentials (if any)
        credentials = content_structure.get('credentials', [])
        if credentials:
            content += "\nCredentials:\n"
            content += "=" * 12 + "\n"
            for cred in credentials:
                label = cred.get('label', cred.get('type', 'Credential'))
                credential_value = cred.get('value', 'N/A')
                content += f"{label}: {credential_value}\n"
        
        # Write to file
        with open(file_path.with_suffix('.txt'), 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_filename(self, content_structure: Dict[str, Any]) -> str:
        """Generate Image filename."""
        title = content_structure.get('title', 'image')
        timestamp = self._get_current_timestamp()
        random_id = random.randint(1000, 9999)
        
        # Clean title for filename
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').lower()
        
        return f"image_{clean_title}_{timestamp}_{random_id}.{self.format_type}"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for filename."""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')
