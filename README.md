# 🤖 Enhanced Browser Automation System with Docker & VNC

A comprehensive, enterprise-grade browser automation system built on top of `browser-use` with advanced features including:

- **🐳 Full Docker containerization** with VNC visualization
- **⚡ FastAPI backend** with real-time WebSocket streaming
- **🖥️ VNC server integration** for live browser viewing
- **🔧 Multi-language code generation** (Python, JavaScript, TypeScript, Java, C#, Go, Rust, PHP, Ruby, Kotlin)
- **📊 Real-time performance monitoring** and metrics
- **🎯 Structured output schemas** with automatic validation
- **🔄 Advanced retry mechanisms** and error handling
- **💾 Intelligent caching** system with TTL
- **🎭 Human behavior simulation** to avoid detection

## 🚀 Features

### Core Capabilities
- **Enhanced Browser Automation**: Built on browser-use with optimized configurations
- **Structured Output**: Automatic schema generation and validation for different task types
- **Performance Monitoring**: Real-time tracking of execution metrics and success rates
- **Intelligent Caching**: Automatic result caching with TTL to avoid redundant operations
- **Advanced Error Handling**: Retry mechanisms with multiple strategies and intelligent error analysis
- **Step Tracking**: Detailed logging of every automation step with timestamps
- **Configuration Management**: Pre-built configurations for different automation scenarios
- **Human Behavior Simulation**: Realistic delays and actions to avoid detection

### Automation Types Supported
- **Login Automation**: Automated login with temporary email generation
- **Form Filling**: Intelligent form detection and completion
- **Web Scraping**: Structured data extraction with pagination support
- **E-commerce Automation**: Product research and cart management
- **Social Media Automation**: Content posting and engagement tracking
- **Search Operations**: Multi-platform search with result extraction
- **File Operations**: Download, upload, and file management
- **Testing Automation**: Automated QA and validation workflows

## 📁 Project Structure

```
playwright-animation/
├── agents.py                 # Main automation backend with enhanced features
├── automation_schemas.py     # Structured output schemas for different tasks
├── automation_configs.py     # Configuration templates and management
├── automation_utils.py       # Utility functions and error handling
├── example_usage.py         # Comprehensive examples and demonstrations
├── requirements.txt         # Python dependencies
├── README.md               # This documentation
└── .env                    # Environment variables (create this)
```

## 🛠️ Installation & Deployment

### 🐳 Docker Deployment (Recommended)

**Prerequisites:**
- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 80, 5901, 6080, 8000 available

**Quick Start:**

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd playwright-animation
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

3. **Deploy with one command**:
   ```bash
   python deploy.py
   ```

4. **Access the system**:
   - 🌐 **Web Dashboard**: http://localhost:80
   - 📚 **API Documentation**: http://localhost:8000/api/docs
   - 🖥️ **VNC Viewer**: vnc://localhost:5901 (password: automation)
   - 🌍 **Web VNC**: http://localhost:6080

**Advanced Deployment Options:**

```bash
# Deploy with monitoring stack (Grafana + Prometheus)
python deploy.py --monitoring

# Deploy with database persistence
python deploy.py --database

# Deploy without rebuilding images
python deploy.py --no-build

# View logs in real-time
python deploy.py logs -f

# Check system health
python deploy.py health

# Stop all services
python deploy.py stop
```

### 📦 Manual Installation (Development)

1. **Install dependencies**:
   ```bash
   pip install -r docker-requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

4. **Run the FastAPI server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 🚀 Quick Start

### 🌐 Web Dashboard Usage

1. **Access the Dashboard**: Open http://localhost:80 in your browser
2. **Enter Task Description**: Describe what you want to automate
3. **Select Configuration**: Choose from pre-built configs or let the system auto-select
4. **Enable VNC**: Check the box to see the browser in real-time
5. **Generate Code**: Optionally select a programming language for code generation
6. **Start Automation**: Click "Start Automation" and watch it work!

### 📡 API Usage

**Create and Run Task:**
```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Navigate to leonardo.ai and login using temp mail",
    "enable_vnc": true,
    "stream_output": true
  }'
```

**Generate Code:**
```bash
curl -X POST "http://localhost:8000/api/generate-code" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Navigate to leonardo.ai and login using temp mail",
    "target_language": "python",
    "include_tests": true,
    "include_docs": true
  }'
```

### 🐍 Python SDK Usage

```python
import asyncio
from agents import BrowserAutomationBackend
from automation_configs import get_recommended_config
from automation_schemas import get_schema_for_task

