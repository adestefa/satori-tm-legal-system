/**
 * Timeline Validation UI Components
 * MVP 1 Task 1.4 - Dashboard UI for Timeline Validation
 */

class TimelineValidationUI {
    constructor() {
        this.timelineData = null;
        this.caseId = null;
    }

    async init(caseId) {
        this.caseId = caseId;
        await this.loadTimelineData();
        this.setupTabHandling();
    }

    async loadTimelineData() {
        try {
            const response = await fetch(`/api/cases/${this.caseId}/validate-timeline`);
            this.timelineData = await response.json();
            
            if (this.timelineData.timeline_available) {
                this.renderTimelineValidation();
            } else {
                this.renderTimelineUnavailable();
            }
        } catch (error) {
            console.error('Failed to load timeline data:', error);
            this.renderTimelineError();
        }
    }

    setupTabHandling() {
        // Tab handling is now managed by review.js setupTabSwitching()
        // This method is kept for compatibility but doesn't add event listeners
    }

    renderTimelineValidation() {
        this.renderValidationBadge();
        this.renderTimelineOverview();
        this.renderTimelineChart();
        this.renderValidationIssues();
        this.renderDocumentDatesTable();
    }

    renderValidationBadge() {
        const badge = document.getElementById('timeline-validation-badge');
        if (!badge) return;

        const { is_chronologically_valid, validation_score } = this.timelineData;
        
        if (is_chronologically_valid) {
            badge.className = 'px-4 py-2 rounded-lg font-medium bg-green-100 text-green-800';
            badge.textContent = `✓ Valid (${Math.round(validation_score)}/100)`;
        } else {
            badge.className = 'px-4 py-2 rounded-lg font-medium bg-red-100 text-red-800';
            badge.textContent = `✗ Issues Found (${Math.round(validation_score)}/100)`;
        }
    }

    renderTimelineOverview() {
        this.renderKeyDatesSummary();
        this.renderValidationStatusSummary();
        this.renderDocumentCoverageSummary();
    }

    renderKeyDatesSummary() {
        const container = document.getElementById('key-dates-summary');
        if (!container) return;

        const { key_dates } = this.timelineData;
        const dates = [
            { label: 'Discovery Date', value: key_dates.discovery_date, required: false },
            { label: 'Dispute Date', value: key_dates.dispute_date, required: true },
            { label: 'Filing Date', value: key_dates.filing_date, required: true }
        ];

        container.innerHTML = dates.map(date => {
            const status = date.value ? '✓' : '○';
            const statusClass = date.value ? 'text-green-600' : (date.required ? 'text-red-600' : 'text-gray-400');
            const dateText = date.value || 'Not provided';
            
            return `
                <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-600">${date.label}:</span>
                    <span class="${statusClass} text-sm font-medium">${status} ${dateText}</span>
                </div>
            `;
        }).join('');
    }

    renderValidationStatusSummary() {
        const container = document.getElementById('validation-status-summary');
        if (!container) return;

        const { summary, timeline_confidence } = this.timelineData;
        
        container.innerHTML = `
            <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Timeline Confidence:</span>
                <span class="text-sm font-medium">${Math.round(timeline_confidence)}%</span>
            </div>
            <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Critical Errors:</span>
                <span class="text-sm font-medium text-red-600">${summary.critical_errors}</span>
            </div>
            <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Warnings:</span>
                <span class="text-sm font-medium text-yellow-600">${summary.warnings}</span>
            </div>
        `;
    }

    renderDocumentCoverageSummary() {
        const container = document.getElementById('document-coverage-summary');
        if (!container) return;

        const { summary } = this.timelineData;
        
        container.innerHTML = `
            <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Documents with Dates:</span>
                <span class="text-sm font-medium">${summary.document_dates_extracted}</span>
            </div>
            <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Key Dates Present:</span>
                <span class="text-sm font-medium">${summary.key_dates_present}/3</span>
            </div>
        `;
    }

    renderTimelineChart() {
        const container = document.getElementById('timeline-chart');
        if (!container) return;

        // Simple timeline visualization using CSS
        const { key_dates } = this.timelineData;
        const dates = [
            { label: 'Discovery', date: key_dates.discovery_date, color: 'bg-blue-500' },
            { label: 'Dispute', date: key_dates.dispute_date, color: 'bg-yellow-500' },
            { label: 'Filing', date: key_dates.filing_date, color: 'bg-green-500' }
        ].filter(d => d.date);

        if (dates.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center">No key dates available for timeline visualization</p>';
            return;
        }

        // Sort dates chronologically
        dates.sort((a, b) => new Date(a.date) - new Date(b.date));

        container.innerHTML = `
            <div class="space-y-4">
                <div class="flex items-center justify-center">
                    <div class="flex items-center space-x-8">
                        ${dates.map((date, index) => `
                            <div class="flex flex-col items-center">
                                <div class="w-4 h-4 ${date.color} rounded-full"></div>
                                <div class="text-xs font-medium text-gray-700 mt-2">${date.label}</div>
                                <div class="text-xs text-gray-500">${this.formatDate(date.date)}</div>
                            </div>
                            ${index < dates.length - 1 ? '<div class="flex-1 h-0.5 bg-gray-300"></div>' : ''}
                        `).join('')}
                    </div>
                </div>
                <div class="text-center text-sm text-gray-600">
                    Timeline spans ${this.calculateTimeSpan(dates)}
                </div>
            </div>
        `;
    }

