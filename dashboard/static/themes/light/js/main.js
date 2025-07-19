// dashboard/static/js/main.js - Manifest-based Processing System

console.log(`🚀 MAIN: Loading main.js module...`);

import { getVersion, getCases, getCaseManifest } from './api.js';
import { renderVersion, showToast, renderCases, renderLoadingState } from './ui.js';
import { initializeEventListeners, updateFilterCounts } from './eventHandlers.js';

// Authentication and User Management
async function loadUserInfo() {
    try {
        const response = await fetch('/api/auth/verify', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const userInfo = await response.json();
            updateUserDisplay(userInfo.username);
        } else {
            // User not authenticated, redirect to login
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error loading user info:', error);
        window.location.href = '/login';
    }
}

function updateUserDisplay(username) {
    // Update user display elements
    const userInitials = document.getElementById('user-initials');
    const userDisplayName = document.getElementById('user-display-name');
    const dropdownUsername = document.getElementById('dropdown-username');
    
    if (userInitials) userInitials.textContent = username.substring(0, 2).toUpperCase();
    if (userDisplayName) userDisplayName.textContent = username;
    if (dropdownUsername) dropdownUsername.textContent = username;
}

async function handleLogout() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            // Redirect to login page
            window.location.href = '/login';
        } else {
            showToast('Error signing out', 'error');
        }
    } catch (error) {
        console.error('Error during logout:', error);
        showToast('Error signing out', 'error');
    }
}

function initializeUserMenu() {
    const userMenuButton = document.getElementById('user-menu-button');
    const userDropdown = document.getElementById('user-dropdown');
    const logoutBtn = document.getElementById('logout-btn');
    
    if (userMenuButton && userDropdown) {
        // Toggle dropdown on button click
        userMenuButton.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('hidden');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!userMenuButton.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.add('hidden');
            }
        });
    }
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    }
}

// Store last known data hash to prevent unnecessary updates
let lastDataHash = null;
let pollingActive = true;

// Manifest processing storage
let manifestPollingIntervals = new Map(); // caseId -> intervalId
let currentManifestStates = new Map(); // caseId -> fileStatusMap

// Parse manifest content into file status map
function parseManifest(manifestContent) {
    console.log(`🎬 ANIMATION: Parsing manifest content:`, manifestContent);
    
    const fileStatus = {};
    
    if (!manifestContent || manifestContent.trim() === '') {
        console.log(`🎬 ANIMATION: Empty manifest content`);
        return fileStatus;
    }
    
    const lines = manifestContent.split('\n').filter(line => line.trim());
    console.log(`🎬 ANIMATION: Found ${lines.length} lines in manifest`);
    
    lines.forEach((line, index) => {
        console.log(`🎬 ANIMATION: Line ${index + 1}: ${line}`);
        const parts = line.split('|');
        if (parts.length >= 7) {
            const [filename, status, startTime, endTime, fileSize, processingTime, errorMessage] = parts;
            
            fileStatus[filename] = {
                status,
                startTime: startTime === 'null' ? null : startTime,
                endTime: endTime === 'null' ? null : endTime,
                fileSize: fileSize === 'null' ? null : parseInt(fileSize),
                processingTime: processingTime === 'null' ? null : parseInt(processingTime),
                errorMessage: errorMessage === 'null' ? null : errorMessage
            };
            console.log(`🎬 ANIMATION: Parsed file ${filename} with status ${status}`);
        } else {
            console.log(`🎬 ANIMATION: Invalid line format: ${line} (${parts.length} parts)`);
        }
    });
    
    console.log(`🎬 ANIMATION: Final parsed fileStatus:`, fileStatus);
    return fileStatus;
}

