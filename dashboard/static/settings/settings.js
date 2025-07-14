// Settings Page JavaScript

// Default settings structure
const DEFAULT_SETTINGS = {
    firm: {
        name: "",
        address: "",
        phone: "",
        email: ""
    },
    document: {
        default_court: "UNITED STATES DISTRICT COURT",
        default_district: "EASTERN DISTRICT OF NEW YORK"
    },
    icloud: {
        account: "",
        password: "",
        folder: "/LegalCases"
    },
    system: {
        auto_save: true,
        data_retention: 90
    }
};

// Current settings (loaded from API)
let currentSettings = { ...DEFAULT_SETTINGS };

// Auto-save timeout
let autoSaveTimeout = null;

// Rate limiting tracking for iCloud test connections
let lastTestTime = null;
const TEST_COOLDOWN = 30000; // 30 seconds
let testCooldownTimeout = null;

// Password visibility toggle function
function togglePasswordVisibility() {
    const passwordField = document.getElementById('icloud-password');
    const eyeClosedIcon = document.getElementById('eye-closed');
    const eyeOpenIcon = document.getElementById('eye-open');
    
    if (passwordField.type === 'password') {
        // Show password
        passwordField.type = 'text';
        eyeClosedIcon.classList.add('hidden');
        eyeOpenIcon.classList.remove('hidden');
    } else {
        // Hide password
        passwordField.type = 'password';
        eyeClosedIcon.classList.remove('hidden');
        eyeOpenIcon.classList.add('hidden');
    }
}

// Make function globally available
window.togglePasswordVisibility = togglePasswordVisibility;

// Load settings from server
async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        if (response.ok) {
            currentSettings = await response.json();
        } else {
            console.log('No existing settings found, using defaults');
            currentSettings = { ...DEFAULT_SETTINGS };
        }
        populateForm();
    } catch (error) {
        console.error('Error loading settings:', error);
        showMessage('Error loading settings. Using defaults.', 'error');
        currentSettings = { ...DEFAULT_SETTINGS };
        populateForm();
    }
}

// Populate form with current settings
function populateForm() {
    // Firm information
    document.getElementById('firm-name').value = currentSettings.firm?.name || '';
    document.getElementById('firm-address').value = currentSettings.firm?.address || '';
    document.getElementById('firm-phone').value = currentSettings.firm?.phone || '';
    document.getElementById('firm-email').value = currentSettings.firm?.email || '';
    
    // Document preferences
    document.getElementById('default-court').value = currentSettings.document?.default_court || 'UNITED STATES DISTRICT COURT';
    document.getElementById('default-district').value = currentSettings.document?.default_district || 'EASTERN DISTRICT OF NEW YORK';
    
    // iCloud integration
    document.getElementById('icloud-account').value = currentSettings.icloud?.account || '';
    document.getElementById('icloud-password').value = currentSettings.icloud?.password || '';
    document.getElementById('icloud-folder').value = currentSettings.icloud?.folder || '/LegalCases';
    
    // System configuration
    document.getElementById('auto-save').checked = currentSettings.system?.auto_save !== false;
    document.getElementById('data-retention').value = currentSettings.system?.data_retention || 90;
}

// Collect form data into settings object
function collectFormData() {
    return {
        firm: {
            name: document.getElementById('firm-name').value.trim(),
            address: document.getElementById('firm-address').value.trim(),
            phone: document.getElementById('firm-phone').value.trim(),
            email: document.getElementById('firm-email').value.trim()
        },
        document: {
            default_court: document.getElementById('default-court').value,
            default_district: document.getElementById('default-district').value
        },
        icloud: {
            account: document.getElementById('icloud-account').value.trim(),
            password: document.getElementById('icloud-password').value.trim(),
            folder: document.getElementById('icloud-folder').value.trim()
        },
        system: {
            auto_save: document.getElementById('auto-save').checked,
            data_retention: parseInt(document.getElementById('data-retention').value)
        }
    };
}

// Validate settings data
function validateSettings(settings) {
    const errors = [];
    
    // Required firm fields
    if (!settings.firm.name) {
        errors.push('Law firm name is required');
    }
    if (!settings.firm.address) {
        errors.push('Business address is required');
    }
    if (!settings.firm.phone) {
        errors.push('Business phone is required');
    }
    if (!settings.firm.email) {
        errors.push('Contact email is required');
    }
    
    // Email format validation
    if (settings.firm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(settings.firm.email)) {
        errors.push('Please enter a valid email address');
    }
    
    // Phone format validation (basic)
    if (settings.firm.phone && !/^[\d\s\-\(\)\+\.]{10,}$/.test(settings.firm.phone)) {
        errors.push('Please enter a valid phone number');
    }
    
    return errors;
}

