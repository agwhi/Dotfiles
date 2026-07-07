# 💻 Dotfiles Setup – macOS Dev Environment

A carefully curated developer setup for Node.js (via fnm-managed Node and
Corepack/pnpm), .NET 8 (C#),
TypeScript (CDK + Serverless), and React/Next.js on macOS, designed to
maximise dev experience and developer security with a fast, consistent
toolchain.

This repository manages your macOS development environment through dotfiles,
providing a unified setup for all your development tools and configurations.

---

## 🎯 Philosophy

This dotfiles repository follows a carefully considered philosophy for
building a productive, secure, and maintainable development environment:

### **Global-first Approach**

Everything here is set up globally (not repo-specific) to provide a
consistent experience across all projects. This includes:

- **Editor configurations** that work everywhere
- **Global tools** that are always available
- **Shell environment** that's consistent across terminals
- **Security tools** that protect all your work

### **Speed & Clarity**

We favor tools that reduce friction and are fast to use:

- **Rust-based tools** (fd, bat, ripgrep, topgrade) for performance
- **Just task runner** for simple, fast automation
- **zsh** as the primary interactive/editor shell for AI-friendly command
  compatibility
- **Minimal prompts** (Starship) that don't slow down your workflow

### **Terminal Native**

Most tools are CLI or TUI based, with Rust-preferred when options exist:

- **CLI-first** approach for automation and scripting
- **TUI tools** for interactive tasks (fzf, fd)
- **Rust ecosystem** for performance-critical tools
- **Cross-platform** compatibility where possible

### **Single Source of Truth**

All config is tracked, versioned, and symlinked:

- **Version controlled** configurations
- **Symlinked** from dotfiles to system locations
- **Backup system** for existing configurations
- **Idempotent** setup scripts

### **Secure by Default**

DevSecOps from day one with built-in security:

- **Secret scanning** (ripsecrets, gitleaks) for all commits
- **Environment management** (direnv) for secure config
- **Global gitignore** for sensitive files
- **Security tools** integrated into daily workflow

---

## 🚀 Quick Start

### Prerequisites

- macOS (tested on macOS 14+)
- Git installed
- Administrator access (for Homebrew installation)

### 1. Clone and Install Prerequisites

```bash
# Clone this repository
git clone <your-repo-url> ~/.dotfiles
cd ~/.dotfiles

# Install Homebrew, just, and other requirements
./install.sh
```

### 2. Set Up Your Environment

```bash
# Complete laptop bootstrap: install packages and create symlinks
just bootstrap
```

This comprehensive setup will:

- Install all Homebrew packages from `system/packages/Brewfile`
- Install VS Code extensions
- Install Node.js LTS and global tools (Biome, AWS CDK)
- Install .NET 8 and Lambda tools
- Configure security tools and direnv
- Configure network security tools (DNS encryption, VPN, firewall)
- Back up existing config files to `backups/`
- Create symlinks from dotfiles to system locations

### 3. Verify Installation

```bash
# Check that everything is working
just quality-check
just security-scan
```

### 4. Essential Commands

```bash
just bootstrap              # Complete laptop setup (alias: just install)
just brew                  # Install all Homebrew packages from system/packages/Brewfile
just backup                # Back up current system config to repo
just edit                  # Open dotfiles folder in VS Code
just upgrade               # Update all packages and tools
just vscode                # Install VS Code extensions (alias: just editor)
just link-only             # Create symlinks only
just --list                # Show all available commands
```

### 5. Next Steps

After bootstrap, you can:

- **Configure AWS CLI**: `just setup-aws-cli`
- **Set up Git config**: Copy `git/gitconfig.local.example` to
  `~/.gitconfig.local`
- **Restart your terminal** to load all shell changes
- **Customize your setup**: Edit configuration files in the dotfiles
  directory

---

## 🛠️ Tools by Category

### 🖥 Terminal + Shell

| Tool       | Description                               |
| ---------- | ----------------------------------------- |
| [Ghostty]  | Terminal emulator (fast, GPU-accelerated) |
| [zsh]      | Primary interactive and editor shell      |
| [Starship] | Minimal, fast prompt                      |
| [Carapace] | Completion engine for CLIs                |
| [Zoxide]   | Smarter `cd`                              |
| [fzf]      | Fuzzy finder                              |
| [fd]       | Better `find`                             |
| [bat]      | Syntax-highlighted `cat`                  |
| [topgrade] | One command to update everything          |

### 📦 Package Managers

| Tool       | Description                                            |
| ---------- | ------------------------------------------------------ |
| [Homebrew] | macOS-native package manager and fnm installer         |
| [fnm]      | Owner for the Node.js runtime and trusted JS commands  |
| [pnpm]     | Preferred Node.js package manager via fnm/Corepack     |
| [cargo]    | Rust package manager (used for many tools)             |

### ✨ Editor / IDE

| Tool      | Description                               |
| --------- | ----------------------------------------- |
| [Neovim]  | For terminal editing                      |
| [VS Code] | Main GUI IDE                              |

**Agent Guidance:**

- `AGENTS.md` - Repo-wide guidance for AI agents working in this
  development ecosystem
- `docs/adr/AGENTS.md` - ADR-specific guidance for decision records
- `system/ai/apm/apm.yml` - Shared AI baseline package manifest for Codex,
  Claude Code, and opencode

### 🚀 Productivity & Launchers

| Tool      | Description                                |
| --------- | ------------------------------------------ |
| [Raycast] | Spotlight replacement w/ dev tools support |

### 🌐 AWS / Cloud Dev

| Tool                        | Description                    |
| --------------------------- | ------------------------------ |
| [awscli]                    | AWS CLI                        |
| [aws-sso-util]              | AWS SSO configuration helper   |
| [cdk]                       | AWS CDK (TypeScript)           |
| [cdk-dia]                   | CDK diagram generator          |
| [Amazon.Lambda.Tools]       | .NET Lambda deployment tools   |
| [Amazon.Lambda.TestTool]    | .NET Lambda local testing      |

### 🔒 DevSecOps

| Tool                   | Description                               |
| ---------------------- | ----------------------------------------- |
| [ripsecrets]           | Fast secret scanner for commits           |
| [gitleaks]             | Deep secret scanning with rulesets        |
| [direnv]               | Auto loads `.envrc` files per directory   |
| [dotenv-linter]        | Lint `.env` files globally                |
| [editorconfig-checker] | Ensures consistent editor settings        |

### 🎨 Code Quality & Formatting

| Tool                   | Description                                             |
| ---------------------- | ------------------------------------------------------- |
| [@biomejs/biome]       | Global code formatter and linter                        |
| [.editorconfig]        | Editor configuration for consistent formatting          |
| [VS Code]              | Configured with 4-space indentation and format-on-save  |

**Formatting Standards:**

- **4-space indentation** (never tabs)
- **LF line endings** (Unix-style)
- **No trailing whitespace**
- **Final newline** at end of files
- **Biome** as default formatter for supported file types

**Using Biome in Projects:**

```bash
# Install global Node.js tools (includes Biome)
just install-node-tools

# In your project directory
biome init                    # Create biome.json configuration
biome check .                 # Check formatting and linting
biome format .                # Format all files
biome lint .                  # Lint all files
```

**Editor Integration:**

- VS Code is configured to use Biome as the default formatter
- Format-on-save is enabled for automatic formatting
- Biome respects the 4-space indentation standard

---

## 🔧 Setup & Management

### Symlink Setup

All configs are symlinked into correct system paths to maintain this repo
as the single source of truth:

```bash
just link
```

The setup script (`setup_symlinks.sh`) safely:

- Backs up existing config files to `.backup` versions
- Creates symlinks from dotfiles repo to system locations
- Logs all actions to `symlink-backups.txt`
- Handles idempotent re-runs safely
- Uses robust path resolution for symlink verification

### Backup System

**Backup current system state:**

```bash
just backup
```

This runs `backup.sh` which:

- Backs up non-symlinked files to the repo
- Updates `system/packages/Brewfile` with current Homebrew packages
- Updates `system/packages/vscode-extensions.txt` with current VS Code extensions
- Logs all actions to `backup-log.txt`

**Backup logs:**

- `symlink-backups.txt` - Log of symlink creation and backups
- `backup-log.txt` - Log of system state backups

### Git Configuration

Symlink `.gitconfig` globally and separate sensitive config:

```bash
cp git/.gitconfig.local.example ~/.gitconfig.local
just link
```

**Structure:**

- `git/gitconfig` → `~/.gitconfig` (safe to commit)
- `~/.gitconfig.local` (personal credentials, not committed)
- `git/.gitconfig.local.example` (template for new machines)

### Backup & Upgrade

**Upgrade everything:**

```bash
topgrade
```

**Available Commands:**

```bash
# Dotfile management (local to this repo)
just setup                  # Full setup: install packages and create symlinks
just brew                  # Install all Homebrew packages from system/packages/Brewfile
just backup                # Back up current system config to repo
just edit                  # Open dotfiles folder in VS Code
just link                  # Set up all dotfile symlinks only
just install-vscode-extensions # Install VS Code extensions only
just install-node-tools    # Install global Node.js tools through fnm/Corepack/pnpm
just setup-security        # Install and configure security tools
just setup-network-security # Configure DNS encryption and VPN tools

# Environment setup (use global commands for other projects)
just setup-node            # Install Node.js LTS and global tools (Biome, CDK)
just setup-dotnet          # Install .NET 8 Lambda tools
just setup-aws             # Configure AWS CLI (CDK tools installed via Node.js)

# Quality checks
just repo-lint             # Lint all code using Biome (local to dotfiles repo)
just readme-lint           # Lint README.md for documentation issues
just security-scan         # Redirects to global 'dotfile security-scan' command
just quality-check         # Redirects to global 'dotfile quality-check' command
just upgrade               # Redirects to global 'dotfile upgrade' command

```

### **Global Justfile Commands**

The dotfiles setup also creates a global justfile (`~/.justfile`) that provides
useful commands for any project. These are available via convenient zsh
aliases:

```bash
# Quality and security (available in any directory)
quality                    # Run security scans + formatting checks
security                   # Run secret scanning only
glint                      # Lint with Biome (if biome.json exists)
gformat                    # Format with Biome (if biome.json exists)
gdocs                      # Lint markdown files
gfix                       # Fix formatting issues

# Environment setup (available anywhere)
gnode                      # Setup Node.js environment
gdotnet                    # Setup .NET environment
gaws                       # Configure AWS CLI
gupgrade                   # Upgrade all packages with topgrade

# Network security (available anywhere)
secure-on                  # Enable DNS encryption + VPN (for public Wi-Fi)
secure-off                 # Disable DNS encryption + VPN
dns-start                  # Start DNS encryption only
dns-stop                   # Stop DNS encryption only
vpn-on                     # Connect VPN only
vpn-off                    # Disconnect VPN only
dns-test                   # Test for DNS leaks
lulu-backup                # Backup LuLu firewall rules
lulu-restore               # Restore LuLu firewall rules
lulu-list                  # List LuLu firewall rule backups

# Project initialization
gbiome                     # Initialize Biome in current project
ghelp                      # Show all available commands

# Direct access to global justfile
dotfile <command>          # Run any global justfile command 
```

**Note:** These aliases are automatically available in any directory and work
with the global justfile configuration.

**Backup non-symlinked files:**

```bash
just backup
```

Updates `system/packages/Brewfile` and
`system/packages/vscode-extensions.txt` (symlinked files are already tracked).

### AWS Development Setup

**Configure AWS CLI with SSO:**

```bash
just setup-aws
```

This will:

- Install AWS CLI and aws-sso-util via Homebrew
- Configure AWS CLI with SSO authentication
- Back up AWS configuration files

**Note:** AWS CDK tools (aws-cdk, cdk-dia) are installed via Node.js setup
(`just setup-node`)

**Manual AWS CLI configuration:**

```bash
aws configure sso
```

Follow the prompts to set up your AWS SSO profile. The configuration will
be backed up automatically.

### Security & DevSecOps Setup

**Install and configure security tools:**

```bash
just setup-security
```

This will:

- Install ripsecrets, gitleaks, direnv, dotenv-linter, and
  editorconfig-checker
- Configure direnv through the repo-managed zsh startup files
- Back up security tool versions

**Run security scans:**

```bash
just security-scan
```

This runs:

- `ripsecrets` - Fast secret scanning for commits
- `gitleaks` - Deep secret scanning with rulesets

**Run quality checks:**

```bash
just quality-check
```

This runs:

- Secret scanning (ripsecrets + gitleaks)
- EditorConfig validation
- Environment file linting

---

## 🛡️ DevSecOps & Security

Security checks are run manually using:

```bash
just quality-check
just security-scan
```

If you want to automate secret scanning, you can add a pre-commit hook like
this:

```bash
#!/bin/sh
just quality-check || exit 1
```

Copy this to `.git/hooks/pre-commit` to enforce checks before every commit
(optional).

---

## 🔒 Privacy & Safety on Public Networks

This setup includes tools to protect your privacy and security when using
public Wi-Fi networks (cafés, airports, hotels, conferences like AWS re:Invent).

### **Quick Start for Public Networks**

```bash
# Enable full protection (DNS encryption + VPN)
secure-on

# Disable when done
secure-off

# Test for DNS leaks
dns-test
```

### **What Each Tool Does**

#### **DNS Encryption (dnscrypt-proxy)**

- **Purpose**: Encrypts DNS queries to prevent snooping
- **How it works**: Routes DNS through secure resolvers (Cloudflare, Quad9)
- **Protection**: Hides which websites you're visiting from network observers
- **Setup**: `brew services start dnscrypt-proxy`

#### **VPN (NordVPN)**

- **Purpose**: Encrypts all internet traffic
- **How it works**: Routes traffic through secure servers
- **Protection**: Hides your IP address and encrypts all data
- **Setup**: Install via `brew install --cask nordvpn`, then configure account

#### **Firewall (LuLu)**

- **Purpose**: Blocks unknown outbound connections
- **How it works**: Prompts for permission when apps try to connect
- **Protection**: Prevents malware from phoning home
- **Setup**: Install via `brew install lulu`, configure rules

#### **Browser (Brave)**

- **Purpose**: Privacy-focused browsing with built-in protections
- **Features**: Shields, WebRTC protection, fingerprinting resistance
- **Setup**: Install via `brew install --cask brave-browser`

### **Manual Configuration Steps**

#### **Brave Browser Settings**

1. Open Brave and go to `brave://settings/`
2. Enable **Shields** for all sites
3. Go to `brave://settings/shields/` and enable:
   - Block trackers & ads
   - Block fingerprinting
   - Block social media trackers
4. Go to `brave://settings/privacy/` and disable:
   - WebRTC IP handling (set to "Disable non-proxied UDP")
   - Allow sites to check if you have payment methods saved

#### **LuLu Firewall Configuration**

1. Open LuLu and go to Preferences
2. Enable "Automatically allow signed applications"
3. Set "Unknown applications" to "Ask user"
4. Backup your rules: `lulu-backup`
5. Restore rules: `lulu-restore`

#### **macOS System Hardening**

1. **Wi-Fi Settings**:
   - Go to System Preferences → Network → Wi-Fi → Advanced
   - Uncheck "Remember networks this computer has joined"
   - Uncheck "Ask to join new networks"

2. **AirDrop & Sharing**:
   - Go to System Preferences → Sharing
   - Disable all services when on public networks
   - Turn off AirDrop in Control Center

3. **Firewall**:
   - Go to System Preferences → Security & Privacy → Firewall
   - Enable firewall and set to "Block all incoming connections"

### **When to Use Secure Mode**

**Enable `secure-on` when:**

- Using café Wi-Fi
- Connecting at airports or hotels
- Attending conferences (AWS re:Invent, etc.)
- Using any untrusted network
- Working with sensitive data

**Disable `secure-off` when:**

- Back on your home/office network
- VPN is causing connectivity issues
- You need maximum speed for downloads

### **Troubleshooting**

#### **DNS Issues**

```bash
# Check if dnscrypt-proxy is running
brew services list | grep dnscrypt-proxy

# Restart DNS service
dns-stop
dns-start

# Test DNS resolution
nslookup google.com 127.0.0.1
```

#### **VPN Issues**

```bash
# Check NordVPN status
nordvpn status

# Reconnect VPN
vpn-off
vpn-on
```

#### **Performance Impact**

- DNS encryption: Minimal impact (~1-5ms)
- VPN: Moderate impact (10-50ms latency, reduced bandwidth)
- Combined: Best protection, moderate performance cost

---

## 🧱 Structure

This repository is organized to provide a clear separation of concerns and
maintainable configuration management:

### **Core Configuration Files**

```text
dotfiles/
├── system/                  # System-wide configuration files
│   ├── vscode/             # Global VS Code configuration
│   │   └── settings.jsonc  # VS Code settings (formatting, extensions)
│   ├── zsh/                # Global shell configuration
│   │   ├── .zshenv         # Non-interactive-safe environment
│   │   ├── .zprofile       # Login-shell PATH setup
│   │   └── .zshrc          # Interactive aliases and tool hooks
│   ├── git/                # Global Git configuration
│   │   ├── gitconfig       # Global git config (safe to commit)
│   │   ├── gitconfig.local.example # Template for local git config (credentials)
│   │   └── gitignore_global # Global gitignore for OS files
│   ├── aws/                # Global AWS configuration
│   │   └── config          # AWS CLI profiles and settings
│   ├── ghostty/            # Global terminal configuration
│   │   └── config          # Terminal appearance and behavior
│   ├── starship/           # Global shell prompt configuration
│   │   └── starship.toml   # Starship prompt configuration (themes, modules)
│   ├── neovim/             # Global Neovim configuration
│   │   └── init.lua        # Neovim initialization script (minimal setup)
│   ├── dnscrypt-proxy/     # DNS encryption configuration
│   │   └── dnscrypt-proxy.toml # DNS proxy settings for privacy
│   ├── packages/           # Package manifests for bootstrap and doctor
│   │   ├── Brewfile        # Homebrew packages and apps
│   │   ├── pnpm-global.txt # Global Node.js tools list
│   │   ├── vscode-extensions.txt # VS Code extensions list
│   │   ├── dotnet-tools.txt # Global .NET tools list
│   │   └── manual-apps.md  # Manual or approval-gated tools
│   ├── ai/                 # Managed AI Tool Surface scaffolding
│   │   ├── apm/            # AI Asset Manager package declarations
│   │   ├── codex/          # Codex-safe managed configuration
│   │   ├── claude/         # Claude-safe managed configuration
│   │   ├── opencode/       # opencode-safe managed configuration
│   │   └── shared/         # Shared AI Asset declarations
│   └── .editorconfig       # Global editor configuration
├── AGENTS.md               # Repo-wide agent guidance
├── docs/adr/AGENTS.md      # ADR-specific agent guidance
├── scripts/                 # Setup and management scripts
│   ├── setup_symlinks.sh   # Symlink creation script
│   ├── backup.sh           # System backup script
│   └── install.sh          # Prerequisites installer
```

### **Management and Automation**

```text
├── .gitignore              # Repository-specific ignore rules
├── LICENSE                 # MIT License
├── justfile                # Task automation (all setup commands)
├── system/global-justfile  # Global justfile for system-wide commands
├── README.md               # This documentation
├── biome.json              # Biome linting and formatting configuration
├── backup-log.txt          # Backup operation logs
└── symlink-backups.txt     # Symlink operation logs
```

### **How the Symlink System Works**

The dotfiles repository uses a sophisticated symlink system to maintain a
single source of truth:

1. **Source of Truth**: All configurations live in this repository
2. **Symlink Creation**: `setup_symlinks.sh` creates symbolic links from
   dotfiles to system locations
3. **Backup Protection**: Existing configs are backed up before symlinking
4. **Idempotent**: Running setup multiple times is safe

**Example Symlinks:**

- `system/vscode/settings.jsonc` → `~/Library/Application Support/Code/User/settings.json`
- `system/zsh/.zshenv` → `~/.zshenv`
- `system/zsh/.zprofile` → `~/.zprofile`
- `system/zsh/.zshrc` → `~/.zshrc`
- `system/git/gitconfig` → `~/.gitconfig`
- `system/dnscrypt-proxy/dnscrypt-proxy.toml` → `~/.config/dnscrypt-proxy/dnscrypt-proxy.toml`

### **Git Ignore Strategy**

This repository uses a two-tier gitignore approach:

- **`.gitignore`** - Repository-specific files only (backup logs, local config)
- **`git/gitignore_global`** - Global gitignore for OS files (`.DS_Store`,
  `Thumbs.db`, etc.)

The global gitignore is symlinked to `~/.gitignore_global` during setup,
providing system-wide OS file filtering while keeping repository concerns
separate.

---

## 🔄 Development Workflow

### **Daily Development**

This dotfiles setup provides a streamlined development workflow:

#### **Starting a New Project**

```bash
# Create a new project directory
mkdir my-project && cd my-project

# Initialize Biome for consistent formatting
biome init

# Start coding with consistent formatting
# VS Code will automatically format on save
```

#### **Quality Assurance**

```bash
# Run quality checks on your project
just quality-check

# Run security scans
just security-scan

# Format code with Biome
biome format .
```

#### **Environment Management**

```bash
# Use direnv for project-specific environment variables
echo 'export API_KEY="your-key"' > .envrc
direnv allow

# Environment variables are automatically loaded/unloaded
```

### **Maintaining Your Dotfiles**

#### **Adding New Tools**

1. **Homebrew packages**: Add to `system/packages/Brewfile`
2. **Node.js tools**: Add to `system/packages/pnpm-global.txt`; they install
   through the `fnm` default Node plus Corepack/pnpm path
3. **VS Code extensions**: Add to `system/packages/vscode-extensions.txt`
4. **Configuration files**: Add to `setup_symlinks.sh`
5. **Run bootstrap**: `just bootstrap` to install and configure everything

#### **Updating Configurations**

```bash
# Edit configuration files in the dotfiles directory
just edit

# Changes are immediately reflected via symlinks
# No need to restart applications in most cases
```

#### **Backup and Sync**

```bash
# Backup current system state
just backup

# Upgrade all tools
just upgrade

# Commit and push changes
git add .
git commit -m "Update dotfiles configuration"
git push
```

### **Best Practices**

#### **Configuration Management**

- **Edit in dotfiles**: Always edit files in the dotfiles directory, not the
  symlinked locations
- **Test changes**: Use `just quality-check` after making changes
- **Backup first**: Run `just backup` before major changes
- **Version control**: Commit changes regularly

#### **Tool Integration**

- **Use just commands**: Prefer `just` commands over manual installation
- **Consistent formatting**: Let Biome handle code formatting
- **Security first**: Run security scans regularly
- **Environment isolation**: Use direnv for project-specific configs

#### **Dotfiles Troubleshooting**

- **Symlink issues**: Run `just link` to recreate symlinks
- **Tool conflicts**: Check for conflicting global installations
- **Permission issues**: Ensure proper file permissions
- **Backup recovery**: Check `backups/` directory for previous configurations

---

## 🍴 Forking This Repository

This is my personal dotfiles setup, tailored to my specific development
workflow and preferences. Rather than contributing directly to this
repository, I encourage you to:

### **Fork and Customize**

1. **Fork this repository** to your own GitHub account
2. **Customize it** for your specific needs and preferences
3. **Make it your own** by adapting tools, configurations, and workflows
4. **Share improvements** by creating your own public dotfiles repository

### **Why Fork Instead of Contribute?**

- **Personal preferences**: Dotfiles are highly personal and subjective
- **Different workflows**: Your development workflow may differ significantly
- **Tool choices**: You might prefer different tools or versions
- **Learning experience**: Building your own setup teaches valuable skills

### **Getting Started with Your Fork**

1. Fork this repository
2. Update the README to reflect your setup
3. Modify configurations to match your preferences
4. Add or remove tools based on your needs
5. Test thoroughly on your system

### **Sharing Your Setup**

If you create an interesting dotfiles setup based on this one, feel free to:

- Link back to this repository as inspiration
- Share your repository with the community
- Write about your customizations and improvements

This approach ensures that everyone can have a dotfiles setup that's
perfectly tailored to their needs while still benefiting from shared ideas
and approaches.

---

## 🤖 AI Usage & Agent Guidance

This repository uses dedicated AI agent surfaces rather than Cursor as a
managed editor. The current model is:

- Codex, Claude Code, opencode, and Pi as AI agent surfaces.
- APM as the shared AI Asset Manager for reusable baseline skills.
- `AGENTS.md` for repo-wide agent guidance.
- `docs/adr/AGENTS.md` for ADR-specific writing guidance.

### Contributor Guidelines

1. Check whether tools or settings are already declared in the README,
   manifests, or ADRs.
2. Update relevant sections when adding or removing tools.
3. Follow `AGENTS.md` for agent-safe commands, validation, and source-of-truth
   boundaries.
4. Record durable tool choices in ADRs when they affect ownership,
   reproducibility, or cleanup policy.

---

<!-- Reference link definitions for table links -->

[Ghostty]: https://ghostty.app
[zsh]: https://www.zsh.org
[Starship]: https://starship.rs
[Carapace]: https://github.com/rsteube/carapace
[Zoxide]: https://github.com/ajeetdsouza/zoxide
[fzf]: https://github.com/junegunn/fzf
[fd]: https://github.com/sharkdp/fd
[bat]: https://github.com/sharkdp/bat
[Homebrew]: https://brew.sh
[pnpm]: https://pnpm.io
[fnm]: https://github.com/Schniz/fnm
[cargo]: https://doc.rust-lang.org/cargo/
[Neovim]: https://neovim.io
[VS Code]: https://code.visualstudio.com
[Raycast]: https://www.raycast.com
[awscli]: https://aws.amazon.com/cli
[cdk]: https://docs.aws.amazon.com/cdk/
[cdk-dia]: https://github.com/pistazie/cdk-dia
[ripsecrets]: https://github.com/snickdx/ripsecrets
[gitleaks]: https://github.com/gitleaks/gitleaks
[direnv]: https://direnv.net
[dotenv-linter]: https://dotenv-linter.github.io
[editorconfig-checker]: https://editorconfig-checker.github.io
[topgrade]: https://github.com/r-darwish/topgrade
