#!/usr/bin/env python3
"""Test script to demonstrate credential generation performance improvements."""

import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.generators.credential_generator import CredentialGenerator
from credentialforge.db.regex_db import RegexDatabase
from credentialforge.utils.prompt_system import EnhancedPromptSystem


def test_credential_performance():
    """Test credential generation performance with different modes."""
    print("🚀 Credential Generation Performance Test")
    print("=" * 50)
    
    # Initialize components
    regex_db = RegexDatabase('./data/regex_db.json')
    prompt_system = EnhancedPromptSystem()
    
    # Test credential types
    credential_types = ['api_key', 'aws_access_key', 'jwt_token', 'github_token', 'password']
    
    print(f"\n📊 Testing {len(credential_types)} credential types:")
    for cred_type in credential_types:
        print(f"   • {cred_type}")
    
    # Test 1: Fast Fallback Mode (Default)
    print(f"\n⚡ Test 1: Fast Fallback Mode (Default)")
    print("-" * 40)
    
    generator_fast = CredentialGenerator(
        regex_db=regex_db,
        llm_interface=None,  # No LLM for fast mode
        prompt_system=prompt_system,
        use_llm_by_default=False
    )
    
    start_time = time.time()
    fast_results = []
    
    for cred_type in credential_types:
        credential = generator_fast.generate_credential(cred_type)
        fast_results.append(credential)
        print(f"   {cred_type}: {credential[:20]}...")
    
    fast_time = time.time() - start_time
    print(f"\n⏱️  Fast mode total time: {fast_time:.3f} seconds")
    print(f"   Average per credential: {fast_time/len(credential_types):.3f} seconds")
    
    # Test 2: LLM Mode (if available)
    print(f"\n🤖 Test 2: LLM Mode (if LLM available)")
    print("-" * 40)
    
    try:
        from credentialforge.llm.llama_interface import LlamaInterface
        
        # Try to initialize LLM
        llm = LlamaInterface()
        llm.initialize_model('tinyllama')
        
        generator_llm = CredentialGenerator(
            regex_db=regex_db,
            llm_interface=llm,
            prompt_system=prompt_system,
            use_llm_by_default=True
        )
        
        start_time = time.time()
        llm_results = []
        
        for cred_type in credential_types:
            credential = generator_llm.generate_credential(cred_type)
            llm_results.append(credential)
            print(f"   {cred_type}: {credential[:20]}...")
        
        llm_time = time.time() - start_time
        print(f"\n⏱️  LLM mode total time: {llm_time:.3f} seconds")
        print(f"   Average per credential: {llm_time/len(credential_types):.3f} seconds")
        
        # Performance comparison
        speedup = llm_time / fast_time if fast_time > 0 else float('inf')
        print(f"\n📈 Performance Comparison:")
        print(f"   Fast mode is {speedup:.1f}x faster than LLM mode")
        
    except Exception as e:
        print(f"   LLM not available: {e}")
        print("   Skipping LLM performance test")
    
    # Test 3: Batch Generation
    print(f"\n📦 Test 3: Batch Generation (Fast Mode)")
    print("-" * 40)
    
    start_time = time.time()
    batch_results = generator_fast.generate_batch(credential_types, count=2)
    batch_time = time.time() - start_time
    
    print(f"   Generated {len(credential_types)} types × 2 each = {len(credential_types) * 2} credentials")
    print(f"   Batch time: {batch_time:.3f} seconds")
    print(f"   Average per credential: {batch_time/(len(credential_types) * 2):.3f} seconds")
    
    # Summary
    print(f"\n✅ Performance Summary:")
    print(f"   • Fast fallback mode: ~{fast_time/len(credential_types):.3f}s per credential")
    print(f"   • Batch generation: ~{batch_time/(len(credential_types) * 2):.3f}s per credential")
    print(f"   • Recommended for production: Fast fallback mode")
    print(f"   • Use LLM mode only when high-quality credentials are critical")


if __name__ == "__main__":
    test_credential_performance()