async def main():
    # Automatic configuration selection
    task = "Navigate to leonardo.ai and login using temp mail"
    config = get_recommended_config(task)
    schema = get_schema_for_task(task)
    
    # Create backend
    backend = BrowserAutomationBackend(config)
    
    # Create and run task
    task_id = "my_task"
    backend.create_task(task_id, task)
    result = await backend.run_task(task_id, schema)
    
    print(f"Status: {result['status']}")
    print(f"Duration: {result['duration']:.2f}s")

asyncio.run(main())
```

### 🖥️ VNC Viewer Access

**Desktop VNC Client:**
- Host: `localhost:5901`
- Password: `automation`

**Web VNC (Browser):**
- URL: http://localhost:6080
- No additional software required

**Real-time Browser Viewing:**
- Watch automation tasks execute live
- Take screenshots during execution
- Full mouse and keyboard control available

### Advanced Usage with Monitoring

```python
import asyncio
from agents import BrowserAutomationBackend, TaskStep
from automation_configs import ConfigManager
from automation_utils import monitor_performance, task_cache

async def advanced_example():
    # Custom configuration
    config_manager = ConfigManager()
    config = config_manager.get_config('fast_automation')
    
    backend = BrowserAutomationBackend(config)
    
    # Add step monitoring
    def step_callback(step: TaskStep):
        print(f"[{step.timestamp.strftime('%H:%M:%S')}] {step.action}: {step.status.value}")
    
    backend.add_step_callback(step_callback)
    
    # Performance monitoring
    @monitor_performance
    async def monitored_task():
        task_id = "advanced_task"
        task_desc = "Search Google for browser automation tools"
        backend.create_task(task_id, task_desc)
        return await backend.run_task(task_id)
    
    result = await monitored_task()
    
    # Save detailed report
    report_file = backend.save_task_report("advanced_task")
    print(f"Report saved: {report_file}")

asyncio.run(advanced_example())
```

## 📋 Configuration Templates

The system includes pre-built configurations optimized for different scenarios:

### Available Configurations

- **`fast_automation`**: Optimized for speed (headless, minimal delays)
- **`visual_automation`**: Full visual feedback for debugging
- **`stealth_automation`**: Human-like behavior to avoid detection
- **`data_extraction`**: Optimized for web scraping
- **`form_automation`**: Specialized for form filling
- **`ecommerce_automation`**: E-commerce specific settings
- **`social_media_automation`**: Social platform optimizations
- **`testing_automation`**: QA and testing workflows

### Custom Configuration

```python
from automation_configs import ConfigManager

config_manager = ConfigManager()

# Create custom config based on template
custom_config = config_manager.create_custom_config(
    name="my_custom_config",
    description="Custom configuration for my use case",
    base_config="visual_automation",
    overrides={
        'browser': {
            'wait_between_actions': 0.5,
            'window_size': {'width': 1440, 'height': 900}
        },
        'performance': {
            'timeout': 120
        }
    }
)

# Save for reuse
config_manager.save_config("my_custom_config", custom_config)
```

## 📊 Structured Output Schemas

The system automatically selects appropriate schemas based on task descriptions:

### Available Schemas

- **LoginResult**: For authentication tasks
- **FormFillResult**: For form submission tasks
- **SearchResult**: For search operations
- **EcommerceActionResult**: For shopping tasks
- **WebScrapingResult**: For data extraction
- **SocialMediaResult**: For social platform tasks
- **FileOperationResult**: For file handling
- **NavigationResult**: For browsing tasks

### Custom Schema

```python
from automation_schemas import create_custom_schema

# Define custom fields
fields = {
    "product_name": {"type": "string", "description": "Product name", "required": True},
    "price": {"type": "number", "description": "Product price"},
    "availability": {"type": "boolean", "description": "In stock status"}
}

custom_schema = create_custom_schema(fields)
```

## 🔧 Error Handling and Retry Logic

### Automatic Retry with Different Strategies

```python
from automation_utils import retry_async, RetryConfig, RetryStrategy

# Configure retry behavior
retry_config = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    strategy=RetryStrategy.EXPONENTIAL,
    backoff_multiplier=2.0,
    jitter=True
)

@retry_async(retry_config)
async def reliable_task():
    # Your automation code here
    pass
```

### Error Analysis and Suggestions

```python
from automation_utils import error_analyzer

try:
    # Automation code
    pass
