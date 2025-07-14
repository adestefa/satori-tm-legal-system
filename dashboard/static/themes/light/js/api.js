// dashboard/static/js/api.js

export async function getCases() {
    try {
        const response = await fetch('/api/cases');
        if (!response.ok) {
            throw new Error(`Failed to fetch cases: ${response.status} ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Failed to fetch cases:", error);
        // Re-throw error so calling code can handle it appropriately
        throw error;
    }
}

export async function processCase(caseId) {
    try {
        if (!caseId) {
            throw new Error('Case ID is required for processing');
        }
        
        const response = await fetch(`/api/cases/${caseId}/process`, {
            method: 'POST',
        });
        if (!response.ok) {
            throw new Error(`Failed to process case ${caseId}: ${response.status} ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Failed to process case ${caseId}:`, error);
        // Re-throw error so calling code can handle it appropriately
        throw error;
    }
}

export async function getCaseFileStatus(caseId) {
    try {
        if (!caseId) {
            throw new Error('Case ID is required for file status');
        }
        
        const response = await fetch(`/api/cases/${caseId}/file-status`);
        if (!response.ok) {
            throw new Error(`Failed to fetch file status for case ${caseId}: ${response.status} ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Failed to fetch file status for case ${caseId}:`, error);
        // Re-throw error so calling code can handle it appropriately
        throw error;
    }
}

export async function getVersion() {
    try {
        const response = await fetch('/api/version');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Failed to fetch version:", error);
        return { version: "N/A" };
    }
}

export async function getCaseManifest(caseId) {
    try {
        if (!caseId) {
            throw new Error('Case ID is required for manifest');
        }
        
        const response = await fetch(`/api/cases/${caseId}/manifest`);
        if (!response.ok) {
            throw new Error(`Failed to fetch manifest for case ${caseId}: ${response.status} ${response.statusText}`);
        }
        return await response.text();
    } catch (error) {
        console.error(`Failed to fetch manifest for case ${caseId}:`, error);
        return '';
    }
}
