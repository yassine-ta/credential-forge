"""Multi-Model Manager for using different LLM models for different tasks."""

import os
import time
from typing import Dict, Optional, Any
from pathlib import Path
from .llama_interface import LlamaInterface
from .exceptions import LLMError


class MultiModelManager:
    """Manages multiple LLM models for different tasks."""
    
    def __init__(self, models_config: Optional[Dict[str, Dict[str, Any]]] = None):
        """Initialize multi-model manager.
        
        Args:
            models_config: Configuration for different models and their tasks
        """
        self.models: Dict[str, LlamaInterface] = {}
        self.task_to_model: Dict[str, str] = {}
        self.models_config = models_config or self._get_default_config()
        
        # Initialize models based on configuration
        self._initialize_models()
    
    def _get_default_config(self) -> Dict[str, Dict[str, Any]]:
        """Get default model configuration."""
        return {
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
    
    def _initialize_models(self) -> None:
        """Initialize models based on configuration."""
        for model_name, config in self.models_config.items():
            model_path = config['model_path']
            
            # Check if model file exists
            if not Path(model_path).exists():
                print(f"Warning: Model {model_name} not found at {model_path}")
                continue
            
            try:
                # Initialize model with task-specific parameters
                model = LlamaInterface(
                    model_path=model_path,
                    n_ctx=config.get('n_ctx', 4096),
                    temperature=config.get('temperature', 0.2),
                    max_tokens=config.get('max_tokens', 512)
                )
                
                self.models[model_name] = model
                
                # Map tasks to this model
                for task in config.get('tasks', []):
                    self.task_to_model[task] = model_name
                
                print(f"✅ Initialized {model_name} for tasks: {config.get('tasks', [])}")
                
            except Exception as e:
                print(f"❌ Failed to initialize {model_name}: {e}")
    
    def get_model_for_task(self, task: str) -> Optional[LlamaInterface]:
        """Get the appropriate model for a specific task.
        
        Args:
            task: Task name (e.g., 'credential_generation', 'content_generation')
            
        Returns:
            LlamaInterface instance or None if no model available
        """
        model_name = self.task_to_model.get(task)
        if model_name and model_name in self.models:
            return self.models[model_name]
        
        # Fallback to first available model
        if self.models:
            first_model = list(self.models.values())[0]
            print(f"Warning: No specific model for task '{task}', using fallback model")
            return first_model
        
        return None
    
    def generate_for_task(self, task: str, prompt: str, **kwargs) -> str:
        """Generate text for a specific task using the appropriate model.
        
        Args:
            task: Task name
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        model = self.get_model_for_task(task)
        if not model:
            raise LLMError(f"No model available for task: {task}")
        
        # Use task-specific parameters if available
        task_config = None
        for model_name, config in self.models_config.items():
            if task in config.get('tasks', []):
                task_config = config
                break
        
        # Override default parameters with task-specific ones
        if task_config:
            kwargs.setdefault('temperature', task_config.get('temperature', 0.2))
            kwargs.setdefault('max_tokens', task_config.get('max_tokens', 512))
        
        return model.generate(prompt, **kwargs)
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available models."""
        available = {}
        for model_name, config in self.models_config.items():
            if model_name in self.models:
                available[model_name] = {
                    'description': config.get('description', ''),
                    'tasks': config.get('tasks', []),
                    'status': 'loaded'
                }
            else:
                available[model_name] = {
                    'description': config.get('description', ''),
                    'tasks': config.get('tasks', []),
                    'status': 'not_loaded'
                }
        return available
    
    def get_task_mapping(self) -> Dict[str, str]:
        """Get mapping of tasks to models."""
        return self.task_to_model.copy()
    
    def add_model(self, name: str, model_path: str, tasks: list, **config) -> bool:
        """Add a new model configuration.
        
        Args:
            name: Model name
            model_path: Path to model file
            tasks: List of tasks this model should handle
            **config: Additional model configuration
            
        Returns:
            True if model was added successfully
        """
        if not Path(model_path).exists():
            print(f"Error: Model file not found at {model_path}")
            return False
        
        try:
            model = LlamaInterface(
                model_path=model_path,
                n_ctx=config.get('n_ctx', 4096),
                temperature=config.get('temperature', 0.2),
                max_tokens=config.get('max_tokens', 512)
            )
            
            self.models[name] = model
            
            # Update task mapping
            for task in tasks:
                self.task_to_model[task] = name
            
            # Update configuration
            self.models_config[name] = {
                'model_path': model_path,
                'tasks': tasks,
                'description': config.get('description', f'Custom model: {name}'),
                **config
            }
            
            print(f"✅ Added model {name} for tasks: {tasks}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add model {name}: {e}")
            return False
    
    def unload_model(self, name: str) -> bool:
        """Unload a specific model to free memory.
        
        Args:
            name: Model name to unload
            
        Returns:
            True if model was unloaded successfully
        """
        if name in self.models:
            try:
                # Remove from task mapping
                tasks_to_remove = []
                for task, model_name in self.task_to_model.items():
                    if model_name == name:
                        tasks_to_remove.append(task)
                
                for task in tasks_to_remove:
                    del self.task_to_model[task]
                
                # Unload model
                del self.models[name]
                print(f"✅ Unloaded model {name}")
                return True
                
            except Exception as e:
                print(f"❌ Failed to unload model {name}: {e}")
                return False
        
        return False
    
    def get_memory_usage(self) -> Dict[str, Dict[str, Any]]:
        """Get memory usage information for loaded models."""
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'total_memory_mb': memory_info.rss / 1024 / 1024,
            'loaded_models': len(self.models),
            'available_models': len(self.models_config)
        }
