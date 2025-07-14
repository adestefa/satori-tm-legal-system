# TM Version Control System

## Overview

The Tiger-Monkey (TM) system uses a dual-tier version control strategy to ensure users always test the latest frontend code while maintaining stable backend service versions.

## Version Control Philosophy

### Frontend-Focused Version Updates
When users request to "tick the version," they are primarily concerned with **frontend cache-busting** to ensure they're testing the latest Dashboard interface code, not backend service changes.

**Primary Goal**: Prevent wasted time testing old cached JavaScript/CSS code in the browser.

### Two-Tier System

#### Tier 1: Frontend/Dashboard Versions (User-Facing)
- **Dashboard Version**: What users see in the UI
- **JavaScript Cache-Busting**: Version parameters on all JS/CSS imports
- **Login Page Version**: Displayed during authentication
- **Updated Frequently**: Every time user requests "tick the version"

#### Tier 2: Backend Service Versions (Development-Focused)
- **Tiger Service**: Only updated when Tiger code changes
- **Monkey Service**: Only updated when Monkey code changes  
- **Browser Service**: Only updated when Browser service changes
- **Updated Rarely**: Only when actual backend functionality changes

## Component Version Tracking

### Dashboard (Frontend Focus)
**Primary Version**: Displayed in UI sidebar and login page
- **Location**: `dashboard/main.py` → `APP_VERSION`
- **Display**: Dashboard sidebar, login page, API responses
- **Cache-Busting**: JavaScript/CSS import version parameters
- **Update Trigger**: Every user request to "tick the version"

**Files to Update**:
```
dashboard/main.py:145                     → APP_VERSION = "1.9.X"
dashboard/static/themes/light/index.html  → SATORI_VERSION + cache-busting (?v=1.9.X&t=timestamp)
dashboard/static/themes/dark/index.html   → SATORI_VERSION + cache-busting
dashboard/static/themes/lexigen/index.html → SATORI_VERSION + cache-busting
dashboard/static/login/index.html         → Version display + cache-busting
dashboard/static/review/index.html        → Cache-busting parameters
dashboard/static/settings/index.html      → Cache-busting parameters
dashboard/static/help/index.html          → Cache-busting parameters
```

### Tiger Service (Backend)
**Purpose**: Document analysis and hydrated JSON generation
- **Location**: `tiger/app/version.py` or embedded in service
- **Update Trigger**: Only when Tiger analysis logic changes
- **Current Focus**: Stable - only update when Tiger functionality changes

### Monkey Service (Backend)  
**Purpose**: Document generation and template processing
- **Location**: `monkey/cli.py` → version argument
- **Metadata**: `monkey/core/document_builder.py` → beaver_version
- **Update Trigger**: Only when Monkey generation logic changes
- **Current Focus**: Stable - only update when Monkey functionality changes

### Browser Service (Backend)
**Purpose**: PDF generation from HTML
- **Location**: `browser/package.json` → version
- **Update Trigger**: Only when Browser/PDF logic changes  
- **Current Focus**: Stable - only update when Browser functionality changes

## Frontend Cache-Busting Strategy

### Problem
Browsers cache JavaScript/CSS files aggressively, causing users to test old code even after updates.

### Solution
Version parameters on all static asset imports:

```html
<!-- Before (Cached) -->
<script src="/static/js/main.js"></script>

<!-- After (Cache-Busted) -->
<script src="/static/js/main.js?v=1.9.3&t=20250714-143000"></script>
```

### Implementation Locations

#### Main Dashboard
```html
<!-- dashboard/static/themes/light/index.html -->
<script src="/static/themes/light/js/main.js?v=${APP_VERSION}&t=${TIMESTAMP}"></script>
<script src="/static/themes/light/js/ui.js?v=${APP_VERSION}&t=${TIMESTAMP}"></script>
<script src="/static/themes/light/js/api.js?v=${APP_VERSION}&t=${TIMESTAMP}"></script>
```

#### Login Page
```html
<!-- dashboard/static/login/index.html -->
<script src="/static/login/login.js?v=${APP_VERSION}&t=${TIMESTAMP}"></script>
```

#### Review Page
```html
<!-- dashboard/static/review/index.html -->
<script src="/static/js/review.js?v=${APP_VERSION}&t=${TIMESTAMP}"></script>
```

#### Settings Page
```html
<!-- dashboard/static/settings/index.html -->
<script src="/static/settings/settings.js?v=${APP_VERSION}&t=${TIMESTAMP}"></script>
```

