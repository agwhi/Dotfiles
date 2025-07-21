#!/bin/bash

# Dotfiles Backup Script
# Safely backs up existing system config files before applying changes
#
# This script backs up all major dotfiles and config fragments that are not symlinked, as well as key system state (Node, .NET, AWS, security tools).
# It also exports the current Brewfile for reproducibility.
#
# Usage: Run before making major changes or re-symlinking dotfiles.

set -euo pipefail

# Get dotfiles directory (scripts are now in scripts/ subdirectory)
dotfiles_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Set backup location within dotfiles directory
timestamp="$(date +%F_%H-%M-%S)"
backup_dir="$dotfiles_dir/backups/$timestamp"
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
    "$HOME/.aws/credentials"
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

# Backup Node.js tools (only if they exist)
echo "📦 Backing up Node.js tools..."
if command -v fnm > /dev/null 2>&1; then
    fnm list > "$backup_dir/node-versions.txt"
    echo "✅ Node.js versions backed up"
fi

if command -v pnpm > /dev/null 2>&1; then
    pnpm list -g > "$backup_dir/pnpm-global.txt" 2>/dev/null || echo "No global pnpm packages" > "$backup_dir/pnpm-global.txt"
    echo "✅ pnpm global packages backed up (includes CDK tools)"
fi

# Backup .NET tools (only if they exist)
echo "📦 Backing up .NET tools..."
if command -v dotnet > /dev/null 2>&1; then
    dotnet tool list --global > "$backup_dir/dotnet-tools.txt"
    echo "✅ .NET global tools backed up"
fi

# Backup AWS tools (only if they exist)
echo "📦 Backing up AWS tools..."
if command -v aws > /dev/null 2>&1; then
    aws --version > "$backup_dir/aws-version.txt"
    echo "✅ AWS version backed up"
fi

if command -v cdk > /dev/null 2>&1; then
    cdk --version > "$backup_dir/cdk-version.txt"
    echo "✅ CDK version backed up"
fi

# Backup security tools (only if they exist)
echo "📦 Backing up security tools..."
if command -v ripsecrets > /dev/null 2>&1; then
    ripsecrets --version > "$backup_dir/ripsecrets-version.txt"
    echo "✅ ripsecrets version backed up"
fi

if command -v gitleaks > /dev/null 2>&1; then
    gitleaks version > "$backup_dir/gitleaks-version.txt"
    echo "✅ gitleaks version backed up"
fi

if command -v direnv > /dev/null 2>&1; then
    direnv --version > "$backup_dir/direnv-version.txt"
    echo "✅ direnv version backed up"
fi

# Export current Brewfile for reproducibility
if command -v brew > /dev/null 2>&1; then
    brew bundle dump --file="$backup_dir/Brewfile" --force
    echo "✅ Brewfile exported to backup directory"
fi


# Log the backup path
echo "$timestamp → $backup_dir" >> "$dotfiles_dir/backup-log.txt"

echo "✅ Backup complete!"
echo "📝 Backup recorded in $dotfiles_dir/backup-log.txt"
