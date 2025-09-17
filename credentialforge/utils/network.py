"""Network utilities for CredentialForge with corporate SSL support."""

import os
import ssl
import requests
import urllib3
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import logging

from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class NetworkConfig:
    """Network configuration manager for corporate environments."""
    
    def __init__(self):
        """Initialize network configuration."""
        self.ssl_verify = True
        self.proxy_settings = {}
        self.trusted_hosts = set()
        self.ca_bundle_path = None
        self.ssl_context = None
        
        # Load configuration from environment
        self._load_from_environment()
    
    def _load_from_environment(self) -> None:
        """Load network configuration from environment variables."""
        # SSL configuration
        if os.getenv('CREDENTIALFORGE_SSL_VERIFY', '').lower() in ('false', '0', 'no', 'off'):
            self.ssl_verify = False
            logger.warning("SSL verification is disabled - this is insecure!")
        
        # CA bundle configuration
        ca_bundle = os.getenv('CREDENTIALFORGE_CA_BUNDLE') or os.getenv('REQUESTS_CA_BUNDLE') or os.getenv('CURL_CA_BUNDLE')
        if ca_bundle and Path(ca_bundle).exists():
            self.ca_bundle_path = ca_bundle
            logger.info(f"Using CA bundle: {ca_bundle}")
        
        # Proxy configuration
        http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
        https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
        no_proxy = os.getenv('NO_PROXY') or os.getenv('no_proxy')
        
        if http_proxy or https_proxy:
            self.proxy_settings = {
                'http': http_proxy,
                'https': https_proxy,
                'no_proxy': no_proxy
            }
            logger.info("Proxy settings detected")
        
        # Trusted hosts
        trusted_hosts = os.getenv('CREDENTIALFORGE_TRUSTED_HOSTS', '')
        if trusted_hosts:
            self.trusted_hosts = set(host.strip() for host in trusted_hosts.split(','))
            logger.info(f"Trusted hosts: {self.trusted_hosts}")
    
    def configure_ssl_for_corporate(self) -> None:
        """Configure SSL settings for corporate networks."""
        try:
            # Create SSL context
            if self.ssl_verify:
                self.ssl_context = ssl.create_default_context()
                
                # Use custom CA bundle if provided
                if self.ca_bundle_path:
                    self.ssl_context.load_verify_locations(self.ca_bundle_path)
                    logger.info(f"Loaded custom CA bundle: {self.ca_bundle_path}")
            else:
                # Create unverified SSL context (for corporate environments)
                self.ssl_context = ssl.create_default_context()
                self.ssl_context.check_hostname = False
                self.ssl_context.verify_mode = ssl.CERT_NONE
                
                # Disable urllib3 SSL warnings
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                logger.warning("SSL verification disabled for corporate network compatibility")
            
            # Configure requests defaults
            if hasattr(requests, 'packages'):
                requests.packages.urllib3.disable_warnings()
            
        except Exception as e:
            logger.error(f"Failed to configure SSL: {e}")
            raise ConfigurationError(f"SSL configuration failed: {e}")
    
    def get_requests_session(self) -> requests.Session:
        """Get a configured requests session.
        
        Returns:
            Configured requests session with SSL and proxy settings
        """
        session = requests.Session()
        
        # Configure SSL verification
        session.verify = self.ssl_verify
        if self.ca_bundle_path and self.ssl_verify:
            session.verify = self.ca_bundle_path
        
        # Configure proxy settings
        if self.proxy_settings:
            session.proxies.update({k: v for k, v in self.proxy_settings.items() if v})
        
        # Configure trusted hosts
        if self.trusted_hosts:
            # Add custom adapter for trusted hosts
            for host in self.trusted_hosts:
                session.mount(f'https://{host}', TrustedHostHTTPSAdapter())
        
        return session
    
    def is_url_trusted(self, url: str) -> bool:
        """Check if a URL is in the trusted hosts list.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is trusted
        """
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            return hostname in self.trusted_hosts if hostname else False
        except Exception:
            return False
    
    def download_file_with_ssl_support(self, url: str, output_path: str, 
                                     progress_callback: Optional[callable] = None) -> bool:
        """Download a file with SSL configuration support.
        
        Args:
            url: URL to download from
            output_path: Local path to save file
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if download successful
            
        Raises:
            ConfigurationError: If download fails
        """
        try:
            session = self.get_requests_session()
            
            logger.info(f"Downloading from {url}")
            response = session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            percent = (downloaded / total_size) * 100
                            progress_callback(percent, downloaded, total_size)
            
            logger.info(f"Download completed: {output_path}")
            return True
            
        except requests.exceptions.SSLError as e:
            error_msg = f"SSL Error downloading {url}: {e}"
            logger.error(error_msg)
            if "certificate verify failed" in str(e).lower():
                error_msg += "\nHint: Set CREDENTIALFORGE_SSL_VERIFY=false for corporate networks"
            raise ConfigurationError(error_msg)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error downloading {url}: {e}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
            
        except Exception as e:
            error_msg = f"Failed to download {url}: {e}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
    
    def test_connectivity(self, url: str = "https://huggingface.co") -> Dict[str, Any]:
        """Test network connectivity to a URL.
        
        Args:
            url: URL to test (defaults to Hugging Face)
            
        Returns:
            Dictionary with connectivity test results
        """
        result = {
            'url': url,
            'success': False,
            'ssl_verify': self.ssl_verify,
            'proxy_used': bool(self.proxy_settings),
            'response_time': None,
            'status_code': None,
            'error': None
        }
        
        try:
            import time
            session = self.get_requests_session()
            
            start_time = time.time()
            response = session.head(url, timeout=10)
            end_time = time.time()
            
            result['success'] = response.status_code < 400
            result['status_code'] = response.status_code
            result['response_time'] = round(end_time - start_time, 2)
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Connectivity test failed for {url}: {e}")
        
        return result


