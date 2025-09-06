# Multi-stage Docker build for Browser Automation System with VNC
FROM python:3.13-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # VNC and X11 dependencies
    tightvncserver \
    xvfb \
    fluxbox \
    x11vnc \
    xterm \
    # Browser dependencies
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    # Additional utilities
    curl \
    git \
    supervisor \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium browser (reliable alternative to Chrome)
RUN apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && chromium-browser --version \
    && echo "Chromium browser installed successfully"

# Create application user
RUN useradd -m -s /bin/bash automation && \
    mkdir -p /home/automation/.vnc && \
    chown -R automation:automation /home/automation

# Set up VNC
USER automation
WORKDIR /home/automation

# Set VNC password
RUN echo "automation" | vncpasswd -f > /home/automation/.vnc/passwd && \
    chmod 600 /home/automation/.vnc/passwd

# Create VNC startup script
RUN echo '#!/bin/bash\n\
xrdb $HOME/.Xresources\n\
xsetroot -solid grey\n\
fluxbox &\n\
x11vnc -forever -usepw -create -display :1 -rfbport 5901 &\n\
exec /bin/bash' > /home/automation/.vnc/xstartup && \
    chmod +x /home/automation/.vnc/xstartup

# Switch back to root for Python setup
USER root

# Install additional system dependencies
RUN apt-get update && apt-get install -y \
    redis-server \
    websockify \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN pip install uv

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY docker-requirements.txt .

# Install Python dependencies with uv
RUN uv pip install --system -r docker-requirements.txt

# Install Playwright browsers (using system Chromium)
RUN playwright install-deps chromium && \
    echo "Using system Chromium browser" && \
    ln -sf /usr/bin/chromium-browser /usr/bin/chromium

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/cache /app/configs /app/reports /app/static /app/templates

# Set permissions
RUN chown -R automation:automation /app

# Copy supervisor configuration
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Expose ports
# 8000: FastAPI
# 5901: VNC
# 80: Nginx (frontend)
EXPOSE 8000 5901 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Create log directories and set permissions
RUN mkdir -p /tmp/supervisor /app/logs && \
    chown -R automation:automation /tmp/supervisor /app/logs

# Switch to automation user
USER automation

# Start supervisor to manage all services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]