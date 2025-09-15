#!/usr/bin/env python3
"""
Debug script for credential generation testing.
This script generates content as text for easier debugging of credential issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from credentialforge.agents.content_generation_agent import ContentGenerationAgent
from credentialforge.llm.llama_interface import LlamaInterface
from credentialforge.db.regex_db import RegexDatabase
from credentialforge.utils.prompt_system import EnhancedPromptSystem

def test_credential_generation():
    """Test credential generation with debug output."""
    print("🔍 Starting Credential Generation Debug Test")
    print("=" * 60)
    
    # Initialize components
    print("📋 Initializing components...")
    
    # Initialize LLM
    try:
        llm = LlamaInterface("models/phi3-mini.gguf")
        print("✅ LLM initialized successfully")
    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
        llm = None
    
    # Initialize regex database
    try:
        regex_db = RegexDatabase("data/regex_db.json")
        print("✅ Regex database initialized successfully")
    except Exception as e:
        print(f"❌ Regex database initialization failed: {e}")
        regex_db = None
    
    # Initialize content generation agent
    try:
        agent = ContentGenerationAgent(
            llm_interface=llm,
            regex_db=regex_db,
            enable_parallel_generation=False  # Disable for easier debugging
        )
        print("✅ Content generation agent initialized successfully")
    except Exception as e:
        print(f"❌ Content generation agent initialization failed: {e}")
        return
    
    # Test credential generation
    print("\n🔑 Testing credential generation...")
    print("-" * 40)
    
    # Test parameters
    topic = "Azure development speech to text"
    credential_types = ["password", "jwt_token"]
    language = "fr"  # French
    format_type = "txt"
    
    print(f"Topic: {topic}")
    print(f"Credential Types: {credential_types}")
    print(f"Language: {language}")
    print(f"Format: {format_type}")
    
    # Generate content
    try:
        print("\n🚀 Generating content...")
        content_data = agent.generate_content(
            topic=topic,
            credential_types=credential_types,
            language=language,
            format_type=format_type,
            context={
                'min_credentials_per_file': 1,
                'max_credentials_per_file': 3
            }
        )
        
        print("✅ Content generation completed!")
        
        # Display results
        print("\n📄 Generated Content:")
        print("=" * 60)
        print(f"Title: {content_data.get('title', 'N/A')}")
        print(f"Language: {content_data.get('language', 'N/A')}")
        print(f"Format: {content_data.get('format_type', 'N/A')}")
        
        # Display sections
        sections = content_data.get('sections', [])
        print(f"\n📝 Sections ({len(sections)}):")
        for i, section in enumerate(sections, 1):
            print(f"\n{i}. {section.get('title', 'Untitled')}")
            print(f"   Content: {section.get('content', 'No content')[:100]}...")
        
        # Display credentials
        credentials = content_data.get('credentials', [])
        print(f"\n🔐 Credentials ({len(credentials)}):")
        for i, cred in enumerate(credentials, 1):
            print(f"\n{i}. Type: {cred.get('type', 'Unknown')}")
            print(f"   Label: {cred.get('label', 'No label')}")
            print(f"   Value: '{cred.get('value', 'No value')}'")
            print(f"   Value Length: {len(cred.get('value', ''))}")
        
        # Display metadata
        metadata = content_data.get('metadata', {})
        print(f"\n📊 Metadata:")
        for key, value in metadata.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"❌ Content generation failed: {e}")
        import traceback
        traceback.print_exc()

def test_individual_credential_generation():
    """Test individual credential generation methods."""
    print("\n🔧 Testing Individual Credential Generation")
    print("=" * 60)
    
    # Initialize components
    try:
        llm = LlamaInterface("models/phi3-mini.gguf")
        regex_db = RegexDatabase("data/regex_db.json")
        agent = ContentGenerationAgent(
            llm_interface=llm,
            regex_db=regex_db,
            enable_parallel_generation=False
        )
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    # Test individual credential types
    credential_types = ["password", "jwt_token", "api_key"]
    language = "fr"
    
    for cred_type in credential_types:
        print(f"\n🔑 Testing {cred_type} generation:")
        print("-" * 30)
        
        try:
            # Test credential value generation
            value = agent._generate_credential_value(cred_type, language)
            print(f"   Generated Value: '{value}'")
            print(f"   Value Length: {len(value)}")
            print(f"   Is Empty: {value == ''}")
            
            # Test credential with label
            credentials = agent._generate_credentials_with_labels([cred_type], language, 1, 1)
            if credentials:
                cred = credentials[0]
                print(f"   With Label: {cred.get('label', 'No label')}")
                print(f"   Final Value: '{cred.get('value', 'No value')}'")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")

def test_prompt_system():
    """Test the prompt system for credential generation."""
    print("\n📝 Testing Prompt System")
    print("=" * 60)
    
    try:
        prompt_system = EnhancedPromptSystem()
        
        # Test credential prompt creation
        credential_type = "password"
        language = "fr"
        company = "Test Company"
        
        prompt = prompt_system.create_credential_prompt(
            credential_type=credential_type,
            language=language,
            company=company
        )
        
        print(f"Generated Prompt for {credential_type} in {language}:")
        print("-" * 40)
        print(prompt)
        
    except Exception as e:
        print(f"❌ Prompt system test failed: {e}")

if __name__ == "__main__":
    print("🧪 CredentialForge Debug Test Suite")
    print("=" * 60)
    
    # Run tests
    test_credential_generation()
    test_individual_credential_generation()
    test_prompt_system()
    
    print("\n✅ Debug test completed!")
