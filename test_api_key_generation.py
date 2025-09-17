#!/usr/bin/env python3
"""Test script to verify API key generation is working correctly."""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_credential_generation():
    """Test credential generation directly."""
    print("🔧 Testing CredentialForge API Key Generation")
    print("=" * 50)
    
    try:
        from credentialforge.generators.credential_generator import CredentialGenerator
        from credentialforge.db.regex_db import RegexDatabase
        
        # Initialize components
        print("📄 Loading regex database...")
        regex_db = RegexDatabase('./data/regex_db.json')
        print(f"✅ Found {len(regex_db.list_credential_types())} credential types")
        
        print("\n🔑 Initializing credential generator...")
        generator = CredentialGenerator(regex_db)
        print("✅ Credential generator initialized")
        
        print("\n🧪 Testing API key generation...")
        for i in range(5):
            api_key = generator.generate_credential('api_key')
            is_valid = generator.validate_credential(api_key, 'api_key')
            
            print(f"  {i+1}. Generated: {api_key}")
            print(f"     Length: {len(api_key)} characters")
            print(f"     Valid: {is_valid}")
            
            if not is_valid:
                print(f"     ❌ FAILED: API key doesn't match regex pattern!")
                return False
        
        print("\n✅ All API keys generated successfully and are valid!")
        
        # Test the pattern directly
        pattern = regex_db.get_pattern('api_key')
        print(f"\n📋 Expected pattern: {pattern}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_interactive_compatibility():
    """Test if the generation works like the working command."""
    print("\n🎯 Testing command-line compatibility...")
    
    try:
        from credentialforge.agents.orchestrator import OrchestratorAgent
        
        # Create the same config as the working command
        config = {
            'output_dir': './test',
            'num_files': 1,
            'formats': ['pdf'],
            'credential_types': ['api_key'],
            'regex_db_path': './data/regex_db.json',
            'topics': ['Cloud security best practices and implementation'],
            'embed_strategy': 'random',
            'batch_size': 10,
            'seed': None,
            'log_level': 'INFO'
        }
        
        print("🤖 Initializing orchestrator...")
        orchestrator = OrchestratorAgent()
        
        print("🚀 Starting generation...")
        results = orchestrator.orchestrate_generation(config)
        
        print(f"📊 Results:")
        print(f"  Files generated: {len(results['files'])}")
        print(f"  Errors: {len(results['errors'])}")
        print(f"  Total credentials: {results['metadata']['total_credentials']}")
        
        if len(results['files']) > 0:
            print("✅ Generation successful!")
            return True
        else:
            print("❌ No files generated!")
            if results['errors']:
                for error in results['errors']:
                    print(f"  Error: {error}")
            return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    success = True
    
    # Test credential generation
    if not test_credential_generation():
        success = False
    
    # Test orchestrator generation
    if not test_interactive_compatibility():
        success = False
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