    renderValidationIssues() {
        const container = document.getElementById('timeline-errors');
        if (!container) return;

        const { validation_details, recommendations } = this.timelineData;
        const errors = validation_details.errors || [];
        const warnings = validation_details.warnings || [];

        if (errors.length === 0 && warnings.length === 0) {
            container.innerHTML = '<div class="text-green-600 bg-green-50 p-4 rounded-lg">✓ No chronological validation issues found</div>';
            return;
        }

        let html = '';

        if (errors.length > 0) {
            html += `
                <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h4 class="font-medium text-red-800 mb-2">Critical Errors (${errors.length})</h4>
                    <ul class="space-y-1">
                        ${errors.map(error => `<li class="text-sm text-red-700">• ${error}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (warnings.length > 0) {
            html += `
                <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h4 class="font-medium text-yellow-800 mb-2">Warnings (${warnings.length})</h4>
                    <ul class="space-y-1">
                        ${warnings.map(warning => `<li class="text-sm text-yellow-700">• ${warning}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (recommendations.length > 0) {
            html += `
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 class="font-medium text-blue-800 mb-2">Recommendations</h4>
                    <ul class="space-y-1">
                        ${recommendations.map(rec => `<li class="text-sm text-blue-700">• ${rec}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        container.innerHTML = html;
    }

    renderDocumentDatesTable() {
        const tbody = document.getElementById('document-dates-table');
        if (!tbody) return;

        const documentDates = this.timelineData.document_dates || [];
        
        if (documentDates.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-4 py-8 text-center text-gray-500">
                        No document dates extracted from case documents.
                    </td>
                </tr>
            `;
            return;
        }

        // Sort dates chronologically
        const sortedDates = documentDates.sort((a, b) => {
            const dateA = new Date(a.parsed_date || a.date);
            const dateB = new Date(b.parsed_date || b.date);
            return dateA - dateB;
        });

        tbody.innerHTML = sortedDates.map((dateInfo, index) => {
            const date = dateInfo.parsed_date || dateInfo.date || 'N/A';
            const sourcePath = dateInfo.source_document || dateInfo.source || 'Unknown';
            const source = sourcePath === 'Unknown' ? 'Unknown' : sourcePath.split('/').pop(); // Extract filename only
            const context = dateInfo.context || dateInfo.type || 'General';
            const sourceLine = dateInfo.source_line || dateInfo.raw_text || 'N/A';
            const confidence = dateInfo.confidence ? `${Math.round(dateInfo.confidence * 100)}%` : 'N/A';
            
            return `
                <tr class="${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}">
                    <td class="px-4 py-3 text-sm text-gray-600 font-medium">${index + 1}</td>
                    <td class="px-4 py-3 text-sm text-gray-900">${this.formatDate(date)}</td>
                    <td class="px-4 py-3 text-sm text-gray-600">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            ${context}
                        </span>
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-600">${source}</td>
                    <td class="px-4 py-3 text-sm text-gray-600">${confidence}</td>
                    <td class="px-4 py-3 text-sm text-gray-500 max-w-md" title="${sourceLine}">
                        <div class="line-clamp-2 leading-relaxed">
                            ${sourceLine}
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    renderTimelineUnavailable() {
        const container = document.getElementById('tab-content-timeline');
        if (!container) return;

        container.innerHTML = `
            <div class="bg-white p-8 rounded-lg shadow-sm text-center">
                <div class="text-gray-400 text-6xl mb-4">⏰</div>
                <h2 class="text-xl font-semibold text-gray-700 mb-2">Timeline Validation Unavailable</h2>
                <p class="text-gray-600 mb-4">${this.timelineData.message}</p>
                <button onclick="window.location.reload()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    Refresh Page
                </button>
            </div>
        `;
    }

    renderTimelineError() {
        const container = document.getElementById('tab-content-timeline');
        if (!container) return;

        container.innerHTML = `
            <div class="bg-white p-8 rounded-lg shadow-sm text-center">
                <div class="text-red-400 text-6xl mb-4">⚠️</div>
                <h2 class="text-xl font-semibold text-gray-700 mb-2">Timeline Validation Error</h2>
                <p class="text-gray-600 mb-4">Unable to load timeline validation data. Please try again.</p>
                <button onclick="window.location.reload()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    Retry
                </button>
            </div>
        `;
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
        } catch {
            return dateString; // Return original if parsing fails
        }
    }

    calculateTimeSpan(dates) {
        if (dates.length < 2) return 'Single date';
        
        const earliest = new Date(Math.min(...dates.map(d => new Date(d.date))));
        const latest = new Date(Math.max(...dates.map(d => new Date(d.date))));
        const diffDays = Math.ceil((latest - earliest) / (1000 * 60 * 60 * 24));
        
        if (diffDays < 30) return `${diffDays} days`;
        if (diffDays < 365) return `${Math.ceil(diffDays / 30)} months`;
        return `${Math.ceil(diffDays / 365)} years`;
    }
}

// Global instance
window.timelineValidationUI = new TimelineValidationUI();