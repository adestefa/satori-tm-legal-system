// dashboard/static/themes/light/js/config.js
// Single source of truth for all animation timing

export const ANIMATION_CONFIG = {
    // File processing timing (in seconds)
    PROCESSING_TIME: 10,     // Time showing ⏳ hourglass 
    TRANSITION_TIME: 5,      // Time for transition to next file
    
    // Calculated totals
    get TOTAL_PER_FILE() {
        return this.PROCESSING_TIME + this.TRANSITION_TIME; // 15 seconds
    },
    
    // Convert to milliseconds for setTimeout
    get PROCESSING_MS() {
        return this.PROCESSING_TIME * 1000; // 10000ms
    },
    
    get TRANSITION_MS() {
        return this.TRANSITION_TIME * 1000; // 5000ms
    },
    
    // Other UI timings
    POLLING_INTERVAL: 2000,     // 2 seconds
    TOAST_DURATION: 3000,       // 3 seconds
    BUTTON_DEBOUNCE: 1000       // 1 second
};

console.log(`⚙️ CONFIG: Animation timing - ${ANIMATION_CONFIG.TOTAL_PER_FILE}s per file (${ANIMATION_CONFIG.PROCESSING_TIME}s + ${ANIMATION_CONFIG.TRANSITION_TIME}s)`);