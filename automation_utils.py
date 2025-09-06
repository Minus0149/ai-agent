"""Utility functions and enhanced error handling for browser automation."""

import asyncio
import time
import random
from typing import Dict, List, Optional, Any, Callable, Tuple
from functools import wraps
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path
import hashlib
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RetryStrategy(Enum):
    """Different retry strategies for failed operations."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"
    RANDOM = "random"

@dataclass
class RetryConfig:
    """Configuration for retry mechanisms."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    backoff_multiplier: float = 2.0
    jitter: bool = True
    retry_on_exceptions: Tuple[Exception, ...] = (Exception,)

class AutomationError(Exception):
    """Base exception for automation errors."""
    pass

class BrowserError(AutomationError):
    """Browser-related errors."""
    pass

class TaskTimeoutError(AutomationError):
    """Task timeout errors."""
    pass

class ValidationError(AutomationError):
    """Data validation errors."""
    pass

class NetworkError(AutomationError):
    """Network-related errors."""
    pass

def calculate_retry_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for retry attempt based on strategy."""
    if config.strategy == RetryStrategy.LINEAR:
        delay = config.base_delay * attempt
    elif config.strategy == RetryStrategy.EXPONENTIAL:
        delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
    elif config.strategy == RetryStrategy.FIBONACCI:
        fib_sequence = [1, 1]
        for i in range(2, attempt + 1):
            fib_sequence.append(fib_sequence[i-1] + fib_sequence[i-2])
        delay = config.base_delay * fib_sequence[min(attempt, len(fib_sequence) - 1)]
    elif config.strategy == RetryStrategy.RANDOM:
        delay = random.uniform(config.base_delay, config.base_delay * 3)
    else:
        delay = config.base_delay
    
    # Apply jitter if enabled
    if config.jitter:
        jitter_factor = random.uniform(0.8, 1.2)
        delay *= jitter_factor
    
    return min(delay, config.max_delay)

def retry_async(config: RetryConfig):
    """Decorator for async functions with retry logic."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except config.retry_on_exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts:
                        logger.error(f"Function {func.__name__} failed after {config.max_attempts} attempts: {e}")
                        raise e
                    
                    delay = calculate_retry_delay(attempt, config)
                    logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s")
                    await asyncio.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator

