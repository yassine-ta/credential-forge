#!/usr/bin/env python3
"""Test script to generate private_key_pem using Qwen2 model."""

import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.llm.multi_model_manager import MultiModelManager
from credentialforge.generators.credential_generator import CredentialGenerator
from credentialforge.db.regex_db import RegexDatabase
from credentialforge.utils.prompt_system import EnhancedPromptSystem


def test_private_key_generation():
    """Test private key generation using Qwen2 model."""
    print("🔐 Private Key Generation Test with Qwen2")
    print("=" * 50)
    
    # Check if Qwen2 model exists
    qwen2_path = Path('./models/qwen2-0.5b.gguf')
    if not qwen2_path.exists():
        print(f"❌ Qwen2 model not found at {qwen2_path}")
        print("Please ensure the model file exists in the models directory.")
        return False
    
    print(f"✅ Found Qwen2 model: {qwen2_path}")
    
    try:
        # Initialize components
        print("\n🔧 Initializing components...")
        
        # Initialize regex database
        regex_db = RegexDatabase('./data/regex_db.json')
        print("✅ Regex database initialized")
        
        # Initialize prompt system
        prompt_system = EnhancedPromptSystem()
        print("✅ Prompt system initialized")
        
        # Configure Qwen2 for credential generation
        models_config = {
            'qwen2': {
                'model_path': './models/qwen2-0.5b.gguf',
                'tasks': ['credential_generation', 'private_key_generation'],
                'description': 'Qwen2 model for private key generation',
                'n_ctx': 4096,
                'temperature': 0.1,  # Low temperature for consistent output
                'max_tokens': 200    # Enough for a complete private key
            }
        }
        
        # Initialize multi-model manager
        multi_model_manager = MultiModelManager(models_config)
        print("✅ Multi-model manager initialized")
        
        # Initialize credential generator with LLM enabled
        credential_generator = CredentialGenerator(
            regex_db=regex_db,
            prompt_system=prompt_system,
            multi_model_manager=multi_model_manager,
            use_llm_by_default=True  # Enable LLM for this test
        )
        print("✅ Credential generator initialized with LLM enabled")
        
        # Test private key generation
        print("\n🔑 Testing private key generation...")
        
        context = {
            'company': 'AXA Technology Solutions',
            'topic': 'cloud infrastructure',
            'language': 'en'
        }
        
        # Generate private key
        start_time = time.time()
        private_key = credential_generator.generate_credential('private_key_pem', context)
        generation_time = time.time() - start_time
        
        print(f"⏱️  Generation time: {generation_time:.2f} seconds")
        print(f"📏 Generated key length: {len(private_key)} characters")
        
        # Display the generated private key
        print("\n🔐 Generated Private Key:")
        print("-" * 50)
        print(private_key)
        print("-" * 50)
        
        # Validate the private key format
        print("\n🔍 Validating private key format...")
        
        # Check if it starts and ends correctly
        starts_correctly = private_key.startswith('-----BEGIN PRIVATE KEY-----')
        ends_correctly = private_key.endswith('-----END PRIVATE KEY-----')
        has_content = len(private_key) > 100  # Should have substantial content
        
        print(f"✅ Starts correctly: {starts_correctly}")
        print(f"✅ Ends correctly: {ends_correctly}")
        print(f"✅ Has content: {has_content}")
        
        if starts_correctly and ends_correctly and has_content:
            print("\n🎉 SUCCESS: Private key generated successfully!")
            return True
        else:
            print("\n❌ FAILED: Private key format is incorrect")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_direct_llm_generation():
    """Test direct LLM generation of private key."""
    print("\n" + "=" * 50)
    print("🔧 Direct LLM Private Key Generation Test")
    print("=" * 50)
    
    try:
        # Initialize Qwen2 directly
        models_config = {
            'qwen2': {
                'model_path': './models/qwen2-0.5b.gguf',
                'tasks': ['private_key_generation'],
                'description': 'Qwen2 for direct private key generation',
                'n_ctx': 4096,
                'temperature': 0.1,
                'max_tokens': 200
            }
        }
        
        multi_model_manager = MultiModelManager(models_config)
        
        # Create a specific prompt for private key generation
        prompt = """Generate a realistic RSA private key in PEM format for a cloud infrastructure system.

The private key must:
1. Start with: -----BEGIN PRIVATE KEY-----
2. End with: -----END PRIVATE KEY-----
3. Contain base64-encoded content between the headers (about 1600+ characters)
4. Be realistic and professional
5. Be suitable for production use

Example format:
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cKB
wEi4t82cZ7Y5yNCqQStW0h8iP7jL4P6bQb+rP3rQ2bQ3rQ4bQ5rQ6bQ7rQ8bQ9rQ
... (many more lines of base64 content) ...
AgEAAoIBAQC7VJTUt9Us8cKBwEi4t82cZ7Y5yNCqQStW0h8iP7jL4P6bQb+rP3rQ
-----END PRIVATE KEY-----

Generate the complete private key now:"""
        
        print("🤖 Generating private key with Qwen2...")
        start_time = time.time()
        
        response = multi_model_manager.generate_for_task(
            'private_key_generation',
            prompt,
            max_tokens=200,
            temperature=0.1
        )
        
        generation_time = time.time() - start_time
        
        print(f"⏱️  Generation time: {generation_time:.2f} seconds")
        print(f"📏 Response length: {len(response)} characters")
        
        # Clean up the response
        private_key = response.strip()
        
        # Display the result
        print("\n🔐 Generated Private Key:")
        print("-" * 50)
        print(private_key)
        print("-" * 50)
        
        # Validate format
        starts_correctly = private_key.startswith('-----BEGIN PRIVATE KEY-----')
        ends_correctly = private_key.endswith('-----END PRIVATE KEY-----')
        has_content = len(private_key) > 100
        
        print(f"\n✅ Starts correctly: {starts_correctly}")
        print(f"✅ Ends correctly: {ends_correctly}")
        print(f"✅ Has content: {has_content}")
        
        if starts_correctly and ends_correctly and has_content:
            print("\n🎉 SUCCESS: Direct LLM generation worked!")
            return True
        else:
            print("\n❌ FAILED: Direct LLM generation format is incorrect")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR in direct generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🚀 Private Key Generation Test Suite")
    print("=" * 60)
    
    # Test 1: Using credential generator
    success1 = test_private_key_generation()
    
    # Test 2: Direct LLM generation
    success2 = test_direct_llm_generation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Credential Generator Test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Direct LLM Test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 or success2:
        print("\n🎉 At least one test passed! Private key generation is working.")
    else:
        print("\n❌ All tests failed. Private key generation needs fixing.")
    
    return success1 or success2


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
