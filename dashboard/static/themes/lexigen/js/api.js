// dashboard/static/js/api.js

export async function getCases() {
    try {
        const response = await fetch('/api/cases');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Failed to fetch cases:", error);
        return []; // Return empty array on error
    }
}

export async function processCase(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}/process`, {
            method: 'POST',
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Failed to process case ${caseId}:`, error);
        return null;
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
