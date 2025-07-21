#!/bin/bash

# Safe Symlink Setup Script for Dotfiles
# ✅ Overrides existing files (use backup.sh first if needed)
# ✅ Uses absolute paths for safety

set -euo pipefail

echo "🔗 Setting up symlinks from dotfiles repo..."

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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
        echo "🗑️  Removing existing $description"
        rm -rf "$target"
    fi

    echo "🔗 Linking $target → $source"
    ln -sn "$source" "$target"
}

# Symlink list (source → target)
create_symlink "$DOTFILES_DIR/system/starship/starship.toml" "$HOME/.config/starship.toml" "Starship config"
create_symlink "$DOTFILES_DIR/system/neovim/init.lua" "$HOME/.config/nvim/init.lua" "Neovim config"

# Cursor configuration - link system-wide config files to home directory
create_symlink "$DOTFILES_DIR/system/cursor/settings.jsonc" "$HOME/.cursor/settings.json" "Cursor settings"
create_symlink "$DOTFILES_DIR/system/cursor/keybindings.jsonc" "$HOME/.cursor/keybindings.json" "Cursor keybindings"
create_symlink "$DOTFILES_DIR/system/cursor/argv.jsonc" "$HOME/.cursor/argv.json" "Cursor argv"
create_symlink "$DOTFILES_DIR/system/cursor/extensions.json" "$HOME/.cursor/extensions.json" "Cursor extensions"
# Cursor rules - repository rules stay in repo, no symlink needed
# The rules are used by Cursor AI directly from the repository

create_symlink "$DOTFILES_DIR/system/nushell/config.nu" "$HOME/Library/Application Support/nushell/config.nu" "Nushell config"
create_symlink "$DOTFILES_DIR/system/nushell/env.nu" "$HOME/Library/Application Support/nushell/env.nu" "Nushell env"
create_symlink "$DOTFILES_DIR/system/git/gitconfig" "$HOME/.gitconfig" "Git config"
create_symlink "$DOTFILES_DIR/system/ghostty/config" "$HOME/Library/Application Support/com.mitchellh.ghostty/config" "Ghostty config"
create_symlink "$DOTFILES_DIR/system/aws/config" "$HOME/.aws/config" "AWS config"
create_symlink "$DOTFILES_DIR/system/vscode/settings.jsonc" "$HOME/Library/Application Support/Code/User/settings.json" "VS Code settings"

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
