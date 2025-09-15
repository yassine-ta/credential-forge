"""Tests for credential and topic generators."""

import pytest
import tempfile
import json
from unittest.mock import Mock, patch
from pathlib import Path

from credentialforge.generators.credential_generator import CredentialGenerator
from credentialforge.generators.topic_generator import TopicGenerator
from credentialforge.db.regex_db import RegexDatabase
from credentialforge.llm.llama_interface import LlamaInterface


class TestCredentialGenerator:
    """Test cases for CredentialGenerator."""
    
    @pytest.fixture
    def mock_regex_db(self):
        """Create mock regex database."""
        db = Mock(spec=RegexDatabase)
        db.patterns = {
            'aws_access_key': {
                'regex': '^AKIA[0-9A-Z]{16}$',
                'generator': 'construct_aws_key()'
            },
            'jwt_token': {
                'regex': '^eyJ[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+$',
                'generator': 'construct_jwt()'
            }
        }
        db.has_credential_type.return_value = True
        db.get_pattern.return_value = '^AKIA[0-9A-Z]{16}$'
        db.get_generator.return_value = 'construct_aws_key()'
        db.validate_credential.return_value = True
        return db
    
    @pytest.fixture
    def generator(self, mock_regex_db):
        """Create CredentialGenerator instance."""
        return CredentialGenerator(mock_regex_db)
    
    def test_generate_credential_success(self, generator, mock_regex_db):
        """Test successful credential generation."""
        with patch.object(generator, '_apply_generator', return_value='AKIA1234567890ABCDEF'):
            result = generator.generate_credential('aws_access_key')
            
            assert result == 'AKIA1234567890ABCDEF'
            assert result in generator.generated_credentials
            mock_regex_db.get_pattern.assert_called_once_with('aws_access_key')
            mock_regex_db.get_generator.assert_called_once_with('aws_access_key')
    
    def test_generate_credential_unknown_type(self, generator):
        """Test error handling for unknown credential type."""
        generator.regex_db.has_credential_type.return_value = False
        
        with pytest.raises(Exception):
            generator.generate_credential('unknown_type')
    
    def test_generate_credential_uniqueness(self, generator, mock_regex_db):
        """Test that generated credentials are unique."""
        with patch.object(generator, '_apply_generator') as mock_generator:
            mock_generator.side_effect = ['AKIA1234567890ABCDEF', 'AKIA0987654321FEDCBA']
            
            result1 = generator.generate_credential('aws_access_key')
            result2 = generator.generate_credential('aws_access_key')
            
            assert result1 != result2
            assert len(generator.generated_credentials) == 2
    
    def test_generate_batch(self, generator, mock_regex_db):
        """Test batch credential generation."""
        with patch.object(generator, '_apply_generator', return_value='AKIA1234567890ABCDEF'):
            results = generator.generate_batch(['aws_access_key', 'jwt_token'], count=2)
            
            assert 'aws_access_key' in results
            assert 'jwt_token' in results
            assert len(results['aws_access_key']) == 2
            assert len(results['jwt_token']) == 2
    
    def test_validate_credential(self, generator, mock_regex_db):
        """Test credential validation."""
        mock_regex_db.validate_credential.return_value = True
        
        result = generator.validate_credential('AKIA1234567890ABCDEF', 'aws_access_key')
        
        assert result is True
        mock_regex_db.validate_credential.assert_called_once_with('AKIA1234567890ABCDEF', 'aws_access_key')
    
    def test_get_generation_stats(self, generator):
        """Test generation statistics."""
        generator.generation_stats['total_generated'] = 5
        generator.generation_stats['by_type']['aws_access_key'] = 3
        generator.generation_stats['by_type']['jwt_token'] = 2
        
        stats = generator.get_generation_stats()
        
        assert stats['total_generated'] == 5
        assert stats['by_type']['aws_access_key'] == 3
        assert stats['by_type']['jwt_token'] == 2


class TestTopicGenerator:
    """Test cases for TopicGenerator."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM interface."""
        llm = Mock(spec=LlamaInterface)
        llm.generate_topic_content.return_value = "Generated topic content"
        return llm
    
    @pytest.fixture
    def generator_with_llm(self, mock_llm):
        """Create TopicGenerator with LLM."""
        return TopicGenerator(mock_llm)
    
    @pytest.fixture
    def generator_without_llm(self):
        """Create TopicGenerator without LLM."""
        return TopicGenerator(None)
    
    def test_generate_topic_content_with_llm(self, generator_with_llm, mock_llm):
        """Test topic content generation with LLM."""
        result = generator_with_llm.generate_topic_content(
            "system architecture", "eml"
        )
        
        assert result == "Generated topic content"
        mock_llm.generate_topic_content.assert_called_once_with(
            "system architecture", "eml", None
        )
    
    def test_generate_topic_content_without_llm(self, generator_without_llm):
        """Test topic content generation without LLM."""
        result = generator_without_llm.generate_topic_content(
            "system architecture", "eml"
        )
        
        assert "system architecture" in result.lower()
        assert len(result) > 50  # Should generate substantial content
    
    def test_generate_multiple_topics(self, generator_without_llm):
        """Test multiple topic generation."""
        topics = ["system architecture", "API documentation"]
        results = generator_without_llm.generate_multiple_topics(topics, "eml")
        
        assert len(results) == 2
        assert "system architecture" in results
        assert "API documentation" in results
    
    def test_get_suggested_topics(self, generator_without_llm):
        """Test getting suggested topics."""
        topics = generator_without_llm.get_suggested_topics("eml")
        
        assert isinstance(topics, list)
        assert len(topics) > 0
        assert all(isinstance(topic, str) for topic in topics)
    
    def test_get_generation_stats(self, generator_without_llm):
        """Test generation statistics."""
        generator_without_llm.generation_stats['total_generated'] = 3
        generator_without_llm.generation_stats['by_topic']['test'] = 2
        generator_without_llm.generation_stats['by_format']['eml'] = 3
        
        stats = generator_without_llm.get_generation_stats()
        
        assert stats['total_generated'] == 3
        assert stats['by_topic']['test'] == 2
        assert stats['by_format']['eml'] == 3


class TestIntegration:
    """Integration tests for generators."""
    
    @pytest.fixture
    def temp_regex_db(self):
        """Create temporary regex database file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            db_data = {
                "credentials": [
                    {
                        "type": "test_key",
                        "regex": "^TEST[0-9]{4}$",
                        "description": "Test Key",
                        "generator": "random_string(8, 'A-Z0-9')"
                    }
                ]
            }
            json.dump(db_data, f)
            return f.name
    
    def test_credential_generator_with_real_db(self, temp_regex_db):
        """Test credential generator with real database."""
        regex_db = RegexDatabase(temp_regex_db)
        generator = CredentialGenerator(regex_db)
        
        credential = generator.generate_credential('test_key')
        
        assert credential.startswith('TEST')
        assert len(credential) == 8
        
        # Clean up
        Path(temp_regex_db).unlink()
    
    def test_topic_generator_template_generation(self):
        """Test topic generator template-based generation."""
        generator = TopicGenerator(None)
        
        content = generator.generate_topic_content("test topic", "eml")
        
        assert "test topic" in content.lower()
        assert len(content) > 100
        assert "configuration" in content.lower() or "system" in content.lower()
