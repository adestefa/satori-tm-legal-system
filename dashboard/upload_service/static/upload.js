/**
 * Standalone Case Upload JavaScript
 * 
 * Provides drag & drop file upload functionality with:
 * - Client-side validation
 * - Progress tracking
 * - Error handling
 * - Professional UI feedback
 */

class CaseUploader {
    constructor() {
        this.fileInput = document.getElementById('file-input');
        this.uploadZone = document.getElementById('upload-zone');
        this.uploadProgress = document.getElementById('upload-progress');
        this.progressBar = document.getElementById('progress-bar');
        this.uploadStatus = document.getElementById('upload-status');
        this.successMessage = document.getElementById('success-message');
        this.errorMessage = document.getElementById('error-message');
        this.fileInfo = document.getElementById('file-info');
        this.retryButton = document.getElementById('retry-button');
        
        this.selectedFile = null;
        this.uploadInProgress = false;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Click to open file dialog
        this.uploadZone.addEventListener('click', () => {
            if (!this.uploadInProgress) {
                this.fileInput.click();
            }
        });
        
        // File selection
        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files[0]);
        });
        
        // Drag and drop events
        this.uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadZone.classList.add('drag-over');
        });
        
        this.uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.uploadZone.classList.remove('drag-over');
        });
        
        this.uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadZone.classList.remove('drag-over');
            
            if (!this.uploadInProgress) {
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileSelection(files[0]);
                }
            }
        });
        
        // Retry button
        this.retryButton.addEventListener('click', () => {
            this.resetUploadState();
        });
        
        // Prevent default drag behaviors on document
        document.addEventListener('dragover', (e) => e.preventDefault());
        document.addEventListener('drop', (e) => e.preventDefault());
    }
    
    handleFileSelection(file) {
        if (!file) return;
        
        // Client-side validation
        const validation = this.validateFile(file);
        if (!validation.valid) {
            this.showError('File Validation Failed', validation.errors);
            return;
        }
        
        this.selectedFile = file;
        this.showFileInfo(file);
        
        // Auto-start upload after file selection
        setTimeout(() => {
            this.startUpload();
        }, 500);
    }
    
    validateFile(file) {
        const errors = [];
        
        // Check file type
        if (!file.name.toLowerCase().endsWith('.zip')) {
            errors.push('File must be a ZIP archive (.zip)');
        }
        
        // Check file size (50MB limit)
        const maxSize = 50 * 1024 * 1024; // 50MB
        if (file.size > maxSize) {
            const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
            errors.push(`File too large: ${sizeMB}MB exceeds 50MB limit`);
        }
        
        // Check minimum size
        if (file.size < 1024) {
            errors.push('File too small to be a valid ZIP archive');
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
    
    showFileInfo(file) {
        const fileName = document.getElementById('file-name');
        const fileSize = document.getElementById('file-size');
        
        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);
        
        this.fileInfo.classList.remove('hidden');
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async startUpload() {
        if (!this.selectedFile || this.uploadInProgress) return;
        
        this.uploadInProgress = true;
        this.hideMessages();
        this.showProgress();
        
        try {
            await this.uploadFile(this.selectedFile);
        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Upload Failed', [error.message || 'An unexpected error occurred']);
        } finally {
            this.uploadInProgress = false;
        }
    }
    
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Simulate progress for better UX
        this.updateProgress(10, 'Validating file...');
        
        const response = await fetch('/api/upload/cases', {
            method: 'POST',
            body: formData
        });
        
        this.updateProgress(50, 'Processing upload...');
        
        if (!response.ok) {
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            if (errorData.detail && typeof errorData.detail === 'object') {
                throw new Error(errorData.detail.error || 'Upload failed');
            } else {
                throw new Error(errorData.detail || 'Upload failed');
            }
        }
        
        this.updateProgress(90, 'Extracting files...');
        
        const result = await response.json();
        
        this.updateProgress(100, 'Upload complete!');
        
        // Show success after brief delay
        setTimeout(() => {
            this.showSuccess(result);
        }, 500);
    }
    
    updateProgress(percentage, status) {
        this.progressBar.style.width = `${percentage}%`;
        this.uploadStatus.textContent = status;
    }
    
    showProgress() {
        this.uploadProgress.classList.remove('hidden');
        this.updateProgress(0, 'Starting upload...');
    }
    
    hideProgress() {
        this.uploadProgress.classList.add('hidden');
    }
    
    showSuccess(result) {
        this.hideProgress();
        
        const details = document.getElementById('success-details');
        let message = `Successfully uploaded ${result.cases.length} case(s): `;
        message += result.cases.map(c => c.name).join(', ');
        details.textContent = message;
        
        this.successMessage.classList.remove('hidden');
        
        // Auto-redirect after 5 seconds
        setTimeout(() => {
            window.location.href = '/';
        }, 5000);
    }
    
    showError(title, errors) {
        this.hideProgress();
        
        const details = document.getElementById('error-details');
        let message = Array.isArray(errors) ? errors.join('. ') : errors;
        details.textContent = message;
        
        this.errorMessage.classList.remove('hidden');
    }
    
    hideMessages() {
        this.successMessage.classList.add('hidden');
        this.errorMessage.classList.add('hidden');
    }
    
    resetUploadState() {
        this.uploadInProgress = false;
        this.selectedFile = null;
        
        this.hideProgress();
        this.hideMessages();
        this.fileInfo.classList.add('hidden');
        
        // Reset file input
        this.fileInput.value = '';
        
        // Reset upload zone
        this.uploadZone.classList.remove('drag-over');
    }
}

// Initialize upload functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Case Upload System initialized');
    new CaseUploader();
});

// Global error handling
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
});