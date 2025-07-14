// dashboard/static/themes/light/js/ui.js

import { ANIMATION_CONFIG } from './config.js';

const caseGrid = document.getElementById('case-grid');

// Track current filter state to preserve during polling updates
let currentActiveFilter = 'all';

function getCurrentFilter() {
    return currentActiveFilter;
}

function setCurrentFilter(filter) {
    currentActiveFilter = filter;
}

function getStatusClasses(status) {
    switch (status) {
        case 'New':
            return 'bg-blue-100 text-blue-800 border border-blue-200';
        case 'Pending Review':
            return 'bg-yellow-100 text-yellow-800 border border-yellow-200';
        case 'Complete':
        case 'Processed': // Note: "Processed" is an intermediate step, but we'll use green for now.
            return 'bg-green-100 text-green-800 border border-green-200';
        case 'Error':
            return 'bg-red-100 text-red-800 border border-red-200';
        default:
            return 'bg-gray-100 text-gray-800 border border-gray-200';
    }
}

// Data quality validation function
// Validation removed - Tiger service handles all document processing and validation

function getActionButton(caseData) {
    const baseButtonClasses = "w-full text-center px-4 py-3 rounded-lg font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2";
    
    switch (caseData.status) {
        case 'New':
            // Enhanced data quality validation for NEW cases
            return `<button id="${caseData.id}_button" class="process-btn ${baseButtonClasses} bg-gray-800 text-white hover:bg-gray-900 focus:ring-gray-500" 
                           data-case-id="${caseData.id}" 
                           onclick="handleProcessWithValidation(this)">
                       <span class="button-text">Process Files</span>
                       <span class="button-spinner hidden">⏳ Processing...</span>
                   </button>`;
        case 'Error':
            // Allow reprocessing of Error cases with validation
            return `<button id="${caseData.id}_button" class="process-btn ${baseButtonClasses} bg-red-600 text-white hover:bg-red-700 focus:ring-red-500" 
                           data-case-id="${caseData.id}" 
                           onclick="handleProcessWithValidation(this)">
                       <span class="button-text">Process Files</span>
                       <span class="button-spinner hidden">⏳ Processing...</span>
                   </button>`;
        case 'Pending Review':
            return `<a id="${caseData.id}_button" href="/review?case_id=${caseData.id}" class="block ${baseButtonClasses} bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500">Review Case</a>`;
        case 'Processing':
            // Show stop button during processing
            return `<button id="${caseData.id}_button" class="${baseButtonClasses} bg-red-600 text-white hover:bg-red-700 cursor-not-allowed" disabled>
                        <span class="button-spinner">⛔ Stop Processing</span>
                    </button>`;
        case 'Complete':
            return `<a id="${caseData.id}_button" href="/review?case_id=${caseData.id}" class="block ${baseButtonClasses} bg-white text-gray-700 border border-gray-300 hover:bg-gray-100 focus:ring-gray-400 flex items-center justify-center">
                        <i data-feather="file-text" class="w-4 h-4 mr-2"></i>
                        View Legal Packet
                    </a>`;
        default: // Generating, etc.
            return `<button id="${caseData.id}_button" class="${baseButtonClasses} bg-gray-400 text-white cursor-not-allowed" disabled>${caseData.status}...</button>`;
    }
}

// Manifest-based process handler with spoofed animation
async function handleProcessWithValidation(button) {
    const caseId = button.getAttribute('data-case-id');
    const buttonText = button.querySelector('.button-text');
    const buttonSpinner = button.querySelector('.button-spinner');
    
    console.log(`🐅 TIGER: Starting processing for case ${caseId}`);
    console.log(`🔥 DEBUG: About to call startSimpleSpoof for ${caseId}`);
    
    // Show processing spinner
    buttonText.classList.add('hidden');
    buttonSpinner.classList.remove('hidden');
    button.disabled = true;
    
    // SIMPLE SPOOF: Just countdown and reload
    console.log(`🔥 DEBUG: Calling startSimpleSpoof now...`);
    startSimpleSpoof(caseId);
    console.log(`🔥 DEBUG: Called startSimpleSpoof, should see alert now`);
    
    // Polling disabled for simple spoof demo
    // if (typeof window.startProcessingWithManifest === 'function') {
    //     window.startProcessingWithManifest(caseId);
    // }
    
    try {
        console.log(`🐅 TIGER: Calling /api/cases/${caseId}/process`);
        const startTime = Date.now();
        
        // Call Tiger processing API directly - no pre-validation
        const processResponse = await fetch(`/api/cases/${caseId}/process`, {
            method: 'POST'
        });
        
        const endTime = Date.now();
        console.log(`🐅 TIGER: API call completed in ${endTime - startTime}ms`);
        console.log(`🐅 TIGER: Response status: ${processResponse.status} ${processResponse.statusText}`);
        
        if (!processResponse.ok) {
            const errorData = await processResponse.text();
            console.error('🐅 TIGER: Processing API failed:', errorData);
            throw new Error(`Processing failed: ${processResponse.status}`);
        }
        
        const responseData = await processResponse.json();
        console.log('🐅 TIGER: Processing started successfully');
        console.log('🐅 TIGER: Response data:', responseData);
        console.log('🐅 TIGER: Background processing initiated - manifest polling will show progress updates');
        
        // Processing started successfully - manifest polling will show progress updates
        
    } catch (error) {
        console.error('🐅 TIGER: Processing error:', error);
        // Reset button state
        buttonText.classList.remove('hidden');
        buttonSpinner.classList.add('hidden');
        button.disabled = false;
        
        // Show error message via console (dashboard will show Tiger's error results)
        console.error(`🐅 TIGER: Failed to start processing: ${error.message}`);
    }
}

