# Justfile for dotfiles task automation
set shell := ["sh", "-cu"]

js_toolchain := "./scripts/js_toolchain.sh"
dotnet_sdk_install := "./scripts/dotnet_sdk_install.sh"
dotnet_toolchain := "./scripts/dotnet_toolchain.sh"

# Set up all dotfile symlinks safely
link:
    ./scripts/setup_symlinks.sh

# Run read-only Development Ecosystem audit
doctor *args:
    @./scripts/doctor.py {{args}}

# Alias for doctor
audit *args:
    @./scripts/doctor.py {{args}}

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
    # Install all CLI tools and apps defined in the package manifest
    brew bundle --file=./system/packages/Brewfile

# Alias for install-brew task
brew: install-brew

# Install VS Code extensions
install-vscode-extensions:
    sed -n '/^[[:space:]]*#/d; /^[[:space:]]*$/d; p' system/packages/vscode-extensions.txt | xargs -n 1 code --install-extension

# Full bootstrap: complete laptop setup
bootstrap: install-brew install-vscode-extensions setup-node setup-dotnet setup-security setup-network-security backup-and-link
    echo "✅ Complete laptop bootstrap complete!"
    echo "📝 Next steps:"
    echo "   - Run 'just setup-aws-cli' to configure AWS"
    echo "   - Copy system/git/gitconfig.local.example to ~/.gitconfig.local and edit"
    echo "   - Configure NordVPN account and Brave browser settings"
    echo "   - Use 'secure-on' when on public Wi-Fi networks"
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
    {{js_toolchain}} corepack enable
    {{js_toolchain}} corepack prepare pnpm@latest --activate
    {{js_toolchain}} pnpm setup
    echo "✅ pnpm installed, activated, and configured"

# Install global Node.js tools
install-node-tools: install-pnpm
    sed -n '/^[[:space:]]*#/d; /^[[:space:]]*$/d; p' system/packages/pnpm-global.txt | xargs -n 1 {{js_toolchain}} pnpm add -g
    echo "✅ Global Node.js tools installed from system/packages/pnpm-global.txt"
    echo "   - Biome: Available for project-specific configuration"
    echo "   - AWS CDK: Available for AWS infrastructure development"
    echo "   - Use 'biome init' in projects to create biome.json"

# Setup Node.js development environment (use global: dotfile setup-node)
setup-node: install-node install-node-tools
    echo "✅ Node.js development environment ready"
    echo "💡 Use 'dotfile setup-node' for future Node.js setup in other projects"

# Install ADR-0006 .NET SDK lines through mise
install-dotnet-sdks:
    {{dotnet_sdk_install}}
    echo "✅ ADR-0006 .NET SDK lines installed through mise"

# Install global .NET tools through the ADR-0006 mise-managed SDK
install-dotnet-tools:
    sed -n '/^[[:space:]]*#/d; /^[[:space:]]*$/d; s/[[:space:]]*#.*$//; p' system/packages/dotnet-tools.txt | while IFS= read -r tool; do {{dotnet_toolchain}} dotnet tool install --global "$tool" || {{dotnet_toolchain}} dotnet tool update --global "$tool"; done
    echo "✅ .NET global tools installed from system/packages/dotnet-tools.txt"

# Setup .NET development environment (use global: dotfile setup-dotnet)
setup-dotnet: install-dotnet-sdks install-dotnet-tools
    echo "✅ .NET development environment ready"
    echo "💡 Use 'dotfile setup-dotnet' for future .NET setup in other projects"

# Configure AWS CLI (use global: dotfile setup-aws)
setup-aws-cli:
    aws configure sso
    echo "✅ AWS CLI configured"
    echo "💡 Use 'dotfile setup-aws' for future AWS setup in other projects"

# Setup direnv for environment management
setup-direnv:
    @echo "direnv is configured by system/zsh/.zshrc"
    @echo "Run 'just link-only' to refresh shell symlinks"

# Setup security tools
setup-security: setup-direnv
    echo "✅ Security tools installed and configured"

# Run security scans (use global: dotfile security-scan)
security-scan:
    @echo "Use 'dotfile security-scan' for system-wide security scans"

# Network security commands are available globally via 'dotfile' aliases
# Use: dotfile secure-mode-on, dotfile dns-leak-test, etc.

# Setup network security tools
setup-network-security:
    # Create dnscrypt-proxy config directory
    mkdir -p ~/.config/dnscrypt-proxy
    echo "✅ Network security tools configured"
    echo "📝 Next steps:"
    echo "   - Run 'secure-on' to enable protection"
    echo "   - Configure NordVPN account in the app"
    echo "   - Set up Brave browser privacy settings"

# Run quality checks (use global: dotfile quality-check)
quality-check:
    @echo "Use 'dotfile quality-check' for system-wide quality checks"

# Fix formatting issues automatically (use global: dotfile fix-formatting)
fix-formatting:
    @echo "Use 'dotfile fix-formatting' for system-wide formatting fixes"

# Fix common formatting issues using sed
fix-formatting-comprehensive:
    # Fix trailing whitespace
    fd -t f -e json -e md -e mdc -e lua -e sh -e txt -e config -x sed -i '' 's/[[:space:]]*$//' {}
    # Ensure final newline
    fd -t f -e json -e md -e mdc -e lua -e sh -e txt -e config -x sh -c 'if [ "$(tail -c1 "$1" | wc -l)" -eq 0 ]; then echo >> "$1"; fi' _ {}
    # Convert tabs to 4 spaces
    fd -t f -e json -e md -e mdc -e lua -e sh -e txt -e config -x sed -i '' 's/\t/    /g' {}
    echo "✅ Comprehensive formatting fixes applied"

readme-lint:
    {{js_toolchain}} markdownlint README.md
    # Lint README.md for documentation issues

# Lint all code using Biome
repo-lint:
    {{js_toolchain}} biome lint --files-ignore-unknown=true .
    # Lint all code using Biome (installed globally via pnpm)
    # Ignores files that Biome doesn't recognize
