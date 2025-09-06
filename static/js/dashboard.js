// Dashboard JavaScript for Browser Automation System

class AutomationDashboard {
    constructor() {
        this.websocket = null;
        this.currentTaskId = null;
        this.vncClient = null;
        this.isConnected = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadPerformanceMetrics();
        this.setupVNC();
    }
    
    setupEventListeners() {
        // Form submission
        document.getElementById('automation-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startAutomation();
        });
        
        // Stop button
        document.getElementById('stop-btn').addEventListener('click', () => {
            this.stopAutomation();
        });
        
        // Clear log
        document.getElementById('clear-log').addEventListener('click', () => {
            this.clearActivityLog();
        });
        
        // VNC controls
        document.getElementById('connect-vnc').addEventListener('click', () => {
            this.connectVNC();
        });
        
        document.getElementById('vnc-fullscreen').addEventListener('click', () => {
            this.toggleVNCFullscreen();
        });
        
        document.getElementById('vnc-screenshot').addEventListener('click', () => {
            this.takeVNCScreenshot();
        });
        
        // Code download
        document.getElementById('download-code').addEventListener('click', () => {
            this.downloadGeneratedCode();
        });
        
        // Language selection change
        document.getElementById('language-select').addEventListener('change', (e) => {
            if (e.target.value && this.currentTaskId) {
                this.generateCode();
            }
        });
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
            ? `${window.location.hostname}:8000`
            : window.location.host;
        const wsUrl = `${protocol}//${host}/ws/dashboard`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            this.isConnected = true;
            this.updateConnectionStatus(true);
            this.addLogEntry('Connected to automation system', 'success');
        };
        
        this.websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        };
        
        this.websocket.onclose = () => {
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.addLogEntry('Disconnected from automation system', 'error');
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => {
                this.connectWebSocket();
            }, 3000);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.addLogEntry('WebSocket connection error', 'error');
        };
    }
    
    handleWebSocketMessage(message) {
        switch (message.type) {
            case 'connected':
                this.addLogEntry('WebSocket connection established', 'success');
                break;
                
            case 'task_started':
                this.onTaskStarted(message);
                break;
                
            case 'step_update':
                this.onStepUpdate(message);
                break;
                
            case 'task_completed':
                this.onTaskCompleted(message);
                break;
                
            case 'task_failed':
                this.onTaskFailed(message);
                break;
                
            case 'task_cancelled':
                this.onTaskCancelled(message);
                break;
                
            default:
                console.log('Unknown message type:', message.type);
        }
    }
    
    async startAutomation() {
        const taskDescription = document.getElementById('task-description').value.trim();
        const configName = document.getElementById('config-select').value;
        const enableVNC = document.getElementById('enable-vnc').checked;
        const streamOutput = document.getElementById('stream-output').checked;
        
        if (!taskDescription) {
            this.showAlert('Please enter a task description', 'warning');
            return;
        }
        
        const requestData = {
            task_description: taskDescription,
            config_name: configName || null,
            enable_vnc: enableVNC,
            stream_output: streamOutput
        };
        
        try {
            this.setFormLoading(true);
            
            const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
                ? `http://${window.location.hostname}:8000/api/tasks`
                : '/api/tasks';
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.currentTaskId = result.task_id;
                this.addLogEntry(`Task created: ${result.task_id}`, 'success');
                
                if (result.vnc_url && enableVNC) {
                    this.connectVNC();
                }
                
                // Generate code if language is selected
                const selectedLanguage = document.getElementById('language-select').value;
                if (selectedLanguage) {
                    this.generateCode();
                }
            } else {
                this.showAlert(`Error: ${result.detail}`, 'danger');
            }
        } catch (error) {
            console.error('Error starting automation:', error);
            this.showAlert('Failed to start automation', 'danger');
        } finally {
            this.setFormLoading(false);
        }
    }
    
    async stopAutomation() {
        if (!this.currentTaskId) {
            return;
        }
        
        try {
            const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
                ? `http://${window.location.hostname}:8000/api/tasks/${this.currentTaskId}`
                : `/api/tasks/${this.currentTaskId}`;
                
            const response = await fetch(apiUrl, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.addLogEntry('Task cancelled', 'warning');
            }
        } catch (error) {
            console.error('Error stopping automation:', error);
            this.showAlert('Failed to stop automation', 'danger');
        }
    }
    
    async generateCode() {
        const taskDescription = document.getElementById('task-description').value.trim();
        const language = document.getElementById('language-select').value;
        
        if (!taskDescription || !language) {
            return;
        }
        
        try {
            const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
                ? `http://${window.location.hostname}:8000/api/generate-code`
                : '/api/generate-code';
                
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    task_description: taskDescription,
                    target_language: language,
                    include_tests: true,
                    include_docs: true
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showGeneratedCode(result);
                this.addLogEntry(`Code generated for ${language}`, 'info');
            } else {
                this.showAlert(`Code generation failed: ${result.detail}`, 'warning');
            }
        } catch (error) {
            console.error('Error generating code:', error);
            this.showAlert('Failed to generate code', 'danger');
        }
    }
    
    showGeneratedCode(codeData) {
        // Update code content
        document.getElementById('main-code-content').textContent = codeData.code;
        
        if (codeData.tests) {
            document.getElementById('tests-content').textContent = codeData.tests;
        }
        
        if (codeData.documentation) {
            document.getElementById('docs-content').innerHTML = this.markdownToHtml(codeData.documentation);
        }
        
        // Store code data for download
        this.generatedCodeData = codeData;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('code-modal'));
        modal.show();
        
        // Highlight syntax
        Prism.highlightAll();
    }
    
    downloadGeneratedCode() {
        if (!this.generatedCodeData) {
            return;
        }
        
        const { language, code, tests, documentation } = this.generatedCodeData;
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        
        // Create zip-like structure (simplified)
        const files = {
            [`automation_script.${this.getFileExtension(language)}`]: code
        };
        
        if (tests) {
            files[`test_automation.${this.getFileExtension(language)}`] = tests;
        }
        
        if (documentation) {
            files['README.md'] = documentation;
        }
        
        // Download main file
        this.downloadFile(
            files[`automation_script.${this.getFileExtension(language)}`],
            `automation_script_${timestamp}.${this.getFileExtension(language)}`,
            'text/plain'
        );
    }
    
    getFileExtension(language) {
        const extensions = {
            python: 'py',
            javascript: 'js',
            typescript: 'ts',
            java: 'java',
            csharp: 'cs',
            go: 'go',
            rust: 'rs',
            php: 'php',
            ruby: 'rb',
            kotlin: 'kt'
        };
        return extensions[language] || 'txt';
    }
    
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    setupVNC() {
        // VNC setup will be handled when connecting
    }
    
    connectVNC() {
        const vncContainer = document.getElementById('vnc-container');
        const vncStatus = document.getElementById('vnc-status');
        const vncCanvas = document.getElementById('vnc-canvas');
        
        try {
            // Hide status and show canvas
            vncStatus.style.display = 'none';
            vncCanvas.style.display = 'block';
            
            // Create RFB connection (noVNC)
            const vncUrl = `ws://${window.location.hostname}:6080`;
            
            this.vncClient = new RFB(vncCanvas, vncUrl, {
                credentials: { password: 'automation' }
            });
            
            this.vncClient.addEventListener('connect', () => {
                this.addLogEntry('VNC connected successfully', 'success');
            });
            
            this.vncClient.addEventListener('disconnect', () => {
                this.addLogEntry('VNC disconnected', 'warning');
                vncStatus.style.display = 'block';
                vncCanvas.style.display = 'none';
            });
            
            this.vncClient.addEventListener('credentialsrequired', () => {
                this.addLogEntry('VNC credentials required', 'info');
            });
            
        } catch (error) {
            console.error('VNC connection error:', error);
            this.addLogEntry('Failed to connect to VNC', 'error');
            vncStatus.style.display = 'block';
            vncCanvas.style.display = 'none';
        }
    }
    
    toggleVNCFullscreen() {
        const vncContainer = document.getElementById('vnc-container');
        
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            vncContainer.requestFullscreen();
        }
    }
    
    async takeVNCScreenshot() {
        try {
            const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
                ? `http://${window.location.hostname}:8000/api/vnc/screenshot`
                : '/api/vnc/screenshot';
                
            const response = await fetch(apiUrl, {
                method: 'POST'
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `vnc_screenshot_${Date.now()}.png`;
                a.click();
                URL.revokeObjectURL(url);
                
                this.addLogEntry('Screenshot saved', 'success');
            }
        } catch (error) {
            console.error('Screenshot error:', error);
            this.addLogEntry('Failed to take screenshot', 'error');
        }
    }
    
    onTaskStarted(message) {
        this.updateTaskStatus({
            id: message.task_id,
            status: 'running',
            description: 'Task started',
            steps: []
        });
        
        this.setFormButtons(false, true);
        this.addLogEntry(`Task started: ${message.task_id}`, 'info');
    }
    
    onStepUpdate(message) {
        const step = message.step;
        this.addStepToTask(step);
        
        const statusClass = step.status === 'completed' ? 'success' : 
                           step.status === 'failed' ? 'error' : 'info';
        
        this.addLogEntry(`Step: ${step.action} - ${step.status}`, statusClass);
    }
    
    onTaskCompleted(message) {
        this.updateTaskStatus({
            id: message.task_id,
            status: 'completed',
            result: message.result
        });
        
        this.setFormButtons(true, false);
        this.addLogEntry('Task completed successfully', 'success');
        this.loadPerformanceMetrics();
    }
    
    onTaskFailed(message) {
        this.updateTaskStatus({
            id: message.task_id,
            status: 'failed',
            error: message.error
        });
        
        this.setFormButtons(true, false);
        this.addLogEntry(`Task failed: ${message.error}`, 'error');
        
        if (message.suggestion) {
            this.addLogEntry(`Suggestion: ${message.suggestion}`, 'info');
        }
        
        this.loadPerformanceMetrics();
    }
    
    onTaskCancelled(message) {
        this.updateTaskStatus({
            id: message.task_id,
            status: 'cancelled'
        });
        
        this.setFormButtons(true, false);
        this.addLogEntry('Task cancelled', 'warning');
    }
    
    updateTaskStatus(taskInfo) {
        const statusContainer = document.getElementById('task-status');
        
        if (taskInfo.status === 'running') {
            statusContainer.innerHTML = `
                <div class="task-info fade-in">
                    <h6>Task: ${taskInfo.id}</h6>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="status-badge ${taskInfo.status}">${taskInfo.status}</span>
                        <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                    </div>
                    <div class="step-list" id="step-list"></div>
                </div>
            `;
        } else {
            const statusBadge = statusContainer.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.className = `status-badge ${taskInfo.status}`;
                statusBadge.textContent = taskInfo.status;
            }
            
            if (taskInfo.result) {
                const resultDiv = document.createElement('div');
                resultDiv.className = 'mt-2';
                resultDiv.innerHTML = `
                    <small class="text-muted">Result:</small>
                    <pre class="text-monospace small">${JSON.stringify(taskInfo.result, null, 2)}</pre>
                `;
                statusContainer.querySelector('.task-info').appendChild(resultDiv);
            }
            
            if (taskInfo.error) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'mt-2 text-danger';
                errorDiv.innerHTML = `
                    <small>Error:</small>
                    <div class="small">${taskInfo.error}</div>
                `;
                statusContainer.querySelector('.task-info').appendChild(errorDiv);
            }
        }
    }
    
    addStepToTask(step) {
        const stepList = document.getElementById('step-list');
        if (!stepList) return;
        
        const stepElement = document.createElement('div');
        stepElement.className = 'step-item fade-in';
        
        const iconClass = step.status === 'completed' ? 'fas fa-check completed' :
                         step.status === 'failed' ? 'fas fa-times failed' :
                         'fas fa-spinner fa-spin running';
        
        stepElement.innerHTML = `
            <div class="step-icon ${step.status}">
                <i class="${iconClass}"></i>
            </div>
            <div class="flex-grow-1">
                <div>${step.action}</div>
                <small class="text-muted">${new Date(step.timestamp).toLocaleTimeString()}</small>
            </div>
        `;
        
        stepList.appendChild(stepElement);
        stepList.scrollTop = stepList.scrollHeight;
    }
    
    async loadPerformanceMetrics() {
        try {
            const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
                ? `http://${window.location.hostname}:8000/api/performance`
                : '/api/performance';
                
            const response = await fetch(apiUrl);
            const metrics = await response.json();
            
            // Update metrics display
            const totalTasks = Object.values(metrics).reduce((sum, func) => sum + func.total_calls, 0);
            const successRate = totalTasks > 0 ? 
                (Object.values(metrics).reduce((sum, func) => sum + func.success_rate * func.total_calls, 0) / totalTasks * 100).toFixed(1) : 0;
            const avgDuration = totalTasks > 0 ?
                (Object.values(metrics).reduce((sum, func) => sum + func.avg_execution_time * func.total_calls, 0) / totalTasks).toFixed(1) : 0;
            
            document.getElementById('total-tasks').textContent = totalTasks;
            document.getElementById('success-rate').textContent = `${successRate}%`;
            document.getElementById('avg-duration').textContent = `${avgDuration}s`;
            
        } catch (error) {
            console.error('Error loading performance metrics:', error);
        }
    }
    
    setFormLoading(loading) {
        const form = document.getElementById('automation-form');
        const startBtn = document.getElementById('start-btn');
        
        if (loading) {
            form.classList.add('loading');
            startBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Starting...';
            startBtn.disabled = true;
        } else {
            form.classList.remove('loading');
            startBtn.innerHTML = '<i class="fas fa-play me-2"></i>Start Automation';
            startBtn.disabled = false;
        }
    }
    
    setFormButtons(enableStart, enableStop) {
        document.getElementById('start-btn').disabled = !enableStart;
        document.getElementById('stop-btn').disabled = !enableStop;
    }
    
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('status-indicator');
        const text = document.getElementById('status-text');
        
        if (connected) {
            indicator.className = 'fas fa-circle text-success';
            text.textContent = 'Connected';
        } else {
            indicator.className = 'fas fa-circle text-danger';
            text.textContent = 'Disconnected';
        }
    }
    
    addLogEntry(message, type = 'info') {
        const logContainer = document.getElementById('activity-log');
        const timestamp = new Date().toLocaleTimeString();
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type} fade-in`;
        logEntry.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="message">${message}</span>
        `;
        
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Limit log entries to prevent memory issues
        const entries = logContainer.querySelectorAll('.log-entry');
        if (entries.length > 100) {
            entries[0].remove();
        }
    }
    
    clearActivityLog() {
        const logContainer = document.getElementById('activity-log');
        logContainer.innerHTML = `
            <div class="log-entry text-muted">
                <span class="timestamp">[${new Date().toLocaleTimeString()}]</span>
                <span class="message">Log cleared</span>
            </div>
        `;
    }
    
    showAlert(message, type) {
        // Create and show Bootstrap alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.insertBefore(alertDiv, document.body.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    markdownToHtml(markdown) {
        // Simple markdown to HTML conversion
        return markdown
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/gim, '<em>$1</em>')
            .replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>')
            .replace(/`(.*?)`/gim, '<code>$1</code>')
            .replace(/\n/gim, '<br>');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new AutomationDashboard();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, reduce update frequency
    } else {
        // Page is visible, resume normal updates
        if (window.dashboard) {
            window.dashboard.loadPerformanceMetrics();
        }
    }
});