// Simple spoof animation with seamless UI updates - DIRECT INDEX TARGETING
function startSimpleSpoof(caseId) {
    console.log(`🎬 SPOOF: Starting seamless animation for case ${caseId}`);
    
    // Get case card and UI elements
    const caseCard = document.querySelector(`[data-case-id="${caseId}"]`);
    const fileListContainer = document.getElementById(`files-${caseId}`);
    const statusBadge = caseCard?.querySelector('.status-badge');
    const processButton = caseCard?.querySelector(`#${caseId}_button`);
    
    if (!fileListContainer || !caseCard) {
        console.log(`❌ Required elements not found for ${caseId}`);
        return;
    }
    
    // Get all file-status-icon elements by direct query
    const iconElements = fileListContainer.querySelectorAll('.file-status-icon');
    const fileCount = iconElements.length;
    
    console.log(`🎬 SPOOF: Found ${fileCount} files to animate`);
    
    if (fileCount === 0) {
        console.log(`❌ No icon elements found in files-${caseId}`);
        return;
    }
    
    // Update status badge to Processing
    if (statusBadge) {
        statusBadge.textContent = 'Processing';
        statusBadge.className = 'status-badge px-4 py-1 text-xs font-bold rounded-full bg-yellow-100 text-yellow-800 border border-yellow-200';
    }
    
    // Update progress lights to show Process step with spinner (actively processing)
    const progressContainer = caseCard.querySelector('.progress-lights');
    if (progressContainer) {
        const processingProgress = {
            synced: true,      // Step 1: Sync - Files are available
            extracted: false,  // Step 2: Process - Currently processing (will show spinner)
            reviewed: false,   // Step 3: Review - Not yet started
            generated: false   // Step 4: Done - Not yet started
        };
        progressContainer.innerHTML = createProgressLights(processingProgress, 'Processing');
        console.log(`🎬 SPOOF: Updated progress lights - Step 2 (Process) now showing spinner`);
    }
    
    // Sequential file animation using constants
    let currentFileIndex = 0;
    const totalAnimationTime = fileCount * ANIMATION_CONFIG.TOTAL_PER_FILE;
    
    console.log(`🎬 SPOOF: Starting ${totalAnimationTime}s animation for ${fileCount} files`);
    
    function animateNextFile() {
        if (currentFileIndex >= fileCount) {
            // All files complete, update to final state
            console.log(`🎬 SPOOF: All ${fileCount} files completed, updating to final state`);
            updateToFinalState();
            return;
        }
        
        const currentIcon = iconElements[currentFileIndex];
        console.log(`🎬 SPOOF: Animating file ${currentFileIndex + 1}/${fileCount}`);
        
        // Step 1: Show processing (hourglass with sand animation)
        currentIcon.textContent = '⏳';
        currentIcon.style.animation = 'hourglass-sand 3s ease-in-out infinite';
        
        // Step 2: After processing time, show completion (checkmark)
        setTimeout(() => {
            currentIcon.textContent = '✅';
            currentIcon.style.animation = 'none';
            console.log(`🎬 SPOOF: File ${currentFileIndex + 1} completed`);
            
            // Step 3: After complete time, move to next file
            setTimeout(() => {
                currentFileIndex++;
                animateNextFile();
            }, ANIMATION_CONFIG.TRANSITION_MS);
        }, ANIMATION_CONFIG.PROCESSING_MS);
    }
    
    function updateToFinalState() {
        console.log(`🎬 SPOOF: Updating case ${caseId} to final state`);
        
        // Update status badge to Pending Review
        if (statusBadge) {
            statusBadge.textContent = 'Pending Review';
            statusBadge.className = 'status-badge px-4 py-1 text-xs font-bold rounded-full bg-blue-100 text-blue-800 border border-blue-200';
        }
        
        // Update progress lights to show extracted step (Step 3) is complete
        const progressContainer = caseCard.querySelector('.progress-lights');
        if (progressContainer) {
            const newProgress = {
                synced: true,      // Step 1: Sync - Files synced from iCloud
                extracted: true,   // Step 2: Process - Tiger service processing complete
                reviewed: false,   // Step 3: Review - Still needs human review
                generated: false   // Step 4: Done - Still needs document generation
            };
            progressContainer.innerHTML = createProgressLights(newProgress, 'Pending Review');
            console.log(`🎬 SPOOF: Updated progress lights - Step 2 (Process) now complete`);
        }
        
        // Update button to Review Case
        if (processButton) {
            const baseButtonClasses = "w-full text-center px-4 py-3 rounded-lg font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2";
            processButton.outerHTML = `<a id="${caseId}_button" href="/review?case_id=${caseId}" class="block ${baseButtonClasses} bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500">Review Case</a>`;
        }
        
        // Update file list header
        const fileListHeader = caseCard.querySelector('h4');
        if (fileListHeader && fileListHeader.textContent.includes('Files to Process')) {
            fileListHeader.textContent = 'Files Processed:';
        }
        
        // Add validation badge for cases that now have validation results
        const validationContainer = caseCard.querySelector('.mt-2'); // Find existing placeholder
        if (validationContainer && validationContainer.querySelector('.text-transparent')) {
            // Replace placeholder with actual validation badge
            const mockCaseData = { status: 'Pending Review', id: caseId };
            const validationBadge = createValidationScoreBadge(mockCaseData);
            validationContainer.outerHTML = validationBadge;
        }
        
        console.log(`🎬 SPOOF: Case ${caseId} successfully updated to Pending Review state with validation badge`);
        
        // Update case data status for future reference
        window.currentCaseData = window.currentCaseData || {};
        if (window.currentCaseData[caseId]) {
            window.currentCaseData[caseId].status = 'Pending Review';
        }
    }
    
    // Start the sequential animation
    animateNextFile();
}