## Version Update Workflow

### When User Says "Tick the Version"

#### Step 1: Update Dashboard Version
```bash
# Update main version
dashboard/main.py:145 → APP_VERSION = "1.9.X"
```

#### Step 2: Update All HTML Templates
```bash
# Generate new timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Update all HTML files with new version and timestamp
dashboard/static/themes/light/index.html
dashboard/static/themes/dark/index.html  
dashboard/static/themes/lexigen/index.html
dashboard/static/login/index.html
dashboard/static/review/index.html
dashboard/static/settings/index.html
dashboard/static/help/index.html
```

#### Step 3: Update Version Displays
```javascript
// Update SATORI_VERSION in HTML templates
const SATORI_VERSION = '1.9.X';
```

#### Step 4: Restart Dashboard
```bash
cd dashboard && ./restart.sh
```

#### Step 5: Force Browser Refresh
```
Ctrl+Shift+R (Hard refresh) or Ctrl+F5
```

### When Backend Services Change

#### Tiger Changes
- Update `tiger/app/version.py` or version metadata
- Only when Tiger analysis logic actually changes

#### Monkey Changes  
- Update `monkey/cli.py` version string
- Update `monkey/core/document_builder.py` beaver_version
- Only when Monkey generation logic actually changes

#### Browser Changes
- Update `browser/package.json` version
- Only when Browser/PDF generation logic actually changes

## Testing Protocol

### Frontend Version Verification
1. Open Dashboard: `http://127.0.0.1:8000`
2. Check sidebar version display matches `APP_VERSION`
3. Open browser dev tools → Network tab
4. Verify JavaScript files load with correct `?v=X.X.X&t=timestamp` parameters
5. Confirm no `304 Not Modified` responses for static assets

### Backend Version Verification
```bash
# Check Monkey version
./monkey/run.sh --version

# Check Browser version  
cd browser && npm version

# Check Tiger version (when implemented)
./tiger/run.sh --version
```

## Common Issues & Solutions

### Dashboard Still Shows Old Version
**Cause**: Browser cache or incomplete cache-busting  
**Solution**: 
1. Verify `APP_VERSION` updated in `main.py`
2. Verify all HTML templates have new `?v=` parameters
3. Hard refresh browser (Ctrl+Shift+R)
4. Clear browser cache if necessary

### JavaScript Errors After Version Update
**Cause**: Mixed old/new JavaScript files  
**Solution**:
1. Ensure ALL JavaScript imports have same version parameter
2. Check for missing version parameters in HTML templates
3. Restart Dashboard service

### Backend Services Show Wrong Version
**Cause**: Version numbers updated unnecessarily  
**Solution**:
1. Only update backend versions when backend code actually changes
2. Backend versions should remain stable between frontend updates

## Version Numbering Scheme

### Dashboard (Frontend) Versioning
- **Major.Minor.Patch** format: `1.9.X`
- **Increment**: Every user request to "tick the version"
- **Frequency**: High (multiple times per day during development)

### Backend Service Versioning
- **Major.Minor.Patch** format: `1.1.X` 
- **Increment**: Only when service functionality changes
- **Frequency**: Low (only when backend logic changes)

## File Checklist for "Tick the Version"

### Required Updates (Every Time)
- [ ] `dashboard/main.py` → `APP_VERSION`
- [ ] `dashboard/static/themes/light/index.html` → version + timestamp
- [ ] `dashboard/static/themes/dark/index.html` → version + timestamp  
- [ ] `dashboard/static/themes/lexigen/index.html` → version + timestamp
- [ ] `dashboard/static/login/index.html` → version + timestamp
- [ ] `dashboard/static/review/index.html` → timestamp
- [ ] `dashboard/static/settings/index.html` → timestamp
- [ ] `dashboard/static/help/index.html` → timestamp

### Optional Updates (Only When Backend Changes)
- [ ] `monkey/cli.py` → version string
- [ ] `monkey/core/document_builder.py` → beaver_version
- [ ] `browser/package.json` → version
- [ ] `tiger/version.py` → version (when implemented)

## Summary

**Frontend Focus**: "Tick the version" = ensure users test latest Dashboard code  
**Cache-Busting**: Version parameters on all static assets  
**Backend Stability**: Service versions only change when service logic changes  
**User Experience**: No more testing old cached code accidentally

This system ensures efficient development workflow while maintaining system stability and clear version tracking.