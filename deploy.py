#!/usr/bin/env python3
"""Deployment script for Browser Automation System."""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
import json
from typing import List, Dict, Any

class AutomationDeployer:
    """Handles deployment of the browser automation system."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.docker_compose_file = self.project_root / "docker-compose.yml"
        self.env_file = self.project_root / ".env"
        self.env_example = self.project_root / ".env.example"
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed."""
        print("🔍 Checking prerequisites...")
        
        required_commands = [
            ("docker", "Docker is required for containerized deployment"),
            ("docker-compose", "Docker Compose is required for orchestration")
        ]
        
        missing = []
        for cmd, description in required_commands:
            if not shutil.which(cmd):
                missing.append((cmd, description))
        
        if missing:
            print("❌ Missing prerequisites:")
            for cmd, desc in missing:
                print(f"   - {cmd}: {desc}")
            return False
        
        print("✅ All prerequisites found")
        return True
    
    def setup_environment(self) -> bool:
        """Set up environment configuration."""
        print("🔧 Setting up environment...")
        
        if not self.env_file.exists():
            if self.env_example.exists():
                shutil.copy(self.env_example, self.env_file)
                print(f"📋 Created .env file from template")
                print("⚠️  Please edit .env file with your API keys before continuing")
                return False
            else:
                print("❌ No .env.example file found")
                return False
        
        # Check if required API keys are set
        required_keys = ["GEMINI_API_KEY"]
        missing_keys = []
        
        try:
            with open(self.env_file, 'r') as f:
                env_content = f.read()
                
            for key in required_keys:
                if f"{key}=your_" in env_content or f"{key}=" in env_content.replace(f"{key}=", f"{key}=\n"):
                    missing_keys.append(key)
            
            if missing_keys:
                print("❌ Missing required API keys in .env file:")
                for key in missing_keys:
                    print(f"   - {key}")
                print("Please update your .env file with valid API keys")
                return False
                
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
            return False
        
        print("✅ Environment configuration ready")
        return True
    
    def build_images(self) -> bool:
        """Build Docker images."""
        print("🏗️  Building Docker images...")
        
        try:
            result = subprocess.run(
                ["docker-compose", "build", "--no-cache"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Build failed: {result.stderr}")
                return False
            
            print("✅ Docker images built successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error building images: {e}")
            return False
    
    def start_services(self, profiles: List[str] = None) -> bool:
        """Start Docker services."""
        profiles = profiles or []
        
        print(f"🚀 Starting services{' with profiles: ' + ', '.join(profiles) if profiles else ''}...")
        
        try:
            cmd = ["docker-compose", "up", "-d"]
            
            for profile in profiles:
                cmd.extend(["--profile", profile])
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Failed to start services: {result.stderr}")
                return False
            
            print("✅ Services started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error starting services: {e}")
            return False
    
    def stop_services(self) -> bool:
        """Stop Docker services."""
        print("🛑 Stopping services...")
        
        try:
            result = subprocess.run(
                ["docker-compose", "down"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Failed to stop services: {result.stderr}")
                return False
            
            print("✅ Services stopped successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping services: {e}")
            return False
    
    def show_status(self) -> None:
        """Show service status."""
        print("📊 Service Status:")
        
        try:
            result = subprocess.run(
                ["docker-compose", "ps"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
    
    def show_logs(self, service: str = None, follow: bool = False) -> None:
        """Show service logs."""
        print(f"📋 Logs{' for ' + service if service else ''}:")
        
        try:
            cmd = ["docker-compose", "logs"]
            
            if follow:
                cmd.append("-f")
            
            if service:
                cmd.append(service)
            
            subprocess.run(cmd, cwd=self.project_root)
            
        except Exception as e:
            print(f"❌ Error getting logs: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on services."""
        print("🏥 Performing health check...")
        
        services = {
            "FastAPI Backend": "http://localhost:8000/health",
            "VNC Server": "localhost:5901",
            "Redis": "localhost:6379"
        }
        
        results = {}
        
        for service, endpoint in services.items():
            try:
                if service == "FastAPI Backend":
                    import requests
                    response = requests.get(endpoint, timeout=5)
                    results[service] = "✅ Healthy" if response.status_code == 200 else "❌ Unhealthy"
                elif service == "VNC Server":
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(('localhost', 5901))
                    sock.close()
                    results[service] = "✅ Healthy" if result == 0 else "❌ Unhealthy"
                elif service == "Redis":
                    import redis
                    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
                    r.ping()
                    results[service] = "✅ Healthy"
            except Exception as e:
                results[service] = f"❌ Error: {str(e)[:50]}"
        
        for service, status in results.items():
            print(f"   {service}: {status}")
        
        return results
    
    def cleanup(self) -> bool:
        """Clean up Docker resources."""
        print("🧹 Cleaning up Docker resources...")
        
        try:
            # Stop and remove containers
            subprocess.run(["docker-compose", "down", "-v"], cwd=self.project_root)
            
            # Remove images
            result = subprocess.run(
                ["docker", "images", "-q", "browser-automation*"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                subprocess.run(["docker", "rmi"] + result.stdout.strip().split())
            
            print("✅ Cleanup completed")
            return True
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return False
    
    def deploy(self, profiles: List[str] = None, build: bool = True) -> bool:
        """Full deployment process."""
        print("🚀 Starting Browser Automation System Deployment")
        print("=" * 50)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Setup environment
        if not self.setup_environment():
            return False
        
        # Build images if requested
        if build and not self.build_images():
            return False
        
        # Start services
        if not self.start_services(profiles):
            return False
        
        # Wait a moment for services to start
        print("⏳ Waiting for services to initialize...")
        import time
        time.sleep(10)
        
        # Show status
        self.show_status()
        
        # Perform health check
        self.health_check()
        
        print("\n" + "=" * 50)
        print("🎉 Deployment completed successfully!")
        print("\n📱 Access URLs:")
        print("   - Dashboard: http://localhost:80")
        print("   - API Docs: http://localhost:8000/api/docs")
        print("   - VNC Viewer: vnc://localhost:5901 (password: automation)")
        print("   - Web VNC: http://localhost:6080")
        
        if "monitoring" in (profiles or []):
            print("   - Grafana: http://localhost:3000 (admin/admin123)")
            print("   - Prometheus: http://localhost:9090")
        
        print("\n💡 Tips:")
        print("   - Use 'python deploy.py logs -f' to follow logs")
        print("   - Use 'python deploy.py stop' to stop services")
        print("   - Use 'python deploy.py health' for health check")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="Browser Automation System Deployment")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy the system")
    deploy_parser.add_argument("--no-build", action="store_true", help="Skip building images")
    deploy_parser.add_argument("--monitoring", action="store_true", help="Enable monitoring stack")
    deploy_parser.add_argument("--database", action="store_true", help="Enable database")
    
    # Other commands
    subparsers.add_parser("start", help="Start services")
    subparsers.add_parser("stop", help="Stop services")
    subparsers.add_parser("restart", help="Restart services")
    subparsers.add_parser("status", help="Show service status")
    subparsers.add_parser("health", help="Perform health check")
    subparsers.add_parser("cleanup", help="Clean up Docker resources")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Show logs")
    logs_parser.add_argument("service", nargs="?", help="Service name")
    logs_parser.add_argument("-f", "--follow", action="store_true", help="Follow logs")
    
    args = parser.parse_args()
    
    deployer = AutomationDeployer()
    
    if args.command == "deploy" or args.command is None:
        profiles = []
        if args.command == "deploy":
            if args.monitoring:
                profiles.append("monitoring")
            if args.database:
                profiles.append("database")
            build = not args.no_build
        else:
            build = True
        
        success = deployer.deploy(profiles, build)
        sys.exit(0 if success else 1)
    
    elif args.command == "start":
        success = deployer.start_services()
        sys.exit(0 if success else 1)
    
    elif args.command == "stop":
        success = deployer.stop_services()
        sys.exit(0 if success else 1)
    
    elif args.command == "restart":
        deployer.stop_services()
        success = deployer.start_services()
        sys.exit(0 if success else 1)
    
    elif args.command == "status":
        deployer.show_status()
    
    elif args.command == "health":
        deployer.health_check()
    
    elif args.command == "logs":
        deployer.show_logs(args.service, args.follow)
    
    elif args.command == "cleanup":
        success = deployer.cleanup()
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()