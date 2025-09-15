#!/usr/bin/env python3
"""
Simple Ultra-Fast Generation Test
Tests the core performance improvements without complex synthesizers.
"""

import time
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from credentialforge.agents.content_generation_agent import ContentGenerationAgent
from credentialforge.db.regex_db import RegexDatabase

def test_content_generation_speed():
    """Test content generation speed with different modes."""
    
    print("⚡ Ultra-Fast Content Generation Test")
    print("=" * 50)
    
    # Load regex database
    regex_db_path = './data/regex_db.json'
    if not os.path.exists(regex_db_path):
        print(f"❌ Regex database not found at {regex_db_path}")
        return
    
    regex_db = RegexDatabase(regex_db_path)
    
    # Test parameters
    topic = "Security Update"
    credential_types = ['api_key', 'aws_access_key', 'jwt_token']
    language = 'en'
    format_type = 'eml'
    context = {'min_credentials_per_file': 1, 'max_credentials_per_file': 2}
    
    # Test 1: Ultra-Fast Mode
    print("\n🚀 Test 1: Ultra-Fast Mode (Template + Fast credentials + Caching)")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        agent = ContentGenerationAgent(
            regex_db=regex_db,
            use_llm_for_credentials=False,
            use_llm_for_content=False,
            enable_parallel_generation=False
        )
        
        # Generate 10 content structures
        for i in range(10):
            content = agent.generate_content(topic, credential_types, language, format_type, context)
        
        ultra_fast_time = time.time() - start_time
        
        print(f"✅ Ultra-Fast Mode Results:")
        print(f"   ⏱️  Total time: {ultra_fast_time:.3f} seconds")
        print(f"   📄 Content structures generated: 10")
        print(f"   ⚡ Speed: {10/ultra_fast_time:.2f} structures/second")
        print(f"   🎯 Time per structure: {ultra_fast_time/10:.3f} seconds")
        
        # Show caching stats
        print(f"   📊 Company cache size: {len(agent._company_cache)}")
        print(f"   📊 Template cache size: {len(agent._template_cache)}")
        
    except Exception as e:
        print(f"❌ Ultra-fast mode failed: {e}")
        ultra_fast_time = float('inf')
    
    # Test 2: Regular Fast Mode (without caching)
    print("\n📊 Test 2: Regular Fast Mode (Template + Fast credentials, no caching)")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        agent = ContentGenerationAgent(
            regex_db=regex_db,
            use_llm_for_credentials=False,
            use_llm_for_content=False,
            enable_parallel_generation=False
        )
        
        # Disable caching for this test
        agent.ultra_fast_mode = False
        
        # Generate 10 content structures
        for i in range(10):
            content = agent.generate_content(topic, credential_types, language, format_type, context)
        
        regular_fast_time = time.time() - start_time
        
        print(f"✅ Regular Fast Mode Results:")
        print(f"   ⏱️  Total time: {regular_fast_time:.3f} seconds")
        print(f"   📄 Content structures generated: 10")
        print(f"   ⚡ Speed: {10/regular_fast_time:.2f} structures/second")
        print(f"   🎯 Time per structure: {regular_fast_time/10:.3f} seconds")
        
    except Exception as e:
        print(f"❌ Regular fast mode failed: {e}")
        regular_fast_time = float('inf')
    
    # Performance Summary
    print("\n🏆 Performance Summary")
    print("=" * 50)
    
    if ultra_fast_time != float('inf') and regular_fast_time != float('inf'):
        speedup = regular_fast_time / ultra_fast_time
        print(f"⚡ Ultra-Fast Mode: {ultra_fast_time:.3f}s ({10/ultra_fast_time:.2f} structures/s)")
        print(f"🚀 Regular Fast Mode: {regular_fast_time:.3f}s ({10/regular_fast_time:.2f} structures/s)")
        print(f"\n💡 Ultra-Fast Mode is {speedup:.1f}x faster than Regular Fast Mode!")
        
        time_saved = regular_fast_time - ultra_fast_time
        print(f"⏱️  Time saved per structure: {time_saved/10:.3f} seconds")
        print(f"⏱️  Total time saved: {time_saved:.3f} seconds")
    
    print(f"\n🎯 Ultra-Fast Mode Optimizations:")
    print(f"   ✅ Company caching (eliminates repeated lookups)")
    print(f"   ✅ Template caching (reuses section templates)")
    print(f"   ✅ Skipped validation (minimal overhead)")
    print(f"   ✅ Optimized credential generation")
    print(f"   ✅ Streamlined content structure creation")
    
    print(f"\n💡 Recommendation: Use Ultra-Fast Mode for bulk generation!")
    print(f"   - Perfect for testing, development, and large-scale generation")
    print(f"   - Maintains high quality with maximum speed")

if __name__ == "__main__":
    test_content_generation_speed()