// Save settings to server
async function saveSettings() {
    const settings = collectFormData();
    const errors = validateSettings(settings);
    
    if (errors.length > 0) {
        showMessage(`Validation errors: ${errors.join(', ')}`, 'error');
        return false;
    }
    
    try {
        const button = document.getElementById('save-settings-btn');
        const originalText = button.innerHTML;
        
        // Show loading state
        button.innerHTML = `<svg class="h-4 w-4 inline-block mr-2 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
        </svg>Saving...`;
        button.disabled = true;
        
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        currentSettings = settings;
        
        // Success feedback
        button.innerHTML = `<svg class="h-4 w-4 inline-block mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>Saved!`;
        button.classList.remove('bg-blue-600', 'hover:bg-blue-700');
        button.classList.add('bg-green-600', 'hover:bg-green-700');
        
        showMessage('Settings saved successfully!', 'success');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('bg-green-600', 'hover:bg-green-700');
            button.classList.add('bg-blue-600', 'hover:bg-blue-700');
            button.disabled = false;
        }, 2000);
        
        return true;
        
    } catch (error) {
        console.error('Error saving settings:', error);
        showMessage(`Error saving settings: ${error.message}`, 'error');
        
        // Reset button
        const button = document.getElementById('save-settings-btn');
        button.innerHTML = `<svg class="h-4 w-4 inline-block mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>Save Settings`;
        button.disabled = false;
        
        return false;
    }
}

// Reset settings to defaults
function resetSettings() {
    if (confirm('Are you sure you want to reset all settings to their default values? This action cannot be undone.')) {
        currentSettings = { ...DEFAULT_SETTINGS };
        populateForm();
        showMessage('Settings reset to defaults. Click "Save Settings" to apply.', 'info');
    }
}

// Auto-save functionality
function scheduleAutoSave() {
    if (!currentSettings.system?.auto_save) return;
    
    if (autoSaveTimeout) {
        clearTimeout(autoSaveTimeout);
    }
    
    autoSaveTimeout = setTimeout(async () => {
        console.log('Auto-saving settings...');
        await saveSettings();
    }, 2000); // Auto-save after 2 seconds of no changes
}

// Show sync-specific messages in the iCloud sync service section
function showSyncMessage(message, type = 'info') {
    const syncContainer = document.getElementById('icloud-test-result');
    
    // Clear existing messages
    syncContainer.innerHTML = '';
    syncContainer.classList.remove('hidden');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `p-3 rounded-lg border ${getMessageClasses(type)}`;
    
    messageDiv.innerHTML = `
        <div class="flex items-center">
            <div class="flex-shrink-0">
                ${getSyncMessageIcon(type)}
            </div>
            <div class="ml-3">
                <p class="text-sm font-medium">${message}</p>
            </div>
        </div>
    `;
    
    syncContainer.appendChild(messageDiv);
}

// Get appropriate icon for sync messages
function getSyncMessageIcon(type) {
    switch (type) {
        case 'success':
            return '<svg class="h-4 w-4 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>';
        case 'error':
            return '<svg class="h-4 w-4 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>';
        case 'warning':
            return '<svg class="h-4 w-4 text-yellow-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" /></svg>';
        default:
            return '<svg class="h-4 w-4 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" /></svg>';
    }
}

