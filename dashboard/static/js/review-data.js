// dashboard/static/js/review-data.js
// JavaScript for the review data page only

function getCaseId() {
    const params = new URLSearchParams(window.location.search);
    return params.get('case_id');
}

async function fetchCaseData(caseId) {
    console.log(`Fetching data for caseId: ${caseId}`);
    try {
        const response = await fetch(`/api/cases/${caseId}/review_data`);
        console.log("Response status:", response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const rawResponse = await response.text();
        console.log("Raw response:", rawResponse);
        return JSON.parse(rawResponse);
    } catch (error) {
        console.error("Failed to fetch or parse case data:", error);
        const container = document.getElementById('review-data-section');
        container.innerHTML = `<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong class="font-bold">Error:</strong>
            <span class="block sm:inline">Failed to load case data. Check the console for details.</span>
        </div>`;
        return null;
    }
}

function renderReviewData(data) {
    const container = document.getElementById('review-data-section');
    if (!data) return;

    const createSection = (title, details) => {
        // Special handling for Parties section to remove ugly sub-labels
        if (title === 'Parties') {
            return createPartiesSection(details);
        }
        
        // Check if this is the factual background section (contains allegations)
        const isFactualBackground = Object.keys(details).includes('allegations');
        
        // Use single column layout for factual background, two-column for others
        const gridClass = isFactualBackground ? 'grid grid-cols-1 gap-y-4' : 'grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4';
        
        let detailsHtml = `<div class="${gridClass}">`;
        for (const [key, value] of Object.entries(details)) {
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            let displayValue = value;
            
            // Handle complex objects and arrays
            if (typeof value === 'object' && value !== null) {
                if (Array.isArray(value)) {
                    // Special handling for defendants array
                    if (key === 'defendants' && value.every(item => typeof item === 'object')) {
                        displayValue = value.map(defendant => defendant.name || 'Unnamed Defendant').join('<br>');
                    } 
                    // Special handling for factual background allegations
                    else if (key === 'allegations' && value.length > 0) {
                        displayValue = `<div class="space-y-3 w-full max-w-none">` + value.map((allegation, index) => {
                            // Check if allegation already starts with a number
                            const trimmedAllegation = allegation.trim();
                            const startsWithNumber = /^\d+\.\s/.test(trimmedAllegation);
                            
                            if (startsWithNumber) {
                                // Already numbered, just add proper formatting with full width
                                return `<div class="text-gray-900 leading-relaxed w-full max-w-none">${allegation}</div>`;
                            } else {
                                // Not numbered, add sequential numbering starting from 11
                                const number = index + 11;
                                return `<div class="flex w-full max-w-none"><span class="font-semibold text-gray-700 mr-3 min-w-[2rem] flex-shrink-0">${number}.</span><span class="text-gray-900 leading-relaxed flex-1">${allegation}</span></div>`;
                            }
                        }).join('') + `</div>`;
                    } 
                    else {
                        displayValue = value.join(', ');
                    }
                } else {
                    displayValue = JSON.stringify(value, null, 2).replace(/[{}"]/g, '').replace(/,/g, '<br>');
                }
            }
            
            detailsHtml += `
                <div>
                    <dt class="text-sm font-medium text-gray-500">${label}</dt>
                    <dd class="mt-1 text-sm text-gray-900">${displayValue}</dd>
                </div>
            `;
        }
        detailsHtml += '</div>';

        return `
            <div class="bg-white p-6 rounded-lg shadow-sm mb-8">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">${title}</h3>
                <dl>${detailsHtml}</dl>
            </div>
        `;
    };

    const createPartiesSection = (details) => {
        let detailsHtml = '<div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">';
        
        // Handle Plaintiff
        if (details.plaintiff) {
            let plaintiffInfo = '';
            const plaintiff = details.plaintiff;
            
            if (plaintiff.name) {
                plaintiffInfo += `<div class="font-medium text-gray-900">${plaintiff.name}</div>`;
            }
            
            if (plaintiff.address) {
                const address = plaintiff.address;
                let addressStr = '';
                if (address.street) addressStr += address.street;
                if (address.city) addressStr += (addressStr ? ', ' : '') + address.city;
                if (address.state) addressStr += (addressStr ? ', ' : '') + address.state;
                if (address.zip_code) addressStr += (addressStr ? ' ' : '') + address.zip_code;
                if (addressStr) {
                    plaintiffInfo += `<div class="text-gray-700 text-sm">${addressStr}</div>`;
                }
            }
            
            if (plaintiff.residency) {
                plaintiffInfo += `<div class="text-gray-600 text-sm">Residency: ${plaintiff.residency}</div>`;
            }
            
            if (plaintiff.consumer_status) {
                plaintiffInfo += `<div class="text-gray-600 text-sm">Status: ${plaintiff.consumer_status}</div>`;
            }
            
            detailsHtml += `
                <div>
                    <dt class="text-sm font-medium text-gray-500">Plaintiff</dt>
                    <dd class="mt-1 text-sm space-y-1">${plaintiffInfo}</dd>
                </div>
            `;
        }
        
        // Handle Defendants
        if (details.defendants) {
            let defendantsInfo = '';
            if (Array.isArray(details.defendants)) {
                defendantsInfo = details.defendants.map(defendant => {
                    return defendant.name || 'Unnamed Defendant';
                }).join('<br>');
            }
            
            detailsHtml += `
                <div>
                    <dt class="text-sm font-medium text-gray-500">Defendants</dt>
                    <dd class="mt-1 text-sm text-gray-900">${defendantsInfo}</dd>
                </div>
            `;
        }
        
        detailsHtml += '</div>';

        return `
            <div class="bg-white p-6 rounded-lg shadow-sm mb-8">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Parties</h3>
                <dl>${detailsHtml}</dl>
            </div>
        `;
    };

    let html = '';
    if (data.parties) html += createSection('Parties', data.parties);
    if (data.case_information) html += createSection('Case Information', data.case_information);
    if (data.filing_details) html += createSection('Filing Details', data.filing_details);
    if (data.factual_background) html += createSection('Factual Background', data.factual_background);
    
    container.innerHTML = html;
    
    // Initialize damage review if damage data exists
    if (data.damages) {
        renderDamagesSection(data.damages);
    }
}

function renderDamagesSection(damages) {
    const container = document.getElementById('damages-section');
    if (!container) {
        console.error('Damages section container not found');
        return;
    }
    
    // Initialize the damage review component
    window.damageReview = new DamageReview(damages);
    window.damageReview.initialize();
}

function renderCausesOfAction(data) {
    const container = document.getElementById('cause-of-action-section');
    if (!data || !Array.isArray(data)) {
        container.innerHTML = '<p>No causes of action found.</p>';
        return;
    }

    let html = '<div class="space-y-6">';
    data.forEach((cause, causeIndex) => {
        const claimsHtml = cause.legal_claims.map((claim, claimIndex) => {
            const claimId = `claim-${causeIndex}-${claimIndex}`;
            const confidenceColor = claim.confidence > 0.7 ? 'text-green-600' : 'text-yellow-600';
            const defaultSelected = claim.confidence > 0.7; // Auto-select high confidence claims
            
            return `
                <div class="claim-item p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
                    <div class="flex items-start space-x-3">
                        <input type="checkbox" 
                               id="${claimId}" 
                               name="legal_claim" 
                               value="${claim.citation}" 
                               data-cause="${causeIndex}"
                               data-claim="${claimIndex}"
                               class="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" 
                               ${claim.selected || defaultSelected ? 'checked' : ''}>
                        <div class="flex-1">
                            <label for="${claimId}" class="cursor-pointer">
                                <div class="font-semibold text-blue-700 text-sm mb-1">${claim.citation}</div>
                                <div class="text-gray-700 text-sm leading-relaxed">${claim.description}</div>
                                <div class="flex items-center justify-between mt-2">
                                    <div class="text-xs ${confidenceColor} font-medium">
                                        Confidence: ${(claim.confidence * 100).toFixed(0)}% | Category: ${claim.category}
                                    </div>
                                    <div class="text-xs text-gray-500">
                                        Against: ${cause.against_defendants.join(', ')}
                                    </div>
                                </div>
                            </label>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        html += `
            <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-xl font-semibold text-gray-800">${cause.title}</h3>
                    <div class="text-sm text-gray-600">Count ${cause.count_number}</div>
                </div>
                <p class="text-gray-600 mb-4">Against Defendants: ${cause.against_defendants.join(', ')}</p>
                <div class="space-y-3">
                    <h4 class="font-medium text-gray-800 mb-3">Legal Claims (Select applicable):</h4>
                    ${claimsHtml}
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    // Enhanced action buttons
    html += `
        <div class="mt-8 bg-gray-50 p-6 rounded-lg border border-gray-200">
            <div class="flex items-center justify-between">
                <div class="text-sm text-gray-600">
                    <p class="mb-1">✓ <strong>High confidence</strong> claims auto-selected</p>
                    <p>Review and adjust selections before saving</p>
                </div>
                <div class="flex space-x-3">
                    <button id="select-all-btn" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
                        Select All
                    </button>
                    <button id="clear-all-btn" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm">
                        Clear All
                    </button>
                    <button id="save-selections-btn" class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                        Save Legal Claims
                    </button>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Add event listeners for helper buttons
    document.getElementById('select-all-btn').addEventListener('click', () => {
        document.querySelectorAll('input[name="legal_claim"]').forEach(checkbox => {
            checkbox.checked = true;
        });
    });
    
    document.getElementById('clear-all-btn').addEventListener('click', () => {
        document.querySelectorAll('input[name="legal_claim"]').forEach(checkbox => {
            checkbox.checked = false;
        });
    });
}

async function saveLegalSelections(caseId, caseData) {
    const saveBtn = document.getElementById('save-selections-btn');
    const originalText = saveBtn.textContent;
    
    try {
        // Show saving state
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
        
        // Collect all checkbox states using the enhanced data attributes
        const checkboxes = document.querySelectorAll('input[name="legal_claim"]');
        const selections = [];
        
        checkboxes.forEach(checkbox => {
            const causeIndex = parseInt(checkbox.getAttribute('data-cause'));
            const claimIndex = parseInt(checkbox.getAttribute('data-claim'));
            const selected = checkbox.checked;
            
            selections.push({
                cause_index: causeIndex,
                claim_index: claimIndex,
                selected: selected
            });
        });

        const response = await fetch(`/api/cases/${caseId}/legal-claims`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ selections: selections })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        // Show success state
        saveBtn.textContent = '✅ Saved';
        saveBtn.className = saveBtn.className.replace('bg-blue-600 hover:bg-blue-700', 'bg-green-600');
        
        // Show success message
        const successMessage = document.createElement('div');
        successMessage.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded z-50';
        successMessage.innerHTML = `
            <div class="flex items-center">
                <strong class="font-bold">Success!</strong>
                <span class="block sm:inline ml-2">${result.message || 'Legal claims saved successfully!'}</span>
            </div>
        `;
        document.body.appendChild(successMessage);
        
        // Remove success message after 3 seconds
        setTimeout(() => {
            if (successMessage.parentNode) {
                successMessage.parentNode.removeChild(successMessage);
            }
        }, 3000);
        
    } catch (error) {
        console.error('Failed to save legal selections:', error);
        
        // Show error state
        saveBtn.textContent = '❌ Error';
        saveBtn.className = saveBtn.className.replace('bg-blue-600 hover:bg-blue-700', 'bg-red-600');
        
        // Show error message
        const errorMessage = document.createElement('div');
        errorMessage.className = 'fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded z-50';
        errorMessage.innerHTML = `
            <div class="flex items-center">
                <strong class="font-bold">Error!</strong>
                <span class="block sm:inline ml-2">${error.message}</span>
            </div>
        `;
        document.body.appendChild(errorMessage);
        
        // Remove error message after 5 seconds
        setTimeout(() => {
            if (errorMessage.parentNode) {
                errorMessage.parentNode.removeChild(errorMessage);
            }
        }, 5000);
    } finally {
        // Reset button after 2 seconds
        setTimeout(() => {
            saveBtn.disabled = false;
            saveBtn.textContent = originalText;
            saveBtn.className = saveBtn.className.replace('bg-green-600', 'bg-blue-600 hover:bg-blue-700');
            saveBtn.className = saveBtn.className.replace('bg-red-600', 'bg-blue-600 hover:bg-blue-700');
        }, 2000);
    }
}

// Initialize the review data page
document.addEventListener('DOMContentLoaded', async () => {
    console.log("DOM fully loaded and parsed");
    const caseId = getCaseId();
    if (!caseId) {
        document.body.innerHTML = '<h1>Error: No Case ID provided.</h1>';
        console.error("No caseId found in URL");
        return;
    }

    console.log(`Case ID is: ${caseId}`);
    
    // Add case ID to tab navigation links
    const tabLinks = document.querySelectorAll('a[href$=".html"]');
    tabLinks.forEach(link => {
        const href = link.getAttribute('href');
        link.setAttribute('href', `${href}?case_id=${caseId}`);
    });

    const caseData = await fetchCaseData(caseId);

    if (caseData) {
        console.log("Case data successfully fetched and parsed:", caseData);
        
        console.log("Rendering review data...");
        renderReviewData(caseData);
        console.log("Finished rendering review data.");

        console.log("Rendering causes of action...");
        renderCausesOfAction(caseData.causes_of_action);
        console.log("Finished rendering causes of action.");

        const saveBtn = document.getElementById('save-selections-btn');
        if(saveBtn) {
            saveBtn.addEventListener('click', () => saveLegalSelections(caseId, caseData));
        }
    } else {
        console.error("caseData is null or undefined. Halting render.");
    }
});