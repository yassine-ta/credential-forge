#!/usr/bin/env python3
"""Simple test script to generate private_key_pem using Qwen2 model."""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.llm.multi_model_manager import MultiModelManager
from credentialforge.generators.credential_generator import CredentialGenerator
from credentialforge.db.regex_db import RegexDatabase
from credentialforge.utils.prompt_system import EnhancedPromptSystem


def generate_private_key_with_qwen2():
    """Generate a private key using Qwen2 model."""
    print("🔐 Generating Private Key with Qwen2")
    print("=" * 40)
    
    # Check if Qwen2 model exists
    qwen2_path = Path('./models/qwen2-0.5b.gguf')
    if not qwen2_path.exists():
        print(f"❌ Qwen2 model not found at {qwen2_path}")
        return None
    
    try:
        # Initialize components
        regex_db = RegexDatabase('./data/regex_db.json')
        prompt_system = EnhancedPromptSystem()
        
        # Configure Qwen2
        models_config = {
            'qwen2': {
                'model_path': './models/qwen2-0.5b.gguf',
                'tasks': ['credential_generation'],
                'description': 'Qwen2 for private key generation',
                'n_ctx': 32768,
                'temperature': 0.88,
                'max_tokens': 1024
            }
        }
        
        # Initialize multi-model manager
        multi_model_manager = MultiModelManager(models_config)
        
        # Initialize credential generator (simplified - no LLM needed)
        credential_generator = CredentialGenerator(regex_db=regex_db)
        
        # Generate private key
        context = {
            'company': 'AXA Technology Solutions',
            'topic': 'cloud infrastructure',
            'language': 'en'
        }
        
        print("🤖 Generating private key...")
        private_key = credential_generator.generate_credential('private_key_pem', context)
        
        # Display the result
        print("\n🔐 Generated Private Key:")
        print("-" * 50)
        print(private_key)
        print("-" * 50)
        
        # Validate format
        starts_correctly = private_key.startswith('-----BEGIN PRIVATE KEY-----')
        ends_correctly = private_key.endswith('-----END PRIVATE KEY-----')
        has_content = len(private_key) > 100
        
        print(f"\n✅ Format validation:")
        print(f"   Starts correctly: {starts_correctly}")
        print(f"   Ends correctly: {ends_correctly}")
        print(f"   Has content: {has_content}")
        print(f"   Length: {len(private_key)} characters")
        
        if starts_correctly and ends_correctly and has_content:
            print("\n🎉 SUCCESS: Private key generated successfully!")
            return private_key
        else:
            print("\n❌ FAILED: Private key format is incorrect")
            return None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function."""
    private_key = generate_private_key_with_qwen2()
    
    if private_key:
        print(f"\n📋 Private Key Variable Assignment:")
        print(f'private_key_pem = """{private_key}"""')
        return True
    else:
        print("\n❌ Failed to generate private key")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
