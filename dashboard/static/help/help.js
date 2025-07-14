// Attorney Notes Template Help Page JavaScript

// Template structure with examples for proper completion
const TEMPLATE_STRUCTURE = `NAME: [Plaintiff Full Legal Name]
Example: Eman Youssef

ADDRESS: [Full Address]
Example: 22-15 22nd Street
East Elmhurst, NY 11370

PHONE: [Phone Number]
Example: (555) 123-4567

CASE_NUMBER: [Court Case Number]
Example: 1:25-cv-01987

COURT_NAME: [Full Court Name]
Example: UNITED STATES DISTRICT COURT

COURT_DISTRICT: [Court District]
Example: EASTERN DISTRICT OF NEW YORK

FILING_DATE: [Date]
Example: April 9, 2025

PLAINTIFF_COUNSEL_NAME: [Attorney Name or TBD]
Example: John Smith, Esq.

DEFENDANTS: [List all defendants with full legal information]
Example:
- EQUIFAX INFORMATION SERVICES, LLC (Georgia corporation, authorized to do business in New York)
- EXPERIAN INFORMATION SOLUTIONS, INC. (Ohio corporation, authorized to do business in New York)
- TRANS UNION, LLC (Delaware corporation, authorized to do business in New York)
- TD BANK, N.A. (Delaware corporation, authorized to do business in New York)

BACKGROUND: [Numbered factual allegations starting with 1.]
Example:
1. Plaintiff [Name] is an individual consumer under the FCRA and NY FCRA, residing in [Location].
2. Plaintiff opened a [Bank] credit card account on or around [Date] with a $[Amount] credit limit.
3. [Continue with factual narrative of the case...]

DAMAGES: [Use the four standard categories below with specific examples]

Financial Harm:
- Being denied credit: [Specific denials with details]
- Having current credit limits reduced: [Specific reductions with amounts and dates]
- Limiting opportunities for credit: [Specific impacts on creditworthiness]
- [Add other financial impacts as applicable]

Reputational Harm:
- Damage to reputation: [How the errors affected plaintiff's standing]
- Adverse impact on credit rating: [Specific credit score impacts]
- Being labeled as credit risk: [Specific reputational damages]
- [Add other reputational impacts as applicable]

Emotional Harm:
- Emotional distress: [Specific stress and anxiety caused]
- Frustration: [Specific instances of frustration from dealing with errors]
- Humiliation: [Specific embarrassing situations caused by credit errors]
- Anxiety: [Specific anxiety about financial future]
- [Add other emotional impacts as applicable]

Personal Costs:
- Time spent resolving issues: [Specific hours/days spent on phone calls, letters, etc.]
- Resources expended: [Costs for documentation, travel, etc.]
- Lost opportunities: [Specific missed opportunities due to credit issues]
- Administrative burden: [Ongoing effort to monitor and correct reports]
- [Add other personal costs as applicable]

IMPORTANT NOTES:
- Use the exact four category names: Financial Harm, Reputational Harm, Emotional Harm, Personal Costs
- Each damage item should start with a dash (-)
- Be specific with dates, amounts, and creditor names when available
- Include evidence indicators like "Have denial letter" or "Documentation available"
- The more specific and detailed, the better the system can process the information
`;

// Auto-resize textarea to fit content
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    const scrollHeight = textarea.scrollHeight;
    const minHeight = 600; // Minimum height in pixels
    textarea.style.height = Math.max(scrollHeight + 20, minHeight) + 'px';
}

// Initialize template content
function loadTemplate() {
    const textarea = document.getElementById('template-textarea');
    textarea.value = TEMPLATE_STRUCTURE;
    autoResizeTextarea(textarea);
}

// Copy template to clipboard
function copyToClipboard() {
    const textarea = document.getElementById('template-textarea');
    textarea.select();
    document.execCommand('copy');
    
    // Show feedback
    const button = document.getElementById('copy-template-btn');
    const originalText = button.innerHTML;
    button.innerHTML = `<svg class="h-4 w-4 inline-block mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
    </svg>Copied!`;
    button.classList.remove('bg-blue-600', 'hover:bg-blue-700');
    button.classList.add('bg-green-600', 'hover:bg-green-700');
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.classList.remove('bg-green-600', 'hover:bg-green-700');
        button.classList.add('bg-blue-600', 'hover:bg-blue-700');
    }, 2000);
}

// Download as text file
function downloadTxt() {
    const textarea = document.getElementById('template-textarea');
    const blob = new Blob([textarea.value], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'Atty_Notes_Template.txt';
    link.click();
    URL.revokeObjectURL(link.href);
}

// Download as Word document (DOCX)
async function downloadDocx() {
    try {
        const button = document.getElementById('download-docx-btn');
        const originalText = button.innerHTML;
        button.innerHTML = `<svg class="h-4 w-4 inline-block mr-2 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
        </svg>Generating...`;
        button.disabled = true;
        
        // Call backend API to generate DOCX
        const response = await fetch('/api/attorney_template/docx', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: document.getElementById('template-textarea').value
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Download the generated DOCX file
        const blob = await response.blob();
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'Atty_Notes_Template.docx';
        link.click();
        URL.revokeObjectURL(link.href);
        
        // Success feedback
        button.innerHTML = `<svg class="h-4 w-4 inline-block mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>Downloaded!`;
        button.classList.remove('bg-purple-600', 'hover:bg-purple-700');
        button.classList.add('bg-green-600', 'hover:bg-green-700');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('bg-green-600', 'hover:bg-green-700');
            button.classList.add('bg-purple-600', 'hover:bg-purple-700');
            button.disabled = false;
        }, 2000);
        
    } catch (error) {
        console.error('Error generating DOCX:', error);
        
        // Error feedback
        const button = document.getElementById('download-docx-btn');
        button.innerHTML = `<svg class="h-4 w-4 inline-block mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
        </svg>Error`;
        button.classList.remove('bg-purple-600', 'hover:bg-purple-700');
        button.classList.add('bg-red-600', 'hover:bg-red-700');
        
        setTimeout(() => {
            button.innerHTML = `<svg class="h-4 w-4 inline-block mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-4.5a1.125 1.125 0 0 1-1.125-1.125v-1.5A3.375 3.375 0 0 0 7.125 2.25H4.875C3.839 2.25 3 3.089 3 4.125v15.75c0 1.036.839 1.875 1.875 1.875h11.25c1.036 0 1.875-.839 1.875-1.875v-8.688a3.375 3.375 0 0 0-.621-1.943l-2.343-3.129a1.406 1.406 0 0 0-1.134-.564H12a.75.75 0 0 1 0-1.5h1.875A2.906 2.906 0 0 1 16.19 5.47l2.343 3.129A4.875 4.875 0 0 1 19.5 11.25Z" />
            </svg>Download .docx`;
            button.classList.remove('bg-red-600', 'hover:bg-red-700');
            button.classList.add('bg-purple-600', 'hover:bg-purple-700');
            button.disabled = false;
        }, 3000);
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    loadTemplate();
    
    // Add event listeners
    document.getElementById('copy-template-btn').addEventListener('click', copyToClipboard);
    document.getElementById('download-txt-btn').addEventListener('click', downloadTxt);
    document.getElementById('download-docx-btn').addEventListener('click', downloadDocx);
    
    // Auto-resize textarea when window resizes
    window.addEventListener('resize', () => {
        const textarea = document.getElementById('template-textarea');
        autoResizeTextarea(textarea);
    });
});