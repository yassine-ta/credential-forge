# Corporate Network Configuration Guide

This guide helps you configure CredentialForge to work with corporate networks that may have SSL certificates, proxies, or other network restrictions.

## Quick Setup

### Option 1: Automated Setup (Windows)
Run the batch file for automatic configuration:
```cmd
setup_corporate_network.bat
```

### Option 2: Interactive Setup
Run the Python configuration script:
```cmd
python setup_corporate_network.py
```

### Option 3: CLI Configuration
Use the built-in CLI command:
```cmd
python -m credentialforge network --configure
```

## Manual Configuration

### Environment Variables

Set these environment variables for corporate networks:

```cmd
# Disable SSL verification (for corporate networks with self-signed certificates)
set CREDENTIALFORGE_SSL_VERIFY=false

# Set trusted hosts
set CREDENTIALFORGE_TRUSTED_HOSTS=huggingface.co,pypi.org,files.pythonhosted.org

# Configure proxy (if required)
set HTTP_PROXY=http://your-proxy:port
set HTTPS_PROXY=http://your-proxy:port
set NO_PROXY=localhost,127.0.0.1,.local

# Custom CA bundle (if available)
set CREDENTIALFORGE_CA_BUNDLE=C:\path\to\corporate-ca-bundle.crt
```

### PowerShell (Permanent Settings)
```powershell
[Environment]::SetEnvironmentVariable('CREDENTIALFORGE_SSL_VERIFY', 'false', 'User')
[Environment]::SetEnvironmentVariable('CREDENTIALFORGE_TRUSTED_HOSTS', 'huggingface.co,pypi.org', 'User')
[Environment]::SetEnvironmentVariable('HTTP_PROXY', 'http://your-proxy:port', 'User')
[Environment]::SetEnvironmentVariable('HTTPS_PROXY', 'http://your-proxy:port', 'User')
```

## Common Corporate Network Issues

### SSL Certificate Verification Failed
**Error:** `certificate verify failed: self-signed certificate in certificate chain`

**Solution:**
```cmd
set CREDENTIALFORGE_SSL_VERIFY=false
set CREDENTIALFORGE_TRUSTED_HOSTS=huggingface.co,pypi.org
```

### Connection Timeouts
**Error:** `Connection timeout` or `Max retries exceeded`

**Solution:**
```cmd
set HTTP_PROXY=http://your-corporate-proxy:8080
set HTTPS_PROXY=http://your-corporate-proxy:8080
set CREDENTIALFORGE_NETWORK_TIMEOUT=60
```

### Model Download Failures
**Error:** `Failed to download model`

**Solutions:**
1. Configure proxy settings
2. Disable SSL verification
3. Manual download:
   ```cmd
   # Download manually and place in models/ directory
   curl -k -L -o models/phi3-mini.gguf "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
   ```

## Testing Network Configuration

### Test Connectivity
```cmd
python -m credentialforge network --test
```

### Verify Settings
```cmd
python -m credentialforge network
```

### Manual Test
```python
from credentialforge.utils.network import configure_corporate_network

# Configure and test
network_config = configure_corporate_network()
result = network_config.test_connectivity("https://huggingface.co")
print(f"Success: {result['success']}")
```

## Configuration File

Create a `config/network_config.yaml` file:

```yaml
network:
  ssl_verify: false
  timeout: 30
  retries: 3
  trusted_hosts:
    - huggingface.co
    - pypi.org
    - files.pythonhosted.org
  proxy:
    http: "http://proxy.company.com:8080"
    https: "http://proxy.company.com:8080"
    no_proxy: "localhost,127.0.0.1,.local"
```

Load the configuration:
```python
from credentialforge.utils.config import ConfigManager
config = ConfigManager('config/network_config.yaml')
```

## Security Considerations

### SSL Verification Disabled
When `CREDENTIALFORGE_SSL_VERIFY=false`:
- ⚠️ **Security Risk**: Man-in-the-middle attacks possible
- ✅ **Corporate Necessity**: Required for self-signed certificates
- 🔧 **Mitigation**: Use trusted hosts list to limit exposure

### Trusted Hosts
Configure only necessary hosts:
```cmd
set CREDENTIALFORGE_TRUSTED_HOSTS=huggingface.co,pypi.org
```

### Custom CA Bundle
If your organization provides a CA bundle:
```cmd
set CREDENTIALFORGE_CA_BUNDLE=C:\corp-certs\ca-bundle.crt
set CREDENTIALFORGE_SSL_VERIFY=true
```

## Troubleshooting

### Check Current Settings
```cmd
echo %CREDENTIALFORGE_SSL_VERIFY%
echo %HTTP_PROXY%
echo %HTTPS_PROXY%
```

### Reset Configuration
```cmd
set CREDENTIALFORGE_SSL_VERIFY=
set CREDENTIALFORGE_TRUSTED_HOSTS=
set HTTP_PROXY=
set HTTPS_PROXY=
```

### Debug Network Issues
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from credentialforge.utils.network import configure_corporate_network
network_config = configure_corporate_network()
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `certificate verify failed` | Corporate SSL/TLS inspection | Set `CREDENTIALFORGE_SSL_VERIFY=false` |
| `Connection timeout` | Network restrictions | Configure proxy settings |
| `Max retries exceeded` | Firewall/filtering | Add to trusted hosts |
| `Name resolution failed` | DNS issues | Check corporate DNS settings |

## Advanced Configuration

### Custom SSL Context
```python
from credentialforge.utils.network import NetworkConfig
import ssl

config = NetworkConfig()
config.ssl_context = ssl.create_default_context()
config.ssl_context.load_verify_locations('/path/to/corporate-ca.crt')
```

### Session Configuration
```python
session = config.get_requests_session()
session.timeout = 60
session.headers.update({'User-Agent': 'CredentialForge/1.0'})
```

### Proxy Authentication
```cmd
set HTTP_PROXY=http://username:password@proxy.company.com:8080
set HTTPS_PROXY=http://username:password@proxy.company.com:8080
```

## Support

If you continue to have network issues:

1. Check with your IT department for:
   - Corporate proxy settings
   - SSL certificate requirements
   - Firewall whitelist requirements

2. Contact CredentialForge support with:
   - Error messages
   - Network configuration
   - Corporate environment details

3. Alternative: Use offline models or manual downloads
