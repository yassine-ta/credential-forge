#!/usr/bin/env python3
"""
Quick test script for credential duplication fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from credentialforge.agents.content_generation_agent import ContentGenerationAgent
from credentialforge.db.regex_db import RegexDatabase

def test_credential_generation():
    """Test credential generation with different scenarios."""
    print("🧪 Testing Credential Generation Logic")
    print("=" * 50)
    
    try:
        # Initialize components
        regex_db = RegexDatabase("./data/regex_db.json")
        agent = ContentGenerationAgent(
            llm_interface=None,
            regex_db=regex_db,
            use_llm_for_credentials=False
        )
        
        # Test scenario 1: Single credential type with min/max = 2
        print("\n📝 Test 1: Single credential type (slack_user_token)")
        credentials = agent._generate_credentials_with_labels(
            credential_types=['slack_user_token'],
            language='en',
            min_creds=2,
            max_creds=2
        )
        
        print(f"Generated {len(credentials)} credentials:")
        for i, cred in enumerate(credentials, 1):
            print(f"  {i}. {cred['label']}: {cred['value']}")
        
        # Test scenario 2: Multiple credential types
        print("\n📝 Test 2: Multiple credential types")
        credentials = agent._generate_credentials_with_labels(
            credential_types=['slack_user_token', 'api_key', 'jwt_token'],
            language='en',
            min_creds=2,
            max_creds=2
        )
        
        print(f"Generated {len(credentials)} credentials:")
        for i, cred in enumerate(credentials, 1):
            print(f"  {i}. {cred['label']}: {cred['value']}")
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_credential_generation()
    sys.exit(0 if success else 1)
