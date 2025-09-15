"""Visio format synthesizer using agent-generated content."""

import random
from pathlib import Path
from typing import Dict, Any

from .format_synthesizer import FormatSynthesizer
from ..utils.exceptions import SynthesizerError


class VisioFormatSynthesizer(FormatSynthesizer):
    """Visio format synthesizer that structures agent-generated content."""
    
    def __init__(self, output_dir: str, format_type: str = 'vsdx', ultra_fast_mode: bool = False):
        """Initialize Visio format synthesizer.
        
        Args:
            output_dir: Output directory for generated files
            format_type: Visio format type (vsdx, vsd, vsdm, vssx, vssm, vstx, vstm)
            ultra_fast_mode: Enable ultra-fast mode with minimal validation
        """
        super().__init__(output_dir, ultra_fast_mode)
        self.format_type = format_type
    
    def synthesize(self, content_structure: Dict[str, Any]) -> str:
        """Structure content into Visio format.
        
        Args:
            content_structure: Generated content from agents
            
        Returns:
            Path to generated Visio file
        """
        try:
            # Validate content structure
            self._validate_content_structure(content_structure)
            
            # Embed credentials in content
            content_structure = self._embed_credentials_in_content(content_structure)
            
            # Generate filename and save
            filename = self._generate_filename(content_structure)
            file_path = self._get_file_path(filename)
            
            # Create Visio document (simplified XML structure)
            self._create_visio_document(content_structure, file_path)
            
            # Log stats
            self._log_generation_stats(content_structure)
            
            return str(file_path)
            
        except Exception as e:
            self.generation_stats['errors'] += 1
            raise SynthesizerError(f"Visio synthesis failed: {e}")
    
    def _create_visio_document(self, content_structure: Dict[str, Any], file_path: Path) -> None:
        """Create Visio document."""
        # Create a simplified Visio-like XML structure
        visio_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<VisioDocument xmlns="http://schemas.microsoft.com/office/visio/2012/main">
    <DocumentProperties>
        <Title>{content_structure.get('title', 'Document')}</Title>
        <Creator>CredentialForge</Creator>
        <Language>{content_structure.get('language', 'en')}</Language>
    </DocumentProperties>
    
    <Pages>
        <Page ID="0" Name="Page-1">
            <PageSheet>
                <PageProps>
                    <PageWidth>8.5</PageWidth>
                    <PageHeight>11</PageHeight>
                </PageProps>
            </PageSheet>
            
            <Shapes>
                <!-- Title Shape -->
                <Shape ID="1" Type="Shape" Name="Title">
                    <XForm>
                        <PinX>4.25</PinX>
                        <PinY>10</PinY>
                        <Width>6</Width>
                        <Height>0.5</Height>
                    </XForm>
                    <Text>
                        <cp IX="0">
                            <pp IX="0" HorzAlign="1"/>
                        </cp>
                        <tp IX="0">
                            <f IX="0">{content_structure.get('title', 'Document')}</f>
                        </tp>
                    </Text>
                </Shape>
"""
        
        # Add shapes for each section
        sections = content_structure.get('sections', [])
        shape_id = 2
        y_position = 9
        
        for i, section in enumerate(sections):
            section_title = section.get('title', 'Section')
            section_content = section.get('content', '')
            
            # Section title shape
            visio_content += f"""
                <Shape ID="{shape_id}" Type="Shape" Name="Section{i+1}_Title">
                    <XForm>
                        <PinX>1</PinX>
                        <PinY>{y_position}</PinY>
                        <Width>6</Width>
                        <Height>0.3</Height>
                    </XForm>
                    <Text>
                        <cp IX="0">
                            <pp IX="0" HorzAlign="0"/>
                        </cp>
                        <tp IX="0">
                            <f IX="0">{section_title}</f>
                        </tp>
                    </Text>
                </Shape>
"""
            shape_id += 1
            y_position -= 0.5
            
            # Section content shape
            visio_content += f"""
                <Shape ID="{shape_id}" Type="Shape" Name="Section{i+1}_Content">
                    <XForm>
                        <PinX>1.5</PinX>
                        <PinY>{y_position}</PinY>
                        <Width>5</Width>
                        <Height>0.8</Height>
                    </XForm>
                    <Text>
                        <cp IX="0">
                            <pp IX="0" HorzAlign="0"/>
                        </cp>
                        <tp IX="0">
                            <f IX="0">{section_content[:200]}...</f>
                        </tp>
                    </Text>
                </Shape>
"""
            shape_id += 1
            y_position -= 1.2
        
        # Add credentials shape if present
        credentials = content_structure.get('credentials', [])
        if credentials and y_position > 2:
            visio_content += f"""
                <Shape ID="{shape_id}" Type="Shape" Name="Credentials">
                    <XForm>
                        <PinX>1</PinX>
                        <PinY>{y_position}</PinY>
                        <Width>6</Width>
                        <Height>1</Height>
                    </XForm>
                    <Text>
                        <cp IX="0">
                            <pp IX="0" HorzAlign="0"/>
                        </cp>
                        <tp IX="0">
                            <f IX="0">Credentials:</f>
                        </tp>
                    </Text>
                </Shape>
"""
            shape_id += 1
            y_position -= 0.3
            
            for j, cred in enumerate(credentials[:3]):  # Limit to 3 credentials
                if y_position > 1:
                    label = cred.get('label', cred.get('type', 'Credential'))
                    visio_content += f"""
                <Shape ID="{shape_id}" Type="Shape" Name="Credential{j+1}">
                    <XForm>
                        <PinX>1.5</PinX>
                        <PinY>{y_position}</PinY>
                        <Width>5</Width>
                        <Height>0.2</Height>
                    </XForm>
                    <Text>
                        <cp IX="0">
                            <pp IX="0" HorzAlign="0"/>
                        </cp>
                        <tp IX="0">
                            <f IX="0">{label}: ***</f>
                        </tp>
                    </Text>
                </Shape>
"""
                    shape_id += 1
                    y_position -= 0.3
        
        visio_content += """
            </Shapes>
        </Page>
    </Pages>
</VisioDocument>
"""
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(visio_content)
    
    def _generate_filename(self, content_structure: Dict[str, Any]) -> str:
        """Generate Visio filename."""
        title = content_structure.get('title', 'diagram')
        timestamp = self._get_current_timestamp()
        random_id = random.randint(1000, 9999)
        
        # Clean title for filename
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').lower()
        
        return f"diagram_{clean_title}_{timestamp}_{random_id}.{self.format_type}"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for filename."""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')
