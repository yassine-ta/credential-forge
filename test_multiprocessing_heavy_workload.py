#!/usr/bin/env python3
"""Test script for multiprocessing with heavy workloads."""

import time
import multiprocessing as mp
from credentialforge.agents.content_generation_agent import ContentGenerationAgent
from credentialforge.db.regex_db import RegexDatabase

def test_heavy_workload_performance():
    """Test multiprocessing vs threading with heavy workloads."""
    
    print("🚀 Testing Heavy Workload Performance")
    print("=" * 50)
    
    # Load regex database
    regex_db = RegexDatabase('data/regex_db.json')
    
    # Heavy workload parameters
    topic = "Enterprise Security Architecture Implementation"
    credential_types = [
        'aws_access_key', 'aws_secret_key', 'aws_session_token', 'private_key_pem', 
        'jwt_token', 'api_key', 'password', 'github_token', 'slack_bot_token', 
        'stripe_secret_key', 'docker_hub_token', 'vault_token', 'ssh_private_key',
        'ssl_certificate', 'gpg_private_key', 'kubernetes_service_account_token'
    ]
    language = 'en'
    format_type = 'pdf'
    context = {
        'min_credentials_per_file': 8,
        'max_credentials_per_file': 12
    }
    
    # Test 1: Multiprocessing Agent
    print("\n🔧 Testing Multiprocessing Agent (Heavy Workload)...")
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
        
        # Show some generated credentials
        print("   Sample credentials:")
        for i, cred in enumerate(mp_result['credentials'][:3]):
            preview = cred['value'][:60] + '...' if len(cred['value']) > 60 else cred['value']
            print(f"   - {cred['type']}: {preview}")
            
    except Exception as e:
        print(f"❌ Multiprocessing failed: {e}")
        mp_time = float('inf')
    finally:
        mp_agent.cleanup()
    
    # Test 2: Threading Agent
    print("\n🧵 Testing Threading Agent (Heavy Workload)...")
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
    print("\n📝 Testing Sequential Agent (Heavy Workload)...")
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
    print("\n📊 Heavy Workload Performance Comparison")
    print("=" * 50)
    print(f"CPU Cores: {mp.cpu_count()}")
    print(f"Credential Types: {len(credential_types)}")
    print(f"Multiprocessing: {mp_time:.2f}s")
    print(f"Threading:       {thread_time:.2f}s")
    print(f"Sequential:      {seq_time:.2f}s")
    
    if mp_time < float('inf') and thread_time < float('inf'):
        speedup = thread_time / mp_time
        print(f"Multiprocessing vs Threading: {speedup:.2f}x")
    
    if mp_time < float('inf') and seq_time < float('inf'):
        parallel_speedup = seq_time / mp_time
        print(f"Multiprocessing vs Sequential: {parallel_speedup:.2f}x")
    
    if thread_time < float('inf') and seq_time < float('inf'):
        thread_speedup = seq_time / thread_time
        print(f"Threading vs Sequential: {thread_speedup:.2f}x")

def test_batch_generation():
    """Test batch generation with multiple documents."""
    
    print("\n📚 Testing Batch Document Generation")
    print("=" * 40)
    
    # Load regex database
    regex_db = RegexDatabase('data/regex_db.json')
    
    # Batch parameters
    topics = [
        "Database Security Implementation",
        "API Gateway Configuration", 
        "Microservices Authentication",
        "Cloud Infrastructure Setup",
        "DevOps Pipeline Security"
    ]
    
    credential_types = ['aws_access_key', 'private_key_pem', 'jwt_token', 'api_key', 'password']
    
    # Test multiprocessing batch
    print("\n🔧 Testing Multiprocessing Batch Generation...")
    mp_agent = ContentGenerationAgent(
        regex_db=regex_db,
        enable_parallel_generation=True,
        use_multiprocessing=True,
        max_parallel_workers=min(4, mp.cpu_count())  # Limit to 4 for batch
    )
    
    start_time = time.time()
    results = []
    try:
        for i, topic in enumerate(topics):
            print(f"   Generating document {i+1}/5: {topic}")
            result = mp_agent.generate_content(
                topic=topic,
                credential_types=credential_types,
                language='en',
                format_type='docx',
                context={'min_credentials_per_file': 3, 'max_credentials_per_file': 5}
            )
            results.append(result)
        
        batch_time = time.time() - start_time
        print(f"✅ Batch generation completed in {batch_time:.2f} seconds")
        print(f"   Generated {len(results)} documents")
        print(f"   Average time per document: {batch_time/len(results):.2f}s")
        
    except Exception as e:
        print(f"❌ Batch generation failed: {e}")
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
    print(f"   Python: {sys.version.split()[0]}")
    
    # Run performance tests
    test_heavy_workload_performance()
    test_batch_generation()
    
    print("\n🎉 Heavy workload tests completed!")
