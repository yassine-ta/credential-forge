"""Tests for CLI interface."""

import pytest
import tempfile
import json
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import Mock, patch

from credentialforge.cli import cli


class TestCLI:
    """Test cases for CLI interface."""
    
    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()
    
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
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "CredentialForge" in result.output
        assert "generate" in result.output
        assert "interactive" in result.output
    
    def test_generate_command_help(self, runner):
        """Test generate command help."""
        result = runner.invoke(cli, ['generate', '--help'])
        
        assert result.exit_code == 0
        assert "--output-dir" in result.output
        assert "--num-files" in result.output
        assert "--formats" in result.output
    
    def test_generate_basic(self, runner, temp_regex_db, temp_output_dir):
        """Test basic generation command."""
        with patch('credentialforge.cli.OrchestratorAgent') as mock_orchestrator:
            mock_instance = Mock()
            mock_instance.orchestrate_generation.return_value = {
                'files': ['test_file.eml'],
                'errors': [],
                'metadata': {
                    'total_files': 1,
                    'total_credentials': 2,
                    'generation_time': 1.0,
                    'files_by_format': {'eml': 1},
                    'credentials_by_type': {'test_key': 2}
                }
            }
            mock_orchestrator.return_value = mock_instance
            
            result = runner.invoke(cli, [
                'generate',
                '--output-dir', temp_output_dir,
                '--num-files', '1',
                '--formats', 'eml',
                '--credential-types', 'test_key',
                '--regex-db', temp_regex_db,
                '--topics', 'test topic'
            ])
            
            assert result.exit_code == 0
            assert "Generation complete!" in result.output
            assert "Generated 1 files" in result.output
    
    def test_generate_missing_required_params(self, runner):
        """Test generate command with missing required parameters."""
        result = runner.invoke(cli, ['generate'])
        
        assert result.exit_code != 0
        assert "Missing option" in result.output or "Error" in result.output
    
    def test_generate_invalid_format(self, runner, temp_regex_db, temp_output_dir):
        """Test generate command with invalid format."""
        result = runner.invoke(cli, [
            'generate',
            '--output-dir', temp_output_dir,
            '--num-files', '1',
            '--formats', 'invalid_format',
            '--credential-types', 'test_key',
            '--regex-db', temp_regex_db,
            '--topics', 'test topic'
        ])
        
        assert result.exit_code != 0
        assert "Error" in result.output
    
    def test_validate_command(self, runner, temp_output_dir):
        """Test validate command."""
        # Create a test file
        test_file = Path(temp_output_dir) / "test.eml"
        test_file.write_text("Test content with TEST1234 credential")
        
        with patch('credentialforge.cli.ValidationAgent') as mock_validator:
            mock_instance = Mock()
            mock_instance.validate_file.return_value = {
                'valid': True,
                'credentials_found': ['TEST1234'],
                'quality_score': 85
            }
            mock_validator.return_value = mock_instance
            
            result = runner.invoke(cli, [
                'validate',
                '--file', str(test_file)
            ])
            
            assert result.exit_code == 0
            assert "File validation passed" in result.output
    
    def test_validate_command_verbose(self, runner, temp_output_dir):
        """Test validate command with verbose output."""
        # Create a test file
        test_file = Path(temp_output_dir) / "test.eml"
        test_file.write_text("Test content")
        
        with patch('credentialforge.cli.ValidationAgent') as mock_validator:
            mock_instance = Mock()
            mock_instance.validate_file.return_value = {
                'valid': True,
                'credentials_found': ['TEST1234'],
                'quality_score': 85
            }
            mock_validator.return_value = mock_instance
            
            result = runner.invoke(cli, [
                'validate',
                '--file', str(test_file),
                '--verbose'
            ])
            
            assert result.exit_code == 0
            assert "Credentials detected" in result.output
            assert "Content quality score" in result.output
    
    def test_db_add_command(self, runner, temp_regex_db):
        """Test database add command."""
        result = runner.invoke(cli, [
            'db', 'add',
            '--type', 'new_key',
            '--regex', '^NEW[0-9]{3}$',
            '--description', 'New Test Key',
            '--db-file', temp_regex_db
        ])
        
        assert result.exit_code == 0
        assert "Added credential type" in result.output
        
        # Verify the credential was added
        with open(temp_regex_db, 'r') as f:
            db_data = json.load(f)
            assert any(cred['type'] == 'new_key' for cred in db_data['credentials'])
    
    def test_db_list_command(self, runner, temp_regex_db):
        """Test database list command."""
        result = runner.invoke(cli, [
            'db', 'list',
            '--db-file', temp_regex_db
        ])
        
        assert result.exit_code == 0
        assert "test_key" in result.output
        assert "Test Key" in result.output
    
    def test_db_list_command_json(self, runner, temp_regex_db):
        """Test database list command with JSON output."""
        result = runner.invoke(cli, [
            'db', 'list',
            '--db-file', temp_regex_db,
            '--format', 'json'
        ])
        
        assert result.exit_code == 0
        # Should be valid JSON
        json.loads(result.output)
    
    def test_version_command(self, runner):
        """Test version command."""
        result = runner.invoke(cli, ['version'])
        
        assert result.exit_code == 0
        assert "CredentialForge version" in result.output
    
    def test_interactive_command(self, runner):
        """Test interactive command."""
        with patch('credentialforge.cli.InteractiveTerminal') as mock_terminal:
            mock_instance = Mock()
            mock_terminal.return_value = mock_instance
            
            # Simulate Ctrl+C
            result = runner.invoke(cli, ['interactive'], input='\x03')
            
            # Should handle KeyboardInterrupt gracefully
            assert result.exit_code == 0 or "Goodbye" in result.output
    
    def test_log_level_option(self, runner):
        """Test log level option."""
        result = runner.invoke(cli, ['--log-level', 'DEBUG', '--help'])
        
        assert result.exit_code == 0
        assert "CredentialForge" in result.output
    
    def test_config_file_option(self, runner):
        """Test config file option."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("defaults:\n  output_dir: ./test\n")
            config_file = f.name
        
        try:
            result = runner.invoke(cli, ['--config-file', config_file, '--help'])
            
            assert result.exit_code == 0
            assert "CredentialForge" in result.output
        finally:
            Path(config_file).unlink()
    
    def test_generate_with_llm_model(self, runner, temp_regex_db, temp_output_dir):
        """Test generate command with LLM model."""
        # Create a dummy model file
        model_file = Path(temp_output_dir) / "model.gguf"
        model_file.write_bytes(b"dummy model content")
        
        with patch('credentialforge.cli.LlamaInterface') as mock_llm, \
             patch('credentialforge.cli.OrchestratorAgent') as mock_orchestrator:
            
            mock_llm_instance = Mock()
            mock_llm.return_value = mock_llm_instance
            
            mock_orchestrator_instance = Mock()
            mock_orchestrator_instance.orchestrate_generation.return_value = {
                'files': ['test_file.eml'],
                'errors': [],
                'metadata': {
                    'total_files': 1,
                    'total_credentials': 1,
                    'generation_time': 1.0,
                    'files_by_format': {'eml': 1},
                    'credentials_by_type': {'test_key': 1}
                }
            }
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            result = runner.invoke(cli, [
                'generate',
                '--output-dir', temp_output_dir,
                '--num-files', '1',
                '--formats', 'eml',
                '--credential-types', 'test_key',
                '--regex-db', temp_regex_db,
                '--topics', 'test topic',
                '--llm-model', str(model_file)
            ])
            
            assert result.exit_code == 0
            assert "Generation complete!" in result.output
            mock_llm.assert_called_once()
    
    def test_generate_with_seed(self, runner, temp_regex_db, temp_output_dir):
        """Test generate command with seed for reproducibility."""
        with patch('credentialforge.cli.OrchestratorAgent') as mock_orchestrator:
            mock_instance = Mock()
            mock_instance.orchestrate_generation.return_value = {
                'files': ['test_file.eml'],
                'errors': [],
                'metadata': {
                    'total_files': 1,
                    'total_credentials': 1,
                    'generation_time': 1.0,
                    'files_by_format': {'eml': 1},
                    'credentials_by_type': {'test_key': 1}
                }
            }
            mock_orchestrator.return_value = mock_instance
            
            result = runner.invoke(cli, [
                'generate',
                '--output-dir', temp_output_dir,
                '--num-files', '1',
                '--formats', 'eml',
                '--credential-types', 'test_key',
                '--regex-db', temp_regex_db,
                '--topics', 'test topic',
                '--seed', '42'
            ])
            
            assert result.exit_code == 0
            assert "Generation complete!" in result.output
    
    def test_generate_with_batch_size(self, runner, temp_regex_db, temp_output_dir):
        """Test generate command with custom batch size."""
        with patch('credentialforge.cli.OrchestratorAgent') as mock_orchestrator:
            mock_instance = Mock()
            mock_instance.orchestrate_generation.return_value = {
                'files': ['test_file.eml'],
                'errors': [],
                'metadata': {
                    'total_files': 1,
                    'total_credentials': 1,
                    'generation_time': 1.0,
                    'files_by_format': {'eml': 1},
                    'credentials_by_type': {'test_key': 1}
                }
            }
            mock_orchestrator.return_value = mock_instance
            
            result = runner.invoke(cli, [
                'generate',
                '--output-dir', temp_output_dir,
                '--num-files', '5',
                '--formats', 'eml',
                '--credential-types', 'test_key',
                '--regex-db', temp_regex_db,
                '--topics', 'test topic',
                '--batch-size', '2'
            ])
            
            assert result.exit_code == 0
            assert "Generation complete!" in result.output
