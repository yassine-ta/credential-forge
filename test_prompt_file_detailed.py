#!/usr/bin/env python3
"""Detailed test script specifically for credential_generation_prompts.txt file."""

import sys
import os
from pathlib import Path
import re
from typing import Dict, List, Any

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.utils.prompt_system import EnhancedPromptSystem


class PromptFileTester:
    """Detailed tester for the credential_generation_prompts.txt file."""
    
    def __init__(self):
        """Initialize the tester."""
        self.prompt_system = EnhancedPromptSystem()
        self.prompt_file_path = Path("prompts/credential_generation_prompts.txt")
        
    def test_prompt_file_exists(self) -> bool:
        """Test if the prompt file exists and is readable."""
        print("🔍 Testing prompt file existence...")
        
        if not self.prompt_file_path.exists():
            print(f"❌ Prompt file not found: {self.prompt_file_path}")
            return False
        
        try:
            content = self.prompt_file_path.read_text(encoding='utf-8')
            if len(content) < 1000:
                print("❌ Prompt file appears to be too short")
                return False
            
            print(f"✅ Prompt file exists and is readable ({len(content)} characters)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to read prompt file: {e}")
            return False
    
    def test_prompt_sections(self) -> bool:
        """Test if all required prompt sections are present."""
        print("\n🔍 Testing prompt sections...")
        
        try:
            content = self.prompt_file_path.read_text(encoding='utf-8')
            
            required_sections = [
                "CREDENTIAL GENERATION PROMPT",
                "CREDENTIAL VALIDATION PROMPT", 
                "BATCH CREDENTIAL GENERATION PROMPT",
                "CONTEXT-AWARE CREDENTIAL GENERATION PROMPT"
            ]
            
            for section in required_sections:
                if section not in content:
                    print(f"❌ Required section not found: {section}")
                    return False
                print(f"   ✅ Found section: {section}")
            
            print("✅ All required prompt sections are present")
            return True
            
        except Exception as e:
            print(f"❌ Failed to test prompt sections: {e}")
            return False
    
    def test_placeholder_variables(self) -> bool:
        """Test if all required placeholder variables are present."""
        print("\n🔍 Testing placeholder variables...")
        
        try:
            content = self.prompt_file_path.read_text(encoding='utf-8')
            
            required_placeholders = [
                "{CREDENTIAL_TYPE}",
                "{COMPANY}",
                "{TOPIC}",
                "{LANGUAGE}",
                "{REGEX_PATTERN}",
                "{DESCRIPTION}",
                "{COUNT}",
                "{INDUSTRY}",
                "{COMPANY_SIZE}",
                "{USE_CASE}"
            ]
            
            for placeholder in required_placeholders:
                if placeholder not in content:
                    print(f"❌ Required placeholder not found: {placeholder}")
                    return False
                print(f"   ✅ Found placeholder: {placeholder}")
            
            print("✅ All required placeholder variables are present")
            return True
            
        except Exception as e:
            print(f"❌ Failed to test placeholder variables: {e}")
            return False
    
    def test_prompt_structure(self) -> bool:
        """Test the structure and format of the prompts."""
        print("\n🔍 Testing prompt structure...")
        
        try:
            content = self.prompt_file_path.read_text(encoding='utf-8')
            
            # Check for XML-like tags
            xml_tags = ["<thinking>", "<reasoning>", "<context>", "<instructions>", "<output>", 
                       "<validation_rules>", "<batch_instructions>", "<context_analysis>", 
                       "<contextual_instructions>"]
            
            for tag in xml_tags:
                if tag not in content:
                    print(f"❌ Required XML tag not found: {tag}")
                    return False
                print(f"   ✅ Found XML tag: {tag}")
            
            # Check for proper closing tags
            for tag in xml_tags:
                closing_tag = tag.replace("<", "</")
                if closing_tag not in content:
                    print(f"❌ Closing tag not found: {closing_tag}")
                    return False
                print(f"   ✅ Found closing tag: {closing_tag}")
            
            print("✅ Prompt structure is correct")
            return True
            
        except Exception as e:
            print(f"❌ Failed to test prompt structure: {e}")
            return False
    
    def test_prompt_loading_in_system(self) -> bool:
        """Test if prompts are properly loaded by the prompt system."""
        print("\n🔍 Testing prompt loading in system...")
        
        try:
            # Check if prompts are loaded
            if 'credential' not in self.prompt_system.prompts:
                print("❌ Credential prompts not loaded in prompt system")
                return False
            
            credential_prompts = self.prompt_system.prompts['credential']
            
            # Check if the loaded content matches the file content
            file_content = self.prompt_file_path.read_text(encoding='utf-8')
            
            if credential_prompts != file_content:
                print("❌ Loaded prompts don't match file content")
                return False
            
            print("✅ Prompts are properly loaded in the system")
            return True
            
        except Exception as e:
            print(f"❌ Failed to test prompt loading: {e}")
            return False
    
    def test_prompt_generation(self) -> bool:
        """Test actual prompt generation with various parameters."""
        print("\n🔍 Testing prompt generation...")
        
        try:
            test_cases = [
                {
                    'credential_type': 'api_key',
                    'regex_pattern': '^[A-Za-z0-9]{32}$',
                    'description': 'API Key',
                    'topic': 'system integration',
                    'language': 'en',
                    'company': 'TechCorp'
                },
                {
                    'credential_type': 'aws_access_key',
                    'regex_pattern': '^AKIA[0-9A-Z]{16}$',
                    'description': 'AWS Access Key ID',
                    'topic': 'cloud infrastructure',
                    'language': 'en',
                    'company': 'CloudCorp'
                },
                {
                    'credential_type': 'jwt_token',
                    'regex_pattern': '^eyJ[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+$',
                    'description': 'JWT Token',
                    'topic': 'authentication',
                    'language': 'fr',
                    'company': 'AuthCorp'
                }
            ]
            
            for i, test_case in enumerate(test_cases, 1):
                try:
                    prompt = self.prompt_system.create_credential_prompt_with_regex(**test_case)
                    
                    if not prompt or len(prompt) < 1000:
                        print(f"   ❌ Test case {i}: Generated prompt too short")
                        return False
                    
                    # Check if all placeholders are replaced
                    for key, value in test_case.items():
                        if f"{{{key.upper()}}}" in prompt:
                            print(f"   ❌ Test case {i}: Placeholder {{{key.upper()}}} not replaced")
                            return False
                    
                    print(f"   ✅ Test case {i}: {test_case['credential_type']} prompt generated successfully")
                    
                except Exception as e:
                    print(f"   ❌ Test case {i}: {e}")
                    return False
            
            print("✅ All prompt generation tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Failed to test prompt generation: {e}")
            return False
    
    def test_prompt_quality(self) -> bool:
        """Test the quality and completeness of generated prompts."""
        print("\n🔍 Testing prompt quality...")
        
        try:
            prompt = self.prompt_system.create_credential_prompt_with_regex(
                credential_type='api_key',
                regex_pattern='^[A-Za-z0-9]{32}$',
                description='API Key',
                topic='system integration',
                language='en',
                company='TechCorp'
            )
            
            # Check for key elements
            quality_checks = [
                ("Company context", "TechCorp" in prompt),
                ("Credential type", "api_key" in prompt),
                ("Regex pattern", "^[A-Za-z0-9]{32}$" in prompt),
                ("Topic context", "system integration" in prompt),
                ("Language specification", "English" in prompt or "en" in prompt),
                ("Instructions section", "<instructions>" in prompt),
                ("Critical requirements", "CRITICAL REQUIREMENTS" in prompt),
                ("Forbidden elements", "FORBIDDEN ELEMENTS" in prompt),
                ("Generation approach", "GENERATION APPROACH" in prompt)
            ]
            
            for check_name, check_result in quality_checks:
                if not check_result:
                    print(f"   ❌ Quality check failed: {check_name}")
                    return False
                print(f"   ✅ Quality check passed: {check_name}")
            
            print("✅ All prompt quality checks passed")
            return True
            
        except Exception as e:
            print(f"❌ Failed to test prompt quality: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests and return overall result."""
        print("🚀 Starting Detailed Credential Generation Prompts Test")
        print("=" * 70)
        
        tests = [
            self.test_prompt_file_exists,
            self.test_prompt_sections,
            self.test_placeholder_variables,
            self.test_prompt_structure,
            self.test_prompt_loading_in_system,
            self.test_prompt_generation,
            self.test_prompt_quality
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        print("\n" + "=" * 70)
        print("📊 DETAILED TEST RESULTS")
        print("=" * 70)
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All detailed tests passed! The credential_generation_prompts.txt file is working perfectly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
            return False


def main():
    """Main function to run the detailed test suite."""
    tester = PromptFileTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