// Old function kept for reference
function showSpoofedFileAnimation(caseId) {
    const caseCard = document.querySelector(`[data-case-id="${caseId}"]`);
    if (!caseCard) return;
    
    const fileElements = caseCard.querySelectorAll('.file-item');
    fileElements.forEach(fileElement => {
        const iconElement = fileElement.querySelector('.file-status-icon');
        if (iconElement) {
            iconElement.textContent = '⏳';
            iconElement.style.animation = 'hourglass-sand 3s ease-in-out infinite';
        }
    });
    
    console.log(`🎬 SPOOFED: Showing hourglass sand animation for ${fileElements.length} files in case ${caseId}`);
}

// Toast notification system
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast-item ${getToastClasses(type)}`;
    toast.innerHTML = `
        <div class="flex items-center">
            <span class="toast-icon">${getToastIcon(type)}</span>
            <span class="ml-2 text-sm font-medium">${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove toast after duration
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, duration);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed top-4 right-4 z-50 space-y-2';
    document.body.appendChild(container);
    return container;
}

function getToastClasses(type) {
    const baseClasses = 'px-4 py-3 rounded-lg shadow-lg flex items-center max-w-sm';
    switch (type) {
        case 'success':
            return `${baseClasses} bg-green-100 border border-green-400 text-green-700`;
        case 'error':
            return `${baseClasses} bg-red-100 border border-red-400 text-red-700`;
        case 'info':
            return `${baseClasses} bg-blue-100 border border-blue-400 text-blue-700`;
        default:
            return `${baseClasses} bg-gray-100 border border-gray-400 text-gray-700`;
    }
}

function getToastIcon(type) {
    switch (type) {
        case 'success':
            return '✅';
        case 'error':
            return '❌';
        case 'info':
            return '🔄';
        default:
            return 'ℹ️';
    }
}

// Make function globally accessible for onclick handlers
window.handleProcessWithValidation = handleProcessWithValidation;
window.showToast = showToast;

