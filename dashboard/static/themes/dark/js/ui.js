// dashboard/static/themes/light/js/ui.js

const caseGrid = document.getElementById('case-grid');

function getStatusClasses(status) {
    switch (status) {
        case 'New':
            return 'bg-blue-100 text-blue-800';
        case 'Pending Review':
            return 'bg-yellow-100 text-yellow-800';
        case 'Complete':
        case 'Processed': // Note: "Processed" is an intermediate step, but we'll use green for now.
            return 'bg-green-100 text-green-800';
        case 'Error':
            return 'bg-red-100 text-red-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
}

function getActionButton(caseData) {
    const baseButtonClasses = "w-full text-center px-4 py-3 rounded-lg font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2";
    
    switch (caseData.status) {
        case 'New':
            return `<button class="process-btn ${baseButtonClasses} bg-gray-700 text-white hover:bg-gray-800 focus:ring-gray-500">Process Files</button>`;
        case 'Pending Review':
            return `<a href="/review?case_id=${caseData.id}" class="block ${baseButtonClasses} bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500">Review Case</a>`;
        case 'Complete':
            return `<button class="download-btn ${baseButtonClasses} bg-gray-200 text-gray-700 hover:bg-gray-300 focus:ring-gray-400 flex items-center justify-center">
                        <i data-feather="download" class="w-4 h-4 mr-2"></i>
                        Download Packet
                    </button>`;
        default: // Processing, Generating, Error, etc.
            return `<button class="${baseButtonClasses} bg-gray-400 text-white cursor-not-allowed" disabled>${caseData.status}...</button>`;
    }
}

function createProgressLights(progress) {
    const steps = ['synced', 'classified', 'extracted', 'reviewed', 'generated'];
    let lightsHtml = '<div class="flex items-center space-x-2">';
    
    steps.forEach(step => {
        const isComplete = progress[step];
        const lightClass = isComplete ? 'bg-green-500' : 'bg-gray-300';
        const title = step.charAt(0).toUpperCase() + step.slice(1);
        lightsHtml += `<div class="w-3 h-3 rounded-full ${lightClass}" title="${title}"></div>`;
    });

    lightsHtml += '</div>';
    return lightsHtml;
}


function createCaseCard(caseData) {
    const card = document.createElement('div');
    card.className = 'bg-white border border-gray-200 rounded-lg p-6 flex flex-col shadow-sm';
    card.dataset.caseId = caseData.id;

    const statusClasses = getStatusClasses(caseData.status);
    const actionButton = getActionButton(caseData);
    const progressLights = createProgressLights(caseData.progress);
    
    const defendantText = caseData.name; // Simplified for now

    const lastUpdated = new Date(caseData.last_updated).toLocaleString();

    card.innerHTML = `
        <div class="flex justify-between items-start mb-2">
            ${progressLights}
            <span class="px-2 py-1 text-xs font-medium rounded-full ${statusClasses}">${caseData.status}</span>
        </div>
        <div class="mb-4">
            <h3 class="text-lg font-bold text-gray-900">${caseData.name}</h3>
            <p class="text-sm text-gray-500">vs. TBD</p>
        </div>
        <div class="flex-grow mb-6">
            <p class="text-sm text-gray-500">Last activity: ${lastUpdated}</p>
        </div>
        <div>
            ${actionButton}
        </div>
    `;
    return card;
}

export function renderCases(cases) {
    if (!caseGrid) return;
    
    const activeSearch = document.getElementById('search-bar').value.toLowerCase();
    
    // Preserve scroll position
    const scrollPosition = window.scrollY;

    caseGrid.innerHTML = ''; // Clear existing grid
    
    const filteredCases = cases.filter(c => c.name.toLowerCase().includes(activeSearch));

    if (filteredCases.length === 0) {
        caseGrid.innerHTML = '<p class="text-gray-500">No cases found.</p>';
        return;
    }

    filteredCases.forEach(caseData => {
        const card = createCaseCard(caseData);
        caseGrid.appendChild(card);
    });

    // After rendering, replace feather icons
    feather.replace();
    
    // Restore scroll position
    window.scrollTo(0, scrollPosition);
}

export function renderVersion(version) {
    const versionElement = document.getElementById('app-version');
    if (versionElement) {
        versionElement.textContent = `v${version}`;
    }
}
