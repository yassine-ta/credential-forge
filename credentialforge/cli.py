#!/usr/bin/env python3
"""Main CLI interface for CredentialForge."""

import sys
import click
import logging
from pathlib import Path
from typing import List, Optional

from .utils.logger import Logger
from .utils.config import ConfigManager
from .utils.validators import Validators
from .utils.interactive import InteractiveTerminal
from .agents.orchestrator import OrchestratorAgent
from .llm.llama_interface import LlamaInterface
from .db.regex_db import RegexDatabase


@click.group()
@click.option('--log-level', default='INFO', 
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='Set the logging level')
@click.option('--config-file', type=click.Path(exists=True),
              help='Path to configuration file')
@click.pass_context
def cli(ctx, log_level: str, config_file: Optional[str]):
    """CredentialForge - Synthetic document generation with embedded credentials.
    
    A sophisticated CLI tool for generating synthetic documents with embedded
    credentials for security testing, vulnerability assessment, and educational
    simulations.
    """
    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj['log_level'] = log_level
    ctx.obj['config_file'] = config_file
    
    # Setup logging
    logger = Logger('credentialforge', level=getattr(logging, log_level))
    ctx.obj['logger'] = logger
    
    # Load configuration
    config_manager = ConfigManager(config_file)
    ctx.obj['config'] = config_manager


@cli.command()
@click.option('--output-dir', required=True, type=click.Path(),
              help='Output directory for generated files')
@click.option('--num-files', default=1, type=int,
              help='Number of files to generate')
@click.option('--formats', default='eml', 
              help='Comma-separated formats (eml,msg,xlsx,pptx,vsdx)')
@click.option('--credential-types', required=True,
              help='Comma-separated credential types')
@click.option('--regex-db', required=True, type=click.Path(exists=True),
              help='Path to regex database file')
@click.option('--topics', required=True,
              help='Comma-separated topics for content generation')
@click.option('--language', default='en',
              help='Comma-separated languages (en,fr,es,de,it,ja,nl,pt,tr,zh)')
@click.option('--embed-strategy', default='random',
              type=click.Choice(['random', 'metadata', 'body']),
              help='Embedding strategy')
@click.option('--batch-size', default=10, type=int,
              help='Batch size for parallel processing')
@click.option('--seed', type=int, help='Random seed for reproducible results')
@click.option('--llm-model', type=click.Path(exists=True),
              help='Path to GGUF model file for offline LLM')
@click.option('--log-level', default='INFO',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='Logging level')
@click.pass_context
def generate(ctx, output_dir: str, num_files: int, formats: str,
             credential_types: str, regex_db: str, topics: str, language: str,
             embed_strategy: str, batch_size: int, seed: Optional[int],
             llm_model: Optional[str], log_level: str):
    """Generate synthetic documents with embedded credentials."""
    logger = ctx.obj['logger']
    config = ctx.obj['config']
    
    try:
        # Validate inputs
        Validators.validate_output_directory(output_dir)
        Validators.validate_file_formats(formats.split(','))
        
        # Parse parameters
        format_list = [f.strip() for f in formats.split(',')]
        credential_type_list = [t.strip() for t in credential_types.split(',')]
        topic_list = [t.strip() for t in topics.split(',')]
        language_list = [l.strip() for l in language.split(',')]
        
        # Load regex database
        logger.info(f"Loading regex database from {regex_db}")
        regex_database = RegexDatabase(regex_db)
        
        # Validate credential types
        for cred_type in credential_type_list:
            Validators.validate_credential_type(cred_type, regex_database)
        
        # Initialize LLM if provided
        llm_interface = None
        if llm_model:
            logger.info(f"Loading LLM model from {llm_model}")
            llm_interface = LlamaInterface(llm_model)
        
        # Create orchestrator
        orchestrator = OrchestratorAgent(llm_interface=llm_interface)
        
        # Prepare generation configuration
        generation_config = {
            'output_dir': output_dir,
            'num_files': num_files,
            'formats': format_list,
            'credential_types': credential_type_list,
            'topics': topic_list,
            'language': language_list,
            'embed_strategy': embed_strategy,
            'batch_size': batch_size,
            'seed': seed,
            'regex_db_path': regex_db,
            'log_level': log_level
        }
        
        # Generate files
        logger.info(f"Starting generation of {num_files} files")
        results = orchestrator.orchestrate_generation(generation_config)
        
        # Display results
        click.echo(f"\n✅ Generation complete!")
        click.echo(f"📁 Generated {len(results['files'])} files in {output_dir}")
        click.echo(f"🔑 Total credentials generated: {results['metadata']['total_credentials']}")
        click.echo(f"📊 Files by format: {results['metadata']['files_by_format']}")
        
        if results['errors']:
            click.echo(f"⚠️  {len(results['errors'])} errors occurred during generation")
            for error in results['errors']:
                logger.warning(f"Generation error: {error}")
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def interactive(ctx):
    """Launch interactive terminal mode for guided generation."""
    logger = ctx.obj['logger']
    config = ctx.obj['config']
    
    try:
        terminal = InteractiveTerminal()
        terminal.run()
    except KeyboardInterrupt:
        click.echo("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Interactive mode failed: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', required=True, type=click.Path(exists=True),
              help='Path to file to validate')
@click.option('--regex-db', type=click.Path(exists=True),
              help='Path to regex database for validation')
