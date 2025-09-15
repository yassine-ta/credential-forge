#!/usr/bin/env python3
"""Test script to verify improved content generation."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from credentialforge.agents.content_generation_agent import ContentGenerationAgent
from credentialforge.utils.prompt_system import EnhancedPromptSystem

def test_content_generation():
    """Test the improved content generation system."""
    print("Testing improved content generation system...")
    
    # Initialize the content generation agent without LLM (will use templates)
    agent = ContentGenerationAgent()
    
    # Test parameters
    topic = "DevOps Pipeline Implementation"
    credential_types = ["api_key", "database_connection"]
    language = "ja"
    format_type = "msg"
    
    print(f"\nGenerating content for:")
    print(f"  Topic: {topic}")
    print(f"  Language: {language}")
    print(f"  Format: {format_type}")
    print(f"  Credential Types: {credential_types}")
    
    try:
        # Generate content
        content_data = agent.generate_content(
            topic=topic,
            credential_types=credential_types,
            language=language,
            format_type=format_type,
            context={
                'min_credentials_per_file': 1,
                'max_credentials_per_file': 2
            }
        )
        
        print(f"\nGenerated Content:")
        print(f"  Title: {content_data['title']}")
        print(f"  Language: {content_data['language']}")
        print(f"  Format: {content_data['format_type']}")
        
        print(f"\nSections:")
        for i, section in enumerate(content_data['sections']):
            print(f"  {i+1}. {section['title']}:")
            content_preview = section['content'][:100] + "..." if len(section['content']) > 100 else section['content']
            print(f"     {content_preview}")
        
        print(f"\nCredentials:")
        for i, cred in enumerate(content_data['credentials']):
            print(f"  {i+1}. {cred['label']}: {cred['value']}")
        
        # Check for template instruction leakage
        print(f"\nQuality Check:")
        has_template_instructions = False
        for section in content_data['sections']:
            content = section['content'].lower()
            if any(phrase in content for phrase in [
                '- use', '- ensure', '- include', '- avoid', 'requirements:', 'generate only'
            ]):
                has_template_instructions = True
                print(f"  ❌ Template instructions found in {section['title']}")
        
        if not has_template_instructions:
            print(f"  ✅ No template instructions detected")
        
        # Check content quality
        empty_sections = 0
        for section in content_data['sections']:
            if len(section['content'].strip()) < 10:
                empty_sections += 1
                print(f"  ⚠️  {section['title']} section is too short")
        
        if empty_sections == 0:
            print(f"  ✅ All sections have substantial content")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during content generation: {e}")
        return False

if __name__ == "__main__":
    success = test_content_generation()
    if success:
        print(f"\n✅ Content generation test completed successfully!")
    else:
        print(f"\n❌ Content generation test failed!")
        sys.exit(1)
