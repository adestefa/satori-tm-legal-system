// dashboard/static/js/eventHandlers.js

import { processCase } from './api.js';

const caseGrid = document.getElementById('case-grid');

export function initializeEventListeners() {
    if (!caseGrid) return;

    caseGrid.addEventListener('click', async (event) => {
        if (event.target.classList.contains('process-btn')) {
            const card = event.target.closest('.case-card');
            const caseId = card.dataset.caseId;
            if (caseId) {
                console.log(`Processing case: ${caseId}`);
                event.target.textContent = 'Processing...';
                event.target.disabled = true;
                await processCase(caseId);
                // The UI will update on the next poll, no need to do anything here
            }
        }
    });
}
