from browser_use import Agent, Browser, ChatGoogle
from dotenv import load_dotenv
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from enum import Enum

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class TaskStep:
    step_id: str
    action: str
    timestamp: datetime
    status: TaskStatus
    details: Dict[str, Any]
    duration: Optional[float] = None
    error: Optional[str] = None

@dataclass
class AutomationTask:
    task_id: str
    description: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    steps: List[TaskStep] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []

class BrowserAutomationBackend:
    """Enhanced browser automation backend with performance optimizations and tracking."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = self._load_config(config)
        self.tasks: Dict[str, AutomationTask] = {}
        self.current_task: Optional[AutomationTask] = None
        self.step_callbacks: List[Callable] = []
        self.performance_metrics = {
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'average_task_duration': 0.0
        }
        
    def _load_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Load configuration with defaults for optimal performance."""
        default_config = {
            'browser': {
                'headless': False,
                'window_size': {'width': 1920, 'height': 1080},
                'highlight_elements': True,
                'wait_between_actions': 0.3,  # Faster than default
                'enable_default_extensions': True,
                'disable_images': False,  # Set to True for faster loading
                'disable_javascript': False,
                'user_agent': None,
                'proxy': None
            },
            'llm': {
                'model': 'gemini-2.5-flash',
                'temperature': 0.1,  # More deterministic
                'max_tokens': 4000
            },
            'performance': {
                'max_steps': 50,
                'timeout': 300,  # 5 minutes
                'retry_attempts': 3,
                'parallel_tasks': False
            },
            'tracking': {
                'save_screenshots': True,
                'save_html': False,
                'log_level': 'INFO'
            }
        }
        
        if config:
            # Deep merge configuration
            for key, value in config.items():
                if key in default_config and isinstance(value, dict):
                    default_config[key].update(value)
                else:
                    default_config[key] = value
                    
        return default_config
    
    def add_step_callback(self, callback: Callable[[TaskStep], None]):
        """Add callback to be called after each step."""
        self.step_callbacks.append(callback)
    
    def _create_browser(self) -> Browser:
        """Create optimized browser instance."""
        browser_config = self.config['browser']
        return Browser(
            headless=browser_config['headless'],
            window_size=browser_config['window_size'],
            highlight_elements=browser_config['highlight_elements'],
            wait_between_actions=browser_config['wait_between_actions'],
            enable_default_extensions=browser_config['enable_default_extensions']
        )
    
    def _create_llm(self) -> ChatGoogle:
        """Create LLM instance with optimized settings."""
        llm_config = self.config['llm']
        return ChatGoogle(
            model=llm_config['model'],
            temperature=llm_config.get('temperature', 0.1)
        )
    
    def create_task(self, task_id: str, description: str) -> AutomationTask:
        """Create a new automation task."""
        task = AutomationTask(
            task_id=task_id,
            description=description,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )
        self.tasks[task_id] = task
        logger.info(f"Created task {task_id}: {description}")
        return task
    
    def _track_step(self, action: str, details: Dict[str, Any], status: TaskStatus = TaskStatus.COMPLETED, error: Optional[str] = None):
        """Track a step in the current task."""
        if not self.current_task:
            return
            
        step = TaskStep(
            step_id=f"step_{len(self.current_task.steps) + 1}",
            action=action,
            timestamp=datetime.now(),
            status=status,
            details=details,
            error=error
        )
        
        self.current_task.steps.append(step)
        
        # Call callbacks
        for callback in self.step_callbacks:
            try:
                callback(step)
            except Exception as e:
                logger.error(f"Error in step callback: {e}")
        
        logger.info(f"Step {step.step_id}: {action} - {status.value}")
    
    async def run_task(self, task_id: str, structured_output_schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Run an automation task with comprehensive tracking."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        self.current_task = task
        
        try:
            # Update task status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            
            self._track_step("task_started", {"task_id": task_id, "description": task.description})
            
            # Create browser and LLM
            browser = self._create_browser()
            llm = self._create_llm()
            
            self._track_step("browser_created", {"config": self.config['browser']})
            
            # Create agent with enhanced configuration
            agent_kwargs = {
                'task': task.description,
                'llm': llm,
                'browser': browser,
                'max_steps': self.config['performance']['max_steps']
            }
            
            if structured_output_schema:
                agent_kwargs['structured_output'] = structured_output_schema
            
            agent = Agent(**agent_kwargs)
            
            self._track_step("agent_created", {"max_steps": self.config['performance']['max_steps']})
            
            # Run the agent with timeout
            start_time = time.time()
            
            try:
                result = await asyncio.wait_for(
                    agent.run(),
                    timeout=self.config['performance']['timeout']
                )
                
                duration = time.time() - start_time
                
                # Update task completion
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.result = result if isinstance(result, dict) else {"output": str(result)}
                
                self._track_step("task_completed", {
                    "duration": duration,
                    "result_type": type(result).__name__
                })
                
                # Update performance metrics
                self.performance_metrics['total_tasks'] += 1
                self.performance_metrics['successful_tasks'] += 1
                self._update_average_duration(duration)
                
                logger.info(f"Task {task_id} completed successfully in {duration:.2f}s")
                
                return {
                    "task_id": task_id,
                    "status": "completed",
                    "result": task.result,
                    "duration": duration,
                    "steps_count": len(task.steps)
                }
                
            except asyncio.TimeoutError:
                error_msg = f"Task {task_id} timed out after {self.config['performance']['timeout']}s"
                task.status = TaskStatus.FAILED
                task.error = error_msg
                self._track_step("task_timeout", {"timeout": self.config['performance']['timeout']}, TaskStatus.FAILED, error_msg)
                raise TimeoutError(error_msg)
                
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            error_msg = str(e)
            
            task.status = TaskStatus.FAILED
            task.error = error_msg
            task.completed_at = datetime.now()
            
            self._track_step("task_failed", {"error": error_msg, "duration": duration}, TaskStatus.FAILED, error_msg)
            
            # Update performance metrics
            self.performance_metrics['total_tasks'] += 1
            self.performance_metrics['failed_tasks'] += 1
            
            logger.error(f"Task {task_id} failed: {error_msg}")
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": error_msg,
                "duration": duration,
                "steps_count": len(task.steps)
            }
        
        finally:
            self.current_task = None
    
    def _update_average_duration(self, duration: float):
        """Update average task duration metric."""
        total_successful = self.performance_metrics['successful_tasks']
        current_avg = self.performance_metrics['average_task_duration']
        
        if total_successful == 1:
            self.performance_metrics['average_task_duration'] = duration
        else:
            # Calculate running average
            self.performance_metrics['average_task_duration'] = (
                (current_avg * (total_successful - 1) + duration) / total_successful
            )
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get detailed status of a task."""
        if task_id not in self.tasks:
            return {"error": f"Task {task_id} not found"}
        
        task = self.tasks[task_id]
        return {
            "task_id": task_id,
            "status": task.status.value,
            "description": task.description,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "steps_count": len(task.steps),
            "result": task.result,
            "error": task.error
        }
    
    def get_task_steps(self, task_id: str) -> List[Dict[str, Any]]:
        """Get detailed steps of a task."""
        if task_id not in self.tasks:
            return []
        
        task = self.tasks[task_id]
        return [{
            "step_id": step.step_id,
            "action": step.action,
            "timestamp": step.timestamp.isoformat(),
            "status": step.status.value,
            "details": step.details,
            "duration": step.duration,
            "error": step.error
        } for step in task.steps]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.performance_metrics.copy()
    
    def save_task_report(self, task_id: str, filepath: Optional[str] = None) -> str:
        """Save detailed task report to file."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        
        if not filepath:
            filepath = f"task_report_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "task": asdict(task),
            "steps": [asdict(step) for step in task.steps],
            "performance_metrics": self.performance_metrics
        }
        
        # Convert datetime objects to strings for JSON serialization
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            return obj
        
        report = convert_datetime(report)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Task report saved to {filepath}")
        return filepath

