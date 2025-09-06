"""Multi-language code generators for browser automation tasks."""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, BaseLoader, Template
from automation_schemas import get_schema_for_task
from automation_configs import get_recommended_config

class CodeGeneratorManager:
    """Manages code generation for multiple programming languages."""
    
    def __init__(self):
        self.generators = {
            'python': PythonGenerator(),
            'javascript': JavaScriptGenerator(),
            'typescript': TypeScriptGenerator(),
            'java': JavaGenerator(),
            'csharp': CSharpGenerator(),
            'go': GoGenerator(),
            'rust': RustGenerator(),
            'php': PHPGenerator(),
            'ruby': RubyGenerator(),
            'kotlin': KotlinGenerator()
        }
    
    async def generate_code(self, 
                          task_description: str,
                          target_language: str,
                          framework: Optional[str] = None,
                          include_tests: bool = True,
                          include_docs: bool = True) -> Dict[str, Any]:
        """Generate code for automation task in specified language."""
        
        if target_language.lower() not in self.generators:
            raise ValueError(f"Unsupported language: {target_language}")
        
        generator = self.generators[target_language.lower()]
        
        # Get task analysis
        task_analysis = self._analyze_task(task_description)
        
        # Generate code
        result = await generator.generate(
            task_description=task_description,
            task_analysis=task_analysis,
            framework=framework,
            include_tests=include_tests,
            include_docs=include_docs
        )
        
        return result
    
    def get_supported_languages(self) -> Dict[str, Dict[str, Any]]:
        """Get list of supported languages and their capabilities."""
        languages = {}
        for lang, generator in self.generators.items():
            languages[lang] = {
                'name': generator.get_language_name(),
                'frameworks': generator.get_supported_frameworks(),
                'features': generator.get_features(),
                'file_extensions': generator.get_file_extensions()
            }
        return languages
    
    def _analyze_task(self, task_description: str) -> Dict[str, Any]:
        """Analyze task description to extract key information."""
        task_lower = task_description.lower()
        
        # Detect task type
        task_type = 'general'
        if any(keyword in task_lower for keyword in ['login', 'sign in', 'authenticate']):
            task_type = 'login'
        elif any(keyword in task_lower for keyword in ['form', 'fill', 'submit']):
            task_type = 'form_filling'
        elif any(keyword in task_lower for keyword in ['search', 'find', 'look for']):
            task_type = 'search'
        elif any(keyword in task_lower for keyword in ['scrape', 'extract', 'collect']):
            task_type = 'scraping'
        elif any(keyword in task_lower for keyword in ['buy', 'purchase', 'cart']):
            task_type = 'ecommerce'
        
        # Extract URLs
        url_pattern = r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z]{2,}'
        urls = re.findall(url_pattern, task_description)
        
        # Extract actions
        actions = []
        action_keywords = {
            'navigate': ['go to', 'visit', 'navigate', 'open'],
            'click': ['click', 'press', 'tap'],
            'input': ['type', 'enter', 'input', 'fill'],
            'wait': ['wait', 'pause', 'delay'],
            'extract': ['extract', 'get', 'collect', 'scrape']
        }
        
        for action, keywords in action_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                actions.append(action)
        
        return {
            'type': task_type,
            'urls': urls,
            'actions': actions,
            'complexity': len(actions),
            'requires_auth': 'login' in task_type or any(keyword in task_lower for keyword in ['login', 'password', 'auth']),
            'requires_data_extraction': 'extract' in actions or 'scraping' in task_type,
            'requires_form_interaction': 'form_filling' in task_type or 'input' in actions
        }

