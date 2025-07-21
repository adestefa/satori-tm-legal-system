// dashboard/static/js/main.js - Manifest-based Processing System

console.log(`🚀 MAIN: Loading main.js module...`);

import { getVersion, getCases, getCaseManifest } from './api.js';
import { renderVersion, showToast, renderCases, renderLoadingState } from './ui.js';
import { initializeEventListeners, updateFilterCounts } from './eventHandlers.js';

// --- State Management ---
// This object will keep track of active polling intervals for each case
const activePollers = {};

// --- Authentication and User Management ---
async function loadUserInfo() {
    try {
        const response = await fetch('/api/auth/verify', { credentials: 'include' });
        if (response.ok) {
            const userInfo = await response.json();
            updateUserDisplay(userInfo.username);
        } else {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error loading user info:', error);
        window.location.href = '/login';
    }
}

function updateUserDisplay(username) {
    const userInitials = document.getElementById('user-initials');
    const userDisplayName = document.getElementById('user-display-name');
    const dropdownUsername = document.getElementById('dropdown-username');
    
    if (userInitials) userInitials.textContent = username.substring(0, 2).toUpperCase();
    if (userDisplayName) userDisplayName.textContent = username;
    if (dropdownUsername) dropdownUsername.textContent = username;
}

async function handleLogout() {
    try {
        const response = await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
        if (response.ok) {
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
        userMenuButton.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('hidden');
        });
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

// --- Core Application Logic ---

/**
 * Parses the manifest content and returns a structured object of file statuses.
 * @param {string} manifestContent - The raw text content of the manifest file.
 * @returns {Object} - An object where keys are filenames and values are their status info.
 */
function parseManifest(manifestContent) {
    const fileStatus = {};
    const lines = manifestContent.trim().split('\n');
    let overallCaseStatus = 'PROCESSING'; // Default to processing unless specified otherwise

    // Read case status from first line only (O(1) efficiency)
    if (lines.length > 0) {
        const firstLine = lines[0];
        const parts = firstLine.split('|');
        if (parts.length >= 2 && parts[0] === 'CASE_STATUS') {
            overallCaseStatus = parts[1];
        }
    }

    // Process file entries from lines 2+ only
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i];
        const parts = line.split('|');
        if (parts.length >= 2) {
            const filename = parts[0];
            const status = parts[1];
            fileStatus[filename] = { status: status };
        }
    }

    return { fileStatus, overallCaseStatus };
}

/**
 * Updates the file status icons in the UI for a specific case.
 * @param {string} caseId - The ID of the case to update.
 * @param {Object} fileStatus - The file status object from parseManifest.
 */
function updateFileStatusInUI(caseId, fileStatus) {
    const caseCard = document.querySelector(`[data-case-id="${caseId}"]`);
    if (!caseCard) return;

    const fileElements = caseCard.querySelectorAll('.file-item');
    fileElements.forEach(fileElement => {
        const fileName = fileElement.getAttribute('data-file-name');
        const iconElement = fileElement.querySelector('.file-status-icon');
        
        if (fileStatus[fileName] && iconElement) {
            let icon = '☐'; // default
            switch (fileStatus[fileName].status) {
                case 'processing': icon = '⏳'; break;
                case 'success': icon = '✅'; break;
                case 'error': icon = '❌'; break;
            }
            iconElement.textContent = icon;
        }
    });
}

/**
 * Starts a self-terminating polling mechanism to check the manifest for a processing case.
 * @param {string} caseId - The ID of the case to poll.
 */
function startManifestPolling(caseId) {
    // Prevent duplicate pollers for the same case
    if (activePollers[caseId]) {
        console.log(`📝 Polling already active for case ${caseId}.`);
        return;
    }

    console.log(`🚀 Starting manifest polling for case ${caseId}.`);

    activePollers[caseId] = setInterval(async () => {
        try {
            const manifestContent = await getCaseManifest(caseId);
            if (!manifestContent) return;

            const { fileStatus, overallCaseStatus } = parseManifest(manifestContent);
            updateFileStatusInUI(caseId, fileStatus);

            // Check if processing is complete for all files
            const isProcessingFinished = !Object.values(fileStatus).some(f => f.status === 'processing');
            
            // Stop polling if the case is no longer processing or all files are done
            // Check for terminal states: PENDING_REVIEW, COMPLETE, ERROR (anything except PROCESSING)
            const isTerminalState = overallCaseStatus !== 'PROCESSING';
            if (isTerminalState && isProcessingFinished) {
                console.log(`✅ Processing finished for case ${caseId}. Final status: ${overallCaseStatus}. Stopping poller.`);
                clearInterval(activePollers[caseId]);
                delete activePollers[caseId];
                // Once polling stops, refresh the entire case grid to get the final state
                await loadCases();
            }
        } catch (error) {
            console.error(`❌ Error during manifest polling for case ${caseId}:`, error);
            clearInterval(activePollers[caseId]);
            delete activePollers[caseId];
        }
    }, 2000); // Poll every 2 seconds
}

// Make the polling starter globally accessible for the process button's onclick handler
window.startProcessingWithManifest = function(caseId) {
    console.log(`▶️ User triggered processing for case ${caseId}.`);
    // The button click in ui.js already calls the API.
    // We just need to start polling here to update the UI.
    startManifestPolling(caseId);
};

/**
 * Loads and renders all cases from the backend.
 */
async function loadCases() {
    try {
        console.log('🔄 Loading case data...');
        const cases = await getCases();
        
        renderCases(cases);
        updateFilterCounts();
        
        // After rendering, check for any cases that are currently processing and start polling them.
        // This handles cases that were already processing when the page was loaded/refreshed.
        cases.forEach(caseData => {
            if (caseData.status === 'Processing') {
                console.log(`🔄 Case ${caseData.id} is in 'Processing' state. Initiating manifest polling.`);
                startManifestPolling(caseData.id);
            }
        });
        
    } catch (error) {
        console.error('❌ Failed to load cases:', error);
    }
}

/**
 * Initializes the entire dashboard application.
 */
async function initialize() {
    try {
        console.log('🚀 Initializing dashboard...');
        
        await loadUserInfo();
        initializeUserMenu();
        
        const versionData = await getVersion();
        renderVersion(versionData.version);
        
        initializeEventListeners();
        
        const allCasesFilter = document.getElementById('filter-all');
        if (allCasesFilter) {
            allCasesFilter.classList.add('text-blue-600', 'bg-blue-50');
            allCasesFilter.classList.remove('text-slate-600');
        }
        
        renderLoadingState();
        await loadCases(); // Initial load
        
        console.log('✅ Dashboard initialized successfully');
        
    } catch (error) {
        console.error('❌ Failed to initialize dashboard:', error);
        showToast('Failed to initialize dashboard', 'error', 5000);
    }
}

// --- Manual Refresh ---
async function handleManualRefresh() {
    try {
        console.log('🔄 Manual refresh triggered...');
        renderLoadingState();
        await loadCases();
        showToast('Cases refreshed successfully', 'success', 2000);
    } catch (error) {
        console.error('❌ Manual refresh failed:', error);
        showToast('Failed to refresh cases', 'error', 3000);
    }
}

// Make functions globally accessible
window.handleManualRefresh = handleManualRefresh;

// --- DOM Ready Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM loaded, starting initialization...');
    initialize();
});
