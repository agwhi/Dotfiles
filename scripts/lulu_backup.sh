#!/bin/bash

# LuLu Firewall Rules Backup Script
# This script helps backup and restore LuLu firewall rules for the network security setup

set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LULU_BACKUP_DIR="$DOTFILES_DIR/backups/lulu"
LULU_PREFS="$HOME/Library/Preferences/com.objective-see.lulu.plist"

echo "🛡️  LuLu Firewall Rules Backup"

# Create backup directory
mkdir -p "$LULU_BACKUP_DIR"

# Function to backup LuLu rules
backup_lulu() {
    echo "📋 Backing up LuLu firewall rules..."

    if [[ -f "$LULU_PREFS" ]]; then
        cp "$LULU_PREFS" "$LULU_BACKUP_DIR/lulu_rules_$(date +%Y%m%d_%H%M%S).plist"
        echo "✅ LuLu rules backed up to $LULU_BACKUP_DIR"
    else
        echo "⚠️  LuLu preferences file not found. Is LuLu installed?"
        echo "   Install with: brew install lulu"
    fi
}

# Function to restore LuLu rules
restore_lulu() {
    echo "📋 Restoring LuLu firewall rules..."

    # Find the most recent backup
    LATEST_BACKUP=$(ls -t "$LULU_BACKUP_DIR"/lulu_rules_*.plist 2>/dev/null | head -1)

    if [[ -n "$LATEST_BACKUP" ]]; then
        echo "🔄 Restoring from: $LATEST_BACKUP"
        cp "$LATEST_BACKUP" "$LULU_PREFS"
        echo "✅ LuLu rules restored"
        echo "💡 Restart LuLu for changes to take effect"
    else
        echo "❌ No backup files found in $LULU_BACKUP_DIR"
    fi
}

# Function to list available backups
list_backups() {
    echo "📋 Available LuLu rule backups:"
    if [[ -d "$LULU_BACKUP_DIR" ]]; then
        ls -la "$LULU_BACKUP_DIR"/lulu_rules_*.plist 2>/dev/null || echo "   No backups found"
    else
        echo "   Backup directory does not exist"
    fi
}

# Main script logic
case "${1:-backup}" in
    "backup")
        backup_lulu
        ;;
    "restore")
        restore_lulu
        ;;
    "list")
        list_backups
        ;;
    *)
        echo "Usage: $0 [backup|restore|list]"
        echo "  backup  - Backup current LuLu rules (default)"
        echo "  restore - Restore most recent backup"
        echo "  list    - List available backups"
        exit 1
        ;;
esac