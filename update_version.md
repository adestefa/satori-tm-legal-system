# Tiger-Monkey Version Update Instructions

This document provides step-by-step instructions for updating version numbers across the entire Tiger-Monkey system.

## Version Number Locations

The TM system has version numbers in multiple locations that must be updated synchronously to maintain consistency across the platform.

### 1. Backend API Version

**File:** `dashboard/main.py`
**Location:** Line ~146
**Pattern:** `APP_VERSION = "X.Y.Z"`

```python
APP_VERSION = "2.0.0"  # Update this version number
```

### 2. Frontend JavaScript Cache-Busting

**File:** `dashboard/static/themes/light/index.html`
**Location:** Lines ~269-274
**Pattern:** `?v=X.Y.Z&t=YYYYMMDD-HHMMSS`

```html
<script src="/themes/light/js/config.js?v=2.0.0&t=20250715-120000" type="module"></script>
<script src="/themes/light/js/api.js?v=2.0.0&t=20250715-120000" type="module"></script>
<script src="/themes/light/js/ani.js?v=2.0.0&t=20250715-120000" type="module"></script>
<script src="/themes/light/js/ui.js?v=2.0.0&t=20250715-120000" type="module"></script>
<script src="/themes/light/js/eventHandlers.js?v=2.0.0&t=20250715-120000" type="module"></script>
<script src="/themes/light/js/main.js?v=2.0.0&t=20250715-120000" type="module"></script>
```

### 3. Frontend SATORI_VERSION Constants

**Files:**
- `dashboard/static/themes/light/index.html` (Line ~16)
- `dashboard/static/themes/lexigen/index.html` (Line ~10)
- `dashboard/static/settings/index.html` (Line ~10)

**Pattern:** `const SATORI_VERSION = "X.Y.Z";`

```javascript
const SATORI_VERSION = "2.0.0";  // Update this version
```

### 4. User-Visible Version Displays

**Files:**
- `dashboard/static/themes/light/index.html` (Line ~187) - Dashboard sidebar
- `dashboard/static/login/index.html` (Line ~108) - Login page footer

**Pattern:** `Powered by Satori AI vX.Y.Z`

```html
<span>Powered by Satori AI v2.0.0</span>
```

### 5. Console Log Version References

**File:** `dashboard/static/themes/light/js/main.js`
**Location:** Line ~446
**Pattern:** `DASHBOARD VERSION: X.Y.Z`

```javascript
console.log('🔍 DASHBOARD VERSION: 2.0.0 - Case upload service added, polling disabled');
```

### 6. Additional HTML Files with Cache-Busting

**Files with `?v=X.Y.Z` parameters:**
- `dashboard/static/login/index.html` (login.js import)
- `dashboard/static/settings/index.html` (CSS and JS imports)
- `dashboard/static/review/index.html` (JS imports)
- `dashboard/static/themes/dark/index.html` (JS imports)
- `dashboard/static/themes/lexigen/index.html` (CSS and JS imports)
- `dashboard/static/help/index.html` (JS imports)

## Step-by-Step Update Process

### 1. Choose New Version Number
Follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes or major new features
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

### 2. Update Backend Version
```bash
# Edit dashboard/main.py
sed -i '' 's/APP_VERSION = "[0-9]*\.[0-9]*\.[0-9]*"/APP_VERSION = "X.Y.Z"/g' dashboard/main.py
```

### 3. Update Frontend Cache-Busting (Bulk)
```bash
# Update all HTML files with version numbers
NEW_VERSION="X.Y.Z"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

find dashboard/static -name "*.html" -exec sed -i '' "s/v=[0-9]*\.[0-9]*\.[0-9]*/v=${NEW_VERSION}/g" {} \;
find dashboard/static -name "*.html" -exec sed -i '' "s/t=[0-9]*-[0-9]*/t=${TIMESTAMP}/g" {} \;
```

### 4. Update SATORI_VERSION Constants
```bash
# Update JavaScript version constants
sed -i '' 's/SATORI_VERSION = "[0-9]*\.[0-9]*\.[0-9]*"/SATORI_VERSION = "X.Y.Z"/g' \
  dashboard/static/themes/light/index.html \
  dashboard/static/themes/lexigen/index.html \
  dashboard/static/settings/index.html
```

