# Simplified iCloud Sync Implementation Plan

## Overview
Create a bare-bones iCloud sync system that connects to iCloud Drive, reads case folders from a parent directory, and copies files to our local case structure for processing.

## Core Components

### 1. iCloud Connection Service
**File:** `dashboard/icloud_service.py`
- Install `pyicloud` dependency
- Basic iCloud authentication with app-specific password
- Simple folder navigation to parent directory
- File listing and download capabilities

### 2. Settings Integration
**Enhancement:** `dashboard/config/settings.json`
- Add iCloud credentials (encrypted storage)
- Add parent folder path setting
- Add sync toggle (enable/disable)

### 3. Simple Sync Operation
**File:** `dashboard/sync_manager.py`
- Connect to iCloud parent folder
- List all case subdirectories
- For each case folder: download all files to local structure
- Target: `/Users/corelogic/satori-dev/TM/test-data/sync-test-cases/{case_name}/`

### 4. Settings UI Enhancement
**Enhancement:** `dashboard/static/settings/`
- Add iCloud credentials form (email, app password, folder path)
- Add "Test Connection" button
- Add "Sync Now" button for manual sync

### 5. API Endpoints
**Enhancement:** `dashboard/main.py`
- `POST /api/icloud/test-connection` - Validate credentials
- `POST /api/icloud/sync` - Trigger manual sync
- `GET /api/icloud/status` - Connection and sync status

## Data Flow
```
iCloud Parent Folder/{case_name}/ → Download → TM/test-data/sync-test-cases/{case_name}/ → Existing File Processing
```

## Settings Schema
```json
{
  "icloud": {
    "email": "lawyer@lawfirm.com",
    "app_password": "[encrypted]",
    "parent_folder": "/Legal Cases",
    "enabled": true
  }
}
```

## Implementation Steps
1. Add `pyicloud` to requirements.txt
2. Create `icloud_service.py` with basic connection/download
3. Create `sync_manager.py` with case folder sync logic
4. Add iCloud settings to UI and API
5. Add manual sync button to dashboard
6. Test with real iCloud account

## Scope Limitations
- Manual sync only (no automatic scheduling)
- Download only (no upload back to iCloud)
- Simple folder mapping (1:1 case folder structure)
- Basic error handling
- No conflict resolution
- No file versioning

This creates a minimal viable sync system that gets case files from iCloud into our existing processing pipeline.