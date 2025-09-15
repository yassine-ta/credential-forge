#!/usr/bin/env python3
"""
Test script to check CredentialGenerator initialization in orchestrator flow.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from credentialforge.agents.orchestrator import OrchestratorAgent
from credentialforge.llm.llama_interface import LlamaInterface

def test_orchestrator_credential_generation():
    """Test credential generation through the orchestrator."""
    print("🔍 Testing Orchestrator Credential Generation")
    print("=" * 60)
    
    # Create config similar to CLI
    config = {
        'output_dir': 'output',
        'num_files': 1,
        'formats': ['jpeg'],
        'credential_types': ['password', 'jwt_token'],
        'topics': ['Azure development speech to text'],
        'regex_db': 'data/regex_db.json',
        'language': 'fr'
    }
    
    print("📋 Configuration:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    # Initialize orchestrator
    print("\n🚀 Initializing Orchestrator...")
    try:
        orchestrator = OrchestratorAgent(config=config)
        print("✅ Orchestrator initialized successfully")
        
        # Check if content generation agent is initialized
        if orchestrator.content_generation_agent:
            print("✅ Content generation agent is initialized")
            
            # Check if credential generator is initialized
            if orchestrator.content_generation_agent.credential_generator:
                print("✅ CredentialGenerator is initialized")
                
                # Test credential generation directly
                print("\n🔑 Testing direct credential generation...")
                try:
                    password_cred = orchestrator.content_generation_agent._generate_credential_value('password', 'fr')
                    print(f"   Password: '{password_cred}' (length: {len(password_cred)})")
                    
                    jwt_cred = orchestrator.content_generation_agent._generate_credential_value('jwt_token', 'fr')
                    print(f"   JWT Token: '{jwt_cred}' (length: {len(jwt_cred)})")
                    
                except Exception as e:
                    print(f"   ❌ Direct credential generation failed: {e}")
            else:
                print("❌ CredentialGenerator is NOT initialized")
        else:
            print("❌ Content generation agent is NOT initialized")
            
    except Exception as e:
        print(f"❌ Orchestrator initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_orchestrator_credential_generation()