def retry_sync(config: RetryConfig):
    """Decorator for sync functions with retry logic."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except config.retry_on_exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts:
                        logger.error(f"Function {func.__name__} failed after {config.max_attempts} attempts: {e}")
                        raise e
                    
                    delay = calculate_retry_delay(attempt, config)
                    logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s")
                    time.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator

class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.metrics = {
            'function_calls': {},
            'execution_times': {},
            'error_counts': {},
            'success_rates': {}
        }
    
    def track_execution(self, func_name: str, duration: float, success: bool):
        """Track function execution metrics."""
        if func_name not in self.metrics['function_calls']:
            self.metrics['function_calls'][func_name] = 0
            self.metrics['execution_times'][func_name] = []
            self.metrics['error_counts'][func_name] = 0
            self.metrics['success_rates'][func_name] = {'success': 0, 'total': 0}
        
        self.metrics['function_calls'][func_name] += 1
        self.metrics['execution_times'][func_name].append(duration)
        self.metrics['success_rates'][func_name]['total'] += 1
        
        if success:
            self.metrics['success_rates'][func_name]['success'] += 1
        else:
            self.metrics['error_counts'][func_name] += 1
    
    def get_stats(self, func_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics."""
        if func_name:
            if func_name not in self.metrics['function_calls']:
                return {}
            
            times = self.metrics['execution_times'][func_name]
            success_data = self.metrics['success_rates'][func_name]
            
            return {
                'function_name': func_name,
                'total_calls': self.metrics['function_calls'][func_name],
                'error_count': self.metrics['error_counts'][func_name],
                'success_rate': success_data['success'] / success_data['total'] if success_data['total'] > 0 else 0,
                'avg_execution_time': sum(times) / len(times) if times else 0,
                'min_execution_time': min(times) if times else 0,
                'max_execution_time': max(times) if times else 0
            }
        else:
            # Return overall stats
            all_stats = {}
            for func in self.metrics['function_calls'].keys():
                all_stats[func] = self.get_stats(func)
            return all_stats

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_performance(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        success = False
        try:
            result = await func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            raise e
        finally:
            duration = time.time() - start_time
            performance_monitor.track_execution(func.__name__, duration, success)
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        success = False
        try:
            result = func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            raise e
        finally:
            duration = time.time() - start_time
            performance_monitor.track_execution(func.__name__, duration, success)
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

class TaskCache:
    """Cache for automation task results."""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_key(self, task_description: str, config: Dict[str, Any]) -> str:
        """Generate cache key for task and config."""
        combined = f"{task_description}_{json.dumps(config, sort_keys=True)}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path for key."""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, task_description: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired."""
        cache_key = self._get_cache_key(task_description, config)
        cache_file = self._get_cache_file(cache_key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                cache_file.unlink()  # Remove expired cache
                return None
            
            logger.info(f"Cache hit for task: {task_description[:50]}...")
            return cached_data['result']
        
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None
    
    def set(self, task_description: str, config: Dict[str, Any], result: Dict[str, Any]):
        """Cache task result."""
        cache_key = self._get_cache_key(task_description, config)
        cache_file = self._get_cache_file(cache_key)
        
        cached_data = {
            'timestamp': datetime.now().isoformat(),
            'task_description': task_description,
            'config': config,
            'result': result
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cached_data, f, indent=2, default=str)
            logger.info(f"Cached result for task: {task_description[:50]}...")
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")
    
    def clear_expired(self):
        """Clear all expired cache entries."""
        cleared_count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cached_time > self.ttl:
                    cache_file.unlink()
                    cleared_count += 1
            except Exception:
                # Remove corrupted cache files
                cache_file.unlink()
                cleared_count += 1
        
        logger.info(f"Cleared {cleared_count} expired cache entries")
    
    def clear_all(self):
        """Clear all cache entries."""
        cleared_count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            cleared_count += 1
        logger.info(f"Cleared all {cleared_count} cache entries")

class ValidationUtils:
    """Utilities for validating automation results."""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate if URL is properly formatted."""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain...
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # host...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return email_pattern.match(email) is not None
    
    @staticmethod
    def validate_task_result(result: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
        """Validate that task result contains required fields."""
        missing_fields = []
        for field in required_fields:
            if field not in result or result[field] is None:
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file operations."""
        import re
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')
        # Limit length
        return sanitized[:255]

class HumanBehaviorSimulator:
    """Simulate human-like behavior to avoid detection."""
    
    @staticmethod
    def random_delay(min_seconds: float = 0.5, max_seconds: float = 2.0) -> float:
        """Generate random delay to simulate human thinking time."""
        return random.uniform(min_seconds, max_seconds)
    
    @staticmethod
    def typing_delay(text_length: int, wpm: int = 60) -> float:
        """Calculate realistic typing delay based on text length and WPM."""
        # Average 5 characters per word
        words = text_length / 5
        minutes = words / wpm
        seconds = minutes * 60
        # Add some randomness
        return seconds * random.uniform(0.8, 1.2)
    
    @staticmethod
    def should_take_break(actions_count: int, break_probability: float = 0.1) -> bool:
        """Determine if a break should be taken based on action count."""
        if actions_count > 0 and actions_count % 10 == 0:
            return random.random() < break_probability
        return False
    
    @staticmethod
    def break_duration() -> float:
        """Generate realistic break duration."""
        return random.uniform(2.0, 8.0)

def generate_temp_email() -> str:
    """Generate a temporary email address."""
    domains = ['tempmail.org', '10minutemail.com', 'guerrillamail.com', 'mailinator.com']
    username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
    domain = random.choice(domains)
    return f"{username}@{domain}"

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def safe_filename_from_url(url: str) -> str:
    """Generate safe filename from URL."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc.replace('.', '_')
    path = parsed.path.replace('/', '_').replace('\\', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{domain}{path}_{timestamp}"

class ErrorAnalyzer:
    """Analyze and categorize automation errors."""
    
    ERROR_CATEGORIES = {
        'network': ['connection', 'timeout', 'dns', 'ssl', 'certificate'],
        'browser': ['element not found', 'stale element', 'no such element', 'webdriver'],
        'authentication': ['login', 'password', 'credentials', 'unauthorized', '401', '403'],
        'captcha': ['captcha', 'recaptcha', 'verification', 'robot'],
        'rate_limit': ['rate limit', 'too many requests', '429', 'throttle'],
        'server_error': ['500', '502', '503', '504', 'internal server error'],
        'validation': ['invalid', 'required field', 'format', 'validation']
    }
    
    @classmethod
    def categorize_error(cls, error_message: str) -> str:
        """Categorize error based on message content."""
        error_lower = error_message.lower()
        
        for category, keywords in cls.ERROR_CATEGORIES.items():
            if any(keyword in error_lower for keyword in keywords):
                return category
        
        return 'unknown'
    
    @classmethod
    def suggest_solution(cls, error_message: str) -> str:
        """Suggest solution based on error category."""
        category = cls.categorize_error(error_message)
        
        solutions = {
            'network': 'Check internet connection and try again. Consider using a different network or VPN.',
            'browser': 'Wait for page to load completely. Try refreshing the page or using different selectors.',
            'authentication': 'Verify credentials are correct. Check if account is locked or requires 2FA.',
            'captcha': 'Manual intervention required for CAPTCHA. Consider using CAPTCHA solving services.',
            'rate_limit': 'Reduce request frequency. Implement delays between actions.',
            'server_error': 'Server is experiencing issues. Try again later or contact site administrator.',
            'validation': 'Check input data format and required fields. Verify form requirements.',
            'unknown': 'Review error details and check automation logs for more information.'
        }
        
        return solutions.get(category, solutions['unknown'])

# Global instances
task_cache = TaskCache()
validation_utils = ValidationUtils()
human_behavior = HumanBehaviorSimulator()
error_analyzer = ErrorAnalyzer()