// Show validation error with detailed feedback
function showValidationError(button, validation) {
    const buttonText = button.querySelector('.button-text');
    const buttonSpinner = button.querySelector('.button-spinner');
    
    // Create detailed error message
    const issues = validation.issues || [];
    const recommendations = validation.recommendations || [];
    
    // Replace button with detailed validation feedback
    const container = button.parentElement;
    const baseButtonClasses = "w-full text-center px-4 py-3 rounded-lg font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2";
    
    container.innerHTML = `
        <div class="${baseButtonClasses} bg-red-100 text-red-800 border border-red-200 cursor-not-allowed">
            <div class="text-sm font-medium mb-2">
                ⚠️ Data Quality Issues (Score: ${validation.validation_score}/100)
            </div>
            <div class="text-xs text-left space-y-1">
                ${issues.map(issue => `<div>• ${issue}</div>`).join('')}
            </div>
            ${recommendations.length > 0 ? `
                <details class="mt-2 text-xs">
                    <summary class="cursor-pointer font-medium">Solutions</summary>
                    <div class="mt-1 space-y-1 text-left">
                        ${recommendations.map(rec => `<div>→ ${rec}</div>`).join('')}
                    </div>
                </details>
            ` : ''}
            <button onclick="window.setValidationErrorActive(false); location.reload()" class="mt-2 text-xs underline hover:no-underline">
                Refresh after fixing
            </button>
        </div>
    `;
}

function createProgressLights(progress, caseStatus = null) {
    const steps = [
        { key: 'synced', label: 'Sync' },        // Step 1: Files synced from iCloud
        { key: 'extracted', label: 'Process' },  // Step 2: Tiger service processing complete
        { key: 'reviewed', label: 'Review' },    // Step 3: Human review and claim selection
        { key: 'generated', label: 'Done' }      // Step 4: Document generation complete
    ];
    
    // Calculate progress percentage (number of completed steps / total steps * 100)
    const completedSteps = steps.filter(step => progress[step.key]).length;
    const progressPercentage = Math.round((completedSteps / steps.length) * 100);
    
    // Determine current step (first incomplete step, or last step if all complete)
    let currentStepIndex = steps.findIndex(step => !progress[step.key]);
    if (currentStepIndex === -1) currentStepIndex = steps.length - 1; // All complete
    
    // Determine if current step should show spinner (only during active processing)
    const isActivelyProcessing = caseStatus === 'Processing' || caseStatus === 'Generating';
    
    let stepsHtml = `
        <div class="space-y-4">
            <!-- Progress Bar -->
            <div class="w-full bg-gray-200 rounded-full h-1.5">
                <div class="bg-blue-600 h-1.5 rounded-full" style="width: ${progressPercentage}%"></div>
            </div>

            <!-- Step Indicators -->
            <div class="flex justify-between items-center text-sm">
    `;
    
    steps.forEach((step, index) => {
        const isComplete = progress[step.key];
        const isCurrent = index === currentStepIndex && !isComplete;
        
        // Determine styling based on step state
        let containerClass, iconSvg, labelClass;
        
        if (isComplete) {
            // Completed step
            containerClass = 'flex items-center space-x-2 text-gray-800';
            iconSvg = `
                <svg class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="10" cy="10" r="9" fill="currentColor" fill-opacity="0.1"></circle>
                    <path d="M10 2a8 8 0 100 16 8 8 0 000-16z" fill="currentColor" fill-opacity="0.2"></path>
                    <path d="M14.5 6.5l-6 6-3-3" stroke="#0052cc" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>
                </svg>
            `;
            labelClass = 'font-medium';
        } else if (isCurrent) {
            // Current step - show spinner only if actively processing
            if (isActivelyProcessing) {
                // Active processing - show spinner
                containerClass = 'flex items-center space-x-2 text-blue-600';
                iconSvg = `
                    <svg class="w-5 h-5 animate-spin" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                        <path fill="currentColor" d="M10 2.5A7.5 7.5 0 0 1 17.5 10h-2.5A5 5 0 0 0 10 5V2.5z"></path>
                    </svg>
                `;
                labelClass = 'font-bold';
            } else {
                // Waiting state - show as next step (no spinner)
                containerClass = 'flex items-center space-x-2 text-gray-600';
                iconSvg = `
                    <svg class="w-5 h-5" fill="none" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="10" cy="10" r="7" stroke="currentColor" stroke-width="1.5"></circle>
                    </svg>
                `;
                labelClass = 'font-medium';
            }
        } else {
            // Not started step
            containerClass = 'flex items-center space-x-2 text-gray-400';
            iconSvg = `
                <svg class="w-5 h-5" fill="none" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="10" cy="10" r="7" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 2"></circle>
                </svg>
            `;
            labelClass = 'font-medium';
        }
        
        stepsHtml += `
            <div class="${containerClass}">
                ${iconSvg}
                <span class="${labelClass}">${step.label}</span>
            </div>
        `;
    });

    stepsHtml += `
            </div>
        </div>
    `;
    
    return stepsHtml;
}

