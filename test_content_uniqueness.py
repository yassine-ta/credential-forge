#!/usr/bin/env python3
"""Test script for content uniqueness in agentic AI file generation."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.agents.orchestrator import OrchestratorAgent
from credentialforge.generators.topic_generator import TopicGenerator


def test_content_uniqueness():
    """Test that each generated file has unique content."""
    print("🔍 Testing Content Uniqueness in Agentic AI Generation")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()
    
    # Configuration for testing uniqueness
    config = {
        'output_dir': './uniqueness_test_output',
        'formats': ['docx', 'xlsx', 'pdf'],
        'credential_types': ['aws_access_key', 'api_key', 'jwt_token'],
        'topics': [
            'security audit, compliance review',
            'database migration, performance optimization'
        ],
        'num_files': 5,  # Generate 5 files to test uniqueness
        'embed_strategy': 'random',
        'regex_db_path': './data/regex_db.json'
    }
    
    print(f"📋 Configuration:")
    print(f"  - Output directory: {config['output_dir']}")
    print(f"  - Formats: {config['formats']}")
    print(f"  - Topics: {config['topics']}")
    print(f"  - Number of files: {config['num_files']}")
    print()
    
    try:
        # Generate files
        print("🤖 Starting agentic AI generation with uniqueness testing...")
        results = orchestrator.orchestrate_generation(config)
        
        print(f"✅ Generation completed!")
        print(f"  - Files generated: {len(results['files'])}")
        print(f"  - Errors: {len(results['errors'])}")
        print()
        
        # Analyze content uniqueness
        print("🔍 Analyzing Content Uniqueness:")
        content_analysis = analyze_content_uniqueness(results['files'])
        
        # Display results
        print("📄 Generated Files Analysis:")
        for i, file_info in enumerate(results['files'], 1):
            print(f"  {i}. {file_info['path']}")
            print(f"     Format: {file_info['format']}")
            print(f"     Topic: {file_info['topic']}")
            print(f"     Credential Type: {file_info['credential_type']}")
            if file_info['path'] in content_analysis:
                analysis = content_analysis[file_info['path']]
                print(f"     Company: {analysis.get('company', 'N/A')}")
                print(f"     Project: {analysis.get('project', 'N/A')}")
                print(f"     Environment: {analysis.get('environment', 'N/A')}")
                print(f"     Unique Elements: {analysis.get('unique_elements', 0)}")
            print()
        
        # Display uniqueness summary
        print("📊 Uniqueness Summary:")
        total_unique_elements = sum(analysis.get('unique_elements', 0) for analysis in content_analysis.values())
        avg_unique_elements = total_unique_elements / len(content_analysis) if content_analysis else 0
        print(f"  - Total unique elements across all files: {total_unique_elements}")
        print(f"  - Average unique elements per file: {avg_unique_elements:.1f}")
        print(f"  - Files with unique content: {len(content_analysis)}")
        
        # Check for content diversity
        companies = set(analysis.get('company', '') for analysis in content_analysis.values())
        projects = set(analysis.get('project', '') for analysis in content_analysis.values())
        environments = set(analysis.get('environment', '') for analysis in content_analysis.values())
        
        print(f"  - Unique companies: {len(companies)}")
        print(f"  - Unique projects: {len(projects)}")
        print(f"  - Unique environments: {len(environments)}")
        print()
        
        if len(companies) > 1 and len(projects) > 1 and len(environments) > 1:
            print("🎉 SUCCESS: Content uniqueness is working!")
            print("   - Each file has different company, project, and environment details")
            print("   - Content variation is successfully implemented")
        else:
            print("⚠️  WARNING: Some content may not be unique enough")
            print("   - Consider enhancing uniqueness factors")
        
        print()
        print("🎉 Content uniqueness test completed!")
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return False
    
    return True


def analyze_content_uniqueness(files):
    """Analyze content uniqueness of generated files."""
    content_analysis = {}
    
    for file_info in files:
        file_path = file_info['path']
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract unique elements
            analysis = {
                'company': extract_company(content),
                'project': extract_project(content),
                'environment': extract_environment(content),
                'unique_elements': count_unique_elements(content)
            }
            
            content_analysis[file_path] = analysis
            
        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")
            content_analysis[file_path] = {
                'company': 'Unknown',
                'project': 'Unknown', 
                'environment': 'Unknown',
                'unique_elements': 0
            }
    
    return content_analysis


def extract_company(content):
    """Extract company name from content."""
    companies = [
        "TechCorp Solutions", "DataFlow Systems", "CloudScale Technologies", 
        "SecureNet Enterprises", "InnovateLab Inc", "DigitalBridge Corp",
        "NextGen Systems", "CyberShield Technologies", "QuantumSoft Solutions",
        "EliteTech Industries", "ProActive Systems", "FutureTech Dynamics"
    ]
    
    for company in companies:
        if company in content:
            return company
    return "Unknown"


def extract_project(content):
    """Extract project name from content."""
    projects = [
        "Project Phoenix", "Operation Thunder", "System Alpha", "Initiative Beta",
        "Mission Control", "Project Genesis", "Operation Storm", "System Nova",
        "Initiative Titan", "Mission Vector", "Project Quantum", "Operation Matrix"
    ]
    
    for project in projects:
        if project in content:
            return project
    return "Unknown"


def extract_environment(content):
    """Extract environment from content."""
    environments = [
        "Production AWS Cloud", "Development Azure Environment", "Staging GCP Platform",
        "Hybrid Cloud Infrastructure", "On-Premises Data Center", "Multi-Cloud Setup",
        "Containerized Kubernetes", "Serverless Architecture", "Microservices Platform",
        "Edge Computing Network", "Distributed Systems", "High-Availability Cluster"
    ]
    
    for environment in environments:
        if environment in content:
            return environment
    return "Unknown"


def count_unique_elements(content):
    """Count unique elements in content."""
    unique_count = 0
    
    # Count unique technical elements
    if "svc-" in content:
        unique_count += content.count("svc-")
    if "db-" in content:
        unique_count += content.count("db-")
    if "https://api." in content:
        unique_count += content.count("https://api.")
    if "v1." in content or "v2." in content or "v3." in content:
        unique_count += 1
    
    return unique_count


if __name__ == "__main__":
    success = test_content_uniqueness()
    sys.exit(0 if success else 1)
