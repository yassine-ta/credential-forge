"""Configuration management for CredentialForge."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from .exceptions import ConfigurationError


class ConfigManager:
    """Configuration manager for CredentialForge."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_file: Optional configuration file path
        """
        self.config_file = config_file
        self.config = self._load_default_config()
        
        if config_file:
            self.load_from_file(config_file)
        
        # Load from environment variables
        self._load_from_environment()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            'defaults': {
                'output_dir': './output',
                'batch_size': 10,
                'log_level': 'INFO',
                'embed_strategy': 'random',
                'models_dir': './models',
                'cache_dir': './cache',
                'config_dir': './config',
                'logs_dir': './logs'
            },
            'llm': {
                'default_model': None,
                'n_threads': 4,
                'n_ctx': 2048,
                'temperature': 0.7
            },
            'network': {
                'ssl_verify': True,
                'timeout': 30,
                'retries': 3,
                'trusted_hosts': [],
                'ca_bundle_path': None,
                'proxy': {
                    'http': None,
                    'https': None,
                    'no_proxy': None
                }
            },
            'formats': {
                'eml': {
                    'max_size': '10MB',
                    'embed_locations': ['body', 'headers']
                },
                'excel': {
                    'max_worksheets': 10,
                    'embed_locations': ['cells', 'formulas']
                },
                'pptx': {
                    'max_slides': 50,
                    'embed_locations': ['content', 'notes']
                },
                'vsdx': {
                    'max_shapes': 1000,
                    'embed_locations': ['labels', 'data_fields']
                }
            },
            'security': {
                'isolation_mode': True,
                'allowed_directories': ['./output', './test'],
                'max_file_size': '50MB'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def load_from_file(self, file_path: str) -> None:
        """Load configuration from file.
        
        Args:
            file_path: Path to configuration file
            
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise ConfigurationError(f"Configuration file not found: {file_path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in {'.yaml', '.yml'}:
                    file_config = yaml.safe_load(f)
                elif path.suffix.lower() == '.json':
                    import json
                    file_config = json.load(f)
                else:
                    raise ConfigurationError(f"Unsupported configuration file format: {path.suffix}")
            
            # Merge with existing config
            self._merge_config(file_config)
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration from {file_path}: {e}")
    
    def save_to_file(self, file_path: str) -> None:
        """Save configuration to file.
        
        Args:
            file_path: Path to save configuration file
            
        Raises:
            ConfigurationError: If file cannot be saved
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                if path.suffix.lower() in {'.yaml', '.yml'}:
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)
                elif path.suffix.lower() == '.json':
                    import json
                    json.dump(self.config, f, indent=2)
                else:
                    raise ConfigurationError(f"Unsupported configuration file format: {path.suffix}")
                    
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration to {file_path}: {e}")
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'CREDENTIALFORGE_OUTPUT_DIR': 'defaults.output_dir',
            'CREDENTIALFORGE_BATCH_SIZE': 'defaults.batch_size',
            'CREDENTIALFORGE_LOG_LEVEL': 'defaults.log_level',
            'CREDENTIALFORGE_EMBED_STRATEGY': 'defaults.embed_strategy',
            'CREDENTIALFORGE_LLM_MODEL': 'llm.default_model',
            'CREDENTIALFORGE_LLM_THREADS': 'llm.n_threads',
            'CREDENTIALFORGE_LLM_CTX': 'llm.n_ctx',
            'CREDENTIALFORGE_LLM_TEMPERATURE': 'llm.temperature',
            'CREDENTIALFORGE_SSL_VERIFY': 'network.ssl_verify',
            'CREDENTIALFORGE_NETWORK_TIMEOUT': 'network.timeout',
            'CREDENTIALFORGE_CA_BUNDLE': 'network.ca_bundle_path',
            'HTTP_PROXY': 'network.proxy.http',
            'HTTPS_PROXY': 'network.proxy.https',
            'NO_PROXY': 'network.proxy.no_proxy',
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if config_key in {'defaults.batch_size', 'llm.n_threads', 'llm.n_ctx', 'network.timeout'}:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                elif config_key == 'llm.temperature':
                    try:
                        value = float(value)
                    except ValueError:
                        continue
                elif config_key == 'network.ssl_verify':
                    value = value.lower() not in {'false', '0', 'no', 'off'}
                
                self.set(config_key, value)
        
        # Handle trusted hosts (comma-separated list)
        trusted_hosts = os.getenv('CREDENTIALFORGE_TRUSTED_HOSTS')
        if trusted_hosts:
            hosts = [host.strip() for host in trusted_hosts.split(',')]
            self.set('network.trusted_hosts', hosts)
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration with existing config.
        
        Args:
            new_config: New configuration to merge
        """
        def merge_dict(base: Dict[str, Any], update: Dict[str, Any]) -> None:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self.config, new_config)
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM-specific configuration.
        
        Returns:
            LLM configuration dictionary
        """
        return self.get('llm', {})
    
    def get_format_config(self, format_name: str) -> Dict[str, Any]:
        """Get format-specific configuration.
        
        Args:
            format_name: Name of the format
            
        Returns:
            Format configuration dictionary
        """
        return self.get(f'formats.{format_name}', {})
    
    def get_network_config(self) -> Dict[str, Any]:
        """Get network configuration.
        
        Returns:
            Network configuration dictionary
        """
        return self.get('network', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration.
        
        Returns:
            Security configuration dictionary
        """
        return self.get('security', {})
    
    def validate(self) -> None:
        """Validate configuration.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Validate required fields
        required_fields = [
            'defaults.output_dir',
            'defaults.batch_size',
            'defaults.log_level'
        ]
        
        for field in required_fields:
            if self.get(field) is None:
                raise ConfigurationError(f"Required configuration field missing: {field}")
        
        # Validate batch size
        batch_size = self.get('defaults.batch_size')
        if not isinstance(batch_size, int) or batch_size < 1 or batch_size > 100:
            raise ConfigurationError("Invalid batch size: must be integer between 1 and 100")
        
        # Validate log level
        log_level = self.get('defaults.log_level')
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if log_level not in valid_levels:
            raise ConfigurationError(f"Invalid log level: {log_level}. Valid levels: {valid_levels}")
        
        # Validate LLM configuration if present
        llm_config = self.get_llm_config()
        if llm_config:
            if 'n_threads' in llm_config and (not isinstance(llm_config['n_threads'], int) or llm_config['n_threads'] < 1):
                raise ConfigurationError("Invalid LLM thread count: must be positive integer")
            
            if 'n_ctx' in llm_config and (not isinstance(llm_config['n_ctx'], int) or llm_config['n_ctx'] < 512):
                raise ConfigurationError("Invalid LLM context size: must be at least 512")
            
            if 'temperature' in llm_config and (not isinstance(llm_config['temperature'], (int, float)) or not 0 <= llm_config['temperature'] <= 2):
                raise ConfigurationError("Invalid LLM temperature: must be between 0 and 2")
