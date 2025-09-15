"""Enhanced Prompt System for CredentialForge with Company Language Mapping."""

import os
import json
import random
from typing import Dict, List, Optional, Any
from pathlib import Path


class EnhancedPromptSystem:
    """Enhanced prompt system with company language mapping integration."""
    
    def __init__(self, prompts_dir: str = "prompts", mapping_file: str = "data/company_language_mapping.json"):
        """Initialize the enhanced prompt system.
        
        Args:
            prompts_dir: Directory containing prompt files
            mapping_file: Path to company language mapping file
        """
        self.prompts_dir = Path(prompts_dir)
        self.mapping_file = Path(mapping_file)
        self.company_mapping = self._load_company_mapping()
        self.prompts = self._load_prompts()
        
    def _load_company_mapping(self) -> Dict[str, Any]:
        """Load company language mapping."""
        try:
            # Try absolute path first
            if self.mapping_file.exists():
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Try relative to current working directory
                alt_path = Path("data/company_language_mapping.json")
                if alt_path.exists():
                    with open(alt_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                else:
                    print(f"Warning: Company mapping file not found at {self.mapping_file} or {alt_path}")
                    return {"company_language_mapping": {"companies": {}}}
        except Exception as e:
            print(f"Warning: Could not load company mapping: {e}")
            return {"company_language_mapping": {"companies": {}}}
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load all prompt files."""
        prompts = {}
        
        # Load system prompts
        system_file = self.prompts_dir / "system_prompts.txt"
        if system_file.exists():
            prompts['system'] = system_file.read_text(encoding='utf-8')
        
        # Load enhanced content generation prompts (preferred)
        enhanced_file = self.prompts_dir / "enhanced_content_prompts.txt"
        if enhanced_file.exists():
            prompts['content'] = enhanced_file.read_text(encoding='utf-8')
        else:
            # Fallback to original content prompts
            content_file = self.prompts_dir / "content_generation_prompts.txt"
            if content_file.exists():
                prompts['content'] = content_file.read_text(encoding='utf-8')
        
        # Load validation prompts
        validation_file = self.prompts_dir / "validation_prompts.txt"
        if validation_file.exists():
            prompts['validation'] = validation_file.read_text(encoding='utf-8')
        
        # Load language-specific prompts
        language_file = self.prompts_dir / "language_specific_prompts.txt"
        if language_file.exists():
            prompts['language'] = language_file.read_text(encoding='utf-8')
        
        # Load credential generation prompts
        credential_file = self.prompts_dir / "credential_generation_prompts.txt"
        if credential_file.exists():
            prompts['credential'] = credential_file.read_text(encoding='utf-8')
        
        return prompts
    
    def get_company_info(self, company_name: Optional[str] = None) -> Dict[str, str]:
        """Get company information including language and region.
        
        Args:
            company_name: Name of the company (optional)
            
        Returns:
            Dictionary with company information
        """
        if not company_name:
            # Return default company info
            return {
                'name': 'TechCorp Solutions',
                'language': 'en',
                'country': 'United States',
                'region': 'North America'
            }
        
        # Get all company sections
        mapping = self.company_mapping.get('company_language_mapping', {})
        all_companies = {}
        
        # Merge companies from all sections
        for section_name in ['companies', 'axa_companies']:
            if section_name in mapping:
                section_data = mapping[section_name]
                # Only update if it's a dictionary, not a list
                if isinstance(section_data, dict):
                    all_companies.update(section_data)
        
        # Try to find exact match first
        if company_name in all_companies:
            company_info = all_companies[company_name]
            return {
                'name': company_name,
                'language': company_info.get('language', 'en'),
                'country': company_info.get('country', 'United States'),
                'region': company_info.get('region', 'North America')
            }
        
        # Try to find partial match
        for comp_name, comp_info in all_companies.items():
            if company_name.lower() in comp_name.lower() or comp_name.lower() in company_name.lower():
                return {
                    'name': comp_name,
                    'language': comp_info.get('language', 'en'),
                    'country': comp_info.get('country', 'United States'),
                    'region': comp_info.get('region', 'North America')
                }
        
        # Fallback to default
        return {
            'name': company_name,
            'language': 'en',
            'country': 'United States',
            'region': 'North America'
        }
    
    def get_random_company(self, language: Optional[str] = None) -> Dict[str, str]:
        """Get a random company that matches the specified language.
        
        Args:
            language: Target language (optional)
            
        Returns:
            Dictionary with company information
        """
        # Get all company sections
        mapping = self.company_mapping.get('company_language_mapping', {})
        all_companies = {}
        
        # Merge companies from all sections
        for section_name in ['companies', 'axa_companies']:
            if section_name in mapping:
                section_data = mapping[section_name]
                # Only update if it's a dictionary, not a list
                if isinstance(section_data, dict):
                    all_companies.update(section_data)
        
        if language:
            # Filter companies by language
            matching_companies = [
                (name, info) for name, info in all_companies.items()
                if info.get('language') == language
            ]
            if matching_companies:
                name, info = random.choice(matching_companies)
                return {
                    'name': name,
                    'language': info.get('language', 'en'),
                    'country': info.get('country', 'United States'),
                    'region': info.get('region', 'North America')
                }
        
        # Fallback to any random company
        if all_companies:
            name, info = random.choice(list(all_companies.items()))
            return {
                'name': name,
                'language': info.get('language', 'en'),
                'country': info.get('country', 'United States'),
                'region': info.get('region', 'North America')
            }
        
        # Ultimate fallback
        return {
            'name': 'TechCorp Solutions',
            'language': 'en',
            'country': 'United States',
            'region': 'North America'
        }
    
    def get_language_info(self, language_code: str) -> Dict[str, str]:
        """Get language information from the mapping.
        
        Args:
            language_code: Language code (e.g., 'en', 'fr', 'es')
            
        Returns:
            Dictionary with language information
        """
        language_codes = self.company_mapping.get('company_language_mapping', {}).get('language_codes', {})
        
        return {
            'code': language_code,
            'name': language_codes.get(language_code, language_code.upper()),
            'instruction': self._get_language_instruction(language_code)
        }
    
    def _get_language_instruction(self, language_code: str) -> str:
        """Get language-specific instruction from prompts."""
        language_prompts = self.prompts.get('language', '')
        
        # Parse language-specific instructions
        lines = language_prompts.split('\n')
        current_lang = None
        instruction = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('## ') and f'({language_code})' in line:
                current_lang = language_code
            elif current_lang == language_code and line.startswith('LANGUAGE_INSTRUCTION:'):
                instruction = line.replace('LANGUAGE_INSTRUCTION:', '').strip()
                break
        
        return instruction or f"Generate all content in {language_code.upper()}"
    
    def create_validation_prompt(self, topic: str, credential_types: List[str], 
                               language: str, format_type: str, 
                               company: Optional[str] = None) -> str:
        """Create a validation prompt with company context.
        
        Args:
            topic: Document topic
            credential_types: List of credential types
            language: Target language
            format_type: File format
            company: Company name (optional)
            
        Returns:
            Formatted validation prompt
        """
        company_info = self.get_company_info(company)
        language_info = self.get_language_info(language)
        
        prompt_template = self.prompts.get('content', '')
        validation_section = self._extract_section(prompt_template, 'VALIDATION PROMPT')
        
        if not validation_section:
            # Fallback validation prompt
            return f"""CRITICAL VALIDATION - UNDERSTAND THESE REQUIREMENTS:

GENERATION TASK:
TOPIC: {topic}
CREDENTIAL TYPES: {', '.join(credential_types)}
LANGUAGE: {language_info['name']} (MUST be in this language only)
FORMAT: {format_type}
COMPANY: {company_info['name']} ({company_info['country']})

STRICT REQUIREMENTS TO FOLLOW:
1. ALL CONTENT MUST BE ABOUT: {topic}
2. ALL CREDENTIALS MUST BE: {', '.join(credential_types)}
3. ALL TEXT MUST BE IN: {language_info['name']} (NO OTHER LANGUAGE ALLOWED)
4. ALL CONTENT MUST BE FOR: {format_type} format
5. ALL CONTENT MUST BE APPROPRIATE FOR: {company_info['name']}

DO NOT DEVIATE FROM THESE REQUIREMENTS.
ACKNOWLEDGE: I understand and will follow these requirements exactly for {company_info['name']}.
"""
        
        return validation_section.format(
            TOPIC=topic,
            CREDENTIAL_TYPES=', '.join(credential_types),
            LANGUAGE=language_info['name'],
            FORMAT=format_type,
            COMPANY=company_info['name']
        )
    
    def create_title_prompt(self, topic: str, language: str, format_type: str, 
                          company: Optional[str] = None) -> str:
        """Create a title generation prompt with company context.
        
        Args:
            topic: Document topic
            language: Target language
            format_type: File format
            company: Company name (optional)
            
        Returns:
            Formatted title prompt
        """
        company_info = self.get_company_info(company)
        language_info = self.get_language_info(language)
        
        prompt_template = self.prompts.get('content', '')
        title_section = self._extract_section(prompt_template, 'TITLE GENERATION PROMPT')
        
        if not title_section:
            # Fallback title prompt
            return f"""CRITICAL INSTRUCTIONS - FOLLOW EXACTLY:

TOPIC: {topic}
LANGUAGE: {language_info['name']} (MUST be in this language only - NO EXCEPTIONS)
FORMAT: {format_type}
COMPANY: {company_info['name']}

STRICT REQUIREMENTS:
1. TITLE MUST BE SPECIFICALLY ABOUT: {topic}
2. LANGUAGE MUST BE: {language_info['name']} (NO OTHER LANGUAGE ALLOWED)
3. FORMAT MUST BE: {format_type}
4. COMPANY CONTEXT: {company_info['name']}
5. TITLE MUST BE: Professional, clear, descriptive
6. LENGTH: Maximum 8 words
7. STYLE: Technical document title appropriate for {company_info['name']}

LANGUAGE ENFORCEMENT: If you generate a title in any language other than {language_info['name']}, you have FAILED.

GENERATE TITLE NOW - MUST BE IN {language_info['name']} ABOUT {topic} FOR {company_info['name']}:
"""
        
        return title_section.format(
            TOPIC=topic,
            LANGUAGE=language_info['name'],
            FORMAT=format_type,
            COMPANY=company_info['name']
        )
    
    def create_section_prompt(self, topic: str, section_name: str, language: str, 
                            format_type: str, company: Optional[str] = None) -> str:
        """Create a section content prompt with company context.
        
        Args:
            topic: Document topic
            section_name: Section name
            language: Target language
            format_type: File format
            company: Company name (optional)
            
        Returns:
            Formatted section prompt
        """
        company_info = self.get_company_info(company)
        language_info = self.get_language_info(language)
        
        prompt_template = self.prompts.get('content', '')
        section_section = self._extract_section(prompt_template, 'SECTION CONTENT PROMPT')
        
        if not section_section:
            # Fallback section prompt
            return f"""CRITICAL INSTRUCTIONS - FOLLOW EXACTLY:

TOPIC: {topic}
LANGUAGE: {language_info['name']} (MUST be in this language only - NO EXCEPTIONS)
FORMAT: {format_type}
SECTION: {section_name}
COMPANY: {company_info['name']}

STRICT REQUIREMENTS:
1. CONTENT MUST BE SPECIFICALLY ABOUT: {topic}
2. LANGUAGE MUST BE: {language_info['name']} (NO OTHER LANGUAGE ALLOWED)
3. FORMAT MUST BE: {format_type}
4. SECTION MUST BE: {section_name}
5. COMPANY CONTEXT: {company_info['name']}
6. CONTENT MUST BE: Professional, technical, realistic, detailed
7. LENGTH: 150-300 words
8. TONE: Professional and technical appropriate for {company_info['name']}

LANGUAGE ENFORCEMENT: If you generate content in any language other than {language_info['name']}, you have FAILED.

GENERATE CONTENT NOW - MUST BE IN {language_info['name']} ABOUT {topic} FOR {company_info['name']} {format_type} {section_name}:
"""
        
        return section_section.format(
            TOPIC=topic,
            LANGUAGE=language_info['name'],
            FORMAT=format_type,
            SECTION=section_name,
            COMPANY=company_info['name']
        )
    
    def create_credential_prompt(self, credential_type: str, language: str, 
                               company: Optional[str] = None) -> str:
        """Create a credential generation prompt with company context.
        
        Args:
            credential_type: Type of credential to generate
            language: Target language
            company: Company name (optional)
            
        Returns:
            Formatted credential prompt
        """
        company_info = self.get_company_info(company)
        language_info = self.get_language_info(language)
        
        prompt_template = self.prompts.get('content', '')
        credential_section = self._extract_section(prompt_template, 'CREDENTIAL GENERATION PROMPT')
        
        if not credential_section:
            # Fallback credential prompt
            credential_type_upper = credential_type.upper()
            return f"""CRITICAL INSTRUCTIONS - FOLLOW EXACTLY:

CREDENTIAL TYPE: {credential_type}
LANGUAGE: {language_info['name']} (MUST be in this language only - NO EXCEPTIONS)
COMPANY: {company_info['name']}

STRICT REQUIREMENTS:
1. GENERATE A REALISTIC {credential_type_upper} VALUE
2. MUST BE PROFESSIONAL AND REALISTIC FOR {company_info['name']}
3. MUST BE APPROPRIATE FOR {credential_type_upper}
4. LENGTH: 8-32 characters
5. FORMAT: Standard {credential_type} format
6. NO PLACEHOLDERS: Do NOT use "example", "generated", "test", or similar words

CREDENTIAL ENFORCEMENT: Generate a REAL credential that would be found in {company_info['name']}'s systems.

GENERATE {credential_type_upper} VALUE NOW FOR {company_info['name']}:
"""
        
        return credential_section.format(
            CREDENTIAL_TYPE=credential_type,
            CREDENTIAL_TYPE_UPPER=credential_type.upper(),
            LANGUAGE=language_info['name'],
            COMPANY=company_info['name']
        )
    
    def create_credential_prompt_with_regex(self, credential_type: str, regex_pattern: str, 
                                          description: str, topic: str, language: str, 
                                          company: Optional[str] = None, example: str = "") -> str:
        """Create a credential generation prompt with regex pattern and context.
        
        Args:
            credential_type: Type of credential to generate
            regex_pattern: Regex pattern that the credential must match
            description: Description of the credential type
            topic: Topic context for the credential
            language: Target language
            company: Company name (optional)
            example: Example credential from regex database
            
        Returns:
            Formatted credential prompt with regex pattern
        """
        company_info = self.get_company_info(company)
        language_info = self.get_language_info(language)
        
        # Get credential prompt template
        credential_template = self.prompts.get('credential', '')
        if not credential_template:
            # Fallback if credential prompts not loaded
            return self._create_fallback_credential_prompt(
                credential_type, regex_pattern, description, topic, 
                language_info['name'], company_info['name'], example
            )
        
        # Extract the main credential generation prompt
        credential_section = self._extract_section(credential_template, 'CREDENTIAL GENERATION PROMPT')
        
        if not credential_section:
            return self._create_fallback_credential_prompt(
                credential_type, regex_pattern, description, topic, 
                language_info['name'], company_info['name']
            )
        
        return credential_section.format(
            CREDENTIAL_TYPE=credential_type,
            REGEX_PATTERN=regex_pattern,
            DESCRIPTION=description,
            EXAMPLE=example,
            TOPIC=topic,
            LANGUAGE=language_info['name'],
            COMPANY=company_info['name']
        )
    
    def _create_fallback_credential_prompt(self, credential_type: str, regex_pattern: str, 
                                         description: str, topic: str, language: str, 
                                         company: str, example: str = "") -> str:
        """Create a fallback credential prompt when template is not available."""
        example_text = f"\nExample: {example}" if example else ""
        return f"""Generate a realistic {description.lower()} for {company} in the context of {topic}.

Type: {credential_type}
Pattern: {regex_pattern}
Description: {description}{example_text}

CRITICAL REQUIREMENTS:
- The credential MUST match this exact regex pattern: {regex_pattern}
- Must be appropriate for {company}'s {topic} implementation
- Must be realistic and professional
- Must follow industry standards for {credential_type}
- Any labels or context must be in {language}

FORBIDDEN:
- NO placeholder words: "example", "generated", "test", "demo", "sample"
- NO obvious fake patterns: "123456", "password", "admin"
- NO content in languages other than {language}

Generate the {credential_type} credential now:"""
    
    def create_enhanced_validation_prompt(self, topic: str, credential_types: List[str], language: str, format_type: str, company: Optional[str] = None) -> str:
        """Create an enhanced validation prompt."""
        try:
            company_info = self.get_company_info(company)
            validation_section = self._extract_section(self.prompts.get('validation', ''), 'PRE-GENERATION VALIDATION')
            
            if not validation_section:
                # Fallback validation prompt
                return f"Validate content generation for {topic} in {language} for {company_info['name']}."
            
            return validation_section.format(
                TOPIC=topic,
                LANGUAGE=language,
                FORMAT=format_type,
                CREDENTIAL_TYPES=', '.join(credential_types),
                COMPANY=company_info['name']
            )
        except Exception as e:
            print(f"Error creating validation prompt: {e}")
            return f"Validate content generation for {topic} in {language}."
    
    def create_enhanced_title_prompt(self, topic: str, language: str, format_type: str, company: Optional[str] = None) -> str:
        """Create an enhanced title generation prompt."""
        try:
            company_info = self.get_company_info(company)
            
            # Create a clean, direct title prompt
            return f"""Generate a professional email subject line in {language} for {company_info['name']} about {topic}.

Requirements:
- Language: {language} only
- Length: 3-8 words maximum
- Style: Professional business email subject
- Context: {company_info['name']} and {topic}

Generate only the subject line, no explanations or instructions:"""
                
        except Exception as e:
            print(f"Error creating title prompt: {e}")
            return f"Generate a title for {topic} in {language}."
    
    def create_enhanced_section_prompt(self, topic: str, language: str, format_type: str, section: str, company: Optional[str] = None) -> str:
        """Create an enhanced section content prompt."""
        try:
            company_info = self.get_company_info(company)
            
            # Create a clean, direct prompt without template instructions
            if section == 'subject':
                return f"""Generate a professional email subject line in {language} for {company_info['name']} about {topic}.

Requirements:
- Language: {language} only
- Length: 3-8 words maximum
- Style: Professional business email subject
- Context: {company_info['name']} and {topic}

Generate only the subject line, no explanations or instructions:"""
            
            elif section == 'greeting':
                return f"""Generate a professional email greeting in {language} for {company_info['name']} team about {topic}.

Requirements:
- Language: {language} only
- Style: Professional business greeting
- Context: Internal company communication about {topic}
- Length: 2-3 sentences
- Include: Reference to {topic} and company context
- Avoid: Generic greetings, template language

Generate only the greeting text with specific context about {topic}:"""
            
            elif section == 'body':
                return f"""Generate professional email body content in {language} for {company_info['name']} about {topic}.

Requirements:
- Language: {language} only
- Topic: Specifically about {topic} - include technical details, implementation steps, and business impact
- Company: {company_info['name']} - reference specific company context and industry
- Length: 150-300 words
- Style: Professional, technical, enterprise-appropriate
- Content: Realistic business communication with specific details about {topic}
- Include: Technical specifications, implementation timeline, business benefits, and next steps
- Avoid: Generic template language, vague statements, or placeholder text

Generate only the body content with specific, actionable information about {topic}:"""
            
            elif section == 'closing':
                return f"""Generate a professional email closing in {language} for {company_info['name']} about {topic}.

Requirements:
- Language: {language} only
- Style: Professional business closing
- Context: Internal company communication about {topic}
- Length: 2-3 sentences
- Include: Reference to {topic} and next steps
- Avoid: Generic closings, template language

Generate only the closing text with specific context about {topic}:"""
            
            elif section == 'signature':
                return f"""Generate a professional email signature in {language} for {company_info['name']}.

Requirements:
- Language: {language} only
- Style: Professional business signature
- Company: {company_info['name']}
- Format: Standard email signature format

Generate only the signature, no explanations or instructions:"""
            
            else:
                return f"""Generate professional {section} content in {language} for {company_info['name']} about {topic}.

Requirements:
- Language: {language} only
- Topic: {topic}
- Company: {company_info['name']}
- Style: Professional, technical

Generate only the content, no explanations or instructions:"""
                
        except Exception as e:
            print(f"Error creating section prompt: {e}")
            return f"Generate {section} content for {topic} in {language}."
    
    def _extract_section(self, prompt_text: str, section_name: str) -> str:
        """Extract a specific section from prompt text.
        
        Args:
            prompt_text: Full prompt text
            section_name: Name of the section to extract
            
        Returns:
            Extracted section text
        """
        if not prompt_text:
            return ""
            
        lines = prompt_text.split('\n')
        section_lines = []
        in_section = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check if this line starts a new section
            if line_stripped.startswith('## '):
                # If we were in a section and found a new section, stop
                if in_section:
                    break
                # Check if this is the section we're looking for
                if section_name.upper() in line_stripped.upper():
                    in_section = True
                    continue
            
            # If we're in the target section, collect the line
            if in_section:
                section_lines.append(line)
        
        result = '\n'.join(section_lines).strip()
        
        # If no section found, return empty string
        if not result:
            return ""
            
        return result
    
    def get_system_prompt(self) -> str:
        """Get the main system prompt.
        
        Returns:
            System prompt text
        """
        return self.prompts.get('system', 'You are CredentialForge, an AI system that generates realistic technical documents.')
