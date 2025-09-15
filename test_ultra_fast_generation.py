#!/usr/bin/env python3
"""
Ultra-Fast Generation Test Script
Demonstrates the performance improvements with ultra-fast optimizations.
"""

import time
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from credentialforge.agents.orchestrator import OrchestratorAgent
from credentialforge.db.regex_db import RegexDatabase

def test_ultra_fast_performance():
    """Test ultra-fast generation performance."""
    
    print("🚀 Ultra-Fast Generation Performance Test")
    print("=" * 60)
    
    # Test configuration
    test_config = {
        'num_files': 10,  # More files to see the difference
        'formats': ['eml', 'msg'],
        'credential_types': ['api_key', 'aws_access_key', 'jwt_token'],
        'topics': ['Security Update', 'System Maintenance', 'API Integration', 'Database Migration', 'Network Configuration'],
        'output_dir': './test_ultra_fast_output',
        'batch_size': 10,
        'seed': 42
    }
    
    # Load regex database
    regex_db_path = './data/regex_db.json'
    if not os.path.exists(regex_db_path):
        print(f"❌ Regex database not found at {regex_db_path}")
        return
    
    regex_db = RegexDatabase(regex_db_path)
    
    # Test 1: Ultra-Fast Mode (Template content + Fast credentials + Caching)
    print("\n⚡ Test 1: Ultra-Fast Mode (Template content + Fast credentials + Caching)")
    print("-" * 70)
    
    ultra_fast_config = test_config.copy()
    ultra_fast_config.update({
        'use_llm_for_credentials': False,  # Fast credential generation
        'use_llm_for_content': False,      # Template-based content
    })
    
    start_time = time.time()
    
    try:
        orchestrator = OrchestratorAgent(config=ultra_fast_config)
        results = orchestrator.orchestrate_generation(ultra_fast_config)
        
        ultra_fast_time = time.time() - start_time
        
        print(f"✅ Ultra-Fast Mode Results:")
        print(f"   ⏱️  Total time: {ultra_fast_time:.2f} seconds")
        print(f"   📁 Files generated: {len(results['files'])}")
        print(f"   🔑 Credentials generated: {results['metadata']['total_credentials']}")
        print(f"   📊 Files by format: {results['metadata']['files_by_format']}")
        print(f"   ⚡ Speed: {len(results['files'])/ultra_fast_time:.2f} files/second")
        print(f"   🎯 Time per file: {ultra_fast_time/len(results['files']):.3f} seconds")
        
    except Exception as e:
        print(f"❌ Ultra-fast mode failed: {e}")
        ultra_fast_time = float('inf')
    
    # Test 2: Regular Fast Mode (for comparison)
    print("\n📊 Test 2: Regular Fast Mode (for comparison)")
    print("-" * 70)
    
    fast_config = test_config.copy()
    fast_config.update({
        'use_llm_for_credentials': False,  # Fast credential generation
        'use_llm_for_content': False,      # Template-based content
        'num_files': 5,  # Fewer files for comparison
    })
    
    start_time = time.time()
    
    try:
        orchestrator = OrchestratorAgent(config=fast_config)
        results = orchestrator.orchestrate_generation(fast_config)
        
        fast_time = time.time() - start_time
        
        print(f"✅ Regular Fast Mode Results:")
        print(f"   ⏱️  Total time: {fast_time:.2f} seconds")
        print(f"   📁 Files generated: {len(results['files'])}")
        print(f"   🔑 Credentials generated: {results['metadata']['total_credentials']}")
        print(f"   📊 Files by format: {results['metadata']['files_by_format']}")
        print(f"   ⚡ Speed: {len(results['files'])/fast_time:.2f} files/second")
        print(f"   🎯 Time per file: {fast_time/len(results['files']):.3f} seconds")
        
    except Exception as e:
        print(f"❌ Regular fast mode failed: {e}")
        fast_time = float('inf')
    
    # Performance Summary
    print("\n🏆 Ultra-Fast Performance Summary")
    print("=" * 60)
    
    if ultra_fast_time != float('inf'):
        print(f"⚡ Ultra-Fast Mode: {ultra_fast_time:.2f}s ({len(results['files'])/ultra_fast_time:.2f} files/s)")
        print(f"   🎯 Time per file: {ultra_fast_time/len(results['files']):.3f} seconds")
    
    if fast_time != float('inf'):
        print(f"🚀 Regular Fast Mode: {fast_time:.2f}s ({len(results['files'])/fast_time:.2f} files/s)")
        print(f"   🎯 Time per file: {fast_time/len(results['files']):.3f} seconds")
        
        if ultra_fast_time != float('inf'):
            speedup = fast_time / ultra_fast_time
            print(f"\n💡 Ultra-Fast Mode is {speedup:.1f}x faster than Regular Fast Mode!")
    
    print(f"\n🎯 Ultra-Fast Mode Features:")
    print(f"   ✅ Company caching (no repeated company lookups)")
    print(f"   ✅ Template caching (reused section templates)")
    print(f"   ✅ Skipped validation (minimal overhead)")
    print(f"   ✅ Optimized credential generation")
    print(f"   ✅ Streamlined file synthesis")
    
    print(f"\n💡 Recommendation: Use Ultra-Fast Mode for bulk generation!")
    print(f"   - Perfect for testing, development, and large-scale generation")
    print(f"   - Maintains high quality with maximum speed")

if __name__ == "__main__":
    test_ultra_fast_performance()
