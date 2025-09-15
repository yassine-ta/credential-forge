#!/usr/bin/env python3
"""Test script for multiprocessing content generation agent."""

import time
import multiprocessing as mp
from credentialforge.agents.content_generation_agent import ContentGenerationAgent
from credentialforge.db.regex_db import RegexDatabase

def test_multiprocessing_performance():
    """Test multiprocessing vs threading performance."""
    
    print("🚀 Testing Multiprocessing Content Generation Agent")
    print("=" * 60)
    
    # Load regex database
    regex_db = RegexDatabase('data/regex_db.json')
    
    # Test parameters
    topic = "Database Security Implementation"
    credential_types = ['aws_access_key', 'private_key_pem', 'jwt_token', 'api_key', 'password']
    language = 'en'
    format_type = 'pdf'
    context = {
        'min_credentials_per_file': 2,
        'max_credentials_per_file': 4
    }
    
    # Test 1: Multiprocessing Agent
    print("\n🔧 Testing Multiprocessing Agent...")
    mp_agent = ContentGenerationAgent(
        regex_db=regex_db,
        enable_parallel_generation=True,
        use_multiprocessing=True,
        max_parallel_workers=mp.cpu_count()
    )
    
    start_time = time.time()
    try:
        mp_result = mp_agent.generate_content(
            topic=topic,
            credential_types=credential_types,
            language=language,
            format_type=format_type,
            context=context
        )
        mp_time = time.time() - start_time
        print(f"✅ Multiprocessing completed in {mp_time:.2f} seconds")
        print(f"   Generated {len(mp_result['sections'])} sections")
        print(f"   Generated {len(mp_result['credentials'])} credentials")
    except Exception as e:
        print(f"❌ Multiprocessing failed: {e}")
        mp_time = float('inf')
    finally:
        mp_agent.cleanup()
    
    # Test 2: Threading Agent
    print("\n🧵 Testing Threading Agent...")
    thread_agent = ContentGenerationAgent(
        regex_db=regex_db,
        enable_parallel_generation=True,
        use_multiprocessing=False,
        max_parallel_workers=mp.cpu_count()
    )
    
    start_time = time.time()
    try:
        thread_result = thread_agent.generate_content(
            topic=topic,
            credential_types=credential_types,
            language=language,
            format_type=format_type,
            context=context
        )
        thread_time = time.time() - start_time
        print(f"✅ Threading completed in {thread_time:.2f} seconds")
        print(f"   Generated {len(thread_result['sections'])} sections")
        print(f"   Generated {len(thread_result['credentials'])} credentials")
    except Exception as e:
        print(f"❌ Threading failed: {e}")
        thread_time = float('inf')
    finally:
        thread_agent.cleanup()
    
    # Test 3: Sequential Agent
    print("\n📝 Testing Sequential Agent...")
    seq_agent = ContentGenerationAgent(
        regex_db=regex_db,
        enable_parallel_generation=False
    )
    
    start_time = time.time()
    try:
        seq_result = seq_agent.generate_content(
            topic=topic,
            credential_types=credential_types,
            language=language,
            format_type=format_type,
            context=context
        )
        seq_time = time.time() - start_time
        print(f"✅ Sequential completed in {seq_time:.2f} seconds")
        print(f"   Generated {len(seq_result['sections'])} sections")
        print(f"   Generated {len(seq_result['credentials'])} credentials")
    except Exception as e:
        print(f"❌ Sequential failed: {e}")
        seq_time = float('inf')
    finally:
        seq_agent.cleanup()
    
    # Performance comparison
    print("\n📊 Performance Comparison")
    print("=" * 40)
    print(f"CPU Cores: {mp.cpu_count()}")
    print(f"Multiprocessing: {mp_time:.2f}s")
    print(f"Threading:       {thread_time:.2f}s")
    print(f"Sequential:      {seq_time:.2f}s")
    
    if mp_time < float('inf') and thread_time < float('inf'):
        speedup = thread_time / mp_time
        print(f"Multiprocessing speedup: {speedup:.2f}x")
    
    if mp_time < float('inf') and seq_time < float('inf'):
        parallel_speedup = seq_time / mp_time
        print(f"Parallel speedup: {parallel_speedup:.2f}x")

def test_credential_generation_performance():
    """Test credential generation performance with different methods."""
    
    print("\n🔐 Testing Credential Generation Performance")
    print("=" * 50)
    
    # Load regex database
    regex_db = RegexDatabase('data/regex_db.json')
    
    # Test credential types
    credential_types = [
        'aws_access_key', 'private_key_pem', 'jwt_token', 'api_key', 'password',
        'github_token', 'slack_bot_token', 'stripe_secret_key', 'docker_hub_token'
    ]
    
    # Test multiprocessing agent
    print("\n🔧 Testing with Multiprocessing...")
    mp_agent = ContentGenerationAgent(
        regex_db=regex_db,
        enable_parallel_generation=True,
        use_multiprocessing=True,
        max_parallel_workers=mp.cpu_count()
    )
    
    start_time = time.time()
    try:
        result = mp_agent.generate_content(
            topic="API Security Configuration",
            credential_types=credential_types,
            language='en',
            format_type='docx',
            context={'min_credentials_per_file': 5, 'max_credentials_per_file': 8}
        )
        mp_time = time.time() - start_time
        
        print(f"✅ Generated {len(result['credentials'])} credentials in {mp_time:.2f}s")
        print("   Credentials generated:")
        for cred in result['credentials']:
            preview = cred['value'][:50] + '...' if len(cred['value']) > 50 else cred['value']
            print(f"   - {cred['type']}: {preview}")
            
    except Exception as e:
        print(f"❌ Multiprocessing credential generation failed: {e}")
    finally:
        mp_agent.cleanup()

if __name__ == "__main__":
    # Set multiprocessing start method for Windows compatibility
    if hasattr(mp, 'set_start_method'):
        try:
            mp.set_start_method('spawn', force=True)
        except RuntimeError:
            pass  # Already set
    
    print(f"🖥️  System Info:")
    print(f"   CPU Cores: {mp.cpu_count()}")
    import sys
    print(f"   Python: {sys.version}")
    
    # Run performance tests
    test_multiprocessing_performance()
    test_credential_generation_performance()
    
    print("\n🎉 Multiprocessing tests completed!")
