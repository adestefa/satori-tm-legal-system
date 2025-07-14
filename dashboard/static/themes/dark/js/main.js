// dashboard/static/js/main.js

import { getCases, getVersion } from './api.js';
import { renderCases, renderVersion } from './ui.js';
import { initializeEventListeners } from './eventHandlers.js';

const POLLING_INTERVAL = 60000; // 1 minute

async function main() {
    const cases = await getCases();
    renderCases(cases);
}

async function updateVersion() {
    const versionData = await getVersion();
    renderVersion(versionData.version);
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    main();
    updateVersion();
    initializeEventListeners();

    // Start polling
    setInterval(main, POLLING_INTERVAL);
});
