// dashboard/static/js/damages-review.js
// Phase 2: Interactive Damage Selection Module

class DamageReview {
    constructor(damages) {
        this.damages = damages || {};
        this.selections = {};
        this.initialized = false;
        
        // Category display names and icons - updated to match Tiger output
        this.categoryConfig = {
            // New Tiger schema categories
            'financial_harm': {
                name: 'Financial Harm',
                icon: '💳',
                description: 'Financial losses and credit denials due to inaccurate reports'
            },
            'reputational_harm': {
                name: 'Reputational Harm', 
                icon: '📊',
                description: 'Damage to credit reputation and standing'
            },
            'emotional_harm': {
                name: 'Emotional Harm',
                icon: '😓',
                description: 'Emotional distress and psychological impact'
            },
            'personal_costs': {
                name: 'Personal Costs',
                icon: '⏰',
                description: 'Time, effort, and resources spent resolving issues'
            },
            // Legacy categories for backward compatibility
            'credit_denials': {
                name: 'Credit Application Denials',
                icon: '💳',
                description: 'Denied credit applications due to inaccurate credit reports'
            },
            'existing_credit_impacts': {
                name: 'Existing Credit Impacts',
                icon: '📊',
                description: 'Changes to existing credit accounts due to reporting errors'
            },
            'employment_issues': {
                name: 'Employment Issues',
                icon: '💼',
                description: 'Employment-related problems caused by credit report errors'
            },
            'housing_issues': {
                name: 'Housing Issues',
                icon: '🏠',
                description: 'Housing or rental problems due to credit report inaccuracies'
            },
            'emotional_distress': {
                name: 'Emotional Distress',
                icon: '😓',
                description: 'Psychological impact and stress from credit report errors'
            },
            'time_and_resources': {
                name: 'Time and Resources',
                icon: '⏰',
                description: 'Time, effort, and costs spent addressing credit report issues'
            }
        };
    }

    initialize() {
        if (this.initialized) return;
        
        console.log('Initializing damage review with data:', this.damages);
        this.renderDamageSection();
        this.setupEventListeners();
        this.initialized = true;
        
        // Auto-select and auto-save high-evidence damages after rendering
        setTimeout(() => this.autoSelectAndSaveDamages(), 1000);
    }

    renderDamageSection() {
        const container = document.getElementById('damages-section');
        if (!container) {
            console.error('Damages section container not found');
            return;
        }

        // Check if we have structured damages
        const structuredDamages = this.damages.structured_damages || [];
        const categorizedDamages = this.damages.categorized_damages || {};
        
        // Check if we have any damage information at all
        const hasActualDamages = this.damages.actual_damages && Object.keys(this.damages.actual_damages).length > 0;
        const hasStatutoryDamages = this.damages.statutory_damages && Object.keys(this.damages.statutory_damages).length > 0;
        const hasPunitiveDamages = this.damages.punitive_damages && Object.keys(this.damages.punitive_damages).length > 0;
        const hasGeneralDamages = this.damages.damages && Array.isArray(this.damages.damages) && this.damages.damages.length > 0;
        
        // If we have no structured damages but have other damage types, show general damages
        if (structuredDamages.length === 0) {
            if (hasActualDamages || hasStatutoryDamages || hasPunitiveDamages || hasGeneralDamages) {
                container.innerHTML = this.renderGeneralDamagesSection();
                return;
            } else {
                container.innerHTML = this.renderNoDamagesMessage();
                return;
            }
        }

        // Generate statistics
        const stats = this.generateStatistics(structuredDamages);
        
        let html = `
            <div class="bg-white p-6 rounded-lg shadow-sm mb-8">
                <div class="flex items-center justify-between mb-6">
                    <h3 class="text-lg font-semibold text-gray-900">💰 Damages Assessment</h3>
                    <div class="text-sm text-gray-600">
                        ${stats.total} damages identified • ${stats.withEvidence} with evidence
                    </div>
                </div>
                
                <div class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div class="flex items-start space-x-3">
                        <div class="text-blue-600 mt-1">ℹ️</div>
                        <div class="text-sm text-blue-800">
                            <p class="font-medium mb-1">Review and Select Damages</p>
                            <p>Select the damages that apply to your case. Items with evidence (✅) are stronger claims. You can expand each category to see individual damages.</p>
                        </div>
                    </div>
                </div>
        `;

        // Render categories
        console.log('🔍 Debug: categoryConfig keys:', Object.keys(this.categoryConfig));
        console.log('🔍 Debug: categorizedDamages keys:', Object.keys(categorizedDamages));
        
        Object.entries(this.categoryConfig).forEach(([categoryKey, categoryInfo]) => {
            const categoryDamages = categorizedDamages[categoryKey] || [];
            console.log(`🔍 Debug: ${categoryKey} has ${categoryDamages.length} damages`);
            if (categoryDamages.length > 0) {
                console.log(`✅ Rendering category: ${categoryKey}`);
                html += this.renderCategorySection(categoryKey, categoryInfo, categoryDamages);
            } else {
                console.log(`❌ Skipping empty category: ${categoryKey}`);
            }
        });

        // Action buttons
        html += this.renderActionButtons(stats);
        html += '</div>';

        container.innerHTML = html;
    }