# Example usage and demonstration
async def main():
    """Demonstration of the enhanced automation backend."""
    
    # Create backend with custom configuration
    config = {
        'browser': {
            'headless': False,
            'window_size': {'width': 1920, 'height': 1080},
            'wait_between_actions': 0.2  # Faster execution
        },
        'performance': {
            'max_steps': 30,
            'timeout': 180  # 3 minutes
        }
    }
    
    backend = BrowserAutomationBackend(config)
    
    # Add step callback for real-time monitoring
    def step_monitor(step: TaskStep):
        print(f"[{step.timestamp.strftime('%H:%M:%S')}] {step.action}: {step.status.value}")
        if step.error:
            print(f"  Error: {step.error}")
    
    backend.add_step_callback(step_monitor)
    
    # Create and run the original task
    task_id = "leonardo_login_task"
    task_description = "Navigate to leonardo.ai and login using a temp mail from temp-mail.io"
    
    backend.create_task(task_id, task_description)
    
    print(f"Starting task: {task_description}")
    print("=" * 60)
    
    try:
        result = await backend.run_task(task_id)
        
        print("\n" + "=" * 60)
        print("TASK COMPLETED")
        print(f"Status: {result['status']}")
        print(f"Duration: {result['duration']:.2f}s")
        print(f"Steps: {result['steps_count']}")
        
        if result['status'] == 'completed':
            print(f"Result: {result['result']}")
        else:
            print(f"Error: {result['error']}")
        
        # Save detailed report
        report_file = backend.save_task_report(task_id)
        print(f"\nDetailed report saved to: {report_file}")
        
        # Show performance metrics
        metrics = backend.get_performance_metrics()
        print(f"\nPerformance Metrics:")
        print(f"  Total tasks: {metrics['total_tasks']}")
        print(f"  Successful: {metrics['successful_tasks']}")
        print(f"  Failed: {metrics['failed_tasks']}")
        print(f"  Average duration: {metrics['average_task_duration']:.2f}s")
        
    except Exception as e:
        print(f"\nTask execution failed: {e}")
        
        # Still save report for debugging
        try:
            report_file = backend.save_task_report(task_id)
            print(f"Debug report saved to: {report_file}")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())