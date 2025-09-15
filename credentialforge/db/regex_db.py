"""Regex database management for CredentialForge."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from .exceptions import DatabaseError
from ..utils.exceptions import ValidationError


class RegexDatabase:
    """Manages regex patterns for credential generation."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize regex database.
        
        Args:
            db_path: Path to database file (JSON format)
        """
        self.db_path = db_path
        self.patterns = {}
        
        if db_path and Path(db_path).exists():
            self.load_from_file(db_path)
        else:
            # Initialize with empty structure
            self.patterns = {"credentials": []}
    
    def load_from_file(self, file_path: str) -> None:
        """Load patterns from JSON file.
        
        Args:
            file_path: Path to JSON database file
            
        Raises:
            DatabaseError: If file cannot be loaded or parsed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'credentials' not in data:
                raise DatabaseError("Invalid database format: missing 'credentials' key")
            
            # Validate and load patterns
            for cred in data['credentials']:
                self._validate_credential_entry(cred)
                self.patterns[cred['type']] = {
                    'regex': cred['regex'],
                    'description': cred['description'],
                    'generator': cred.get('generator', 'random_string(32, "A-Za-z0-9")'),
                    'examples': cred.get('examples', []),
                    'realistic_format': cred.get('realistic_format', True)
                }
            
            self.db_path = file_path
            
        except json.JSONDecodeError as e:
            raise DatabaseError(f"Invalid JSON in database file: {e}")
        except FileNotFoundError:
            raise DatabaseError(f"Database file not found: {file_path}")
        except Exception as e:
            raise DatabaseError(f"Failed to load database: {e}")
    
    def save(self, file_path: Optional[str] = None) -> None:
        """Save patterns to JSON file.
        
        Args:
            file_path: Path to save database file (uses db_path if not specified)
            
        Raises:
            DatabaseError: If file cannot be saved
        """
        save_path = file_path or self.db_path
        if not save_path:
            raise DatabaseError("No file path specified for saving")
        
        try:
            # Convert patterns to database format
            credentials = []
            for cred_type, info in self.patterns.items():
                credentials.append({
                    'type': cred_type,
                    'regex': info['regex'],
                    'description': info['description'],
                    'generator': info['generator'],
                    'examples': info.get('examples', []),
                    'realistic_format': info.get('realistic_format', True)
                })
            
            data = {'credentials': credentials}
            
            # Ensure directory exists
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.db_path = save_path
            
        except Exception as e:
            raise DatabaseError(f"Failed to save database: {e}")
    
    def add_credential_type(self, cred_type: str, regex: str, description: str, 
                           generator: Optional[str] = None, examples: Optional[List[str]] = None) -> None:
        """Add new credential type to database.
        
        Args:
            cred_type: Credential type identifier
            regex: Regex pattern for validation
            description: Human-readable description
            generator: Generator function specification
            examples: List of example strings
            
        Raises:
            ValidationError: If credential type is invalid
        """
        # Validate inputs
        if not cred_type or not cred_type.strip():
            raise ValidationError("Credential type cannot be empty")
        
        if not regex or not regex.strip():
            raise ValidationError("Regex pattern cannot be empty")
        
        if not description or not description.strip():
            raise ValidationError("Description cannot be empty")
        
        # Validate regex pattern
        try:
            re.compile(regex)
        except re.error as e:
            raise ValidationError(f"Invalid regex pattern: {e}")
        
        # Check for duplicates
        if cred_type in self.patterns:
            raise ValidationError(f"Credential type already exists: {cred_type}")
        
        # Add to patterns
        self.patterns[cred_type] = {
            'regex': regex,
            'description': description,
            'generator': generator or 'random_string(32, "A-Za-z0-9")',
            'examples': examples or [],
            'realistic_format': True
        }
    
    def remove_credential_type(self, cred_type: str) -> None:
        """Remove credential type from database.
        
        Args:
            cred_type: Credential type to remove
            
        Raises:
            ValidationError: If credential type doesn't exist
        """
        if cred_type not in self.patterns:
            raise ValidationError(f"Credential type not found: {cred_type}")
        
        del self.patterns[cred_type]
    
    def get_pattern(self, cred_type: str) -> str:
        """Get regex pattern for credential type.
        
        Args:
            cred_type: Credential type
            
        Returns:
            Regex pattern string
            
        Raises:
            ValidationError: If credential type not found
        """
        if cred_type not in self.patterns:
            raise ValidationError(f"Credential type not found: {cred_type}")
        
        return self.patterns[cred_type]['regex']
    
    def get_generator(self, cred_type: str) -> str:
        """Get generator function for credential type.
        
        Args:
            cred_type: Credential type
            
        Returns:
            Generator function specification
            
        Raises:
            ValidationError: If credential type not found
        """
        if cred_type not in self.patterns:
            raise ValidationError(f"Credential type not found: {cred_type}")
        
        return self.patterns[cred_type]['generator']
    
    def get_description(self, cred_type: str) -> str:
        """Get description for credential type.
        
        Args:
            cred_type: Credential type
            
        Returns:
            Description string
            
        Raises:
            ValidationError: If credential type not found
        """
        if cred_type not in self.patterns:
            raise ValidationError(f"Credential type not found: {cred_type}")
        
        return self.patterns[cred_type]['description']
    
    def get_examples(self, cred_type: str) -> List[str]:
        """Get examples for credential type.
        
        Args:
            cred_type: Credential type
            
        Returns:
            List of example strings
            
        Raises:
            ValidationError: If credential type not found
        """
        if cred_type not in self.patterns:
            raise ValidationError(f"Credential type not found: {cred_type}")
        
        return self.patterns[cred_type].get('examples', [])
    
    def has_credential_type(self, cred_type: str) -> bool:
        """Check if credential type exists.
        
        Args:
            cred_type: Credential type to check
            
        Returns:
            True if credential type exists
        """
        return cred_type in self.patterns
    
    def list_credential_types(self) -> Dict[str, Dict[str, str]]:
        """List all credential types.
        
        Returns:
            Dictionary mapping credential types to their information
        """
        return self.patterns.copy()
    
    def validate_credential(self, credential: str, cred_type: str) -> bool:
        """Validate credential against its pattern.
        
        Args:
            credential: Credential to validate
            cred_type: Credential type
            
        Returns:
            True if credential matches pattern
            
        Raises:
            ValidationError: If credential type not found
        """
        pattern = self.get_pattern(cred_type)
        return bool(re.match(pattern, credential))
    
    def search_credential_types(self, query: str) -> List[str]:
        """Search credential types by description or type.
        
        Args:
            query: Search query
            
        Returns:
            List of matching credential types
        """
        query = query.lower()
        matches = []
        
        for cred_type, info in self.patterns.items():
            if (query in cred_type.lower() or 
                query in info['description'].lower()):
                matches.append(cred_type)
        
        return matches
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        return {
            'total_types': len(self.patterns),
            'types': list(self.patterns.keys()),
            'file_path': self.db_path,
            'file_exists': bool(self.db_path and Path(self.db_path).exists())
        }
    
    def _validate_credential_entry(self, cred: Dict[str, Any]) -> None:
        """Validate credential entry from database.
        
        Args:
            cred: Credential entry dictionary
            
        Raises:
            DatabaseError: If entry is invalid
        """
        required_fields = ['type', 'regex', 'description']
        
        for field in required_fields:
            if field not in cred:
                raise DatabaseError(f"Missing required field: {field}")
        
        # Validate regex pattern
        try:
            re.compile(cred['regex'])
        except re.error as e:
            raise DatabaseError(f"Invalid regex pattern for {cred['type']}: {e}")
        
        # Validate generator if present
        if 'generator' in cred and cred['generator']:
            # Basic validation - should be a string
            if not isinstance(cred['generator'], str):
                raise DatabaseError(f"Invalid generator for {cred['type']}: must be string")
    
    def export_to_file(self, file_path: str, format: str = 'json') -> None:
        """Export database to file in specified format.
        
        Args:
            file_path: Path to export file
            format: Export format ('json', 'csv', 'yaml')
            
        Raises:
            DatabaseError: If export fails
        """
        try:
            if format.lower() == 'json':
                self.save(file_path)
            elif format.lower() == 'csv':
                self._export_csv(file_path)
            elif format.lower() == 'yaml':
                self._export_yaml(file_path)
            else:
                raise DatabaseError(f"Unsupported export format: {format}")
                
        except Exception as e:
            raise DatabaseError(f"Export failed: {e}")
    
    def _export_csv(self, file_path: str) -> None:
        """Export to CSV format."""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Type', 'Regex', 'Description', 'Generator'])
            
            for cred_type, info in self.patterns.items():
                writer.writerow([
                    cred_type,
                    info['regex'],
                    info['description'],
                    info['generator']
                ])
    
    def _export_yaml(self, file_path: str) -> None:
        """Export to YAML format."""
        import yaml
        
        data = {'credentials': []}
        for cred_type, info in self.patterns.items():
            data['credentials'].append({
                'type': cred_type,
                'regex': info['regex'],
                'description': info['description'],
                'generator': info['generator']
            })
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)
