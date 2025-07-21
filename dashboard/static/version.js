// SATORI AI VERSION MANAGEMENT (JSONP)
// ====================================
// Single source of truth for all version references
// Auto-generated on server startup

window.satoriVersion = {
    version: "2.1.8",
    buildDate: "2025-07-21",
    gitCommit: "b71b67f",
    environment: "development",
    features: {
        deployment_infrastructure: true,
        go_adapter: true,
        shadow_repository: true,
        client_data_protection: true
    },
    // Cache busting parameter for asset loading
    cacheBuster: "2025072114"
};

// Auto-update DOM elements with version class
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
        // Update version display elements
        document.querySelectorAll('.version-display, .satori-version').forEach(el => {
            el.textContent = `v${window.satoriVersion.version}`;
        });
        
        // Update powered-by elements
        document.querySelectorAll('.powered-by-satori').forEach(el => {
            el.textContent = `Powered by Satori AI v${window.satoriVersion.version}`;
        });
        
        // Console logging for debugging
        console.log(`🚀 Satori AI Tiger-Monkey v${window.satoriVersion.version} - ${window.satoriVersion.environment}`);
        console.log(`📅 Build: ${window.satoriVersion.buildDate} | Commit: ${window.satoriVersion.gitCommit}`);
    });
}