except Exception as e:
    category = error_analyzer.categorize_error(str(e))
    suggestion = error_analyzer.suggest_solution(str(e))
    print(f"Error category: {category}")
    print(f"Suggestion: {suggestion}")
```

## 📈 Performance Monitoring

### Real-time Metrics

```python
from automation_utils import performance_monitor, monitor_performance

@monitor_performance
async def tracked_function():
    # Your code here
    pass

# Get performance statistics
stats = performance_monitor.get_stats()
print(f"Success rate: {stats['tracked_function']['success_rate']:.1%}")
print(f"Average time: {stats['tracked_function']['avg_execution_time']:.2f}s")
```

### Caching System

```python
from automation_utils import task_cache

# Check cache before running task
cached_result = task_cache.get(task_description, config)
if cached_result:
    return cached_result

# Run task and cache result
result = await run_task()
task_cache.set(task_description, config, result)
```

## 🎭 Human Behavior Simulation

```python
from automation_utils import human_behavior

# Add realistic delays
delay = human_behavior.random_delay(0.5, 2.0)
await asyncio.sleep(delay)

# Calculate typing delay
text = "Hello, world!"
typing_delay = human_behavior.typing_delay(len(text), wpm=60)

# Check if break is needed
if human_behavior.should_take_break(action_count):
    break_time = human_behavior.break_duration()
    await asyncio.sleep(break_time)
```

## 📝 Examples

Run the comprehensive examples:

```bash
python example_usage.py
```

This will demonstrate:
- Enhanced Leonardo.ai login automation
- Web search with result extraction
- Form filling with validation
- Data extraction from e-commerce sites
- Batch processing multiple tasks

## 🔍 Debugging and Logging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

### Save Detailed Reports

```python
# Automatic report generation
report_file = backend.save_task_report(task_id)
print(f"Detailed report: {report_file}")

# Custom report location
report_file = backend.save_task_report(task_id, "./reports/my_report.json")
```

## 🛡️ Security and Best Practices

1. **Environment Variables**: Store API keys in `.env` file, never in code
2. **Rate Limiting**: Built-in delays and human behavior simulation
3. **Error Handling**: Comprehensive exception handling with graceful degradation
4. **Validation**: Input validation and output verification
5. **Caching**: Avoid redundant operations with intelligent caching
6. **Monitoring**: Real-time performance and error tracking

## 🔧 Troubleshooting

### Common Issues

1. **Browser not found**: Run `playwright install`
2. **API key errors**: Check `.env` file configuration
3. **Import errors**: Ensure all dependencies are installed
4. **Timeout issues**: Adjust timeout settings in configuration
5. **Element not found**: Enable visual mode for debugging

### Performance Optimization

1. **Use headless mode** for production (`fast_automation` config)
2. **Enable caching** for repeated tasks
3. **Disable images** for faster loading
4. **Reduce wait times** between actions
5. **Use batch processing** for multiple similar tasks

## 📚 API Reference

### BrowserAutomationBackend

- `create_task(task_id, description)`: Create new automation task
- `run_task(task_id, schema=None)`: Execute task with optional structured output
- `get_task_status(task_id)`: Get current task status
- `get_task_steps(task_id)`: Get detailed step information
- `save_task_report(task_id, filepath=None)`: Save comprehensive report
- `add_step_callback(callback)`: Add real-time step monitoring

### Configuration Management

- `get_recommended_config(task_description)`: Auto-select optimal config
- `ConfigManager.get_config(name)`: Load configuration by name
- `ConfigManager.create_custom_config()`: Create custom configuration
- `ConfigManager.list_configs()`: List all available configurations

### Schema Management

- `get_schema_for_task(task_description)`: Auto-select appropriate schema
- `create_custom_schema(fields)`: Create custom output schema
- `COMMON_SCHEMAS`: Dictionary of predefined schemas

## 🤝 Contributing

This is a comprehensive automation system designed for flexibility and extensibility. Key areas for enhancement:

1. **Additional Schemas**: New structured output formats
2. **Configuration Templates**: Specialized configs for new use cases
3. **Utility Functions**: Additional helper functions and validators
4. **Error Handlers**: Enhanced error detection and recovery
5. **Performance Optimizations**: Speed and efficiency improvements

## 📄 License

This project builds upon the browser-use library and follows its licensing terms.

## 🙏 Acknowledgments

- Built on top of the excellent [browser-use](https://github.com/browser-use/browser-use) library
- Powered by Google's Gemini AI for intelligent automation
- Uses Playwright for robust browser automation

---

**Ready to automate the web with intelligence and reliability!** 🚀