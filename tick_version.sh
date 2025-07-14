#!/bin/bash

# TM Dashboard-Only Version Update Script
# Usage: ./tick_version.sh [new_version]
# If no version provided, auto-increments patch version
# IMPORTANT: Only updates Dashboard versions - Tiger/Monkey versions remain unchanged

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TM_DIR="$SCRIPT_DIR"

echo -e "${BLUE}🎯 TM Dashboard Version Update Script${NC}"
echo "================================================"
echo -e "${YELLOW}NOTE: This script only updates Dashboard frontend versions${NC}"
echo -e "${YELLOW}      Backend service versions (Tiger/Monkey) remain unchanged${NC}"
echo ""

# Function to get current version from main.py
get_current_version() {
    grep "APP_VERSION = " "$TM_DIR/dashboard/main.py" | sed 's/.*"\([^"]*\)".*/\1/'
}

# Function to increment patch version
increment_version() {
    local version=$1
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)
    local patch=$(echo $version | cut -d. -f3)
    local new_patch=$((patch + 1))
    echo "$major.$minor.$new_patch"
}

# Get current version
CURRENT_VERSION=$(get_current_version)
echo -e "📍 Current Dashboard version: ${YELLOW}$CURRENT_VERSION${NC}"

# Display current service versions for reference
echo ""
echo -e "${BLUE}📋 Current Service Versions (unchanged):${NC}"
if [ -f "$TM_DIR/tiger/app/config/settings.py" ]; then
    TIGER_VERSION=$(grep "self.version = " "$TM_DIR/tiger/app/config/settings.py" | sed 's/.*"\([^"]*\)".*/\1/')
    echo -e "   🐅 Tiger Service: ${GREEN}$TIGER_VERSION${NC} (unchanged)"
fi
if [ -f "$TM_DIR/monkey/cli.py" ]; then
    MONKEY_VERSION=$(grep "version=" "$TM_DIR/monkey/cli.py" | sed 's/.*v\([0-9]\+\.[0-9]\+\.[0-9]\+\).*/\1/')
    echo -e "   🐒 Monkey Service: ${GREEN}$MONKEY_VERSION${NC} (unchanged)"
fi

# Determine new version
if [ -n "$1" ]; then
    NEW_VERSION="$1"
    echo -e "🎯 Using provided version: ${GREEN}$NEW_VERSION${NC}"
else
    NEW_VERSION=$(increment_version "$CURRENT_VERSION")
    echo -e "🔢 Auto-incrementing to: ${GREEN}$NEW_VERSION${NC}"
fi

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
echo -e "⏰ Cache-busting timestamp: ${YELLOW}$TIMESTAMP${NC}"

echo ""
echo -e "${BLUE}📝 Updating Dashboard files only...${NC}"

# Update main.py APP_VERSION (Dashboard backend)
echo -e "   ✏️  Updating dashboard/main.py"
sed -i.bak "s/APP_VERSION = \"[^\"]*\"/APP_VERSION = \"$NEW_VERSION\"/" "$TM_DIR/dashboard/main.py"

# Function to update HTML file with version and timestamp
update_html_file() {
    local file_path="$1"
    local file_name=$(basename "$file_path")
    
    if [ -f "$file_path" ]; then
        echo -e "   ✏️  Updating $file_name"
        
        # Update SATORI_VERSION (handle both single and double quotes)
        sed -i.bak "s/const SATORI_VERSION = ['\"][^'\"]*['\"]/const SATORI_VERSION = \"$NEW_VERSION\"/" "$file_path"
        
        # Update "Powered by Satori AI" version references (handle both patterns)
        sed -i.bak "s/Powered by Satori AI v[0-9]\+\.[0-9]\+\.[0-9]\+/Powered by Satori AI v$NEW_VERSION/g" "$file_path"
        
        # Update cache-busting parameters (?v=X.X.X&t=timestamp)
        sed -i.bak "s/\?v=[^&]*&t=[^'\"]*/?v=$NEW_VERSION\&t=$TIMESTAMP/g" "$file_path"
        
        # Add cache-busting to files that don't have it yet
        sed -i.bak "s/\.js\(['\"][^?]\)/\.js?v=$NEW_VERSION\&t=$TIMESTAMP\1/g" "$file_path"
        sed -i.bak "s/\.css\(['\"][^?]\)/\.css?v=$NEW_VERSION\&t=$TIMESTAMP\1/g" "$file_path"
        
        # Clean up any double cache-busting that might have been created
        sed -i.bak "s/\?v=[^&]*&t=[^'\"]*\?v=[^&]*&t=[^'\"]*/?v=$NEW_VERSION\&t=$TIMESTAMP/g" "$file_path"
    else
        echo -e "   ⚠️  File not found: $file_name"
    fi
}

