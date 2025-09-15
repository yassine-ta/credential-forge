#!/usr/bin/env python3
"""Test script for enhanced agentic AI file generation."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.agents.orchestrator import OrchestratorAgent
from credentialforge.db.regex_db import RegexDatabase


def test_enhanced_generation():
    """Test the enhanced generation features."""
    print("🚀 Testing Enhanced Agentic AI File Generation")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()
    
    # Enhanced configuration
    config = {
        'output_dir': './test_output',
        'formats': ['docx', 'xlsx', 'pdf'],
        'credential_types': ['aws_access_key', 'api_key', 'jwt_token', 'db_connection'],
        'topics': [
            'security audit, compliance review',
            'database migration, performance optimization', 
            'API documentation, monitoring setup',
            'system architecture, deployment procedures'
        ],
        'num_files': 3,
        'embed_strategy': 'random',
        'regex_db_path': './data/regex_db.json'
    }
    
    print(f"📋 Configuration:")
    print(f"  - Output directory: {config['output_dir']}")
    print(f"  - Formats: {config['formats']}")
    print(f"  - Credential types: {config['credential_types']}")
    print(f"  - Topics: {config['topics']}")
    print(f"  - Number of files: {config['num_files']}")
    print()
    
    try:
        # Generate files
        print("🤖 Starting agentic AI generation...")
        results = orchestrator.orchestrate_generation(config)
        
        print(f"✅ Generation completed!")
        print(f"  - Files generated: {len(results['files'])}")
        print(f"  - Errors: {len(results['errors'])}")
        print()
        
        # Display results
        print("📄 Generated Files:")
        for i, file_info in enumerate(results['files'], 1):
            print(f"  {i}. {file_info['path']}")
            print(f"     Format: {file_info['format']}")
            print(f"     Topic: {file_info['topic']}")
            print(f"     Credential Type: {file_info['credential_type']}")
            print()
        
        # Display errors if any
        if results['errors']:
            print("❌ Errors:")
            for error in results['errors']:
                print(f"  - {error}")
            print()
        
        # Display statistics
        stats = orchestrator.get_generation_stats()
        print("📊 Generation Statistics:")
        print(f"  - Total files generated: {stats['total_files']}")
        print(f"  - Total credentials embedded: {stats['total_credentials']}")
        if stats['total_files'] > 0:
            print(f"  - Average credentials per file: {stats['total_credentials'] / stats['total_files']:.1f}")
        print(f"  - Credentials by type:")
        for cred_type, count in stats['credentials_by_type'].items():
            print(f"    - {cred_type}: {count}")
        print()
        
        print("🎉 Enhanced generation test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = test_enhanced_generation()
    sys.exit(0 if success else 1)
