"""Configuration templates for different automation scenarios."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class AutomationConfig:
    """Base configuration class for automation tasks."""
    name: str
    description: str
    browser_config: Dict[str, Any]
    llm_config: Dict[str, Any]
    performance_config: Dict[str, Any]
    tracking_config: Dict[str, Any]
    custom_settings: Optional[Dict[str, Any]] = None

# Predefined configuration templates
CONFIG_TEMPLATES = {
    "fast_automation": {
        "name": "Fast Automation",
        "description": "Optimized for speed with minimal visual feedback",
        "browser_config": {
            "headless": True,
            "window_size": {"width": 1280, "height": 720},
            "highlight_elements": False,
            "wait_between_actions": 0.1,
            "enable_default_extensions": False,
            "disable_images": True,
            "disable_javascript": False,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "llm_config": {
            "model": "gemini-2.5-flash",
            "temperature": 0.0,
            "max_tokens": 2000
        },
        "performance_config": {
            "max_steps": 25,
            "timeout": 120,
            "retry_attempts": 2,
            "parallel_tasks": True
        },
        "tracking_config": {
            "save_screenshots": False,
            "save_html": False,
            "log_level": "WARNING"
        }
    },
    
    "visual_automation": {
        "name": "Visual Automation",
        "description": "Full visual feedback for debugging and demonstration",
        "browser_config": {
            "headless": False,
            "window_size": {"width": 1920, "height": 1080},
            "highlight_elements": True,
            "wait_between_actions": 1.0,
            "enable_default_extensions": True,
            "disable_images": False,
            "disable_javascript": False
        },
        "llm_config": {
            "model": "gemini-2.5-flash",
            "temperature": 0.1,
            "max_tokens": 4000
        },
        "performance_config": {
            "max_steps": 50,
            "timeout": 600,
            "retry_attempts": 3,
            "parallel_tasks": False
        },
        "tracking_config": {
            "save_screenshots": True,
            "save_html": True,
            "log_level": "INFO"
        }
    },
    
    "stealth_automation": {
        "name": "Stealth Automation",
        "description": "Designed to avoid detection with human-like behavior",
        "browser_config": {
            "headless": False,
            "window_size": {"width": 1366, "height": 768},
            "highlight_elements": False,
            "wait_between_actions": 2.0,
            "enable_default_extensions": True,
            "disable_images": False,
            "disable_javascript": False,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
        "llm_config": {
            "model": "gemini-2.5-flash",
            "temperature": 0.2,
            "max_tokens": 4000
        },
        "performance_config": {
            "max_steps": 40,
            "timeout": 480,
            "retry_attempts": 3,
            "parallel_tasks": False
        },
        "tracking_config": {
            "save_screenshots": True,
            "save_html": False,
            "log_level": "INFO"
        },
        "custom_settings": {
            "random_delays": True,
            "human_typing_speed": True,
            "mouse_movements": True
        }
    },
    
    "data_extraction": {
        "name": "Data Extraction",
        "description": "Optimized for web scraping and data collection",
        "browser_config": {
            "headless": True,
            "window_size": {"width": 1920, "height": 1080},
            "highlight_elements": False,
            "wait_between_actions": 0.5,
            "enable_default_extensions": False,
            "disable_images": True,
            "disable_javascript": False
        },
        "llm_config": {
            "model": "gemini-2.5-flash",
            "temperature": 0.0,
            "max_tokens": 6000
        },
        "performance_config": {
            "max_steps": 100,
            "timeout": 900,
            "retry_attempts": 5,
            "parallel_tasks": True
        },
        "tracking_config": {
            "save_screenshots": False,
            "save_html": True,
            "log_level": "INFO"
        },
        "custom_settings": {
            "pagination_handling": True,
            "data_validation": True,
            "export_formats": ["json", "csv", "xlsx"]
        }
    },
    
    "form_automation": {
        "name": "Form Automation",
        "description": "Specialized for form filling and submission",
        "browser_config": {
            "headless": False,
            "window_size": {"width": 1440, "height": 900},
            "highlight_elements": True,
            "wait_between_actions": 0.8,
            "enable_default_extensions": True,
            "disable_images": False,
            "disable_javascript": False
        },
        "llm_config": {
            "model": "gemini-2.5-flash",
            "temperature": 0.1,
            "max_tokens": 3000
        },
        "performance_config": {
            "max_steps": 30,
            "timeout": 300,
            "retry_attempts": 3,
            "parallel_tasks": False
        },
        "tracking_config": {
            "save_screenshots": True,
            "save_html": False,
            "log_level": "INFO"
        },
        "custom_settings": {
            "form_validation": True,
            "auto_captcha_detection": True,
            "field_mapping": True
        }
    },
    
    "ecommerce_automation": {
        "name": "E-commerce Automation",
        "description": "Optimized for online shopping and product research",
        "browser_config": {
            "headless": False,
            "window_size": {"width": 1600, "height": 1000},
            "highlight_elements": True,
            "wait_between_actions": 1.2,
            "enable_default_extensions": True,
            "disable_images": False,
            "disable_javascript": False
        },
        "llm_config": {
            "model": "gemini-2.5-flash",
            "temperature": 0.1,
            "max_tokens": 4000
        },
        "performance_config": {
            "max_steps": 60,
            "timeout": 600,
            "retry_attempts": 3,
            "parallel_tasks": False
        },
        "tracking_config": {
            "save_screenshots": True,
            "save_html": False,
            "log_level": "INFO"
        },
        "custom_settings": {
            "price_tracking": True,
            "product_comparison": True,
            "cart_management": True,
            "checkout_automation": False  # Safety feature
        }
    },
    
    "social_media_automation": {
        "name": "Social Media Automation",
        "description": "For social media interactions and content management",
        "browser_config": {
            "headless": False,
            "window_size": {"width": 1280, "height": 800},
            "highlight_elements": True,
            "wait_between_actions": 2.5,
            "enable_default_extensions": True,
            "disable_images": False,
            "disable_javascript": False
        },
        "llm_config": {
            "model": "gemini-2.5-flash",
            "temperature": 0.3,
            "max_tokens": 3000
        },
        "performance_config": {
            "max_steps": 40,
            "timeout": 480,
            "retry_attempts": 2,
            "parallel_tasks": False
        },
        "tracking_config": {
            "save_screenshots": True,
            "save_html": False,
            "log_level": "INFO"
        },
        "custom_settings": {
            "rate_limiting": True,
            "content_moderation": True,
            "engagement_tracking": True,
            "platform_specific_rules": True
        }
    },
    
    "testing_automation": {
        "name": "Testing Automation",
        "description": "For automated testing and quality assurance",
        "browser_config": {
            "headless": True,
            "window_size": {"width": 1920, "height": 1080},
            "highlight_elements": False,
            "wait_between_actions": 0.3,
            "enable_default_extensions": False,
            "disable_images": True,
            "disable_javascript": False
        },
        "llm_config": {
            "model": "gemini-2.5-flash",
            "temperature": 0.0,
            "max_tokens": 4000
        },
        "performance_config": {
            "max_steps": 80,
            "timeout": 600,
            "retry_attempts": 1,
            "parallel_tasks": True
        },
        "tracking_config": {
            "save_screenshots": True,
            "save_html": True,
            "log_level": "DEBUG"
        },
        "custom_settings": {
            "assertion_checking": True,
            "performance_monitoring": True,
            "error_reporting": True,
            "test_coverage": True
        }
    }
}

class ConfigManager:
    """Manager for automation configurations."""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path("./configs")
        self.config_dir.mkdir(exist_ok=True)
    
    def get_config(self, config_name: str) -> Dict[str, Any]:
        """Get a configuration by name."""
        if config_name in CONFIG_TEMPLATES:
            return CONFIG_TEMPLATES[config_name].copy()
        
        # Try to load from file
        config_file = self.config_dir / f"{config_name}.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        
        raise ValueError(f"Configuration '{config_name}' not found")
    
    def save_config(self, config_name: str, config: Dict[str, Any]) -> str:
        """Save a configuration to file."""
        config_file = self.config_dir / f"{config_name}.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return str(config_file)
    
    def list_configs(self) -> Dict[str, str]:
        """List all available configurations."""
        configs = {}
        
        # Add built-in templates
        for name, config in CONFIG_TEMPLATES.items():
            configs[name] = config["description"]
        
        # Add custom configs from files
        for config_file in self.config_dir.glob("*.json"):
            name = config_file.stem
            if name not in configs:
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                        configs[name] = config_data.get("description", "Custom configuration")
                except:
                    configs[name] = "Custom configuration (error loading)"
        
        return configs
    
    def create_custom_config(self, 
                           name: str,
                           description: str,
                           base_config: str = "visual_automation",
                           overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a custom configuration based on a template."""
        base = self.get_config(base_config)
        
        if overrides:
            # Deep merge overrides
            for key, value in overrides.items():
                if key in base and isinstance(value, dict) and isinstance(base[key], dict):
                    base[key].update(value)
                else:
                    base[key] = value
        
        base["name"] = name
        base["description"] = description
        
        return base
    
    def optimize_config_for_task(self, task_description: str) -> str:
        """Recommend the best configuration for a given task."""
        task_lower = task_description.lower()
        
        # Speed-focused keywords
        if any(keyword in task_lower for keyword in ['fast', 'quick', 'speed', 'batch', 'bulk']):
            return "fast_automation"
        
        # Stealth keywords
        elif any(keyword in task_lower for keyword in ['stealth', 'undetected', 'bypass', 'avoid detection']):
            return "stealth_automation"
        
        # Data extraction keywords
        elif any(keyword in task_lower for keyword in ['scrape', 'extract', 'collect', 'harvest', 'data']):
            return "data_extraction"
        
        # Form keywords
        elif any(keyword in task_lower for keyword in ['form', 'fill', 'submit', 'register', 'signup']):
            return "form_automation"
        
        # E-commerce keywords
        elif any(keyword in task_lower for keyword in ['buy', 'shop', 'product', 'cart', 'price']):
            return "ecommerce_automation"
        
        # Social media keywords
        elif any(keyword in task_lower for keyword in ['social', 'post', 'tweet', 'facebook', 'instagram']):
            return "social_media_automation"
        
        # Testing keywords
        elif any(keyword in task_lower for keyword in ['test', 'verify', 'check', 'validate', 'qa']):
            return "testing_automation"
        
        # Default to visual for debugging and general use
        else:
            return "visual_automation"

def get_recommended_config(task_description: str) -> Dict[str, Any]:
    """Get recommended configuration for a task description."""
    manager = ConfigManager()
    config_name = manager.optimize_config_for_task(task_description)
    return manager.get_config(config_name)

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two configurations with override taking precedence."""
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(value, dict) and isinstance(result[key], dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result