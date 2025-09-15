#!/usr/bin/env python3
"""Demonstration of CredentialForge Agentic AI functionality."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.agents.orchestrator import OrchestratorAgent
from credentialforge.agents.credential_agent import CredentialAgent
from credentialforge.agents.topic_agent import TopicAgent
from credentialforge.agents.embedding_agent import EmbeddingAgent
from credentialforge.db.regex_db import RegexDatabase
from credentialforge.generators.credential_generator import CredentialGenerator
from credentialforge.generators.topic_generator import TopicGenerator


def demonstrate_agentic_ai():
    """Demonstrate the agentic AI workflow."""
    print("🤖 CredentialForge Agentic AI Demonstration")
    print("=" * 60)
    
    # Load regex database
    regex_db = RegexDatabase("./data/regex_db.json")
    print(f"📋 Loaded {len(regex_db.list_credential_types())} credential types from database")
    
    # Initialize agents
    print("\n🧠 Initializing AI Agents...")
    credential_agent = CredentialAgent()
    topic_agent = TopicAgent()
    embedding_agent = EmbeddingAgent()
    
    # Initialize generators
    credential_generator = CredentialGenerator(regex_db)
    topic_generator = TopicGenerator()
    
    # Example 1: API Documentation in Excel format
    print("\n📊 Example 1: API Documentation in Excel format")
    print("-" * 50)
    
    topic = "API documentation"
    file_format = "xlsx"
    credential_types = ["aws_access_key", "api_key"]
    
    print(f"Topic: {topic}")
    print(f"Format: {file_format}")
    print(f"Credential Types: {credential_types}")
    
    # Generate topic content
    topic_content = topic_generator.generate_topic_content(topic, file_format)
    print(f"✅ Generated topic content ({len(topic_content)} characters)")
    
    # Generate credentials
    credentials = []
    for cred_type in credential_types:
        credential = credential_generator.generate_credential(cred_type)
        credentials.append(credential)
        print(f"✅ Generated {cred_type}: {credential[:20]}...")
    
    # Determine embedding strategy
    strategy = embedding_agent.determine_embedding_strategy(file_format, credential_types, len(topic_content))
    print(f"✅ Embedding strategy: {strategy}")
    
    # Example 2: System Architecture in PowerPoint format
    print("\n📈 Example 2: System Architecture in PowerPoint format")
    print("-" * 50)
    
    topic = "system architecture"
    file_format = "pptx"
    credential_types = ["jwt_token", "db_connection"]
    
    print(f"Topic: {topic}")
    print(f"Format: {file_format}")
    print(f"Credential Types: {credential_types}")
    
    # Generate topic content
    topic_content = topic_generator.generate_topic_content(topic, file_format)
    print(f"✅ Generated topic content ({len(topic_content)} characters)")
    
    # Generate credentials
    credentials = []
    for cred_type in credential_types:
        credential = credential_generator.generate_credential(cred_type)
        credentials.append(credential)
        print(f"✅ Generated {cred_type}: {credential[:30]}...")
    
    # Determine embedding strategy
    strategy = embedding_agent.determine_embedding_strategy(file_format, credential_types, len(topic_content))
    print(f"✅ Embedding strategy: {strategy}")
    
    # Example 3: Network Diagram in Visio format
    print("\n🔗 Example 3: Network Diagram in Visio format")
    print("-" * 50)
    
    topic = "network topology"
    file_format = "vsdx"
    credential_types = ["mongodb_uri", "stripe_key"]
    
    print(f"Topic: {topic}")
    print(f"Format: {file_format}")
    print(f"Credential Types: {credential_types}")
    
    # Generate topic content
    topic_content = topic_generator.generate_topic_content(topic, file_format)
    print(f"✅ Generated topic content ({len(topic_content)} characters)")
    
    # Generate credentials
    credentials = []
    for cred_type in credential_types:
        credential = credential_generator.generate_credential(cred_type)
        credentials.append(credential)
        print(f"✅ Generated {cred_type}: {credential[:30]}...")
    
    # Determine embedding strategy
    strategy = embedding_agent.determine_embedding_strategy(file_format, credential_types, len(topic_content))
    print(f"✅ Embedding strategy: {strategy}")
    
    # Show agent statistics
    print("\n📊 Agent Statistics")
    print("-" * 30)
    print(f"Credential Agent: {credential_agent.get_generation_stats()}")
    print(f"Topic Agent: {topic_agent.get_generation_stats()}")
    print(f"Embedding Agent: {embedding_agent.get_embedding_stats()}")
    
    print("\n🎉 Agentic AI demonstration complete!")
    print("\nThe system successfully:")
    print("• Analyzed topics and file formats")
    print("• Generated appropriate content for each format")
    print("• Created realistic credentials using regex patterns")
    print("• Determined optimal embedding strategies")
    print("• Coordinated multiple AI agents for complex generation tasks")


def demonstrate_orchestrator():
    """Demonstrate the orchestrator agent."""
    print("\n🎭 Orchestrator Agent Demonstration")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()
    
    # Define generation criteria
    config = {
        'output_dir': './agentic_demo_output',
        'num_files': 3,
        'formats': ['eml', 'xlsx', 'pptx'],
        'credential_types': ['aws_access_key', 'jwt_token', 'api_key'],
        'topics': ['API documentation', 'system architecture', 'security implementation'],
        'embed_strategy': 'random',
        'batch_size': 1,
        'regex_db_path': './data/regex_db.json'
    }
    
    print("🎯 Generation Criteria:")
    print(f"  • Topics: {config['topics']}")
    print(f"  • Formats: {config['formats']}")
    print(f"  • Credential Types: {config['credential_types']}")
    print(f"  • Output Directory: {config['output_dir']}")
    
    # Orchestrate generation
    print("\n🚀 Orchestrating generation...")
    results = orchestrator.orchestrate_generation(config)
    
    print(f"\n✅ Generation Results:")
    print(f"  • Files Generated: {len(results['files'])}")
    print(f"  • Total Credentials: {results['metadata']['total_credentials']}")
    print(f"  • Generation Time: {results['metadata']['generation_time']:.2f}s")
    print(f"  • Files by Format: {results['metadata']['files_by_format']}")
    print(f"  • Credentials by Type: {results['metadata']['credentials_by_type']}")
    
    if results['errors']:
        print(f"  • Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"    - {error}")
    
    print(f"\n📁 Generated Files:")
    for file_info in results['files']:
        if isinstance(file_info, dict):
            file_path = file_info.get('path', str(file_info))
        else:
            file_path = file_info
        print(f"  • {Path(file_path).name}")


if __name__ == "__main__":
    try:
        demonstrate_agentic_ai()
        demonstrate_orchestrator()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