// Show message to user
function showMessage(message, type = 'info') {
    const messagesContainer = document.getElementById('settings-messages');
    
    // Clear existing messages
    messagesContainer.innerHTML = '';
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `p-4 rounded-lg border ${getMessageClasses(type)}`;
    
    messageDiv.innerHTML = `
        <div class="flex items-center">
            <div class="flex-shrink-0">
                ${getMessageIcon(type)}
            </div>
            <div class="ml-3">
                <p class="text-sm font-medium">${message}</p>
            </div>
            <div class="ml-auto pl-3">
                <button onclick="hideMessage()" class="text-gray-400 hover:text-gray-600">
                    <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.classList.remove('hidden');
    
    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            hideMessage();
        }, 5000);
    }
}

// Hide message
function hideMessage() {
    const messagesContainer = document.getElementById('settings-messages');
    messagesContainer.classList.add('hidden');
}

// Get CSS classes for message type
function getMessageClasses(type) {
    switch (type) {
        case 'success':
            return 'bg-green-50 border-green-200 text-green-800';
        case 'error':
            return 'bg-red-50 border-red-200 text-red-800';
        case 'warning':
            return 'bg-yellow-50 border-yellow-200 text-yellow-800';
        default:
            return 'bg-blue-50 border-blue-200 text-blue-800';
    }
}

// Get icon for message type
function getMessageIcon(type) {
    switch (type) {
        case 'success':
            return `<svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>`;
        case 'error':
            return `<svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>`;
        case 'warning':
            return `<svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>`;
        default:
            return `<svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
            </svg>`;
    }
}

// Template Upload Functionality
let currentTemplate = null;

// Initialize template upload
function initializeTemplateUpload() {
    const uploadInput = document.getElementById('summons-template-upload');
    const statusDiv = document.getElementById('summons-template-status');
    const previewBtn = document.getElementById('preview-template-btn');
    const removeBtn = document.getElementById('remove-template-btn');
    
    // Check for existing template
    checkExistingTemplate();
    
    // File upload handler
    uploadInput.addEventListener('change', handleTemplateUpload);
    
    // Preview button handler
    previewBtn.addEventListener('click', previewTemplate);
    
    // Remove button handler
    removeBtn.addEventListener('click', removeTemplate);
    
    // Drag and drop handlers
    const dropZone = uploadInput.parentElement;
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-blue-400', 'bg-blue-50');
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-blue-400', 'bg-blue-50');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-blue-400', 'bg-blue-50');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadInput.files = files;
            handleTemplateUpload({ target: uploadInput });
        }
    });
}

// Check for existing template
async function checkExistingTemplate() {
    try {
        const response = await fetch('/api/templates/summons');
        if (response.ok) {
            const result = await response.json();
            if (result.exists) {
                currentTemplate = result.template;
                updateTemplateStatus('success', result.template.name, result.template.upload_date);
            }
        }
    } catch (error) {
        console.error('Error checking existing template:', error);
    }
}

// Handle template upload
async function handleTemplateUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    if (!file.name.endsWith('.docx')) {
        showMessage('Please upload a Microsoft Word (.docx) file only.', 'error');
        return;
    }
    
    // Validate file size (5MB limit)
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
        showMessage('File size must be less than 5MB.', 'error');
        return;
    }
    
    // Show uploading status
    updateTemplateStatus('uploading', file.name);
    
    // Create FormData
    const formData = new FormData();
    formData.append('template', file);
    
    try {
        const response = await fetch('/api/templates/summons', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            currentTemplate = result.template;
            updateTemplateStatus('success', result.template.name, result.template.upload_date);
            showMessage('Template uploaded successfully!', 'success');
        } else {
            const error = await response.json();
            updateTemplateStatus('error', file.name, null, error.detail || 'Upload failed');
            showMessage(error.detail || 'Template upload failed.', 'error');
        }
    } catch (error) {
        console.error('Error uploading template:', error);
        updateTemplateStatus('error', file.name, null, 'Upload failed');
        showMessage('Error uploading template. Please try again.', 'error');
    }
}

// Update template status display
function updateTemplateStatus(status, filename, uploadDate = null, errorMessage = null) {
    const statusDiv = document.getElementById('summons-template-status');
    const previewBtn = document.getElementById('preview-template-btn');
    const removeBtn = document.getElementById('remove-template-btn');
    
    switch (status) {
        case 'uploading':
            statusDiv.className = 'bg-blue-50 border border-blue-200 rounded-lg p-3';
            statusDiv.innerHTML = `
                <div class="flex items-center">
                    <svg class="animate-spin h-5 w-5 text-blue-600 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span class="text-sm font-medium text-blue-800">Uploading ${filename}...</span>
                </div>
            `;
            previewBtn.disabled = true;
            removeBtn.disabled = true;
            break;
            
        case 'success':
            statusDiv.className = 'bg-green-50 border border-green-200 rounded-lg p-3';
            statusDiv.innerHTML = `
                <div class="flex items-center">
                    <svg class="h-5 w-5 text-green-600 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span class="text-sm font-medium text-green-800">Template uploaded successfully</span>
                </div>
                <p class="text-xs text-green-700 mt-1">
                    <strong>${filename}</strong> ${uploadDate ? `• Uploaded: ${new Date(uploadDate).toLocaleString()}` : ''}
                </p>
            `;
            previewBtn.disabled = false;
            previewBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            removeBtn.disabled = false;
            removeBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            break;
            
        case 'error':
            statusDiv.className = 'bg-red-50 border border-red-200 rounded-lg p-3';
            statusDiv.innerHTML = `
                <div class="flex items-center">
                    <svg class="h-5 w-5 text-red-600 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                    </svg>
                    <span class="text-sm font-medium text-red-800">Upload failed</span>
                </div>
                <p class="text-xs text-red-700 mt-1">${errorMessage || 'Please try again'}</p>
            `;
            previewBtn.disabled = true;
            removeBtn.disabled = true;
            break;
            
        default:
            statusDiv.className = 'bg-yellow-50 border border-yellow-200 rounded-lg p-3';
            statusDiv.innerHTML = `
                <div class="flex items-center">
                    <svg class="h-5 w-5 text-yellow-600 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                    </svg>
                    <span class="text-sm font-medium text-yellow-800">No custom template uploaded</span>
                </div>
                <p class="text-xs text-yellow-700 mt-1">Using default system template. Upload a custom template to generate summons with your preferred formatting.</p>
            `;
            previewBtn.disabled = true;
            previewBtn.classList.add('opacity-50', 'cursor-not-allowed');
            removeBtn.disabled = true;
            removeBtn.classList.add('opacity-50', 'cursor-not-allowed');
    }
}

// Preview template
function previewTemplate() {
    if (!currentTemplate) return;
    
    // Open template preview in new window
    const previewUrl = `/api/templates/summons/preview`;
    window.open(previewUrl, '_blank', 'width=800,height=600,scrollbars=yes');
}

// Remove template
async function removeTemplate() {
    if (!currentTemplate) return;
    
    if (!confirm('Are you sure you want to remove this template? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/templates/summons', {
            method: 'DELETE'
        });
        
        if (response.ok) {
            currentTemplate = null;
            updateTemplateStatus('none');
            showMessage('Template removed successfully.', 'success');
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Failed to remove template.', 'error');
        }
    } catch (error) {
        console.error('Error removing template:', error);
        showMessage('Error removing template. Please try again.', 'error');
    }
}

// Load changelog from server
async function loadChangelog() {
    try {
        const response = await fetch('/api/changelog');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update version info
        document.getElementById('current-version').textContent = data.current_version;
        document.getElementById('changelog-last-updated').textContent = 
            new Date(data.last_updated).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        
        // Convert markdown to HTML (basic conversion)
        const htmlContent = convertMarkdownToHtml(data.content);
        document.getElementById('changelog-content').innerHTML = htmlContent;
        
    } catch (error) {
        console.error('Error loading changelog:', error);
        document.getElementById('changelog-content').innerHTML = `
            <div class="text-center py-8">
                <div class="text-red-600">
                    <svg class="h-12 w-12 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    <p class="text-gray-600">Error loading changelog</p>
                    <p class="text-sm text-gray-500 mt-1">${error.message}</p>
                </div>
            </div>
        `;
    }
}

// Basic markdown to HTML converter
function convertMarkdownToHtml(markdown) {
    let html = markdown;
    
    // Convert headers
    html = html.replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold text-gray-900 mt-6 mb-3">$1</h3>');
    html = html.replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold text-gray-900 mt-8 mb-4">$1</h2>');
    html = html.replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold text-gray-900 mt-8 mb-6">$1</h1>');
    
    // Convert bold text
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>');
    
    // Convert code blocks
    html = html.replace(/`([^`]*)`/g, '<code class="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm">$1</code>');
    
    // Convert lists
    html = html.replace(/^- (.*$)/gm, '<li class="ml-4 text-gray-700">• $1</li>');
    
    // Convert links
    html = html.replace(/\[([^\]]*)\]\(([^\)]*)\)/g, '<a href="$2" class="text-blue-600 hover:underline">$1</a>');
    
    // Convert line breaks
    html = html.replace(/\n/g, '<br>');
    
    // Wrap in container
    return `<div class="changelog-content">${html}</div>`;
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    // Load settings from server
    loadSettings();
    
    // Initialize template upload functionality
    initializeTemplateUpload();
    
    // Initialize creditor addresses functionality
    initializeCreditorAddresses();
    
    // Load changelog
    loadChangelog();
    
    // Add event listeners
    document.getElementById('save-settings-btn').addEventListener('click', saveSettings);
    document.getElementById('reset-settings-btn').addEventListener('click', resetSettings);
    
    // Add auto-save listeners to form inputs
    const formInputs = document.querySelectorAll('input, textarea, select');
    formInputs.forEach(input => {
        input.addEventListener('input', scheduleAutoSave);
        input.addEventListener('change', scheduleAutoSave);
    });
    
    // Handle auto-save toggle
    document.getElementById('auto-save').addEventListener('change', (e) => {
        currentSettings.system.auto_save = e.target.checked;
        if (!e.target.checked && autoSaveTimeout) {
            clearTimeout(autoSaveTimeout);
        }
    });
    
    // Handle DOCX download
    document.getElementById('download-docx-btn').addEventListener('click', downloadTemplateAsDocx);
    
    // Handle iCloud test connection
    document.getElementById('test-icloud-btn').addEventListener('click', testICloudConnection);
    
    // Handle iCloud sync cases
    document.getElementById('sync-icloud-btn').addEventListener('click', syncICloudCases);
});

