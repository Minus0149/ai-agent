#!/usr/bin/env python3
"""VPS-specific deployment script for Browser Automation System."""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

class VPSDeployer:
    """Handles VPS-specific deployment of the browser automation system."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.docker_compose_file = self.project_root / "docker-compose.yml"
        self.env_file = self.project_root / ".env"
        self.env_example = self.project_root / ".env.example"
        
    def check_vps_requirements(self) -> bool:
        """Check VPS-specific requirements."""
        print("🔍 Checking VPS requirements...")
        
        # Check available memory
        try:
            result = subprocess.run(["free", "-m"], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                mem_line = lines[1].split()
                total_mem = int(mem_line[1])
                if total_mem < 2048:
                    print(f"⚠️  Warning: Low memory detected ({total_mem}MB). Recommended: 2GB+")
                else:
                    print(f"✅ Memory: {total_mem}MB")
        except Exception:
            print("⚠️  Could not check memory")
        
        # Check disk space
        try:
            result = subprocess.run(["df", "-h", "."], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                disk_line = lines[1].split()
                available = disk_line[3]
                print(f"✅ Disk space available: {available}")
        except Exception:
            print("⚠️  Could not check disk space")
        
        return True
    
    def setup_environment(self) -> bool:
        """Set up environment configuration for VPS."""
        print("🔧 Setting up VPS environment...")
        
        if not self.env_file.exists():
            if self.env_example.exists():
                # Copy and modify for VPS
                with open(self.env_example, 'r') as f:
                    content = f.read()
                
                # VPS-specific modifications
                content = content.replace(
                    "GOOGLE_API_KEY=your_google_api_key_here",
                    "GOOGLE_API_KEY=AIzaSyDummy_Key_Replace_With_Your_Actual_Key"
                )
                content += "\n# VPS-specific settings\n"
                content += "DOCKER_BUILDKIT=1\n"
                content += "COMPOSE_DOCKER_CLI_BUILD=1\n"
                
                with open(self.env_file, 'w') as f:
                    f.write(content)
                
                print(f"📋 Created VPS-optimized .env file")
                print("⚠️  Please edit .env file with your actual API keys")
                return True
            else:
                print("❌ No .env.example file found")
                return False
        
        print("✅ Environment file exists")
        return True
    
    def build_with_retry(self, max_retries: int = 3) -> bool:
        """Build Docker images with retry logic for VPS."""
        print(f"🏗️  Building Docker images (max {max_retries} retries)...")
        
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1}/{max_retries}")
                
                # Use BuildKit for better caching and performance
                env = os.environ.copy()
                env['DOCKER_BUILDKIT'] = '1'
                env['COMPOSE_DOCKER_CLI_BUILD'] = '1'
                
                result = subprocess.run(
                    ["docker-compose", "build", "--no-cache", "automation-backend"],
                    cwd=self.project_root,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1 hour timeout
                )
                
                if result.returncode == 0:
                    print("✅ Docker images built successfully")
                    return True
                else:
                    print(f"❌ Build attempt {attempt + 1} failed:")
                    print(result.stderr[-1000:])  # Show last 1000 chars of error
                    
                    if attempt < max_retries - 1:
                        print(f"Retrying in 30 seconds...")
                        time.sleep(30)
                    
            except subprocess.TimeoutExpired:
                print(f"❌ Build attempt {attempt + 1} timed out")
                if attempt < max_retries - 1:
                    print(f"Retrying in 30 seconds...")
                    time.sleep(30)
            except Exception as e:
                print(f"❌ Build attempt {attempt + 1} error: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in 30 seconds...")
                    time.sleep(30)
        
        print("❌ All build attempts failed")
        return False
    
    def start_services_vps(self) -> bool:
        """Start services with VPS-specific settings."""
        print("🚀 Starting services on VPS...")
        
        try:
            # Start with limited resources
            result = subprocess.run(
                ["docker-compose", "up", "-d", "--remove-orphans"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Failed to start services: {result.stderr}")
                return False
            
            print("✅ Services started successfully")
            
            # Wait for services to be ready
            print("⏳ Waiting for services to initialize...")
            time.sleep(30)
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting services: {e}")
            return False
    
    def health_check_vps(self) -> bool:
        """Perform VPS-specific health check."""
        print("🏥 Performing VPS health check...")
        
        services = {
            "Redis": ("docker", "exec", "automation-redis", "redis-cli", "ping"),
            "Backend": ("curl", "-f", "http://localhost:8000/health"),
        }
        
        all_healthy = True
        
        for service, cmd in services.items():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"   ✅ {service}: Healthy")
                else:
                    print(f"   ❌ {service}: Unhealthy")
                    all_healthy = False
            except Exception as e:
                print(f"   ❌ {service}: Error - {str(e)[:50]}")
                all_healthy = False
        
        return all_healthy
    
    def deploy_vps(self) -> bool:
        """Full VPS deployment process."""
        print("🚀 Starting VPS Browser Automation System Deployment")
        print("=" * 60)
        
        # Check VPS requirements
        if not self.check_vps_requirements():
            return False
        
        # Setup environment
        if not self.setup_environment():
            return False
        
        # Build with retry
        if not self.build_with_retry():
            print("\n💡 Build failed. Troubleshooting tips:")
            print("   1. Check if you have enough disk space (need ~5GB)")
            print("   2. Check if you have enough memory (need ~2GB)")
            print("   3. Try: docker system prune -a")
            print("   4. Check VPS network connectivity")
            return False
        
        # Start services
        if not self.start_services_vps():
            return False
        
        # Health check
        if not self.health_check_vps():
            print("⚠️  Some services may not be fully ready yet")
        
        print("\n" + "=" * 60)
        print("🎉 VPS Deployment completed!")
        print("\n📱 Access URLs:")
        print("   - Dashboard: http://YOUR_VPS_IP:80")
        print("   - API Docs: http://YOUR_VPS_IP:8000/api/docs")
        print("   - VNC: vnc://YOUR_VPS_IP:5901 (password: automation)")
        print("   - Web VNC: http://YOUR_VPS_IP:6080")
        
        print("\n🔒 Security Notes:")
        print("   - Configure firewall to allow ports 80, 8000, 5901, 6080")
        print("   - Consider using HTTPS in production")
        print("   - Change default VNC password")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="VPS Browser Automation System Deployment")
    parser.add_argument("--retry", type=int, default=3, help="Number of build retries")
    
    args = parser.parse_args()
    
    deployer = VPSDeployer()
    success = deployer.deploy_vps()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()