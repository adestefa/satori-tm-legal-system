// dashboard/static/js/eventHandlers.js

import { processCase } from './api.js';
import { main } from './main.js';

const caseList = document.getElementById('case-list');

export function initializeEventListeners() {
    if (!caseList) return;

    caseList.addEventListener('click', async (event) => {
        if (event.target.classList.contains('process-btn')) {
            const card = event.target.closest('.case-card');
            const caseId = card.dataset.caseId;
            if (caseId) {
                console.log(`Processing case: ${caseId}`);
                event.target.textContent = 'Processing...';
                event.target.disabled = true;
                await processCase(caseId);
                main(); // Refresh the case list
            }
        }
    });
}
