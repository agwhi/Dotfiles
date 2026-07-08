#!/bin/bash

# install.sh - Install requirements for dotfiles just scripts
# This script installs the prerequisites needed to use the justfile tasks

set -euo pipefail

echo "🔧 Installing prerequisites for dotfiles..."

# Check if Homebrew is installed
if ! command -v brew > /dev/null 2>&1; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ $(uname -m) == "arm64" ]]; then
        shellenv_line='eval "$(/opt/homebrew/bin/brew shellenv)"'
        if [[ ! -f ~/.zprofile ]] || ! grep -qxF "$shellenv_line" ~/.zprofile; then
            echo "$shellenv_line" >> ~/.zprofile
        fi
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

echo ""
echo "🎉 Prerequisites installed successfully!"
echo ""
echo "Next steps:"
echo "  just bootstrap   # Complete laptop setup (packages, toolchains, symlinks)"
echo "  just brew        # Install Homebrew packages only"
echo "  just backup      # Backup current system config"
echo "  just doctor      # Audit the development ecosystem"
echo ""
echo "For more commands, run: just --list"