class TrustedHostHTTPSAdapter(requests.adapters.HTTPAdapter):
    """Custom HTTPS adapter for trusted hosts."""
    
    def init_poolmanager(self, *args, **kwargs):
        """Initialize pool manager with custom SSL context."""
        kwargs['ssl_context'] = ssl.create_default_context()
        kwargs['ssl_context'].check_hostname = False
        kwargs['ssl_context'].verify_mode = ssl.CERT_NONE
        return super().init_poolmanager(*args, **kwargs)


def configure_corporate_network() -> NetworkConfig:
    """Configure network settings for corporate environments.
    
    Returns:
        Configured NetworkConfig instance
    """
    config = NetworkConfig()
    config.configure_ssl_for_corporate()
    
    # Test connectivity
    test_result = config.test_connectivity()
    if test_result['success']:
        logger.info("Network connectivity test passed")
    else:
        logger.warning(f"Network connectivity test failed: {test_result.get('error', 'Unknown error')}")
    
    return config


def download_model_with_ssl_support(model_name: str, url: str, models_dir: str) -> str:
    """Download a model with SSL support for corporate networks.
    
    Args:
        model_name: Name of the model
        url: URL to download from
        models_dir: Directory to save model
        
    Returns:
        Path to downloaded model file
        
    Raises:
        ConfigurationError: If download fails
    """
    config = configure_corporate_network()
    
    model_file = Path(models_dir) / f"{model_name}.gguf"
    
    def progress_callback(percent, downloaded, total):
        """Progress callback for download."""
        if total > 0:
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total / (1024 * 1024)
            print(f"\rDownloading {model_name}: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", 
                  end='', flush=True)
    
    success = config.download_file_with_ssl_support(
        url, str(model_file), progress_callback
    )
    
    if success:
        print(f"\nModel downloaded successfully: {model_file}")
        return str(model_file)
    else:
        raise ConfigurationError(f"Failed to download model {model_name}")


# Environment variable setup helpers
def setup_corporate_ssl_env():
    """Set up environment variables for corporate SSL configuration."""
    print("Corporate Network SSL Configuration Helper")
    print("=" * 50)
    
    # Check current settings
    print("\nCurrent SSL Settings:")
    print(f"  SSL_VERIFY: {os.getenv('CREDENTIALFORGE_SSL_VERIFY', 'true')}")
    print(f"  CA_BUNDLE: {os.getenv('CREDENTIALFORGE_CA_BUNDLE', 'not set')}")
    print(f"  HTTP_PROXY: {os.getenv('HTTP_PROXY', 'not set')}")
    print(f"  HTTPS_PROXY: {os.getenv('HTTPS_PROXY', 'not set')}")
    
    print("\nRecommended settings for corporate networks:")
    print("  set CREDENTIALFORGE_SSL_VERIFY=false")
    print("  set CREDENTIALFORGE_TRUSTED_HOSTS=huggingface.co,pypi.org")
    print("  set HTTP_PROXY=http://your-proxy:port")
    print("  set HTTPS_PROXY=http://your-proxy:port")
    
    return configure_corporate_network()


if __name__ == "__main__":
    setup_corporate_ssl_env()
