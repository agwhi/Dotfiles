#!/bin/bash

# Dotfiles Backup Script
# Safely backs up existing system config files before applying changes

set -euo pipefail

# Set backup location
timestamp="$(date +%F_%H-%M-%S)"
backup_dir="$HOME/dotfiles-backup/$timestamp"
mkdir -p "$backup_dir"

echo "📦 Starting backup to: $backup_dir"

# List of files to back up (matches symlink targets)
files_to_backup=(
  "$HOME/.config/starship.toml"
  "$HOME/.config/nvim/init.lua"
  "$HOME/.cursor"
  "$HOME/Library/Application Support/nushell/config.nu"
  "$HOME/Library/Application Support/nushell/env.nu"
  "$HOME/.gitconfig"
  "$HOME/.gitconfig.local"
  "$HOME/.aws/config"
  "$HOME/Library/Application Support/com.mitchellh.ghostty/config"
  "$HOME/Library/Application Support/Code/User/settings.json"
  "$HOME/.gitignore_global"
)

# Loop through and back up existing files
for path in "${files_to_backup[@]}"; do
  if [[ -e "$path" ]]; then
    # Preserve full path inside backup dir
    dest="$backup_dir${path/#$HOME/}"
    mkdir -p "$(dirname "$dest")"
    cp -a "$path" "$dest"
    echo "✅ Backed up: $path → $dest"
  else
    echo "⚠️  Skipping missing file: $path"
  fi
done

# Log the backup path
dotfiles_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "$timestamp → $backup_dir" >> "$dotfiles_dir/backup-log.txt"

echo "✅ Backup complete!"
echo "📝 Backup recorded in $dotfiles_dir/backup-log.txt"