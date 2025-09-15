#!/usr/bin/env python3
"""
Test script to demonstrate fast file generation performance.
This script shows the difference between LLM-based and template-based generation.
"""

import time
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from credentialforge.agents.orchestrator import OrchestratorAgent
from credentialforge.db.regex_db import RegexDatabase
from credentialforge.llm.llama_interface import LlamaInterface

def test_generation_performance():
    """Test generation performance with different configurations."""
    
    print("🚀 Credential Forge Performance Test")
    print("=" * 50)
    
    # Test configuration
    test_config = {
        'num_files': 3,
        'formats': ['eml', 'msg'],
        'credential_types': ['api_key', 'aws_access_key', 'jwt_token'],
        'topics': ['Security Update', 'System Maintenance', 'API Integration'],
        'output_dir': './test_fast_output',
        'batch_size': 3,
        'seed': 42
    }
    
    # Load regex database
    regex_db_path = './data/regex_db.json'
    if not os.path.exists(regex_db_path):
        print(f"❌ Regex database not found at {regex_db_path}")
        return
    
    regex_db = RegexDatabase(regex_db_path)
    
    # Test 1: Fast Mode (Template-based content + Fast credentials)
    print("\n📊 Test 1: Fast Mode (Template-based content + Fast credentials)")
    print("-" * 60)
    
    fast_config = test_config.copy()
    fast_config.update({
        'use_llm_for_credentials': False,  # Fast credential generation
        'use_llm_for_content': False,      # Template-based content
    })
    
    start_time = time.time()
    
    try:
        orchestrator = OrchestratorAgent(config=fast_config)
        results = orchestrator.orchestrate_generation(fast_config)
        
        fast_time = time.time() - start_time
        
        print(f"✅ Fast Mode Results:")
        print(f"   ⏱️  Total time: {fast_time:.2f} seconds")
        print(f"   📁 Files generated: {len(results['files'])}")
        print(f"   🔑 Credentials generated: {results['metadata']['total_credentials']}")
        print(f"   📊 Files by format: {results['metadata']['files_by_format']}")
        print(f"   ⚡ Speed: {len(results['files'])/fast_time:.2f} files/second")
        
    except Exception as e:
        print(f"❌ Fast mode failed: {e}")
        fast_time = float('inf')
    
    # Test 2: Mixed Mode (LLM content + Fast credentials)
    print("\n📊 Test 2: Mixed Mode (LLM content + Fast credentials)")
    print("-" * 60)
    
    mixed_config = test_config.copy()
    mixed_config.update({
        'use_llm_for_credentials': False,  # Fast credential generation
        'use_llm_for_content': True,       # LLM-based content
    })
    
    start_time = time.time()
    
    try:
        orchestrator = OrchestratorAgent(config=mixed_config)
        results = orchestrator.orchestrate_generation(mixed_config)
        
        mixed_time = time.time() - start_time
        
        print(f"✅ Mixed Mode Results:")
        print(f"   ⏱️  Total time: {mixed_time:.2f} seconds")
        print(f"   📁 Files generated: {len(results['files'])}")
        print(f"   🔑 Credentials generated: {results['metadata']['total_credentials']}")
        print(f"   📊 Files by format: {results['metadata']['files_by_format']}")
        print(f"   ⚡ Speed: {len(results['files'])/mixed_time:.2f} files/second")
        
    except Exception as e:
        print(f"❌ Mixed mode failed: {e}")
        mixed_time = float('inf')
    
    # Test 3: Full LLM Mode (if LLM is available)
    print("\n📊 Test 3: Full LLM Mode (LLM content + LLM credentials)")
    print("-" * 60)
    
    llm_config = test_config.copy()
    llm_config.update({
        'use_llm_for_credentials': True,   # LLM-based credentials
        'use_llm_for_content': True,       # LLM-based content
    })
    
    start_time = time.time()
    
    try:
        orchestrator = OrchestratorAgent(config=llm_config)
        results = orchestrator.orchestrate_generation(llm_config)
        
        llm_time = time.time() - start_time
        
        print(f"✅ Full LLM Mode Results:")
        print(f"   ⏱️  Total time: {llm_time:.2f} seconds")
        print(f"   📁 Files generated: {len(results['files'])}")
        print(f"   🔑 Credentials generated: {results['metadata']['total_credentials']}")
        print(f"   📊 Files by format: {results['metadata']['files_by_format']}")
        print(f"   ⚡ Speed: {len(results['files'])/llm_time:.2f} files/second")
        
    except Exception as e:
        print(f"❌ Full LLM mode failed: {e}")
        llm_time = float('inf')
    
    # Performance Summary
    print("\n🏆 Performance Summary")
    print("=" * 50)
    
    if fast_time != float('inf'):
        print(f"🚀 Fast Mode:     {fast_time:.2f}s ({len(results['files'])/fast_time:.2f} files/s)")
    
    if mixed_time != float('inf'):
        speedup_mixed = mixed_time / fast_time if fast_time != float('inf') else 0
        print(f"⚡ Mixed Mode:    {mixed_time:.2f}s ({len(results['files'])/mixed_time:.2f} files/s) - {speedup_mixed:.1f}x slower")
    
    if llm_time != float('inf'):
        speedup_llm = llm_time / fast_time if fast_time != float('inf') else 0
        print(f"🤖 Full LLM Mode: {llm_time:.2f}s ({len(results['files'])/llm_time:.2f} files/s) - {speedup_llm:.1f}x slower")
    
    print(f"\n💡 Recommendation: Use Fast Mode for bulk generation!")
    print(f"   - Fast Mode is {mixed_time/fast_time:.1f}x faster than Mixed Mode" if mixed_time != float('inf') and fast_time != float('inf') else "")
    print(f"   - Fast Mode is {llm_time/fast_time:.1f}x faster than Full LLM Mode" if llm_time != float('inf') and fast_time != float('inf') else "")

if __name__ == "__main__":
    test_generation_performance()
