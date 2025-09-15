# New Agent-Based Architecture Design

## Current Problem
The current architecture has synthesizers hardcoding content instead of letting agents handle content creation. This causes:
- Language issues (hardcoded English text)
- Credential type mismatches (hardcoded "API Key" instead of selected type)
- Poor coordination between topic, regex, and language selection

## New Architecture

### 1. Content Generation Flow
```
User Selection (Topic, Regex, Language) 
    ↓
Orchestrator Agent
    ↓
Content Generation Agents
    ↓
Format-Specific Synthesizers (Structure Only)
    ↓
Final Document
```

### 2. Agent Responsibilities

#### **Content Generation Agents**
- **Topic Agent**: Generate topic-specific content in selected language
- **Credential Agent**: Generate credentials based on selected regex patterns
- **Language Agent**: Ensure all content is in selected language
- **Structure Agent**: Determine document structure based on format

#### **Synthesizers (Format Only)**
- **EML Synthesizer**: Structure content into email format
- **PPT Synthesizer**: Structure content into presentation format
- **PDF Synthesizer**: Structure content into document format
- **Excel Synthesizer**: Structure content into spreadsheet format

### 3. New Agent Interface

```python
class ContentGenerationAgent:
    def generate_content(self, 
                        topic: str,
                        credential_types: List[str],
                        language: str,
                        format_type: str,
                        context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate all content needed for a document.
        
        Returns:
        {
            'title': 'Document Title',
            'sections': [
                {'title': 'Section 1', 'content': '...'},
                {'title': 'Section 2', 'content': '...'}
            ],
            'credentials': [
                {'type': 'password', 'value': '...', 'label': 'Mot de passe'},
                {'type': 'api_key', 'value': '...', 'label': 'Clé API'}
            ],
            'metadata': {...}
        }
        """
```

### 4. New Synthesizer Interface

```python
class BaseSynthesizer:
    def synthesize(self, content_structure: Dict[str, Any]) -> str:
        """
        Structure the content into the specific format.
        
        Args:
            content_structure: Generated content from agents
            
        Returns:
            Path to generated file
        """
```

### 5. Implementation Plan

1. **Create Content Generation Agent**
2. **Refactor Synthesizers to be format-only**
3. **Update Orchestrator to use new flow**
4. **Test with different topics, languages, and formats**

## Benefits

1. **Proper Language Support**: All content generated in selected language
2. **Correct Credential Types**: Credentials match selected regex patterns
3. **Better Coordination**: Topic, regex, and language work together
4. **Maintainable Code**: Clear separation of concerns
5. **Extensible**: Easy to add new formats or languages
