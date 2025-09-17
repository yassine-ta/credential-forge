#!/usr/bin/env python3
"""Test script for SSL configuration in corporate networks."""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ssl_configuration():
    """Test SSL configuration and model download capability."""
    print("CredentialForge SSL Configuration Test")
    print("=" * 40)
    
    # Test 1: Import modules
    print("\n1. Testing module imports...")
    try:
        from credentialforge.utils.network import configure_corporate_network, NetworkConfig
        from credentialforge.llm.llama_interface import LlamaInterface
        print("✅ All modules imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Network configuration
    print("\n2. Testing network configuration...")
    try:
        network_config = configure_corporate_network()
        print(f"✅ Network config created")
        print(f"   SSL Verify: {network_config.ssl_verify}")
        print(f"   Proxy: {'Configured' if network_config.proxy_settings else 'None'}")
    except Exception as e:
        print(f"❌ Network config failed: {e}")
        return False
    
    # Test 3: Connectivity test
    print("\n3. Testing connectivity...")
    test_urls = [
        "https://huggingface.co",
        "https://httpbin.org/get"
    ]
    
    for url in test_urls:
        try:
            result = network_config.test_connectivity(url)
            if result['success']:
                print(f"✅ {url} - OK ({result.get('response_time', 'N/A')}s)")
            else:
                print(f"❌ {url} - Failed: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"❌ {url} - Exception: {e}")
    
    # Test 4: Model download capability (dry run)
    print("\n4. Testing model download capability...")
    try:
        # Check if models directory exists
        models_dir = project_root / "models"
        models_dir.mkdir(exist_ok=True)
        print(f"✅ Models directory ready: {models_dir}")
        
        # Test download URL access (without actually downloading)
        test_model_url = "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
        
        session = network_config.get_requests_session()
        response = session.head(test_model_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Model download URL accessible")
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                print(f"   Model size: {size_mb:.1f} MB")
        else:
            print(f"❌ Model URL returned status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Model download test failed: {e}")
    
    # Test 5: Environment variables
    print("\n5. Checking environment variables...")
    env_vars = [
        'CREDENTIALFORGE_SSL_VERIFY',
        'CREDENTIALFORGE_TRUSTED_HOSTS',
        'HTTP_PROXY',
        'HTTPS_PROXY',
        'CREDENTIALFORGE_CA_BUNDLE'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Truncate long values
            display_value = value if len(value) <= 50 else value[:47] + "..."
            print(f"✅ {var}: {display_value}")
        else:
            print(f"⚪ {var}: not set")
    
    print("\n" + "=" * 40)
    print("SSL Configuration Test Complete")
    print("\nIf you see SSL/network errors above:")
    print("1. Run: setup_corporate_network.bat")
    print("2. Or set: CREDENTIALFORGE_SSL_VERIFY=false")
    print("3. Configure proxy if needed")
    
    return True

def test_actual_download():
    """Test actual model download (optional)."""
    print("\n" + "=" * 40)
    print("OPTIONAL: Test Actual Model Download")
    print("=" * 40)
    
    response = input("Download a small test model (~2.3GB)? This will test actual download. (y/N): ")
    if response.lower() != 'y':
        print("Skipping actual download test.")
        return
    
    try:
        from credentialforge.llm.llama_interface import LlamaInterface
        
        print("\nDownloading phi3-mini model...")
        print("This may take several minutes depending on your connection...")
        
        model_path = LlamaInterface.download_model('phi3-mini')
        print(f"✅ Model downloaded successfully to: {model_path}")
        
        # Verify file exists and has reasonable size
        model_file = Path(model_path)
        if model_file.exists():
            size_mb = model_file.stat().st_size / (1024 * 1024)
            print(f"✅ Downloaded file size: {size_mb:.1f} MB")
            
            if size_mb > 1000:  # Should be around 2.3GB
                print("✅ File size looks correct")
            else:
                print("⚠️  File size seems small, download may be incomplete")
        
    except Exception as e:
        print(f"❌ Model download failed: {e}")
        print("\nTry these solutions:")
        print("1. Set CREDENTIALFORGE_SSL_VERIFY=false")
        print("2. Configure proxy settings")
        print("3. Check corporate firewall/filtering")

if __name__ == "__main__":
    try:
        success = test_ssl_configuration()
        
        if success:
            test_actual_download()
        
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
