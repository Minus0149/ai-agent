# VPS Deployment Guide - Browser Automation System

## 🚨 Chrome Installation Issue - RESOLVED

This guide addresses the Docker build error you encountered:
```
failed to solve: process "/bin/sh -c apt-get update && apt-get install -y curl gnupg ca-certificates..."
exit code: 100
```

### Root Cause
The Google Chrome repository (`https://dl.google.com/linux/chrome/deb/`) is returning 404 errors, causing installation failures on VPS environments.

### Solution
We've switched from Google Chrome to **Chromium browser** which is:
- ✅ More reliable on VPS environments
- ✅ Available in standard Ubuntu repositories
- ✅ Fully compatible with Playwright automation
- ✅ Lighter weight and faster to install

## 🚀 Quick VPS Deployment

### Prerequisites
- VPS with Ubuntu 20.04+ (4GB RAM, 10GB disk recommended)
- Docker and Docker Compose installed
- SSH access to your VPS

### Step 1: Install Docker on VPS
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes
exit
```

### Step 2: Upload Project to VPS
```bash
# From your local machine
scp -r . user@your-vps-ip:/home/user/browser-automation/

# SSH into VPS
ssh user@your-vps-ip
cd /home/user/browser-automation/
```

### Step 3: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
# Set your GOOGLE_API_KEY or GEMINI_API_KEY
```

### Step 4: Deploy with VPS Script
```bash
# Make deployment script executable
chmod +x deploy-vps.py

# Deploy to VPS
python3 deploy-vps.py deploy
```

### Step 5: Configure Firewall
```bash
# Allow required ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 8000  # API
sudo ufw allow 5901  # VNC
sudo ufw allow 6080  # Web VNC
sudo ufw --force enable
```

## 🔧 Manual Deployment (Alternative)

If the automated script doesn't work:

```bash
# Build with VPS-optimized configuration
docker-compose -f docker-compose.vps.yml build --no-cache

# Start services
docker-compose -f docker-compose.vps.yml up -d

# Check status
docker-compose -f docker-compose.vps.yml ps

# View logs
docker-compose -f docker-compose.vps.yml logs -f
```

## 📱 Access Your System

Once deployed, access your browser automation system:

- **🌐 Main Dashboard**: `http://YOUR_VPS_IP:80`
- **📚 API Documentation**: `http://YOUR_VPS_IP:8000/api/docs`
- **🖥️ VNC Direct**: `vnc://YOUR_VPS_IP:5901` (password: `automation`)
- **🌍 Web VNC**: `http://YOUR_VPS_IP:6080`

## 🔍 Testing Browser Setup

Test if Chromium is working correctly:

```bash
# Test browser installation
python3 test-browser.py

# Test inside Docker container
docker exec -it browser-automation-backend chromium-browser --version

# Test Playwright
docker exec -it browser-automation-backend python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

## 🛠️ Troubleshooting

### Build Still Failing?

1. **Clean Docker cache**:
   ```bash
   docker system prune -af
   docker volume prune -f
   ```

2. **Check VPS resources**:
   ```bash
   free -h  # Check memory
   df -h    # Check disk space
   ```

3. **Manual Chromium test**:
   ```bash
   # Test if Chromium can be installed
   sudo apt update
   sudo apt install -y chromium-browser
   chromium-browser --version
   ```

### Services Not Starting?

1. **Check logs**:
   ```bash
   docker-compose -f docker-compose.vps.yml logs automation-backend
   docker-compose -f docker-compose.vps.yml logs redis
   ```

2. **Check ports**:
   ```bash
   sudo netstat -tlnp | grep -E ':(80|8000|5901|6080)'
   ```

3. **Restart services**:
   ```bash
   docker-compose -f docker-compose.vps.yml restart
   ```

### Browser Not Working?

1. **Check Chromium in container**:
   ```bash
   docker exec -it browser-automation-backend which chromium-browser
   docker exec -it browser-automation-backend chromium-browser --version
   ```

2. **Test VNC connection**:
   ```bash
   # Install VNC viewer locally and connect to YOUR_VPS_IP:5901
   ```

3. **Check browser arguments**:
   - The system uses `--no-sandbox` for VPS compatibility
   - `--disable-dev-shm-usage` for memory optimization
   - `--disable-gpu` for headless operation

## 🔒 Security Recommendations

### Production Deployment

1. **Change default passwords**:
   ```bash
   # Change VNC password
   docker exec -it browser-automation-backend vncpasswd
   ```

2. **Enable HTTPS**:
   ```bash
   # Deploy with SSL profile
   python3 deploy-vps.py deploy --ssl
   ```

3. **Restrict access**:
   ```bash
   # Allow only specific IPs
   sudo ufw allow from YOUR_IP_ADDRESS to any port 22
   sudo ufw allow from YOUR_IP_ADDRESS to any port 8000
   ```

### Monitoring

```bash
# Monitor resource usage
docker stats

# Monitor logs
docker-compose -f docker-compose.vps.yml logs -f --tail=100

# Health check
python3 deploy-vps.py health
```

## 📊 Performance Optimization

### VPS Resource Limits
The system is configured with:
- **Backend**: 2GB RAM, 1 CPU core
- **Redis**: 512MB RAM, 0.5 CPU core
- **Nginx**: 128MB RAM, 0.25 CPU core

### Scaling Up
For higher loads, modify `docker-compose.vps.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 4G      # Increase memory
      cpus: '2.0'     # Increase CPU
```

## 🆘 Support

If you encounter issues:

1. **Check this guide first** - Most common issues are covered
2. **Run diagnostics**: `python3 deploy-vps.py health`
3. **Check logs**: `docker-compose -f docker-compose.vps.yml logs`
4. **Test browser**: `python3 test-browser.py`

## 📝 Changelog

### v2.1 - VPS Chrome Fix
- ✅ Replaced Google Chrome with Chromium browser
- ✅ Added VPS-specific Docker Compose configuration
- ✅ Created automated VPS deployment script
- ✅ Added comprehensive testing and health checks
- ✅ Optimized for VPS resource constraints
- ✅ Enhanced security and monitoring

---

**🎉 Your browser automation system is now VPS-ready with reliable Chromium browser support!**