    renderCategorySection(categoryKey, categoryInfo, damages) {
        const selectedCount = damages.filter(d => d.selected).length;
        const evidenceCount = damages.filter(d => d.evidence_available).length;
        const isExpanded = damages.some(d => d.selected); // Auto-expand if any selected

        return `
            <div class="damage-category mb-4 border border-gray-200 rounded-lg" data-category="${categoryKey}">
                <div class="category-header p-4 cursor-pointer hover:bg-gray-50" onclick="toggleCategory('${categoryKey}')">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                            <span class="text-xl">${categoryInfo.icon}</span>
                            <div>
                                <h4 class="font-medium text-gray-900">${categoryInfo.name}</h4>
                                <p class="text-sm text-gray-600">${categoryInfo.description}</p>
                            </div>
                        </div>
                        <div class="flex items-center space-x-4">
                            <div class="text-sm text-gray-500">
                                ${damages.length} item${damages.length !== 1 ? 's' : ''}
                                ${evidenceCount > 0 ? `• ${evidenceCount} with evidence` : ''}
                                ${selectedCount > 0 ? `• ${selectedCount} selected` : ''}
                            </div>
                            <div class="flex items-center space-x-2">
                                <button type="button" class="text-xs px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200" onclick="selectAllInCategory('${categoryKey}', event)">
                                    Select All
                                </button>
                                <button type="button" class="text-xs px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200" onclick="clearAllInCategory('${categoryKey}', event)">
                                    Clear All
                                </button>
                                <span class="expand-icon text-gray-400 transform transition-transform ${isExpanded ? 'rotate-180' : ''}" id="expand-${categoryKey}">
                                    ▼
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="category-content ${isExpanded ? '' : 'hidden'}" id="content-${categoryKey}">
                    <div class="px-4 pb-4 space-y-3">
                        ${damages.map((damage, index) => this.renderDamageItem(damage, categoryKey, index)).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderDamageItem(damage, categoryKey, index) {
        const damageId = `damage-${categoryKey}-${index}`;
        const evidenceIcon = damage.evidence_available ? 
            '<span class="text-green-600 text-sm" title="Evidence available">✅</span>' : 
            '<span class="text-yellow-600 text-sm" title="Evidence needed">⚠️</span>';
        
        return `
            <div class="damage-item p-3 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
                <div class="flex items-start space-x-3">
                    <input type="checkbox" 
                           id="${damageId}" 
                           name="damage_selection" 
                           value="${categoryKey}-${index}"
                           data-category="${categoryKey}"
                           data-index="${index}"
                           class="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" 
                           ${damage.selected ? 'checked' : ''}
                           onchange="updateDamageSelection('${categoryKey}', ${index}, this.checked)">
                    
                    <div class="flex-1">
                        <label for="${damageId}" class="cursor-pointer">
                            <div class="flex items-center justify-between">
                                <div class="flex-1">
                                    <div class="text-sm font-medium text-gray-900 mb-1">
                                        ${damage.description}
                                    </div>
                                    ${damage.entity && damage.entity !== 'N/A' ? `
                                        <div class="text-xs text-gray-600">
                                            <span class="font-medium">Entity:</span> ${damage.entity}
                                            ${damage.date && damage.date !== 'N/A' ? `• <span class="font-medium">Date:</span> ${damage.date}` : ''}
                                        </div>
                                    ` : ''}
                                </div>
                                <div class="ml-3 flex items-center space-x-2">
                                    ${evidenceIcon}
                                    <span class="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
                                        ${damage.type.replace(/_/g, ' ')}
                                    </span>
                                </div>
                            </div>
                        </label>
                    </div>
                </div>
            </div>
        `;
    }

    renderGeneralDamagesSection() {
        const hasActualDamages = this.damages.actual_damages && Object.keys(this.damages.actual_damages).length > 0;
        const hasStatutoryDamages = this.damages.statutory_damages && Object.keys(this.damages.statutory_damages).length > 0;
        const hasPunitiveDamages = this.damages.punitive_damages && Object.keys(this.damages.punitive_damages).length > 0;
        const hasGeneralDamages = this.damages.damages && Array.isArray(this.damages.damages) && this.damages.damages.length > 0;
        
        let html = `
            <div class="bg-white p-6 rounded-lg shadow-sm mb-8">
                <div class="flex items-center justify-between mb-6">
                    <h3 class="text-lg font-semibold text-gray-900">💰 Damages Information</h3>
                    <div class="text-sm text-gray-600">
                        Legal damages extracted from case documents
                    </div>
                </div>
                
                <div class="space-y-6">
        `;

        // Display actual damages
        if (hasActualDamages) {
            html += `
                <div class="border border-gray-200 rounded-lg p-4">
                    <h4 class="font-medium text-gray-900 mb-3 flex items-center">
                        <span class="text-green-600 mr-2">💵</span>
                        Actual Damages
                    </h4>
                    <div class="text-sm text-gray-700 space-y-2">
            `;
            
            Object.entries(this.damages.actual_damages).forEach(([key, value]) => {
                if (value && key !== 'amount') {
                    const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    
                    if (key === 'specific_denials' && Array.isArray(value)) {
                        // Special handling for specific denials array
                        html += `<div><strong>${label}:</strong></div>`;
                        html += `<div class="ml-4 space-y-3 mt-2">`;
                        value.forEach((denial, index) => {
                            html += `
                                <div class="border-l-4 border-red-300 pl-4 py-2 bg-red-50">
                                    <div class="text-sm">
                                        <strong>Denial ${index + 1}:</strong> ${denial.creditor || 'Unknown Creditor'}
                                        ${denial.date ? ` (${denial.date})` : ''}
                                        ${denial.credit_score ? ` - Credit Score: ${denial.credit_score}` : ''}
                                    </div>
                                    ${denial.reasons && denial.reasons.length > 0 ? `
                                        <div class="mt-1 text-xs text-gray-600">
                                            <strong>Reasons:</strong> ${denial.reasons.join('; ')}
                                        </div>
                                    ` : ''}
                                    ${denial.source_document ? `
                                        <div class="mt-1 text-xs text-gray-500">
                                            Source: ${denial.source_document}
                                        </div>
                                    ` : ''}
                                </div>
                            `;
                        });
                        html += `</div>`;
                    } else if (key === 'categories' && Array.isArray(value)) {
                        // Special handling for categories array
                        html += `<div><strong>${label}:</strong></div>`;
                        html += `<div class="ml-4 mt-2">`;
                        html += `<ul class="list-disc list-inside space-y-1 text-sm">`;
                        value.forEach(category => {
                            html += `<li>${category}</li>`;
                        });
                        html += `</ul></div>`;
                    } else if (Array.isArray(value)) {
                        // General array handling
                        html += `<div><strong>${label}:</strong> ${value.join(', ')}</div>`;
                    } else if (typeof value === 'object') {
                        // General object handling
                        html += `<div><strong>${label}:</strong> ${JSON.stringify(value, null, 2).replace(/[{}\"]/g, '').replace(/,/g, '<br>')}</div>`;
                    } else {
                        // Simple value
                        html += `<div><strong>${label}:</strong> ${value}</div>`;
                    }
                }
            });
            