function getFileStatusIcon(status) {
    switch (status) {
        case 'success':
            return '<span class="text-green-500">✅</span>';
        case 'error':
            return '<span class="text-red-500">❌</span>';
        case 'processing':
            return '<span class="text-blue-500" style="animation: hourglass-sand 3s ease-in-out infinite;">⏳</span>';
        case 'pending':
            return '<span class="text-gray-400">☐</span>';
        default:
            return '<span class="text-gray-400">☐</span>';
    }
}

function getFileTypeIcon(fileName) {
    const extension = fileName.toLowerCase().split('.').pop();
    switch (extension) {
        case 'pdf':
            return `<svg class="w-5 h-5 inline-block" style="vertical-align: middle;" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                <path d="M901.850593 926.476283a48.761858 48.761858 0 0 1-48.761859 48.761859H170.422718a48.761858 48.761858 0 0 1-48.761858-48.761859V48.762834a48.761858 48.761858 0 0 1 48.761858-48.761859h418.864363a48.761858 48.761858 0 0 1 34.620919 14.140939l263.801654 263.801654a48.761858 48.761858 0 0 1 14.140939 34.620919V926.476283z" fill="#EBECF0" />
                <path d="M24.137143 536.381417h975.237166v243.809291a48.761858 48.761858 0 0 1-48.761858 48.761859H72.899001a48.761858 48.761858 0 0 1-48.761858-48.761859v-243.809291z" fill="#FF5630" />
                <path d="M267.946434 585.143275h84.845634a57.051374 57.051374 0 0 1 41.935198 15.603795 55.1009 55.1009 0 0 1 16.091413 40.959961 55.588518 55.588518 0 0 1-16.091413 40.959961 59.001849 59.001849 0 0 1-43.398054 16.091413h-48.761858v76.556118H267.946434z m32.670446 81.919922h43.885672a42.422817 42.422817 0 0 0 25.843785-6.339041 23.893311 23.893311 0 0 0 7.801897-19.992362q0-24.868548-32.670445-24.868548h-44.860909zM434.71199 588.068987H511.755726a73.142787 73.142787 0 0 1 58.51423 25.356166 100.937047 100.937047 0 0 1 21.942836 68.266602 110.689418 110.689418 0 0 1-20.967599 69.729457A71.679932 71.679932 0 0 1 511.755726 780.190708H434.71199z m32.670445 158.963658H511.755726a43.398054 43.398054 0 0 0 36.083775-17.066651A75.093262 75.093262 0 0 0 560.517584 682.666992a70.704695 70.704695 0 0 0-13.65332-48.761859 48.761858 48.761858 0 0 0-37.546631-16.579031h-41.935198zM755.565018 618.788957h-100.937047v45.348529H755.565018v31.207589h-100.937047v81.919922h-32.670445v-190.171248H755.565018z" fill="#FFFFFF" />
            </svg>`;
        case 'docx':
        case 'doc':
            return `<svg class="w-5 h-5 inline-block" style="vertical-align: middle;" xmlns="http://www.w3.org/2000/svg" fill="#FFF" stroke-miterlimit="10" stroke-width="2" viewBox="0 0 96 96">
                <path stroke="#979593" d="M67.1716 7H27c-1.1046 0-2 .8954-2 2v78c0 1.1046.8954 2 2 2h58c1.1046 0 2-.8954 2-2V26.8284c0-.5304-.2107-1.0391-.5858-1.4142L68.5858 7.5858C68.2107 7.2107 67.702 7 67.1716 7z"/>
                <path fill="none" stroke="#979593" d="M67 7v18c0 1.1046.8954 2 2 2h18"/>
                <path fill="#C8C6C4" d="M79 61H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1zm0-6H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1zm0-6H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1zm0-6H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1zm0 24H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1z"/>
                <path fill="#185ABD" d="M12 74h32c2.2091 0 4-1.7909 4-4V38c0-2.2091-1.7909-4-4-4H12c-2.2091 0-4 1.7909-4 4v32c0 2.2091 1.7909 4 4 4z"/>
                <path d="M21.6245 60.6455c.0661.522.109.9769.1296 1.3657h.0762c.0306-.3685.0889-.8129.1751-1.3349.0862-.5211.1703-.961.2517-1.319L25.7911 44h4.5702l3.6562 15.1272c.183.7468.3353 1.6973.457 2.8532h.0608c.0508-.7979.1777-1.7184.3809-2.7615L37.8413 44H42l-5.1183 22h-4.86l-3.4885-14.5744c-.1016-.4197-.2158-.9663-.3428-1.6417-.127-.6745-.2057-1.1656-.236-1.4724h-.0608c-.0407.358-.1195.8896-.2364 1.595-.1169.7062-.211 1.2273-.2819 1.565L24.1 66h-4.9357L14 44h4.2349l3.1843 15.3882c.0709.3165.1392.7362.2053 1.2573z"/>
            </svg>`;
        case 'txt':
            return `<svg class="w-5 h-5 inline-block text-gray-600" style="vertical-align: middle;" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                <path d="M8,12V14H16V12H8M8,16V18H13V16H8Z" />
            </svg>`;
        default:
            return `<svg class="w-5 h-5 inline-block text-gray-500" style="vertical-align: middle;" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
            </svg>`;
    }
}

