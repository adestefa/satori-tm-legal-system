// dashboard/static/review/js/review.js

let websocket = null;

function getCaseId() {
    const params = new URLSearchParams(window.location.search);
    const caseId = params.get('case_id');
    return caseId ? caseId.toLowerCase() : caseId;
}

function initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    try {
        websocket = new WebSocket(wsUrl);
        
        websocket.onopen = () => {
            console.log('WebSocket connected for real-time updates');
        };
        
        websocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('WebSocket message received:', data);
                
                // Handle complaint generation complete event
                if (data.type === 'complaint_generated') {
                    const resolvers = window.complaintGenerationResolvers || {};
                    const resolver = resolvers[data.case_id];
                    if (resolver) {
                        console.log(`Complaint ready for case ${data.case_id}`);
                        resolver();
                    }
                }
                
                // Handle file system events (single or batched)
                if (data.type === 'file_system_change') {
                    console.log('File system change:', data.event_type, data.path);
                } else if (data.type === 'file_system_batch') {
                    console.log(`File system batch: ${data.event_count} events at ${data.timestamp}`);
                    // Process individual events in the batch if needed
                    if (data.events && Array.isArray(data.events)) {
                        data.events.forEach(event => {
                            console.log('Batched event:', event.event_type, event.path);
                        });
                    }
                }
            } catch (error) {
                console.error('Error processing WebSocket message:', error);
                console.error('Raw message data:', event.data);
                // Log the problematic JSON for debugging
                if (event.data.length > 1000) {
                    console.error('Message appears to be corrupted (too long):', event.data.substring(0, 500) + '...');
                } else {
                    console.error('Full problematic message:', event.data);
                }
            }
        };
        
        websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        websocket.onclose = () => {
            console.log('WebSocket disconnected');
            // Optionally implement reconnection logic here
        };
    } catch (error) {
        console.error('Failed to initialize WebSocket:', error);
    }
}

function checkAndShowValidationAlert(caseId, caseData) {
    // Check if case has validation issues (using Rodriguez as example)
    const hasValidationIssues = caseId === 'Rodriguez';
    
    if (hasValidationIssues) {
        const alertElement = document.getElementById('validation-alert');
        const messageElement = document.getElementById('validation-alert-message');
        const showTimelineButton = document.getElementById('show-timeline-tab');
        
        if (alertElement) {
            // Calculate validation score (mock implementation)
            const validationScore = 65;
            
            // Update alert message with specific score
            if (messageElement) {
                messageElement.textContent = `This case has a validation score of ${validationScore}% with date chronology issues. Review the Timeline Validation tab for detailed analysis and recommendations.`;
            }
            
            // Show the alert
            alertElement.classList.remove('hidden');
            
            // Highlight the Timeline Validation tab with a red indicator
            const timelineTab = document.getElementById('tab-timeline');
            if (timelineTab) {
                // Add a red dot indicator to the tab
                const tabText = timelineTab.textContent.trim();
                if (!tabText.includes('🔴')) {
                    timelineTab.innerHTML = timelineTab.innerHTML + ' <span class="text-red-600 font-bold">●</span>';
                }
            }
            
            // Add click handler for timeline button
            if (showTimelineButton) {
                showTimelineButton.addEventListener('click', () => {
                    // Switch to timeline validation tab
                    const timelineTab = document.getElementById('tab-timeline');
                    if (timelineTab) {
                        timelineTab.click();
                        
                        // Highlight the timeline tab briefly
                        timelineTab.classList.add('animate-pulse');
                        setTimeout(() => {
                            timelineTab.classList.remove('animate-pulse');
                        }, 2000);
                    }
                });
            }
        }
    }
}

