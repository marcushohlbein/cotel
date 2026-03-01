#!/bin/bash
# Auto-index repository with repo-intel when entering a project

# Check if repo-intel is installed
if ! command -v repo-intel &> /dev/null; then
    echo "⚠️  repo-intel not installed. Install with: pip install repo-intel"
    exit 0
fi

# Check if this is a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    exit 0
fi

# Check if already indexed recently (within last hour)
INDEX_DB=".repo-intel/index.db"
if [ -f "$INDEX_DB" ]; then
    LAST_INDEX=$(stat -f %m "$INDEX_DB" 2>/dev/null || stat -c %Y "$INDEX_DB" 2>/dev/null)
    NOW=$(date +%s)
    AGE=$((NOW - LAST_INDEX))
    
    # Skip if indexed within last hour
    if [ $AGE -lt 3600 ]; then
        exit 0
    fi
fi

# Auto-index in background
echo "🔄 Auto-indexing repository with repo-intel..."
repo-intel index --project auto > /dev/null 2>&1 &

exit 0
