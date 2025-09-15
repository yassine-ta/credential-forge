#!/usr/bin/env python3
"""Demonstration script showing how to use multiple LLM models for different tasks."""

import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from credentialforge.llm.multi_model_manager import MultiModelManager
from credentialforge.generators.credential_generator import CredentialGenerator
from credentialforge.agents.content_generation_agent import ContentGenerationAgent
from credentialforge.db.regex_db import RegexDatabase
from credentialforge.utils.prompt_system import EnhancedPromptSystem


def demo_multi_model_setup():
    """Demonstrate multi-model setup and configuration."""
    print("🚀 Multi-Model Configuration Demo")
    print("=" * 50)
    
    # Check available models
    models_dir = Path('./models')
    available_models = []
    
    if models_dir.exists():
        for model_file in models_dir.glob('*.gguf'):
            available_models.append(model_file.name)
    
    print(f"\n📁 Available Models: {available_models}")
    
    # Create custom model configuration
    custom_config = {
        'tinyllama': {
            'model_path': './models/tinyllama.gguf',
            'tasks': ['credential_generation', 'topic_generation'],
            'description': 'Fast, lightweight model for simple tasks',
            'n_ctx': 2048,
            'temperature': 0.1,
            'max_tokens': 50
        },
        'qwen2': {
            'model_path': './models/qwen2-0.5b.gguf',
            'tasks': ['content_generation', 'email_content'],
            'description': 'Balanced model for content generation',
            'n_ctx': 4096,
            'temperature': 0.3,
            'max_tokens': 200
        },
        'phi3': {
            'model_path': './models/phi3-mini.gguf',
            'tasks': ['high_quality_content', 'complex_topics'],
            'description': 'High-quality model for complex tasks',
            'n_ctx': 4096,
            'temperature': 0.2,
            'max_tokens': 300
        }
    }
    
    # Initialize multi-model manager
    print(f"\n🔧 Initializing Multi-Model Manager...")
    try:
        manager = MultiModelManager(custom_config)
        
        # Show available models and their tasks
        available = manager.get_available_models()
        print(f"\n📊 Model Status:")
        for model_name, info in available.items():
            status_icon = "✅" if info['status'] == 'loaded' else "❌"
            print(f"   {status_icon} {model_name}: {info['description']}")
            print(f"      Tasks: {', '.join(info['tasks'])}")
        
        # Show task mapping
        task_mapping = manager.get_task_mapping()
        print(f"\n🎯 Task-to-Model Mapping:")
        for task, model in task_mapping.items():
            print(f"   {task} → {model}")
        
        return manager
        
    except Exception as e:
        print(f"❌ Failed to initialize multi-model manager: {e}")
        print("   Using single model fallback...")
        return None


def demo_credential_generation_with_models(manager):
    """Demonstrate credential generation using different models."""
    print(f"\n🔑 Credential Generation with Multi-Model")
    print("-" * 40)
    
    # Initialize components
    regex_db = RegexDatabase('./data/regex_db.json')
    prompt_system = EnhancedPromptSystem()
    
    # Test credential types
    credential_types = ['api_key', 'aws_access_key', 'jwt_token']
    
    if manager:
        # Use multi-model manager
        generator = CredentialGenerator(
            regex_db=regex_db,
            multi_model_manager=manager,
            prompt_system=prompt_system,
            use_llm_by_default=True  # Enable LLM mode for demo
        )
        
        print(f"   Using multi-model manager for credential generation")
        
        for cred_type in credential_types:
            start_time = time.time()
            credential = generator.generate_credential(cred_type)
            generation_time = time.time() - start_time
            
            print(f"   {cred_type}: {credential[:30]}...")
            print(f"      Generated in {generation_time:.3f} seconds")
    
    else:
        # Fallback to fast mode
        generator = CredentialGenerator(
            regex_db=regex_db,
            prompt_system=prompt_system,
            use_llm_by_default=False  # Use fast fallback
        )
        
        print(f"   Using fast fallback mode (no models available)")
        
        for cred_type in credential_types:
            start_time = time.time()
            credential = generator.generate_credential(cred_type)
            generation_time = time.time() - start_time
            
            print(f"   {cred_type}: {credential[:30]}...")
            print(f"      Generated in {generation_time:.3f} seconds")


