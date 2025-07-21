#!/bin/bash

# install.sh - Install requirements for dotfiles just scripts
# This script installs the prerequisites needed to use the justfile tasks

set -e

echo "🔧 Installing prerequisites for dotfiles..."

# Check if Homebrew is installed
if ! command -v brew > /dev/null 2>&1; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    echo "✅ Homebrew already installed"
fi

# Install just if not already installed
if ! command -v just > /dev/null 2>&1; then
    echo "📦 Installing just..."
    brew install just
else
    echo "✅ just already installed"
fi

# Install brew bundle if not available
if ! brew bundle --help > /dev/null 2>&1; then
    echo "📦 Installing brew bundle..."
    brew tap Homebrew/bundle
else
    echo "✅ brew bundle already available"
fi

echo ""
echo "🎉 Prerequisites installed successfully!"
echo ""
echo "Next steps:"
echo "  just setup    # Full setup: install packages and create symlinks"
echo "  just brew     # Install Homebrew packages only"
echo "  just backup   # Backup current system config"
echo "  just edit     # Open dotfiles in Cursor"
echo ""
echo "For more commands, run: just --list" 