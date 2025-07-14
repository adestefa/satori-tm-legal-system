// dashboard/static/themes/lexigen/js/main.js

import { getCases, getVersion } from './api.js';
import { renderCases, renderVersion } from './ui.js';
import { initializeEventListeners } from './eventHandlers.js';

const POLLING_INTERVAL = 5000; // 5 seconds

async function main() {
    const cases = await getCases();
    renderCases(cases);
}

async function updateVersion() {
    const data = await getVersion();
    renderVersion(data.version);
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    main();
    updateVersion();
    initializeEventListeners();

    // Start polling
    setInterval(main, POLLING_INTERVAL);
});