async function fetchCaseData(caseId) {
    // Version and path verification console logs (v1.9.10)
    console.log(`🔍 DASHBOARD VERSION: 1.9.10 - NY_FCRA.json fix`);
    console.log(`🔍 TIGER RESOURCES PATH: tiger/app/resources/legal-spec/NY_FCRA.json`);
    console.log(`Fetching data for caseId: ${caseId}`);
    try {
        const response = await fetch(`/api/cases/${caseId}/review_data`);
        console.log("Response status:", response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const rawResponse = await response.text();
        console.log("Raw response:", rawResponse);
        const parsedData = JSON.parse(rawResponse);
        console.log("🔍 FETCH: Parsed data:", parsedData);
        console.log("🔍 FETCH: Parsed data has causes_of_action?", !!parsedData.causes_of_action);
        return parsedData;
    } catch (error) {
        console.error("Failed to fetch or parse case data:", error);
        const container = document.getElementById('review-data-section');
        container.innerHTML = `<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong class="font-bold">Error:</strong>
            <span class="block sm:inline">Data still processing please try again in a few mins</span>
        </div>`;
        return null;
    }
}

function renderCaseName(data) {
    const container = document.getElementById('case-name-header');
    if (!container || !data) return;
    
    // Generate case name from plaintiff and first defendant
    let caseName = '';
    if (data.parties?.plaintiff?.name && data.parties?.defendants?.length > 0) {
        const plaintiffLastName = data.parties.plaintiff.name.split(' ').pop();
        const firstDefendantShortName = data.parties.defendants[0].short_name || 
                                       data.parties.defendants[0].name.split(' ')[0];
        caseName = `${plaintiffLastName} v. ${firstDefendantShortName}, et al.`;
    }
    
    // Add case number if available
    let caseNumber = '';
    if (data.case_information?.case_number) {
        caseNumber = data.case_information.case_number;
    }
    
    // Display case name and number
    if (caseName || caseNumber) {
        container.innerHTML = `
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                ${caseName ? `<h2 class="text-xl font-semibold text-blue-900 mb-1">${caseName}</h2>` : ''}
                ${caseNumber ? `<p class="text-blue-700 text-sm">Case No. ${caseNumber}</p>` : ''}
            </div>
        `;
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
                defendantsInfo = details.defendants.map((defendant, index) => {
                    const name = defendant.name || 'Unnamed Defendant';
                    return `${index + 1}. ${name}`;
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
    console.log('🔍 Checking for damages data:', data.damages ? 'EXISTS' : 'MISSING');
    console.log('🔍 Damages object:', data.damages);
    if (data.damages) {
        console.log('✅ Calling renderDamagesSection...');
        renderDamagesSection(data.damages);
    } else {
        console.log('❌ No damages data found - renderDamagesSection not called');
    }
}

function renderDamagesSection(damages) {
    console.log('🚀 renderDamagesSection called with:', damages);
    
    const container = document.getElementById('damages-section');
    if (!container) {
        console.error('❌ Damages section container not found');
        return;
    }
    
    console.log('✅ Damages container found:', container);
    
    // Check if DamageReview class exists
    if (typeof DamageReview === 'undefined') {
        console.error('❌ DamageReview class not defined - damages-review.js not loaded?');
        return;
    }
    
    console.log('✅ DamageReview class available');
    
    try {
        // Initialize the damage review component
        console.log('🔧 Creating DamageReview instance...');
        window.damageReview = new DamageReview(damages);
        // Pass case ID for auto-save functionality
        window.damageReview.caseId = window.caseId || 'youssef';
        console.log('🔧 Calling initialize...');
        window.damageReview.initialize();
        console.log('✅ DamageReview initialization complete');
    } catch (error) {
        console.error('❌ Error initializing DamageReview:', error);
    }
}

function renderCausesOfAction(data) {
    console.log('🔍 renderCausesOfAction called with data:', data);
    console.log('🔍 Is data an array?', Array.isArray(data));
    console.log('🔍 Data length:', data ? data.length : 'undefined');
    
    const container = document.getElementById('cause-of-action-section');
    console.log('🔍 Container found:', container ? 'YES' : 'NO');
    
    if (!data || !Array.isArray(data)) {
        console.log('❌ No causes of action data or not an array');
        container.innerHTML = '<p>No causes of action found.</p>';
        return;
    }

    let html = '<div class="space-y-6">';
    data.forEach((cause, causeIndex) => {
        console.log(`🔍 Processing cause ${causeIndex}:`, cause);
        console.log(`🔍 Cause title:`, cause.title);
        console.log(`🔍 Legal claims:`, cause.legal_claims);
        console.log(`🔍 Legal claims count:`, cause.legal_claims ? cause.legal_claims.length : 'undefined');
        
        if (!cause.legal_claims || !Array.isArray(cause.legal_claims)) {
            console.log(`❌ No legal_claims array found for cause ${causeIndex}`);
            return;
        }
        
        const claimsHtml = cause.legal_claims.map((claim, claimIndex) => {
            console.log(`🔍 Processing claim ${claimIndex} for cause ${causeIndex}:`, claim);
            console.log(`🔍 Claim selected:`, claim.selected);
            console.log(`🔍 Claim confidence:`, claim.confidence);
            const claimId = `claim-${causeIndex}-${claimIndex}`;
            const confidenceColor = claim.confidence >= 0.5 ? 'text-green-600' : 'text-yellow-600';
            const defaultSelected = claim.confidence >= 0.5; // Auto-select 50%+ confidence claims
            
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
                               onchange="handleClaimSelectionChange()"
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
    
    console.log('🔍 Final HTML being inserted into container:', html);
    
    // Enhanced action buttons
    html += `
        <div class="mt-8 bg-gray-50 p-6 rounded-lg border border-gray-200">
            <div class="flex items-center justify-between">
                <div class="text-sm text-gray-600">
                    <p class="mb-1">✓ <strong>50%+ confidence</strong> claims auto-selected</p>
                    <p>Review and adjust selections before saving</p>
                </div>
                <div class="flex space-x-3">
                    <button id="select-all-btn" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
                        Select All
                    </button>
                    <button id="clear-all-btn" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm">
                        Clear All
                    </button>
                    <button id="save-selections-btn" class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium" disabled>
                        ✅ High-confidence claims auto-saved
                    </button>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    console.log('🔍 HTML has been inserted into container. Container content:', container.innerHTML);
    
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

function renderLegalViolations(data) {
    const container = document.getElementById('legal-violations-section');
    if (!data || !Array.isArray(data)) {
        container.innerHTML = '<p>No legal violations found.</p>';
        return;
    }

    let html = '<div class="space-y-4">';
    data.forEach(violation => {
        html += `
            <div class="bg-white p-6 rounded-lg shadow-sm">
                <p class="font-semibold text-gray-800">${violation}</p>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

function setupTabSwitching() {
    const tabs = {
        review: {
            button: document.getElementById('tab-review'),
            content: document.getElementById('tab-content-review'),
        },
        timeline: {
            button: document.getElementById('tab-timeline'),
            content: document.getElementById('tab-content-timeline'),
        },
        complaint: {
            button: document.getElementById('tab-complaint'),
            content: document.getElementById('tab-content-complaint'),
        },
        summons: {
            button: document.getElementById('tab-summons'),
            content: document.getElementById('tab-content-summons'),
        },
        packet: {
            button: document.getElementById('tab-packet'),
            content: document.getElementById('tab-content-packet'),
        }
    };

    const switchTab = (activeTab) => {
        // Hide all tab content and deactivate all tabs
        Object.values(tabs).forEach(tab => {
            if (tab.button && tab.content) {
                if (tab.button === activeTab.button) {
                    tab.button.classList.add('border-blue-500', 'text-blue-600');
                    tab.button.classList.remove('border-transparent', 'text-gray-500');
                    tab.content.classList.remove('hidden');
                } else {
                    tab.button.classList.remove('border-blue-500', 'text-blue-600');
                    tab.button.classList.add('border-transparent', 'text-gray-500');
                    tab.content.classList.add('hidden');
                }
            }
        });
    };

    tabs.review.button.addEventListener('click', (e) => {
        e.preventDefault();
        switchTab(tabs.review);
    });

    tabs.timeline.button.addEventListener('click', (e) => {
        e.preventDefault();
        switchTab(tabs.timeline);
        // Initialize timeline validation if not already done
        if (window.timelineValidationUI && window.timelineValidationUI.caseId) {
            window.timelineValidationUI.renderTimelineValidation();
        }
    });

    tabs.complaint.button.addEventListener('click', async (e) => {
        e.preventDefault();
        switchTab(tabs.complaint);
        await checkAndLoadExistingComplaint(getCaseId());
    });

    tabs.summons.button.addEventListener('click', async (e) => {
        e.preventDefault();
        switchTab(tabs.summons);
        await loadSummonsInterface(getCaseId());
    });

    tabs.packet.button.addEventListener('click', async (e) => {
        e.preventDefault();
        switchTab(tabs.packet);
        await loadLegalPacketInterface(getCaseId());
    });

}

async function checkAndLoadExistingComplaint(caseId) {
    try {
        // Check if a complaint already exists
        const response = await fetch(`/api/cases/${caseId}/last-complaint`);
        if (!response.ok) {
            console.log("No existing complaint found or error checking for complaint");
            return;
        }
        
        const result = await response.json();
        if (result.exists) {
            console.log("Found existing complaint, loading it automatically");
            await loadExistingComplaint(caseId, result.generated_at);
        } else {
            console.log("No existing complaint found, showing placeholder");
            showComplaintPlaceholder(caseId);
        }
    } catch (error) {
        console.error("Error checking for existing complaint:", error);
        showComplaintPlaceholder(caseId);
    }
}

async function loadExistingComplaint(caseId, generatedAt) {
    const contentDiv = document.getElementById('preview-content');
    const generateBtn = document.getElementById('generate-complaint');
    
    try {
        // Fetch the existing HTML
        const htmlResponse = await fetch(`/api/cases/${caseId}/complaint-html`);
        if (!htmlResponse.ok) {
            throw new Error(`Failed to fetch complaint HTML: ${htmlResponse.status}`);
        }

        const htmlContent = await htmlResponse.text();

        // Display the HTML natively (no iframe) for better mobile UX and accessibility
        const generatedDate = new Date(generatedAt).toLocaleString();
        
        // Extract both the CSS styles and body content from the HTML
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlContent, 'text/html');
        const bodyContent = doc.body.innerHTML;
        
        // Extract CSS styles from the head section
        const styleElements = doc.querySelectorAll('style');
        let extractedStyles = '';
        styleElements.forEach(style => {
            extractedStyles += style.textContent;
        });
        
        contentDiv.innerHTML = `
            <div class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <div class="text-green-800">
                    <strong>✓ Complaint loaded</strong> (generated: ${generatedDate})
                </div>
            </div>
            <style>
                ${extractedStyles}
                .complaint-content .section-title { 
                    font-weight: bold; 
                    text-align: center; 
                    margin-top: 20px; 
                    margin-bottom: 10px; 
                }
                .complaint-content .caption { 
                    text-align: center; 
                    font-weight: bold; 
                }
                .complaint-content .case-number { 
                    text-align: right; 
                }
                .complaint-content p { 
                    margin-bottom: 10px; 
                    line-height: 1.5; 
                }
            </style>
            <div class="complaint-content bg-white p-8 border border-gray-200 rounded-lg shadow-sm" 
                 style="font-family: 'Times New Roman', serif; line-height: 1.6; max-width: none;">
                ${bodyContent}
            </div>
        `;

        // Show the "Edit Complaint" and "Open in New Tab" buttons
        const editBtn = document.getElementById('edit-complaint');
        const openTabBtn = document.getElementById('open-in-new-tab');
        
        editBtn.classList.remove('hidden');
        openTabBtn.classList.remove('hidden');
        
        // Set up button click handlers
        editBtn.onclick = () => enterEditMode(caseId);
        openTabBtn.onclick = () => {
            window.open(`/complaint/${caseId}`, '_blank');
        };

        // Update generate button text
        generateBtn.textContent = 'Regenerate Complaint';

    } catch (error) {
        console.error('Failed to load existing complaint:', error);
        showComplaintPlaceholder(caseId);
    }
}

function showComplaintPlaceholder(caseId) {
    const contentDiv = document.getElementById('preview-content');
    const generateBtn = document.getElementById('generate-complaint');
    
    contentDiv.innerHTML = `
        <div class="flex items-center justify-center h-full text-gray-500">
            <div class="text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 class="mt-2 text-sm font-medium text-gray-900">No complaint generated yet</h3>
                <p class="mt-1 text-sm text-gray-500">Click "Generate Complaint" to create your document.</p>
            </div>
        </div>
    `;
    
    // Reset generate button text
    generateBtn.textContent = 'Generate Complaint';
    
    // Hide the "Edit" and "Open in New Tab" buttons
    const editBtn = document.getElementById('edit-complaint');
    const openTabBtn = document.getElementById('open-in-new-tab');
    editBtn.classList.add('hidden');
    openTabBtn.classList.add('hidden');
}

async function generateComplaint(caseId) {
    const loadingDiv = document.getElementById('preview-loading');
    const contentDiv = document.getElementById('preview-content');
    const generateBtn = document.getElementById('generate-complaint');

    try {
        // Show loading state
        loadingDiv.classList.remove('hidden');
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';

        // Call the API to generate the complaint
        const response = await fetch(`/api/cases/${caseId}/generate-complaint`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Auto-generate summons documents at the same time
        try {
            console.log('Auto-generating summons documents...');
            generateBtn.textContent = 'Generating Summons...';
            
            const summonsResponse = await fetch(`/api/cases/${caseId}/generate-summons`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (summonsResponse.ok) {
                const summonsResult = await summonsResponse.json();
                console.log('Summons auto-generation result:', summonsResult);
            } else {
                console.warn('Summons auto-generation failed, but complaint was successful');
            }
        } catch (summonsError) {
            console.error('Error auto-generating summons:', summonsError);
        }

        // Set up promise to wait for WebSocket notification
        generateBtn.textContent = 'Processing...';
        
        // Create a promise that resolves when we receive the WebSocket event
        const complaintReadyPromise = new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Complaint generation timed out. Please try refreshing the page.'));
            }, 60000); // 60 second timeout
            
            // Store resolver to be called from WebSocket handler
            window.complaintGenerationResolvers = window.complaintGenerationResolvers || {};
            window.complaintGenerationResolvers[caseId] = () => {
                clearTimeout(timeout);
                resolve();
            };
        });
        
        // Wait for the complaint to be ready
        let htmlContent;
        try {
            await complaintReadyPromise;
            generateBtn.textContent = 'Fetching complaint...';
            
            // Now fetch the generated complaint
            const htmlResponse = await fetch(`/api/cases/${caseId}/complaint-html`);
            if (!htmlResponse.ok) {
                throw new Error(`Failed to fetch complaint HTML: ${htmlResponse.status}`);
            }
            
            // Get the HTML content within the try block
            htmlContent = await htmlResponse.text();
            
            // Clean up resolver
            delete window.complaintGenerationResolvers[caseId];
            
        } catch (error) {
            // Clean up resolver on error
            if (window.complaintGenerationResolvers) {
                delete window.complaintGenerationResolvers[caseId];
            }
            throw error;
        }

        // Display the HTML in an iframe
        contentDiv.innerHTML = `
            <iframe srcdoc="${htmlContent.replace(/"/g, '&quot;')}" 
                    style="width: 100%; height: 100%; border: none; background: white;">
            </iframe>
        `;

        // Show the "Edit" and "Open in New Tab" buttons
        const editBtn = document.getElementById('edit-complaint');
        const openTabBtn = document.getElementById('open-in-new-tab');
        
        editBtn.classList.remove('hidden');
        openTabBtn.classList.remove('hidden');
        
        // Set up button click handlers
        editBtn.onclick = () => enterEditMode(caseId);
        openTabBtn.onclick = () => {
            window.open(`/complaint/${caseId}`, '_blank');
        };

        // Show success message for both documents
        showSuccessMessage('Complaint and summons documents generated successfully! Check the Summons tab to view and print individual summons.');

        console.log("Complaint and summons generated successfully");

    } catch (error) {
        console.error('Failed to generate complaint:', error);
        contentDiv.innerHTML = `
            <div class="p-4 text-center">
                <div class="text-red-600 font-semibold">Error generating complaint</div>
                <div class="text-gray-600 mt-2">${error.message}</div>
                <button onclick="generateComplaint('${caseId}')" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    Try Again
                </button>
            </div>
        `;
    } finally {
        // Hide loading state
        loadingDiv.classList.add('hidden');
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Complaint';
    }
}


document.addEventListener('DOMContentLoaded', async () => {
    console.log("DOM fully loaded and parsed");
    const caseId = getCaseId();
    if (!caseId) {
        document.body.innerHTML = '<h1>Error: No Case ID provided.</h1>';
        console.error("No caseId found in URL");
        return;
    }

    console.log(`Case ID is: ${caseId}`);
    
    // Initialize WebSocket connection for real-time updates
    initializeWebSocket();
    
    // Setup tab switching
    setupTabSwitching();
    
    // Check if this is a Complete case and auto-switch to Packet tab
    try {
        const statusResponse = await fetch(`/api/cases/${caseId}/status`);
        if (statusResponse.ok) {
            const statusData = await statusResponse.json();
            if (statusData.status === 'Complete') {
                // Auto-switch to Packet tab for Complete cases
                const packetTab = document.getElementById('tab-packet');
                if (packetTab) {
                    packetTab.click();
                }
            }
        }
    } catch (error) {
        console.log('Could not check case status, proceeding normally');
    }
    
    // Setup generate complaint button
    const generateBtn = document.getElementById('generate-complaint');
    generateBtn.addEventListener('click', () => generateComplaint(caseId));

    const caseData = await fetchCaseData(caseId);

    if (caseData) {
        console.log("Case data successfully fetched and parsed:", caseData);
        
        console.log("Rendering case name...");
        renderCaseName(caseData);
        console.log("Finished rendering case name.");
        
        console.log("Checking validation status...");
        checkAndShowValidationAlert(caseId, caseData);
        console.log("Finished checking validation status.");
        
        console.log("Rendering review data...");
        renderReviewData(caseData);
        console.log("Finished rendering review data.");

        console.log("Rendering causes of action...");
        console.log("🔍 MAIN: caseData.causes_of_action:", caseData.causes_of_action);
        console.log("🔍 MAIN: Type of causes_of_action:", typeof caseData.causes_of_action);
        console.log("🔍 MAIN: Is array?", Array.isArray(caseData.causes_of_action));
        renderCausesOfAction(caseData.causes_of_action);
        console.log("Finished rendering causes of action.");

        // Legacy legal violations section removed - now integrated into causes of action

        const saveBtn = document.getElementById('save-selections-btn');
        if(saveBtn) {
            saveBtn.addEventListener('click', () => saveLegalSelections(caseId, caseData));
        }
        
        // Auto-save high confidence claims and pre-populated damages on page load
        setTimeout(() => autoSaveDefaultSelections(caseId, caseData), 1000);
    } else {
        console.error("caseData is null or undefined. Halting render.");
    }
    
    // Check for existing complaint on initial load if we're on the complaint tab
    const complaintTab = document.getElementById('tab-complaint');
    if (complaintTab && complaintTab.classList.contains('border-blue-500')) {
        await checkAndLoadExistingComplaint(caseId);
    }
    
    // Initialize timeline validation UI
    if (window.timelineValidationUI) {
        await window.timelineValidationUI.init(caseId);
    }

});

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

// Summons Interface Functions
async function loadSummonsInterface(caseId) {
    console.log('Loading summons interface for case:', caseId);
    
    try {
        // Load case data to get defendants list
        const response = await fetch(`/api/cases/${caseId}/data`);
        if (!response.ok) {
            throw new Error('Data still processing please try again in a few mins');
        }
        
        const caseData = await response.json();
        const defendants = caseData.parties?.defendants || [];
        
        if (defendants.length === 0) {
            document.getElementById('summons-defendants-list').innerHTML = `
                <div class="text-center py-8">
                    <p class="text-gray-600">No defendants found in case data.</p>
                </div>
            `;
            return;
        }
        
        // Display defendants list with individual summons buttons
        await renderDefendantsList(defendants, caseId);
        
        // Summons are now auto-generated with complaint - no manual button needed
        
        // Check for existing summons files and update UI state
        await checkAndUpdateSummonsStatus(caseId);
        
    } catch (error) {
        console.error('Error loading summons interface:', error);
        document.getElementById('summons-defendants-list').innerHTML = `
            <div class="text-center py-8">
                <p class="text-red-600">Error loading defendants information.</p>
            </div>
        `;
    }
}

async function checkAndUpdateSummonsStatus(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}/summons-status`);
        if (!response.ok) {
            console.log('No existing summons found');
            return;
        }
        
        const summonsStatus = await response.json();
        console.log('Summons status:', summonsStatus);
        
        if (summonsStatus.exists && summonsStatus.count > 0) {
            // Update generation status header
            updateSummonsGenerationStatus(summonsStatus.last_generated, summonsStatus.count);
            
            // Update individual defendant statuses
            for (let i = 0; i < summonsStatus.count; i++) {
                const statusElement = document.getElementById(`summons-status-${i}`);
                const printButton = document.getElementById(`print-summons-${i}`);
                
                if (statusElement) {
                    statusElement.textContent = 'Generated';
                    statusElement.className = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800';
                }
                
                if (printButton) {
                    printButton.disabled = false;
                    printButton.classList.remove('opacity-50');
                }
            }
        }
        
    } catch (error) {
        console.error('Error checking summons status:', error);
    }
}

function updateSummonsGenerationStatus(lastGenerated, count) {
    // Find or create the status header element
    let statusHeader = document.getElementById('summons-generation-status');
    if (!statusHeader) {
        // Create status header if it doesn't exist
        const summonsContent = document.querySelector('#summons .tab-pane-content');
        if (summonsContent) {
            statusHeader = document.createElement('div');
            statusHeader.id = 'summons-generation-status';
            statusHeader.className = 'mb-4 p-3 bg-green-50 border border-green-200 rounded-lg';
            summonsContent.insertBefore(statusHeader, summonsContent.firstChild);
        }
    }
    
    if (statusHeader && lastGenerated) {
        const generatedDate = new Date(lastGenerated);
        const formattedDate = generatedDate.toLocaleString();
        
        statusHeader.innerHTML = `
            <div class="flex items-center text-green-800">
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                </svg>
                <span class="font-medium">Summons Generated</span>
            </div>
            <p class="text-sm text-green-700 mt-1">
                ${count} summons documents generated on ${formattedDate}
            </p>
        `;
    }
}

async function renderDefendantsList(defendants, caseId) {
    const container = document.getElementById('summons-defendants-list');
    
    let html = `
        <div class="space-y-4">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Defendants (${defendants.length})</h3>
    `;
    
    // Process defendants with async address formatting
    for (let index = 0; index < defendants.length; index++) {
        const defendant = defendants[index];
        const defendantName = defendant.name || `Defendant ${index + 1}`;
        const defendantAddress = await formatDefendantAddress(defendant.address, defendantName);
        
        html += `
            <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h4 class="font-semibold text-gray-900">${defendantName}</h4>
                        <p class="text-sm text-gray-600 mt-1">${defendantAddress}</p>
                        <div class="mt-2">
                            <span id="summons-status-${index}" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                Not Generated
                            </span>
                        </div>
                    </div>
                    <div class="ml-4">
                        <button 
                            id="print-summons-${index}" 
                            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm disabled:opacity-50" 
                            disabled
                            onclick="printIndividualSummons('${caseId}', ${index})">
                            Print Summons
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    html += `</div>`;
    container.innerHTML = html;
}

// Cache for creditor addresses
let creditorAddressCache = null;

async function loadCreditorAddresses() {
    if (creditorAddressCache) return creditorAddressCache;
    
    try {
        const response = await fetch('/api/creditor-addresses');
        if (response.ok) {
            const data = await response.json();
            creditorAddressCache = data.creditor_addresses || {};
            return creditorAddressCache;
        }
    } catch (error) {
        console.error('Failed to load creditor addresses:', error);
    }
    
    return {};
}

function getCreditorAddressKey(defendantName) {
    // Convert defendant name to match creditor address keys
    // e.g., "Experian Information Solutions, Inc. (Ohio corporation...)" -> "experian_information_solutions_inc"
    
    // First, stop at the first parenthesis (remove entity type info)
    let cleanName = defendantName;
    if (cleanName.includes('(')) {
        cleanName = cleanName.split('(')[0].trim();
    }
    
    return cleanName
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, '') // Remove punctuation
        .replace(/\s+/g, '_') // Replace spaces with underscores
        .replace(/_+/g, '_') // Clean up multiple underscores
        .replace(/^_|_$/g, ''); // Remove leading/trailing underscores
}

async function formatDefendantAddress(address, defendantName) {
    // First try to get address from creditor directory
    if (defendantName) {
        const creditorAddresses = await loadCreditorAddresses();
        const creditorKey = getCreditorAddressKey(defendantName);
        
        console.log(`🔍 CREDITOR DEBUG: "${defendantName}" -> "${creditorKey}"`);
        console.log('🔍 Available creditor keys:', Object.keys(creditorAddresses));
        
        // Test exact matches for known defendants
        const testMatches = {
            'trans_union_llc': creditorAddresses['trans_union_llc'],
            'td_bank_na': creditorAddresses['td_bank_na'], 
            'experian_information_solutions_inc': creditorAddresses['experian_information_solutions_inc'],
            'equifax_information_services_llc': creditorAddresses['equifax_information_services_llc']
        };
        console.log('🔍 Test matches:', testMatches);
        
        if (creditorAddresses[creditorKey] && creditorAddresses[creditorKey].address) {
            const creditorAddr = creditorAddresses[creditorKey].address;
            const parts = [];
            if (creditorAddr.street) parts.push(creditorAddr.street);
            if (creditorAddr.city || creditorAddr.state || creditorAddr.zip_code) {
                const cityStateZip = [creditorAddr.city, creditorAddr.state, creditorAddr.zip_code].filter(Boolean).join(' ');
                if (cityStateZip) parts.push(cityStateZip);
            }
            if (parts.length > 0) {
                console.log(`✅ CREDITOR MATCH: Found address for ${defendantName}:`, parts.join(', '));
                return parts.join(', ');
            }
        } else {
            console.log(`❌ CREDITOR MISS: No address found for key "${creditorKey}"`);
        }
    }
    
    // Fall back to extracted address from case data
    if (!address) {
        console.log('❌ NO ADDRESS: Neither creditor nor extracted address available');
        return 'Address not available';
    }
    
    const parts = [];
    if (address.street) parts.push(address.street);
    if (address.city || address.state || address.zip_code) {
        const cityStateZip = [address.city, address.state, address.zip_code].filter(Boolean).join(' ');
        if (cityStateZip) parts.push(cityStateZip);
    }
    
    console.log(`🔄 EXTRACTED: Using extracted address:`, parts.join(', '));
    return parts.length > 0 ? parts.join(', ') : 'Address not available';
}

// generateAllSummons function removed - summons are now auto-generated with complaint

function updateSummonsStatus(summonsFiles) {
    summonsFiles.forEach((file, index) => {
        const statusElement = document.getElementById(`summons-status-${index}`);
        const printButton = document.getElementById(`print-summons-${index}`);
        
        if (statusElement) {
            statusElement.textContent = 'Generated';
            statusElement.className = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800';
        }
        
        if (printButton) {
            printButton.disabled = false;
            printButton.classList.remove('opacity-50');
        }
    });
    
    // Also update the generation status header with current timestamp
    const now = new Date().toISOString();
    updateSummonsGenerationStatus(now, summonsFiles.length);
}

function printIndividualSummons(caseId, defendantIndex) {
    console.log(`Opening summons for case ${caseId}, defendant ${defendantIndex}`);
    
    // Open summons in new tab for printing
    const summonsUrl = `/summons/${caseId}/${defendantIndex}.html`;
    window.open(summonsUrl, '_blank');
}

// Legal Packet Interface Functions
async function loadLegalPacketInterface(caseId) {
    console.log('Loading legal packet interface for case:', caseId);
    
    try {
        // Load packet data from API
        const response = await fetch(`/api/cases/${caseId}/packet-data`);
        if (!response.ok) {
            throw new Error('Failed to load packet data');
        }
        
        const packetData = await response.json();
        
        // Render the three sections
        renderGeneratedDocuments(packetData.generated_documents || []);
        renderSourceDocuments(packetData.source_documents || []);
        renderProcessingSummary(packetData.processing_data || {});
        renderProcessingData(packetData.processing_data || {});
        
        // Setup button handlers
        setupPacketButtonHandlers(caseId);
        
    } catch (error) {
        console.error('Error loading packet interface:', error);
        showPacketError('Failed to load legal packet data. Please try again.');
    }
}

function renderGeneratedDocuments(documents) {
    const container = document.getElementById('generated-documents');
    console.log('Generated documents:', documents);
    
    if (documents.length === 0) {
        container.innerHTML = `
            <div class="text-center py-6">
                <p class="text-gray-500">No generated documents found.</p>
                <p class="text-sm text-gray-400 mt-1">Documents will appear here after generating the complaint.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    documents.forEach(doc => {
        const createdDate = new Date(doc.created_at).toLocaleString();
        const modifiedDate = doc.modified_at ? new Date(doc.modified_at).toLocaleString() : 'Not modified';
        const fileSize = doc.size ? formatFileSize(doc.size) : 'Unknown size';
        
        html += `
            <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <div class="flex items-center mb-2">
                            <span class="text-lg mr-2">${getDocumentIcon(doc.type)}</span>
                            <h4 class="font-semibold text-gray-900">${doc.name}</h4>
                            <span class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                Generated
                            </span>
                        </div>
                        <div class="text-sm text-gray-600">
                            <p>Type: ${doc.type} | Size: ${fileSize} | Modified: ${modifiedDate}${doc.edit_count ? ` | Edits: ${doc.edit_count} revision(s)` : ''}</p>
                        </div>
                    </div>
                    <div class="ml-4 flex flex-col space-y-2">
                        <button class="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                                onclick="viewDocument('${doc.view_url || doc.path}')">
                            View
                        </button>
                        <button class="px-3 py-1 border border-gray-300 text-gray-700 rounded text-sm hover:bg-gray-50 hover:border-gray-400"
                                onclick="downloadDocument('${doc.view_url || doc.path}', '${doc.name}')">
                            Download
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function renderSourceDocuments(documents) {
    const container = document.getElementById('source-documents');
    console.log('Source documents:', documents);
    
    if (documents.length === 0) {
        container.innerHTML = `
            <div class="text-center py-6">
                <p class="text-gray-500">No source documents found.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    documents.forEach(doc => {
        const syncedDate = new Date(doc.synced_at).toLocaleString();
        const modifiedDate = new Date(doc.modified_at).toLocaleString();
        const fileSize = formatFileSize(doc.size);
        
        html += `
            <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <div class="flex items-center mb-2">
                            <span class="text-lg mr-2">${getDocumentIcon(doc.type)}</span>
                            <h4 class="font-semibold text-gray-900">${doc.name}</h4>
                            <span class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                Source
                            </span>
                        </div>
                        <div class="text-sm text-gray-600">
                            <p>Type: ${doc.type} | Size: ${fileSize} | Synced: ${syncedDate} | Modified: ${modifiedDate}</p>
                        </div>
                    </div>
                    <div class="ml-4 flex flex-col space-y-2">
                        <button class="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                                onclick="viewDocument('${doc.view_url || doc.path}')">
                            View
                        </button>
                        <button class="px-3 py-1 border border-gray-300 text-gray-700 rounded text-sm hover:bg-gray-50 hover:border-gray-400"
                                onclick="downloadDocument('${doc.view_url || doc.path}', '${doc.name}')">
                            Download
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function renderProcessingSummary(data) {
    const container = document.getElementById('processing-summary');
    
    const validationScore = data.validation_score || 0;
    const statusColor = validationScore >= 100 ? 'text-green-600' : validationScore >= 95 ? 'text-blue-600' : 'text-orange-600';
    const statusIcon = validationScore >= 100 ? '✅' : validationScore >= 95 ? '🔄' : '⚠️';
    const statusText = validationScore >= 100 ? 'Complete' : validationScore >= 95 ? 'Processing' : 'Needs Review';
    
    container.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="text-center">
                <div class="text-3xl font-bold ${statusColor} mb-1">${statusIcon} ${statusText}</div>
                <p class="text-sm text-gray-600">Case Status</p>
            </div>
            <div class="text-center">
                <div class="text-3xl font-bold text-blue-600 mb-1">${validationScore}%</div>
                <p class="text-sm text-gray-600">Validation Score</p>
            </div>
            <div class="text-center">
                <div class="text-3xl font-bold text-purple-600 mb-1">${data.files_processed || 0}</div>
                <p class="text-sm text-gray-600">Files Processed</p>
            </div>
            <div class="text-center">
                <div class="text-3xl font-bold text-indigo-600 mb-1">${data.generated_count || 0}</div>
                <p class="text-sm text-gray-600">Documents Generated</p>
            </div>
        </div>
    `;
}

function renderProcessingData(data) {
    const container = document.getElementById('processing-data');
    
    const processedDate = data.processed_at ? new Date(data.processed_at).toLocaleString() : 'Not processed';
    const extractionTime = data.processing_time ? `${data.processing_time}s` : 'Unknown';
    const validationScore = data.validation_score || 'Not available';
    
    container.innerHTML = `
        <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                    <h5 class="font-semibold text-gray-800 mb-2">🔍 Processing Status</h5>
                    <div class="text-sm text-gray-600 space-y-1">
                        <p><strong>Processed:</strong> ${processedDate}</p>
                        <p><strong>Processing Time:</strong> ${extractionTime}</p>
                        <p><strong>Status:</strong> <span class="text-green-600 font-medium">Complete</span></p>
                    </div>
                </div>
                <div>
                    <h5 class="font-semibold text-gray-800 mb-2">✅ Data Quality</h5>
                    <div class="text-sm text-gray-600 space-y-1">
                        <p><strong>Validation Score:</strong> ${validationScore}%</p>
                        <p><strong>Files Processed:</strong> ${data.files_processed || 0}</p>
                        <p><strong>Entities Extracted:</strong> ${data.entities_extracted || 0}</p>
                    </div>
                </div>
                <div>
                    <h5 class="font-semibold text-gray-800 mb-2">📊 Case Statistics</h5>
                    <div class="text-sm text-gray-600 space-y-1">
                        <p><strong>Total Files:</strong> ${data.total_files || 0}</p>
                        <p><strong>Generated Docs:</strong> ${data.generated_count || 0}</p>
                        <p><strong>Last Updated:</strong> ${data.last_updated ? new Date(data.last_updated).toLocaleString() : 'Unknown'}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function setupPacketButtonHandlers(caseId) {
    // Download Packet button
    const downloadBtn = document.getElementById('download-packet');
    downloadBtn.addEventListener('click', () => downloadLegalPacket(caseId));
    
}

// Helper functions
function getDocumentIcon(type) {
    const icons = {
        'complaint': '⚖️',
        'summons': '📋',
        'pdf': '📄',
        'docx': '📝',
        'txt': '📃',
        'default': '📄'
    };
    return icons[type.toLowerCase()] || icons.default;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function viewDocument(path) {
    // Open document in new tab for viewing
    console.log('ViewDocument called with path:', path);
    window.open(path, '_blank');
}

function downloadDocument(path, filename) {
    // Create download link and trigger download
    const link = document.createElement('a');
    link.href = path;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

async function downloadLegalPacket(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}/download-packet`, {
            method: 'POST'
        });
        if (!response.ok) {
            throw new Error('Failed to create packet download');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${caseId}-legal-packet.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        showSuccessMessage('Legal packet downloaded successfully!');
    } catch (error) {
        console.error('Download packet error:', error);
        showErrorMessage('Failed to download legal packet. Please try again.');
    }
}


function showPacketError(message) {
    const container = document.getElementById('generated-documents');
    container.innerHTML = `
        <div class="text-center py-8">
            <div class="text-red-400 text-4xl mb-4">⚠️</div>
            <p class="text-red-600 font-medium">${message}</p>
        </div>
    `;
}

function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded z-50';
    successDiv.innerHTML = `
        <div class="flex items-center">
            <strong class="font-bold">Success!</strong>
            <span class="block sm:inline ml-2">${message}</span>
        </div>
    `;
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.parentNode.removeChild(successDiv);
        }
    }, 3000);
}

async function autoSaveDefaultSelections(caseId, caseData) {
    console.log(`🔄 AUTO-SAVE: Starting automatic save of default selections for case ${caseId}`);
    
    try {
        // Check if we already have saved selections to avoid overriding lawyer's choices
        const hasExistingSelections = document.querySelectorAll('input[name="legal_claim"]:checked').length > 0;
        
        // Collect all currently selected checkboxes (auto-selected 50%+ confidence claims)
        const checkboxes = document.querySelectorAll('input[name="legal_claim"]');
        const selections = [];
        let autoSelectedCount = 0;
        
        checkboxes.forEach(checkbox => {
            const causeIndex = parseInt(checkbox.getAttribute('data-cause'));
            const claimIndex = parseInt(checkbox.getAttribute('data-claim'));
            const selected = checkbox.checked;
            
            if (selected) {
                autoSelectedCount++;
            }
            
            selections.push({
                cause_index: causeIndex,
                claim_index: claimIndex,
                selected: selected
            });
        });
        
        // Only auto-save if we have high-confidence claims selected
        if (autoSelectedCount === 0) {
            console.log(`🔄 AUTO-SAVE: No high-confidence claims found, skipping auto-save`);
            return;
        }
        
        console.log(`🔄 AUTO-SAVE: Found ${autoSelectedCount} high-confidence claims to auto-save`);
        
        // Auto-save selections silently (no UI feedback)
        const response = await fetch(`/api/cases/${caseId}/legal-claims`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                selections: selections,
                auto_save: true  // Flag to indicate this is an automatic save
            })
        });

        if (!response.ok) {
            console.warn(`🔄 AUTO-SAVE: Failed to auto-save selections: ${response.status}`);
            return;
        }

        const result = await response.json();
        console.log(`✅ AUTO-SAVE: Successfully auto-saved ${autoSelectedCount} high-confidence legal claims`);
        
        // Show discrete success notification
        showDiscreteNotification('✅ High-confidence claims auto-selected and saved');
        
        // Update save button to show it's already saved
        const saveBtn = document.getElementById('save-selections-btn');
        if (saveBtn) {
            saveBtn.textContent = '✅ High-confidence claims auto-saved';
            saveBtn.className = 'px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium';
            saveBtn.disabled = true;
        }
        
    } catch (error) {
        console.error('🔄 AUTO-SAVE: Error during auto-save:', error);
        // Fail silently - don't interrupt the user's workflow
    }
}

function showDiscreteNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'fixed bottom-4 right-4 bg-blue-100 border border-blue-400 text-blue-700 px-4 py-2 rounded-lg z-50 text-sm shadow-lg';
    notification.innerHTML = `
        <div class="flex items-center">
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }, 4000);
}

function handleClaimSelectionChange() {
    console.log('📝 User made manual claim selection change');
    
    // Enable save button when user makes manual changes
    const saveBtn = document.getElementById('save-selections-btn');
    if (saveBtn) {
        saveBtn.textContent = 'Save Your Changes';
        saveBtn.className = 'px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium';
        saveBtn.disabled = false;
        
        // Add visual indicator that changes need saving
        if (!saveBtn.classList.contains('pulse-attention')) {
            saveBtn.classList.add('pulse-attention');
            // Remove after 5 seconds
            setTimeout(() => {
                saveBtn.classList.remove('pulse-attention');
            }, 5000);
        }
    }
}

// Add global CSS for pulse attention effect
if (!document.getElementById('review-auto-save-styles')) {
    const styles = document.createElement('style');
    styles.id = 'review-auto-save-styles';
    styles.textContent = `
        .pulse-attention {
            animation: pulse-blue 2s ease-in-out infinite;
        }
        
        @keyframes pulse-blue {
            0%, 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
            50% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); }
        }
    `;
    document.head.appendChild(styles);
}

function showErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded z-50';
    errorDiv.innerHTML = `
        <div class="flex items-center">
            <strong class="font-bold">Error!</strong>
            <span class="block sm:inline ml-2">${message}</span>
        </div>
    `;
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}

// ===============================
// COMPLAINT EDITING FUNCTIONALITY
// ===============================

let editState = {
    isEditing: false,
    originalContent: null,
    hasChanges: false,
    currentCaseId: null,
    autoSaveTimer: null
};

async function enterEditMode(caseId) {
    console.log(`📝 ENTERING EDIT MODE for case: ${caseId}`);
    
    try {
        // Fetch the raw HTML content for editing
        const response = await fetch(`/api/cases/${caseId}/complaint-content`);
        if (!response.ok) {
            throw new Error(`Failed to fetch complaint content: ${response.status}`);
        }
        
        const data = await response.json();
        const htmlContent = data.html_content;
        
        // Store original content and case ID
        editState.originalContent = htmlContent;
        editState.currentCaseId = caseId;
        editState.isEditing = true;
        editState.hasChanges = false;
        
        // Transform preview into editable mode
        const contentDiv = document.getElementById('preview-content');
        const editControls = document.getElementById('edit-controls');
        
        // Replace iframe with editable div
        contentDiv.innerHTML = `
            <div class="edit-mode-indicator mb-3 p-2 bg-blue-100 border-l-4 border-blue-500 text-blue-700">
                <strong>EDITING MODE:</strong> Click in the document below to edit content
            </div>
            <style>
                #editable-complaint .section-title { 
                    font-weight: bold; 
                    text-align: center; 
                    margin-top: 20px; 
                    margin-bottom: 10px; 
                }
                #editable-complaint .caption { 
                    text-align: center; 
                    font-weight: bold; 
                }
                #editable-complaint .case-number { 
                    text-align: right; 
                }
                #editable-complaint p { 
                    margin-bottom: 10px; 
                    line-height: 1.5; 
                }
            </style>
            <div id="editable-complaint" 
                 contenteditable="true" 
                 class="edit-content p-6 bg-white border-2 border-blue-300 rounded-lg"
                 style="height: calc(100% - 120px); overflow-y: auto; font-family: 'Times New Roman', serif; line-height: 1.6;">
                ${htmlContent}
            </div>
        `;
        
        // Show edit controls
        editControls.classList.remove('hidden');
        
        // Hide other buttons during edit mode
        const editBtn = document.getElementById('edit-complaint');
        const openTabBtn = document.getElementById('open-in-new-tab');
        const generateBtn = document.getElementById('generate-complaint');
        
        editBtn.classList.add('hidden');
        openTabBtn.classList.add('hidden');
        generateBtn.classList.add('hidden');
        
        // Set up event handlers
        setupEditEventHandlers();
        
        // Start auto-save timer
        startAutoSave();
        
        showSuccessMessage('Edit mode activated! Click in the document to make changes.');
        
    } catch (error) {
        console.error('Failed to enter edit mode:', error);
        showErrorMessage('Failed to load complaint for editing. Please try again.');
    }
}

function setupEditEventHandlers() {
    const editableDiv = document.getElementById('editable-complaint');
    const saveBtn = document.getElementById('save-edit');
    const cancelBtn = document.getElementById('cancel-edit');
    
    // Track changes in the content
    if (editableDiv) {
        editableDiv.addEventListener('input', () => {
            editState.hasChanges = true;
            saveBtn.disabled = false;
            saveBtn.classList.remove('bg-gray-400');
            saveBtn.classList.add('bg-green-600', 'hover:bg-green-700');
        });
        
        // Add visual feedback on focus
        editableDiv.addEventListener('focus', () => {
            editableDiv.classList.add('ring-2', 'ring-blue-500');
        });
        
        editableDiv.addEventListener('blur', () => {
            editableDiv.classList.remove('ring-2', 'ring-blue-500');
        });
    }
    
    // Save button handler
    if (saveBtn) {
        saveBtn.onclick = () => saveComplaintEdits();
    }
    
    // Cancel button handler
    if (cancelBtn) {
        cancelBtn.onclick = () => cancelEditMode();
    }
    
    // Prevent accidental navigation during editing
    window.addEventListener('beforeunload', (event) => {
        if (editState.isEditing && editState.hasChanges) {
            event.preventDefault();
            event.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return event.returnValue;
        }
    });
}

async function saveComplaintEdits() {
    const saveBtn = document.getElementById('save-edit');
    const saveText = saveBtn.querySelector('.save-text');
    const saveSpinner = saveBtn.querySelector('.save-spinner');
    const editableDiv = document.getElementById('editable-complaint');
    
    if (!editableDiv || !editState.hasChanges) {
        return;
    }
    
    try {
        // Show loading state
        saveText.classList.add('hidden');
        saveSpinner.classList.remove('hidden');
        saveBtn.disabled = true;
        
        const editedContent = editableDiv.innerHTML;
        
        // Prepare the save request
        const saveData = {
            html_content: editedContent,
            change_summary: 'Manual edits made through dashboard interface',
            user_id: 'dashboard_user' // This could be enhanced with actual user tracking
        };
        
        const response = await fetch(`/api/cases/${editState.currentCaseId}/save-complaint-edits`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(saveData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Save failed: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Success feedback - removed alert per user request
        console.log(`✅ SAVE COMPLETE:`, result);
        
        // Update state
        editState.hasChanges = false;
        editState.originalContent = editedContent;
        
        // Reset button state
        saveText.classList.remove('hidden');
        saveSpinner.classList.add('hidden');
        saveBtn.disabled = true;
        saveBtn.classList.remove('bg-green-600', 'hover:bg-green-700');
        saveBtn.classList.add('bg-gray-400');
        
        // Auto-return to preview mode after successful save
        setTimeout(() => {
            exitEditMode();
        }, 1000); // Brief delay to show save completion
        
    } catch (error) {
        console.error('Failed to save complaint edits:', error);
        showErrorMessage(`Failed to save changes: ${error.message}`);
        
        // Reset button state
        saveText.classList.remove('hidden');
        saveSpinner.classList.add('hidden');
        saveBtn.disabled = false;
        saveBtn.classList.remove('bg-gray-400');
        saveBtn.classList.add('bg-green-600', 'hover:bg-green-700');
    }
}

function cancelEditMode() {
    if (editState.hasChanges) {
        if (!confirm('You have unsaved changes. Are you sure you want to cancel?')) {
            return;
        }
    }
    
    exitEditMode();
    showSuccessMessage('Edit mode cancelled. No changes were saved.');
}

function exitEditMode() {
    console.log(`🚪 EXITING EDIT MODE for case: ${editState.currentCaseId}`);
    
    // Clear auto-save timer
    if (editState.autoSaveTimer) {
        clearInterval(editState.autoSaveTimer);
        editState.autoSaveTimer = null;
    }
    
    // Reset edit state
    editState.isEditing = false;
    editState.hasChanges = false;
    editState.originalContent = null;
    const caseId = editState.currentCaseId;
    editState.currentCaseId = null;
    
    // Hide edit controls
    const editControls = document.getElementById('edit-controls');
    editControls.classList.add('hidden');
    
    // Show regular buttons
    const editBtn = document.getElementById('edit-complaint');
    const openTabBtn = document.getElementById('open-in-new-tab');
    const generateBtn = document.getElementById('generate-complaint');
    
    editBtn.classList.remove('hidden');
    openTabBtn.classList.remove('hidden');
    generateBtn.classList.remove('hidden');
    
    // Reload the complaint in preview mode
    if (caseId) {
        loadExistingComplaint(caseId);
    }
}

function startAutoSave() {
    // Auto-save draft every 30 seconds
    editState.autoSaveTimer = setInterval(() => {
        if (editState.isEditing && editState.hasChanges) {
            const editableDiv = document.getElementById('editable-complaint');
            if (editableDiv) {
                const draftContent = editableDiv.innerHTML;
                localStorage.setItem(`complaint_draft_${editState.currentCaseId}`, draftContent);
                console.log('📝 Draft auto-saved to localStorage');
            }
        }
    }, 30000);
}

function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded z-50';
    successDiv.innerHTML = `
        <div class="flex items-center">
            <strong class="font-bold">Success!</strong>
            <span class="block sm:inline ml-2">${message}</span>
        </div>
    `;
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.parentNode.removeChild(successDiv);
        }
    }, 4000);
}