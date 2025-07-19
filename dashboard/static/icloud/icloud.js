// iCloud Configuration Page JavaScript

// Default iCloud configuration
const DEFAULT_ICLOUD_CONFIG = {
    folder: "CASES",
    sync_interval: 30,
    log_level: "info",
    backup_enabled: false
};

// Current configuration (loaded from API)
let currentConfig = { ...DEFAULT_ICLOUD_CONFIG };

// Auto-save timeout
let autoSaveTimeout = null;

// Rate limiting for connection tests
let lastTestTime = null;
const TEST_COOLDOWN = 30000; // 30 seconds

// Load configuration from server
async function loadConfiguration() {
    try {
        const response = await fetch('/api/icloud/config');
        if (response.ok) {
            currentConfig = await response.json();
        } else {
            console.log('No existing iCloud configuration found, using defaults');
            currentConfig = { ...DEFAULT_ICLOUD_CONFIG };
        }
        populateForm();
        updateStatus();
    } catch (error) {
        console.error('Error loading iCloud configuration:', error);
        showMessage('Error loading configuration. Using defaults.', 'error');
        currentConfig = { ...DEFAULT_ICLOUD_CONFIG };
        populateForm();
    }
}

// Populate form with current configuration
function populateForm() {
    document.getElementById('icloud-folder').value = currentConfig.folder || 'CASES';
    document.getElementById('sync-interval').value = currentConfig.sync_interval || 30;
    document.getElementById('log-level').value = currentConfig.log_level || 'info';
    document.getElementById('backup-enabled').checked = currentConfig.backup_enabled || false;
}

// Collect form data into configuration object
function collectFormData() {
    return {
        folder: document.getElementById('icloud-folder').value.trim(),
        sync_interval: parseInt(document.getElementById('sync-interval').value) || 30,
        log_level: document.getElementById('log-level').value,
        backup_enabled: document.getElementById('backup-enabled').checked
    };
}

// Validate configuration data
function validateConfiguration(config) {
    const errors = [];
    
    if (!config.folder) {
        errors.push('iCloud folder name is required');
    }
    
    if (config.sync_interval < 10 || config.sync_interval > 300) {
        errors.push('Sync interval must be between 10 and 300 seconds');
    }
    
    if (!['info', 'debug', 'warning', 'error'].includes(config.log_level)) {
        errors.push('Invalid log level');
    }
    
    return errors;
}

