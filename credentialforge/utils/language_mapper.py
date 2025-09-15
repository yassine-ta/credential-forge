"""Language mapping utilities for CredentialForge."""

import json
from pathlib import Path
from typing import Dict, Optional, List
from ..utils.exceptions import ValidationError


class LanguageMapper:
    """Maps companies to their primary languages for localized content generation."""
    
    def __init__(self, mapping_file: Optional[str] = None):
        """Initialize language mapper.
        
        Args:
            mapping_file: Path to company language mapping JSON file
        """
        if mapping_file is None:
            # Default to the mapping file in data directory
            project_root = Path(__file__).parent.parent.parent
            mapping_file = project_root / "data" / "company_language_mapping.json"
        
        self.mapping_file = Path(mapping_file)
        self.mapping_data = self._load_mapping_data()
    
    def _load_mapping_data(self) -> Dict:
        """Load company language mapping data from JSON file.
        
        Returns:
            Dictionary containing mapping data
            
        Raises:
            ValidationError: If mapping file cannot be loaded
        """
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValidationError(f"Language mapping file not found: {self.mapping_file}")
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in mapping file: {e}")
        except Exception as e:
            raise ValidationError(f"Error loading mapping file: {e}")
    
    def get_company_language(self, company_name: str) -> str:
        """Get the primary language for a company.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Language code (e.g., 'en', 'fr', 'es')
        """
        # Check in regular companies first
        companies = self.mapping_data.get('company_language_mapping', {}).get('companies', {})
        if company_name in companies:
            return companies[company_name]['language']
        
        # Check in AXA companies
        axa_companies = self.mapping_data.get('company_language_mapping', {}).get('axa_companies', {})
        if company_name in axa_companies:
            return axa_companies[company_name]['language']
        
        # Default to English if company not found
        return 'en'
    
    def get_company_info(self, company_name: str) -> Dict[str, str]:
        """Get complete company information including language, country, and region.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Dictionary with language, country, and region information
        """
        # Check in regular companies first
        companies = self.mapping_data.get('company_language_mapping', {}).get('companies', {})
        if company_name in companies:
            return companies[company_name]
        
        # Check in AXA companies
        axa_companies = self.mapping_data.get('company_language_mapping', {}).get('axa_companies', {})
        if company_name in axa_companies:
            return axa_companies[company_name]
        
        # Default information if company not found
        return {
            'language': 'en',
            'country': 'United States',
            'region': 'North America'
        }
    
    def get_companies_by_language(self, language_code: str) -> List[str]:
        """Get all companies that use a specific language.
        
        Args:
            language_code: Language code (e.g., 'en', 'fr', 'es')
            
        Returns:
            List of company names using the specified language
        """
        companies = []
        
        # Check regular companies
        regular_companies = self.mapping_data.get('company_language_mapping', {}).get('companies', {})
        for company, info in regular_companies.items():
            if info.get('language') == language_code:
                companies.append(company)
        
        # Check AXA companies
        axa_companies = self.mapping_data.get('company_language_mapping', {}).get('axa_companies', {})
        for company, info in axa_companies.items():
            if info.get('language') == language_code:
                companies.append(company)
        
        return companies
    
    def get_companies_by_region(self, region: str) -> List[str]:
        """Get all companies in a specific region.
        
        Args:
            region: Region name (e.g., 'Europe', 'North America')
            
        Returns:
            List of company names in the specified region
        """
        companies = []
        
        # Check regular companies
        regular_companies = self.mapping_data.get('company_language_mapping', {}).get('companies', {})
        for company, info in regular_companies.items():
            if info.get('region') == region:
                companies.append(company)
        
        # Check AXA companies
        axa_companies = self.mapping_data.get('company_language_mapping', {}).get('axa_companies', {})
        for company, info in axa_companies.items():
            if info.get('region') == region:
                companies.append(company)
        
        return companies
    
    def get_supported_languages(self) -> List[str]:
        """Get list of all supported language codes.
        
        Returns:
            List of supported language codes
        """
        language_codes = self.mapping_data.get('company_language_mapping', {}).get('language_codes', {})
        return list(language_codes.keys())
    
    def get_language_name(self, language_code: str) -> str:
        """Get the full name of a language from its code.
        
        Args:
            language_code: Language code (e.g., 'en', 'fr')
            
        Returns:
            Full language name (e.g., 'English', 'French')
        """
        language_codes = self.mapping_data.get('company_language_mapping', {}).get('language_codes', {})
        return language_codes.get(language_code, language_code)
    
    def get_regions(self) -> List[str]:
        """Get list of all supported regions.
        
        Returns:
            List of supported regions
        """
        regions = self.mapping_data.get('company_language_mapping', {}).get('regions', {})
        return list(regions.keys())
    
    def get_languages_by_region(self, region: str) -> List[str]:
        """Get languages used in a specific region.
        
        Args:
            region: Region name
            
        Returns:
            List of language codes used in the region
        """
        regions = self.mapping_data.get('company_language_mapping', {}).get('regions', {})
        return regions.get(region, [])
    
    def get_all_companies(self) -> List[str]:
        """Get list of all companies in the mapping.
        
        Returns:
            List of all company names
        """
        companies = []
        
        # Add regular companies
        regular_companies = self.mapping_data.get('company_language_mapping', {}).get('companies', {})
        companies.extend(regular_companies.keys())
        
        # Add AXA companies
        axa_companies = self.mapping_data.get('company_language_mapping', {}).get('axa_companies', {})
        companies.extend(axa_companies.keys())
        
        return companies
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the language mapping.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_companies': 0,
            'languages_count': 0,
            'regions_count': 0
        }
        
        # Count companies
        regular_companies = self.mapping_data.get('company_language_mapping', {}).get('companies', {})
        axa_companies = self.mapping_data.get('company_language_mapping', {}).get('axa_companies', {})
        stats['total_companies'] = len(regular_companies) + len(axa_companies)
        
        # Count languages
        language_codes = self.mapping_data.get('company_language_mapping', {}).get('language_codes', {})
        stats['languages_count'] = len(language_codes)
        
        # Count regions
        regions = self.mapping_data.get('company_language_mapping', {}).get('regions', {})
        stats['regions_count'] = len(regions)
        
        return stats
    
    def validate_mapping(self) -> bool:
        """Validate the language mapping data.
        
        Returns:
            True if mapping is valid, False otherwise
        """
        try:
            # Check required structure
            mapping = self.mapping_data.get('company_language_mapping', {})
            if not mapping:
                return False
            
            # Check required sections
            required_sections = ['companies', 'axa_companies', 'language_codes', 'regions']
            for section in required_sections:
                if section not in mapping:
                    return False
            
            # Validate company data structure
            for company_type in ['companies', 'axa_companies']:
                companies = mapping.get(company_type, {})
                for company, info in companies.items():
                    if not isinstance(info, dict):
                        return False
                    required_fields = ['language', 'country', 'region']
                    for field in required_fields:
                        if field not in info:
                            return False
            
            return True
            
        except Exception:
            return False
