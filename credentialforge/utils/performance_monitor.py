"""Performance monitoring and memory management utilities for CredentialForge."""

import time
import psutil
import threading
import gc
from typing import Dict, List, Optional, Any, Callable
from contextlib import contextmanager
from dataclasses import dataclass
from collections import deque


@dataclass
class PerformanceMetrics:
    """Performance metrics data class."""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    memory_before: float
    memory_after: float
    memory_delta: float
    cpu_percent: float
    success: bool
    error_message: Optional[str] = None


class PerformanceMonitor:
    """Performance monitoring and memory management utility."""
    
    def __init__(self, max_history: int = 1000):
        """Initialize performance monitor.
        
        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self._lock = threading.Lock()
        
        # System monitoring
        self.system_stats = {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'disk_total_gb': psutil.disk_usage('/').total / (1024**3) if hasattr(psutil, 'disk_usage') else 0
        }
    
    @contextmanager
    def monitor_operation(self, operation_name: str):
        """Context manager for monitoring operations.
        
        Args:
            operation_name: Name of the operation being monitored
            
        Yields:
            PerformanceMetrics object for the operation
        """
        start_time = time.time()
        memory_before = self._get_memory_usage()
        cpu_before = psutil.cpu_percent()
        
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=start_time,
            end_time=0.0,
            duration=0.0,
            memory_before=memory_before,
            memory_after=0.0,
            memory_delta=0.0,
            cpu_percent=0.0,
            success=False
        )
        
        try:
            yield metrics
            metrics.success = True
        except Exception as e:
            metrics.error_message = str(e)
            raise
        finally:
            end_time = time.time()
            memory_after = self._get_memory_usage()
            cpu_after = psutil.cpu_percent()
            
            metrics.end_time = end_time
            metrics.duration = end_time - start_time
            metrics.memory_after = memory_after
            metrics.memory_delta = memory_after - memory_before
            metrics.cpu_percent = (cpu_before + cpu_after) / 2
            
            with self._lock:
                self.metrics_history.append(metrics)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics."""
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            **self.system_stats,
            'memory_used_gb': memory.used / (1024**3),
            'memory_available_gb': memory.available / (1024**3),
            'memory_percent': memory.percent,
            'cpu_percent': cpu_percent,
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'cpu_count_physical': psutil.cpu_count(logical=False)
        }
    
    def get_performance_summary(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance summary for operations.
        
        Args:
            operation_name: Optional operation name to filter by
            
        Returns:
            Dictionary with performance summary
        """
        with self._lock:
            if operation_name:
                metrics = [m for m in self.metrics_history if m.operation_name == operation_name]
            else:
                metrics = list(self.metrics_history)
        
        if not metrics:
            return {'message': 'No metrics available'}
        
        successful_metrics = [m for m in metrics if m.success]
        failed_metrics = [m for m in metrics if not m.success]
        
        if successful_metrics:
            durations = [m.duration for m in successful_metrics]
            memory_deltas = [m.memory_delta for m in successful_metrics]
            cpu_percents = [m.cpu_percent for m in successful_metrics]
            
            summary = {
                'total_operations': len(metrics),
                'successful_operations': len(successful_metrics),
                'failed_operations': len(failed_metrics),
                'success_rate': len(successful_metrics) / len(metrics) * 100,
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'avg_memory_delta': sum(memory_deltas) / len(memory_deltas),
                'avg_cpu_percent': sum(cpu_percents) / len(cpu_percents),
                'total_duration': sum(durations)
            }
        else:
            summary = {
                'total_operations': len(metrics),
                'successful_operations': 0,
                'failed_operations': len(failed_metrics),
                'success_rate': 0.0,
                'message': 'No successful operations to analyze'
            }
        
        if failed_metrics:
            error_messages = [m.error_message for m in failed_metrics if m.error_message]
            summary['common_errors'] = list(set(error_messages))
        
        return summary
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get detailed statistics for a specific operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Dictionary with operation statistics
        """
        return self.get_performance_summary(operation_name)
    
    def cleanup_memory(self) -> Dict[str, Any]:
        """Perform memory cleanup and return cleanup statistics.
        
        Returns:
            Dictionary with cleanup statistics
        """
        memory_before = self._get_memory_usage()
        
        # Force garbage collection
        collected = gc.collect()
        
        memory_after = self._get_memory_usage()
        memory_freed = memory_before - memory_after
        
        return {
            'memory_before_mb': memory_before,
            'memory_after_mb': memory_after,
            'memory_freed_mb': memory_freed,
            'objects_collected': collected,
            'cleanup_timestamp': time.time()
        }
    
    def get_memory_usage_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get memory usage history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of memory usage snapshots
        """
        with self._lock:
            recent_metrics = list(self.metrics_history)[-limit:]
        
        return [
            {
                'timestamp': m.start_time,
                'operation': m.operation_name,
                'memory_mb': m.memory_after,
                'duration': m.duration,
                'success': m.success
            }
            for m in recent_metrics
        ]
    
    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
        with self._lock:
            self.metrics_history.clear()
    
    def export_metrics(self, filepath: str) -> None:
        """Export metrics to a file.
        
        Args:
            filepath: Path to export file
        """
        import json
        
        with self._lock:
            metrics_data = [
                {
                    'operation_name': m.operation_name,
                    'start_time': m.start_time,
                    'end_time': m.end_time,
                    'duration': m.duration,
                    'memory_before': m.memory_before,
                    'memory_after': m.memory_after,
                    'memory_delta': m.memory_delta,
                    'cpu_percent': m.cpu_percent,
                    'success': m.success,
                    'error_message': m.error_message
                }
                for m in self.metrics_history
            ]
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)


class MemoryManager:
    """Memory management utility for large operations."""
    
    def __init__(self, memory_limit_gb: float = 4.0, cleanup_threshold: float = 0.8):
        """Initialize memory manager.
        
        Args:
            memory_limit_gb: Memory limit in GB
            cleanup_threshold: Threshold for automatic cleanup (0.0-1.0)
        """
        self.memory_limit_bytes = memory_limit_gb * 1024**3
        self.cleanup_threshold = cleanup_threshold
        self.cleanup_count = 0
    
    def check_memory_usage(self) -> Dict[str, Any]:
        """Check current memory usage.
        
        Returns:
            Dictionary with memory usage information
        """
        memory = psutil.virtual_memory()
        process = psutil.Process()
        
        system_usage = memory.used / memory.total
        process_usage = process.memory_info().rss / self.memory_limit_bytes
        
        return {
            'system_memory_percent': system_usage * 100,
            'process_memory_percent': process_usage * 100,
            'system_memory_gb': memory.used / (1024**3),
            'process_memory_mb': process.memory_info().rss / (1024**2),
            'memory_limit_gb': self.memory_limit_bytes / (1024**3),
            'needs_cleanup': system_usage > self.cleanup_threshold or process_usage > self.cleanup_threshold
        }
    
    def cleanup_if_needed(self) -> bool:
        """Perform cleanup if memory usage is high.
        
        Returns:
            True if cleanup was performed, False otherwise
        """
        memory_info = self.check_memory_usage()
        
        if memory_info['needs_cleanup']:
            self.cleanup_memory()
            return True
        
        return False
    
    def cleanup_memory(self) -> Dict[str, Any]:
        """Perform memory cleanup.
        
        Returns:
            Dictionary with cleanup statistics
        """
        memory_before = psutil.Process().memory_info().rss / (1024**2)
        
        # Force garbage collection
        collected = gc.collect()
        
        memory_after = psutil.Process().memory_info().rss / (1024**2)
        memory_freed = memory_before - memory_after
        
        self.cleanup_count += 1
        
        return {
            'memory_before_mb': memory_before,
            'memory_after_mb': memory_after,
            'memory_freed_mb': memory_freed,
            'objects_collected': collected,
            'cleanup_count': self.cleanup_count,
            'cleanup_timestamp': time.time()
        }


# Global performance monitor instance
_global_monitor = None


def get_global_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def monitor_operation(operation_name: str):
    """Decorator for monitoring operations.
    
    Args:
        operation_name: Name of the operation
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            monitor = get_global_monitor()
            with monitor.monitor_operation(operation_name) as metrics:
                result = func(*args, **kwargs)
                return result
        return wrapper
    return decorator


@contextmanager
def performance_context(operation_name: str):
    """Context manager for performance monitoring.
    
    Args:
        operation_name: Name of the operation
        
    Yields:
        PerformanceMetrics object
    """
    monitor = get_global_monitor()
    with monitor.monitor_operation(operation_name) as metrics:
        yield metrics
