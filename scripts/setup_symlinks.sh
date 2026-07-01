#!/bin/bash

# Safe Symlink Setup Script for Dotfiles
# ✅ Backs up existing files before replacing them
# ✅ Uses absolute paths for safety

set -euo pipefail

echo "🔗 Setting up symlinks from dotfiles repo..."

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR=""

backup_existing_target() {
    local target="$1"
    local description="$2"

    if [[ ! -e "$target" && ! -L "$target" ]]; then
        return
    fi

    if [[ -z "$BACKUP_DIR" ]]; then
        local timestamp
        timestamp="$(date +%F_%H-%M-%S)"
        BACKUP_DIR="$DOTFILES_DIR/backups/symlinks-$timestamp"
        mkdir -p "$BACKUP_DIR"
        echo "$timestamp → $BACKUP_DIR" >> "$DOTFILES_DIR/symlink-backups.txt"
    fi

    local dest="$BACKUP_DIR${target/#$HOME/}"
    mkdir -p "$(dirname "$dest")"
    cp -a "$target" "$dest"
    echo "💾 Backed up existing $description to $dest"
}

# Function to create symlink safely
create_symlink() {
    local source="$1"
    local target="$2"
    local description="$3"

    echo "➡️  $description"
    echo "    Source: $source"
    echo "    Target: $target"

    local target_dir
    target_dir="$(dirname "$target")"
    mkdir -p "$target_dir"

    if [[ "$source" == "$target" ]]; then
        echo "✅ $description already lives at target"
        return
    fi

    # Don't sync if target is inside the dotfiles repo
    if [[ "$target" != "$DOTFILES_DIR"* ]] && [[ -e "$target" ]] && [[ ! -e "$source" ]]; then
        echo "📋 Copying existing $description to repo"
        cp -r "$target" "$source"
    elif [[ "$target" == "$DOTFILES_DIR"* ]]; then
        echo "⚠️  Skipping copy: target is inside dotfiles repo"
    fi

    if [[ ! -e "$source" ]]; then
        echo "⚠️  Source does not exist, skipping"
        return
    fi

    # Check if target already exists and is correctly symlinked
    if [[ -L "$target" ]]; then
        local current_target="$(readlink "$target")"
        if [[ "$current_target" == "$source" ]]; then
            echo "✅ $description already correctly symlinked"
            return
        fi
    fi

    # Remove existing file/directory/symlink if it exists
    if [[ -e "$target" || -L "$target" ]]; then
        backup_existing_target "$target" "$description"
        echo "🗑️  Removing existing $description"
        rm -rf "$target"
    fi

    echo "🔗 Linking $target → $source"
    ln -sn "$source" "$target"
}

# Symlink list (source → target)
create_symlink "$DOTFILES_DIR" "$HOME/.dotfiles" "Dotfiles repo shortcut"
create_symlink "$DOTFILES_DIR/system/starship/starship.toml" "$HOME/.config/starship.toml" "Starship config"
create_symlink "$DOTFILES_DIR/system/neovim/init.lua" "$HOME/.config/nvim/init.lua" "Neovim config"
create_symlink "$DOTFILES_DIR/system/zsh/.zshenv" "$HOME/.zshenv" "zsh env"
create_symlink "$DOTFILES_DIR/system/zsh/.zprofile" "$HOME/.zprofile" "zsh login config"
create_symlink "$DOTFILES_DIR/system/zsh/.zshrc" "$HOME/.zshrc" "zsh interactive config"
create_symlink "$DOTFILES_DIR/system/mise/config.toml" "$HOME/.config/mise/config.toml" "mise config"

# Cursor configuration - link system-wide config files to home directory
create_symlink "$DOTFILES_DIR/system/cursor/settings.jsonc" "$HOME/.cursor/settings.json" "Cursor settings"
create_symlink "$DOTFILES_DIR/system/cursor/keybindings.jsonc" "$HOME/.cursor/keybindings.json" "Cursor keybindings"
create_symlink "$DOTFILES_DIR/system/cursor/argv.jsonc" "$HOME/.cursor/argv.json" "Cursor argv"
create_symlink "$DOTFILES_DIR/system/cursor/extensions.json" "$HOME/.cursor/extensions.json" "Cursor extensions"
# Cursor rules - repository rules stay in repo, no symlink needed
# The rules are used by Cursor AI directly from the repository

create_symlink "$DOTFILES_DIR/system/git/gitconfig" "$HOME/.gitconfig" "Git config"
create_symlink "$DOTFILES_DIR/system/ghostty/config" "$HOME/Library/Application Support/com.mitchellh.ghostty/config" "Ghostty config"
create_symlink "$DOTFILES_DIR/system/aws/config" "$HOME/.aws/config" "AWS config"
create_symlink "$DOTFILES_DIR/system/vscode/settings.jsonc" "$HOME/Library/Application Support/Code/User/settings.json" "VS Code settings"

# Global justfile for system-wide commands
create_symlink "$DOTFILES_DIR/system/global-justfile" "$HOME/.justfile" "Global justfile"

# Topgrade configuration
create_symlink "$DOTFILES_DIR/system/topgrade.toml" "$HOME/.config/topgrade.toml" "Topgrade config"

# Direnv configuration
create_symlink "$DOTFILES_DIR/system/direnv.toml" "$HOME/.config/direnv/direnv.toml" "Direnv config"

# DNS encryption configuration
create_symlink "$DOTFILES_DIR/system/dnscrypt-proxy/dnscrypt-proxy.toml" "$HOME/.config/dnscrypt-proxy/dnscrypt-proxy.toml" "DNS encryption config"

# Global Git ignore setup
if [[ -e "$DOTFILES_DIR/system/git/gitignore_global" ]]; then
    echo "🔧 Setting up global gitignore"
    create_symlink "$DOTFILES_DIR/system/git/gitignore_global" "$HOME/.gitignore_global" "Global gitignore"
fi

if [[ -e "$DOTFILES_DIR/system/git/gitconfig.local" ]]; then
    echo "🔧 Setting up local gitconfig"
    create_symlink "$DOTFILES_DIR/system/git/gitconfig.local" "$HOME/.gitconfig.local" "Git local config"
fi

echo "✅ Symlink setup complete!"