// Save configuration to server
async function saveConfiguration() {
    try {
        const config = collectFormData();
        const errors = validateConfiguration(config);
        
        if (errors.length > 0) {
            showMessage('Validation errors: ' + errors.join(', '), 'error');
            return;
        }
        
        const response = await fetch('/api/icloud/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            currentConfig = config;
            showMessage('Configuration saved successfully', 'success');
            updateStatus();
        } else {
            const errorData = await response.json();
            showMessage('Error saving configuration: ' + (errorData.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error saving configuration:', error);
        showMessage('Error saving configuration: ' + error.message, 'error');
    }
}

// Test iCloud connection
async function testConnection() {
    // Rate limiting
    const now = Date.now();
    if (lastTestTime && (now - lastTestTime) < TEST_COOLDOWN) {
        const remaining = Math.ceil((TEST_COOLDOWN - (now - lastTestTime)) / 1000);
        showMessage(`Please wait ${remaining} seconds before testing again`, 'warning');
        return;
    }
    
    const testBtn = document.getElementById('test-connection-btn');
    const originalText = testBtn.innerHTML;
    
    try {
        // Update button state
        testBtn.disabled = true;
        testBtn.innerHTML = `
            <svg class="h-4 w-4 inline-block mr-2 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
            </svg>
            Testing...
        `;
        
        const config = collectFormData();
        const response = await fetch('/api/icloud/test-connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showMessage('Connection test successful!', 'success');
            updateConnectionStatus('connected');
            updateLastSync(new Date().toISOString());
        } else {
            showMessage('Connection test failed: ' + (result.error || 'Unknown error'), 'error');
            updateConnectionStatus('failed');
        }
        
        lastTestTime = now;
        
    } catch (error) {
        console.error('Connection test error:', error);
        showMessage('Connection test failed: ' + error.message, 'error');
        updateConnectionStatus('failed');
    } finally {
        // Restore button state
        testBtn.disabled = false;
        testBtn.innerHTML = originalText;
    }
}

// Download configured sync adapter package
async function downloadPackage() {
    try {
        const config = collectFormData();
        const errors = validateConfiguration(config);
        
        if (errors.length > 0) {
            showMessage('Please fix configuration errors before downloading: ' + errors.join(', '), 'error');
            return;
        }
        
        const downloadBtn = document.getElementById('download-package-btn');
        const originalText = downloadBtn.innerHTML;
        
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = `
            <svg class="h-5 w-5 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
            </svg>
            <span>Generating...</span>
        `;
        
        const response = await fetch('/api/icloud/download-package', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'icloud-sync-adapter.tar.gz';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showMessage('Sync adapter package downloaded successfully', 'success');
        } else {
            const errorData = await response.json();
            showMessage('Error downloading package: ' + (errorData.detail || 'Unknown error'), 'error');
        }
        
    } catch (error) {
        console.error('Download error:', error);
        showMessage('Error downloading package: ' + error.message, 'error');
    } finally {
        const downloadBtn = document.getElementById('download-package-btn');
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = `
            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
            <span>Download Package</span>
        `;
    }
}

// Update status dashboard
async function updateStatus() {
    try {
        const response = await fetch('/api/icloud/status');
        if (response.ok) {
            const status = await response.json();
            updateConnectionStatus(status.connection_status);
            updateLastSync(status.last_sync);
            updateFilesSynced(status.files_synced);
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

// Update connection status indicator
function updateConnectionStatus(status) {
    const statusElement = document.getElementById('connection-status');
    const indicatorElement = document.getElementById('connection-indicator');
    
    switch (status) {
        case 'connected':
            statusElement.textContent = 'Connected';
            statusElement.className = 'text-sm text-green-600';
            indicatorElement.className = 'h-3 w-3 rounded-full bg-green-500';
            break;
        case 'connecting':
            statusElement.textContent = 'Connecting...';
            statusElement.className = 'text-sm text-yellow-600';
            indicatorElement.className = 'h-3 w-3 rounded-full bg-yellow-500';
            break;
        case 'failed':
            statusElement.textContent = 'Connection failed';
            statusElement.className = 'text-sm text-red-600';
            indicatorElement.className = 'h-3 w-3 rounded-full bg-red-500';
            break;
        default:
            statusElement.textContent = 'Not configured';
            statusElement.className = 'text-sm text-gray-500';
            indicatorElement.className = 'h-3 w-3 rounded-full bg-gray-400';
    }
}

// Update last sync time
function updateLastSync(timestamp) {
    const lastSyncElement = document.getElementById('last-sync');
    if (timestamp) {
        const date = new Date(timestamp);
        lastSyncElement.textContent = date.toLocaleString();
        lastSyncElement.className = 'text-sm text-gray-900';
    } else {
        lastSyncElement.textContent = 'Never';
        lastSyncElement.className = 'text-sm text-gray-500';
    }
}

// Update files synced count
function updateFilesSynced(count) {
    const filesSyncedElement = document.getElementById('files-synced');
    filesSyncedElement.textContent = count || 0;
    filesSyncedElement.className = count > 0 ? 'text-sm text-gray-900' : 'text-sm text-gray-500';
}

// Show message to user
function showMessage(message, type) {
    const messagesContainer = document.getElementById('icloud-messages');
    const messageId = 'message-' + Date.now();
    
    let bgColor, textColor, icon;
    switch (type) {
        case 'success':
            bgColor = 'bg-green-50';
            textColor = 'text-green-800';
            icon = `<svg class="h-5 w-5 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
            </svg>`;
            break;
        case 'error':
            bgColor = 'bg-red-50';
            textColor = 'text-red-800';
            icon = `<svg class="h-5 w-5 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
            </svg>`;
            break;
        case 'warning':
            bgColor = 'bg-yellow-50';
            textColor = 'text-yellow-800';
            icon = `<svg class="h-5 w-5 text-yellow-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
            </svg>`;
            break;
        default:
            bgColor = 'bg-blue-50';
            textColor = 'text-blue-800';
            icon = `<svg class="h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
            </svg>`;
    }
    
    const messageHtml = `
        <div id="${messageId}" class="flex items-center p-4 ${bgColor} border border-opacity-20 rounded-lg mb-3">
            <div class="flex-shrink-0">
                ${icon}
            </div>
            <div class="ml-3">
                <p class="text-sm font-medium ${textColor}">${message}</p>
            </div>
            <div class="ml-auto pl-3">
                <div class="-mx-1.5 -my-1.5">
                    <button type="button" class="inline-flex ${bgColor} rounded-md p-1.5 ${textColor} hover:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-${bgColor} focus:ring-${textColor.replace('text-', '')}" onclick="document.getElementById('${messageId}').remove()">
                        <span class="sr-only">Dismiss</span>
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    messagesContainer.innerHTML = messageHtml + messagesContainer.innerHTML;
    messagesContainer.classList.remove('hidden');
    
    // Auto-remove success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            const element = document.getElementById(messageId);
            if (element) {
                element.remove();
            }
            // Hide container if no messages left
            if (messagesContainer.children.length === 0) {
                messagesContainer.classList.add('hidden');
            }
        }, 5000);
    }
}

// Auto-save function with debouncing
function autoSave() {
    if (autoSaveTimeout) {
        clearTimeout(autoSaveTimeout);
    }
    
    autoSaveTimeout = setTimeout(() => {
        saveConfiguration();
    }, 1000); // Save 1 second after user stops typing
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Load existing configuration
    loadConfiguration();
    
    // Set up periodic status updates
    setInterval(updateStatus, 30000); // Update every 30 seconds
    
    // Event listeners
    document.getElementById('save-config-btn').addEventListener('click', saveConfiguration);
    document.getElementById('test-connection-btn').addEventListener('click', testConnection);
    document.getElementById('download-package-btn').addEventListener('click', downloadPackage);
    
    // Auto-save on form changes
    const formFields = ['icloud-folder', 'sync-interval', 'log-level', 'backup-enabled'];
    formFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('input', autoSave);
            field.addEventListener('change', autoSave);
        }
    });
    
    // Form validation
    document.getElementById('icloud-folder').addEventListener('input', function() {
        const value = this.value.trim();
        if (!value) {
            this.setCustomValidity('Folder name is required');
        } else {
            this.setCustomValidity('');
        }
    });
    
    document.getElementById('sync-interval').addEventListener('input', function() {
        const value = parseInt(this.value);
        if (value < 10 || value > 300) {
            this.setCustomValidity('Sync interval must be between 10 and 300 seconds');
        } else {
            this.setCustomValidity('');
        }
    });
});