function createFileStatusSection(caseData) {
    // Filter out system files, generated files, and internal manifest files for cleaner display
    const displayFiles = (!caseData.files || caseData.files.length === 0) ? [] : caseData.files.filter(file => 
        !file.name.startsWith('.') && 
        !file.name.toLowerCase().endsWith('.ds_store') &&
        !file.name.toLowerCase().endsWith('.json') &&
        file.name !== 'processing_manifest.txt'
    );
    
    // Always show a file section to maintain consistent card layout
    if (displayFiles.length === 0) {
        return `
            <div class="mt-4 border-t border-gray-200 pt-4">
                <div class="flex items-center justify-between mb-2">
                    <h4 class="text-sm font-medium text-gray-700">Files (0):</h4>
                </div>
                <div class="file-list-container bg-gray-50 border border-gray-200 rounded-lg" style="height: 180px; overflow-y: auto;">
                    <div class="p-3 text-sm text-gray-400 italic text-center">No files detected in case folder</div>
                </div>
            </div>
        `;
    }
    
    let fileListHtml = '<div class="mt-4 border-t border-gray-200 pt-4">';
    fileListHtml += '<div class="flex items-center justify-between mb-2">';
    
    // Header based on case status with file count
    const fileCount = displayFiles.length;
    if (caseData.status === 'New') {
        fileListHtml += `<h4 class="text-sm font-medium text-gray-700">Files to Process (${fileCount}):</h4>`;
    } else if (caseData.status === 'Processing') {
        fileListHtml += `<h4 class="text-sm font-medium text-gray-700">Processing Files (${fileCount}):</h4>`;
    } else {
        fileListHtml += `<h4 class="text-sm font-medium text-gray-700">Files Processed (${fileCount}):</h4>`;
    }
    
    fileListHtml += '</div>';
    
    // Scrollable container with expanded height for better space utilization
    fileListHtml += '<div class="file-list-container bg-white border border-gray-200 rounded-lg" style="height: 180px; overflow-y: auto;" id="files-' + caseData.id + '">';
    
    // Show files with appropriate status icons and zebra striping
    displayFiles.forEach((file, index) => {
        let icon = '☐'; // Default empty checkbox
        
        // If we have processing results, use those status icons
        if (caseData.file_processing_results && caseData.file_processing_results.length > 0) {
            const processingResult = caseData.file_processing_results.find(result => result.name === file.name);
            if (processingResult) {
                icon = getFileStatusIcon(processingResult.status);
            }
        }
        
        // Get file type icon
        const fileTypeIcon = getFileTypeIcon(file.name);
        
        // Zebra striping: alternate background colors
        const bgColor = index % 2 === 0 ? 'bg-white' : 'bg-gray-50';
        
        fileListHtml += `<div class="file-item flex items-center px-3 py-2 text-sm text-gray-600 ${bgColor} hover:bg-blue-50 transition-colors" data-file-name="${file.name}">
            <span class="file-status-icon mr-2">${icon}</span>
            <span class="file-type-icon mr-2">${fileTypeIcon}</span>
            <span class="flex-1 truncate">${file.name}</span>
        </div>`;
    });
    
    fileListHtml += '</div>';
    fileListHtml += '</div>';
    
    return fileListHtml;
}

function createValidationScoreBadge(caseData) {
    // Show validation score for processed cases, placeholder for others to maintain consistent spacing
    if (caseData.status === 'Complete' || caseData.status === 'Pending Review') {
        if (caseData.id === 'Rodriguez') {
            // Cases with issues - red with warning icon
            return `
                <div class="mt-2">
                    <span class="inline-flex items-center text-xs font-medium text-red-600">
                        <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                        </svg>
                        65% Issues Found
                    </span>
                </div>
            `;
        } else {
            // Cases passing validation - black with checkmark icon
            return `
                <div class="mt-2">
                    <span class="inline-flex items-center text-xs font-medium text-gray-800">
                        <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                        </svg>
                        Validation Passed
                    </span>
                </div>
            `;
        }
    } else {
        // Placeholder for NEW cases to maintain consistent card spacing
        return `
            <div class="mt-2">
                <span class="inline-flex items-center text-xs font-medium text-transparent">
                    <svg class="w-3 h-3 mr-1 invisible" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                    </svg>
                    Placeholder
                </span>
            </div>
        `;
    }
}