// Download attorney template as DOCX
async function downloadTemplateAsDocx() {
    const button = document.getElementById('download-docx-btn');
    const originalText = button.innerHTML;
    
    try {
        // Show loading state
        button.innerHTML = `
            <svg class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generating...
        `;
        button.disabled = true;
        
        // Get template content
        const templateResponse = await fetch('/api/attorney_template');
        const templateContent = await templateResponse.text();
        
        // Generate DOCX
        const docxResponse = await fetch('/api/attorney_template/docx', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: templateContent
            })
        });
        
        if (!docxResponse.ok) {
            throw new Error('Failed to generate DOCX');
        }
        
        // Download the file
        const blob = await docxResponse.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'Attorney_Notes_Template.docx';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // Success feedback
        button.innerHTML = `
            <svg class="h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
            Downloaded!
        `;
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 2000);
        
    } catch (error) {
        console.error('Error downloading DOCX:', error);
        showMessage('Error downloading template. Please try again.', 'error');
        
        // Reset button
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Test iCloud connection (v1.9.0 NEW session-based authentication)
async function testICloudConnection() {
    console.log("="*60);
    console.log("🔍 CLIENT: iCloud Test Sync Button Clicked - v1.9.0");
    console.log("📊 Using NEW session-based iCloudPD authentication");
    console.log("="*60);
    
    const button = document.getElementById('test-icloud-btn');
    const originalText = button.innerHTML;
    
    // Check rate limiting
    const now = Date.now();
    if (lastTestTime && (now - lastTestTime) < TEST_COOLDOWN) {
        const remainingSeconds = Math.ceil((TEST_COOLDOWN - (now - lastTestTime)) / 1000);
        console.log(`⏳ Rate limiting active: ${remainingSeconds}s remaining`);
        showMessage(`Please wait ${remainingSeconds} seconds before testing again to avoid Apple rate limiting.`, 'warning');
        return;
    }
    
    // Get current iCloud settings
    const icloudAccount = document.getElementById('icloud-account').value.trim();
    const icloudPassword = document.getElementById('icloud-password').value.trim();
    const icloudFolder = document.getElementById('icloud-folder').value.trim();
    
    // COMPREHENSIVE DEBUG LOGGING
    console.log('📋 Credentials from form fields:');
    console.log(`   📧 Account: ${icloudAccount}`);
    console.log(`   🔐 Password: ${'*'.repeat(icloudPassword.length)} (length: ${icloudPassword.length})`);
    console.log(`   📂 Folder: ${icloudFolder}`);
    console.log(`   🔢 Password type: ${typeof icloudPassword}`);
    console.log(`   ✅ Expected password: btzp-duba-fpyf-fviy`);
    console.log(`   ❓ Password match: ${icloudPassword === 'btzp-duba-fpyf-fviy'}`);
    
    // Validate required fields
    if (!icloudAccount || !icloudPassword || !icloudFolder) {
        console.log('❌ Missing required fields');
        showSyncMessage('Please enter all iCloud credentials before testing the connection.', 'error');
        return;
    }
    
    try {
        // Show loading state
        button.innerHTML = `
            <svg class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Testing Connection...
        `;
        button.disabled = true;
        
        // First save current settings to ensure they're available for the test
        console.log('💾 Saving settings before test...');
        await saveSettings();
        
        // Test iCloud connection using the NEW v1.9.0 endpoint
        console.log('🚀 Sending test connection request to /api/icloud/test-connection');
        console.log('📡 Request details:');
        console.log('   Method: POST');
        console.log('   Headers: Content-Type: application/json');
        console.log('   Body: (none - credentials read from saved settings file)');
        
        const response = await fetch('/api/icloud/test-connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        console.log(`📡 Response status: ${response.status}`);
        console.log(`📡 Response ok: ${response.ok}`);
        
        const result = await response.json();
        console.log('📨 Full response data:');
        console.log(JSON.stringify(result, null, 2));
        
        // Detailed analysis of response
        if (result.success) {
            console.log('✅ SUCCESS: iCloud authentication test passed!');
            console.log(`📱 Auth method: ${result.authentication_method || 'unknown'}`);
            console.log(`👤 Account: ${result.account || 'unknown'}`);
        } else {
            console.log('❌ FAILED: iCloud authentication test failed');
            console.log(`🚨 Error: ${result.error || 'unknown error'}`);
            
            // Error pattern analysis
            const errorStr = (result.error || '').toLowerCase();
            if (errorStr.includes('rate limit') || errorStr.includes('503')) {
                console.log('⏳ This is Apple rate limiting - expected after multiple tests');
            } else if (errorStr.includes('socket')) {
                console.log('🔌 Socket error - this should be FIXED in v1.9.0!');
            } else if (errorStr.includes('icloudpd')) {
                console.log('📦 iCloudPD dependency issue detected');
            }
        }
        
        if (result.success) {
            // Record successful test time for rate limiting
            lastTestTime = Date.now();
            
            // Success state
            button.innerHTML = `
                <svg class="h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
                Connection Successful!
            `;
            button.classList.remove('bg-blue-600', 'hover:bg-blue-700');
            button.classList.add('bg-green-600', 'hover:bg-green-700');
            
            let message = `iCloud connection successful!`;
            
            // Check if the result indicates cached data
            if (result.message && result.message.includes('cached result')) {
                message = result.message;
            } else if (result.folder_info) {
                const folderInfo = result.folder_info;
                message += ` Found ${folderInfo.folder_count || 0} case folders in "${result.folder}".`;
            } else if (result.note) {
                message += ` ${result.note}`;
            }
            
            showSyncMessage(message, 'success');
            
        } else {
            throw new Error(`Connection failed: ${result.error}`);
        }
        
        // Reset button after 3 seconds
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('bg-green-600', 'hover:bg-green-700');
            button.classList.add('bg-blue-600', 'hover:bg-blue-700');
            button.disabled = false;
        }, 3000);
        
    } catch (error) {
        console.error('Error testing iCloud connection:', error);
        
        // Error state
        button.innerHTML = `
            <svg class="h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
            Connection Failed
        `;
        button.classList.remove('bg-blue-600', 'hover:bg-blue-700');
        button.classList.add('bg-red-600', 'hover:bg-red-700');
        
        // Enhanced error messaging for rate limiting
        let errorMessage = 'iCloud connection failed. Please check your credentials and try again.';
        if (error.message && error.message.includes('503')) {
            errorMessage = 'Apple is temporarily rate limiting requests (503 error). Please wait a few minutes before testing again.';
        } else if (error.message && error.message.includes('Failed to initiate srp authentication')) {
            errorMessage = 'iCloud authentication failed. This may be due to rate limiting or invalid credentials. Please wait 30+ seconds before retrying.';
        }
        
        showSyncMessage(errorMessage, 'error');
        
        // Reset button after 3 seconds
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('bg-red-600', 'hover:bg-red-700');
            button.classList.add('bg-blue-600', 'hover:bg-blue-700');
            button.disabled = false;
        }, 3000);
    }
}