### 5. Update User-Visible Displays
```bash
# Update version displays in UI
sed -i '' 's/Satori AI v[0-9]*\.[0-9]*\.[0-9]*/Satori AI vX.Y.Z/g' \
  dashboard/static/themes/light/index.html \
  dashboard/static/login/index.html
```

### 6. Update Console Log References
```bash
# Update version in console logs
sed -i '' 's/DASHBOARD VERSION: [0-9]*\.[0-9]*\.[0-9]*/DASHBOARD VERSION: X.Y.Z/g' \
  dashboard/static/themes/light/js/main.js
```

### 7. Verification Commands
```bash
# Verify all versions are updated correctly
echo "=== Backend API Version ==="
grep "APP_VERSION" dashboard/main.py

echo "=== SATORI_VERSION Constants ==="
grep -r "SATORI_VERSION" dashboard/static/ | grep -v "node_modules"

echo "=== User-Visible Versions ==="
grep -r "Satori AI v" dashboard/static/ | grep -v "node_modules"

echo "=== Console Log Versions ==="
grep -r "DASHBOARD VERSION" dashboard/static/

echo "=== Cache-Busting Versions ==="
grep -r "?v=" dashboard/static/ | head -10
```

## Automated Update Script

For convenience, you can use this automated script:

```bash
#!/bin/bash
# update_version.sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <new_version>"
    echo "Example: $0 2.1.0"
    exit 1
fi

NEW_VERSION=$1
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "Updating TM system to version $NEW_VERSION..."

# 1. Backend API version
sed -i '' "s/APP_VERSION = \"[0-9]*\.[0-9]*\.[0-9]*\"/APP_VERSION = \"$NEW_VERSION\"/g" dashboard/main.py

# 2. Cache-busting parameters
find dashboard/static -name "*.html" -exec sed -i '' "s/v=[0-9]*\.[0-9]*\.[0-9]*/v=$NEW_VERSION/g" {} \;
find dashboard/static -name "*.html" -exec sed -i '' "s/t=[0-9]*-[0-9]*/t=$TIMESTAMP/g" {} \;

# 3. SATORI_VERSION constants
sed -i '' "s/SATORI_VERSION = \"[0-9]*\.[0-9]*\.[0-9]*\"/SATORI_VERSION = \"$NEW_VERSION\"/g" \
  dashboard/static/themes/light/index.html \
  dashboard/static/themes/lexigen/index.html \
  dashboard/static/settings/index.html

# 4. User-visible displays
sed -i '' "s/Satori AI v[0-9]*\.[0-9]*\.[0-9]*/Satori AI v$NEW_VERSION/g" \
  dashboard/static/themes/light/index.html \
  dashboard/static/login/index.html

# 5. Console log references
sed -i '' "s/DASHBOARD VERSION: [0-9]*\.[0-9]*\.[0-9]*/DASHBOARD VERSION: $NEW_VERSION/g" \
  dashboard/static/themes/light/js/main.js

echo "Version update complete!"
echo "Don't forget to:"
echo "1. Test the updated system"
echo "2. Commit changes: git add . && git commit -m 'Update version to $NEW_VERSION'"
echo "3. Create git tag: git tag v$NEW_VERSION"
echo "4. Push changes: git push && git push --tags"
```

## Testing After Version Update

1. **Restart Dashboard:**
   ```bash
   ./dashboard/restart.sh
   ```

2. **Verify API Version:**
   ```bash
   curl http://127.0.0.1:8000/api/version
   # Should return: {"version":"X.Y.Z"}
   ```

3. **Check Browser Cache:**
   - Hard refresh (Ctrl+Shift+R) to ensure new assets load
   - Verify version displays in dashboard sidebar and login page
   - Check browser developer tools that JS files load with new version parameters

4. **Verify Console Logs:**
   - Check browser console for correct version in log messages
   - Ensure no 404 errors for missing assets

## Version History Integration

Consider updating:
- `dashboard/changelog.md` - Add release notes
- `TM/CLAUDE.md` - Update version references in documentation
- Release tags in Git repository

## Common Issues

1. **Browser Caching:** Always hard refresh after version updates
2. **Missed Files:** Use grep commands above to verify all locations updated
3. **Timestamp Sync:** Ensure timestamp format matches existing pattern
4. **Console Errors:** Check for any 404s indicating missed cache-busting updates

---

**Last Updated:** 2025-07-15  
**Current Version:** 2.0.0  
**Documentation Status:** ✅ Complete