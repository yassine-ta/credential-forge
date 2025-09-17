#!/usr/bin/env python3
"""
Test script for full document generation with the fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from credentialforge.agents.orchestrator import OrchestratorAgent

def test_full_generation():
    """Test full document generation to verify the fix."""
    print("🧪 Testing Full Document Generation")
    print("=" * 50)
    
    # Create a config similar to interactive mode
    config = {
        'output_dir': './output',
        'num_files': 1,
        'formats': ['doc'],
        'credential_types': ['slack_user_token'],  # Single credential type
        'topics': ['Application Security Testing'],
        'language': 'es',
        'regex-db': './data/regex_db.json',
        'batch_size': 1,
        'use_llm_for_credentials': False,
        'use_llm_for_content': False,
        'min_credentials_per_file': 1,  # This should now generate only 1 credential
        'max_credentials_per_file': 1
    }
    
    try:
        # Initialize and run orchestrator
        orchestrator = OrchestratorAgent(config=config)
        results = orchestrator.orchestrate_generation(config)
        
        if results.get('success', False):
            print(f"✅ Generated {results.get('total_files', 0)} files successfully!")
            
            # Find the generated file
            if results.get('files'):
                file_info = results['files'][0]
                file_path = file_info.get('file_path')
                
                if file_path and os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Count credential occurrences
                    slack_count = content.count('slack_user_token_')
                    
                    print(f"📄 File: {file_path}")
                    print(f"🔍 Slack tokens found: {slack_count}")
                    
                    if slack_count == 1:
                        print("✅ SUCCESS: Only one credential generated (no duplicates)!")
                        return True
                    else:
                        print(f"❌ FAILURE: Found {slack_count} slack tokens (expected 1)")
                        return False
        else:
            print(f"❌ Generation failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_full_generation()
    print(f"\n{'🎉 TEST PASSED' if success else '💥 TEST FAILED'}")
    sys.exit(0 if success else 1)
