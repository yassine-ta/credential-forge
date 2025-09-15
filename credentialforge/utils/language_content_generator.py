"""Language-aware content generation for CredentialForge."""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..utils.exceptions import ValidationError


class LanguageContentGenerator:
    """Generates language-aware content with localized terms and phrases."""
    
    def __init__(self, glossary_path: str = 'data/language_glossary.json'):
        """Initialize language content generator.
        
        Args:
            glossary_path: Path to the language glossary JSON file
        """
        self.glossary_path = Path(glossary_path)
        self.language_data = self._load_language_data()
        self.supported_languages = list(self.language_data['languages'].keys())
    
    def _load_language_data(self) -> Dict[str, Any]:
        """Load language data from JSON file.
        
        Returns:
            Dictionary containing language data
            
        Raises:
            ValidationError: If file cannot be loaded or parsed
        """
        try:
            if not self.glossary_path.exists():
                raise ValidationError(f"Language glossary file not found: {self.glossary_path}")
            
            with open(self.glossary_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in language glossary: {e}")
        except Exception as e:
            raise ValidationError(f"Failed to load language glossary: {e}")
    
    def get_localized_term(self, term: str, language: str) -> str:
        """Get localized version of a technical term.
        
        Args:
            term: English technical term
            language: Target language code
            
        Returns:
            Localized term or original if not found
        """
        if language not in self.supported_languages:
            return term
        
        language_info = self.language_data['languages'][language]
        technical_terms = language_info.get('technical_terms', {})
        
        return technical_terms.get(term, term)
    
    def get_localized_phrase(self, phrase: str, language: str) -> str:
        """Get localized version of a common phrase.
        
        Args:
            phrase: English phrase key
            language: Target language code
            
        Returns:
            Localized phrase or original if not found
        """
        if language not in self.supported_languages:
            return phrase
        
        language_info = self.language_data['languages'][language]
        common_phrases = language_info.get('common_phrases', {})
        
        return common_phrases.get(phrase, phrase)
    
    def localize_content(self, content: str, language: str) -> str:
        """Localize content by replacing English terms with localized versions.
        
        Args:
            content: Content to localize
            language: Target language code
            
        Returns:
            Localized content
        """
        if language not in self.supported_languages:
            return content
        
        localized_content = content
        language_info = self.language_data['languages'][language]
        
        # Split content into template variables and regular text
        import re
        # Find all template variables {variable}
        template_vars = re.findall(r'\{[^}]+\}', content)
        
        # Replace technical terms in non-template parts
        technical_terms = language_info.get('technical_terms', {})
        for english_term, localized_term in technical_terms.items():
            # Simple word boundary replacement
            pattern = re.compile(rf'\b{re.escape(english_term)}\b', re.IGNORECASE)
            localized_content = pattern.sub(localized_term, localized_content)
        
        # Replace common phrases in non-template parts
        common_phrases = language_info.get('common_phrases', {})
        for english_phrase, localized_phrase in common_phrases.items():
            # Simple word boundary replacement
            pattern = re.compile(rf'\b{re.escape(english_phrase)}\b', re.IGNORECASE)
            localized_content = pattern.sub(localized_phrase, localized_content)
        
        return localized_content
    
    def generate_localized_credential_description(self, credential_type: str, language: str) -> str:
        """Generate localized description for a credential type.
        
        Args:
            credential_type: Type of credential
            language: Target language code
            
        Returns:
            Localized credential description
        """
        descriptions = {
            'aws_access_key': f"{self.get_localized_term('key', language)} d'{self.get_localized_term('access', language)} AWS",
            'aws_secret_key': f"{self.get_localized_term('secret', language)} AWS",
            'github_token': f"{self.get_localized_term('token', language)} GitHub",
            'password': self.get_localized_term('password', language),
            'jwt_token': f"{self.get_localized_term('token', language)} JWT",
            'api_key': f"{self.get_localized_term('key', language)} API",
            'db_connection': f"{self.get_localized_term('connection', language)} {self.get_localized_term('database', language)}",
            'slack_token': f"{self.get_localized_term('token', language)} Slack",
            'stripe_key': f"{self.get_localized_term('key', language)} Stripe",
            'mongodb_uri': f"URI MongoDB"
        }
        
        return descriptions.get(credential_type, credential_type)
    
    def generate_localized_system_message(self, message_type: str, language: str, **kwargs) -> str:
        """Generate localized system messages.
        
        Args:
            message_type: Type of message to generate
            language: Target language code
            **kwargs: Additional parameters for message generation
            
        Returns:
            Localized system message
        """
        if language not in self.supported_languages:
            language = 'en'  # Fallback to English
        
        messages = {
            'authentication_success': f"{self.get_localized_phrase('success', language)}: {self.get_localized_term('authentication', language)} {self.get_localized_phrase('completed', language)}",
            'authentication_failed': f"{self.get_localized_phrase('failure', language)}: {self.get_localized_term('authentication', language)} {self.get_localized_phrase('failed', language)}",
            'connection_established': f"{self.get_localized_term('connection', language)} {self.get_localized_phrase('established', language)}",
            'connection_lost': f"{self.get_localized_term('connection', language)} {self.get_localized_phrase('lost', language)}",
            'system_starting': f"{self.get_localized_term('system', language)} {self.get_localized_phrase('starting', language)}",
            'system_stopping': f"{self.get_localized_term('system', language)} {self.get_localized_phrase('stopping', language)}",
            'backup_completed': f"{self.get_localized_term('backup', language)} {self.get_localized_phrase('completed', language)}",
            'update_available': f"{self.get_localized_term('update', language)} {self.get_localized_phrase('available', language)}",
            'security_alert': f"{self.get_localized_term('security', language)} {self.get_localized_phrase('alert', language)}",
            'maintenance_scheduled': f"{self.get_localized_term('maintenance', language)} {self.get_localized_phrase('scheduled', language)}"
        }
        
        return messages.get(message_type, message_type)
    
    def get_language_name(self, language_code: str) -> str:
        """Get the display name for a language code.
        
        Args:
            language_code: Language code (e.g., 'en', 'fr', 'es')
            
        Returns:
            Language display name
        """
        if language_code in self.supported_languages:
            return self.language_data['languages'][language_code]['name']
        return language_code
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes.
        
        Returns:
            List of supported language codes
        """
        return self.supported_languages.copy()
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported.
        
        Args:
            language_code: Language code to check
            
        Returns:
            True if language is supported
        """
        return language_code in self.supported_languages
