"""FastAPI application for browser automation with streaming and VNC support."""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our automation components
from agents import BrowserAutomationBackend, TaskStep, TaskStatus
from automation_schemas import get_schema_for_task, COMMON_SCHEMAS
from automation_configs import get_recommended_config, ConfigManager
from automation_utils import (
    performance_monitor, task_cache, error_analyzer,
    format_duration, generate_temp_email
)
from code_generators import CodeGeneratorManager
from vnc_manager import VNCManager

# FastAPI app initialization
app = FastAPI(
    title="Browser Automation System",
    description="Enhanced browser automation with streaming, VNC, and code generation",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global managers
config_manager = ConfigManager()
code_generator = CodeGeneratorManager()
vnc_manager = VNCManager()

# Active connections and tasks
active_connections: Dict[str, WebSocket] = {}
active_tasks: Dict[str, Dict[str, Any]] = {}
active_backends: Dict[str, BrowserAutomationBackend] = {}

# Pydantic models for API
class TaskRequest(BaseModel):
    task_description: str
    config_name: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None
    schema_name: Optional[str] = None
    custom_schema: Optional[Dict[str, Any]] = None
    stream_output: bool = True
    enable_vnc: bool = True

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    vnc_url: Optional[str] = None
    websocket_url: Optional[str] = None

class CodeGenerationRequest(BaseModel):
    task_description: str
    target_language: str
    framework: Optional[str] = None
    include_tests: bool = True
    include_docs: bool = True

class CodeGenerationResponse(BaseModel):
    language: str
    framework: Optional[str]
    code: str
    tests: Optional[str] = None
    documentation: Optional[str] = None
    dependencies: List[str] = []

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except:
                self.disconnect(client_id)
    
    async def broadcast(self, message: dict):
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(client_id)
        
        for client_id in disconnected:
            self.disconnect(client_id)

manager = ConnectionManager()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "fastapi": "running",
            "vnc": vnc_manager.is_running(),
            "automation_backend": "ready"
        }
    }

# Main dashboard
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Browser Automation Dashboard"
    })

