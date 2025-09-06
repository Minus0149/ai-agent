"""Example usage of the enhanced browser automation system."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Import our enhanced automation components
from agents import BrowserAutomationBackend, TaskStep
from automation_schemas import get_schema_for_task, LoginResult, COMMON_SCHEMAS
from automation_configs import get_recommended_config, ConfigManager
from automation_utils import (
    RetryConfig, RetryStrategy, retry_async, monitor_performance,
    task_cache, validation_utils, human_behavior, error_analyzer,
    generate_temp_email, format_duration
)

class AutomationExamples:
    """Collection of automation examples and demonstrations."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.results = []
    
    async def run_leonardo_login_example(self):
        """Enhanced version of the original Leonardo.ai login task."""
        print("\n" + "=" * 80)
        print("LEONARDO.AI LOGIN AUTOMATION EXAMPLE")
        print("=" * 80)
        
        # Get optimized configuration for this task
        task_description = "Navigate to leonardo.ai and login using a temp mail from temp-mail.io"
        config = get_recommended_config(task_description)
        
        # Get appropriate schema for login automation
        schema = get_schema_for_task(task_description)
        
        # Create backend with optimized config
        backend = BrowserAutomationBackend(config)
        
        # Add monitoring callback
        def step_monitor(step: TaskStep):
            timestamp = step.timestamp.strftime('%H:%M:%S')
            print(f"[{timestamp}] {step.action}: {step.status.value}")
            if step.error:
                print(f"  ❌ Error: {step.error}")
                print(f"  💡 Suggestion: {error_analyzer.suggest_solution(step.error)}")
            elif step.status.value == 'completed':
                print(f"  ✅ Success")
        
        backend.add_step_callback(step_monitor)
        
        # Create and run task
        task_id = "leonardo_login_enhanced"
        backend.create_task(task_id, task_description)
        
        print(f"Task: {task_description}")
        print(f"Config: {config['name']} - {config['description']}")
        print(f"Schema: Login automation with structured output")
        print("-" * 80)
        
        try:
            # Check cache first
            cached_result = task_cache.get(task_description, config)
            if cached_result:
                print("📋 Using cached result")
                return cached_result
            
            # Run the task with structured output
            result = await backend.run_task(task_id, schema)
            
            # Cache the result
            task_cache.set(task_description, config, result)
            
            # Display results
            print("\n" + "-" * 80)
            print("TASK RESULTS")
            print("-" * 80)
            print(f"Status: {result['status']}")
            print(f"Duration: {format_duration(result['duration'])}")
            print(f"Steps: {result['steps_count']}")
            
            if result['status'] == 'completed' and result.get('result'):
                # Try to parse as LoginResult
                try:
                    login_result = LoginResult.model_validate(result['result'])
                    print(f"\n📧 Login Details:")
                    print(f"  Success: {'✅' if login_result.success else '❌'}")
                    if login_result.temp_email:
                        print(f"  Temp Email: {login_result.temp_email}")
                    if login_result.username:
                        print(f"  Username: {login_result.username}")
                    print(f"  Login URL: {login_result.login_url}")
                    if login_result.error_message:
                        print(f"  Error: {login_result.error_message}")
                except Exception as e:
                    print(f"Raw result: {json.dumps(result['result'], indent=2)}")
            
            # Save detailed report
            report_file = backend.save_task_report(task_id)
            print(f"\n📄 Detailed report: {report_file}")
            
            # Show performance metrics
            metrics = backend.get_performance_metrics()
            print(f"\n📊 Performance Metrics:")
            print(f"  Success Rate: {metrics['successful_tasks']}/{metrics['total_tasks']}")
            print(f"  Average Duration: {format_duration(metrics['average_task_duration'])}")
            
            self.results.append({
                'task': 'leonardo_login',
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            print(f"\n❌ Task failed: {e}")
            print(f"💡 Suggestion: {error_analyzer.suggest_solution(str(e))}")
            return {'status': 'failed', 'error': str(e)}
    
    async def run_web_search_example(self):
        """Example of web search automation."""
        print("\n" + "=" * 80)
        print("WEB SEARCH AUTOMATION EXAMPLE")
        print("=" * 80)
        
        task_description = "Search Google for 'browser automation tools' and extract top 5 results with titles and URLs"
        config = get_recommended_config(task_description)
        schema = get_schema_for_task(task_description)
        
        backend = BrowserAutomationBackend(config)
        
        # Add performance monitoring
        @monitor_performance
        async def monitored_task():
            task_id = "web_search_demo"
            backend.create_task(task_id, task_description)
            return await backend.run_task(task_id, schema)
        
        print(f"Task: {task_description}")
        print("-" * 80)
        
        try:
            result = await monitored_task()
            
            print(f"\n✅ Search completed in {format_duration(result['duration'])}")
            if result.get('result'):
                print(f"Results: {json.dumps(result['result'], indent=2)}")
            
            self.results.append({
                'task': 'web_search',
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def run_form_filling_example(self):
        """Example of form filling automation."""
        print("\n" + "=" * 80)
        print("FORM FILLING AUTOMATION EXAMPLE")
        print("=" * 80)
        
        task_description = "Fill out a contact form on a demo website with sample data"
        config = get_recommended_config(task_description)
        
        # Customize config for form filling
        config['browser']['wait_between_actions'] = 1.0  # Slower for form filling
        config['custom_settings'] = {
            'form_data': {
                'name': 'John Doe',
                'email': generate_temp_email(),
                'message': 'This is a test message from automation system'
            }
        }
        
        schema = get_schema_for_task(task_description)
        backend = BrowserAutomationBackend(config)
        
        print(f"Task: {task_description}")
        print(f"Generated email: {config['custom_settings']['form_data']['email']}")
        print("-" * 80)
        
        try:
            task_id = "form_filling_demo"
            backend.create_task(task_id, task_description)
            result = await backend.run_task(task_id, schema)
            
            print(f"\n✅ Form filling completed in {format_duration(result['duration'])}")
            
            self.results.append({
                'task': 'form_filling',
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            print(f"❌ Form filling failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def run_data_extraction_example(self):
        """Example of data extraction automation."""
        print("\n" + "=" * 80)
        print("DATA EXTRACTION AUTOMATION EXAMPLE")
        print("=" * 80)
        
        task_description = "Extract product information from an e-commerce website including names, prices, and ratings"
        config = get_recommended_config(task_description)
        schema = get_schema_for_task(task_description)
        
        backend = BrowserAutomationBackend(config)
        
        print(f"Task: {task_description}")
        print("-" * 80)
        
        try:
            task_id = "data_extraction_demo"
            backend.create_task(task_id, task_description)
            result = await backend.run_task(task_id, schema)
            
            print(f"\n✅ Data extraction completed in {format_duration(result['duration'])}")
            
            self.results.append({
                'task': 'data_extraction',
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            print(f"❌ Data extraction failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def run_batch_automation_example(self):
        """Example of running multiple automation tasks in sequence."""
        print("\n" + "=" * 80)
        print("BATCH AUTOMATION EXAMPLE")
        print("=" * 80)
        
        tasks = [
            "Navigate to google.com and search for 'Python automation'",
            "Visit github.com and search for 'browser-use' repositories",
            "Go to stackoverflow.com and search for 'web scraping' questions"
        ]
        
        # Use fast automation config for batch processing
        config = self.config_manager.get_config('fast_automation')
        backend = BrowserAutomationBackend(config)
        
        batch_results = []
        
        for i, task_desc in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] {task_desc}")
            print("-" * 40)
            
            try:
                task_id = f"batch_task_{i}"
                backend.create_task(task_id, task_desc)
                
                # Add retry logic for batch processing
                retry_config = RetryConfig(
                    max_attempts=2,
                    strategy=RetryStrategy.LINEAR,
                    base_delay=1.0
                )
                
                @retry_async(retry_config)
                async def run_with_retry():
                    return await backend.run_task(task_id)
                
                result = await run_with_retry()
                batch_results.append(result)
                
                print(f"✅ Completed in {format_duration(result['duration'])}")
                
            except Exception as e:
                print(f"❌ Failed: {e}")
                batch_results.append({'status': 'failed', 'error': str(e)})
        
        # Summary
        successful = sum(1 for r in batch_results if r.get('status') == 'completed')
        total_time = sum(r.get('duration', 0) for r in batch_results)
        
        print(f"\n📊 Batch Summary:")
        print(f"  Success Rate: {successful}/{len(tasks)}")
        print(f"  Total Time: {format_duration(total_time)}")
        print(f"  Average Time: {format_duration(total_time / len(tasks))}")
        
        self.results.append({
            'task': 'batch_automation',
            'results': batch_results,
            'timestamp': datetime.now().isoformat()
        })
        
        return batch_results
    
    def save_all_results(self, filename: str = None):
        """Save all example results to file."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"automation_examples_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 All results saved to: {filename}")
        return filename
    
    def print_performance_summary(self):
        """Print overall performance summary."""
        from automation_utils import performance_monitor
        
        print("\n" + "=" * 80)
        print("PERFORMANCE SUMMARY")
        print("=" * 80)
        
        stats = performance_monitor.get_stats()
        
        if stats:
            for func_name, func_stats in stats.items():
                print(f"\n📈 {func_name}:")
                print(f"  Calls: {func_stats['total_calls']}")
                print(f"  Success Rate: {func_stats['success_rate']:.1%}")
                print(f"  Avg Time: {format_duration(func_stats['avg_execution_time'])}")
                print(f"  Min Time: {format_duration(func_stats['min_execution_time'])}")
                print(f"  Max Time: {format_duration(func_stats['max_execution_time'])}")
        else:
            print("No performance data available")

async def main():
    """Run all automation examples."""
    print("🤖 ENHANCED BROWSER AUTOMATION SYSTEM DEMO")
    print("=" * 80)
    print("This demo showcases the comprehensive automation capabilities")
    print("including performance monitoring, caching, error handling, and more.")
    
    examples = AutomationExamples()
    
    # Clear expired cache entries
    task_cache.clear_expired()
    
    try:
        # Run the original Leonardo.ai example (enhanced)
        await examples.run_leonardo_login_example()
        
        # Run additional examples
        await examples.run_web_search_example()
        await examples.run_form_filling_example()
        await examples.run_data_extraction_example()
        await examples.run_batch_automation_example()
        
        # Save results and show summary
        results_file = examples.save_all_results()
        examples.print_performance_summary()
        
        print("\n" + "=" * 80)
        print("🎉 ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"📄 Results saved to: {results_file}")
        print("\n💡 Key Features Demonstrated:")
        print("  ✅ Structured output schemas")
        print("  ✅ Automatic configuration optimization")
        print("  ✅ Performance monitoring and caching")
        print("  ✅ Error handling and retry mechanisms")
        print("  ✅ Step-by-step tracking")
        print("  ✅ Batch processing capabilities")
        print("  ✅ Human behavior simulation")
        print("  ✅ Comprehensive logging and reporting")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print(f"💡 Suggestion: {error_analyzer.suggest_solution(str(e))}")

if __name__ == "__main__":
    asyncio.run(main())