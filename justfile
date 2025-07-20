# Justfile for dotfiles task automation

# Set up all dotfile symlinks safely
link:
    ./setup_symlinks.sh

# Backup existing config files before symlinking
backup:
    ./backup.sh

# Backup and then create symlinks
backup-and-link: backup link
    echo "✅ Backup and symlink setup complete!"

# Upgrade all packages and tools
upgrade:
  topgrade

# Install all Homebrew packages
install-brew:
  # Install all CLI tools and apps defined in Brewfile
  brew bundle --file=./Brewfile

# Alias for install-brew task
brew: install-brew

# Install VS Code extensions
install-vscode-extensions:
  cat vscode/extensions.txt | xargs -n 1 code --install-extension

# Full setup: install packages and create symlinks
setup: install-brew install-vscode-extensions backup-and-link
  echo "✅ Full dotfiles setup complete!"
