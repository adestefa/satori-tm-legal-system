// dashboard/static/js/ani.js - File Processing Animation System

console.log(`🎬 ANI: Loading animation module...`);

// Animation state management
let hybridAnimationStates = new Map(); // caseId -> { currentIndex, fileList, manifestOverride, completed }

// Start hybrid file animation - immediate sequential animation with manifest override capability
export function startHybridFileAnimation(caseId) {
    console.log(`🎭 HYBRID: Starting animation for case ${caseId}`);
    
    const caseCard = document.querySelector(`[data-case-id="${caseId}"]`);
    if (!caseCard) {
        console.error(`🎭 HYBRID: Case card not found for ${caseId}`);
        return;
    }
    
    const fileElements = caseCard.querySelectorAll('.file-item');
    const fileList = Array.from(fileElements);
    
    if (fileList.length === 0) {
        console.error(`🎭 HYBRID: No files found for case ${caseId}`);
        return;
    }
    
    console.log(`🎭 HYBRID: Found ${fileList.length} files to animate for case ${caseId}`);
    
    // Initialize hybrid state
    hybridAnimationStates.set(caseId, {
        currentIndex: 0,
        fileList: fileList,
        manifestOverride: false,
        completed: false
    });
    
    // Start sequential animation immediately
    animateNextFile(caseId);
}

// Animate files one by one with 17-second intervals (extended for server processing time)
function animateNextFile(caseId) {
    const state = hybridAnimationStates.get(caseId);
    if (!state || state.manifestOverride || state.completed) {
        console.log(`🎭 HYBRID: Animation stopped for ${caseId} - override: ${state?.manifestOverride}, completed: ${state?.completed}`);
        return;
    }
    
    if (state.currentIndex >= state.fileList.length) {
        // All files complete
        console.log(`🎭 HYBRID: All files animated for case ${caseId}`);
        completeHybridAnimation(caseId);
        return;
    }
    
    const currentFile = state.fileList[state.currentIndex];
    const fileName = currentFile.getAttribute('data-file-name') || `File ${state.currentIndex + 1}`;
    const iconElement = currentFile.querySelector('.file-status-icon');
    
    if (!iconElement) {
        console.error(`🎭 HYBRID: Icon element not found for file ${fileName}`);
        // Move to next file
        state.currentIndex++;
        setTimeout(() => animateNextFile(caseId), 100);
        return;
    }
    
    console.log(`🎭 HYBRID: Animating file ${fileName} (${state.currentIndex + 1}/${state.fileList.length})`);
    
    // Step 1: Start processing animation (hourglass with sand animation)
    iconElement.textContent = '⏳';
    iconElement.style.animation = 'hourglass-sand 3s ease-in-out infinite';
    
    // Step 2: After 15 seconds, show completion (checkmark) - extended for server processing time
    setTimeout(() => {
        if (hybridAnimationStates.get(caseId)?.manifestOverride) {
            console.log(`🎭 HYBRID: Manifest override detected, stopping spoof animation for ${fileName}`);
            return;
        }
        
        iconElement.textContent = '✅';
        iconElement.style.animation = 'none';
        console.log(`🎭 HYBRID: File ${fileName} completed`);
        
        // Step 3: After 2 more seconds, move to next file (total 17 seconds per file)
        setTimeout(() => {
            if (hybridAnimationStates.get(caseId)?.manifestOverride) {
                return;
            }
            
            state.currentIndex++;
            animateNextFile(caseId);
        }, 2000);
    }, 15000);
}

// Complete hybrid animation and update case status
function completeHybridAnimation(caseId) {
    const state = hybridAnimationStates.get(caseId);
    if (!state || state.manifestOverride) {
        return;
    }
    
    console.log(`🎭 HYBRID: Completing animation for case ${caseId}`);
    state.completed = true;
    
    // Update the case button to "Ready for Review" state
    const button = document.querySelector(`#${caseId}_button`);
    if (button && button.tagName === 'BUTTON') {
        button.disabled = false;
        button.className = 'w-full text-center px-4 py-3 rounded-lg font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2 bg-green-600 text-white hover:bg-green-700 focus:ring-green-500';
        button.innerHTML = 'Ready for Review';
        
        // Update onclick to navigate to review page
        button.onclick = function() {
            window.location.href = `/review?case_id=${caseId}`;
        };
    }
    
    // Update case status display
    const caseCard = document.querySelector(`[data-case-id="${caseId}"]`);
    if (caseCard) {
        const statusElement = caseCard.querySelector('.case-status');
        if (statusElement) {
            statusElement.textContent = 'Ready for Review';
            statusElement.className = 'case-status bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium';
        }
        
        // Update progress indicators (first 3 steps complete)
        const progressElements = caseCard.querySelectorAll('.progress-indicator');
        progressElements.forEach((element, index) => {
            if (index < 3) { // First 3 steps complete (Synced, Classified, Extracted)
                element.className = 'progress-indicator w-6 h-6 rounded-full bg-green-500 text-white text-xs font-bold flex items-center justify-center';
                element.textContent = index + 1;
            }
        });
    }
    
    // Show completion toast
    if (window.showToast) {
        window.showToast(`Case ${caseId} processing completed! Ready for review.`, 'success', 4000);
    }
    
    console.log(`🎭 HYBRID: Animation completed for case ${caseId}`);
    
    // Clean up state
    hybridAnimationStates.delete(caseId);
}

// Enable manifest override for a case (called when real data becomes available)
export function enableManifestOverride(caseId) {
    const hybridState = hybridAnimationStates.get(caseId);
    if (hybridState && !hybridState.manifestOverride) {
        console.log(`🎬 ANI: Enabling manifest override for ${caseId}`);
        hybridState.manifestOverride = true;
        hybridAnimationStates.set(caseId, hybridState);
    }
}

// Force complete animation (called when manifest shows all files complete)
export function forceCompleteAnimation(caseId) {
    const hybridState = hybridAnimationStates.get(caseId);
    if (hybridState && !hybridState.completed) {
        console.log(`🎬 ANI: Force completing animation for ${caseId}`);
        completeHybridAnimation(caseId);
    }
}

// Make functions globally available for backward compatibility
window.startHybridFileAnimation = startHybridFileAnimation;
window.enableManifestOverride = enableManifestOverride;
window.forceCompleteAnimation = forceCompleteAnimation;

console.log(`🎬 ANI: Animation module loaded successfully`);