# API Routes
@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """Create a new automation task."""
    task_id = str(uuid.uuid4())
    
    try:
        # Get configuration
        if task_request.config_name:
            config = config_manager.get_config(task_request.config_name)
        elif task_request.custom_config:
            config = task_request.custom_config
        else:
            config = get_recommended_config(task_request.task_description)
        
        # Enable VNC if requested
        if task_request.enable_vnc:
            config['browser']['headless'] = False
            vnc_url = vnc_manager.get_vnc_url()
        else:
            config['browser']['headless'] = True
            vnc_url = None
        
        # Get schema
        if task_request.schema_name and task_request.schema_name in COMMON_SCHEMAS:
            schema = COMMON_SCHEMAS[task_request.schema_name]
        elif task_request.custom_schema:
            schema = task_request.custom_schema
        else:
            schema = get_schema_for_task(task_request.task_description)
        
        # Create backend and task
        backend = BrowserAutomationBackend(config)
        
        # Add streaming callback if enabled
        if task_request.stream_output:
            def stream_callback(step: TaskStep):
                asyncio.create_task(manager.send_personal_message({
                    "type": "step_update",
                    "task_id": task_id,
                    "step": {
                        "step_id": step.step_id,
                        "action": step.action,
                        "timestamp": step.timestamp.isoformat(),
                        "status": step.status.value,
                        "details": step.details,
                        "error": step.error
                    }
                }, task_id))
            
            backend.add_step_callback(stream_callback)
        
        # Store task info
        active_tasks[task_id] = {
            "request": task_request.dict(),
            "config": config,
            "schema": schema,
            "created_at": datetime.now(),
            "status": "created"
        }
        active_backends[task_id] = backend
        
        # Create the automation task
        backend.create_task(task_id, task_request.task_description)
        
        # Start task in background
        background_tasks.add_task(run_automation_task, task_id, backend, schema)
        
        return TaskResponse(
            task_id=task_id,
            status="created",
            message="Task created successfully",
            vnc_url=vnc_url,
            websocket_url=f"/ws/{task_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def run_automation_task(task_id: str, backend: BrowserAutomationBackend, schema: Optional[Dict]):
    """Run automation task in background."""
    try:
        active_tasks[task_id]["status"] = "running"
        active_tasks[task_id]["started_at"] = datetime.now()
        
        # Notify start
        await manager.send_personal_message({
            "type": "task_started",
            "task_id": task_id,
            "timestamp": datetime.now().isoformat()
        }, task_id)
        
        # Run the task
        result = await backend.run_task(task_id, schema)
        
        # Update task info
        active_tasks[task_id]["status"] = result["status"]
        active_tasks[task_id]["result"] = result
        active_tasks[task_id]["completed_at"] = datetime.now()
        
        # Notify completion
        await manager.send_personal_message({
            "type": "task_completed",
            "task_id": task_id,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }, task_id)
        
    except Exception as e:
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["error"] = str(e)
        active_tasks[task_id]["completed_at"] = datetime.now()
        
        await manager.send_personal_message({
            "type": "task_failed",
            "task_id": task_id,
            "error": str(e),
            "suggestion": error_analyzer.suggest_solution(str(e)),
            "timestamp": datetime.now().isoformat()
        }, task_id)
    
    finally:
        # Cleanup
        if task_id in active_backends:
            del active_backends[task_id]

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and details."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = active_tasks[task_id].copy()
    
    # Add backend info if available
    if task_id in active_backends:
        backend = active_backends[task_id]
        task_info["backend_status"] = backend.get_task_status(task_id)
        task_info["steps"] = backend.get_task_steps(task_id)
    
    return task_info

@app.get("/api/tasks")
async def list_tasks():
    """List all tasks."""
    return {
        "tasks": list(active_tasks.keys()),
        "count": len(active_tasks),
        "active_count": len([t for t in active_tasks.values() if t["status"] == "running"])
    }

@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a running task."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update status
    active_tasks[task_id]["status"] = "cancelled"
    
    # Cleanup backend
    if task_id in active_backends:
        del active_backends[task_id]
    
    # Notify cancellation
    await manager.send_personal_message({
        "type": "task_cancelled",
        "task_id": task_id,
        "timestamp": datetime.now().isoformat()
    }, task_id)
    
    return {"message": "Task cancelled successfully"}

# Code generation endpoints
@app.post("/api/generate-code", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    """Generate code for automation task in specified language."""
    try:
        result = await code_generator.generate_code(
            task_description=request.task_description,
            target_language=request.target_language,
            framework=request.framework,
            include_tests=request.include_tests,
            include_docs=request.include_docs
        )
        
        return CodeGenerationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/supported-languages")
async def get_supported_languages():
    """Get list of supported programming languages."""
    return code_generator.get_supported_languages()

@app.get("/api/configs")
async def list_configs():
    """List available configurations."""
    return config_manager.list_configs()

@app.get("/api/schemas")
async def list_schemas():
    """List available schemas."""
    return {
        "schemas": list(COMMON_SCHEMAS.keys()),
        "count": len(COMMON_SCHEMAS)
    }

@app.get("/api/performance")
async def get_performance_metrics():
    """Get performance metrics."""
    return performance_monitor.get_stats()

# VNC endpoints
@app.get("/api/vnc/status")
async def vnc_status():
    """Get VNC server status."""
    return {
        "running": vnc_manager.is_running(),
        "url": vnc_manager.get_vnc_url(),
        "port": vnc_manager.get_port()
    }

@app.post("/api/vnc/start")
async def start_vnc():
    """Start VNC server."""
    try:
        vnc_manager.start()
        return {"message": "VNC server started", "url": vnc_manager.get_vnc_url()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vnc/stop")
async def stop_vnc():
    """Stop VNC server."""
    try:
        vnc_manager.stop()
        return {"message": "VNC server stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time communication
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    
    try:
        # Send initial connection message
        await manager.send_personal_message({
            "type": "connected",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat(),
            "message": "WebSocket connection established"
        }, client_id)
        
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            elif message.get("type") == "get_task_status":
                task_id = message.get("task_id")
                if task_id and task_id in active_tasks:
                    await manager.send_personal_message({
                        "type": "task_status",
                        "task_id": task_id,
                        "status": active_tasks[task_id]
                    }, client_id)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)

# Server-Sent Events for streaming
@app.get("/api/stream/{task_id}")
async def stream_task_updates(task_id: str):
    """Stream task updates via Server-Sent Events."""
    
    async def event_generator():
        while task_id in active_tasks:
            task_info = active_tasks[task_id]
            
            # Send current status
            yield f"data: {json.dumps(task_info, default=str)}\n\n"
            
            # Check if task is completed
            if task_info["status"] in ["completed", "failed", "cancelled"]:
                break
            
            await asyncio.sleep(1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )