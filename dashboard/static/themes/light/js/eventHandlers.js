// dashboard/static/js/eventHandlers.js

import { processCase } from './api.js';
import { setCurrentFilter } from './ui.js';

const caseGrid = document.getElementById('case-grid');

export function initializeEventListeners() {
    if (!caseGrid) return;

    console.log("Initializing event listeners");
    caseGrid.addEventListener('click', async (event) => {
        // Remove conflicting process-btn handler - now handled by onclick with validation
        // if (event.target.classList.contains('process-btn')) {
        //     Moved to onclick="handleProcessWithValidation(this)" in ui.js for proper validation
        // }
        
        // Keep other event handlers here if needed in the future
        console.log("Event delegation active for future handlers");
    });
    
    // Search functionality
    const searchBar = document.getElementById('search-bar');
    const searchClearBtn = document.getElementById('search-clear-btn');
    
    if (searchBar) {
        searchBar.addEventListener('input', handleSearch);
        
        // Show/hide clear button based on input
        searchBar.addEventListener('input', function() {
            if (searchClearBtn) {
                if (this.value.length > 0) {
                    searchClearBtn.classList.remove('hidden');
                } else {
                    searchClearBtn.classList.add('hidden');
                }
            }
        });
    }
    
    // Clear search functionality
    if (searchClearBtn) {
        searchClearBtn.addEventListener('click', function() {
            if (searchBar) {
                searchBar.value = '';
                searchClearBtn.classList.add('hidden');
                // Trigger search to reset view
                handleSearch({ target: { value: '' } });
            }
        });
    }
    
    // Manual sync button
    const syncButton = document.getElementById('sync-button');
    if (syncButton) {
        syncButton.addEventListener('click', handleManualSync);
    }
    
    // Filter buttons
    initializeFilterButtons();
}

function initializeFilterButtons() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            
            const filter = this.getAttribute('data-filter');
            console.log('Filter button clicked:', filter);
            
            // Update active state
            filterButtons.forEach(btn => {
                btn.classList.remove('text-blue-600', 'bg-blue-50');
                btn.classList.add('text-slate-600');
            });
            
            this.classList.remove('text-slate-600');
            this.classList.add('text-blue-600', 'bg-blue-50');
            
            // Update page title
            updatePageTitle(filter);
            
            // Apply filter
            applyStatusFilter(filter);
        });
    });
}

function updatePageTitle(filter) {
    const pageTitle = document.querySelector('h2');
    if (pageTitle) {
        switch (filter) {
            case 'all':
                pageTitle.textContent = 'All Cases';
                break;
            case 'New':
                pageTitle.textContent = 'New Cases';
                break;
            case 'Pending Review':
                pageTitle.textContent = 'Pending Review';
                break;
            case 'Complete':
                pageTitle.textContent = 'Completed Cases';
                break;
            default:
                pageTitle.textContent = 'All Cases';
        }
    }
}

function applyStatusFilter(filter) {
    console.log('Applying filter:', filter);
    
    // Store the current filter to preserve during polling updates
    setCurrentFilter(filter);
    
    // Get all case cards
    const caseCards = document.querySelectorAll('[data-case-id]');
    console.log('Found case cards:', caseCards.length);
    
    let visibleCount = 0;
    
    caseCards.forEach(card => {
        const statusBadge = card.querySelector('.status-badge');
        const caseStatus = statusBadge?.textContent?.trim() || '';
        const caseId = card.dataset.caseId;
        console.log(`🔧 FILTER DEBUG: Card ${caseId} status: "${caseStatus}", Filter: "${filter}"`);
        
        // Check if button exists and its current display state
        const button = card.querySelector(`#${caseId}_button`);
        if (button) {
            console.log(`🔧 FILTER DEBUG: Button for ${caseId} before filter - display: "${button.style.display}"`);
        }
        
        if (filter === 'all' || caseStatus === filter) {
            card.style.display = '';
            visibleCount++;
            console.log(`🔧 FILTER DEBUG: Card ${caseId} set to VISIBLE`);
        } else {
            card.style.display = 'none';
            console.log(`🔧 FILTER DEBUG: Card ${caseId} set to HIDDEN`);
        }
        
        // Check button state after filter
        if (button) {
            console.log(`🔧 FILTER DEBUG: Button for ${caseId} after filter - display: "${button.style.display}"`);
        }
    });
    
    console.log('Visible cards after filter:', visibleCount);
    
    // CRITICAL FIX: Ensure NO buttons have display:none applied directly
    // Buttons should only be controlled by their parent card's visibility
    const allButtons = document.querySelectorAll('[data-case-id] button, [data-case-id] a[id$="_button"]');
    allButtons.forEach(button => {
        if (button.style.display === 'none') {
            console.log(`🔧 FILTER FIX: Removing display:none from button ${button.id}`);
            button.style.display = '';
        }
    });
    
    // Update counts
    updateFilterCounts();
    
    // Show "No results" message if no cards are visible
    const caseGrid = document.getElementById('case-grid');
    let noResultsMessage = document.getElementById('no-results-message');
    
    if (visibleCount === 0 && filter !== 'all') {
        if (!noResultsMessage) {
            noResultsMessage = document.createElement('div');
            noResultsMessage.id = 'no-results-message';
            noResultsMessage.className = 'w-full text-center text-gray-500 py-8';
            noResultsMessage.innerHTML = `
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
                </svg>
                <p class="mt-2 text-lg font-medium">No ${filter.toLowerCase()} cases</p>
                <p class="text-sm">Try selecting "All Cases" to see all available cases</p>
            `;
            caseGrid.appendChild(noResultsMessage);
        }
        noResultsMessage.style.display = '';
    } else if (noResultsMessage) {
        noResultsMessage.style.display = 'none';
    }
}

export function updateFilterCounts() {
    const caseCards = document.querySelectorAll('[data-case-id]');
    let newCount = 0;
    let pendingCount = 0;
    let completeCount = 0;
    
    caseCards.forEach(card => {
        const statusBadge = card.querySelector('.status-badge');
        const caseStatus = statusBadge?.textContent?.trim() || '';
        
        if (caseStatus === 'New') {
            newCount++;
        } else if (caseStatus === 'Pending Review') {
            pendingCount++;
        } else if (caseStatus === 'Complete') {
            completeCount++;
        }
    });
    
    // Update count badges
    const newCountElement = document.getElementById('new-count');
    const pendingCountElement = document.getElementById('pending-count');
    const completeCountElement = document.getElementById('complete-count');
    
    if (newCountElement) {
        newCountElement.textContent = newCount;
    }
    
    if (pendingCountElement) {
        pendingCountElement.textContent = pendingCount;
    }
    
    if (completeCountElement) {
        completeCountElement.textContent = completeCount;
    }
}

function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase().trim();
    console.log('Search term:', searchTerm);
    
    // Get all case cards
    const caseCards = document.querySelectorAll('[data-case-id]');
    
    caseCards.forEach(card => {
        const caseId = card.getAttribute('data-case-id');
        
        // Get case name from h3 element (based on actual HTML structure)
        const caseName = card.querySelector('h3')?.textContent || '';
        
        // Get case ID which may contain case number information
        const caseIdText = caseId || '';
        
        // Search in case name and case ID
        const searchableText = `${caseName} ${caseIdText}`.toLowerCase();
        
        if (searchTerm === '' || searchableText.includes(searchTerm)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show "No results" message if no cards are visible
    const visibleCards = document.querySelectorAll('[data-case-id]:not([style*="display: none"])');
    const caseGrid = document.getElementById('case-grid');
    let noResultsMessage = document.getElementById('no-results-message');
    
    if (visibleCards.length === 0 && searchTerm !== '') {
        if (!noResultsMessage) {
            noResultsMessage = document.createElement('div');
            noResultsMessage.id = 'no-results-message';
            noResultsMessage.className = 'col-span-full text-center text-gray-500 py-8';
            noResultsMessage.innerHTML = `
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                </svg>
                <p class="mt-2 text-lg font-medium">No cases found</p>
                <p class="text-sm">Try adjusting your search terms</p>
            `;
            caseGrid.appendChild(noResultsMessage);
        }
        noResultsMessage.style.display = '';
    } else if (noResultsMessage) {
        noResultsMessage.style.display = 'none';
    }
}

async function handleManualSync() {
    const syncButton = document.getElementById('sync-button');
    const syncText = syncButton?.querySelector('.sync-text');
    
    if (!syncButton || !syncText) return;
    
    try {
        // Show loading state
        syncButton.disabled = true;
        syncText.textContent = 'Syncing...';
        syncButton.classList.add('opacity-75');
        
        // Use HTMX to refresh the case grid instead of full page refresh
        const caseGrid = document.getElementById('case-grid');
        if (caseGrid) {
            // Trigger HTMX refresh
            htmx.trigger(caseGrid, 'refresh');
        }
        
        // Show success feedback
        syncText.textContent = 'Synced!';
        setTimeout(() => {
            syncText.textContent = 'Manual Sync';
            syncButton.disabled = false;
            syncButton.classList.remove('opacity-75');
        }, 1000);
        
    } catch (error) {
        console.error('Manual sync failed:', error);
        syncText.textContent = 'Sync Failed';
        setTimeout(() => {
            syncText.textContent = 'Manual Sync';
            syncButton.disabled = false;
            syncButton.classList.remove('opacity-75');
        }, 2000);
    }
}
