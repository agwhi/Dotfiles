# Justfile for dotfiles task automation

# Set up all dotfile symlinks safely
link:
    ./scripts/setup_symlinks.sh

# Backup existing config files before symlinking
backup:
    ./scripts/backup.sh

# Backup and then create symlinks
backup-and-link: backup link
    echo "✅ Backup and symlink setup complete!"

# Upgrade all packages and tools (use global: dotfile upgrade)
upgrade:
    @echo "Use 'dotfile upgrade' for system-wide upgrades"

# Install all Homebrew packages
install-brew:
    # Install all CLI tools and apps defined in Brewfile
    brew bundle --file=./system/Brewfile

# Alias for install-brew task
brew: install-brew

# Install VS Code extensions
install-vscode-extensions:
    cat system/vscode/extensions.txt | xargs -n 1 code --install-extension

# Full bootstrap: complete laptop setup
bootstrap: install-brew install-vscode-extensions setup-node setup-dotnet setup-security backup-and-link
    echo "✅ Complete laptop bootstrap complete!"
    echo "📝 Next steps:"
    echo "   - Run 'just setup-aws-cli' to configure AWS"
    echo "   - Copy system/git/gitconfig.local.example to ~/.gitconfig.local and edit"
    echo "   - Restart your terminal to load all changes"

# Alias for bootstrap (for discoverability)
install: bootstrap

# Alias for VS Code extensions (for discoverability)
vscode: install-vscode-extensions
editor: install-vscode-extensions

# Alias for symlink setup (for discoverability)
link-only: link

# Open dotfiles folder in Cursor editor
edit:
    cursor .

# Install latest Node.js LTS
install-node:
    fnm install --lts
    fnm use lts-latest
    fnm default lts-latest
    echo "✅ Node.js LTS installed and set as default"

# Enable corepack and install pnpm
install-pnpm:
    corepack enable
    corepack prepare pnpm@latest --activate
    pnpm setup
    echo "✅ pnpm installed, activated, and configured"

# Install global Node.js tools
install-node-tools: install-pnpm
    source ~/.config/nushell/env.nu; cat system/pnpm-global.txt | xargs -n 1 pnpm add -g
    echo "✅ Global Node.js tools installed from pnpm-global.txt"
    echo "   - Biome: Available for project-specific configuration"
    echo "   - AWS CDK: Available for AWS infrastructure development"
    echo "   - Use 'biome init' in projects to create biome.json"

# Setup Node.js development environment (use global: dotfile setup-node)
setup-node: install-node install-node-tools
    echo "✅ Node.js development environment ready"
    echo "💡 Use 'dotfile setup-node' for future Node.js setup in other projects"

# Install global .NET Lambda tools
install-dotnet-tools:
    dotnet tool install -g Amazon.Lambda.Tools || echo "Amazon.Lambda.Tools already installed"
    dotnet tool install -g Amazon.Lambda.TestTool-8.0 || echo "Amazon.Lambda.TestTool-8.0 already installed"
    echo "✅ .NET Lambda tools installed"

# Setup .NET development environment (use global: dotfile setup-dotnet)
setup-dotnet: install-dotnet-tools
    echo "✅ .NET development environment ready"
    echo "💡 Use 'dotfile setup-dotnet' for future .NET setup in other projects"

# Configure AWS CLI (use global: dotfile setup-aws)
setup-aws-cli:
    aws configure sso
    echo "✅ AWS CLI configured"
    echo "💡 Use 'dotfile setup-aws' for future AWS setup in other projects"

# Setup direnv for environment management
setup-direnv:
    echo 'eval "$(direnv hook nushell)"' >> ~/.config/nushell/config.nu
    echo "✅ direnv configured for nushell"

# Setup security tools
setup-security: setup-direnv
    echo "✅ Security tools installed and configured"

# Run security scans (use global: dotfile security-scan)
security-scan:
    @echo "Use 'dotfile security-scan' for system-wide security scans"

# Run quality checks (use global: dotfile quality-check)
quality-check:
    @echo "Use 'dotfile quality-check' for system-wide quality checks"

# Fix formatting issues automatically (use global: dotfile fix-formatting)
fix-formatting:
    @echo "Use 'dotfile fix-formatting' for system-wide formatting fixes"

# Fix common formatting issues using sed
fix-formatting-comprehensive:
    # Fix trailing whitespace
    fd -t f -e json -e md -e mdc -e lua -e nu -e sh -e txt -e config -x sed -i '' 's/[[:space:]]*$//' {}
    # Ensure final newline
    fd -t f -e json -e md -e mdc -e lua -e nu -e sh -e txt -e config -x sh -c 'if [ "$(tail -c1 "$1" | wc -l)" -eq 0 ]; then echo >> "$1"; fi' _ {}
    # Convert tabs to 4 spaces
    fd -t f -e json -e md -e mdc -e lua -e nu -e sh -e txt -e config -x sed -i '' 's/\t/    /g' {}
    echo "✅ Comprehensive formatting fixes applied"

readme-lint:
    markdownlint README.md
    # Lint README.md for documentation issues

# Lint all code using Biome
repo-lint:
    biome lint --files-ignore-unknown=true .
    # Lint all code using Biome (installed globally via pnpm)
    # Ignores files that Biome doesn't recognize
