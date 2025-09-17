"""Fast credential generation using regex database patterns."""

import re
import random
import string
import base64
from typing import Dict, List, Optional, Set, Any

from ..db.regex_db import RegexDatabase
from ..utils.exceptions import GenerationError, ValidationError


class CredentialGenerator:
    """Fast credential generator using regex database patterns."""
    
    def __init__(self, regex_db: RegexDatabase):
        """Initialize credential generator.
        
        Args:
            regex_db: RegexDatabase instance containing patterns
        """
        self.regex_db = regex_db
        self.generated_credentials: Set[str] = set()
        self.generation_stats = {
            'total_generated': 0,
            'by_type': {},
            'errors': 0
        }
    
    def generate_credential(self, credential_type: str, 
                           context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a synthetic credential using regex database patterns.
        
        Args:
            credential_type: Type of credential to generate
            context: Context for generation (company, topic, language)
            
        Returns:
            Generated credential string
            
        Raises:
            GenerationError: If generation fails
            ValidationError: If credential type is invalid
        """
        try:
            # Validate credential type
            if not self.regex_db.has_credential_type(credential_type):
                raise ValidationError(f"Unknown credential type: {credential_type}")
            
            # Get pattern from regex database
            pattern = self.regex_db.get_pattern(credential_type)
            
            # Generate credential using fast fallback
            credential = self._generate_fast(credential_type, pattern, context)
            
            # Ensure uniqueness within session
            attempts = 0
            max_attempts = 10  # Increased attempts to avoid timestamp fallback
            while credential in self.generated_credentials and attempts < max_attempts:
                credential = self._generate_fast(credential_type, pattern, context)
                attempts += 1
            
            if attempts >= max_attempts:
                # Instead of adding timestamp suffix that breaks regex, regenerate with different seed
                import time
                random.seed(int(time.time() * 1000000))  # Use microsecond precision for better randomness
                credential = self._generate_fast(credential_type, pattern, context)
            
            # Track generation
            self.generated_credentials.add(credential)
            self.generation_stats['total_generated'] += 1
            self.generation_stats['by_type'][credential_type] = \
                self.generation_stats['by_type'].get(credential_type, 0) + 1
            
            return credential
            
        except Exception as e:
            self.generation_stats['errors'] += 1
            if isinstance(e, (GenerationError, ValidationError)):
                raise
            else:
                raise GenerationError(f"Credential generation failed: {e}")
    
    def generate_batch(self, credential_types: List[str], count: int = 1,
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, List[str]]:
        """Generate multiple credentials.
        
        Args:
            credential_types: List of credential types
            count: Number of credentials per type
            context: Optional context for generation
            
        Returns:
            Dictionary mapping types to generated credentials
        """
        results = {}
        
        for cred_type in credential_types:
            results[cred_type] = []
            for _ in range(count):
                try:
                    credential = self.generate_credential(cred_type, context)
                    results[cred_type].append(credential)
                except Exception as e:
                    # Log error but continue with other credentials
                    self.generation_stats['errors'] += 1
                    continue
        
        return results
    
    def _generate_realistic_jwt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a realistic JWT token with proper structure."""
        import json
        import time
        
        # Common JWT headers
        headers = [
            {"alg": "HS256", "typ": "JWT"},
            {"alg": "RS256", "typ": "JWT"},
            {"alg": "ES256", "typ": "JWT"},
            {"alg": "HS512", "typ": "JWT"}
        ]
        
        # Select random header
        header = random.choice(headers)
        
        # Generate realistic payload
        current_time = int(time.time())
        payload = {
            "sub": f"user_{random.randint(1000, 9999)}",
            "iat": current_time - random.randint(0, 86400),  # Issued at (up to 1 day ago)
            "exp": current_time + random.randint(3600, 86400 * 7),  # Expires in 1 hour to 7 days
            "iss": "api.company.com" if not context else context.get('company', 'api.company.com').lower().replace(' ', ''),
            "aud": "api.company.com" if not context else context.get('company', 'api.company.com').lower().replace(' ', ''),
        }
        
        # Add optional claims
        if random.random() < 0.7:  # 70% chance
            payload["name"] = f"User {random.randint(1, 1000)}"
        if random.random() < 0.5:  # 50% chance
            payload["email"] = f"user{random.randint(1, 1000)}@company.com"
        if random.random() < 0.3:  # 30% chance
            payload["role"] = random.choice(["admin", "user", "moderator", "viewer"])
        if random.random() < 0.4:  # 40% chance
            payload["scope"] = random.choice(["read", "write", "admin", "read write"])
        
        # Encode header and payload
        header_encoded = base64.urlsafe_b64encode(
            json.dumps(header, separators=(',', ':')).encode('utf-8')
        ).decode('utf-8').rstrip('=')
        
        payload_encoded = base64.urlsafe_b64encode(
            json.dumps(payload, separators=(',', ':')).encode('utf-8')
        ).decode('utf-8').rstrip('=')
        
        # Generate realistic signature (43 characters like real JWT signatures)
        signature_chars = string.ascii_letters + string.digits + '-_'
        signature = ''.join(random.choices(signature_chars, k=43))
        
        return f"{header_encoded}.{payload_encoded}.{signature}"
    
    def _generate_fast(self, credential_type: str, pattern: str, 
                      context: Optional[Dict[str, Any]] = None) -> str:
        """Generate credential using fast deterministic method based on regex database.
        
        Args:
            credential_type: Type of credential to generate
            pattern: Regex pattern that the credential must match
            context: Optional context with company, topic, language info
            
        Returns:
            Generated credential string
        """
        try:
            # Generate credential based on type using regex database information
            if credential_type == "api_key":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            
            elif credential_type == "aws_access_key":
                return 'AKIA' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
            
            elif credential_type == "aws_secret_key":
                chars = string.ascii_letters + string.digits + '+/='
                return ''.join(random.choices(chars, k=40))
            
            elif credential_type == "aws_session_token":
                chars = string.ascii_letters + string.digits + '+/='
                return ''.join(random.choices(chars, k=356))
            
            elif credential_type == "aws_cloudfront_key_pair_id":
                return ''.join(random.choices(string.ascii_uppercase + string.digits, k=14))
            
            elif credential_type == "azure_client_id":
                return f"{random.randint(10000000, 99999999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(100000000000, 999999999999)}"
            
            elif credential_type == "azure_client_secret":
                chars = string.ascii_letters + string.digits + '+/'
                return ''.join(random.choices(chars, k=32))
            
            elif credential_type == "azure_subscription_id":
                return f"{random.randint(10000000, 99999999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(100000000000, 999999999999)}"
            
            elif credential_type == "google_api_key":
                return 'AIza' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=35))
            
            elif credential_type == "google_oauth_token":
                return 'ya29.' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=100))
            
            elif credential_type == "google_service_account_key":
                chars = string.ascii_letters + string.digits + '+/'
                return ''.join(random.choices(chars, k=1000))
            
            elif credential_type == "openai_api_key":
                return 'sk-' + ''.join(random.choices(string.ascii_letters + string.digits, k=48))
            
            elif credential_type == "anthropic_api_key":
                return 'sk-ant-' + ''.join(random.choices(string.ascii_letters + string.digits, k=48))
            
            elif credential_type == "cohere_api_key":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=40))
            
            elif credential_type == "huggingface_token":
                return 'hf_' + ''.join(random.choices(string.ascii_letters + string.digits, k=34))
            
            elif credential_type == "replicate_api_token":
                return 'r8_' + ''.join(random.choices(string.ascii_letters + string.digits, k=40))
            
            elif credential_type == "jwt_token":
                return self._generate_realistic_jwt(context)
            
            elif credential_type == "github_token":
                return 'ghp_' + ''.join(random.choices(string.ascii_letters + string.digits, k=36))
            
            elif credential_type == "github_app_token":
                return 'ghu_' + ''.join(random.choices(string.ascii_letters + string.digits, k=36))
            
            elif credential_type == "gitlab_token":
                return 'glpat-' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=20))
            
            elif credential_type == "bitbucket_app_password":
                chars = string.ascii_letters + string.digits + '+/'
                return ''.join(random.choices(chars, k=24))
            
            elif credential_type == "slack_bot_token":
                return 'xoxb-' + str(random.randint(10000000000, 99999999999)) + '-' + str(random.randint(10000000000, 99999999999)) + '-' + ''.join(random.choices(string.ascii_letters + string.digits, k=24))
            
            elif credential_type == "slack_user_token":
                return 'xoxp-' + str(random.randint(10000000000, 99999999999)) + '-' + str(random.randint(10000000000, 99999999999)) + '-' + ''.join(random.choices(string.ascii_letters + string.digits, k=24))
            
            elif credential_type == "discord_bot_token":
                chars = string.ascii_letters + string.digits + '.-_'
                return ''.join(random.choices(chars, k=59))
            
            elif credential_type == "telegram_bot_token":
                return str(random.randint(10000000, 9999999999)) + ':' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=35))
            
            elif credential_type == "stripe_secret_key":
                return 'sk_test_' + ''.join(random.choices(string.ascii_letters + string.digits, k=24))
            
            elif credential_type == "stripe_live_key":
                return 'sk_live_' + ''.join(random.choices(string.ascii_letters + string.digits, k=24))
            
            elif credential_type == "paypal_client_id":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=80))
            
            elif credential_type == "paypal_client_secret":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=80))
            
            elif credential_type == "square_access_token":
                return 'sq0atp-' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=22))
            
            elif credential_type == "square_application_id":
                return 'sq0idp-' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=22))
            
            elif credential_type == "twilio_account_sid":
                return 'AC' + ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            
            elif credential_type == "twilio_auth_token":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            
            elif credential_type == "sendgrid_api_key":
                return 'SG.' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=22)) + '.' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=43))
            
            elif credential_type == "mailgun_api_key":
                return 'key-' + ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            
            elif credential_type == "datadog_api_key":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            
            elif credential_type == "newrelic_license_key":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=40))
            
            elif credential_type == "sentry_dsn":
                return 'https://' + ''.join(random.choices(string.ascii_letters + string.digits, k=32)) + '@sentry.io/' + str(random.randint(100000, 999999))
            
            elif credential_type == "docker_hub_token":
                return 'dckr_pat_' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=24))
            
            elif credential_type == "npm_token":
                return 'npm_' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=36))
            
            elif credential_type == "pypi_token":
                return 'pypi-' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=40))
            
            elif credential_type == "vault_token":
                return 'hvs.' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=24))
            
            elif credential_type == "consul_token":
                return f"{random.randint(10000000, 99999999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(100000000000, 999999999999)}"
            
            elif credential_type == "kubernetes_service_account_token":
                header = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9"
                payload_chars = string.ascii_letters + string.digits + '-_'
                payload = ''.join(random.choices(payload_chars, k=100))
                signature_chars = string.ascii_letters + string.digits + '-_'
                signature = ''.join(random.choices(signature_chars, k=100))
                return f"{header}.{payload}.{signature}"
            
            elif credential_type == "prometheus_bearer_token":
                return ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=32))
            
            elif credential_type == "grafana_api_key":
                return 'eyJrIjoi' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=40))
            
            elif credential_type == "zapier_webhook_url":
                return 'https://hooks.zapier.com/hooks/catch/' + str(random.randint(100000, 999999)) + '/' + ''.join(random.choices(string.ascii_letters + string.digits, k=26)) + '/'
            
            elif credential_type == "ifttt_webhook_key":
                return ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=24))
            
            elif credential_type == "webhook_secret":
                return 'whsec_' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=32))
            
            elif credential_type == "ssh_private_key":
                base64_chars = string.ascii_letters + string.digits + '+/='
                lines = []
                for _ in range(25):
                    line = ''.join(random.choices(base64_chars, k=64))
                    lines.append(line)
                final_line = ''.join(random.choices(base64_chars, k=32))
                lines.append(final_line)
                content = '\n'.join(lines)
                return f"-----BEGIN RSA PRIVATE KEY-----\n{content}\n-----END RSA PRIVATE KEY-----"
            
            elif credential_type == "gpg_private_key":
                base64_chars = string.ascii_letters + string.digits + '+/='
                lines = []
                for _ in range(30):
                    line = ''.join(random.choices(base64_chars, k=64))
                    lines.append(line)
                final_line = ''.join(random.choices(base64_chars, k=32))
                lines.append(final_line)
                content = '\n'.join(lines)
                return f"-----BEGIN PGP PRIVATE KEY BLOCK-----\n{content}\n-----END PGP PRIVATE KEY BLOCK-----"
            
            elif credential_type == "ssl_certificate":
                base64_chars = string.ascii_letters + string.digits + '+/='
                lines = []
                for _ in range(20):
                    line = ''.join(random.choices(base64_chars, k=64))
                    lines.append(line)
                final_line = ''.join(random.choices(base64_chars, k=32))
                lines.append(final_line)
                content = '\n'.join(lines)
                return f"-----BEGIN CERTIFICATE-----\n{content}\n-----END CERTIFICATE-----"
            
            elif credential_type == "private_key_pem":
                base64_chars = string.ascii_letters + string.digits + '+/='
                lines = []
                for _ in range(25):
                    line = ''.join(random.choices(base64_chars, k=64))
                    lines.append(line)
                final_line = ''.join(random.choices(base64_chars, k=32))
                lines.append(final_line)
                content = '\n'.join(lines)
                return f"-----BEGIN PRIVATE KEY-----\n{content}\n-----END PRIVATE KEY-----"
            
            elif credential_type == "password":
                chars = string.ascii_letters + string.digits + '@#$%^&+='
                length = random.randint(8, 16)
                return ''.join(random.choices(chars, k=length))
            
            elif credential_type == "db_connection":
                return f"mysql://user{random.randint(100, 999)}:pass{random.randint(100, 999)}@localhost:3306/db{random.randint(100, 999)}"
            
            elif credential_type == "mongodb_uri":
                return f"mongodb://user{random.randint(100, 999)}:pass{random.randint(100, 999)}@localhost:27017/db{random.randint(100, 999)}"
            
            elif credential_type == "redis_url":
                return f"redis://user{random.randint(100, 999)}:pass{random.randint(100, 999)}@localhost:6379"
            
            elif credential_type == "postgres_url":
                return f"postgres://user{random.randint(100, 999)}:pass{random.randint(100, 999)}@localhost:5432/db{random.randint(100, 999)}"
            
            elif credential_type == "mysql_url":
                return f"mysql://user{random.randint(100, 999)}:pass{random.randint(100, 999)}@localhost:3306/db{random.randint(100, 999)}"
            
            elif credential_type == "elasticsearch_url":
                return f"https://user{random.randint(100, 999)}:pass{random.randint(100, 999)}@localhost:9200"
            
            elif credential_type == "twitter_api_key":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=25))
            
            elif credential_type == "twitter_api_secret":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=50))
            
            elif credential_type == "facebook_app_id":
                return str(random.randint(100000000000000, 999999999999999))
            
            elif credential_type == "facebook_app_secret":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            
            elif credential_type == "linkedin_client_id":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            
            elif credential_type == "linkedin_client_secret":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            
            elif credential_type == "digitalocean_token":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=64))
            
            elif credential_type == "heroku_api_key":
                return f"{random.randint(10000000, 99999999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(100000000000, 999999999999)}"
            
            elif credential_type == "jenkins_api_token":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            
            elif credential_type == "travis_ci_token":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=22))
            
            elif credential_type == "circleci_token":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=40))
            
            elif credential_type == "rubygems_api_key":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=40))
            
            elif credential_type == "maven_settings_password":
                chars = string.ascii_letters + string.digits + '@#$%^&+='
                length = random.randint(8, 16)
                return ''.join(random.choices(chars, k=length))
            
            elif credential_type == "gradle_properties_key":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            
            elif credential_type == "sonarqube_token":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=40))
            
            elif credential_type == "nexus_repository_token":
                return ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=24))
            
            elif credential_type == "etcd_ca_cert":
                base64_chars = string.ascii_letters + string.digits + '+/='
                lines = []
                for _ in range(20):
                    line = ''.join(random.choices(base64_chars, k=64))
                    lines.append(line)
                final_line = ''.join(random.choices(base64_chars, k=32))
                lines.append(final_line)
                content = '\n'.join(lines)
                return f"-----BEGIN CERTIFICATE-----\n{content}\n-----END CERTIFICATE-----"
            
            elif credential_type == "influxdb_token":
                return ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=40))
            
            elif credential_type == "kibana_api_key":
                return ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=32))
            
            elif credential_type == "splunk_token":
                return ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=24))
            
            else:
                # Parse pattern to determine length and character set
                return self._parse_pattern_and_generate(pattern)
        
        except Exception as e:
            raise GenerationError(f"Fast generation failed: {e}")
    
    def _post_process_credential(self, credential: str, credential_type: str) -> str:
        """Post-process credential to fix common issues."""
        return credential  # No post-processing needed for fast generation
    
    
    def _parse_pattern_and_generate(self, pattern: str) -> str:
        """Parse regex pattern and generate matching credential."""
        import re
        import random
        import string
        
        try:
            # Remove anchors
            clean_pattern = pattern.replace('^', '').replace('$', '')
            
            # Handle quantifiers like {16}, {32}, etc.
            quantifier_match = re.search(r'\{(\d+)\}', clean_pattern)
            if quantifier_match:
                length = int(quantifier_match.group(1))
            else:
                # Estimate length from pattern
                length = len(clean_pattern.replace('[', '').replace(']', '').replace('(', '').replace(')', ''))
                if length < 8:
                    length = 16  # Default minimum length
            
            # Determine character set
            if 'A-Z' in clean_pattern and 'a-z' in clean_pattern and '0-9' in clean_pattern:
                chars = string.ascii_letters + string.digits
            elif 'A-Z' in clean_pattern and '0-9' in clean_pattern:
                chars = string.ascii_uppercase + string.digits
            elif 'a-z' in clean_pattern and '0-9' in clean_pattern:
                chars = string.ascii_lowercase + string.digits
            elif 'A-Z' in clean_pattern:
                chars = string.ascii_uppercase
            elif 'a-z' in clean_pattern:
                chars = string.ascii_lowercase
            elif '0-9' in clean_pattern:
                chars = string.digits
            else:
                chars = string.ascii_letters + string.digits
            
            # Add special characters if present in pattern
            if '+' in clean_pattern or '/' in clean_pattern or '=' in clean_pattern:
                chars += '+/='
            if '@' in clean_pattern or '#' in clean_pattern or '$' in clean_pattern:
                chars += '@#$%^&+='
            
            return ''.join(random.choices(chars, k=length))
            
        except Exception:
            # Ultimate fallback
            return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    def validate_credential(self, credential: str, credential_type: str) -> bool:
        """Validate a generated credential against its pattern.
        
        Args:
            credential: Credential to validate
            credential_type: Type of credential
            
        Returns:
            True if credential is valid
        """
        try:
            return self.regex_db.validate_credential(credential, credential_type)
        except Exception:
            return False
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics.
        
        Returns:
            Dictionary with generation statistics
        """
        return {
            'total_generated': self.generation_stats['total_generated'],
            'unique_generated': len(self.generated_credentials),
            'by_type': self.generation_stats['by_type'].copy(),
            'errors': self.generation_stats['errors'],
            'credential_types': list(self.generation_stats['by_type'].keys())
        }
    
    def clear_generated_credentials(self) -> None:
        """Clear the set of generated credentials."""
        self.generated_credentials.clear()
        self.generation_stats = {
            'total_generated': 0,
            'by_type': {},
            'errors': 0
        }
    