@click.option('--verbose', is_flag=True, help='Show detailed validation results')
@click.pass_context
def validate(ctx, file: str, regex_db: Optional[str], verbose: bool):
    """Validate generated files for credential detectability and content quality."""
    logger = ctx.obj['logger']
    
    try:
        from .agents.validation_agent import ValidationAgent
        
        validator = ValidationAgent()
        results = validator.validate_file(file, regex_db, verbose)
        
        if results['valid']:
            click.echo(f"✅ File validation passed: {file}")
            if verbose:
                click.echo(f"🔍 Credentials detected: {results['credentials_found']}")
                click.echo(f"📝 Content quality score: {results['quality_score']}")
        else:
            click.echo(f"❌ File validation failed: {file}")
            if results['errors']:
                for error in results['errors']:
                    click.echo(f"  - {error}")
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def db():
    """Manage regex database."""
    pass


@db.command('add')
@click.option('--type', required=True, help='Credential type identifier')
@click.option('--regex', required=True, help='Regex pattern for validation')
@click.option('--description', required=True, help='Human-readable description')
@click.option('--generator', help='Generator function specification')
@click.option('--db-file', default='regex_db.json', 
              help='Database file path')
@click.pass_context
def db_add(ctx, type: str, regex: str, description: str, 
           generator: Optional[str], db_file: str):
    """Add new credential type to database."""
    logger = ctx.obj['logger']
    
    try:
        from .db.regex_db import RegexDatabase
        
        # Load existing database or create new one
        if Path(db_file).exists():
            regex_db = RegexDatabase(db_file)
        else:
            regex_db = RegexDatabase()
        
        # Add new credential type
        regex_db.add_credential_type(type, regex, description, generator)
        regex_db.save(db_file)
        
        click.echo(f"✅ Added credential type '{type}' to {db_file}")
        
    except Exception as e:
        logger.error(f"Failed to add credential type: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@db.command('list')
@click.option('--db-file', default='regex_db.json',
              help='Database file path')
@click.option('--format', default='table',
              type=click.Choice(['table', 'json', 'yaml']),
              help='Output format')
@click.pass_context
def db_list(ctx, db_file: str, format: str):
    """List all credential types in database."""
    logger = ctx.obj['logger']
    
    try:
        from .db.regex_db import RegexDatabase
        
        if not Path(db_file).exists():
            click.echo(f"❌ Database file not found: {db_file}")
            sys.exit(1)
        
        regex_db = RegexDatabase(db_file)
        types = regex_db.list_credential_types()
        
        if format == 'table':
            click.echo(f"\n📋 Credential Types in {db_file}:")
            click.echo("-" * 60)
            for cred_type, info in types.items():
                click.echo(f"Type: {cred_type}")
                click.echo(f"  Description: {info['description']}")
                click.echo(f"  Regex: {info['regex']}")
                if info.get('generator'):
                    click.echo(f"  Generator: {info['generator']}")
                click.echo()
        elif format == 'json':
            import json
            click.echo(json.dumps(types, indent=2))
        elif format == 'yaml':
            import yaml
            click.echo(yaml.dump(types, default_flow_style=False))
        
    except Exception as e:
        logger.error(f"Failed to list credential types: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def version(ctx):
    """Show version information."""
    from . import __version__
    click.echo(f"CredentialForge version {__version__}")


@cli.command()
@click.option('--test', is_flag=True, help='Test network connectivity')
@click.option('--configure', is_flag=True, help='Configure network settings interactively')
@click.option('--ssl-verify/--no-ssl-verify', default=None, 
              help='Enable/disable SSL verification')
@click.option('--trusted-hosts', help='Comma-separated list of trusted hosts')
@click.option('--proxy', help='HTTP/HTTPS proxy URL')
@click.pass_context
def network(ctx, test: bool, configure: bool, ssl_verify: Optional[bool], 
           trusted_hosts: Optional[str], proxy: Optional[str]):
    """Configure network settings for corporate environments."""
    from .utils.network import configure_corporate_network, setup_corporate_ssl_env
    import os
    
    logger = ctx.obj['logger']
    
    try:
        if configure:
            # Run interactive configuration
            setup_corporate_ssl_env()
            return
        
        # Apply command-line options
        if ssl_verify is not None:
            os.environ['CREDENTIALFORGE_SSL_VERIFY'] = 'true' if ssl_verify else 'false'
            click.echo(f"✅ SSL verification {'enabled' if ssl_verify else 'disabled'}")
        
        if trusted_hosts:
            os.environ['CREDENTIALFORGE_TRUSTED_HOSTS'] = trusted_hosts
            click.echo(f"✅ Trusted hosts set to: {trusted_hosts}")
        
        if proxy:
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy
            click.echo(f"✅ Proxy set to: {proxy}")
        
        if test:
            # Test network connectivity
            click.echo("🔍 Testing network connectivity...")
            network_config = configure_corporate_network()
            
            test_urls = ["https://huggingface.co", "https://pypi.org"]
            for url in test_urls:
                result = network_config.test_connectivity(url)
                if result['success']:
                    click.echo(f"✅ {url} - OK ({result['response_time']}s)")
                else:
                    click.echo(f"❌ {url} - Failed: {result.get('error', 'Unknown error')}")
        
        # Show current settings
        click.echo("\n📋 Current Network Settings:")
        click.echo(f"  SSL Verify: {os.getenv('CREDENTIALFORGE_SSL_VERIFY', 'true')}")
        click.echo(f"  Trusted Hosts: {os.getenv('CREDENTIALFORGE_TRUSTED_HOSTS', 'none')}")
        click.echo(f"  HTTP Proxy: {os.getenv('HTTP_PROXY', 'none')}")
        click.echo(f"  HTTPS Proxy: {os.getenv('HTTPS_PROXY', 'none')}")
        
    except Exception as e:
        logger.error(f"Network configuration failed: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point for CredentialForge CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