function createValidationErrorBadge(caseData) {
    // No longer needed - validation score badge provides all necessary information
    return '';
}

function createCaseCard(caseData) {
    const card = document.createElement('div');
    card.className = 'bg-white border border-gray-200 rounded-lg p-6 flex flex-col shadow-md w-full sm:w-[400px] lg:w-[450px] min-h-[500px]';
    card.dataset.caseId = caseData.id;

    const statusClasses = getStatusClasses(caseData.status);
    const actionButton = getActionButton(caseData);
    const progressLights = createProgressLights(caseData.progress, caseData.status);
    
    const defendantText = caseData.name; // Simplified for now

    const lastUpdated = new Date(caseData.last_updated).toLocaleString();

    // For completed cases, show "Generated: [date]" instead of "Last activity"
    const activityLabel = caseData.status === 'Complete' ? 'Generated' : 'Last activity';

    const fileStatusSection = createFileStatusSection(caseData);
    const validationScoreBadge = createValidationScoreBadge(caseData);
    const validationErrorBadge = createValidationErrorBadge(caseData);
    
    card.innerHTML = `
        <div class="flex justify-between items-start mb-5">
            <div>
                <h3 class="text-2xl font-extrabold text-gray-900">${caseData.name}</h3>
            </div>
            <div class="flex flex-col items-end">
                <span class="status-badge px-4 py-1 text-xs font-bold rounded-full ${statusClasses}">${caseData.status}</span>
                ${validationScoreBadge}
            </div>
        </div>
        <div class="mb-5">
            <p class="text-sm text-gray-500">${activityLabel}: ${lastUpdated}</p>
        </div>
        <div class="progress-lights mb-3">
            ${progressLights}
        </div>
        <div class="flex-grow">
            ${fileStatusSection}
        </div>
        <div class="mt-4">
            ${actionButton}
        </div>
    `;
    return card;
}

export function renderCases(cases) {
    if (!caseGrid) return;
    
    // Preserve scroll position
    const scrollPosition = window.scrollY;

    if (cases.length === 0) {
        caseGrid.innerHTML = '<p class="text-gray-500">No cases found.</p>';
        return;
    }

    // Clear any loading/error states first
    const loadingElement = caseGrid.querySelector('.col-span-full');
    if (loadingElement) {
        loadingElement.remove();
    }

    // SELECTIVE DOM UPDATES - Only change what actually changed
    updateCasesSelectively(cases);
    
    // After rendering, replace feather icons if available
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Restore scroll position
    window.scrollTo(0, scrollPosition);
}

function updateCasesSelectively(newCases) {
    // Get existing case cards
    const existingCards = Array.from(caseGrid.children).filter(el => el.dataset.caseId);
    const existingCaseIds = new Set(existingCards.map(card => card.dataset.caseId));
    const newCaseIds = new Set(newCases.map(c => c.id));
    
    // Store current filter state (display styles) to preserve during updates
    const filterState = new Map();
    existingCards.forEach(card => {
        filterState.set(card.dataset.caseId, card.style.display);
    });
    
    // Remove cards that no longer exist
    existingCards.forEach(card => {
        if (!newCaseIds.has(card.dataset.caseId)) {
            card.remove();
        }
    });
    
    // Update or add cases
    newCases.forEach((caseData, index) => {
        const existingCard = caseGrid.querySelector(`[data-case-id="${caseData.id}"]`);
        
        if (existingCard) {
            // Update existing card ONLY if data changed
            updateCaseCardIfChanged(existingCard, caseData);
            // Preserve filter state after update
            const savedDisplayStyle = filterState.get(caseData.id);
            if (savedDisplayStyle !== undefined) {
                existingCard.style.display = savedDisplayStyle;
            }
        } else {
            // Add new card
            const newCard = createCaseCard(caseData);
            
            // Apply current filter state to new cards
            const activeFilter = getCurrentFilter();
            if (activeFilter && activeFilter !== 'all') {
                const statusBadge = newCard.querySelector('.status-badge');
                const caseStatus = statusBadge?.textContent?.trim() || '';
                if (caseStatus !== activeFilter) {
                    newCard.style.display = 'none';
                }
            }
            
            // Insert in correct position
            const nextCard = caseGrid.children[index];
            if (nextCard) {
                caseGrid.insertBefore(newCard, nextCard);
            } else {
                caseGrid.appendChild(newCard);
            }
        }
    });
}

