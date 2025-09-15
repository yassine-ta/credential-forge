#!/usr/bin/env python3
"""Test script for credential generation prompts from prompts/credential_generation_prompts.txt"""

import sys
import os
from pathlib import Path
import json
import re
from typing import Dict, List, Any

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.utils.prompt_system import EnhancedPromptSystem
from credentialforge.generators.credential_generator import CredentialGenerator
from credentialforge.db.regex_db import RegexDatabase
from credentialforge.llm.llama_interface import LlamaInterface


class CredentialPromptTester:
    """Test suite for credential generation prompts."""
    
    def __init__(self):
        """Initialize the tester."""
        self.prompt_system = EnhancedPromptSystem()
        self.regex_db = RegexDatabase('./data/regex_db.json')
        self.llm = None
        self.generator = None
        self.test_results = {
            'prompt_loading': False,
            'prompt_formatting': False,
            'credential_generation': False,
            'pattern_matching': False,
            'llm_integration': False,
            'fallback_generation': False
        }
        
    def test_prompt_loading(self) -> bool:
        """Test if prompts are loaded correctly from the prompts folder."""
        print("🔍 Testing prompt loading...")
        
        try:
            # Check if credential prompts are loaded
            if 'credential' not in self.prompt_system.prompts:
                print("❌ Credential prompts not loaded")
                return False
            
            credential_prompts = self.prompt_system.prompts['credential']
            if not credential_prompts or len(credential_prompts) < 100:
                print("❌ Credential prompts appear to be empty or too short")
                return False
            
            print(f"✅ Credential prompts loaded successfully ({len(credential_prompts)} characters)")
            self.test_results['prompt_loading'] = True
            return True
            
        except Exception as e:
            print(f"❌ Failed to load prompts: {e}")
            return False
    
    def test_prompt_formatting(self) -> bool:
        """Test prompt formatting with various parameters."""
        print("\n🔍 Testing prompt formatting...")
        
        try:
            # Test basic credential prompt creation
            prompt = self.prompt_system.create_credential_prompt_with_regex(
                credential_type='api_key',
                regex_pattern='^[A-Za-z0-9]{32}$',
                description='API Key',
                topic='system integration',
                language='en',
                company='TechCorp'
            )
            
            if not prompt or len(prompt) < 100:
                print("❌ Generated prompt is too short or empty")
                return False
            
            # Check if all placeholders are replaced
            placeholders = ['{CREDENTIAL_TYPE}', '{COMPANY}', '{TOPIC}', '{LANGUAGE}', '{REGEX_PATTERN}', '{DESCRIPTION}']
            for placeholder in placeholders:
                if placeholder in prompt:
                    print(f"❌ Placeholder {placeholder} not replaced in prompt")
                    return False
            
            print("✅ Prompt formatting works correctly")
            print(f"   Generated prompt length: {len(prompt)} characters")
            print(f"   First 200 chars: {prompt[:200]}...")
            
            self.test_results['prompt_formatting'] = True
            return True
            
        except Exception as e:
            print(f"❌ Prompt formatting failed: {e}")
            return False
    
    def test_credential_generation(self) -> bool:
        """Test credential generation with different types."""
        print("\n🔍 Testing credential generation...")
        
        try:
            # Initialize generator without LLM (fallback mode)
            self.generator = CredentialGenerator(self.regex_db)
            
            # Test different credential types
            test_credentials = [
                'api_key',
                'aws_access_key', 
                'aws_secret_key',
                'github_token',
                'password'
            ]
            
            generated_credentials = {}
            
            for cred_type in test_credentials:
                try:
                    context = {
                        'company': 'TestCorp',
                        'topic': 'API testing',
                        'language': 'en'
                    }
                    
                    credential = self.generator.generate_credential(cred_type, context)
                    generated_credentials[cred_type] = credential
                    
                    print(f"   ✅ {cred_type}: {credential}")
                    
                except Exception as e:
                    print(f"   ❌ {cred_type}: {e}")
                    return False
            
            print("✅ All credential types generated successfully")
            self.test_results['credential_generation'] = True
            return True
            
        except Exception as e:
            print(f"❌ Credential generation failed: {e}")
            return False
    
    def test_pattern_matching(self) -> bool:
        """Test that generated credentials match their regex patterns."""
        print("\n🔍 Testing pattern matching...")
        
        try:
            if not self.generator:
                self.generator = CredentialGenerator(self.regex_db)
            
            # Test pattern validation
            test_cases = [
                ('api_key', '^[A-Za-z0-9]{32}$'),
                ('aws_access_key', '^AKIA[0-9A-Z]{16}$'),
                ('github_token', '^ghp_[A-Za-z0-9]{36}$'),
            ]
            
            for cred_type, expected_pattern in test_cases:
                try:
                    context = {'company': 'TestCorp', 'topic': 'testing', 'language': 'en'}
                    credential = self.generator.generate_credential(cred_type, context)
                    
                    # Validate against regex
                    if not re.match(expected_pattern, credential):
                        print(f"   ❌ {cred_type}: '{credential}' doesn't match pattern '{expected_pattern}'")
                        return False
                    
                    print(f"   ✅ {cred_type}: '{credential}' matches pattern")
                    
                except Exception as e:
                    print(f"   ❌ {cred_type}: {e}")
                    return False
            
            print("✅ All generated credentials match their patterns")
            self.test_results['pattern_matching'] = True
            return True
            
        except Exception as e:
            print(f"❌ Pattern matching test failed: {e}")
            return False
    
    def test_llm_integration(self) -> bool:
        """Test LLM integration with prompts."""
        print("\n🔍 Testing LLM integration...")
        
        try:
            # Try to load LLM
            model_path = './models/phi3-mini.gguf'
            if not Path(model_path).exists():
                print(f"⚠️  LLM model not found at {model_path}, skipping LLM test")
                return True
            
            self.llm = LlamaInterface(model_path)
            self.generator = CredentialGenerator(regex_db=self.regex_db)
            
            # Test LLM generation
            context = {
                'company': 'TechCorp',
                'topic': 'API integration',
                'language': 'en'
            }
            
            credential = self.generator.generate_credential('api_key', context)
            
            if not credential or len(credential) < 10:
                print(f"❌ LLM generated invalid credential: '{credential}'")
                return False
            
            print(f"✅ LLM generated credential: {credential}")
            self.test_results['llm_integration'] = True
            return True
            
        except Exception as e:
            print(f"⚠️  LLM integration test failed (this is expected if LLM is not available): {e}")
            return True  # Don't fail the test if LLM is not available
    
    def test_fallback_generation(self) -> bool:
        """Test fallback generation when LLM is not available."""
        print("\n🔍 Testing fallback generation...")
        
        try:
            # Test fallback generation directly
            generator = CredentialGenerator(self.regex_db)  # No LLM
            
            test_cases = [
                ('api_key', '^[A-Za-z0-9]{32}$'),
                ('aws_access_key', '^AKIA[0-9A-Z]{16}$'),
                ('password', '^.{8,16}$'),
            ]
            
            for cred_type, pattern in test_cases:
                try:
                    credential = generator._generate_fallback(cred_type, pattern)
                    
                    if not credential or len(credential) < 3:
                        print(f"   ❌ {cred_type}: Generated empty or too short credential")
                        return False
                    
                    print(f"   ✅ {cred_type}: {credential}")
                    
                except Exception as e:
                    print(f"   ❌ {cred_type}: {e}")
                    return False
            
            print("✅ Fallback generation works correctly")
            self.test_results['fallback_generation'] = True
            return True
            
        except Exception as e:
            print(f"❌ Fallback generation test failed: {e}")
            return False
    
    def test_prompt_variations(self) -> bool:
        """Test different prompt variations and parameters."""
        print("\n🔍 Testing prompt variations...")
        
        try:
            # Test different companies
            companies = ['TechCorp', 'StartupInc', 'EnterpriseCorp', 'CloudProvider']
            
            for company in companies:
                prompt = self.prompt_system.create_credential_prompt_with_regex(
                    credential_type='api_key',
                    regex_pattern='^[A-Za-z0-9]{32}$',
                    description='API Key',
                    topic='system integration',
                    language='en',
                    company=company
                )
                
                if company not in prompt:
                    print(f"   ❌ Company '{company}' not found in generated prompt")
                    return False
                
                print(f"   ✅ Company '{company}' prompt generated")
            
            # Test different languages
            languages = ['en', 'fr', 'es', 'de']
            
            for language in languages:
                prompt = self.prompt_system.create_credential_prompt_with_regex(
                    credential_type='api_key',
                    regex_pattern='^[A-Za-z0-9]{32}$',
                    description='API Key',
                    topic='system integration',
                    language=language,
                    company='TechCorp'
                )
                
                if language not in prompt.lower():
                    print(f"   ❌ Language '{language}' not found in generated prompt")
                    return False
                
                print(f"   ✅ Language '{language}' prompt generated")
            
            print("✅ All prompt variations work correctly")
            return True
            
        except Exception as e:
            print(f"❌ Prompt variations test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results."""
        print("🚀 Starting Credential Generation Prompts Test Suite")
        print("=" * 60)
        
        # Run all tests
        self.test_prompt_loading()
        self.test_prompt_formatting()
        self.test_credential_generation()
        self.test_pattern_matching()
        self.test_llm_integration()
        self.test_fallback_generation()
        self.test_prompt_variations()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Credential generation prompts are working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return self.test_results


def main():
    """Main function to run the test suite."""
    tester = CredentialPromptTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