# Update Dashboard HTML templates only
update_html_file "$TM_DIR/dashboard/static/themes/light/index.html"
update_html_file "$TM_DIR/dashboard/static/themes/dark/index.html" 
update_html_file "$TM_DIR/dashboard/static/themes/lexigen/index.html"
update_html_file "$TM_DIR/dashboard/static/login/index.html"
update_html_file "$TM_DIR/dashboard/static/review/index.html"
update_html_file "$TM_DIR/dashboard/static/settings/index.html"
update_html_file "$TM_DIR/dashboard/static/help/index.html"

# Clean up backup files
echo -e "   🧹 Cleaning up backup files"
find "$TM_DIR/dashboard/static" -name "*.bak" -delete
rm -f "$TM_DIR/dashboard/main.py.bak"

echo ""
echo -e "${BLUE}🔄 Restarting Dashboard service...${NC}"

# Restart dashboard
cd "$TM_DIR/dashboard"
if [ -f "./restart.sh" ]; then
    ./restart.sh
else
    echo -e "   ⚠️  restart.sh not found, please restart manually"
fi

echo ""
echo -e "${GREEN}✅ Dashboard version update complete!${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo -e "   Previous version: ${YELLOW}$CURRENT_VERSION${NC}"
echo -e "   New version:      ${GREEN}$NEW_VERSION${NC}"
echo -e "   Timestamp:        ${YELLOW}$TIMESTAMP${NC}"
echo -e "   Services updated: ${GREEN}Dashboard only${NC}"
echo ""
echo -e "${BLUE}🔍 Next steps:${NC}"
echo -e "   1. Open Dashboard: ${YELLOW}http://127.0.0.1:8000${NC}"
echo -e "   2. Hard refresh:   ${YELLOW}Ctrl+Shift+R${NC}"
echo -e "   3. Check version in sidebar"
echo ""
echo -e "${BLUE}🛠️  Verify cache-busting:${NC}"
echo -e "   • Open browser dev tools → Network tab"
echo -e "   • Reload page and check JS files have ${YELLOW}?v=$NEW_VERSION&t=$TIMESTAMP${NC}"
echo -e "   • No ${RED}304 Not Modified${NC} responses for static assets"
echo ""

# Optional: Display files that were updated
echo -e "${BLUE}📁 Dashboard files updated:${NC}"
echo -e "   • dashboard/main.py"
echo -e "   • dashboard/static/themes/light/index.html"
echo -e "   • dashboard/static/themes/dark/index.html"
echo -e "   • dashboard/static/themes/lexigen/index.html"
echo -e "   • dashboard/static/login/index.html"
echo -e "   • dashboard/static/review/index.html"
echo -e "   • dashboard/static/settings/index.html"
echo -e "   • dashboard/static/help/index.html"

echo ""
echo -e "${BLUE}📁 Service versions unchanged:${NC}"
if [ -f "$TM_DIR/tiger/app/config/settings.py" ]; then
    echo -e "   • Tiger Service: ${GREEN}$TIGER_VERSION${NC}"
fi
if [ -f "$TM_DIR/monkey/cli.py" ]; then
    echo -e "   • Monkey Service: ${GREEN}$MONKEY_VERSION${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Ready to test latest Dashboard frontend!${NC}"