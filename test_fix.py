#!/usr/bin/env python3
"""Test script to verify the PathLike fix."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from credentialforge.agents.orchestrator import OrchestratorAgent
from credentialforge.db.regex_db import RegexDatabase
import tempfile
from pathlib import Path

def test_generation():
    """Test file generation to see if PathLike error is fixed."""
    try:
        # Create temp output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            # Initialize orchestrator with correct parameters
            orchestrator = OrchestratorAgent()
            
            print("🧪 Testing file generation with PathLike fix...")
            
            # Generate a small batch using the generate_files method
            results = orchestrator.generate_files(
                num_files=2,
                formats=['pdf'],
                topics=['Test topic'],
                credential_types=['api_key'],
                regex_db_path="./data/regex_db.json",
                output_dir=output_dir
            )
            
            print(f"✅ Generated {len(results['files'])} files")
            print(f"❌ Errors: {len(results['errors'])}")
            
            # Check file types
            for file_path in results['files']:
                print(f"📄 File type: {type(file_path)} - {file_path}")
                if isinstance(file_path, dict):
                    print("⚠️  WARNING: File is still a dictionary!")
                    return False
                else:
                    print("✅ File is a string/Path as expected")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_generation()
    if success:
        print("\n🎉 Test passed! PathLike error should be fixed.")
    else:
        print("\n💥 Test failed. PathLike error may still exist.")