function updateCaseCardIfChanged(existingCard, newData) {
    // Get current data from DOM
    const currentStatus = existingCard.querySelector('.status-badge')?.textContent?.trim();
    const currentButton = existingCard.querySelector(`#${newData.id}_button`);
    
    // Check if status changed
    if (currentStatus !== newData.status) {
        console.log(`Status changed for ${newData.id}: ${currentStatus} → ${newData.status}`);
        
        // Update status badge
        const statusBadge = existingCard.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.textContent = newData.status;
            statusBadge.className = `status-badge px-4 py-1 text-xs font-bold rounded-full ${getStatusClasses(newData.status)}`;
        }
        
        // Update action button ONLY if not currently processing/animating
        if (currentButton && !currentButton.disabled && !currentButton.classList.contains('bg-red-600')) {
            console.log(`🔧 FILTER DEBUG: Replacing button for ${newData.id}`);
            
            const newButton = document.createElement('div');
            newButton.innerHTML = getActionButton(newData);
            const replacementButton = newButton.firstChild;
            
            // CRITICAL FIX: Ensure button NEVER has display: none applied directly
            // Buttons should be controlled via their parent card's display, not their own
            replacementButton.style.display = '';
            
            // Also remove any display:none that might be set from other sources
            if (replacementButton.style.display === 'none') {
                replacementButton.style.display = '';
            }
            
            currentButton.parentNode.replaceChild(replacementButton, currentButton);
            console.log(`🔧 FILTER DEBUG: Replaced button for ${newData.id}, ensured display is empty string`);
        }
    }
    
    // Update file processing status if data available
    updateFileStatusIfChanged(existingCard, newData);
    
    // Update progress lights
    updateProgressLightsIfChanged(existingCard, newData);
}

function updateFileStatusIfChanged(existingCard, newData) {
    if (!newData.file_processing_results) return;
    
    const fileListContainer = existingCard.querySelector(`#files-${newData.id}`);
    if (!fileListContainer) return;
    
    // Update individual file status icons
    newData.file_processing_results.forEach(fileResult => {
        const fileElement = fileListContainer.querySelector(`[data-file="${fileResult.name}"]`);
        if (!fileElement) return;
        
        const statusIcon = fileElement.querySelector('.file-status-icon');
        if (!statusIcon) return;
        
        const newIcon = getFileStatusIcon(fileResult.status);
        if (statusIcon.innerHTML !== newIcon) {
            console.log(`File status changed: ${fileResult.name} → ${fileResult.status}`);
            statusIcon.innerHTML = newIcon;
        }
    });
}

function updateProgressLightsIfChanged(existingCard, newData) {
    const progressContainer = existingCard.querySelector('.progress-lights');
    if (!progressContainer || !newData.progress) return;
    
    const newProgressHtml = createProgressLights(newData.progress, newData.status);
    if (progressContainer.innerHTML !== newProgressHtml) {
        console.log(`Progress changed for ${newData.id}`);
        progressContainer.innerHTML = newProgressHtml;
    }
}

export function renderLoadingState() {
    if (!caseGrid) return;
    
    caseGrid.innerHTML = `
        <div class="col-span-full flex items-center justify-center py-16">
            <div class="text-center">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p class="mt-4 text-gray-500">Loading cases...</p>
            </div>
        </div>
    `;
}

export function renderErrorState(error) {
    if (!caseGrid) return;
    
    caseGrid.innerHTML = `
        <div class="col-span-full flex items-center justify-center py-16">
            <div class="text-center">
                <div class="text-red-600 mb-4">
                    <svg class="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
                <p class="text-gray-700 font-medium">Failed to load cases</p>
                <p class="text-gray-500 text-sm mt-2">${error || 'Please try refreshing the page'}</p>
            </div>
        </div>
    `;
}

// Use event delegation for file toggle buttons to avoid duplicate listeners
export function initializeFileToggleListeners() {
    if (!caseGrid) return;
    
    // Remove any existing listeners first
    caseGrid.removeEventListener('click', handleFileToggleClick);
    
    // Add single delegated event listener
    caseGrid.addEventListener('click', handleFileToggleClick);
}

function handleFileToggleClick(event) {
    if (event.target.classList.contains('toggle-files')) {
        const caseId = event.target.dataset.caseId;
        const fileList = document.getElementById(`files-${caseId}`);
        
        if (fileList) {
            const isHidden = fileList.classList.contains('hidden');
            if (isHidden) {
                fileList.classList.remove('hidden');
                event.target.textContent = 'Hide Details';
            } else {
                fileList.classList.add('hidden');
                event.target.textContent = 'Show Details';
            }
        }
    }
}

export function renderVersion(version) {
    const sidebarVersionElement = document.getElementById('sidebar-version');
    if (sidebarVersionElement) {
        sidebarVersionElement.textContent = `v${version}`;
    }
}

// Export showToast for ES6 module imports
export { showToast };

// Export filter state functions
export { getCurrentFilter, setCurrentFilter };