// Start manifest polling for a specific case
function startManifestPolling(caseId) {
    // Stop any existing polling for this case
    stopManifestPolling(caseId);
    
    console.log(`📝 MANIFEST: Starting polling for case ${caseId}`);
    
    const pollManifest = async () => {
        try {
            const manifestContent = await getCaseManifest(caseId);
            const fileStatus = parseManifest(manifestContent);
            
            // Check if manifest state changed
            const currentState = JSON.stringify(fileStatus);
            const lastState = currentManifestStates.get(caseId);
            
            if (currentState !== lastState) {
                console.log(`🎬 ANIMATION: Manifest updated for case ${caseId}`);
                console.log(`🎬 ANIMATION: Previous state:`, lastState ? JSON.parse(lastState) : 'none');
                console.log(`🎬 ANIMATION: Current state:`, fileStatus);
                
                // Check if we have real manifest data and should override spoof animation
                const hasRealData = Object.keys(fileStatus).length > 0;
                if (hasRealData && window.enableManifestOverride) {
                    console.log(`🎬 ANIMATION: Real manifest data detected, overriding spoof animation for ${caseId}`);
                    window.enableManifestOverride(caseId);
                }
                
                currentManifestStates.set(caseId, currentState);
                updateFileStatusInUI(caseId, fileStatus);
                
                // Check if all files are complete (success or error)
                const allComplete = Object.values(fileStatus).every(f => 
                    f.status === 'success' || f.status === 'error'
                );
                
                if (allComplete && Object.keys(fileStatus).length > 0) {
                    console.log(`📝 MANIFEST: All files complete for case ${caseId}, stopping polling`);
                    stopManifestPolling(caseId);
                    
                    // Complete the hybrid animation if it's still running
                    if (window.forceCompleteAnimation) {
                        console.log(`🎬 ANIMATION: Completing hybrid animation due to manifest completion`);
                        window.forceCompleteAnimation(caseId);
                    }
                    
                    // Case data refresh disabled - users can refresh manually
                    // setTimeout(() => {
                    //     loadCases();
                    // }, 1000);
                }
            }
            
        } catch (error) {
            console.error(`📝 MANIFEST: Error polling manifest for case ${caseId}:`, error);
        }
    };
    
    // Poll immediately, then every 100 milliseconds for real-time animation
    pollManifest();
    const intervalId = setInterval(pollManifest, 100);
    manifestPollingIntervals.set(caseId, intervalId);
}

// Stop manifest polling for a specific case
function stopManifestPolling(caseId) {
    const intervalId = manifestPollingIntervals.get(caseId);
    if (intervalId) {
        clearInterval(intervalId);
        manifestPollingIntervals.delete(caseId);
        console.log(`📝 MANIFEST: Stopped polling for case ${caseId}`);
    }
}

// Update file status in the UI
function updateFileStatusInUI(caseId, fileStatus) {
    console.log(`🎬 ANIMATION: Updating UI for case ${caseId} with fileStatus:`, fileStatus);
    
    const caseCard = document.querySelector(`[data-case-id="${caseId}"]`);
    if (!caseCard) {
        console.log(`🎬 ANIMATION: Case card not found for ${caseId}`);
        return;
    }
    
    const fileElements = caseCard.querySelectorAll('.file-item');
    console.log(`🎬 ANIMATION: Found ${fileElements.length} file elements`);
    
    fileElements.forEach((fileElement, index) => {
        const fileName = fileElement.getAttribute('data-file-name');
        const iconElement = fileElement.querySelector('.file-status-icon');
        
        console.log(`🎬 ANIMATION: File ${index + 1}: ${fileName}, has icon: ${!!iconElement}`);
        
        if (fileName && iconElement && fileStatus[fileName]) {
            const status = fileStatus[fileName];
            let icon = '☐'; // default
            
            switch (status.status) {
                case 'processing':
                    icon = '⏳';
                    iconElement.style.animation = 'hourglass-sand 3s ease-in-out infinite';
                    console.log(`🎬 ANIMATION: ${fileName} → PROCESSING (⏳)`);
                    break;
                case 'success':
                    icon = '✅';
                    iconElement.style.animation = 'none';
                    console.log(`🎬 ANIMATION: ${fileName} → SUCCESS (✅)`);
                    break;
                case 'error':
                    icon = '❌';
                    iconElement.style.animation = 'none';
                    console.log(`🎬 ANIMATION: ${fileName} → ERROR (❌)`);
                    break;
                default:
                    icon = '☐';
                    iconElement.style.animation = 'none';
                    console.log(`🎬 ANIMATION: ${fileName} → DEFAULT (☐)`);
                    break;
            }
            
            iconElement.textContent = icon;
            
            // Update title with processing details
            let title = `${fileName}`;
            if (status.fileSize) {
                title += `\nSize: ${formatFileSize(status.fileSize)}`;
            }
            if (status.processingTime) {
                title += `\nProcessing time: ${status.processingTime}ms`;
            }
            if (status.errorMessage) {
                title += `\nError: ${status.errorMessage}`;
            }
            fileElement.title = title;
        }
    });
}

// Format file size for display
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Global function to start processing with manifest tracking
window.startProcessingWithManifest = function(caseId) {
    console.log(`🚀 Starting processing with manifest tracking for case ${caseId}`);
    startManifestPolling(caseId);
};

// Animation functions are now in ani.js module

// Calculate simple hash of case data for comparison
function calculateCasesHash(cases) {
    const dataForHash = cases.map(c => ({
        id: c.id,
        status: c.status,
        last_updated: c.last_updated,
        file_count: c.files ? c.files.length : 0,
        progress: c.progress,
        file_processing_results: c.file_processing_results || []
    }));
    
    const dataStr = JSON.stringify(dataForHash, null, 0);
    const hash = btoa(dataStr).slice(0, 16);
    
    console.log('🔢 Hash calculation data:', dataForHash);
    console.log('🔢 Hash string:', dataStr.substring(0, 100) + '...');
    console.log('🔢 Generated hash:', hash);
    
    return hash;
}

