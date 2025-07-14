# Quick Edit Plan - Complaint In-Place Editing MVP

## Overview
Implement simple in-place editing for complaint documents to allow lawyers to make final edits before printing. No complex formatting tools - just edit text, save, and print. Focus on speed and market readiness.

## Core Requirements
- ✅ **Edit in place** - Transform complaint preview into editable text
- ✅ **Save changes** - Update the HTML file with edits
- ✅ **Delta tracking** - Save changes to `atty_notes_edits.txt` in case folder
- ✅ **Print ready** - Maintain legal document formatting after edits
- ✅ **Simple UX** - Edit → Save → Print workflow

## Implementation Plan

### Phase 1: Basic Editing Infrastructure (Day 1)

#### Backend API Endpoints
- [ ] **Create `POST /api/cases/{case_id}/save-complaint-edits`**
  - Accept: `{ "html_content": "<html>...", "text_changes": "summary of changes" }`
  - Save: Updated HTML to existing complaint file
  - Create: `atty_notes_edits.txt` with change summary and timestamp
  - Return: Success response with file paths

- [ ] **Create `GET /api/cases/{case_id}/complaint-content`**
  - Return: Raw HTML content of current complaint file
  - Include: Last modified timestamp and file size
  - Handle: File not found errors gracefully

#### File Management
- [ ] **Backup system** - Copy original before edits to `complaint_original.html`
- [ ] **Delta file creation** - `atty_notes_edits.txt` with format:
  ```
  COMPLAINT EDITS - [timestamp]
  ================
  Original file: complaint.html
  Backup created: complaint_original.html
  
  Changes made:
  [user's change summary or auto-detected changes]
  
  Last edited: [timestamp]
  User: [current user]
  ```

### Phase 2: Frontend Edit Mode (Day 1-2)

#### Edit Mode Toggle
- [ ] **Add "Edit Complaint" button** to complaint tab header
- [ ] **Transform preview** - Replace static HTML with `contentEditable` div
- [ ] **Visual indicators** - Light blue border, "EDITING MODE" label
- [ ] **Preserve styling** - Maintain legal document formatting during edit

#### Save/Cancel Controls
- [ ] **Save button** with loading state ("Saving..." animation)
- [ ] **Cancel button** to revert changes (reload original content)
- [ ] **Auto-detect changes** - Enable save button only when content modified
- [ ] **Confirmation dialog** - "Are you sure?" for cancel if unsaved changes

#### Content Management
- [ ] **Load original content** via API when entering edit mode
- [ ] **Track changes** - Compare original vs current content
- [ ] **Preserve HTML structure** - Maintain legal document tags and styling
- [ ] **Character limit warnings** - Alert if content becomes too long

### Phase 3: Save and Print Integration (Day 2)

#### Save Functionality
- [ ] **Save API call** with error handling and retry logic
- [ ] **Success feedback** - "Saved successfully" toast notification
- [ ] **Error handling** - Clear error messages for save failures
- [ ] **Change summary** - Auto-generate or prompt user for edit description

#### Print Integration
- [ ] **"Save & Print" button** - Combined action for workflow efficiency
- [ ] **Print preview** - Show updated document after save
- [ ] **Print optimization** - Ensure edited content prints correctly
- [ ] **Exit edit mode** - Return to normal preview after successful save

### Phase 4: Data Persistence and Recovery (Day 2-3)

#### Delta Tracking
- [ ] **Change detection** - Compare original vs edited HTML content
- [ ] **Text extraction** - Pull changed text portions for delta file
- [ ] **Timestamp tracking** - Record when edits were made
- [ ] **User attribution** - Track which user made changes

#### Recovery Mechanisms
- [ ] **Draft auto-save** - Store edits in localStorage every 30 seconds
- [ ] **Restore drafts** - Offer to restore unsaved changes on page reload
- [ ] **Original backup** - Always preserve original file as fallback
- [ ] **Edit history** - Show "Last edited" timestamp in complaint tab

## Technical Implementation

### API Endpoints
```
POST /api/cases/{case_id}/save-complaint-edits
Body: {
  "html_content": "<html>...</html>",
  "change_summary": "Updated plaintiff address and added defendant",
  "user_id": "current_user"
}
Response: {
  "success": true,
  "files_updated": ["complaint.html", "atty_notes_edits.txt"],
  "backup_created": "complaint_original.html",
  "timestamp": "2025-07-11T09:00:00Z"
}

GET /api/cases/{case_id}/complaint-content
Response: {
  "html_content": "<html>...</html>",
  "last_modified": "2025-07-11T08:30:00Z",
  "file_size": 15234,
  "has_edits": false
}
```

### Frontend JavaScript
```javascript
// Edit mode state
let editState = {
  isEditing: false,
  originalContent: null,
  hasChanges: false,
  autoSaveTimer: null
};

// Main functions
function enterEditMode() { /* Transform preview to editable */ }
function saveEdits() { /* Call save API and update UI */ }
function cancelEdits() { /* Revert to original content */ }
function autoSave() { /* Save draft to localStorage */ }
```

### File Structure
```
outputs/tests/youssef/
├── complaint.html              # Current complaint (may be edited)
├── complaint_original.html     # Backup of original (created on first edit)
├── atty_notes_edits.txt       # Delta file with change tracking
└── summons/                   # Existing summons files
```

## Success Criteria
- [ ] Lawyer can click "Edit Complaint" and modify text content
- [ ] Save button updates the HTML file with changes
- [ ] `atty_notes_edits.txt` created with change summary
- [ ] Print output maintains legal formatting after edits
- [ ] Edit mode integrates seamlessly with existing review page
- [ ] No data loss - original always backed up
- [ ] Fast workflow: Edit → Save → Print (under 30 seconds)

## User Workflow
1. **Review complaint** in normal preview mode
2. **Click "Edit Complaint"** - enters edit mode with blue border
3. **Make text changes** - edit directly in the document
4. **Click "Save"** - updates files and shows success message
5. **Click "Print"** - prints the updated complaint
6. **Continue workflow** - return to normal mode for next steps

## Integration Points

### Existing Systems
- **Review page** - Add edit functionality to complaint tab
- **File system** - Save edits to existing output directory structure
- **Settings** - Use current user info for edit attribution
- **Print system** - Ensure edited content prints correctly

### Next Phase (iCloud Sync)
- **File monitoring** - iCloud sync will detect and upload edited files
- **Delta sync** - Include `atty_notes_edits.txt` in sync operations
- **Conflict resolution** - Handle edits made on multiple devices

## Timeline
- **Day 1**: Backend API endpoints and basic edit mode toggle
- **Day 2**: Save/cancel functionality and change tracking
- **Day 3**: Polish, testing, and integration with print workflow

## Risk Mitigation
- [ ] Always backup original before any edits
- [ ] Validate HTML structure before saving
- [ ] Test print output after various edit scenarios
- [ ] Handle network failures with local draft storage
- [ ] Provide clear feedback for all user actions

---

**Priority**: Market-ready MVP with simple edit capability
**Dependencies**: Existing review page infrastructure
**Success Metric**: Lawyers can edit and print in under 30 seconds