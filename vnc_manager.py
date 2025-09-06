"""VNC Manager for browser visualization and remote access."""

import os
import subprocess
import time
import psutil
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class VNCManager:
    """Manages VNC server for browser visualization."""
    
    def __init__(self, display: str = ":1", port: int = 5901, password: str = "automation"):
        self.display = display
        self.port = port
        self.password = password
        self.vnc_process = None
        self.xvfb_process = None
        self.fluxbox_process = None
        self.websockify_process = None
        self.websockify_port = 6080
        
        # Set up VNC directory
        self.vnc_dir = Path.home() / ".vnc"
        self.vnc_dir.mkdir(exist_ok=True)
        
        # Set up password file
        self.setup_password()
    
    def setup_password(self):
        """Set up VNC password."""
        try:
            passwd_file = self.vnc_dir / "passwd"
            
            # Create password using vncpasswd
            process = subprocess.Popen(
                ["vncpasswd", "-f"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=f"{self.password}\n{self.password}\n")
            
            if process.returncode == 0:
                with open(passwd_file, "wb") as f:
                    f.write(stdout.encode())
                os.chmod(passwd_file, 0o600)
                logger.info("VNC password set successfully")
            else:
                logger.error(f"Failed to set VNC password: {stderr}")
                
        except Exception as e:
            logger.error(f"Error setting up VNC password: {e}")
    
    def start_xvfb(self):
        """Start Xvfb (X Virtual Framebuffer)."""
        try:
            if self.is_xvfb_running():
                logger.info("Xvfb already running")
                return True
            
            cmd = [
                "Xvfb",
                self.display,
                "-screen", "0", "1920x1080x24",
                "-ac",
                "+extension", "GLX",
                "+render",
                "-noreset"
            ]
            
            self.xvfb_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for Xvfb to start
            time.sleep(2)
            
            if self.xvfb_process.poll() is None:
                logger.info(f"Xvfb started on display {self.display}")
                return True
            else:
                logger.error("Failed to start Xvfb")
                return False
                
        except Exception as e:
            logger.error(f"Error starting Xvfb: {e}")
            return False
    
    def start_fluxbox(self):
        """Start Fluxbox window manager."""
        try:
            if self.is_fluxbox_running():
                logger.info("Fluxbox already running")
                return True
            
            env = os.environ.copy()
            env["DISPLAY"] = self.display
            
            self.fluxbox_process = subprocess.Popen(
                ["fluxbox"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(1)
            
            if self.fluxbox_process.poll() is None:
                logger.info("Fluxbox started successfully")
                return True
            else:
                logger.error("Failed to start Fluxbox")
                return False
                
        except Exception as e:
            logger.error(f"Error starting Fluxbox: {e}")
            return False
    
    def start_vnc_server(self):
        """Start VNC server."""
        try:
            if self.is_vnc_running():
                logger.info("VNC server already running")
                return True
            
            cmd = [
                "x11vnc",
                "-forever",
                "-usepw",
                "-shared",
                "-display", self.display,
                "-rfbport", str(self.port)
            ]
            
            self.vnc_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(2)
            
            if self.vnc_process.poll() is None:
                logger.info(f"VNC server started on port {self.port}")
                return True
            else:
                logger.error("Failed to start VNC server")
                return False
                
        except Exception as e:
            logger.error(f"Error starting VNC server: {e}")
            return False
    
    def start_websockify(self):
        """Start websockify for web-based VNC access."""
        try:
            if self.is_websockify_running():
                logger.info("Websockify already running")
                return True
            
            cmd = [
                "websockify",
                f"{self.websockify_port}",
                f"localhost:{self.port}"
            ]
            
            self.websockify_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(2)
            
            if self.websockify_process.poll() is None:
                logger.info(f"Websockify started on port {self.websockify_port}")
                return True
            else:
                logger.error("Failed to start websockify")
                return False
                
        except Exception as e:
            logger.error(f"Error starting websockify: {e}")
            return False
    
    def start(self):
        """Start all VNC components."""
        logger.info("Starting VNC server components...")
        
        # Start Xvfb first
        if not self.start_xvfb():
            raise Exception("Failed to start Xvfb")
        
        # Start window manager
        if not self.start_fluxbox():
            logger.warning("Failed to start Fluxbox, continuing without window manager")
        
        # Start VNC server
        if not self.start_vnc_server():
            raise Exception("Failed to start VNC server")
        
        # Start websockify for web access
        if not self.start_websockify():
            logger.warning("Failed to start websockify, web VNC access not available")
        
        logger.info("VNC server started successfully")
        return True
    
    def stop(self):
        """Stop all VNC components."""
        logger.info("Stopping VNC server components...")
        
        processes = [
            ("websockify", self.websockify_process),
            ("VNC server", self.vnc_process),
            ("Fluxbox", self.fluxbox_process),
            ("Xvfb", self.xvfb_process)
        ]
        
        for name, process in processes:
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    logger.info(f"{name} stopped")
                except subprocess.TimeoutExpired:
                    process.kill()
                    logger.warning(f"{name} force killed")
                except Exception as e:
                    logger.error(f"Error stopping {name}: {e}")
        
        # Kill any remaining processes
        self.kill_remaining_processes()
        
        logger.info("VNC server stopped")
    
    def kill_remaining_processes(self):
        """Kill any remaining VNC-related processes."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if any(keyword in cmdline.lower() for keyword in 
                          ['x11vnc', 'xvfb', 'fluxbox', 'websockify']):
                        if self.display in cmdline:
                            proc.kill()
                            logger.info(f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Error killing remaining processes: {e}")
    
    def is_xvfb_running(self) -> bool:
        """Check if Xvfb is running."""
        return self._is_process_running("Xvfb", self.display)
    
    def is_fluxbox_running(self) -> bool:
        """Check if Fluxbox is running."""
        return self._is_process_running("fluxbox")
    
    def is_vnc_running(self) -> bool:
        """Check if VNC server is running."""
        return self._is_process_running("x11vnc", str(self.port))
    
    def is_websockify_running(self) -> bool:
        """Check if websockify is running."""
        return self._is_process_running("websockify", str(self.websockify_port))
    
    def _is_process_running(self, process_name: str, identifier: str = None) -> bool:
        """Check if a specific process is running."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if process_name.lower() in proc.info['name'].lower():
                        if identifier:
                            cmdline = ' '.join(proc.info['cmdline'] or [])
                            if identifier in cmdline:
                                return True
                        else:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception:
            return False
    
    def is_running(self) -> bool:
        """Check if VNC server is running."""
        return self.is_vnc_running()
    
    def get_vnc_url(self) -> str:
        """Get VNC connection URL."""
        return f"vnc://localhost:{self.port}"
    
    def get_web_vnc_url(self) -> str:
        """Get web-based VNC URL."""
        return f"http://localhost:{self.websockify_port}"
    
    def get_port(self) -> int:
        """Get VNC port."""
        return self.port
    
    def get_display(self) -> str:
        """Get X display."""
        return self.display
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed VNC server status."""
        return {
            "running": self.is_running(),
            "display": self.display,
            "vnc_port": self.port,
            "websockify_port": self.websockify_port,
            "vnc_url": self.get_vnc_url(),
            "web_vnc_url": self.get_web_vnc_url(),
            "components": {
                "xvfb": self.is_xvfb_running(),
                "fluxbox": self.is_fluxbox_running(),
                "vnc_server": self.is_vnc_running(),
                "websockify": self.is_websockify_running()
            }
        }
    
    def restart(self):
        """Restart VNC server."""
        logger.info("Restarting VNC server...")
        self.stop()
        time.sleep(2)
        return self.start()
    
    def take_screenshot(self, output_path: str = None) -> str:
        """Take a screenshot of the VNC display."""
        try:
            if not output_path:
                timestamp = int(time.time())
                output_path = f"/tmp/vnc_screenshot_{timestamp}.png"
            
            env = os.environ.copy()
            env["DISPLAY"] = self.display
            
            cmd = ["import", "-window", "root", output_path]
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Screenshot saved to {output_path}")
                return output_path
            else:
                logger.error(f"Failed to take screenshot: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None

# Global VNC manager instance
vnc_manager = VNCManager()

# Auto-start VNC server if in Docker environment
if os.getenv("DOCKER_CONTAINER"):
    try:
        vnc_manager.start()
        logger.info("VNC server auto-started in Docker container")
    except Exception as e:
        logger.error(f"Failed to auto-start VNC server: {e}")