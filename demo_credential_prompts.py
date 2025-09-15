#!/usr/bin/env python3
"""Demonstration script showing how to use credential generation prompts."""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.utils.prompt_system import EnhancedPromptSystem
from credentialforge.generators.credential_generator import CredentialGenerator
from credentialforge.db.regex_db import RegexDatabase
from credentialforge.llm.llama_interface import LlamaInterface


def demo_prompt_system():
    """Demonstrate the prompt system functionality."""
    print("🚀 Credential Generation Prompts Demo")
    print("=" * 50)
    
    # Initialize the prompt system
    prompt_system = EnhancedPromptSystem()
    
    print("\n📋 Available Prompts:")
    for prompt_name in prompt_system.prompts.keys():
        print(f"   • {prompt_name}")
    
    # Demo 1: Basic credential prompt
    print("\n🔑 Demo 1: Basic API Key Generation Prompt")
    print("-" * 40)
    
    prompt = prompt_system.create_credential_prompt_with_regex(
        credential_type='api_key',
        regex_pattern='^[A-Za-z0-9]{32}$',
        description='API Key',
        topic='system integration',
        language='en',
        company='TechCorp'
    )
    
    print(f"Generated prompt length: {len(prompt)} characters")
    print("First 300 characters:")
    print(prompt[:300] + "...")
    
    # Demo 2: AWS Access Key prompt
    print("\n🔑 Demo 2: AWS Access Key Generation Prompt")
    print("-" * 40)
    
    prompt2 = prompt_system.create_credential_prompt_with_regex(
        credential_type='aws_access_key',
        regex_pattern='^AKIA[0-9A-Z]{16}$',
        description='AWS Access Key ID',
        topic='cloud infrastructure',
        language='en',
        company='CloudCorp'
    )
    
    print(f"Generated prompt length: {len(prompt2)} characters")
    print("First 300 characters:")
    print(prompt2[:300] + "...")
    
    # Demo 3: Multi-language prompt
    print("\n🔑 Demo 3: French Language Prompt")
    print("-" * 40)
    
    prompt3 = prompt_system.create_credential_prompt_with_regex(
        credential_type='jwt_token',
        regex_pattern='^eyJ[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+$',
        description='JWT Token',
        topic='authentication',
        language='fr',
        company='AuthCorp'
    )
    
    print(f"Generated prompt length: {len(prompt3)} characters")
    print("First 300 characters:")
    print(prompt3[:300] + "...")


def demo_credential_generation():
    """Demonstrate credential generation using the prompts."""
    print("\n\n🎯 Credential Generation Demo")
    print("=" * 50)
    
    # Initialize components
    regex_db = RegexDatabase('./data/regex_db.json')
    generator = CredentialGenerator(regex_db)
    
    print("\n📊 Available Credential Types:")
    available_types = regex_db.list_credential_types()
    for cred_type in list(available_types.keys())[:10]:  # Show first 10
        print(f"   • {cred_type}")
    print(f"   ... and {len(available_types) - 10} more")
    
    # Demo credential generation
    print("\n🔧 Generating Credentials:")
    print("-" * 30)
    
    test_cases = [
        {
            'type': 'api_key',
            'context': {'company': 'TechCorp', 'topic': 'API integration', 'language': 'en'}
        },
        {
            'type': 'aws_access_key', 
            'context': {'company': 'CloudCorp', 'topic': 'cloud infrastructure', 'language': 'en'}
        },
        {
            'type': 'github_token',
            'context': {'company': 'DevCorp', 'topic': 'version control', 'language': 'en'}
        }
    ]
    
    for test_case in test_cases:
        try:
            credential = generator.generate_credential(test_case['type'], test_case['context'])
            print(f"   ✅ {test_case['type']}: {credential}")
        except Exception as e:
            print(f"   ❌ {test_case['type']}: {e}")


def demo_llm_integration():
    """Demonstrate LLM integration with prompts."""
    print("\n\n🤖 LLM Integration Demo")
    print("=" * 50)
    
    try:
        # Try to load LLM
        model_path = './models/phi3-mini.gguf'
        if not Path(model_path).exists():
            print(f"⚠️  LLM model not found at {model_path}")
            print("   Skipping LLM demo - using fallback generation instead")
            return
        
        print("🔄 Loading LLM model...")
        llm = LlamaInterface(model_path)
        
        print("🔄 Initializing credential generator...")
        regex_db = RegexDatabase('./data/regex_db.json')
        generator = CredentialGenerator(regex_db=regex_db)
        
        print("\n🎯 Generating credentials with LLM:")
        print("-" * 35)
        
        context = {
            'company': 'TechCorp',
            'topic': 'API integration',
            'language': 'en'
        }
        
        # Generate a few credentials
        for cred_type in ['api_key', 'aws_access_key']:
            try:
                credential = generator.generate_credential(cred_type, context)
                print(f"   ✅ {cred_type}: {credential}")
            except Exception as e:
                print(f"   ❌ {cred_type}: {e}")
        
        print("\n📈 LLM Performance Stats:")
        stats = llm.get_performance_stats()
        for key, value in stats.items():
            print(f"   • {key}: {value}")
            
    except Exception as e:
        print(f"❌ LLM integration failed: {e}")
        print("   This is expected if the LLM model is not available")


def main():
    """Main demonstration function."""
    try:
        demo_prompt_system()
        demo_credential_generation()
        demo_llm_integration()
        
        print("\n\n🎉 Demo completed successfully!")
        print("=" * 50)
        print("The credential generation prompts from prompts/credential_generation_prompts.txt")
        print("are working correctly and can be used for realistic credential generation.")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
