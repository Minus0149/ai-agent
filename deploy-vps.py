#!/usr/bin/env python3
"""VPS-specific deployment script for Browser Automation System."""

import os
import sys
import subprocess
import argparse
import shutil
import time
from pathlib import Path
import json
from typing import List, Dict, Any

class VPSAutomationDeployer:
    """Handles VPS-specific deployment of the browser automation system."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.docker_compose_file = self.project_root / "docker-compose.vps.yml"
        self.env_file = self.project_root / ".env"
        self.env_example = self.project_root / ".env.example"
        
    def check_vps_prerequisites(self) -> bool:
        """Check VPS-specific prerequisites."""
        print("🔍 Checking VPS prerequisites...")
        
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
            print("\n📋 Install Docker on your VPS:")
            print("   curl -fsSL https://get.docker.com -o get-docker.sh")
            print("   sudo sh get-docker.sh")
            print("   sudo usermod -aG docker $USER")
            return False
        
        print("✅ VPS prerequisites checked")
        return True
    
    def build_vps_images(self) -> bool:
        """Build Docker images with VPS-specific optimizations."""
        print("🏗️  Building VPS-optimized Docker images...")
        
        try:
            cmd = ["docker-compose", "-f", str(self.docker_compose_file), "build", "--no-cache"]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Build failed: {result.stderr}")
                print("\n🔧 Troubleshooting tips:")
                print("   - Check internet connectivity")
                print("   - Ensure sufficient disk space (10GB+)")
                print("   - Try: docker system prune -f")
                return False
            
            print("✅ VPS-optimized Docker images built successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error building images: {e}")
            return False
    
    def start_vps_services(self, profiles: List[str] = None) -> bool:
        """Start Docker services with VPS-specific configuration."""
        profiles = profiles or []
        
        print(f"🚀 Starting VPS services{' with profiles: ' + ', '.join(profiles) if profiles else ''}...")
        
        try:
            cmd = ["docker-compose", "-f", str(self.docker_compose_file), "up", "-d"]
            
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
            
            print("✅ VPS services started successfully")
            
            # Wait for services to be ready
            print("⏳ Waiting for services to initialize...")
            time.sleep(30)
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting services: {e}")
            return False
    
    def vps_health_check(self) -> Dict[str, Any]:
        """Perform VPS-specific health check."""
        print("🏥 Performing VPS health check...")
        
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
                    response = requests.get(endpoint, timeout=10)
                    results[service] = "✅ Healthy" if response.status_code == 200 else "❌ Unhealthy"
                elif service == "VNC Server":
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex(('localhost', 5901))
                    sock.close()
                    results[service] = "✅ Healthy" if result == 0 else "❌ Unhealthy"
                elif service == "Redis":
                    import redis
                    r = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_timeout=5)
                    r.ping()
                    results[service] = "✅ Healthy"
            except Exception as e:
                results[service] = f"❌ Error: {str(e)[:50]}"
        
        for service, status in results.items():
            print(f"   {service}: {status}")
        
        return results
    
    def deploy_to_vps(self, profiles: List[str] = None, build: bool = True) -> bool:
        """Full VPS deployment process."""
        print("🚀 Starting VPS Browser Automation System Deployment")
        print("=" * 60)
        
        # Check VPS prerequisites
        if not self.check_vps_prerequisites():
            return False
        
        # Setup environment
        if not self.env_file.exists():
            if self.env_example.exists():
                shutil.copy(self.env_example, self.env_file)
                print(f"📋 Created .env file from template")
                print("⚠️  Please edit .env file with your API keys before continuing")
                return False
        
        # Build images if requested
        if build and not self.build_vps_images():
            return False
        
        # Start services
        if not self.start_vps_services(profiles):
            return False
        
        # Perform health check
        self.vps_health_check()
        
        print("\n" + "=" * 60)
        print("🎉 VPS Deployment completed successfully!")
        print("\n📱 Access URLs:")
        print("   - Dashboard: http://YOUR_VPS_IP:80")
        print("   - API Docs: http://YOUR_VPS_IP:8000/api/docs")
        print("   - VNC Viewer: vnc://YOUR_VPS_IP:5901 (password: automation)")
        print("   - Web VNC: http://YOUR_VPS_IP:6080")
        
        print("\n💡 VPS Management Tips:")
        print("   - Monitor resources: docker stats")
        print("   - View logs: docker-compose -f docker-compose.vps.yml logs -f")
        print("   - Update system: docker-compose -f docker-compose.vps.yml pull")
        print("   - Backup data: tar -czf backup.tar.gz logs cache configs reports")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="VPS Browser Automation System Deployment")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy to VPS")
    deploy_parser.add_argument("--no-build", action="store_true", help="Skip building images")
    
    # Other commands
    subparsers.add_parser("health", help="Perform health check")
    
    args = parser.parse_args()
    
    deployer = VPSAutomationDeployer()
    
    if args.command == "deploy" or args.command is None:
        build = not (args.command == "deploy" and args.no_build)
        success = deployer.deploy_to_vps([], build)
        sys.exit(0 if success else 1)
    
    elif args.command == "health":
        deployer.vps_health_check()
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()