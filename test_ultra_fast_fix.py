#!/usr/bin/env python3
"""
Test the ultra-fast credential generation fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from credentialforge.agents.content_generation_agent import ContentGenerationAgent
from credentialforge.db.regex_db import RegexDatabase

def test_ultra_fast_fix():
    """Test that ultra-fast mode generates proper credentials."""
    print("🧪 Testing Ultra-Fast Credential Generation Fix")
    print("=" * 60)
    
    try:
        # Initialize components
        regex_db = RegexDatabase("./data/regex_db.json")
        agent = ContentGenerationAgent(
            llm_interface=None,
            regex_db=regex_db,
            use_llm_for_credentials=False,  # This triggers ultra-fast mode
            use_llm_for_content=False       # This triggers ultra-fast mode
        )
        
        print(f"Ultra-fast mode enabled: {agent.ultra_fast_mode}")
        
        # Test ultra-fast credential generation
        print("\n📝 Testing ultra-fast credential generation...")
        credentials = agent._generate_credentials_ultra_fast(
            credential_types=['slack_user_token'],
            min_creds=1,
            max_creds=1
        )
        
        print(f"Generated {len(credentials)} credentials:")
        for i, cred in enumerate(credentials, 1):
            value = cred['value']
            print(f"  {i}. {cred['label']}: {value}")
            
            # Check if it's a proper Slack token format
            if value.startswith('xoxp-') and len(value) > 40:
                print(f"     ✅ Proper Slack token format!")
                return True
            else:
                print(f"     ❌ Wrong format - expected xoxp-..., got {value}")
                return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ultra_fast_fix()
    print(f"\n{'🎉 FIX WORKING' if success else '💥 FIX FAILED'}")
    sys.exit(0 if success else 1)