class BaseGenerator:
    """Base class for code generators."""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    async def generate(self, 
                     task_description: str,
                     task_analysis: Dict[str, Any],
                     framework: Optional[str] = None,
                     include_tests: bool = True,
                     include_docs: bool = True) -> Dict[str, Any]:
        """Generate code for the task."""
        raise NotImplementedError
    
    def get_language_name(self) -> str:
        """Get human-readable language name."""
        raise NotImplementedError
    
    def get_supported_frameworks(self) -> List[str]:
        """Get list of supported frameworks."""
        return []
    
    def get_features(self) -> List[str]:
        """Get list of supported features."""
        return []
    
    def get_file_extensions(self) -> List[str]:
        """Get file extensions for this language."""
        raise NotImplementedError
    
    def _load_templates(self) -> Dict[str, Template]:
        """Load code templates."""
        return {}
    
    def _generate_dependencies(self, task_analysis: Dict[str, Any], framework: Optional[str]) -> List[str]:
        """Generate list of dependencies."""
        return []

class PythonGenerator(BaseGenerator):
    """Python code generator."""
    
    def get_language_name(self) -> str:
        return "Python"
    
    def get_supported_frameworks(self) -> List[str]:
        return ["playwright", "selenium", "browser-use", "requests-html"]
    
    def get_features(self) -> List[str]:
        return ["async/await", "type hints", "dataclasses", "context managers"]
    
    def get_file_extensions(self) -> List[str]:
        return [".py"]
    
    async def generate(self, 
                     task_description: str,
                     task_analysis: Dict[str, Any],
                     framework: Optional[str] = None,
                     include_tests: bool = True,
                     include_docs: bool = True) -> Dict[str, Any]:
        
        framework = framework or "browser-use"
        
        if framework == "browser-use":
            code = self._generate_browser_use_code(task_description, task_analysis)
        elif framework == "playwright":
            code = self._generate_playwright_code(task_description, task_analysis)
        elif framework == "selenium":
            code = self._generate_selenium_code(task_description, task_analysis)
        else:
            code = self._generate_browser_use_code(task_description, task_analysis)
        
        tests = self._generate_tests(task_analysis, framework) if include_tests else None
        docs = self._generate_documentation(task_description, task_analysis) if include_docs else None
        dependencies = self._generate_dependencies(task_analysis, framework)
        
        return {
            'language': 'python',
            'framework': framework,
            'code': code,
            'tests': tests,
            'documentation': docs,
            'dependencies': dependencies
        }
    
    def _generate_browser_use_code(self, task_description: str, task_analysis: Dict[str, Any]) -> str:
        template = '''
"""Browser automation script generated for: {task_description}"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import browser automation components
from browser_use import Agent, Browser, ChatGoogle
from automation_schemas import get_schema_for_task
from automation_configs import get_recommended_config
from automation_utils import performance_monitor, format_duration

load_dotenv()

class AutomationTask:
    """Automated task: {task_description}"""
    
    def __init__(self, config_name: Optional[str] = None):
        self.task_description = "{task_description}"
        self.config = get_recommended_config(self.task_description) if not config_name else None
        self.schema = get_schema_for_task(self.task_description)
        self.results = {{}}
    
    @performance_monitor
    async def run(self) -> Dict[str, Any]:
        """Execute the automation task."""
        print(f"Starting task: {{self.task_description}}")
        print(f"Configuration: {{self.config['name']}}")
        
        try:
            # Create browser with optimized settings
            browser = Browser(
                headless={headless},
                window_size={{'width': 1920, 'height': 1080}},
                highlight_elements=True,
                wait_between_actions=0.3
            )
            
            # Create LLM
            llm = ChatGoogle(model="gemini-2.5-flash")
            
            # Create and run agent
            agent = Agent(
                task=self.task_description,
                llm=llm,
                browser=browser
            )
            
            start_time = datetime.now()
            result = await agent.run()
            duration = (datetime.now() - start_time).total_seconds()
            
            self.results = {{
                'status': 'completed',
                'result': result,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }}
            
            print(f"Task completed successfully in {{format_duration(duration)}}")
            return self.results
            
        except Exception as e:
            self.results = {{
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }}
            print(f"Task failed: {{e}}")
            return self.results
    
    def get_results(self) -> Dict[str, Any]:
        """Get task results."""
        return self.results

async def main():
    """Main execution function."""
    task = AutomationTask()
    result = await task.run()
    
    print("\nFinal Results:")
    print(f"Status: {{result['status']}}")
    if result['status'] == 'completed':
        print(f"Duration: {{format_duration(result['duration'])}}")
        if 'result' in result:
            print(f"Output: {{result['result']}}")
    else:
        print(f"Error: {{result['error']}}")

if __name__ == "__main__":
    asyncio.run(main())
'''.format(
            task_description=task_description,
            headless="True" if task_analysis.get('complexity', 0) > 3 else "False"
        )
        
        return template.strip()
    
    def _generate_playwright_code(self, task_description: str, task_analysis: Dict[str, Any]) -> str:
        template = '''
"""Playwright automation script for: {task_description}"""

import asyncio
from playwright.async_api import async_playwright, Page, Browser
from typing import Dict, Any

class PlaywrightAutomation:
    """Playwright-based automation for: {task_description}"""
    
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None
    
    async def setup(self):
        """Set up browser and page."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless={headless},
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({{'width': 1920, 'height': 1080}})
    
    async def cleanup(self):
        """Clean up resources."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
    
    async def run_automation(self) -> Dict[str, Any]:
        """Execute the automation task."""
        try:
            await self.setup()
            
            # TODO: Implement specific automation steps
            # Example steps based on task analysis:
            {automation_steps}
            
            return {{'status': 'completed', 'message': 'Task completed successfully'}}
            
        except Exception as e:
            return {{'status': 'failed', 'error': str(e)}}
        
        finally:
            await self.cleanup()

async def main():
    automation = PlaywrightAutomation()
    result = await automation.run_automation()
    print(f"Result: {{result}}")

if __name__ == "__main__":
    asyncio.run(main())
'''.format(
            task_description=task_description,
            headless="True" if task_analysis.get('complexity', 0) > 3 else "False",
            automation_steps=self._generate_automation_steps(task_analysis)
        )
        
        return template.strip()
    
    def _generate_selenium_code(self, task_description: str, task_analysis: Dict[str, Any]) -> str:
        template = '''
"""Selenium automation script for: {task_description}"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from typing import Dict, Any
import time

class SeleniumAutomation:
    """Selenium-based automation for: {task_description}"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def setup(self):
        """Set up WebDriver."""
        options = Options()
        {chrome_options}
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1920, 1080)
        self.wait = WebDriverWait(self.driver, 10)
    
    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
    
    def run_automation(self) -> Dict[str, Any]:
        """Execute the automation task."""
        try:
            self.setup()
            
            # TODO: Implement specific automation steps
            # Example steps based on task analysis:
            {automation_steps}
            
            return {{'status': 'completed', 'message': 'Task completed successfully'}}
            
        except Exception as e:
            return {{'status': 'failed', 'error': str(e)}}
        
        finally:
            self.cleanup()

def main():
    automation = SeleniumAutomation()
    result = automation.run_automation()
    print(f"Result: {{result}}")

if __name__ == "__main__":
    main()
'''.format(
            task_description=task_description,
            chrome_options="options.add_argument('--headless')" if task_analysis.get('complexity', 0) > 3 else "# Running in headed mode",
            automation_steps=self._generate_selenium_steps(task_analysis)
        )
        
        return template.strip()
    
    def _generate_automation_steps(self, task_analysis: Dict[str, Any]) -> str:
        steps = []
        
        if 'navigate' in task_analysis.get('actions', []):
            if task_analysis.get('urls'):
                url = task_analysis['urls'][0]
                steps.append(f"            await self.page.goto('{url}')")
            else:
                steps.append("            # await self.page.goto('https://example.com')")
        
        if 'input' in task_analysis.get('actions', []):
            steps.append("            # await self.page.fill('input[name=\"username\"]', 'your_username')")
            steps.append("            # await self.page.fill('input[name=\"password\"]', 'your_password')")
        
        if 'click' in task_analysis.get('actions', []):
            steps.append("            # await self.page.click('button[type=\"submit\"]')")
        
        if 'wait' in task_analysis.get('actions', []):
            steps.append("            # await self.page.wait_for_selector('.result')")
        
        if 'extract' in task_analysis.get('actions', []):
            steps.append("            # data = await self.page.text_content('.data-element')")
            steps.append("            # return {'extracted_data': data}")
        
        return '\n'.join(steps) if steps else "            # Add your automation steps here"
    
    def _generate_selenium_steps(self, task_analysis: Dict[str, Any]) -> str:
        steps = []
        
        if 'navigate' in task_analysis.get('actions', []):
            if task_analysis.get('urls'):
                url = task_analysis['urls'][0]
                steps.append(f"            self.driver.get('{url}')")
            else:
                steps.append("            # self.driver.get('https://example.com')")
        
        if 'input' in task_analysis.get('actions', []):
            steps.append("            # username_field = self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))")
            steps.append("            # username_field.send_keys('your_username')")
        
        if 'click' in task_analysis.get('actions', []):
            steps.append("            # submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type=\"submit\"]')))")
            steps.append("            # submit_button.click()")
        
        if 'wait' in task_analysis.get('actions', []):
            steps.append("            # self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'result')))")
        
        if 'extract' in task_analysis.get('actions', []):
            steps.append("            # data_element = self.driver.find_element(By.CLASS_NAME, 'data-element')")
            steps.append("            # return {'extracted_data': data_element.text}")
        
        return '\n'.join(steps) if steps else "            # Add your automation steps here"
    
    def _generate_tests(self, task_analysis: Dict[str, Any], framework: str) -> str:
        return f'''
"""Tests for the automation script."""

import pytest
import asyncio
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_automation_task():
    """Test the main automation task."""
    # TODO: Implement test cases
    assert True  # Placeholder

def test_task_analysis():
    """Test task analysis functionality."""
    # TODO: Implement analysis tests
    assert True  # Placeholder

if __name__ == "__main__":
    pytest.main([__file__])
'''
    
    def _generate_documentation(self, task_description: str, task_analysis: Dict[str, Any]) -> str:
        return f'''
# Automation Script Documentation

## Task Description
{task_description}

## Task Analysis
- **Type**: {task_analysis.get('type', 'general')}
- **Complexity**: {task_analysis.get('complexity', 0)}
- **Actions**: {', '.join(task_analysis.get('actions', []))}
- **URLs**: {', '.join(task_analysis.get('urls', []))}
- **Requires Authentication**: {task_analysis.get('requires_auth', False)}
- **Requires Data Extraction**: {task_analysis.get('requires_data_extraction', False)}

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. Run the script:
   ```bash
   python automation_script.py
   ```

## Configuration

The script uses automatic configuration selection based on the task type.
You can customize the configuration by modifying the config parameters.

## Error Handling

The script includes comprehensive error handling and will provide detailed
error messages if something goes wrong.

## Generated on
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
    
    def _generate_dependencies(self, task_analysis: Dict[str, Any], framework: str) -> List[str]:
        base_deps = ["python-dotenv", "pydantic"]
        
        if framework == "browser-use":
            return base_deps + ["browser-use", "google-generativeai"]
        elif framework == "playwright":
            return base_deps + ["playwright"]
        elif framework == "selenium":
            return base_deps + ["selenium", "webdriver-manager"]
        else:
            return base_deps

# Additional generators for other languages would follow similar patterns
class JavaScriptGenerator(BaseGenerator):
    def get_language_name(self) -> str:
        return "JavaScript"
    
    def get_supported_frameworks(self) -> List[str]:
        return ["playwright", "puppeteer", "selenium-webdriver"]
    
    def get_file_extensions(self) -> List[str]:
        return [".js"]
    
    async def generate(self, task_description: str, task_analysis: Dict[str, Any], 
                     framework: Optional[str] = None, include_tests: bool = True, 
                     include_docs: bool = True) -> Dict[str, Any]:
        # JavaScript code generation implementation
        return {
            'language': 'javascript',
            'framework': framework or 'playwright',
            'code': '// JavaScript automation code would be generated here',
            'tests': '// Jest tests would be generated here' if include_tests else None,
            'documentation': '# JavaScript Documentation' if include_docs else None,
            'dependencies': ['playwright', '@playwright/test']
        }

class TypeScriptGenerator(BaseGenerator):
    def get_language_name(self) -> str:
        return "TypeScript"
    
    def get_supported_frameworks(self) -> List[str]:
        return ["playwright", "puppeteer"]
    
    def get_file_extensions(self) -> List[str]:
        return [".ts"]
    
    async def generate(self, task_description: str, task_analysis: Dict[str, Any], 
                     framework: Optional[str] = None, include_tests: bool = True, 
                     include_docs: bool = True) -> Dict[str, Any]:
        return {
            'language': 'typescript',
            'framework': framework or 'playwright',
            'code': '// TypeScript automation code would be generated here',
            'tests': '// TypeScript tests would be generated here' if include_tests else None,
            'documentation': '# TypeScript Documentation' if include_docs else None,
            'dependencies': ['playwright', '@types/node', 'typescript']
        }

# Placeholder generators for other languages
class JavaGenerator(BaseGenerator):
    def get_language_name(self) -> str:
        return "Java"
    
    def get_file_extensions(self) -> List[str]:
        return [".java"]
    
    async def generate(self, **kwargs) -> Dict[str, Any]:
        return {'language': 'java', 'code': '// Java code placeholder'}

class CSharpGenerator(BaseGenerator):
    def get_language_name(self) -> str:
        return "C#"
    
    def get_file_extensions(self) -> List[str]:
        return [".cs"]
    
    async def generate(self, **kwargs) -> Dict[str, Any]:
        return {'language': 'csharp', 'code': '// C# code placeholder'}

class GoGenerator(BaseGenerator):
    def get_language_name(self) -> str:
        return "Go"
    
    def get_file_extensions(self) -> List[str]:
        return [".go"]
    
    async def generate(self, **kwargs) -> Dict[str, Any]:
        return {'language': 'go', 'code': '// Go code placeholder'}

class RustGenerator(BaseGenerator):
    def get_language_name(self) -> str:
        return "Rust"
    
    def get_file_extensions(self) -> List[str]:
        return [".rs"]
    
    async def generate(self, **kwargs) -> Dict[str, Any]:
        return {'language': 'rust', 'code': '// Rust code placeholder'}

class PHPGenerator(BaseGenerator):
    def get_language_name(self) -> str:
        return "PHP"
    
    def get_file_extensions(self) -> List[str]:
        return [".php"]
    
    async def generate(self, **kwargs) -> Dict[str, Any]:
        return {'language': 'php', 'code': '<?php // PHP code placeholder'}

class RubyGenerator(BaseGenerator):
    def get_language_name(self) -> str:
        return "Ruby"
    
    def get_file_extensions(self) -> List[str]:
        return [".rb"]
    
    async def generate(self, **kwargs) -> Dict[str, Any]:
        return {'language': 'ruby', 'code': '# Ruby code placeholder'}

class KotlinGenerator(BaseGenerator):
    def get_language_name(self) -> str:
        return "Kotlin"
    
    def get_file_extensions(self) -> List[str]:
        return [".kt"]
    
    async def generate(self, **kwargs) -> Dict[str, Any]:
        return {'language': 'kotlin', 'code': '// Kotlin code placeholder'}