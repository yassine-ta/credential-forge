#!/usr/bin/env python3
"""Corporate network configuration setup script for CredentialForge."""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from credentialforge.utils.network import setup_corporate_ssl_env, configure_corporate_network
    from credentialforge.utils.config import ConfigManager
except ImportError as e:
    print(f"Error importing CredentialForge modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)


def main():
    """Main configuration setup function."""
    print("CredentialForge Corporate Network Configuration")
    print("=" * 50)
    
    # Check if we're in a corporate environment
    corporate_indicators = [
        os.getenv('HTTP_PROXY'),
        os.getenv('HTTPS_PROXY'),
        os.getenv('CORPORATE_PROXY'),
        Path('C:/Program Files/corporate-ca-bundle.crt').exists(),
        'corp' in os.getenv('USERDOMAIN', '').lower()
    ]
    
    if any(corporate_indicators):
        print("🏢 Corporate environment detected!")
    else:
        print("🏠 Personal/home environment detected")
    
    print("\n1. Current Environment Variables:")
    env_vars = [
        'HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY',
        'CREDENTIALFORGE_SSL_VERIFY', 'CREDENTIALFORGE_CA_BUNDLE',
        'CREDENTIALFORGE_TRUSTED_HOSTS', 'REQUESTS_CA_BUNDLE'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'not set')
        if len(value) > 50:
            value = value[:47] + "..."
        print(f"  {var}: {value}")
    
    print("\n2. Configuration Options:")
    print("  [1] Configure for corporate network (disable SSL verification)")
    print("  [2] Configure proxy settings")
    print("  [3] Set trusted hosts")
    print("  [4] Test network connectivity")
    print("  [5] Create configuration file")
    print("  [6] Show recommended settings")
    print("  [0] Exit")
    
    while True:
        try:
            choice = input("\nSelect option (0-6): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                configure_corporate_ssl()
            elif choice == '2':
                configure_proxy()
            elif choice == '3':
                configure_trusted_hosts()
            elif choice == '4':
                test_connectivity()
            elif choice == '5':
                create_config_file()
            elif choice == '6':
                show_recommended_settings()
            else:
                print("Invalid choice. Please select 0-6.")
                
        except KeyboardInterrupt:
            print("\n\nConfiguration cancelled.")
            break
        except Exception as e:
            print(f"Error: {e}")


def configure_corporate_ssl():
    """Configure SSL settings for corporate networks."""
    print("\n🔒 SSL Configuration for Corporate Networks")
    print("-" * 40)
    
    print("This will disable SSL certificate verification for downloads.")
    print("⚠️  WARNING: This reduces security but may be necessary in corporate environments.")
    
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm != 'y':
        return
    
    # Set environment variables
    os.environ['CREDENTIALFORGE_SSL_VERIFY'] = 'false'
    os.environ['CREDENTIALFORGE_TRUSTED_HOSTS'] = 'huggingface.co,pypi.org,files.pythonhosted.org'
    
    print("\n✅ SSL verification disabled")
    print("✅ Trusted hosts configured")
    
    # Show PowerShell commands to make permanent
    print("\nTo make these settings permanent, run these commands in PowerShell:")
    print("  [Environment]::SetEnvironmentVariable('CREDENTIALFORGE_SSL_VERIFY', 'false', 'User')")
    print("  [Environment]::SetEnvironmentVariable('CREDENTIALFORGE_TRUSTED_HOSTS', 'huggingface.co,pypi.org,files.pythonhosted.org', 'User')")


def configure_proxy():
    """Configure proxy settings."""
    print("\n🌐 Proxy Configuration")
    print("-" * 25)
    
    print("Enter your corporate proxy settings:")
    http_proxy = input("HTTP Proxy (e.g., http://proxy.company.com:8080): ").strip()
    https_proxy = input("HTTPS Proxy (leave blank to use HTTP proxy): ").strip()
    no_proxy = input("No Proxy hosts (comma-separated, e.g., localhost,127.0.0.1): ").strip()
    
    if not https_proxy and http_proxy:
        https_proxy = http_proxy
    
    if http_proxy:
        os.environ['HTTP_PROXY'] = http_proxy
        print(f"✅ HTTP_PROXY set to: {http_proxy}")
    
    if https_proxy:
        os.environ['HTTPS_PROXY'] = https_proxy
        print(f"✅ HTTPS_PROXY set to: {https_proxy}")
    
    if no_proxy:
        os.environ['NO_PROXY'] = no_proxy
        print(f"✅ NO_PROXY set to: {no_proxy}")
    
    print("\nTo make these settings permanent, add to your PowerShell profile or use:")
    if http_proxy:
        print(f"  [Environment]::SetEnvironmentVariable('HTTP_PROXY', '{http_proxy}', 'User')")
    if https_proxy:
        print(f"  [Environment]::SetEnvironmentVariable('HTTPS_PROXY', '{https_proxy}', 'User')")
    if no_proxy:
        print(f"  [Environment]::SetEnvironmentVariable('NO_PROXY', '{no_proxy}', 'User')")


def configure_trusted_hosts():
    """Configure trusted hosts."""
    print("\n🛡️  Trusted Hosts Configuration")
    print("-" * 32)
    
    current_hosts = os.getenv('CREDENTIALFORGE_TRUSTED_HOSTS', '')
    print(f"Current trusted hosts: {current_hosts or 'none'}")
    
    print("\nRecommended hosts for CredentialForge:")
    recommended = ['huggingface.co', 'pypi.org', 'files.pythonhosted.org', 'github.com']
    for i, host in enumerate(recommended, 1):
        print(f"  {i}. {host}")
    
    print("\nOptions:")
    print("  [1] Use recommended hosts")
    print("  [2] Add custom host")
    print("  [3] Clear all trusted hosts")
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == '1':
        hosts = ','.join(recommended)
        os.environ['CREDENTIALFORGE_TRUSTED_HOSTS'] = hosts
        print(f"✅ Trusted hosts set to: {hosts}")
    elif choice == '2':
        new_host = input("Enter hostname to trust: ").strip()
        if new_host:
            current_list = current_hosts.split(',') if current_hosts else []
            if new_host not in current_list:
                current_list.append(new_host)
                hosts = ','.join(current_list)
                os.environ['CREDENTIALFORGE_TRUSTED_HOSTS'] = hosts
                print(f"✅ Added {new_host} to trusted hosts")
    elif choice == '3':
        if 'CREDENTIALFORGE_TRUSTED_HOSTS' in os.environ:
            del os.environ['CREDENTIALFORGE_TRUSTED_HOSTS']
        print("✅ Cleared all trusted hosts")


def test_connectivity():
    """Test network connectivity."""
    print("\n🔍 Network Connectivity Test")
    print("-" * 28)
    
    # Configure network settings
    network_config = configure_corporate_network()
    
    # Test URLs
    test_urls = [
        "https://huggingface.co",
        "https://pypi.org",
        "https://github.com",
        "https://google.com"
    ]
    
    print("Testing connectivity to important sites...")
    
    for url in test_urls:
        print(f"\nTesting {url}...")
        result = network_config.test_connectivity(url)
        
        if result['success']:
            print(f"  ✅ Success ({result['response_time']}s)")
        else:
            print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
            
            if 'certificate verify failed' in str(result.get('error', '')):
                print("     💡 Try disabling SSL verification for corporate networks")
            elif 'connection' in str(result.get('error', '')).lower():
                print("     💡 Check proxy settings")
    
    print(f"\nSSL Verification: {'Enabled' if network_config.ssl_verify else 'Disabled'}")
    print(f"Proxy Settings: {'Configured' if network_config.proxy_settings else 'None'}")


def create_config_file():
    """Create a configuration file with network settings."""
    print("\n📄 Create Configuration File")
    print("-" * 31)
    
    config = ConfigManager()
    
    # Update network configuration based on environment
    ssl_verify = os.getenv('CREDENTIALFORGE_SSL_VERIFY', 'true').lower() not in ('false', '0', 'no')
    config.set('network.ssl_verify', ssl_verify)
    
    if os.getenv('HTTP_PROXY'):
        config.set('network.proxy.http', os.getenv('HTTP_PROXY'))
    if os.getenv('HTTPS_PROXY'):
        config.set('network.proxy.https', os.getenv('HTTPS_PROXY'))
    if os.getenv('NO_PROXY'):
        config.set('network.proxy.no_proxy', os.getenv('NO_PROXY'))
    
    trusted_hosts = os.getenv('CREDENTIALFORGE_TRUSTED_HOSTS')
    if trusted_hosts:
        config.set('network.trusted_hosts', trusted_hosts.split(','))
    
    # Save configuration
    config_file = Path('config') / 'network_config.yaml'
    config_file.parent.mkdir(exist_ok=True)
    
    try:
        config.save_to_file(str(config_file))
        print(f"✅ Configuration saved to: {config_file}")
        
        print("\nTo use this configuration file:")
        print(f"  config = ConfigManager('{config_file}')")
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")


def show_recommended_settings():
    """Show recommended settings for different environments."""
    print("\n💡 Recommended Settings")
    print("-" * 23)
    
    print("For Corporate Networks:")
    print("  set CREDENTIALFORGE_SSL_VERIFY=false")
    print("  set CREDENTIALFORGE_TRUSTED_HOSTS=huggingface.co,pypi.org")
    print("  set HTTP_PROXY=http://your-proxy:port")
    print("  set HTTPS_PROXY=http://your-proxy:port")
    
    print("\nFor Home/Personal Networks:")
    print("  set CREDENTIALFORGE_SSL_VERIFY=true")
    print("  # No proxy settings needed")
    
    print("\nFor Networks with Custom CA:")
    print("  set CREDENTIALFORGE_CA_BUNDLE=C:/path/to/ca-bundle.crt")
    print("  set CREDENTIALFORGE_SSL_VERIFY=true")
    
    print("\nBatch file example for Windows:")
    print("  @echo off")
    print("  set CREDENTIALFORGE_SSL_VERIFY=false")
    print("  set CREDENTIALFORGE_TRUSTED_HOSTS=huggingface.co,pypi.org")
    print("  echo Network configuration applied!")


if __name__ == "__main__":
    main()
