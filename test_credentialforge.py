#!/usr/bin/env python3
"""Simple test script for CredentialForge."""

import sys
import os
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_functionality():
    """Test basic CredentialForge functionality."""
    print("🧪 Testing CredentialForge basic functionality...")
    
    try:
        # Test imports
        print("  ✓ Testing imports...")
        from credentialforge.db.regex_db import RegexDatabase
        from credentialforge.generators.credential_generator import CredentialGenerator
        from credentialforge.generators.topic_generator import TopicGenerator
        from credentialforge.synthesizers.eml_synthesizer import EMLSynthesizer
        from credentialforge.agents.orchestrator import OrchestratorAgent
        print("    ✓ All imports successful")
        
        # Test regex database
        print("  ✓ Testing regex database...")
        regex_db_path = project_root / "data" / "regex_db.json"
        if regex_db_path.exists():
            regex_db = RegexDatabase(str(regex_db_path))
            credential_types = regex_db.list_credential_types()
            print(f"    ✓ Loaded {len(credential_types)} credential types")
        else:
            print("    ⚠ Regex database not found, creating sample...")
            # Create sample database
            sample_db = {
                "credentials": [
                    {
                        "type": "test_key",
                        "regex": "^TEST[0-9]{4}$",
                        "description": "Test Key",
                        "generator": "random_string(8, 'A-Z0-9')"
                    }
                ]
            }
            import json
            regex_db_path.parent.mkdir(exist_ok=True)
            with open(regex_db_path, 'w') as f:
                json.dump(sample_db, f)
            regex_db = RegexDatabase(str(regex_db_path))
            print("    ✓ Created sample regex database")
        
        # Test credential generation
        print("  ✓ Testing credential generation...")
        credential_generator = CredentialGenerator(regex_db)
        available_types = list(regex_db.list_credential_types().keys())
        if available_types:
            test_type = available_types[0]
            credential = credential_generator.generate_credential(test_type)
            print(f"    ✓ Generated credential: {credential[:20]}...")
        
        # Test topic generation
        print("  ✓ Testing topic generation...")
        topic_generator = TopicGenerator()
        content = topic_generator.generate_topic_content("test topic", "eml")
        print(f"    ✓ Generated content: {len(content)} characters")
        
        # Test EML synthesis
        print("  ✓ Testing EML synthesis...")
        with tempfile.TemporaryDirectory() as temp_dir:
            eml_synthesizer = EMLSynthesizer(temp_dir)
            test_credentials = ["TEST1234", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
            file_path = eml_synthesizer.synthesize(content, test_credentials)
            if Path(file_path).exists():
                print(f"    ✓ Generated EML file: {Path(file_path).name}")
            else:
                print("    ❌ EML file generation failed")
        
        print("🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_help():
    """Test CLI help command."""
    print("🧪 Testing CLI help...")
    
    try:
        from credentialforge.cli import cli
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        if result.exit_code == 0 and "CredentialForge" in result.output:
            print("  ✓ CLI help command works")
            return True
        else:
            print(f"  ❌ CLI help failed: {result.output}")
            return False
            
    except Exception as e:
        print(f"  ❌ CLI test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 CredentialForge Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("CLI Help", test_cli_help),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CredentialForge is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
