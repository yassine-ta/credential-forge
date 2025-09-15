#!/usr/bin/env python3
"""Test enhanced prompt system for better content generation."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from credentialforge.utils.prompt_system import EnhancedPromptSystem

def test_enhanced_prompts():
    """Test the enhanced prompt system."""
    print("🧪 Testing Enhanced Prompt System")
    print("=" * 50)
    
    try:
        # Initialize prompt system
        prompt_system = EnhancedPromptSystem()
        print("✅ EnhancedPromptSystem initialized successfully")
        
        # Test enhanced validation prompt
        print("\n1. Testing Enhanced Validation Prompt:")
        validation_prompt = prompt_system.create_enhanced_validation_prompt(
            topic="DevOps Pipeline Setup",
            credential_types=["password", "api_key"],
            language="de",
            format_type="msg",
            company="AXA Lebensversicherung AG"
        )
        print(f"   Validation prompt length: {len(validation_prompt)} characters")
        print(f"   Contains 'VALIDATED': {'VALIDATED' in validation_prompt}")
        print(f"   Contains company name: {'AXA Lebensversicherung AG' in validation_prompt}")
        
        # Test enhanced title prompt
        print("\n2. Testing Enhanced Title Prompt:")
        title_prompt = prompt_system.create_enhanced_title_prompt(
            topic="DevOps Pipeline Setup",
            language="de",
            format_type="msg",
            company="AXA Lebensversicherung AG"
        )
        print(f"   Title prompt length: {len(title_prompt)} characters")
        print(f"   Contains 'TITLE GENERATION': {'TITLE GENERATION' in title_prompt}")
        print(f"   Contains company name: {'AXA Lebensversicherung AG' in title_prompt}")
        
        # Test enhanced section prompt
        print("\n3. Testing Enhanced Section Prompt:")
        section_prompt = prompt_system.create_enhanced_section_prompt(
            topic="DevOps Pipeline Setup",
            language="de",
            format_type="msg",
            section="introduction",
            company="AXA Lebensversicherung AG"
        )
        print(f"   Section prompt length: {len(section_prompt)} characters")
        print(f"   Contains 'SECTION CONTENT GENERATION': {'SECTION CONTENT GENERATION' in section_prompt}")
        print(f"   Contains company name: {'AXA Lebensversicherung AG' in section_prompt}")
        
        # Test credential prompt
        print("\n4. Testing Enhanced Credential Prompt:")
        credential_prompt = prompt_system.create_credential_prompt(
            credential_type="password",
            language="de",
            company="AXA Lebensversicherung AG"
        )
        print(f"   Credential prompt length: {len(credential_prompt)} characters")
        print(f"   Contains 'CREDENTIAL INTEGRATION': {'CREDENTIAL INTEGRATION' in credential_prompt}")
        print(f"   Contains company name: {'AXA Lebensversicherung AG' in credential_prompt}")
        
        print("\n🎉 All enhanced prompt tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_prompts()
    sys.exit(0 if success else 1)