            html += `</div></div>`;
        }

        // Display statutory damages
        if (hasStatutoryDamages) {
            html += `
                <div class="border border-gray-200 rounded-lg p-4">
                    <h4 class="font-medium text-gray-900 mb-3 flex items-center">
                        <span class="text-blue-600 mr-2">⚖️</span>
                        Statutory Damages
                    </h4>
                    <div class="text-sm text-gray-700 space-y-2">
            `;
            
            Object.entries(this.damages.statutory_damages).forEach(([key, value]) => {
                if (value) {
                    html += `<div><strong>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> ${value}</div>`;
                }
            });
            
            html += `</div></div>`;
        }

        // Display punitive damages
        if (hasPunitiveDamages) {
            html += `
                <div class="border border-gray-200 rounded-lg p-4">
                    <h4 class="font-medium text-gray-900 mb-3 flex items-center">
                        <span class="text-red-600 mr-2">⚡</span>
                        Punitive Damages
                    </h4>
                    <div class="text-sm text-gray-700 space-y-2">
            `;
            
            Object.entries(this.damages.punitive_damages).forEach(([key, value]) => {
                if (value) {
                    html += `<div><strong>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> ${value}</div>`;
                }
            });
            
            html += `</div></div>`;
        }

        // Display general damages list
        if (hasGeneralDamages) {
            html += `
                <div class="border border-gray-200 rounded-lg p-4">
                    <h4 class="font-medium text-gray-900 mb-3 flex items-center">
                        <span class="text-purple-600 mr-2">📋</span>
                        General Damages
                    </h4>
                    <div class="text-sm text-gray-700">
                        <ul class="list-disc list-inside space-y-1">
            `;
            
            this.damages.damages.forEach(damage => {
                html += `<li>${damage}</li>`;
            });
            
            html += `
                        </ul>
                    </div>
                </div>
            `;
        }

        html += `
                </div>
                
                <div class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div class="flex items-start space-x-3">
                        <div class="text-blue-600 mt-1">ℹ️</div>
                        <div class="text-sm text-blue-800">
                            <p class="font-medium mb-1">Damages Information Available</p>
                            <p>The system has extracted general damages information from your case documents. For more detailed damage selection and categorization, add a structured DAMAGES section to your attorney notes.</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        return html;
    }

    renderNoDamagesMessage() {
        return `
            <div class="bg-white p-6 rounded-lg shadow-sm mb-8">
                <div class="text-center py-8">
                    <div class="text-gray-400 text-4xl mb-4">💰</div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">No Structured Damages Found</h3>
                    <p class="text-gray-600 mb-4">No DAMAGES section was found in the attorney notes. To use this feature:</p>
                    <div class="text-sm text-gray-600 text-left max-w-md mx-auto">
                        <p class="mb-2">1. Add a DAMAGES section to your attorney notes</p>
                        <p class="mb-2">2. List damages in the format: "- Denied Auto Loan: Wells Fargo, April 20, 2025. Have denial letter."</p>
                        <p class="mb-2">3. Process the case again to extract structured damages</p>
                    </div>
                </div>
            </div>
        `;
    }

    renderActionButtons(stats) {
        return `
            <div class="mt-8 p-4 bg-gray-50 border border-gray-200 rounded-lg relative z-10 clear-both">
                <div class="flex items-center justify-between">
                    <div class="text-sm text-gray-600">
                        <p class="mb-1">💡 <strong>Tip:</strong> Select damages that are well-documented and relevant to your case</p>
                        <p>Evidence indicators: ✅ = Have documentation, ⚠️ = Need to collect evidence</p>
                    </div>
                    <div class="action-buttons">
                        <button type="button" id="select-all-damages" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
                            Select All Damages
                        </button>
                        <button type="button" id="clear-all-damages" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm">
                            Clear All Damages
                        </button>
                        <button type="button" id="save-damage-selections" class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                            Save Damage Selections
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        // Global action buttons
        const selectAllBtn = document.getElementById('select-all-damages');
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => this.selectAllDamages());
        }

        const clearAllBtn = document.getElementById('clear-all-damages');
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', () => this.clearAllDamages());
        }

        const saveBtn = document.getElementById('save-damage-selections');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveDamageSelections());
        }
    }

    selectAllDamages() {
        document.querySelectorAll('input[name="damage_selection"]').forEach(checkbox => {
            checkbox.checked = true;
            const category = checkbox.getAttribute('data-category');
            const index = parseInt(checkbox.getAttribute('data-index'));
            this.updateDamageSelection(category, index, true);
        });
    }

    clearAllDamages() {
        document.querySelectorAll('input[name="damage_selection"]').forEach(checkbox => {
            checkbox.checked = false;
            const category = checkbox.getAttribute('data-category');
            const index = parseInt(checkbox.getAttribute('data-index'));
            this.updateDamageSelection(category, index, false);
        });
    }

    updateDamageSelection(category, index, selected) {
        // Update internal state
        if (!this.selections[category]) {
            this.selections[category] = {};
        }
        this.selections[category][index] = selected;
        
        // Update damage object if it exists
        if (this.damages.categorized_damages && this.damages.categorized_damages[category]) {
            const damage = this.damages.categorized_damages[category][index];
            if (damage) {
                damage.selected = selected;
            }
        }
        
        // Update structured damages array
        if (this.damages.structured_damages) {
            const structuredDamage = this.damages.structured_damages.find(d => 
                d.category === category && d.type === this.damages.categorized_damages[category][index]?.type
            );
            if (structuredDamage) {
                structuredDamage.selected = selected;
            }
        }
        
        console.log(`Damage selection updated: ${category}[${index}] = ${selected}`);
    }

    async saveDamageSelections() {
        const saveBtn = document.getElementById('save-damage-selections');
        const originalText = saveBtn.textContent;
        
        try {
            // Show saving state
            saveBtn.disabled = true;
            saveBtn.textContent = 'Saving...';
            
            // Collect all selections
            const selections = {};
            document.querySelectorAll('input[name="damage_selection"]').forEach(checkbox => {
                const category = checkbox.getAttribute('data-category');
                const index = parseInt(checkbox.getAttribute('data-index'));
                const selected = checkbox.checked;
                
                if (!selections[category]) {
                    selections[category] = {};
                }
                selections[category][index] = selected;
            });

            const caseId = getCaseId();
            const response = await fetch(`/api/cases/${caseId}/damages`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ selections: selections })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // Show success state
            saveBtn.textContent = '✅ Saved';
            saveBtn.className = saveBtn.className.replace('bg-blue-600 hover:bg-blue-700', 'bg-green-600');
            
            // Show success message
            this.showMessage('Success! Damage selections saved successfully.', 'success');
            
        } catch (error) {
            console.error('Failed to save damage selections:', error);
            
            // Show error state
            saveBtn.textContent = '❌ Error';
            saveBtn.className = saveBtn.className.replace('bg-blue-600 hover:bg-blue-700', 'bg-red-600');
            
            // Show error message
            this.showMessage(`Error: ${error.message}`, 'error');
        } finally {
            // Reset button after 2 seconds
            setTimeout(() => {
                saveBtn.disabled = false;
                saveBtn.textContent = originalText;
                saveBtn.className = saveBtn.className.replace('bg-green-600', 'bg-blue-600 hover:bg-blue-700');
                saveBtn.className = saveBtn.className.replace('bg-red-600', 'bg-blue-600 hover:bg-blue-700');
            }, 2000);
        }
    }

    showMessage(message, type) {
        const messageDiv = document.createElement('div');
        const bgColor = type === 'success' ? 'bg-green-100 border-green-400 text-green-700' : 'bg-red-100 border-red-400 text-red-700';
        messageDiv.className = `fixed top-4 right-4 ${bgColor} px-4 py-3 rounded border z-50`;
        messageDiv.innerHTML = `
            <div class="flex items-center">
                <strong class="font-bold">${type === 'success' ? 'Success!' : 'Error!'}</strong>
                <span class="block sm:inline ml-2">${message}</span>
            </div>
        `;
        document.body.appendChild(messageDiv);
        
        // Remove message after 3 seconds for success, 5 seconds for error
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, type === 'success' ? 3000 : 5000);
    }

    generateStatistics(damages) {
        return {
            total: damages.length,
            withEvidence: damages.filter(d => d.evidence_available).length,
            selected: damages.filter(d => d.selected).length
        };
    }

    async autoSelectAndSaveDamages() {
        console.log('🔄 DAMAGE AUTO-SAVE: Starting automatic selection of high-evidence damages');
        
        try {
            const structuredDamages = this.damages.structured_damages || [];
            if (structuredDamages.length === 0) {
                console.log('🔄 DAMAGE AUTO-SAVE: No structured damages found, skipping auto-selection');
                return;
            }
            
            let autoSelectedCount = 0;
            const damageSelections = [];
            
            // Auto-select damages with evidence available
            structuredDamages.forEach((damage, index) => {
                const shouldAutoSelect = damage.evidence_available === true && !damage.selected;
                
                if (shouldAutoSelect) {
                    // Find the checkbox and select it
                    const checkbox = document.querySelector(`input[data-category="${damage.category}"][data-index="${index}"]`);
                    if (checkbox) {
                        checkbox.checked = true;
                        damage.selected = true;
                        autoSelectedCount++;
                        
                        // Update the UI to show selection
                        updateDamageSelection(damage.category, index, true);
                    }
                }
                
                damageSelections.push({
                    category: damage.category,
                    index: index,
                    selected: damage.selected || shouldAutoSelect
                });
            });
            
            if (autoSelectedCount === 0) {
                console.log('🔄 DAMAGE AUTO-SAVE: No high-evidence damages to auto-select');
                return;
            }
            
            console.log(`🔄 DAMAGE AUTO-SAVE: Auto-selected ${autoSelectedCount} damages with evidence`);
            
            // Auto-save the selections
            const caseId = this.caseId || window.currentCaseId || 'youssef'; // Get from instance, global, or default
            const response = await fetch(`/api/cases/${caseId}/damages`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    selections: damageSelections,
                    auto_save: true 
                })
            });

            if (!response.ok) {
                console.warn(`🔄 DAMAGE AUTO-SAVE: Failed to auto-save damage selections: ${response.status}`);
                return;
            }

            console.log(`✅ DAMAGE AUTO-SAVE: Successfully auto-saved ${autoSelectedCount} damage selections`);
            
            // Show discrete notification
            this.showDiscreteNotification(`✅ ${autoSelectedCount} damages with evidence auto-selected and saved`);
            
        } catch (error) {
            console.error('🔄 DAMAGE AUTO-SAVE: Error during auto-save:', error);
            // Fail silently to not interrupt workflow
        }
    }

    showDiscreteNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'fixed bottom-4 left-4 bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded-lg z-50 text-sm shadow-lg';
        notification.innerHTML = `
            <div class="flex items-center">
                <span>${message}</span>
            </div>
        `;
        document.body.appendChild(notification);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.opacity = '0';
                notification.style.transition = 'opacity 0.3s ease';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, 4000);
    }
}

