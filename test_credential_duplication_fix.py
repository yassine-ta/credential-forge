#!/usr/bin/env python3
"""
Test script to verify the credential duplication fix.
This script generates a simple document to check if credentials are duplicated.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from credentialforge.agents.orchestrator import OrchestratorAgent
from credentialforge.llm.llama_interface import LlamaInterface

def test_credential_duplication_fix():
    """Test that credentials are not duplicated in generated documents."""
    print("🧪 Testing Credential Duplication Fix")
    print("=" * 50)
    
    # Create a minimal config
    config = {
        'output_dir': './output',
        'num_files': 1,
        'formats': ['doc'],
        'credential_types': ['pypi_token'],
        'topics': ['Database Migration Guide'],
        'language': 'es',
        'regex_db_path': './data/regex_db.json',
        'batch_size': 1,
        'use_llm_for_credentials': False,  # Use fast generation
        'use_llm_for_content': False,     # Use fast generation
        'min_credentials_per_file': 2,
        'max_credentials_per_file': 2
    }
    
    try:
        # Initialize orchestrator without LLM for fast testing
        print("📋 Initializing orchestrator...")
        orchestrator = OrchestratorAgent(config=config)
        print("✅ Orchestrator initialized")
        
        # Generate a test document
        print("\n🚀 Generating test document...")
        results = orchestrator.orchestrate_generation(config)
        
        if results.get('success', False):
            print("✅ Document generated successfully!")
            print(f"Files generated: {results.get('total_files', 0)}")
            
            # Check the generated file for duplicate credentials
            if results.get('files'):
                file_info = results['files'][0]
                file_path = file_info.get('file_path')
                
                if file_path and os.path.exists(file_path):
                    print(f"\n📄 Checking file: {file_path}")
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Count occurrences of credential headers
                    config_details_count = content.count("Configuration Details:")
                    detalles_config_count = content.count("Detalles de Configuración:")
                    pypi_token_count = content.count("pypi_token_")
                    
                    print(f"Configuration Details: {config_details_count} occurrences")
                    print(f"Detalles de Configuración: {detalles_config_count} occurrences")
                    print(f"PyPI tokens found: {pypi_token_count} occurrences")
                    
                    # Check for duplication
                    total_headers = config_details_count + detalles_config_count
                    if total_headers <= 1:
                        print("✅ SUCCESS: No credential section duplication detected!")
                        return True
                    else:
                        print("❌ FAILURE: Credential sections are still duplicated!")
                        print("\nDocument content preview:")
                        print("-" * 40)
                        # Show first 1000 characters
                        print(content[:1000])
                        if len(content) > 1000:
                            print("...")
                        return False
                else:
                    print("❌ Generated file not found")
                    return False
            else:
                print("❌ No files in results")
                return False
        else:
            print(f"❌ Generation failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_credential_duplication_fix()
    if success:
        print("\n🎉 Test PASSED - Credential duplication fix is working!")
    else:
        print("\n💥 Test FAILED - Credential duplication still exists!")
    
    sys.exit(0 if success else 1)