// Load existing manifest states for all cases on page load
async function loadExistingManifestStates() {
    try {
        console.log('📝 MANIFEST: Loading existing manifest states on page load...');
        const cases = await getCases();
        
        for (const caseData of cases) {
            if (caseData.status === 'Processing' || caseData.status === 'NEW') {
                try {
                    const manifestContent = await getCaseManifest(caseData.id);
                    if (manifestContent && manifestContent.trim()) {
                        const fileStatus = parseManifest(manifestContent);
                        
                        // Check if any files are still processing
                        const hasProcessingFiles = Object.values(fileStatus).some(f => 
                            f.status === 'processing'
                        );
                        
                        if (hasProcessingFiles) {
                            console.log(`📝 MANIFEST: Found active processing for case ${caseData.id}, starting polling`);
                            startManifestPolling(caseData.id);
                        }
                        
                        // Update UI with current manifest state
                        updateFileStatusInUI(caseData.id, fileStatus);
                    }
                } catch (error) {
                    console.log(`📝 MANIFEST: No existing manifest for case ${caseData.id}`);
                }
            }
        }
    } catch (error) {
        console.error('❌ Failed to load existing manifest states:', error);
    }
}

// Load and render cases with delta detection
async function loadCases() {
    if (!pollingActive) return;
    
    try {
        console.log('🔄 Polling cases...');
        const cases = await getCases();
        const currentHash = calculateCasesHash(cases);
        
        console.log('📊 Current hash:', currentHash);
        console.log('📊 Last hash:', lastDataHash);
        console.log('📊 Case statuses:', cases.map(c => `${c.name}: ${c.status}`));
        
        // Only update DOM if data actually changed
        if (currentHash !== lastDataHash) {
            console.log('✅ Case data changed, updating display');
            renderCases(cases);
            updateFilterCounts(); // Update filter counts after rendering cases
            lastDataHash = currentHash;
        } else {
            console.log('⚪ No changes detected, skipping DOM update');
        }
        
    } catch (error) {
        console.error('❌ Failed to load cases:', error);
        // Don't show error toast on every polling failure
    }
}

// Initialize dashboard with JavaScript polling
async function initialize() {
    try {
        console.log('🚀 Initializing dashboard with JavaScript polling...');
        
        // Load and verify user authentication
        await loadUserInfo();
        
        // Initialize user menu
        initializeUserMenu();
        
        // Load version info
        const versionData = await getVersion();
        renderVersion(versionData.version);
        
        // Initialize event handlers
        initializeEventListeners();
        
        // Set up default filter state (All Cases should be selected by default)
        const allCasesFilter = document.getElementById('filter-all');
        if (allCasesFilter) {
            allCasesFilter.classList.add('text-blue-600', 'bg-blue-50');
            allCasesFilter.classList.remove('text-slate-600');
        }
        
        // Load cases initially
        renderLoadingState();
        await loadCases();
        
        // Update filter counts after cases are loaded
        updateFilterCounts();
        
        // Load existing manifest states to restore processing status
        await loadExistingManifestStates();
        
        // POLLING DISABLED - Users can refresh manually to see changes
        // setInterval(loadCases, 10000);
        
        console.log('✅ Dashboard initialized successfully');
        
    } catch (error) {
        console.error('❌ Failed to initialize dashboard:', error);
        showToast('Failed to initialize dashboard', 'error', 5000);
    }
}

// Manual refresh function for sync button
async function handleManualRefresh() {
    try {
        console.log('🔄 Manual refresh triggered...');
        
        // Trigger HTMX refresh of the case grid
        const caseGrid = document.getElementById('case-grid');
        if (caseGrid) {
            // Use HTMX to refresh the grid
            htmx.trigger(caseGrid, 'refresh');
        }
        
        showToast('Cases refreshed successfully', 'success', 2000);
        
    } catch (error) {
        console.error('❌ Manual refresh failed:', error);
        showToast('Failed to refresh cases', 'error', 3000);
    }
}

// Make functions globally accessible
window.handleManualRefresh = handleManualRefresh;

// DOM ready initialization
document.addEventListener('DOMContentLoaded', () => {
    // Version and path verification console logs (v2.1.0)
    console.log('🔍 DASHBOARD VERSION: 2.1.0 - Case upload service added, polling disabled');
    console.log('🔍 TIGER RESOURCES PATH: tiger/app/resources/legal-spec/NY_FCRA.json');
    console.log('📄 DOM loaded, starting initialization...');
    initialize();
});