// Global functions for onclick handlers
function toggleCategory(categoryKey) {
    const content = document.getElementById(`content-${categoryKey}`);
    const icon = document.getElementById(`expand-${categoryKey}`);
    
    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        icon.classList.add('rotate-180');
    } else {
        content.classList.add('hidden');
        icon.classList.remove('rotate-180');
    }
}

function selectAllInCategory(categoryKey, event) {
    event.stopPropagation();
    document.querySelectorAll(`input[data-category="${categoryKey}"]`).forEach(checkbox => {
        checkbox.checked = true;
        const index = parseInt(checkbox.getAttribute('data-index'));
        updateDamageSelection(categoryKey, index, true);
    });
}

function clearAllInCategory(categoryKey, event) {
    event.stopPropagation();
    document.querySelectorAll(`input[data-category="${categoryKey}"]`).forEach(checkbox => {
        checkbox.checked = false;
        const index = parseInt(checkbox.getAttribute('data-index'));
        updateDamageSelection(categoryKey, index, false);
    });
}

function updateDamageSelection(category, index, selected) {
    // This will be called by the global DamageReview instance
    if (window.damageReview) {
        window.damageReview.updateDamageSelection(category, index, selected);
    }
}

// Helper function to get case ID (should be available globally)
function getCaseId() {
    const params = new URLSearchParams(window.location.search);
    return params.get('case_id');
}