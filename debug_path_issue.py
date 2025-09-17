#!/usr/bin/env python3
"""Debug script to identify the path handling issue."""

import sys
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.agents.orchestrator import OrchestratorAgent
from credentialforge.db.regex_db import RegexDatabase

def debug_path_issue():
    """Debug the path handling issue."""
    try:
        # Initialize components
        regex_db = RegexDatabase('./data/regex_db.json')
        
        # Create temporary output directory
        output_dir = tempfile.mkdtemp()
        print(f"Output directory: {output_dir}")
        
        # Configuration
        config = {
            'output_dir': output_dir,
            'num_files': 1,
            'formats': ['eml'],
            'credential_types': ['api_key'],
            'topics': ['test generation'],
            'embed_strategy': 'random',
            'batch_size': 1,
            'seed': 42,
            'use_multiprocessing': False,  # Disable multiprocessing for easier debugging
            'parallel_workers': 1
        }
        
        # Create orchestrator
        orchestrator = OrchestratorAgent(regex_db, config)
        
        # Try generation
        print("Starting generation...")
        result = orchestrator.orchestrate_generation(config)
        
        print(f"Generation successful!")
        print(f"Files generated: {len(result.get('files', []))}")
        print(f"Errors: {result.get('errors', [])}")
        
        if result.get('files'):
            for file_info in result['files']:
                print(f"Generated file: {file_info}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_path_issue()
    sys.exit(0 if success else 1)