def demo_content_generation_with_models(manager):
    """Demonstrate content generation using different models."""
    print(f"\n📝 Content Generation with Multi-Model")
    print("-" * 40)
    
    if not manager:
        print("   No models available, skipping content generation demo")
        return
    
    # Initialize content generation agent
    regex_db = RegexDatabase('./data/regex_db.json')
    
    content_agent = ContentGenerationAgent(
        multi_model_manager=manager,
        regex_db=regex_db,
        use_llm_for_credentials=True
    )
    
    # Test different content generation tasks
    test_tasks = [
        ('topic_generation', 'Generate a technical topic about cloud security'),
        ('content_generation', 'Write a brief introduction about API security'),
        ('high_quality_content', 'Create a detailed explanation of JWT tokens')
    ]
    
    for task, prompt in test_tasks:
        try:
            start_time = time.time()
            
            # Use the appropriate model for each task
            response = manager.generate_for_task(task, prompt)
            
            generation_time = time.time() - start_time
            
            print(f"   Task: {task}")
            print(f"   Model: {manager.get_task_mapping().get(task, 'unknown')}")
            print(f"   Response: {response[:100]}...")
            print(f"   Time: {generation_time:.3f} seconds")
            print()
            
        except Exception as e:
            print(f"   Task: {task} - Failed: {e}")


def demo_memory_usage(manager):
    """Demonstrate memory usage monitoring."""
    print(f"\n💾 Memory Usage Monitoring")
    print("-" * 40)
    
    if manager:
        memory_info = manager.get_memory_usage()
        print(f"   Total Memory: {memory_info['total_memory_mb']:.1f} MB")
        print(f"   Loaded Models: {memory_info['loaded_models']}")
        print(f"   Available Models: {memory_info['available_models']}")
        
        # Show how to unload models to free memory
        print(f"\n   💡 Tip: Use manager.unload_model('model_name') to free memory")
    else:
        print("   No models loaded")


def demo_custom_model_addition(manager):
    """Demonstrate adding custom models."""
    print(f"\n➕ Custom Model Addition")
    print("-" * 40)
    
    if not manager:
        print("   No manager available, skipping custom model demo")
        return
    
    # Example of adding a custom model (if you have one)
    custom_model_path = './models/custom-model.gguf'
    
    if Path(custom_model_path).exists():
        success = manager.add_model(
            name='custom_model',
            model_path=custom_model_path,
            tasks=['custom_task'],
            description='Custom model for specific tasks',
            n_ctx=2048,
            temperature=0.2
        )
        
        if success:
            print(f"   ✅ Added custom model successfully")
        else:
            print(f"   ❌ Failed to add custom model")
    else:
        print(f"   ℹ️  Custom model not found at {custom_model_path}")
        print(f"   💡 To add a custom model, place it in ./models/ and update the path")


def main():
    """Main demo function."""
    print("🎯 Multi-Model Usage Demonstration")
    print("=" * 60)
    
    # Setup multi-model manager
    manager = demo_multi_model_setup()
    
    # Demo different use cases
    demo_credential_generation_with_models(manager)
    demo_content_generation_with_models(manager)
    demo_memory_usage(manager)
    demo_custom_model_addition(manager)
    
    # Summary
    print(f"\n✅ Multi-Model Demo Complete!")
    print(f"\n📋 Summary:")
    print(f"   • Use TinyLlama for fast credential generation")
    print(f"   • Use Qwen2 for balanced content generation")
    print(f"   • Use Phi-3 for high-quality complex content")
    print(f"   • Fast Fallback mode for maximum performance")
    print(f"   • Multi-model manager handles task routing automatically")
    
    print(f"\n💡 Best Practices:")
    print(f"   • Load only the models you need")
    print(f"   • Use fast fallback for bulk generation")
    print(f"   • Use specific models for quality-critical tasks")
    print(f"   • Monitor memory usage with large models")


if __name__ == "__main__":
    main()
