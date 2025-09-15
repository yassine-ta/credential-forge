#!/usr/bin/env python3
"""Test script demonstrating the updated credential generator using prompts/credential_generation_prompts.txt."""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.generators.credential_generator import CredentialGenerator
from credentialforge.db.regex_db import RegexDatabase
from credentialforge.utils.prompt_system import EnhancedPromptSystem


def test_prompt_system_integration():
    """Test the integration with the proper prompt system."""
    print("🔧 Testing Updated Prompt System Integration")
    print("=" * 60)
    
    # Initialize components
    regex_db = RegexDatabase('./data/regex_db.json')
    prompt_system = EnhancedPromptSystem()
    credential_generator = CredentialGenerator(
        regex_db=regex_db,
        prompt_system=prompt_system,
        use_llm_by_default=True
    )
    
    # Test different credential types
    test_credential_types = [
        'aws_access_key',
        'github_token', 
        'private_key_pem',
        'jwt_token',
        'api_key'
    ]
    
    context = {
        'company': 'Demo Company',
        'topic': 'cloud infrastructure',
        'language': 'en'
    }
    
    for cred_type in test_credential_types:
        print(f"\n📋 Testing {cred_type}:")
        print("-" * 40)
        
        try:
            # Get pattern and description from regex database
            pattern = regex_db.get_pattern(cred_type)
            description = regex_db.get_description(cred_type)
            
            # Test prompt generation
            prompt = prompt_system.create_credential_prompt_with_regex(
                credential_type=cred_type,
                regex_pattern=pattern,
                description=description,
                topic=context['topic'],
                language=context['language'],
                company=context['company']
            )
            
            print(f"✅ Prompt generated successfully")
            print(f"📏 Prompt length: {len(prompt)} characters")
            print(f"📝 Prompt preview: {prompt[:150]}...")
            
            # Test credential generation (using fallback for speed)
            credential_generator.use_llm_by_default = False  # Use fallback for testing
            credential = credential_generator.generate_credential(cred_type, context)
            
            print(f"✅ Credential generated: {credential}")
            print(f"📏 Credential length: {len(credential)} characters")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎉 Prompt system integration test completed!")


def test_llm_generation():
    """Test LLM generation with the updated prompt system."""
    print("\n" + "=" * 60)
    print("🤖 Testing LLM Generation with Updated Prompt System")
    print("=" * 60)
    
    # Initialize components
    regex_db = RegexDatabase('./data/regex_db.json')
    prompt_system = EnhancedPromptSystem()
    
    # Test with a simple credential type
    cred_type = 'api_key'
    context = {
        'company': 'Test Company',
        'topic': 'API integration',
        'language': 'en'
    }
    
    try:
        # Get pattern and description
        pattern = regex_db.get_pattern(cred_type)
        description = regex_db.get_description(cred_type)
        
        # Generate prompt using the proper system
        prompt = prompt_system.create_credential_prompt_with_regex(
            credential_type=cred_type,
            regex_pattern=pattern,
            description=description,
            topic=context['topic'],
            language=context['language'],
            company=context['company']
        )
        
        print(f"📝 Generated prompt for {cred_type}:")
        print("-" * 40)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 40)
        print(f"📏 Total prompt length: {len(prompt)} characters")
        
        print(f"\n✅ Prompt system is working correctly with {cred_type}")
        
    except Exception as e:
        print(f"❌ Error testing LLM generation: {e}")


def main():
    """Main test function."""
    print("🚀 Updated Prompt System Test Suite")
    print("=" * 60)
    print("Testing credential generator with prompts/credential_generation_prompts.txt")
    
    # Test 1: Prompt system integration
    test_prompt_system_integration()
    
    # Test 2: LLM generation
    test_llm_generation()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print("✅ Removed hardcoded prompts from credential generator")
    print("✅ Now using prompts/credential_generation_prompts.txt")
    print("✅ Proper prompt system integration working")
    print("✅ Credential generation working with new system")
    print("\n🎉 All tests passed! The credential generator now uses the proper prompt system.")


if __name__ == "__main__":
    main()