// Creditor Addresses Management
let currentCreditors = [];
let editingCreditorIndex = -1;

async function initializeCreditorAddresses() {
    // Load creditors from server
    await loadCreditorAddresses();
    
    // Set up event listeners
    document.getElementById('add-creditor-btn').addEventListener('click', () => showCreditorModal());
    document.getElementById('close-modal-btn').addEventListener('click', hideCreditorModal);
    document.getElementById('cancel-modal-btn').addEventListener('click', hideCreditorModal);
    document.getElementById('creditor-form').addEventListener('submit', handleCreditorSubmit);
    
    // Close modal when clicking outside
    document.getElementById('creditor-modal').addEventListener('click', (e) => {
        if (e.target.id === 'creditor-modal') {
            hideCreditorModal();
        }
    });
}

async function loadCreditorAddresses() {
    try {
        const response = await fetch('/api/creditor-addresses');
        if (response.ok) {
            const data = await response.json();
            // Convert registry format to list format for UI
            const creditorData = data.creditor_addresses || {};
            currentCreditors = Object.entries(creditorData).map(([key, creditor]) => ({
                name: creditor.legal_name,
                address: {
                    street: creditor.address.street,
                    city: creditor.address.city,
                    state: creditor.address.state,
                    zip_code: creditor.address.zip_code
                },
                category: creditor.cra_type,
                entity_type: creditor.entity_type,
                short_name: creditor.short_name
            }));
            renderCreditorsList();
        } else {
            console.error('Failed to load creditor addresses');
            showMessage('Failed to load creditor addresses', 'error');
        }
    } catch (error) {
        console.error('Error loading creditor addresses:', error);
        showMessage('Error loading creditor addresses', 'error');
    }
}

