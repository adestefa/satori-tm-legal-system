#!/bin/bash

# Version Update Script for TM Dashboard
# Updates version numbers and cache-busting timestamps across all files

if [ $# -ne 1 ]; then
    echo "Usage: $0 <new_version>"
    echo "Example: $0 1.9.4"
    exit 1
fi

NEW_VERSION=$1
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

echo "🔄 Updating TM Dashboard to version $NEW_VERSION..."

# Update backend version
echo "📁 Updating backend version..."
sed -i '' "s/APP_VERSION = \"[0-9.]*\"/APP_VERSION = \"$NEW_VERSION\"/" /Users/corelogic/satori-dev/TM/dashboard/main.py

# Update all HTML files
echo "📁 Updating frontend versions..."

# Main dashboard
sed -i '' "s/const SATORI_VERSION = \"[0-9.]*\"/const SATORI_VERSION = \"$NEW_VERSION\"/" /Users/corelogic/satori-dev/TM/dashboard/static/themes/light/index.html
sed -i '' "s/v=[0-9.]*&t=[0-9-]*/v=$NEW_VERSION\&t=$TIMESTAMP/g" /Users/corelogic/satori-dev/TM/dashboard/static/themes/light/index.html

# Login page
sed -i '' "s/Powered by Satori AI v[0-9.]*/Powered by Satori AI v$NEW_VERSION/" /Users/corelogic/satori-dev/TM/dashboard/static/login/index.html
sed -i '' "s/v=[0-9.]*&t=[0-9-]*/v=$NEW_VERSION\&t=$TIMESTAMP/g" /Users/corelogic/satori-dev/TM/dashboard/static/login/index.html

# Settings page
sed -i '' "s/v=[0-9.]*&t=[0-9-]*/v=$NEW_VERSION\&t=$TIMESTAMP/g" /Users/corelogic/satori-dev/TM/dashboard/static/settings/index.html

# Review page
sed -i '' "s/v=[0-9.]*&t=[0-9-]*/v=$NEW_VERSION\&t=$TIMESTAMP/g" /Users/corelogic/satori-dev/TM/dashboard/static/review/index.html

# Help page
sed -i '' "s/v=[0-9.]*&t=[0-9-]*/v=$NEW_VERSION\&t=$TIMESTAMP/g" /Users/corelogic/satori-dev/TM/dashboard/static/help/index.html

# Dark theme
sed -i '' "s/const SATORI_VERSION = \"[0-9.]*\"/const SATORI_VERSION = \"$NEW_VERSION\"/" /Users/corelogic/satori-dev/TM/dashboard/static/themes/dark/index.html
sed -i '' "s/v=[0-9.]*&t=[0-9-]*/v=$NEW_VERSION\&t=$TIMESTAMP/g" /Users/corelogic/satori-dev/TM/dashboard/static/themes/dark/index.html

# Lexigen theme
sed -i '' "s/const SATORI_VERSION = \"[0-9.]*\"/const SATORI_VERSION = \"$NEW_VERSION\"/" /Users/corelogic/satori-dev/TM/dashboard/static/themes/lexigen/index.html
sed -i '' "s/v=[0-9.]*&t=[0-9-]*/v=$NEW_VERSION\&t=$TIMESTAMP/g" /Users/corelogic/satori-dev/TM/dashboard/static/themes/lexigen/index.html

echo "✅ Version updated to $NEW_VERSION with timestamp $TIMESTAMP"
echo "🔄 Please restart the dashboard server for changes to take effect"
echo ""
echo "Files updated:"
echo "  - dashboard/main.py (APP_VERSION)"
echo "  - All HTML files (SATORI_VERSION and cache-busting)"
echo "  - All theme files (light, dark, lexigen)"
echo "  - Login, settings, review, and help pages"