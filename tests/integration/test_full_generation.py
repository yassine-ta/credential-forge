"""Integration tests for full generation workflow."""

import pytest
import tempfile
import json
from pathlib import Path

from credentialforge.agents.orchestrator import OrchestratorAgent
from credentialforge.db.regex_db import RegexDatabase
from credentialforge.llm.llama_interface import LlamaInterface


class TestFullGeneration:
    """Integration tests for complete generation workflow."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_regex_db(self):
        """Create sample regex database."""
        return {
            "credentials": [
                {
                    "type": "aws_access_key",
                    "regex": "^AKIA[0-9A-Z]{16}$",
                    "description": "AWS Access Key ID",
                    "generator": "construct_aws_key()"
                },
                {
                    "type": "jwt_token",
                    "regex": "^eyJ[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+$",
                    "description": "JWT Token",
                    "generator": "construct_jwt()"
                }
            ]
        }
    
    @pytest.fixture
    def temp_regex_db_file(self, sample_regex_db):
        """Create temporary regex database file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_regex_db, f)
            return f.name
    
    def test_full_generation_workflow(self, temp_output_dir, temp_regex_db_file):
        """Test complete generation workflow."""
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Configure generation
        config = {
            'output_dir': temp_output_dir,
            'num_files': 2,
            'formats': ['eml', 'xlsx'],
            'credential_types': ['aws_access_key', 'jwt_token'],
            'topics': ['system architecture', 'API documentation'],
            'embed_strategy': 'random',
            'batch_size': 1,
            'regex_db_path': temp_regex_db_file
        }
        
        # Generate files
        results = orchestrator.orchestrate_generation(config)
        
        # Verify results
        assert len(results['files']) == 2
        assert all(Path(f).exists() for f in results['files'])
        assert results['metadata']['total_credentials'] == 4  # 2 files * 2 credentials each
        assert results['metadata']['total_files'] == 2
        
        # Check file formats
        file_formats = [Path(f).suffix.lower() for f in results['files']]
        assert '.eml' in file_formats
        assert '.xlsx' in file_formats
        
        # Clean up
        Path(temp_regex_db_file).unlink()
    
    def test_generation_with_errors(self, temp_output_dir, temp_regex_db_file):
        """Test generation workflow with some errors."""
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Configure generation with invalid format
        config = {
            'output_dir': temp_output_dir,
            'num_files': 3,
            'formats': ['eml', 'invalid_format'],  # Invalid format
            'credential_types': ['aws_access_key'],
            'topics': ['test topic'],
            'regex_db_path': temp_regex_db_file
        }
        
        # This should raise an error due to invalid format
        with pytest.raises(Exception):
            orchestrator.orchestrate_generation(config)
        
        # Clean up
        Path(temp_regex_db_file).unlink()
    
    def test_batch_processing(self, temp_output_dir, temp_regex_db_file):
        """Test batch processing with multiple files."""
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Configure generation with larger batch
        config = {
            'output_dir': temp_output_dir,
            'num_files': 10,
            'formats': ['eml'],
            'credential_types': ['aws_access_key'],
            'topics': ['batch test'],
            'batch_size': 3,
            'regex_db_path': temp_regex_db_file
        }
        
        # Generate files
        results = orchestrator.orchestrate_generation(config)
        
        # Verify results
        assert len(results['files']) == 10
        assert all(Path(f).exists() for f in results['files'])
        assert results['metadata']['total_files'] == 10
        assert results['metadata']['total_credentials'] == 10
        
        # Check all files are EML format
        for file_path in results['files']:
            assert Path(file_path).suffix.lower() == '.eml'
        
        # Clean up
        Path(temp_regex_db_file).unlink()
    
    def test_multiple_formats_generation(self, temp_output_dir, temp_regex_db_file):
        """Test generation with multiple file formats."""
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Configure generation with multiple formats
        config = {
            'output_dir': temp_output_dir,
            'num_files': 4,
            'formats': ['eml', 'xlsx', 'pptx', 'vsdx'],
            'credential_types': ['aws_access_key', 'jwt_token'],
            'topics': ['multi-format test'],
            'regex_db_path': temp_regex_db_file
        }
        
        # Generate files
        results = orchestrator.orchestrate_generation(config)
        
        # Verify results
        assert len(results['files']) == 4
        assert all(Path(f).exists() for f in results['files'])
        
        # Check file formats
        file_formats = [Path(f).suffix.lower() for f in results['files']]
        expected_formats = ['.eml', '.xlsx', '.pptx', '.vsdx']
        for expected_format in expected_formats:
            assert expected_format in file_formats
        
        # Clean up
        Path(temp_regex_db_file).unlink()
    
    def test_credential_uniqueness(self, temp_output_dir, temp_regex_db_file):
        """Test that generated credentials are unique."""
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Configure generation
        config = {
            'output_dir': temp_output_dir,
            'num_files': 5,
            'formats': ['eml'],
            'credential_types': ['aws_access_key'],
            'topics': ['uniqueness test'],
            'regex_db_path': temp_regex_db_file
        }
        
        # Generate files
        results = orchestrator.orchestrate_generation(config)
        
        # Verify results
        assert len(results['files']) == 5
        
        # Check that credentials are embedded in files
        credentials_found = []
        for file_path in results['files']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for AWS access key pattern
                import re
                aws_keys = re.findall(r'AKIA[0-9A-Z]{16}', content)
                credentials_found.extend(aws_keys)
        
        # Should have found some credentials
        assert len(credentials_found) > 0
        
        # Clean up
        Path(temp_regex_db_file).unlink()
    
    def test_topic_content_generation(self, temp_output_dir, temp_regex_db_file):
        """Test that topic-specific content is generated."""
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Configure generation with specific topics
        config = {
            'output_dir': temp_output_dir,
            'num_files': 2,
            'formats': ['eml'],
            'credential_types': ['aws_access_key'],
            'topics': ['database configuration', 'API security'],
            'regex_db_path': temp_regex_db_file
        }
        
        # Generate files
        results = orchestrator.orchestrate_generation(config)
        
        # Verify results
        assert len(results['files']) == 2
        
        # Check that topic content is present
        for file_path in results['files']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Should contain some topic-related content
                assert len(content) > 100  # Substantial content
                assert any(keyword in content.lower() for keyword in 
                          ['database', 'api', 'configuration', 'security'])
        
        # Clean up
        Path(temp_regex_db_file).unlink()
    
    def test_generation_statistics(self, temp_output_dir, temp_regex_db_file):
        """Test generation statistics tracking."""
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Configure generation
        config = {
            'output_dir': temp_output_dir,
            'num_files': 3,
            'formats': ['eml', 'xlsx'],
            'credential_types': ['aws_access_key', 'jwt_token'],
            'topics': ['statistics test'],
            'regex_db_path': temp_regex_db_file
        }
        
        # Generate files
        results = orchestrator.orchestrate_generation(config)
        
        # Check statistics
        stats = orchestrator.get_generation_stats()
        
        assert stats['total_files'] == 3
        assert stats['total_credentials'] == 6  # 3 files * 2 credentials each
        assert 'eml' in stats['files_by_format']
        assert 'xlsx' in stats['files_by_format']
        assert 'aws_access_key' in stats['credentials_by_type']
        assert 'jwt_token' in stats['credentials_by_type']
        
        # Clean up
        Path(temp_regex_db_file).unlink()
    
    def test_reproducible_generation(self, temp_output_dir, temp_regex_db_file):
        """Test that generation is reproducible with same seed."""
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Configure generation with seed
        config = {
            'output_dir': temp_output_dir,
            'num_files': 2,
            'formats': ['eml'],
            'credential_types': ['aws_access_key'],
            'topics': ['reproducible test'],
            'seed': 42,
            'regex_db_path': temp_regex_db_file
        }
        
        # Generate files twice with same seed
        results1 = orchestrator.orchestrate_generation(config)
        results2 = orchestrator.orchestrate_generation(config)
        
        # Results should be similar (same number of files, similar structure)
        assert len(results1['files']) == len(results2['files'])
        assert results1['metadata']['total_credentials'] == results2['metadata']['total_credentials']
        
        # Clean up
        Path(temp_regex_db_file).unlink()