function renderCreditorsList() {
    const container = document.getElementById('creditors-list');
    
    if (currentCreditors.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <svg class="h-12 w-12 mx-auto mb-4 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                </svg>
                <p>No creditor addresses configured.</p>
                <p class="text-sm mt-1">Click "Add New Creditor" to get started.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    currentCreditors.forEach((creditor, index) => {
        const categoryClass = getCategoryClass(creditor.category);
        html += `
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <div class="flex items-center mb-2">
                            <h4 class="font-semibold text-gray-900">${creditor.name}</h4>
                            <span class="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${categoryClass}">
                                ${creditor.category}
                            </span>
                        </div>
                        <div class="text-sm text-gray-600">
                            <p>${creditor.address.street}</p>
                            <p>${creditor.address.city}, ${creditor.address.state} ${creditor.address.zip_code}</p>
                        </div>
                    </div>
                    <div class="ml-4 flex space-x-2">
                        <button onclick="editCreditor(${index})" class="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm">
                            Edit
                        </button>
                        <button onclick="deleteCreditor(${index})" class="px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm">
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function getCategoryClass(category) {
    switch (category) {
        case 'Credit Bureau':
            return 'bg-blue-100 text-blue-800';
        case 'Bank':
            return 'bg-green-100 text-green-800';
        case 'Credit Card Company':
            return 'bg-purple-100 text-purple-800';
        case 'Collection Agency':
            return 'bg-red-100 text-red-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
}

function showCreditorModal(creditorIndex = -1) {
    const modal = document.getElementById('creditor-modal');
    const form = document.getElementById('creditor-form');
    const modalTitle = document.getElementById('modal-title');
    const saveBtnText = document.getElementById('save-btn-text');
    
    editingCreditorIndex = creditorIndex;
    
    if (creditorIndex >= 0) {
        // Editing existing creditor
        const creditor = currentCreditors[creditorIndex];
        modalTitle.textContent = 'Edit Creditor';
        saveBtnText.textContent = 'Update Creditor';
        
        // Populate form with existing data
        document.getElementById('creditor-name').value = creditor.name;
        document.getElementById('creditor-street').value = creditor.address.street;
        document.getElementById('creditor-city').value = creditor.address.city;
        document.getElementById('creditor-state').value = creditor.address.state;
        document.getElementById('creditor-zip').value = creditor.address.zip_code;
        document.getElementById('creditor-category').value = creditor.category;
    } else {
        // Adding new creditor
        modalTitle.textContent = 'Add New Creditor';
        saveBtnText.textContent = 'Save Creditor';
        form.reset();
    }
    
    modal.classList.remove('hidden');
}

function hideCreditorModal() {
    const modal = document.getElementById('creditor-modal');
    modal.classList.add('hidden');
    editingCreditorIndex = -1;
}

async function handleCreditorSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const creditorData = {
        name: formData.get('name'),
        address: {
            street: formData.get('street'),
            city: formData.get('city'),
            state: formData.get('state').toUpperCase(),
            zip_code: formData.get('zip_code')
        },
        formatted_address: `${formData.get('street')}\n${formData.get('city')}, ${formData.get('state').toUpperCase()} ${formData.get('zip_code')}`,
        category: formData.get('category')
    };
    
    if (editingCreditorIndex >= 0) {
        // Update existing creditor
        currentCreditors[editingCreditorIndex] = creditorData;
    } else {
        // Add new creditor
        currentCreditors.push(creditorData);
    }
    
    // Save to server
    await saveCreditorAddresses();
    
    // Update UI
    renderCreditorsList();
    hideCreditorModal();
    
    const action = editingCreditorIndex >= 0 ? 'updated' : 'added';
    showMessage(`Creditor ${action} successfully!`, 'success');
}

async function saveCreditorAddresses() {
    try {
        // Convert list format back to registry format
        const creditorAddresses = {};
        currentCreditors.forEach((creditor, index) => {
            const key = creditor.name.toLowerCase().replace(/[^a-z0-9]/g, '_');
            creditorAddresses[key] = {
                legal_name: creditor.name,
                short_name: creditor.short_name || creditor.name.split(' ')[0].toUpperCase(),
                address: creditor.address,
                entity_type: creditor.entity_type || "corporation, authorized to do business in New York",
                cra_type: creditor.category
            };
        });

        const response = await fetch('/api/creditor-addresses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                creditor_addresses: creditorAddresses
            })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to save creditor addresses: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error saving creditor addresses:', error);
        showMessage('Error saving creditor addresses', 'error');
        throw error;
    }
}

function editCreditor(index) {
    showCreditorModal(index);
}

async function deleteCreditor(index) {
    const creditor = currentCreditors[index];
    
    if (!confirm(`Are you sure you want to delete "${creditor.name}"? This action cannot be undone.`)) {
        return;
    }
    
    currentCreditors.splice(index, 1);
    
    try {
        await saveCreditorAddresses();
        renderCreditorsList();
        showMessage('Creditor deleted successfully!', 'success');
    } catch (error) {
        // Re-add the creditor if save failed
        currentCreditors.splice(index, 0, creditor);
        showMessage('Failed to delete creditor', 'error');
    }
}

// Sync cases from iCloud
async function syncICloudCases() {
    const button = document.getElementById('sync-icloud-btn');
    const originalText = button.innerHTML;
    
    // Get current iCloud settings
    const icloudAccount = document.getElementById('icloud-account').value.trim();
    const icloudPassword = document.getElementById('icloud-password').value.trim();
    const icloudFolder = document.getElementById('icloud-folder').value.trim();
    
    // Validate required fields
    if (!icloudAccount || !icloudPassword || !icloudFolder) {
        showSyncMessage('Please enter all iCloud credentials before syncing cases.', 'error');
        return;
    }
    
    try {
        // Show loading state
        button.innerHTML = `
            <svg class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Syncing Cases...
        `;
        button.disabled = true;
        
        // First save current settings to ensure they're available for the sync
        await saveSettings();
        
        // Start sync operation
        const response = await fetch('/api/icloud/sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Success state
            button.innerHTML = `
                <svg class="h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
                Sync Complete!
            `;
            button.classList.remove('bg-green-600', 'hover:bg-green-700');
            button.classList.add('bg-blue-600', 'hover:bg-blue-700');
            
            let message = `iCloud sync successful!`;
            
            if (result.synced_cases && result.synced_cases.length > 0) {
                message += ` Synced ${result.synced_cases.length} cases: ${result.synced_cases.map(c => c.name).join(', ')}.`;
            } else {
                message += ' All cases are already up to date.';
            }
            
            if (result.errors && result.errors.length > 0) {
                message += ` Note: ${result.errors.length} errors occurred during sync.`;
            }
            
            showSyncMessage(message, 'success');
            
        } else {
            throw new Error(`Sync failed: ${result.error}`);
        }
        
        // Reset button after 3 seconds
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
            button.classList.remove('bg-blue-600', 'hover:bg-blue-700');
            button.classList.add('bg-green-600', 'hover:bg-green-700');
        }, 3000);
        
    } catch (error) {
        console.error('Error syncing iCloud cases:', error);
        showSyncMessage('iCloud sync failed. Please check your connection and try again.', 'error');
        
        // Reset button
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Make functions globally accessible
window.hideMessage = hideMessage;
window.editCreditor = editCreditor;
window.deleteCreditor = deleteCreditor;