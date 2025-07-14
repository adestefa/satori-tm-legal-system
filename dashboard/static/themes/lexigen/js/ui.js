// dashboard/static/themes/lexigen/js/ui.js

const caseList = document.getElementById('case-list');

function getStatusClasses(status) {
    switch (status) {
        case 'New':
            return 'bg-blue-100 text-blue-800 border border-blue-200';
        case 'Pending Review':
            return 'bg-yellow-100 text-yellow-800 border border-yellow-200';
        case 'Complete':
        case 'Processed':
            return 'bg-green-100 text-green-800 border border-green-200';
        case 'Error':
            return 'bg-red-100 text-red-800 border border-red-200';
        default:
            return 'bg-gray-100 text-gray-800 border border-gray-200';
    }
}

function getActionButton(caseData) {
    const baseButtonClasses = "w-full text-center px-4 py-3 rounded-lg font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2";
    
    switch (caseData.status) {
        case 'New':
            return `<button class="process-btn ${baseButtonClasses} bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500">Process Files</button>`;
        case 'Pending Review':
            return `<a href="/review?case_id=${caseData.id}" class="block ${baseButtonClasses} bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500">Review Case</a>`;
        case 'Complete':
            return `<button class="download-btn ${baseButtonClasses} bg-gray-300 text-gray-600 border border-gray-300 hover:bg-gray-400 focus:ring-gray-400 flex items-center justify-center">
                        <i data-feather="download" class="w-4 h-4 mr-2"></i>
                        Download Packet
                    </button>`;
        default:
            return `<button class="${baseButtonClasses} bg-gray-400 text-white cursor-not-allowed" disabled>${caseData.status}...</button>`;
    }
}

function createCaseCard(caseData) {
    const card = document.createElement('div');
    card.className = 'bg-white border border-gray-200 rounded-lg p-6 flex justify-between items-center shadow-sm hover:shadow-md transition-shadow';
    card.dataset.caseId = caseData.id;

    const statusClasses = getStatusClasses(caseData.status);
    const actionButton = getActionButton(caseData);
    
    let timeText = '';
    if (caseData.status === 'Complete') {
        timeText = `Completed: ${caseData.completed_date}`;
    } else if (caseData.status === 'New' && caseData.detected_time) {
        const detectedTime = new Date(caseData.detected_time);
        const now = new Date();
        const diffMinutes = Math.floor((now - detectedTime) / (1000 * 60));
        timeText = `Detected: ${diffMinutes} minutes ago`;
    } else {
        const lastUpdated = new Date(caseData.last_updated);
        const now = new Date();
        const diffHours = Math.floor((now - lastUpdated) / (1000 * 60 * 60));
        timeText = `Last activity: ${diffHours} hours ago`;
    }

    card.innerHTML = `
        <div class="flex-1">
            <div class="flex justify-between items-start mb-3">
                <div>
                    <h3 class="text-lg font-semibold text-gray-900">${caseData.name}</h3>
                    <p class="text-sm text-gray-600">vs. ${caseData.defendant}</p>
                </div>
                <span class="px-3 py-1 text-xs font-medium rounded-full ${statusClasses}">${caseData.status}</span>
            </div>
            <p class="text-sm text-gray-500 mb-4">${timeText}</p>
        </div>
        <div class="w-48 ml-6">
            ${actionButton}
        </div>
    `;
    return card;
}

export function renderCases(cases) {
    if (!caseList) return;
    
    const activeSearch = document.getElementById('search-bar').value.toLowerCase();
    
    // Preserve scroll position
    const scrollPosition = window.scrollY;

    caseList.innerHTML = ''; // Clear existing list
    
    const filteredCases = cases.filter(c => 
        c.name.toLowerCase().includes(activeSearch) || 
        c.defendant.toLowerCase().includes(activeSearch)
    );

    if (filteredCases.length === 0) {
        caseList.innerHTML = '<p class="text-gray-500">No cases found.</p>';
        return;
    }

    filteredCases.forEach(caseData => {
        const card = createCaseCard(caseData);
        caseList.appendChild(card);
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
